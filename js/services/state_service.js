import { dataBase, dbKey } from '../db/init_db.js';

export const StateTypes = {
  Default: 'default',
  SystemMessageEditing: 'system_message_editing',
  Image: 'image',
  ImageEditing: 'image_editing',
  Dalle3: 'dalle3',
  Midjourney: 'midjourney',
  Suno: 'suno',
  Flux: 'flux',
  Transcribe: 'transcribation'
};

class StateService {
  constructor() {
    this.CURRENT_STATE = 'current_state';
  }

  async getCurrentState(userId) {
    try {
      const buf = await dataBase.get(dbKey(userId, this.CURRENT_STATE));
      const state = buf.toString('utf-8');
      return StateTypes[state] ? state : StateTypes.Default;
    } catch (e) {
      await this.setCurrentState(userId, StateTypes.Default);
      return StateTypes.Default;
    }
  }

  async setCurrentState(userId, state) {
    await dataBase.set(dbKey(userId, this.CURRENT_STATE), state);
    await dataBase.commit();
  }

  async isDefaultState(userId) {
    const current = await this.getCurrentState(userId);
    return current === StateTypes.Default;
  }

  async isImageState(userId) {
    const current = await this.getCurrentState(userId);
    return current === StateTypes.Image;
  }

  async isFluxState(userId) {
    const current = await this.getCurrentState(userId);
    return current === StateTypes.Flux;
  }

  async isDalle3State(userId) {
    const current = await this.getCurrentState(userId);
    return current === StateTypes.Dalle3;
  }

  async isMidjourneyState(userId) {
    const current = await this.getCurrentState(userId);
    return current === StateTypes.Midjourney;
  }

  async isSunoState(userId) {
    const current = await this.getCurrentState(userId);
    return current === StateTypes.Suno;
  }

  async isImageEditingState(userId) {
    const current = await this.getCurrentState(userId);
    return current === StateTypes.ImageEditing;
  }
}

export const stateService = new StateService();
