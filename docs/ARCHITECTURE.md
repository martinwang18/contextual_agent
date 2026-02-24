# System Architecture Documentation

## Overview
The Contextual Agent is a web-based application that aggregates and ranks contextual information from multiple public APIs to provide users with the most relevant events and information for a specific location and date.

## Architecture Pattern
**Pattern**: Layered Architecture (3-tier)

```
┌─────────────────────────────────────┐
│     Presentation Layer              │  ← Frontend (HTML/CSS/JS)
├─────────────────────────────────────┤
│     Application Layer               │  ← Backend (Flask API + Services)
├─────────────────────────────────────┤
│     Data Layer                      │  ← External APIs + Cache
└─────────────────────────────────────┘
```

## Component Breakdown

### 1. Presentation Layer (Frontend)

**Responsibilities**:
- User input collection and validation
- Display results in ranked order
- Error message display
- Loading states

**Technologies**:
- HTML5 for structure
- CSS3 for styling
- Vanilla JavaScript for interactivity
- Fetch API for HTTP requests

**Key Files**:
- `frontend/index.html` - Main interface
- `frontend/css/styles.css` - Styling
- `frontend/js/app.js` - Client-side logic

### 2. Application Layer (Backend)

#### 2.1 API Routes (`backend/api/routes.py`)
**Responsibilities**:
- HTTP request handling
- Input validation
- Response formatting
- Error handling

**Endpoints**:
```
POST /api/search
  Request: {date: string, zipcode: string}
  Response: {status, query, results[], metadata}

GET /api/health
  Response: {status: "ok"}
```

#### 2.2 Service Layer (`backend/services/`)
**Responsibilities**:
- Business logic execution
- External API integration
- Data transformation
- Caching

**Services**:

##### GeocodingService
```python
class GeocodingService:
    def get_location(zipcode: str) -> Location:
        """Convert zipcode to city, state, coordinates"""
```

##### WeatherService
```python
class WeatherService:
    def get_weather(lat, lon, date) -> WeatherData:
        """Fetch weather conditions"""

    def get_alerts(lat, lon) -> List[Alert]:
        """Fetch active weather alerts"""
```

##### NewsService
```python
class NewsService:
    def get_local_news(city, state, date) -> List[Article]:
        """Fetch local news"""

    def get_global_news(date) -> List[Article]:
        """Fetch global news"""
```

##### RankingService
```python
class RankingService:
    def score_item(item) -> float:
        """Calculate relevance score"""

    def rank_items(items) -> List[Item]:
        """Sort and return top 5"""
```

#### 2.3 Models (`backend/models/`)
**Responsibilities**:
- Data structure definitions
- Type validation
- Serialization

**Classes**:
```python
class Location:
    zipcode: str
    city: str
    state: str
    latitude: float
    longitude: float

class ContextualItem:
    title: str
    description: str
    category: str
    score: float
    source: str
    timestamp: datetime
    metadata: dict

class SearchResult:
    query: dict
    results: List[ContextualItem]
    metadata: dict
```

### 3. Data Layer

#### 3.1 External APIs
- **OpenWeatherMap**: Weather data + alerts
- **NewsAPI**: News articles
- **Zipcodebase**: Geocoding
- **Eventbrite** (optional): Local events

#### 3.2 Cache Layer (`backend/utils/cache.py`)
**Purpose**: Reduce API calls and improve response time

**Strategy**:
```python
class CacheManager:
    # TTL (Time To Live) in seconds
    WEATHER_TTL = 3600      # 1 hour
    NEWS_TTL = 1800         # 30 minutes
    GEOCODING_TTL = 86400   # 24 hours

    def get(key):
        """Retrieve from cache"""

    def set(key, value, ttl):
        """Store in cache with expiration"""

    def invalidate(key):
        """Remove from cache"""
```

## Data Flow Sequence

### Successful Request Flow

```
User                Frontend            Backend API         Services            External APIs
  |                     |                    |                  |                      |
  |--Enter date/zip---->|                    |                  |                      |
  |                     |                    |                  |                      |
  |                     |--POST /api/search->|                  |                      |
  |                     |                    |                  |                      |
  |                     |                    |--validate input->|                      |
  |                     |                    |                  |                      |
  |                     |                    |                  |--get_location()----->|
  |                     |                    |                  |<----{city,lat,lon}---|
  |                     |                    |                  |                      |
  |                     |                    |                  |--get_weather()------>|
  |                     |                    |                  |--get_news()--------->|
  |                     |                    |                  |--get_events()------->|
  |                     |                    |                  |<----weather_data-----|
  |                     |                    |                  |<----news_articles----|
  |                     |                    |                  |<----events_list------|
  |                     |                    |                  |                      |
  |                     |                    |                  |--rank_items()        |
  |                     |                    |                  |                      |
  |                     |                    |<--top 5 results--|                      |
  |                     |<--JSON response----|                  |                      |
  |                     |                    |                  |                      |
  |<--Display results---|                    |                  |                      |
  |                     |                    |                  |                      |
```

### Error Handling Flow

