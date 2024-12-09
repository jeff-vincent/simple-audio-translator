import asyncio
import os
import redis

class SpeechToText():
    def __init__(self):
        self.redis_host = os.environ.get('REDIS_HOST')
        self.redis_port = os.environ.get('REDIS_PORT')
        self.r = redis.Redis(host=self.redis_host, port=self.redis_port, db=0)
        self.audio_chunk = None

    async def read_audio_from_redis_queue(self):
        pass

    async def convert_audio_to_text(self):
        pass

    async def write_text_to_redis_queue(self):
        pass

    async def run(self):
        while True:
            self.audio_chunk = self.read_audio_from_redis_queue()
            if self.audio_chunk:
                text = self.convert_audio_to_text(self.audio_chunk)
                self.write_text_to_redis_queue(text)

if __name__ == "__main__":
    speech_to_text = SpeechToText()
    asyncio.run(speech_to_text.run())
