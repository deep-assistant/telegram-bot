import { asyncPost, asyncGet } from './utils.js';
import { OpenAI } from 'openai';
import config from '../config.js';
import { dataBase, dbKey } from '../db/init_db.js';
import { formatImageFromRequest, getImageModelByLabel } from './image_utils.js';

// Map to track in-progress image generations
const generatingMap = {};

// Stable Diffusion txt2img helper
async function txt2img(prompt, negativePrompt, model, width, height, guidanceScale, steps, waitImage) {
  const response = await asyncPost(
    'https://api.goapi.ai/sd/txt2img',
    {
      headers: { 'X-API-Key': config.GO_API_KEY, 'Content-Type': 'application/json' },
      json: { prompt, model_id: model, negative_prompt: negativePrompt, width, height, guidance_scale: guidanceScale, num_inference_steps: steps, lora_model: null, lora_strength: null }
    }
  );
  const result = await response.json();
  const id = result.id;

  if (result.status === 'processing') {
    await waitImage();
    let attempt = 0;
    while (true) {
      if (attempt === 30) return null;
      await new Promise(r => setTimeout(r, 30000));
      const pollResp = await asyncPost('https://api.goapi.ai/sd/fetch', { json: { id } });
      const pollResult = await pollResp.json();
      attempt++;
      if (pollResult.status === 'processing') continue;
      return pollResult;
    }
  }

  return result;
}

export class ImageService {
  static CURRENT_IMAGE_MODEL = 'current_image_model';
  static CURRENT_SAMPLER = 'current_sampler';
  static CURRENT_STEPS = 'current_steps';
  static CURRENT_CFG = 'current_cfg';
  static CURRENT_SIZE = 'current_size';
  static DALLE_SIZE = 'dalee_size';
  static MIDJOURNEY_SIZE = 'midjourney_size';
  static FLUX_MODEL = 'flux_model';

  static defaultModel = 'cyberrealistic';
  static defaultSampler = 'DPM++SDEKarras';
  static defaultSteps = 31;
  static defaultCfg = '7';
  static defaultSize = '512x512';
  static defaultDalleSize = '1024x1024';
  static defaultMidjourneySize = '1:1';
  static defaultFluxModel = 'Qubico/flux1-dev';

  setWaitingImage(userId, value) {
    generatingMap[userId] = value;
  }

  getWaitingImage(userId) {
    if (!(userId in generatingMap)) {
      this.setWaitingImage(userId, false);
      return false;
    }
    return generatingMap[userId];
  }

  async getCurrentImage(userId) {
    try {
      const buf = await dataBase.get(dbKey(userId, ImageService.CURRENT_IMAGE_MODEL));
      return buf.toString('utf-8');
    } catch {
      await this.setCurrentImage(userId, ImageService.defaultModel);
      return ImageService.defaultModel;
    }
  }

  async setCurrentImage(userId, state) {
    await dataBase.set(dbKey(userId, ImageService.CURRENT_IMAGE_MODEL), state);
  }

  async getSampler(userId) {
    try {
      const buf = await dataBase.get(dbKey(userId, ImageService.CURRENT_SAMPLER));
      return buf.toString('utf-8');
    } catch {
      await this.setSamplerState(userId, ImageService.defaultSampler);
      return ImageService.defaultSampler;
    }
  }

  async setSamplerState(userId, state) {
    await dataBase.set(dbKey(userId, ImageService.CURRENT_SAMPLER), state);
  }

  async getSteps(userId) {
    try {
      const buf = await dataBase.get(dbKey(userId, ImageService.CURRENT_STEPS));
      return buf.toString('utf-8');
    } catch {
      await this.setStepsState(userId, ImageService.defaultSteps);
      return ImageService.defaultSteps;
    }
  }

  async setStepsState(userId, state) {
    await dataBase.set(dbKey(userId, ImageService.CURRENT_STEPS), state);
  }

