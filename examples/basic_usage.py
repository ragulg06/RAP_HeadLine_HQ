#!/usr/bin/env python3
"""
Basic usage example for RAP IQ - AI News Intelligence Platform

This script demonstrates how to use the RAP IQ platform programmatically.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.pipeline import EnterpriseNewsPipeline
from src.models import model_manager
from src.utils import setup_logging, print_system_status


async def basic_news_query():
    """Demonstrate basic news query functionality."""
    
    print("🔍 Basic News Query Example")
    print("=" * 50)
    
    # Initialize the pipeline
    pipeline = EnterpriseNewsPipeline()
    
    # Example 1: Simple company news query
    print("\n1. Simple Company News Query:")
    print("-" * 30)
    
    result = await pipeline.process_enterprise_query(
        user_input="What's the latest news about Tesla?",
        company="Tesla",
        style="professional",
        time_range="24 hours",
        impact_threshold=5.0
    )
    
    print(f"Query: What's the latest news about Tesla?")
    print(f"Response: {result[:200]}...")
    
    # Example 2: Different response styles
    print("\n2. Different Response Styles:")
    print("-" * 30)
    
    styles = ["professional", "casual", "executive", "technical"]
    
    for style in styles:
        print(f"\nStyle: {style}")
        result = await pipeline.process_enterprise_query(
            user_input="Tell me about Apple's recent developments",
            company="Apple",
            style=style,
            time_range="6 hours",
            impact_threshold=4.0
        )
        print(f"Response: {result[:150]}...")


async def advanced_features():
    """Demonstrate advanced features."""
    
    print("\n🔧 Advanced Features Example")
    print("=" * 50)
    
    pipeline = EnterpriseNewsPipeline()
    
    # Example 3: Company name extraction
    print("\n3. Company Name Extraction:")
    print("-" * 30)
    
    queries = [
        "What's happening with Microsoft today?",
        "Give me the latest on Google's stock",
        "Tell me about Amazon's earnings"
    ]
    
    for query in queries:
        result = await pipeline.process_enterprise_query(
            user_input=query,
            company=None,  # Let the system extract company name
            style="professional",
            time_range="24 hours",
            impact_threshold=5.0
        )
        print(f"Query: {query}")
        print(f"Response: {result[:100]}...")
    
    # Example 4: Different time ranges
    print("\n4. Different Time Ranges:")
    print("-" * 30)
    
    time_ranges = ["1 hour", "6 hours", "24 hours"]
    
    for time_range in time_ranges:
        print(f"\nTime Range: {time_range}")
        result = await pipeline.process_enterprise_query(
            user_input="What's the latest on Tesla?",
            company="Tesla",
            style="professional",
            time_range=time_range,
            impact_threshold=5.0
        )
        print(f"Response: {result[:100]}...")


async def session_management():
    """Demonstrate session management features."""
    
    print("\n📊 Session Management Example")
    print("=" * 50)
    
    pipeline = EnterpriseNewsPipeline()
    session_id = "example_session_123"
    
    # Example 5: Session-based queries
    print("\n5. Session-Based Queries:")
    print("-" * 30)
    
    queries = [
        "What's the latest on Tesla?",
        "Tell me more about their recent developments",
        "What about their financial performance?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\nQuery {i}: {query}")
        
        result = await pipeline.process_enterprise_query(
            user_input=query,
            company="Tesla" if i == 1 else None,  # Only specify company in first query
            style="professional",
            time_range="24 hours",
            impact_threshold=5.0,
            session_id=session_id
        )
        
        print(f"Response: {result[:100]}...")
    
    # Get session data
    session_data = pipeline.get_session_data(session_id)
    print(f"\nSession Data: {session_data}")


async def error_handling():
    """Demonstrate error handling."""
    
    print("\n⚠️ Error Handling Example")
    print("=" * 50)
    
    pipeline = EnterpriseNewsPipeline()
    
    # Example 6: Invalid company name
    print("\n6. Invalid Company Name:")
    print("-" * 30)
    
    result = await pipeline.process_enterprise_query(
        user_input="What's the latest on NonexistentCompany123?",
        company="NonexistentCompany123",
        style="professional",
        time_range="24 hours",
        impact_threshold=5.0
    )
    
    print(f"Query: What's the latest on NonexistentCompany123?")
    print(f"Response: {result}")
    
    # Example 7: Empty query
    print("\n7. Empty Query:")
    print("-" * 30)
    
    result = await pipeline.process_enterprise_query(
        user_input="",
        company="Tesla",
        style="professional",
        time_range="24 hours",
        impact_threshold=5.0
    )
    
    print(f"Query: (empty)")
    print(f"Response: {result}")


async def performance_monitoring():
    """Demonstrate performance monitoring."""
    
    print("\n⚡ Performance Monitoring Example")
    print("=" * 50)
    
    pipeline = EnterpriseNewsPipeline()
    
    # Example 8: Performance tracking
    print("\n8. Performance Tracking:")
    print("-" * 30)
    
    import time
    
    start_time = time.time()
    
    result = await pipeline.process_enterprise_query(
        user_input="What's the latest on Microsoft?",
        company="Microsoft",
        style="professional",
        time_range="24 hours",
        impact_threshold=5.0,
        session_id="performance_test"
    )
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"Query: What's the latest on Microsoft?")
    print(f"Processing Time: {processing_time:.2f} seconds")
    print(f"Response Length: {len(result)} characters")
    print(f"Response: {result[:100]}...")


async def main():
    """Main function to run all examples."""
    
    print("🚀 RAP IQ - Basic Usage Examples")
    print("=" * 60)
    
    # Setup logging
    logger = setup_logging()
    
    # Print system status
    print_system_status()
    
    # Load models
    print("\n🔄 Loading AI models...")
    if not model_manager.load_models():
        print("❌ Failed to load models")
        return
    
    print("✅ Models loaded successfully!")
    
    try:
        # Run examples
        await basic_news_query()
        await advanced_features()
        await session_management()
        await error_handling()
        await performance_monitoring()
        
        print("\n🎉 All examples completed successfully!")
        print("💡 You can now use these patterns in your own applications.")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        logger.error(f"Example error: {e}")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main()) 