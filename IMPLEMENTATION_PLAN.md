# Implementation Plan & Architecture

This document outlines the step-by-step implementation plan and system architecture for the Contextual Agent application.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│                      (Frontend - Browser)                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Date Input  │  Zipcode Input  │  [Search Button]        │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Results Display Area                         │  │
│  │  1. [Weather Alert] 🌩️  Score: 95                        │  │
│  │  2. [Local Event] 🎉     Score: 85                        │  │
│  │  3. [News Story] 📰      Score: 78                        │  │
│  │  4. [Weather Info] 🌤️   Score: 65                        │  │
│  │  5. [Global Event] 🌍    Score: 60                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP Request (POST /api/search)
                            │ {date: "2024-01-15", zipcode: "10001"}
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND SERVER (Flask/Express)                │
│                         localhost:8080                           │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              API Routes (api/)                             │ │
│  │  - POST /api/search    → Main search endpoint             │ │
│  │  - GET  /api/health    → Health check                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            ↓                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         Controller Layer (services/)                       │ │
│  │  • Input Validation                                        │ │
│  │  • Orchestrate API calls                                   │ │
│  │  • Data aggregation                                        │ │
│  └────────────────────────────────────────────────────────────┘ │
│         ↓              ↓              ↓              ↓           │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐    │
│  │ Geocoding│   │ Weather  │   │   News   │   │  Events  │    │
│  │ Service  │   │ Service  │   │ Service  │   │ Service  │    │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘    │
│         ↓              ↓              ↓              ↓           │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Ranking Engine (services/)                    │ │
│  │  • Score each item based on relevance                      │ │
│  │  • Apply weights (local > regional > global)               │ │
│  │  • Sort and return top 5                                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            ↓                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Cache Layer (Optional)                        │ │
│  │  • In-memory cache for repeated queries                    │ │
│  │  • TTL: 1 hour for weather, 30 min for news               │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │ External API Calls
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL APIS (Public)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Zipcodebase  │  │OpenWeatherMap│  │   NewsAPI    │          │
│  │              │  │              │  │              │          │
│  │ Zipcode → Geo│  │Weather + Alert│  │News Articles │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Request Flow
1. User enters date and zipcode → Frontend validation
2. POST request to `/api/search` with `{date, zipcode}`
3. Backend validates input
4. Geocoding service converts zipcode → `{city, state, lat, lon}`
5. Parallel API calls:
   - Weather service → get weather + alerts
   - News service → get local + global news
   - Events service → get local events (optional)
6. Ranking engine scores all items
7. Top 5 items returned to frontend
8. Frontend displays results

### Response Format
```json
{
  "status": "success",
  "query": {
    "date": "2024-01-15",
    "zipcode": "10001",
    "location": "New York, NY"
  },
  "results": [
    {
      "rank": 1,
      "category": "weather_alert",
      "title": "Severe Thunderstorm Warning",
      "description": "Severe thunderstorm warning in effect until 8 PM EST",
      "score": 95,
      "source": "OpenWeatherMap",
      "timestamp": "2024-01-15T14:30:00Z",
      "metadata": {
        "severity": "high",
        "expires": "2024-01-15T20:00:00Z"
      }
    },
    {
      "rank": 2,
      "category": "local_event",
      "title": "City Marathon - Road Closures",
      "description": "Annual marathon causing road closures downtown",
      "score": 85,
      "source": "Local News",
      "timestamp": "2024-01-15T06:00:00Z",
      "metadata": {
        "location": "Downtown New York"
      }
    }
    // ... 3 more items
  ],
  "metadata": {
    "total_items_analyzed": 47,
    "response_time_ms": 1243
  }
}
```

---

## Implementation Phases

### Phase 1: Project Setup (Week 1)
**Goal**: Set up development environment and basic structure

**Tasks**:
- [ ] Set up Git repository ✅ (Already done)
- [ ] Create virtual environment
- [ ] Install dependencies
- [ ] Create folder structure ✅ (Already done)
- [ ] Set up `.env` configuration
- [ ] Register for API keys
- [ ] Test API connections

