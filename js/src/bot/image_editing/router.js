import { Router } from 'aiogram';
import { TextCommand, Photo, StateCommand, CompositeFilters } from '../filters.js';
import { get_remove_background_command } from '../commands.js';
import { sendPhotoAsFile } from '../utils.js';
import config from '../../../config.js';
import { imageEditing } from '../../services/image_editing.js';
import { tokenizeService } from '../../services/tokenize_service.js';
import { stateService, StateTypes } from '../../services/state_service.js';

export const imageEditingRouter = new Router();

// Prompt user to send photo for background removal
imageEditingRouter.message(TextCommand([get_remove_background_command()]), async (message) => {
  await message.answer('Пришлите фотографию, чтобы удалить фон.');
  await stateService.setCurrentState(message.from_user.id, StateTypes.ImageEditing);
});

// Handle background removal when photo is sent in correct state
imageEditingRouter.message(
  CompositeFilters([Photo(), StateCommand(StateTypes.ImageEditing)]),
  async (message, album) => {
    const userId = message.from_user.id;
    await stateService.setCurrentState(userId, StateTypes.Default);
    const waitMsg = await message.answer('**⌛️Ожидайте ответ...**');
    const photo = album[0].photo.slice(-1)[0];
    try {
      const fileInfo = await message.bot.get_file({ file_id: photo.file_id });
      const fileUrl = `https://api.telegram.org/file/bot${config.TOKEN}/${fileInfo.file_path}`;
      const result = await imageEditing.removeBackground(fileUrl);
      const imageUrl = result.data.task_result.task_output.image_url;
      await message.replyPhoto(imageUrl);
      await sendPhotoAsFile(message, imageUrl, 'Вот картинка в оригинальном качестве', '.png');
      await tokenizeService.update_user_token(userId, 400, 'subtract');
      await message.answer('🤖 Затрачено на удаление фона изображения 400⚡️\n\n❔ /help - Информация по ⚡️');
    } catch (e) {
      console.error(e);
    } finally {
      await waitMsg.delete();
    }
  }
);
