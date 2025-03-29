import pandas as pd

def get_raw_data(session, region):
    """
    VPC 엔드포인트 정보를 조회합니다.
    """
    client = session.client('ec2', region_name=region)
    response = client.describe_vpc_endpoints()
    return response

def get_filtered_data(raw_data):
    """
    VPC 엔드포인트의 주요 필드를 추출합니다:
      - VpcEndpointId, VpcId, ServiceName, State, RouteTableIds, PolicyDocument
    """
    rows = []
    for ep in raw_data.get('VpcEndpoints', []):
        row = {
            'VpcEndpointId': ep.get('VpcEndpointId'),
            'VpcId': ep.get('VpcId'),
            'ServiceName': ep.get('ServiceName'),
            'State': ep.get('State'),
            'RouteTableIds': ",".join(ep.get('RouteTableIds', [])) if ep.get('RouteTableIds') else None,
            'PolicyDocument': str(ep.get('PolicyDocument')) if ep.get('PolicyDocument') else None
        }
        rows.append(row)
    return pd.DataFrame(rows)
