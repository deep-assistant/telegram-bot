import { config } from '../config.js';
// import { OpenAI } from 'openai';
import { OpenAI } from './openai_stub.js';
import { getUserName } from '../bot/utils.js';
import { DEFAULT_ERROR_MESSAGE } from '../bot/constants.js';
import { asyncPost } from './utils.js';

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
      // Count symbols in the current item
      let itemLength = 0;
      if (typeof item === 'string') {
        itemLength = item.length;
      } else if (item && item.content) {
        itemLength = String(item.content).length;
      } else if (item) {
        itemLength = JSON.stringify(item).length;
      }
      
      // If adding this item would exceed the limit, stop
      if (symbols + itemLength >= 4000) break;
      
      cutDialog.push(item);
      symbols += itemLength;
    }
    history[userId] = cutDialog.reverse();
  }

  // Enhanced method to validate and truncate message content
  validateMessageLength(content, maxLength = 4000) {
    if (!content) return content;
    
    // Handle string content
    if (typeof content === 'string') {
      if (content.length <= maxLength) return content;
      return content.substring(0, maxLength) + '\n\n[Сообщение обрезано из-за превышения лимита длины]';
    }
    
    // Handle array content (for multimodal)
    if (Array.isArray(content)) {
      let totalLength = 0;
      const truncatedContent = [];
      
      for (const item of content) {
        if (item.type === 'text') {
          const textLength = item.text ? item.text.length : 0;
          if (totalLength + textLength > maxLength) {
            const remainingLength = maxLength - totalLength;
            if (remainingLength > 100) {
              truncatedContent.push({
                ...item,
                text: item.text.substring(0, remainingLength) + '\n\n[Сообщение обрезано из-за превышения лимита длины]'
              });
            }
            break;
          }
          totalLength += textLength;
          truncatedContent.push(item);
        } else {
          // Keep non-text items (like images) as they don't contribute to text length
          truncatedContent.push(item);
        }
      }
      
      return truncatedContent;
    }
    
    return content;
  }

  async query_chatgpt(userId, message, systemMessage, gptModel, botModel, singleMessage) {
    // Cut history to prevent context from becoming too long
    this.cutHistory(userId);
    
    // Validate and truncate message content to prevent API errors
    const validatedMessage = this.validateMessageLength(message, 4000);
    return this.queryChatGPT(userId, validatedMessage, systemMessage, gptModel, botModel, singleMessage);
  }

  async queryChatGPT(userId, message, systemMessage, gptModel, botModel, singleMessage) {
    const params = { masterToken: config.adminToken };
const payload = { userId: getUserName(userId), content: message, systemMessage, model: gptModel };
const response = await asyncPost(`${config.proxyUrl}/completions`, { params, json: payload });
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
      return { success: true, response: finalContent, model: responseModel };
    } else {
      const errData = await response.json();
      return { success: false, response: `Ошибка 😔: ${errData.message}` };
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
    // Validate prompt length to prevent API errors
    const validatedPrompt = this.validateMessageLength(prompt, 4000);
    const conversation = await getFreeConversation();
    const url = `https://api.goapi.xyz/api/chatgpt/v1/conversation/${conversation}`;
const payload = JSON.stringify({ model: 'gpt-4o', content: { content_type: 'multimodal_text', parts: [validatedPrompt] }, stream: true });
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
