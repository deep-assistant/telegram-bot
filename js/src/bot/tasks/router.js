import { Router } from 'aiogram';
import { Message, InlineKeyboardButton, InlineKeyboardMarkup } from 'aiogram/types.js';
import { StartWith } from '../filters.js';
import { sendVariationImage } from './images/router.js';
import { sunoCreateMessages } from './suno/router.js';
import { sendPhotoAsFile } from '../utils.js';
import { GENERATION_FAILED_DEFAULT_ERROR_MESSAGE } from '../constants.js';
import { imageService, sunoService } from '../../services/index.js';

export const taskRouter = new Router();

// Handle Midjourney task updates and variations/upscales
taskRouter.message(StartWith('1:midjourney:'), async (message) => {
  try {
    const data = message.text.replace('1:midjourney:', '');
    const [taskId, action] = data.split(':');
    const task = await imageService.taskFetch(taskId);
    if (task.status === 'finished') {
      const imageUrl = task.task_result.discord_image_url;
      if (action === 'generate') {
        await sendVariationImage(message, imageUrl, task.task_id);
      } else if (action === 'upscale') {
        await message.replyPhoto(imageUrl);
        await sendPhotoAsFile(message, imageUrl, 'Вот ваше изображение в оригинальном качестве');
        await message.answer('Cгенерировать Midjourney еще? 🔥', {
          reply_markup: new InlineKeyboardMarkup({ inline_keyboard: [[
            new InlineKeyboardButton({ text: 'Сгенерировать 🔥', callback_data: 'midjourney-generate' })
          ]] })
        });
      }
      return;
    }
    if (task.status === 'processing') {
      await message.answer('⌛️ Задача в процессе!');
      return;
    }
    await message.answer(GENERATION_FAILED_DEFAULT_ERROR_MESSAGE);
  } catch (e) {
    console.error(`Failed to fetch Midjourney task ${message.text}:`, e);
    await message.answer(GENERATION_FAILED_DEFAULT_ERROR_MESSAGE);
  }
});

// Handle Suno task updates
taskRouter.message(StartWith('1:suno:'), async (message) => {
  try {
    const taskId = message.text.replace('1:suno:', '').split(':')[0];
    const task = await sunoService.taskFetch(taskId);
    const status = task.data.status;
    if (status === 'completed') {
      await sunoCreateMessages(message, task);
      return;
    }
    if (status === 'processing' || status === 'pending') {
      await message.answer('⌛️ Задача в процессе!');
      return;
    }
    if (status === 'failed') {
      const humanReadableError = sunoService.getHumanReadableError(task.data?.error);
      await message.answer(humanReadableError);
      return;
    }
    await message.answer(GENERATION_FAILED_DEFAULT_ERROR_MESSAGE);
  } catch (e) {
    console.error(`Failed to fetch Suno task ${message.text}:`, e);
    await message.answer(GENERATION_FAILED_DEFAULT_ERROR_MESSAGE);
  }
});

// Handle Flux task updates
taskRouter.message(StartWith('1:flux:'), async (message) => {
  try {
    const taskId = message.text.replace('1:flux:', '').split(':')[0];
    const task = await imageService.taskFluxFetch(taskId);
    const status = task.data.status;
    if (status === 'pending' || status === 'processing') {
      await message.answer('⌛️ Задача в процессе!');
      return;
    }
    if (status === 'completed') {
      const imageUrl = task.data.output.image_url;
      await message.bot.sendChatAction(message.chat.id, 'typing');
      await message.replyPhoto(imageUrl);
      await sendPhotoAsFile(message, imageUrl, 'Вот картинка в оригинальном качестве');
      await message.answer('Cгенерировать Flux еще? 🔥', {
        reply_markup: new InlineKeyboardMarkup({ inline_keyboard: [[
          new InlineKeyboardButton({ text: 'Сгенерировать 🔥', callback_data: 'flux-generate' })
        ]] })
      });
      return;
    }
    await message.answer(GENERATION_FAILED_DEFAULT_ERROR_MESSAGE);
  } catch (e) {
    console.error(`Failed to fetch Flux task ${message.text}:`, e);
    await message.answer(GENERATION_FAILED_DEFAULT_ERROR_MESSAGE);
  }
});
