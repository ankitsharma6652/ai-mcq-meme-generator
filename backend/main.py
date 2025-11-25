from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
from typing import List, Optional
from datetime import timedelta
import os
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
import io
import docx
import json
import time
import random
import httpx
import urllib.parse
import replicate
import shutil
import uuid
from groq import Groq
from dotenv import load_dotenv
from gradio_client import Client

# Import new modules
# Import new modules
import models, schemas, database
from auth import core as auth
import category_endpoints

# Load environment variables from parent directory
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path)

# Initialize Database Tables
models.Base.metadata.create_all(bind=database.engine)

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI()

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- SECURITY & PRODUCTION CONFIG ---
# ... (Existing Security Config) ...

# 1. Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 2. Trusted Host Middleware (Prevent Host Header Attacks)
# In production, set ALLOWED_HOSTS to your domain (e.g., ["example.com", "*.example.com"])
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=ALLOWED_HOSTS
)

# 3. CORS (Restrict in production)
# In production, replace ["*"] with specific origins
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(category_endpoints.router)

# Superuser Configuration
SUPERUSER_EMAILS = [
    "digitalaks9@gmail.com",
    "ankitcoolji@gmail.com"
]


def populate_superusers(db: Session):
    """Set is_superuser=True for admin emails"""
    for email in SUPERUSER_EMAILS:
        normalized_email = email.lower().strip()
        user = db.query(models.User).filter(models.User.email == normalized_email).first()
        if user:
            if not user.is_superuser:
                print(f"Promoting user to superuser: {normalized_email}")
                user.is_superuser = True
                db.add(user)
    db.commit()

# 4. Health Check Endpoint (For Load Balancers/Docker)
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.on_event("startup")
async def startup_event():
    # Create tables
    models.Base.metadata.create_all(bind=database.engine)
    
    # Populate superusers
    db = database.SessionLocal()
    try:
        populate_superusers(db)
    finally:
        db.close()

    print("--> STARTUP: Listing all registered routes:")
    for route in app.routes:
        if hasattr(route, "methods"):
            print(f"   Route: {route.path} [{','.join(route.methods)}]")
        else:
            print(f"   Route: {route.path} (Mount)")

# --- OAUTH ROUTES (from separate file) ---
try:
    from auth.oauth_routes import router as oauth_router
    app.include_router(oauth_router)
except ImportError as e:
    print(f"Warning: OAuth routes not loaded: {e}")

# --- AUTHENTICATION ROUTES ---

