#!/usr/bin/env python3
"""
Launcher script for the SoniTranslate Live Stream API

This script checks dependencies and starts the translation service.
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed."""
    
    missing_deps = []
    
    # Check Python packages
    required_packages = [
        'fastapi',
        'uvicorn', 
        'ffmpeg',
        'pydantic',
        'requests',
        'yt_dlp'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✓ {package} is installed")
        except ImportError:
            missing_deps.append(package)
            logger.error(f"✗ {package} is missing")
    
    # Check system dependencies
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      capture_output=True, check=True)
        logger.info("✓ FFmpeg system binary is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning("⚠ FFmpeg system binary not found - may cause issues")
    
    return missing_deps

def install_dependencies(missing_deps):
    """Install missing dependencies."""
    
    if not missing_deps:
        return True
    
    logger.info(f"Installing missing dependencies: {missing_deps}")
    
    try:
        # Install from requirements files
        if os.path.exists('requirements_serve.txt'):
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', 
                '-r', 'requirements_serve.txt'
            ], check=True)
        
        # Install individual packages
        for dep in missing_deps:
            if dep == 'ffmpeg':
                dep = 'ffmpeg-python'
            
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', dep
            ], check=True)
            
        logger.info("Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        return False

def main():
    """Main launcher function."""
    
    print("🚀 SoniTranslate Live Stream API Launcher")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('serve.py'):
        logger.error("serve.py not found! Please run this from the SoniTranslate directory.")
        sys.exit(1)
    
    if not os.path.exists('app_rvc.py'):
        logger.error("app_rvc.py not found! Please run this from the SoniTranslate directory.")
        sys.exit(1)
    
    # Check dependencies
    logger.info("Checking dependencies...")
    missing_deps = check_dependencies()
    
    if missing_deps:
        install_choice = input(f"\nMissing dependencies: {missing_deps}\nInstall them? (y/n): ")
        if install_choice.lower() == 'y':
            if not install_dependencies(missing_deps):
                logger.error("Failed to install dependencies. Please install manually.")
                sys.exit(1)
        else:
            logger.error("Cannot start service without required dependencies.")
            sys.exit(1)
    
    # Start the service
    print("\n🌟 Starting SoniTranslate Live Stream API...")
    print("📡 Service will be available at: http://localhost:8000")
    print("📚 API documentation: http://localhost:8000/docs")
    print("🔍 Alternative docs: http://localhost:8000/redoc")
    print("\nSupported endpoints:")
    print("  POST /english    - Translate to English")
    print("  POST /tamil      - Translate to Tamil") 
    print("  POST /malayalam  - Translate to Malayalam")
    print("  POST /gujarati   - Translate to Gujarati")
    print("  POST /kannada    - Translate to Kannada")
    print("  POST /marathi    - Translate to Marathi")
    print("  POST /japanese   - Translate to Japanese")
    print("  POST /korean     - Translate to Korean")
    print("\nPress Ctrl+C to stop the service")
    print("=" * 50)
    
    try:
        # Start uvicorn server
        subprocess.run([
            sys.executable, '-m', 'uvicorn', 
            'serve:app',
            '--host', '0.0.0.0',
            '--port', '8000',
            '--reload',
            '--log-level', 'info'
        ], check=True)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Service stopped by user")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 