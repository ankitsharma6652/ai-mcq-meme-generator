# 🔄 Server Restart Instructions

## Current Status:
✅ Replicate API key is configured
✅ Startup script created: `start_server.sh`
⚠️ Server is currently running WITHOUT the API key

## To Enable AI Video Generation:

### Step 1: Stop Current Server
In the terminal where the server is running, press:
```
Ctrl + C
```

You should see the server stop.

### Step 2: Start New Server with API Key
Run this command:
```bash
./start_server.sh
```

Or manually (make sure to set your API key in .env file first):
```bash
./start_server.sh
```

### Step 3: Verify AI is Enabled
You should see in the terminal:
```
🚀 Starting server with Replicate AI enabled...
📝 API Token: r8_ber4XOA...
```

Then the normal uvicorn startup messages.

### Step 4: Test AI Video Generation
1. Refresh browser (http://localhost:8000)
2. Go to AI Meme tab
3. Select "Short Video"
4. Enter: "white husky dog dancing"
5. Click Generate
6. Wait 30-60 seconds
7. See your AI-generated video! 🎬

## Troubleshooting:

**If you see "Replicate API key not configured":**
- Make sure you stopped the old server
- Make sure you ran `./start_server.sh` or exported the API key
- Check terminal for the "🚀 Starting server with Replicate AI enabled..." message

**If generation is slow:**
- AI video generation takes 30-60 seconds
- This is normal! Be patient 😊

**If you get an error:**
- Check your Replicate credits: https://replicate.com/account/billing
- Make sure the API key is correct
