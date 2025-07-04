#!/usr/bin/env python3
"""
Robust Live Video Translation Script

Enhanced version that can handle various live stream detection scenarios.
"""

import sys
import subprocess
import os
import time
from simple_live_detector import SimpleLiveDetector

def main():
    """Robust live video translation with enhanced error handling."""
    
    if len(sys.argv) < 3:
        print("🎥 Robust Live Video Translation")
        print("=" * 40)
        print("Usage: python robust_live_translate.py <youtube_url> <language> [output_file]")
        print()
        print("Examples:")
        print("  python robust_live_translate.py 'https://www.youtube.com/@nasa' tamil")
        print("  python robust_live_translate.py 'https://www.youtube.com/@BBCNews' malayalam bbc_audio.mp3")
        print("  python robust_live_translate.py 'https://www.youtube.com/@SpaceX' japanese")
        print()
        print("Supported languages: english, tamil, malayalam, gujarati, kannada, marathi, japanese, korean")
        print()
        print("💡 Make sure the API server is running: python run_serve.py")
        return
    
    youtube_url = sys.argv[1].replace('\\', '')  # Remove escaped characters
    language = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    print(f"🔧 Cleaned URL: {youtube_url}")
    
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
    
    print(f"🚀 Starting robust live translation...")
    print(f"   URL: {youtube_url}")
    print(f"   Language: {language}")
    if output_file:
        print(f"   Output: {output_file}")
    print()
    
    # Check if server is running
    print("🔍 Checking if API server is running...")
    try:
        import requests
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
        else:
            print("❌ API server is not responding properly")
            print("💡 Start the server with: python run_serve.py")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API server: {e}")
        print("💡 Start the server with: python run_serve.py")
        return
    
    # Try different approaches to find live stream
    print("🔍 Detecting live stream...")
    
    # Method 1: Try with auto-find
    print("   Method 1: Using auto-find...")
    cmd1 = [
        sys.executable, 'cli_translate.py', 'translate',
        youtube_url,
        '--language', language,
        '--auto-find'
    ]
    
    if output_file:
        cmd1.extend(['--output', output_file])
    
    cmd1.extend(['--chunk-duration', '20', '--model', 'small'])
    
    try:
        print(f"   Trying: {' '.join(cmd1)}")
        result = subprocess.run(cmd1, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Translation started successfully!")
            return
        else:
            print(f"   Method 1 failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("   Method 1 timed out")
    except Exception as e:
        print(f"   Method 1 error: {e}")
    
    # Method 2: Try with live-check
    print("   Method 2: Using live-check...")
    cmd2 = [
        sys.executable, 'cli_translate.py', 'translate',
        youtube_url,
        '--language', language,
        '--live-check'
    ]
    
    if output_file:
        cmd2.extend(['--output', output_file])
    
    cmd2.extend(['--chunk-duration', '20', '--model', 'small'])
    
    try:
        print(f"   Trying: {' '.join(cmd2)}")
        result = subprocess.run(cmd2, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Translation started successfully!")
            return
        else:
            print(f"   Method 2 failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("   Method 2 timed out")
    except Exception as e:
        print(f"   Method 2 error: {e}")
    
    # Method 3: Try direct translation (assume it's live)
    print("   Method 3: Direct translation (assuming live)...")
    cmd3 = [
        sys.executable, 'cli_translate.py', 'translate',
        youtube_url,
        '--language', language
    ]
    
    if output_file:
        cmd3.extend(['--output', output_file])
    
    cmd3.extend(['--chunk-duration', '20', '--model', 'small'])
    
    try:
        print(f"   Trying: {' '.join(cmd3)}")
        result = subprocess.run(cmd3, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Translation started successfully!")
            return
        else:
            print(f"   Method 3 failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("   Method 3 timed out")
    except Exception as e:
        print(f"   Method 3 error: {e}")
    
    # Method 4: Use simple detector
    print("   Method 4: Using simple live detector...")
    try:
        detector = SimpleLiveDetector()
        is_live = detector.is_live_stream(youtube_url)
        
        if is_live:
            print(f"   ✅ Simple detector confirms live stream")
            # Try direct translation again
            result = subprocess.run(cmd3, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("✅ Translation started successfully!")
                return
        else:
            print(f"   ❌ Simple detector says not live")
            
    except Exception as e:
        print(f"   Method 4 error: {e}")
    
    # All methods failed
    print("\n❌ All methods failed to start translation")
    print("\n💡 Troubleshooting tips:")
    print("   1. Make sure the API server is running: python run_serve.py")
    print("   2. Check if the URL is actually a live stream")
    print("   3. Try a different channel or URL")
    print("   4. Check server logs for more details")
    print("   5. Try installing yt-dlp: pip install yt-dlp")

if __name__ == "__main__":
    main() 