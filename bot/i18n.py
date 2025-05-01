import gettext
from pathlib import Path
from typing import Dict

LANG_DEFAULT = "en"
_LOCALES_DIR = Path(__file__).resolve().parent / "locales"
_CACHE: Dict[str, gettext.GNUTranslations] = {}


def _gt(locale: str) -> gettext.GNUTranslations:
    if locale not in _CACHE:
        _CACHE[locale] = gettext.translation(
            domain="messages",
            localedir=_LOCALES_DIR,
            languages=[locale],
            fallback=True,
        )
    return _CACHE[locale]


def t(msgid: str, locale: str) -> str:
    return _gt(locale).gettext(msgid)


def get_locale(message) -> str:
    lang = (getattr(message.from_user, "language_code", "") or "").lower()
    return "ru" if lang.startswith("ru") else "en"
