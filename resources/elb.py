import pandas as pd

def get_raw_data(session, region):
    """
    Classic ELB와 ELBv2 (ALB, NLB) 정보를 모두 조회하여 반환합니다.
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
    raw_data에서 Classic ELB와 ELBv2 정보를 통합하여,
    다음 핵심 필드를 추출합니다:
      - Provider: "classic" 또는 "v2"
      - LoadBalancerName
      - Type (Classic은 "classic", ELBv2는 실제 Type, 예: "application" 또는 "network")
      - DNSName
      - Scheme
      - VpcId
      - CreatedTime
      - State (ELBv2의 경우, State.Code; Classic은 해당 정보 없음)
    DataFrame으로 반환합니다.
    """
    rows = []
    # Classic ELB 처리
    for elb in raw_data.get("Classic", []):
        row = {
            "Provider": "classic",
            "LoadBalancerName": elb.get("LoadBalancerName"),
            "Type": "classic",
            "DNSName": elb.get("DNSName"),
            "Scheme": elb.get("Scheme", "N/A"),
            "VpcId": elb.get("VPCId", "N/A"),
            "CreatedTime": str(elb.get("CreatedTime")),
            "State": "N/A"  # Classic ELB에는 별도의 상태 정보가 없음
        }
        rows.append(row)
    
    # ELBv2 처리 (ALB, NLB)
    for elb in raw_data.get("v2", []):
        row = {
            "Provider": "v2",
            "LoadBalancerName": elb.get("LoadBalancerName"),
            "Type": elb.get("Type", "N/A"),
            "DNSName": elb.get("DNSName"),
            "Scheme": elb.get("Scheme", "N/A"),
            "VpcId": elb.get("VpcId", "N/A"),
            "CreatedTime": str(elb.get("CreatedTime")),
            "State": elb.get("State", {}).get("Code", "N/A")
        }
        rows.append(row)
    
    return pd.DataFrame(rows)
