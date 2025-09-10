from datetime import datetime, timedelta
import json

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from services import statisticsService
import config

# Create router for statistics commands
statisticsRouter = Router()

def is_admin(user_id: int) -> bool:
    """Check if user is admin."""
    return user_id in getattr(config, 'ADMIN_IDS', [])

def format_number(num: int) -> str:
    """Format number with thousands separator."""
    return f"{num:,}".replace(",", " ")

def create_stats_keyboard():
    """Create inline keyboard for statistics navigation."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Сегодня", callback_data="stats_today"),
                InlineKeyboardButton(text="📅 Вчера", callback_data="stats_yesterday")
            ],
            [
                InlineKeyboardButton(text="📈 Неделя", callback_data="stats_week"),
                InlineKeyboardButton(text="📊 Месяц", callback_data="stats_month")
            ],
            [
                InlineKeyboardButton(text="🤖 Модели", callback_data="stats_models"),
                InlineKeyboardButton(text="⏰ По времени", callback_data="stats_time")
            ],
            [
                InlineKeyboardButton(text="💰 Токены", callback_data="stats_tokens")
            ]
        ]
    )
    return keyboard

def format_daily_stats(date: datetime, title: str) -> str:
    """Format daily statistics message."""
    try:
        daily_users = statisticsService.get_daily_users_count(date)
        token_stats = statisticsService.get_token_statistics(date)
        model_stats = statisticsService.get_model_statistics(date)
        
        message = f"📊 *{title}* ({date.strftime('%d.%m.%Y')})\n\n"
        
        # Users
        message += f"👥 *Пользователи:* {format_number(daily_users)}\n\n"
        
        # Tokens
        total_spent = token_stats.get("total_spent", 0)
        message += f"⚡️ *Потрачено токенов:* {format_number(total_spent)}\n"
        
        if token_stats.get("by_model"):
            message += "\n*По моделям:*\n"
            for model, tokens in sorted(token_stats["by_model"].items(), key=lambda x: x[1], reverse=True):
                message += f"• {model}: {format_number(tokens)} ⚡️\n"
        
        # Models usage
        if model_stats:
            message += "\n*Использование моделей:*\n"
            for model_mode, data in sorted(model_stats.items(), key=lambda x: x[1].get("count", 0), reverse=True):
                count = data.get("count", 0)
                users = len(data.get("users", []))
                message += f"• {model_mode}: {count} запросов ({users} польз.)\n"
        
        return message
        
    except Exception as e:
        print(f"Error formatting daily stats: {e}")
        return f"❌ Ошибка при получении статистики за {date.strftime('%d.%m.%Y')}"

def format_period_stats(start_date: datetime, end_date: datetime, title: str) -> str:
    """Format statistics for a period."""
    try:
        period_stats = statisticsService.get_period_statistics(start_date, end_date)
        
        message = f"📊 *{title}*\n"
        message += f"📅 {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}\n\n"
        
        # Daily users summary
        daily_users = period_stats.get("daily_users", [])
        total_unique_users = len(set([user for day in daily_users for user in day.get("users", [])]))
        avg_daily_users = sum([day.get("users", 0) for day in daily_users]) / len(daily_users) if daily_users else 0
        
        message += f"👥 *Пользователи:*\n"
        message += f"• Уникальных за период: {format_number(total_unique_users)}\n"
        message += f"• Среднее в день: {format_number(int(avg_daily_users))}\n\n"
        
        # Token statistics
        total_tokens = period_stats.get("total_tokens_spent", 0)
        message += f"⚡️ *Токены:*\n"
        message += f"• Всего потрачено: {format_number(total_tokens)}\n"
        
        tokens_by_model = period_stats.get("tokens_by_model", {})
        if tokens_by_model:
            message += "• По моделям:\n"
            for model, tokens in sorted(tokens_by_model.items(), key=lambda x: x[1], reverse=True)[:5]:
                message += f"  - {model}: {format_number(tokens)} ⚡️\n"
        
        # Model usage summary
        model_usage = period_stats.get("model_usage", {})
        if model_usage:
            message += "\n*🤖 Модели:*\n"
            for model_mode, data in sorted(model_usage.items(), key=lambda x: x[1].get("count", 0), reverse=True)[:5]:
                count = data.get("count", 0)
                users = data.get("unique_users", 0)
                message += f"• {model_mode}: {count} запросов ({users} польз.)\n"
        
        return message
        
    except Exception as e:
        print(f"Error formatting period stats: {e}")
        return f"❌ Ошибка при получении статистики за период"

def format_time_stats(date: datetime = None) -> str:
    """Format usage time statistics."""
    try:
        if date is None:
            date = datetime.now()
            
        usage_stats = statisticsService.get_usage_time_statistics(date)
        
        message = f"⏰ *Статистика по времени* ({date.strftime('%d.%m.%Y')})\n\n"
        
        if not usage_stats or not any(usage_stats.values()):
            message += "📊 Нет данных об активности за этот день"
            return message
        
        # Calculate total activity per hour
        hourly_totals = {}
        for hour, activities in usage_stats.items():
            total = sum(activities.values())
            hourly_totals[hour] = total
        
        # Find peak hours
        sorted_hours = sorted(hourly_totals.items(), key=lambda x: x[1], reverse=True)
        peak_hours = [hour for hour, total in sorted_hours[:3] if total > 0]
        
        if peak_hours:
            message += "*🔥 Пиковые часы:*\n"
            for hour in peak_hours[:3]:
                total = hourly_totals[hour]
                message += f"• {hour}: {format_number(total)} действий\n"
            message += "\n"
        
        # Show hourly breakdown (only hours with activity)
        active_hours = [(hour, total) for hour, total in sorted_hours if total > 0]
        if active_hours:
            message += "*📈 Активность по часам:*\n"
            for hour, total in active_hours:
                # Create simple bar chart
                bar_length = min(10, max(1, int(total / max(hourly_totals.values()) * 10)))
                bar = "█" * bar_length + "░" * (10 - bar_length)
                message += f"`{hour} {bar}` {total}\n"
        
        return message
        
    except Exception as e:
        print(f"Error formatting time stats: {e}")
        return f"❌ Ошибка при получении статистики по времени"

async def format_token_balance_stats() -> str:
    """Format token balance statistics from API."""
    try:
        balance_stats = await statisticsService.get_token_balance_statistics()
        
        message = "💰 *Статистика токенов*\n\n"
        
        if "error" in balance_stats:
            message += f"❌ Ошибка получения данных: {balance_stats['error']}"
            return message
        
        # Format API response (structure depends on actual API)
        if "total_purchased" in balance_stats:
            message += f"🛒 *Куплено токенов:* {format_number(balance_stats['total_purchased'])}\n"
        
        if "total_spent" in balance_stats:
            message += f"💸 *Потрачено токенов:* {format_number(balance_stats['total_spent'])}\n"
        
        if "current_balance" in balance_stats:
            message += f"💳 *Текущий баланс:* {format_number(balance_stats['current_balance'])}\n"
        
        return message
        
    except Exception as e:
        print(f"Error formatting token balance stats: {e}")
        return "❌ Ошибка при получении статистики токенов"

@statisticsRouter.message(Command("stats"))
async def cmd_statistics(message: Message):
    """Main statistics command."""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Доступ запрещен. Команда только для администраторов.")
        return
    
    await message.answer(
        "📊 *Статистика бота*\n\nВыберите период или тип статистики:",
        reply_markup=create_stats_keyboard(),
        parse_mode="Markdown"
    )

@statisticsRouter.callback_query(F.data == "stats_today")
async def show_today_stats(callback_query: CallbackQuery):
    """Show today's statistics."""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    today = datetime.now()
    stats_message = format_daily_stats(today, "Статистика сегодня")
    
    await callback_query.message.edit_text(
        stats_message,
        reply_markup=create_stats_keyboard(),
        parse_mode="Markdown"
    )
    await callback_query.answer()

