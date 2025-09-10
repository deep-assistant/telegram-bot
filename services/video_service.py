import asyncio
import logging
import json

from config import GO_API_KEY
from services.utils import async_post, async_get

# Временное хранение данных пользователей
user_temp_data = {}

class VideoService:
    def store_user_data(self, user_id: str, prompt: str = None, style: str = None):
        """Сохраняет временные данные пользователя"""
        if user_id not in user_temp_data:
            user_temp_data[user_id] = {}
        if prompt is not None:
            user_temp_data[user_id]['prompt'] = prompt
        if style is not None:
            user_temp_data[user_id]['style'] = style

    def get_user_data(self, user_id: str):
        """Получает временные данные пользователя"""
        return user_temp_data.get(user_id, {})

    def clear_user_data(self, user_id: str):
        """Очищает временные данные пользователя"""
        if user_id in user_temp_data:
            del user_temp_data[user_id]

    async def generate_video(self, prompt: str, style: str = "realistic", task_id_get=None):
        """Генерирует видео используя Kling API через GoAPI.ai"""
        logging.info(f"Video: начинаем генерацию видео для промпта '{prompt}' в стиле '{style}'")
        
        # Подготавливаем промпт в зависимости от стиля
        enhanced_prompt = self._enhance_prompt(prompt, style)
        
        # Создаем задачу через GoAPI.ai Kling API
        json_data = {
            "model": "kling-v1-5",
            "task_type": "text_to_video",
            "input": {
                "prompt": enhanced_prompt,
                "negative_prompt": "bad quality, blurry, distorted, low resolution, watermark",
                "cfg_scale": 7.5,
                "duration": "5s",  # 5 секунд видео
                "aspect_ratio": "16:9"
            }
        }
        
        headers = {
            'X-API-Key': GO_API_KEY,
            'Content-Type': 'application/json'
        }
        
        logging.info(f"Video: отправляем JSON: {json_data}")
        
        try:
            response = await async_post(
                "https://api.goapi.ai/api/v1/kling/v1/videos/text2video",
                headers=headers,
                json=json_data
            )
            response_json = response.json()
            logging.info(f"Video: ответ от API: {response_json}")
            
            if 'data' not in response_json:
                error_message = response_json.get('message', 'Unknown error occurred while creating video task.')
                logging.error(f"Video: ошибка создания задачи: {error_message}")
                raise Exception(f"API Error: {error_message}")
                
            task_id = response_json['data'].get('task_id')
            logging.info(f"Video: создан task_id: {task_id}")
            
            if task_id and task_id_get:
                await task_id_get(task_id)
                
            # Ожидаем завершения задачи
            attempts = 0
            max_attempts = 60  # 30 минут максимум (каждые 30 секунд)
            
            while True:
                if attempts >= max_attempts:
                    logging.error(f"Video: превышено число попыток ожидания результата для task_id {task_id}")
                    return {}
                    
                await asyncio.sleep(30)  # Ждем 30 секунд между проверками
                attempts += 1
                
                result = await self.task_fetch(task_id)
                status = result.get('data', {}).get('status')
                logging.info(f"Video: polling attempt {attempts}/{max_attempts}, статус: {status}, task_id: {task_id}")
                
                if status == "pending":
                    logging.info(f"Video: задача {task_id} все еще в очереди...")
                    continue
                elif status == "processing":
                    logging.info(f"Video: задача {task_id} обрабатывается...")
                    continue
                elif status == "completed":
                    logging.info(f"Video: задача {task_id} завершена успешно!")
                    return result
                elif status == "failed":
                    error_msg = result.get('data', {}).get('error', {}).get('message', 'Unknown error')
                    logging.error(f"Video: задача {task_id} завершилась с ошибкой: {error_msg}")
                    return result
                else:
                    logging.warning(f"Video: неизвестный статус {status} для задачи {task_id}")
                    continue
                    
        except Exception as e:
            logging.error(f"Video: ошибка при генерации видео: {e}")
            return {}

    async def task_fetch(self, task_id):
        """Получает статус задачи"""
        url = f"https://api.goapi.ai/api/v1/kling/v1/videos/{task_id}"
        
        try:
            response = await async_get(
                url,
                headers={
                    'X-API-Key': GO_API_KEY,
                    'Content-Type': 'application/json'
                }
            )
            return response.json()
        except Exception as e:
            logging.error(f"Video: ошибка при получении статуса задачи {task_id}: {e}")
            return {"data": {"status": "failed", "error": {"message": str(e)}}}

    def _enhance_prompt(self, prompt: str, style: str) -> str:
        """Улучшает промпт в зависимости от выбранного стиля"""
        style_enhancements = {
            "realistic": "photorealistic, high quality, detailed, cinematic lighting",
            "cartoon": "cartoon style, animated, colorful, stylized",
            "anime": "anime style, manga, japanese animation",
            "cinematic": "cinematic, professional filmmaking, dramatic lighting, movie scene",
            "artistic": "artistic, creative, painterly, aesthetic"
        }
        
        enhancement = style_enhancements.get(style, "high quality, detailed")
        return f"{prompt}, {enhancement}"


videoService = VideoService()