@app.post("/api/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = auth.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return auth.create_user(db=db, user=user)

@app.post("/api/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.get_user_by_email(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Log Login Activity
    log_activity(db, user.id, "login", {"ip": "unknown"}) # In real app, get IP from request
    
    
    return {"access_token": access_token, "token_type": "bearer"}

# Helper to get current user from token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    from jose import JWTError, jwt
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = auth.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

@app.get("/api/profile")
def get_user_profile(current_user: models.User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "phone_number": current_user.phone_number,
        "profile_picture": current_user.profile_picture,
        "bio": current_user.bio,
        "designation": current_user.designation,
        "nature_of_work": current_user.nature_of_work,
        "company_name": current_user.company_name,
        "linkedin_url": current_user.linkedin_url,
        "twitter_url": current_user.twitter_url,
        "github_url": current_user.github_url,
        "website_url": current_user.website_url,
        "created_at": current_user.created_at
    }

@app.get("/api/is-superuser")
def check_superuser(current_user: models.User = Depends(get_current_user)):
    """Check if current user is a superuser"""
    return {
        "is_superuser": current_user.is_superuser,
        "email": current_user.email
    }

@app.put("/api/profile")
def update_user_profile(
    profile: schemas.UserProfileUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print(f"DEBUG: Received profile update: {profile.dict()}")
    # Update only provided fields
    if profile.full_name is not None:
        current_user.full_name = profile.full_name
    if profile.phone_number is not None:
        current_user.phone_number = profile.phone_number
    if profile.profile_picture is not None:
        current_user.profile_picture = profile.profile_picture
    if profile.bio is not None:
        current_user.bio = profile.bio
    if profile.designation is not None:
        current_user.designation = profile.designation
    if profile.nature_of_work is not None:
        current_user.nature_of_work = profile.nature_of_work
    if profile.company_name is not None:
        current_user.company_name = profile.company_name
    if profile.linkedin_url is not None:
        current_user.linkedin_url = profile.linkedin_url
    if profile.twitter_url is not None:
        current_user.twitter_url = profile.twitter_url
    if profile.github_url is not None:
        current_user.github_url = profile.github_url
    if profile.website_url is not None:
        current_user.website_url = profile.website_url
    
    db.commit()
    db.refresh(current_user)
    
    return {"message": "Profile updated successfully"}

# --- ACTIVITY LOGGING HELPER ---
def log_activity(db: Session, user_id: int, action: str, details: dict = None):
    try:
        activity = models.ActivityLog(
            user_id=user_id,
            action=action,
            details=details
        )
        db.add(activity)
        db.commit()
    except Exception as e:
        print(f"Failed to log activity: {e}")

# --- END AUTHENTICATION ---

# --- HELPER FUNCTIONS ---
def call_groq_with_fallback(messages, json_mode=False):
    """
    Calls Groq API with retries and model fallback.
    If one model is rate limited, it switches to the next.
    """
    # List of models to try in order
    models = [
        "llama-3.3-70b-versatile",
        "mixtral-8x7b-32768", 
        "gemma2-9b-it",
        "llama-3.1-8b-instant"
    ]
    
    last_error = None

    for model in models:
        # Try each model with retries
        for attempt in range(3):
            try:
                headers = {
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                }
                data = {
                    "messages": messages,
                    "model": model,
                    "temperature": 0.7
                }
                if json_mode:
                    data["response_format"] = {"type": "json_object"}

                response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
                response.raise_for_status()
                return response.json(), model
                
            except requests.exceptions.HTTPError as e:
                last_error = e
                if e.response.status_code == 429:
                    # Rate limit hit
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    print(f"Rate limit on {model} (Attempt {attempt+1}). Retrying in {delay:.2f}s...")
                    time.sleep(delay)
                    continue # Retry same model
                else:
                    # Other error, try next model immediately
                    print(f"Error on {model}: {str(e)}")
                    break 
            except Exception as e:
                last_error = e
                print(f"Unexpected error on {model}: {str(e)}")
                break
        
        # If we are here, the model failed 3 times or had non-429 error
        print(f"Switching from {model} to next model...")

    # If all models fail
    raise Exception(f"All AI models failed. Last error: {str(last_error)}")


# --- CONFIGURATION ---
# Get a free API key from: https://console.groq.com/keys
# Groq offers FREE, FAST inference with models like Llama and Mixtral
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
if not GROQ_API_KEY:
    print("⚠️  WARNING: GROQ_API_KEY not set in environment variables")
# ---------------------

# Duplicate app initialization removed

# Models
class LLMConfig(BaseModel):
    provider: str = "mock"  # mock, ollama, openai, custom
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None

class GenerateRequest(BaseModel):
    text: str
    num_questions: int = 10
    difficulty: str = "auto"
    content_type: str = "coding"
    include_explanation: bool = True
    llm_config: Optional[LLMConfig] = None

class URLRequest(BaseModel):
    url: str

class BookmarkRequest(BaseModel):
    content_type: str
    content_id: int
    content_index: Optional[int] = None
    content_data: Optional[dict] = None

# Utilities
def extract_text_from_pdf(file_content: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(file_content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

def extract_text_from_url(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        # Basic text extraction - can be improved
        paragraphs = soup.find_all('p')
        text = "\n".join([p.get_text() for p in paragraphs])
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching URL: {str(e)}")

# Mock MCQ Generator (Replace with AI Model later)
def generate_mock_mcqs(text: str, num: int, difficulty: str, c_type: str):
    questions = []
    for i in range(num):
        questions.append({
            "question": f"Sample Question {i+1} about {c_type} generated from text length {len(text)}",
            "options": {
                "a": "Option A",
                "b": "Option B",
                "c": "Option C",
                "d": "Option D"
            },
            "correct_option": "a",
            "explanation": "This is a sample explanation.",
            "difficulty": difficulty if difficulty != "auto" else "medium",
            "tags": ["sample", c_type]
        })
    return questions

def generate_with_huggingface(prompt: str, api_key: str, model: str):
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # HF Inference API often requires a specific prompt format for chat models
    # Qwen/DeepSeek usually work with standard chat templates or raw text
    # We'll use a simple prompt structure
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 2048,
            "temperature": 0.7,
            "return_full_text": False
        }
    }

    response = requests.post(api_url, headers=headers, json=payload)
    response.raise_for_status()
    result = response.json()
    
    # HF returns a list of dicts, usually [{'generated_text': '...'}]
    if isinstance(result, list) and len(result) > 0:
        return result[0].get("generated_text", "")
    elif isinstance(result, dict) and "generated_text" in result:
        return result["generated_text"]
    else:
        raise ValueError(f"Unexpected HF response: {result}")

# Global variable to cache the model to avoid reloading
local_model = None
local_tokenizer = None

def get_local_model(model_name: str):
    global local_model, local_tokenizer
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch

    if local_model is None:
        print(f"Loading local model: {model_name}...")
        try:
            local_tokenizer = AutoTokenizer.from_pretrained(model_name)
            local_model = AutoModelForCausalLM.from_pretrained(
                model_name, 
                torch_dtype=torch.float16, 
                device_map="auto",
                trust_remote_code=True
            )
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Failed to load model: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to load local model: {str(e)}")
    
    return local_model, local_tokenizer

def generate_with_local(prompt: str, model_name: str):
    model, tokenizer = get_local_model(model_name)
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant that outputs JSON."},
        {"role": "user", "content": prompt}
    ]
    
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    
    generated_ids = model.generate(
        model_inputs.input_ids,
        max_new_tokens=2048,
        temperature=0.7,
        do_sample=True
    )
    
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return response

def generate_mcqs_with_llm(text: str, num: int, difficulty: str, c_type: str, config: LLMConfig):
    prompt = f"""
    You are an expert tutor specializing in {c_type}.
    Goal: Generate {num} {difficulty} difficulty multiple choice questions based on the text below.
    
    CRITICAL INSTRUCTIONS:
    1. Output ONLY valid JSON. No markdown, no explanations outside JSON.
    2. Format: {{ "questions": [ {{ "question": "...", "options": {{ "a": "...", "b": "...", "c": "...", "d": "..." }}, "correct_option": "a", "explanation": "...", "difficulty": "...", "tags": ["..."] }} ] }}
    3. For CODING questions: Include code snippets using triple backticks with language (```python, ```javascript, etc.)
    4. For MATH questions: Show COMPLETE step-by-step calculations in the explanation:
       - Step 1: [show calculation]
       - Step 2: [show calculation]
       - Final Answer: [result]
    5. For questions with formulas or calculations, show ALL intermediate steps clearly.
    
    Text Content:
    {text[:3000]}
    """

    try:
        content = ""
        used_model = "unknown"
        if config.provider == "huggingface":
            content = generate_with_huggingface(prompt, config.api_key, config.model)
            used_model = config.model
        elif config.provider == "local":
            # Use a default small model if none specified to avoid huge downloads
            model_name = config.model or "Qwen/Qwen2.5-Coder-1.5B-Instruct"
            content = generate_with_local(prompt, model_name)
            used_model = model_name
        else:
            # Use Groq/OpenAI with fallback
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ]
            result, used_model = call_groq_with_fallback(messages, json_mode=True)
            content = result['choices'][0]['message']['content']

        # Clean up markdown if present
        content = content.replace("```json", "").replace("```", "").strip()
        # Sometimes HF returns the prompt too, try to find the JSON start
        if "{" in content:
            content = content[content.find("{"):content.rfind("}")+1]
        
        import json
        try:
            data = json.loads(content)
            return data.get("questions", []), used_model
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {content}")
            return [], used_model
    except Exception as e:
        print(f"Error generating MCQs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class MemePromptRequest(BaseModel):
    topic: str
    count: int = 1
    meme_type: str = "image"  # image, gif, video

@app.post("/api/generate-meme-prompt")
def generate_meme_prompt(request: MemePromptRequest):
    """
    Generates creative prompts for memes (image/GIF/video) based on the topic using Groq.
    Returns a list of prompts and URLs.
    """
    
    # Different prompt templates based on meme type
    if request.meme_type == "gif":
        prompt_structure = """\"An animated GIF meme showing [describe animated scene]. The animation should loop showing [describe the funny action/reaction]. Include text overlay: '[INSERT SHORT TEXT HERE]' in bold, white font.\""""
        style_note = "Focus on simple, looping animations that are funny and relatable."
    elif request.meme_type == "video":
        prompt_structure = """\"A short video meme (3-5 seconds) showing [describe video scene]. The scene should show [describe the funny sequence]. Include text overlay: '[INSERT SHORT TEXT HERE]' in bold, white font.\""""
        style_note = "Focus on short, punchy video clips with clear visual humor."
    else:  # image
        prompt_structure = """\"A high-quality webcomic meme. [Describe scene]. [Describe characters]. A large, white speech bubble with the text '[INSERT SHORT TEXT HERE]' written clearly in a bold, black font.\""""
        style_note = "Use a clean, digital art style."
    
    system_prompt = f"""You are a professional meme creator. Your goal is to create {request.count} DISTINCT, funny, and visual meme concepts for {request.meme_type.upper()} format based on the user's topic.
    
    Output ONLY valid JSON containing a list of prompts.
    Format: {{ "prompts": ["prompt1", "prompt2", ...] }}
    
    Each prompt must follow this structure:
    {prompt_structure}
    
    Rules:
    1. Make each concept completely different.
    2. Make it funny and relatable to: "{request.topic}".
    3. CRITICAL: Keep the text overlay EXTREMELY SHORT (max 3-6 words). Long text will be unreadable.
    4. {style_note}
    5. Ensure the text is the main focus.
    6. MULTILINGUAL SUPPORT: 
       - If the user inputs Hindi (Devanagari script), translate and understand the meaning, then create relevant English meme concepts that match the Hindi context.
       - If the user uses "Hinglish" (Hindi in English script), understand the meaning and generate relevant memes.
       - Extract the CORE CONCEPT/EMOTION from any language and create universally relatable meme ideas.
       - For search purposes, always output prompts in English with universal humor themes.
    7. IMPORTANT: Focus on the EMOTION and SITUATION described, not just literal translation.
    """

    try:
        # Detect if input contains non-Latin characters (Hindi, etc.)
        has_non_latin = any(ord(char) > 127 for char in request.topic)
        
        topic_to_use = request.topic
        
        # If non-Latin text detected, ask AI to translate and extract search keywords
        if has_non_latin:
            print(f"🌐 Non-Latin text detected: {request.topic}")
            
            # Simple, direct translation prompt
            translation_prompt = f"""Translate this text to English and extract 3-5 simple search keywords for finding memes/GIFs.

Input: {request.topic}

Output ONLY JSON:
{{
  "english": "simple English translation",
  "keywords": ["keyword1", "keyword2", "keyword3"]
}}"""

            translation_messages = [
                {"role": "system", "content": "You are a translator. Output ONLY valid JSON."},
                {"role": "user", "content": translation_prompt}
            ]
            
            try:
                translation_result, _ = call_groq_with_fallback(translation_messages, json_mode=True)
                translation_content = translation_result['choices'][0]['message']['content'].strip()
                
                # Clean markdown
                translation_content = translation_content.replace("```json", "").replace("```", "").strip()
                
                translation_data = json.loads(translation_content)
                english_text = translation_data.get("english", request.topic)
                keywords = translation_data.get("keywords", [])
                
                # Use English translation for meme generation
                topic_to_use = english_text
                print(f"✅ Translated: {english_text}")
                print(f"🔍 Keywords: {keywords}")
                
            except Exception as e:
                print(f"❌ Translation failed: {e}")
                # Fallback: use original text
                topic_to_use = request.topic
        
        user_message = f"Create {request.count} {request.meme_type} meme concepts about: {topic_to_use}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # Use the new helper function
        result, used_model = call_groq_with_fallback(messages, json_mode=True)
        
        content = result['choices'][0]['message']['content'].strip()
        print(f"Raw Groq Response: {content}")

        # Clean markdown if present
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "")
        elif content.startswith("```"):
            content = content.replace("```", "")
            
        try:
            parsed = json.loads(content)
            prompts = parsed.get("prompts", [])
            if not prompts:
                # Try to find any list in the json
                for key, value in parsed.items():
                    if isinstance(value, list):
                        prompts = value
                        break
            
            if not prompts:
                # If still no prompts, just use the raw content as one prompt
                return {"prompts": [content], "model": used_model, "meme_type": request.meme_type}
                
            # Strict limit enforcement
            return {"prompts": prompts[:request.count], "model": used_model, "meme_type": request.meme_type}
        except json.JSONDecodeError:
            print("JSON Parse Error, falling back to raw text")
            # Fallback: treat the whole text as one prompt if parsing fails
            return {"prompts": [content], "model": used_model, "meme_type": request.meme_type}
    except Exception as e:
        print(f"Error generating meme prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-ai-video")
async def generate_ai_video(request: dict):
    """
    Generate AI videos using Replicate (text-to-video)
    This creates CUSTOM videos from text prompts using AI models
    """
    prompt = request.get("prompt", "")
    
    # Replicate API key - get from https://replicate.com/account/api-tokens
    replicate_api_key = os.environ.get("REPLICATE_API_TOKEN", "YOUR_REPLICATE_API_KEY")
    
    if replicate_api_key == "YOUR_REPLICATE_API_KEY":
        return {
            "error": "Replicate API key not configured",
            "message": "Please add REPLICATE_API_TOKEN to environment variables",
            "setup_url": "https://replicate.com/account/api-tokens"
        }
    
    try:
        print(f"🎬 Generating AI video for: '{prompt[:100]}'...")
        
        # Use AnimateDiff model (fast, good quality, cheap)
        # Alternative: zeroscope-v2-xl (better quality, slower, more expensive)
        output = replicate.run(
            "lucataco/animate-diff:beecf59c4aee8d81bf04f0381033dfa10dc16e845b4ae00d281e2fa377e48a9f",
            input={
                "prompt": prompt,
                "num_frames": 16,  # Short video
                "num_inference_steps": 25,  # Balance speed/quality
                "guidance_scale": 7.5
            }
        )
        
        # Output is a URL to the generated video
        if output:
            video_url = output if isinstance(output, str) else output[0]
            print(f"✅ AI video generated: {video_url[:50]}...")
            return {
                "url": video_url,
                "type": "video",
                "source": "replicate-ai",
                "format": "mp4",
                "note": "AI-generated custom video"
            }
        else:
            raise Exception("No output from Replicate")
            
    except Exception as e:
        print(f"❌ Replicate AI video error: {e}")
        return {
            "error": str(e),
            "type": "video",
            "message": "AI video generation failed. Falling back to search."
        }

@app.post("/api/generate-gif-video")
async def generate_gif_video(request: dict):
    """
    Generate GIF or video memes using appropriate free APIs
    Supports: GIF (via Tenor), Video (via Replicate/Stability AI)
    """
    import sys
    
    # Collect logs to return to frontend
    debug_logs = []
    def log(msg):
        print(msg, file=sys.stderr)
        debug_logs.append(msg)
    
    log(f"📨 RECEIVED REQUEST: {request}")
    
    prompt = request.get("prompt", "")
    meme_type = request.get("meme_type", "gif")
    index = request.get("index", 0)
    
    try:
        if meme_type == "gif":
            # ... (existing GIF logic) ...
            keywords = " ".join(prompt.split()[:8])
            tenor_url = f"https://tenor.googleapis.com/v2/search?q={urllib.parse.quote(keywords)}&key=AIzaSyAyimkuYQYF_FXVALexPuGQctUWRURdCYQ&limit=10&media_filter=gif"
            
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(tenor_url, timeout=10.0)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("results") and len(data["results"]) > 0:
                            result_index = index % len(data["results"])
                            gif_url = data["results"][result_index]["media_formats"]["gif"]["url"]
                            return {"url": gif_url, "type": "gif", "source": "tenor", "debug_logs": debug_logs}
                except Exception as e:
                    log(f"Tenor API error: {e}")
            
            return {
                "error": "GIF search failed",
                "type": "gif",
                "fallback_url": f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}",
                "debug_logs": debug_logs
            }
            
        elif meme_type == "video":
            log(f"🎥 Video generation request for: '{prompt}'")
            
            # HYBRID APPROACH: Try different methods based on environment
            # Priority 1: Local Model (Mac M3) - DISABLED (MPS compatibility issues)
            # Priority 2: Custom Hosted Model (if configured) - CHEAP
            # Priority 3: Replicate API (paid) - MODERATE
            # Priority 4: Tenor Search (free) - FALLBACK
            
            # OPTION 1: Try Local Model (TEMPORARILY DISABLED - MPS issues)
            # Uncomment when MPS compatibility is fixed or use CPU (slower)
            """
            try:
                from backend.local_video_gen import is_local_generation_available, generate_video
                
                if is_local_generation_available():
                    log(f"🖥️ Local generation available (Apple Silicon detected)")
                    log(f"🎬 Attempting local AI video generation...")
                    
                    # Generate unique filename
                    filename = f"local_video_{int(time.time())}_{index}.mp4"
                    filepath = os.path.join("frontend", filename)
                    
                    # Generate video locally
                    result_path = generate_video(prompt, filepath, num_frames=16)
                    
                    if result_path and os.path.exists(result_path):
                        video_url = f"/{filename}"
                        log(f"✅ Local AI video generated: {video_url}")
                        return {
                            "url": video_url,
                            "type": "video",
                            "source": "local-ai",
                            "format": "mp4",
                            "debug_logs": debug_logs
                        }
                    else:
                        log(f"⚠️ Local generation returned no result, trying next option...")
                        ai_error = "Local Gen Failed"
                else:
                    log(f"ℹ️ Local generation not available (not on Apple Silicon)")
            except Exception as e:
                log(f"⚠️ Local generation failed: {str(e)}")
                ai_error = "Local Gen Error"
            """
            log(f"ℹ️ Local AI generation disabled (use Tenor for fast results)")
            
            # OPTION 2: Try Custom Hosted Model (if endpoint configured)
            custom_endpoint = os.environ.get("CUSTOM_VIDEO_ENDPOINT", "")
            if custom_endpoint:
                log(f"🌐 Attempting custom hosted model: {custom_endpoint}")
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            custom_endpoint,
                            json={"prompt": prompt},
                            timeout=120.0
                        )
                        if response.status_code == 200:
                            data = response.json()
                            video_url = data.get("url")
                            if video_url:
                                log(f"✅ Custom model video generated: {video_url}")
                                return {
                                    "url": video_url,
                                    "type": "video",
                                    "source": "custom-hosted",
                                    "format": "mp4",
                                    "debug_logs": debug_logs
                                }
                except Exception as e:
                    log(f"⚠️ Custom hosted model failed: {str(e)}")
                    ai_error = "Custom Model Failed"
            
            # OPTION 3: Try Replicate (Paid, High Quality)
            replicate_api_key = os.environ.get("REPLICATE_API_TOKEN", "")
            ai_error = None # Reset ai_error for this section, or manage it differently
            
            if replicate_api_key:
                log(f"🔑 Replicate API Token found: {replicate_api_key[:5]}...")
            else:
                log(f"❌ No Replicate API Token found!")
                ai_error = "API Key Missing"
            
            if replicate_api_key and replicate_api_key != "YOUR_REPLICATE_API_KEY":
                log(f"🤖 Attempting AI video generation via Replicate...")
                try:
                    log(f"⏳ Calling Replicate run()...")
                    output = replicate.run(
                        "lucataco/animate-diff:beecf59c4aee8d81bf04f0381033dfa10dc16e845b4ae00d281e2fa377e48a9f",
                        input={
                            "prompt": prompt,
                            "num_frames": 16,
                            "num_inference_steps": 25,
                            "guidance_scale": 7.5
                        }
                    )
                    
                    log(f"📥 Replicate output: {output}")
                    
                    if output:
                        video_url = output if isinstance(output, str) else output[0]
                        log(f"✅ AI video generated successfully: {video_url}")
                        return {
                            "url": video_url,
                            "type": "video",
                            "source": "replicate-ai",
                            "format": "mp4",
                            "debug_logs": debug_logs
                        }
                except Exception as e:
                    error_msg = str(e)
                    log(f"⚠️ AI generation failed: {error_msg}")
                    log(f"⚠️ Falling back to search...")
                    
                    # Simplify error message for UI
                    if "402" in error_msg or "credit" in error_msg.lower():
                        ai_error = "Insufficient Credits"
                    elif "401" in error_msg:
                        ai_error = "Invalid API Key"
                    else:
                        ai_error = "AI Error"
            else:
                log(f"ℹ️ Replicate API key missing/invalid, skipping AI...")
                if not ai_error:
                    ai_error = "Replicate Key Missing"
            
            # OPTION 1.5: Try Hugging Face Spaces via Gradio Client (Free, No Token Needed!)
            log(f"🤖 Attempting AI video generation via Hugging Face Space...")
            try:
                from gradio_client import Client
                
                # Try multiple public Spaces (in order of reliability)
                spaces_to_try = [
                    ("multimodalart/stable-video-diffusion", "/video"),  # Stable Video Diffusion
                    ("fffiloni/text-to-video", "/predict"),  # Text to Video
                ]
                
                for space_url, api_name in spaces_to_try:
                    try:
                        log(f"🔗 Connecting to HF Space: {space_url}")
                        client = Client(space_url)
                        
                        # Shorten prompt to avoid issues
                        short_prompt = " ".join(prompt.split()[:15])
                        log(f"📝 Prompt: {short_prompt}")
                        
                        # Call the space's prediction endpoint
                        result = client.predict(
                            short_prompt,  # prompt
                            api_name=api_name
                        )
                        
                        log(f"📥 Received result from HF Space: {result}")
                        
                        # Result is usually a file path or URL
                        if result:
                            video_url = result
                            
                            # If it's a tuple/list, get the first element (usually the video path)
                            if isinstance(result, (tuple, list)):
                                video_url = result[0] if result else None
                            
                            if video_url and isinstance(video_url, str):
                                # If it's already a URL, use it directly
                                if video_url.startswith('http'):
                                    log(f"✅ HF Space video URL: {video_url}")
                                    return {
                                        "url": video_url,
                                        "type": "video",
                                        "source": "huggingface-space",
                                        "format": "mp4",
                                        "debug_logs": debug_logs
                                    }
                                # If it's a local file path, download it
                                elif os.path.exists(video_url):
                                    # Copy to frontend directory
                                    filename = f"hf_space_video_{int(time.time())}_{index}.mp4"
                                    filepath = os.path.join("frontend", filename)
                                    import shutil
                                    shutil.copy(video_url, filepath)
                                    local_url = f"/{filename}"
                                    log(f"✅ HF Space video saved: {local_url}")
                                    return {
                                        "url": local_url,
                                        "type": "video",
                                        "source": "huggingface-space",
                                        "format": "mp4",
                                        "debug_logs": debug_logs
                                    }
                        
                        # If we got here, this space worked but didn't return a valid result
                        # Try the next one
                        log(f"⚠️ Space {space_url} returned invalid result, trying next...")
                        
                    except Exception as space_error:
                        log(f"⚠️ Space {space_url} failed: {str(space_error)}")
                        continue  # Try next space
                
                # If all spaces failed
                raise Exception("All HF Spaces failed or are unavailable")
                    
            except Exception as e:
                error_msg = str(e)
                log(f"⚠️ HF Space generation failed: {error_msg}")
                ai_error = "HF Space Failed"
            
            # OPTION 2: Search-based (fallback)
            # Extract better search keywords
            stop_words = ['a', 'an', 'the', 'showing', 'video', 'meme', 'short', 'scene', 'clip', 'of', 'with', 'funny', 'hilarious']
            words = prompt.lower().split()
            keywords = ' '.join([w for w in words if w not in stop_words])[:50]
            
            if len(keywords) < 3:
                keywords = " ".join(prompt.split()[:5])
            
            log(f"🔍 Searching for: '{keywords}'")
            
            # PRIMARY: Try Tenor MP4 first (better for memes/funny content)
            tenor_video_url = f"https://tenor.googleapis.com/v2/search?q={urllib.parse.quote(keywords)}&key=AIzaSyAyimkuYQYF_FXVALexPuGQctUWRURdCYQ&limit=10&media_filter=mp4&contentfilter=medium"
            
            log(f"🔍 Trying Tenor MP4...")
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(tenor_video_url, timeout=10.0)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("results") and len(data["results"]) > 0:
                            result_index = index % len(data["results"])
                            video_url = data["results"][result_index]["media_formats"]["mp4"]["url"]
                            log(f"✅ Found Tenor video!")
                            
                            # Add note about AI failure if applicable
                            note = None
                            if ai_error:
                                note = f"AI Failed ({ai_error}). Showing related video."
                                
                            return {
                                "url": video_url,
                                "type": "video",
                                "source": "tenor",
                                "format": "mp4",
                                "debug_logs": debug_logs,
                                "note": note
                            }
                except Exception as e:
                    log(f"⚠️ Tenor error: {e}")
            
            # FALLBACK 1: Try Pexels (for professional stock videos)
            log(f"🔍 Trying Pexels...")
            pexels_api_key = "DEjFt9Y9dYdmOezDYNmuMmHWakmncsALlKrnVfh0jeTcXw5tViCm569z"
            pexels_video_url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(keywords)}&per_page=10&page=1"
            
            async with httpx.AsyncClient() as client:
                try:
                    headers = {"Authorization": pexels_api_key}
                    response = await client.get(pexels_video_url, headers=headers, timeout=10.0)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("videos") and len(data["videos"]) > 0:
                            result_index = index % len(data["videos"])
                            video_data = data["videos"][result_index]
                            video_files = video_data["video_files"]
                            
                            # Get smallest video for faster loading
                            video_url = None
                            for vf in sorted(video_files, key=lambda x: x.get('width', 9999)):
                                if vf.get("width") and vf.get("width") <= 640:
                                    video_url = vf["link"]
                                    break
                            
                            if not video_url and video_files:
                                video_url = video_files[0]["link"]
                            
                            if video_url:
                                log(f"✅ Found Pexels video!")
                                return {
                                    "url": video_url,
                                    "type": "video",
                                    "source": "pexels",
                                    "format": "mp4",
                                    "debug_logs": debug_logs
                                }
                except Exception as e:
                    log(f"⚠️ Pexels error: {e}")
            
            # FALLBACK 2: Tenor GIFs
            log(f"🔍 Trying Tenor GIFs...")
            fallback_gif_url = f"https://tenor.googleapis.com/v2/search?q={urllib.parse.quote(keywords)}&key=AIzaSyAyimkuYQYF_FXVALexPuGQctUWRURdCYQ&limit=10&media_filter=gif"
            
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(fallback_gif_url, timeout=10.0)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("results") and len(data["results"]) > 0:
                            result_index = index % len(data["results"])
                            gif_url = data["results"][result_index]["media_formats"]["gif"]["url"]
                            return {
                                "url": gif_url,
                                "type": "video",
                                "source": "tenor",
                                "format": "gif",
                                "note": "Showing animated GIF (video not found)"
                            }
                except Exception as e:
                    print(f"Tenor GIF fallback error: {e}")
            
            # Final fallback: Static image
            return {
                "error": "Video search failed. Try different keywords.",
                "type": "video",
                "fallback_url": f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt + ' cinematic')}?width=1280&height=720"
            }
        
        return {"error": "Invalid meme type", "type": meme_type}
        
    except Exception as e:
        print(f"Error in GIF/Video generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



class MemeRequest(BaseModel):
    question: str
    correct_option: str
    explanation: str
    llm_config: Optional[LLMConfig] = None

# ... (keep existing functions)

def generate_meme_caption_with_ai(question: str, explanation: str) -> str:
    """Generate a funny meme caption using AI"""
    prompt = f"""Generate a SHORT, FUNNY meme caption for this coding question.
    
Question: {question}
Explanation: {explanation}

Format: "TOP TEXT | BOTTOM TEXT"
Make it relatable to programmers. Keep each part under 50 characters.
Examples:
- "WHEN THE CODE WORKS | BUT YOU DON'T KNOW WHY"
- "STACKOVERFLOW | MY BEST FRIEND"
- "IT WORKS ON MY MACHINE | FAMOUS LAST WORDS"

Your caption:"""

    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are a witty programmer who creates funny meme captions."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.9,
            "max_tokens": 100
        }
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        caption = result["choices"][0]["message"]["content"].strip()
        
        # Clean up the caption
        caption = caption.replace('"', '').replace("'", '').strip()
        if '|' not in caption:
            # If AI didn't follow format, create a simple one
            caption = "CODING LIFE | NEVER BORING"
        
        return caption
    except Exception as e:
        print(f"Meme caption error: {e}")
        return "WHEN THE CODE WORKS | BUT YOU DON'T KNOW WHY"

