from enum import Enum
from db import data_base, db_key


class ContextMode(Enum):
    PERSONAL = "personal"  # Личный контекст - для каждого пользователя индивидуальный
    GENERAL = "general"    # Общий контекст - общий для всего чата


class ContextService:
    CONTEXT_MODE_KEY = "context_mode"

    def get_context_mode(self, user_id: str) -> ContextMode:
        """Получить текущий режим контекста для пользователя"""
        try:
            mode = data_base[db_key(user_id, self.CONTEXT_MODE_KEY)].decode('utf-8')
            return ContextMode(mode)
        except (KeyError, ValueError):
            # По умолчанию используем личный контекст
            self.set_context_mode(user_id, ContextMode.PERSONAL)
            return ContextMode.PERSONAL

    def set_context_mode(self, user_id: str, mode: ContextMode):
        """Установить режим контекста для пользователя"""
        with data_base.transaction():
            data_base[db_key(user_id, self.CONTEXT_MODE_KEY)] = mode.value
        data_base.commit()

    def get_dialog_identifier(self, user_id: str, chat_id: str) -> str:
        """
        Получить идентификатор диалога в зависимости от режима контекста
        
        Args:
            user_id: ID пользователя
            chat_id: ID чата
            
        Returns:
            Идентификатор диалога для API
        """
        mode = self.get_context_mode(user_id)
        
        if mode == ContextMode.PERSONAL:
            # Личный контекст - используем user_id
            return str(user_id)
        else:
            # Общий контекст - используем chat_id
            return f"chat_{chat_id}"

    def is_general_context(self, user_id: str) -> bool:
        """Проверить, использует ли пользователь общий контекст"""
        return self.get_context_mode(user_id) == ContextMode.GENERAL

    def is_personal_context(self, user_id: str) -> bool:
        """Проверить, использует ли пользователь личный контекст"""
        return self.get_context_mode(user_id) == ContextMode.PERSONAL


contextService = ContextService()