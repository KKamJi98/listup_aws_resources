import pandas as pd
from utils.name_tag import extract_name_tag

def get_raw_data(session, region):
    """
    Subnet 전체 목록 describe_subnets() 결과(원본 JSON)를 반환
    """
    ec2_client = session.client('ec2', region_name=region)
    response = ec2_client.describe_subnets()
    return response

def get_filtered_data(raw_data):
    """
    원본 JSON에서 주요 필드만 추출해 DataFrame으로 반환
    """
    rows = []
    for subnet in raw_data.get('Subnets', []):
        name = extract_name_tag(subnet.get('Tags', []))
        if not name:
            name = "N/A"
        row = {
            'Name': name,
            'SubnetId': subnet.get('SubnetId'),
            'VpcId': subnet.get('VpcId'),
            'CidrBlock': subnet.get('CidrBlock'),
            'AvailabilityZone': subnet.get('AvailabilityZone'),
            'State': subnet.get('State'),
            'AvailableIpAddressCount': subnet.get('AvailableIpAddressCount'),
            'DefaultForAz': subnet.get('DefaultForAz'),
            'MapPublicIpOnLaunch': subnet.get('MapPublicIpOnLaunch'),
            'Tags': extract_tags(subnet.get('Tags', []))
        }
        rows.append(row)
    return pd.DataFrame(rows)

def extract_tags(tags):
    """
    Subnet Tags 배열에서 Key=Value 형태의 문자열 목록을 반환하거나,
    필요한 특정 Tag만 골라서 반환할 수도 있음.
    """
    if not tags:
        return None
    # 예) 단순히 모든 태그를 "Key=Value" 형태로 joined string 생성
    return ";".join([f"{t['Key']}={t['Value']}" for t in tags if 'Key' in t and 'Value' in t])
