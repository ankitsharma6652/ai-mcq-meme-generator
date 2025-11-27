# Free AI Video Generation with Hugging Face

You can use Hugging Face's **free Inference API** to generate videos using open-source models like **ModelScope Text-to-Video**.

## 1. Get a Free Hugging Face Token

1.  Go to [Hugging Face Settings > Tokens](https://huggingface.co/settings/tokens).
2.  Click **"Create new token"**.
3.  Name it (e.g., "MemeGen").
4.  Select **"Read"** permissions.
5.  Click **"Create token"** and copy it (starts with `hf_...`).

## 2. Configure the Server

You need to set the `HF_TOKEN` environment variable.

### Option A: Edit `start_server.sh` (Recommended)

Open `start_server.sh` and replace the placeholder:

```bash
export HF_TOKEN="hf_your_actual_token_here"
```

### Option B: Run manually

```bash
export HF_TOKEN="hf_your_actual_token_here"
./start_server.sh
```

## 3. Restart the Server

After setting the token, restart the server for changes to take effect.

## How it Works

The system now uses **ModelScope Text-to-Video** (by Alibaba DAMO Vision Intelligence Lab):
- ✅ **Completely free** via Hugging Face Inference API
- ✅ **No local GPU required** - runs on HF's servers
- ✅ **Open-source model** - `damo-vilab/text-to-video-ms-1.7b`
- ⚠️ **May have queue times** on free tier (model loading ~20-60s)
- ⚠️ **Rate limited** but generous for personal use

### Video Generation Flow:
1.  **Replicate** (High Quality, Paid) ❌ *Requires credits*
2.  **Hugging Face ModelScope** (Good Quality, Free) ✅ **NEW!**
3.  **Tenor** (Search, Free) ✅ *Fallback*
4.  **Pexels** (Stock Video, Free) ✅ *Fallback*

## Alternative Models

You can also try these free models by changing the `API_URL` in `backend/main.py`:

- **AnimateDiff-Lightning:** `guoyww/animatediff-lightning-4step`
- **Text2Video-Zero:** `damo-vilab/text-to-video-zero`
- **Zeroscope:** `cerspense/zeroscope_v2_576w`

## Troubleshooting

**503 Error (Model Loading):**
- The model is "cold starting" on HF servers
- Wait 20-60 seconds and try again
- This is normal for free tier

**Rate Limit:**
- Free tier has generous limits
- If you hit limits, wait a few minutes
- Consider upgrading to HF Pro for faster inference

**Video Quality:**
- ModelScope generates 2-4 second videos
- Resolution: 256x256 (optimized for speed)
- For higher quality, use Replicate (paid)
