"""
Pipeline module for orchestrating news processing workflow.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from .crawlers import DuckDuckGoCrawler, RSSCrawler, AdvancedNewsCrawler, NewsExtractor
from .ai import ConversationalAI, ResponseGenerator
from .models import model_manager
from .config import config


class NewsAggregator:
    """Orchestrates multiple crawlers and aggregates results."""
    
    def __init__(self):
        self.crawlers = [
            DuckDuckGoCrawler(),
            RSSCrawler()
        ]
        self.extractor = NewsExtractor()
        self.cache = {}
    
    async def fetch_all_news(self, company: str, time_range_hours: int = 24) -> List[Dict]:
        """Fetch news from all sources."""
        print(f"🔍 Fetching news for: {company}")
        
        all_results = []
        
        # Run crawlers concurrently
        tasks = []
        for crawler in self.crawlers:
            tasks.append(crawler.fetch(company))
        
        try:
            crawler_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for results in crawler_results:
                if isinstance(results, list):
                    all_results.extend(results)
        
        except Exception as e:
            print(f"❌ Crawling error: {e}")
        
        # Deduplicate by URL and title similarity
        unique_results = self._deduplicate(all_results)
        
        # Filter by time range
        cutoff_time = datetime.now() - timedelta(hours=time_range_hours)
        filtered_results = self._filter_by_time(unique_results, cutoff_time)
        
        # Sort by impact score and recency
        sorted_results = sorted(filtered_results,
                              key=lambda x: (x['impact_score'], x['timestamp']),
                              reverse=True)
        
        return sorted_results[:10]  # Return top 10 results
    
    def _deduplicate(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate articles."""
        seen_urls = set()
        seen_titles = set()
        unique_results = []
        
        for result in results:
            url = result.get('url', '')
            title = result.get('title', '').lower()
            
            # Simple deduplication by URL and similar titles
            if url not in seen_urls and title not in seen_titles:
                seen_urls.add(url)
                seen_titles.add(title)
                unique_results.append(result)
        
        return unique_results
    
    def _filter_by_time(self, results: List[Dict], cutoff_time: datetime) -> List[Dict]:
        """Filter results by time range."""
        filtered = []
        for result in results:
            try:
                timestamp_str = result.get('timestamp', '')
                if timestamp_str:
                    # Handle different timestamp formats
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    except:
                        timestamp = datetime.now()  # Default to now if parsing fails
                    
                    if timestamp >= cutoff_time:
                        filtered.append(result)
                else:
                    filtered.append(result)  # Include if no timestamp
            except:
                filtered.append(result)  # Include if parsing fails
        
        return filtered


class NewsPipeline:
    """Basic news processing pipeline."""
    
    def __init__(self):
        self.aggregator = NewsAggregator()
        self.response_generator = ResponseGenerator(
            model_manager.model, 
            model_manager.tokenizer
        )
    
    async def process_news_query(self, company: str, style: str, time_range: str, impact_threshold: float) -> str:
        """Main pipeline to process news query."""
        
        try:
            # Convert time range to hours
            time_mapping = {"1 hour": 1, "6 hours": 6, "24 hours": 24}
            hours = time_mapping.get(time_range, 24)
            
            print(f"🚀 Processing query for {company}...")
            
            # Step 1: Fetch news from all sources
            news_items = await self.aggregator.fetch_all_news(company, hours)
            
            if not news_items:
                return f"❌ No recent news found for '{company}'. Please check the company name and try again."
            
            # Step 2: Filter by impact threshold
            filtered_news = [item for item in news_items if item['impact_score'] >= impact_threshold]
            
            if not filtered_news:
                return f"📊 Found {len(news_items)} news items for '{company}', but none meet your impact threshold of {impact_threshold}/10. Try lowering the threshold."
            
            print(f"✅ Found {len(filtered_news)} relevant news items")
            
            # Step 3: Generate styled summary
            summary = self.response_generator.generate_summary(filtered_news, style, company)
            
            return summary
        
        except Exception as e:
            error_msg = f"❌ Error processing query: {str(e)}"
            print(error_msg)
            return error_msg


