"""
Tests for SES identity module.
"""

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
        "Tags": {},
    }
    mock_session.client.assert_called_once_with("ses", region_name="us-east-1")


def test_get_raw_data_with_identities():
    """Test get_raw_data with identities."""
    # Mock session and client
    mock_session = MagicMock()
    mock_client = MagicMock()
    mock_sts_client = MagicMock()

    # Setup mock clients
    mock_session.client.side_effect = lambda service, **kwargs: {
        "ses": mock_client,
        "sts": mock_sts_client,
    }[service]

    mock_sts_client.get_caller_identity.return_value = {"Account": "123456789012"}

    # Mock responses
    mock_client.list_identities.return_value = {
        "Identities": ["test@example.com", "example.com"]
    }
    mock_client.get_identity_verification_attributes.return_value = {
        "VerificationAttributes": {
            "test@example.com": {
                "VerificationStatus": "Success",
            },
            "example.com": {
                "VerificationStatus": "Pending",
            },
        }
    }

    # Mock tag responses
    mock_client.list_tags_for_resource.side_effect = [
        {"Tags": [{"Key": "Environment", "Value": "Production"}]},
        {"Tags": [{"Key": "Project", "Value": "Website"}]},
    ]

    # Call function
    result = get_raw_data(mock_session, "us-east-1")

    # Verify result
    assert "Identities" in result
    assert len(result["Identities"]) == 2
    assert "test@example.com" in result["Identities"]
    assert "example.com" in result["Identities"]

    assert "VerificationAttributes" in result
    assert "test@example.com" in result["VerificationAttributes"]
    assert (
        result["VerificationAttributes"]["test@example.com"]["VerificationStatus"]
        == "Success"
    )

    assert "Tags" in result
    assert "test@example.com" in result["Tags"]
    assert len(result["Tags"]["test@example.com"]) == 1
    assert result["Tags"]["test@example.com"][0]["Key"] == "Environment"
    assert result["Tags"]["test@example.com"][0]["Value"] == "Production"


def test_get_filtered_data_empty():
    """Test get_filtered_data with empty data."""
    raw_data = {
        "Identities": [],
        "VerificationAttributes": {},
        "Tags": {},
    }

    result = get_filtered_data(raw_data)

    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_get_filtered_data_with_identities():
    """Test get_filtered_data with identities."""
    raw_data = {
        "Identities": ["test@example.com", "example.com"],
        "VerificationAttributes": {
            "test@example.com": {
                "VerificationStatus": "Success",
            },
            "example.com": {
                "VerificationStatus": "Pending",
            },
        },
        "Tags": {
            "test@example.com": [{"Key": "Environment", "Value": "Production"}],
            "example.com": [
                {"Key": "Project", "Value": "Website"},
                {"Key": "Owner", "Value": "Marketing"},
            ],
        },
    }

    result = get_filtered_data(raw_data)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2

    # Check first row
    assert result.iloc[0]["Identity"] == "test@example.com"
    assert result.iloc[0]["IdentityType"] == "Email"
    assert result.iloc[0]["IdentityStatus"] == "Success"
    assert result.iloc[0]["Tags"] == "Environment:Production"

    # Check second row
    assert result.iloc[1]["Identity"] == "example.com"
    assert result.iloc[1]["IdentityType"] == "Domain"
    assert result.iloc[1]["IdentityStatus"] == "Pending"
    assert result.iloc[1]["Tags"] == "Project:Website, Owner:Marketing"
