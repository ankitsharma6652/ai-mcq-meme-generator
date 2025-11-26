"""
OAuth Configuration for Social Login Providers
Configure your OAuth credentials in environment variables or .env file
"""
import os
from typing import Dict

class OAuthProvider:
    def __init__(self, name: str, client_id: str, client_secret: str, 
                 authorize_url: str, token_url: str, user_info_url: str, scopes: list):
        self.name = name
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorize_url = authorize_url
        self.token_url = token_url
        self.user_info_url = user_info_url
        self.scopes = scopes



# Lazy provider initialization - reads env vars at runtime, not import time
def get_providers() -> Dict[str, OAuthProvider]:
    """Create providers dictionary with current environment variables"""
    return {
        "google": OAuthProvider(
            name="google",
            client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
            authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
            token_url="https://oauth2.googleapis.com/token",
            user_info_url="https://www.googleapis.com/oauth2/v2/userinfo",
            scopes=["openid", "email", "profile"]
        ),
        "github": OAuthProvider(
            name="github",
            client_id=os.getenv("GITHUB_CLIENT_ID", ""),
            client_secret=os.getenv("GITHUB_CLIENT_SECRET", ""),
            authorize_url="https://github.com/login/oauth/authorize",
            token_url="https://github.com/login/oauth/access_token",
            user_info_url="https://api.github.com/user",
            scopes=["user:email"]
        ),
        "linkedin": OAuthProvider(
            name="linkedin",
            client_id=os.getenv("LINKEDIN_CLIENT_ID", ""),
            client_secret=os.getenv("LINKEDIN_CLIENT_SECRET", ""),
            authorize_url="https://www.linkedin.com/oauth/v2/authorization",
            token_url="https://www.linkedin.com/oauth/v2/accessToken",
            user_info_url="https://api.linkedin.com/v2/me",
            scopes=["r_liteprofile", "r_emailaddress"]
        ),
        "twitter": OAuthProvider(
            name="twitter",
            client_id=os.getenv("TWITTER_CLIENT_ID", ""),
            client_secret=os.getenv("TWITTER_CLIENT_SECRET", ""),
            authorize_url="https://twitter.com/i/oauth2/authorize",
            token_url="https://api.twitter.com/2/oauth2/token",
            user_info_url="https://api.twitter.com/2/users/me",
            scopes=["tweet.read", "users.read"]
        )
    }

# Get redirect URI for your application
def get_redirect_uri(provider_name: str) -> str:
    """Generate redirect URI for OAuth callback"""
    base_url = os.getenv("APP_BASE_URL", "http://localhost:8000")
    return f"{base_url}/api/auth/callback/{provider_name}"
