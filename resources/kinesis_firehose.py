import pandas as pd

def get_raw_data(session, region):
    """
    Kinesis Data Firehose의 Delivery Stream 목록을 조회하고,
    각 Delivery Stream에 대해 describe_delivery_stream()으로 상세 정보를 수집합니다.
    반환 구조: {"DeliveryStreams": [stream_detail, ...]}
    """
    client = session.client('firehose', region_name=region)
    stream_names = []
    response = client.list_delivery_streams()
    stream_names.extend(response.get("DeliveryStreamNames", []))
    while response.get("HasMoreDeliveryStreams", False):
        response = client.list_delivery_streams(
            ExclusiveStartDeliveryStreamName=stream_names[-1]
        )
        stream_names.extend(response.get("DeliveryStreamNames", []))
        
    streams = []
    for name in stream_names:
        detail_response = client.describe_delivery_stream(DeliveryStreamName=name)
        streams.append(detail_response.get("DeliveryStreamDescription", {}))
    return {"DeliveryStreams": streams}

def get_filtered_data(raw_data):
    """
    추출 필드:
      - DeliveryStreamName
      - DeliveryStreamStatus
      - DeliveryStreamType
      - VersionId
      - DeliveryStreamArn
    """
    rows = []
    for stream in raw_data.get("DeliveryStreams", []):
        row = {
            "DeliveryStreamName": stream.get("DeliveryStreamName"),
            "DeliveryStreamStatus": stream.get("DeliveryStreamStatus"),
            "DeliveryStreamType": stream.get("DeliveryStreamType"),
            "VersionId": stream.get("VersionId"),
            "DeliveryStreamArn": stream.get("DeliveryStreamArn")
        }
        rows.append(row)
    return pd.DataFrame(rows)
