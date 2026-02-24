# API Integration Guide

This document provides detailed information about the public APIs used in the Contextual Agent application, including setup instructions, rate limits, and example requests.

## Overview of Required APIs

| API | Purpose | Free Tier | Rate Limit (Free) |
|-----|---------|-----------|-------------------|
| OpenWeatherMap | Weather data & alerts | ✅ Yes | 60 calls/min, 1000 calls/day |
| NewsAPI | News articles & headlines | ✅ Yes | 100 requests/day |
| Zipcodebase / ZipCodeAPI | Zipcode to location mapping | ✅ Yes | 10,000/month |
| Weatherstack (Alternative) | Weather data | ✅ Yes | 1000 calls/month |
| The News API (Alternative) | News aggregation | ✅ Yes | 500 requests/day |

---

## 1. OpenWeatherMap API

### Purpose
Provides current weather, forecasts, and severe weather alerts for specific locations.

### Setup
1. Sign up at: https://openweathermap.org/api
2. Choose the **Free tier**
3. Generate API key from dashboard
4. Add to `.env`: `WEATHER_API_KEY=your_api_key_here`

### Documentation
- Main docs: https://openweathermap.org/api
- Current Weather: https://openweathermap.org/current
- Weather Alerts: https://openweathermap.org/api/one-call-api (One Call API 3.0)

### Example Request
```bash
# Get current weather by coordinates
GET https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=imperial

# Get weather alerts (One Call API)
GET https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={API_KEY}&exclude=minutely,hourly
```

### Response Example
```json
{
  "weather": [{"main": "Rain", "description": "light rain"}],
  "main": {
    "temp": 68.5,
    "feels_like": 67.8,
    "humidity": 72
  },
  "alerts": [
    {
      "event": "Severe Thunderstorm Warning",
      "description": "...",
      "start": 1234567890,
      "end": 1234567890
    }
  ]
}
```

### Rate Limits
- Free tier: 60 calls/minute, 1,000 calls/day
- Consider caching responses for same location/day

---

## 2. NewsAPI

### Purpose
Aggregates news articles from various sources, searchable by keyword, location, and date.

### Setup
1. Sign up at: https://newsapi.org/register
2. Get your API key
3. Add to `.env`: `NEWS_API_KEY=your_api_key_here`

### Documentation
- Main docs: https://newsapi.org/docs
- Everything endpoint: https://newsapi.org/docs/endpoints/everything
- Top headlines: https://newsapi.org/docs/endpoints/top-headlines

### Example Request
```bash
# Get news for a specific date and location
GET https://newsapi.org/v2/everything?q={city_name}&from={date}&to={date}&sortBy=relevancy&apiKey={API_KEY}

# Get top headlines by country
GET https://newsapi.org/v2/top-headlines?country=us&apiKey={API_KEY}
```

### Response Example
```json
{
  "status": "ok",
  "totalResults": 38,
  "articles": [
    {
      "source": {"name": "CNN"},
      "author": "John Doe",
      "title": "Breaking news headline",
      "description": "Article description...",
      "url": "https://...",
      "publishedAt": "2024-01-15T10:00:00Z"
    }
  ]
}
```

### Rate Limits
- Free tier: 100 requests/day
- Dev tier: Only articles from last 30 days
- Tip: Cache results and batch queries

---

## 3. Zipcodebase API

### Purpose
Convert USA zipcodes to city, state, coordinates, and timezone information.

### Setup
1. Sign up at: https://zipcodebase.com/
2. Get API key
3. Add to `.env`: `GEOCODING_API_KEY=your_api_key_here`

### Alternative: ZipCodeAPI.com
- URL: https://www.zipcodeapi.com/
- Free tier: 10 requests/hour

### Documentation
- Zipcodebase docs: https://zipcodebase.com/documentation

### Example Request
```bash
# Get location info from zipcode
GET https://app.zipcodebase.com/api/v1/search?apikey={API_KEY}&codes={zipcode}&country=US
```

### Response Example
```json
{
  "query": {
    "codes": ["10001"],
    "country": "US"
  },
  "results": {
    "10001": [
      {
        "postal_code": "10001",
        "country_code": "US",
        "latitude": "40.75021",
        "longitude": "-73.99698",
        "city": "New York",
        "state": "New York",
        "state_code": "NY"
      }
    ]
  }
}
```

### Rate Limits
- Free tier: 10,000 requests/month

---

## 4. Alternative: Google Geocoding API

### Purpose
Convert addresses and zipcodes to geographic coordinates (if needed).

