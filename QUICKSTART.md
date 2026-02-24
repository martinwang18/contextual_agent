# Quick Start Guide

Get your Contextual Agent application running in minutes!

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (already installed)

## Option 1: Automated Setup (Recommended)

Run the setup script:

```bash
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Create configuration file
- Display next steps

Then start the application:

```bash
./run.sh
```

Open your browser and go to: **http://localhost:8080**

## Option 2: Manual Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

The `.env` file is already created in `config/.env` with default values.

**Optional**: Add real API keys for better results (see step 4)

### 4. Get API Keys (Optional but Recommended)

The app works with mock data by default, but real API keys provide actual results:

1. **OpenWeatherMap** (Weather data)
   - Sign up: https://openweathermap.org/api
   - Free tier: 1,000 calls/day
   - Add to `config/.env`: `WEATHER_API_KEY=your_key_here`

2. **NewsAPI** (News articles)
   - Sign up: https://newsapi.org/register
   - Free tier: 100 requests/day
   - Add to `config/.env`: `NEWS_API_KEY=your_key_here`

3. **Zipcodebase** (Zipcode to location)
   - Sign up: https://zipcodebase.com/
   - Free tier: 10,000 requests/month
   - Add to `config/.env`: `GEOCODING_API_KEY=your_key_here`

### 5. Run the Application

```bash
cd backend
python app.py
```

Or use the shortcut:

```bash
./run.sh
```

### 6. Open in Browser

Navigate to: **http://localhost:8080**

## Testing the Application

### Try These Examples

1. **New York City**
   - Zipcode: `10001`
   - Date: Today

2. **Los Angeles**
   - Zipcode: `90210`
   - Date: Today

3. **Chicago**
   - Zipcode: `60601`
   - Date: Today

### Expected Behavior

**Without API Keys** (Mock Data):
- Returns sample weather and news items
- Works for common zipcodes (10001, 90210, 60601, 02101, 98101)
- Demonstrates ranking algorithm

**With API Keys** (Real Data):
- Returns actual weather conditions and alerts
- Returns real news articles for the location
- More accurate and relevant results

## Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run unit tests
python -m pytest tests/

# Or run specific test
python tests/test_ranking.py
```

## Troubleshooting

### Port 8080 Already in Use

Change the port in `config/.env`:
```
PORT=8081
```

Then restart the application.

### Module Not Found Errors

Make sure you're in the virtual environment:
```bash
source venv/bin/activate
```

And dependencies are installed:
```bash
pip install -r requirements.txt
```

### API Errors

If you see API-related errors:
1. Check that your API keys are correct in `config/.env`
2. Verify you haven't exceeded rate limits
3. The app will fall back to mock data if APIs fail

### Empty Results

- Check that the zipcode is a valid 5-digit USA zipcode
- Try a different date (some dates may have limited news)
- Without API keys, only common test zipcodes work

## What's Next?

1. **Get API Keys**: For real data instead of mock data
2. **Explore the Code**: Check out the backend services in `backend/services/`
3. **Customize**: Modify the ranking algorithm in `backend/services/ranking_service.py`
4. **Add Features**: See `IMPLEMENTATION_PLAN.md` for enhancement ideas

## Project Structure

```
contextual_agent/
├── backend/               # Backend Python code
│   ├── app.py            # Main Flask application
│   ├── api/              # API endpoints
│   ├── services/         # Business logic
│   ├── models/           # Data models
│   └── utils/            # Utilities
├── frontend/             # Frontend web interface
│   ├── index.html        # Main page
│   ├── css/styles.css    # Styling
│   └── js/app.js         # JavaScript
├── config/               # Configuration
│   └── .env              # Environment variables
├── tests/                # Unit tests
├── setup.sh              # Automated setup script
└── run.sh                # Quick run script
```

## Need Help?

- Check **README.md** for detailed documentation
- See **API_GUIDE.md** for API integration details
- Review **IMPLEMENTATION_PLAN.md** for architecture info
- Open an issue on GitHub

## Development Mode

For development with auto-reload:

```bash
cd backend
FLASK_ENV=development python app.py
```

Or set in `config/.env`:
```
DEBUG=True
```

---

**Happy Coding! 🚀**
