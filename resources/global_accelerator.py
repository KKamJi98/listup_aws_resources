import pandas as pd

def get_raw_data(session, region):
    """
    Global Accelerator는 글로벌 서비스이므로 region 인자는 크게 무시됩니다.
    boto3 클라이언트를 사용해 list_accelerators()를 호출하고,
    각 Accelerator의 상세 정보를 describe_accelerator()로 조회하여 반환합니다.
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
    Global Accelerator의 원본 데이터에서 AcceleratorArn, Name, Status, IpAddressType, Enabled,
    CreatedTime, LastModifiedTime 등의 핵심 필드를 추출해 DataFrame으로 반환합니다.
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
