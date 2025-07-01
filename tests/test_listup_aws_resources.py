import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from listup_aws_resources import main


@patch("json.dump")
@patch("pandas.ExcelWriter")
@patch("boto3.Session")
def test_main(mock_session, mock_excel_writer, mock_json_dump):
    # Mock the boto3 session and client
    mock_client = MagicMock()
    mock_client.list_streams.return_value = {"StreamNames": [], "HasMoreStreams": False}
    mock_client.list_delivery_streams.return_value = {
        "DeliveryStreamNames": [],
        "HasMoreDeliveryStreams": False,
    }
    mock_session.return_value.client.return_value = mock_client

    # Mock the ExcelWriter context manager
    mock_excel_writer.return_value.__enter__.return_value = MagicMock()
    mock_excel_writer.return_value.__exit__.return_value = None

    try:
        main()
    except Exception as e:
        pytest.fail(f"main() raised an exception: {e}")
