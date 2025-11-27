# Pexels Video API Setup Guide

## Why Pexels?
- ✅ **FREE** - No cost, generous limits
- ✅ **High Quality** - Professional stock videos
- ✅ **Better Search** - More relevant results than Tenor
- ✅ **Millions of Videos** - Huge library
- ✅ **No Watermarks** - Clean videos

## Setup Steps:

### 1. Get Your Free API Key
1. Visit: https://www.pexels.com/api/
2. Click "Get Started" or "Sign Up"
3. Create a free account (email + password)
4. Go to your API dashboard
5. Copy your API key (looks like: `YOUR_API_KEY_HERE`)

### 2. Add API Key to Code
Open `/backend/main.py` and find line ~477:
```python
pexels_api_key = "YOUR_PEXELS_API_KEY"  # Replace with actual key
```

Replace with your actual key:
```python
pexels_api_key = "563492ad6f91700001000001abcdef1234567890"  # Your actual key
```

### 3. Restart Server
The server should auto-reload, but if not:
```bash
# Stop the server (Ctrl+C)
# Then restart:
venv/bin/uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Test It!
1. Go to AI Meme tab
2. Select "Short Video"
3. Enter: "dog dancing"
4. Generate!

You should now get **actual relevant videos** of dogs dancing! 🐕💃

## API Limits:
- **Free Tier**: 200 requests/hour
- **Rate Limit**: Plenty for personal use
- **No Credit Card Required**: Completely free!

## Fallback System:
If Pexels fails or you haven't added the key:
1. Falls back to Tenor MP4 videos
2. Falls back to Tenor GIFs
3. Falls back to static images

So the system will still work even without the Pexels key!
