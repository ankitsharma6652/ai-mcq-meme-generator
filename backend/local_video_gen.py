"""
Local AI Video Generation using ModelScope on Apple Silicon
"""
import os
import torch
import time
from typing import Optional

# Global variable to cache the pipeline
_pipeline = None
_model_loaded = False

def is_local_generation_available() -> bool:
    """Check if local generation is available (Mac with MPS)"""
    try:
        # Check if we're on Mac with Apple Silicon (MPS backend)
        return torch.backends.mps.is_available()
    except:
        return False

def get_model_path() -> str:
    """Get the path where models are cached"""
    return os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "diffusers")

def is_model_downloaded() -> bool:
    """Check if ModelScope model is already downloaded"""
    model_path = get_model_path()
    model_dir = os.path.join(model_path, "models--damo-vilab--text-to-video-ms-1.7b")
    return os.path.exists(model_dir)

def load_pipeline():
    """Load the text-to-video pipeline (cached after first load)"""
    global _pipeline, _model_loaded
    
    if _pipeline is not None:
        return _pipeline
    
    print("🔄 Loading ModelScope text-to-video model...")
    print("⏳ First time: This will download ~4GB (one-time only)")
    
    try:
        from diffusers import DiffusionPipeline
        
        # Load ModelScope Text-to-Video
        _pipeline = DiffusionPipeline.from_pretrained(
            "damo-vilab/text-to-video-ms-1.7b",
            torch_dtype=torch.float32,  # Use float32 for CPU
        )
        
        # Use CPU for more stable generation (MPS has NaN issues)
        # CPU is slower but produces valid frames
        _pipeline.to("cpu")
        
        # Enable memory optimizations
        _pipeline.enable_attention_slicing()
        
        _model_loaded = True
        print("✅ Model loaded successfully (using CPU for stability)!")
        return _pipeline
        
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        _model_loaded = False
        return None

def generate_video(prompt: str, output_path: str, num_frames: int = 16) -> Optional[str]:
    """
    Generate a video from text prompt using local model
    
    Args:
        prompt: Text description of the video
        output_path: Where to save the video file
        num_frames: Number of frames to generate (default: 16 = ~2 seconds)
    
    Returns:
        Path to generated video, or None if failed
    """
    try:
        # Load pipeline (cached after first call)
        pipe = load_pipeline()
        if pipe is None:
            return None
        
        print(f"🎬 Generating video: {prompt[:50]}...")
        start_time = time.time()
        
        # Generate video frames
        # Note: First generation is slower (~30s), subsequent ones are faster (~10-15s)
        video_frames = pipe(
            prompt,
            num_inference_steps=25,  # Lower = faster but lower quality
            num_frames=num_frames,
            height=256,  # ModelScope default
            width=256,
        ).frames
        
        # video_frames is a list of lists of PIL Images
        # We need to convert to video file
        frames = video_frames[0]  # Get first (and only) video
        
        # Save as MP4 using imageio
        import imageio
        import numpy as np
        
        # Convert PIL images to numpy arrays and handle NaN values from MPS
        frame_arrays = []
        for frame in frames:
            arr = np.array(frame, dtype=np.float32)
            # Replace NaN with 0 (black) - MPS sometimes produces NaN
            arr = np.nan_to_num(arr, nan=0.0, posinf=255.0, neginf=0.0)
            # Clip to valid range
            arr = np.clip(arr, 0, 255)
            # Convert to uint8
            arr = arr.astype(np.uint8)
            frame_arrays.append(arr)
        
        # Save as video (8 fps for smooth playback)
        imageio.mimsave(output_path, frame_arrays, fps=8, codec='libx264')
        
        elapsed = time.time() - start_time
        print(f"✅ Video generated in {elapsed:.1f}s: {output_path}")
        
        return output_path
        
    except Exception as e:
        print(f"❌ Local generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_status() -> dict:
    """Get status of local generation capability"""
    return {
        "available": is_local_generation_available(),
        "model_downloaded": is_model_downloaded(),
        "model_loaded": _model_loaded,
        "device": "mps" if is_local_generation_available() else "none"
    }
