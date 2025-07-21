"""
Utility functions for datetime formatting.
"""

from datetime import datetime


def format_datetime(dt_value, format_str="%Y-%m-%d"):
    """
    Format a datetime object to a standardized string format.

    Parameters
    ----------
    dt_value : datetime or str or None
        The datetime value to format. Can be a datetime object, a string, or None.
    format_str : str, default "%Y-%m-%d"
        The format string to use for formatting.

    Returns
    -------
    str or None
        The formatted datetime string, or None if input is None.
    """
    if dt_value is None:
        return None

    if isinstance(dt_value, str):
        try:
            # Try to parse the string as a datetime
            dt_value = datetime.fromisoformat(dt_value.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            # If parsing fails, return the original string
            return dt_value

    if hasattr(dt_value, "strftime"):
        return dt_value.strftime(format_str)

    # If we can't format it, return the original value
    return dt_value