@statisticsRouter.callback_query(F.data == "stats_yesterday")
async def show_yesterday_stats(callback_query: CallbackQuery):
    """Show yesterday's statistics."""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    yesterday = datetime.now() - timedelta(days=1)
    stats_message = format_daily_stats(yesterday, "Статистика вчера")
    
    await callback_query.message.edit_text(
        stats_message,
        reply_markup=create_stats_keyboard(),
        parse_mode="Markdown"
    )
    await callback_query.answer()

@statisticsRouter.callback_query(F.data == "stats_week")
async def show_week_stats(callback_query: CallbackQuery):
    """Show this week's statistics."""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    today = datetime.now()
    week_start = today - timedelta(days=7)
    stats_message = format_period_stats(week_start, today, "Статистика за неделю")
    
    await callback_query.message.edit_text(
        stats_message,
        reply_markup=create_stats_keyboard(),
        parse_mode="Markdown"
    )
    await callback_query.answer()

@statisticsRouter.callback_query(F.data == "stats_month")
async def show_month_stats(callback_query: CallbackQuery):
    """Show this month's statistics."""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    today = datetime.now()
    month_start = today - timedelta(days=30)
    stats_message = format_period_stats(month_start, today, "Статистика за месяц")
    
    await callback_query.message.edit_text(
        stats_message,
        reply_markup=create_stats_keyboard(),
        parse_mode="Markdown"
    )
    await callback_query.answer()

