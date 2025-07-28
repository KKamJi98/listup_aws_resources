"""
AWS Security Groups resource module.

This module provides functions to retrieve and filter AWS Security Groups data.
"""

from typing import Any

import pandas as pd
from botocore.exceptions import ClientError


def get_raw_data(session: Any, region: str) -> list[dict[str, Any]]:
    """
    AWS Security Group 리소스 정보를 조회합니다.

    Args:
        session: boto3 세션 객체
        region: AWS 리전명

    Returns:
        list: Security Group 리소스 정보 목록
    """
    try:
        ec2_client = session.client("ec2")
        response = ec2_client.describe_security_groups()
        security_groups = response.get("SecurityGroups", [])

        # 추가 페이지가 있는 경우 모두 조회
        while "NextToken" in response:
            response = ec2_client.describe_security_groups(
                NextToken=response["NextToken"]
            )
            security_groups.extend(response.get("SecurityGroups", []))

        # 각 보안 그룹에 대해 0.0.0.0/0 AnyOpen 여부 확인
        for sg in security_groups:
            sg["HasAnyOpenInbound"] = _check_any_open_inbound(sg)

        return security_groups
    except ClientError as e:
        print(f"Error fetching security groups in {region}: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error fetching security groups in {region}: {e}")
        return []


def _check_any_open_inbound(sg: dict[str, Any]) -> bool:
    """
    보안 그룹에 0.0.0.0/0 또는 ::/0 인바운드 규칙이 있는지 확인합니다.

    Args:
        sg: 보안 그룹 데이터

    Returns:
        bool: AnyOpen 인바운드 규칙 존재 여부
    """
    for rule in sg.get("IpPermissions", []):
        # IPv4 범위 확인
        for ip_range in rule.get("IpRanges", []):
            if ip_range.get("CidrIp") == "0.0.0.0/0":
                return True

        # IPv6 범위 확인
        for ipv6_range in rule.get("Ipv6Ranges", []):
            if ipv6_range.get("CidrIpv6") == "::/0":
                return True

    return False


def get_filtered_data(raw_data: list[dict[str, Any]]) -> pd.DataFrame:
    """
    원시 Security Group 데이터를 필터링하여 필요한 정보만 추출합니다.

    Args:
        raw_data: Security Group 원시 데이터

    Returns:
        DataFrame: 필터링된 Security Group 데이터
    """
    if not raw_data:
        return pd.DataFrame()

    filtered_data = []

    for sg in raw_data:
        # 인바운드 규칙 문자열로 변환
        inbound_rules = _format_rules(sg.get("IpPermissions", []), "from")

        # 아웃바운드 규칙 문자열로 변환
        outbound_rules = _format_rules(sg.get("IpPermissionsEgress", []), "to")

        # 필터링된 데이터 생성
        filtered_sg = {
            "SecurityGroupId": sg.get("GroupId", ""),
            "SecurityGroupName": sg.get("GroupName", ""),
            "VpcId": sg.get("VpcId", ""),
            "Description": sg.get("Description", ""),
            "AnyOpenInbound": "⚠️ YES" if sg.get("HasAnyOpenInbound", False) else "No",
            "InboundRules": inbound_rules,
            "OutboundRules": outbound_rules,
            "Tags": _format_tags(sg.get("Tags", [])),
        }

        filtered_data.append(filtered_sg)

    return pd.DataFrame(filtered_data)


def _format_rules(rules: list[dict[str, Any]], direction: str) -> list[str]:
    """
    보안 그룹 규칙을 문자열 형태로 포맷팅합니다.

    Args:
        rules: 보안 그룹 규칙 목록
        direction: 규칙 방향 ("from" 또는 "to")

    Returns:
        list: 포맷팅된 규칙 문자열 목록
    """
    formatted_rules = []

    for rule in rules:
        protocol = rule.get("IpProtocol", "-1")
        if protocol == "-1":
            protocol = "All"

        from_port = rule.get("FromPort", "All")
        to_port = rule.get("ToPort", "All")

        # 포트 범위 표시
        port_range = "All"
        if from_port != "All" and to_port != "All":
            if from_port == to_port:
                port_range = str(from_port)
            else:
                port_range = f"{from_port}-{to_port}"

        # 모든 소스/대상 수집
        sources_destinations = []

        # IPv4 범위 처리
        for ip_range in rule.get("IpRanges", []):
            cidr = ip_range.get("CidrIp", "")
            description = ip_range.get("Description", "")
            ip_text = cidr
            if description:
                ip_text += f" ({description})"
            sources_destinations.append(ip_text)

        # IPv6 범위 처리
        for ipv6_range in rule.get("Ipv6Ranges", []):
            cidr = ipv6_range.get("CidrIpv6", "")
            description = ipv6_range.get("Description", "")
            ip_text = cidr
            if description:
                ip_text += f" ({description})"
            sources_destinations.append(ip_text)

        # 보안 그룹 참조 처리
        for sg_ref in rule.get("UserIdGroupPairs", []):
            sg_id = sg_ref.get("GroupId", "")
            description = sg_ref.get("Description", "")
            sg_text = sg_id
            if description:
                sg_text += f" ({description})"
            sources_destinations.append(sg_text)

        # Prefix List ID 처리
        for prefix_list in rule.get("PrefixListIds", []):
            prefix_id = prefix_list.get("PrefixListId", "")
            description = prefix_list.get("Description", "")
            prefix_text = prefix_id
            if description:
                prefix_text += f" ({description})"
            sources_destinations.append(prefix_text)

        # 규칙 문자열 생성
        if sources_destinations:
            for source_dest in sources_destinations:
                formatted_rules.append(
                    f"{protocol}:{port_range} {direction} {source_dest}"
                )

    return formatted_rules


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
