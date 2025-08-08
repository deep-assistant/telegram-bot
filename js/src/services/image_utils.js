import { findInList, findInListByField } from './utils.js';

export const imageModels = [
  { value: 'sdxl', label: 'sdxl' },
  { value: 'anything-v5', label: 'anything-v5' },
  { value: 'dark-sushi-25d', label: 'dark-sushi-25d' },
  { value: 'dark-sushi-mix', label: 'dark-sushi-mix' },
  { value: 'cityedgestylemix', label: 'cityedgestylemix' },
  { value: 'cetusmix', label: 'cetusmix' },
  { value: 'ghostmix', label: 'ghostmix' },
  { value: 'dosmix', label: 'dosmix' },
  { value: 'ddosmix', label: 'ddosmix' },
  { value: 'cinnamon', label: 'cinnamon' },
  { value: 'three-delicacy-wonton', label: 'three-delicacy-wonton' },
  { value: 'm9rbgas9t4w', label: 'm9rbgas9t4w' },
  { value: 'majicmixrealistic', label: 'majicmixrealistic' },
  { value: 'majicmixsombre', label: 'majicmixsombre' },
  { value: 'majicmixfantasy', label: 'majicmixfantasy' },
  { value: 'cyberrealistic', label: 'cyberrealistic' },
  { value: 'chilloutmix', label: 'chilloutmix' }
];

export const samplers = [
  { value: 'Euler', label: 'Euler' },
  { value: 'Euler a', label: 'EulerA' },
  { value: 'Heun', label: 'Heun' },
  { value: 'DPM++ 2MKarras', label: 'DPM++2MKarras' },
  { value: 'DPM++ SDE Karras', label: 'DPM++SDEKarras' },
  { value: 'DDIM', label: 'DDIM' }
];

export const cgfValues = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20];
export const stepsValues = [21, 31, 41, 51];
export const sizeValues = ['512x512', '512x768', '768x512', '768x768', '1024x1024'];
export const samplersValues = samplers.map(s => s.label);
export const imageModelsValues = imageModels.map(m => m.label);

export function getImageModelByValue(label) {
  return findInListByField(imageModels, 'value', label);
}

export function getImageModelByLabel(label) {
  return findInListByField(imageModels, 'label', label);
}

export function getSamplersByValue(label) {
  return findInListByField(samplers, 'value', label);
}

export function getSamplersByLabel(label) {
  return findInListByField(samplers, 'label', label);
}

export function formatImageFromRequest(text) {
  // Remove JSON prompt/size blocks
  const re1 = /\{\s*"prompt"\s*:\s*".*?",\s*"size"\s*:\s*".*?"\s*\}/gs;
  const step1 = text.replace(re1, '');
  const re2 = /\{\s*"prompt"\s*:\s*".*?"\s*,\s*"size"\s*:\s*".*?"\s*,\s*"n"\s*:\s*\d+\s*\}/gs;
  const step2 = step1.replace(re2, '');
  const re3 = /!\[image\]\(https:\/\/files\.oaiusercontent\.com\/file-.*?\)/g;
  const cleanedText = step2.replace(re3, '');

  const imageMatch = text.match(/!\[image\]\((https:\/\/files\.oaiusercontent\.com\/file-.*?)\)/);
  const image = imageMatch ? imageMatch[1] : null;

  return { text: cleanedText, image };
}

export function getImageFromResponse(text) {
  const match = text.match(/!\[image\]\((https:\/\/files\.oaiusercontent\.com\/file-.*?)\)/);
  return match ? match[1] : null;
}