from fastapi import BackgroundTasks

def prefetch_image(url: str):
    try:
        requests.get(url, timeout=5)
    except Exception as e:
        print(f"Failed to prefetch image: {e}")

@app.post("/api/generate-meme")
def generate_meme(request: MemeRequest, background_tasks: BackgroundTasks):
    # 1. Generate Caption using AI
    caption = generate_meme_caption_with_ai(request.question, request.explanation)
    
    # 2. Use Pollinations.ai for free image generation (no API key needed)
    # This generates meme-style images based on text prompts
    top_text, bottom_text = caption.split('|') if '|' in caption else (caption, "")
    top_text = top_text.strip()
    bottom_text = bottom_text.strip()
    
    # Generate a meme-appropriate image using Pollinations.ai
    # We'll use a simple meme template approach
    import urllib.parse
    
    # Create a prompt for a meme-style image
    meme_prompt = f"classic internet meme template, simple background, meme format"
    encoded_prompt = urllib.parse.quote(meme_prompt)
    
    # Pollinations.ai provides free image generation
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=600&nologo=true&seed={hash(caption) % 10000}"
    
    # Pre-fetch the image in background to warm up the cache
    background_tasks.add_task(prefetch_image, image_url)
    
    return {
        "caption": caption,
        "top_text": top_text,
        "bottom_text": bottom_text,
        "image_url": image_url
    }

