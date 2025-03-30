import pandas as pd

def get_raw_data(session, region):
    """
    Kinesis Firehose의 전체 목록을 조회
    list_delivery_streams()로 Delivery Stream 목록을 조회하고, 각 Delivery Stream의 상세 정보를 describe_delivery_stream()로 조회하여 반환
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
    원본 JSON에서 주요 필드만 추출해 DataFrame으로 반환
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
