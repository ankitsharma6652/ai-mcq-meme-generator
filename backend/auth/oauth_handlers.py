"""
OAuth Authentication Handlers
Handles OAuth flows for social login providers
"""
import httpx
import secrets
from urllib.parse import urlencode
from fastapi import HTTPException
from typing import Dict, Optional
from auth.oauth_config import get_providers, get_redirect_uri

# Store for OAuth state tokens (in production, use Redis or database)
oauth_states = {}

def generate_oauth_url(provider_name: str) -> str:
    """
    Generate OAuth authorization URL for given provider
    """
    providers = get_providers()
    if provider_name not in providers:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider_name}")
    
    provider = providers[provider_name]
    
    if not provider.client_id:
        raise HTTPException(
            status_code=500, 
            detail=f"{provider_name.upper()}_CLIENT_ID not configured. Please set up OAuth credentials."
        )
    
    # Generate state token for CSRF protection
    state = secrets.token_urlsafe(32)
    oauth_states[state] = provider_name
    
    # Build authorization URL
    params = {
        "client_id": provider.client_id,
        "redirect_uri": get_redirect_uri(provider_name),
        "scope": " ".join(provider.scopes),
        "state": state,
        "response_type": "code"
    }
    
    # LinkedIn uses different parameter name
    if provider_name == "linkedin":
        params["response_type"] = "code"
    
    return f"{provider.authorize_url}?{urlencode(params)}"


async def exchange_code_for_token(provider_name: str, code: str) -> str:
    """
    Exchange authorization code for access token
    """
    providers = get_providers()
    if provider_name not in providers:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider_name}")
    
    provider = providers[provider_name]
    
    data = {
        "client_id": provider.client_id,
        "client_secret": provider.client_secret,
        "code": code,
        "redirect_uri": get_redirect_uri(provider_name),
        "grant_type": "authorization_code"
    }
    
    headers = {"Accept": "application/json"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(provider.token_url, data=data, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Failed to get access token from {provider_name}")
        
        token_data = response.json()
        return token_data.get("access_token")


async def get_user_info(provider_name: str, access_token: str) -> Dict:
    """
    Fetch user information from OAuth provider
    """
    providers = get_providers()
    if provider_name not in providers:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider_name}")
    
    provider = providers[provider_name]
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(provider.user_info_url, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Failed to get user info from {provider_name}")
        
        user_data = response.json()
        
        # Normalize user data across providers
        return normalize_user_data(provider_name, user_data)


def normalize_user_data(provider_name: str, raw_data: Dict) -> Dict:
    """
    Normalize user data from different providers into consistent format
    """
    normalized = {
        "provider": provider_name,
        "provider_user_id": None,
        "email": None,
        "full_name": None,
        "picture": None
    }
    
    if provider_name == "google":
        normalized["provider_user_id"] = raw_data.get("id")
        normalized["email"] = raw_data.get("email")
        normalized["full_name"] = raw_data.get("name")
        normalized["picture"] = raw_data.get("picture")
    
    elif provider_name == "github":
        normalized["provider_user_id"] = str(raw_data.get("id"))
        normalized["email"] = raw_data.get("email")
        normalized["full_name"] = raw_data.get("name") or raw_data.get("login")
        normalized["picture"] = raw_data.get("avatar_url")
    
    elif provider_name == "linkedin":
        normalized["provider_user_id"] = raw_data.get("id")
        # LinkedIn requires separate API call for email
        normalized["email"] = raw_data.get("email")  # Will need to fetch separately
        first_name = raw_data.get("localizedFirstName", "")
        last_name = raw_data.get("localizedLastName", "")
        normalized["full_name"] = f"{first_name} {last_name}".strip()
        normalized["picture"] = None  # LinkedIn profile pictures require separate call
    
    elif provider_name == "twitter":
        normalized["provider_user_id"] = raw_data.get("data", {}).get("id")
        normalized["email"] = raw_data.get("email")  # Requires additional scope
        normalized["full_name"] = raw_data.get("data", {}).get("name")
        normalized["picture"] = raw_data.get("data", {}).get("profile_image_url")
    
    return normalized


def verify_state(state: str) -> Optional[str]:
    """
    Verify OAuth state token to prevent CSRF attacks
    """
    return oauth_states.pop(state, None)
