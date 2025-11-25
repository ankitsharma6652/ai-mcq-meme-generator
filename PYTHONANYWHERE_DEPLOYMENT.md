# PythonAnywhere Deployment Guide

## Step 1: Create Account

1. Go to https://www.pythonanywhere.com/registration/register/beginner/
2. Create a **free Beginner account**
3. Choose a username (this will be your URL: `yourusername.pythonanywhere.com`)

## Step 2: Get Your Code (Clone from GitHub)

Since your code is now on GitHub, this is the best way!

1. **In PythonAnywhere:**
   - Click on the **Consoles** tab
   - Start a new **Bash console**
   - Run these commands:

```bash
# Clone your repository
git clone https://github.com/ankitsharma6652/ai-mcq-meme-generator.git

# Go into the directory
cd ai-mcq-meme-generator
```

## Step 3: Set Up Virtual Environment

In the same Bash console:

```bash
# Create virtual environment
python3.10 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 4: Set Up Database

```bash
# Create the database
python3 create_tables.py
```

## Step 5: Configure Web App

1. Go to the **Web** tab
2. Click **Add a new web app**
3. Choose **Manual configuration**
4. Select **Python 3.10**

### Configure WSGI File

1. Click on the **WSGI configuration file** link
2. **Delete all existing content**
3. **Paste this code:**

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/ai-mcq-meme-generator'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables (IMPORTANT: Update with your keys)
os.environ['GROQ_API_KEY'] = "YOUR_GROQ_API_KEY"
os.environ['REPLICATE_API_TOKEN'] = "YOUR_REPLICATE_API_TOKEN"
os.environ['HF_TOKEN'] = "YOUR_HF_TOKEN"

# Database URL
os.environ['DATABASE_URL'] = f"sqlite:///{project_home}/backend/meme_quiz_generator.db"

# Import the FastAPI app
from backend.main import app as application

# Wrap with ASGI middleware for PythonAnywhere
from a2wsgi import ASGIMiddleware
application = ASGIMiddleware(application)
```

**CRITICAL:** 
- Replace `YOUR_USERNAME` with your actual PythonAnywhere username.
- Replace `YOUR_GROQ_API_KEY`, etc. with your actual keys from your local `.env` file.

4. Click **Save**

### Configure Virtual Environment

1. In the **Web** tab, scroll to **Virtualenv** section
2. Enter the path: `/home/YOUR_USERNAME/ai-mcq-meme-generator/venv`
3. Click the checkmark

### Configure Static Files

1. Scroll to **Static files** section
2. Add these mappings:

| URL | Directory |
|-----|-----------|
| `/` | `/home/YOUR_USERNAME/ai-mcq-meme-generator/frontend` |

## Step 6: Set Up Superusers

In the Bash console:

```bash
cd ai-mcq-meme-generator
source venv/bin/activate
python3 -c "
from backend.database import SessionLocal
from backend.models import User

db = SessionLocal()

# Update your email to superuser
user = db.query(User).filter(User.email == 'digitalaks9@gmail.com').first()
if user:
    user.is_superuser = True
    db.commit()
    print('✅ Superuser set!')
else:
    print('❌ User not found. Please log in first via the web app.')

db.close()
"
```

## Step 7: Reload Web App

1. Go back to the **Web** tab
2. Click the big green **Reload** button
3. Wait for it to finish

## Step 8: Visit Your App!

Your app will be live at: `https://YOUR_USERNAME.pythonanywhere.com`

## Troubleshooting

### Check Error Logs

If the app doesn't work:
1. Go to **Web** tab
2. Scroll to **Log files**
3. Click on **Error log** to see what went wrong

### Common Issues

**Issue: "No module named 'backend'"**
- Fix: Make sure the WSGI file has the correct project path

**Issue: "Database locked"**
- Fix: In Bash console, run:
  ```bash
  cd ai-mcq-meme-generator/backend
  rm -f *.db-wal *.db-shm
  ```

**Issue: Static files not loading**
- Fix: Check that the static files path is correct in the Web tab

### Update Your App

When you make changes locally:
1. Push to GitHub: `git push`
2. In PythonAnywhere Bash console:
   ```bash
   cd ai-mcq-meme-generator
   git pull
   ```
3. Reload Web App

## Upgrade Options

If you need more resources:
- **Hacker Plan**: $5/month - More CPU, storage, custom domain
- **Web Developer Plan**: $12/month - Even more resources

---

Good luck with your deployment! 🚀
