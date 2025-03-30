import pandas as pd

def get_raw_data(session, region):
    """
    NAT Gateway의 전체 목록 조회
    """
    client = session.client('ec2', region_name=region)
    response = client.describe_nat_gateways()
    return response

def get_filtered_data(raw_data):
    """
    원본 JSON에서 주요 필드만 추출해 DataFrame으로 반환
    """
    rows = []
    for nat in raw_data.get('NatGateways', []):
        row = {
            'NatGatewayId': nat.get('NatGatewayId'),
            'State': nat.get('State'),
            'VpcId': nat.get('VpcId'),
            'SubnetId': nat.get('SubnetId'),
            'CreateTime': str(nat.get('CreateTime'))
        }
        rows.append(row)
    return pd.DataFrame(rows)
