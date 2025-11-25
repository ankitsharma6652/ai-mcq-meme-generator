# ==================== BOOKMARK ENDPOINTS ====================

@app.post("/api/bookmarks/toggle")
async def toggle_bookmark(
    content_type: str,
    content_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Toggle bookmark (save/unsave) for MCQ, meme, or quiz"""
    # Check if bookmark exists
    existing = db.query(models.Bookmark).filter(
        models.Bookmark.user_id == current_user.id,
        models.Bookmark.content_type == content_type,
        models.Bookmark.content_id == content_id
    ).first()
    
    if existing:
        # Unsave (remove bookmark)
        db.delete(existing)
        db.commit()
        return {"bookmarked": False, "message": "Removed from saved items"}
    else:
        # Save (add bookmark)
        bookmark = models.Bookmark(
            user_id=current_user.id,
            content_type=content_type,
            content_id=content_id
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
        item = {"id": bm.id, "content_type": bm.content_type, "content_id": bm.content_id, "created_at": bm.created_at}
        
        if bm.content_type == 'mcq':
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
