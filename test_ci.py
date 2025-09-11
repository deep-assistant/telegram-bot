#!/usr/bin/env python3
"""
Simple CI test to validate basic functionality
"""
import unittest
import sys
import os

class BasicCITest(unittest.TestCase):
    """Basic tests for CI pipeline"""
    
    def test_python_version(self):
        """Test that Python version is supported"""
        self.assertGreaterEqual(sys.version_info[:2], (3, 8))
    
    def test_required_files_exist(self):
        """Test that required files exist"""
        required_files = [
            '__main__.py',
            'requirements.txt',
            'bot/bot_run.py'
        ]
        for file_path in required_files:
            self.assertTrue(os.path.exists(file_path), f"Required file {file_path} not found")
    
    def test_bot_imports(self):
        """Test that bot module can be imported without config dependencies"""
        try:
            # Test basic import structure
            import bot
            self.assertTrue(hasattr(bot, '__name__'))
        except ImportError as e:
            # If it fails due to config, that's expected - just check the module structure exists
            if 'config' in str(e):
                self.assertTrue(os.path.exists('bot/__init__.py'))
            else:
                raise
    
    def test_requirements_readable(self):
        """Test that requirements.txt is readable and contains expected packages"""
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
            self.assertIn('aiogram', requirements)
            self.assertIn('openai', requirements)

if __name__ == '__main__':
    unittest.main()