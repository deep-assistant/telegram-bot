#!/usr/bin/env python3
"""
Test script for Suno error handling functionality.
Tests the human-readable error message generation for various API error scenarios.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.suno_service import SunoService

def test_moderation_failure_error():
    """Test the moderation failure error case from the GitHub issue."""
    suno_service = SunoService()
    
    # Test case from the actual issue
    error_data = {
        "code": 10000,
        "raw_message": "clips generation failed: moderation_failure; Unable to generate lyrics from song description",
        "message": "clips generation failed",
        "detail": None
    }
    
    result = suno_service.get_human_readable_error(error_data)
    print("=== Test: Moderation Failure Error ===")
    print("Input error:", error_data)
    print("Human-readable output:")
    print(result)
    print()
    
    # Verify it contains the expected elements
    assert "ограничений контента" in result
    assert "без вокала" in result
    assert "изменить описание" in result
    print("✅ Test passed: Contains expected content moderation guidance")

def test_generic_clips_generation_failed():
    """Test generic clips generation failed error."""
    suno_service = SunoService()
    
    error_data = {
        "message": "clips generation failed: unknown_error",
    }
    
    result = suno_service.get_human_readable_error(error_data)
    print("=== Test: Generic Clips Generation Failed ===")
    print("Input error:", error_data)
    print("Human-readable output:")
    print(result)
    print()
    
    assert "Не удалось создать музыкальную композицию" in result
    assert "сервиса Suno" in result
    print("✅ Test passed: Contains expected generic error guidance")

def test_unknown_error():
    """Test handling of unknown error."""
    suno_service = SunoService()
    
    error_data = {
        "message": "Some unknown API error occurred",
    }
    
    result = suno_service.get_human_readable_error(error_data)
    print("=== Test: Unknown Error ===")
    print("Input error:", error_data)
    print("Human-readable output:")
    print(result)
    print()
    
    assert "Произошла ошибка при генерации музыки" in result
    assert "Some unknown API error occurred" in result
    print("✅ Test passed: Contains error message and generic guidance")

def test_empty_error():
    """Test handling of empty error data."""
    suno_service = SunoService()
    
    result = suno_service.get_human_readable_error(None)
    print("=== Test: Empty Error Data ===")
    print("Input error: None")
    print("Human-readable output:")
    print(result)
    print()
    
    assert "неизвестная ошибка" in result
    print("✅ Test passed: Handles None error data gracefully")

if __name__ == "__main__":
    print("Testing Suno Error Handling Implementation")
    print("=" * 50)
    print()
    
    try:
        test_moderation_failure_error()
        test_generic_clips_generation_failed()
        test_unknown_error()
        test_empty_error()
        
        print("=" * 50)
        print("🎉 All tests passed! The error handling implementation works correctly.")
        print()
        print("Summary of improvements:")
        print("• Moderation failures now show specific guidance about content restrictions")
        print("• Generic generation failures provide clear troubleshooting steps") 
        print("• Unknown errors display the original error message with helpful context")
        print("• Empty error data is handled gracefully")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)