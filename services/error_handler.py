"""
Error handling utilities for image generation services.
"""

def parse_midjourney_error(error_data):
    """
    Parse Midjourney API error response and return user-friendly message.
    
    Args:
        error_data (dict): The error object from Midjourney API response
        
    Returns:
        str: User-friendly error message
    """
    if not error_data or not isinstance(error_data, dict):
        return None
        
    raw_message = error_data.get('raw_message', '')
    error_code = error_data.get('code')
    
    # Handle banned prompt errors
    if 'Banned Prompt' in raw_message:
        # Extract the banned word from the message
        # Format: "Banned Prompt: word"
        if ':' in raw_message:
            banned_word = raw_message.split(':', 1)[1].strip()
            return f'🚫 "{banned_word}" is banned prompt by MidJourney, please try another prompt.'
    
    # Handle other known error codes
    if error_code == 10000:
        return f'🚫 Prompt check failed: {raw_message}. Please try another prompt.'
    
    # Generic fallback for other errors
    if raw_message:
        return f'🚫 MidJourney error: {raw_message}. Please try again.'
    
    return None


def get_user_friendly_error_message(result_data, service_name="image generation"):
    """
    Get user-friendly error message from service result data.
    
    Args:
        result_data (dict): The result from image generation service
        service_name (str): Name of the service for generic messages
        
    Returns:
        str: User-friendly error message or None if no error
    """
    if not result_data or not isinstance(result_data, dict):
        return None
    
    # Check for error field in the response
    if "error" in result_data:
        error_data = result_data["error"]
        
        # Try to parse MidJourney specific errors
        if service_name.lower() == "midjourney":
            midjourney_error = parse_midjourney_error(error_data)
            if midjourney_error:
                return midjourney_error
        
        # Generic error fallback
        if isinstance(error_data, dict):
            message = error_data.get('message', error_data.get('raw_message', ''))
            if message:
                return f'🚫 {service_name.title()} error: {message}. Please try again.'
    
    # Check for failed status
    if result_data.get("status") == "failed":
        return f'🚫 {service_name.title()} generation failed. Please try again.'
    
    return None