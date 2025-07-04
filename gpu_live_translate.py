#!/usr/bin/env python3
"""
GPU-Optimized Live Video Translation Script

Specifically optimized for RTX 4090 for maximum performance.
"""

import sys
import subprocess
import os
from gpu_config import set_environment_variables, print_gpu_status, get_optimized_config

def main():
    """GPU-optimized live video translation with RTX 4090 settings."""
    
    if len(sys.argv) < 3:
        print("🎮 GPU-Optimized Live Video Translation")
        print("=" * 50)
        print("Usage: python gpu_live_translate.py <youtube_url> <language> [output_file]")
        print()
        print("Examples:")
        print("  python gpu_live_translate.py 'https://www.youtube.com/@nasa' tamil")
        print("  python gpu_live_translate.py 'https://www.youtube.com/@BBCNews' malayalam bbc_audio.mp3")
        print("  python gpu_live_translate.py 'https://www.youtube.com/@SpaceX' japanese")
        print()
        print("Supported languages: english, tamil, malayalam, gujarati, kannada, marathi, japanese, korean")
        print()
        print("💡 Optimized for RTX 4090 - maximum performance!")
        return
    
    # Set GPU optimizations
    set_environment_variables()
    
    # Print GPU status
    print_gpu_status()
    
    youtube_url = sys.argv[1].replace('\\', '')  # Remove escaped characters
    language = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
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
        print(f"Supported languages: {', '.join(supported_languages)}")
        return
    
    # Get optimized configuration
    config = get_optimized_config()
    
    print(f"\n🚀 Starting GPU-optimized live translation...")
    print(f"   URL: {youtube_url}")
    print(f"   Language: {language}")
    print(f"   Compute Type: {config['compute_type']}")
    print(f"   Batch Size: {config['batch_size']}")
    print(f"   Chunk Duration: {config['chunk_duration']}s")
    print(f"   Model: {config['transcriber_model']}")
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
    
    # Build optimized CLI command
    cmd = [
        sys.executable, 'cli_translate.py', 'translate',
        youtube_url,
        '--language', language,
        '--auto-find',  # Auto-find live stream
        '--chunk-duration', str(config['chunk_duration']),
        '--model', config['transcriber_model']
    ]
    
    if output_file:
        cmd.extend(['--output', output_file])
    
    print(f"🔧 Command: {' '.join(cmd)}")
    print()
    
    try:
        # Run the translation with GPU optimizations
        print("🔄 Starting GPU-optimized translation (press Ctrl+C to stop)...")
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Translation stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Translation failed: {e}")
        print("💡 Make sure the API server is running: python run_serve.py")
        print("💡 Check if the URL is a valid live stream")
    except FileNotFoundError:
        print("❌ cli_translate.py not found!")
        print("💡 Make sure you're running this from the SoniTranslate directory")

def check_gpu_requirements():
    """Check if GPU requirements are met."""
    try:
        import torch
        if not torch.cuda.is_available():
            print("⚠️  CUDA not available. Install PyTorch with CUDA support.")
            print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
            return False
        
        gpu_count = torch.cuda.device_count()
        if gpu_count == 0:
            print("⚠️  No GPU detected. Performance will be limited.")
            return False
        
        print(f"✅ CUDA available with {gpu_count} GPU(s)")
        return True
        
    except ImportError:
        print("❌ PyTorch not installed. Install with:")
        print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
        return False

if __name__ == "__main__":
    # Check GPU requirements first
    if not check_gpu_requirements():
        print("\n💡 You can still run the script, but performance will be limited.")
        print("   For best performance, install PyTorch with CUDA support.")
    
    main() 