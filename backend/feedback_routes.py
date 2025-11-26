from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from database import get_db
from models import Feedback, User
from auth.jwt_handler import decode_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

security = HTTPBearer(auto_error=False)

def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if token is provided, otherwise return None"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_token(token)
        if not payload:
            return None
        
        email = payload.get("sub")
        if not email:
            return None
        
        user = db.query(User).filter(User.email == email).first()
        return user
    except Exception:
        return None

class FeedbackCreate(BaseModel):
    # Guest fields (optional, required if not logged in)
    guest_name: Optional[str] = None
    guest_email: Optional[EmailStr] = None
    guest_mobile: Optional[str] = None
    guest_country: Optional[str] = None
    
    # Feedback content
    message: str
    rating: Optional[int] = None  # 1-5

@router.post("/submit")
async def submit_feedback(
    feedback_data: FeedbackCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Submit feedback (works for both guests and logged-in users)"""
    
    # Validation
    if not current_user:
        # Guest mode - require name and email
        if not feedback_data.guest_name or not feedback_data.guest_email:
            raise HTTPException(
                status_code=400,
                detail="Name and email are required for guest feedback"
            )
    
    if not feedback_data.message or len(feedback_data.message.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Feedback message must be at least 10 characters"
        )
    
    if feedback_data.rating and (feedback_data.rating < 1 or feedback_data.rating > 5):
        raise HTTPException(
            status_code=400,
            detail="Rating must be between 1 and 5"
        )
    
    # Create feedback entry
    feedback = Feedback(
        user_id=current_user.id if current_user else None,
        guest_name=feedback_data.guest_name if not current_user else None,
        guest_email=feedback_data.guest_email if not current_user else None,
        guest_mobile=feedback_data.guest_mobile if not current_user else None,
        guest_country=feedback_data.guest_country if not current_user else None,
        message=feedback_data.message,
        rating=feedback_data.rating,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    return {
        "success": True,
        "message": "Thank you for your feedback!",
        "feedback_id": feedback.id
    }

@router.get("/list")
async def list_feedback(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """List all feedback (admin only)"""
    if not current_user or not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    feedbacks = db.query(Feedback).order_by(Feedback.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "feedbacks": [
            {
                "id": f.id,
                "user_id": f.user_id,
                "user_name": f.user.full_name if f.user else f.guest_name,
                "user_email": f.user.email if f.user else f.guest_email,
                "guest_mobile": f.guest_mobile,
                "guest_country": f.guest_country,
                "message": f.message,
                "rating": f.rating,
                "created_at": f.created_at.isoformat(),
                "is_read": f.is_read,
                "admin_notes": f.admin_notes
            }
            for f in feedbacks
        ]
    }
