import pandas as pd

def get_raw_data(session, region):
    """
    Classic ELB와 ELBv2 (ALB, NLB) 정보를 모두 조회하여 반환
    - Classic ELB: boto3 클라이언트 'elb' 사용, describe_load_balancers() 호출
    - ELBv2: boto3 클라이언트 'elbv2' 사용, describe_load_balancers() 호출
    반환 구조:
    {
        "Classic": [list of Classic ELB descriptions],
        "v2": [list of ELBv2 load balancer descriptions]
    }
    """
    raw_data = {"Classic": [], "v2": []}

    # Classic ELB
    elb_client = session.client('elb', region_name=region)
    classic_response = elb_client.describe_load_balancers()
    raw_data["Classic"] = classic_response.get("LoadBalancerDescriptions", [])

    # ELBv2 (ALB, NLB)
    elbv2_client = session.client('elbv2', region_name=region)
    v2_response = elbv2_client.describe_load_balancers()
    raw_data["v2"] = v2_response.get("LoadBalancers", [])

    return raw_data

def get_filtered_data(raw_data):
    """
    원본 JSON에서 주요 필드만 추출해 DataFrame으로 반환
    각 날짜는 "YYYY-MM-DD" 형식으로 변환
    """
    rows = []
    # Classic ELB 처리
    for elb in raw_data.get("Classic", []):
        row = {
            "LoadBalancerName": elb.get("LoadBalancerName"),
            "Type": "classic",
            "DNSName": elb.get("DNSName"),
            "Scheme": elb.get("Scheme", "N/A"),
            "VpcId": elb.get("VPCId", "N/A"),
            "CreatedDate": elb.get("CreatedTime").strftime("%Y-%m-%d") if elb.get("CreatedTime") else "N/A",
            "State": "N/A"  # Classic ELB에는 별도의 상태 정보가 없음
        }
        rows.append(row)
    
    # ELBv2 처리 (ALB, NLB)
    for elb in raw_data.get("v2", []):
        row = {
            "LoadBalancerName": elb.get("LoadBalancerName"),
            "Type": elb.get("Type", "N/A"),
            "DNSName": elb.get("DNSName"),
            "Scheme": elb.get("Scheme", "N/A"),
            "VpcId": elb.get("VpcId", "N/A"),
            "CreatedDate": elb.get("CreatedTime").strftime("%Y-%m-%d") if elb.get("CreatedTime") else "N/A",
            "State": elb.get("State", {}).get("Code", "N/A")
        }
        rows.append(row)
    
    return pd.DataFrame(rows)
