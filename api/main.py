import asyncio
import threading
import redis
import json
import base64
from fastapi import FastAPI, WebSocket

app = FastAPI()

# Store WebSocket connections
connections = {}

# Initialize Redis client
r = redis.Redis()

@app.websocket("/ws/audio")
async def audio_stream(websocket: WebSocket):
    """
    Handles WebSocket connections for audio streaming.
    Receives audio chunks from clients and pushes them to the Redis queue.
    """
    connection_id = f"{websocket.client.host}:{websocket.client.port}"
    connections[connection_id] = websocket
    await websocket.accept()
    print(f"WebSocket connection {connection_id} accepted.")
    
    try:
        while True:
            # Receive audio chunk
            audio_chunk = await websocket.receive_bytes()
            print(f"Received audio chunk: {len(audio_chunk)} bytes")
            
            # Encode audio chunk and store it in Redis
            labeled_data = {
                'audio': base64.b64encode(audio_chunk).decode('utf-8'),
                'connection_id': connection_id
            }
            r.rpush('incoming_audio', json.dumps(labeled_data))
    except Exception as e:
        print(f"WebSocket error in {connection_id}: {e}")
    finally:
        # Cleanup on disconnect
        del connections[connection_id]
        print(f"WebSocket connection {connection_id} closed.")

@app.on_event("startup")
async def start_background_tasks():
    """
    Starts the background task for processing audio messages from Redis in a separate thread and event loop.
    """
    # Create a thread and run the `send_response` in its own event loop
    thread = threading.Thread(target=start_send_response_loop)
    thread.daemon = True  # Set as a daemon thread so it exits with the program
    thread.start()

def start_send_response_loop():
    """
    Starts a new event loop in a separate thread and runs the `send_response` function.
    """
    loop = asyncio.new_event_loop()  # Create a new event loop
    asyncio.set_event_loop(loop)  # Set it as the current event loop for this thread
    loop.run_until_complete(send_response())  # Run the function

async def send_response():
    """
    Background task to process audio messages from Redis and send responses back to WebSocket clients.
    """
    while True:
        try:
            # Blocking pop from the Redis queue for translated audio
            result = r.blpop('translated_audio', timeout=0)
            if result:
                key, data = result
                data = json.loads(data)
                
                # Decode audio data and get connection ID
                audio_chunk = base64.b64decode(data['audio'])
                connection_id = data['connection_id']

                # Retrieve the WebSocket connection
                websocket = connections.get(connection_id)
                if websocket:
                    try:
                        # Send the audio chunk back to the WebSocket client
                        await websocket.send_bytes(audio_chunk)
                        print(f"Sent audio chunk to {connection_id}")
                    except Exception as e:
                        print(f"Failed to send audio chunk to {connection_id}: {e}")
        except Exception as e:
            print(f"Error in send_response: {e}")
            await asyncio.sleep(5)  # Avoid tight loop in case of errors
        await asyncio.sleep(1)  # Delay to avoid busy-waiting
