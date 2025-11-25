# OAuth Setup Guide

This guide will help you set up social login (Google, GitHub, LinkedIn, Twitter) for your application.

## Prerequisites

- A deployed version of your app (or use `http://localhost:8000` for development)
- Developer accounts on the platforms you want to support

## Setup Steps

### 1. Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable "Google+ API"
4. Go to "Credentials" → "Create Credentials" → "OAuth client ID"
5. Configure consent screen with your app details
6. Choose "Web application" as application type
7. Add authorized redirect URI: `http://localhost:8000/api/auth/callback/google`
8. Copy `Client ID` and `Client Secret` to `.env` file

### 2. GitHub OAuth Setup

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Fill in:
   - **Application name**: Your app name
   - **Homepage URL**: `http://localhost:8000`
   - **Authorization callback URL**: `http://localhost:8000/api/auth/callback/github`
4. Click "Register application"
5. Copy `Client ID` and generate a `Client Secret`
6. Add to `.env` file

### 3. LinkedIn OAuth Setup

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/apps)
2. Click "Create app"
3. Fill in required details
4. Go to "Auth" tab
5. Add redirect URL: `http://localhost:8000/api/auth/callback/linkedin`
6. Copy `Client ID` and `Client Secret` to `.env` file

### 4. Twitter/X OAuth 2.0 Setup

1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create a new project and app
3. Go to app settings → "User authentication settings"
4. Enable "OAuth 2.0"
5. Add callback URL: `http://localhost:8000/api/auth/callback/twitter`
6. Copy `Client ID` and `Client Secret` to `.env` file

## Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Fill in your OAuth credentials in `.env`:
   ```bash
   GOOGLE_CLIENT_ID=your_actual_client_id
   GOOGLE_CLIENT_SECRET=your_actual_client_secret
   # ... etc for other providers
   ```

3. Update `APP_BASE_URL` for production:
   ```bash
   APP_BASE_URL=https://your-production-domain.com
   ```

4. Restart your backend server:
   ```bash
   ./start_server.sh
   ```

## Testing OAuth

1. Start your app: `./start_server.sh`
2. Go to `http://localhost:8000`
3. Click "Login" button
4. Try any social login button
5. You'll be redirected to the provider's login page
6. After authorization, you'll be redirected back with a token

## Production Deployment

When deploying to production:

1. Update all redirect URIs in each provider's settings to use your production domain
2. Update `APP_BASE_URL` in `.env` to your production URL
3. Use HTTPS for all callback URLs
4. Store secrets securely (use environment variables, not .env file in production)

## Troubleshooting

**Error: "redirect_uri_mismatch"**
- Make sure the redirect URI in your OAuth app settings exactly matches the one in the code

**Error: "OAuth provider not configured"**
- Check that CLIENT_ID and CLIENT_SECRET are set in .env
- Restart the server after updating .env

**Error: "Invalid state parameter"**
- This is a security check. Try logging in again
- In production, implement persistent state storage (Redis/database)

## Security Notes

- Never commit `.env` file to version control
- Use HTTPS in production
- Regularly rotate OAuth secrets
- Implement rate limiting for OAuth endpoints
- Store OAuth state in secure, persistent storage for production

## File Structure

```
backend/
├── auth/
│   ├── oauth_config.py      # Provider configurations
│   ├── oauth_handlers.py    # OAuth flow logic
│   └── oauth_routes.py      # FastAPI routes
frontend/
└── oauth_helper.js          # Frontend OAuth utilities
```
