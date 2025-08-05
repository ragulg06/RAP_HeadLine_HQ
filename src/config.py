"""
Configuration module for RAP IQ platform.
"""

import os
import torch
from dataclasses import dataclass
from typing import Dict, List, Optional
from transformers import BitsAndBytesConfig


@dataclass
class ModelConfig:
    """Configuration for AI models."""
    model_name: str = "microsoft/DialoGPT-medium"
    max_tokens: int = 300
    temperature: float = 0.7
    context_window: int = 2048
    load_in_4bit: bool = True
    bnb_4bit_compute_dtype: str = "float16"
    bnb_4bit_use_double_quant: bool = True
    bnb_4bit_quant_type: str = "nf4"
    
    def get_quantization_config(self) -> BitsAndBytesConfig:
        """Get quantization configuration for GPU efficiency."""
        return BitsAndBytesConfig(
            load_in_4bit=self.load_in_4bit,
            bnb_4bit_compute_dtype=getattr(torch, self.bnb_4bit_compute_dtype),
            bnb_4bit_use_double_quant=self.bnb_4bit_use_double_quant,
            bnb_4bit_quant_type=self.bnb_4bit_quant_type
        )


@dataclass
class CrawlerConfig:
    """Configuration for news crawlers."""
    timeout: int = 30
    max_results: int = 15
    user_agent: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    impact_threshold: float = 5.0
    time_range_hours: int = 24
    
    # RSS feed configurations
    rss_feeds: Dict[str, List[str]] = None
    
    def __post_init__(self):
        if self.rss_feeds is None:
            self.rss_feeds = {
                'tesla': ['https://www.tesla.com/blog/rss'],
                'apple': ['https://www.apple.com/newsroom/rss-feed.rss'],
                'microsoft': ['https://blogs.microsoft.com/feed/'],
                'google': ['https://blog.google/rss/'],
                'amazon': ['https://press.aboutamazon.com/rss/news-releases.xml']
            }


@dataclass
class ServerConfig:
    """Configuration for web server."""
    host: str = "0.0.0.0"
    port: int = 7860
    share: bool = True
    debug: bool = False
    show_error: bool = True
    quiet: bool = False
    inbrowser: bool = True
    show_tips: bool = True
    enable_queue: bool = True
    max_threads: int = 10


@dataclass
class UIConfig:
    """Configuration for user interface."""
    theme: str = "soft"
    max_width: str = "1400px"
    font_family: str = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
    chat_height: int = 650
    output_height: int = 600


class Config:
    """Main configuration class."""
    
    def __init__(self):
        self.model = ModelConfig()
        self.crawler = CrawlerConfig()
        self.server = ServerConfig()
        self.ui = UIConfig()
        
        # Environment variables
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.gpu_memory = self._get_gpu_memory()
        
    def _get_gpu_memory(self) -> float:
        """Get available GPU memory in GB."""
        if torch.cuda.is_available():
            return torch.cuda.get_device_properties(0).total_memory / 1e9
        return 0.0
    
    def get_environment_info(self) -> Dict[str, str]:
        """Get environment information for logging."""
        return {
            "device": self.device,
            "gpu_memory_gb": f"{self.gpu_memory:.1f}",
            "model_name": self.model.model_name,
            "max_results": str(self.crawler.max_results),
            "timeout": str(self.crawler.timeout)
        }
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        try:
            # Validate model settings
            assert self.model.max_tokens > 0
            assert 0 <= self.model.temperature <= 2.0
            
            # Validate crawler settings
            assert self.crawler.timeout > 0
            assert self.crawler.max_results > 0
            assert 0 <= self.crawler.impact_threshold <= 10
            
            # Validate server settings
            assert 1024 <= self.server.port <= 65535
            
            return True
        except AssertionError:
            return False


# Global configuration instance
config = Config() 