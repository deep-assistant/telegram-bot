import fs from 'fs/promises';

export const SKIP_SSL_CHECK = false;

export function include(arr, value) {
  const trimmedValue = value.trim();
  return arr.some(x => x.trim() === trimmedValue);
}

export function getUserName(userId) {
  return String(userId);
}

export function divideIntoChunks(arr, chunkSize) {
  const chunks = [];
  for (let i = 0; i < arr.length; i += chunkSize) {
    chunks.push(arr.slice(i, i + chunkSize));
  }
  return chunks;
}

export async function downloadImage(photoUrl, filePath, skipSsl = SKIP_SSL_CHECK) {
  // Note: skipSsl not implemented in fetch
  const response = await fetch(photoUrl);
  if (!response.ok) {
    throw new Error(`Failed to download image: ${response.status}`);
  }
  const arrayBuffer = await response.arrayBuffer();
  const buffer = Buffer.from(arrayBuffer);
  await fs.writeFile(filePath, buffer);
}

export async function sendPhoto(message, photoUrl, caption, ext = ".jpg", replyMarkup = null) {
  const photoPath = 'photo' + ext;
  await downloadImage(photoUrl, photoPath);
  // Stub: replace with actual sendPhoto implementation
  const returnedMessage = await message.answerPhoto(photoPath, caption, replyMarkup);
  await fs.unlink(photoPath);
  return returnedMessage;
}

export async function sendPhotoAsFile(message, photoUrl, caption, ext = ".jpg", replyMarkup = null) {
  const photoPath = 'photo' + ext;
  await downloadImage(photoUrl, photoPath);
  // Stub: replace with actual sendDocument implementation
  const returnedMessage = await message.answerDocument(photoPath, caption, replyMarkup);
  await fs.unlink(photoPath);
  return returnedMessage;
}