### Setup
1. Enable Geocoding API in Google Cloud Console
2. Create credentials
3. Add to `.env`: `GOOGLE_GEOCODING_KEY=your_api_key_here`

### Documentation
- https://developers.google.com/maps/documentation/geocoding

### Example Request
```bash
GET https://maps.googleapis.com/maps/api/geocode/json?address={zipcode}&key={API_KEY}
```

### Rate Limits
- Free tier: $200 credit/month (~40,000 requests)

---

## 5. Eventbrite API (Optional for Local Events)

### Purpose
Fetch local events happening in specific areas.

### Setup
1. Sign up at: https://www.eventbrite.com/platform/
2. Create an app and get API token
3. Add to `.env`: `EVENTBRITE_TOKEN=your_token_here`

### Documentation
- https://www.eventbrite.com/platform/api

### Example Request
```bash
GET https://www.eventbriteapi.com/v3/events/search/?location.address={city}&location.within=25mi&token={TOKEN}
```

### Rate Limits
- 1000 requests per hour per token

---

## 6. Alternative News Sources

### MediaStack API
- URL: https://mediastack.com/
- Free tier: 500 requests/month
- Good for international news

### Currents API
- URL: https://currentsapi.services/
- Free tier: 600 requests/day
- News from multiple countries

### GNews API
- URL: https://gnews.io/
- Free tier: 100 requests/day
- Clean API, good documentation

---

## API Key Security Best Practices

### Do's
- ✅ Store API keys in `.env` file (never commit to Git)
- ✅ Add `.env` to `.gitignore`
- ✅ Use environment variables in code
- ✅ Rotate keys periodically
- ✅ Set up rate limiting in your application

### Don'ts
- ❌ Never hardcode API keys in source code
- ❌ Never commit API keys to version control
- ❌ Never expose keys in frontend JavaScript
- ❌ Never share keys in public forums

### Example .env File Structure
```bash
# Weather API
WEATHER_API_KEY=your_openweathermap_key_here

# News API
NEWS_API_KEY=your_newsapi_key_here

# Geocoding API
GEOCODING_API_KEY=your_geocoding_key_here

# Optional: Event APIs
EVENTBRITE_TOKEN=your_eventbrite_token_here

# App Configuration
PORT=8080
DEBUG=False
CACHE_TIMEOUT=300
```

---

## Rate Limiting Strategy

### Implementation Tips

1. **Caching**
   - Cache weather data for 1 hour per location
   - Cache news data for 30 minutes
   - Cache zipcode lookups indefinitely (they don't change)

2. **Request Batching**
   - Group similar API calls together
   - Make parallel requests where possible
   - Use async/await for better performance

3. **Fallback Strategies**
   - If primary API fails, try alternative
   - Return partial results if some APIs fail
   - Show cached data when APIs are rate-limited

4. **Monitoring**
   - Log API usage
   - Track rate limit headers
   - Alert when approaching limits

---

## Example Python Code

### Making API Requests
```python
import requests
import os
from dotenv import load_dotenv

load_dotenv('config/.env')

def get_weather(lat, lon):
    api_key = os.getenv('WEATHER_API_KEY')
    url = f"https://api.openweathermap.org/data/2.5/weather"
    params = {
        'lat': lat,
        'lon': lon,
        'appid': api_key,
        'units': 'imperial'
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather: {e}")
        return None

def get_news(city, date):
    api_key = os.getenv('NEWS_API_KEY')
    url = "https://newsapi.org/v2/everything"
    params = {
        'q': city,
        'from': date,
        'to': date,
        'sortBy': 'relevancy',
        'apiKey': api_key
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return None
```

---

## Testing API Connections

Before full implementation, test each API:

```bash
# Test OpenWeatherMap
curl "https://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_API_KEY"

# Test NewsAPI
curl "https://newsapi.org/v2/top-headlines?country=us&apiKey=YOUR_API_KEY"

# Test Zipcodebase
curl "https://app.zipcodebase.com/api/v1/search?apikey=YOUR_API_KEY&codes=10001&country=US"
```

---

## Cost Estimation (Free Tiers)

With conservative usage:
- **100 users/day** × 1 search each = 100 searches/day
- Each search makes ~4 API calls (zipcode, weather, news, events)
- Total: 400 API calls/day

This is well within free tier limits for all services.

---

## Support & Resources

- OpenWeatherMap Support: https://openweathermap.org/faq
- NewsAPI Support: https://newsapi.org/support
- Stack Overflow tags: #openweathermap #newsapi #api-integration
