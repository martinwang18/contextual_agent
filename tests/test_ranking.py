"""
Unit Tests for Ranking Service
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.ranking_service import RankingService
from backend.models.item import ContextualItem
from datetime import datetime


class TestRankingService(unittest.TestCase):
    """Test cases for RankingService"""

    def setUp(self):
        """Set up test fixtures"""
        self.ranker = RankingService()

    def test_weather_alert_scores_highest(self):
        """Weather alerts should score higher than regular weather"""
        items = [
            ContextualItem(
                title='Regular Weather',
                description='Sunny day',
                category='weather',
                source='Test',
                timestamp=datetime.utcnow().isoformat()
            ),
            ContextualItem(
                title='Storm Warning',
                description='Severe storm approaching',
                category='weather_alert',
                source='Test',
                timestamp=datetime.utcnow().isoformat()
            )
        ]

        ranked = self.ranker.rank_items(items)

        self.assertEqual(ranked[0].category, 'weather_alert')
        self.assertGreater(ranked[0].score, ranked[1].score)

    def test_returns_top_5_only(self):
        """Should return maximum of 5 items"""
        items = [
            ContextualItem(
                title=f'Item {i}',
                description='Description',
                category='local_news',
                source='Test',
                timestamp=datetime.utcnow().isoformat()
            )
            for i in range(10)
        ]

        ranked = self.ranker.rank_items(items)

        self.assertEqual(len(ranked), 5)

    def test_severity_modifier(self):
        """High severity should increase score"""
        items = [
            ContextualItem(
                title='Low Severity',
                description='Minor issue',
                category='weather_alert',
                source='Test',
                timestamp=datetime.utcnow().isoformat(),
                metadata={'severity': 'low'}
            ),
            ContextualItem(
                title='High Severity',
                description='Major issue',
                category='weather_alert',
                source='Test',
                timestamp=datetime.utcnow().isoformat(),
                metadata={'severity': 'high'}
            )
        ]

        ranked = self.ranker.rank_items(items)

        self.assertEqual(ranked[0].title, 'High Severity')
        self.assertGreater(ranked[0].score, ranked[1].score)

    def test_empty_list(self):
        """Should handle empty list gracefully"""
        ranked = self.ranker.rank_items([])
        self.assertEqual(len(ranked), 0)

    def test_score_caps_at_100(self):
        """Score should not exceed 100"""
        item = ContextualItem(
            title='High Score Item',
            description='Should cap at 100',
            category='weather_alert',
            source='Test',
            timestamp=datetime.utcnow().isoformat(),
            metadata={'severity': 'high', 'is_breaking': True}
        )

        score = self.ranker._calculate_score(item, datetime.utcnow().strftime('%Y-%m-%d'))
        self.assertLessEqual(score, 100)


if __name__ == '__main__':
    unittest.main()
