#!/usr/bin/env python3
"""
Debug Live Video Translation Script

Enhanced version with detailed logging and error handling for troubleshooting.
"""

import sys
import subprocess
import os
import time
import requests
import json
from gpu_config import set_environment_variables, print_gpu_status, get_optimized_config

def check_server_status():
    """Check detailed server status."""
    print("🔍 Checking server status...")
    
    try:
        # Check root endpoint
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Server running - Active streams: {data.get('active_streams', 0)}")
            return True
        else:
            print(f"   ❌ Server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot connect to server: {e}")
        return False

def test_live_stream_detection(url):
    """Test live stream detection separately."""
    print(f"🔍 Testing live stream detection for: {url}")
    
    try:
        # Test the find-live command
        cmd = [
            sys.executable, 'cli_translate.py', 'find-live'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("   ✅ Live stream detection working")
            return True
        else:
            print(f"   ❌ Live stream detection failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing live stream detection: {e}")
        return False

def test_translation_endpoint(url, language):
    """Test translation endpoint directly."""
    print(f"🔍 Testing translation endpoint...")
    
    try:
        # Test with a simple request
        test_data = {
            "youtube_url": url,
            "chunk_duration": 20,
            "transcriber_model": "base"
        }
        
        response = requests.post(f"http://localhost:8000/{language}", 
                               json=test_data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Translation started - Stream ID: {data.get('stream_id', 'unknown')}")
            return data.get('stream_id')
        else:
            print(f"   ❌ Translation failed - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error testing translation endpoint: {e}")
        return None

def monitor_stream_status(stream_id, timeout=60):
    """Monitor stream status for debugging."""
    print(f"📊 Monitoring stream {stream_id}...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"http://localhost:8000/status/{stream_id}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                chunks = data.get('chunks_processed', 0)
                duration = data.get('total_duration', 0)
                error = data.get('error_message', '')
                
                print(f"   Status: {status} | Chunks: {chunks} | Duration: {duration:.1f}s")
                
                if error:
                    print(f"   ❌ Error: {error}")
                    return False
                
                if status == "active" and chunks > 0:
                    print("   ✅ Stream is working correctly!")
                    return True
                    
            else:
                print(f"   ❌ Status check failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error checking status: {e}")
        
        time.sleep(2)
    
    print("   ⏰ Timeout waiting for stream to start")
    return False

def main():
    """Debug live video translation with detailed logging."""
    
    if len(sys.argv) < 3:
        print("🔧 Debug Live Video Translation")
        print("=" * 50)
        print("Usage: python debug_live_translate.py <youtube_url> <language>")
        print()
        print("This script provides detailed debugging information.")
        return
    
    # Set GPU optimizations
    set_environment_variables()
    print_gpu_status()
    
    youtube_url = sys.argv[1].replace('\\', '')  # Remove escaped characters
    language = sys.argv[2]
    
    print(f"\n🔧 Cleaned URL: {youtube_url}")
    
    # Validate language
    supported_languages = [
        'english', 'tamil', 'malayalam', 'gujarati', 'kannada', 
        'marathi', 'japanese', 'korean', 'hindi', 'spanish', 
        'french', 'german', 'chinese', 'arabic', 'portuguese', 
        'russian', 'italian'
    ]
    
    if language not in supported_languages:
        print(f"❌ Unsupported language: {language}")
        return
    
    # Get optimized configuration
    config = get_optimized_config()
    
    print(f"\n🚀 Starting debug translation...")
    print(f"   URL: {youtube_url}")
    print(f"   Language: {language}")
    print(f"   Compute Type: {config['compute_type']}")
    print(f"   Batch Size: {config['batch_size']}")
    print(f"   Chunk Duration: {config['chunk_duration']}s")
    print(f"   Model: {config['transcriber_model']}")
    print()
    
    # Step 1: Check server status
    if not check_server_status():
        print("❌ Server is not running properly")
        print("💡 Start the server with: python run_serve.py")
        return
    
    # Step 2: Test live stream detection
    if not test_live_stream_detection(youtube_url):
        print("❌ Live stream detection is not working")
        return
    
    # Step 3: Test translation endpoint
    stream_id = test_translation_endpoint(youtube_url, language)
    if not stream_id:
        print("❌ Translation endpoint is not working")
        return
    
    # Step 4: Monitor stream status
    print(f"\n📊 Monitoring stream {stream_id} for 60 seconds...")
    success = monitor_stream_status(stream_id, timeout=60)
    
    if success:
        print("\n✅ Translation is working correctly!")
        print("💡 The issue might be intermittent. Try running again.")
    else:
        print("\n❌ Translation failed during processing")
        print("💡 Check the server logs for more details")
        print("💡 Try using a different URL or language")

if __name__ == "__main__":
    main() 