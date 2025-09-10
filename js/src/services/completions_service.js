import { config } from '../config.js';
// import { OpenAI } from 'openai';
import { OpenAI } from './openai_stub.js';
import { getUserName } from '../bot/utils.js';
import { DEFAULT_ERROR_MESSAGE } from '../bot/constants.js';
import { asyncPost } from './utils.js';
import { apiPriorityService } from './api_priority_service.js';

// In-memory storage for history and conversation toggle flags
const history = {};
const conversations = {};

async function setToggleConversation(key, flag) {
  await new Promise(resolve => setTimeout(resolve, 1000));
  conversations[key] = flag;
}

async function getFreeConversation() {
  while (true) {
    console.log(conversations);
    for (const [key, value] of Object.entries(conversations)) {
      if (value) {
        await setToggleConversation(key, false);
        return key;
      }
    }
  }
}

class CompletionsService {
  constructor() {
    this.openai = new OpenAI({ apiKey: config.keyDeepinfra, baseURL: 'https://api.deepinfra.com/v1/openai' });
  }

  clearHistory(userId) {
    history[userId] = [];
  }

  getHistory(userId) {
    if (!history[userId]) history[userId] = [];
    return history[userId];
  }

  updateHistory(userId, item) {
    this.getHistory(userId).push(item);
  }

  cutHistory(userId) {
    const dialog = this.getHistory(userId).slice();
    const reverted = dialog.reverse();
    const cutDialog = [];
    let symbols = 0;
    for (const item of reverted) {
      if (symbols >= 6000) continue;
      cutDialog.push(item);
    }
    history[userId] = cutDialog.reverse();
  }

  async queryChatGPT(userId, message, systemMessage, gptModel, botModel, singleMessage) {
    const requestContext = {
      userId,
      hasMedia: Array.isArray(message) && message.some(m => m.type === 'image_url'),
      singleMessage
    };

    // Get the best API provider for this model
    const bestProvider = apiPriorityService.getBestApiForModel(gptModel, requestContext);
    const startTime = Date.now();

    try {
      const params = { masterToken: config.adminToken };
      const payload = { userId: getUserName(userId), content: message, systemMessage, model: gptModel };
      
      // Use the selected provider's URL
      const apiUrl = `${bestProvider.url}/completions`;
      const response = await asyncPost(apiUrl, { params, json: payload });
      
      const responseTime = Date.now() - startTime;

      if (response.status === 200) {
        const completions = await response.json();
        const responseContent = completions.choices[0].message.content;
        const responseModel = completions.model;
        
        // Estimate tokens used (rough approximation)
        const tokensUsed = Math.ceil((responseContent.length + (typeof message === 'string' ? message.length : JSON.stringify(message).length)) / 4);
        
        // Record successful request
        apiPriorityService.recordSuccess(bestProvider.id, responseTime, tokensUsed);

        let reasoningContent = null;
        const firstThink = responseContent.indexOf('<think>');
        const lastThink = responseContent.indexOf('</think>');
        if (firstThink !== -1 && lastThink !== -1) {
          reasoningContent = responseContent.substring(firstThink, lastThink + '</think>'.length);
        }
        const finalContent = reasoningContent ? responseContent.replace(reasoningContent, '').trim() : responseContent;
        return { success: true, response: finalContent, model: responseModel, provider: bestProvider.id };
      } else {
        const errData = await response.json();
        const error = new Error(`API Error: ${errData.message || 'Unknown error'}`);
        apiPriorityService.recordFailure(bestProvider.id, error);
        return { success: false, response: `Ошибка 😔: ${errData.message}` };
      }
    } catch (error) {
      const responseTime = Date.now() - startTime;
      apiPriorityService.recordFailure(bestProvider.id, error);
      
      // Try fallback provider if available
      if (bestProvider.id !== 'primary') {
        console.log(`Falling back to primary provider due to error: ${error.message}`);
        const fallbackProvider = { id: 'primary', url: config.proxyUrl };
        try {
          const params = { masterToken: config.adminToken };
          const payload = { userId: getUserName(userId), content: message, systemMessage, model: gptModel };
          const response = await asyncPost(`${fallbackProvider.url}/completions`, { params, json: payload });
          
          if (response.status === 200) {
            const completions = await response.json();
            const responseContent = completions.choices[0].message.content;
            const responseModel = completions.model;
            
            let reasoningContent = null;
            const firstThink = responseContent.indexOf('<think>');
            const lastThink = responseContent.indexOf('</think>');
            if (firstThink !== -1 && lastThink !== -1) {
              reasoningContent = responseContent.substring(firstThink, lastThink + '</think>'.length);
            }
            const finalContent = reasoningContent ? responseContent.replace(reasoningContent, '').trim() : responseContent;
            return { success: true, response: finalContent, model: responseModel, provider: 'primary-fallback' };
          }
        } catch (fallbackError) {
          console.error('Fallback also failed:', fallbackError);
        }
      }
      
      return { success: false, response: `Ошибка 😔: ${error.message}` };
    }
  }

  async getFile(parts, conversation) {
    const url = `https://api.goapi.xyz/api/chatgpt/v1/conversation/${conversation}/download`;
    const payload = JSON.stringify({ file_id: parts[0].asset_pointer.split('file-service://')[1] });
    const headers = { 'X-API-Key': config.goApiKey, 'Content-Type': 'application/json' };
    const response = await asyncPost(url, { data: payload, headers });
    return response.json();
  }

  async getMultiModalConversation(prompt, attempt = 0) {
    if (attempt === 3) {
      return { text: DEFAULT_ERROR_MESSAGE, url_image: null };
    }
    const conversation = await getFreeConversation();
    const url = `https://api.goapi.xyz/api/chatgpt/v1/conversation/${conversation}`;
const payload = JSON.stringify({ model: 'gpt-4o', content: { content_type: 'multimodal_text', parts: [prompt] }, stream: true });
const headers = { 'X-API-Key': config.goApiKey, 'Content-Type': 'application/json' };
const response = await asyncPost(url, { data: payload, headers });
    let images = [];
    let texts = [];
    console.log(await response.text());
    if (response.status === 200) {
      const rawText = await response.text();
      for (const line of rawText.split('\n')) {
        if (!line) continue;
        if (line.startsWith('data: ')) {
          try {
            const dataObj = JSON.parse(line.slice('data: '.length));
            const content = dataObj.message.content;
            if (!content || !content.parts) continue;
            const part = content.parts[0];
            if (content.content_type === 'multimodal_text') images.push(part);
            else if (content.content_type === 'text') texts.push(part);
          } catch (e) {
            console.error('Failed to parse multimodal data:', e);
          }
        }
      }
      const cleanedText = texts.length ? texts[texts.length - 1].replace(/【[^】]*】/g, '').trim() : '';
      if (images.length === 0) {
        await setToggleConversation(conversation, true);
        return { text: cleanedText, url_image: null };
      }
      const imageResult = await this.getFile(images, conversation);
      const result = { text: cleanedText, url_image: imageResult.data.download_url };
      await setToggleConversation(conversation, true);
      return result;
    } else if (response.status === 400) {
      return this.getMultiModalConversation(prompt, attempt + 1);
    }
  }
}

export const completionsService = new CompletionsService();
