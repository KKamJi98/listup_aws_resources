
import pandas as pd
from botocore.exceptions import ClientError

def get_raw_data(session, region):
    """
    AWS Security Group Rule 리소스 정보를 조회합니다.
    """
    try:
        ec2_client = session.client('ec2', region_name=region)
        response = ec2_client.describe_security_group_rules()
        rules = response.get('SecurityGroupRules', [])
        
        while 'NextToken' in response:
            response = ec2_client.describe_security_group_rules(
                NextToken=response['NextToken']
            )
            rules.extend(response.get('SecurityGroupRules', []))
            
        return rules
    except ClientError as e:
        print(f"Error fetching security group rules in {region}: {e}")
        return []

def get_filtered_data(raw_data):
    """
    원시 Security Group Rule 데이터를 필터링하여 필요한 정보만 추출합니다.
    """
    if not raw_data:
        return pd.DataFrame()
        
    filtered_data = []
    
    for rule in raw_data:
        filtered_rule = {
            'SecurityGroupRuleId': rule.get('SecurityGroupRuleId', ''),
            'GroupId': rule.get('GroupId', ''),
            'IsEgress': rule.get('IsEgress', ''),
            'IpProtocol': rule.get('IpProtocol', ''),
            'FromPort': rule.get('FromPort', ''),
            'ToPort': rule.get('ToPort', ''),
            'CidrIpv4': rule.get('CidrIpv4', ''),
            'Description': rule.get('Description', '')
        }
        filtered_data.append(filtered_rule)
    
    return pd.DataFrame(filtered_data)
