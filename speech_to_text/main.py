import asyncio
import json
import os
import redis
import base64
import websockets

async def connect_socket(uri):
    async with websockets.connect(uri) as websocket:
        return websocket

class SpeechToText():
    def __init__(self):
        # self.vosk_uri = os.environ.get('VOSK_URI')
        self.vosk_uri = 'ws://localhost:2700'
        self.redis_host = os.environ.get('REDIS_HOST')
        self.redis_port = os.environ.get('REDIS_PORT')
        # self.r = redis.Redis(host=self.redis_host, port=self.redis_port, db=0)
        self.r = redis.Redis()
        self.vosk_ws_connection = None
        
    async def connect_socket(self):
        async with websockets.connect(self.vosk_uri) as websocket:
            self.vosk_ws_connection = websocket

    async def read_audio_from_redis_queue(self):
        # read audio chunk from redis
        key, data = self.r.blpop("incoming_audio", timeout=0)
        if data:
            print(f"Processing data from {key}")
            # data = data.decode("utf8")
            data = json.loads(data)
            # convert json back to original bytes
            audio_chunk = base64.b64decode(data['audio_chunk'])
            return audio_chunk

    async def convert_audio_to_text(self, data):
        # TODO: replace vosk with something else...
        return None

    async def write_text_to_redis_queue(self, text):
        # build dict with text
        # convert dict to json
        # write json to redis
        pass

    async def run(self):
        while True:
            audio_chunk = await self.read_audio_from_redis_queue()
            if audio_chunk:
                await self.connect_socket()
                text = await self.convert_audio_to_text(audio_chunk)
                await self.write_text_to_redis_queue(text)

if __name__ == "__main__":
    speech_to_text = SpeechToText()
    asyncio.run(speech_to_text.run())
