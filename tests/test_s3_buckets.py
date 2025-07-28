"""
Tests for S3 buckets resource module.
"""

import sys
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pandas as pd
import pytest
from botocore.exceptions import ClientError

sys.path.insert(0, ".")

from resources.s3_buckets import get_filtered_data, get_raw_data


class TestS3Buckets:
    """Test cases for S3 buckets module."""

    def test_get_raw_data_success(self):
        """Test successful retrieval of S3 buckets data."""
        # Mock session and client
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_session.client.return_value = mock_client

        # Mock response data
        mock_response = {
            "Buckets": [
                {
                    "Name": "test-bucket-1",
                    "CreationDate": datetime(
                        2023, 5, 15, 12, 30, 45, tzinfo=timezone.utc
                    ),
                },
                {
                    "Name": "test-bucket-2",
                    "CreationDate": datetime(
                        2023, 6, 20, 8, 15, 30, tzinfo=timezone.utc
                    ),
                },
            ]
        }

        mock_client.list_buckets.return_value = mock_response

        # Call the function
        result = get_raw_data(mock_session)

        # Assertions
        assert result == mock_response
        mock_client.list_buckets.assert_called_once()

    def test_get_raw_data_client_error(self):
        """Test handling of client errors."""
        # Mock session and client
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_session.client.return_value = mock_client

        # Mock client error
        mock_client.list_buckets.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access denied"}},
            "ListBuckets",
        )

        # Call the function
        result = get_raw_data(mock_session)

        # Assertions
        assert result == {"Buckets": []}

    def test_get_raw_data_unexpected_error(self):
        """Test handling of unexpected errors."""
        # Mock session and client
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_session.client.return_value = mock_client

        # Mock unexpected error
        mock_client.list_buckets.side_effect = Exception("Unexpected error")

        # Call the function
        result = get_raw_data(mock_session)

        # Assertions
        assert result == {"Buckets": []}

    def test_get_filtered_data_empty_input(self):
        """Test filtering with empty input."""
        result = get_filtered_data({})
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_get_filtered_data_no_buckets(self):
        """Test filtering with no buckets."""
        raw_data = {"Buckets": []}
        result = get_filtered_data(raw_data)
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_get_filtered_data_complete_buckets(self):
        """Test filtering with complete bucket data."""
        raw_data = {
            "Buckets": [
                {
                    "Name": "test-bucket-1",
                    "CreationDate": datetime(
                        2023, 5, 15, 12, 30, 45, tzinfo=timezone.utc
                    ),
                },
                {
                    "Name": "test-bucket-2",
                    "CreationDate": datetime(
                        2023, 6, 20, 8, 15, 30, tzinfo=timezone.utc
                    ),
                },
            ]
        }

        result = get_filtered_data(raw_data)

        # Assertions
        assert len(result) == 2
        assert result.iloc[0]["BucketName"] == "test-bucket-1"
        assert result.iloc[0]["CreationDate"] == "2023-05-15"
        assert result.iloc[1]["BucketName"] == "test-bucket-2"
        assert result.iloc[1]["CreationDate"] == "2023-06-20"

    def test_get_filtered_data_missing_fields(self):
        """Test filtering with missing optional fields."""
        raw_data = {
            "Buckets": [
                {
                    "Name": "minimal-bucket",
                    # Missing CreationDate
                }
            ]
        }

        result = get_filtered_data(raw_data)

        # Assertions
        assert len(result) == 1
        assert result.iloc[0]["BucketName"] == "minimal-bucket"
        assert result.iloc[0]["CreationDate"] is None

    def test_get_filtered_data_empty_name(self):
        """Test filtering with empty bucket name."""
        raw_data = {
            "Buckets": [
                {
                    # Missing Name field
                    "CreationDate": datetime(
                        2023, 5, 15, 12, 30, 45, tzinfo=timezone.utc
                    ),
                }
            ]
        }

        result = get_filtered_data(raw_data)

        # Assertions
        assert len(result) == 1
        assert result.iloc[0]["BucketName"] == ""
        assert result.iloc[0]["CreationDate"] == "2023-05-15"
