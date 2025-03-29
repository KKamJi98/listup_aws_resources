import pandas as pd

def get_raw_data(session, region):
    """
    ElastiCache 클러스터 정보를 조회합니다.
    boto3 클라이언트 'elasticache'를 사용하여 describe_cache_clusters()를 호출합니다.
    ShowCacheNodeInfo=True로 추가 정보를 포함할 수 있습니다.
    """
    client = session.client('elasticache', region_name=region)
    response = client.describe_cache_clusters(ShowCacheNodeInfo=True)
    return response

def get_filtered_data(raw_data):
    """
    원본 데이터에서 다음 핵심 필드를 추출합니다:
      - CacheClusterId, Engine, CacheNodeType, EngineVersion,
      - CacheClusterStatus, NumCacheNodes, PreferredAvailabilityZone
    """
    rows = []
    for cluster in raw_data.get('CacheClusters', []):
        row = {
            'CacheClusterId': cluster.get('CacheClusterId'),
            'Engine': cluster.get('Engine'),
            'CacheNodeType': cluster.get('CacheNodeType'),
            'EngineVersion': cluster.get('EngineVersion'),
            'CacheClusterStatus': cluster.get('CacheClusterStatus'),
            'NumCacheNodes': cluster.get('NumCacheNodes'),
            'PreferredAvailabilityZone': cluster.get('PreferredAvailabilityZone')
        }
        rows.append(row)
    return pd.DataFrame(rows)
