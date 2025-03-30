import pandas as pd
from utils.name_tag import extract_name_tag

def get_raw_data(session, region):
    """
    EC2 인스턴스 전체 목록 describe_instances() 결과(원본 JSON)를 반환
    """
    ec2_client = session.client('ec2', region_name=region)
    response = ec2_client.describe_instances()
    # 보통 {'Reservations': [...]} 구조로 옴
    return response

def get_filtered_data(raw_data):
    """
    원본 JSON에서 주요 필드만 추출해 DataFrame으로 반환
    """
    rows = []
    reservations = raw_data.get('Reservations', [])
    for r in reservations:
        for inst in r.get('Instances', []):
            name = extract_name_tag(inst.get('Tags', []))
            if not name:
                name = "N/A"
            row = {
                'Name': name,
                'InstanceId': inst.get('InstanceId'),
                'InstanceType': inst.get('InstanceType'),
                'State': inst.get('State', {}).get('Name'),
                'PublicIp': inst.get('PublicIpAddress'),
                'PrivateIp': inst.get('PrivateIpAddress'),
                'LaunchTime': str(inst.get('LaunchTime'))  # 문자열 변환
            }
            rows.append(row)

    df = pd.DataFrame(rows)
    return df
