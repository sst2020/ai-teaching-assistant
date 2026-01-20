#!/bin/bash

# Setup script for AI Teaching Assistant Backend Environment

echo "Creating conda environment with Python 3.11..."
conda create -n ai_teaching_assistant_backend python=3.11 -y

echo "Activating the environment..."
conda activate ai_teaching_assistant_backend

echo "Changing to backend directory..."
cd "$(dirname "$0")/backend"

echo "Installing production dependencies..."
pip install -r requirements-production.txt

echo "Environment setup complete!"
echo "To activate this environment in the future, run: conda activate ai_teaching_assistant_backend"
echo "Then navigate to the backend directory to run the application."