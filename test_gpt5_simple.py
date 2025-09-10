#!/usr/bin/env python3
"""
Simple test to verify GPT-5 has been added to the code.
"""

def test_python_service():
    """Test GPT-5 in Python service file"""
    with open('services/gpt_service.py', 'r') as f:
        content = f.read()
        assert 'GPT_5 = "gpt-5"' in content, "GPT_5 should be in Python GPTModels enum"
        assert '"gpt-5"' in content, "gpt-5 should be in gpt_models mapping"
    print("✅ Python service test passed")

def test_javascript_service():
    """Test GPT-5 in JavaScript service file"""
    with open('js/src/services/gpt_service.js', 'r') as f:
        content = f.read()
        assert "GPT_5: 'gpt-5'" in content, "GPT_5 should be in JavaScript GPTModels"
        assert "[GPTModels.GPT_5]: 'gpt-5'" in content, "GPT_5 should be in gptModelsMap"
    print("✅ JavaScript service test passed")

def test_python_router():
    """Test GPT-5 pricing in Python router"""
    with open('bot/gpt/router.py', 'r') as f:
        content = f.read()
        assert '*GPT-5:* 1000 токенов = 10000 ⚡️' in content, "GPT-5 pricing should be in router"
        assert 'if "gpt-5" in model:' in content, "GPT-5 detection should be in detect_model function"
    print("✅ Python router test passed")

def main():
    print("🧪 Testing GPT-5 integration (simple)...\n")
    
    test_python_service()
    test_javascript_service()
    test_python_router()
    
    print("\n🎉 All simple tests passed! GPT-5 has been successfully added to the codebase.")

if __name__ == "__main__":
    main()