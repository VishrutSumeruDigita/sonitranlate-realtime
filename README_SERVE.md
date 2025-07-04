# SoniTranslate Live Stream API

Real-time translation service for YouTube live streams with language-specific endpoints.

## Features

- **Real-time Translation**: Translate YouTube live streams in real-time
- **Multiple Languages**: Support for 17+ target languages including Tamil, Malayalam, Gujarati, Kannada, Marathi, Japanese, Korean, and more
- **Language-specific Endpoints**: Dedicated endpoints for each target language
- **Audio Streaming**: Stream translated audio in real-time
- **Background Processing**: Efficient chunk-based processing with background tasks
- **Status Monitoring**: Track translation progress and status
- **RESTful API**: Easy-to-use REST API with comprehensive documentation

## Supported Languages

- English (`/english`)
- Tamil (`/tamil`)
- Malayalam (`/malayalam`) 
- Gujarati (`/gujarati`)
- Kannada (`/kannada`)
- Marathi (`/marathi`)
- Japanese (`/japanese`)
- Korean (`/korean`)
- Hindi (`/hindi`)
- Spanish (`/spanish`)
- French (`/french`)
- German (`/german`)
- Chinese (`/chinese`)
- Arabic (`/arabic`)
- Portuguese (`/portuguese`)
- Russian (`/russian`)
- Italian (`/italian`)

## Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements_serve.txt
   ```

2. **Install system dependencies**:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install ffmpeg

   # macOS
   brew install ffmpeg

   # Windows (via chocolatey)
   choco install ffmpeg
   ```

## Quick Start

1. **Start the service**:
   ```bash
   python run_serve.py
   ```

2. **Access the API**:
   - Service: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## API Usage

### Start Translation (Language-specific endpoints)

**Translate to Tamil**:
```bash
curl -X POST "http://localhost:8000/tamil" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/@nasa/live",
    "chunk_duration": 30,
    "transcriber_model": "base",
    "origin_language": "Automatic detection"
  }'
```

**Response**:
```json
{
  "stream_id": "tamil_abc123def",
  "language": "tamil",
  "target_language": "Tamil (ta)",
  "youtube_url": "https://www.youtube.com/@nasa/live",
  "status": "starting",
  "websocket_url": "/stream/tamil_abc123def",
  "status_url": "/status/tamil_abc123def"
}
```

### Generic Start Translation

```bash
curl -X POST "http://localhost:8000/start/kannada" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/@BBCNews/live",
    "chunk_duration": 20
  }'
```

### Check Translation Status

```bash
curl "http://localhost:8000/status/tamil_abc123def"
```

**Response**:
```json
{
  "stream_id": "tamil_abc123def",
  "status": "active",
  "target_language": "Tamil (ta)",
  "youtube_url": "https://www.youtube.com/@nasa/live",
  "chunks_processed": 15,
  "total_duration": 450.0,
  "error_message": null
}
```

### Stream Translated Audio

```bash
curl "http://localhost:8000/stream/tamil_abc123def" --output translated_audio.mp3
```

### Stop Translation

```bash
curl -X POST "http://localhost:8000/stop/tamil_abc123def"
```

### List Active Streams

```bash
curl "http://localhost:8000/streams"
```

### Get Supported Languages

```bash
curl "http://localhost:8000/languages"
```

## Python Client Example

```python
from example_client import LiveTranslationClient

# Initialize client
client = LiveTranslationClient()

# Start Tamil translation
result = client.start_translation(
    youtube_url="https://www.youtube.com/@nasa/live",
    language="tamil",
    chunk_duration=30
)

stream_id = result['stream_id']

# Monitor status
status = client.get_status(stream_id)
print(f"Status: {status['status']}")

# Stream audio to file
client.stream_audio(stream_id, "translated_audio.mp3")

# Stop translation
client.stop_translation(stream_id)
```

## Request Parameters

### StreamRequest

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `youtube_url` | string | required | YouTube channel or live stream URL |
| `chunk_duration` | integer | 30 | Duration of each audio chunk in seconds |
| `quality` | string | "audio_only" | Stream quality preference |
| `transcriber_model` | string | "base" | Whisper model for transcription ("base", "small", "medium", "large") |
| `origin_language` | string | "Automatic detection" | Source language for translation |

