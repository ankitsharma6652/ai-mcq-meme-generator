from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, JSON, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone_number = Column(String(50), unique=True, index=True, nullable=True)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Profile fields
    profile_picture = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    designation = Column(String(100), nullable=True)
    nature_of_work = Column(String(100), nullable=True)
    company_name = Column(String(150), nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    twitter_url = Column(String(255), nullable=True)
    github_url = Column(String(255), nullable=True)
    website_url = Column(String(255), nullable=True)

    # Relationships
    social_accounts = relationship("SocialAccount", back_populates="user")
    activities = relationship("ActivityLog", back_populates="user")
    contents = relationship("GeneratedContent", back_populates="user")
    quiz_results = relationship("QuizResult", back_populates="user")
    mcq_generations = relationship("MCQGeneration", back_populates="user")
    quiz_sessions = relationship("QuizSession", back_populates="user")
    meme_generations = relationship("MemeGeneration", back_populates="user")
    user_events = relationship("UserEvent", back_populates="user")
    login_history = relationship("UserLoginHistory", back_populates="user")

class SocialAccount(Base):
    __tablename__ = "social_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    provider = Column(String(50), nullable=False)
    social_id = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True)
    
    user = relationship("User", back_populates="social_accounts")

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="activities")

class GeneratedContent(Base):
    __tablename__ = "generated_contents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content_type = Column(String(50), nullable=False)
    prompt = Column(Text, nullable=True)
    result_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="contents")

class QuizResult(Base):
    __tablename__ = "quiz_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic = Column(String(255), nullable=False)
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    answers = Column(JSON, nullable=True)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="quiz_results")

# ==================== NORMALIZED ANALYTICS TABLES ====================

class MCQGeneration(Base):
    """Track MCQ generation metadata"""
    __tablename__ = "mcq_generations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Input Details
    input_type = Column(String(50), nullable=False, index=True)  # paste_text, upload_file, url
    content_type = Column(String(50), nullable=False, index=True)  # coding, general, auto
    difficulty = Column(String(20), nullable=False, index=True)  # easy, medium, hard, auto
    num_questions = Column(Integer, nullable=False)
    include_explanation = Column(Boolean, default=True)
    
    # Category & Discovery
    category = Column(String(50), nullable=True, index=True)  # Science, History, Technology, etc.
    
    # Source Content
    source_content = Column(Text, nullable=True)
    source_url = Column(String(500), nullable=True)
    source_filename = Column(String(255), nullable=True)
    
    # Generation Details
    model_name = Column(String(100), nullable=True)
    generation_time_seconds = Column(Float, nullable=True)
    questions_data = Column(JSON, nullable=True)  # Legacy column for compatibility
    
    # Engagement Tracking
    view_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    save_count = Column(Integer, default=0)
    quiz_completion_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="mcq_generations")
    questions = relationship("MCQQuestion", back_populates="generation", cascade="all, delete-orphan")
    quiz_sessions = relationship("QuizSession", back_populates="mcq_generation")

class MCQQuestion(Base):
    """Individual questions - normalized for better analytics"""
    __tablename__ = "mcq_questions"

    id = Column(Integer, primary_key=True, index=True)
    generation_id = Column(Integer, ForeignKey("mcq_generations.id"), nullable=False, index=True)
    
    # Question Details
    question_number = Column(Integer, nullable=False)  # 1, 2, 3, etc.
    question_text = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_answer = Column(String(1), nullable=False)  # A, B, C, or D
    explanation = Column(Text, nullable=True)
    
    # Analytics
    times_attempted = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)
    times_wrong = Column(Integer, default=0)
    average_time_to_answer = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    generation = relationship("MCQGeneration", back_populates="questions")
    answers = relationship("QuestionAnswer", back_populates="question")

