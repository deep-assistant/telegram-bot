import logging
from aiogram import Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command

from bot.commands import search_command, search_text
from bot.filters import TextCommand
from services.web_search_service import web_search_service

searchRouter = Router()

logger = logging.getLogger(__name__)


@searchRouter.message(Command("search"))
@searchRouter.message(TextCommand(search_command()))
@searchRouter.message(TextCommand(search_text()))
async def search_handler(message: Message):
    """Handle search command"""
    try:
        # Extract search query from message
        query = ""
        if message.text:
            # Remove command prefix
            text = message.text.strip()
            if text.startswith("/search"):
                query = text[7:].strip()
            elif text == search_text():
                # No query provided with button click
                await message.answer(
                    "🔍 Для поиска отправьте команду в формате:\n"
                    "`/search ваш запрос`\n\n"
                    "Например: `/search новости искусственный интеллект`",
                    parse_mode="Markdown"
                )
                return
            else:
                query = text
        
        if not query:
            await message.answer(
                "🔍 Для поиска отправьте команду в формате:\n"
                "`/search ваш запрос`\n\n"
                "Например: `/search новости искусственный интеллект`",
                parse_mode="Markdown"
            )
            return
        
        # Send "searching" message
        status_message = await message.answer(
            f"🔍 Поиск информации по запросу: *{query}*\n"
            "⏳ Ищем в различных поисковых системах...",
            parse_mode="Markdown"
        )
        
        # Perform search
        search_response = await web_search_service.search(query, max_results=8)
        
        if not search_response.results:
            await status_message.edit_text(
                f"🔍 Поиск по запросу: *{query}*\n"
                "❌ К сожалению, ничего не найдено. Попробуйте изменить запрос.",
                parse_mode="Markdown"
            )
            return
        
        # Format results
        response_text = f"🔍 Результаты поиска по запросу: *{query}*\n\n"
        
        for i, result in enumerate(search_response.results, 1):
            # Limit snippet length for readability
            snippet = result.snippet[:150] + "..." if len(result.snippet) > 150 else result.snippet
            
            response_text += f"*{i}. {result.title}*\n"
            response_text += f"{snippet}\n"
            response_text += f"🔗 [Читать полностью]({result.url})\n"
            response_text += f"📍 Источник: {result.source}\n\n"
        
        # Add summary
        sources_text = ", ".join(search_response.sources_used)
        response_text += f"📊 Найдено {search_response.total_results} результатов из источников: {sources_text}"
        
        # Create keyboard for new search
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Новый поиск", callback_data="new_search")]
        ])
        
        # Update the status message with results
        await status_message.edit_text(
            response_text,
            parse_mode="Markdown",
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        await message.answer(
            "❌ Произошла ошибка при поиске. Попробуйте еще раз.",
            parse_mode="Markdown"
        )


@searchRouter.callback_query(lambda c: c.data == "new_search")
async def new_search_callback(callback_query):
    """Handle new search button"""
    await callback_query.answer()
    await callback_query.message.answer(
        "🔍 Отправьте новый запрос для поиска:\n"
        "`/search ваш запрос`",
        parse_mode="Markdown"
    )