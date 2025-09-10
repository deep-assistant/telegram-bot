import json
import time
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from config import PROXY_URL, ADMIN_TOKEN
from db import data_base, db_key
from services.utils import async_get, async_post


class StatisticsService:
    """
    Service for collecting and analyzing bot usage statistics.
    Tracks daily users, token usage, models, and usage patterns.
    """
    
    # Database keys for statistics storage
    DAILY_USERS_PREFIX = "daily_users"
    TOKEN_USAGE_PREFIX = "token_usage" 
    MODEL_STATS_PREFIX = "model_stats"
    USAGE_TIME_PREFIX = "usage_time"
    USER_ACTIVITY_PREFIX = "user_activity"
    
    def _get_date_key(self, date: datetime = None) -> str:
        """Get date string in YYYY-MM-DD format for database keys."""
        if date is None:
            date = datetime.now()
        return date.strftime('%Y-%m-%d')
    
    def _get_hour_key(self, timestamp: datetime = None) -> str:
        """Get hour string in YYYY-MM-DD-HH format for time-based statistics."""
        if timestamp is None:
            timestamp = datetime.now()
        return timestamp.strftime('%Y-%m-%d-%H')
    
    def track_user_activity(self, user_id: str, activity_type: str = "message"):
        """
        Track daily user activity.
        
        Args:
            user_id: Telegram user ID
            activity_type: Type of activity (message, command, etc.)
        """
        try:
            date_key = self._get_date_key()
            hour_key = self._get_hour_key()
            
            # Track daily unique users
            daily_users_key = db_key("stats", f"{self.DAILY_USERS_PREFIX}_{date_key}")
            try:
                daily_users = json.loads(data_base[daily_users_key].decode('utf-8'))
            except KeyError:
                daily_users = []
            
            if user_id not in daily_users:
                daily_users.append(user_id)
                with data_base.transaction():
                    data_base[daily_users_key] = json.dumps(daily_users)
                data_base.commit()
            
            # Track hourly activity for usage patterns
            activity_key = db_key("stats", f"{self.USER_ACTIVITY_PREFIX}_{hour_key}")
            try:
                activity_data = json.loads(data_base[activity_key].decode('utf-8'))
            except KeyError:
                activity_data = {}
            
            if activity_type not in activity_data:
                activity_data[activity_type] = 0
            activity_data[activity_type] += 1
            
            with data_base.transaction():
                data_base[activity_key] = json.dumps(activity_data)
            data_base.commit()
            
        except Exception as e:
            print(f"Error tracking user activity: {e}")
    
    def track_token_usage(self, user_id: str, tokens_spent: int, model: str = "unknown"):
        """
        Track token spending for statistics.
        
        Args:
            user_id: Telegram user ID
            tokens_spent: Number of tokens spent
            model: AI model used
        """
        try:
            date_key = self._get_date_key()
            
            # Track daily token usage
            token_key = db_key("stats", f"{self.TOKEN_USAGE_PREFIX}_{date_key}")
            try:
                token_data = json.loads(data_base[token_key].decode('utf-8'))
            except KeyError:
                token_data = {"total_spent": 0, "by_user": {}, "by_model": {}}
            
            token_data["total_spent"] += tokens_spent
            
            if user_id not in token_data["by_user"]:
                token_data["by_user"][user_id] = 0
            token_data["by_user"][user_id] += tokens_spent
            
            if model not in token_data["by_model"]:
                token_data["by_model"][model] = 0
            token_data["by_model"][model] += tokens_spent
            
            with data_base.transaction():
                data_base[token_key] = json.dumps(token_data)
            data_base.commit()
            
        except Exception as e:
            print(f"Error tracking token usage: {e}")
    
    def track_model_usage(self, user_id: str, model: str, mode: str = "default"):
        """
        Track model and mode usage statistics.
        
        Args:
            user_id: Telegram user ID  
            model: AI model used
            mode: Usage mode (default, transcribe, etc.)
        """
        try:
            date_key = self._get_date_key()
            
            model_key = db_key("stats", f"{self.MODEL_STATS_PREFIX}_{date_key}")
            try:
                model_data = json.loads(data_base[model_key].decode('utf-8'))
            except KeyError:
                model_data = {}
            
            stats_key = f"{model}_{mode}"
            if stats_key not in model_data:
                model_data[stats_key] = {"count": 0, "users": []}
            
            model_data[stats_key]["count"] += 1
            if user_id not in model_data[stats_key]["users"]:
                model_data[stats_key]["users"].append(user_id)
            
            with data_base.transaction():
                data_base[model_key] = json.dumps(model_data)
            data_base.commit()
            
        except Exception as e:
            print(f"Error tracking model usage: {e}")
    
    def get_daily_users_count(self, date: datetime = None) -> int:
        """Get number of unique users for a specific date."""
        try:
            date_key = self._get_date_key(date)
            daily_users_key = db_key("stats", f"{self.DAILY_USERS_PREFIX}_{date_key}")
            daily_users = json.loads(data_base[daily_users_key].decode('utf-8'))
            return len(daily_users)
        except KeyError:
            return 0
        except Exception as e:
            print(f"Error getting daily users count: {e}")
            return 0
    
    def get_token_statistics(self, date: datetime = None) -> Dict:
        """Get token usage statistics for a specific date."""
        try:
            date_key = self._get_date_key(date)
            token_key = db_key("stats", f"{self.TOKEN_USAGE_PREFIX}_{date_key}")
            return json.loads(data_base[token_key].decode('utf-8'))
        except KeyError:
            return {"total_spent": 0, "by_user": {}, "by_model": {}}
        except Exception as e:
            print(f"Error getting token statistics: {e}")
            return {"total_spent": 0, "by_user": {}, "by_model": {}}
    
    def get_model_statistics(self, date: datetime = None) -> Dict:
        """Get model and mode usage statistics for a specific date."""
        try:
            date_key = self._get_date_key(date)
            model_key = db_key("stats", f"{self.MODEL_STATS_PREFIX}_{date_key}")
            return json.loads(data_base[model_key].decode('utf-8'))
        except KeyError:
            return {}
        except Exception as e:
            print(f"Error getting model statistics: {e}")
            return {}
    
    def get_usage_time_statistics(self, date: datetime = None) -> Dict:
        """Get hourly usage pattern statistics for a specific date."""
        try:
            if date is None:
                date = datetime.now()
            
            usage_stats = {}
            
            # Get hourly data for the specified date
            for hour in range(24):
                hour_time = date.replace(hour=hour, minute=0, second=0, microsecond=0)
                hour_key = self._get_hour_key(hour_time)
                activity_key = db_key("stats", f"{self.USER_ACTIVITY_PREFIX}_{hour_key}")
                
                try:
                    activity_data = json.loads(data_base[activity_key].decode('utf-8'))
                    usage_stats[f"{hour:02d}:00"] = activity_data
                except KeyError:
                    usage_stats[f"{hour:02d}:00"] = {}
            
            return usage_stats
        except Exception as e:
            print(f"Error getting usage time statistics: {e}")
            return {}
    
    async def get_token_balance_statistics(self) -> Dict:
        """Get statistics about purchased tokens from external API."""
        try:
            params = {"masterToken": ADMIN_TOKEN}
            response = await async_get(f"{PROXY_URL}/tokens/stats", params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API returned status {response.status_code}"}
                
        except Exception as e:
            print(f"Error getting token balance statistics: {e}")
            return {"error": str(e)}
    
    def get_period_statistics(self, start_date: datetime, end_date: datetime) -> Dict:
        """Get comprehensive statistics for a date range."""
        try:
            stats = {
                "period": {
                    "start": start_date.strftime('%Y-%m-%d'),
                    "end": end_date.strftime('%Y-%m-%d')
                },
                "daily_users": [],
                "total_tokens_spent": 0,
                "tokens_by_model": defaultdict(int),
                "model_usage": defaultdict(lambda: {"count": 0, "unique_users": set()}),
                "hourly_activity": defaultdict(lambda: defaultdict(int))
            }
            
            current_date = start_date
            while current_date <= end_date:
                # Daily users
                daily_users = self.get_daily_users_count(current_date)
                stats["daily_users"].append({
                    "date": current_date.strftime('%Y-%m-%d'),
                    "users": daily_users
                })
                
                # Token statistics
                token_stats = self.get_token_statistics(current_date)
                stats["total_tokens_spent"] += token_stats.get("total_spent", 0)
                
                for model, tokens in token_stats.get("by_model", {}).items():
                    stats["tokens_by_model"][model] += tokens
                
                # Model statistics
                model_stats = self.get_model_statistics(current_date)
                for model_mode, data in model_stats.items():
                    stats["model_usage"][model_mode]["count"] += data.get("count", 0)
                    stats["model_usage"][model_mode]["unique_users"].update(data.get("users", []))
                
                # Usage time statistics
                usage_time = self.get_usage_time_statistics(current_date)
                for hour, activities in usage_time.items():
                    for activity, count in activities.items():
                        stats["hourly_activity"][hour][activity] += count
                
                current_date += timedelta(days=1)
            
            # Convert sets to counts for JSON serialization
            for model_mode in stats["model_usage"]:
                stats["model_usage"][model_mode]["unique_users"] = len(stats["model_usage"][model_mode]["unique_users"])
            
            return dict(stats)
            
        except Exception as e:
            print(f"Error getting period statistics: {e}")
            return {"error": str(e)}


# Global instance
statisticsService = StatisticsService()