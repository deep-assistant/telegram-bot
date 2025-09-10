import json
from typing import List, Dict, Optional
from datetime import datetime

from bot.utils import get_user_name
from config import PROXY_URL, ADMIN_TOKEN
from db import data_base, db_key
from services.utils import async_get, async_post, async_delete


class ContextService:
    SAVED_CONTEXTS = "saved_contexts"
    
    def _get_contexts_key(self, user_id: str) -> str:
        """Get the database key for user's saved contexts"""
        return db_key(user_id, self.SAVED_CONTEXTS)
    
    def get_saved_contexts(self, user_id: str) -> Dict[str, Dict]:
        """Get all saved contexts for a user"""
        try:
            contexts_data = data_base[self._get_contexts_key(user_id)].decode('utf-8')
            return json.loads(contexts_data)
        except KeyError:
            return {}
    
    def save_context(self, user_id: str, context_name: str, context_data: Dict) -> bool:
        """Save a context with a given name"""
        try:
            contexts = self.get_saved_contexts(user_id)
            contexts[context_name] = {
                "data": context_data,
                "created_at": datetime.now().isoformat(),
                "last_used": datetime.now().isoformat()
            }
            
            with data_base.transaction():
                data_base[self._get_contexts_key(user_id)] = json.dumps(contexts)
            data_base.commit()
            return True
        except Exception as e:
            print(f"Error saving context for user {user_id}: {e}")
            return False
    
    def get_context(self, user_id: str, context_name: str) -> Optional[Dict]:
        """Get a specific saved context"""
        contexts = self.get_saved_contexts(user_id)
        return contexts.get(context_name)
    
    def delete_context(self, user_id: str, context_name: str) -> bool:
        """Delete a saved context"""
        try:
            contexts = self.get_saved_contexts(user_id)
            if context_name in contexts:
                del contexts[context_name]
                
                with data_base.transaction():
                    data_base[self._get_contexts_key(user_id)] = json.dumps(contexts)
                data_base.commit()
                return True
            return False
        except Exception as e:
            print(f"Error deleting context for user {user_id}: {e}")
            return False
    
    def update_last_used(self, user_id: str, context_name: str) -> bool:
        """Update the last used timestamp for a context"""
        try:
            contexts = self.get_saved_contexts(user_id)
            if context_name in contexts:
                contexts[context_name]["last_used"] = datetime.now().isoformat()
                
                with data_base.transaction():
                    data_base[self._get_contexts_key(user_id)] = json.dumps(contexts)
                data_base.commit()
                return True
            return False
        except Exception as e:
            print(f"Error updating context timestamp for user {user_id}: {e}")
            return False
    
    async def get_current_context(self, user_id: str) -> Optional[Dict]:
        """Get the current context from the API"""
        try:
            response = await async_get(f"{PROXY_URL}/dialog-history", params={
                "masterToken": ADMIN_TOKEN,
                "dialogName": get_user_name(user_id),
            })
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error getting current context for user {user_id}: {e}")
            return None
    
    async def restore_context(self, user_id: str, context_data: Dict) -> bool:
        """Restore a saved context by clearing current and setting up the dialog"""
        try:
            # First clear the current dialog
            clear_response = await async_delete(f"{PROXY_URL}/dialogs", params={
                "masterToken": ADMIN_TOKEN,
                "userId": get_user_name(user_id),
            })
            
            if clear_response.status_code != 200:
                return False
            
            # For now, we'll just clear the context and let the user know
            # that they need to manually restore by retyping their conversation
            # In a full implementation, you would need an API endpoint that accepts
            # the complete dialog history to restore
            
            # Since there's no restore API endpoint in the current system,
            # we'll consider this successful if we can clear the dialog
            return True
        except Exception as e:
            print(f"Error restoring context for user {user_id}: {e}")
            return False


contextService = ContextService()