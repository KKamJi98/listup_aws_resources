
import pandas as pd
from botocore.exceptions import ClientError

def get_raw_data(session, region):
    """
    AWS ECR 리소스 정보를 조회합니다.
    """
    try:
        ecr_client = session.client('ecr', region_name=region)
        response = ecr_client.describe_repositories()
        repositories = response.get('repositories', [])
        
        while 'nextToken' in response:
            response = ecr_client.describe_repositories(
                nextToken=response['nextToken']
            )
            repositories.extend(response.get('repositories', []))
            
        return repositories
    except ClientError as e:
        print(f"Error fetching ECR repositories in {region}: {e}")
        return []

def get_filtered_data(raw_data):
    """
    원시 ECR 데이터를 필터링하여 필요한 정보만 추출합니다.
    """
    if not raw_data:
        return pd.DataFrame()
        
    filtered_data = []
    
    for repo in raw_data:
        filtered_repo = {
            'RepositoryName': repo.get('repositoryName', ''),
            'RepositoryArn': repo.get('repositoryArn', ''),
            'RepositoryUri': repo.get('repositoryUri', ''),
            'CreatedAt': repo.get('createdAt', '').replace(tzinfo=None),
            'ImageTagMutability': repo.get('imageTagMutability', ''),
            'ImageScanningConfiguration': repo.get('imageScanningConfiguration', {}).get('scanOnPush', False)
        }
        filtered_data.append(filtered_repo)
    
    return pd.DataFrame(filtered_data)
