from datetime import datetime
from aiogram import Router, types
from aiogram.filters import Command

from bot.filters import TextCommand
from bot.commands import remind_command, remind_command_text, list_reminders_command, cancel_reminder_command
from services.reminder_service import reminderService
from bot.gpt.utils import send_markdown_message

reminderRouter = Router()


@reminderRouter.message(Command("remind"))
async def handle_remind_command(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text
    
    if not text or len(text.strip()) <= 7:  # "/remind" is 7 characters
        await message.answer(
            "📅 **Система напоминаний**\n\n"
            "Использование: `/remind \"через время напомни о чем-то\"`\n\n"
            "**Примеры:**\n"
            "• `/remind \"через 30 минут проверить почту\"`\n"
            "• `/remind \"через 2 часа встреча с командой\"`\n"
            "• `/remind \"через 1 день сделать отчет\"`\n"
            "• `/remind \"через 1 неделю запланировать отпуск\"`\n\n"
            "**Поддерживаемые единицы времени:**\n"
            "• секунды (сек)\n"
            "• минуты (мин)\n"
            "• часы\n"
            "• дни\n"
            "• недели\n\n"
            "**Дополнительные команды:**\n"
            "• `/list_reminders` - показать активные напоминания\n"
            "• `/cancel_reminder [ID]` - отменить напоминание",
            parse_mode="Markdown"
        )
        return
    
    reminder = await reminderService.create_reminder(user_id, chat_id, text, message.bot)
    
    if reminder:
        trigger_time_str = reminder.trigger_time.strftime("%d.%m.%Y в %H:%M")
        await message.answer(
            f"✅ **Напоминание создано!**\n\n"
            f"📝 **Сообщение:** {reminder.message}\n"
            f"⏰ **Время:** {trigger_time_str}\n"
            f"🆔 **ID:** `{reminder.id}`\n\n"
            f"Используйте `/cancel_reminder {reminder.id}` для отмены",
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            "❌ **Не удалось создать напоминание**\n\n"
            "Проверьте формат времени. Используйте:\n"
            "• `через X минут`\n"
            "• `через X часов`\n"
            "• `через X дней`\n"
            "• `через X недель`\n\n"
            "**Пример:** `/remind \"через 30 минут проверить почту\"`",
            parse_mode="Markdown"
        )


@reminderRouter.message(Command("list_reminders"))
async def handle_list_reminders_command(message: types.Message):
    user_id = message.from_user.id
    reminders = reminderService.get_user_reminders(user_id)
    
    if not reminders:
        await message.answer(
            "📭 **У вас нет активных напоминаний**\n\n"
            "Создайте новое напоминание командой `/remind`",
            parse_mode="Markdown"
        )
        return
    
    response = "📅 **Ваши активные напоминания:**\n\n"
    
    for reminder in reminders:
        trigger_time_str = reminder.trigger_time.strftime("%d.%m.%Y в %H:%M")
        response += (
            f"🆔 **ID:** `{reminder.id}`\n"
            f"📝 **Сообщение:** {reminder.message}\n"
            f"⏰ **Время:** {trigger_time_str}\n"
            f"🗑️ **Отменить:** `/cancel_reminder {reminder.id}`\n\n"
        )
    
    await send_markdown_message(message, response)


@reminderRouter.message(Command("cancel_reminder"))
async def handle_cancel_reminder_command(message: types.Message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    parts = text.split()
    if len(parts) < 2:
        await message.answer(
            "❌ **Неверный формат команды**\n\n"
            "Использование: `/cancel_reminder [ID]`\n\n"
            "Чтобы узнать ID напоминания, используйте `/list_reminders`",
            parse_mode="Markdown"
        )
        return
    
    reminder_id = parts[1]
    success = reminderService.cancel_reminder(user_id, reminder_id)
    
    if success:
        await message.answer(
            f"✅ **Напоминание отменено**\n\n"
            f"Напоминание с ID `{reminder_id}` было успешно удалено.",
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            f"❌ **Напоминание не найдено**\n\n"
            f"Напоминание с ID `{reminder_id}` не существует или уже отменено.\n\n"
            f"Используйте `/list_reminders` для просмотра активных напоминаний.",
            parse_mode="Markdown"
        )


@reminderRouter.message(TextCommand([remind_command_text()]))
async def handle_remind_text_command(message: types.Message):
    await message.answer(
        "📅 **Система напоминаний**\n\n"
        "Чтобы создать напоминание, используйте команду `/remind`\n\n"
        "**Пример:** `/remind \"через 30 минут проверить почту\"`",
        parse_mode="Markdown"
    )