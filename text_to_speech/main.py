import asyncio
import base64
import json
import os

import redis
from openai import OpenAI

class TextToSpeech():
    def __init__(self):
        self.redis_host = os.environ.get('REDIS_HOST')
        self.redis_port = os.environ.get('REDIS_PORT')
        # self.r = redis.Redis(host=self.redis_host, port=self.redis_port, db=0)
        self.r = redis.Redis()
        self.openai_api_client = OpenAI(api_key='')


    async def read_translated_text_from_redis_queue(self):
        key, data = self.r.blpop("translated_text", timeout=0)
        if data:
            print(f"Processing data from {key}")
            data = json.loads(data)
            translated_text = data['text']
            connection_id = data['connection_id']

            return translated_text, connection_id

    async def convert_translated_text_to_audio(self, text):
        response = self.openai_api_client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
            )
        return response.content

    async def write_translated_audio_to_redis_queue(self, translated_audio, connection_id):
        data = {'audio': base64.b64encode(translated_audio).decode('utf-8'), 'connection_id': connection_id}
        self.r.rpush('translated_audio', json.dumps(data))
        return None

    async def run(self):
        while True:
            translated_text, connection_id = await self.read_translated_text_from_redis_queue()
            if translated_text:
                translated_audio = await self.convert_translated_text_to_audio(translated_text)
                await self.write_translated_audio_to_redis_queue(translated_audio, connection_id)

if __name__ == "__main__":
    text_to_speech = TextToSpeech()
    asyncio.run(text_to_speech.run())
