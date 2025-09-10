#!/usr/bin/env python3
"""
Basic import test for new functionality
"""

import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test if we can import the new commands"""
    try:
        from bot.commands import (
            save_context_command, save_context_text,
            list_contexts_command, list_contexts_text,
            load_context_command, delete_context_command
        )
        
        print("✅ Successfully imported new context commands:")
        print(f"  - Save context: '{save_context_command()}' / '{save_context_text()}'")
        print(f"  - List contexts: '{list_contexts_command()}' / '{list_contexts_text()}'") 
        print(f"  - Load context: '{load_context_command()}'")
        print(f"  - Delete context: '{delete_context_command()}'")
        
        return True
    except Exception as e:
        print(f"❌ Failed to import commands: {e}")
        return False

def test_state_types():
    """Test if we can import the new state types"""
    try:
        from services.state_service import StateTypes
        
        # Check if ContextNaming exists
        context_naming = StateTypes.ContextNaming
        print(f"✅ Successfully imported StateTypes.ContextNaming: '{context_naming.value}'")
        
        return True
    except Exception as e:
        print(f"❌ Failed to import StateTypes: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running Import Tests")
    print("=" * 30)
    
    commands_ok = test_imports()
    state_ok = test_state_types()
    
    if commands_ok and state_ok:
        print("\n✅ All import tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some import tests failed!")
        sys.exit(1)