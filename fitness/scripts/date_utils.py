#!/usr/bin/env python3
"""Date utilities for fitness tracking system.

This module provides datetime utility functions for formatting and parsing
datetime strings in the format YYYY-MM-DD-<unix epoch seconds>.
"""

from datetime import datetime as dt


def get_current_datetime() -> str:
    """Get current datetime in format YYYY-MM-DD-<unix epoch seconds>.
    
    Returns:
        Current datetime as a string in format YYYY-MM-DD-<unix epoch seconds>.
    """
    now = dt.now()
    date_str = now.strftime("%Y-%m-%d")
    unix_seconds = int(now.timestamp())
    return f"{date_str}-{unix_seconds}"


def format_datetime_for_filename(datetime_str: str) -> str:
    """Format datetime for use in filenames (ensures valid filename characters).
    
    Args:
        datetime_str: Datetime string in format YYYY-MM-DD-<unix epoch seconds>.
        
    Returns:
        Formatted datetime string safe for use in filenames.
        
    Raises:
        ValueError: If datetime_str is not in the expected format.
    """
    # Validate format first
    parts = datetime_str.split("-")
    if len(parts) < 4:
        raise ValueError(f"Invalid datetime format: {datetime_str}. Expected YYYY-MM-DD-<unix epoch seconds>")
    
    # The format YYYY-MM-DD-<unix epoch seconds> is already filename-safe
    # (uses only hyphens, digits, and no special characters)
    # But we'll validate and ensure no invalid characters
    for char in datetime_str:
        if not (char.isalnum() or char == '-'):
            raise ValueError(f"Invalid character in datetime string: {char}. Only alphanumeric characters and hyphens are allowed.")
    
    return datetime_str


def parse_datetime(datetime_str: str) -> dt:
    """Parse datetime string in format YYYY-MM-DD-<unix epoch seconds>.
    
    Args:
        datetime_str: Datetime string in format YYYY-MM-DD-<unix epoch seconds>.
        
    Returns:
        Parsed datetime object.
        
    Raises:
        ValueError: If datetime_str is not in the expected format or cannot be parsed.
    """
    parts = datetime_str.split("-")
    if len(parts) < 4:
        raise ValueError(f"Invalid datetime format: {datetime_str}. Expected YYYY-MM-DD-<unix epoch seconds>")
    
    # Extract date part (YYYY-MM-DD) and unix epoch seconds
    date_part = "-".join(parts[:3])
    unix_seconds_str = parts[3]
    
    # Validate unix seconds is numeric
    try:
        unix_seconds = int(unix_seconds_str)
    except ValueError:
        raise ValueError(f"Invalid unix epoch seconds: {unix_seconds_str}. Must be an integer.")
    
    # Parse the date part
    try:
        date_obj = dt.strptime(date_part, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(f"Invalid date format: {date_part}. Expected YYYY-MM-DD: {e}")
    
    # Create datetime from unix timestamp to ensure accuracy
    try:
        parsed_dt = dt.fromtimestamp(unix_seconds)
    except (ValueError, OSError) as e:
        raise ValueError(f"Invalid unix timestamp: {unix_seconds}. {e}")
    
    return parsed_dt
