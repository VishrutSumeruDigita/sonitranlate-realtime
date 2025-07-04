#!/usr/bin/env python3
"""
Quick Live Video Translation Script

Simple script to translate YouTube live streams with minimal arguments.
Usage: python live_translate.py <youtube_url> <language> [output_file]
"""

import sys
import subprocess
import os

def main():
    """Quick live video translation with minimal arguments."""
    
    if len(sys.argv) < 3:
        print("🎥 Quick Live Video Translation")
        print("=" * 40)
        print("Usage: python live_translate.py <youtube_url> <language> [output_file]")
        print()
        print("Examples:")
        print("  python live_translate.py 'https://www.youtube.com/@nasa/live' tamil")
        print("  python live_translate.py 'https://www.youtube.com/@BBCNews/live' malayalam bbc_audio.mp3")
        print("  python live_translate.py 'https://www.youtube.com/@SpaceX/live' japanese")
        print()
        print("Supported languages: english, tamil, malayalam, gujarati, kannada, marathi, japanese, korean")
        print()
        print("💡 Make sure the API server is running: python run_serve.py")
        return
    
    youtube_url = sys.argv[1]
    language = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Validate language
    supported_languages = [
        'english', 'tamil', 'malayalam', 'gujarati', 'kannada', 
        'marathi', 'japanese', 'korean', 'hindi', 'spanish', 
        'french', 'german', 'chinese', 'arabic', 'portuguese', 
        'russian', 'italian'
    ]
    
    if language not in supported_languages:
        print(f"❌ Unsupported language: {language}")
        print(f"Supported languages: {', '.join(supported_languages)}")
        return
    
    print(f"🚀 Starting live translation...")
    print(f"   URL: {youtube_url}")
    print(f"   Language: {language}")
    if output_file:
        print(f"   Output: {output_file}")
    print()
    
    # Build CLI command
    cmd = [
        sys.executable, 'cli_translate.py', 'live',
        youtube_url,
        '--language', language
    ]
    
    if output_file:
        cmd.extend(['--output', output_file])
    
    # Add fast mode for better performance
    cmd.append('--fast')
    
    try:
        # Run the translation
        print("🔄 Starting translation (press Ctrl+C to stop)...")
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Translation stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Translation failed: {e}")
        print("💡 Make sure the API server is running: python run_serve.py")
    except FileNotFoundError:
        print("❌ cli_translate.py not found!")
        print("💡 Make sure you're running this from the SoniTranslate directory")

if __name__ == "__main__":
    main() 