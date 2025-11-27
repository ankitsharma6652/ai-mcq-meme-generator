# Hosting Your Own Free AI Video Model

## 🎯 **Best Solution: Your Own Hugging Face Space**

This gives your users **free, quality AI videos** without you paying per-video costs!

## 📋 **Setup Guide**

### **Step 1: Create a Hugging Face Account**
1. Go to https://huggingface.co/join
2. Sign up (free)

### **Step 2: Create a New Space**
1. Go to https://huggingface.co/new-space
2. **Name:** `your-username/meme-video-generator`
3. **SDK:** Select **Gradio**
4. **Hardware:** Select **CPU Basic** (free) or **T4 Small** ($0.60/hr)
5. Click **Create Space**

### **Step 3: Add Your Model Code**

Create `app.py` in your Space:

```python
import gradio as gr
import torch
from diffusers import DiffusionPipeline
import numpy as np
import imageio

# Load model (cached after first run)
pipe = DiffusionPipeline.from_pretrained(
    "damo-vilab/text-to-video-ms-1.7b",
    torch_dtype=torch.float16,
    variant="fp16"
)

# Use GPU if available
device = "cuda" if torch.cuda.is_available() else "cpu"
pipe.to(device)
pipe.enable_attention_slicing()

def generate_video(prompt):
    """Generate video from text prompt"""
    # Generate frames
    video_frames = pipe(
        prompt,
        num_inference_steps=25,
        num_frames=16,
        height=256,
        width=256,
    ).frames[0]
    
    # Convert to numpy arrays
    frames = [np.array(frame) for frame in video_frames]
    
    # Save as video
    output_path = "output.mp4"
    imageio.mimsave(output_path, frames, fps=8, codec='libx264')
    
    return output_path

# Create Gradio interface
demo = gr.Interface(
    fn=generate_video,
    inputs=gr.Textbox(label="Video Prompt", placeholder="A cat dancing in space"),
    outputs=gr.Video(label="Generated Video"),
    title="Free AI Meme Video Generator",
    description="Generate short videos from text using ModelScope"
)

if __name__ == "__main__":
    demo.launch()
```

### **Step 4: Add Requirements**

Create `requirements.txt`:

```
diffusers
transformers
accelerate
torch
imageio
imageio-ffmpeg
gradio
```

### **Step 5: Configure Your App**

In `start_server.sh`, add:

```bash
export CUSTOM_VIDEO_ENDPOINT="https://your-username-meme-video-generator.hf.space/api/predict"
```

Replace `your-username` with your actual HF username.

---

## 💰 **Cost Comparison**

| Solution | Cost/Video | Cost/1000 Videos | Quality | Speed |
|----------|-----------|------------------|---------|-------|
| **Your HF Space (Free)** | $0 | $0 | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Your HF Space (Paid)** | ~$0.001 | ~$1 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Replicate** | ~$0.01 | ~$10 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Tenor Search** | $0 | $0 | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🚀 **Production Flow**

With your own Space:

```
User Request
    ↓
1. Try Local Model (if dev on Mac) ✅ FREE
    ↓ (if not local)
2. Try YOUR HF Space ✅ FREE for users!
    ↓ (if Space busy)
3. Try Replicate (backup) ⚠️ Costs you money
    ↓ (if no credits)
4. Tenor Search ✅ FREE fallback
```

---

## 📊 **Free Tier Limits**

**HF Spaces Free GPU:**
- 48 hours/week of GPU time
- ~10-15 seconds per video
- **~10,000-15,000 videos/week FREE!**

**When to upgrade to paid ($18/month):**
- If you need 24/7 availability
- If you exceed free tier limits
- Still way cheaper than Replicate!

---

## 🔧 **Alternative: Modal Labs**

Even better for production:

```python
# modal_video_gen.py
import modal

stub = modal.Stub("video-generator")

@stub.function(
    gpu="T4",
    image=modal.Image.debian_slim().pip_install(
        "diffusers", "transformers", "torch", "imageio"
    )
)
def generate_video(prompt: str):
    from diffusers import DiffusionPipeline
    import imageio
    
    pipe = DiffusionPipeline.from_pretrained("damo-vilab/text-to-video-ms-1.7b")
    pipe.to("cuda")
    
    frames = pipe(prompt, num_frames=16).frames[0]
    imageio.mimsave("output.mp4", frames, fps=8)
    
    return "output.mp4"

@stub.webhook(method="POST")
def api(data: dict):
    prompt = data.get("prompt")
    video_path = generate_video.call(prompt)
    return {"url": video_path}
```

**Modal Costs:**
- Pay only when generating: ~$0.0001/second
- ~$0.001-0.002 per video
- **10x cheaper than Replicate!**

---

## ✅ **Recommendation**

**For your production app:**

1. **Start with:** Your own HF Space (free tier)
2. **Upgrade to:** Modal Labs when you scale ($5-20/month)
3. **Keep:** Tenor as ultimate fallback (always free)

**This gives users FREE, QUALITY videos!** 🎉
