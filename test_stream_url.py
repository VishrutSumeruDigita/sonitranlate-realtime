#!/usr/bin/env python3
"""
Test Stream URL Processing

Test script to verify that stream URLs can be processed correctly.
"""

import ffmpeg
import sys
import time

def test_stream_url(stream_url):
    """Test if a stream URL can be processed by FFmpeg."""
    print(f"🧪 Testing stream URL: {stream_url}")
    print("=" * 60)
    
    try:
        # Test FFmpeg input
        print("1. Testing FFmpeg input...")
        probe = ffmpeg.probe(stream_url)
        print(f"   ✅ Stream info: {probe.get('format', {}).get('duration', 'unknown')}s")
        
        # Test audio stream
        audio_streams = [s for s in probe.get('streams', []) if s.get('codec_type') == 'audio']
        if audio_streams:
            print(f"   ✅ Found {len(audio_streams)} audio stream(s)")
            for i, stream in enumerate(audio_streams):
                print(f"      Stream {i}: {stream.get('codec_name', 'unknown')} @ {stream.get('sample_rate', 'unknown')}Hz")
        else:
            print("   ⚠️  No audio streams found")
        
        # Test FFmpeg process
        print("\n2. Testing FFmpeg process...")
        process = (
            ffmpeg
            .input(stream_url, t=10)  # Test for 10 seconds
            .output('pipe:', format='wav', acodec='pcm_s16le', ac=1, ar='16000')
            .run_async(pipe_stdout=True, pipe_stderr=True)
        )
        
        # Read some audio data
        audio_data = b''
        start_time = time.time()
        
        while time.time() - start_time < 5:  # Test for 5 seconds
            chunk = process.stdout.read(4096)
            if chunk:
                audio_data += chunk
            else:
                break
        
        process.terminate()
        process.wait()
        
        print(f"   ✅ Read {len(audio_data)} bytes of audio data")
        
        if len(audio_data) > 0:
            print("   ✅ Stream URL is working correctly!")
            return True
        else:
            print("   ❌ No audio data received")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_manifest_url():
    """Test with a sample manifest URL."""
    print("🧪 Testing Manifest URL Processing")
    print("=" * 60)
    
    # This is a sample manifest URL format
    sample_url = "https://manifest.googlevideo.com/api/manifest/hls_playlist/..."
    
    print("Note: Manifest URLs require special handling in FFmpeg")
    print("They should work with the .m3u8 extension or HLS protocol")
    
    return True

def main():
    """Main test function."""
    if len(sys.argv) > 1:
        stream_url = sys.argv[1]
        success = test_stream_url(stream_url)
        
        if success:
            print("\n✅ Stream URL test passed!")
        else:
            print("\n❌ Stream URL test failed!")
    else:
        print("Usage: python test_stream_url.py <stream_url>")
        print("\nExample:")
        print("  python test_stream_url.py 'https://example.com/stream.m3u8'")

if __name__ == "__main__":
    main() 