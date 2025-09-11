from datetime import datetime, timedelta
from db import data_base, db_key


class ContextService:
    LAST_INTERACTION_DATE = "last_interaction_date"
    CONTEXT_NOTIFICATION_SENT = "context_notification_sent"
    
    def __init__(self):
        self.data_base = data_base
    
    def update_last_interaction(self, user_id: str):
        """Update the last interaction timestamp for a user"""
        current_time = datetime.now().isoformat()
        with data_base.transaction():
            data_base[db_key(user_id, self.LAST_INTERACTION_DATE)] = current_time
        data_base.commit()
        
        # Reset notification flag when user interacts
        self.reset_notification_sent(user_id)
    
    def get_last_interaction(self, user_id: str):
        """Get the last interaction timestamp for a user"""
        try:
            timestamp_str = data_base[db_key(user_id, self.LAST_INTERACTION_DATE)].decode('utf-8')
            return datetime.fromisoformat(timestamp_str)
        except KeyError:
            return None
    
    def should_show_context_notification(self, user_id: str) -> bool:
        """Check if we should show context notification to user"""
        last_interaction = self.get_last_interaction(user_id)
        
        # If no previous interaction recorded, don't show notification
        if last_interaction is None:
            return False
        
        # Check if more than 24 hours have passed since last interaction
        time_since_last = datetime.now() - last_interaction
        one_day = timedelta(hours=24)
        
        # Only show notification if it's been more than 24 hours and we haven't sent notification yet
        if time_since_last >= one_day:
            return not self.is_notification_sent(user_id)
        
        return False
    
    def set_notification_sent(self, user_id: str):
        """Mark that we've sent the context notification to this user"""
        with data_base.transaction():
            data_base[db_key(user_id, self.CONTEXT_NOTIFICATION_SENT)] = "true"
        data_base.commit()
    
    def is_notification_sent(self, user_id: str) -> bool:
        """Check if we've already sent the context notification"""
        try:
            sent = data_base[db_key(user_id, self.CONTEXT_NOTIFICATION_SENT)].decode('utf-8')
            return sent == "true"
        except KeyError:
            return False
    
    def reset_notification_sent(self, user_id: str):
        """Reset the notification sent flag"""
        try:
            with data_base.transaction():
                del data_base[db_key(user_id, self.CONTEXT_NOTIFICATION_SENT)]
            data_base.commit()
        except KeyError:
            pass  # Key doesn't exist, nothing to reset


contextService = ContextService()