import pandas as pd

def get_raw_data(session, region=None):
    """
    S3는 글로벌 리소스이므로, region 인자는 무시하고 S3 버킷 목록을 조회합니다.
    boto3 클라이언트를 사용해 list_buckets()를 호출하고, 원본 JSON 응답을 반환합니다.
    """
    s3_client = session.client('s3')
    response = s3_client.list_buckets()
    return response

def get_filtered_data(raw_data):
    """
    S3 버킷 목록에서 BucketName, CreationDate 등의 핵심 필드를 추출하여 DataFrame으로 반환합니다.
    """
    rows = []
    for bucket in raw_data.get('Buckets', []):
        row = {
            'BucketName': bucket.get('Name'),
            'CreationDate': str(bucket.get('CreationDate'))
        }
        rows.append(row)
    return pd.DataFrame(rows)