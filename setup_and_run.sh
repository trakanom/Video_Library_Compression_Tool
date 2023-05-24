#!/bin/bash

# Update system
echo "Updating system..."
sudo apt update -y

# Install ffmpeg and ffprobe
echo "Installing ffmpeg and ffprobe..."
sudo apt install ffmpeg -y

# Set up Python environment
echo "Setting up Python environment..."
python3 -m venv env
source env/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Run the program
echo "Running the program..."
python app.py
