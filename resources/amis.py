import pandas as pd

def get_raw_data(session, region):
    """
    현재 계정이 소유한 AMI 이미지를 조회
    describe_images() 호출 시 Owners=['self']를 지정
    """
    client = session.client('ec2', region_name=region)
    response = client.describe_images(Owners=['self'])
    return response

def get_filtered_data(raw_data):
    """
    AMI의 주요 필드 추출
    """
    rows = []
    for image in raw_data.get('Images', []):
        row = {
            'ImageId': image.get('ImageId'),
            'Name': image.get('Name'),
            'CreationDate': image.get('CreationDate'),
            'State': image.get('State'),
            'Public': image.get('Public')
        }
        rows.append(row)
    return pd.DataFrame(rows)
