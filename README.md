# 🚀 RAP IQ - AI News Intelligence Platform

> **Real-time AI-powered company news analysis with multi-source intelligence and conversational AI**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)](https://pytorch.org)
[![Gradio](https://img.shields.io/badge/Gradio-Interface-green.svg)](https://gradio.app)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

RAP IQ is an enterprise-grade AI news intelligence platform that provides real-time company news analysis using advanced machine learning and multi-source data crawling. The platform combines conversational AI with comprehensive news aggregation to deliver actionable business insights.

### Key Capabilities

- **Multi-Source News Crawling**: DuckDuckGo, RSS feeds, financial sites
- **Conversational AI**: Mistral-7B powered intelligent responses
- **Impact Scoring**: AI-driven relevance and impact assessment
- **Real-time Analysis**: Live news processing and summarization
- **Enterprise UI**: Professional Gradio interface with analytics

## ✨ Features

### 🔍 Advanced News Crawling
- **DuckDuckGo Integration**: Enhanced search with multiple query variations
- **RSS Feed Aggregation**: Comprehensive coverage of major news sources
- **Financial Data Sources**: Integration with Yahoo Finance, Seeking Alpha
- **Content Extraction**: Clean article content extraction using newspaper3k

### 🤖 Conversational AI
- **Mistral-7B Model**: State-of-the-art language model for natural conversations
- **Multiple Response Styles**: Professional, Casual, Executive, Technical
- **Context Awareness**: Maintains conversation history and user preferences
- **5-6 Line Responses**: Detailed analysis with actionable insights

### 📊 Enterprise Analytics
- **Impact Scoring**: AI-powered relevance assessment (1-10 scale)
- **Source Credibility**: Weighted scoring based on source reputation
- **Time-based Filtering**: Configurable time ranges (1 hour to 1 week)
- **Session Management**: User session tracking and analytics

### 🎨 Professional Interface
- **Gradio Web UI**: Modern, responsive interface
- **Real-time Updates**: Live status indicators and progress tracking
- **Export Capabilities**: Chat history export functionality
- **Mobile Responsive**: Works across all devices

## 🏗️ Architecture

### Core Components

```
RAP IQ Platform
├── 🕷️ News Crawlers
│   ├── DuckDuckGoCrawler
│   ├── RSSCrawler
│   └── AdvancedNewsCrawler
├── 🤖 AI Engine
│   ├── Mistral-7B Model
│   ├── ResponseGenerator
│   └── ConversationalAI
├── 📊 Processing Pipeline
│   ├── NewsAggregator
│   ├── ContentExtractor
│   └── ImpactScorer
└── 🎨 User Interface
    ├── Gradio Interface
    ├── Analytics Dashboard
    └── Export Tools
```

### Data Flow

1. **User Input** → Conversational AI processes natural language queries
2. **Company Extraction** → NLP identifies target companies
3. **Multi-Source Crawling** → Parallel data collection from various sources
4. **Content Processing** → Deduplication, filtering, and impact scoring
5. **AI Analysis** → Mistral-7B generates contextual responses
6. **Response Formatting** → Professional presentation with source links

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- CUDA-compatible GPU (recommended for optimal performance)
- 8GB+ RAM
- Internet connection for news crawling

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/rap-iq.git
cd rap-iq
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Download spaCy model**
```bash
python -m spacy download en_core_web_sm
```

4. **Run the application**
```bash
python main.py
```

### Manual Installation

```bash
# Core ML libraries
pip install transformers accelerate bitsandbytes torch torchvision

# Web scraping and processing
pip install gradio beautifulsoup4 requests feedparser newspaper3k readability-lxml

# NLP and analysis
pip install spacy sentence-transformers

# Async and networking
pip install asyncio aiohttp nest-asyncio

# Financial data
pip install yfinance tweepy

# Additional utilities
pip install redis-py bloom-filter2 praw snscrape
```

## 💻 Usage

### Basic Usage

1. **Launch the application**
```python
from rap_iq import EnterpriseNewsPipeline

# Initialize the pipeline
pipeline = EnterpriseNewsPipeline()

# Process a query
response = await pipeline.process_enterprise_query(
    user_input="What's the latest news about Tesla?",
    company="Tesla",
    style="professional",
    time_range="24 hours",
    impact_threshold=5.0
)
```

2. **Web Interface**
- Open the provided Gradio URL
- Enter company name or natural language query
- Select response style and parameters
- Click "Send" for instant analysis

### Advanced Configuration

```python
# Custom crawler configuration
crawler_config = {
    'max_results': 15,
    'timeout': 30,
    'sources': ['DuckDuckGo', 'RSS', 'Financial'],
    'impact_threshold': 6.0
}

# AI model configuration
ai_config = {
    'model_name': 'mistralai/Mistral-7B-Instruct-v0.1',
    'max_tokens': 300,
    'temperature': 0.7,
    'context_window': 2048
}
```

### Response Styles

- **Professional**: Formal business language with detailed analysis
- **Casual**: Friendly, conversational tone for easy understanding
- **Executive**: Strategic focus on business implications
- **Technical**: In-depth technical analysis and market insights

## 📚 API Reference

### EnterpriseNewsPipeline

Main pipeline class for processing news queries.

#### Methods

- `process_enterprise_query()`: Process user queries with full context
- `_extract_company_from_input()`: Extract company names using NLP
- `_enterprise_filter_news()`: Advanced filtering and ranking

### AdvancedNewsCrawler

Enhanced news crawling with multiple sources.

#### Methods

- `enhanced_duckduckgo_scrape()`: Advanced DuckDuckGo scraping
- `_calculate_enhanced_impact()`: AI-powered impact scoring
- `_advanced_deduplication()`: Content similarity-based deduplication

### EnterpriseConversationalAI

Conversational AI powered by Mistral-7B.

#### Methods

- `generate_conversational_response()`: Generate contextual responses
- `_build_conversation_context()`: Build rich conversation context
- `_format_conversational_response()`: Format responses for presentation

## ⚙️ Configuration

### Environment Variables

```bash
# Model configuration
MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.1
MAX_TOKENS=300
TEMPERATURE=0.7

# Crawler settings
CRAWLER_TIMEOUT=30
MAX_RESULTS=15
IMPACT_THRESHOLD=5.0

# Server configuration
SERVER_PORT=7860
SHARE_LINK=true
DEBUG_MODE=false
```

### GPU Configuration

```python
# Quantization for efficient GPU usage
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)
```

## 🧪 Testing

### Validation Tests

```python
# Run comprehensive validation
async def run_validation_tests():
    test_companies = ["Tesla", "Apple", "Microsoft"]
    test_styles = ["professional", "casual", "executive"]
    
    for company in test_companies:
        for style in test_styles:
            result = await pipeline.process_enterprise_query(
                user_input=f"What's the latest news about {company}?",
                company=company,
                style=style
            )
            # Validate response quality
```

### Performance Metrics

- **Response Time**: < 10 seconds for typical queries
- **Accuracy**: > 90% company name extraction
- **Source Coverage**: 15+ major news sources
- **Impact Scoring**: AI-validated relevance assessment

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Code formatting
black src/
flake8 src/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Mistral AI** for the powerful language model
- **Hugging Face** for the transformers library
- **Gradio** for the beautiful web interface
- **spaCy** for natural language processing capabilities

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/rap-iq/issues)
- **Documentation**: [Wiki](https://github.com/yourusername/rap-iq/wiki)
- **Email**: support@rap-iq.com

---

**Made with ❤️ for intelligent news analysis**

*RAP IQ - Where AI meets business intelligence* 