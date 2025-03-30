import pandas as pd

def get_raw_data(session, region=None):
    """
    S3 버킷 목록 조회
    정확한 CreateionDate를 얻기 위해서는 us-east-1 리전에서 조회해야 함
    """
    s3_client = session.client('s3')
    response = s3_client.list_buckets()
    return response

def get_filtered_data(raw_data):
    """
    원본 JSON에서 주요 필드만 추출해 DataFrame으로 반환
    """
    rows = []
    for bucket in raw_data.get('Buckets', []):
        row = {
            'BucketName': bucket.get('Name'),
            'CreationDate': str(bucket.get('CreationDate'))
        }
        rows.append(row)
    return pd.DataFrame(rows)