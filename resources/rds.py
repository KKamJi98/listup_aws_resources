import pandas as pd

def get_raw_data(session, region):
    """
    RDS 인스턴스 전체 목록 describe_db_instances() 결과(원본 JSON)를 반환
    """
    rds_client = session.client('rds', region_name=region)
    response = rds_client.describe_db_instances()
    return response

def get_filtered_data(raw_data):
    """
    DBInstanceIdentifier, DBInstanceClass, 엔진, 상태, Endpoint, AllocatedStorage 등 추출
    """
    rows = []
    for dbi in raw_data.get('DBInstances', []):
        row = {
            'DBInstanceIdentifier': dbi.get('DBInstanceIdentifier'),
            'DBInstanceClass': dbi.get('DBInstanceClass'),
            'Engine': dbi.get('Engine'),
            'DBInstanceStatus': dbi.get('DBInstanceStatus'),
            'Endpoint': dbi.get('Endpoint', {}).get('Address') if dbi.get('Endpoint') else None,
            'AllocatedStorage': dbi.get('AllocatedStorage')
        }
        rows.append(row)
    return pd.DataFrame(rows)
