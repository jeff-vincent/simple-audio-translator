import asyncio
import os
import redis

class TextToSpeech():
    def __init__(self):
        self.redis_host = os.environ.get('REDIS_HOST')
        self.redis_port = os.environ.get('REDIS_PORT')
        self.r = redis.Redis(host=self.redis_host, port=self.redis_port, db=0)
        self.translated_text = None
        self.output_audio = None


    async def read_translated_text_from_redis_queue(self):
        pass

    async def convert_translated_text_to_audio(self):
        pass

    async def write_translated_audio_to_redis_queue(self):
        pass

    async def run(self):
        while True:
            self.translated_text = self.read_translated_text_from_redis_queue()
            if self.translated_text:
                translated_audio = self.translate_text(self.incoming_text)
                self.write_translated_audio_to_redis_queue(translated_audio)

if __name__ == "__main__":
    text_to_speech = TextToSpeech()
    asyncio.run(text_to_speech.run())
