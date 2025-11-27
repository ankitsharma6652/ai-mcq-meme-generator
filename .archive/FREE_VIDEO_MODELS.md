# Free Open-Source Text-to-Video Models

## ✅ Currently Implemented: ModelScope Text-to-Video

**Model:** `damo-vilab/text-to-video-ms-1.7b`  
**Developer:** Alibaba DAMO Vision Intelligence Lab  
**Access:** Hugging Face Inference API (Free)

### Features:
- ✅ Completely free via HF Inference API
- ✅ No local GPU required
- ✅ Generates 2-4 second videos
- ✅ Good frame consistency
- ⚠️ Resolution: 256x256 (optimized for speed)
- ⚠️ May have 20-60s queue time (cold start)

### How to Use:
1. Get a free HF token from https://huggingface.co/settings/tokens
2. Set `HF_TOKEN` in `start_server.sh`
3. Restart the server
4. Generate videos!

---

## 🔄 Alternative Free Models

You can switch to these models by editing `backend/main.py` (line ~595):

### 1. AnimateDiff-Lightning
```python
API_URL = "https://api-inference.huggingface.co/models/ByteDance/AnimateDiff-Lightning"
```
- **Speed:** Very fast (4-step generation)
- **Quality:** Good for animations
- **Best for:** Animated memes, motion graphics

### 2. Text2Video-Zero
```python
API_URL = "https://api-inference.huggingface.co/models/damo-vilab/text-to-video-ms-zero"
```
- **Speed:** Medium
- **Quality:** Zero-shot (no training data needed)
- **Best for:** Experimental/creative videos

### 3. Zeroscope v2
```python
API_URL = "https://api-inference.huggingface.co/models/cerspense/zeroscope_v2_576w"
```
- **Speed:** Slower
- **Quality:** Higher resolution (576x320)
- **Best for:** Better quality videos (if you can wait)

### 4. HunyuanVideo (Tencent)
```python
API_URL = "https://api-inference.huggingface.co/models/tencent/HunyuanVideo"
```
- **Speed:** Slow
- **Quality:** Very high
- **Best for:** Production-quality videos
- ⚠️ May not be available on free tier

---

## 🖥️ Running Models Locally (Advanced)

If you have a powerful GPU (8GB+ VRAM), you can run these models locally for unlimited use:

### Setup:
```bash
pip install diffusers transformers accelerate torch
```

### Example Code:
```python
from diffusers import DiffusionPipeline
import torch

# Load model
pipe = DiffusionPipeline.from_pretrained(
    "damo-vilab/text-to-video-ms-1.7b",
    torch_dtype=torch.float16
)
pipe.to("cuda")

# Generate video
prompt = "A cat dancing in space"
video_frames = pipe(prompt, num_frames=16).frames

# Save video
from diffusers.utils import export_to_video
export_to_video(video_frames, "output.mp4")
```

### Requirements:
- **GPU:** NVIDIA with 8GB+ VRAM (RTX 3060 or better)
- **RAM:** 16GB+ system RAM
- **Storage:** 10GB+ for model weights
- **Time:** 30-120 seconds per video (depending on GPU)

---

## 📊 Model Comparison

| Model | Speed | Quality | Resolution | Free API | Local GPU |
|-------|-------|---------|------------|----------|-----------|
| **ModelScope** | ⭐⭐⭐ | ⭐⭐⭐ | 256x256 | ✅ | 8GB+ |
| **AnimateDiff** | ⭐⭐⭐⭐ | ⭐⭐⭐ | 512x512 | ✅ | 10GB+ |
| **Zeroscope** | ⭐⭐ | ⭐⭐⭐⭐ | 576x320 | ✅ | 12GB+ |
| **HunyuanVideo** | ⭐ | ⭐⭐⭐⭐⭐ | 720p | ⚠️ | 16GB+ |
| **Text2Video-Zero** | ⭐⭐⭐ | ⭐⭐ | 512x512 | ✅ | 8GB+ |

---

## 🎯 Recommendations

**For this project (Meme Generator):**
- ✅ **Use ModelScope** (currently implemented) - Best balance of speed/quality for free tier
- ✅ **Fallback to Tenor** - Always works, huge meme library

**If you have a GPU:**
- Run ModelScope locally for unlimited generation
- No API rate limits
- Faster generation (if GPU is good)

**If you want better quality:**
- Use Replicate (paid but cheap: ~$0.01 per video)
- Or wait for Zeroscope on HF (slower but free)

---

## 🔧 Troubleshooting

**503 Service Unavailable:**
- Model is "cold starting" on HF servers
- Wait 30-60 seconds and retry
- Normal for free tier

**Rate Limit Exceeded:**
- Free tier: ~100 requests/hour
- Wait a few minutes
- Consider HF Pro ($9/month) for unlimited

**Poor Video Quality:**
- ModelScope is optimized for speed (256x256)
- For better quality, use Replicate or run locally
- Or switch to Zeroscope (edit `backend/main.py`)

**Video Not Playing:**
- Check browser console for errors
- Ensure video file was saved (check `frontend/` folder)
- Try refreshing the page
