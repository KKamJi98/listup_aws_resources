import pandas as pd


def get_raw_data(session, region=None):
    """
    Route 53의 Hosted Zone 목록을 조회
    """
    client = session.client("route53")
    response = client.list_hosted_zones()
    return response


def get_filtered_data(raw_data):
    """
    원본 JSON에서 주요 필드만 추출해 DataFrame으로 반환
    """
    rows = []
    for zone in raw_data.get("HostedZones", []):
        # zone["Name"]의 마지막에 '.'이 있는 경우 제거
        name = zone.get("Name", "")
        if name.endswith("."):
            name = name[:-1]
        row = {
            "Name": name,
            "Id": zone.get("Id"),
            "CallerReference": zone.get("CallerReference"),
            "ResourceRecordSetCount": zone.get("ResourceRecordSetCount"),
            "Config": zone.get("Config"),
        }
        rows.append(row)
    return pd.DataFrame(rows)