# Endpoints
@app.post("/api/extract-url")
def extract_url(request: URLRequest):
    text = extract_text_from_url(request.url)
    return {"text": text}

@app.post("/api/extract-file")
async def extract_file(file: UploadFile = File(...)):
    content = await file.read()
    if file.filename.endswith('.pdf'):
        text = extract_text_from_pdf(content)
    elif file.filename.endswith('.txt') or file.filename.endswith('.md'):
        text = content.decode('utf-8')
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    return {"text": text}

# ---------------------
# Helper Functions for Analytics
# ---------------------

# Optional OAuth2 scheme
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# Helper function to get current user (optional - doesn't fail if not logged in)
def get_current_user_optional(
    token: str = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db)
):
    """Get current user if token exists, otherwise return None"""
    if not token:
        return None
    try:
        return get_current_user(token, db)
    except:
        return None

# ---------------------


@app.post("/api/generate-mcqs")
async def generate_mcqs(
    request: GenerateRequest, 
    req: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_optional)
):
    """Generate MCQs and save in normalized format"""
    import time
    start_time = time.time()
    
    # Override client config to use server-side credentials
    config = LLMConfig(
        provider="openai",
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
        model="llama-3.3-70b-versatile"
    )
    
    if config.api_key == "gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx":
        raise HTTPException(status_code=500, detail="Server Configuration Error: Please set the GROQ_API_KEY")

    try:
        # Generate MCQs
        questions, used_model = generate_mcqs_with_llm(
            request.text, 
            request.num_questions, 
            request.difficulty, 
            request.content_type, 
            config
        )
        
        generation_time = time.time() - start_time
        
        # Save to normalized database
        try:
            # 1. Create MCQ Generation record
            mcq_gen = models.MCQGeneration(
                user_id=current_user.id if current_user else None,
                input_type=request.input_type if hasattr(request, 'input_type') else 'paste_text',
                content_type=request.content_type,
                difficulty=request.difficulty,
                num_questions=request.num_questions,
                include_explanation=request.include_explanation if hasattr(request, 'include_explanation') else True,
                category=request.category if hasattr(request, 'category') else None,
                source_content=request.text[:5000] if request.text else None,
                source_url=request.source_url if hasattr(request, 'source_url') else None,
                source_filename=request.source_filename if hasattr(request, 'source_filename') else None,
                model_name=used_model,
                generation_time_seconds=generation_time,
                questions_data=[],  # Empty for normalized schema
                ip_address=req.client.host if req.client else None,
                user_agent=req.headers.get('user-agent', None)
            )
            db.add(mcq_gen)
            db.flush()  # Get the ID without committing
            
            # 2. Save each question as a separate row
            saved_questions = []
            for idx, q in enumerate(questions, 1):
                # Get options - check both uppercase and lowercase keys
                options = q.get('options', {})
                option_a = options.get('A') or options.get('a', '')
                option_b = options.get('B') or options.get('b', '')
                option_c = options.get('C') or options.get('c', '')
                option_d = options.get('D') or options.get('d', '')
                
                # Get correct answer - normalize to uppercase
                correct_ans = q.get('correct_answer') or q.get('correct_option', '')
                if isinstance(correct_ans, str):
                    correct_ans = correct_ans.upper()
                
                mcq_question = models.MCQQuestion(
                    generation_id=mcq_gen.id,
                    question_number=idx,
                    question_text=q.get('question', ''),
                    option_a=option_a,
                    option_b=option_b,
                    option_c=option_c,
                    option_d=option_d,
                    correct_answer=correct_ans,
                    explanation=q.get('explanation', ''),
                    times_attempted=0,
                    times_correct=0,
                    times_wrong=0
                )
                db.add(mcq_question)
                saved_questions.append(mcq_question)
            
            db.commit()
            db.refresh(mcq_gen)
            
            # Add IDs to the response
            for i, sq in enumerate(saved_questions):
                db.refresh(sq)
                questions[i]['id'] = sq.id
            
            # Return with generation ID for quiz tracking
            return {
                "questions": questions, 
                "model": used_model,
                "generation_id": mcq_gen.id
            }
        except Exception as db_error:
            print(f"Analytics save error: {db_error}")
            db.rollback()
            # Don't fail the request if analytics fails
            return {"questions": questions, "model": used_model}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Generation Failed: {str(e)}")


