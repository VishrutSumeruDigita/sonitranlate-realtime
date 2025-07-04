#!/usr/bin/env python3
"""
Simple Live Stream Detector

A simplified version that can detect live streams without complex dependencies.
"""

import re
import requests
from typing import Optional, Dict
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleLiveDetector:
    """Simple live stream detector that works without yt-dlp."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def is_live_stream(self, url: str) -> bool:
        """
        Check if a URL points to a live stream.
        
        Args:
            url: YouTube URL to check
            
        Returns:
            True if it's a live stream, False otherwise
        """
        try:
            # Clean the URL
            url = url.replace('\\', '')
            
            # Check for live indicators in URL
            live_indicators = ['/live', 'live=1', 'is_live']
            if any(indicator in url.lower() for indicator in live_indicators):
                return True
            
            # For channel URLs, try to detect if they're currently live
            if '/@' in url or '/channel/' in url:
                return self._check_channel_live(url)
            
            # For video URLs, check if they're live
            if '/watch?v=' in url:
                return self._check_video_live(url)
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking if live: {e}")
            return False
    
    def _check_channel_live(self, channel_url: str) -> bool:
        """Check if a channel is currently live."""
        try:
            # Try to access the live page
            live_url = f"{channel_url}/live" if not channel_url.endswith('/live') else channel_url
            
            response = self.session.get(live_url, timeout=10)
            
            # Check for live indicators in the page content
            content = response.text.lower()
            live_indicators = [
                'is live now',
                'live now',
                'currently live',
                'live stream',
                'watching live',
                'live chat'
            ]
            
            return any(indicator in content for indicator in live_indicators)
            
        except Exception as e:
            logger.error(f"Error checking channel live status: {e}")
            return False
    
    def _check_video_live(self, video_url: str) -> bool:
        """Check if a video URL is a live stream."""
        try:
            response = self.session.get(video_url, timeout=10)
            content = response.text.lower()
            
            # Check for live indicators
            live_indicators = [
                'is live now',
                'live now',
                'currently live',
                'live stream',
                'watching live',
                'live chat',
                'live_status'
            ]
            
            return any(indicator in content for indicator in live_indicators)
            
        except Exception as e:
            logger.error(f"Error checking video live status: {e}")
            return False
    
    def get_live_stream_info(self, url: str) -> Optional[Dict]:
        """
        Get basic live stream information.
        
        Args:
            url: YouTube URL
            
        Returns:
            Basic stream info or None
        """
        if not self.is_live_stream(url):
            return None
        
        try:
            # Extract basic info from URL
            if '/watch?v=' in url:
                video_id = re.search(r'/watch\?v=([^&]+)', url)
                if video_id:
                    return {
                        'url': url,
                        'title': f'Live Stream {video_id.group(1)}',
                        'is_live': True,
                        'video_id': video_id.group(1)
                    }
            
            # For channel URLs
            if '/@' in url:
                channel_name = re.search(r'/@([^/]+)', url)
                if channel_name:
                    return {
                        'url': url,
                        'title': f'Live Stream from {channel_name.group(1)}',
                        'is_live': True,
                        'channel': channel_name.group(1)
                    }
            
            return {
                'url': url,
                'title': 'Live Stream',
                'is_live': True
            }
            
        except Exception as e:
            logger.error(f"Error getting stream info: {e}")
            return None

def test_live_detection():
    """Test the live detection functionality."""
    detector = SimpleLiveDetector()
    
    test_urls = [
        "https://www.youtube.com/@ZeeNews",
        "https://www.youtube.com/@nasa",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Not live
        "https://www.youtube.com/@BBCNews/live",
    ]
    
    print("🧪 Testing Live Stream Detection")
    print("=" * 40)
    
    for url in test_urls:
        print(f"\n🔍 Testing: {url}")
        is_live = detector.is_live_stream(url)
        print(f"   Is live: {is_live}")
        
        if is_live:
            info = detector.get_live_stream_info(url)
            print(f"   Info: {info}")

if __name__ == "__main__":
    test_live_detection() 