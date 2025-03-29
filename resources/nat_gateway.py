import pandas as pd

def get_raw_data(session, region):
    """
    NAT Gateway 정보를 조회합니다.
    """
    client = session.client('ec2', region_name=region)
    response = client.describe_nat_gateways()
    return response

def get_filtered_data(raw_data):
    """
    NAT Gateway의 주요 필드를 추출합니다:
      - NatGatewayId, State, VpcId, SubnetId, CreateTime
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
