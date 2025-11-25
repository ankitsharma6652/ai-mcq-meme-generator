from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
import phonenumbers
from datetime import datetime

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    phone_number: Optional[str] = None

# Phone number validation removed for social login simplicity

class UserCreate(UserBase):
    password: Optional[str] = None  # Optional for OAuth users

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    designation: Optional[str] = None
    nature_of_work: Optional[str] = None
    company_name: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    github_url: Optional[str] = None
    website_url: Optional[str] = None

# --- Token Schema ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Social Login Schema ---
class SocialLogin(BaseModel):
    provider: str # google, github
    token: str # Access token from frontend

# --- Activity Schema ---
class ActivityCreate(BaseModel):
    action: str
    details: Optional[Dict[str, Any]] = None

# --- Quiz Session Schema (Normalized) ---
class QuizSessionCreate(BaseModel):
    mcq_generation_id: Optional[int] = None
    total_questions: int
    questions_answered: int
    correct_answers: int
    wrong_answers: int
    score_percentage: float
    started_at: datetime
    completed_at: Optional[datetime] = None
    time_taken_seconds: Optional[float] = None
    is_completed: bool = False
    content_type: Optional[str] = None
    difficulty: Optional[str] = None
    input_type: Optional[str] = None
    device_type: Optional[str] = None

class QuestionAnswerCreate(BaseModel):
    quiz_session_id: int
    question_id: int
    user_answer: str  # A, B, C, or D
    is_correct: bool
    time_spent_seconds: Optional[float] = None

# --- Event Tracking Schema ---
class UserEventCreate(BaseModel):
    session_id: Optional[str] = None
    event_type: str  # page_view, button_click, mcq_generate, etc.
    event_category: str  # navigation, engagement, conversion
    event_action: str
    event_label: Optional[str] = None
    event_value: Optional[float] = None
    page_url: Optional[str] = None
    page_title: Optional[str] = None
    referrer: Optional[str] = None
    device_type: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    time_on_page: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

# --- Session Tracking Schema ---
class UserSessionCreate(BaseModel):
    session_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    is_active: bool = True
    pages_viewed: int = 0
    mcqs_generated: int = 0
    quizzes_taken: int = 0
    memes_generated: int = 0
    device_type: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    referrer: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None

# --- Meme Generation Schema ---
class MemeGenerationCreate(BaseModel):
    input_type: str  # topic, url
    topic: Optional[str] = None
    source_url: Optional[str] = None
    meme_type: str  # image, gif, video
    num_memes: int
    model_name: Optional[str] = None
    image_model: Optional[str] = None
    generation_time_seconds: Optional[float] = None
    memes_data: List[Dict[str, Any]]  # [{url, type, source, note}]
    total_generated: int
    successful_generations: int
    failed_generations: int

class GeneratedMemeCreate(BaseModel):
    generation_id: int
    meme_url: str
    meme_type: str
    source: Optional[str] = None
    note: Optional[str] = None

# --- Social Schemas ---
class SocialLikeCreate(BaseModel):
    content_type: str # 'quiz' or 'meme'
    content_id: int

class SocialCommentCreate(BaseModel):
    content_type: str
    content_id: int
    text: str

class SocialCommentResponse(BaseModel):
    id: int
    user_name: str
    user_avatar: Optional[str]
    text: str
    created_at: datetime
    
    class Config:
        orm_mode = True
