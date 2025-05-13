import pandas as pd
from utils.name_tag import extract_name_tag
import botocore  # Import botocore for exception handling

def get_raw_data(session, region):
    """
    Internet Gateway의 전체 목록 조회
    """
    client = session.client('ec2', region_name=region)
    try:
        response = client.describe_internet_gateways()
        return response
    except botocore.exceptions.ClientError as e:
        print(f"An error occurred while describing internet gateways: {e}")
        return None


def get_filtered_data(raw_data):
    """
    원본 JSON에서 주요 필드만 추출해 DataFrame으로 반환
    """
    rows = []
    for igw in raw_data.get('InternetGateways', []):
        name = extract_name_tag(igw.get('Tags', []))
        if not name:
            name = "N/A"
        
        # Extract VPC IDs from attachments
        vpc_ids = []
        state = "N/A"
        for attachment in igw.get('Attachments', []):
            vpc_ids.append(attachment.get('VpcId'))
            state = attachment.get('State')
        
        vpc_id = ', '.join(vpc_ids) if vpc_ids else "N/A"
        
        row = {
            'Name': name,
            'InternetGatewayId': igw.get('InternetGatewayId'),
            'VpcId': vpc_id,
            'State': state,
        }
        rows.append(row)
    return pd.DataFrame(rows)