```
Frontend                Backend                 External API
   |                       |                         |
   |----POST /api/search-->|                         |
   |                       |----request data-------->|
   |                       |                         X (timeout/error)
   |                       |<----error response------|
   |                       |                         |
   |                       |--try alternative API--->|
   |                       |<----success-------------|
   |                       |                         |
   |<--partial results-----|                         |
   |                       |                         |
```

## Ranking Algorithm

### Scoring Matrix

| Category | Base Score | Modifiers |
|----------|------------|-----------|
| Weather Alert | 90-100 | +10 for severity=high |
| Severe Weather | 80-90 | +5 for temperature extreme |
| Local Event (today) | 75-85 | +5 for high attendance |
| Local News | 60-75 | +10 for breaking news |
| Normal Weather | 40-50 | -5 for common conditions |
| Regional News | 50-60 | +5 for regional impact |
| Global News | 40-55 | +10 if affects local area |

### Ranking Logic
```python
def calculate_score(item):
    base_score = CATEGORY_SCORES[item.category]

    # Geographic relevance
    if item.is_local:
        base_score += 15
    elif item.is_regional:
        base_score += 5

    # Temporal relevance
    if item.date == query_date:
        base_score += 10

    # Severity/Impact
    if item.severity == 'high':
        base_score += 10
    elif item.severity == 'medium':
        base_score += 5

    # Breaking news bonus
    if item.is_breaking:
        base_score += 5

    return min(base_score, 100)
```

### Tie Breaking
When items have the same score:
1. Prefer local over regional over global
2. Prefer more recent timestamps
3. Prefer items with higher engagement (if available)

## Security Considerations

### Input Validation
- Zipcode: Must be exactly 5 digits, valid USA zipcode
- Date: Must be valid ISO format (YYYY-MM-DD)
- Sanitize all user inputs to prevent injection

### API Key Management
- Store in environment variables only
- Never commit to version control
- Rotate keys periodically
- Use different keys for dev/prod

### Rate Limiting
```python
# Limit requests per IP
@limiter.limit("30 per minute")
def search():
    # ...
```

### CORS Configuration
```python
# Only allow specific origins
CORS(app, origins=[
    'http://localhost:8080',
    'https://yourdomain.com'
])
```

## Performance Optimization

### Caching Strategy
1. **Geocoding**: Cache indefinitely (zipcodes don't change)
2. **Weather**: Cache for 1 hour
3. **News**: Cache for 30 minutes
4. **Events**: Cache for 24 hours

### Parallel API Calls
```python
import asyncio

async def gather_data(location, date):
    tasks = [
        get_weather(location),
        get_news(location, date),
        get_events(location, date)
    ]
    results = await asyncio.gather(*tasks)
    return results
```

### Response Time Targets
- Geocoding: < 200ms
- Each API call: < 1s
- Total response time: < 3s
- Frontend render: < 500ms

## Scalability Considerations

### Current Architecture Limitations
- Single-server deployment
- In-memory caching (lost on restart)
- Synchronous request handling

### Future Enhancements
1. **Horizontal Scaling**
   - Deploy multiple server instances
   - Use load balancer (nginx, AWS ELB)

2. **Distributed Caching**
   - Replace in-memory cache with Redis
   - Share cache across instances

3. **Async Processing**
   - Use Celery for background tasks
   - Queue non-critical API calls

4. **Database Integration**
   - Store user preferences
   - Cache historical data
   - Analytics and logging

## Monitoring & Observability

### Logging Strategy
```python
import logging

# Log levels by environment
if ENVIRONMENT == 'production':
    logging.basicConfig(level=logging.WARNING)
else:
    logging.basicConfig(level=logging.DEBUG)

# Log format
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Metrics to Track
- Request count per endpoint
- Response time (p50, p95, p99)
- API failure rate
- Cache hit ratio
- Error rate by type

### Health Checks
```python
@app.route('/api/health')
def health_check():
    return {
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'weather': check_weather_api(),
            'news': check_news_api(),
            'geocoding': check_geocoding_api()
        }
    }
```

## Testing Strategy

### Unit Tests
- Test each service independently
- Mock external API calls
- Test ranking algorithm logic

### Integration Tests
- Test API endpoints
- Test service coordination
- Test error handling

### End-to-End Tests
- Simulate user workflows
- Test with real API calls (limited)
- Validate UI rendering

## Deployment Architecture

### Development
```
localhost:8080 → Flask dev server → External APIs
```

### Production (Future)
```
Internet → Load Balancer → [App Server 1, App Server 2, ...] → Redis Cache → External APIs
                         ↓
                    PostgreSQL (optional)
```

## Technology Decisions

### Why Flask?
- Lightweight and simple
- Excellent for APIs
- Large ecosystem
- Easy to learn

### Why Vanilla JavaScript?
- No build step required
- Fast and lightweight
- Sufficient for MVP
- Easy to upgrade to React later

### Why In-Memory Cache?
- Simple to implement
- No external dependencies
- Sufficient for single-server MVP
- Easy to upgrade to Redis

## References

- Flask Documentation: https://flask.palletsprojects.com/
- REST API Best Practices: https://restfulapi.net/
- OpenWeatherMap API: https://openweathermap.org/api
- NewsAPI Documentation: https://newsapi.org/docs
