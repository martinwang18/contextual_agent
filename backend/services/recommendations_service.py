"""
Recommendations Service
Provides retail/grocery recommendations based on contextual information using OpenAI GPT-4
"""

import logging
import json
import os

logger = logging.getLogger(__name__)


class RecommendationsService:
    """Service for generating retail and grocery recommendations using OpenAI GPT-4"""

    def __init__(self):
        """Initialize OpenAI client via Portkey gateway"""
        self.portkey_api_key = os.getenv('PORTKEY_API_KEY')
        # Support both OPENAI_VIRTUAL_KEY and OPENAI_VIRTUAL_API_KEY
        self.openai_virtual_key = os.getenv('OPENAI_VIRTUAL_KEY') or os.getenv('OPENAI_VIRTUAL_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')  # Optional: Direct OpenAI API key

        if not self.portkey_api_key:
            logger.warning("No PORTKEY_API_KEY found, recommendations will be limited")
            self.client = None
        else:
            try:
                from openai import OpenAI

                # Use Portkey gateway with either virtual key or direct API key
                headers = {
                    "x-portkey-api-key": self.portkey_api_key,
                }

                if self.openai_virtual_key:
                    # Use virtual key (recommended approach)
                    headers["x-portkey-virtual-key"] = self.openai_virtual_key
                    api_key = "dummy-key"
                    logger.info("Using Portkey OpenAI virtual key")
                elif self.openai_api_key:
                    # Use direct OpenAI API key through Portkey
                    headers["x-portkey-provider"] = "openai"
                    api_key = self.openai_api_key
                    logger.info("Using direct OpenAI API key via Portkey")
                else:
                    logger.warning("No OPENAI_VIRTUAL_KEY or OPENAI_API_KEY found")
                    self.client = None
                    return

                self.client = OpenAI(
                    api_key=api_key,
                    base_url="https://cybertron-service-gateway.doordash.team/v1",
                    default_headers=headers
                )
                logger.info(f"OpenAI client initialized via Portkey gateway")
                logger.info(f"Using headers: {list(headers.keys())}")
                logger.info(f"Virtual key present: {bool(self.openai_virtual_key)}")
            except Exception as e:
                logger.error(f"Error initializing OpenAI client: {str(e)}")
                self.client = None

    def _call_gpt4(self, prompt, max_tokens=1000):
        """
        Call GPT-4 via Portkey gateway

        Args:
            prompt: The prompt to send to GPT-4
            max_tokens: Maximum tokens in response

        Returns:
            Parsed JSON response or None on error
        """
        if not self.client:
            logger.error("OpenAI client not initialized")
            return None

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract content from response
            content = response.choices[0].message.content

            # Parse JSON from response
            # Look for JSON block in markdown code fence or plain JSON
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()

            return json.loads(json_str)

        except Exception as e:
            logger.error(f"Error calling GPT-4 via Portkey: {str(e)}")
            return None

    def get_recommendations_for_holidays(self, holidays):
        """
        Get retail recommendations based on holidays using GPT-4

        Args:
            holidays: List of holiday items

        Returns:
            Dict with 'items' (list of recommendations) and 'reasoning' (overall explanation)
        """
        if not holidays or not self.client:
            return {
                'items': self._get_fallback_holiday_recommendations(holidays),
                'reasoning': 'Using fallback recommendations due to unavailable LLM service.'
            }

        try:
            # Extract holiday information
            holiday_names = [h.get('title', '').replace('🎉 ', '').replace('🎄 ', '').replace('🎆 ', '') for h in holidays]
            holiday_descriptions = [h.get('description', '') for h in holidays]

            prompt = f"""You are a retail recommendation expert. Given the following holiday(s), provide exactly 5 retail or grocery items that people would want to buy for this occasion.

Holidays:
{', '.join(holiday_names)}

Descriptions:
{', '.join(holiday_descriptions)}

Provide your response as a JSON object with:
1. "reasoning": A 1-2 sentence explanation of why these items were recommended as a group
2. "items": An array of exactly 5 items, each with:
   - "item": The product name (e.g., "Christmas Tree", "BBQ Supplies")
   - "rationale": Why someone would buy this for the holiday (1-2 sentences)
   - "category": Product category (e.g., "Decorations", "Food", "Clothing", "Supplies", "Gifts", "Home")

Focus on items that are specifically relevant to the holiday and would be top sellers.

Return ONLY the JSON object, no other text:
```json
{{
  "reasoning": "...",
  "items": [
    {{"item": "...", "rationale": "...", "category": "..."}},
    ...
  ]
}}
```"""

            result = self._call_gpt4(prompt)

            if result and isinstance(result, dict) and 'items' in result and isinstance(result['items'], list):
                # Add context to each recommendation
                for rec in result['items']:
                    rec['context'] = holiday_names[0] if holiday_names else 'Holiday'
                logger.info(f"Generated {len(result['items'])} LLM-based holiday recommendations")
                return {
                    'items': result['items'][:5],
                    'reasoning': result.get('reasoning', '')
                }
            else:
                logger.warning("Invalid LLM response, using fallback")
                return {
                    'items': self._get_fallback_holiday_recommendations(holidays),
                    'reasoning': 'Using fallback recommendations due to invalid LLM response.'
                }

        except Exception as e:
            logger.error(f"Error generating holiday recommendations: {str(e)}")
            return {
                'items': self._get_fallback_holiday_recommendations(holidays),
                'reasoning': f'Error occurred: {str(e)}'
            }

    def get_recommendations_for_weather(self, weather_items):
        """
        Get retail recommendations based on weather using GPT-4

        Args:
            weather_items: List of weather items

        Returns:
            Dict with 'items' (list of recommendations) and 'reasoning' (overall explanation)
        """
        if not weather_items or not self.client:
            return {
                'items': self._get_fallback_weather_recommendations(weather_items),
                'reasoning': 'Using fallback recommendations due to unavailable LLM service.'
            }

        try:
            # Extract weather information
            weather_info = []
            for w in weather_items:
                temp = w.get('metadata', {}).get('temperature')
                title = w.get('title', '')
                description = w.get('description', '')
                weather_info.append({
                    'temperature': temp,
                    'title': title,
                    'description': description
                })

            temp = weather_info[0]['temperature']
            temp_str = f"{int(temp)}°F" if temp else "current weather"

            prompt = f"""You are a retail recommendation expert. Given the following weather conditions, provide exactly 5 retail or grocery items that people would want to buy.

Weather Information:
- Temperature: {temp_str}
- Condition: {weather_info[0]['title']}
- Details: {weather_info[0]['description']}

Provide your response as a JSON object with:
1. "reasoning": A 1-2 sentence explanation of why these items were recommended based on the weather
2. "items": An array of exactly 5 items, each with:
   - "item": The product name (be specific, e.g., "Winter Coat", "Sunscreen SPF 50+")
   - "rationale": Why someone would buy this for this weather (reference the specific conditions)
   - "category": Product category (e.g., "Clothing", "Food", "Beverages", "Home", "Personal Care", "Emergency", "Electronics", "Outdoor")

Focus on practical items people would need or want for these specific weather conditions.

Return ONLY the JSON object, no other text:
```json
{{
  "reasoning": "...",
  "items": [
    {{"item": "...", "rationale": "...", "category": "..."}},
    ...
  ]
}}
```"""

            result = self._call_gpt4(prompt)

            if result and isinstance(result, dict) and 'items' in result and isinstance(result['items'], list):
                # Add context to each recommendation
                for rec in result['items']:
                    rec['context'] = f"Weather: {temp_str}"
                logger.info(f"Generated {len(result['items'])} LLM-based weather recommendations")
                return {
                    'items': result['items'][:5],
                    'reasoning': result.get('reasoning', '')
                }
            else:
                logger.warning("Invalid LLM response, using fallback")
                return {
                    'items': self._get_fallback_weather_recommendations(weather_items),
                    'reasoning': 'Using fallback recommendations due to invalid LLM response.'
                }

        except Exception as e:
            logger.error(f"Error generating weather recommendations: {str(e)}")
            return {
                'items': self._get_fallback_weather_recommendations(weather_items),
                'reasoning': f'Error occurred: {str(e)}'
            }

    def get_recommendations_for_news(self, news_items, is_local=True):
        """
        Get retail recommendations based on news content using GPT-4

        Args:
            news_items: List of news items
            is_local: Whether these are local or national news

        Returns:
            Dict with 'items' (list of recommendations) and 'reasoning' (overall explanation)
        """
        if not news_items or not self.client:
            return {
                'items': self._get_fallback_news_recommendations(news_items, is_local),
                'reasoning': 'Using fallback recommendations due to unavailable LLM service.'
            }

        try:
            # Extract top news headlines and descriptions
            news_summary = []
            for news in news_items[:10]:
                news_summary.append({
                    'title': news.get('title', ''),
                    'description': news.get('description', '')[:200]  # Limit description length
                })

            news_type = "local" if is_local else "national"

            prompt = f"""You are a retail recommendation expert. Analyze the following {news_type} news headlines and provide exactly 3-5 retail or grocery items that people might want to buy based on current events and trends.

News Headlines:
{chr(10).join([f"- {n['title']}: {n['description']}" for n in news_summary[:5]])}

Based on these news items, identify themes (e.g., severe weather, sports events, food trends, emergencies, local events) and recommend relevant retail products.

Provide your response as a JSON object with:
1. "reasoning": A 1-2 sentence explanation of the overall themes in the news and why these items were recommended
2. "items": An array of 3-5 items, each with:
   - "item": The product name (e.g., "Emergency Kit", "Team Merchandise", "Cooking Ingredients")
   - "rationale": Why this is relevant based on the news themes (reference specific news if possible)
   - "category": Product category (e.g., "Emergency", "Food", "Sports", "Apparel", "Electronics", "Home", "Media")

Focus on actionable items people would want based on what's happening in the news.

Return ONLY the JSON object, no other text:
```json
{{
  "reasoning": "...",
  "items": [
    {{"item": "...", "rationale": "...", "category": "..."}},
    ...
  ]
}}
```"""

            result = self._call_gpt4(prompt, max_tokens=1000)

            if result and isinstance(result, dict) and 'items' in result and isinstance(result['items'], list):
                logger.info(f"Generated {len(result['items'])} LLM-based {news_type} news recommendations")
                return {
                    'items': result['items'][:5],
                    'reasoning': result.get('reasoning', '')
                }
            else:
                logger.warning("Invalid LLM response, using fallback")
                return {
                    'items': self._get_fallback_news_recommendations(news_items, is_local),
                    'reasoning': 'Using fallback recommendations due to invalid LLM response.'
                }

        except Exception as e:
            logger.error(f"Error generating news recommendations: {str(e)}")
            return {
                'items': self._get_fallback_news_recommendations(news_items, is_local),
                'reasoning': f'Error occurred: {str(e)}'
            }

    # Fallback methods with basic recommendations
    def _get_fallback_holiday_recommendations(self, holidays):
        """Fallback holiday recommendations when LLM is not available"""
        if not holidays:
            return []
        return [
            {'item': 'Greeting Cards', 'rationale': 'Send wishes to loved ones', 'category': 'Supplies'},
            {'item': 'Gift Wrap', 'rationale': 'Present gifts beautifully', 'category': 'Supplies'},
            {'item': 'Decorations', 'rationale': 'Celebrate the occasion', 'category': 'Decorations'}
        ]

    def _get_fallback_weather_recommendations(self, weather_items):
        """Fallback weather recommendations when LLM is not available"""
        if not weather_items:
            return []
        return [
            {'item': 'Weather-appropriate Clothing', 'rationale': 'Stay comfortable', 'category': 'Clothing'},
            {'item': 'Hot/Cold Beverages', 'rationale': 'Match the temperature', 'category': 'Beverages'},
            {'item': 'Seasonal Food Items', 'rationale': 'Enjoy seasonal favorites', 'category': 'Food'}
        ]

    def _get_fallback_news_recommendations(self, news_items, is_local):
        """Fallback news recommendations when LLM is not available"""
        if not news_items:
            return []
        return [
            {'item': 'Local Newspaper', 'rationale': 'Stay informed', 'category': 'Media'},
            {'item': 'Coffee', 'rationale': 'Read the news with coffee', 'category': 'Beverages'}
        ]
