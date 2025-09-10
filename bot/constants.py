def get_default_error_message(error_id: str = None) -> str:
    """Generate default error message with optional error ID for support"""
    error_text = """Что-то пошло не так 😔
Пожалуйста попробуйте ещё раз или позже.
Можно так же попробовать другой промт.
Если проблема повторяется, то убедитесь:
1. что вы перезапускали бота (/start) 
2. что ваш контекст сброшен (/clear).
Если и это не помогает, пожалуйста, обратитесь в поддержку (@deepGPT) в раздел *Ошибки*."""
    
    if error_id:
        error_text += f"\n\n🆔 ID ошибки: `{error_id}`"
        error_text += "\n_(укажите этот ID при обращении в поддержку)_"
    
    return error_text

DEFAULT_ERROR_MESSAGE = get_default_error_message()

def get_generation_failed_error_message(error_id: str = None) -> str:
    """Generate generation failed error message with optional error ID for support"""
    error_text = """Генерация не удалась. Что-то пошло не так 😔
Пожалуйста попробуйте ещё раз или позже.
Можно так же попробовать другой промт.
Если проблема повторяется, то убедитесь:
1. что вы перезапускали бота (/start) 
2. что ваш контекст сброшен (/clear).
Если и это не помогает, пожалуйста, обратитесь в поддержку (@deepGPT) в раздел *Ошибки*."""
    
    if error_id:
        error_text += f"\n\n🆔 ID ошибки: `{error_id}`"
        error_text += "\n_(укажите этот ID при обращении в поддержку)_"
    
    return error_text

GENERATION_FAILED_DEFAULT_ERROR_MESSAGE = get_generation_failed_error_message()

def get_context_clear_failed_error_message(error_id: str = None) -> str:
    """Generate context clear failed error message with optional error ID for support"""
    error_text = """Не удалось очистить контекст 😔
Пожалуйста попробуйте ещё раз или позже.
Можно так же попробовать другой промт.
Если проблема повторяется, то убедитесь:
1. что вы перезапускали бота (/start) 
2. что ваш контекст сброшен (/clear).
Если и это не помогает, пожалуйста, обратитесь в поддержку (@deepGPT) в раздел *Ошибки*."""
    
    if error_id:
        error_text += f"\n\n🆔 ID ошибки: `{error_id}`"
        error_text += "\n_(укажите этот ID при обращении в поддержку)_"
    
    return error_text

DIALOG_CONTEXT_CLEAR_FAILED_DEFAULT_ERROR_MESSAGE = get_context_clear_failed_error_message()