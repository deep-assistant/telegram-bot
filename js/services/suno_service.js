import config from '../config.js';
import { asyncGet, asyncPost } from './utils.js';

class SunoService {
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
      if (result.data?.status === 'processing') continue;
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
