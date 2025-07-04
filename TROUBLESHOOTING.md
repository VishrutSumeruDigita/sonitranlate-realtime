# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### 1. **"No live stream found at provided URL" Error**

This is the most common issue. Here are the solutions in order of preference:

#### **Solution A: Use the Robust Script**
```bash
# Use the enhanced script that tries multiple methods
python robust_live_translate.py "https://www.youtube.com/@ZeeNews" tamil
```

#### **Solution B: Install yt-dlp**
```bash
# Install the required dependency
pip install yt-dlp

# Then try the original script
python live_translate.py "https://www.youtube.com/@ZeeNews" tamil
```

#### **Solution C: Use Direct Live Stream URLs**
```bash
# Instead of channel URL, use the actual live stream URL
python live_translate.py "https://www.youtube.com/@ZeeNews/live" tamil
```

#### **Solution D: Manual CLI with Different Options**
```bash
# Try without auto-find
python cli_translate.py translate "https://www.youtube.com/@ZeeNews" --language tamil

# Try with live-check
python cli_translate.py translate "https://www.youtube.com/@ZeeNews" --language tamil --live-check

# Try with auto-find
python cli_translate.py translate "https://www.youtube.com/@ZeeNews" --language tamil --auto-find
```

### 2. **Server Connection Issues**

#### **Check if Server is Running**
```bash
# Test server connectivity
python test_server.py

# Start server if not running
python run_serve.py
```

#### **Check Server Logs**
Look for errors in the server terminal where you ran `python run_serve.py`

### 3. **URL Format Issues**

#### **Clean URLs Manually**
```bash
# Remove escaped characters manually
python live_translate.py "https://www.youtube.com/watch?v=abc123" tamil
```

#### **Use Different URL Formats**
```bash
# Try channel URL
python live_translate.py "https://www.youtube.com/@ZeeNews" tamil

# Try live URL
python live_translate.py "https://www.youtube.com/@ZeeNews/live" tamil

# Try video URL (if it's live)
python live_translate.py "https://www.youtube.com/watch?v=abc123" tamil
```

### 4. **Dependency Issues**

#### **Missing yt-dlp**
```bash
pip install yt-dlp
```

#### **Missing requests**
```bash
pip install requests
```

#### **Missing other dependencies**
```bash
pip install -r requirements_serve.txt
```

### 5. **Performance Issues**

#### **Use Faster Settings**
```bash
# Use smaller model and shorter chunks
python cli_translate.py translate "URL" --language tamil --model small --chunk-duration 20
```

#### **Check System Resources**
- Ensure enough RAM (at least 4GB free)
- Check CPU usage
- Monitor disk space

## Step-by-Step Debugging

### **Step 1: Test Server**
```bash
python test_server.py
```

### **Step 2: Test Live Detection**
```bash
python simple_live_detector.py
```

### **Step 3: Test Basic Translation**
```bash
# Try with a known working URL
python live_translate.py "https://www.youtube.com/@nasa" english
```

### **Step 4: Check Logs**
Look for specific error messages in:
- Server terminal
- Client terminal
- System logs

## Advanced Troubleshooting

### **Enable Debug Logging**
```bash
# Start server with debug logging
uvicorn serve:app --host 0.0.0.0 --port 8000 --log-level debug
```

### **Test Individual Components**
```bash
# Test None comparison fix
python test_none_fix.py

# Test general fixes
python test_fixes.py
```

### **Check Network Connectivity**
```bash
# Test if you can access YouTube
curl -I "https://www.youtube.com"

# Test if you can access the server
curl -I "http://localhost:8000"
```

## Common Error Messages and Solutions

### **"ModuleNotFoundError: No module named 'yt_dlp'"**
```bash
pip install yt-dlp
```

### **"Connection refused"**
```bash
# Start the server
python run_serve.py
```

### **"No live stream found"**
- Try different URL formats
- Use the robust script
- Install yt-dlp
- Check if the channel is actually live

### **"'<' not supported between instances of 'NoneType' and 'float'"**
- This should be fixed in the latest version
- Run `python test_none_fix.py` to verify

### **"Invalid stream info: missing URL"**
- The live stream detection failed
- Try a different URL or method

## Getting Help

### **1. Check the Logs**
Always check the terminal output for error messages.

### **2. Use the Test Scripts**
```bash
python test_server.py
python test_none_fix.py
python simple_live_detector.py
```

### **3. Try the Robust Script**
```bash
python robust_live_translate.py "URL" language
```

### **4. Check Dependencies**
```bash
pip list | grep -E "(yt-dlp|requests|fastapi|uvicorn)"
```

### **5. Verify URL Format**
Make sure the URL is:
- A valid YouTube URL
- Actually a live stream
- Not blocked or private

## Quick Fix Checklist

- [ ] Server is running (`python run_serve.py`)
- [ ] yt-dlp is installed (`pip install yt-dlp`)
- [ ] URL is valid and live
- [ ] No firewall blocking connections
- [ ] Enough system resources available
- [ ] Using the latest version of scripts

## Emergency Workaround

If nothing else works, try this manual approach:

```bash
# 1. Start server
python run_serve.py

# 2. In another terminal, use direct API call
curl -X POST "http://localhost:8000/tamil" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "YOUR_URL_HERE",
    "chunk_duration": 30,
    "transcriber_model": "base"
  }'
``` 