class EnterpriseNewsPipeline:
    """Enterprise-grade news processing pipeline."""
    
    def __init__(self):
        self.advanced_crawler = AdvancedNewsCrawler()
        self.rss_crawler = RSSCrawler()
        self.conversational_ai = ConversationalAI()
        self.session_data = {}
    
    async def process_enterprise_query(self,
                                     user_input: str,
                                     company: str = None,
                                     style: str = "professional",
                                     time_range: str = "24 hours",
                                     impact_threshold: float = 5.0,
                                     session_id: str = "default") -> str:
        """Process enterprise-level news query with full context."""
        
        start_time = time.time()
        
        try:
            # Extract company name if not provided
            if not company:
                company = self._extract_company_from_input(user_input)
            
            if not company:
                return self.conversational_ai.generate_conversational_response(
                    user_input, None, style
                ) + "\n\n💡 *Tip: Mention a specific company name for detailed news analysis.*"
            
            print(f"🔍 Processing enterprise query for: {company}")
            
            # Multi-source data gathering
            news_tasks = [
                self.advanced_crawler.enhanced_duckduckgo_scrape(company, 15),
                self.rss_crawler.fetch(company)
            ]
            
            # Parallel execution
            crawler_results = await asyncio.gather(*news_tasks, return_exceptions=True)
            
            # Combine and process results
            all_news = []
            for results in crawler_results:
                if isinstance(results, list):
                    all_news.extend(results)
            
            if not all_news:
                return f"❌ No recent news found for '{company}'. The company might be private, very new, or the name might need clarification. Try alternative spellings or check if it's a publicly traded company."
            
            # Advanced filtering and ranking
            filtered_news = self._enterprise_filter_news(all_news, impact_threshold, time_range)
            
            # Store session data
            self.session_data[session_id] = {
                'last_company': company,
                'last_results': filtered_news,
                'query_time': datetime.now().isoformat(),
                'processing_time': time.time() - start_time
            }
            
            # Generate conversational response
            response = self.conversational_ai.generate_conversational_response(
                user_input, filtered_news, style
            )
            
            # Add enterprise metadata
            processing_time = time.time() - start_time
            response += f"\n\n---\n📊 **Enterprise Analytics**: Processed {len(all_news)} sources in {processing_time:.2f}s | Found {len(filtered_news)} relevant items"
            
            return response
        
        except Exception as e:
            error_response = f"❌ **System Error**: {str(e)}\n\n"
            error_response += "🔧 **Troubleshooting**: The system encountered an issue. "
            error_response += "This could be due to network connectivity, rate limiting, or data processing challenges. "
            error_response += "Please try again in a moment or contact support if the issue persists."
            return error_response
    
    def _extract_company_from_input(self, user_input: str) -> str:
        """Extract company name from user input using NLP."""
        try:
            if not model_manager.nlp:
                return None
            
            doc = model_manager.nlp(user_input)
            
            # Look for organizations
            for ent in doc.ents:
                if ent.label_ in ["ORG", "COMPANY"]:
                    return ent.text
            
            # Common company keywords
            company_indicators = ['stock', 'shares', 'ticker', 'company', 'corp', 'inc', 'ltd']
            
            # Simple pattern matching for common formats
            words = user_input.split()
            for i, word in enumerate(words):
                if word.lower() in company_indicators and i > 0:
                    return words[i-1]
            
            return None
        
        except Exception as e:
            return None
    
    def _enterprise_filter_news(self, news_items: List[Dict], impact_threshold: float, time_range: str) -> List[Dict]:
        """Enterprise-level news filtering with advanced criteria."""
        
        # Time filtering
        time_mapping = {"1 hour": 1, "6 hours": 6, "24 hours": 24, "1 week": 168}
        hours = time_mapping.get(time_range, 24)
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        filtered = []
        
        for item in news_items:
            try:
                # Impact threshold filter
                if item.get('impact_score', 0) < impact_threshold:
                    continue
                
                # Time filter
                timestamp_str = item.get('timestamp', '')
                if timestamp_str:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        if timestamp < cutoff_time:
                            continue
                    except:
                        pass  # Include if timestamp parsing fails
                
                # Content quality filter
                title = item.get('title', '')
                if len(title) < 10 or 'error' in title.lower():
                    continue
                
                # URL validation
                url = item.get('url', '')
                if not url or not url.startswith('http'):
                    continue
                
                filtered.append(item)
            
            except Exception as e:
                continue
        
        # Advanced ranking algorithm
        for item in filtered:
            # Boost score based on source credibility
            source = item.get('source', '').lower()
            if any(trusted in source for trusted in ['reuters', 'bloomberg', 'cnbc', 'ap', 'wsj']):
                item['impact_score'] = min(item['impact_score'] + 1.0, 10.0)
            
            # Boost recent news
            try:
                timestamp = datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00'))
                hours_old = (datetime.now(timestamp.tzinfo) - timestamp).total_seconds() / 3600
                if hours_old < 1:  # Less than 1 hour old
                    item['impact_score'] = min(item['impact_score'] + 0.5, 10.0)
            except:
                pass
        
        # Sort by impact score and return top items
        return sorted(filtered, key=lambda x: x['impact_score'], reverse=True)[:12]
    
    def get_session_data(self, session_id: str) -> Dict:
        """Get session data for analytics."""
        return self.session_data.get(session_id, {})
    
    def clear_session_data(self, session_id: str):
        """Clear session data."""
        if session_id in self.session_data:
            del self.session_data[session_id] 