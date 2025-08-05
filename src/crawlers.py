"""
News crawlers module for fetching news from multiple sources.
"""

import asyncio
import aiohttp
import requests
import feedparser
import urllib.parse
import ssl
import certifi
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import newspaper
from readability import Document
from .config import config


class BaseCrawler:
    """Base class for all news crawlers."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.crawler.user_agent
        })
    
    async def fetch(self, company: str) -> List[Dict]:
        """Fetch news for given company."""
        raise NotImplementedError
    
    def _calculate_impact(self, title: str, snippet: str = "") -> float:
        """Calculate impact score based on keywords."""
        high_impact = ['acquisition', 'merger', 'lawsuit', 'bankruptcy', 'ceo', 'scandal', 'investigation']
        medium_impact = ['earnings', 'revenue', 'partnership', 'launch', 'investment', 'breakthrough']
        low_impact = ['update', 'comment', 'statement', 'meeting', 'interview']
        
        text = f"{title} {snippet}".lower()
        score = 5.0  # Base score
        
        for keyword in high_impact:
            if keyword in text:
                score += 3.0
        
        for keyword in medium_impact:
            if keyword in text:
                score += 1.5
        
        for keyword in low_impact:
            if keyword in text:
                score += 0.5
        
        return min(score, 10.0)


class DuckDuckGoCrawler(BaseCrawler):
    """Scrape DuckDuckGo search results."""
    
    async def fetch(self, company: str) -> List[Dict]:
        """Fetch news from DuckDuckGo."""
        try:
            query = f"{company} news"
            url = f"https://html.duckduckgo.com/html/?q={query}"
            
            response = self.session.get(url, timeout=config.crawler.timeout)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            for result in soup.find_all('div', class_='result')[:5]:
                try:
                    title_elem = result.find('a', class_='result__a')
                    if title_elem:
                        title = title_elem.get_text().strip()
                        link = title_elem.get('href')
                        
                        results.append({
                            'title': title,
                            'url': link,
                            'source': 'DuckDuckGo',
                            'timestamp': datetime.now().isoformat(),
                            'impact_score': self._calculate_impact(title)
                        })
                except Exception as e:
                    continue
            
            return results
            
        except Exception as e:
            print(f"❌ DuckDuckGo error: {e}")
            return []


class RSSCrawler(BaseCrawler):
    """Fetch from RSS feeds."""
    
    def __init__(self):
        super().__init__()
        self.rss_feeds = config.crawler.rss_feeds
    
    async def fetch(self, company: str) -> List[Dict]:
        """Fetch from RSS feeds."""
        try:
            company_lower = company.lower()
            feeds = self.rss_feeds.get(company_lower, [])
            
            # Add generic news RSS
            feeds.append(f'https://news.google.com/rss/search?q={company}&hl=en-US&gl=US&ceid=US:en')
            
            results = []
            for feed_url in feeds:
                try:
                    # Set SSL context for secure connections
                    ssl_context = ssl.create_default_context(cafile=certifi.where())
                    
                    feed = feedparser.parse(feed_url)
                    for entry in feed.entries[:3]:  # Limit to 3 per feed
                        results.append({
                            'title': entry.title,
                            'url': entry.link,
                            'source': f'RSS-{feed.feed.get("title", "Unknown")}',
                            'timestamp': entry.get('published', datetime.now().isoformat()),
                            'impact_score': self._calculate_impact(entry.title),
                            'summary': entry.get('summary', '')[:200] + '...'
                        })
                except Exception as e:
                    continue
            
            return results
            
        except Exception as e:
            print(f"❌ RSS error: {e}")
            return []


class AdvancedNewsCrawler(BaseCrawler):
    """Enterprise-level multi-source news crawler."""
    
    def __init__(self):
        super().__init__()
        
        # Major news sources for targeted scraping
        self.news_sources = {
            'reuters': 'https://www.reuters.com/site-search/?query={}',
            'bloomberg': 'https://www.bloomberg.com/search?query={}',
            'cnbc': 'https://www.cnbc.com/search/?query={}',
            'marketwatch': 'https://www.marketwatch.com/tools/quotes/lookup.asp?siteID=mktw&Lookup={}',
            'yahoo_finance': 'https://finance.yahoo.com/quote/{}/news',
            'seeking_alpha': 'https://seekingalpha.com/symbol/{}/news',
            'fool': 'https://www.fool.com/search/?q={}',
            'benzinga': 'https://www.benzinga.com/search?q={}'
        }
    
    async def enhanced_duckduckgo_scrape(self, company: str, max_results: int = 15) -> List[Dict]:
        """Enhanced DuckDuckGo scraping with multiple query variations."""
        
        # Multiple search variations for comprehensive coverage
        search_queries = [
            f'"{company}" news today',
            f'{company} earnings latest',
            f'{company} stock news',
            f'{company} press release',
            f'{company} acquisition merger',
            f'{company} CEO announcement',
            f'{company} financial results'
        ]
        
        all_results = []
        
        for query in search_queries:
            try:
                encoded_query = urllib.parse.quote_plus(query)
                urls = [
                    f"https://html.duckduckgo.com/html/?q={encoded_query}",
                    f"https://duckduckgo.com/html/?q={encoded_query}&df=d",  # Last day
                    f"https://duckduckgo.com/html/?q={encoded_query}&df=w"   # Last week
                ]
                
                for url in urls:
                    try:
                        response = self.session.get(url, timeout=15)
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Enhanced parsing for different result types
                        results = soup.find_all(['div'], class_=['result', 'web-result', 'result__body'])
                        
                        for result in results[:5]:  # Top 5 per variation
                            try:
                                # Multiple selectors for title
                                title_elem = (result.find('a', class_=['result__a', 'result__url']) or
                                            result.find('h3') or
                                            result.find('a'))
                                
                                if title_elem:
                                    title = title_elem.get_text().strip()
                                    link = title_elem.get('href', '')
                                    
                                    # Extract snippet if available
                                    snippet_elem = result.find(['span', 'div'], class_=['result__snippet', 'snippet'])
                                    snippet = snippet_elem.get_text().strip() if snippet_elem else ""
                                    
                                    # Calculate enhanced impact score
                                    impact_score = self._calculate_enhanced_impact(title, snippet, query)
                                    
                                    all_results.append({
                                        'title': title,
                                        'url': link,
                                        'snippet': snippet,
                                        'source': 'DuckDuckGo-Enhanced',
                                        'search_query': query,
                                        'timestamp': datetime.now().isoformat(),
                                        'impact_score': impact_score,
                                        'content_type': self._classify_content_type(title, snippet)
                                    })
                                    
                            except Exception as e:
                                continue
                                
                    except Exception as e:
                        print(f"⚠️ URL error for {url}: {e}")
                        continue
                        
            except Exception as e:
                print(f"⚠️ Query error for {query}: {e}")
                continue
        
        # Remove duplicates and return top results
        unique_results = self._advanced_deduplication(all_results)
        return sorted(unique_results, key=lambda x: x['impact_score'], reverse=True)[:max_results]
    
    def _calculate_enhanced_impact(self, title: str, snippet: str, query: str) -> float:
        """Advanced impact scoring with multiple factors."""
        
        # Weighted keyword categories
        impact_keywords = {
            'critical': ['bankruptcy', 'lawsuit', 'investigation', 'scandal', 'fraud', 'fired', 'resignation'],
            'high': ['acquisition', 'merger', 'ipo', 'earnings beat', 'breakthrough', 'partnership'],
            'medium': ['earnings', 'revenue', 'quarterly', 'investment', 'expansion', 'launch'],
            'low': ['update', 'statement', 'comment', 'meeting', 'interview']
        }
        
        text = f"{title} {snippet}".lower()
        base_score = 5.0
        
        # Keyword-based scoring
        for level, keywords in impact_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    if level == 'critical':
                        base_score += 4.0
                    elif level == 'high':
                        base_score += 2.5
                    elif level == 'medium':
                        base_score += 1.5
                    elif level == 'low':
                        base_score += 0.5
        
        # Recency boost (based on query type)
        if 'today' in query or 'latest' in query:
            base_score += 1.0
        
        # Length penalty for very short content
        if len(snippet) < 50:
            base_score -= 0.5
        
        return min(base_score, 10.0)
    
    def _classify_content_type(self, title: str, snippet: str) -> str:
        """Classify the type of news content."""
        text = f"{title} {snippet}".lower()
        
        if any(word in text for word in ['earnings', 'quarterly', 'revenue', 'profit']):
            return 'Financial'
        elif any(word in text for word in ['acquisition', 'merger', 'deal', 'partnership']):
            return 'M&A'
        elif any(word in text for word in ['product', 'launch', 'release', 'innovation']):
            return 'Product'
        elif any(word in text for word in ['ceo', 'executive', 'leadership']):
            return 'Leadership'
        elif any(word in text for word in ['stock', 'shares', 'market', 'trading']):
            return 'Market'
        else:
            return 'General'
    
    def _advanced_deduplication(self, results: List[Dict]) -> List[Dict]:
        """Advanced deduplication using content similarity."""
        if not results:
            return []
        
        unique_results = []
        seen_urls = set()
        seen_titles = set()
        
        for result in results:
            url = result.get('url', '')
            title = result.get('title', '').lower().strip()
            
            # URL-based deduplication
            if url in seen_urls:
                continue
            
            # Title similarity check
            is_similar = False
            for seen_title in seen_titles:
                # Simple similarity check (can be enhanced with fuzzy matching)
                if len(set(title.split()) & set(seen_title.split())) / max(len(title.split()), len(seen_title.split())) > 0.7:
                    is_similar = True
                    break
            
            if not is_similar:
                seen_urls.add(url)
                seen_titles.add(title)
                unique_results.append(result)
        
        return unique_results


class NewsExtractor:
    """Extract clean content from news URLs."""
    
    @staticmethod
    def extract_content(url: str) -> str:
        """Extract main content from news article."""
        try:
            article = newspaper.Article(url)
            article.download()
            article.parse()
            return article.text[:1000]  # Limit text length
            
        except Exception as e:
            try:
                # Fallback to readability
                response = requests.get(url, timeout=10)
                doc = Document(response.content)
                soup = BeautifulSoup(doc.summary(), 'html.parser')
                return soup.get_text()[:1000]
            except:
                return "Content extraction failed" 