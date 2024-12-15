import asyncio
import json
import os
import redis
import base64
import websockets
import assemblyai
import random
import string

class SpeechToText():
    def __init__(self):
        self.redis_host = os.environ.get('REDIS_HOST')
        self.redis_port = os.environ.get('REDIS_PORT')
        # self.r = redis.Redis(host=self.redis_host, port=self.redis_port, db=0)
        self.r = redis.Redis()
        self.assembly_ai = assemblyai.settings.api_key = '' 
        
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
            # write to tmp file; return filepath
            random_string = ''.join(random.choices(string.ascii_letters,k=7))
            filepath = f'{random_string}.mp3'
            with open(filepath, 'wb') as f:
                f.write(audio_chunk)
            return filepath

    async def convert_audio_to_text(self, filepath):
        # Assembly AI https://www.assemblyai.com/docs/api-reference/streaming/realtime#handshake
        transcriber = assemblyai.Transcriber()
        transcript = transcriber.transcribe(filepath)


        if transcript.status == assemblyai.TranscriptStatus.error:
            print(transcript.error)
        else:
            print(transcript.text)
            return transcript.text

        return None
    
    # def on_data(self, transcript: assemblyai.RealtimeTranscript):
    #     print(transcript)
    #     print(type(transcript))
    #     # if not transcript.text:
    #     #     return

    #     # if isinstance(transcript, assemblyai.RealtimeFinalTranscript):
    #     #     print(transcript.text, end="\r\n")
    #     # else:
    #     #     print(transcript.text, end="\r")

    # def on_error(self, error: assemblyai.RealtimeError):
    #     print("An error occured:", error)

    async def write_text_to_redis_queue(self, text):
        self.r.rpush('written_text', text)
        return None

    async def run(self):
        while True:
            filepath = await self.read_audio_from_redis_queue()
            if filepath:
                # await self.connect_socket()
                text = await self.convert_audio_to_text(filepath)
                if text:
                    await self.write_text_to_redis_queue(text)

if __name__ == "__main__":
    speech_to_text = SpeechToText()
    asyncio.run(speech_to_text.run())
