import asyncio
import re
import json
import io
from datetime import datetime
from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, BufferedInputFile

from bot.filters import TextCommand, StartWithQuery, StateCommand
from services import (
    transferService,
    tokenizeService,
    stateService,
    StateTypes
)
from bot.utils import get_user_name

transferRouter = Router()

# Временное хранилище данных переводов
transfer_data = {}

def create_transfer_confirmation_keyboard(transfer_id: str):
    """Клавиатура подтверждения перевода"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить",
                    callback_data=f"transfer_confirm {transfer_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data=f"transfer_cancel {transfer_id}"
                ),
            ]
        ]
    )

@transferRouter.message(TextCommand(["/cancel"]))
async def cancel_command(message: types.Message):
    """Отмена через команду"""
    user_id = message.from_user.id
    current_state = stateService.get_current_state(user_id)
    
    if current_state in [StateTypes.TransferInputReceiver, StateTypes.TransferInputAmount]:
        if user_id in transfer_data:
            del transfer_data[user_id]
        
        stateService.set_current_state(user_id, StateTypes.Default)
        
        await message.answer(
            "❌ Перевод отменён\n\n"
            "/transfer - Начать новый перевод"
        )
    else:
        await message.answer(
            "Нет активного перевода для отмены\n\n"
            "/transfer - Начать перевод"
        )

@transferRouter.message(TextCommand(["/transfer_history", "📜 История переводов", "📜 История"]))
async def transfer_history_command(message: types.Message):
    """История переводов"""
    user_id = message.from_user.id
    
    loading = await message.answer("⏳ Загружаю историю...")
    
    history = await transferService.get_history(user_id, limit=50)
    
    if not history or len(history) == 0:
        await loading.delete()
        await message.answer(
            "📜 <b>История переводов пуста</b>\n\n"
            "/transfer - Сделать перевод",
            parse_mode="HTML"
        )
        return
    
    # Подготовить данные для JSON файла
    current_user_id = get_user_name(user_id)
    
    formatted_history = []
    for transfer in history:
        is_sent = transfer["sender"]["user_id"] == current_user_id
        
        formatted_history.append({
            "type": "sent" if is_sent else "received",
            "transfer_id": transfer["id"],
            "amount": transfer["amounts"]["transfer"],
            "fee": transfer["amounts"]["fee"],
            "total": transfer["amounts"]["total_debited"],
            "sender": {
                "user_id": transfer["sender"]["user_id"],
                "username": transfer["sender"]["username"],
                "full_name": transfer["sender"]["full_name"]
            },
            "receiver": {
                "user_id": transfer["receiver"]["user_id"],
                "username": transfer["receiver"]["username"],
                "full_name": transfer["receiver"]["full_name"]
            },
            "timestamp": transfer["timestamp"],
            "status": transfer["status"]
        })
    
    # Создать JSON файл
    json_data = json.dumps({
        "user_id": current_user_id,
        "export_date": datetime.now().isoformat(),
        "total_transfers": len(formatted_history),
        "history": formatted_history
    }, ensure_ascii=False, indent=2)
    
    # Отправить файл
    file_stream = io.BytesIO(json_data.encode('utf-8'))
    filename = f"transfer_history_{user_id}.json"
    
    input_file = BufferedInputFile(file_stream.read(), filename=filename)
    
    # Краткая статистика в сообщении
    text = "📜 <b>ИСТОРИЯ ПЕРЕВОДОВ</b>\n\n"
    text += f"📊 Всего переводов: {len(formatted_history)}\n\n"
    
    sent_count = sum(1 for t in formatted_history if t["type"] == "sent")
    received_count = sum(1 for t in formatted_history if t["type"] == "received")
    
    text += f"📤 Отправлено: {sent_count}\n"
    text += f"📥 Получено: {received_count}\n\n"
    
    # Последние 5 переводов
    text += "<b>Последние 5 переводов:</b>\n\n"
    for transfer in formatted_history[:5]:
        icon = "📤" if transfer["type"] == "sent" else "📥"
        other = transfer["receiver"] if transfer["type"] == "sent" else transfer["sender"]
        direction = "→" if transfer["type"] == "sent" else "←"
        
        timestamp = datetime.fromisoformat(transfer["timestamp"].replace('Z', '+00:00'))
        date_str = timestamp.strftime('%d.%m %H:%M')
        
        status_icon = "✅" if transfer["status"] == "completed" else "❌"
        
        text += f"{icon} <b>{transfer['amount']:,}⚡️</b> {direction} {other['username']}\n"
        text += f"   {status_icon} {date_str}\n\n"
    
    text += "\n/transfer - Новый перевод"
    
    await loading.delete()
    await message.answer_document(input_file, caption=text, parse_mode="HTML")

@transferRouter.message(TextCommand(["/transfer", "💸 Перевести энергию", "💸 Перевести"]))
async def start_transfer(message: types.Message):
    """Начать процесс перевода"""
    user_id = message.from_user.id
    
    # Получить настройки
    settings = await transferService.get_settings()
    if not settings or not settings.get("enabled"):
        await message.answer(
            "❌ Переводы временно недоступны\n"
            "Попробуйте позже"
        )
        return
    
    # Проверка баланса и премиума
    tokens = await tokenizeService.get_tokens(user_id)
    balance = tokens.get("tokens", 0)
    
    min_required = settings["limits"]["min_balance_required"]
    
    # TODO: Получить реальный премиум статус когда будет реализован
    is_premium = False
    
    has_access = balance >= min_required or is_premium
    
    if not has_access:
        await message.answer(
            f"❌ <b>Недостаточно прав для переводов</b>\n\n"
            f"Для доступа к переводам нужно:\n"
            f"• Баланс от <b>{min_required:,}⚡️</b> (у вас: {balance:,}⚡️)\n"
            f"ИЛИ\n"
            f"• Премиум статус 👑\n\n"
            f"/buy - Пополнить баланс",
            parse_mode="HTML"
        )
        return
    
    # Получить статистику за сегодня
    stats = await transferService.get_stats(user_id)
    today_count = stats["today"]["count"] if stats and stats.get("today") else 0
    
    # Лимиты
    max_daily = settings["limits"]["max_daily_transfers_premium" if is_premium else "max_daily_transfers_regular"]
    fee_percent = settings["fees"]["premium_percent" if is_premium else "regular_percent"]
    
    # Установить состояние
    stateService.set_current_state(user_id, StateTypes.TransferInputReceiver)
    
    await message.answer(
        f"💸 <b>ПЕРЕВОД ЭНЕРГИИ</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Ваш баланс: <b>{balance:,}⚡️</b>\n"
        f"💳 Комиссия: <b>{fee_percent}%</b>\n\n"
        f"📊 <b>Лимиты:</b>\n"
        f"• Сегодня: {today_count}/{max_daily} переводов\n"
        f"• Минимум: {settings['limits']['min_transfer_amount']:,}⚡️\n"
        f"• Максимум: {settings['limits']['max_transfer_amount']:,}⚡️\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"Введите username получателя:\n"
        f"<code>@username</code>\n\n"
        f"Для отмены: /cancel",
        parse_mode="HTML"
    )

@transferRouter.message(StateCommand(StateTypes.TransferInputReceiver))
async def input_receiver(message: types.Message):
    """Обработка ввода получателя"""
    user_id = message.from_user.id
    receiver_username = message.text.strip()
    
    # Пропустить если это команда (она будет обработана другим handler)
    if receiver_username.startswith('/'):
        return
    
    # Валидация формата
    if not re.match(r'^@[a-zA-Z0-9_]{5,32}$', receiver_username):
        await message.answer(
            "❌ Неверный формат username\n\n"
            "Правильный формат: <code>@username</code>\n"
            "Telegram username должен содержать от 5 до 32 символов\n\n"
            "Попробуйте снова или /cancel для отмены",
            parse_mode="HTML"
        )
        return
    
    # Проверка: не самому себе
    sender_username = message.from_user.username
    if sender_username and receiver_username.lower() == f"@{sender_username.lower()}":
        await message.answer(
            "❌ Нельзя переводить самому себе\n\n"
            "Введите другой username или /cancel"
        )
        return
    
    # Проверка существования
    loading_msg = await message.answer("⏳ Проверяю пользователя...")
    
    check_result = await transferService.check_user_exists(receiver_username)
    
    await loading_msg.delete()
    
    if not check_result.get("exists"):
        await message.answer(
            f"❌ Пользователь {receiver_username} не найден в системе\n\n"
            f"<b>Возможные причины:</b>\n"
            f"• Пользователь не запускал бота (/start)\n"
            f"• Неверный username\n"
            f"• Опечатка в написании\n\n"
            f"Попробуйте снова или /cancel для отмены",
            parse_mode="HTML"
        )
        return
    
    # Получить актуальные данные получателя из Telegram
    receiver_id = check_result.get("user_id")
    receiver_username_clean = None
    receiver_full_name = "Unknown"
    
    try:
        receiver_chat = await message.bot.get_chat(receiver_id)
        receiver_username_clean = receiver_chat.username
        receiver_first_name = receiver_chat.first_name or ""
        receiver_last_name = receiver_chat.last_name or ""
        receiver_full_name = f"{receiver_first_name} {receiver_last_name}".strip()
        
        # Если не удалось получить имя, берем из БД
        if not receiver_full_name:
            receiver_full_name = check_result.get("full_name", "Unknown")
    except Exception as e:
        print(f"Failed to get receiver data from Telegram in check: {e}")
        # Используем данные из БД как fallback
        receiver_full_name = check_result.get("full_name", "Unknown")
    
    # Получить баланс
    tokens = await tokenizeService.get_tokens(user_id)
    balance = tokens.get("tokens", 0)
    
    # Сохранить данные
    transfer_data[user_id] = {
        "receiver_username": receiver_username,
        "receiver_id": receiver_id,
        "receiver_full_name": receiver_full_name,
        "receiver_username_clean": receiver_username_clean  # Для последующей синхронизации
    }
    
    # Следующий шаг
    stateService.set_current_state(user_id, StateTypes.TransferInputAmount)
    
    await message.answer(
        f"✅ Пользователь найден!\n\n"
        f"👤 Username: {receiver_username}\n"
        f"📝 Имя: <b>{check_result.get('full_name')}</b>\n\n"
        f"💰 Ваш баланс: <b>{balance:,}⚡️</b>\n\n"
        f"💸 Введите сумму для перевода:\n\n"
        f"Для отмены: /cancel",
        parse_mode="HTML"
    )

@transferRouter.message(StateCommand(StateTypes.TransferInputAmount))
async def input_amount(message: types.Message):
    """Обработка ввода суммы"""
    user_id = message.from_user.id
    
    # Пропустить если это команда (она будет обработана другим handler)
    if message.text.strip().startswith('/'):
        return
    
    # Проверить данные
    if user_id not in transfer_data:
        await message.answer(
            "❌ Данные перевода не найдены\n"
            "Начните заново: /transfer"
        )
        stateService.set_current_state(user_id, StateTypes.Default)
        return
    
    # Парсинг суммы
    try:
        amount_str = message.text.strip().replace(" ", "").replace(",", "")
        amount = int(amount_str)
    except ValueError:
        await message.answer(
            "❌ Неверный формат суммы\n\n"
            "Введите целое число, например:\n"
            "<code>1000</code> или <code>5000</code>\n\n"
            "Попробуйте снова или /cancel",
            parse_mode="HTML"
        )
        return
    
    # Получить настройки
    settings = await transferService.get_settings()
    min_amount = settings.get("limits", {}).get("min_transfer_amount", 100)
    max_amount = settings.get("limits", {}).get("max_transfer_amount", 100000)
    fee_percent = settings.get("fees", {}).get("regular_percent", 1.0)
    
    # Валидация суммы
    if amount < min_amount:
        await message.answer(
            f"❌ Минимальная сумма перевода: <b>{min_amount}⚡️</b>\n\n"
            f"Попробуйте снова или /cancel",
            parse_mode="HTML"
        )
        return
    
    if amount > max_amount:
        await message.answer(
            f"❌ Максимальная сумма перевода: <b>{max_amount:,}⚡️</b>\n\n"
            f"Попробуйте снова или /cancel",
            parse_mode="HTML"
        )
        return
    
    # Рассчитать комиссию
    fee = int(amount * fee_percent / 100)
    total = amount + fee
    
    # Проверка баланса
    tokens = await tokenizeService.get_tokens(user_id)
    balance = tokens.get("tokens", 0)
    
    if balance < total:
        await message.answer(
            f"❌ <b>Недостаточно средств</b>\n\n"
            f"Ваш баланс: <b>{balance:,}⚡️</b>\n"
            f"Сумма перевода: <b>{amount:,}⚡️</b>\n"
            f"Комиссия ({fee_percent}%): <b>{fee:,}⚡️</b>\n"
            f"Требуется: <b>{total:,}⚡️</b>\n"
            f"Не хватает: <b>{total - balance:,}⚡️</b>\n\n"
            f"/buy - Пополнить баланс\n"
            f"/cancel - Отменить перевод",
            parse_mode="HTML"
        )
        return
    
    # Сохранить сумму
    transfer_data[user_id]["amount"] = amount
    transfer_data[user_id]["fee"] = fee
    transfer_data[user_id]["total"] = total
    transfer_data[user_id]["balance_before"] = balance
    
    receiver_username = transfer_data[user_id]["receiver_username"]
    receiver_full_name = transfer_data[user_id]["receiver_full_name"]
    transfer_id = str(user_id)
    
    # Подтверждение
    await message.answer(
        f"💸 <b>ПОДТВЕРЖДЕНИЕ ПЕРЕВОДА</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Отправитель:</b>\n"
        f"   {message.from_user.first_name} {message.from_user.last_name or ''}\n\n"
        f"👤 <b>Получатель:</b>\n"
        f"   {receiver_username}\n"
        f"   {receiver_full_name}\n\n"
        f"💰 <b>Сумма:</b> {amount:,}⚡️\n"
        f"💳 <b>Комиссия ({fee_percent}%):</b> {fee:,}⚡️\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📤 <b>Будет списано:</b> <b>{total:,}⚡️</b>\n"
        f"📥 <b>Получатель получит:</b> <b>{amount:,}⚡️</b>\n\n"
        f"💼 <b>Баланс после:</b> {balance - total:,}⚡️\n\n"
        f"⚠️ <b>Отменить перевод после подтверждения будет невозможно!</b>",
        reply_markup=create_transfer_confirmation_keyboard(transfer_id),
        parse_mode="HTML"
    )

@transferRouter.callback_query(StartWithQuery("transfer_confirm"))
async def confirm_transfer(callback_query: CallbackQuery):
    """Подтверждение перевода"""
    user_id = callback_query.from_user.id
    
    # Проверить данные
    if user_id not in transfer_data:
        await callback_query.answer("❌ Данные перевода истекли", show_alert=True)
        await callback_query.message.delete()
        return
    
    data = transfer_data[user_id]
    
    # Выполнить
    await callback_query.message.edit_text("⏳ <b>Выполняю перевод...</b>", parse_mode="HTML")
    
    # Получить данные отправителя из Telegram
    sender_username = callback_query.from_user.username
    sender_first_name = callback_query.from_user.first_name or ""
    sender_last_name = callback_query.from_user.last_name or ""
    sender_full_name = f"{sender_first_name} {sender_last_name}".strip()
    
    # Получить актуальные данные получателя из Telegram (могли быть получены раньше)
    receiver_username = data.get("receiver_username_clean")
    receiver_full_name = data.get("receiver_full_name")
    
    # Если не были получены раньше, попробовать снова
    if not receiver_username or not receiver_full_name:
        try:
            receiver_chat = await callback_query.bot.get_chat(data["receiver_id"])
            receiver_username = receiver_chat.username
            receiver_first_name = receiver_chat.first_name or ""
            receiver_last_name = receiver_chat.last_name or ""
            receiver_full_name = f"{receiver_first_name} {receiver_last_name}".strip()
        except Exception as e:
            print(f"Failed to get receiver data from Telegram: {e}")
    
    result = await transferService.execute_transfer(
        get_user_name(user_id),
        data["receiver_id"],
        data["amount"],
        sender_username=sender_username,
        sender_full_name=sender_full_name if sender_full_name else None,
        receiver_username=receiver_username,
        receiver_full_name=receiver_full_name if receiver_full_name else None
    )
    
    if result.get("success"):
        # Успешно
        result_data = result["data"]
        
        transfer_id = str(result_data.get('transferId', 'N/A'))
        
        await callback_query.message.edit_text(
            f"✅ <b>ПЕРЕВОД ВЫПОЛНЕН УСПЕШНО!</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Получатель: {data['receiver_username']}\n"
            f"💰 Сумма: <b>{data['amount']:,}⚡️</b>\n"
            f"💳 Комиссия: <b>{data['fee']:,}⚡️</b>\n"
            f"📤 Списано: <b>{data['total']:,}⚡️</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"💼 Новый баланс: <b>{result_data['newBalance']:,}⚡️</b>\n\n"
            f"🆔 ID перевода: <code>{transfer_id}</code>\n\n"
            f"/transfer - Новый перевод\n"
            f"/transfer_history - История",
            parse_mode="HTML"
        )
        
        # Уведомить получателя
        try:
            sender_name = f"{callback_query.from_user.first_name} {callback_query.from_user.last_name or ''}".strip()
            sender_username = f"@{callback_query.from_user.username}" if callback_query.from_user.username else "Пользователь"
            
            await callback_query.bot.send_message(
                chat_id=data["receiver_id"],
                text=(
                    f"💰 <b>ВЫ ПОЛУЧИЛИ ПЕРЕВОД!</b>\n\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"👤 <b>От кого:</b>\n"
                    f"   {sender_username}\n"
                    f"   {sender_name}\n\n"
                    f"💵 <b>Сумма:</b> <b>{data['amount']:,}⚡️</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━\n\n"
                    f"/balance - Проверить баланс"
                ),
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Failed to notify receiver: {e}")
        
        await callback_query.answer("✅ Успешно!", show_alert=False)
    else:
        # Ошибка
        error_msg = result.get("error", "Неизвестная ошибка")
        
        await callback_query.message.edit_text(
            f"❌ <b>ОШИБКА ПЕРЕВОДА</b>\n\n"
            f"{error_msg}\n\n"
            f"Ваш баланс не изменён.\n"
            f"Попробуйте позже или обратитесь в поддержку.\n\n"
            f"/transfer - Попробовать снова",
            parse_mode="HTML"
        )
        await callback_query.answer("❌ Ошибка", show_alert=True)
    
    # Очистить
    del transfer_data[user_id]
    stateService.set_current_state(user_id, StateTypes.Default)

@transferRouter.callback_query(StartWithQuery("transfer_cancel"))
async def cancel_transfer(callback_query: CallbackQuery):
    """Отмена перевода"""
    user_id = callback_query.from_user.id
    
    if user_id in transfer_data:
        del transfer_data[user_id]
    
    stateService.set_current_state(user_id, StateTypes.Default)
    
    await callback_query.message.edit_text(
        "❌ Перевод отменён\n\n"
        "/transfer - Начать новый перевод"
    )
    await callback_query.answer("Отменено", show_alert=False)

