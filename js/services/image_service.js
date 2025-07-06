import { asyncPost, asyncGet } from './utils.js';
// import { OpenAI } from 'openai';
import { OpenAI } from './openai_stub.js';
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

  /**
   * Generate an image via DALL·E 3
   */
  async generateDalle(userId, prompt) {
    const client = new OpenAI({
      apiKey: config.GO_API_KEY,
      baseURL: 'https://api.goapi.xyz/v1/',
    });
    const chatCompletion = await client.chat.completions.create({
      model: 'gpt-4-gizmo-g-pmuQfob8d',
      max_tokens: 30000,
      messages: [
        { role: 'user', content: `You should generate images in size ${await this.getDalleSize(userId)}` },
        { role: 'user', content: prompt },
      ],
      stream: false,
    });
    const formatted = formatImageFromRequest(chatCompletion.choices[0].message.content);
    return {
      image: formatted.image,
      text: formatted.text,
      total_tokens: chatCompletion.usage.total_tokens,
    };
  }

  /**
   * Poll for Midjourney result until ready
   */
  async tryFetchMidjourney(taskId) {
    await new Promise(resolve => setTimeout(resolve, 10000));
    let attempts = 0;
    while (true) {
      if (attempts === 15) {
        return {};
      }
      await new Promise(resolve => setTimeout(resolve, 30000));
      attempts++;
      const result = await this.taskFetch(taskId);
      console.log(result);
      if (result.status === 'processing') continue;
      return result;
    }
  }

  /**
   * Generate an image via Midjourney
   */
  async generateMidjourney(userId, prompt, taskIdGet) {
    const data = {
      prompt,
      aspect_ratio: await this.getMidjourneySize(userId),
      process_mode: 'turbo',
    };
    const response = await asyncPost(
      'https://api.goapi.ai/mj/v2/imagine',
      { headers: { 'X-API-KEY': config.GO_API_KEY }, json: data }
    );
    const body = await response.json();
    const taskId = body.task_id;
    if (taskId) await taskIdGet(taskId);
    return await this.tryFetchMidjourney(taskId);
  }

  /**
   * Fetch a Midjourney task status
   */
  async taskFetch(taskId) {
    const response = await asyncPost(
      'https://api.goapi.ai/mj/v2/fetch',
      { json: { task_id: taskId } }
    );
    return await response.json();
  }

  /**
   * Upscale a Midjourney image
   */
  async upscaleImage(taskId, index, taskIdGet) {
    console.log(taskId);
    const response = await asyncPost(
      'https://api.goapi.ai/mj/v2/upscale',
      { headers: { 'X-API-KEY': config.GO_API_KEY }, json: { origin_task_id: taskId, index } }
    );
    const body = await response.json();
    const newTaskId = body.task_id;
    if (newTaskId) await taskIdGet(newTaskId);
    return await this.tryFetchMidjourney(newTaskId);
  }

  /**
   * Create a variation of a Midjourney image
   */
  async variationImage(taskId, index, taskIdGet) {
    const response = await asyncPost(
      'https://api.goapi.ai/mj/v2/variation',
      { headers: { 'X-API-KEY': config.GO_API_KEY }, json: { origin_task_id: taskId, index } }
    );
    const body = await response.json();
    const newTaskId = body.task_id;
    if (newTaskId) await taskIdGet(newTaskId);
    return await this.tryFetchMidjourney(newTaskId);
  }

  /**
   * Generate an image via Flux API
   */
  async generateFlux(userId, prompt, taskIdGet) {
    const payload = {
      model: await this.getFluxModel(userId),
      task_type: 'txt2img',
      input: { prompt },
    };
    const headers = { 'X-API-Key': config.GO_API_KEY, 'Content-Type': 'application/json' };
    const response = await asyncPost(
      'https://api.goapi.ai/api/v1/task',
      { headers, json: payload }
    );
    const data = await response.json();
    const taskId = data.data.task_id;
    let attempts = 0;
    await taskIdGet(taskId);
    while (true) {
      if (attempts === 10) return;
      await new Promise(resolve => setTimeout(resolve, 10000));
      attempts++;
      const statusResp = await asyncGet(
        `https://api.goapi.ai/api/v1/task/${taskId}`,
        { headers }
      );
      const result = await statusResp.json();
      const status = result.data?.status;
      if (status === 'pending' || status === 'processing') continue;
      if (status === 'completed') return result;
    }
  }

  /**
   * Fetch Flux task status
   */
  async taskFluxFetch(taskId) {
    const headers = { 'X-API-Key': config.GO_API_KEY, 'Content-Type': 'application/json' };
    const response = await asyncGet(
      `https://api.goapi.ai/api/v1/task/${taskId}`,
      { headers }
    );
    return await response.json();
  }
}

export const imageService = new ImageService();