**Deliverables**:
- Working dev environment
- All API keys obtained and tested
- Basic project skeleton

**Files to create**:
```
config/.env.example
requirements.txt or package.json
.gitignore
```

---

### Phase 2: Backend Foundation (Week 1-2)
**Goal**: Build core backend with API integrations

#### Task 2.1: Set up Flask/Express Server
**Files to create**:
- `backend/app.py` (main application file)
- `backend/api/routes.py` (API endpoints)
- `backend/utils/config.py` (configuration loader)

**Key endpoints**:
```python
# backend/app.py (Flask example)
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/search', methods=['POST'])
def search():
    # Main search endpoint
    pass

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
```

#### Task 2.2: Implement Service Layer
**Files to create**:
- `backend/services/geocoding_service.py`
- `backend/services/weather_service.py`
- `backend/services/news_service.py`
- `backend/services/events_service.py` (optional)

**Example service structure**:
```python
# backend/services/weather_service.py
import requests
import os

class WeatherService:
    def __init__(self):
        self.api_key = os.getenv('WEATHER_API_KEY')
        self.base_url = "https://api.openweathermap.org/data/2.5"

    def get_weather(self, lat, lon, date=None):
        """Fetch weather data for coordinates"""
        # Implementation here
        pass

    def get_alerts(self, lat, lon):
        """Fetch weather alerts"""
        # Implementation here
        pass
```

#### Task 2.3: Implement Ranking Engine
**Files to create**:
- `backend/services/ranking_service.py`
- `backend/models/item.py` (data model for ranked items)

**Ranking logic**:
```python
# backend/services/ranking_service.py
class RankingService:
    # Scoring weights
    WEIGHTS = {
        'weather_alert': 95,
        'severe_weather': 85,
        'local_event_today': 80,
        'local_news': 70,
        'normal_weather': 50,
        'regional_news': 60,
        'global_news': 45
    }

    def score_item(self, item):
        """Calculate relevance score for an item"""
        base_score = self.WEIGHTS.get(item['category'], 50)

        # Apply modifiers
        if item.get('severity') == 'high':
            base_score += 10

        if item.get('is_breaking'):
            base_score += 5

        return min(base_score, 100)

    def rank_items(self, items):
        """Sort items by score and return top 5"""
        scored_items = []
        for item in items:
            item['score'] = self.score_item(item)
            scored_items.append(item)

        scored_items.sort(key=lambda x: x['score'], reverse=True)
        return scored_items[:5]
```

**Deliverables**:
- Working backend server on localhost:8080
- All service integrations functional
- Ranking algorithm implemented

---

### Phase 3: Frontend Development (Week 2)
**Goal**: Create user interface

**Files to create**:
- `frontend/index.html`
- `frontend/css/styles.css`
- `frontend/js/app.js`

#### Task 3.1: HTML Structure
```html
<!-- frontend/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contextual Agent</title>
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 Contextual Agent</h1>
            <p>Discover what matters most for your location and date</p>
        </header>

        <main>
            <form id="searchForm">
                <div class="form-group">
                    <label for="date">Date</label>
                    <input type="date" id="date" required>
                </div>

                <div class="form-group">
                    <label for="zipcode">Zipcode (USA)</label>
                    <input type="text" id="zipcode" pattern="[0-9]{5}"
                           placeholder="e.g., 10001" required>
                </div>

                <button type="submit">Get Trending Items</button>
            </form>

            <div id="loading" class="hidden">
                <div class="spinner"></div>
                <p>Analyzing contextual data...</p>
            </div>

            <div id="results" class="hidden">
                <h2>Top 5 Trending Items</h2>
                <div id="resultsList"></div>
            </div>

            <div id="error" class="hidden"></div>
        </main>
    </div>

    <script src="js/app.js"></script>
</body>
</html>
```

