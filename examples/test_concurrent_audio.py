#!/usr/bin/env python3
"""
Test script for concurrent audio message handling.
This script tests the fix for issue #50 - Bot does not recognize multiple audio messages at the same time.
"""

import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.gpt.router import transcribe_voice


async def mock_transcribe_voice_sync(user_id: str, voice_file_url: str):
    """Mock the transcribe_voice_sync function to simulate processing time"""
    # Simulate processing time
    await asyncio.sleep(0.5)  # 500ms delay to simulate real processing
    return {
        "success": True, 
        "text": f"Transcribed audio for user {user_id} from {voice_file_url}", 
        "energy": 15
    }


async def test_concurrent_audio_processing():
    """Test that multiple audio messages can be processed concurrently"""
    print("🎤 Testing concurrent audio message handling...")
    
    # Mock the transcribe_voice_sync function
    with patch('bot.gpt.router.transcribe_voice_sync', side_effect=mock_transcribe_voice_sync):
        # Create multiple concurrent transcription tasks
        tasks = []
        start_time = time.time()
        
        # Simulate 5 concurrent audio messages
        for i in range(5):
            task = asyncio.create_task(
                transcribe_voice(f"user_{i}", f"http://example.com/audio_{i}.ogg")
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Analyze results
        total_time = end_time - start_time
        successful_results = [r for r in results if isinstance(r, dict) and r.get("success")]
        
        print(f"⏱️  Total processing time: {total_time:.2f} seconds")
        print(f"✅ Successfully processed: {len(successful_results)}/5 audio messages")
        print(f"🔧 Expected time for sequential processing: ~2.5 seconds")
        print(f"🚀 Actual time (concurrent): {total_time:.2f} seconds")
        
        # Assert that concurrent processing is faster than sequential
        if total_time < 2.0:  # Should be much faster than 2.5 seconds
            print("✅ PASS: Concurrent processing is working correctly!")
            return True
        else:
            print("❌ FAIL: Processing took too long, concurrent handling may not be working")
            return False


async def test_error_handling():
    """Test that errors in one audio message don't affect others"""
    print("\n🛡️  Testing error handling...")
    
    async def failing_transcribe_voice_sync(user_id: str, voice_file_url: str):
        if user_id == "user_error":
            raise Exception("Simulated transcription error")
        await asyncio.sleep(0.1)
        return {"success": True, "text": f"OK for {user_id}", "energy": 15}
    
    with patch('bot.gpt.router.transcribe_voice_sync', side_effect=failing_transcribe_voice_sync):
        tasks = [
            asyncio.create_task(transcribe_voice("user_ok_1", "audio1.ogg")),
            asyncio.create_task(transcribe_voice("user_error", "audio2.ogg")),
            asyncio.create_task(transcribe_voice("user_ok_2", "audio3.ogg")),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
        errors = sum(1 for r in results if isinstance(r, Exception))
        
        print(f"✅ Successful transcriptions: {successful}")
        print(f"❌ Failed transcriptions: {errors}")
        
        if successful >= 2 and errors <= 1:
            print("✅ PASS: Error handling works correctly!")
            return True
        else:
            print("❌ FAIL: Error handling is not working as expected")
            return False


async def main():
    """Run all tests"""
    print("🚀 Starting concurrent audio processing tests...\n")
    
    test1_passed = await test_concurrent_audio_processing()
    test2_passed = await test_error_handling()
    
    print(f"\n📊 Test Results:")
    print(f"{'✅' if test1_passed else '❌'} Concurrent processing test")
    print(f"{'✅' if test2_passed else '❌'} Error handling test")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! The concurrent audio handling fix is working.")
        return 0
    else:
        print("\n❌ Some tests failed. Please review the implementation.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)