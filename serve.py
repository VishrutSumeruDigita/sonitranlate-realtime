#!/usr/bin/env python3
"""
Real-time YouTube Live Stream Translation Service

This service provides endpoints for real-time translation of YouTube live streams
into various target languages. Each language has its own endpoint for streaming
translated audio.

Referenced from app_rvc.py SoniTranslate functionality.
"""

import asyncio
import io
import json
import logging
import os
import tempfile
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional

import ffmpeg
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from pydub import AudioSegment

# Import SoniTranslate components
from app_rvc import SoniTranslate, prog_disp
from soni_translate.language_configuration import LANGUAGES
from youtube.youtube_stream_grepper import YouTubeLiveStreamGrabber
from channel_manager import ChannelManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SoniTranslate Live Stream API",
    description="Real-time translation of YouTube live streams",
    version="1.0.0"
)

# Initialize SoniTranslate
translator = SoniTranslate()

# Initialize Channel Manager
channel_manager = ChannelManager()

# Global state management
active_streams: Dict[str, dict] = {}
executor = ThreadPoolExecutor(max_workers=10)

# Supported target languages for the service
TARGET_LANGUAGES = {
    "english": "English (en)",
    "tamil": "Tamil (ta)",
    "malayalam": "Malayalam (ml)",
    "gujarati": "Gujarati (gu)",
    "kannada": "Kannada (kn)",
    "marathi": "Marathi (mr)",
    "japanese": "Japanese (ja)",
    "korean": "Korean (ko)",
    "hindi": "Hindi (hi)",
    "spanish": "Spanish (es)",
    "french": "French (fr)",
    "german": "German (de)",
    "chinese": "Chinese - Simplified (zh-CN)",
    "arabic": "Arabic (ar)",
    "portuguese": "Portuguese (pt)",
    "russian": "Russian (ru)",
    "italian": "Italian (it)"
}


class StreamRequest(BaseModel):
    youtube_url: str
    chunk_duration: int = 30  # seconds per chunk
    quality: str = "audio_only"
    transcriber_model: str = "base"  # faster for real-time
    origin_language: str = "Automatic detection"


class StreamStatus(BaseModel):
    stream_id: str
    status: str  # "starting", "active", "stopped", "error"
    target_language: str
    youtube_url: str
    chunks_processed: int
    total_duration: float
    error_message: Optional[str] = None


