import asyncio
import threading
import redis
import json
import base64
from fastapi import FastAPI, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Queue to manage WebSocket connections
cq = []

# Initialize Redis client
r = redis.Redis()

pubsub = r.pubsub()
pubsub.subscribe('output')


@app.websocket("/ws/audio")
async def audio_stream(websocket: WebSocket):
    """
    Handles WebSocket connections for audio streaming.
    Receives audio chunks from clients and pushes them to the Redis queue.
    """
    connection_id = f"{websocket.client.host}:{websocket.client.port}"
    await websocket.accept()
    connection = {
        "connection_id": connection_id,
        "websocket": websocket,
        "source_language": "English",
        "target_language": "Spanish"
    }
    cq.append(connection) 
    print(f"WebSocket connection {connection_id} accepted.")

    try:
        while True:
            # Receive any type of data
            message = await websocket.receive()

            # Handle text messages for language updates
            if "text" in message:
                try:
                    data = json.loads(message["text"])
                    connection["source_language"] = data.get("source_language", connection["source_language"])
                    connection["target_language"] = data.get("target_language", connection["target_language"])
                    print(f"Updated languages for {connection_id}: {connection['source_language']} -> {connection['target_language']}")
                except json.JSONDecodeError:
                    print(f"Invalid JSON from {connection_id}: {message['text']}")

            # Handle binary audio data
            elif "bytes" in message:
                audio_chunk = message["bytes"]
                print(f"Received audio chunk from {connection_id}: {len(audio_chunk)} bytes")

                # Encode audio chunk and store it in Redis
                labeled_data = {
                    'audio': base64.b64encode(audio_chunk).decode('utf-8'),
                    'connection_id': connection_id,
                    'source_language': connection["source_language"],
                    'target_language': connection["target_language"],
                }
                r.rpush('incoming_audio', json.dumps(labeled_data))

    except Exception as e:
        print(f"WebSocket error in {connection_id}: {e}")
    finally:
        # Cleanup on disconnect
        cq = [c for c in cq if c['connection_id'] != connection_id]
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
    try:
        for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])

                # Decode audio data and get connection ID
                audio_chunk = base64.b64decode(data["audio"])
                connection_id = data["connection_id"]
                print(connection_id)

                for conn in cq:
                    if conn["connection_id"] == connection_id:
                        websocket = conn["websocket"]

                # Send the audio chunk to the WebSocket client if it exists and is active
                if websocket:
                    try:
                        await websocket.send_bytes(audio_chunk)
                        print(f"Sent audio chunk to {connection_id}")
                    except Exception as e:
                        print(f"Failed to send audio chunk to {connection_id}: {e}")

    except Exception as e:
        print(f"Error in send_response: {e}")
        await asyncio.sleep(5)  # Avoid tight loop in case of errors


@app.post('/store')
def store_translation(request: Request):
    """
    Stores the translated text in Redis.
    """
    data = request.json()
    print(data)
    return None
