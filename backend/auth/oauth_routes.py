"""
OAuth API Routes
FastAPI endpoints for OAuth authentication
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional

from auth import oauth_handlers
from auth import core as auth
import schemas, models
from database import get_db
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["OAuth Authentication"])


@router.get("/login/{provider}")
async def oauth_login(provider: str):
    """
    Initiate OAuth flow for specified provider
    Returns redirect URL to provider's authorization page
    """
    try:
        logger.info(f"Initiating OAuth login for provider: {provider}")
        auth_url = oauth_handlers.generate_oauth_url(provider)
        logger.info(f"Generated auth URL: {auth_url}")
        return {"authorization_url": auth_url}
    except Exception as e:
        logger.error(f"Error generating OAuth URL: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/callback/{provider}")
async def oauth_callback(
    provider: str,
    code: str,
    state: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    OAuth callback endpoint
    Handles the redirect from OAuth provider after user authorizes
    """
    logger.info(f"Received OAuth callback for provider: {provider}")
    
    # Verify state to prevent CSRF
    verified_provider = oauth_handlers.verify_state(state)
    if not verified_provider or verified_provider != provider:
        logger.error(f"Invalid state parameter. Received: {state}")
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    try:
        # Exchange code for access token
        logger.info("Exchanging code for access token...")
        access_token = await oauth_handlers.exchange_code_for_token(provider, code)
        logger.info("Successfully obtained access token")
        
        # Get user info from provider
        logger.info("Fetching user info from provider...")
        user_info = await oauth_handlers.get_user_info(provider, access_token)
        logger.info(f"Got user info: {user_info}")
        
        # Find or create user in database
        user = get_or_create_oauth_user(db, user_info)
        logger.info(f"User created/found: {user.email}, ID: {user.id}")
        
        # Generate JWT token for our application
        app_access_token = auth.create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # Log login activity
        import main
        log_activity = main.log_activity
        log_activity(db, user.id, "oauth_login", {
            "provider": provider,
            "provider_user_id": user_info.get("provider_user_id")
        })
        
        # Create UserLoginHistory record
        login_record = models.UserLoginHistory(
            user_id=user.id,
            email=user.email,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get('user-agent', None),
            auth_provider=provider
        )
        db.add(login_record)
        db.commit()
        
        # Redirect to frontend with token
        # Use APP_BASE_URL from environment, default to localhost if not set (but prefer env)
        app_base_url = os.environ.get("APP_BASE_URL", "http://localhost:8000")
        # Remove trailing slash if present to avoid double slashes
        if app_base_url.endswith('/'):
            app_base_url = app_base_url[:-1]
            
        frontend_url = f"{app_base_url}/?token={app_access_token}&provider={provider}"
        logger.info(f"Redirecting to frontend: {frontend_url}")
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        logger.error(f"ERROR in OAuth callback: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"OAuth authentication failed: {str(e)}")


def get_or_create_oauth_user(db: Session, user_info: dict) -> models.User:
    """
    Find existing user by email or create new user from OAuth data
    """
    email = user_info.get("email")
    
    if not email:
        # Some providers might not return email
        # Use provider ID as fallback
        email = f"{user_info['provider']}_{user_info['provider_user_id']}@oauth.local"
    
    # Check if user exists
    user = auth.get_user_by_email(db, email)
    
    if not user:
        # Create new user without password (OAuth users don't need one)
        user_create = schemas.UserCreate(
            email=email,
            password=None,  # OAuth users don't have passwords
            full_name=user_info.get("full_name") or email.split("@")[0],
            phone_number=None
        )
        
        user = auth.create_user(db, user_create)
        
        # Save profile picture from OAuth provider
        if user_info.get("picture"):
            user.profile_picture = user_info.get("picture")
            db.commit()
            db.refresh(user)
        # TODO: Store OAuth provider info in social_accounts table if needed
    else:
        # Update profile picture if it changed
        if user_info.get("picture") and not user.profile_picture:
            user.profile_picture = user_info.get("picture")
            db.commit()
            db.refresh(user)
    
    return user
