import { Router } from 'aiogram'; // Stub import

export const agreementRouter = new Router();

export const AgreementStatuses = {
  ACCEPT_AGREEMENT: 'accept_agreement',
  DECLINE_AGREEMENT: 'decline_agreement'
};

import { TextCommandQuery } from '../filters.js';
import { agreementService } from '../../services/index.js';

export async function agreementHandler(message) {
  const isAgreement = agreementService.get_agreement_status(message.from_user.id);

  if (!isAgreement) {
    await message.answer(
      '📑 Вы ознакомлены и принимаете [пользовательское соглашение](https://grigoriy-grisha.github.io/chat_gpt_agreement/) и [политику конфиденциальности](https://grigoriy-grisha.github.io/chat_gpt_agreement/PrivacyPolicy)?',
      {
        reply_markup: {
          resize_keyboard: true,
          inline_keyboard: [
            [
              { text: 'Да ✅', callback_data: AgreementStatuses.ACCEPT_AGREEMENT },
              { text: 'Нет ❌', callback_data: AgreementStatuses.DECLINE_AGREEMENT }
            ]
          ]
        }
      }
    );
  }

  return isAgreement;
}

// Callback query handler for agreement buttons
agreementRouter.callbackQuery(
  TextCommandQuery([AgreementStatuses.ACCEPT_AGREEMENT, AgreementStatuses.DECLINE_AGREEMENT]),
  async (callbackQuery) => {
    if (callbackQuery.data === AgreementStatuses.ACCEPT_AGREEMENT) {
      await callbackQuery.answer('Успешно! Спасибо! 🥰');
      agreementService.set_agreement_status(callbackQuery.from_user.id, true);
      await callbackQuery.message.delete();
    }

    if (callbackQuery.data === AgreementStatuses.DECLINE_AGREEMENT) {
      await callbackQuery.answer('К сожалению, мы не можем вам предоставить функционал без подтверждения согласия! ☹️');
    }

    await callbackQuery.message.delete();
  }
);
