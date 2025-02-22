from datetime import datetime, timezone
from tempfile import NamedTemporaryFile

from aiogram import Router
from aiogram import types

from bot.filters import TextCommand
from bot.gpt.utils import send_markdown_message

from bot.commands import here_and_now_command

diagnosticsRouter = Router()

@diagnosticsRouter.message(TextCommand([here_and_now_command()]))
async def handle_here_and_now(message: types.Message):
    # Capture start time in UTC for latency and performance measurement
    start_time = datetime.now(timezone.utc)

    user = message.from_user
    chat = message.chat

    # User info fields with availability check
    user_info = []
    if user.id:
        user_info.append(f"User ID: `{user.id}`")
    if user.full_name.strip():
        user_info.append(f"Full Name: `{user.full_name.strip()}`")
    if user.username:
        user_info.append(f"Username: `@{user.username}`")
    if user.is_bot is not None:
        user_info.append(f"Is Bot: `{'Yes' if user.is_bot else 'No'}`")
    if user.language_code:
        user_info.append(f"Language: `{user.language_code}`")
    if user.is_premium is not None:
        user_info.append(f"Premium: `{'Yes' if user.is_premium else 'No'}`")
    if user.added_to_attachment_menu is not None:
        user_info.append(f"Added to Attachment Menu: `{'Yes' if user.added_to_attachment_menu else 'No'}`")

    # Chat status
    try:
        chat_member = await message.bot.get_chat_member(chat.id, user.id)
        if chat_member.status:
            if chat_member.status == "administrator":
                user_info.append(f"Chat Status: Admin (Can ban: `{chat_member.can_restrict_members}`, Can promote: `{chat_member.can_promote_members}`)")
            else:
                user_info.append(f"Chat Status: `{chat_member.status.capitalize()}`")
    except Exception:
        pass  # Silently skip if unavailable

    # Profile photo count and optional retrieval
    profile_photo_file_id = None
    try:
        profile_photos = await message.bot.get_user_profile_photos(user.id, limit=1)
        if profile_photos.total_count is not None:
            photo_count = profile_photos.total_count
            user_info.append(f"Has Profile Photo: `{'Yes (' + str(photo_count) + ' photos)' if photo_count > 0 else 'No'}`")
            if photo_count > 0:
                profile_photo_file_id = profile_photos.photos[0][-1].file_id
    except Exception:
        pass  # Silently skip if unavailable

    # Chat info fields with availability check
    chat_info = []
    if chat.id:
        chat_info.append(f"Chat ID: `{chat.id}`")
    if chat.type:
        chat_info.append(f"Type: `{chat.type}`")
    if chat.title:
        chat_info.append(f"Title: `{chat.title}`")
    if chat.username:
        chat_info.append(f"Username: `@{chat.username}`")

    # Date and time
    telegram_time = message.date  # Telegram's timestamp (UTC)
    bot_time = datetime.now(timezone.utc)  # Bot's time in UTC

    # Calculate latency (time from message sent to processing start)
    latency = (start_time - telegram_time).total_seconds()  # In seconds

    # Build response with only available fields
    response_lines = ["**Here and Now**:"]
    if user_info:
        response_lines.append("**User Info**:")
        response_lines.extend(user_info)
    if chat_info:
        response_lines.append("\n**Chat Info**:")
        response_lines.extend(chat_info)
    response_lines.append("\n**Timestamps**:")
    response_lines.append(f"Telegram Time: *{telegram_time.strftime('%B %d, %Y %H:%M:%S UTC')}*")
    response_lines.append(f"Bot Time: *{bot_time.strftime('%B %d, %Y %H:%M:%S UTC')}*")

    # Add performance metrics
    response_lines.append("\n**Performance Metrics**:")
    response_lines.append(f"Latency: *{latency:.2f}* seconds")
    
    # Capture end time for performance measurement (before sending)
    end_time = datetime.now(timezone.utc)
    processing_time = (end_time - start_time).total_seconds()  # In seconds
    response_lines.append(f"Processing Time: *{processing_time:.2f}* seconds")

    response = "\n".join(response_lines)
    await send_markdown_message(message, response)

    # Optionally send profile photo if available
    if profile_photo_file_id:
        await message.answer_photo(profile_photo_file_id, caption="Your current profile photo")