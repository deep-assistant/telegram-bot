import re

from bot.commands import all_commands_and_texts

def is_empty_prompt(prompt: str) -> bool:
    stripped_prompt = prompt.strip()
    return (stripped_prompt in all_commands_and_texts) or \
        (not any(char.isalnum() for char in stripped_prompt)) or \
        (re.match(r'^/[a-zA-Z]+$', stripped_prompt)) or \
        (re.match(r'^1:(midjourney|dalle|flux|sd|suno):.+$', stripped_prompt))