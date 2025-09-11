from enum import Enum

from aiogram import Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from bot.filters import TextCommandQuery
from services.agreement_service import agreementService

agreementRouter = Router()


class AgreementStatuses(Enum):
    ACCEPT_AGREEMENT = "accept_agreement"
    DECLINE_AGREEMENT = "decline_agreement"


async def agreement_handler(message: Message) -> bool:
    is_agreement = agreementService.get_agreement_status(message.from_user.id)

    if not is_agreement:
        await message.answer(
            text="📑 Вы ознакомлены и принимаете [пользовательское соглашение](https://deep-assistant.github.io/telegram-bot/) и [политику конфиденциальности](https://deep-assistant.github.io/telegram-bot/privacy.html)?",
            reply_markup=InlineKeyboardMarkup(
                resize_keyboard=True,
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="Да ✅", callback_data=AgreementStatuses.ACCEPT_AGREEMENT.value),
                        InlineKeyboardButton(text="Нет ❌", callback_data=AgreementStatuses.DECLINE_AGREEMENT.value)
                    ],
                ]
            )
        )

    return is_agreement


@agreementRouter.callback_query(
    TextCommandQuery([AgreementStatuses.ACCEPT_AGREEMENT.value, AgreementStatuses.DECLINE_AGREEMENT.value])
)
async def handle_change_system_message_query(callback_query: CallbackQuery):
    if callback_query.data == AgreementStatuses.ACCEPT_AGREEMENT.value:
        await callback_query.answer("Успешно! Спасибо! 🥰")
        agreementService.set_agreement_status(callback_query.from_user.id, True)
        await callback_query.message.delete()

    if callback_query.data == AgreementStatuses.DECLINE_AGREEMENT.value:
        await callback_query.answer(
            "К сожалению, мы не можем вам предоставить функционал без подтверждения согласия! ☹️")

    await callback_query.message.delete()
