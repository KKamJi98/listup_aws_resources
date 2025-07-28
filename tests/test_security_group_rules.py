"""
Tests for security_group_rules module.
"""

import unittest
from unittest.mock import MagicMock

import pandas as pd
from botocore.exceptions import ClientError

from resources.security_group_rules import get_filtered_data, get_raw_data


class TestSecurityGroupRules(unittest.TestCase):
    """Test cases for security_group_rules module."""

    def test_get_raw_data_success(self):
        """Test successful retrieval of security group rules data."""
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_session.client.return_value = mock_client

        mock_client.describe_security_group_rules.return_value = {
            "SecurityGroupRules": [
                {
                    "SecurityGroupRuleId": "sgr-12345",
                    "GroupId": "sg-12345",
                    "IsEgress": False,
                    "IpProtocol": "tcp",
                    "FromPort": 80,
                    "ToPort": 80,
                    "CidrIpv4": "0.0.0.0/0",
                    "Description": "HTTP access",
                    "Tags": [],
                }
            ]
        }

        result = get_raw_data(mock_session, "us-east-1")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["SecurityGroupRuleId"], "sgr-12345")
        mock_client.describe_security_group_rules.assert_called_once()

    def test_get_raw_data_with_pagination(self):
        """Test retrieval with pagination."""
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_session.client.return_value = mock_client

        # First call returns data with NextToken
        mock_client.describe_security_group_rules.side_effect = [
            {
                "SecurityGroupRules": [{"SecurityGroupRuleId": "sgr-1"}],
                "NextToken": "token123",
            },
            {"SecurityGroupRules": [{"SecurityGroupRuleId": "sgr-2"}]},
        ]

        result = get_raw_data(mock_session, "us-east-1")

        self.assertEqual(len(result), 2)
        self.assertEqual(mock_client.describe_security_group_rules.call_count, 2)

    def test_get_raw_data_client_error(self):
        """Test handling of ClientError."""
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_session.client.return_value = mock_client

        mock_client.describe_security_group_rules.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied"}}, "DescribeSecurityGroupRules"
        )

        result = get_raw_data(mock_session, "us-east-1")

        self.assertEqual(result, [])

    def test_get_raw_data_unexpected_error(self):
        """Test handling of unexpected errors."""
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_session.client.return_value = mock_client

        mock_client.describe_security_group_rules.side_effect = Exception(
            "Unexpected error"
        )

        result = get_raw_data(mock_session, "us-east-1")

        self.assertEqual(result, [])

    def test_get_filtered_data_empty_input(self):
        """Test filtering with empty input."""
        result = get_filtered_data([])

        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)

    def test_get_filtered_data_inbound_rule(self):
        """Test filtering inbound security group rule."""
        raw_data = [
            {
                "SecurityGroupRuleId": "sgr-12345",
                "GroupId": "sg-12345",
                "IsEgress": False,
                "IpProtocol": "tcp",
                "FromPort": 80,
                "ToPort": 80,
                "CidrIpv4": "0.0.0.0/0",
                "Description": "HTTP access",
                "Tags": [{"Key": "Name", "Value": "WebRule"}],
            }
        ]

        result = get_filtered_data(raw_data)

        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["Direction"], "Inbound")
        self.assertEqual(result.iloc[0]["Protocol"], "tcp")
        self.assertEqual(result.iloc[0]["PortRange"], "80")
        self.assertEqual(result.iloc[0]["Source/Destination"], "0.0.0.0/0")
        self.assertEqual(result.iloc[0]["AnyOpen"], "⚠️ YES")
        self.assertEqual(result.iloc[0]["Tags"], "Name=WebRule")

    def test_get_filtered_data_outbound_rule(self):
        """Test filtering outbound security group rule."""
        raw_data = [
            {
                "SecurityGroupRuleId": "sgr-67890",
                "GroupId": "sg-67890",
                "IsEgress": True,
                "IpProtocol": "tcp",
                "FromPort": 443,
                "ToPort": 443,
                "CidrIpv4": "10.0.0.0/8",
                "Description": "HTTPS to private",
                "Tags": [],
            }
        ]

        result = get_filtered_data(raw_data)

        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["Direction"], "Outbound")
        self.assertEqual(result.iloc[0]["AnyOpen"], "No")

    def test_get_filtered_data_ipv6_any_open(self):
        """Test filtering IPv6 any open rule."""
        raw_data = [
            {
                "SecurityGroupRuleId": "sgr-ipv6",
                "GroupId": "sg-ipv6",
                "IsEgress": False,
                "IpProtocol": "tcp",
                "FromPort": 22,
                "ToPort": 22,
                "CidrIpv6": "::/0",
                "Description": "SSH IPv6",
                "Tags": [],
            }
        ]

        result = get_filtered_data(raw_data)

        self.assertEqual(result.iloc[0]["Source/Destination"], "::/0")
        self.assertEqual(result.iloc[0]["AnyOpen"], "⚠️ YES")

    def test_get_filtered_data_security_group_reference(self):
        """Test filtering rule with security group reference."""
        raw_data = [
            {
                "SecurityGroupRuleId": "sgr-ref",
                "GroupId": "sg-ref",
                "IsEgress": False,
                "IpProtocol": "tcp",
                "FromPort": 3306,
                "ToPort": 3306,
                "ReferencedGroupInfo": {"GroupId": "sg-source"},
                "Description": "MySQL from app servers",
                "Tags": [],
            }
        ]

        result = get_filtered_data(raw_data)

        self.assertEqual(result.iloc[0]["Source/Destination"], "sg-source")
        self.assertEqual(result.iloc[0]["AnyOpen"], "No")

    def test_get_filtered_data_prefix_list(self):
        """Test filtering rule with prefix list."""
        raw_data = [
            {
                "SecurityGroupRuleId": "sgr-prefix",
                "GroupId": "sg-prefix",
                "IsEgress": True,
                "IpProtocol": "tcp",
                "FromPort": 443,
                "ToPort": 443,
                "PrefixListId": "pl-12345",
                "Description": "HTTPS to S3",
                "Tags": [],
            }
        ]

        result = get_filtered_data(raw_data)

        self.assertEqual(result.iloc[0]["Source/Destination"], "pl-12345")

    def test_get_filtered_data_all_protocol(self):
        """Test filtering rule with all protocols."""
        raw_data = [
            {
                "SecurityGroupRuleId": "sgr-all",
                "GroupId": "sg-all",
                "IsEgress": True,
                "IpProtocol": "-1",
                "CidrIpv4": "10.0.0.0/16",
                "Description": "All traffic",
                "Tags": [],
            }
        ]

        result = get_filtered_data(raw_data)

        self.assertEqual(result.iloc[0]["Protocol"], "All")
        self.assertEqual(result.iloc[0]["PortRange"], "All")

    def test_get_filtered_data_port_range(self):
        """Test filtering rule with port range."""
        raw_data = [
            {
                "SecurityGroupRuleId": "sgr-range",
                "GroupId": "sg-range",
                "IsEgress": False,
                "IpProtocol": "tcp",
                "FromPort": 8000,
                "ToPort": 8999,
                "CidrIpv4": "192.168.1.0/24",
                "Description": "App port range",
                "Tags": [],
            }
        ]

        result = get_filtered_data(raw_data)

        self.assertEqual(result.iloc[0]["PortRange"], "8000-8999")


if __name__ == "__main__":
    unittest.main()
