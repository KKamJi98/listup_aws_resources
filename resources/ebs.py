import pandas as pd

def get_raw_data(session, region):
    """
    EBS Volume 정보를 조회합니다.
    boto3 클라이언트를 사용하여 describe_volumes()를 호출하고,
    원본 JSON 응답을 그대로 반환합니다.
    """
    ec2_client = session.client('ec2', region_name=region)
    response = ec2_client.describe_volumes()
    return response

def get_filtered_data(raw_data):
    """
    원본 JSON 응답에서 EBS Volume의 주요 필드를 추출하여 DataFrame으로 반환합니다.
    추출 필드:
      - VolumeId
      - Name (태그 'Name'이 있으면 사용, 없으면 VolumeId)
      - Size (GB)
      - VolumeType
      - State
      - AvailabilityZone
      - CreateTime
      - Tags (전체 태그 정보를 "Key=Value;Key=Value" 형태로 병합)
    """
    rows = []
    for volume in raw_data.get('Volumes', []):
        name = extract_name_tag(volume.get('Tags', []))
        row = {
            'VolumeId': volume.get('VolumeId'),
            'Name': name if name else volume.get('VolumeId'),
            'Size': volume.get('Size'),
            'VolumeType': volume.get('VolumeType'),
            'State': volume.get('State'),
            'AvailabilityZone': volume.get('AvailabilityZone'),
            'CreateTime': str(volume.get('CreateTime')),
            'Tags': ";".join([f"{t.get('Key')}={t.get('Value')}" for t in volume.get('Tags', [])]) if volume.get('Tags') else None,
        }
        rows.append(row)
    return pd.DataFrame(rows)

def extract_name_tag(tags):
    """
    태그 리스트에서 'Name' 태그의 값을 추출하여 반환합니다.
    존재하지 않으면 None 반환.
    """
    if not tags:
        return None
    for tag in tags:
        if tag.get('Key') == 'Name':
            return tag.get('Value')
    return None
