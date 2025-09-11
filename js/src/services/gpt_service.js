import { dataBase, dbKey } from '../db/init_db.js';

export const GPTModels = {
  Claude_3_Opus: 'claude-3-opus',
  Claude_3_5_Sonnet: 'claude-3-5-sonnet',
  Claude_3_5_Haiku: 'claude-3-5-haiku',
  Claude_3_7_Sonnet: 'claude-3-7-sonnet',
  Uncensored: 'uncensored',
  O1_mini: 'o1-mini',
  O1_preview: 'o1-preview',
  GPT_4o_mini: 'gpt-4o-mini',
  GPT_4_Unofficial: 'gpt-4o-unofficial',
  GPT_4o: 'gpt-4o',
  GPT_Auto: 'gpt-auto',
  GPT_3_5: 'gpt-3.5',
  Llama3_1_405B: 'Llama3_1_405B',
  Llama3_1_70B: 'Llama3_1_70B',
  Llama3_1_8B: 'Llama3_1_8B',
  Llama_3_70b: 'Llama_3_70B',
  DeepSeek_Chat: 'deepseek-chat',
  DeepSeek_Reasoner: 'deepseek-reasoner',
  O3_mini: 'o3-mini'
};

export const SystemMessages = {
  Custom: 'custom',
  Default: 'default',
  SoftwareDeveloper: 'software_developer',
  Happy: 'happy',
  QuestionAnswer: 'question_answer',
  DeepPromt: 'deep',
  Transcribe: 'transcribe'
};

// Mapping from GPTModels values to API model identifiers
const gptModelsMap = {
  [GPTModels.Claude_3_Opus]: 'claude-3-opus',
  [GPTModels.Claude_3_5_Sonnet]: 'claude-3-5-sonnet',
  [GPTModels.Claude_3_5_Haiku]: 'claude-3-5-haiku',
  [GPTModels.Claude_3_7_Sonnet]: 'claude-3-7-sonnet',
  [GPTModels.Uncensored]: 'uncensored',
  [GPTModels.O1_mini]: 'o1-mini',
  [GPTModels.O1_preview]: 'o1-preview',
  [GPTModels.GPT_3_5]: 'gpt-3.5-turbo',
  [GPTModels.GPT_4o]: 'gpt-4o',
  [GPTModels.GPT_Auto]: 'gpt-auto',
  [GPTModels.GPT_4_Unofficial]: 'gpt-4o-unofficial',
  [GPTModels.GPT_4o_mini]: 'gpt-4o-mini',
  [GPTModels.Llama3_1_405B]: 'meta-llama/Meta-Llama-3.1-405B',
  [GPTModels.Llama3_1_70B]: 'meta-llama/Meta-Llama-3.1-70B',
  [GPTModels.Llama3_1_8B]: 'meta-llama/Meta-Llama-3.1-8B',
  [GPTModels.Llama_3_70b]: 'meta-llama/Meta-Llama-3-70B-Instruct',
  [GPTModels.DeepSeek_Chat]: 'deepseek-chat',
  [GPTModels.DeepSeek_Reasoner]: 'deepseek-reasoner',
  [GPTModels.O3_mini]: 'o3-mini'
};

class GPTService {
  static CURRENT_MODEL_KEY = 'current_model';
  static CURRENT_SYSTEM_MESSAGE_KEY = 'current_system_message';

  constructor() {
    this.isRequesting = {};
  }

  setIsRequesting(userId, value) {
    // no-op or track in-memory if needed
  }

  getIsRequesting(userId) {
    return false;
  }

  async getCurrentModel(userId) {
    try {
      const buf = await dataBase.get(dbKey(userId, GPTService.CURRENT_MODEL_KEY));
      const model = buf.toString('utf-8');
      if (Object.values(GPTModels).includes(model)) return model;
    } catch {
      // ignore
    }
    // default
    await this.setCurrentModel(userId, GPTModels.GPT_4o);
    return GPTModels.GPT_4o;
  }

  async setCurrentModel(userId, model) {
    await dataBase.set(dbKey(userId, GPTService.CURRENT_MODEL_KEY), model);
  }

  async getCurrentSystemMessage(userId) {
    try {
      const buf = await dataBase.get(dbKey(userId, GPTService.CURRENT_SYSTEM_MESSAGE_KEY));
      return buf.toString('utf-8');
    } catch {
      await this.setCurrentSystemMessage(userId, SystemMessages.Default);
      return SystemMessages.Default;
    }
  }

  async setCurrentSystemMessage(userId, value) {
    await dataBase.set(dbKey(userId, GPTService.CURRENT_SYSTEM_MESSAGE_KEY), value);
  }

  async getMappingGptModel(userId) {
    // map stored model to API model
    const currentModel = await this.getCurrentModel(userId);
    return gptModelsMap[currentModel];
  }
}

export const gptService = new GPTService();