# ==================== ANALYTICS ENDPOINTS ====================

@app.post("/api/quiz-session")
async def submit_quiz_session(
    session: schemas.QuizSessionCreate,
    answers: List[schemas.QuestionAnswerCreate],
    req: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_optional)
):
    """Save quiz session with normalized answers"""
    try:
        # 1. Create quiz session
        quiz_session = models.QuizSession(
            user_id=current_user.id if current_user else None,
            mcq_generation_id=session.mcq_generation_id,
            total_questions=session.total_questions,
            questions_answered=session.questions_answered,
            correct_answers=session.correct_answers,
            wrong_answers=session.wrong_answers,
            score_percentage=session.score_percentage,
            started_at=session.started_at,
            completed_at=session.completed_at,
            time_taken_seconds=session.time_taken_seconds,
            is_completed=session.is_completed,
            content_type=session.content_type,
            difficulty=session.difficulty,
            input_type=session.input_type,
            device_type=session.device_type,
            ip_address=req.client.host if req.client else None,
            user_agent=req.headers.get('user-agent', None)
        )
        db.add(quiz_session)
        db.flush()
        
        # 2. Save each answer and update question statistics
        for ans in answers:
            # Save answer
            question_answer = models.QuestionAnswer(
                quiz_session_id=quiz_session.id,
                question_id=ans.question_id,
                user_answer=ans.user_answer,
                is_correct=ans.is_correct,
                time_spent_seconds=ans.time_spent_seconds
            )
            db.add(question_answer)
            
            # Update question statistics
            question = db.query(models.MCQQuestion).filter(
                models.MCQQuestion.id == ans.question_id
            ).first()
            
            if question:
                question.times_attempted += 1
                if ans.is_correct:
                    question.times_correct += 1
                else:
                    question.times_wrong += 1
                
                # Update average time
                if ans.time_spent_seconds:
                    if question.average_time_to_answer:
                        question.average_time_to_answer = (
                            (question.average_time_to_answer * (question.times_attempted - 1) + 
                             ans.time_spent_seconds) / question.times_attempted
                        )
                    else:
                        question.average_time_to_answer = ans.time_spent_seconds
        
        db.commit()
        db.refresh(quiz_session)
        
        return {"success": True, "session_id": quiz_session.id}
    except Exception as e:
        print(f"Quiz session save error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/meme-generation")
async def save_meme_generation(
    meme_gen: schemas.MemeGenerationCreate,
    req: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_optional)
):
    """Save meme generation with normalized memes"""
    try:
        # 1. Create meme generation record
        meme_generation = models.MemeGeneration(
            user_id=current_user.id if current_user else None,
            input_type=meme_gen.input_type,
            topic=meme_gen.topic,
            source_url=meme_gen.source_url,
            meme_type=meme_gen.meme_type,
            num_memes=meme_gen.num_memes,
            model_name=meme_gen.model_name,
            image_model=meme_gen.image_model,
            generation_time_seconds=meme_gen.generation_time_seconds,
            total_generated=meme_gen.total_generated,
            successful_generations=meme_gen.successful_generations,
            failed_generations=meme_gen.failed_generations,
            memes_data=[],  # Empty for normalized schema
            ip_address=req.client.host if req.client else None,
            user_agent=req.headers.get('user-agent', None)
        )
        db.add(meme_generation)
        db.flush()
        
        # 2. Save each meme as separate row
        for meme_data in meme_gen.memes_data:
            generated_meme = models.GeneratedMeme(
                generation_id=meme_generation.id,
                meme_url=meme_data.get('url', ''),
                meme_type=meme_data.get('type', meme_gen.meme_type),
                source=meme_data.get('source', ''),
                note=meme_data.get('note', ''),
                views=0,
                downloads=0
            )
            db.add(generated_meme)
        
        db.commit()
        db.refresh(meme_generation)
        
        return {"success": True, "generation_id": meme_generation.id}
    except Exception as e:
        print(f"Meme generation save error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ==================== AUTH TRACKING ====================

@app.post("/api/logout")
async def logout_user(
    req: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_optional)
):
    """Log out user and record logout time"""
    if not current_user:
        return {"success": True, "message": "Already logged out"}
        
    try:
        # Find the most recent login record for this user that doesn't have a logout time
        last_login = db.query(models.UserLoginHistory).filter(
            models.UserLoginHistory.user_id == current_user.id,
            models.UserLoginHistory.logout_time == None
        ).order_by(models.UserLoginHistory.login_time.desc()).first()
        
        if last_login:
            last_login.logout_time = func.now()
            db.commit()
            
        return {"success": True}
    except Exception as e:
        print(f"Logout error: {e}")
        return {"success": False, "error": str(e)}

# ==================== EVENT & SESSION TRACKING ====================

@app.post("/api/track-event")
async def track_event(
    event: schemas.UserEventCreate,
    req: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_optional)
):
    """Track user events for journey analysis"""
    try:
        user_event = models.UserEvent(
            user_id=current_user.id if current_user else None,
            session_id=event.session_id,
            event_type=event.event_type,
            event_category=event.event_category,
            event_action=event.event_action,
            event_label=event.event_label,
            event_value=event.event_value,
            page_url=event.page_url,
            page_title=event.page_title,
            referrer=event.referrer,
            device_type=event.device_type,
            browser=event.browser,
            os=event.os,
            time_on_page=event.time_on_page,
            event_metadata=event.metadata,
            ip_address=req.client.host if req.client else None,
            user_agent=req.headers.get('user-agent', None)
        )
        db.add(user_event)
        db.commit()
        
        return {"success": True}
    except Exception as e:
        print(f"Event tracking error: {e}")
        db.rollback()
        return {"success": False, "error": str(e)}

@app.post("/api/track-session")
async def track_session(
    session: schemas.UserSessionCreate,
    req: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_optional)
):
    """Track or update user session"""
    try:
        # Check if session exists
        existing_session = db.query(models.UserSession).filter(
            models.UserSession.session_id == session.session_id
        ).first()
        
        if existing_session:
            # Update existing session
            existing_session.ended_at = session.ended_at
            existing_session.duration_seconds = session.duration_seconds
            existing_session.is_active = session.is_active
            existing_session.pages_viewed = session.pages_viewed
            existing_session.mcqs_generated = session.mcqs_generated
            existing_session.quizzes_taken = session.quizzes_taken
            existing_session.memes_generated = session.memes_generated
        else:
            # Create new session
            user_session = models.UserSession(
                user_id=current_user.id if current_user else None,
                session_id=session.session_id,
                started_at=session.started_at,
                ended_at=session.ended_at,
                duration_seconds=session.duration_seconds,
                is_active=session.is_active,
                pages_viewed=session.pages_viewed,
                mcqs_generated=session.mcqs_generated,
                quizzes_taken=session.quizzes_taken,
                memes_generated=session.memes_generated,
                ip_address=req.client.host if req.client else None,
                user_agent=req.headers.get('user-agent', None)
            )
            db.add(user_session)
        
        db.commit()
        return {"success": True}
    except Exception as e:
        print(f"Session tracking error: {e}")
        db.rollback()
        return {"success": False, "error": str(e)}

