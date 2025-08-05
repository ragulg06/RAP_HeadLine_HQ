"""
Test module for the news pipeline functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from src.pipeline import NewsPipeline, EnterpriseNewsPipeline
from src.crawlers import DuckDuckGoCrawler, RSSCrawler


class TestNewsPipeline:
    """Test cases for the basic news pipeline."""
    
    @pytest.fixture
    def pipeline(self):
        """Create a pipeline instance for testing."""
        return NewsPipeline()
    
    @pytest.mark.asyncio
    async def test_process_news_query_success(self, pipeline):
        """Test successful news query processing."""
        # Mock the aggregator to return test data
        test_news = [
            {
                'title': 'Test News 1',
                'url': 'http://example.com/1',
                'source': 'Test Source',
                'impact_score': 7.5,
                'timestamp': '2024-01-01T12:00:00'
            }
        ]
        
        with patch.object(pipeline.aggregator, 'fetch_all_news', return_value=test_news):
            result = await pipeline.process_news_query(
                company="Tesla",
                style="📊 Formal business summary",
                time_range="24 hours",
                impact_threshold=5.0
            )
            
            assert "Tesla" in result
            assert "Test News 1" in result
            assert "http://example.com/1" in result
    
    @pytest.mark.asyncio
    async def test_process_news_query_no_results(self, pipeline):
        """Test news query with no results."""
        with patch.object(pipeline.aggregator, 'fetch_all_news', return_value=[]):
            result = await pipeline.process_news_query(
                company="NonexistentCompany",
                style="📊 Formal business summary",
                time_range="24 hours",
                impact_threshold=5.0
            )
            
            assert "No recent news found" in result
            assert "NonexistentCompany" in result
    
    @pytest.mark.asyncio
    async def test_process_news_query_low_impact(self, pipeline):
        """Test news query with low impact results."""
        test_news = [
            {
                'title': 'Low Impact News',
                'url': 'http://example.com/low',
                'source': 'Test Source',
                'impact_score': 3.0,
                'timestamp': '2024-01-01T12:00:00'
            }
        ]
        
        with patch.object(pipeline.aggregator, 'fetch_all_news', return_value=test_news):
            result = await pipeline.process_news_query(
                company="Tesla",
                style="📊 Formal business summary",
                time_range="24 hours",
                impact_threshold=5.0
            )
            
            assert "none meet your impact threshold" in result


class TestEnterpriseNewsPipeline:
    """Test cases for the enterprise news pipeline."""
    
    @pytest.fixture
    def enterprise_pipeline(self):
        """Create an enterprise pipeline instance for testing."""
        return EnterpriseNewsPipeline()
    
    @pytest.mark.asyncio
    async def test_process_enterprise_query_success(self, enterprise_pipeline):
        """Test successful enterprise query processing."""
        test_news = [
            {
                'title': 'Enterprise Test News',
                'url': 'http://example.com/enterprise',
                'source': 'Enterprise Source',
                'impact_score': 8.0,
                'timestamp': '2024-01-01T12:00:00',
                'snippet': 'This is a test snippet'
            }
        ]
        
        with patch.object(enterprise_pipeline.advanced_crawler, 'enhanced_duckduckgo_scrape', return_value=test_news):
            with patch.object(enterprise_pipeline.rss_crawler, 'fetch', return_value=[]):
                result = await enterprise_pipeline.process_enterprise_query(
                    user_input="What's the latest on Tesla?",
                    company="Tesla",
                    style="professional",
                    time_range="24 hours",
                    impact_threshold=5.0
                )
                
                assert "Tesla" in result
                assert "Enterprise Test News" in result
                assert "Enterprise Analytics" in result
    
    def test_extract_company_from_input(self, enterprise_pipeline):
        """Test company name extraction from user input."""
        # Test with organization entity
        with patch('src.pipeline.model_manager') as mock_model_manager:
            mock_nlp = Mock()
            mock_doc = Mock()
            mock_ent = Mock()
            mock_ent.text = "Apple"
            mock_ent.label_ = "ORG"
            mock_doc.ents = [mock_ent]
            mock_nlp.return_value = mock_doc
            mock_model_manager.nlp = mock_nlp
            
            result = enterprise_pipeline._extract_company_from_input("Tell me about Apple's latest news")
            assert result == "Apple"
    
    def test_enterprise_filter_news(self, enterprise_pipeline):
        """Test enterprise news filtering."""
        test_news = [
            {
                'title': 'High Impact News',
                'url': 'http://example.com/high',
                'source': 'Reuters',
                'impact_score': 8.0,
                'timestamp': '2024-01-01T12:00:00'
            },
            {
                'title': 'Low Impact News',
                'url': 'http://example.com/low',
                'source': 'Unknown Source',
                'impact_score': 3.0,
                'timestamp': '2024-01-01T12:00:00'
            }
        ]
        
        filtered = enterprise_pipeline._enterprise_filter_news(
            test_news, 
            impact_threshold=5.0, 
            time_range="24 hours"
        )
        
        # Should only return high impact news
        assert len(filtered) == 1
        assert filtered[0]['title'] == 'High Impact News'
        # Reuters source should get a boost
        assert filtered[0]['impact_score'] >= 8.0


class TestCrawlers:
    """Test cases for news crawlers."""
    
    @pytest.fixture
    def duckduckgo_crawler(self):
        """Create a DuckDuckGo crawler instance."""
        return DuckDuckGoCrawler()
    
    @pytest.fixture
    def rss_crawler(self):
        """Create an RSS crawler instance."""
        return RSSCrawler()
    
    def test_calculate_impact(self, duckduckgo_crawler):
        """Test impact score calculation."""
        # High impact keywords
        high_impact_title = "Tesla announces major acquisition deal"
        score = duckduckgo_crawler._calculate_impact(high_impact_title)
        assert score > 7.0
        
        # Low impact keywords
        low_impact_title = "Tesla provides update on meeting"
        score = duckduckgo_crawler._calculate_impact(low_impact_title)
        assert score < 7.0
    
    @pytest.mark.asyncio
    async def test_duckduckgo_fetch_error_handling(self, duckduckgo_crawler):
        """Test DuckDuckGo crawler error handling."""
        with patch.object(duckduckgo_crawler.session, 'get', side_effect=Exception("Network error")):
            result = await duckduckgo_crawler.fetch("Tesla")
            assert result == []
    
    @pytest.mark.asyncio
    async def test_rss_fetch_error_handling(self, rss_crawler):
        """Test RSS crawler error handling."""
        with patch('src.crawlers.feedparser.parse', side_effect=Exception("RSS error")):
            result = await rss_crawler.fetch("Tesla")
            assert result == []


# Integration tests
class TestIntegration:
    """Integration tests for the complete pipeline."""
    
    @pytest.mark.asyncio
    async def test_full_pipeline_integration(self):
        """Test the complete pipeline integration."""
        from src.pipeline import EnterpriseNewsPipeline
        
        pipeline = EnterpriseNewsPipeline()
        
        # Mock all external dependencies
        with patch.object(pipeline.advanced_crawler, 'enhanced_duckduckgo_scrape', return_value=[]):
            with patch.object(pipeline.rss_crawler, 'fetch', return_value=[]):
                with patch.object(pipeline.conversational_ai, 'generate_conversational_response', return_value="Mock response"):
                    result = await pipeline.process_enterprise_query(
                        user_input="What's happening with Tesla?",
                        company="Tesla",
                        style="professional",
                        time_range="24 hours",
                        impact_threshold=5.0
                    )
                    
                    assert "Mock response" in result


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 