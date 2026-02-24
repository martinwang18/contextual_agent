# How to Get Free API Keys

This guide walks you through getting free API keys for the Contextual Agent application.

## 📋 Quick Summary

All three APIs offer generous free tiers - no credit card required for initial signup!

| API | Free Tier | Time to Get Key | Sign Up Link |
|-----|-----------|----------------|--------------|
| OpenWeatherMap | 1,000 calls/day | ~2 minutes | https://openweathermap.org/api |
| NewsAPI | 100 requests/day | ~1 minute | https://newsapi.org/register |
| Zipcodebase | 10,000/month | ~1 minute | https://zipcodebase.com/ |

---

## 1. OpenWeatherMap (Weather Data)

### What it provides:
- Current weather conditions
- Weather forecasts
- Severe weather alerts

### Steps:

1. **Go to:** https://openweathermap.org/api
2. **Click:** "Get API Key" or "Sign Up"
3. **Fill out the form:**
   - Email address
   - Username
   - Password
   - Agree to terms
4. **Verify your email** (check inbox/spam)
5. **Log in** to your account
6. **Go to:** "API Keys" tab in your account
7. **Copy** your default API key (starts immediately)

**Free tier includes:**
- ✅ 1,000 API calls per day
- ✅ 60 calls per minute
- ✅ Current weather data
- ✅ 5-day forecast

**API Key location after signup:**
- Dashboard → API Keys → Copy the key under "Key"

---

## 2. NewsAPI (News Articles)

### What it provides:
- News articles from 80,000+ sources
- Top headlines by country/category
- Search news by keyword, date, and location

### Steps:

1. **Go to:** https://newsapi.org/register
2. **Fill out the simple form:**
   - First name
   - Email address
   - Password
3. **Click:** "Submit"
4. **Your API key appears immediately!** (No email verification needed)
5. **Copy** your API key from the confirmation page

**Free tier includes:**
- ✅ 100 requests per day
- ✅ Access to articles from last 30 days
- ✅ All news sources
- ⚠️ For development/personal use only

**API Key location:**
- Shown immediately after signup
- Also available at: https://newsapi.org/account

**Important notes:**
- Free tier is for development only
- Cannot be used in production apps with >100 users
- Perfect for learning and testing!

---

## 3. Zipcodebase (Geocoding)

### What it provides:
- Convert USA zipcodes to city, state, coordinates
- Timezone information
- Multiple zipcode lookups

### Steps:

1. **Go to:** https://zipcodebase.com/
2. **Click:** "Get Free API Key" or "Sign Up"
3. **Fill out the form:**
   - Email address
   - Password
   - Company name (can be "Personal" or your name)
4. **Verify your email**
5. **Log in** to your dashboard
6. **Copy** your API key from the dashboard

**Free tier includes:**
- ✅ 10,000 requests per month
- ✅ No credit card required
- ✅ All features included

**API Key location after signup:**
- Dashboard → API Key section (shown prominently)

---

## Alternative: ZipCodeAPI.com

If Zipcodebase doesn't work, try this alternative:

1. **Go to:** https://www.zipcodeapi.com/
2. **Sign up** for free account
3. **Get:** 10 requests per hour (free tier)

**Note:** Lower limits, but good backup option.

---

## 4. Add Keys to Your Application

Once you have your API keys:

1. **Open:** `config/.env` in your project
2. **Replace** the empty values:

```bash
# Paste your actual API keys here
WEATHER_API_KEY=abc123your_openweathermap_key_here
NEWS_API_KEY=xyz789your_newsapi_key_here
GEOCODING_API_KEY=def456your_zipcodebase_key_here
```

3. **Save** the file
4. **Restart** your application:
   ```bash
   ./run.sh
   ```

---

## 🔒 Security Reminders

- ✅ **NEVER** commit `.env` file to git (already in .gitignore)
- ✅ **NEVER** share your API keys publicly
- ✅ **NEVER** push keys to GitHub
- ✅ Keep keys in `config/.env` only
- ✅ Use environment variables in production

---

## 🧪 Testing Your Keys

After adding keys, test the application:

1. Start the app: `./run.sh`
2. Open: http://localhost:8080
3. Enter any USA zipcode (not just test ones!)
4. Check the results - you should see:
   - ✅ Real weather data for that location
   - ✅ Actual news articles
   - ✅ Accurate location information

Check the terminal logs - you should NOT see these warnings:
- ❌ "No WEATHER_API_KEY set, using mock data"
- ❌ "No NEWS_API_KEY set, using mock data"
- ❌ "No GEOCODING_API_KEY set, using mock data"

---

## 📊 Rate Limit Management

### To avoid hitting limits:

**OpenWeatherMap** (1,000/day):
- Cache results for 1 hour (already implemented)
- ~40 searches per hour sustainable

**NewsAPI** (100/day):
- Cache results for 30 minutes (already implemented)
- ~4 searches per hour sustainable

**Zipcodebase** (10,000/month):
- Cache indefinitely (already implemented)
- Essentially unlimited for normal use

Our caching system helps you stay well within limits!

---

## ❓ Troubleshooting

### "Invalid API Key" error
- Double-check you copied the entire key
- No extra spaces before/after the key
- Make sure you verified your email (OpenWeatherMap)

### "Rate limit exceeded"
- Wait a few minutes
- Check your dashboard for current usage
- Cache is working (check logs for "cache hit")

### Still seeing mock data
- Make sure `.env` file is saved
- Restart the application
- Check terminal for warning messages
- Verify keys are not empty in `.env`

---

## 💡 Tips

1. **OpenWeatherMap**: Key activates immediately but may show as inactive for ~10 minutes
2. **NewsAPI**: Key works instantly, no waiting
3. **Zipcodebase**: Usually instant activation
4. **Save your keys**: Store them in a password manager
5. **Test individually**: Add one key at a time and test

---

## 🚀 Upgrade Options (Future)

If you need more requests later:

- **OpenWeatherMap**: $40/month for 100,000 calls/day
- **NewsAPI**: $449/month for business use
- **Zipcodebase**: $9.99/month for 100,000 requests

But the free tiers are perfect for development and learning!

---

**Total time to get all 3 keys: ~5 minutes**

Ready to get started? Pick the first API and follow the steps!
