"""
Error reporting service for sending error reports to private chats or repositories.
"""
import asyncio
import logging
from typing import Optional, Dict, Any
try:
    import config
except ImportError:
    # Handle case where config is not available (e.g., in tests)
    class MockConfig:
        ERROR_LOGGING_ENABLED = False
        ERROR_LOGGING_CHAT_ID = ''
        ERROR_LOGGING_GITHUB_REPO = ''
        ERROR_LOGGING_GITHUB_TOKEN = ''
    config = MockConfig()
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

class ErrorReporter:
    """Service for reporting errors to external destinations."""
    
    def __init__(self, bot: Optional[Bot] = None):
        self.bot = bot
        self.enabled = getattr(config, 'ERROR_LOGGING_ENABLED', False)
        self.chat_id = getattr(config, 'ERROR_LOGGING_CHAT_ID', '')
        self.github_repo = getattr(config, 'ERROR_LOGGING_GITHUB_REPO', '')
        self.github_token = getattr(config, 'ERROR_LOGGING_GITHUB_TOKEN', '')

    async def send_to_private_chat(self, error_message: str) -> bool:
        """
        Send error report to a private Telegram chat.
        
        Args:
            error_message (str): Formatted error message
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.enabled or not self.chat_id or not self.bot:
            return False
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=error_message,
                parse_mode='Markdown'
            )
            return True
        except TelegramAPIError as e:
            logging.error(f"Failed to send error report to private chat: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error sending to private chat: {e}")
            return False

    async def send_to_github(self, error_message: str, error_guid: str) -> bool:
        """
        Create a GitHub issue with the error report.
        
        Args:
            error_message (str): Formatted error message
            error_guid (str): Error GUID for the issue title
            
        Returns:
            bool: True if created successfully, False otherwise
        """
        if not self.enabled or not self.github_repo or not self.github_token or not HTTPX_AVAILABLE:
            return False
        
        try:
            url = f"https://api.github.com/repos/{self.github_repo}/issues"
            
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            }
            
            data = {
                "title": f"Bot Error Report - {error_guid}",
                "body": error_message,
                "labels": ["bug", "bot-error"]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, headers=headers)
                
            if response.status_code == 201:
                return True
            else:
                logging.error(f"Failed to create GitHub issue: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"Unexpected error creating GitHub issue: {e}")
            return False

    async def report_error(
        self, 
        error_message: str, 
        error_guid: str,
        prefer_github: bool = True
    ) -> Dict[str, bool]:
        """
        Report error to configured destinations.
        
        Args:
            error_message (str): Formatted error message
            error_guid (str): Error GUID
            prefer_github (bool): Whether to prefer GitHub over Telegram
            
        Returns:
            Dict[str, bool]: Results of reporting attempts
        """
        results = {
            "telegram": False,
            "github": False
        }
        
        if not self.enabled:
            return results
        
        # Try both destinations
        telegram_task = self.send_to_private_chat(error_message)
        github_task = self.send_to_github(error_message, error_guid)
        
        # Run both in parallel
        try:
            telegram_result, github_result = await asyncio.gather(
                telegram_task, 
                github_task, 
                return_exceptions=True
            )
            
            results["telegram"] = telegram_result if not isinstance(telegram_result, Exception) else False
            results["github"] = github_result if not isinstance(github_result, Exception) else False
            
        except Exception as e:
            logging.error(f"Error in error reporting: {e}")
        
        return results

# Global error reporter instance
_error_reporter: Optional[ErrorReporter] = None

def get_error_reporter(bot: Optional[Bot] = None) -> ErrorReporter:
    """Get or create the global error reporter instance."""
    global _error_reporter
    if _error_reporter is None:
        _error_reporter = ErrorReporter(bot)
    elif bot and not _error_reporter.bot:
        _error_reporter.bot = bot
    return _error_reporter