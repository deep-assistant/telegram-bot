import asyncio
import logging
import requests
import json
import re

from config import GO_API_KEY, OPENROUTER_API_KEY
from services.utils import async_post, async_get
from db import data_base, db_key

# Временное хранение данных пользователей
user_temp_data = {}

class SunoService:
    def get_human_readable_error(self, error_data):
        """Convert API error messages to human-readable format"""
        if not error_data:
            return "❌ Произошла неизвестная ошибка при генерации музыки."
            
        error_msg = error_data.get('raw_message', '') or error_data.get('message', '')
        
        if 'moderation_failure' in error_msg and 'Unable to generate lyrics' in error_msg:
            return """❌ Не удалось создать музыку из-за ограничений контента.

🔍 Возможные причины:
• В описании музыки содержится неподходящий контент
• Запрос на создание музыки "без вокала/текста" может вызвать проблемы с генерацией лирики
• Описание нарушает правила сообщества

💡 Рекомендации:
• Попробуйте изменить описание музыки
• Используйте более общие термины вместо "без вокала"
• Избегайте запросов на инструментальную музыку, если хотите получить песню с текстом

Попробуйте с другим описанием!"""
        
        if 'clips generation failed' in error_msg:
            return """❌ Не удалось создать музыкальную композицию.

Возможные причины:
• Проблемы на стороне сервиса Suno
• Неподходящее описание для генерации
• Временные технические неполадки

Попробуйте изменить описание или повторить попытку позже."""
        
        # Generic fallback for other errors
        return f"""❌ Произошла ошибка при генерации музыки.

Детали ошибки: {error_msg}

Попробуйте изменить описание или повторить попытку позже."""
    def store_user_data(self, user_id: str, topic: str = None, style: str = None):
        """Сохраняет временные данные пользователя"""
        if user_id not in user_temp_data:
            user_temp_data[user_id] = {}
        if topic is not None:
            user_temp_data[user_id]['topic'] = topic
        if style is not None:
            user_temp_data[user_id]['style'] = style

    def get_user_data(self, user_id: str):
        """Получает временные данные пользователя"""
        return user_temp_data.get(user_id, {})

    def clear_user_data(self, user_id: str):
        """Очищает временные данные пользователя"""
        if user_id in user_temp_data:
            del user_temp_data[user_id]

    def generate_lyrics_with_timestamps(self, user_prompt: str, style: str = "pop") -> str:
        system_prompt = (
            f"Сгенерируй текст песни в стиле {style} с таймкодами для Diffrhythm. Формат:\n"
            "[mm:ss.ms]Первая строчка\n"
            "[mm:ss.ms]Вторая строчка\n"
            "[mm:ss.ms]Третья строчка\n"
            "...\n"
            "Тема: " + user_prompt + "\n"
            "Используй равномерные интервалы между строками (3-5 секунд). "
            "Первая строка может начинаться с 00:05.00 или позже. "
            "Не добавляй никаких пояснений, только текст песни с таймкодами. "
            "Каждая строка должна быть отдельной строкой с таймкодом."
        )
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "deepseek/deepseek-chat-v3-0324:free",
                "messages": [
                    {"role": "system", "content": system_prompt}
                ]
            })
        )
        data = response.json()
        lyrics = data["choices"][0]["message"]["content"]
        # Фильтруем строки: оставляем только строки с таймкодами в формате [mm:ss.ms]
        timestamp_pattern = r'^\[\d{2}:\d{2}\.\d{2}\].*$'
        filtered_lines = []
        for line in lyrics.splitlines():
            line = line.strip()
            if line and re.match(timestamp_pattern, line):
                filtered_lines.append(line)
        
        if not filtered_lines:
            logging.warning(f"Diffrhythm: не найдено строк с таймкодами в ответе OpenRouter: {lyrics}")
            # Возвращаем базовый пример если ничего не найдено
            return "[00:05.00]Hello, this is a test song\n[00:10.00]Generated by AI for you\n[00:15.00]Hope you like this tune"
        
        lyrics = '\n'.join(filtered_lines)
        logging.info(f"Diffrhythm: отфильтрованная лирика: {lyrics}")
        return lyrics

    async def generate_suno(self, prompt, style, task_id_get):
        # Генерируем лирику с таймкодами через OpenRouter
        logging.info(f"Diffrhythm: начинаем генерацию лирики для темы '{prompt}' в стиле '{style}'")
        lyrics = self.generate_lyrics_with_timestamps(prompt, style)
        logging.info(f"Diffrhythm: сгенерирована лирика длиной {len(lyrics)} символов")
        
        # 1. Create the task using the new /api/v1/task endpoint
        json_data = {
            "model": "Qubico/diffrhythm",
            "task_type": "txt2audio-base",
            "input": {
                "lyrics": lyrics,
                "style_prompt": style,
                "style_audio": ""
            },
            "config": {
                "webhook_config": {
                    "endpoint": "",
                    "secret": ""
                }
            }
        }
        headers = {
            'X-API-Key': GO_API_KEY,
            'Content-Type': 'application/json'
        }
        logging.info(f"Diffrhythm: отправляем JSON: {json_data}")
        logging.info(f"Diffrhythm: headers: {headers}")
        logging.info(f"Diffrhythm: размер лирики: {len(lyrics)} символов, количество строк: {len(lyrics.splitlines())}")
        response = await async_post(
            "https://api.goapi.ai/api/v1/task",
            headers=headers,
            json=json_data
        )
        response_json = response.json()
        logging.info(f"Diffrhythm: ответ от API: {response_json}")
        if 'data' not in response_json:
            error_message = response_json.get('message', 'Unknown error occurred while creating Diffrhythm task.')
            logging.error(f"Diffrhythm: ошибка создания задачи: {error_message}")
            raise Exception(f"API Error: {error_message}")
        task_id = response_json['data'].get('task_id')
        logging.info(f"Diffrhythm: создан task_id: {task_id}")
        if task_id:
            await task_id_get(task_id)
        attempts = 0
        max_attempts = 30  # Увеличиваем с 15 до 30 попыток (15 минут)
        while True:
            if attempts >= max_attempts:
                logging.error(f"Diffrhythm: превышено число попыток ожидания результата для task_id {task_id} (максимум {max_attempts} попыток)")
                return {}
            await asyncio.sleep(30)
            attempts += 1
            result = await self.task_fetch(task_id)
            status = result.get('data', {}).get('status')
            logging.info(f"Diffrhythm: polling attempt {attempts}/{max_attempts}, статус: {status}, task_id: {task_id}")
            
            if status == "pending":
                logging.info(f"Diffrhythm: задача {task_id} все еще в очереди...")
                continue
            elif status == "processing":
                logging.info(f"Diffrhythm: задача {task_id} обрабатывается...")
                continue
            elif status == "completed":
                logging.info(f"Diffrhythm: задача {task_id} завершена успешно!")
                return result
            elif status == "failed":
                error_msg = result.get('data', {}).get('error', {}).get('message', 'Unknown error')
                logging.error(f"Diffrhythm: задача {task_id} завершилась с ошибкой: {error_msg}")
                return result
            else:
                logging.warning(f"Diffrhythm: неизвестный статус {status} для задачи {task_id}")
                continue

    async def task_fetch(self, task_id):
        # 4. Updated polling endpoint
        url = f"https://api.goapi.ai/api/v1/task/{task_id}"
        response = await async_get(
            url,
            headers={
                'X-API-Key': GO_API_KEY,
                'Content-Type': 'application/json'
            }
        )
        return response.json()


sunoService = SunoService()