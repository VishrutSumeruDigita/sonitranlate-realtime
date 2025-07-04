#!/usr/bin/env python3
"""
Test script to verify the fixes for URL handling and live stream detection.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from youtube.youtube_stream_grepper import YouTubeLiveStreamGrabber

def test_url_cleaning():
    """Test URL cleaning functionality."""
    print("🧪 Testing URL cleaning...")
    
    test_urls = [
        "http://youtube.com/watch\\?v\\=7qG_7mgzx-o",
        "https://www.youtube.com/@ZeeNews",
        "https://www.youtube.com/watch?v=abc123",
        "https://youtu.be/abc123"
    ]
    
    for url in test_urls:
        cleaned = url.replace('\\', '')
        print(f"   Original: {url}")
        print(f"   Cleaned:  {cleaned}")
        print()

def test_live_stream_detection():
    """Test live stream detection."""
    print("🧪 Testing live stream detection...")
    
    grabber = YouTubeLiveStreamGrabber()
    
    # Test with a known live channel
    test_url = "https://www.youtube.com/@ZeeNews"
    
    try:
        print(f"🔍 Checking if {test_url} is live...")
        is_live = grabber.is_channel_live(test_url)
        print(f"   Is live: {is_live}")
        
        if is_live:
            print("🔍 Getting live stream info...")
            stream_info = grabber.get_live_stream_url(test_url)
            if stream_info:
                print(f"   Title: {stream_info.get('title', 'Unknown')}")
                print(f"   URL: {stream_info.get('url', 'Unknown')}")
                print(f"   Has formats: {'formats' in stream_info}")
                if 'formats' in stream_info:
                    print(f"   Format count: {len(stream_info['formats'])}")
            else:
                print("   No stream info found")
        else:
            print("   Channel is not live")
            
    except Exception as e:
        print(f"   Error: {e}")

def test_direct_video_url():
    """Test direct video URL handling."""
    print("🧪 Testing direct video URL...")
    
    # This is a test video URL (not live)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    grabber = YouTubeLiveStreamGrabber()
    
    try:
        print(f"🔍 Checking if {test_url} is live...")
        is_live = grabber.is_channel_live(test_url)
        print(f"   Is live: {is_live}")
        
        if not is_live:
            print("   Expected: Video is not live")
        else:
            print("   Unexpected: Video appears to be live")
            
    except Exception as e:
        print(f"   Error: {e}")

def main():
    """Run all tests."""
    print("🧪 Running SoniTranslate Fix Tests")
    print("=" * 50)
    
    test_url_cleaning()
    test_live_stream_detection()
    test_direct_video_url()
    
    print("✅ Tests completed!")

if __name__ == "__main__":
    main() 