# 🚀 SoniTranslate Live Stream API - Run Guide

Complete guide to run and use the real-time YouTube live stream translation service.

## 📋 **Prerequisites**

### **System Requirements**
- Python 3.8+
- FFmpeg installed on your system
- GPU recommended (CUDA support for faster processing)

### **Install Dependencies**

```bash
# Install Python dependencies
pip install -r requirements_serve.txt

# Install system FFmpeg
# Ubuntu/Debian:
sudo apt update && sudo apt install ffmpeg

# macOS:
brew install ffmpeg

# Windows (via chocolatey):
choco install ffmpeg
```

## 🎯 **Quick Start**

### **1. Start the API Server**

```bash
# Method 1: Smart launcher (recommended)
python run_serve.py

# Method 2: Direct start
python serve.py

# Method 3: Manual uvicorn
uvicorn serve:app --host 0.0.0.0 --port 8000 --reload
```

### **2. Verify Installation**

```bash
# Run test suite
python test_serve.py

# Check available channels
python channel_manager.py
```

### **3. Access the Service**

- **API Service**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 🎮 **Usage Methods**

### **Method 1: CLI Interface (Recommended for Custom URLs)**

The CLI provides easy command-line access with terminal arguments:

```bash
# List supported languages
python cli_translate.py languages

# List configured channels
python cli_translate.py channels

# Find live streams from configured channels
python cli_translate.py find-live

# Quick live video translation (positional arguments)
python cli_translate.py live "https://www.youtube.com/@nasa/live" --language tamil

# Start translation with custom URL (positional or --url)
python cli_translate.py translate "https://www.youtube.com/@nasa/live" --language tamil

# Start translation with custom settings
python cli_translate.py translate "https://www.youtube.com/@BBCNews/live" \
  --language malayalam --chunk-duration 20 --model small --output audio.mp3

# Auto-find live stream from channel URL
python cli_translate.py translate "https://www.youtube.com/@nasa" --language tamil --auto-find

# Check if URL is live before starting
python cli_translate.py translate "https://www.youtube.com/@nasa/live" --language tamil --live-check

# Monitor active streams
python cli_translate.py streams
```

### **Method 1.5: Ultra-Simple Live Video Script**

For the simplest possible usage with live video arguments:

```bash
# Super simple: just URL and language
python live_translate.py "https://www.youtube.com/@nasa/live" tamil

# With output file
python live_translate.py "https://www.youtube.com/@BBCNews/live" malayalam bbc_audio.mp3

# Translate SpaceX launch
python live_translate.py "https://www.youtube.com/@SpaceX/live" japanese
```

**CLI Examples:**

```bash
# Quick live video translation (positional arguments)
python cli_translate.py live "https://www.youtube.com/@nasa/live" --language tamil

# Ultra-simple live video translation
python live_translate.py "https://www.youtube.com/@nasa/live" tamil

# Translate BBC News to Malayalam with custom settings
python cli_translate.py translate "https://www.youtube.com/@BBCNews/live" \
  --language malayalam \
  --chunk-duration 20 \
  --model small \
  --output bbc_malayalam.mp3

# Auto-find live stream from channel URL
python cli_translate.py translate "https://www.youtube.com/@nasa" --language tamil --auto-find

# Check if URL is live before starting
python cli_translate.py translate "https://www.youtube.com/@nasa/live" --language tamil --live-check

# Quick live video with fast settings
python cli_translate.py live "https://www.youtube.com/@SpaceX/live" --language japanese --fast
```

### **Method 2: Python Client**

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

# Monitor status
status = client.get_status(result['stream_id'])
print(f"Status: {status['status']}")

# Stream audio to file
client.stream_audio(result['stream_id'], "translated_audio.mp3")
```

### **Method 3: Direct API Calls**

```bash
# List languages
curl http://localhost:8000/languages

# List channels
curl http://localhost:8000/channels

# Start Tamil translation
curl -X POST "http://localhost:8000/tamil" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/@nasa/live",
    "chunk_duration": 30,
    "transcriber_model": "base"
  }'

# Check status
curl http://localhost:8000/status/tamil_abc123def

# Stream audio
curl http://localhost:8000/stream/tamil_abc123def --output audio.mp3
```

### **Method 4: Interactive Web Interface**

1. Start the server: `python run_serve.py`
2. Open http://localhost:8000/docs
3. Use the interactive Swagger UI to test endpoints

## 📺 **Adding Custom YouTube Channels**

### **Via Configuration File**

Edit `config.json` to add your favorite channels:

```json
{
  "channels": {
    "news": [
      {
        "name": "Your Custom News",
        "url": "https://www.youtube.com/@YourChannel",
        "description": "Your favorite news channel",
        "languages": ["tamil", "malayalam", "english"]
      }
    ]
  }
}
```

### **Via API**

```bash
# Add a new channel
curl -X POST "http://localhost:8000/channels/add" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "news",
    "name": "My Channel",
    "url": "https://www.youtube.com/@mychannel",
    "description": "My favorite channel",
    "languages": ["tamil", "english"]
  }'
