"""
AWS EC2 instances resource module.

This module provides functions to retrieve and filter AWS EC2 instances data.
"""

from typing import Any

import pandas as pd
from botocore.exceptions import ClientError

from utils.datetime_format import format_datetime
from utils.name_tag import extract_name_tag


def get_raw_data(session: Any, region: str) -> dict[str, Any]:
    """
    EC2 인스턴스 전체 목록 describe_instances() 결과(원본 JSON)를 반환

    Args:
        session: boto3 세션 객체
        region: AWS 리전명

    Returns:
        dict: EC2 인스턴스 원시 데이터
    """
    try:
        ec2_client = session.client("ec2", region_name=region)
        response = ec2_client.describe_instances()
        return response
    except ClientError as e:
        print(f"Error fetching EC2 instances in {region}: {e}")
        return {"Reservations": []}
    except Exception as e:
        print(f"Unexpected error fetching EC2 instances in {region}: {e}")
        return {"Reservations": []}


def get_filtered_data(raw_data: dict[str, Any]) -> pd.DataFrame:
    """
    원본 JSON에서 주요 필드만 추출해 DataFrame으로 반환

    Args:
        raw_data: EC2 인스턴스 원시 데이터

    Returns:
        DataFrame: 필터링된 EC2 인스턴스 데이터
    """
    if not raw_data:
        return pd.DataFrame()

    rows = []
    reservations = raw_data.get("Reservations", [])

    for r in reservations:
        for inst in r.get("Instances", []):
            name = extract_name_tag(inst.get("Tags", []))
            if not name:
                name = "N/A"

            # Security Groups 정보 추출
            security_groups = inst.get("SecurityGroups", [])
            sg_ids = [sg.get("GroupId", "") for sg in security_groups]
            sg_names = [sg.get("GroupName", "") for sg in security_groups]

            row = {
                "Name": name,
                "InstanceId": inst.get("InstanceId", ""),
                "InstanceType": inst.get("InstanceType", ""),
                "State": inst.get("State", {}).get("Name", ""),
                "PublicIp": inst.get("PublicIpAddress", ""),
                "PrivateIp": inst.get("PrivateIpAddress", ""),
                "SecurityGroupIds": ", ".join(sg_ids),
                "SecurityGroupNames": ", ".join(sg_names),
                "LaunchTime": format_datetime(inst.get("LaunchTime")),
            }
            rows.append(row)

    return pd.DataFrame(rows)
