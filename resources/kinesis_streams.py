import pandas as pd

def get_raw_data(session, region):
    """
    Kinesis Data Streams 목록을 조회하고, 각 스트림에 대해 describe_stream() 호출로 상세 정보를 수집합니다.
    Pagination이 있을 수 있으므로 모든 스트림 이름을 모아서 조회합니다.
    반환 구조: {"Streams": [stream_detail, ...]}
    """
    client = session.client('kinesis', region_name=region)
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
    추출 필드:
      - StreamName
      - StreamStatus
      - RetentionPeriodHours
      - OpenShardCount
      - StreamARN
    """
    rows = []
    for stream in raw_data.get("Streams", []):
        row = {
            "StreamName": stream.get("StreamName"),
            "StreamStatus": stream.get("StreamStatus"),
            "RetentionPeriodHours": stream.get("RetentionPeriodHours"),
            "OpenShardCount": stream.get("OpenShardCount"),
            "StreamARN": stream.get("StreamARN")
        }
        rows.append(row)
    return pd.DataFrame(rows)
