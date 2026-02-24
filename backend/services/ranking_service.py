"""
Ranking Service
Scores and ranks contextual items by relevance
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class RankingService:
    """Service for scoring and ranking contextual items"""

    # Base scores for each category
    CATEGORY_SCORES = {
        'weather_alert': 95,
        'severe_weather': 85,
        'local_event': 80,
        'local_news': 70,
        'weather': 50,
        'regional_news': 55,
        'global_news': 45
    }

    def rank_items(self, items, query_date=None):
        """
        Score and rank items, returning top 5

        Args:
            items: List of ContextualItem objects
            query_date: Date string for temporal relevance (optional)

        Returns:
            List of top 5 ranked items
        """
        if not items:
            return []

        # Score each item
        scored_items = []
        for item in items:
            score = self._calculate_score(item, query_date)
            item.score = score
            scored_items.append(item)

        # Sort by score (descending)
        scored_items.sort(key=lambda x: x.score, reverse=True)

        # Return top 5
        top_items = scored_items[:5]

        logger.info(f"Ranked {len(items)} items, returning top {len(top_items)}")

        return top_items

    def _calculate_score(self, item, query_date=None):
        """
        Calculate relevance score for an item

        Args:
            item: ContextualItem object
            query_date: Query date for temporal relevance

        Returns:
            float: Score between 0-100
        """
        # Start with base category score
        base_score = self.CATEGORY_SCORES.get(item.category, 50)

        # Apply modifiers
        modifiers = 0

        # Severity modifier (for weather and alerts)
        if item.metadata:
            severity = item.metadata.get('severity', '')
            if severity == 'high':
                modifiers += 10
            elif severity == 'medium':
                modifiers += 5

            # Temperature extremes
            temp = item.metadata.get('temperature')
            if temp:
                if temp > 95 or temp < 32:
                    modifiers += 5

            # Breaking news
            if item.metadata.get('is_breaking'):
                modifiers += 5

        # Temporal relevance
        if query_date and item.timestamp:
            try:
                item_date = datetime.fromisoformat(item.timestamp.replace('Z', '+00:00'))
                query_dt = datetime.strptime(query_date, '%Y-%m-%d')

                # Same day = bonus
                if item_date.date() == query_dt.date():
                    modifiers += 10
                # Within 1 day = smaller bonus
                elif abs((item_date.date() - query_dt.date()).days) <= 1:
                    modifiers += 5
            except:
                pass

        # Calculate final score (cap at 100)
        final_score = min(base_score + modifiers, 100)

        return final_score
