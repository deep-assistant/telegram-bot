import { findInList, findInListByField } from './utils.js';
export const imageModels = [
  { value: 'sdxl', label: 'sdxl' },
  { value: 'anything-v5', label: 'anything-v5' },
  // ... other models ...
];
export const samplers = [
  { value: 'Euler', label: 'Euler' },
  { value: 'Euler a', label: 'EulerA' },
  // ... other samplers ...
];
export const cgfValues = Array.from({ length: 11 }, (_, i) => i * 2);
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
  // Remove JSON-like blocks and image markdown
  const cleaned = text.replace(/\{\s*"prompt".*?\}/gs, '').replace(/!\[image\]\(https:\/\/files\.oaiusercontent\.com\/file-.*?\)/g, '');
  // Extract image URL
  const match = text.match(/!\[image\]\((https:\/\/files\.oaiusercontent\.com\/file-.*?)\)/);
  const image = match ? match[1] : null;
  return { image, text: cleaned };
}
