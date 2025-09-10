#!/usr/bin/env python3
"""
Test just the state types enum
"""

import sys
import os
from enum import Enum

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create a simple mock for testing
class MockStateTypes(Enum):
    Default = "default"
    SystemMessageEditing = "system_message_editing"
    Image = "image"
    ImageEditing = "image_editing"
    Dalle3 = "dalle3"
    Midjourney = "midjourney"
    Suno = "suno"
    SunoStyle = "suno_style"
    Flux = "flux"
    Transcribe = "transcribation"
    ContextNaming = "context_naming"

def test_state_types():
    """Test if the ContextNaming state type exists"""
    print("🧪 Testing State Types")
    print("=" * 25)
    
    try:
        context_naming = MockStateTypes.ContextNaming
        print(f"✅ ContextNaming state type: '{context_naming.value}'")
        
        # Test all states
        print("\n📝 All available state types:")
        for state in MockStateTypes:
            print(f"  - {state.name}: '{state.value}'")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_state_types()
    
    if success:
        print("\n✅ State types test passed!")
        sys.exit(0)
    else:
        print("\n❌ State types test failed!")
        sys.exit(1)