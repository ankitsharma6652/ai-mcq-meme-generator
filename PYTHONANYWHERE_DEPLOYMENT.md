# PythonAnywhere Deployment Guide

## Step 1: Create Account

1. Go to https://www.pythonanywhere.com/registration/register/beginner/
2. Create a **free Beginner account**
3. Choose a username (this will be your URL: `yourusername.pythonanywhere.com`)
   - Suggested: `memucate` or `quizmeme` or `ankitsharma6652`

## Step 2: Upload Your Code

### Option A: Upload ZIP File (Easiest)

1. **Download the ZIP file** from your local machine:
   - Location: `/Users/ankit-sharma/Downloads/ai-mcq-meme-generator/ai-mcq-meme-generator.zip`

2. **In PythonAnywhere:**
   - Click on the **Files** tab
   - Click **Upload a file**
   - Select `ai-mcq-meme-generator.zip`
   - Wait for upload to complete

3. **Extract the ZIP:**
   - Click on **Consoles** tab
   - Start a new **Bash console**
   - Run:
     ```bash
     unzip ai-mcq-meme-generator.zip -d ai-mcq-meme-generator
     cd ai-mcq-meme-generator
     ```

### Option B: Clone from GitHub (If you get GitHub working)

```bash
git clone https://github.com/ankitsharma6652/ai-mcq-meme-generator.git
cd ai-mcq-meme-generator
```

## Step 3: Set Up Virtual Environment

In the Bash console:

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

# Set environment variables
os.environ['DATABASE_URL'] = f"sqlite:///{project_home}/backend/mcq_meme_v2.db"

# Import the FastAPI app
from backend.main import app as application

# Wrap with ASGI middleware for PythonAnywhere
from a2wsgi import ASGIMiddleware
application = ASGIMiddleware(application)
```

**Important:** Replace `YOUR_USERNAME` with your actual PythonAnywhere username!

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

When you make changes:
1. Upload new files via **Files** tab
2. Click **Reload** in **Web** tab

## Environment Variables (Optional)

If you need to set environment variables:
1. Go to **Web** tab
2. Scroll to **Environment variables**
3. Add:
   - `GROQ_API_KEY`: Your Groq API key
   - `DATABASE_URL`: `sqlite:///./mcq_meme_v2.db`

## Free Tier Limitations

- Your app will sleep after inactivity
- Limited CPU seconds per day
- 512 MB storage
- No custom domain (unless you upgrade)

## Upgrade Options

If you need more resources:
- **Hacker Plan**: $5/month - More CPU, storage, custom domain
- **Web Developer Plan**: $12/month - Even more resources

---

## Quick Reference

**Your App URL:** `https://YOUR_USERNAME.pythonanywhere.com`
**Admin Panel:** `https://YOUR_USERNAME.pythonanywhere.com/admin`
**Files Location:** `/home/YOUR_USERNAME/ai-mcq-meme-generator`

---

Good luck with your deployment! 🚀
