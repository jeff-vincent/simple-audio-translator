from fastapi import FastAPI, WebSocket
import asyncio
import io

app = FastAPI()

# Store WebSocket connections
connections = {}

@app.websocket("/ws/audio")
async def audio_stream(websocket: WebSocket):
    # Unique identifier for the connection
    connection_id = f"{websocket.client.host}:{websocket.client.port}"
    
    # Store the connection in the dictionary
    connections[connection_id] = websocket
    await websocket.accept()
    print(f"WebSocket connection {connection_id} accepted.")
    
    try:
        while True:
            audio_chunk = await websocket.receive_bytes()
            print(f"Received audio chunk: {len(audio_chunk)} bytes")
            
            # Process the audio (you can implement your processing here)
            # For now, we just stream it back to the client

            # Send the audio chunk back to the same WebSocket connection
            await websocket.send_bytes(audio_chunk)
            print(f"Sent audio chunk back to {connection_id}")
    except Exception as e:
        print(f"WebSocket error in {connection_id}: {e}")
    finally:
        # Remove the connection from the dictionary when it closes
        del connections[connection_id]
        print(f"WebSocket connection {connection_id} closed.")
