#!/usr/bin/env python3
"""
GPU Configuration for RTX 4090

Optimized settings for maximum performance with RTX 4090.
"""

import os
import torch

# GPU Configuration for RTX 4090
RTX_4090_CONFIG = {
    # Compute settings optimized for RTX 4090
    "compute_type": "bfloat16",  # Best performance/quality balance for RTX 4090
    "batch_size": 4,  # RTX 4090 can handle larger batches
    "chunk_duration": 20,  # Optimal chunk size for RTX 4090
    "transcriber_model": "base",  # Use base model for better quality with RTX 4090
    
    # Memory optimization
    "enable_cache": False,  # Disable cache for real-time processing
    "segment_duration_limit": 15,  # Slightly longer segments for better quality
    
    # Audio settings
    "volume_original_audio": 0.1,
    "volume_translated_audio": 1.0,
    "mix_method_audio": "Adjusting volumes and mixing audio",
    "output_type": "audio (mp3)",
    
    # Performance settings
    "is_gui": False,
    "low_cpu_mem_usage": True,
}

def get_gpu_info():
    """Get GPU information and capabilities."""
    try:
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_info = []
            
            for i in range(gpu_count):
                gpu_name = torch.cuda.get_device_name(i)
                gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3  # GB
                gpu_info.append({
                    "id": i,
                    "name": gpu_name,
                    "memory_gb": round(gpu_memory, 2)
                })
            
            return gpu_info
        else:
            return None
    except Exception as e:
        print(f"Error getting GPU info: {e}")
        return None

def is_rtx_4090():
    """Check if RTX 4090 is available."""
    gpu_info = get_gpu_info()
    if gpu_info:
        for gpu in gpu_info:
            if "RTX 4090" in gpu["name"]:
                return True
    return False

def get_optimized_config():
    """Get optimized configuration based on available GPU."""
    if is_rtx_4090():
        print("🎮 RTX 4090 detected! Using optimized settings.")
        return RTX_4090_CONFIG
    elif torch.cuda.is_available():
        print("🎮 GPU detected! Using standard GPU settings.")
        # Fallback to standard GPU settings
        config = RTX_4090_CONFIG.copy()
        config["batch_size"] = 2  # Smaller batch for other GPUs
        config["compute_type"] = "float16"  # Use float16 for other GPUs
        return config
    else:
        print("💻 No GPU detected! Using CPU settings.")
        # CPU fallback
        config = RTX_4090_CONFIG.copy()
        config["batch_size"] = 1
        config["compute_type"] = "float32"
        config["chunk_duration"] = 30  # Longer chunks for CPU
        return config

def set_environment_variables():
    """Set environment variables for optimal GPU performance."""
    # Set CUDA environment variables for RTX 4090
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # Use first GPU
    os.environ["CUDA_LAUNCH_BLOCKING"] = "0"  # Non-blocking CUDA operations
    
    # Memory optimization
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"
    
    # Performance optimization
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    
    # For RTX 4090, enable tensor cores
    if is_rtx_4090():
        os.environ["TORCH_CUDNN_V8_API_ENABLED"] = "1"
        print("🚀 RTX 4090 optimizations enabled!")

def print_gpu_status():
    """Print current GPU status and configuration."""
    print("🎮 GPU Status Report")
    print("=" * 40)
    
    gpu_info = get_gpu_info()
    if gpu_info:
        for gpu in gpu_info:
            print(f"GPU {gpu['id']}: {gpu['name']}")
            print(f"  Memory: {gpu['memory_gb']} GB")
            
            # Check if it's RTX 4090
            if "RTX 4090" in gpu["name"]:
                print("  ✅ RTX 4090 detected - optimal performance available!")
            else:
                print("  ⚠️  Other GPU - using standard settings")
    else:
        print("❌ No GPU detected - using CPU mode")
    
    config = get_optimized_config()
    print(f"\n📊 Optimized Configuration:")
    print(f"  Compute Type: {config['compute_type']}")
    print(f"  Batch Size: {config['batch_size']}")
    print(f"  Chunk Duration: {config['chunk_duration']}s")
    print(f"  Model: {config['transcriber_model']}")

if __name__ == "__main__":
    set_environment_variables()
    print_gpu_status() 