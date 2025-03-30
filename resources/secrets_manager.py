import pandas as pd
from utils.name_tag import extract_name_tag

def get_raw_data(session, region):
    """
    AWS Secrets Manager의 전체 비밀 목록을 조회합니다.
    """
    client = session.client('secretsmanager', region_name=region)
    secrets = []
    response = client.list_secrets()
    secrets.extend(response.get('SecretList', []))
    while 'NextToken' in response:
        response = client.list_secrets(NextToken=response['NextToken'])
        secrets.extend(response.get('SecretList', []))
    return {"SecretList": secrets}

def get_filtered_data(raw_data):
    """
    원본 JSON에서 주요 필드만 추출해 DataFrame으로 반환
    """
    rows = []
    for secret in raw_data.get('SecretList', []):
        name = extract_name_tag(secret.get('Tags', []))
        if not name:
            name = "N/A"
        row = {
            'Name': name,
            'ARN': secret.get('ARN'),
            'Description': secret.get('Description'),
            'LastChangedDate': str(secret.get('LastChangedDate')),
            'Tags': ";".join([f"{tag.get('Key')}={tag.get('Value')}" for tag in secret.get('Tags', [])]) if secret.get('Tags') else None
        }
        rows.append(row)
    return pd.DataFrame(rows)