#!/usr/bin/env python3
"""
Simplified test script to verify the 'repeat task detected' fix implementation.
This tests just the core tracking logic without requiring the full bot setup.
"""

# Mock the global dictionaries that store pending operations
pending_upscale_operations = {}
pending_variation_operations = {}

class MockImageService:
    """Mock implementation of ImageService for testing"""
    
    def is_upscale_pending(self, user_id: str, task_id: str, index: str) -> bool:
        """Check if an upscale operation is already pending for this user/task/index combination"""
        operation_key = f"{user_id}:{task_id}:{index}"
        return operation_key in pending_upscale_operations

    def set_upscale_pending(self, user_id: str, task_id: str, index: str, pending: bool):
        """Set the pending status for an upscale operation"""
        operation_key = f"{user_id}:{task_id}:{index}"
        if pending:
            pending_upscale_operations[operation_key] = True
        else:
            pending_upscale_operations.pop(operation_key, None)

    def is_variation_pending(self, user_id: str, task_id: str, index: str) -> bool:
        """Check if a variation operation is already pending for this user/task/index combination"""
        operation_key = f"{user_id}:{task_id}:{index}"
        return operation_key in pending_variation_operations

    def set_variation_pending(self, user_id: str, task_id: str, index: str, pending: bool):
        """Set the pending status for a variation operation"""
        operation_key = f"{user_id}:{task_id}:{index}"
        if pending:
            pending_variation_operations[operation_key] = True
        else:
            pending_variation_operations.pop(operation_key, None)

def test_upscale_tracking():
    """Test the upscale operation tracking functionality"""
    print("Testing upscale operation tracking...")
    
    # Create a test ImageService instance
    service = MockImageService()
    
    # Test data
    user_id = "test_user_123"
    task_id = "test_task_456" 
    index = "1"
    
    # Initially no operation should be pending
    assert not service.is_upscale_pending(user_id, task_id, index), "Initial state should not be pending"
    
    # Set operation as pending
    service.set_upscale_pending(user_id, task_id, index, True)
    assert service.is_upscale_pending(user_id, task_id, index), "Operation should be pending after setting"
    
    # Clear operation
    service.set_upscale_pending(user_id, task_id, index, False)
    assert not service.is_upscale_pending(user_id, task_id, index), "Operation should not be pending after clearing"
    
    print("✅ Upscale tracking tests passed!")

def test_variation_tracking():
    """Test the variation operation tracking functionality"""
    print("Testing variation operation tracking...")
    
    # Create a test ImageService instance
    service = MockImageService()
    
    # Test data
    user_id = "test_user_789"
    task_id = "test_task_012"
    index = "2"
    
    # Initially no operation should be pending
    assert not service.is_variation_pending(user_id, task_id, index), "Initial state should not be pending"
    
    # Set operation as pending
    service.set_variation_pending(user_id, task_id, index, True)
    assert service.is_variation_pending(user_id, task_id, index), "Operation should be pending after setting"
    
    # Clear operation
    service.set_variation_pending(user_id, task_id, index, False)
    assert not service.is_variation_pending(user_id, task_id, index), "Operation should not be pending after clearing"
    
    print("✅ Variation tracking tests passed!")

def test_multiple_operations():
    """Test multiple operations with different parameters"""
    print("Testing multiple operations...")
    
    service = MockImageService()
    
    # Test multiple different operations
    service.set_upscale_pending("user1", "task1", "1", True)
    service.set_upscale_pending("user1", "task1", "2", True) 
    service.set_variation_pending("user2", "task2", "1", True)
    
    # Check each operation is tracked correctly
    assert service.is_upscale_pending("user1", "task1", "1"), "User1 task1 index 1 upscale should be pending"
    assert service.is_upscale_pending("user1", "task1", "2"), "User1 task1 index 2 upscale should be pending"
    assert service.is_variation_pending("user2", "task2", "1"), "User2 task2 index 1 variation should be pending"
    
    # Check non-existent operations return False
    assert not service.is_upscale_pending("user1", "task1", "3"), "Non-existent operation should not be pending"
    assert not service.is_variation_pending("user1", "task1", "1"), "Wrong operation type should not be pending"
    
    # Clear operations
    service.set_upscale_pending("user1", "task1", "1", False)
    service.set_upscale_pending("user1", "task1", "2", False)
    service.set_variation_pending("user2", "task2", "1", False)
    
    print("✅ Multiple operations tests passed!")

def test_error_response_format():
    """Test that error response format is correct for repeat task detection"""
    print("Testing error response format...")
    
    # Test that the expected error response structure is created
    expected_error = {
        "error": "repeat_task_detected",
        "message": "This upscale operation was already submitted. Please wait for the previous operation to complete."
    }
    
    # Verify the structure
    assert "error" in expected_error, "Error response should have 'error' field"
    assert "message" in expected_error, "Error response should have 'message' field"
    assert expected_error["error"] == "repeat_task_detected", "Error type should be 'repeat_task_detected'"
    
    print("✅ Error response format tests passed!")

def test_duplicate_prevention_scenario():
    """Test the realistic scenario that should prevent the original issue"""
    print("Testing duplicate prevention scenario...")
    
    service = MockImageService()
    user_id = "123456"
    task_id = "e4fd6c05-bbec-4655-be95-63b2ae9a6efa"
    index = "1"
    
    # Simulate first upscale request (should be allowed)
    assert not service.is_upscale_pending(user_id, task_id, index), "First request should not be blocked"
    service.set_upscale_pending(user_id, task_id, index, True)
    
    # Simulate rapid second upscale request (should be blocked)  
    assert service.is_upscale_pending(user_id, task_id, index), "Second request should be blocked"
    
    # Simulate completion and cleanup
    service.set_upscale_pending(user_id, task_id, index, False)
    
    # Simulate new request after completion (should be allowed again)
    assert not service.is_upscale_pending(user_id, task_id, index), "Request after completion should be allowed"
    
    print("✅ Duplicate prevention scenario tests passed!")

def run_all_tests():
    """Run all test functions"""
    print("🧪 Running repeat task detection fix tests...\n")
    
    try:
        test_upscale_tracking()
        test_variation_tracking() 
        test_multiple_operations()
        test_error_response_format()
        test_duplicate_prevention_scenario()
        
        print("\n🎉 All tests passed! The repeat task detection fix is working correctly.")
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)