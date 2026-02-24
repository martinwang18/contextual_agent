#!/bin/bash

# Contextual Agent - Setup Script
# Automates the setup process for the application

set -e

echo "================================================"
echo "🚀 Contextual Agent - Setup Script"
echo "================================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Found Python $PYTHON_VERSION"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet
echo "✅ Dependencies installed"
echo ""

# Check if .env exists
if [ ! -f "config/.env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp config/.env.example config/.env
    echo "✅ .env file created at config/.env"
    echo ""
    echo "⚠️  IMPORTANT: Edit config/.env and add your API keys!"
    echo ""
else
    echo "ℹ️  .env file already exists at config/.env"
    echo ""
fi

# Summary
echo "================================================"
echo "✅ Setup Complete!"
echo "================================================"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Get API Keys (see API_GUIDE.md for instructions):"
echo "   - OpenWeatherMap: https://openweathermap.org/api"
echo "   - NewsAPI: https://newsapi.org/register"
echo "   - Zipcodebase: https://zipcodebase.com/"
echo ""
echo "2. Add your API keys to config/.env"
echo ""
echo "3. Run the application:"
echo "   source venv/bin/activate"
echo "   python backend/app.py"
echo ""
echo "4. Open your browser:"
echo "   http://localhost:8080"
echo ""
echo "================================================"
echo ""
echo "💡 Tip: The app will work with mock data if API keys are not set,"
echo "   but real API keys provide better results!"
echo ""
