# Using Hugging Face Spaces for Free Video Generation

## ✅ NEW APPROACH: Gradio Client (No Token Needed!)

Instead of using the HF Inference API (which has deprecated endpoints), we now connect directly to **public Hugging Face Spaces** using the Gradio Client library.

### Advantages:
- ✅ **No HF token required!**
- ✅ Uses public, free Spaces
- ✅ More reliable than Inference API
- ✅ No setup needed - works out of the box
- ⚠️ May have queue times (shared resources)

### How It Works:

The system connects to public Spaces like:
- **KingNish/Instant-Video** - AnimateDiff-based instant video generation
- **Other public text-to-video Spaces** (can be configured)

These Spaces are hosted by the community and are completely free to use!

## Alternative: Run Models Locally

If you want **unlimited, faster generation**, you can run models locally on your Mac.

### Requirements:
- **Mac with Apple Silicon** (M1/M2/M3/M4) - Recommended
- **OR** NVIDIA GPU with 8GB+ VRAM
- **16GB+ RAM**

### Setup for Mac (Apple Silicon):

```bash
# Install PyTorch with MPS support
pip install torch torchvision

# Install diffusers and dependencies
pip install diffusers transformers accelerate

# Install for Apple Silicon optimization
pip install --upgrade --pre torch torchvision --index-url https://download.pytorch.org/whl/nightly/cpu
```

### Example Local Generation Code:

```python
from diffusers import DiffusionPipeline
import torch

# Load model (first time will download ~4GB)
pipe = DiffusionPipeline.from_pretrained(
    "damo-vilab/text-to-video-ms-1.7b",
    torch_dtype=torch.float16,
    variant="fp16"
)

# Use MPS (Metal Performance Shaders) on Mac
pipe.to("mps")

# Generate video
prompt = "A cat dancing in space"
video_frames = pipe(prompt, num_frames=16).frames

# Save
from diffusers.utils import export_to_video
export_to_video(video_frames, "output.mp4")
```

### Integration into Backend:

If you want to run locally, I can modify `backend/main.py` to:
1. Check if models are downloaded
2. Use local generation if available
3. Fall back to Spaces/Tenor if not

**Would you like me to implement local model support?**

## Current Flow:

1. **Replicate** (Paid, High Quality) ❌ *Requires credits*
2. **HF Spaces** (Free, Good Quality) ✅ **NEW - No token needed!**
3. **Tenor** (Free, Search-based) ✅ *Always works*
4. **Pexels** (Free, Stock video) ✅ *Fallback*

## Testing:

Try generating a video now! The system will:
1. Skip Replicate (no credits)
2. Connect to HF Space (may take 10-30s first time)
3. Generate a short video
4. Fall back to Tenor if Space is busy

**No configuration needed - just refresh and try!** 🚀
