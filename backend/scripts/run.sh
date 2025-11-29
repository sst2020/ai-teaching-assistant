#!/bin/bash
# Run the development server (Unix/Linux/macOS)
cd "$(dirname "$0")/.."
python -m uvicorn app.main:app --reload --port 8000

