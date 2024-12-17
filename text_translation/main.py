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
        self.openai_api_client = OpenAI(api_key='')

    async def read_text_from_redis_queue(self):
        key, data = self.r.blpop("text_to_translate", timeout=0)
        if data:
            print(f"Processing data from {key}")
            data = json.loads(data)
            text_to_tranlate = data['text']
            connection_id = data['connection_id']

            return text_to_tranlate, connection_id

    def translate_text(self, data):
        # TODO: add dropdown to select source / target language in UI
        source_language = 'English'
        target_language = 'Spanish'
        prompt = f"Translate the following from {source_language} to {target_language}: {data}"
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
        

    def write_translated_text_to_redis_queue(self, translated_text, connection_id):
        data = {'text': translated_text, 'connection_id': connection_id}
        self.r.rpush('translated_text', json.dumps(data))

    async def run(self):
        while True:
            text_to_translate, connection_id = await self.read_text_from_redis_queue()
            if text_to_translate:
                translated_text = self.translate_text(text_to_translate)
                print(translated_text)
                self.write_translated_text_to_redis_queue(translated_text, connection_id)

if __name__ == "__main__":
    text_translator = TextTranslator()
    asyncio.run(text_translator.run())
