import pandas as pd
from utils.name_tag import extract_name_tag

def get_raw_data(session, region):
    """
    EBS 스냅샷 정보를 조회합니다.
    OwnerIds=['self']를 통해 현재 계정이 소유한 스냅샷만 조회합니다.
    """
    client = session.client('ec2', region_name=region)
    response = client.describe_snapshots(OwnerIds=['self'])
    return response

def get_filtered_data(raw_data):
    """
    EBS 스냅샷의 주요 필드를 추출합니다:
      - SnapshotId, VolumeId, StartTime, State, VolumeSize, Description
    """
    rows = []
    for snap in raw_data.get('Snapshots', []):
        name =  extract_name_tag(snap.get('Tags', []))
        if not name:
            name = "N/A"
        row = {
            'SnapshotId': snap.get('SnapshotId'),
            'VolumeId': snap.get('VolumeId'),
            'StartTime': str(snap.get('StartTime')),
            'State': snap.get('State'),
            'VolumeSize': snap.get('VolumeSize'),
            'Description': snap.get('Description')
        }
        rows.append(row)
    return pd.DataFrame(rows)
