# 🎬 AI Video Generation - Complete Setup Guide

## ✅ **Current Implementation: Hybrid 4-Tier System**

Your app now uses a smart fallback system that prioritizes free, quality options:

### **Tier 1: Local Model (Development - Your Mac M3)**
- ✅ **FREE** - Unlimited generation
- ✅ **FAST** - 10-20 seconds per video
- ✅ **QUALITY** - AI-generated, custom videos
- ✅ **OFFLINE** - No API needed
- ⚠️ **Only works on your Mac** (Apple Silicon)

### **Tier 2: Custom Hosted Model (Production - Optional)**
- ✅ **FREE for users** - You host it
- ✅ **QUALITY** - Same AI model as local
- ✅ **SCALABLE** - Handles multiple users
- 💰 **Cost:** $0-18/month (HF Spaces) or $5-20/month (Modal)

### **Tier 3: Replicate API (Backup)**
- ⚠️ **PAID** - ~$0.01 per video
- ✅ **HIGH QUALITY** - Best results
- ✅ **RELIABLE** - Always available
- 💰 **Cost:** Pay per use

### **Tier 4: Tenor Search (Ultimate Fallback)**
- ✅ **FREE** - Always available
- ✅ **FAST** - Instant results
- ⚠️ **SEARCH-BASED** - Not custom AI
- ✅ **RELIABLE** - Never fails

---

## 🚀 **Quick Start**

### **For Development (Your Mac):**

1. **Refresh your browser** - Local model is ready!
2. **Generate a video** - First time will download model (~4GB, one-time)
3. **Wait ~30s** for first video (subsequent: ~10-15s)
4. **Enjoy unlimited free AI videos!**

### **For Production:**

**Option A: Use Replicate (Easiest)**
- Already configured
- Just add credits to your Replicate account
- Cost: ~$0.01/video

**Option B: Host Your Own Model (Best for users)**
- Follow `HOSTING_YOUR_MODEL.md`
- Create HF Space or Modal endpoint
- Set `CUSTOM_VIDEO_ENDPOINT` in `start_server.sh`
- Users get FREE AI videos!

---

## 📊 **Cost Comparison**

| Scenario | Solution | Cost/Month | Quality |
|----------|----------|------------|---------|
| **Development** | Local (Mac M3) | $0 | ⭐⭐⭐⭐ |
| **Production (Low Traffic)** | HF Space Free | $0 | ⭐⭐⭐⭐ |
| **Production (Medium)** | HF Space Paid | $18 | ⭐⭐⭐⭐ |
| **Production (High)** | Modal Labs | $20-100 | ⭐⭐⭐⭐ |
| **Production (Premium)** | Replicate | $30-300 | ⭐⭐⭐⭐⭐ |
| **Always Available** | Tenor (Fallback) | $0 | ⭐⭐ |

---

## 🎯 **Recommended Setup**

### **Phase 1: Development (Now)**
```bash
# You're all set! Just generate videos on your Mac
# Local model will download automatically on first use
```

### **Phase 2: MVP/Testing**
```bash
# Use Tenor for all users (free, reliable)
# Test with small Replicate credits
```

### **Phase 3: Production**
```bash
# Create your own HF Space (see HOSTING_YOUR_MODEL.md)
# Set CUSTOM_VIDEO_ENDPOINT
# Users get free AI videos!
# Replicate as backup
# Tenor as ultimate fallback
```

---

## 🔧 **Configuration**

### **Environment Variables:**

```bash
# Local Development (Mac M3)
# No configuration needed - auto-detected!

# Custom Hosted Model (Optional)
export CUSTOM_VIDEO_ENDPOINT="https://your-space.hf.space/api/predict"

# Replicate API (Backup)
export REPLICATE_API_TOKEN="r8_your_token_here"
```

---

## 📝 **Testing Local Generation**

1. **Start the server** (already running)
2. **Open browser** and refresh
3. **Generate a video meme**
4. **Check console logs** - you'll see:
   ```
   🖥️ Local generation available (Apple Silicon detected)
   🎬 Attempting local AI video generation...
   🔄 Loading ModelScope text-to-video model...
   ⏳ First time: This will download ~4GB (one-time only)
   ...
   ✅ Local AI video generated: /local_video_xxx.mp4
   ```

5. **First generation:** ~30-60 seconds (downloads model)
6. **Subsequent:** ~10-20 seconds

---

## 🐛 **Troubleshooting**

### **Local generation not working?**
```bash
# Check if MPS is available
python3 -c "import torch; print(torch.backends.mps.is_available())"
# Should print: True
```

### **Model download slow?**
- Normal! ~4GB download on first use
- Cached in `~/.cache/huggingface/diffusers`
- Only happens once

### **Out of memory?**
- Close other apps
- M3 Pro has enough RAM (18GB+)
- Model uses ~8GB

### **Want to skip local and test fallback?**
- Temporarily rename `backend/local_video_gen.py`
- Will skip to next tier (Replicate/Tenor)

---

## 🎉 **Summary**

You now have:
- ✅ **Local AI generation** on your Mac M3 (FREE, unlimited)
- ✅ **Custom hosted model** support (for production)
- ✅ **Replicate backup** (high quality, paid)
- ✅ **Tenor fallback** (always works, free)
- ✅ **Smart auto-detection** (uses best available option)

**For your users in production:** Host your own model on HF Spaces = **FREE, QUALITY AI videos!** 🚀
