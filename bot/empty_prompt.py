import re

from bot.gpt.command_types import change_model_text, change_system_message_text, balance_text, clear_text, \
    get_history_text
from bot.images import images_command_text
from bot.payment.command_types import balance_payment_command_text
from bot.referral import referral_command_text
from bot.suno.command_types import suno_text

# TODO: move all commands to bot.commands (so it will be easier to update them when added or deleted)

commands = [
    balance_text(),
    balance_payment_command_text(),
    change_model_text(),
    change_system_message_text(),
    suno_text(),
    images_command_text(),
    clear_text(),
    get_history_text(),
    referral_command_text(),
]

def is_empty_prompt(prompt: str) -> bool:
    stripped_prompt = prompt.strip()
    return (stripped_prompt in commands) or \
        (not any(char.isalnum() for char in stripped_prompt)) or \
        (re.match(r'^/[a-zA-Z]+$', stripped_prompt)) or \
        (re.match(r'^1:(midjourney|dalle|flux|sd|suno):.+$', stripped_prompt))