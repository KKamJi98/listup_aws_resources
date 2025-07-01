import pandas as pd

from utils.name_tag import extract_name_tag


def get_raw_data(session, region):
    """
    Elastic IP의 전체 목록 조회
    """
    client = session.client("ec2", region_name=region)
    response = client.describe_addresses()
    return response


def get_filtered_data(raw_data):
    """
    원본 JSON에서 주요 필드만 추출해 DataFrame으로 반환
    """
    rows = []
    for eip in raw_data.get("Addresses", []):
        name = extract_name_tag(eip.get("Tags", []))
        if not name:
            name = "N/A"
        row = {
            "Name": name,
            "PublicIp": eip.get("PublicIp"),
            "AllocationId": eip.get("AllocationId"),
            "AssociationId": eip.get("AssociationId"),
            "Domain": eip.get("Domain"),
            "InstanceId": eip.get("InstanceId"),
            "NetworkInterfaceId": eip.get("NetworkInterfaceId"),
            "PrivateIpAddress": eip.get("PrivateIpAddress"),
        }
        rows.append(row)
    return pd.DataFrame(rows)
