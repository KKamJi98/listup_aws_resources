"""
Tests for SES identity module.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pandas as pd
import pytest

from resources.ses_identity import get_filtered_data, get_raw_data


def test_get_raw_data_empty():
    """Test get_raw_data with empty response."""
    # Mock session and client
    mock_session = MagicMock()
    mock_client = MagicMock()
    mock_session.client.return_value = mock_client

    # Mock empty response
    mock_client.list_identities.return_value = {"Identities": []}

    # Call function
    result = get_raw_data(mock_session, "us-east-1")

    # Verify result
    assert result == {
        "Identities": [],
        "VerificationAttributes": {},
        "DkimAttributes": {},
        "NotificationAttributes": {},
    }
    mock_session.client.assert_called_once_with("ses", region_name="us-east-1")


def test_get_raw_data_with_identities():
    """Test get_raw_data with identities."""
    # Mock session and client
    mock_session = MagicMock()
    mock_client = MagicMock()
    mock_session.client.return_value = mock_client

    # Mock responses
    mock_client.list_identities.return_value = {
        "Identities": ["test@example.com", "info@example.com"]
    }
    mock_client.get_identity_verification_attributes.return_value = {
        "VerificationAttributes": {
            "test@example.com": {
                "VerificationStatus": "Success",
                "VerificationStartDate": datetime(2023, 1, 15, tzinfo=timezone.utc),
            },
            "info@example.com": {
                "VerificationStatus": "Pending",
                "VerificationStartDate": datetime(2023, 2, 20, tzinfo=timezone.utc),
            },
        }
    }
    mock_client.get_identity_dkim_attributes.return_value = {
        "DkimAttributes": {
            "test@example.com": {
                "DkimEnabled": True,
                "DkimVerificationStatus": "Success",
            },
            "info@example.com": {
                "DkimEnabled": False,
                "DkimVerificationStatus": "NotStarted",
            },
        }
    }
    mock_client.get_identity_notification_attributes.return_value = {
        "NotificationAttributes": {
            "test@example.com": {
                "BounceTopic": "arn:aws:sns:us-east-1:123456789012:bounce-topic",
                "ComplaintTopic": "arn:aws:sns:us-east-1:123456789012:complaint-topic",
                "DeliveryTopic": "arn:aws:sns:us-east-1:123456789012:delivery-topic",
            },
            "info@example.com": {},
        }
    }

    # Call function
    result = get_raw_data(mock_session, "us-east-1")

    # Verify result
    assert "Identities" in result
    assert len(result["Identities"]) == 2
    assert "test@example.com" in result["Identities"]
    assert "info@example.com" in result["Identities"]

    assert "VerificationAttributes" in result
    assert "test@example.com" in result["VerificationAttributes"]
    assert (
        result["VerificationAttributes"]["test@example.com"]["VerificationStatus"]
        == "Success"
    )

    assert "DkimAttributes" in result
    assert "test@example.com" in result["DkimAttributes"]
    assert result["DkimAttributes"]["test@example.com"]["DkimEnabled"] is True

    assert "NotificationAttributes" in result
    assert "test@example.com" in result["NotificationAttributes"]
    assert "BounceTopic" in result["NotificationAttributes"]["test@example.com"]


def test_get_filtered_data_empty():
    """Test get_filtered_data with empty data."""
    raw_data = {
        "Identities": [],
        "VerificationAttributes": {},
        "DkimAttributes": {},
        "NotificationAttributes": {},
    }

    result = get_filtered_data(raw_data)

    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_get_filtered_data_with_identities():
    """Test get_filtered_data with identities."""
    raw_data = {
        "Identities": ["test@example.com", "info@example.com"],
        "VerificationAttributes": {
            "test@example.com": {
                "VerificationStatus": "Success",
                "VerificationStartDate": datetime(2023, 1, 15, tzinfo=timezone.utc),
            },
            "info@example.com": {
                "VerificationStatus": "Pending",
                "VerificationStartDate": datetime(2023, 2, 20, tzinfo=timezone.utc),
            },
        },
        "DkimAttributes": {
            "test@example.com": {
                "DkimEnabled": True,
                "DkimVerificationStatus": "Success",
            },
            "info@example.com": {
                "DkimEnabled": False,
                "DkimVerificationStatus": "NotStarted",
            },
        },
        "NotificationAttributes": {
            "test@example.com": {
                "BounceTopic": "arn:aws:sns:us-east-1:123456789012:bounce-topic",
                "ComplaintTopic": "arn:aws:sns:us-east-1:123456789012:complaint-topic",
                "DeliveryTopic": "arn:aws:sns:us-east-1:123456789012:delivery-topic",
            },
            "info@example.com": {},
        },
    }

    result = get_filtered_data(raw_data)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2

    # Check first row
    assert result.iloc[0]["Identity"] == "test@example.com"
    assert result.iloc[0]["VerificationStatus"] == "Success"
    assert result.iloc[0]["DkimEnabled"] == "Yes"
    assert result.iloc[0]["DkimVerificationStatus"] == "Success"
    assert (
        result.iloc[0]["BounceNotifications"]
        == "arn:aws:sns:us-east-1:123456789012:bounce-topic"
    )
    assert result.iloc[0]["CreatedDate"] == "2023-01-15"

    # Check second row
    assert result.iloc[1]["Identity"] == "info@example.com"
    assert result.iloc[1]["VerificationStatus"] == "Pending"
    assert result.iloc[1]["DkimEnabled"] == "No"
    assert result.iloc[1]["DkimVerificationStatus"] == "NotStarted"
    assert result.iloc[1]["BounceNotifications"] == "Not configured"
    assert result.iloc[1]["CreatedDate"] == "2023-02-20"
