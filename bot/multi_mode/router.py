import asyncio
from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command

from bot.agreement import agreement_handler
from bot.commands import multi_mode_command, exit_multi_mode_command, get_response_command
from bot.filters import TextCommand, StateCommand
from bot.gpt.utils import is_chat_member
from bot.gpt.router import handle_gpt_request
from services import stateService, StateTypes, multiModeService

multiModeRouter = Router()


def create_multi_mode_keyboard(message_count: int = 0, auto_seconds: int = None) -> InlineKeyboardMarkup:
    """Create inline keyboard for multi-mode"""
    buttons = []
    
    # Get response button
    response_text = f"✅ Получить ответ ({message_count} сообщ.)" if message_count > 0 else "✅ Получить ответ"
    buttons.append([InlineKeyboardButton(text=response_text, callback_data="multi_get_response")])
    
    # Auto-confirm settings
    if auto_seconds:
        buttons.append([InlineKeyboardButton(text=f"⏱️ Авто: {auto_seconds}с", callback_data="multi_auto_settings")])
    else:
        buttons.append([InlineKeyboardButton(text="⏱️ Настроить авто-ответ", callback_data="multi_auto_settings")])
    
    # Exit multi-mode
    buttons.append([InlineKeyboardButton(text="❌ Выйти из режима", callback_data="multi_exit")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def create_auto_settings_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for auto-confirmation settings"""
    buttons = [
        [InlineKeyboardButton(text="5 секунд", callback_data="multi_auto_5")],
        [InlineKeyboardButton(text="10 секунд", callback_data="multi_auto_10")],
        [InlineKeyboardButton(text="30 секунд", callback_data="multi_auto_30")],
        [InlineKeyboardButton(text="60 секунд", callback_data="multi_auto_60")],
        [InlineKeyboardButton(text="Отключить", callback_data="multi_auto_off")],
        [InlineKeyboardButton(text="← Назад", callback_data="multi_back")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@multiModeRouter.message(TextCommand(multi_mode_command()))
async def enter_multi_mode_handler(message: Message):
    """Handler for /multi_mode command"""
    user_id = message.from_user.id
    
    # Check agreement and subscription
    is_agreement = await agreement_handler(message)
    if not is_agreement:
        return
    
    is_subscribe = await is_chat_member(message)
    if not is_subscribe:
        return
    
    # Set multi-mode state
    stateService.set_current_state(user_id, StateTypes.MultiMode)
    multiModeService.clear_messages(user_id)
    
    keyboard = create_multi_mode_keyboard()
    
    await message.answer(
        "📋 *Режим нескольких сообщений активирован!*\n\n"
        "Теперь вы можете отправлять несколько сообщений подряд. "
        "Они будут накапливаться, а затем обработаны как один запрос.\n\n"
        "• Отправляйте сообщения как обычно\n"
        "• Нажмите \"Получить ответ\" для обработки всех сообщений\n"
        "• Настройте авто-ответ для автоматической обработки\n"
        "• Используйте \"Выйти из режима\" для возврата к обычному режиму",
        reply_markup=keyboard
    )


@multiModeRouter.message(TextCommand(exit_multi_mode_command()))
async def exit_multi_mode_handler(message: Message):
    """Handler for /exit_multi command"""
    user_id = message.from_user.id
    
    if not stateService.is_multi_mode_state(user_id):
        await message.answer("❌ Вы не находитесь в режиме нескольких сообщений.")
        return
    
    # Clear data and set default state
    multiModeService.clear_messages(user_id)
    multiModeService.clear_auto_confirm_seconds(user_id)
    stateService.set_current_state(user_id, StateTypes.Default)
    
    await message.answer("✅ Вы вышли из режима нескольких сообщений.")


@multiModeRouter.message(TextCommand(get_response_command()))
async def get_response_handler(message: Message):
    """Handler for /get_response command"""
    user_id = message.from_user.id
    
    if not stateService.is_multi_mode_state(user_id):
        await message.answer("❌ Эта команда доступна только в режиме нескольких сообщений.")
        return
    
    await process_multi_mode_messages(message)


@multiModeRouter.callback_query(lambda c: c.data.startswith("multi_"))
async def multi_mode_callback_handler(callback: CallbackQuery):
    """Handler for multi-mode callback queries"""
    user_id = callback.from_user.id
    
    if callback.data == "multi_get_response":
        await process_multi_mode_messages(callback.message)
    
    elif callback.data == "multi_auto_settings":
        keyboard = create_auto_settings_keyboard()
        await callback.message.edit_text(
            "⏱️ *Настройки авто-ответа*\n\n"
            "Выберите время ожидания после последнего сообщения, "
            "после которого автоматически будет получен ответ:",
            reply_markup=keyboard
        )
    
    elif callback.data.startswith("multi_auto_"):
        if callback.data == "multi_auto_off":
            multiModeService.clear_auto_confirm_seconds(user_id)
            await callback.answer("✅ Авто-ответ отключён")
        elif callback.data == "multi_auto_5":
            multiModeService.set_auto_confirm_seconds(user_id, 5)
            await callback.answer("✅ Авто-ответ: 5 секунд")
        elif callback.data == "multi_auto_10":
            multiModeService.set_auto_confirm_seconds(user_id, 10)
            await callback.answer("✅ Авто-ответ: 10 секунд")
        elif callback.data == "multi_auto_30":
            multiModeService.set_auto_confirm_seconds(user_id, 30)
            await callback.answer("✅ Авто-ответ: 30 секунд")
        elif callback.data == "multi_auto_60":
            multiModeService.set_auto_confirm_seconds(user_id, 60)
            await callback.answer("✅ Авто-ответ: 60 секунд")
        
        # Update keyboard
        message_count = multiModeService.get_message_count(user_id)
        auto_seconds = multiModeService.get_auto_confirm_seconds(user_id)
        keyboard = create_multi_mode_keyboard(message_count, auto_seconds)
        
        await callback.message.edit_text(
            "📋 *Режим нескольких сообщений активен*\n\n"
            f"Накоплено сообщений: {message_count}\n"
            f"Авто-ответ: {'включён' if auto_seconds else 'отключён'}",
            reply_markup=keyboard
        )
    
    elif callback.data == "multi_back":
        message_count = multiModeService.get_message_count(user_id)
        auto_seconds = multiModeService.get_auto_confirm_seconds(user_id)
        keyboard = create_multi_mode_keyboard(message_count, auto_seconds)
        
        await callback.message.edit_text(
            "📋 *Режим нескольких сообщений активен*\n\n"
            f"Накоплено сообщений: {message_count}\n"
            f"Авто-ответ: {'включён' if auto_seconds else 'отключён'}",
            reply_markup=keyboard
        )
    
    elif callback.data == "multi_exit":
        multiModeService.clear_messages(user_id)
        multiModeService.clear_auto_confirm_seconds(user_id)
        stateService.set_current_state(user_id, StateTypes.Default)
        
        await callback.message.edit_text("✅ Вы вышли из режима нескольких сообщений.")


async def process_multi_mode_messages(message: Message):
    """Process accumulated messages in multi-mode"""
    user_id = message.from_user.id
    
    message_count = multiModeService.get_message_count(user_id)
    if message_count == 0:
        await message.answer("❌ Нет накопленных сообщений для обработки.")
        return
    
    # Get combined text
    combined_text = multiModeService.get_combined_text(user_id)
    
    # Clear messages
    multiModeService.clear_messages(user_id)
    
    # Return to default state for processing
    stateService.set_current_state(user_id, StateTypes.Default)
    
    # Process through GPT
    await handle_gpt_request(message, combined_text)
    
    # Return to multi-mode state
    stateService.set_current_state(user_id, StateTypes.MultiMode)
    
    # Show updated keyboard
    auto_seconds = multiModeService.get_auto_confirm_seconds(user_id)
    keyboard = create_multi_mode_keyboard(0, auto_seconds)
    
    await message.answer(
        "📋 *Режим нескольких сообщений*\n\n"
        "Готов к приёму новых сообщений!",
        reply_markup=keyboard
    )


# Auto-confirmation timer storage
auto_timers = {}


async def schedule_auto_response(user_id: str, message: Message):
    """Schedule auto-response after specified time"""
    auto_seconds = multiModeService.get_auto_confirm_seconds(user_id)
    if not auto_seconds:
        return
    
    # Cancel previous timer if exists
    if user_id in auto_timers:
        auto_timers[user_id].cancel()
    
    async def auto_response():
        try:
            await asyncio.sleep(auto_seconds)
            # Check if user is still in multi-mode and has messages
            if (stateService.is_multi_mode_state(user_id) and 
                multiModeService.get_message_count(user_id) > 0):
                await process_multi_mode_messages(message)
        except asyncio.CancelledError:
            pass
        finally:
            auto_timers.pop(user_id, None)
    
    # Start new timer
    auto_timers[user_id] = asyncio.create_task(auto_response())


# Handler for regular messages in multi-mode
@multiModeRouter.message(StateCommand(StateTypes.MultiMode))
async def multi_mode_message_handler(message: Message):
    """Handler for messages in multi-mode state"""
    user_id = message.from_user.id
    
    # Check agreement and subscription
    is_agreement = await agreement_handler(message)
    if not is_agreement:
        return
    
    is_subscribe = await is_chat_member(message)
    if not is_subscribe:
        return
    
    # Add message to batch
    text = message.text or message.caption or ""
    if text.strip():
        multiModeService.add_message(user_id, text.strip())
        
        message_count = multiModeService.get_message_count(user_id)
        auto_seconds = multiModeService.get_auto_confirm_seconds(user_id)
        
        # Update keyboard
        keyboard = create_multi_mode_keyboard(message_count, auto_seconds)
        
        await message.answer(
            f"📝 *Сообщение добавлено* ({message_count} накоплено)\n\n"
            "Отправьте ещё сообщения или нажмите \"Получить ответ\".",
            reply_markup=keyboard
        )
        
        # Schedule auto-response if enabled
        await schedule_auto_response(user_id, message)
    else:
        await message.answer("❌ Пустые сообщения не добавляются в накопитель.")