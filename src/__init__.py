"""
RAP IQ - AI News Intelligence Platform

A comprehensive AI-powered news analysis platform with multi-source crawling,
conversational AI, and enterprise-grade analytics.
"""

__version__ = "1.0.0"
__author__ = "RAP IQ Team"
__email__ = "support@rap-iq.com"

from .config import Config
from .models import ModelManager
from .crawlers import NewsCrawler, DuckDuckGoCrawler, RSSCrawler
from .ai import ConversationalAI, ResponseGenerator
from .pipeline import NewsPipeline, EnterpriseNewsPipeline
from .utils import setup_logging, validate_environment

__all__ = [
    'Config',
    'ModelManager', 
    'NewsCrawler',
    'DuckDuckGoCrawler',
    'RSSCrawler',
    'ConversationalAI',
    'ResponseGenerator',
    'NewsPipeline',
    'EnterpriseNewsPipeline',
    'setup_logging',
    'validate_environment'
] 