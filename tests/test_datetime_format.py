"""
Tests for datetime formatting utility functions.
"""

from datetime import datetime, timezone

import pytest

from utils.datetime_format import format_datetime


def test_format_datetime_with_datetime_object():
    """Test formatting a datetime object."""
    dt = datetime(2023, 5, 15, 12, 30, 45, tzinfo=timezone.utc)
    result = format_datetime(dt)
    assert result == "2023-05-15"


def test_format_datetime_with_string():
    """Test formatting a datetime string."""
    dt_str = "2023-05-15T12:30:45Z"
    result = format_datetime(dt_str)
    assert result == "2023-05-15"


def test_format_datetime_with_none():
    """Test formatting None value."""
    result = format_datetime(None)
    assert result is None


def test_format_datetime_with_invalid_string():
    """Test formatting an invalid datetime string."""
    dt_str = "not-a-datetime"
    result = format_datetime(dt_str)
    assert result == "not-a-datetime"


def test_format_datetime_with_custom_format():
    """Test formatting with a custom format string."""
    dt = datetime(2023, 5, 15, 12, 30, 45)
    result = format_datetime(dt, format_str="%Y/%m/%d %H:%M")
    assert result == "2023/05/15 12:30"
