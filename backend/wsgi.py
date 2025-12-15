import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/ai-mcq-meme-generator'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables (Or set them in the WSGI configuration tab)
os.environ['DATABASE_URL'] = f"sqlite:///{project_home}/backend/mcq_meme.db"

# Import the FastAPI app
from backend.main import app as application

# PythonAnywhere uses WSGI, but FastAPI is ASGI.
# We need to wrap it using a2wsgi or similar if we want to run it via the Web tab.
# However, standard FastAPI deployment on PA often uses a worker class or just the WSGI adapter.

from fastapi.middleware.wsgi import WSGIMiddleware
from a2wsgi import ASGIMiddleware

# Wrap the ASGI app with ASGIMiddleware to make it WSGI compatible
application = ASGIMiddleware(application)
