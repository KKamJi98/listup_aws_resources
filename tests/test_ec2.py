"""
Tests for EC2 resource module.
"""

import sys
from datetime import UTC, datetime, timezone
from unittest.mock import MagicMock

import pandas as pd
from botocore.exceptions import ClientError

sys.path.insert(0, ".")

from resources.ec2 import get_filtered_data, get_raw_data


class TestEC2:
    """Test cases for EC2 module."""

    def test_get_raw_data_success(self):
        """Test successful retrieval of EC2 instances data."""
        # Mock session and client
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_session.client.return_value = mock_client

        # Mock response data
        mock_response = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-1234567890abcdef0",
                            "InstanceType": "t3.micro",
                            "State": {"Name": "running"},
                            "PublicIpAddress": "203.0.113.12",
                            "PrivateIpAddress": "10.0.1.12",
                            "LaunchTime": datetime(2023, 5, 15, 12, 30, 45, tzinfo=UTC),
                            "Tags": [{"Key": "Name", "Value": "test-instance"}],
                        }
                    ]
                }
            ]
        }

        mock_client.describe_instances.return_value = mock_response

        # Call the function
        result = get_raw_data(mock_session, "us-east-1")

        # Assertions
        assert result == mock_response
        mock_client.describe_instances.assert_called_once()

    def test_get_raw_data_client_error(self):
        """Test handling of client errors."""
        # Mock session and client
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_session.client.return_value = mock_client

        # Mock client error
        mock_client.describe_instances.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access denied"}},
            "DescribeInstances",
        )

        # Call the function
        result = get_raw_data(mock_session, "us-east-1")

        # Assertions
        assert result == {"Reservations": []}

    def test_get_raw_data_unexpected_error(self):
        """Test handling of unexpected errors."""
        # Mock session and client
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_session.client.return_value = mock_client

        # Mock unexpected error
        mock_client.describe_instances.side_effect = Exception("Unexpected error")

        # Call the function
        result = get_raw_data(mock_session, "us-east-1")

        # Assertions
        assert result == {"Reservations": []}

    def test_get_filtered_data_empty_input(self):
        """Test filtering with empty input."""
        result = get_filtered_data({})
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_get_filtered_data_no_reservations(self):
        """Test filtering with no reservations."""
        raw_data = {"Reservations": []}
        result = get_filtered_data(raw_data)
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_get_filtered_data_complete_instance(self):
        """Test filtering with complete instance data."""
        raw_data = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-1234567890abcdef0",
                            "InstanceType": "t3.micro",
                            "State": {"Name": "running"},
                            "PublicIpAddress": "203.0.113.12",
                            "PrivateIpAddress": "10.0.1.12",
                            "LaunchTime": datetime(2023, 5, 15, 12, 30, 45, tzinfo=UTC),
                            "Tags": [{"Key": "Name", "Value": "test-instance"}],
                        }
                    ]
                }
            ]
        }

        result = get_filtered_data(raw_data)

        # Assertions
        assert len(result) == 1
        assert result.iloc[0]["Name"] == "test-instance"
        assert result.iloc[0]["InstanceId"] == "i-1234567890abcdef0"
        assert result.iloc[0]["InstanceType"] == "t3.micro"
        assert result.iloc[0]["State"] == "running"
        assert result.iloc[0]["PublicIp"] == "203.0.113.12"
        assert result.iloc[0]["PrivateIp"] == "10.0.1.12"
        assert result.iloc[0]["LaunchTime"] == "2023-05-15"

    def test_get_filtered_data_no_name_tag(self):
        """Test filtering with instance having no Name tag."""
        raw_data = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-1234567890abcdef0",
                            "InstanceType": "t3.micro",
                            "State": {"Name": "running"},
                            "Tags": [{"Key": "Environment", "Value": "dev"}],
                        }
                    ]
                }
            ]
        }

        result = get_filtered_data(raw_data)

        # Assertions
        assert len(result) == 1
        assert result.iloc[0]["Name"] == "N/A"

    def test_get_filtered_data_missing_fields(self):
        """Test filtering with missing optional fields."""
        raw_data = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-minimal",
                            "Tags": [],
                        }
                    ]
                }
            ]
        }

        result = get_filtered_data(raw_data)

        # Assertions
        assert len(result) == 1
        assert result.iloc[0]["Name"] == "N/A"
        assert result.iloc[0]["InstanceId"] == "i-minimal"
        assert result.iloc[0]["InstanceType"] == ""
        assert result.iloc[0]["State"] == ""
        assert result.iloc[0]["PublicIp"] == ""
        assert result.iloc[0]["PrivateIp"] == ""
        assert result.iloc[0]["LaunchTime"] is None

    def test_get_filtered_data_multiple_instances(self):
        """Test filtering with multiple instances across reservations."""
        raw_data = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-instance1",
                            "InstanceType": "t3.micro",
                            "State": {"Name": "running"},
                            "Tags": [{"Key": "Name", "Value": "instance-1"}],
                        },
                        {
                            "InstanceId": "i-instance2",
                            "InstanceType": "t3.small",
                            "State": {"Name": "stopped"},
                            "Tags": [{"Key": "Name", "Value": "instance-2"}],
                        },
                    ]
                },
                {
                    "Instances": [
                        {
                            "InstanceId": "i-instance3",
                            "InstanceType": "t3.medium",
                            "State": {"Name": "terminated"},
                            "Tags": [{"Key": "Name", "Value": "instance-3"}],
                        }
                    ]
                },
            ]
        }

        result = get_filtered_data(raw_data)

        # Assertions
        assert len(result) == 3
        assert result.iloc[0]["Name"] == "instance-1"
        assert result.iloc[0]["State"] == "running"
        assert result.iloc[1]["Name"] == "instance-2"
        assert result.iloc[1]["State"] == "stopped"
        assert result.iloc[2]["Name"] == "instance-3"
        assert result.iloc[2]["State"] == "terminated"
