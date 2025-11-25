#!/bin/bash
# API Keys are loaded from .env file (not committed to git)
# If you need to set them manually, create a .env file in the project root

# Enable unbuffered output for real-time logs
export PYTHONUNBUFFERED=1
venv/bin/uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
