import os
import logging
from typing import Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Initialize environment variables
load_dotenv()

# Configure logging for production readiness
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Singleton pattern for the OpenAI client to reuse the connection pool
_client: Optional[AsyncOpenAI] = None

def _get_openai_client() -> AsyncOpenAI:
    """
    Returns a singleton instance of the AsyncOpenAI client.
    Ensures that the client is instantiated only once to optimize network overhead.
    """
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("CRITICAL: OPENAI_API_KEY environment variable is missing.")
        _client = AsyncOpenAI(api_key=api_key)
    return _client

async def generate_speech(text: str, voice: str = "alloy") -> bytes:
    """
    Converts input text to speech using OpenAI's fast tts-1 model.
    Optimized for real-time streaming with asynchronous execution.
    
    Args:
        text (str): The input text to be synthesized.
        voice (str): The voice model ID (e.g., 'alloy', 'echo', 'onyx').
        
    Returns:
        bytes: The generated audio data in MP3 format, or an empty byte string if an error occurs.
    """
    if not text or not text.strip():
        logger.warning("Empty text provided for TTS generation. Skipping API call.")
        return b""

    try:
        logger.info(f"Requesting TTS for text chunk: '{text[:40]}...'")
        client = _get_openai_client()
        
        # 'tts-1' is specifically optimized for low latency real-time applications
        response = await client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
            response_format="mp3"
        )
        
        audio_bytes = response.read()
        logger.info("TTS audio generated and successfully read into memory.")
        return audio_bytes
        
    except Exception as e:
        logger.error(f"Failed to generate speech via OpenAI API: {e}", exc_info=True)
        return b""
