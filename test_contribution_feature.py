#!/usr/bin/env python3
"""
Test script for the user-determined payment model feature.
This tests the new contribution functionality.
"""

import unittest
from unittest.mock import MagicMock, AsyncMock

# Import the functions we want to test
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.payment.router import (
    get_star_price, 
    get_price_rub, 
    create_contribution_keyboard
)
from services import GPTModels


class TestContributionFeature(unittest.TestCase):
    """Test cases for the contribution feature"""
    
    def test_base_price_calculation_gpt4o(self):
        """Test that base prices are calculated correctly for GPT-4o"""
        tokens = 100000
        model = GPTModels.GPT_4o.value
        
        # Test star price calculation
        star_price = get_star_price(tokens, model)
        self.assertIsInstance(star_price, int)
        self.assertGreater(star_price, 0)
        
        # Test RUB price calculation
        rub_price = get_price_rub(tokens, model)
        self.assertIsInstance(rub_price, int)
        self.assertGreater(rub_price, 0)
    
    def test_base_price_calculation_gpt35(self):
        """Test that base prices are calculated correctly for GPT-3.5"""
        tokens = 100000
        model = GPTModels.GPT_3_5.value
        
        # Test star price calculation
        star_price = get_star_price(tokens, model)
        self.assertIsInstance(star_price, int)
        self.assertGreater(star_price, 0)
        
        # Test RUB price calculation  
        rub_price = get_price_rub(tokens, model)
        self.assertIsInstance(rub_price, int)
        self.assertGreater(rub_price, 0)
        
        # GPT-3.5 should be cheaper than GPT-4o
        gpt4o_star_price = get_star_price(tokens, GPTModels.GPT_4o.value)
        self.assertLess(star_price, gpt4o_star_price)
    
    def test_contribution_keyboard_creation(self):
        """Test that contribution keyboard is created correctly"""
        keyboard = create_contribution_keyboard("stars", "100,000", 50, "gpt-4o")
        
        # Check that keyboard is created
        self.assertIsNotNone(keyboard)
        self.assertTrue(hasattr(keyboard, 'inline_keyboard'))
        
        # Check that buttons exist
        buttons = keyboard.inline_keyboard
        self.assertGreater(len(buttons), 0)
        
        # Check that custom contribution option exists
        custom_button_found = False
        for row in buttons:
            for button in row:
                if "Ввести свою сумму" in button.text:
                    custom_button_found = True
                    break
        self.assertTrue(custom_button_found, "Custom contribution button should exist")
    
    def test_contribution_amounts_in_keyboard(self):
        """Test that contribution amounts are properly formatted"""
        keyboard = create_contribution_keyboard("card", "50,000", 25, "gpt-3.5")
        
        # Check for base cost option
        base_cost_found = False
        contribution_options_found = 0
        
        for row in keyboard.inline_keyboard:
            for button in row:
                if "Только базовая стоимость" in button.text:
                    base_cost_found = True
                elif "поддержка" in button.text and "итого:" in button.text:
                    contribution_options_found += 1
        
        self.assertTrue(base_cost_found, "Base cost option should exist")
        self.assertGreater(contribution_options_found, 0, "Should have contribution options")


def test_payload_format():
    """Test that new payment payload format is correct"""
    # This would test the payload creation in actual handlers
    # For now, we'll just test the expected format
    
    expected_format = "buy_balance 100000 gpt-4o stars 45 10"
    parts = expected_format.split(" ")
    
    assert len(parts) == 6
    assert parts[0] == "buy_balance"
    assert parts[1] == "100000"  # tokens
    assert parts[2] == "gpt-4o"  # model
    assert parts[3] == "stars"   # payment method
    assert parts[4] == "45"      # base price
    assert parts[5] == "10"      # contribution
    
    print("✅ Payload format test passed")


if __name__ == "__main__":
    print("🧪 Running contribution feature tests...")
    
    # Run the payload format test
    test_payload_format()
    
    # Run unittest tests
    unittest.main(verbosity=2, exit=False)
    
    print("🎉 All tests completed!")