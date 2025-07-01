import pandas as pd

from utils.name_tag import extract_name_tag


def get_raw_data(session, region):
    """
    EBS Volume 정보를 조회합니다.
    """
    ec2_client = session.client("ec2", region_name=region)
    response = ec2_client.describe_volumes()
    return response


def get_filtered_data(raw_data):
    """
    원본 JSON 응답에서 EBS Volume의 주요 필드를 추출하여 DataFrame으로 반환합니다.
    """
    rows = []
    for volume in raw_data.get("Volumes", []):
        name = extract_name_tag(volume.get("Tags", []))
        row = {
            "Name": name if name else "N/A",
            "VolumeId": volume.get("VolumeId"),
            "Size": volume.get("Size"),
            "VolumeType": volume.get("VolumeType"),
            "State": volume.get("State"),
            "AvailabilityZone": volume.get("AvailabilityZone"),
            "CreateTime": (
                volume.get("CreateTime").strftime("%Y-%m-%d")
                if volume.get("CreateTime")
                else "N/A"
            ),
            "Tags": (
                ";".join(
                    [f"{t.get('Key')}={t.get('Value')}" for t in volume.get("Tags", [])]
                )
                if volume.get("Tags")
                else None
            ),
        }
        rows.append(row)
    return pd.DataFrame(rows)
