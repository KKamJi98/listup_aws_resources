import pandas as pd
from utils.name_tag import extract_name_tag

def get_raw_data(session, region):
    client = session.client('ec2', region_name=region)
    response = client.describe_vpc_endpoints()
    return response

def get_filtered_data(raw_data):
    rows = []
    for ep in raw_data.get('VpcEndpoints', []):
        name = extract_name_tag(ep.get('Tags'))
        if not name:
            name = "N/A"
        row = {
            'Name': name,
            'VpcEndpointId': ep.get('VpcEndpointId'),
            'VpcId': ep.get('VpcId'),
            'ServiceName': ep.get('ServiceName'),
            'State': ep.get('State'),
            'RouteTableIds': ",".join(ep.get('RouteTableIds', [])) if ep.get('RouteTableIds') else None,
            'PolicyDocument': str(ep.get('PolicyDocument')) if ep.get('PolicyDocument') else None
        }
        rows.append(row)
    return pd.DataFrame(rows)
