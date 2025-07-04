#!/usr/bin/env python3
"""
Example client for the SoniTranslate Live Stream API

This script demonstrates how to use the real-time translation service
to translate YouTube live streams into different languages.
"""

import requests
import time
import json
from typing import Optional

class LiveTranslationClient:
    """Client for interacting with the live translation service."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def get_supported_languages(self):
        """Get list of supported target languages."""
        response = self.session.get(f"{self.base_url}/languages")
        return response.json()
    
    def start_translation(self, youtube_url: str, language: str, 
                         chunk_duration: int = 30, 
                         transcriber_model: str = "base",
                         origin_language: str = "Automatic detection") -> Optional[dict]:
        """Start a translation stream for a specific language."""
        
        payload = {
            "youtube_url": youtube_url,
            "chunk_duration": chunk_duration,
            "transcriber_model": transcriber_model,
            "origin_language": origin_language
        }
        
        response = self.session.post(f"{self.base_url}/start/{language}", json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error starting translation: {response.text}")
            return None
    
    def get_status(self, stream_id: str):
        """Get the status of a translation stream."""
        response = self.session.get(f"{self.base_url}/status/{stream_id}")
        return response.json()
    
    def stop_translation(self, stream_id: str):
        """Stop a translation stream."""
        response = self.session.post(f"{self.base_url}/stop/{stream_id}")
        return response.json()
    
    def list_active_streams(self):
        """List all active translation streams."""
        response = self.session.get(f"{self.base_url}/streams")
        return response.json()
    
    def stream_audio(self, stream_id: str, output_file: str = None):
        """Stream translated audio and optionally save to file."""
        
        url = f"{self.base_url}/stream/{stream_id}"
        
        with self.session.get(url, stream=True) as response:
            if response.status_code != 200:
                print(f"Error streaming audio: {response.text}")
                return
            
            file_handle = None
            if output_file:
                file_handle = open(output_file, 'wb')
            
            try:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        if file_handle:
                            file_handle.write(chunk)
                        
                        # Process audio chunk here if needed
                        print(f"Received audio chunk: {len(chunk)} bytes")
                        
            finally:
                if file_handle:
                    file_handle.close()


def main():
    """Example usage of the live translation client."""
    
    # Initialize client
    client = LiveTranslationClient()
    
    # Get supported languages
    print("Getting supported languages...")
    languages = client.get_supported_languages()
    print("Supported languages:", list(languages['supported_languages'].keys()))
    
    # Example YouTube live stream URLs (replace with actual live streams)
    test_urls = [
        "https://www.youtube.com/@nasa/live",
        "https://www.youtube.com/@SpaceX/live",
        "https://www.youtube.com/@BBCNews/live"
    ]
    
    # Start translation to Tamil
    youtube_url = input("Enter YouTube live stream URL (or press Enter for example): ").strip()
    if not youtube_url:
        youtube_url = test_urls[0]
        print(f"Using example URL: {youtube_url}")
    
    target_language = input("Enter target language (default: tamil): ").strip() or "tamil"
    
    print(f"\nStarting translation to {target_language}...")
    result = client.start_translation(youtube_url, target_language)
    
    if not result:
        print("Failed to start translation")
        return
    
    stream_id = result['stream_id']
    print(f"Started stream with ID: {stream_id}")
    print(f"Status URL: {result['status_url']}")
    print(f"Stream URL: {result['websocket_url']}")
    
    # Monitor status
    print("\nMonitoring translation status...")
    for i in range(10):  # Check status for 10 iterations
        status = client.get_status(stream_id)
        print(f"Status: {status['status']}, Chunks: {status['chunks_processed']}, Duration: {status['total_duration']:.1f}s")
        
        if status['status'] == 'error':
            print(f"Error: {status['error_message']}")
            break
        elif status['status'] == 'active':
            print("Translation is active!")
            break
        
        time.sleep(2)
    
    # Option to stream audio
    stream_audio = input("\nDo you want to stream the translated audio? (y/n): ").strip().lower()
    if stream_audio == 'y':
        output_file = f"translated_audio_{target_language}_{int(time.time())}.mp3"
        print(f"Streaming audio to {output_file}...")
        print("Press Ctrl+C to stop streaming")
        
        try:
            client.stream_audio(stream_id, output_file)
        except KeyboardInterrupt:
            print("\nStopping audio stream...")
    
    # Stop the translation
    stop_stream = input("\nDo you want to stop the translation stream? (y/n): ").strip().lower()
    if stop_stream == 'y':
        print("Stopping translation...")
        result = client.stop_translation(stream_id)
        print(f"Result: {result}")
    
    # List all active streams
    print("\nActive streams:")
    streams = client.list_active_streams()
    for stream in streams['active_streams']:
        print(f"  - {stream['stream_id']}: {stream['language']} ({stream['status']})")


if __name__ == "__main__":
    main() 