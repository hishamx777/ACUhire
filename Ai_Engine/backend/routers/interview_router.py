import os
import asyncio
from dotenv import load_dotenv
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
)

# Load environment variables (Make sure DEEPGRAM_API_KEY is in your .env file)
load_dotenv()

# Initialize the router for the AcuHire interview engine
router = APIRouter(
    prefix="/interview",
    tags=["Real-time Interview Engine"]
)

# Deepgram client configuration
config = DeepgramClientOptions(
    options={"keepalive": "true"}
)
deepgram_client = DeepgramClient(os.getenv("DEEPGRAM_API_KEY"), config)


@router.websocket("/ws/stream")
async def audio_stream_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint handling bidirectional real-time audio streaming.
    Receives audio chunks from the frontend and returns STT transcripts via Deepgram.
    """
    await websocket.accept()
    print("Client connected to AcuHire STT stream.")

    # Create a LiveClient instance for this specific connection
    dg_connection = deepgram_client.listen.asyncwebsocket.v("1")

    # Define event handlers for Deepgram
    async def on_message(self, result, **kwargs):
        sentence = result.channel.alternatives[0].transcript
        if not sentence:
            return

        is_final = result.is_final
        
        # Prepare the payload to send back to the frontend
        payload = {
            "type": "transcript",
            "text": sentence,
            "is_final": is_final
        }
        
        # Send the transcript back to the frontend
        await websocket.send_json(payload)
        
        # Here we will later inject the Logic (Keyword matching) when is_final == True
        if is_final:
            print(f"Final Transcript Received: {sentence}")

    async def on_error(self, error, **kwargs):
        print(f"Deepgram Error: {error}")

    # Bind the events to the connection
    dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
    dg_connection.on(LiveTranscriptionEvents.Error, on_error)

    # Configure the live stream options
    options = LiveOptions(
        model="nova-2", # Deepgram's fastest model
        language="ar",  # Arabic language
        smart_format=True,
        encoding="linear16", # Common audio encoding for WebSockets
        channels=1,
        sample_rate=16000,
        endpointing=True # This enables VAD (Voice Activity Detection)
    )

    try:
        # Start the Deepgram connection
        await dg_connection.start(options)

        # Continuous loop to receive audio chunks from the frontend
        while True:
            # Receive audio binary data
            data = await websocket.receive_bytes()
            
            # Forward the audio binary data to Deepgram
            await dg_connection.send(data)

    except WebSocketDisconnect:
        print("Client disconnected from the stream.")
    except Exception as e:
        print(f"Connection Exception: {e}")
    finally:
        # Ensure Deepgram connection is closed properly
        await dg_connection.finish()