@statisticsRouter.callback_query(F.data == "stats_models")
async def show_models_stats(callback_query: CallbackQuery):
    """Show model usage statistics."""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    today = datetime.now()
    model_stats = statisticsService.get_model_statistics(today)
    
    message = f"🤖 *Статистика моделей* ({today.strftime('%d.%m.%Y')})\n\n"
    
    if not model_stats:
        message += "📊 Нет данных об использовании моделей за сегодня"
    else:
        total_requests = sum(data.get("count", 0) for data in model_stats.values())
        message += f"🔢 *Всего запросов:* {format_number(total_requests)}\n\n"
        
        for model_mode, data in sorted(model_stats.items(), key=lambda x: x[1].get("count", 0), reverse=True):
            count = data.get("count", 0)
            users = len(data.get("users", []))
            percentage = (count / total_requests * 100) if total_requests > 0 else 0
            
            message += f"*{model_mode}*\n"
            message += f"• Запросов: {format_number(count)} ({percentage:.1f}%)\n"
            message += f"• Пользователей: {format_number(users)}\n\n"
    
    await callback_query.message.edit_text(
        message,
        reply_markup=create_stats_keyboard(),
        parse_mode="Markdown"
    )
    await callback_query.answer()

@statisticsRouter.callback_query(F.data == "stats_time")
async def show_time_stats(callback_query: CallbackQuery):
    """Show usage time statistics."""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    stats_message = format_time_stats()
    
    await callback_query.message.edit_text(
        stats_message,
        reply_markup=create_stats_keyboard(),
        parse_mode="Markdown"
    )
    await callback_query.answer()

@statisticsRouter.callback_query(F.data == "stats_tokens")
async def show_tokens_stats(callback_query: CallbackQuery):
    """Show token balance statistics."""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    stats_message = await format_token_balance_stats()
    
    await callback_query.message.edit_text(
        stats_message,
        reply_markup=create_stats_keyboard(),
        parse_mode="Markdown"
    )
    await callback_query.answer()

# Debug command for testing (remove in production)
@statisticsRouter.message(Command("teststats"))
async def cmd_test_statistics(message: Message):
    """Test command to generate sample statistics data."""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Доступ запрещен")
        return
    
    # Generate some test data
    user_id = str(message.from_user.id)
    
    statisticsService.track_user_activity(user_id, "message")
    statisticsService.track_token_usage(user_id, 150, "gpt-4")
    statisticsService.track_model_usage(user_id, "gpt-4", "default")
    
    await message.answer("✅ Тестовые данные добавлены в статистику")