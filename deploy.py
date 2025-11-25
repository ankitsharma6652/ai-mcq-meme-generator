import os
import requests
import sys

# Configuration
USERNAME = os.environ.get('PA_USERNAME', '').strip()
API_TOKEN = os.environ.get('PA_API_TOKEN', '').strip()
DOMAIN = os.environ.get('PA_DOMAIN', '').strip()
BASE_URL = f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}"

if not all([USERNAME, API_TOKEN, DOMAIN]):
    print("❌ Missing environment variables (PA_USERNAME, PA_API_TOKEN, PA_DOMAIN)")
    sys.exit(1)

HEADERS = {'Authorization': f'Token {API_TOKEN}'}

# Get uploaded file path, repo path
repo_path = f'/home/{USERNAME}/ai-mcq-meme-generator'

try:
    # Pull latest code
    print(f"📥 Pulling latest code to {repo_path}...")
    response = requests.post(
        f'{BASE_URL}/consoles/{USERNAME}.pythonanywhere.com/send_input/',
        headers=HEADERS,
        json={'input': f'cd {repo_path} && git pull origin main\n'}
    )
    
    if response.status_code == 200:
        print("✅ Code pulled successfully")
    else:
        print(f"⚠️ Failed to pull code: {response.status_code}")
    
    # Reload web app
    print(f"🔄 Reloading {DOMAIN}...")
    response = requests.post(
        f'{BASE_URL}/webapps/{DOMAIN}/reload/',
        headers=HEADERS,
    )
    
    if response.status_code == 200:
        print("✅ Web app reloaded successfully")
    else:
        print(f"❌ Failed to reload: {response.status_code} - {response.text}")
        sys.exit(1)

except Exception as e:
    print(f"❌ Deployment error: {e}")
    sys.exit(1)
