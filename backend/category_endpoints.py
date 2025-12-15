# Category and Trending Endpoints

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional, List
from datetime import datetime, timedelta
import models
from database import get_db

router = APIRouter()

# Predefined categories
CATEGORIES = [
    "Science",
    "History", 
    "Technology",
    "Pop Culture",
    "Geography",
    "Sports",
    "Literature",
    "Current Events",
    "Programming",
    "Mathematics",
    "General Knowledge"
]

@router.get("/api/categories")
async def get_categories():
    """Get list of available categories"""
    return {"categories": CATEGORIES}

from pydantic import BaseModel

class ViewRequest(BaseModel):
    content_type: str
    content_id: int

@router.post("/api/content/view")
async def track_view(
    request: ViewRequest,
    db: Session = Depends(get_db)
):
    """Track content view"""
    try:
        if request.content_type == "mcq":
            item = db.query(models.MCQGeneration).filter(models.MCQGeneration.id == request.content_id).first()
            if item:
                item.view_count += 1
                db.commit()
        elif request.content_type == "meme":
            item = db.query(models.MemeGeneration).filter(models.MemeGeneration.id == request.content_id).first()
            if item:
                item.view_count += 1
                db.commit()
        
        return {"success": True}
    except Exception as e:
        print(f"View tracking error: {e}")
        return {"success": False}

@router.post("/api/content/share")
async def track_share(
    request: ViewRequest,
    db: Session = Depends(get_db)
):
    """Track content share"""
    try:
        if request.content_type == "mcq":
            item = db.query(models.MCQGeneration).filter(models.MCQGeneration.id == request.content_id).first()
            if item:
                item.share_count += 1
                db.commit()
        elif request.content_type == "meme":
            item = db.query(models.MemeGeneration).filter(models.MemeGeneration.id == request.content_id).first()
            if item:
                item.share_count += 1
                db.commit()
        
        return {"success": True}
    except Exception as e:
        print(f"Share tracking error: {e}")
        return {"success": False}

@router.get("/api/trending")
async def get_trending(
    content_type: Optional[str] = None,  # mcq, meme, all
    limit: int = 10,
    days: int = 7,  # Trending in last N days
    db: Session = Depends(get_db)
):
    """Get trending content"""
    result = {"mcqs": [], "memes": []}
    
    # Calculate trending score: views + (saves * 2) + (shares * 3)
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    if content_type in [None, "all", "mcq"]:
        # Get trending MCQs
        mcqs = db.query(models.MCQGeneration).filter(
            models.MCQGeneration.created_at >= cutoff_date
        ).all()
        
        # Calculate trending score
        mcq_scores = []
        for mcq in mcqs:
            score = (mcq.view_count or 0) + (mcq.save_count or 0) * 2 + (mcq.share_count or 0) * 3
            mcq_scores.append((mcq, score))
        
        # Sort by score
        mcq_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Get top items
        for mcq, score in mcq_scores[:limit]:
            result["mcqs"].append({
                "id": mcq.id,
                "difficulty": mcq.difficulty,
                "num_questions": mcq.num_questions,
                "category": mcq.category,
                "view_count": mcq.view_count or 0,
                "save_count": mcq.save_count or 0,
                "share_count": mcq.share_count or 0,
                "trending_score": score,
                "created_at": mcq.created_at,
                "user_id": mcq.user_id
            })
    
    if content_type in [None, "all", "meme"]:
        # Get trending Memes
        memes = db.query(models.MemeGeneration).filter(
            models.MemeGeneration.created_at >= cutoff_date
        ).all()
        
        # Calculate trending score
        meme_scores = []
        for meme in memes:
            score = (meme.view_count or 0) + (meme.save_count or 0) * 2 + (meme.share_count or 0) * 3
            meme_scores.append((meme, score))
        
        # Sort by score
        meme_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Get top items
        for meme, score in meme_scores[:limit]:
            result["memes"].append({
                "id": meme.id,
                "topic": meme.topic,
                "num_memes": meme.num_memes,
                "category": meme.category,
                "view_count": meme.view_count or 0,
                "save_count": meme.save_count or 0,
                "share_count": meme.share_count or 0,
                "trending_score": score,
                "created_at": meme.created_at,
                "user_id": meme.user_id
            })
    
    return result

@router.get("/api/content/by-category")
async def get_content_by_category(
    category: str,
    content_type: Optional[str] = None,  # mcq, meme, all
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get content by category"""
    result = {"mcqs": [], "memes": []}
    
    if content_type in [None, "all", "mcq"]:
        mcqs = db.query(models.MCQGeneration).filter(
            models.MCQGeneration.category == category
        ).order_by(desc(models.MCQGeneration.created_at)).limit(limit).all()
        
        for mcq in mcqs:
            result["mcqs"].append({
                "id": mcq.id,
                "difficulty": mcq.difficulty,
                "num_questions": mcq.num_questions,
                "category": mcq.category,
                "view_count": mcq.view_count or 0,
                "save_count": mcq.save_count or 0,
                "created_at": mcq.created_at,
                "user_id": mcq.user_id
            })
    
    if content_type in [None, "all", "meme"]:
        memes = db.query(models.MemeGeneration).filter(
            models.MemeGeneration.category == category
        ).order_by(desc(models.MemeGeneration.created_at)).limit(limit).all()
        
        for meme in memes:
            result["memes"].append({
                "id": meme.id,
                "topic": meme.topic,
                "num_memes": meme.num_memes,
                "category": meme.category,
                "view_count": meme.view_count or 0,
                "save_count": meme.save_count or 0,
                "created_at": meme.created_at,
                "user_id": meme.user_id
            })
    
    return result
