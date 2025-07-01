
import pandas as pd
from botocore.exceptions import ClientError

def get_raw_data(session, region):
    """
    AWS Auto Scaling Group 리소스 정보를 조회합니다.
    """
    try:
        asg_client = session.client('autoscaling', region_name=region)
        response = asg_client.describe_auto_scaling_groups()
        asgs = response.get('AutoScalingGroups', [])
        
        while 'NextToken' in response:
            response = asg_client.describe_auto_scaling_groups(
                NextToken=response['NextToken']
            )
            asgs.extend(response.get('AutoScalingGroups', []))
            
        return asgs
    except ClientError as e:
        print(f"Error fetching Auto Scaling Groups in {region}: {e}")
        return []

def get_filtered_data(raw_data):
    """
    원시 Auto Scaling Group 데이터를 필터링하여 필요한 정보만 추출합니다.
    """
    if not raw_data:
        return pd.DataFrame()
        
    filtered_data = []
    
    for asg in raw_data:
        filtered_asg = {
            'AutoScalingGroupName': asg.get('AutoScalingGroupName', ''),
            'LaunchConfigurationName': asg.get('LaunchConfigurationName', ''),
            'MinSize': asg.get('MinSize', ''),
            'MaxSize': asg.get('MaxSize', ''),
            'DesiredCapacity': asg.get('DesiredCapacity', ''),
            'AvailabilityZones': ", ".join(asg.get('AvailabilityZones', [])),
            'HealthCheckType': asg.get('HealthCheckType', ''),
            'CreatedTime': asg.get('CreatedTime', '').replace(tzinfo=None)
        }
        filtered_data.append(filtered_asg)
    
    return pd.DataFrame(filtered_data)