class LiveStreamProcessor:
    """Handles real-time processing of live streams."""
    
    def __init__(self, stream_id: str, youtube_url: str, target_language: str, 
                 chunk_duration: int = 30, transcriber_model: str = "base",
                 origin_language: str = "Automatic detection"):
        self.stream_id = stream_id
        self.youtube_url = youtube_url
        self.target_language = target_language
        self.chunk_duration = chunk_duration
        self.transcriber_model = transcriber_model
        self.origin_language = origin_language
        
        self.status = "starting"
        self.chunks_processed = 0
        self.total_duration = 0.0
        self.error_message = None
        self.audio_queue = asyncio.Queue()
        self.stop_flag = threading.Event()
        
        # Get live stream URL
        self.grabber = YouTubeLiveStreamGrabber(audio_only=True)
        self.stream_info = None
        
    async def start_processing(self):
        """Start the live stream processing."""
        try:
            logger.info(f"Starting live stream processing for: {self.youtube_url}")
            
            # Get live stream info
            self.stream_info = self.grabber.get_live_stream_url(self.youtube_url)
            if not self.stream_info:
                self.status = "error"
                self.error_message = "No live stream found at the provided URL"
                logger.error(f"No live stream found for: {self.youtube_url}")
                return
            
            logger.info(f"Found live stream: {self.stream_info.get('title', 'Unknown')}")
            logger.info(f"Stream info keys: {list(self.stream_info.keys())}")
            
            # Log formats info for debugging
            if 'formats' in self.stream_info:
                logger.info(f"Number of formats: {len(self.stream_info['formats'])}")
                audio_formats = [f for f in self.stream_info['formats'] if f.get('acodec') != 'none']
                logger.info(f"Number of audio formats: {len(audio_formats)}")
                if audio_formats:
                    logger.info(f"Sample audio format keys: {list(audio_formats[0].keys())}")
            
            # Validate stream info has required fields
            if 'url' not in self.stream_info:
                self.status = "error"
                self.error_message = "Invalid stream info: missing URL"
                logger.error(f"Invalid stream info: {self.stream_info}")
                return
            
            self.status = "active"
            
            # Start audio capture and processing
            await asyncio.create_task(self._process_stream())
            
        except Exception as e:
            logger.error(f"Error starting stream processing: {e}")
            self.status = "error"
            self.error_message = str(e)
    
    async def _process_stream(self):
        """Process the live stream in chunks."""
        try:
            # Get the best audio format from the stream info
            if 'formats' in self.stream_info and self.stream_info['formats']:
                # Find best audio format
                audio_formats = [f for f in self.stream_info['formats'] if f.get('acodec') != 'none']
                if audio_formats:
                    # Sort by quality and get the best (handle None values)
                    audio_formats.sort(key=lambda x: (x.get('abr') or 0) + (x.get('tbr') or 0), reverse=True)
                    if 'url' not in audio_formats[0]:
                        raise Exception("Audio format missing URL")
                    stream_url = audio_formats[0]['url']
                else:
                    # Fallback to first format with audio
                    fallback_formats = [f for f in self.stream_info['formats'] if f.get('acodec') != 'none']
                    if fallback_formats:
                        if 'url' not in fallback_formats[0]:
                            raise Exception("Fallback format missing URL")
                        stream_url = fallback_formats[0]['url']
                    else:
                        # Last resort: any format with URL
                        url_formats = [f for f in self.stream_info['formats'] if 'url' in f]
                        if url_formats:
                            stream_url = url_formats[0]['url']
                        else:
                            raise Exception("No valid formats with URL found")
            else:
                # Fallback: get formats from the video URL
                audio_format = self.grabber.get_best_audio_format(self.stream_info['url'])
                if not audio_format:
                    raise Exception("No audio format available")
                stream_url = audio_format['url']
            
            logger.info(f"Using audio stream URL: {stream_url}")
            
            # Start FFmpeg process to capture audio chunks
            process = (
                ffmpeg
                .input(stream_url, t=None)  # Continuous input
                .output('pipe:', format='wav', acodec='pcm_s16le', ac=1, ar='16000')
                .run_async(pipe_stdout=True, pipe_stderr=True)
            )
            
            chunk_size = 16000 * self.chunk_duration  # 16kHz * duration in seconds
            audio_buffer = b''
            
            while not self.stop_flag.is_set():
                # Read audio data from FFmpeg
                chunk = process.stdout.read(4096)
                if not chunk:
                    break
                
                audio_buffer += chunk
                
                # Process when we have enough audio for a chunk
                if len(audio_buffer) >= chunk_size * 2:  # 2 bytes per sample
                    # Extract one chunk worth of audio
                    chunk_data = audio_buffer[:chunk_size * 2]
                    audio_buffer = audio_buffer[chunk_size * 2:]
                    
                    # Process this chunk in background
                    asyncio.create_task(self._process_audio_chunk(chunk_data))
                    
                    self.chunks_processed += 1
                    self.total_duration += self.chunk_duration
            
            # Clean up FFmpeg process
            process.terminate()
            process.wait()
            
        except Exception as e:
            logger.error(f"Error in stream processing: {e}")
            self.status = "error"
            self.error_message = str(e)
    
    async def _process_audio_chunk(self, audio_data: bytes):
        """Process a single audio chunk through translation."""
        try:
            # Save audio chunk to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_audio_path = temp_file.name
            
            try:
                # Process through SoniTranslate
                output_path = await asyncio.get_event_loop().run_in_executor(
                    executor, self._translate_audio_chunk, temp_audio_path
                )
                
                if output_path and os.path.exists(output_path):
                    # Read translated audio
                    with open(output_path, 'rb') as f:
                        translated_audio = f.read()
                    
                    # Add to audio queue
                    await self.audio_queue.put({
                        'chunk_id': self.chunks_processed,
                        'audio_data': translated_audio,
                        'timestamp': time.time()
                    })
                    
                    # Clean up
                    os.unlink(output_path)
                
            finally:
                # Clean up temp file
                if os.path.exists(temp_audio_path):
                    os.unlink(temp_audio_path)
                    
        except Exception as e:
            logger.error(f"Error processing audio chunk: {e}")
    
    def _translate_audio_chunk(self, audio_path: str) -> Optional[str]:
        """Translate a single audio chunk using SoniTranslate."""
        try:
            # Configure for fast real-time processing
            output_path = translator.multilingual_media_conversion(
                media_file=audio_path,
                origin_language=self.origin_language,
                target_language=self.target_language,
                transcriber_model=self.transcriber_model,
                compute_type="bfloat16",  # Optimized for RTX 4090
                batch_size=4,  # Increased batch size for RTX 4090
                output_type="audio (mp3)",
                mix_method_audio="Adjusting volumes and mixing audio",
                volume_original_audio=0.1,  # Lower original audio
                volume_translated_audio=1.0,
                segment_duration_limit=15,  # Slightly longer segments for better quality
                enable_cache=False,  # No caching for real-time
                is_gui=False
            )
            
            return output_path
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return None
    
    def stop(self):
        """Stop the stream processing."""
        self.stop_flag.set()
        self.status = "stopped"
    
    async def get_audio_chunk(self):
        """Get the next translated audio chunk."""
        try:
            chunk = await asyncio.wait_for(self.audio_queue.get(), timeout=5.0)
            return chunk
        except asyncio.TimeoutError:
            return None


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "SoniTranslate Live Stream API",
        "version": "1.0.0",
        "supported_languages": list(TARGET_LANGUAGES.keys()),
        "active_streams": len(active_streams)
    }


