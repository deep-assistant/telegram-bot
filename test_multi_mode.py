import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

import pytest

from services.multi_mode_service import MultiModeService, MultiModeMessage
from services.state_service import StateService, StateTypes
from bot.multi_mode.router import (
    create_multi_mode_keyboard,
    create_auto_settings_keyboard,
    schedule_auto_response
)


class TestMultiModeMessage(unittest.TestCase):
    def test_message_creation(self):
        """Test MultiModeMessage creation and serialization"""
        text = "Test message"
        timestamp = datetime.now()
        message = MultiModeMessage(text, timestamp)
        
        self.assertEqual(message.text, text)
        self.assertEqual(message.timestamp, timestamp)
    
    def test_message_serialization(self):
        """Test message to_dict and from_dict methods"""
        text = "Test message"
        timestamp = datetime.now()
        message = MultiModeMessage(text, timestamp)
        
        # Test serialization
        data = message.to_dict()
        self.assertEqual(data["text"], text)
        self.assertEqual(data["timestamp"], timestamp.isoformat())
        
        # Test deserialization
        restored_message = MultiModeMessage.from_dict(data)
        self.assertEqual(restored_message.text, text)
        self.assertEqual(restored_message.timestamp.replace(microsecond=0), 
                        timestamp.replace(microsecond=0))


class TestMultiModeService(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        # Mock the database
        self.mock_db = {}
        
        patcher = patch('services.multi_mode_service.data_base')
        self.mock_data_base = patcher.start()
        self.mock_data_base.__getitem__.side_effect = lambda key: self.mock_db[key].encode('utf-8')
        self.mock_data_base.__setitem__.side_effect = lambda key, value: self.mock_db.__setitem__(key, value)
        self.mock_data_base.__delitem__.side_effect = lambda key: self.mock_db.__delitem__(key)
        self.mock_data_base.__contains__.side_effect = lambda key: key in self.mock_db
        
        # Mock transaction
        self.mock_data_base.transaction.return_value.__enter__ = MagicMock()
        self.mock_data_base.transaction.return_value.__exit__ = MagicMock()
        self.mock_data_base.commit = MagicMock()
        
        self.addCleanup(patcher.stop)
        
        # Mock db_key function
        patcher2 = patch('services.multi_mode_service.db_key')
        self.mock_db_key = patcher2.start()
        self.mock_db_key.side_effect = lambda user_id, key: f"{user_id}:{key}"
        self.addCleanup(patcher2.stop)
        
        self.service = MultiModeService()
        self.user_id = "123456"
    
    def test_add_message(self):
        """Test adding messages to batch"""
        text1 = "First message"
        text2 = "Second message"
        
        self.service.add_message(self.user_id, text1)
        self.service.add_message(self.user_id, text2)
        
        messages = self.service.get_messages(self.user_id)
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].text, text1)
        self.assertEqual(messages[1].text, text2)
    
    def test_get_combined_text(self):
        """Test getting combined text from messages"""
        self.service.add_message(self.user_id, "First message")
        self.service.add_message(self.user_id, "Second message")
        
        combined = self.service.get_combined_text(self.user_id)
        expected = "Сообщение 1: First message\n\nСообщение 2: Second message"
        self.assertEqual(combined, expected)
    
    def test_get_message_count(self):
        """Test getting message count"""
        self.assertEqual(self.service.get_message_count(self.user_id), 0)
        
        self.service.add_message(self.user_id, "Test message")
        self.assertEqual(self.service.get_message_count(self.user_id), 1)
        
        self.service.add_message(self.user_id, "Another message")
        self.assertEqual(self.service.get_message_count(self.user_id), 2)
    
    def test_clear_messages(self):
        """Test clearing messages"""
        self.service.add_message(self.user_id, "Test message")
        self.assertEqual(self.service.get_message_count(self.user_id), 1)
        
        self.service.clear_messages(self.user_id)
        self.assertEqual(self.service.get_message_count(self.user_id), 0)
    
    def test_auto_confirm_seconds(self):
        """Test auto-confirmation timer settings"""
        # Initially no timer
        self.assertIsNone(self.service.get_auto_confirm_seconds(self.user_id))
        
        # Set timer
        self.service.set_auto_confirm_seconds(self.user_id, 30)
        self.assertEqual(self.service.get_auto_confirm_seconds(self.user_id), 30)
        
        # Clear timer
        self.service.clear_auto_confirm_seconds(self.user_id)
        self.assertIsNone(self.service.get_auto_confirm_seconds(self.user_id))


