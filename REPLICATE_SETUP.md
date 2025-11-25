# Replicate AI Video Generation Setup

## 🎬 What is Replicate?
Replicate lets you run AI models (like SORA-style video generation) via API.
- **Similar to SORA** but actually available!
- **$5 FREE credits** = ~500 short videos
- **Fast**: 30-60 seconds per video
- **Custom videos**: Generate ANY scene from text!

## 📝 Setup Steps:

### 1. Sign Up for Replicate
1. Go to: **https://replicate.com/**
2. Click "Sign Up" (free account)
3. Verify your email

### 2. Get Your API Token
1. Go to: **https://replicate.com/account/api-tokens**
2. Click "Create Token"
3. Copy your API token (starts with `r8_...`)

### 3. Add API Token to Environment

**Option A: Environment Variable (Recommended)**
```bash
export REPLICATE_API_TOKEN="r8_your_token_here"
```

**Option B: Add to your shell profile**
Add to `~/.zshrc` or `~/.bashrc`:
```bash
export REPLICATE_API_TOKEN="r8_your_token_here"
```

Then reload:
```bash
source ~/.zshrc
```

### 4. Restart the Server
```bash
# Stop the server (Ctrl+C)
# Then restart:
venv/bin/uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## 🎯 How It Works:

### Before (Search-based):
- Input: "Hanuman bringing Sanjeevani"
- Output: Random unrelated videos from Tenor

### After (AI-generated):
- Input: "Hanuman bringing Sanjeevani herb from mountain"
- Output: **CUSTOM AI-generated video** of that exact scene!

## 💰 Pricing:

- **Free Tier**: $5 credit (no credit card needed!)
- **Cost per video**: ~$0.01 (AnimateDiff model)
- **Total free videos**: ~500 videos!

## 🎨 Example Prompts:

1. **"White husky dog dancing happily"**
   → AI generates a custom video of a husky dancing!

2. **"Hanuman flying with mountain in hand"**
   → AI generates mythological scene!

3. **"Programmer debugging code at 3 AM"**
   → AI generates coding meme video!

## ⚙️ Models Available:

1. **AnimateDiff** (Current)
   - Fast (30-60s)
   - Cheap ($0.01/video)
   - Good quality

2. **Zeroscope V2 XL** (Alternative)
   - Slower (2-3 min)
   - More expensive ($0.05/video)
   - Better quality

## 🚀 Ready to Test!

Once you've added your API token and restarted the server:
1. Go to AI Meme tab
2. Select "Short Video"
3. Enter: "cat playing piano"
4. Generate!

You'll get a **custom AI-generated video** of a cat playing piano! 🎹🐱

## 📊 Check Your Usage:
https://replicate.com/account/billing

## ❓ Troubleshooting:

**Error: "Replicate API key not configured"**
→ Make sure you exported the REPLICATE_API_TOKEN environment variable

**Error: "Insufficient credits"**
→ You've used your $5 free credit. Add payment method or wait for free tier reset.

**Slow generation**
→ AI video generation takes 30-60 seconds. Be patient!