@app.get("/languages")
async def get_supported_languages():
    """Get list of supported target languages."""
    return {
        "supported_languages": TARGET_LANGUAGES,
        "total_count": len(TARGET_LANGUAGES)
    }


@app.post("/start/{language}")
async def start_translation_stream(
    language: str, 
    request: StreamRequest, 
    background_tasks: BackgroundTasks
):
    """Start a live translation stream for a specific language."""
    
    # Validate language
    if language not in TARGET_LANGUAGES:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported language: {language}. Supported languages: {list(TARGET_LANGUAGES.keys())}"
        )
    
    # Generate unique stream ID
    stream_id = f"{language}_{uuid.uuid4().hex[:8]}"
    
    # Create processor
    processor = LiveStreamProcessor(
        stream_id=stream_id,
        youtube_url=request.youtube_url,
        target_language=TARGET_LANGUAGES[language],
        chunk_duration=request.chunk_duration,
        transcriber_model=request.transcriber_model,
        origin_language=request.origin_language
    )
    
    # Store in active streams
    active_streams[stream_id] = {
        "processor": processor,
        "language": language,
        "created_at": time.time()
    }
    
    # Start processing in background
    background_tasks.add_task(processor.start_processing)
    
    return {
        "stream_id": stream_id,
        "language": language,
        "target_language": TARGET_LANGUAGES[language],
        "youtube_url": request.youtube_url,
        "status": "starting",
        "websocket_url": f"/stream/{stream_id}",
        "status_url": f"/status/{stream_id}"
    }


@app.get("/status/{stream_id}")
async def get_stream_status(stream_id: str):
    """Get the status of a translation stream."""
    
    if stream_id not in active_streams:
        raise HTTPException(status_code=404, detail="Stream not found")
    
    processor = active_streams[stream_id]["processor"]
    
    return StreamStatus(
        stream_id=stream_id,
        status=processor.status,
        target_language=processor.target_language,
        youtube_url=processor.youtube_url,
        chunks_processed=processor.chunks_processed,
        total_duration=processor.total_duration,
        error_message=processor.error_message
    )


@app.get("/stream/{stream_id}")
async def stream_translated_audio(stream_id: str):
    """Stream translated audio chunks."""
    
    if stream_id not in active_streams:
        raise HTTPException(status_code=404, detail="Stream not found")
    
    processor = active_streams[stream_id]["processor"]
    
    async def generate_audio():
        """Generate audio chunks for streaming."""
        while processor.status == "active" and not processor.stop_flag.is_set():
            chunk = await processor.get_audio_chunk()
            if chunk:
                # Yield audio data with headers
                yield b'--audio-boundary\r\n'
                yield b'Content-Type: audio/mpeg\r\n'
                yield f'Content-Length: {len(chunk["audio_data"])}\r\n'.encode()
                yield f'X-Chunk-ID: {chunk["chunk_id"]}\r\n'.encode()
                yield f'X-Timestamp: {chunk["timestamp"]}\r\n'.encode()
                yield b'\r\n'
                yield chunk["audio_data"]
                yield b'\r\n'
            else:
                # Send keep-alive
                yield b'--audio-boundary\r\n'
                yield b'Content-Type: text/plain\r\n'
                yield b'Content-Length: 0\r\n'
                yield b'\r\n\r\n'
            
            await asyncio.sleep(0.1)  # Brief pause
    
    return StreamingResponse(
        generate_audio(),
        media_type="multipart/x-mixed-replace; boundary=audio-boundary",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Stream-ID": stream_id
        }
    )


@app.post("/stop/{stream_id}")
async def stop_translation_stream(stream_id: str):
    """Stop a translation stream."""
    
    if stream_id not in active_streams:
        raise HTTPException(status_code=404, detail="Stream not found")
    
    processor = active_streams[stream_id]["processor"]
    processor.stop()
    
    # Remove from active streams
    del active_streams[stream_id]
    
    return {"message": f"Stream {stream_id} stopped successfully"}


