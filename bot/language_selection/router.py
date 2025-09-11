"""
Language selection router for the Telegram bot.
"""

from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from bot.i18n import _, set_user_language, get_user_language, get_available_languages

languageRouter = Router()

@languageRouter.message(Command("language"))
async def handle_language_command(message: types.Message):
    """Handle /language command to show language selection."""
    user_id = message.from_user.id
    current_lang = get_user_language(user_id)
    
    # Create language selection keyboard
    keyboard = create_language_keyboard(current_lang)
    
    text = _(
        "language.select", 
        user_id=user_id, 
        language="en"  # Show in both languages
    )
    
    await message.answer(text=text, reply_markup=keyboard)

def create_language_keyboard(current_lang: str = None) -> InlineKeyboardMarkup:
    """Create language selection inline keyboard."""
    languages = get_available_languages()
    keyboard = []
    
    # Create buttons in rows of 2
    row = []
    for lang_code, lang_name in languages.items():
        # Add checkmark for current language
        button_text = f"✅ {lang_name}" if lang_code == current_lang else lang_name
        button = InlineKeyboardButton(
            text=button_text,
            callback_data=f"set_language:{lang_code}"
        )
        row.append(button)
        
        # Add row when we have 2 buttons
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    # Add remaining button if any
    if row:
        keyboard.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@languageRouter.callback_query(lambda c: c.data and c.data.startswith("set_language:"))
async def handle_language_selection(callback_query: types.CallbackQuery):
    """Handle language selection callback."""
    user_id = callback_query.from_user.id
    selected_language = callback_query.data.split(":")[1]
    
    # Set user language
    success = set_user_language(user_id, selected_language)
    
    if success:
        # Get success message in the new language
        success_text = _("language.changed", user_id=user_id)
        current_text = _("language.current", user_id=user_id)
        
        response_text = f"{success_text}\n{current_text}"
        
        # Update keyboard to show new selection
        new_keyboard = create_language_keyboard(selected_language)
        
        await callback_query.message.edit_text(
            text=response_text,
            reply_markup=new_keyboard
        )
    else:
        # Error message
        error_text = _("common.error", user_id=user_id)
        await callback_query.answer(error_text, show_alert=True)
    
    await callback_query.answer()