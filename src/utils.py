"""
Utilities module with helper functions and logging setup.
"""

import logging
import os
import sys
from typing import Dict, Any
from .config import config


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Setup logging configuration."""
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/rap_iq.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger('rap_iq')
    logger.info("Logging setup complete")
    
    return logger


def validate_environment() -> Dict[str, Any]:
    """Validate the environment and return status."""
    
    status = {
        "python_version": sys.version,
        "cuda_available": False,
        "gpu_memory": 0.0,
        "required_packages": [],
        "missing_packages": [],
        "spacy_model": False
    }
    
    # Check CUDA
    try:
        import torch
        status["cuda_available"] = torch.cuda.is_available()
        if status["cuda_available"]:
            status["gpu_memory"] = torch.cuda.get_device_properties(0).total_memory / 1e9
    except ImportError:
        status["missing_packages"].append("torch")
    
    # Check required packages
    required_packages = [
        "transformers", "accelerate", "bitsandbytes", "gradio", 
        "beautifulsoup4", "requests", "feedparser", "newspaper3k",
        "spacy", "sentence_transformers", "aiohttp", "nest_asyncio"
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            status["required_packages"].append(package)
        except ImportError:
            status["missing_packages"].append(package)
    
    # Check spaCy model
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        status["spacy_model"] = True
    except OSError:
        status["spacy_model"] = False
    
    return status


def print_system_status():
    """Print system status information."""
    
    print("\n" + "="*70)
    print("🚀 RAP IQ - SYSTEM STATUS")
    print("="*70)
    
    # Environment info
    env_info = config.get_environment_info()
    print(f"🔥 Device: {env_info['device']}")
    print(f"📊 GPU Memory: {env_info['gpu_memory_gb']}GB")
    print(f"🤖 Model: {env_info['model_name']}")
    print(f"🔍 Max Results: {env_info['max_results']}")
    print(f"⏱️ Timeout: {env_info['timeout']}s")
    
    # Validation
    validation = validate_environment()
    
    print(f"\n📦 Package Status:")
    if validation["missing_packages"]:
        print(f"❌ Missing: {', '.join(validation['missing_packages'])}")
    else:
        print("✅ All required packages installed")
    
    print(f"🧠 spaCy Model: {'✅ Loaded' if validation['spacy_model'] else '❌ Not found'}")
    print(f"🔥 CUDA: {'✅ Available' if validation['cuda_available'] else '❌ Not available'}")
    
    print("="*70)


def create_project_structure():
    """Create the project directory structure."""
    
    directories = [
        "src",
        "logs",
        "data",
        "tests",
        "docs",
        "examples"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ Project structure created")


def get_project_info() -> Dict[str, str]:
    """Get project information."""
    
    return {
        "name": "RAP IQ",
        "version": "1.0.0",
        "description": "AI News Intelligence Platform",
        "author": "RAP IQ Team",
        "email": "support@rap-iq.com",
        "repository": "https://github.com/yourusername/rap-iq",
        "license": "MIT"
    }


def format_timestamp(timestamp: str) -> str:
    """Format timestamp for display."""
    
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to specified length."""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations."""
    
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename


def calculate_processing_time(start_time: float) -> str:
    """Calculate and format processing time."""
    
    elapsed = time.time() - start_time
    
    if elapsed < 1:
        return f"{elapsed*1000:.0f}ms"
    elif elapsed < 60:
        return f"{elapsed:.1f}s"
    else:
        minutes = int(elapsed // 60)
        seconds = elapsed % 60
        return f"{minutes}m {seconds:.1f}s"


def validate_company_name(company: str) -> bool:
    """Validate company name format."""
    
    if not company or len(company.strip()) < 2:
        return False
    
    # Check for common invalid patterns
    invalid_patterns = [
        'http://', 'https://', 'www.', '.com', '.org', '.net',
        'test', 'example', 'demo', 'sample'
    ]
    
    company_lower = company.lower()
    for pattern in invalid_patterns:
        if pattern in company_lower:
            return False
    
    return True


def extract_domain_from_url(url: str) -> str:
    """Extract domain from URL."""
    
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    except:
        return "unknown"


def is_high_impact_news(title: str, snippet: str = "") -> bool:
    """Check if news is high impact based on keywords."""
    
    high_impact_keywords = [
        'breaking', 'exclusive', 'urgent', 'critical', 'major',
        'acquisition', 'merger', 'bankruptcy', 'lawsuit', 'scandal',
        'ceo', 'resignation', 'fired', 'investigation'
    ]
    
    text = f"{title} {snippet}".lower()
    
    for keyword in high_impact_keywords:
        if keyword in text:
            return True
    
    return False


def format_impact_score(score: float) -> str:
    """Format impact score with color coding."""
    
    if score >= 8:
        return f"🔴 {score:.1f}/10 (Critical)"
    elif score >= 6:
        return f"🟡 {score:.1f}/10 (High)"
    elif score >= 4:
        return f"🟢 {score:.1f}/10 (Medium)"
    else:
        return f"⚪ {score:.1f}/10 (Low)"


# Import time for processing time calculation
import time 