@app.get("/streams")
async def list_active_streams():
    """List all active translation streams."""
    
    streams = []
    for stream_id, stream_data in active_streams.items():
        processor = stream_data["processor"]
        streams.append({
            "stream_id": stream_id,
            "language": stream_data["language"],
            "target_language": processor.target_language,
            "status": processor.status,
            "chunks_processed": processor.chunks_processed,
            "total_duration": processor.total_duration,
            "created_at": stream_data["created_at"]
        })
    
    return {"active_streams": streams, "total_count": len(streams)}


@app.get("/channels")
async def list_channels():
    """List all configured channels."""
    all_channels = channel_manager.get_all_channels()
    return {
        "channels": all_channels,
        "total_categories": len(all_channels),
        "total_channels": sum(len(channels) for channels in all_channels.values())
    }


@app.get("/channels/{category}")
async def get_channels_by_category(category: str):
    """Get channels in a specific category."""
    channels = channel_manager.get_channels_by_category(category)
    return {
        "category": category,
        "channels": [
            {
                "name": ch.name,
                "url": ch.url,
                "description": ch.description,
                "languages": ch.languages
            } for ch in channels
        ],
        "total_count": len(channels)
    }


@app.get("/channels/language/{language}")
async def get_channels_for_language(language: str):
    """Get all channels that support a specific language."""
    channels = channel_manager.get_channels_for_language(language)
    return {
        "language": language,
        "channels": [
            {
                "name": ch.name,
                "url": ch.url,
                "description": ch.description,
                "languages": ch.languages
            } for ch in channels
        ],
        "total_count": len(channels)
    }


@app.post("/channels/add")
async def add_channel(
    category: str,
    name: str,
    url: str,
    description: str = "",
    languages: List[str] = None
):
    """Add a new channel to the configuration."""
    if languages is None:
        languages = ["english"]
    
    channel_manager.add_channel(category, name, url, description, languages)
    return {"message": f"Channel '{name}' added to category '{category}'"}


@app.delete("/channels/{name}")
async def remove_channel(name: str):
    """Remove a channel by name."""
    success = channel_manager.remove_channel(name)
    if success:
        return {"message": f"Channel '{name}' removed successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Channel '{name}' not found")


# Language-specific convenience endpoints
@app.post("/english")
async def translate_to_english(request: StreamRequest, background_tasks: BackgroundTasks):
    """Start English translation stream."""
    return await start_translation_stream("english", request, background_tasks)

@app.post("/tamil")  
async def translate_to_tamil(request: StreamRequest, background_tasks: BackgroundTasks):
    """Start Tamil translation stream."""
    return await start_translation_stream("tamil", request, background_tasks)

@app.post("/malayalam")
async def translate_to_malayalam(request: StreamRequest, background_tasks: BackgroundTasks):
    """Start Malayalam translation stream."""
    return await start_translation_stream("malayalam", request, background_tasks)

@app.post("/gujarati")
async def translate_to_gujarati(request: StreamRequest, background_tasks: BackgroundTasks):
    """Start Gujarati translation stream."""
    return await start_translation_stream("gujarati", request, background_tasks)

@app.post("/kannada")
async def translate_to_kannada(request: StreamRequest, background_tasks: BackgroundTasks):
    """Start Kannada translation stream."""
    return await start_translation_stream("kannada", request, background_tasks)

@app.post("/marathi")
async def translate_to_marathi(request: StreamRequest, background_tasks: BackgroundTasks):
    """Start Marathi translation stream."""
    return await start_translation_stream("marathi", request, background_tasks)

@app.post("/japanese")
async def translate_to_japanese(request: StreamRequest, background_tasks: BackgroundTasks):
    """Start Japanese translation stream."""
    return await start_translation_stream("japanese", request, background_tasks)

@app.post("/korean")
async def translate_to_korean(request: StreamRequest, background_tasks: BackgroundTasks):
    """Start Korean translation stream."""
    return await start_translation_stream("korean", request, background_tasks)


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    # Stop all active streams
    for stream_id in list(active_streams.keys()):
        processor = active_streams[stream_id]["processor"]
        processor.stop()
    
    active_streams.clear()
    executor.shutdown(wait=True)


if __name__ == "__main__":
    # Add required dependencies check
    try:
        import ffmpeg
        logger.info("FFmpeg available")
    except ImportError:
        logger.error("FFmpeg-python not installed. Run: pip install ffmpeg-python")
        exit(1)
    
    # Start the server
    uvicorn.run(
        "serve:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

