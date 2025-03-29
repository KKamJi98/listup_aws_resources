import pandas as pd

def get_raw_data(session, region=None):
    """
    Route53 HostedZone는 글로벌 서비스이므로 region 인자는 무시합니다.
    list_hosted_zones()를 호출하여 전체 HostedZone 목록을 조회합니다.
    """
    client = session.client('route53')
    response = client.list_hosted_zones()
    return response

def get_filtered_data(raw_data):
    """
    추출 필드:
      - Id
      - Name (추출 시 trailing '.' 제거)
      - CallerReference
      - ResourceRecordSetCount
      - Config (전체 혹은 필요한 부분)
    """
    rows = []
    for zone in raw_data.get("HostedZones", []):
        # zone["Name"]의 마지막에 '.'이 있는 경우 제거
        name = zone.get("Name", "")
        if name.endswith('.'):
            name = name[:-1]
        row = {
            "Id": zone.get("Id"),
            "Name": name,
            "CallerReference": zone.get("CallerReference"),
            "ResourceRecordSetCount": zone.get("ResourceRecordSetCount"),
            "Config": zone.get("Config")
        }
        rows.append(row)
    return pd.DataFrame(rows)
