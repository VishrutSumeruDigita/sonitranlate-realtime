#!/usr/bin/env python3
"""
CLI Tool for SoniTranslate Live Stream Translation

This tool provides command-line interface for translating YouTube live streams
with support for custom URLs and predefined channels.
"""

import argparse
import asyncio
import json
import sys
import time
from typing import Optional

from example_client import LiveTranslationClient
from channel_manager import ChannelManager
from youtube.youtube_stream_grepper import YouTubeLiveStreamGrabber


class CLITranslator:
    """Command-line interface for live stream translation."""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.client = LiveTranslationClient(api_url)
        self.channel_manager = ChannelManager()
        self.grabber = YouTubeLiveStreamGrabber()
    
    def list_channels(self, category: Optional[str] = None, language: Optional[str] = None):
        """List available channels."""
        if category:
            channels = self.channel_manager.get_channels_by_category(category)
            print(f"\n📺 Channels in category '{category}':")
        elif language:
            channels = self.channel_manager.get_channels_for_language(language)
            print(f"\n🎯 Channels supporting '{language}':")
        else:
            all_channels = self.channel_manager.get_all_channels()
            print("\n📺 All Available Channels:")
            
            for cat, channel_list in all_channels.items():
                print(f"\n📂 {cat.upper()}")
                print("=" * (len(cat) + 4))
                for channel in channel_list:
                    print(f"  📺 {channel.name}")
                    print(f"     URL: {channel.url}")
                    print(f"     Languages: {', '.join(channel.languages)}")
                    print()
            return
        
        if not channels:
            print("  No channels found.")
            return
        
        for i, channel in enumerate(channels, 1):
            print(f"  {i}. {channel.name}")
            print(f"     URL: {channel.url}")
            print(f"     Description: {channel.description}")
            print(f"     Languages: {', '.join(channel.languages)}")
            print()
    
    def check_live_streams(self, urls: list):
        """Check which URLs have live streams."""
        print("\n🔍 Checking for live streams...")
        live_streams = []
        
        for url in urls:
            print(f"  Checking: {url}")
            try:
                is_live = self.grabber.is_channel_live(url)
                if is_live:
                    stream_info = self.grabber.get_live_stream_url(url)
                    if stream_info:
                        print(f"    ✅ LIVE: {stream_info['title']}")
                        live_streams.append({
                            'url': url,
                            'title': stream_info['title'],
                            'viewers': stream_info.get('view_count', 'N/A')
                        })
                    else:
                        print(f"    ⚠️  Live detection failed")
                else:
                    print(f"    📵 Not live")
            except Exception as e:
                print(f"    ❌ Error: {e}")
        
        return live_streams
    
    def translate_stream(self, url: str, language: str, 
                        chunk_duration: int = 30,
                        transcriber_model: str = "base",
                        output_file: Optional[str] = None,
                        monitor_only: bool = False):
        """Start translation of a live stream."""
        
        print(f"\n🚀 Starting {language} translation for: {url}")
        
        # Check if stream is live
        if not self.grabber.is_channel_live(url):
            print("❌ Error: No live stream found at the provided URL")
            return None
        
        # Start translation
        result = self.client.start_translation(
            youtube_url=url,
            language=language,
            chunk_duration=chunk_duration,
            transcriber_model=transcriber_model
        )
        
        if not result:
            print("❌ Failed to start translation")
            return None
        
        stream_id = result['stream_id']
        print(f"✅ Translation started! Stream ID: {stream_id}")
        
        if monitor_only:
            return self.monitor_translation(stream_id)
        
        # Monitor and optionally stream audio
        if output_file:
            print(f"📁 Streaming audio to: {output_file}")
            try:
                self.client.stream_audio(stream_id, output_file)
            except KeyboardInterrupt:
                print("\n⏹️  Audio streaming stopped by user")
        
        return stream_id
    
    def monitor_translation(self, stream_id: str, duration: int = 60):
        """Monitor translation progress."""
        print(f"\n📊 Monitoring translation (Stream ID: {stream_id})")
        print("Press Ctrl+C to stop monitoring")
        
        start_time = time.time()
        
        try:
            while time.time() - start_time < duration:
                status = self.client.get_status(stream_id)
                
                print(f"\rStatus: {status['status']} | "
                      f"Chunks: {status['chunks_processed']} | "
                      f"Duration: {status['total_duration']:.1f}s", end="")
                
                if status['status'] == 'error':
                    print(f"\n❌ Translation error: {status['error_message']}")
                    break
                elif status['status'] == 'active':
                    print(" ✅")
                    break
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n⏹️  Monitoring stopped by user")
        
        return stream_id
    
    def add_channel(self, category: str, name: str, url: str, 
                   description: str = "", languages: list = None):
        """Add a new channel to configuration."""
        if languages is None:
            languages = ["english"]
        
        self.channel_manager.add_channel(category, name, url, description, languages)
        print(f"✅ Channel '{name}' added to category '{category}'")
    
    def remove_channel(self, name: str):
        """Remove a channel from configuration."""
        success = self.channel_manager.remove_channel(name)
        if success:
            print(f"✅ Channel '{name}' removed successfully")
        else:
            print(f"❌ Channel '{name}' not found")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="SoniTranslate Live Stream CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all channels
  python cli_translate.py --list-channels
  
  # Translate NASA live stream to Tamil
  python cli_translate.py --url "https://www.youtube.com/@nasa/live" --language tamil
  
  # Use predefined channel
  python cli_translate.py --channel "BBC News" --language english
  
  # Check live streams
  python cli_translate.py --check-live "https://www.youtube.com/@nasa/live"
  
  # Add custom channel
  python cli_translate.py --add-channel "My Channel" --url "https://youtube.com/@mychannel" --category entertainment
        """
    )
    
    # Main action arguments
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument('--url', help='YouTube live stream URL')
    action_group.add_argument('--channel', help='Use predefined channel by name')
    action_group.add_argument('--list-channels', action='store_true', help='List all available channels')
    action_group.add_argument('--check-live', nargs='+', help='Check if URLs have live streams')
    action_group.add_argument('--add-channel', help='Add new channel (requires --url and --category)')
    action_group.add_argument('--remove-channel', help='Remove channel by name')
    
    # Translation options
    parser.add_argument('--language', '-l', 
                       choices=['english', 'tamil', 'malayalam', 'gujarati', 'kannada', 
                               'marathi', 'japanese', 'korean', 'hindi', 'spanish', 
                               'french', 'german', 'chinese', 'arabic', 'portuguese', 
                               'russian', 'italian'],
                       help='Target language for translation')
    
    parser.add_argument('--chunk-duration', '-d', type=int, default=30,
                       help='Audio chunk duration in seconds (default: 30)')
    
    parser.add_argument('--transcriber-model', '-m', 
                       choices=['base', 'small', 'medium', 'large'], default='base',
                       help='Whisper model for transcription (default: base)')
    
    parser.add_argument('--output-file', '-o', help='Save translated audio to file')
    
    parser.add_argument('--monitor-only', action='store_true',
                       help='Only monitor translation, don\'t stream audio')
    
    parser.add_argument('--monitor-duration', type=int, default=60,
                       help='Duration to monitor translation in seconds (default: 60)')
    
    # Channel management options
    parser.add_argument('--category', help='Channel category (for adding channels)')
    parser.add_argument('--description', help='Channel description (for adding channels)')
    parser.add_argument('--languages', nargs='+', 
                       choices=['english', 'tamil', 'malayalam', 'gujarati', 'kannada', 
                               'marathi', 'japanese', 'korean', 'hindi', 'spanish', 
                               'french', 'german', 'chinese', 'arabic', 'portuguese', 
                               'russian', 'italian'],
                       help='Supported languages for channel (for adding channels)')
    
    # Filter options
    parser.add_argument('--category-filter', help='Filter channels by category')
    parser.add_argument('--language-filter', help='Filter channels by supported language')
    
    # API options
    parser.add_argument('--api-url', default='http://localhost:8000',
                       help='API server URL (default: http://localhost:8000)')
    
    args = parser.parse_args()
    
    # Initialize CLI translator
    cli = CLITranslator(args.api_url)
    
    try:
        # Handle different actions
        if args.list_channels:
            cli.list_channels(args.category_filter, args.language_filter)
            
        elif args.check_live:
            cli.check_live_streams(args.check_live)
            
        elif args.add_channel:
            if not args.url or not args.category:
                print("❌ Error: --add-channel requires --url and --category")
                sys.exit(1)
            
            cli.add_channel(
                category=args.category,
                name=args.add_channel,
                url=args.url,
                description=args.description or "",
                languages=args.languages or ["english"]
            )
            
        elif args.remove_channel:
            cli.remove_channel(args.remove_channel)
            
        elif args.channel:
            # Use predefined channel
            if not args.language:
                print("❌ Error: --language is required for translation")
                sys.exit(1)
            
            channel = cli.channel_manager.get_channel_by_name(args.channel)
            if not channel:
                print(f"❌ Error: Channel '{args.channel}' not found")
                print("Use --list-channels to see available channels")
                sys.exit(1)
            
            cli.translate_stream(
                url=channel.url,
                language=args.language,
                chunk_duration=args.chunk_duration,
                transcriber_model=args.transcriber_model,
                output_file=args.output_file,
                monitor_only=args.monitor_only
            )
            
        elif args.url:
            # Use custom URL
            if not args.language:
                print("❌ Error: --language is required for translation")
                sys.exit(1)
            
            cli.translate_stream(
                url=args.url,
                language=args.language,
                chunk_duration=args.chunk_duration,
                transcriber_model=args.transcriber_model,
                output_file=args.output_file,
                monitor_only=args.monitor_only
            )
    
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 