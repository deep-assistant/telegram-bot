export function getDefaultErrorMessage(errorId = null) {
    let errorText = `Что-то пошло не так 😔
Пожалуйста попробуйте ещё раз или позже.
Можно так же попробовать другой промт.
Если проблема повторяется, то убедитесь:
1. что вы перезапускали бота (/start) 
2. что ваш контекст сброшен (/clear).
Если и это не помогает, пожалуйста, обратитесь в поддержку (@deepGPT) в раздел **Ошибки**.`;
    
    if (errorId) {
        errorText += `\n\n🆔 ID ошибки: \`${errorId}\``;
        errorText += `\n_(укажите этот ID при обращении в поддержку)_`;
    }
    
    return errorText;
}

export const DEFAULT_ERROR_MESSAGE = getDefaultErrorMessage();
export function getGenerationFailedErrorMessage(errorId = null) {
    let errorText = `Генерация не удалась. Что-то пошло не так 😔
Пожалуйста попробуйте ещё раз или позже.
Можно так же попробовать другой промт.
Если проблема повторяется, то убедитесь:
1. что вы перезапускали бота (/start) 
2. что ваш контекст сброшен (/clear).
Если и это не помогает, пожалуйста, обратитесь в поддержку (@deepGPT) в раздел **Ошибки**.`;
    
    if (errorId) {
        errorText += `\n\n🆔 ID ошибки: \`${errorId}\``;
        errorText += `\n_(укажите этот ID при обращении в поддержку)_`;
    }
    
    return errorText;
}

export const GENERATION_FAILED_DEFAULT_ERROR_MESSAGE = getGenerationFailedErrorMessage();
export function getContextClearFailedErrorMessage(errorId = null) {
    let errorText = `Не удалось очистить контекст 😔
Пожалуйста попробуйте ещё раз или позже.
Можно так же попробовать другой промт.
Если проблема повторяется, то убедитесь:
1. что вы перезапускали бота (/start) 
2. что ваш контекст сброшен (/clear).
Если и это не помогает, пожалуйста, обратитесь в поддержку (@deepGPT) в раздел **Ошибки**.`;
    
    if (errorId) {
        errorText += `\n\n🆔 ID ошибки: \`${errorId}\``;
        errorText += `\n_(укажите этот ID при обращении в поддержку)_`;
    }
    
    return errorText;
}

export const DIALOG_CONTEXT_CLEAR_FAILED_DEFAULT_ERROR_MESSAGE = getContextClearFailedErrorMessage();