class TestStateService(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        # Mock the database
        self.mock_db = {}
        
        patcher = patch('services.state_service.data_base')
        self.mock_data_base = patcher.start()
        self.mock_data_base.__getitem__.side_effect = lambda key: self.mock_db[key].encode('utf-8')
        self.mock_data_base.__setitem__.side_effect = lambda key, value: self.mock_db.__setitem__(key, value)
        
        # Mock transaction
        self.mock_data_base.transaction.return_value.__enter__ = MagicMock()
        self.mock_data_base.transaction.return_value.__exit__ = MagicMock()
        self.mock_data_base.commit = MagicMock()
        
        self.addCleanup(patcher.stop)
        
        # Mock db_key function
        patcher2 = patch('services.state_service.db_key')
        self.mock_db_key = patcher2.start()
        self.mock_db_key.side_effect = lambda user_id, key: f"{user_id}:{key}"
        self.addCleanup(patcher2.stop)
        
        self.service = StateService()
        self.user_id = "123456"
    
    def test_multi_mode_state(self):
        """Test multi-mode state management"""
        # Initially default state
        self.assertTrue(self.service.is_default_state(self.user_id))
        self.assertFalse(self.service.is_multi_mode_state(self.user_id))
        
        # Set multi-mode state
        self.service.set_current_state(self.user_id, StateTypes.MultiMode)
        self.assertFalse(self.service.is_default_state(self.user_id))
        self.assertTrue(self.service.is_multi_mode_state(self.user_id))
        
        # Return to default
        self.service.set_current_state(self.user_id, StateTypes.Default)
        self.assertTrue(self.service.is_default_state(self.user_id))
        self.assertFalse(self.service.is_multi_mode_state(self.user_id))


class TestKeyboards(unittest.TestCase):
    def test_multi_mode_keyboard_creation(self):
        """Test multi-mode keyboard creation"""
        keyboard = create_multi_mode_keyboard()
        self.assertIsNotNone(keyboard)
        self.assertTrue(len(keyboard.inline_keyboard) >= 3)
        
        # Test with message count
        keyboard_with_count = create_multi_mode_keyboard(message_count=5)
        response_button = keyboard_with_count.inline_keyboard[0][0]
        self.assertIn("5", response_button.text)
        
        # Test with auto seconds
        keyboard_with_auto = create_multi_mode_keyboard(auto_seconds=30)
        auto_button = keyboard_with_auto.inline_keyboard[1][0]
        self.assertIn("30с", auto_button.text)
    
    def test_auto_settings_keyboard_creation(self):
        """Test auto-settings keyboard creation"""
        keyboard = create_auto_settings_keyboard()
        self.assertIsNotNone(keyboard)
        self.assertTrue(len(keyboard.inline_keyboard) >= 5)
        
        # Check if all time options are present
        button_texts = [button.text for row in keyboard.inline_keyboard for button in row]
        self.assertIn("5 секунд", button_texts)
        self.assertIn("10 секунд", button_texts)
        self.assertIn("30 секунд", button_texts)
        self.assertIn("60 секунд", button_texts)
        self.assertIn("Отключить", button_texts)


class TestIntegration(unittest.IsolatedAsyncioTestCase):
    async def test_auto_response_scheduling(self):
        """Test auto-response scheduling functionality"""
        user_id = "123456"
        
        # Mock message
        mock_message = MagicMock()
        mock_message.from_user.id = user_id
        
        # Mock services
        with patch('bot.multi_mode.router.multiModeService') as mock_multi_service, \
             patch('bot.multi_mode.router.stateService') as mock_state_service, \
             patch('bot.multi_mode.router.process_multi_mode_messages') as mock_process:
            
            # Set up mocks
            mock_multi_service.get_auto_confirm_seconds.return_value = 1  # 1 second for quick test
            mock_state_service.is_multi_mode_state.return_value = True
            mock_multi_service.get_message_count.return_value = 2
            
            # Schedule auto-response
            await schedule_auto_response(user_id, mock_message)
            
            # Wait for auto-response to trigger
            await asyncio.sleep(1.1)
            
            # Verify that process_multi_mode_messages was called
            mock_process.assert_called_once_with(mock_message)


class TestErrorHandling(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        # Mock the database to raise KeyError
        patcher = patch('services.multi_mode_service.data_base')
        self.mock_data_base = patcher.start()
        self.mock_data_base.__getitem__.side_effect = KeyError("Key not found")
        
        self.addCleanup(patcher.stop)
        
        # Mock db_key function
        patcher2 = patch('services.multi_mode_service.db_key')
        self.mock_db_key = patcher2.start()
        self.mock_db_key.side_effect = lambda user_id, key: f"{user_id}:{key}"
        self.addCleanup(patcher2.stop)
        
        self.service = MultiModeService()
        self.user_id = "123456"
    
    def test_get_messages_empty_db(self):
        """Test getting messages when database is empty"""
        messages = self.service.get_messages(self.user_id)
        self.assertEqual(len(messages), 0)
    
    def test_get_auto_confirm_seconds_empty_db(self):
        """Test getting auto-confirm seconds when not set"""
        seconds = self.service.get_auto_confirm_seconds(self.user_id)
        self.assertIsNone(seconds)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)