#!/usr/bin/env python3
"""
Main entry point for RAP IQ - AI News Intelligence Platform

This script initializes and launches the enterprise news intelligence platform.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.models import model_manager
from src.interface import interface
from src.utils import setup_logging, print_system_status, validate_environment


async def main():
    """Main application entry point."""
    
    print("🚀 Starting RAP IQ - AI News Intelligence Platform...")
    
    # Setup logging
    logger = setup_logging()
    logger.info("Application starting...")
    
    # Print system status
    print_system_status()
    
    # Validate environment
    validation = validate_environment()
    
    if validation["missing_packages"]:
        print(f"❌ Missing packages: {', '.join(validation['missing_packages'])}")
        print("Please install missing packages: pip install -r requirements.txt")
        return False
    
    if not validation["spacy_model"]:
        print("❌ spaCy model not found")
        print("Please install spaCy model: python -m spacy download en_core_web_sm")
        return False
    
    # Load models
    print("🔄 Loading AI models...")
    if not model_manager.load_models():
        print("❌ Failed to load models")
        return False
    
    # Print model info
    model_info = model_manager.get_model_info()
    print(f"✅ Models loaded successfully!")
    print(f"   Device: {model_info['device']}")
    print(f"   Model: {model_info['model_name']}")
    print(f"   Parameters: {model_info.get('model_parameters', 'Unknown'):,}")
    
    # Launch interface
    print("🎨 Launching web interface...")
    interface.launch()
    
    return True


def run_tests():
    """Run validation tests."""
    
    print("🧪 Running validation tests...")
    
    async def test_pipeline():
        """Test the news pipeline."""
        from src.pipeline import EnterpriseNewsPipeline
        
        pipeline = EnterpriseNewsPipeline()
        
        test_cases = [
            ("Tesla", "professional"),
            ("Apple", "casual"),
            ("Microsoft", "executive")
        ]
        
        success_count = 0
        
        for company, style in test_cases:
            try:
                result = await pipeline.process_enterprise_query(
                    user_input=f"What's the latest news about {company}?",
                    company=company,
                    style=style,
                    time_range="24 hours",
                    impact_threshold=4.0
                )
                
                # Validate response quality
                is_valid = (
                    len(result) > 200 and  # Substantial response
                    company.lower() in result.lower() and
                    "source" in result.lower() and
                    not result.startswith("❌")
                )
                
                if is_valid:
                    success_count += 1
                    print(f"✅ {company} ({style}): PASS")
                else:
                    print(f"⚠️ {company} ({style}): Response too short or missing elements")
            
            except Exception as e:
                print(f"❌ {company} ({style}): ERROR - {e}")
        
        print(f"\n📊 Test Results: {success_count}/{len(test_cases)} passed")
        
        if success_count == len(test_cases):
            print("🎉 ALL TESTS PASSED! System is enterprise-ready!")
            return True
        else:
            print("⚠️ Some tests failed, but system should still work")
            return False
    
    # Run tests
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(test_pipeline())
    loop.close()
    
    return result


if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            # Run tests
            success = run_tests()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == "status":
            # Show system status
            print_system_status()
            sys.exit(0)
        elif sys.argv[1] == "help":
            # Show help
            print("""
RAP IQ - AI News Intelligence Platform

Usage:
    python main.py          # Launch the application
    python main.py test     # Run validation tests
    python main.py status   # Show system status
    python main.py help     # Show this help

Examples:
    python main.py
    python main.py test
    python main.py status
            """)
            sys.exit(0)
    
    # Run main application
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(main())
        loop.close()
        
        if not success:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Application error: {e}")
        sys.exit(1) 