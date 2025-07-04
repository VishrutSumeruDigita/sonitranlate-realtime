#!/usr/bin/env python3
"""
YouTube Live Stream Grabber

This module provides functionality to extract live stream URLs from YouTube channels.
It can handle various YouTube URL formats and detect active live streams.
"""

import yt_dlp
import re
import requests
import time
from typing import Optional, Dict, List, Union
from urllib.parse import urlparse, parse_qs
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YouTubeLiveStreamGrabber:
    """
    A class to grab live streams from YouTube channels.
    """
    
    def __init__(self, quality: str = 'best', audio_only: bool = False):
        """
        Initialize the YouTube Live Stream Grabber.
        
        Args:
            quality: Video quality preference ('best', 'worst', or specific format)
            audio_only: Whether to extract only audio stream
        """
        self.quality = quality
        self.audio_only = audio_only
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'bestaudio/best' if audio_only else 'best',
            'extractaudio': audio_only,
            'audioformat': 'mp3' if audio_only else None,
        }
    
    def _normalize_channel_url(self, url: str) -> str:
        """
        Normalize various YouTube channel URL formats.
        
        Args:
            url: Raw YouTube channel URL
            
        Returns:
            Normalized channel URL
        """
        # Remove any trailing slashes and normalize
        url = url.rstrip('/')
        
        # Handle different URL formats
        if 'youtube.com/c/' in url:
            return url
        elif 'youtube.com/channel/' in url:
            return url
        elif 'youtube.com/user/' in url:
            return url
        elif 'youtube.com/@' in url:
            return url
        elif 'youtube.com/' in url and '/live' in url:
            # Remove /live suffix to get channel URL
            return url.replace('/live', '')
        elif 'youtu.be/' in url:
            # Handle youtu.be short URLs
            video_id = url.split('/')[-1]
            return f"https://www.youtube.com/watch?v={video_id}"
        else:
            # If it's just a channel name, assume it's a handle
            if not url.startswith('http'):
                return f"https://www.youtube.com/@{url}"
            return url
    
    def _extract_channel_id(self, url: str) -> Optional[str]:
        """
        Extract channel ID from various YouTube URL formats.
        
        Args:
            url: YouTube channel URL
            
        Returns:
            Channel ID if found, None otherwise
        """
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get('channel_id')
        except Exception as e:
            logger.error(f"Error extracting channel ID: {e}")
            return None
    
    def get_live_stream_url(self, channel_url: str) -> Optional[Dict]:
        """
        Get the live stream URL from a YouTube channel.
        
        Args:
            channel_url: YouTube channel URL
            
        Returns:
            Dictionary containing live stream information or None if no live stream
        """
        try:
            # Normalize the channel URL
            normalized_url = self._normalize_channel_url(channel_url)
            
            # Try to get live stream directly
            live_url = f"{normalized_url}/live"
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(live_url, download=False)
                    
                    # Check if it's actually a live stream
                    if info.get('is_live') or info.get('live_status') == 'is_live':
                        return {
                            'url': info.get('url'),
                            'title': info.get('title'),
                            'channel': info.get('channel'),
                            'channel_url': info.get('channel_url'),
                            'thumbnail': info.get('thumbnail'),
                            'duration': info.get('duration'),
                            'view_count': info.get('view_count'),
                            'is_live': True,
                            'formats': info.get('formats', [])
                        }
                    else:
                        logger.info(f"No live stream found at {live_url}")
                        return None
                        
                except Exception as e:
                    logger.error(f"Error accessing live stream: {e}")
                    # Try alternative method
                    return self._find_live_stream_alternative(normalized_url)
                    
        except Exception as e:
            logger.error(f"Error getting live stream: {e}")
            return None
    
    def _find_live_stream_alternative(self, channel_url: str) -> Optional[Dict]:
        """
        Alternative method to find live streams by searching recent videos.
        
        Args:
            channel_url: YouTube channel URL
            
        Returns:
            Dictionary containing live stream information or None
        """
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # Get channel info and recent videos
                info = ydl.extract_info(channel_url, download=False)
                
                # Check if we have entries (recent videos)
                if 'entries' in info:
                    for entry in info['entries'][:10]:  # Check first 10 videos
                        if entry.get('is_live') or entry.get('live_status') == 'is_live':
                            # Get full info for this live video
                            full_info = ydl.extract_info(entry['url'], download=False)
                            return {
                                'url': full_info.get('url'),
                                'title': full_info.get('title'),
                                'channel': full_info.get('channel'),
                                'channel_url': full_info.get('channel_url'),
                                'thumbnail': full_info.get('thumbnail'),
                                'duration': full_info.get('duration'),
                                'view_count': full_info.get('view_count'),
                                'is_live': True,
                                'formats': full_info.get('formats', [])
                            }
                
                logger.info("No live stream found in recent videos")
                return None
                
        except Exception as e:
            logger.error(f"Error in alternative live stream search: {e}")
            return None
    
    def get_stream_formats(self, stream_url: str) -> List[Dict]:
        """
        Get available formats for a stream URL.
        
        Args:
            stream_url: YouTube stream URL
            
        Returns:
            List of available formats
        """
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(stream_url, download=False)
                return info.get('formats', [])
        except Exception as e:
            logger.error(f"Error getting stream formats: {e}")
            return []
    
    def get_best_audio_format(self, stream_url: str) -> Optional[Dict]:
        """
        Get the best audio format for a stream.
        
        Args:
            stream_url: YouTube stream URL
            
        Returns:
            Best audio format information or None
        """
        try:
            formats = self.get_stream_formats(stream_url)
            
            # Filter audio-only formats
            audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
            
            if not audio_formats:
                # If no audio-only formats, get best format with audio
                audio_formats = [f for f in formats if f.get('acodec') != 'none']
            
            if audio_formats:
                # Sort by quality (bitrate or audio quality) - handle None values
                audio_formats.sort(key=lambda x: (x.get('abr') or 0) + (x.get('tbr') or 0), reverse=True)
                return audio_formats[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting best audio format: {e}")
            return None
    
    def is_channel_live(self, channel_url: str) -> bool:
        """
        Check if a channel is currently live.
        
        Args:
            channel_url: YouTube channel URL
            
        Returns:
            True if channel is live, False otherwise
        """
        stream_info = self.get_live_stream_url(channel_url)
        return stream_info is not None and stream_info.get('is_live', False)
    
    def wait_for_live_stream(self, channel_url: str, check_interval: int = 60, max_wait: int = 3600) -> Optional[Dict]:
        """
        Wait for a channel to go live.
        
        Args:
            channel_url: YouTube channel URL
            check_interval: Time between checks in seconds
            max_wait: Maximum time to wait in seconds
            
        Returns:
            Live stream information when available or None if timeout
        """
        start_time = time.time()
        logger.info(f"Waiting for live stream from {channel_url}")
        
        while time.time() - start_time < max_wait:
            stream_info = self.get_live_stream_url(channel_url)
            if stream_info:
                logger.info(f"Live stream found: {stream_info['title']}")
                return stream_info
            
            logger.info(f"No live stream yet, waiting {check_interval} seconds...")
            time.sleep(check_interval)
        
        logger.info(f"Timeout waiting for live stream from {channel_url}")
        return None


def get_live_stream_from_channel(channel_url: str, quality: str = 'best', audio_only: bool = False) -> Optional[Dict]:
    """
    Convenience function to get live stream from a YouTube channel.
    
    Args:
        channel_url: YouTube channel URL
        quality: Video quality preference
        audio_only: Whether to get only audio stream
        
    Returns:
        Live stream information or None
    """
    grabber = YouTubeLiveStreamGrabber(quality=quality, audio_only=audio_only)
    return grabber.get_live_stream_url(channel_url)


def main():
    """
    Example usage of the YouTube Live Stream Grabber.
    """
    # Example channel URLs for testing
    test_channels = [
        "https://www.youtube.com/@nasa"
    ]
    
    grabber = YouTubeLiveStreamGrabber(audio_only=True)
    
    for channel_url in test_channels:
        print(f"\nChecking {channel_url}...")
        stream_info = grabber.get_live_stream_url(channel_url)
        
        if stream_info:
            print(f"✅ LIVE: {stream_info['title']}")
            print(f"   Channel: {stream_info['channel']}")
            print(f"   Stream URL: {stream_info['url']}")
            print(f"   Viewers: {stream_info.get('view_count', 'N/A')}")
        else:
            print("❌ No live stream found")


if __name__ == "__main__":
    main()




