# Contextual Agent Web Application

A web application that provides the top 5 trending contextual events and information relevant to a specific USA zipcode and date.

## Features

- 📅 Date-based contextual search
- 📍 Zipcode-specific results for USA locations
- 🌤️ Weather information and alerts
- 📰 Local and global news events
- 🎉 Community events and activities
- 🏆 Smart ranking algorithm for relevance

## Quick Start

### Prerequisites

- Python 3.8+ (recommended) or Node.js 14+
- Git
- API keys for required services (see API_GUIDE.md)

### Installation

1. **Clone the repository**
   ```bash
   cd /Users/martin.wang/martin_projects/contextual_agent
   ```

2. **Set up Python virtual environment** (if using Python)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp config/.env.example config/.env
   # Edit config/.env and add your API keys
   ```

5. **Run the application**
   ```bash
   python backend/app.py
   ```

6. **Access the application**
   - Open your browser and navigate to `http://localhost:8080`

## Project Structure

```
contextual_agent/
├── backend/                 # Backend application code
│   ├── api/                # API endpoint handlers
│   ├── models/             # Data models
│   ├── services/           # Business logic and external API integrations
│   └── utils/              # Utility functions
├── frontend/               # Frontend assets
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript files
│   └── assets/            # Images, icons, etc.
├── config/                 # Configuration files
├── tests/                  # Test files
├── docs/                   # Additional documentation
├── README.md              # This file
├── REQUIREMENTS.md        # Detailed requirements specification
├── API_GUIDE.md          # API integration guide
└── IMPLEMENTATION_PLAN.md # Development roadmap
```

## Usage

1. Enter a date (YYYY-MM-DD format)
2. Enter a 5-digit USA zipcode
3. Click "Get Trending Items"
4. View the top 5 contextual items ranked by relevance

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black backend/
flake8 backend/
```

### API Documentation
See `API_GUIDE.md` for detailed information about external API integrations.

## Configuration

All configuration is managed through environment variables stored in `config/.env`:

- `WEATHER_API_KEY` - OpenWeatherMap API key
- `NEWS_API_KEY` - NewsAPI key
- `GEOCODING_API_KEY` - Geocoding API key
- `PORT` - Server port (default: 8080)
- `DEBUG` - Debug mode (default: False)

## Technologies Used

- **Backend**: Python/Flask (or Node.js/Express)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla or React)
- **APIs**: OpenWeatherMap, NewsAPI, Geocoding services
- **Testing**: pytest, unittest

## Roadmap

- [x] Requirements specification
- [ ] MVP implementation
  - [ ] Basic UI
  - [ ] API integrations
  - [ ] Ranking algorithm
- [ ] Enhanced features
  - [ ] Caching layer
  - [ ] Improved UI/UX
  - [ ] Additional data sources
- [ ] Production deployment

## Contributing

1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions, please open an issue in the repository.

## Acknowledgments

- OpenWeatherMap for weather data
- NewsAPI for news aggregation
- Public data sources and APIs
