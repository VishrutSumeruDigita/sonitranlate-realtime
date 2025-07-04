#!/usr/bin/env python3
"""
CLI for SoniTranslate Live Stream Translation

This script provides command-line interface for translating YouTube live streams
with support for custom URLs and various options.
"""

import argparse
import sys
import time
import json
import requests
from typing import Optional
from channel_manager import ChannelManager
from youtube.youtube_stream_grepper import YouTubeLiveStreamGrabber

class CLITranslator:
    """Command-line interface for live stream translation."""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()
        self.channel_manager = ChannelManager()
        self.grabber = YouTubeLiveStreamGrabber()
    
    def check_server(self) -> bool:
        """Check if the API server is running."""
        try:
            response = self.session.get(f"{self.api_url}/", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def list_languages(self):
        """List supported languages."""
        try:
            response = self.session.get(f"{self.api_url}/languages")
            if response.status_code == 200:
                data = response.json()
                print("🌍 Supported Languages:")
                print("=" * 30)
                for lang, full_name in data['supported_languages'].items():
                    print(f"  {lang:12} - {full_name}")
                print(f"\nTotal: {data['total_count']} languages")
            else:
                print("❌ Failed to get languages")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def list_channels(self, category: Optional[str] = None):
        """List configured channels."""
        try:
            if category:
                response = self.session.get(f"{self.api_url}/channels/{category}")
            else:
                response = self.session.get(f"{self.api_url}/channels")
            
            if response.status_code == 200:
                data = response.json()
                if category:
                    print(f"📺 Channels in '{category}' category:")
                    print("=" * 40)
                    for channel in data['channels']:
                        print(f"  📺 {channel['name']}")
                        print(f"     URL: {channel['url']}")
                        print(f"     Description: {channel['description']}")
                        print(f"     Languages: {', '.join(channel['languages'])}")
                        print()
                else:
                    print("📺 Available Channel Categories:")
                    print("=" * 35)
                    for cat, channels in data['channels'].items():
                        print(f"  📂 {cat.upper()} ({len(channels)} channels)")
                        for channel in channels:
                            print(f"    - {channel['name']}")
                        print()
                    print(f"Total: {data['total_channels']} channels in {data['total_categories']} categories")
            else:
                print("❌ Failed to get channels")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def find_live_streams(self, limit: int = 5):
        """Find currently live streams from configured channels."""
        print("🔍 Searching for live streams...")
        print("=" * 35)
        
        live_streams = []
        all_channels = self.channel_manager.get_all_channels()
        
        for category, channels in all_channels.items():
            print(f"\n📂 Checking {category} channels...")
            for channel in channels:
                try:
                    print(f"  🔍 {channel.name}...", end=" ")
                    is_live = self.grabber.is_channel_live(channel.url)
                    
                    if is_live:
                        stream_info = self.grabber.get_live_stream_url(channel.url)
                        if stream_info:
                            print("✅ LIVE")
                            live_streams.append({
                                'name': channel.name,
                                'url': channel.url,
                                'stream_url': stream_info['url'],
                                'title': stream_info['title'],
                                'viewers': stream_info.get('view_count', 'N/A'),
                                'languages': channel.languages
                            })
                        else:
                            print("❌ Error getting stream info")
                    else:
                        print("📵 Not live")
                        
                except Exception as e:
                    print(f"❌ Error: {e}")
        
        if live_streams:
            print(f"\n🎬 Found {len(live_streams)} live streams:")
            print("=" * 40)
            for i, stream in enumerate(live_streams[:limit], 1):
                print(f"{i}. {stream['name']}")
                print(f"   Title: {stream['title']}")
                print(f"   Viewers: {stream['viewers']}")
                print(f"   Languages: {', '.join(stream['languages'])}")
                print(f"   URL: {stream['url']}")
                print()
        else:
            print("\n📵 No live streams found")
        
        return live_streams
    
    def start_translation(self, youtube_url: str, language: str, 
                         chunk_duration: int = 30, 
                         transcriber_model: str = "base",
                         origin_language: str = "Automatic detection",
                         output_file: Optional[str] = None):
        """Start a translation stream."""
        
        print(f"🚀 Starting {language} translation...")
        print(f"   URL: {youtube_url}")
        print(f"   Chunk duration: {chunk_duration}s")
        print(f"   Model: {transcriber_model}")
        
        try:
            # Start translation
            payload = {
                "youtube_url": youtube_url,
                "chunk_duration": chunk_duration,
                "transcriber_model": transcriber_model,
                "origin_language": origin_language
            }
            
            response = self.session.post(f"{self.api_url}/start/{language}", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                stream_id = result['stream_id']
                print(f"✅ Translation started! Stream ID: {stream_id}")
                
                # Monitor status
                self.monitor_translation(stream_id, output_file)
                
            else:
                print(f"❌ Failed to start translation: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def monitor_translation(self, stream_id: str, output_file: Optional[str] = None):
        """Monitor translation progress."""
        print(f"\n📊 Monitoring translation {stream_id}...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                # Get status
                response = self.session.get(f"{self.api_url}/status/{stream_id}")
                if response.status_code == 200:
                    status = response.json()
                    
                    print(f"\rStatus: {status['status']} | "
                          f"Chunks: {status['chunks_processed']} | "
                          f"Duration: {status['total_duration']:.1f}s", end="")
                    
                    if status['status'] == 'error':
                        print(f"\n❌ Error: {status['error_message']}")
                        break
                    elif status['status'] == 'active':
                        # Stream audio if output file specified
                        if output_file:
                            self.stream_audio_to_file(stream_id, output_file)
                            break
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping translation...")
            self.stop_translation(stream_id)
    
    def stream_audio_to_file(self, stream_id: str, output_file: str):
        """Stream translated audio to file."""
        print(f"\n🎵 Streaming audio to {output_file}...")
        
        try:
            response = self.session.get(f"{self.api_url}/stream/{stream_id}", stream=True)
            
            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        print(f"\rReceived: {len(chunk)} bytes", end="")
            
            print(f"\n✅ Audio saved to {output_file}")
            
        except Exception as e:
            print(f"\n❌ Error streaming audio: {e}")
    
    def stop_translation(self, stream_id: str):
        """Stop a translation stream."""
        try:
            response = self.session.post(f"{self.api_url}/stop/{stream_id}")
            if response.status_code == 200:
                print("✅ Translation stopped")
            else:
                print("❌ Failed to stop translation")
        except Exception as e:
            print(f"❌ Error stopping translation: {e}")
    
    def list_active_streams(self):
        """List all active translation streams."""
        try:
            response = self.session.get(f"{self.api_url}/streams")
            if response.status_code == 200:
                data = response.json()
                if data['active_streams']:
                    print("🔄 Active Translation Streams:")
                    print("=" * 35)
                    for stream in data['active_streams']:
                        print(f"  📺 {stream['stream_id']}")
                        print(f"     Language: {stream['language']}")
                        print(f"     Status: {stream['status']}")
                        print(f"     Chunks: {stream['chunks_processed']}")
                        print(f"     Duration: {stream['total_duration']:.1f}s")
                        print()
                else:
                    print("📵 No active translation streams")
            else:
                print("❌ Failed to get active streams")
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="SoniTranslate Live Stream Translation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List supported languages
  python cli_translate.py languages

  # List configured channels
  python cli_translate.py channels

  # Find live streams
  python cli_translate.py find-live

  # Quick live video translation (positional argument)
  python cli_translate.py live "https://www.youtube.com/@nasa/live" --language tamil

  # Quick live video with fast settings
  python cli_translate.py live "https://www.youtube.com/@BBCNews/live" --language malayalam --fast

  # Start Tamil translation (positional URL)
  python cli_translate.py translate "https://www.youtube.com/@nasa/live" --language tamil

  # Start translation with custom settings
  python cli_translate.py translate "https://www.youtube.com/@BBCNews/live" \\
    --language malayalam --chunk-duration 20 --model small --output audio.mp3

  # Auto-find live stream from channel URL
  python cli_translate.py translate "https://www.youtube.com/@nasa" --language tamil --auto-find

  # Check if URL is live before starting
  python cli_translate.py translate "https://www.youtube.com/@nasa/live" --language tamil --live-check

  # Monitor active streams
  python cli_translate.py streams
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Languages command
    subparsers.add_parser('languages', help='List supported languages')
    
    # Channels command
    channels_parser = subparsers.add_parser('channels', help='List configured channels')
    channels_parser.add_argument('--category', help='Show channels in specific category')
    
    # Find live streams command
    subparsers.add_parser('find-live', help='Find currently live streams')
    
    # Quick live video command
    live_parser = subparsers.add_parser('live', help='Quick translation of live video')
    live_parser.add_argument('youtube_url', help='YouTube live stream URL')
    live_parser.add_argument('--language', required=True, help='Target language')
    live_parser.add_argument('--output', help='Output audio file')
    live_parser.add_argument('--fast', action='store_true', help='Use fast settings (small model, 20s chunks)')
    
    # Translate command
    translate_parser = subparsers.add_parser('translate', help='Start translation')
    translate_parser.add_argument('--url', help='YouTube URL (or use positional argument)')
    translate_parser.add_argument('youtube_url', nargs='?', help='YouTube live stream URL (positional argument)')
    translate_parser.add_argument('--language', required=True, help='Target language')
    translate_parser.add_argument('--chunk-duration', type=int, default=30, help='Chunk duration in seconds')
    translate_parser.add_argument('--model', default='base', help='Transcriber model (base/small/medium/large)')
    translate_parser.add_argument('--origin-language', default='Automatic detection', help='Source language')
    translate_parser.add_argument('--output', help='Output audio file')
    translate_parser.add_argument('--live-check', action='store_true', help='Check if URL is live before starting')
    translate_parser.add_argument('--auto-find', action='store_true', help='Auto-find live stream from channel URL')
    
    # Streams command
    subparsers.add_parser('streams', help='List active translation streams')
    
    # Server check
    parser.add_argument('--api-url', default='http://localhost:8000', help='API server URL')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize CLI translator
    cli = CLITranslator(args.api_url)
    
    # Check if server is running
    if not cli.check_server():
        print("❌ API server is not running!")
        print("Please start the server first:")
        print("  python run_serve.py")
        return
    
    # Execute commands
    if args.command == 'languages':
        cli.list_languages()
    
    elif args.command == 'channels':
        cli.list_channels(args.category)
    
    elif args.command == 'find-live':
        cli.find_live_streams()
    
    elif args.command == 'live':
        # Quick live video translation with optimized settings
        chunk_duration = 20 if args.fast else 30
        model = 'small' if args.fast else 'base'
        
        print(f"🚀 Quick live video translation starting...")
        print(f"   URL: {args.youtube_url}")
        print(f"   Language: {args.language}")
        print(f"   Fast mode: {'Yes' if args.fast else 'No'}")
        
        cli.start_translation(
            youtube_url=args.youtube_url,
            language=args.language,
            chunk_duration=chunk_duration,
            transcriber_model=model,
            origin_language="Automatic detection",
            output_file=args.output
        )
    
    elif args.command == 'translate':
        # Handle URL argument (positional or --url)
        youtube_url = args.youtube_url or args.url
        if not youtube_url:
            print("❌ Error: YouTube URL is required!")
            print("Usage: python cli_translate.py translate <youtube_url> --language <language>")
            print("   or: python cli_translate.py translate --url <youtube_url> --language <language>")
            return
        
        # Clean URL (remove escaped characters)
        youtube_url = youtube_url.replace('\\', '')
        
        # Auto-find live stream if requested
        if args.auto_find:
            print(f"🔍 Auto-finding live stream from: {youtube_url}")
            try:
                # First check if it's already a live stream
                if cli.grabber.is_channel_live(youtube_url):
                    print(f"✅ URL is already a live stream: {youtube_url}")
                else:
                    # Try to find live stream from channel
                    stream_info = cli.grabber.get_live_stream_url(youtube_url)
                    if stream_info and stream_info.get('url'):
                        youtube_url = stream_info['url']
                        print(f"✅ Found live stream: {stream_info.get('title', 'Unknown')}")
                    else:
                        print("❌ No live stream found at the provided URL")
                        print("💡 The URL might be a direct video URL or the channel is not live")
                        return
            except Exception as e:
                print(f"❌ Error finding live stream: {e}")
                return
        
        # Check if live before starting
        if args.live_check:
            print(f"🔍 Checking if {youtube_url} is live...")
            try:
                if not cli.grabber.is_channel_live(youtube_url):
                    print("❌ Error: No live stream found at the provided URL")
                    print("💡 Try using --auto-find to automatically find the live stream")
                    return
                print("✅ Live stream confirmed!")
            except Exception as e:
                print(f"❌ Error checking live status: {e}")
                return
        
        cli.start_translation(
            youtube_url=youtube_url,
            language=args.language,
            chunk_duration=args.chunk_duration,
            transcriber_model=args.model,
            origin_language=args.origin_language,
            output_file=args.output
        )
    
    elif args.command == 'streams':
        cli.list_active_streams()


if __name__ == "__main__":
    main() 