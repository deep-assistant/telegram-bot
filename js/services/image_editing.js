import config from '../config.js';
import { asyncPost } from './utils.js';

class ImageEditing {
  async removeBackground(imageUrl) {
    const headers = { 'X-API-KEY': config.GO_API_KEY, 'Content-Type': 'application/json' };
    const data = {
      task_type: 'background_remove',
      result_type: 'url',
      task_input: { image: imageUrl }
    };
    const response = await asyncPost('https://api.goapi.ai/api/image_toolkit/v2/create', { json: data, headers });
    const result = await response.json();
    return this.fetchImageEditing(result.data.task_id);
  }

  async fetchImageEditing(taskId) {
    const headers = { 'X-API-KEY': config.GO_API_KEY, 'Content-Type': 'application/json' };
    const data = { task_id: taskId };
    const response = await asyncPost('https://api.goapi.ai/api/image_toolkit/v2/fetch', { json: data, headers });
    return response.json();
  }
}

export const imageEditing = new ImageEditing();
