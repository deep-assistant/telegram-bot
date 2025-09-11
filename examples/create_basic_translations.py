#!/usr/bin/env python3
"""
Create basic translation files for the bot internationalization.
"""

import json
import os

def create_basic_translations():
    """Create basic translation files for key languages."""
    
    # Create translations directory
    os.makedirs('../bot/i18n/translations', exist_ok=True)
    
    # Basic Russian translations (current language)
    russian_translations = {
        "commands.start": "/start",
        "commands.help": "/help",
        "commands.balance": "/balance", 
        "commands.model": "/model",
        "commands.system": "/system",
        "commands.clear": "/clear",
        "commands.image": "/image",
        "commands.suno": "/suno", 
        "commands.buy": "/buy",
        "commands.referral": "/referral",
        "commands.api": "/api",
        "commands.app": "/app",

        "common.yes": "Да ✅",
        "common.no": "Нет ❌",
        "common.cancel": "Отмена ❌",
        "common.back": "Назад",
        "common.forward": "Вперед", 
        "common.error": "Ошибка",
        "common.success": "Успешно",
        "common.loading": "Загрузка...",
        "common.check": "Проверить ✅",
        "common.subscribe": "Подписаться 👊🏻",

        "menu.balance": "✨ Баланс",
        "menu.buy_balance": "💎 Пополнить баланс",
        "menu.change_model": "🛠️ Сменить модель", 
        "menu.change_mode": "⚙️ Сменить Режим",
        "menu.music_generation": "🎵 Генерация музыки",
        "menu.image_generation": "🖼️ Генерация картинки",
        "menu.clear_context": "🧹 Очистить контекст",
        "menu.chat_history": "📖 История диалога",
        "menu.referral_link": "🔗 Реферральная ссылка",
        "menu.help": "🆘 Помощь",
        "menu.donation": "💖 Пожертвование",

        "generate.action": "Сгенерировать 🔥",
        "generate.more": "Сгенерировать еще? 🔥",
        "generate.midjourney_more": "Cгенерировать Midjourney еще? 🔥",
        "generate.flux_more": "Cгенерировать Flux еще? 🔥",
        "generate.dalle_more": "Cгенерировать DALL·E 3 еще? 🔥",
        "generate.suno_more": "Cгенерировать Suno еще? 🔥",

        "models.gpt4o": "🤖 GPT-4o",
        "models.gpt35": "🦾 GPT-3.5",
        "models.current": "Модель: {model}",
        "models.size": "Размер: {size}",
        "models.steps": "Шаги: {steps}",
        "models.cfg_scale": "CFG Scale: {cfg}",

        "payment.choose_method": "Выбирете способ оплаты",
        "payment.telegram_stars": "Telegram Stars ⭐️",
        "payment.card_payment": "Оплата картой 💳", 
        "payment.pay_stars": "Оплатить {stars} ⭐️",
        "payment.back_to_method": "⬅️ Назад к выбору способа оплаты",

        "status.not_subscribed": "Вы не подписались! 😡",
        "status.image_original": "Вот ваше изображение в оригинальном качестве",
        "status.image_quality": "Вот картинка в оригинальном качестве",
        "status.context_cleared": "Контекст диалога успешно очищен! 👌🏻",
        "status.dialog_empty": "Диалог уже пуст!",

        "placeholder.ask_question": "💬 Задай свой вопрос",
        "placeholder.describe": "Опиши",

        "agreement.text": "📑 Вы ознакомлены и принимаете [пользовательское соглашение](https://grigoriy-grisha.github.io/chat_gpt_agreement/) и [политику конфиденциальности](https://grigoriy-grisha.github.io/chat_gpt_agreement/PrivacyPolicy)?",

        "error.not_enough_energy": "У вас не хватает *⚡️*. 😔\n\n/balance - ✨ Проверить Баланс\n/buy - 💎 Пополнить баланс \n/referral - 👥 Пригласить друга, чтобы получить бесплатно *⚡️*!\n/model - 🛠️ Сменить модель",
        "error.voice_not_recognized": "Error: Голосовое сообщение не распознано",
        "error.file_not_supported": "😔 К сожалению, данный тип файлов не поддерживается!\n\nСледите за обновлениями в канале @gptDeep или напишите нам в чате @deepGPT",
        "error.file_processing": "😔 К сожалению, при обработке файлов произошли ошибки:\n{error_text}\n\nСледите за обновлениями в канале @gptDeep",

        "welcome.hello": "👋 Привет! Я бот от разработчиков deep.foundation!\n\n🤖 Я готов помочь тебе с любой задачей, просто напиши сообщение или нажми кнопку в меню!\n\n/help - ✨ обзор команд и возможностей\n/balance - ⚡️ узнать свой баланс\n/referral - 🔗 подробности рефералки\n\nВсё бесплатно, если не платить.\nКаждый день твой баланс будет пополняться на сумму от *10 000⚡️* (энергии)!\n\nЕсли нужно больше:\n💎 Можно пополнить баланс Telegram звёздами или банковской картой.\n👥 Понравилось? Поделись с друзьями и получи бонус за каждого приглашенного друга! Приводя много друзей ты сможешь пользоваться нейросетями практически безлимитно.\n\n/referral - получай больше с реферальной системой:\n*5 000⚡️️* за каждого приглашенного пользователя;\n*+500⚡️️* к ежедневному пополнению баланса за каждого друга.\n\n🏠 Если что-то пошло не так или хочешь поделиться вдохновением, напиши в наше сообщество @deepGPT.",

        "referral.arrived": "👋 Ты прибыл по реферальной ссылке, чтобы получить награду нужно подписаться на мой канал.",
        "referral.reward": "🎉 Вы получили *5 000*⚡️!\n\n/balance - ✨ Узнать баланс\n/referral - 🔗 Подробности рефералки",
        "referral.new_referral": "🎉 Добавлен новый реферал! \nВы получили *5 000*⚡️!\nВаш реферал должен проявить любую активность в боте через 24 часа, чтобы вы получили еще *5 000*⚡️ и +500⚡️️ к ежедневному пополнению баланса.\n\n/balance - ✨ Узнать баланс\n/referral - 🔗 Подробности рефералки",

        "help.info": "Основной ресурc для доступа к нейросетям - ⚡️ (энергия).\nЭто универсальный ресурс для всего функционала бота.\n\nКаждая нейросеть тратит разное количество ⚡️.\nКоличество затраченных ⚡️ зависит от длины истории диалога, моделей нейросетей и объёма ваших вопросов и ответов от нейросети.\nДля экономии используйте команду - /clear, чтобы не переполнять историю диалога и не увеличивать расход ⚡️ (энергии)! \nРекомендуется очищать контекст перед началом обсуждения новой темы. А также если выбранная модель начала отказывать в помощи.\n\n/app - 🔥 Получить ссылку к приложению!\n/start - 🔄 Рестарт бота, перезапускает бот, помогает обновить бота до последней версии.\n/model - 🛠️ Сменить модель, перезапускает бот, позволяет сменить модель бота.\n/system - ⚙️ Системное сообщение, позволяет сменить системное сообщение, чтобы изменить режим взаимодействия с ботом.   \n/clear - 🧹 Очистить контекст, помогает забыть боту всю историю.  \n/balance - ✨ Баланс, позволяет узнать баланс ⚡️.\n/image - 🖼️ Генерация картинки (Midjourney, DALL·E 3, Flux, Stable Diffusion)\n/buy - 💎 Пополнить баланс, позволяет пополнить баланс ⚡️.\n/referral - 🔗 Получить реферральную ссылку\n/suno - 🎵 Генерация музыки (Suno)\n/text - Отправить текстовое сообщение",

        "app.link": "Ссылка на приложение: https://t.me/DeepGPTBot/App",

        "language.select": "Выберите язык / Select language",
        "language.changed": "Язык изменен на русский",
        "language.current": "Текущий язык: русский",

        "units.energy": "⚡️",
        "units.rub": "RUB", 
        "units.stars": "⭐️"
    }
    
    # English translations
    english_translations = {
        "commands.start": "/start",
        "commands.help": "/help",
        "commands.balance": "/balance", 
        "commands.model": "/model",
        "commands.system": "/system",
        "commands.clear": "/clear",
        "commands.image": "/image",
        "commands.suno": "/suno", 
        "commands.buy": "/buy",
        "commands.referral": "/referral",
        "commands.api": "/api",
        "commands.app": "/app",

        "common.yes": "Yes ✅",
        "common.no": "No ❌",
        "common.cancel": "Cancel ❌",
        "common.back": "Back",
        "common.forward": "Forward", 
        "common.error": "Error",
        "common.success": "Success",
        "common.loading": "Loading...",
        "common.check": "Check ✅",
        "common.subscribe": "Subscribe 👊🏻",

        "menu.balance": "✨ Balance",
        "menu.buy_balance": "💎 Top up balance",
        "menu.change_model": "🛠️ Change model", 
        "menu.change_mode": "⚙️ Change Mode",
        "menu.music_generation": "🎵 Music generation",
        "menu.image_generation": "🖼️ Image generation",
        "menu.clear_context": "🧹 Clear context",
        "menu.chat_history": "📖 Chat history",
        "menu.referral_link": "🔗 Referral link",
        "menu.help": "🆘 Help",
        "menu.donation": "💖 Donation",

        "generate.action": "Generate 🔥",
        "generate.more": "Generate more? 🔥",
        "generate.midjourney_more": "Generate Midjourney more? 🔥",
        "generate.flux_more": "Generate Flux more? 🔥",
        "generate.dalle_more": "Generate DALL·E 3 more? 🔥",
        "generate.suno_more": "Generate Suno more? 🔥",

        "models.gpt4o": "🤖 GPT-4o",
        "models.gpt35": "🦾 GPT-3.5",
        "models.current": "Model: {model}",
        "models.size": "Size: {size}",
        "models.steps": "Steps: {steps}",
        "models.cfg_scale": "CFG Scale: {cfg}",

        "payment.choose_method": "Choose payment method",
        "payment.telegram_stars": "Telegram Stars ⭐️",
        "payment.card_payment": "Card payment 💳", 
        "payment.pay_stars": "Pay {stars} ⭐️",
        "payment.back_to_method": "⬅️ Back to payment method selection",

        "status.not_subscribed": "You didn't subscribe! 😡",
        "status.image_original": "Here's your image in original quality",
        "status.image_quality": "Here's the image in original quality",
        "status.context_cleared": "Dialog context successfully cleared! 👌🏻",
        "status.dialog_empty": "Dialog is already empty!",

        "placeholder.ask_question": "💬 Ask your question",
        "placeholder.describe": "Describe",

        "agreement.text": "📑 Have you read and do you accept the [user agreement](https://grigoriy-grisha.github.io/chat_gpt_agreement/) and [privacy policy](https://grigoriy-grisha.github.io/chat_gpt_agreement/PrivacyPolicy)?",

        "error.not_enough_energy": "You don't have enough *⚡️*. 😔\n\n/balance - ✨ Check Balance\n/buy - 💎 Top up balance \n/referral - 👥 Invite a friend to get free *⚡️*!\n/model - 🛠️ Change model",
        "error.voice_not_recognized": "Error: Voice message not recognized",
        "error.file_not_supported": "😔 Unfortunately, this file type is not supported!\n\nFollow updates on channel @gptDeep or write to us in chat @deepGPT",
        "error.file_processing": "😔 Unfortunately, errors occurred while processing files:\n{error_text}\n\nFollow updates on channel @gptDeep",

        "welcome.hello": "👋 Hello! I'm a bot from deep.foundation developers!\n\n🤖 I'm ready to help you with any task, just write a message or click a button in the menu!\n\n/help - ✨ overview of commands and features\n/balance - ⚡️ check your balance\n/referral - 🔗 referral details\n\nEverything is free, if you don't pay.\nEvery day your balance will be replenished by *10,000⚡️* (energy)!\n\nIf you need more:\n💎 You can top up your balance with Telegram stars or bank card.\n👥 Liked it? Share with friends and get a bonus for each invited friend! By bringing many friends you can use neural networks almost unlimited.\n\n/referral - get more with the referral system:\n*5,000⚡️️* for each invited user;\n*+500⚡️️* to daily balance replenishment for each friend.\n\n🏠 If something went wrong or you want to share inspiration, write to our community @deepGPT.",

        "referral.arrived": "👋 You arrived via a referral link, to get a reward you need to subscribe to my channel.",
        "referral.reward": "🎉 You received *5,000*⚡️!\n\n/balance - ✨ Check balance\n/referral - 🔗 Referral details",
        "referral.new_referral": "🎉 New referral added! \nYou received *5,000*⚡️!\nYour referral must show any activity in the bot within 24 hours so you get another *5,000*⚡️ and +500⚡️️ to daily balance replenishment.\n\n/balance - ✨ Check balance\n/referral - 🔗 Referral details",

        "help.info": "The main resource for accessing neural networks - ⚡️ (energy).\nThis is a universal resource for all bot functionality.\n\nEach neural network spends a different amount of ⚡️.\nThe amount of ⚡️ spent depends on the length of dialogue history, neural network models and the volume of your questions and answers from the neural network.\nTo save, use the command - /clear, so as not to overflow the dialogue history and not increase the consumption of ⚡️ (energy)! \nIt is recommended to clear the context before starting a discussion of a new topic. And also if the selected model started refusing to help.\n\n/app - 🔥 Get link to application!\n/start - 🔄 Bot restart, restarts the bot, helps update the bot to the latest version.\n/model - 🛠️ Change model, restarts the bot, allows you to change the bot model.\n/system - ⚙️ System message, allows you to change the system message to change the mode of interaction with the bot.   \n/clear - 🧹 Clear context, helps the bot forget all history.  \n/balance - ✨ Balance, allows you to check the balance ⚡️.\n/image - 🖼️ Image generation (Midjourney, DALL·E 3, Flux, Stable Diffusion)\n/buy - 💎 Top up balance, allows you to top up the balance ⚡️.\n/referral - 🔗 Get referral link\n/suno - 🎵 Music generation (Suno)\n/text - Send text message",

        "app.link": "Link to application: https://t.me/DeepGPTBot/App",

        "language.select": "Select language / Выберите язык",
        "language.changed": "Language changed to English",
        "language.current": "Current language: English",

        "units.energy": "⚡️",
        "units.rub": "RUB", 
        "units.stars": "⭐️"
    }
    
    # Save Russian translations
    with open('../bot/i18n/translations/ru.json', 'w', encoding='utf-8') as f:
        json.dump(russian_translations, f, ensure_ascii=False, indent=2)
    print(f"Created ru.json with {len(russian_translations)} translations")
    
    # Save English translations  
    with open('../bot/i18n/translations/en.json', 'w', encoding='utf-8') as f:
        json.dump(english_translations, f, ensure_ascii=False, indent=2)
    print(f"Created en.json with {len(english_translations)} translations")
    
    # Create basic template for other languages (using English as base)
    template_languages = ['zh', 'hi', 'es', 'ar', 'fr', 'bn', 'pt', 'de', 'ja', 'ko', 'it']
    
    for lang in template_languages:
        # Start with English translations as template
        template_translations = english_translations.copy()
        # Update language-specific items
        template_translations["language.changed"] = f"Language changed to {lang}"
        template_translations["language.current"] = f"Current language: {lang}"
        
        with open(f'../bot/i18n/translations/{lang}.json', 'w', encoding='utf-8') as f:
            json.dump(template_translations, f, ensure_ascii=False, indent=2)
        print(f"Created {lang}.json template")
    
    print(f"\nSuccessfully created translation files for {len(template_languages) + 2} languages!")

if __name__ == '__main__':
    create_basic_translations()