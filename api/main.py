from fastapi import FastAPI, WebSocket
from fastapi.concurrency import run_in_threadpool
import asyncio
import redis
import json
import base64

app = FastAPI()

# Store WebSocket connections
connections = {}
audio_chunks = []

r = redis.Redis()

@app.websocket("/ws/audio")
async def audio_stream(websocket: WebSocket):
    connection_id = f"{websocket.client.host}:{websocket.client.port}"
    connections[connection_id] = websocket
    await websocket.accept()
    print(f"WebSocket connection {connection_id} accepted.")
    
    try:
        while True:
            # Receive audio chunk
            audio_chunk = await websocket.receive_bytes()
            print(f"Received audio chunk: {len(audio_chunk)} bytes")
            print(audio_chunk)
            labeled_data = {'audio_chunk': base64.b64encode(audio_chunk).decode('utf-8'), 'connection_id': connection_id}
            result = r.rpush('incoming_audio', json.dumps(labeled_data))
            print(result)
            
            # Store the audio chunk with its connection ID
            # audio_chunks.append(labeled_data)
    except Exception as e:
        print(f"WebSocket error in {connection_id}: {e}")
    finally:
        # Cleanup on disconnect
        del connections[connection_id]
        print(f"WebSocket connection {connection_id} closed.")

@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(send_response())

async def send_response():
    while True:
        if audio_chunks:
            for audio_chunk_dict in audio_chunks[:]:  # Copy list to avoid modification during iteration
                connection_id = audio_chunk_dict['connection_id']
                audio_chunk = audio_chunk_dict['audio_chunk']

                # Send back to the same WebSocket connection
                websocket = connections.get(connection_id)
                if websocket:
                    try:
                        await websocket.send_bytes(audio_chunk)
                        print(f"Sent audio chunk to {connection_id}")
                    except Exception as e:
                        print(f"Failed to send audio chunk to {connection_id}: {e}")
                
                # Remove processed chunk
                audio_chunks.remove(audio_chunk_dict)
        await asyncio.sleep(1)  # Delay to avoid busy-waiting
