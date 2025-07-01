import pandas as pd
from botocore.exceptions import ClientError


def get_raw_data(session, region):
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
            sg["HasAnyOpenInbound"] = False
            for rule in sg.get("IpPermissions", []):
                for ip_range in rule.get("IpRanges", []):
                    if ip_range.get("CidrIp") == "0.0.0.0/0":
                        sg["HasAnyOpenInbound"] = True
                        break
                if sg["HasAnyOpenInbound"]:
                    break

        return security_groups
    except ClientError as e:
        print(f"Error fetching security groups in {region}: {e}")
        return []


def get_filtered_data(raw_data):
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
        inbound_rules = []
        for rule in sg.get("IpPermissions", []):
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

            # IP 범위 표시
            ip_ranges = []
            for ip_range in rule.get("IpRanges", []):
                cidr = ip_range.get("CidrIp", "")
                description = ip_range.get("Description", "")
                ip_text = cidr
                if description:
                    ip_text += f" ({description})"
                ip_ranges.append(ip_text)

            # 보안 그룹 참조 표시
            sg_references = []
            for sg_ref in rule.get("UserIdGroupPairs", []):
                sg_id = sg_ref.get("GroupId", "")
                sg_references.append(sg_id)

            # 규칙 문자열 생성
            sources = ip_ranges + sg_references
            if sources:
                for source in sources:
                    inbound_rules.append(f"{protocol}:{port_range} from {source}")

        # 아웃바운드 규칙 문자열로 변환
        outbound_rules = []
        for rule in sg.get("IpPermissionsEgress", []):
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

            # IP 범위 표시
            ip_ranges = []
            for ip_range in rule.get("IpRanges", []):
                cidr = ip_range.get("CidrIp", "")
                description = ip_range.get("Description", "")
                ip_text = cidr
                if description:
                    ip_text += f" ({description})"
                ip_ranges.append(ip_text)

            # 보안 그룹 참조 표시
            sg_references = []
            for sg_ref in rule.get("UserIdGroupPairs", []):
                sg_id = sg_ref.get("GroupId", "")
                sg_references.append(sg_id)

            # 규칙 문자열 생성
            destinations = ip_ranges + sg_references
            if destinations:
                for destination in destinations:
                    outbound_rules.append(f"{protocol}:{port_range} to {destination}")

        # 필터링된 데이터 생성
        filtered_sg = {
            "SecurityGroupId": sg.get("GroupId", ""),
            "SecurityGroupName": sg.get("GroupName", ""),
            "VpcId": sg.get("VpcId", ""),
            "Description": sg.get("Description", ""),
            "AnyOpenInbound": "⚠️ YES" if sg.get("HasAnyOpenInbound", False) else "No",
            "InboundRules": "\n".join(inbound_rules) if inbound_rules else "-",
            "OutboundRules": "\n".join(outbound_rules) if outbound_rules else "-",
            "Tags": ", ".join(
                [
                    f"{tag.get('Key', '')}={tag.get('Value', '')}"
                    for tag in sg.get("Tags", [])
                ]
            ),
        }

        filtered_data.append(filtered_sg)

    return pd.DataFrame(filtered_data)
