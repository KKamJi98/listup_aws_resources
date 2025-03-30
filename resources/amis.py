import pandas as pd
from datetime import datetime

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
    AMI의 주요 필드를 추출합니다.
    각 날짜는 "YYYY-MM-DD" 형식으로 변환
    """
    rows = []
    for image in raw_data.get('Images', []):
        row = {
            'Name': image.get('Name') if image.get('Name') else "N/A",
            'ImageId': image.get('ImageId'),
            'CreationDate': datetime.strptime(image.get('CreationDate'), "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d") if image.get('CreationDate') else "N/A",
            'State': image.get('State'),
            'Public': image.get('Public')
        }
        rows.append(row)
    return pd.DataFrame(rows)
