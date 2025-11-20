def payment_command_start():
    return "/donut"

def payment_command_text():
    return "💖 Пожертвование"

def balance_payment_command_text():
    return "💎 Пополнить баланс"

def balance_payment_command_start():
    return "/buy"

def referral_command():
    return "/referral"

def change_model_command():
    return "/model"

def change_model_text():
    return "🛠️ Сменить модель"

def change_system_message_command():
    return "/system"

def change_system_message_text():
    return "⚙️ Сменить Режим"

def balance_text():
    return "✨ Баланс"

def balance_command():
    return "/balance"

def clear_text():
    return "🧹 Очистить контекст"

def clear_command():
    return "/clear"

def multimodal_command():
    return "/multimodal"

def get_history_command():
    return "/history"

def get_history_text():
    return "📖 История диалога"

def help_command():
    return "/help"

def app_command():
    return "/app"

def help_text():
    return "🆘 Помощь"

def referral_command_text():
    return "🔗 Реферальная ссылка"

def images_command():
    return "/image"

def images_command_text():
    return "🖼️ Генерация картинки"

def get_remove_background_command():
    return "/remove_background"

# TODO: rename to /music
def suno_command():
    return "/suno"

def suno_text():
    return "🎵 Генерация музыки"

def here_and_now_command():
    return "/here_and_now"

def api_command():
    return "/api"

def transfer_command():
    return "/transfer"

def transfer_text():
    return "💸 Перевести энергию"

all_commands = [
    payment_command_start(),
    payment_command_text(),
    balance_payment_command_text(),
    balance_payment_command_start(),
    referral_command(),
    change_model_command(),
    change_model_text(),
    change_system_message_command(),
    change_system_message_text(),
    balance_text(),
    balance_command(),
    clear_text(),
    clear_command(),
    multimodal_command(),
    get_history_command(),
    get_history_text(),
    help_command(),
    app_command(),
    help_text(),
    referral_command_text(),
    images_command(),
    images_command_text(),
    get_remove_background_command(),
    suno_command(),
    suno_text(),
    here_and_now_command(),
    api_command(),
    transfer_command(),
    transfer_text(),
]