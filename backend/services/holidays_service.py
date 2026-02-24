"""
Holidays Service
Identifies holidays and significant events for a given date
"""

import logging
from datetime import datetime
from models.item import ContextualItem

logger = logging.getLogger(__name__)


class HolidaysService:
    """Service for identifying holidays and special events"""

    # US Federal Holidays and common observances
    HOLIDAYS = {
        '01-01': {'name': 'New Year\'s Day', 'type': 'federal', 'description': 'Beginning of the new calendar year'},
        '01-15': {'name': 'Martin Luther King Jr. Day', 'type': 'federal', 'description': 'Honoring civil rights leader (3rd Monday)'},
        '02-14': {'name': 'Valentine\'s Day', 'type': 'observance', 'description': 'Day of love and romance'},
        '02-17': {'name': 'Presidents\' Day', 'type': 'federal', 'description': 'Honoring US presidents (3rd Monday)'},
        '03-17': {'name': 'St. Patrick\'s Day', 'type': 'observance', 'description': 'Irish cultural celebration'},
        '05-26': {'name': 'Memorial Day', 'type': 'federal', 'description': 'Honoring fallen military members (last Monday)'},
        '06-19': {'name': 'Juneteenth', 'type': 'federal', 'description': 'Commemorating end of slavery'},
        '07-04': {'name': 'Independence Day', 'type': 'federal', 'description': 'Celebrating US independence'},
        '09-01': {'name': 'Labor Day', 'type': 'federal', 'description': 'Honoring American workers (1st Monday)'},
        '10-14': {'name': 'Columbus Day / Indigenous Peoples\' Day', 'type': 'federal', 'description': 'Observance (2nd Monday)'},
        '10-31': {'name': 'Halloween', 'type': 'observance', 'description': 'Trick-or-treating and costumes'},
        '11-11': {'name': 'Veterans Day', 'type': 'federal', 'description': 'Honoring military veterans'},
        '11-27': {'name': 'Thanksgiving', 'type': 'federal', 'description': 'Family gathering and gratitude (4th Thursday)'},
        '12-24': {'name': 'Christmas Eve', 'type': 'observance', 'description': 'Day before Christmas'},
        '12-25': {'name': 'Christmas Day', 'type': 'federal', 'description': 'Christian holiday celebration'},
        '12-31': {'name': 'New Year\'s Eve', 'type': 'observance', 'description': 'Last day of the year'},
    }

    # Notable recurring events
    RECURRING_EVENTS = {
        'super-bowl': {'month': 2, 'week': 1, 'day': 'Sunday', 'name': 'Super Bowl', 'description': 'NFL Championship game'},
        'march-madness': {'month': 3, 'name': 'March Madness', 'description': 'NCAA Basketball Tournament'},
        'tax-day': {'month': 4, 'day': 15, 'name': 'Tax Day', 'description': 'US Federal tax filing deadline'},
        'mothers-day': {'month': 5, 'week': 2, 'day': 'Sunday', 'name': 'Mother\'s Day', 'description': 'Honoring mothers'},
        'fathers-day': {'month': 6, 'week': 3, 'day': 'Sunday', 'name': 'Father\'s Day', 'description': 'Honoring fathers'},
        'black-friday': {'month': 11, 'name': 'Black Friday', 'description': 'Major shopping day after Thanksgiving'},
    }

    def __init__(self):
        pass

    def get_holidays(self, date_str, location=None):
        """
        Get holidays and special events for a given date

        Args:
            date_str: Date string (YYYY-MM-DD)
            location: Optional Location object (for local events)

        Returns:
            List of ContextualItem objects
        """
        holidays = []

        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            month_day = date_obj.strftime('%m-%d')

            # Check for exact date matches
            if month_day in self.HOLIDAYS:
                holiday_info = self.HOLIDAYS[month_day]
                item = ContextualItem(
                    title=f"🎉 {holiday_info['name']}",
                    description=holiday_info['description'],
                    category='holiday',
                    source='US Calendar',
                    timestamp=datetime.utcnow().isoformat(),
                    metadata={
                        'type': holiday_info['type'],
                        'is_federal': holiday_info['type'] == 'federal',
                        'date': date_str
                    }
                )
                holidays.append(item)
                logger.info(f"Found holiday: {holiday_info['name']} on {date_str}")

            # Check for special seasonal events
            season_events = self._check_seasonal_events(date_obj, location)
            holidays.extend(season_events)

            # Check for notable dates
            notable = self._check_notable_dates(date_obj)
            holidays.extend(notable)

        except Exception as e:
            logger.error(f"Error getting holidays: {str(e)}")

        return holidays

    def _check_seasonal_events(self, date_obj, location=None):
        """Check for seasonal events and special days"""
        events = []
        month = date_obj.month
        day = date_obj.day

        # Super Bowl (typically first Sunday in February)
        if month == 2 and date_obj.weekday() == 6 and 1 <= day <= 7:
            events.append(ContextualItem(
                title="🏈 Super Bowl Sunday",
                description="NFL Championship game - one of the biggest sporting events of the year",
                category='event',
                source='Sports Calendar',
                timestamp=datetime.utcnow().isoformat(),
                metadata={'type': 'sports', 'importance': 'major'}
            ))

        # Mother's Day (2nd Sunday in May)
        if month == 5 and date_obj.weekday() == 6 and 8 <= day <= 14:
            events.append(ContextualItem(
                title="💐 Mother's Day",
                description="Day to honor and celebrate mothers and mother figures",
                category='event',
                source='US Calendar',
                timestamp=datetime.utcnow().isoformat(),
                metadata={'type': 'observance', 'importance': 'major'}
            ))

        # Father's Day (3rd Sunday in June)
        if month == 6 and date_obj.weekday() == 6 and 15 <= day <= 21:
            events.append(ContextualItem(
                title="👔 Father's Day",
                description="Day to honor and celebrate fathers and father figures",
                category='event',
                source='US Calendar',
                timestamp=datetime.utcnow().isoformat(),
                metadata={'type': 'observance', 'importance': 'major'}
            ))

        # Black Friday (Friday after Thanksgiving)
        if month == 11 and date_obj.weekday() == 4 and 23 <= day <= 29:
            events.append(ContextualItem(
                title="🛍️ Black Friday",
                description="Major shopping day with significant retail sales and deals",
                category='event',
                source='Retail Calendar',
                timestamp=datetime.utcnow().isoformat(),
                metadata={'type': 'shopping', 'importance': 'major'}
            ))

        # Cyber Monday
        if month == 11 and date_obj.weekday() == 0 and 26 <= day <= 30:
            events.append(ContextualItem(
                title="💻 Cyber Monday",
                description="Online shopping day with major e-commerce deals",
                category='event',
                source='Retail Calendar',
                timestamp=datetime.utcnow().isoformat(),
                metadata={'type': 'shopping', 'importance': 'major'}
            ))

        return events

    def _check_notable_dates(self, date_obj):
        """Check for other notable dates"""
        notable = []
        month = date_obj.month
        day = date_obj.day

        # Tax Day (April 15)
        if month == 4 and day == 15:
            notable.append(ContextualItem(
                title="📋 Tax Day",
                description="Deadline for filing US federal income tax returns",
                category='event',
                source='IRS',
                timestamp=datetime.utcnow().isoformat(),
                metadata={'type': 'financial', 'importance': 'major'}
            ))

        # First day of seasons
        if (month == 3 and 19 <= day <= 21):
            notable.append(ContextualItem(
                title="🌸 First Day of Spring",
                description="Spring equinox - beginning of spring season",
                category='event',
                source='Calendar',
                timestamp=datetime.utcnow().isoformat(),
                metadata={'type': 'seasonal'}
            ))
        elif (month == 6 and 20 <= day <= 22):
            notable.append(ContextualItem(
                title="☀️ First Day of Summer",
                description="Summer solstice - longest day of the year",
                category='event',
                source='Calendar',
                timestamp=datetime.utcnow().isoformat(),
                metadata={'type': 'seasonal'}
            ))
        elif (month == 9 and 21 <= day <= 23):
            notable.append(ContextualItem(
                title="🍂 First Day of Fall",
                description="Autumn equinox - beginning of fall season",
                category='event',
                source='Calendar',
                timestamp=datetime.utcnow().isoformat(),
                metadata={'type': 'seasonal'}
            ))
        elif (month == 12 and 20 <= day <= 22):
            notable.append(ContextualItem(
                title="❄️ First Day of Winter",
                description="Winter solstice - shortest day of the year",
                category='event',
                source='Calendar',
                timestamp=datetime.utcnow().isoformat(),
                metadata={'type': 'seasonal'}
            ))

        return notable