#### Task 3.2: JavaScript Logic
```javascript
// frontend/js/app.js
const API_BASE = 'http://localhost:8080/api';

document.getElementById('searchForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const date = document.getElementById('date').value;
    const zipcode = document.getElementById('zipcode').value;

    // Show loading, hide results/error
    toggleLoading(true);

    try {
        const response = await fetch(`${API_BASE}/search`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ date, zipcode })
        });

        if (!response.ok) throw new Error('Search failed');

        const data = await response.json();
        displayResults(data.results);

    } catch (error) {
        showError('Unable to fetch results. Please try again.');
    } finally {
        toggleLoading(false);
    }
});

function displayResults(results) {
    const container = document.getElementById('resultsList');
    container.innerHTML = '';

    results.forEach((item, index) => {
        const card = createResultCard(item, index + 1);
        container.appendChild(card);
    });

    document.getElementById('results').classList.remove('hidden');
}

function createResultCard(item, rank) {
    const card = document.createElement('div');
    card.className = 'result-card';
    card.innerHTML = `
        <div class="rank">${rank}</div>
        <div class="content">
            <h3>${getCategoryIcon(item.category)} ${item.title}</h3>
            <p>${item.description}</p>
            <div class="meta">
                <span class="category">${item.category}</span>
                <span class="score">Score: ${item.score}</span>
                <span class="source">${item.source}</span>
            </div>
        </div>
    `;
    return card;
}

function getCategoryIcon(category) {
    const icons = {
        'weather_alert': '⚠️',
        'local_event': '🎉',
        'weather': '🌤️',
        'local_news': '📰',
        'global_news': '🌍'
    };
    return icons[category] || '📌';
}
```

**Deliverables**:
- Functional web interface
- Form validation
- Results display
- Error handling

---

### Phase 4: Testing & Refinement (Week 3)
**Goal**: Test thoroughly and fix bugs

#### Task 4.1: Unit Tests
**Files to create**:
- `tests/test_services.py`
- `tests/test_ranking.py`
- `tests/test_api.py`

```python
# tests/test_ranking.py
import unittest
from backend.services.ranking_service import RankingService

class TestRankingService(unittest.TestCase):
    def setUp(self):
        self.ranker = RankingService()

    def test_weather_alert_scores_highest(self):
        items = [
            {'category': 'weather_alert', 'title': 'Storm Warning'},
            {'category': 'local_news', 'title': 'Local Story'}
        ]
        ranked = self.ranker.rank_items(items)
        self.assertEqual(ranked[0]['category'], 'weather_alert')

    def test_returns_top_5_only(self):
        items = [{'category': 'local_news', 'title': f'Story {i}'}
                 for i in range(10)]
        ranked = self.ranker.rank_items(items)
        self.assertEqual(len(ranked), 5)
```

#### Task 4.2: Integration Tests
- Test full workflow from frontend to backend
- Test API failure scenarios
- Test edge cases (invalid zipcode, future dates, etc.)

#### Task 4.3: Manual Testing Checklist
- [ ] Valid zipcode returns results
- [ ] Invalid zipcode shows error
- [ ] Future date works correctly
- [ ] Past date works correctly
- [ ] Weather alerts appear first
- [ ] Results are relevant to location
- [ ] Loading spinner appears
- [ ] Error messages are clear
- [ ] Responsive design on mobile

**Deliverables**:
- Test suite with >80% coverage
- Bug-free core functionality
- Documented known issues

---

### Phase 5: Polish & Documentation (Week 3-4)
**Goal**: Improve UX and finalize documentation

#### Task 5.1: UI/UX Enhancements
- Add loading animations
- Improve result card design
- Add tooltips for scores
- Implement responsive design
- Add favicon and branding

#### Task 5.2: Performance Optimization
- Implement caching layer
- Optimize API calls (parallel requests)
- Add request debouncing
- Minimize bundle size

#### Task 5.3: Documentation
- [ ] Update README with screenshots
- [ ] Create API documentation
- [ ] Write deployment guide
- [ ] Document troubleshooting steps

**Deliverables**:
- Polished, production-ready application
- Complete documentation
- Deployment-ready codebase

---

## Technology Stack Decision Matrix

### Backend Options

