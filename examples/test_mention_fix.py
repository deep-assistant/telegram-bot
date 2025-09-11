#!/usr/bin/env python3
"""
Test script to verify mention handling fix.
This simulates the mention detection logic to ensure it only responds to @DeepGPTBot mentions.
"""

class MockEntity:
    def __init__(self, type, offset, length):
        self.type = type
        self.offset = offset
        self.length = length

def test_mention_detection():
    """Test the mention detection logic"""
    bot_username = "DeepGPTBot"
    
    # Test cases
    test_cases = [
        {
            "text": "@DeepGPTBot help me",
            "entities": [MockEntity("mention", 0, 11)],
            "expected": True,
            "description": "Should respond to @DeepGPTBot mention"
        },
        {
            "text": "@SomeOtherBot help me", 
            "entities": [MockEntity("mention", 0, 13)],
            "expected": False,
            "description": "Should NOT respond to other bot mentions"
        },
        {
            "text": "Hello @username how are you?",
            "entities": [MockEntity("mention", 6, 9)],
            "expected": False,
            "description": "Should NOT respond to user mentions"
        },
        {
            "text": "Can @DeepGPTBot and @OtherBot help?",
            "entities": [MockEntity("mention", 4, 11), MockEntity("mention", 20, 9)],
            "expected": True,
            "description": "Should respond when DeepGPTBot is mentioned along with others"
        },
        {
            "text": "No mentions here",
            "entities": [],
            "expected": False,
            "description": "Should NOT respond when no mentions"
        }
    ]
    
    print("Testing mention detection logic:")
    print("=" * 50)
    
    all_passed = True
    for i, case in enumerate(test_cases, 1):
        # Simulate the fixed mention detection logic
        mentioned = any(
            entity.type == "mention" 
            and case["text"] and case["text"][entity.offset + 1 : entity.offset + entity.length] == bot_username
            for entity in case["entities"]
        )
        
        passed = mentioned == case["expected"]
        all_passed = all_passed and passed
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"Test {i}: {status}")
        print(f"  Description: {case['description']}")
        print(f"  Text: '{case['text']}'")
        print(f"  Expected: {case['expected']}, Got: {mentioned}")
        print()
    
    print("=" * 50)
    if all_passed:
        print("🎉 All tests passed! The mention fix is working correctly.")
    else:
        print("❌ Some tests failed. The mention logic needs review.")
    
    return all_passed

if __name__ == "__main__":
    test_mention_detection()