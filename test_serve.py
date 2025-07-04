#!/usr/bin/env python3
"""
Test script for the SoniTranslate Live Stream API

This script tests the YouTube stream grabber and basic functionality
of the live translation service.
"""

import sys
import time
import logging
import asyncio
from youtube.youtube_stream_grepper import YouTubeLiveStreamGrabber

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_youtube_stream_grabber():
    """Test the YouTube live stream grabber functionality."""
    
    print("🧪 Testing YouTube Live Stream Grabber")
    print("=" * 50)
    
    # Test channels that often have live streams
    test_channels = [
        "https://www.youtube.com/@NASA"
    ]
    
    grabber = YouTubeLiveStreamGrabber(audio_only=True)
    live_streams_found = []
    
    for channel_url in test_channels:
        print(f"\n📺 Checking {channel_url}...")
        
        try:
            # Check if channel is live
            is_live = grabber.is_channel_live(channel_url)
            
            if is_live:
                # Get stream info
                stream_info = grabber.get_live_stream_url(channel_url)
                
                if stream_info:
                    print(f"✅ LIVE STREAM FOUND!")
                    print(f"   Title: {stream_info['title']}")
                    print(f"   Channel: {stream_info['channel']}")
                    print(f"   Viewers: {stream_info.get('view_count', 'N/A')}")
                    
                    # Test audio format extraction
                    audio_format = grabber.get_best_audio_format(stream_info['url'])
                    if audio_format:
                        print(f"   Audio Format: {audio_format.get('ext', 'unknown')}")
                        print(f"   Audio Bitrate: {audio_format.get('abr', 'unknown')} kbps")
                    
                    live_streams_found.append({
                        'channel': channel_url,
                        'title': stream_info['title'],
                        'stream_url': stream_info['url']
                    })
                else:
                    print(f"❌ Live detection failed")
            else:
                print(f"📵 No live stream currently")
                
        except Exception as e:
            print(f"⚠️  Error checking {channel_url}: {e}")
    
    print(f"\n📊 Summary: Found {len(live_streams_found)} live streams")
    return live_streams_found

def test_url_normalization():
    """Test URL normalization functionality."""
    
    print("\n🔧 Testing URL Normalization")
    print("=" * 30)
    
    grabber = YouTubeLiveStreamGrabber()
    
    test_urls = [
        "https://www.youtube.com/@nasa",
        "https://www.youtube.com/c/NASA",
        "https://www.youtube.com/channel/UCLA_DiR1FfKNvjuUpBHmylQ",
        "https://www.youtube.com/@nasa/live",
        "nasa",  # Just channel name
        "https://youtu.be/dQw4w9WgXcQ"  # Regular video
    ]
    
    for url in test_urls:
        try:
            normalized = grabber._normalize_channel_url(url)
            print(f"  {url} → {normalized}")
        except Exception as e:
            print(f"  {url} → Error: {e}")

def test_dependencies():
    """Test if all required dependencies are available."""
    
    print("\n🔍 Testing Dependencies")
    print("=" * 25)
    
    dependencies = [
        ('yt_dlp', 'YouTube downloader'),
        ('fastapi', 'FastAPI web framework'),
        ('uvicorn', 'ASGI server'),
        ('pydantic', 'Data validation'),
        ('ffmpeg', 'FFmpeg Python bindings'),
        ('requests', 'HTTP requests'),
        ('asyncio', 'Async programming')
    ]
    
    missing = []
    
    for dep, description in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} - {description}")
        except ImportError:
            print(f"❌ {dep} - {description} (MISSING)")
            missing.append(dep)
    
    # Test system FFmpeg
    try:
        import subprocess
        subprocess.run(['ffmpeg', '-version'], 
                      capture_output=True, check=True)
        print("✅ ffmpeg - System binary available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  ffmpeg - System binary not found")
        missing.append('ffmpeg-system')
    
    return missing

async def test_live_stream_processing():
    """Test live stream processing with a mock stream."""
    
    print("\n⚡ Testing Live Stream Processing")
    print("=" * 35)
    
    # This would require an actual live stream to test properly
    # For now, just test the class initialization
    
    try:
        from serve import LiveStreamProcessor
        
        processor = LiveStreamProcessor(
            stream_id="test_123",
            youtube_url="https://www.youtube.com/@nasa/live",
            target_language="Tamil (ta)",
            chunk_duration=10,
            transcriber_model="base"
        )
        
        print("✅ LiveStreamProcessor initialized successfully")
        print(f"   Stream ID: {processor.stream_id}")
        print(f"   Target Language: {processor.target_language}")
        print(f"   Chunk Duration: {processor.chunk_duration}s")
        
        return True
        
    except Exception as e:
        print(f"❌ LiveStreamProcessor test failed: {e}")
        return False

def main():
    """Run all tests."""
    
    print("🚀 SoniTranslate Live Stream API Test Suite")
    print("=" * 60)
    
    # Test dependencies first
    missing_deps = test_dependencies()
    
    if missing_deps:
        print(f"\n⚠️  Missing dependencies: {missing_deps}")
        print("Please install them before running the service:")
        print("pip install -r requirements_serve.txt")
        
        # Continue with available tests
    
    # Test URL normalization
    test_url_normalization()
    
    # Test YouTube stream grabber
    live_streams = test_youtube_stream_grabber()
    
    # Test live stream processing
    asyncio.run(test_live_stream_processing())
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 Test Summary")
    print("=" * 60)
    
    if not missing_deps:
        print("✅ All dependencies available")
    else:
        print(f"⚠️  {len(missing_deps)} missing dependencies")
    
    print(f"📺 {len(live_streams)} live streams found")
    
    if live_streams:
        print("\n🎬 Available live streams for testing:")
        for i, stream in enumerate(live_streams[:3], 1):  # Show max 3
            print(f"   {i}. {stream['title']}")
            print(f"      Channel: {stream['channel']}")
    
    print("\n🚀 Ready to start the service!")
    print("Run: python run_serve.py")
    
    return len(missing_deps) == 0 and len(live_streams) > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 