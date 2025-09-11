from bot.i18n import _

def payment_command_start():
    return "/donut"

def payment_command_text(user_id=None):
    return _("menu.donation", user_id=user_id)

def balance_payment_command_text(user_id=None):
    return _("menu.buy_balance", user_id=user_id)

def balance_payment_command_start():
    return "/buy"

def referral_command():
    return "/referral"

def change_model_command():
    return "/model"

def change_model_text(user_id=None):
    return _("menu.change_model", user_id=user_id)

def change_system_message_command():
    return "/system"

def change_system_message_text(user_id=None):
    return _("menu.change_mode", user_id=user_id)

def balance_text(user_id=None):
    return _("menu.balance", user_id=user_id)

def balance_command():
    return "/balance"

def clear_text(user_id=None):
    return _("menu.clear_context", user_id=user_id)

def clear_command():
    return "/clear"

def multimodal_command():
    return "/multimodal"

def get_history_command():
    return "/history"

def get_history_text(user_id=None):
    return _("menu.chat_history", user_id=user_id)

def help_command():
    return "/help"

def app_command():
    return "/app"

def help_text(user_id=None):
    return _("menu.help", user_id=user_id)

def referral_command_text(user_id=None):
    return _("menu.referral_link", user_id=user_id)

def images_command():
    return "/image"

def images_command_text(user_id=None):
    return _("menu.image_generation", user_id=user_id)

def get_remove_background_command():
    return "/remove_background"

# TODO: rename to /music
def suno_command():
    return "/suno"

def suno_text(user_id=None):
    return _("menu.music_generation", user_id=user_id)

def here_and_now_command():
    return "/here_and_now"

def api_command():
    return "/api"

def language_command():
    return "/language"

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
    language_command(),
]