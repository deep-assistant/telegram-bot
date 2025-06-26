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

class GPTService {
  constructor() {
    this.isRequesting = {};
  }

  async getCurrentModel(userId) {
    // TODO: load from database, default to GPT_4o
    return GPTModels.GPT_4o;
  }

  async setCurrentModel(userId, model) {
    // TODO: store user preference
    await dataBase.set(dbKey(userId, 'current_model'), model);
    await dataBase.commit();
  }

  setIsRequesting(userId, value) {
    this.isRequesting[userId] = value;
  }

  getIsRequesting(userId) {
    return !!this.isRequesting[userId];
  }

  async getCurrentSystemMessage(userId) {
    // TODO: load from database, default to SystemMessages.Default
    return SystemMessages.Default;
  }

  async setCurrentSystemMessage(userId, value) {
    // TODO: store in database
    await dataBase.set(dbKey(userId, 'current_system_message'), value);
    await dataBase.commit();
  }

  getMappingGptModel(userId) {
    // TODO: map current model to API model
    return this.getCurrentModel(userId);
  }
}

export const gptService = new GPTService();