# ==================== END EVENT & SESSION TRACKING ====================

# Serve Frontend
# We will mount the frontend directory to serve static files
# Ensure the directory exists
if not os.path.exists("frontend"):
    os.makedirs("frontend")

# --- IMAGE UPLOAD PROXY ---
@app.post("/api/upload-image")
async def upload_image(file: UploadFile = File(...), current_user: models.User = Depends(get_current_user)):
    """
    Upload image to local storage to avoid external API dependencies.
    """
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join("frontend", "uploads")
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        if not file_extension:
            file_extension = ".png" # Default fallback
            
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Return URL (relative to root since frontend is mounted at /)
        # The static mount serves 'frontend' at '/', so 'frontend/uploads/x.png' is accessible at '/uploads/x.png'
        return {"link": f"/uploads/{unique_filename}"}
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server upload error: {str(e)}")

# ==================== ANALYTICS DASHBOARD ENDPOINTS ====================

@app.post("/api/social/like")
async def toggle_like(
    like_data: schemas.SocialLikeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if like exists
    existing_like = db.query(models.SocialLike).filter(
        models.SocialLike.user_id == current_user.id,
        models.SocialLike.content_type == like_data.content_type,
        models.SocialLike.content_id == like_data.content_id
    ).first()
    
    if existing_like:
        db.delete(existing_like)
        db.commit()
        liked = False
    else:
        new_like = models.SocialLike(
            user_id=current_user.id,
            content_type=like_data.content_type,
            content_id=like_data.content_id
        )
        db.add(new_like)
        db.commit()
        liked = True
        
    # Get updated count
    count = db.query(models.SocialLike).filter(
        models.SocialLike.content_type == like_data.content_type,
        models.SocialLike.content_id == like_data.content_id
    ).count()
    
    return {"liked": liked, "likes_count": count}

@app.post("/api/social/comment")
async def add_comment(
    comment_data: schemas.SocialCommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    comment = models.SocialComment(
        user_id=current_user.id,
        content_type=comment_data.content_type,
        content_id=comment_data.content_id,
        text=comment_data.text
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return {
        "id": comment.id,
        "user_name": current_user.full_name or "User",
        "user_avatar": current_user.profile_picture,
        "text": comment.text,
        "created_at": comment.created_at
    }

@app.get("/api/social/comments")
async def get_comments(
    content_type: str,
    content_id: int,
    db: Session = Depends(get_db)
):
    comments = db.query(models.SocialComment).filter(
        models.SocialComment.content_type == content_type,
        models.SocialComment.content_id == content_id
    ).order_by(models.SocialComment.created_at.asc()).all()
    
    return [{
        "id": c.id,
        "user_name": c.user.full_name if c.user else "Unknown",
        "user_avatar": c.user.profile_picture if c.user else None,
        "text": c.text,
        "created_at": c.created_at
    } for c in comments]

@app.get("/api/social/feed")
async def get_social_feed(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_optional)
):
    """Get public social feed"""
    feed = []
    
    # Fetch recent Quizzes
    # Fetch recent Quizzes - ONLY from logged in users
    recent_quizzes = db.query(models.QuizSession).filter(
        models.QuizSession.user_id != None
    ).order_by(models.QuizSession.started_at.desc()).limit(20).all()
    for q in recent_quizzes:
        user = db.query(models.User).filter(models.User.id == q.user_id).first()
        user_name = user.full_name if user else "Anonymous"
        user_pic = user.profile_picture if user else None
        
        likes_count = db.query(models.SocialLike).filter(
            models.SocialLike.content_type == 'quiz',
            models.SocialLike.content_id == q.id
        ).count()
        
        has_liked = False
        if current_user:
            has_liked = db.query(models.SocialLike).filter(
                models.SocialLike.user_id == current_user.id,
                models.SocialLike.content_type == 'quiz',
                models.SocialLike.content_id == q.id
            ).first() is not None
        
        comments_count = db.query(models.SocialComment).filter(
            models.SocialComment.content_type == 'quiz',
            models.SocialComment.content_id == q.id
        ).count()
        
        
        # Get ALL questions with answers
        sample_answers = db.query(models.QuestionAnswer).filter(
            models.QuestionAnswer.quiz_session_id == q.id
        ).all()  # Changed from limit(3) to all()
        
        questions_preview = []
        for ans in sample_answers:
            question = db.query(models.MCQQuestion).filter(
                models.MCQQuestion.id == ans.question_id
            ).first()
            if question:
                # Map option letter to actual text
                option_map = {
                    'A': question.option_a or '',
                    'B': question.option_b or '',
                    'C': question.option_c or '',
                    'D': question.option_d or ''
                }
                
                # Convert to uppercase for mapping
                user_answer_letter = ans.user_answer.upper() if isinstance(ans.user_answer, str) else ans.user_answer
                correct_answer_letter = question.correct_answer.upper() if isinstance(question.correct_answer, str) else question.correct_answer
                
                user_answer_text = option_map.get(user_answer_letter, ans.user_answer)
                correct_answer_text = option_map.get(correct_answer_letter, question.correct_answer)
                
                # Fallback if options are empty
                if not user_answer_text or not user_answer_text.strip():
                    user_answer_text = f"Option {user_answer_letter}"
                if not correct_answer_text or not correct_answer_text.strip():
                    correct_answer_text = f"Option {correct_answer_letter}"
                
                questions_preview.append({
                    "question": question.question_text,
                    "options": {
                        "A": question.option_a or "Option A",
                        "B": question.option_b or "Option B",
                        "C": question.option_c or "Option C",
                        "D": question.option_d or "Option D"
                    },
                    "user_answer": user_answer_text, # Keep for backward compatibility if needed
                    "correct_answer": correct_answer_text, # Keep for backward compatibility
                    "user_answer_letter": user_answer_letter,
                    "correct_answer_letter": correct_answer_letter,
                    "is_correct": ans.is_correct,
                    "explanation": question.explanation
                })
        
        feed.append({
            "id": f"quiz_{q.id}",
            "content_id": q.id,
            "type": "quiz",
            "user": user_name,
            "user_pic": user_pic,
            "action": "completed a quiz",
            "content": f"Scored {q.score_percentage}% ({q.correct_answers}/{q.total_questions})",
            "details": f"Completed in {int(q.time_taken_seconds)}s",
            "questions_preview": questions_preview,
            "time": q.started_at,
            "likes": likes_count,
            "has_liked": has_liked,
            "comments": comments_count
        })
        
    # Fetch recent Memes - ONLY from logged in users
    recent_memes = db.query(models.MemeGeneration).filter(
        models.MemeGeneration.user_id != None
    ).order_by(models.MemeGeneration.created_at.desc()).limit(20).all()
    for m in recent_memes:
        user = db.query(models.User).filter(models.User.id == m.user_id).first()
        user_name = user.full_name if user else "Anonymous"
        user_pic = user.profile_picture if user else None
        
        first_meme = db.query(models.GeneratedMeme).filter(models.GeneratedMeme.generation_id == m.id).first()
        image_url = first_meme.meme_url if first_meme else None
        
        likes_count = db.query(models.SocialLike).filter(
            models.SocialLike.content_type == 'meme',
            models.SocialLike.content_id == m.id
        ).count()
        
        has_liked = False
        if current_user:
            has_liked = db.query(models.SocialLike).filter(
                models.SocialLike.user_id == current_user.id,
                models.SocialLike.content_type == 'meme',
                models.SocialLike.content_id == m.id
            ).first() is not None
        
        comments_count = db.query(models.SocialComment).filter(
            models.SocialComment.content_type == 'meme',
            models.SocialComment.content_id == m.id
        ).count()
        
        feed.append({
            "id": f"meme_{m.id}",
            "content_id": m.id,
            "type": "meme",
            "user": user_name,
            "user_pic": user_pic,
            "action": "cooked up a meme",
            "content": m.topic,
            "image_url": image_url,
            "details": f"Generated {m.num_memes} variants",
            "time": m.created_at,
            "likes": likes_count,
            "has_liked": has_liked,
            "comments": comments_count
        })
    
    # Fetch recent MCQ Generations - ONLY from logged in users
    recent_mcqs = db.query(models.MCQGeneration).filter(
        models.MCQGeneration.user_id != None
    ).order_by(models.MCQGeneration.created_at.desc()).limit(20).all()
    for mcq in recent_mcqs:
        user = db.query(models.User).filter(models.User.id == mcq.user_id).first()
        user_name = user.full_name if user else "Anonymous"
        user_pic = user.profile_picture if user else None
        
        likes_count = db.query(models.SocialLike).filter(
            models.SocialLike.content_type == 'mcq',
            models.SocialLike.content_id == mcq.id
        ).count()
        
        has_liked = False
        if current_user:
            has_liked = db.query(models.SocialLike).filter(
                models.SocialLike.user_id == current_user.id,
                models.SocialLike.content_type == 'mcq',
                models.SocialLike.content_id == mcq.id
            ).first() is not None
        
        comments_count = db.query(models.SocialComment).filter(
            models.SocialComment.content_type == 'mcq',
            models.SocialComment.content_id == mcq.id
        ).count()
        
        
        
        # Get ALL questions with options and correct answers for MCQ generations
        all_questions = db.query(models.MCQQuestion).filter(
            models.MCQQuestion.generation_id == mcq.id
        ).all()
        
        questions_data = []
        for q in all_questions:
            # Map correct answer letter to actual text
            option_map = {
                'A': q.option_a or '',
                'B': q.option_b or '',
                'C': q.option_c or '',
                'D': q.option_d or ''
            }
            
            correct_answer_letter = q.correct_answer.upper() if isinstance(q.correct_answer, str) else q.correct_answer
            correct_text = option_map.get(correct_answer_letter, q.correct_answer)
            
            # Fallback if option is empty
            if not correct_text or not correct_text.strip():
                correct_text = f"Option {correct_answer_letter}"
            
            questions_data.append({
                "question": q.question_text,
                "options": {
                    "A": q.option_a or "Option A",
                    "B": q.option_b or "Option B",
                    "C": q.option_c or "Option C",
                    "D": q.option_d or "Option D"
                },
                "correct_answer": q.correct_answer,
                "correct_answer_text": correct_text,
                "explanation": q.explanation
            })
        
        feed.append({
            "id": f"mcq_{mcq.id}",
            "content_id": mcq.id,
            "type": "mcq",
            "user": user_name,
            "user_pic": user_pic,
            "action": "generated MCQs",
            "content": f"{mcq.num_questions} {mcq.difficulty} questions",
            "details": f"Category: {mcq.category or 'General'}",
            "questions_data": questions_data,
            "time": mcq.created_at,
            "likes": likes_count,
            "has_liked": has_liked,
            "comments": comments_count
        })
        
    feed.sort(key=lambda x: x["time"], reverse=True)
    return feed[:40]

# ==================== BOOKMARK ENDPOINTS ====================

@app.post("/api/bookmarks/toggle")
async def toggle_bookmark(
    request: BookmarkRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Toggle bookmark (save/unsave) for MCQ, meme, quiz, or individual items"""
    # Check if bookmark exists
    query = db.query(models.Bookmark).filter(
        models.Bookmark.user_id == current_user.id,
        models.Bookmark.content_type == request.content_type,
        models.Bookmark.content_id == request.content_id
    )
    
    if request.content_index is not None:
        query = query.filter(models.Bookmark.content_index == request.content_index)
    else:
        query = query.filter(models.Bookmark.content_index.is_(None))
    
    existing = query.first()
    
    if existing:
        # Unsave (remove bookmark)
        db.delete(existing)
        db.commit()
        return {"bookmarked": False, "message": "Removed from saved items"}
    else:
        # Save (add bookmark)
        bookmark = models.Bookmark(
            user_id=current_user.id,
            content_type=request.content_type,
            content_id=request.content_id,
            content_index=request.content_index,
            content_data=request.content_data
        )
        db.add(bookmark)
        db.commit()
        return {"bookmarked": True, "message": "Saved successfully"}

@app.get("/api/bookmarks")
async def get_bookmarks(
    content_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all bookmarks for the current user"""
    query = db.query(models.Bookmark).filter(models.Bookmark.user_id == current_user.id)
    
    if content_type:
        query = query.filter(models.Bookmark.content_type == content_type)
    
    bookmarks = query.order_by(models.Bookmark.created_at.desc()).all()
    
    # Fetch actual content for each bookmark
    result = []
    for bm in bookmarks:
        item = {
            "id": bm.id, 
            "content_type": bm.content_type, 
            "content_id": bm.content_id, 
            "content_index": bm.content_index,
            "created_at": bm.created_at
        }
        
        # For individual items, use stored content_data
        if bm.content_data:
            item['content_data'] = bm.content_data
            item['content'] = bm.content_data  # Also set content for backward compatibility
        elif bm.content_type == 'mcq':
            mcq = db.query(models.MCQGeneration).filter(models.MCQGeneration.id == bm.content_id).first()
            if mcq:
                item['content'] = {
                    "difficulty": mcq.difficulty,
                    "num_questions": mcq.num_questions,
                    "questions": mcq.questions_data,
                    "created_at": mcq.created_at
                }
        elif bm.content_type == 'meme':
            meme_gen = db.query(models.MemeGeneration).filter(models.MemeGeneration.id == bm.content_id).first()
            if meme_gen:
                memes = db.query(models.GeneratedMeme).filter(models.GeneratedMeme.generation_id == meme_gen.id).all()
                item['content'] = {
                    "topic": meme_gen.topic,
                    "memes": [{"url": m.meme_url, "prompt": m.prompt_used} for m in memes],
                    "created_at": meme_gen.created_at
                }
        elif bm.content_type == 'quiz':
            quiz = db.query(models.QuizSession).filter(models.QuizSession.id == bm.content_id).first()
            if quiz:
                item['content'] = {
                    "score": quiz.score_percentage,
                    "time_taken": quiz.time_taken_seconds,
                    "created_at": quiz.started_at
                }
        
        result.append(item)
    
    return result

@app.get("/api/bookmarks/check")
async def check_bookmark(
    content_type: str,
    content_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Check if content is bookmarked"""
    bookmark = db.query(models.Bookmark).filter(
        models.Bookmark.user_id == current_user.id,
        models.Bookmark.content_type == content_type,
        models.Bookmark.content_id == content_id
    ).first()
    
    return {"bookmarked": bookmark is not None}

# ==================== END BOOKMARK ENDPOINTS ====================

@app.get("/api/analytics/dashboard")
async def get_analytics_dashboard(
    time_range: str = "all",
    target_email: Optional[str] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive analytics for the dashboard.
    Includes Leaderboards, Social Feed, and Deep Content Analytics.
    """
    
    # Determine scope - Allow anyone to filter
    if target_email and target_email != "global":
        scope_user_email = target_email
    elif target_email == "global":
        scope_user_email = None # None means global/all users
    else:
        scope_user_email = current_user.email # Default to self
        
    try:
        # Base queries
        mcq_query = db.query(models.MCQGeneration)
        quiz_query = db.query(models.QuizSession)
        meme_query = db.query(models.MemeGeneration)
        
        # Apply User Filter
        if scope_user_email:
            user = auth.get_user_by_email(db, scope_user_email)
            if not user:
                return {"error": "User not found"}
            mcq_query = mcq_query.filter(models.MCQGeneration.user_id == user.id)
            quiz_query = quiz_query.filter(models.QuizSession.user_id == user.id)
            meme_query = meme_query.filter(models.MemeGeneration.user_id == user.id)
            
        # --- 1. KPIs ---
        total_quizzes = quiz_query.count()
        total_memes = meme_query.count()
        total_mcqs = mcq_query.count()
        
        # Calculate Avg Score & Time
        quiz_stats = quiz_query.with_entities(
            func.avg(models.QuizSession.score_percentage),
            func.avg(models.QuizSession.time_taken_seconds),
            func.sum(models.QuizSession.time_taken_seconds)
        ).first()
        
        avg_score = round(quiz_stats[0] or 0, 1)
        total_time_spent = round((quiz_stats[2] or 0) / 60, 1) # in minutes
        
        # --- MCQ Analytics ---
        difficulty_stats = mcq_query.with_entities(
            models.MCQGeneration.difficulty,
            func.count(models.MCQGeneration.id)
        ).group_by(models.MCQGeneration.difficulty).all()
        
        difficulty_dist = {str(stat[0]): stat[1] for stat in difficulty_stats}

        # --- 2. LEADERBOARDS (Global Only) ---
        leaderboard = []
        memeboard = []
        mcqboard = []
        
        if not scope_user_email: # Only calculate leaderboards in global mode
            # Quiz Leaderboard (Top Scorers)
            top_scorers = db.query(
                models.User.full_name,
                models.User.email,
                models.User.profile_picture,
                func.avg(models.QuizSession.score_percentage).label('avg_score'),
                func.count(models.QuizSession.id).label('quizzes_taken')
            ).join(models.QuizSession).group_by(models.User.id).order_by(desc('avg_score')).limit(5).all()
            
            leaderboard = [{
                "name": u.full_name or u.email.split('@')[0],
                "avatar": u.profile_picture,
                "score": round(u.avg_score or 0, 1),
                "quizzes": u.quizzes_taken
            } for u in top_scorers]
            
            # Meme Leaderboard (Top Creators)
            top_creators = db.query(
                models.User.full_name,
                models.User.email,
                models.User.profile_picture,
                func.count(models.MemeGeneration.id).label('memes_created')
            ).join(models.MemeGeneration).group_by(models.User.id).order_by(desc('memes_created')).limit(5).all()
            
            memeboard = [{
                "name": u.full_name or u.email.split('@')[0],
                "avatar": u.profile_picture,
                "memes": u.memes_created
            } for u in top_creators]
            
            # MCQ Leaderboard (Top Generators)
            top_mcq_creators = db.query(
                models.User.full_name,
                models.User.email,
                models.User.profile_picture,
                func.count(models.MCQGeneration.id).label('mcqs_created')
            ).join(models.MCQGeneration).group_by(models.User.id).order_by(desc('mcqs_created')).limit(5).all()
            
            mcqboard = [{
                "name": u.full_name or u.email.split('@')[0],
                "avatar": u.profile_picture,
                "mcqs": u.mcqs_created
            } for u in top_mcq_creators]

        # --- Question Level Analytics ---
        q_query = db.query(models.MCQQuestion).join(models.MCQGeneration)
        if scope_user_email:
             # Re-fetch user to be safe (though we did it above)
             user_obj = auth.get_user_by_email(db, scope_user_email)
             if user_obj:
                q_query = q_query.filter(models.MCQGeneration.user_id == user_obj.id)
             
        q_stats = q_query.with_entities(
            func.sum(models.MCQQuestion.times_correct),
            func.sum(models.MCQQuestion.times_wrong),
            func.avg(models.MCQQuestion.average_time_to_answer)
        ).first()
        
        total_correct = q_stats[0] or 0
        total_wrong = q_stats[1] or 0
        avg_q_time = round(q_stats[2] or 0, 1)

        # --- 3. TOPICS & TRENDS ---
        top_topics = []
        topic_counts = {}
        
        # Get MCQ topics (Most Searched Content)
        recent_mcqs = mcq_query.order_by(models.MCQGeneration.created_at.desc()).limit(100).all()
        for mcq in recent_mcqs:
            # Clean and normalize topic
            topic = (mcq.source_content or "").strip()[:40] 
            if len(topic) > 3:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
        # Get Meme topics
        recent_memes = meme_query.order_by(models.MemeGeneration.created_at.desc()).limit(100).all()
        for meme in recent_memes:
            topic = (meme.topic or "").strip()
            if len(topic) > 3:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:8]
        top_topics = [{"text": k, "value": v} for k, v in sorted_topics]
        
        # --- 4. SOCIAL FEED (Instagram Style) ---
        feed = []
        
        # Fetch recent Quizzes with User info
        recent_quizzes = quiz_query.order_by(models.QuizSession.started_at.desc()).limit(15).all()
        for q in recent_quizzes:
            user = db.query(models.User).filter(models.User.id == q.user_id).first()
            user_name = user.full_name if user else "Anonymous"
            user_pic = user.profile_picture if user else None
            
            # Get Likes
            likes_count = db.query(models.SocialLike).filter(
                models.SocialLike.content_type == 'quiz',
                models.SocialLike.content_id == q.id
            ).count()
            
            has_liked = db.query(models.SocialLike).filter(
                models.SocialLike.user_id == current_user.id,
                models.SocialLike.content_type == 'quiz',
                models.SocialLike.content_id == q.id
            ).first() is not None
            
            feed.append({
                "id": f"quiz_{q.id}",
                "content_id": q.id,
                "type": "quiz",
                "user": user_name,
                "user_pic": user_pic,
                "action": "aced a quiz",
                "content": f"Scored {q.score_percentage}%",
                "details": f"Completed in {int(q.time_taken_seconds)}s",
                "time": q.started_at,
                "likes": likes_count,
                "has_liked": has_liked
            })
            
        # Fetch recent Memes with User info
        recent_memes_feed = meme_query.order_by(models.MemeGeneration.created_at.desc()).limit(15).all()
        for m in recent_memes_feed:
            user = db.query(models.User).filter(models.User.id == m.user_id).first()
            user_name = user.full_name if user else "Anonymous"
            user_pic = user.profile_picture if user else None
            
            # Fetch actual meme image
            first_meme = db.query(models.GeneratedMeme).filter(models.GeneratedMeme.generation_id == m.id).first()
            image_url = first_meme.meme_url if first_meme else None
            
            # Get Likes
            likes_count = db.query(models.SocialLike).filter(
                models.SocialLike.content_type == 'meme',
                models.SocialLike.content_id == m.id
            ).count()
            
            has_liked = db.query(models.SocialLike).filter(
                models.SocialLike.user_id == current_user.id,
                models.SocialLike.content_type == 'meme',
                models.SocialLike.content_id == m.id
            ).first() is not None
            
            feed.append({
                "id": f"meme_{m.id}",
                "content_id": m.id,
                "type": "meme",
                "user": user_name,
                "user_pic": user_pic,
                "action": "cooked up a meme",
                "content": m.topic,
                "image_url": image_url,
                "details": f"Generated {m.num_memes} variants",
                "time": m.created_at,
                "likes": likes_count,
                "has_liked": has_liked
            })
            
        # Sort feed by time
        feed.sort(key=lambda x: x["time"], reverse=True)
        feed = feed[:30] # Keep top 30
        
        return {
            "kpis": {
                "total_quizzes": total_quizzes,
                "avg_score": avg_score,
                "total_memes": total_memes,
                "total_time_minutes": total_time_spent,
                "total_correct_answers": total_correct,
                "total_wrong_answers": total_wrong,
                "avg_question_time": avg_q_time
            },
            "mcq_analytics": {
                "difficulty_distribution": difficulty_dist,
                "total_mcqs": total_mcqs
            },
            "leaderboard": leaderboard,
            "memeboard": memeboard,
            "mcqboard": mcqboard,
            "top_topics": top_topics,
            "feed": feed,
            "scope": "Global" if scope_user_email is None else "Personal"
        }
        
    except Exception as e:
        print(f"Analytics Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/users")
async def get_analytics_users(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of users for filtering (Available to all users now)"""
    users = db.query(models.User).all()
    return [{"email": u.email, "name": u.full_name or "User"} for u in users]

# ==================== END ANALYTICS DASHBOARD ENDPOINTS ====================

# ==================== ADMIN PANEL ENDPOINTS ====================

@app.get("/api/admin/tables")
async def get_tables(db: Session = Depends(get_db)):
    """Get list of all database tables and basic stats"""
    try:
        # Get all table names
        from sqlalchemy import inspect, text
        inspector = inspect(database.engine)
        tables = inspector.get_table_names()
        
        # Get basic stats
        stats = {}
        try:
            result = db.execute(text("SELECT COUNT(*) FROM users")).fetchone()
            stats["Total Users"] = result[0] if result else 0
        except:
            stats["Total Users"] = 0
            
        try:
            result = db.execute(text("SELECT COUNT(*) FROM mcq_history")).fetchone()
            stats["Total MCQs"] = result[0] if result else 0
        except:
            stats["Total MCQs"] = 0
        
        # Get database name/path
        db_name = str(database.engine.url)
        
        return {
            "tables": tables, 
            "stats": stats,
            "database": db_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/table/{table_name}")
async def get_table_data(
    table_name: str, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get data from a specific table (Superusers only)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        from sqlalchemy import text
        # Validate table name to prevent SQL injection
        from sqlalchemy import inspect
        inspector = inspect(database.engine)
        valid_tables = inspector.get_table_names()
        
        if table_name not in valid_tables:
            raise HTTPException(status_code=400, detail="Invalid table name")
        
        # Get table data (limit to 100 rows for safety)
        query = text(f"SELECT * FROM {table_name} LIMIT 100")
        result = db.execute(query)
        
        # Convert to list of dicts
        columns = result.keys()
        data = [dict(zip(columns, row)) for row in result.fetchall()]
        
        # Get column info
        column_info = []
        for col in inspector.get_columns(table_name):
            column_info.append({
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col.get("nullable", True)
            })
        
        return {
            "data": data,
            "columns": list(columns),
            "column_info": column_info,
            "row_count": len(data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class QueryRequest(BaseModel):
    query: str

@app.post("/api/admin/query")
async def execute_query(request: QueryRequest, db: Session = Depends(get_db)):
    """Execute any SQL query - FULL ADMIN ACCESS"""
    try:
        from sqlalchemy import text
        
        query_lower = request.query.strip().lower()
        
        # Execute query
        result = db.execute(text(request.query))
        
        # For SELECT queries, return data
        if query_lower.startswith('select'):
            columns = result.keys()
            data = [dict(zip(columns, row)) for row in result.fetchall()]
            db.commit()  # Commit any changes
            return {"results": data, "message": f"Query executed. {len(data)} rows returned."}
        
        # For DDL/DML queries (CREATE, DROP, DELETE, UPDATE, etc.)
        else:
            db.commit()  # Commit the changes
            affected_rows = result.rowcount if hasattr(result, 'rowcount') else 0
            return {
                "results": [], 
                "message": f"Query executed successfully. {affected_rows} rows affected."
            }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ==================== END ADMIN PANEL ENDPOINTS ====================

# Admin Panel Route
@app.get("/admin")
async def admin_panel():
    """Serve the admin panel"""
    admin_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "admin.html")
    return FileResponse(admin_path)

# Serve Frontend
# We will mount the frontend directory to serve static files
# Ensure the directory exists
import os
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if not os.path.exists(frontend_dir):
    raise RuntimeError(f"Frontend directory not found at {frontend_dir}")

app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
