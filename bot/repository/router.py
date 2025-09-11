import asyncio

from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from bot.commands import (
    repository_command, repository_text,
    show_repository_command, show_repository_text,
    clear_repository_command, clear_repository_text
)
from bot.filters import TextCommand
from services.repository_service import repositoryService
from services.state_service import stateService, StateTypes

repositoryRouter = Router()


@repositoryRouter.message(TextCommand([repository_command(), repository_text()]))
async def handle_set_repository(message: Message):
    """Handle /repo command to set repository URL"""
    user_id = str(message.from_user.id)
    
    # Check if URL is provided with the command
    text_parts = message.text.split(' ', 1)
    if len(text_parts) > 1:
        repository_url = text_parts[1].strip()
        
        # Validate the GitHub URL
        if repositoryService.validate_github_url(repository_url):
            repositoryService.set_current_repository(user_id, repository_url)
            repo_info = repositoryService.parse_repository_info(repository_url)
            
            await message.answer(f"""✅ Репозиторий успешно установлен!

📁 **{repo_info['full_name']}**
🔗 {repo_info['url']}

Теперь бот будет учитывать контекст этого репозитория при ответах на ваши вопросы.""")
        else:
            await message.answer("""❌ Неверный формат URL репозитория.

Пожалуйста, используйте формат: https://github.com/owner/repository

**Пример:**
/repo https://github.com/torvalds/linux""")
    else:
        await message.answer("""📁 **Установка репозитория**

Для установки репозитория используйте команду:
`/repo <URL_репозитория>`

**Пример:**
/repo https://github.com/torvalds/linux

**Другие команды:**
/show_repo - показать текущий репозиторий
/clear_repo - очистить репозиторий""")


@repositoryRouter.message(TextCommand([show_repository_command(), show_repository_text()]))
async def handle_show_repository(message: Message):
    """Handle /show_repo command to show current repository"""
    user_id = str(message.from_user.id)
    repository_url = repositoryService.get_current_repository(user_id)
    
    if repository_url:
        repo_info = repositoryService.parse_repository_info(repository_url)
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🗑️ Очистить репозиторий", callback_data="clear_repository")]
            ]
        )
        
        await message.answer(f"""📁 **Текущий репозиторий:**

📋 **{repo_info['full_name']}**
🔗 {repo_info['url']}

Бот учитывает контекст этого репозитория при ответах.""", reply_markup=keyboard)
    else:
        await message.answer("""📁 **Репозиторий не установлен**

Для установки используйте:
`/repo <URL_репозитория>`

**Пример:**
/repo https://github.com/torvalds/linux""")


@repositoryRouter.message(TextCommand([clear_repository_command(), clear_repository_text()]))
async def handle_clear_repository(message: Message):
    """Handle /clear_repo command to clear repository"""
    user_id = str(message.from_user.id)
    repository_url = repositoryService.get_current_repository(user_id)
    
    if repository_url:
        repositoryService.clear_current_repository(user_id)
        await message.answer("✅ Репозиторий успешно очищен!")
    else:
        await message.answer("📁 Репозиторий не был установлен.")


@repositoryRouter.callback_query(lambda c: c.data == "clear_repository")
async def handle_clear_repository_callback(callback_query):
    """Handle clear repository callback from inline button"""
    user_id = str(callback_query.from_user.id)
    repositoryService.clear_current_repository(user_id)
    
    await callback_query.message.edit_text("✅ Репозиторий успешно очищен!")
    await callback_query.answer("Репозиторий очищен")