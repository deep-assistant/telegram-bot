import logging

from openai import AsyncOpenAI
from config import PROXY_URL  # Import PROXY_URL from config
from services.utils import async_get  # Assuming this is your async HTTP utility

class VoiceService:
    def __init__(self, token):
        """Initialize the VoiceService with a token, which can be a string or a dict with 'id'."""
        if isinstance(token, str):
            api_key = token  # Use the string directly as the API key
        elif hasattr(token, "__getitem__"):  # Check if token is dict-like (supports token["id"])
            try:
                api_key = token["id"]  # Extract 'id' from the token
            except (KeyError, TypeError) as e:
                logging.error(f"Invalid token format: {e}")
                raise ValueError("Token must be a string or a dictionary with an 'id' key containing the API key")
        else:
            logging.error(f"Unsupported token type: {type(token)}")
            raise ValueError("Token must be a string or a dictionary with an 'id' key containing the API key")

        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=f"{PROXY_URL}/v1/"
        )

    async def transcribe_voice(self, voice_file_url: str):
        """Transcribe a voice file from a URL using OpenAI Whisper."""
        try:
            # Fetch voice data asynchronously
            voice_response = await async_get(voice_file_url)
            if voice_response.status_code != 200:
                return {"success": False, "text": f"Error: Не удалось скачать аудиофайл (статус: {voice_response.status_code})"}

            voice_data = voice_response.content

            # Perform transcription using the pre-initialized client
            transcription = await self.client.audio.transcriptions.create(
                file=('audio.ogg', voice_data, 'audio/ogg'),
                model="whisper-1",
                language="ru"
            )

            logging.info(f"Transcription - Duration: {transcription.duration}, Text: {transcription.text}")

            return {
                "success": True,
                "text": transcription.text,
                "energy": int(transcription.duration * 15)
            }

        except Exception as e:
            logging.error(f"Error transcribing voice: {e}")
            return {
                "success": False,
                "text": f"Error: Не удалось распознать голосовое сообщение ({str(e)})"
            }