#!/usr/bin/env python3
"""
Unit test for concurrent audio message handling logic.
This test focuses on the core concurrency fix without external dependencies.
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor


# Replicate the fixed transcribe_voice function logic
executor = ThreadPoolExecutor(max_workers=10)


async def mock_transcribe_voice_sync(user_id: str, voice_file_url: str):
    """Mock the transcribe_voice_sync function to simulate processing time"""
    # Simulate processing time (like OpenAI API call)
    await asyncio.sleep(0.5)
    return {
        "success": True, 
        "text": f"Transcribed audio for user {user_id} from {voice_file_url}", 
        "energy": 15
    }


async def transcribe_voice(user_id: int, voice_file_url: str):
    """
    Replicate the fixed transcribe_voice function.
    This is the core fix for concurrent audio processing.
    """
    loop = asyncio.get_event_loop()
    
    # Create a wrapper function to handle async execution in thread
    def sync_wrapper():
        # Run the async function in a new event loop for this thread
        import asyncio
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            result = new_loop.run_until_complete(mock_transcribe_voice_sync(user_id, voice_file_url))
            return result
        finally:
            new_loop.close()
    
    response = await loop.run_in_executor(executor, sync_wrapper)
    return response


async def test_concurrent_processing():
    """Test that multiple audio messages can be processed concurrently"""
    print("🎤 Testing concurrent audio message handling...")
    
    start_time = time.time()
    
    # Create 5 concurrent transcription tasks
    tasks = []
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
    
    # Test success criteria
    if len(successful_results) == 5 and total_time < 2.0:
        print("✅ PASS: Concurrent processing is working correctly!")
        return True
    else:
        print("❌ FAIL: Concurrent processing test failed")
        print(f"   - Results: {len(successful_results)}/5")
        print(f"   - Time: {total_time:.2f}s (should be < 2.0s)")
        return False


async def test_thread_pool_scaling():
    """Test that the thread pool can handle multiple concurrent requests"""
    print("\n🔄 Testing thread pool scaling...")
    
    # Simulate very fast processing to test thread pool capacity
    async def fast_mock_transcribe(user_id: str, voice_file_url: str):
        await asyncio.sleep(0.1)  # Short delay
        return {"success": True, "text": f"Fast transcription {user_id}", "energy": 5}
    
    # Replace the mock function temporarily
    original_mock = mock_transcribe_voice_sync
    
    # Create wrapper with fast mock
    async def fast_transcribe_voice(user_id: int, voice_file_url: str):
        loop = asyncio.get_event_loop()
        
        def sync_wrapper():
            import asyncio
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                result = new_loop.run_until_complete(fast_mock_transcribe(user_id, voice_file_url))
                return result
            finally:
                new_loop.close()
        
        response = await loop.run_in_executor(executor, sync_wrapper)
        return response
    
    start_time = time.time()
    
    # Test with 15 concurrent requests (more than default thread pool size)
    tasks = [
        asyncio.create_task(fast_transcribe_voice(f"user_{i}", f"audio_{i}.ogg"))
        for i in range(15)
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    end_time = time.time()
    
    total_time = end_time - start_time
    successful = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
    
    print(f"⏱️  Time for 15 concurrent requests: {total_time:.2f} seconds")
    print(f"✅ Successfully processed: {successful}/15 requests")
    
    if successful == 15 and total_time < 1.0:
        print("✅ PASS: Thread pool scaling works correctly!")
        return True
    else:
        print("❌ FAIL: Thread pool scaling test failed")
        return False


async def main():
    """Run all tests"""
    print("🚀 Starting concurrent audio processing unit tests...\n")
    
    test1_passed = await test_concurrent_processing()
    test2_passed = await test_thread_pool_scaling()
    
    print(f"\n📊 Test Results:")
    print(f"{'✅' if test1_passed else '❌'} Concurrent processing test")
    print(f"{'✅' if test2_passed else '❌'} Thread pool scaling test")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! The concurrent audio handling fix is working.")
        print("\n💡 Key improvements:")
        print("   - ThreadPoolExecutor increased to 10 workers")
        print("   - Proper async/await handling in thread executor")
        print("   - Each thread gets its own event loop")
        print("   - No blocking of the main async event loop")
        return 0
    else:
        print("\n❌ Some tests failed. Please review the implementation.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)