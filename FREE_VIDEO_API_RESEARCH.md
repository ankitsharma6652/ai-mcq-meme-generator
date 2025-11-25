# Free Text-to-Video API Research

## Summary
After extensive research, **none of the popular "free" text-to-video services offer truly free public APIs** for developers.

## Services Investigated

### 1. **Adobe Express / Firefly**
- **Web Interface:** Free tier available
- **API Access:** Enterprise only, no free developer API
- **Firefly Video API:** In beta, requires Adobe enterprise account
- **Verdict:** ❌ Not suitable for free integration

### 2. **Renderforest**
- **Web Interface:** Free tier with watermarks
- **API Access:** Has API but pricing not disclosed, likely paid
- **Documentation:** NodeJS and PHP SDKs available
- **Verdict:** ❌ No confirmed free API tier

### 3. **Pictory.ai**
- **Web Interface:** Free trial available
- **API Access:** No public API found
- **Verdict:** ❌ No API available

### 4. **Kapwing**
- **Web Interface:** Free tier (5 TTS minutes/month)
- **API Access:** Limited to transcription API and plugin system
- **Video Generation API:** Not publicly available
- **Verdict:** ❌ No text-to-video API for developers

## Current Solution

Since free text-to-video APIs are not available, the system uses:

1. **Replicate** (Paid) - Tries first if API key is configured
2. **Hugging Face** (Free but unreliable) - Tries if HF_TOKEN is set
3. **Tenor** (Free, Reliable) - **Primary fallback** for GIFs and MP4 videos
4. **Pexels** (Free, Reliable) - Stock video search fallback

## Recommendation

**Use Tenor as the primary source** for meme videos. It's:
- ✅ Completely free
- ✅ No API limits for reasonable use
- ✅ Large library of GIFs and short videos
- ✅ Perfect for meme content
- ✅ Reliable and fast

The system is now configured to skip static image fallbacks and always return moving videos from Tenor when AI generation fails.
