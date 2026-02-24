"""
Input Validation Utilities
Validates user input for security and correctness
"""

import re
from datetime import datetime


def validate_zipcode(zipcode):
    """
    Validate USA zipcode format

    Args:
        zipcode: String to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not zipcode:
        return False

    # Must be exactly 5 digits
    pattern = r'^\d{5}$'
    return bool(re.match(pattern, zipcode))


def validate_date(date_str):
    """
    Validate date format (YYYY-MM-DD)

    Args:
        date_str: Date string to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not date_str:
        return False

    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def sanitize_input(text):
    """
    Sanitize user input to prevent injection attacks

    Args:
        text: Input text to sanitize

    Returns:
        str: Sanitized text
    """
    if not text:
        return ""

    # Remove potentially dangerous characters
    # Keep only alphanumeric, spaces, and basic punctuation
    sanitized = re.sub(r'[^\w\s\-.,]', '', str(text))
    return sanitized.strip()
