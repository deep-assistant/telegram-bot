import { config } from '../config.js';
import { asyncGet, asyncPost } from './utils.js';

class SunoService {
  // Convert API error messages to human-readable format
  getHumanReadableError(error) {
    const errorMsg = error?.raw_message || error?.message || '';
    
    if (errorMsg.includes('moderation_failure') && errorMsg.includes('Unable to generate lyrics')) {
      return `❌ Не удалось создать музыку из-за ограничений контента.

🔍 Возможные причины:
• В описании музыки содержится неподходящий контент
• Запрос на создание музыки "без вокала/текста" может вызвать проблемы с генерацией лирики
• Описание нарушает правила сообщества

💡 Рекомендации:
• Попробуйте изменить описание музыки
• Используйте более общие термины вместо "без вокала"
• Избегайте запросов на инструментальную музыку, если хотите получить песню с текстом

Попробуйте с другим описанием!`;
    }
    
    if (errorMsg.includes('clips generation failed')) {
      return `❌ Не удалось создать музыкальную композицию.

Возможные причины:
• Проблемы на стороне сервиса Suno
• Неподходящее описание для генерации
• Временные технические неполадки

Попробуйте изменить описание или повторить попытку позже.`;
    }
    
    // Generic fallback for other errors
    return `❌ Произошла ошибка при генерации музыки.

Детали ошибки: ${errorMsg}

Попробуйте изменить описание или повторить попытку позже.`;
  }
  async generateSuno(prompt, taskIdCallback) {
    const headers = { 'X-API-Key': config.GO_API_KEY, 'Content-Type': 'application/json' };
    const payload = {
      model: 'music-s',
      task_type: 'generate_music',
      input: { gpt_description_prompt: prompt, make_instrumental: false },
      config: { service_mode: 'public', webhook_config: { endpoint: '', secret: '' } }
    };
    const response = await asyncPost('https://api.goapi.ai/api/v1/task', { json: payload, headers });
    const data = response.json();
    if (!data || !data.data) {
      throw new Error(data.message || 'Unknown error creating Suno task.');
    }
    const taskId = data.data.task_id;
    if (taskId) taskIdCallback(taskId);
    let attempts = 0;
    while (true) {
      if (attempts >= 15) return {};
      await new Promise(r => setTimeout(r, 30000));
      attempts++;
      const result = await this.taskFetch(taskId);
      const status = result.data?.status;
      
      if (status === 'processing' || status === 'pending') continue;
      if (status === 'completed') return result;
      if (status === 'failed') {
        // Include error information for proper handling
        result.humanReadableError = this.getHumanReadableError(result.data?.error);
        return result;
      }
      
      return result;
    }
  }

  async taskFetch(taskId) {
    const headers = { 'X-API-Key': config.GO_API_KEY, 'Content-Type': 'application/json' };
    const response = await asyncGet(`https://api.goapi.ai/api/v1/task/${taskId}`, { headers });
    return response.json();
  }
}

export const sunoService = new SunoService();
