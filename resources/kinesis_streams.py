import pandas as pd


def get_raw_data(session, region):
    """
    Kinesis Streams의 전체 목록을 조회
    list_streams()로 Stream 목록을 조회하고, 각 Stream의 상세 정보를 describe_stream()로 조회하여 반환
    """
    client = session.client("kinesis", region_name=region)
    stream_names = []
    response = client.list_streams()
    stream_names.extend(response.get("StreamNames", []))
    while response.get("HasMoreStreams", False):
        # ExclusiveStartStreamName는 마지막 스트림 이름을 지정합니다.
        response = client.list_streams(ExclusiveStartStreamName=stream_names[-1])
        stream_names.extend(response.get("StreamNames", []))

    streams = []
    for name in stream_names:
        detail_response = client.describe_stream(StreamName=name)
        streams.append(detail_response.get("StreamDescription", {}))
    return {"Streams": streams}


def get_filtered_data(raw_data):
    """
    원본 JSON에서 주요 필드만 추출해 DataFrame으로 반환
    """
    rows = []
    for stream in raw_data.get("Streams", []):
        row = {
            "StreamName": stream.get("StreamName"),
            "StreamStatus": stream.get("StreamStatus"),
            "RetentionPeriodHours": stream.get("RetentionPeriodHours"),
            "OpenShardCount": stream.get("OpenShardCount"),
            "StreamARN": stream.get("StreamARN"),
        }
        rows.append(row)
    return pd.DataFrame(rows)
