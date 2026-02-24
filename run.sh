#!/bin/bash

# Contextual Agent - Run Script
# Quick script to start the application

set -e

echo "🚀 Starting Contextual Agent..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f "config/.env" ]; then
    echo "⚠️  Warning: config/.env not found. Using mock data."
    echo ""
fi

# Change to backend directory and run
cd backend
python app.py
