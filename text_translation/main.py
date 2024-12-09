import asyncio
import os
import redis

class TextTranslator():
    def __init__(self):
        self.redis_host = os.environ.get('REDIS_HOST')
        self.redis_port = os.environ.get('REDIS_PORT')
        self.r = redis.Redis(host=self.redis_host, port=self.redis_port, db=0)
        self.incoming_text = None
        self.output_text = None


    async def read_text_from_redis_queue(self):
        pass

    async def translate_text(self):
        pass

    async def write_translated_text_to_redis_queue(self):
        pass

    async def run(self):
        while True:
            self.incoming_text = self.read_text_from_redis_queue()
            if self.incoming_text:
                translated_text = self.translate_text(self.incoming_text)
                self.write_translated_text_to_redis_queue(translated_text)

if __name__ == "__main__":
    text_translator = TextTranslator()
    asyncio.run(text_translator.run())
