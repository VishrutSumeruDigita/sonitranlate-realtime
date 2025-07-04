#!/usr/bin/env python3
"""
Test Server Script

Simple script to test if the SoniTranslate server is working properly.
"""

import requests
import json
import time

def test_server():
    """Test if the server is running and responding."""
    print("🧪 Testing SoniTranslate Server")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Check if server is running
    print("1. Testing server connectivity...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Server is running")
            data = response.json()
            print(f"   📊 Active streams: {data.get('active_streams', 0)}")
        else:
            print(f"   ❌ Server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot connect to server: {e}")
        print("   💡 Make sure to start the server with: python run_serve.py")
        return False
    
    # Test 2: Check supported languages
    print("\n2. Testing languages endpoint...")
    try:
        response = requests.get(f"{base_url}/languages", timeout=5)
        if response.status_code == 200:
            data = response.json()
            languages = data.get('supported_languages', {})
            print(f"   ✅ Found {len(languages)} supported languages")
            print(f"   📋 Languages: {', '.join(languages.keys())}")
        else:
            print(f"   ❌ Languages endpoint returned status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error getting languages: {e}")
    
    # Test 3: Check channels endpoint
    print("\n3. Testing channels endpoint...")
    try:
        response = requests.get(f"{base_url}/channels", timeout=5)
        if response.status_code == 200:
            data = response.json()
            channels = data.get('channels', [])
            print(f"   ✅ Found {len(channels)} configured channels")
        else:
            print(f"   ❌ Channels endpoint returned status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error getting channels: {e}")
    
    # Test 4: Check streams endpoint
    print("\n4. Testing streams endpoint...")
    try:
        response = requests.get(f"{base_url}/streams", timeout=5)
        if response.status_code == 200:
            data = response.json()
            streams = data.get('active_streams', [])
            print(f"   ✅ Found {len(streams)} active streams")
        else:
            print(f"   ❌ Streams endpoint returned status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error getting streams: {e}")
    
    # Test 5: Test a simple translation request (without starting it)
    print("\n5. Testing translation endpoint structure...")
    try:
        # Just test the endpoint structure, don't actually start translation
        test_data = {
            "youtube_url": "https://www.youtube.com/@test",
            "chunk_duration": 30,
            "transcriber_model": "base"
        }
        
        response = requests.post(f"{base_url}/tamil", json=test_data, timeout=10)
        # We expect this to fail because the URL is not real, but we can check the response
        if response.status_code in [400, 422]:  # Expected errors for invalid URL
            print("   ✅ Translation endpoint is responding (expected error for test URL)")
        elif response.status_code == 200:
            print("   ⚠️  Translation started (unexpected for test URL)")
        else:
            print(f"   ❌ Translation endpoint returned status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing translation endpoint: {e}")
    
    print("\n✅ Server test completed!")
    print("\n💡 If all tests passed, the server is working correctly.")
    print("   You can now try running live translations.")
    
    return True

def test_live_detection():
    """Test live stream detection without yt-dlp."""
    print("\n🧪 Testing Live Stream Detection (Simple Method)")
    print("=" * 50)
    
    try:
        from simple_live_detector import SimpleLiveDetector
        
        detector = SimpleLiveDetector()
        
        test_urls = [
            "https://www.youtube.com/@ZeeNews",
            "https://www.youtube.com/@nasa",
            "https://www.youtube.com/@BBCNews/live",
        ]
        
        for url in test_urls:
            print(f"\n🔍 Testing: {url}")
            try:
                is_live = detector.is_live_stream(url)
                print(f"   Is live: {is_live}")
                
                if is_live:
                    info = detector.get_live_stream_info(url)
                    print(f"   Info: {info}")
            except Exception as e:
                print(f"   Error: {e}")
                
    except ImportError:
        print("❌ Simple live detector not available")
        print("💡 Make sure simple_live_detector.py is in the current directory")

if __name__ == "__main__":
    print("🚀 SoniTranslate Server Test Suite")
    print("=" * 50)
    
    # Test server
    server_ok = test_server()
    
    # Test live detection
    test_live_detection()
    
    if server_ok:
        print("\n🎉 All tests completed! Server appears to be working correctly.")
    else:
        print("\n❌ Server tests failed. Please check the server status.") 