## Response Format

### StreamStatus

| Field | Type | Description |
|-------|------|-------------|
| `stream_id` | string | Unique stream identifier |
| `status` | string | Current status ("starting", "active", "stopped", "error") |
| `target_language` | string | Target language for translation |
| `youtube_url` | string | Source YouTube URL |
| `chunks_processed` | integer | Number of audio chunks processed |
| `total_duration` | float | Total duration processed in seconds |
| `error_message` | string | Error message if status is "error" |

## Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   YouTube       │────│   Stream     │────│   Translation   │
│   Live Stream   │    │   Grabber    │    │   Processing    │
└─────────────────┘    └──────────────┘    └─────────────────┘
                               │                      │
                               │                      │
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Audio         │────│   FFmpeg     │────│   SoniTranslate │
│   Streaming     │    │   Processing │    │   Engine        │
└─────────────────┘    └──────────────┘    └─────────────────┘
```

### Processing Flow

1. **Stream Detection**: YouTube Stream Grabber detects live streams
2. **Audio Capture**: FFmpeg captures live audio in chunks
3. **Real-time Translation**: SoniTranslate processes chunks through:
   - Speech recognition (Whisper)
   - Text translation (Google Translator)
   - Text-to-speech (Azure TTS)
4. **Audio Streaming**: Translated audio streams back to clients

## Performance Optimization

### Real-time Settings

- **Chunk Duration**: 20-30 seconds for optimal latency vs quality
- **Transcriber Model**: "base" or "small" for faster processing
- **Batch Size**: 1 for minimum latency
- **Compute Type**: "float16" for speed on GPU

### Resource Management

- **Concurrent Streams**: Up to 10 simultaneous translations
- **Memory Management**: Automatic cleanup of temporary files
- **Background Processing**: Non-blocking audio processing
- **Error Recovery**: Automatic retry on processing failures

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "No live stream found" | URL not live | Check if stream is currently live |
| "No audio format available" | Stream unavailable | Try different YouTube URL |
| "Translation error" | Processing failure | Check SoniTranslate configuration |
| "FFmpeg error" | System dependency | Install FFmpeg system binary |

### Status Codes

- `200`: Success
- `400`: Bad request (invalid parameters)
- `404`: Stream not found
- `500`: Internal server error

## Advanced Configuration

### Environment Variables

```bash
export SONITR_DEVICE=cuda           # Use GPU acceleration
export YOUR_HF_TOKEN=your_token     # Hugging Face token for speaker diarization
export OPENAI_API_KEY=your_key      # OpenAI API for GPT translation
```

### Custom TTS Voices

Modify `TARGET_LANGUAGES` in `serve.py` to add custom TTS voices:

```python
TARGET_LANGUAGES = {
    "custom_tamil": "Tamil (ta)",
    # Add more custom configurations
}
```

## Troubleshooting

### Dependencies

```bash
# Check FFmpeg
ffmpeg -version

# Check Python packages
pip list | grep -E "(fastapi|uvicorn|yt-dlp)"

# Reinstall dependencies
pip install -r requirements_serve.txt --force-reinstall
```

### Service Issues

```bash
# Check if port is available
netstat -an | grep 8000

# Run with debug logging
uvicorn serve:app --host 0.0.0.0 --port 8000 --log-level debug

# Check service health
curl http://localhost:8000/
```

### Live Stream Issues

1. **Verify stream is live**: Check YouTube URL manually
2. **Check network connectivity**: Test internet connection
3. **Validate URL format**: Ensure proper YouTube URL format
4. **Monitor logs**: Check service logs for detailed errors

## Development

### Running in Development Mode

```bash
python run_serve.py
```

### API Testing

Use the interactive documentation at http://localhost:8000/docs to test endpoints.

### Custom Extensions

The service can be extended with:
- Additional language endpoints
- Custom transcription models
- Alternative TTS providers
- Enhanced audio processing
- WebSocket support for real-time updates

## License

This service uses the same license as SoniTranslate. Please refer to the main project license for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review service logs
3. Test with example YouTube streams
4. Verify all dependencies are installed 