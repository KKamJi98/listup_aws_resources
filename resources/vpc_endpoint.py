import pandas as pd
from utils.name_tag import extract_name_tag

def get_raw_data(session, region):
    '''
    vpc endpoint의 전체 목록 조회
    '''
    client = session.client('ec2', region_name=region)
    response = client.describe_vpc_endpoints()
    return response

def get_filtered_data(raw_data):
    '''
    원본 JSON에서 주요 필드와 생성 날짜(YYYY-MM-DD 형식)를 추출해 DataFrame으로 반환
    '''
    rows = []
    for ep in raw_data.get('VpcEndpoints', []):
        name = extract_name_tag(ep.get('Tags'))
        if not name:
            name = "N/A"

        creation_timestamp = ep.get('CreationTimestamp')
        formatted_date = creation_timestamp.strftime('%Y-%m-%d') if creation_timestamp else "N/A"

        row = {
            'Name': name,
            'VpcEndpointId': ep.get('VpcEndpointId'),
            'VpcId': ep.get('VpcId'),
            'ServiceName': ep.get('ServiceName'),
            'State': ep.get('State'),
            'CreationDate': formatted_date,
            'RouteTableIds': ",".join(ep.get('RouteTableIds', [])) if ep.get('RouteTableIds') else None,
            'PolicyDocument': str(ep.get('PolicyDocument')) if ep.get('PolicyDocument') else None
        }
        rows.append(row)
    return pd.DataFrame(rows)