class QuizSession(Base):
    """Track each quiz session"""
    __tablename__ = "quiz_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    mcq_generation_id = Column(Integer, ForeignKey("mcq_generations.id"), nullable=True, index=True)
    
    # Session Details
    total_questions = Column(Integer, nullable=False)
    questions_answered = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    wrong_answers = Column(Integer, default=0)
    score_percentage = Column(Float, nullable=True)
    
    # Timing
    started_at = Column(DateTime(timezone=True), nullable=False, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    time_taken_seconds = Column(Float, nullable=True)
    is_completed = Column(Boolean, default=False, index=True)
    
    # Session Info
    content_type = Column(String(50), nullable=True, index=True)
    difficulty = Column(String(20), nullable=True, index=True)
    input_type = Column(String(50), nullable=True)
    
    # Metadata
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    device_type = Column(String(50), nullable=True)  # mobile, tablet, desktop
    
    # Relationships
    user = relationship("User", back_populates="quiz_sessions")
    mcq_generation = relationship("MCQGeneration", back_populates="quiz_sessions")
    answers = relationship("QuestionAnswer", back_populates="quiz_session")

class QuestionAnswer(Base):
    """Track each individual answer"""
    __tablename__ = "question_answers"

    id = Column(Integer, primary_key=True, index=True)
    quiz_session_id = Column(Integer, ForeignKey("quiz_sessions.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("mcq_questions.id"), nullable=False, index=True)
    
    # Answer Details
    user_answer = Column(String(1), nullable=False)  # A, B, C, or D
    is_correct = Column(Boolean, nullable=False, index=True)
    time_spent_seconds = Column(Float, nullable=True)
    
    # Metadata
    answered_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    quiz_session = relationship("QuizSession", back_populates="answers")
    question = relationship("MCQQuestion", back_populates="answers")

class MemeGeneration(Base):
    """Track meme generations"""
    __tablename__ = "meme_generations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Input Details
    input_type = Column(String(50), nullable=False, index=True)  # topic, url
    topic = Column(Text, nullable=True)
    source_url = Column(String(500), nullable=True)
    
    # Meme Configuration
    meme_type = Column(String(20), nullable=False, index=True)  # image, gif, video
    num_memes = Column(Integer, default=1)
    
    # Category & Discovery
    category = Column(String(50), nullable=True, index=True)  # Science, History, Technology, etc.
    
    # Generation Details
    model_name = Column(String(100), nullable=True)
    image_model = Column(String(100), nullable=True)
    generation_time_seconds = Column(Float, nullable=True)
    
    # Success Metrics
    total_generated = Column(Integer, nullable=False)
    successful_generations = Column(Integer, nullable=False)
    failed_generations = Column(Integer, nullable=False)
    memes_data = Column(JSON, nullable=True)  # Legacy column for compatibility
    
    # Engagement Tracking
    view_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    save_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="meme_generations")
    memes = relationship("GeneratedMeme", back_populates="generation")

class GeneratedMeme(Base):
    """Individual memes"""
    __tablename__ = "generated_memes"

    id = Column(Integer, primary_key=True, index=True)
    generation_id = Column(Integer, ForeignKey("meme_generations.id"), nullable=False, index=True)
    
    # Meme Details
    meme_url = Column(String(1000), nullable=False)
    meme_type = Column(String(20), nullable=False)  # image, gif, video
    source = Column(String(100), nullable=True)  # pollinations, flux, etc.
    note = Column(Text, nullable=True)
    
    # Analytics
    views = Column(Integer, default=0)
    downloads = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    generation = relationship("MemeGeneration", back_populates="memes")

# ==================== USER JOURNEY & EVENT TRACKING ====================

class UserEvent(Base):
    """Track every user interaction for journey analysis"""
    __tablename__ = "user_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String(100), nullable=True, index=True)  # Browser session ID
    
    # Event Details
    event_type = Column(String(100), nullable=False, index=True)  # page_view, button_click, mcq_generate, quiz_start, etc.
    event_category = Column(String(50), nullable=False, index=True)  # navigation, engagement, conversion
    event_action = Column(String(100), nullable=False)
    event_label = Column(String(255), nullable=True)
    event_value = Column(Float, nullable=True)
    
    # Page/Context
    page_url = Column(String(500), nullable=True)
    page_title = Column(String(255), nullable=True)
    referrer = Column(String(500), nullable=True)
    
    # User Context
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    device_type = Column(String(50), nullable=True)  # mobile, tablet, desktop
    browser = Column(String(100), nullable=True)
    os = Column(String(100), nullable=True)
    
    # Timing
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    time_on_page = Column(Float, nullable=True)  # seconds
    
    # Additional Data
    event_metadata = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="user_events")

class UserLoginHistory(Base):
    __tablename__ = "user_login_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    
    # Timing
    login_time = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    logout_time = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Context
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    device_type = Column(String(50), nullable=True)
    auth_provider = Column(String(50), default="google")
    
    # Relationships
    user = relationship("User", back_populates="login_history")

class UserSession(Base):
    """Track user sessions for retention analysis"""
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Session Details
    started_at = Column(DateTime(timezone=True), nullable=False, index=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # Session Metrics
    pages_viewed = Column(Integer, default=0)
    mcqs_generated = Column(Integer, default=0)
    quizzes_taken = Column(Integer, default=0)
    memes_generated = Column(Integer, default=0)
    
    # User Context
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)

class SocialLike(Base):
    """Track likes on content (Quiz or Meme)"""
    __tablename__ = "social_likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content_type = Column(String(20), nullable=False) # 'quiz' or 'meme'
    content_id = Column(Integer, nullable=False) # ID of QuizSession or MemeGeneration
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Ensure unique like per user per content
    __table_args__ = (
        UniqueConstraint('user_id', 'content_type', 'content_id', name='unique_user_like'),
    )

class SocialComment(Base):
    """Track comments on content"""
    __tablename__ = "social_comments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content_type = Column(String(20), nullable=False) # 'quiz' or 'meme'
    content_id = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to User for displaying name/avatar
    user = relationship("User")
    device_type = Column(String(50), nullable=True)
    browser = Column(String(100), nullable=True)
    os = Column(String(100), nullable=True)
    referrer = Column(String(500), nullable=True)
    utm_source = Column(String(100), nullable=True)
    utm_medium = Column(String(100), nullable=True)
    utm_campaign = Column(String(100), nullable=True)

# ==================== BOOKMARKS ====================

class Bookmark(Base):
    __tablename__ = "bookmarks"
    # No unique constraint - allow multiple bookmarks of same item with different indices
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content_type = Column(String(20), nullable=False)  # 'mcq', 'mcq_question', 'meme', 'meme_single', 'quiz'
    content_id = Column(Integer, nullable=False)
    content_index = Column(Integer, nullable=True)  # For individual questions/memes
    content_data = Column(JSON, nullable=True)  # Store the actual question/meme data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to User
    user = relationship("User")

# ==================== END NORMALIZED TABLES ====================