```

### **Via CLI**

```bash
# Add channel using channel manager
python channel_manager.py
```

## 🌍 **Supported Languages**

| Language | Endpoint | Example |
|----------|----------|---------|
| English | `/english` | `python cli_translate.py translate --url "..." --language english` |
| Tamil | `/tamil` | `python cli_translate.py translate --url "..." --language tamil` |
| Malayalam | `/malayalam` | `python cli_translate.py translate --url "..." --language malayalam` |
| Gujarati | `/gujarati` | `python cli_translate.py translate --url "..." --language gujarati` |
| Kannada | `/kannada` | `python cli_translate.py translate --url "..." --language kannada` |
| Marathi | `/marathi` | `python cli_translate.py translate --url "..." --language marathi` |
| Japanese | `/japanese` | `python cli_translate.py translate --url "..." --language japanese` |
| Korean | `/korean` | `python cli_translate.py translate --url "..." --language korean` |

## ⚙️ **Configuration Options**

### **Translation Settings**

| Parameter | Default | Description | CLI Option |
|-----------|---------|-------------|------------|
| `chunk_duration` | 30 | Audio chunk duration in seconds | `--chunk-duration` |
| `transcriber_model` | "base" | Whisper model (base/small/medium/large) | `--model` |
| `origin_language` | "Automatic detection" | Source language | `--origin-language` |

### **Environment Variables**

```bash
# GPU acceleration
export SONITR_DEVICE=cuda

# Hugging Face token for speaker diarization
export YOUR_HF_TOKEN=your_token_here

# OpenAI API for GPT translation
export OPENAI_API_KEY=your_key_here
```

## 🔧 **Troubleshooting**

### **Common Issues**

**1. Server won't start:**
```bash
# Check dependencies
python test_serve.py

# Install missing packages
pip install -r requirements_serve.txt
```

**2. FFmpeg not found:**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Verify installation
ffmpeg -version
```

**3. No live streams found:**
```bash
# Check if URL is actually live
python cli_translate.py find-live

# Test with known live channels
python cli_translate.py translate \
  --url "https://www.youtube.com/@nasa/live" \
  --language english
```

**4. Translation errors:**
```bash
# Check server logs
# Use smaller model for faster processing
python cli_translate.py translate \
  --url "..." \
  --language tamil \
  --model small \
  --chunk-duration 20
```

### **Performance Optimization**

```bash
# For faster processing (lower quality)
python cli_translate.py translate \
  --url "..." \
  --language tamil \
  --model small \
  --chunk-duration 15

# For better quality (slower)
python cli_translate.py translate \
  --url "..." \
  --language tamil \
  --model large \
  --chunk-duration 45
```

## 📊 **Monitoring & Management**

### **Check Active Streams**

```bash
# List all active translations
python cli_translate.py streams

# Or via API
curl http://localhost:8000/streams
```

### **Stop Translation**

```bash
# Stop specific stream
curl -X POST "http://localhost:8000/stop/stream_id"

# Stop all streams (restart server)
```

### **View Logs**

```bash
# Server logs are displayed in terminal
# For more detailed logs, run with debug:
uvicorn serve:app --host 0.0.0.0 --port 8000 --log-level debug
```

## 🎯 **Example Workflows**

### **Workflow 1: Quick Translation**

```bash
# 1. Start server
python run_serve.py

# 2. In another terminal, start translation
python cli_translate.py translate \
  --url "https://www.youtube.com/@nasa/live" \
  --language tamil \
  --output nasa_tamil.mp3
```

### **Workflow 2: Multi-language Monitoring**

```bash
# 1. Start multiple translations
python cli_translate.py translate --url "..." --language tamil --output tamil.mp3 &
python cli_translate.py translate --url "..." --language malayalam --output malayalam.mp3 &

# 2. Monitor all streams
python cli_translate.py streams
```

### **Workflow 3: Custom Channel Setup**

```bash
# 1. Add your channels to config.json
# 2. Find live streams
python cli_translate.py find-live

# 3. Start translation from live stream
python cli_translate.py translate \
  --url "https://www.youtube.com/@YourChannel/live" \
  --language tamil
```

## 🚀 **Production Deployment**

### **Using Docker (if available)**

```bash
# Build and run with Docker
docker build -t sonitranslate-live .
docker run -p 8000:8000 sonitranslate-live
```

### **Using Systemd Service**

```bash
# Create service file
sudo nano /etc/systemd/system/sonitranslate.service

# Start service
sudo systemctl enable sonitranslate
sudo systemctl start sonitranslate
```

## 📞 **Support**

- **Documentation**: README_SERVE.md
- **API Docs**: http://localhost:8000/docs
- **Test Suite**: `python test_serve.py`
- **Channel Manager**: `python channel_manager.py`

## 🎉 **Success Indicators**

✅ **Server running**: `http://localhost:8000` responds  
✅ **API working**: `python cli_translate.py languages` shows languages  
✅ **Live streams**: `python cli_translate.py find-live` finds streams  
✅ **Translation**: `python cli_translate.py translate --url "..." --language tamil` works  

Happy translating! 🎵🌍 