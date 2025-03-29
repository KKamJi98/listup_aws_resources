import pandas as pd

def get_raw_data(session, region):
    """
    Secrets Manager는 리전별로 동작하므로 boto3 클라이언트를 사용해 list_secrets()를 호출합니다.
    Pagination 처리가 필요하므로 모든 페이지의 SecretList를 수집하여 반환합니다.
    반환 구조: {"SecretList": [secret1, secret2, ...]}
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
    Secrets Manager의 원본 응답에서 주요 필드만 추출하여 DataFrame으로 반환합니다.
    추출 필드:
      - Name: 태그 'Name'이 있으면 해당 값을, 없으면 secret의 Name 값을 사용
      - ARN
      - Description
      - LastChangedDate
      - Tags: 전체 태그를 "Key=Value;Key=Value" 형식으로 병합
    """
    rows = []
    for secret in raw_data.get('SecretList', []):
        name_tag = extract_name_tag(secret.get('Tags', []))
        row = {
            'Name': name_tag if name_tag else secret.get('Name'),
            'ARN': secret.get('ARN'),
            'Description': secret.get('Description'),
            'LastChangedDate': str(secret.get('LastChangedDate')),
            'Tags': ";".join([f"{tag.get('Key')}={tag.get('Value')}" for tag in secret.get('Tags', [])]) if secret.get('Tags') else None
        }
        rows.append(row)
    return pd.DataFrame(rows)

def extract_name_tag(tags):
    """
    태그 리스트에서 'Name' 태그의 값을 추출합니다.
    없으면 None 반환.
    """
    if not tags:
        return None
    for tag in tags:
        if tag.get('Key') == 'Name':
            return tag.get('Value')
    return None
