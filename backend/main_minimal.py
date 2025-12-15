from fastapi import FastAPI
import sys

app = FastAPI()

@app.get("/ping")
def ping():
    return {"status": "pong", "python": sys.version}

@app.get("/")
def root():
    return {"message": "Minimal app is working!"}
