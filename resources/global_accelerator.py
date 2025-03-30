import pandas as pd

def get_raw_data(session, region):
    """
    Global Accelerator(Global)의 전체 목록을 조회
    list_accelerators()로 Accelerator 목록을 조회하고, 각 Accelerator의 상세 정보를 describe_accelerator()로 조회하여 반환
    """
    client = session.client('globalaccelerator', region_name=region)
    response = client.list_accelerators()
    accelerators = response.get('Accelerators', [])
    
    details = []
    for acc in accelerators:
        arn = acc.get('AcceleratorArn')
        if arn:
            detail_response = client.describe_accelerator(AcceleratorArn=arn)
            details.append(detail_response.get('Accelerator'))
    
    return {"Accelerators": details}

def get_filtered_data(raw_data):
    """
    원본 JSON에서 주요 필드만 추출해 DataFrame으로 반환
    """
    rows = []
    for acc in raw_data.get("Accelerators", []):
        row = {
            'AcceleratorArn': acc.get('AcceleratorArn'),
            'Name': acc.get('Name'),
            'Status': acc.get('Status'),
            'IpAddressType': acc.get('IpAddressType'),
            'Enabled': acc.get('Enabled'),
            'CreatedTime': str(acc.get('CreatedTime')),
            'LastModifiedTime': str(acc.get('LastModifiedTime'))
        }
        rows.append(row)
    return pd.DataFrame(rows)
