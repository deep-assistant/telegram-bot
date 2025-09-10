import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from services.video_service import VideoService

class TestVideoService(unittest.TestCase):
    
    def setUp(self):
        self.video_service = VideoService()
        self.test_user_id = "123456"
        
    def test_store_user_data(self):
        """Test storing user data"""
        self.video_service.store_user_data(self.test_user_id, prompt="test prompt", style="realistic")
        user_data = self.video_service.get_user_data(self.test_user_id)
        
        self.assertEqual(user_data['prompt'], "test prompt")
        self.assertEqual(user_data['style'], "realistic")
        
    def test_get_user_data_empty(self):
        """Test getting user data when no data exists"""
        user_data = self.video_service.get_user_data("nonexistent_user")
        self.assertEqual(user_data, {})
        
    def test_clear_user_data(self):
        """Test clearing user data"""
        self.video_service.store_user_data(self.test_user_id, prompt="test")
        self.video_service.clear_user_data(self.test_user_id)
        user_data = self.video_service.get_user_data(self.test_user_id)
        
        self.assertEqual(user_data, {})
        
    def test_enhance_prompt(self):
        """Test prompt enhancement"""
        test_prompt = "A cat playing with a ball"
        
        enhanced_realistic = self.video_service._enhance_prompt(test_prompt, "realistic")
        self.assertIn("photorealistic", enhanced_realistic)
        self.assertIn(test_prompt, enhanced_realistic)
        
        enhanced_cartoon = self.video_service._enhance_prompt(test_prompt, "cartoon")
        self.assertIn("cartoon style", enhanced_cartoon)
        self.assertIn(test_prompt, enhanced_cartoon)
        
        enhanced_anime = self.video_service._enhance_prompt(test_prompt, "anime")
        self.assertIn("anime style", enhanced_anime)
        self.assertIn(test_prompt, enhanced_anime)

async def run_async_tests():
    """Run async tests"""
    video_service = VideoService()
    
    # Test that generate_video returns empty dict on API error
    with patch('services.video_service.async_post') as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {"error": "API Error"}
        mock_post.return_value = mock_response
        
        result = await video_service.generate_video("test prompt", "realistic")
        assert result == {}
        
    print("Async tests passed!")

if __name__ == "__main__":
    # Run sync tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run async tests
    asyncio.run(run_async_tests())
    
    print("All tests completed!")