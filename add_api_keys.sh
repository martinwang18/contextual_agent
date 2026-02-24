#!/bin/bash

# Helper script to add API keys to .env file
# Usage: ./add_api_keys.sh

echo "================================================"
echo "🔑 Contextual Agent - API Key Setup"
echo "================================================"
echo ""
echo "This script will help you add your API keys to config/.env"
echo ""
echo "📚 First, get your free API keys:"
echo "   See docs/GET_API_KEYS.md for detailed instructions"
echo ""
echo "   1. OpenWeatherMap: https://openweathermap.org/api"
echo "   2. NewsAPI: https://newsapi.org/register"
echo "   3. Zipcodebase: https://zipcodebase.com/"
echo ""
echo "================================================"
echo ""

# Check if .env exists
if [ ! -f "config/.env" ]; then
    echo "❌ config/.env not found!"
    echo "   Creating from template..."
    cp config/.env.example config/.env
fi

echo "Enter your API keys (press Enter to skip any):"
echo ""

# OpenWeatherMap
read -p "🌤️  OpenWeatherMap API Key: " WEATHER_KEY
if [ ! -z "$WEATHER_KEY" ]; then
    sed -i.bak "s/^WEATHER_API_KEY=.*/WEATHER_API_KEY=$WEATHER_KEY/" config/.env
    echo "   ✅ Weather API key added"
fi

# NewsAPI
read -p "📰 NewsAPI Key: " NEWS_KEY
if [ ! -z "$NEWS_KEY" ]; then
    sed -i.bak "s/^NEWS_API_KEY=.*/NEWS_API_KEY=$NEWS_KEY/" config/.env
    echo "   ✅ News API key added"
fi

# Zipcodebase
read -p "📍 Zipcodebase API Key: " GEO_KEY
if [ ! -z "$GEO_KEY" ]; then
    sed -i.bak "s/^GEOCODING_API_KEY=.*/GEOCODING_API_KEY=$GEO_KEY/" config/.env
    echo "   ✅ Geocoding API key added"
fi

# Clean up backup file
rm -f config/.env.bak

echo ""
echo "================================================"
echo "✅ Configuration Updated!"
echo "================================================"
echo ""
echo "Next steps:"
echo "  1. Start the application: ./run.sh"
echo "  2. Open http://localhost:8080"
echo "  3. Try any USA zipcode (not just test ones!)"
echo ""
echo "You should now see real weather and news data!"
echo ""
