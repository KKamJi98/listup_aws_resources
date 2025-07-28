import pandas as pd

from utils.name_tag import extract_name_tag


def get_raw_data(session, region):
    """
    VPC 전체 목록 describe_vpcs() 결과(원본 JSON)를 반환
    """
    ec2_client = session.client("ec2", region_name=region)
    response = ec2_client.describe_vpcs()
    return response


def get_filtered_data(raw_data):
    """
    원본 JSON에서 주요 필드만 추출해 DataFrame으로 반환
    """
    rows = []
    for vpc in raw_data.get("Vpcs", []):
        name = extract_name_tag(vpc.get("Tags", []))
        if not name:
            name = "N/A"
        row = {
            "Name": name,
            "VpcId": vpc.get("VpcId"),
            "State": vpc.get("State"),
            "CidrBlock": vpc.get("CidrBlock"),
            "IsDefault": vpc.get("IsDefault"),
        }
        rows.append(row)
    return pd.DataFrame(rows)
    return None