  async getCfgModel(userId) {
    try {
      const buf = await dataBase.get(dbKey(userId, ImageService.CURRENT_CFG));
      return buf.toString('utf-8');
    } catch {
      await this.setCfgState(userId, ImageService.defaultCfg);
      return ImageService.defaultCfg;
    }
  }

  async setCfgState(userId, state) {
    await dataBase.set(dbKey(userId, ImageService.CURRENT_CFG), state);
  }

  async getSizeModel(userId) {
    try {
      const buf = await dataBase.get(dbKey(userId, ImageService.CURRENT_SIZE));
      return buf.toString('utf-8');
    } catch {
      await this.setSizeState(userId, ImageService.defaultSize);
      return ImageService.defaultSize;
    }
  }

  async setSizeState(userId, state) {
    await dataBase.set(dbKey(userId, ImageService.CURRENT_SIZE), state);
  }

  async getDalleSize(userId) {
    try {
      const buf = await dataBase.get(dbKey(userId, ImageService.DALLE_SIZE));
      return buf.toString('utf-8');
    } catch {
      await this.setDalleSize(userId, ImageService.defaultDalleSize);
      return ImageService.defaultDalleSize;
    }
  }

  async setDalleSize(userId, state) {
    await dataBase.set(dbKey(userId, ImageService.DALLE_SIZE), state);
  }

  async getMidjourneySize(userId) {
    try {
      const buf = await dataBase.get(dbKey(userId, ImageService.MIDJOURNEY_SIZE));
      return buf.toString('utf-8');
    } catch {
      await this.setMidjourneySize(userId, ImageService.defaultMidjourneySize);
      return ImageService.defaultMidjourneySize;
    }
  }

  async setMidjourneySize(userId, state) {
    await dataBase.set(dbKey(userId, ImageService.MIDJOURNEY_SIZE), state);
  }

  async getFluxModel(userId) {
    try {
      const buf = await dataBase.get(dbKey(userId, ImageService.FLUX_MODEL));
      return buf.toString('utf-8');
    } catch {
      await this.setFluxModel(userId, ImageService.defaultFluxModel);
      return ImageService.defaultFluxModel;
    }
  }

  async setFluxModel(userId, state) {
    await dataBase.set(dbKey(userId, ImageService.FLUX_MODEL), state);
  }

  /**
   * Generate an image via Stable Diffusion
   */
  async generate(prompt, userId, waitImage) {
    const currentModel = await this.getCurrentImage(userId);
    let modelObj = getImageModelByLabel(currentModel);
    if (!modelObj) {
      await this.setCurrentImage(userId, ImageService.defaultModel);
      modelObj = getImageModelByLabel(ImageService.defaultModel);
    }
    const size = await this.getSizeModel(userId);
    const [height, width] = size.split('x').map(s => parseInt(s, 10));
    const result = await txt2img(
      prompt,
      '',
      modelObj.value,
      width,
      height,
      parseInt(await this.getCfgModel(userId), 10),
      parseInt(await this.getSteps(userId), 10),
      waitImage
    );
    return result;
  }

  async generateDalle(userId, prompt) {
    // TODO: implement DALL·E generation using OpenAI API
  }

  async tryFetchMidjourney(taskId) {
    // TODO: implement polling for Midjourney
  }

  async generateMidjourney(userId, prompt, taskIdGet) {
    // TODO: implement Midjourney generation
  }

  async taskFetch(taskId) {
    // TODO: implement fetch for tasks
  }

  async upscaleImage(taskId, index, taskIdGet) {
    // TODO: implement image upscaling
  }

  async variationImage(taskId, index, taskIdGet) {
    // TODO: implement image variation
  }

  async generateFlux(userId, prompt, taskIdGet) {
    // TODO: implement Flux generation
  }

  async taskFluxFetch(taskId) {
    // TODO: implement Flux task fetch
  }
}

export const imageService = new ImageService();
