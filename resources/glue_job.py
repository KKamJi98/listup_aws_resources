import pandas as pd

def get_raw_data(session, region):
    """
    Glue Job 목록을 조회합니다.
    get_jobs()를 호출하여 모든 Job 정보를 반환합니다.
    """
    client = session.client('glue', region_name=region)
    response = client.get_jobs()
    # 반환 구조는 {"Jobs": [job, job, ...]}
    return response

def get_filtered_data(raw_data):
    """
    추출 필드:
      - JobName
      - CreatedOn
      - LastModifiedOn
      - Role
      - Command (예: command.Name)
    """
    rows = []
    for job in raw_data.get("Jobs", []):
        row = {
            "JobName": job.get("Name"),
            "CreatedOn": str(job.get("CreatedOn")),
            "LastModifiedOn": str(job.get("LastModifiedOn")),
            "Role": job.get("Role"),
            "Command": job.get("Command", {}).get("Name")
        }
        rows.append(row)
    return pd.DataFrame(rows)
