"""
Test script for the context notification feature
"""
import sys
import os
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock the config module for testing
import types
config = types.ModuleType('config')
config.TOKEN = "test_token"
config.ANALYTICS_URL = "https://test.com"
config.PROXY_URL = "https://test.com"
config.ADMIN_TOKEN = "test_admin"
config.KEY_DEEPINFRA = "test_key"
config.IS_DEV = True
config.PAYMENTS_TOKEN = "test_payments"
config.GO_API_KEY = "test_go"
config.GUO_GUO_KEY = "test_guo"
config.OPENROUTER_API_KEY = "test_openrouter"
config.WEBHOOK_ENABLED = False
config.WEBHOOK_URL = "https://test.com/webhook"
config.WEBHOOK_PATH = "/webhook"
config.WEBHOOK_HOST = "0.0.0.0"
config.WEBHOOK_PORT = 3000
config.HTTPX_DISABLE_SSL_VERIFY = False

sys.modules['config'] = config

def test_context_service():
    """Test the context service functionality"""
    print("Testing ContextService...")
    
    try:
        from services.context_service import ContextService
        
        # Create a test instance
        context_service = ContextService()
        test_user_id = "test_user_123"
        
        print("✓ ContextService imported successfully")
        
        # Test updating last interaction
        context_service.update_last_interaction(test_user_id)
        print("✓ update_last_interaction works")
        
        # Test getting last interaction
        last_interaction = context_service.get_last_interaction(test_user_id)
        assert last_interaction is not None, "Last interaction should not be None"
        print(f"✓ get_last_interaction works: {last_interaction}")
        
        # Test notification logic for recent interaction (should be False)
        should_notify = context_service.should_show_context_notification(test_user_id)
        assert should_notify == False, "Should not notify for recent interaction"
        print("✓ should_show_context_notification works for recent interaction")
        
        # Test notification logic for old interaction
        # Manually set an old timestamp
        old_time = datetime.now() - timedelta(hours=25)
        from db import data_base, db_key
        with data_base.transaction():
            data_base[db_key(test_user_id, context_service.LAST_INTERACTION_DATE)] = old_time.isoformat()
        data_base.commit()
        
        should_notify = context_service.should_show_context_notification(test_user_id)
        assert should_notify == True, "Should notify for old interaction"
        print("✓ should_show_context_notification works for old interaction")
        
        # Test notification sent flag
        context_service.set_notification_sent(test_user_id)
        is_sent = context_service.is_notification_sent(test_user_id)
        assert is_sent == True, "Notification sent flag should be True"
        print("✓ notification sent flag works")
        
        # Test notification logic after flag is set (should be False)
        should_notify = context_service.should_show_context_notification(test_user_id)
        assert should_notify == False, "Should not notify after flag is set"
        print("✓ should_show_context_notification respects notification flag")
        
        # Test reset notification
        context_service.reset_notification_sent(test_user_id)
        is_sent = context_service.is_notification_sent(test_user_id)
        assert is_sent == False, "Notification sent flag should be False after reset"
        print("✓ reset_notification_sent works")
        
        print("\n🎉 All ContextService tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ ContextService test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_middleware_import():
    """Test that the middleware can be imported"""
    print("\nTesting ContextMiddleware import...")
    
    try:
        from bot.middlewares.ContextMiddleware import ContextMiddleware
        print("✓ ContextMiddleware imported successfully")
        
        # Test basic instantiation
        middleware = ContextMiddleware()
        print("✓ ContextMiddleware instantiation works")
        
        print("\n🎉 ContextMiddleware import test passed!")
        return True
        
    except Exception as e:
        print(f"❌ ContextMiddleware import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Testing Context Notification Feature")
    print("=" * 50)
    
    success = True
    success &= test_context_service()
    success &= test_middleware_import()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("The context notification feature is ready for deployment.")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please check the errors above.")
    print("=" * 50)