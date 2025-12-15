# Add this to backend/main.py after the meme prompt generation endpoint

@app.post("/api/generate-gif-video")
async def generate_gif_video(request: dict):
    """
    Generate GIF or video memes using appropriate APIs
    """
    prompt = request.get("prompt", "")
    meme_type = request.get("meme_type", "gif")
    
    try:
        if meme_type == "gif":
            # Option 1: Use Giphy API to search for relevant GIFs
            # For demo, we'll use Giphy's public API
            import urllib.parse
            import httpx
            
            # Extract keywords from prompt
            keywords = " ".join(prompt.split()[:10])
            
            # Giphy Translate API - converts text to GIF
            giphy_api_key = "YOUR_GIPHY_API_KEY"  # Get free key from https://developers.giphy.com/
            
            # Using Giphy's public beta key for demonstration
            # IMPORTANT: Replace with your own key for production
            giphy_url = f"https://api.giphy.com/v1/gifs/translate?api_key={giphy_api_key}&s={urllib.parse.quote(keywords)}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(giphy_url, timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("data") and data["data"].get("images"):
                        gif_url = data["data"]["images"]["original"]["url"]
                        return {"url": gif_url, "type": "gif"}
            
            # Fallback: Return error if Giphy fails
            return {"error": "GIF generation requires Giphy API key", "type": "gif"}
            
        elif meme_type == "video":
            # For video generation, we can use:
            # 1. Stability AI Video API
            # 2. Replicate with free models
            # 3. Runway ML API
            
            # For now, return a message that video generation needs setup
            return {
                "error": "Video generation requires additional API setup (Replicate/Stability AI)",
                "type": "video",
                "message": "Please add your Replicate API key to enable video generation"
            }
        
        return {"error": "Invalid meme type", "type": meme_type}
        
    except Exception as e:
        print(f"Error in GIF/Video generation: {str(e)}")
        return {"error": str(e), "type": meme_type}
