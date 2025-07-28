"""
AWS Security Group Rules resource module.

This module provides functions to retrieve and filter AWS Security Group Rules data.
"""

from typing import Any

import pandas as pd
from botocore.exceptions import ClientError


def get_raw_data(session: Any, region: str) -> list[dict[str, Any]]:
    """
    AWS Security Group Rules 리소스 정보를 조회합니다.

    Args:
        session: boto3 세션 객체
        region: AWS 리전명

    Returns:
        list: Security Group Rules 리소스 정보 목록
    """
    try:
        ec2_client = session.client("ec2")
        response = ec2_client.describe_security_group_rules()
        security_group_rules = response.get("SecurityGroupRules", [])

        # 추가 페이지가 있는 경우 모두 조회
        while "NextToken" in response:
            response = ec2_client.describe_security_group_rules(
                NextToken=response["NextToken"]
            )
            security_group_rules.extend(response.get("SecurityGroupRules", []))

        return security_group_rules
    except ClientError as e:
        print(f"Error fetching security group rules in {region}: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error fetching security group rules in {region}: {e}")
        return []


def get_filtered_data(raw_data: list[dict[str, Any]]) -> pd.DataFrame:
    """
    원시 Security Group Rules 데이터를 필터링하여 필요한 정보만 추출합니다.

    Args:
        raw_data: Security Group Rules 원시 데이터

    Returns:
        DataFrame: 필터링된 Security Group Rules 데이터
    """
    if not raw_data:
        return pd.DataFrame()

    filtered_data = []

    for rule in raw_data:
        # 규칙 방향 확인
        is_egress = rule.get("IsEgress", False)
        direction = "Outbound" if is_egress else "Inbound"

        # 프로토콜 정보
        protocol = rule.get("IpProtocol", "")
        if protocol == "-1":
            protocol = "All"

        # 포트 정보
        from_port = rule.get("FromPort")
        to_port = rule.get("ToPort")

        if from_port is not None and to_port is not None:
            if from_port == to_port:
                port_range = str(from_port)
            else:
                port_range = f"{from_port}-{to_port}"
        else:
            port_range = "All"

        # 소스/대상 정보
        source_dest = ""
        if rule.get("CidrIpv4"):
            source_dest = rule.get("CidrIpv4")
        elif rule.get("CidrIpv6"):
            source_dest = rule.get("CidrIpv6")
        elif rule.get("ReferencedGroupInfo"):
            ref_group = rule.get("ReferencedGroupInfo", {})
            source_dest = ref_group.get("GroupId", "")
        elif rule.get("PrefixListId"):
            source_dest = rule.get("PrefixListId")

        # AnyOpen 여부 확인
        any_open = "⚠️ YES" if source_dest in ["0.0.0.0/0", "::/0"] else "No"

        filtered_rule = {
            "SecurityGroupRuleId": rule.get("SecurityGroupRuleId", ""),
            "GroupId": rule.get("GroupId", ""),
            "Direction": direction,
            "Protocol": protocol,
            "PortRange": port_range,
            "Source/Destination": source_dest,
            "AnyOpen": any_open,
            "Description": rule.get("Description", ""),
            "Tags": _format_tags(rule.get("Tags", [])),
        }

        filtered_data.append(filtered_rule)

    return pd.DataFrame(filtered_data)


def _format_tags(tags: list[dict[str, str]]) -> str:
    """
    태그 목록을 문자열로 포맷팅합니다.

    Args:
        tags: 태그 목록

    Returns:
        str: 포맷팅된 태그 문자열
    """
    if not tags:
        return ""

    return ", ".join([f"{tag.get('Key', '')}={tag.get('Value', '')}" for tag in tags])
