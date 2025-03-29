import pandas as pd

def get_raw_data(session, region):
    """
    EKS 클러스터 전체 목록 list_clusters() + describe_cluster()
    보통 list_clusters()로 이름 목록 -> describe_cluster()로 세부 정보
    """
    eks_client = session.client('eks', region_name=region)
    cluster_list = eks_client.list_clusters()
    clusters = []
    for name in cluster_list.get('clusters', []):
        detail = eks_client.describe_cluster(name=name)
        clusters.append(detail.get('cluster', {}))
    # 반환 형태를 dict로 통일
    return {"Clusters": clusters}

def get_filtered_data(raw_data):
    """
    클러스터 이름, 상태, 엔드포인트, 버전, 생성일 등 추출
    """
    rows = []
    for cluster in raw_data.get('Clusters', []):
        row = {
            'Name': cluster.get('name'),
            'Status': cluster.get('status'),
            'Endpoint': cluster.get('endpoint'),
            'Version': cluster.get('version'),
            'CreatedAt': str(cluster.get('createdAt'))
        }
        rows.append(row)
    return pd.DataFrame(rows)