| Technology | Pros | Cons | Recommendation |
|------------|------|------|----------------|
| **Python/Flask** | ✅ Easy setup<br>✅ Great for APIs<br>✅ Rich ecosystem | ❌ Slower than Node.js<br>❌ Need to manage async | ⭐ **Recommended** for beginners |
| **Python/FastAPI** | ✅ Modern async support<br>✅ Auto documentation<br>✅ Fast | ❌ Slightly steeper learning curve | Good alternative |
| **Node.js/Express** | ✅ JavaScript everywhere<br>✅ Async by default<br>✅ Fast | ❌ Callback complexity<br>❌ Less structured | Good for JS devs |

### Frontend Options

| Technology | Pros | Cons | Recommendation |
|------------|------|------|----------------|
| **Vanilla JS** | ✅ No dependencies<br>✅ Fast<br>✅ Simple | ❌ More code for complex UIs | ⭐ **Recommended** for MVP |
| **React** | ✅ Component-based<br>✅ Large ecosystem<br>✅ State management | ❌ Build setup<br>❌ Learning curve | Phase 2 enhancement |
| **Vue.js** | ✅ Easy to learn<br>✅ Good docs<br>✅ Flexible | ❌ Smaller ecosystem | Good alternative |

---

## File Structure Summary

```
contextual_agent/
├── backend/
│   ├── app.py                      # Main application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py               # API endpoint definitions
│   ├── services/
│   │   ├── __init__.py
│   │   ├── geocoding_service.py    # Zipcode → Location
│   │   ├── weather_service.py      # Weather API integration
│   │   ├── news_service.py         # News API integration
│   │   ├── events_service.py       # Events API (optional)
│   │   └── ranking_service.py      # Scoring & ranking logic
│   ├── models/
│   │   ├── __init__.py
│   │   └── item.py                 # Data models
│   └── utils/
│       ├── __init__.py
│       ├── config.py               # Configuration management
│       ├── cache.py                # Caching utilities
│       └── validators.py           # Input validation
├── frontend/
│   ├── index.html                  # Main HTML page
│   ├── css/
│   │   └── styles.css              # Styling
│   ├── js/
│   │   └── app.js                  # Frontend logic
│   └── assets/
│       └── favicon.ico
├── config/
│   ├── .env                        # Environment variables (gitignored)
│   └── .env.example                # Template for .env
├── tests/
│   ├── __init__.py
│   ├── test_services.py
│   ├── test_ranking.py
│   └── test_api.py
├── docs/
│   └── ARCHITECTURE.md
├── .gitignore
├── requirements.txt                # Python dependencies
├── README.md
├── REQUIREMENTS.md
├── API_GUIDE.md
└── IMPLEMENTATION_PLAN.md
```

---

## Key Dependencies

### Python (requirements.txt)
```
Flask==3.0.0
Flask-CORS==4.0.0
requests==2.31.0
python-dotenv==1.0.0
pytest==7.4.3
```

### Node.js (package.json) - Alternative
```json
{
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "axios": "^1.6.0",
    "dotenv": "^16.3.1"
  }
}
```

---

## Deployment Considerations (Future)

### Local Development
- Run on `localhost:8080`
- Use `.env` for configuration
- SQLite for caching (if needed)

### Production Options
1. **Heroku**: Easy deployment, free tier available
2. **AWS Elastic Beanstalk**: Scalable, more control
3. **DigitalOcean App Platform**: Balance of simplicity and control
4. **Docker**: Containerize for any platform

---

## Next Steps

1. **Review this plan** and adjust based on your preferences
2. **Set up development environment** (Phase 1)
3. **Register for API keys** (see API_GUIDE.md)
4. **Start coding** backend services (Phase 2)

---

## Questions to Consider

Before starting implementation:
- [ ] Python or Node.js for backend?
- [ ] Will you need user authentication later?
- [ ] Do you want to store search history?
- [ ] Should we support date ranges or just single dates?
- [ ] Any specific news categories to prioritize?

---

## Success Metrics

- ✅ Application runs on localhost:8080
- ✅ Search returns results in <5 seconds
- ✅ Top 5 results are relevant and properly ranked
- ✅ Graceful error handling
- ✅ Clean, maintainable code
- ✅ All tests passing
- ✅ Documentation complete

---

*Ready to start building! Refer to README.md for quick start instructions.*
