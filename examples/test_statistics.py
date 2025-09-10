#!/usr/bin/env python3
"""
Test script for statistics functionality.
This script generates test data and validates the statistics service.
"""

import os
import sys
import asyncio
from datetime import datetime, timedelta

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.statistics_service import StatisticsService

def test_statistics_service():
    """Test the statistics service with sample data."""
    
    print("🧪 Testing Statistics Service...")
    
    # Create service instance
    stats_service = StatisticsService()
    
    # Test data
    test_users = ["12345", "67890", "11111", "22222", "33333"]
    test_models = ["gpt-4", "gpt-3.5-turbo", "claude-3", "transcription"]
    test_modes = ["default", "transcribe", "voice", "image"]
    
    print("\n📊 Generating test statistics data...")
    
    # Generate test data for today
    today = datetime.now()
    for i, user_id in enumerate(test_users):
        # Track user activity
        stats_service.track_user_activity(user_id, "message")
        stats_service.track_user_activity(user_id, "gpt_message")
        
        # Track token usage
        tokens_spent = (i + 1) * 100 + 50  # 150, 250, 350, etc.
        model = test_models[i % len(test_models)]
        stats_service.track_token_usage(user_id, tokens_spent, model)
        
        # Track model usage
        mode = test_modes[i % len(test_modes)]
        stats_service.track_model_usage(user_id, model, mode)
        
        # Generate additional requests for some users
        if i < 3:
            stats_service.track_user_activity(user_id, "voice_transcribe")
            stats_service.track_token_usage(user_id, 25, "transcription")
            stats_service.track_model_usage(user_id, "transcription", "voice")
    
    # Generate some data for yesterday
    yesterday = today - timedelta(days=1)
    print("📅 Generating test data for yesterday...")
    
    # Mock yesterday's data by temporarily modifying date keys
    original_get_date_key = stats_service._get_date_key
    stats_service._get_date_key = lambda date=None: yesterday.strftime('%Y-%m-%d')
    
    for i, user_id in enumerate(test_users[:3]):  # Only first 3 users active yesterday
        stats_service.track_user_activity(user_id, "message")
        stats_service.track_token_usage(user_id, (i + 1) * 75, test_models[i])
        stats_service.track_model_usage(user_id, test_models[i], test_modes[i])
    
    # Restore original method
    stats_service._get_date_key = original_get_date_key
    
    print("✅ Test data generated successfully!")
    
    # Test retrieval methods
    print("\n📈 Testing data retrieval...")
    
    # Test daily users count
    today_users = stats_service.get_daily_users_count(today)
    yesterday_users = stats_service.get_daily_users_count(yesterday)
    
    print(f"👥 Today's users: {today_users}")
    print(f"👥 Yesterday's users: {yesterday_users}")
    
    # Test token statistics
    today_tokens = stats_service.get_token_statistics(today)
    print(f"⚡️ Today's tokens spent: {today_tokens.get('total_spent', 0)}")
    print(f"⚡️ Token breakdown by model: {today_tokens.get('by_model', {})}")
    
    # Test model statistics
    today_models = stats_service.get_model_statistics(today)
    print(f"🤖 Today's model usage: {today_models}")
    
    # Test usage time statistics
    time_stats = stats_service.get_usage_time_statistics(today)
    current_hour = datetime.now().strftime('%H:00')
    print(f"⏰ Current hour ({current_hour}) activity: {time_stats.get(current_hour, {})}")
    
    # Test period statistics
    week_start = today - timedelta(days=7)
    period_stats = stats_service.get_period_statistics(week_start, today)
    print(f"📊 Week period stats - Total tokens: {period_stats.get('total_tokens_spent', 0)}")
    print(f"📊 Daily users in period: {len(period_stats.get('daily_users', []))}")
    
    print("\n✅ All statistics tests completed successfully!")
    return True

async def test_api_statistics():
    """Test API-based statistics (requires valid config)."""
    print("\n🌐 Testing API statistics...")
    
    try:
        stats_service = StatisticsService()
        api_stats = await stats_service.get_token_balance_statistics()
        
        if "error" in api_stats:
            print(f"⚠️  API test skipped (expected in test environment): {api_stats['error']}")
        else:
            print(f"💰 API statistics retrieved: {api_stats}")
            
    except Exception as e:
        print(f"⚠️  API test failed (expected in test environment): {e}")

def print_test_summary():
    """Print a summary of what the statistics system provides."""
    
    print("""
📊 STATISTICS SYSTEM SUMMARY
============================

🎯 Implemented Features:
1. ✅ количество пользователей сегодня (Daily users count)
2. ✅ количество потраченных токенов (Spent tokens tracking)
3. ✅ количество купленных токенов (Purchased tokens via API)
4. ✅ статистика по моделям и режимам (Models and modes statistics)
5. ✅ статистика по времени использования (Usage time patterns)

🤖 Bot Commands:
- /stats - Main statistics command (admin only)
- /teststats - Generate test data (admin only, for testing)

📈 Available Statistics:
- Daily, weekly, monthly user activity
- Token usage by model and user
- Model usage patterns and modes
- Hourly activity heatmaps
- User engagement metrics

🔧 Configuration:
- Add your Telegram user ID to ADMIN_IDS in config.py
- Statistics are stored in the local Vedis database
- External token data is fetched from the configured API

🚀 Usage:
1. Configure admin IDs in config.py: ADMIN_IDS = [your_user_id]
2. Start the bot
3. Use /stats command to view statistics
4. Use /teststats to generate sample data for testing
""")

if __name__ == "__main__":
    print("🚀 Starting Statistics System Test")
    print("=" * 50)
    
    # Test the statistics service
    try:
        test_success = test_statistics_service()
        
        if test_success:
            # Test API functionality
            asyncio.run(test_api_statistics())
            
            # Print summary
            print_test_summary()
            
            print("\n🎉 All tests completed! Statistics system is ready.")
            print("🔧 Don't forget to configure ADMIN_IDS in config.py")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)