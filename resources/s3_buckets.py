"""
AWS S3 buckets resource module.

This module provides functions to retrieve and filter AWS S3 buckets data.
"""

from typing import Any, Dict, Optional

import pandas as pd
from botocore.exceptions import ClientError

from utils.datetime_format import format_datetime


def get_raw_data(session: Any, region: Optional[str] = None) -> Dict[str, Any]:
    """
    S3 버킷 목록 조회
    정확한 CreationDate를 얻기 위해서는 us-east-1 리전에서 조회해야 함

    Args:
        session: boto3 세션 객체
        region: AWS 리전명 (S3는 글로벌 서비스이므로 사용되지 않음)

    Returns:
        dict: S3 버킷 원시 데이터
    """
    try:
        s3_client = session.client("s3")
        response = s3_client.list_buckets()
        return response
    except ClientError as e:
        print(f"Error fetching S3 buckets: {e}")
        return {"Buckets": []}
    except Exception as e:
        print(f"Unexpected error fetching S3 buckets: {e}")
        return {"Buckets": []}


def get_filtered_data(raw_data: Dict[str, Any]) -> pd.DataFrame:
    """
    원본 JSON에서 주요 필드만 추출해 DataFrame으로 반환

    Args:
        raw_data: S3 버킷 원시 데이터

    Returns:
        DataFrame: 필터링된 S3 버킷 데이터
    """
    if not raw_data:
        return pd.DataFrame()

    rows = []
    for bucket in raw_data.get("Buckets", []):
        row = {
            "BucketName": bucket.get("Name", ""),
            "CreationDate": format_datetime(bucket.get("CreationDate")),
        }
        rows.append(row)

    return pd.DataFrame(rows)
