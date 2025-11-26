import sys
import time
from fastapi import FastAPI
from a2wsgi import ASGIMiddleware

# 1. Create FastAPI App
print("DEBUG: Creating FastAPI app...")
app = FastAPI()

@app.get("/ping")
def ping():
    print("DEBUG: FastAPI /ping endpoint executed!")
    return {"status": "pong"}

# 2. Wrap with a2wsgi
print("DEBUG: Wrapping with a2wsgi...")
asgi_wrapper = ASGIMiddleware(app)

# 3. Create a custom WSGI handler to log requests
def application(environ, start_response):
    print(f"DEBUG: WSGI Request Received: {environ.get('PATH_INFO')}")
    
    try:
        # Call the a2wsgi wrapper
        print("DEBUG: Calling a2wsgi wrapper...")
        return asgi_wrapper(environ, start_response)
    except Exception as e:
        print(f"DEBUG: Exception in a2wsgi: {e}")
        raise e
