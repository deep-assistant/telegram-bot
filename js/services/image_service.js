import { asyncPost, asyncGet } from './utils.js';
import { dataBase, dbKey } from '../db/init_db.js';
import config from '../config.js';
import { getImageModelByLabel } from './image_utils.js';

export class ImageService {
  constructor() {
    this.generatingMap = {};
    this.CURRENT_IMAGE_MODEL = 'current_image_model';
  }

  setWaitingImage(userId, value) {
    this.generatingMap[userId] = value;
  }

  getWaitingImage(userId) {
    return !!this.generatingMap[userId];
  }

  async generate(prompt, userId, waitImage) {
    // TODO: implement text-to-image call
    return { output: [] };
  }

  // TODO: add methods for getCurrentImage, setCurrentImage, getSampler, setSampler, etc.
}

export const imageService = new ImageService();
