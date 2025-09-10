import logging
from datetime import datetime, timezone

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from bot.filters import TextCommand
from bot.gpt.utils import send_markdown_message
from .service import ErrorReportingService

errorReportingRouter = Router()


def is_admin(user_id: int) -> bool:
    """Check if user is an administrator"""
    service = ErrorReportingService()
    return user_id in service.admin_user_ids


@errorReportingRouter.message(Command("errors"))
async def handle_errors_command(message: Message):
    """Show recent error reports (admin only)"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Недостаточно прав доступа.")
        return
    
    service = ErrorReportingService()
    errors = await service.get_recent_errors(limit=5)
    
    if not errors:
        await message.answer("✅ Ошибок не найдено.")
        return
    
    response_lines = ["🔍 **Последние ошибки:**", ""]
    
    for i, error in enumerate(errors[:5], 1):
        timestamp = datetime.fromisoformat(error['timestamp']).strftime('%d.%m.%Y %H:%M:%S')
        context = error['context']
        
        response_lines.extend([
            f"**{i}. {error['exception_type']}**",
            f"📅 `{timestamp}`",
            f"💬 `{error['exception_message'][:100]}{'...' if len(error['exception_message']) > 100 else ''}`"
        ])
        
        if context.get('user_id'):
            response_lines.append(f"👤 Пользователь: `{context['user_id']}`")
        if context.get('chat_id'):
            response_lines.append(f"💭 Чат: `{context['chat_id']}`")
        
        response_lines.append("")
    
    response_lines.extend([
        "Используйте `/error_detail <номер>` для подробностей",
        "Используйте `/clear_errors` для очистки журнала"
    ])
    
    response = '\n'.join(response_lines)
    await send_markdown_message(message, response)


@errorReportingRouter.message(Command("error_detail"))
async def handle_error_detail_command(message: Message):
    """Show detailed error information (admin only)"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Недостаточно прав доступа.")
        return
    
    # Parse error number from command
    args = message.text.split()[1:] if message.text else []
    if not args or not args[0].isdigit():
        await message.answer("❌ Укажите номер ошибки: `/error_detail 1`")
        return
    
    error_num = int(args[0])
    service = ErrorReportingService()
    errors = await service.get_recent_errors(limit=10)
    
    if error_num < 1 or error_num > len(errors):
        await message.answer(f"❌ Ошибка с номером {error_num} не найдена.")
        return
    
    error = errors[error_num - 1]
    
    # Format detailed error message
    timestamp = datetime.fromisoformat(error['timestamp']).strftime('%d.%m.%Y %H:%M:%S UTC')
    context = error['context']
    
    response_lines = [
        f"🔍 **Детали ошибки #{error_num}**",
        "",
        f"**Время:** `{timestamp}`",
        f"**Тип:** `{error['exception_type']}`",
        f"**Сообщение:** `{error['exception_message']}`",
        "",
        "**Контекст:**"
    ]
    
    for key, value in context.items():
        if value is not None:
            response_lines.append(f"• {key}: `{value}`")
    
    # Add traceback
    response_lines.extend([
        "",
        "**Трассировка:**",
        f"```\n{error['traceback']}\n```"
    ])
    
    response = '\n'.join(response_lines)
    
    # Handle message length limit
    if len(response) > 4000:
        # Send traceback as a separate message
        context_response = '\n'.join(response_lines[:-3])
        await send_markdown_message(message, context_response)
        
        traceback_response = f"**Трассировка ошибки #{error_num}:**\n```\n{error['traceback']}\n```"
        await send_markdown_message(message, traceback_response)
    else:
        await send_markdown_message(message, response)


@errorReportingRouter.message(Command("clear_errors"))
async def handle_clear_errors_command(message: Message):
    """Clear error log (admin only)"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Недостаточно прав доступа.")
        return
    
    service = ErrorReportingService()
    success = await service.clear_error_log()
    
    if success:
        await message.answer("✅ Журнал ошибок очищен.")
    else:
        await message.answer("❌ Не удалось очистить журнал ошибок.")


@errorReportingRouter.message(Command("test_error"))
async def handle_test_error_command(message: Message):
    """Test error reporting (admin only)"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Недостаточно прав доступа.")
        return
    
    # Trigger a test error
    raise RuntimeError("Тестовая ошибка для проверки системы отчетности")


@errorReportingRouter.message(Command("error_stats"))
async def handle_error_stats_command(message: Message):
    """Show error statistics (admin only)"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Недостаточно прав доступа.")
        return
    
    service = ErrorReportingService()
    errors = await service.get_recent_errors(limit=100)  # Get more for statistics
    
    if not errors:
        await message.answer("✅ Ошибок не найдено.")
        return
    
    # Calculate statistics
    error_types = {}
    recent_errors = 0
    now = datetime.now(timezone.utc)
    
    for error in errors:
        # Count by type
        error_type = error['exception_type']
        error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # Count recent errors (last 24 hours)
        error_time = datetime.fromisoformat(error['timestamp'])
        if (now - error_time).total_seconds() < 86400:  # 24 hours
            recent_errors += 1
    
    response_lines = [
        "📊 **Статистика ошибок**",
        "",
        f"📈 Всего ошибок: `{len(errors)}`",
        f"🕐 За последние 24 часа: `{recent_errors}`",
        "",
        "**По типам:**"
    ]
    
    # Sort by frequency
    sorted_types = sorted(error_types.items(), key=lambda x: x[1], reverse=True)
    for error_type, count in sorted_types[:10]:  # Top 10
        response_lines.append(f"• `{error_type}`: {count}")
    
    response = '\n'.join(response_lines)
    await send_markdown_message(message, response)