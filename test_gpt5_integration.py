#!/usr/bin/env python3
"""
Test script to verify GPT-5 integration is working correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.gpt_service import GPTModels, gpt_models
from bot.gpt.router import detect_model

def test_gpt5_enum():
    """Test that GPT-5 is in the GPTModels enum"""
    print("Testing GPT-5 in GPTModels enum...")
    assert hasattr(GPTModels, 'GPT_5'), "GPT_5 should be in GPTModels enum"
    assert GPTModels.GPT_5.value == "gpt-5", f"Expected 'gpt-5', got {GPTModels.GPT_5.value}"
    print("✅ GPT-5 enum test passed")

def test_gpt5_mapping():
    """Test that GPT-5 is in the gpt_models mapping"""
    print("Testing GPT-5 in gpt_models mapping...")
    assert GPTModels.GPT_5.value in gpt_models, "GPT-5 should be in gpt_models mapping"
    assert gpt_models[GPTModels.GPT_5.value] == "gpt-5", f"Expected 'gpt-5', got {gpt_models[GPTModels.GPT_5.value]}"
    print("✅ GPT-5 mapping test passed")

def test_detect_model():
    """Test that detect_model function correctly identifies GPT-5"""
    print("Testing detect_model function...")
    result = detect_model("gpt-5")
    assert result == "gpt-5", f"Expected 'gpt-5', got {result}"
    
    result = detect_model("gpt-5-turbo")
    assert result == "gpt-5", f"Expected 'gpt-5', got {result}"
    print("✅ detect_model test passed")

def main():
    print("🧪 Testing GPT-5 integration...\n")
    
    test_gpt5_enum()
    test_gpt5_mapping()
    test_detect_model()
    
    print("\n🎉 All tests passed! GPT-5 integration is working correctly.")

if __name__ == "__main__":
    main()