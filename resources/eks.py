import pandas as pd


def get_raw_data(session, region):
    """
    EKS 클러스터 전체 목록 list_clusters() + describe_cluster()
    {"Clusters": [cluster_detail, ...]} 형태로 반환
    """
    eks_client = session.client("eks", region_name=region)
    cluster_list = eks_client.list_clusters()
    clusters = []
    for name in cluster_list.get("clusters", []):
        detail = eks_client.describe_cluster(name=name)
        clusters.append(detail.get("cluster", {}))
    return {"Clusters": clusters}


def get_filtered_data(raw_data):
    """
    원본 JSON에서 주요 필드만 추출해 DataFrame으로 반환
    각 날짜는 "YYYY-MM-DD" 형식으로 변환
    """
    rows = []
    for cluster in raw_data.get("Clusters", []):
        row = {
            "Name": cluster.get("name"),
            "Status": cluster.get("status"),
            "Endpoint": cluster.get("endpoint"),
            "Version": cluster.get("version"),
            "CreatedAt": (
                cluster.get("createdAt").strftime("%Y-%m-%d")
                if cluster.get("createdAt")
                else "N/A"
            ),
        }
        rows.append(row)
    return pd.DataFrame(rows)
