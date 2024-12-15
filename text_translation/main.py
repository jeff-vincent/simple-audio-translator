import asyncio
import os
import redis
import json
from openai import OpenAI

class TextTranslator():
    def __init__(self):
        self.redis_host = os.environ.get('REDIS_HOST')
        self.redis_port = os.environ.get('REDIS_PORT')
        self.r = redis.Redis()
        self.incoming_text = None
        self.output_text = None
        self.openai_api_client = OpenAI(api_key='')


    async def read_text_from_redis_queue(self):
        key, data = self.r.blpop("written_text", timeout=0)
        if data:
            print(f"Processing data from {key}")
            print(data)
            return data

    def translate_text(self, data):
        prompt = f"If the following text is in English, translate it to Spanish, and if it is in Spanish, translate it to English: {data}"
        response = self.openai_api_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                { 'role': "system", 'content': "You are a helpful assistant." },
                {
                    'role': "user",
                    'content': prompt,
                },
            ],
        )
        return response.choices[0].message.content
        

    async def write_translated_text_to_redis_queue(self):
        pass

    async def run(self):
        while True:
            data = await self.read_text_from_redis_queue()
            if data:
                translated_text = self.translate_text(data)
                print(translated_text)
            #     self.write_translated_text_to_redis_queue(translated_text)

if __name__ == "__main__":
    text_translator = TextTranslator()
    asyncio.run(text_translator.run())
