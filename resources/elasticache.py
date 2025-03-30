import pandas as pd

def get_raw_data(session, region):
    """
    ElastiCache 클러스터 정보 조회
    ShowCacheNodeInfo=True로 추가 정보를 포함 시킴
    """
    client = session.client('elasticache', region_name=region)
    response = client.describe_cache_clusters(ShowCacheNodeInfo=True)
    return response

def get_filtered_data(raw_data):
    """
    원본 JSON에서 주요 필드만 추출해 DataFrame으로 반환
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
