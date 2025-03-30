import pandas as pd

def get_raw_data(session, region):
    """
    Glue Job 목록 조회
    """
    client = session.client('glue', region_name=region)
    response = client.get_jobs()
    # 반환 구조는 {"Jobs": [job, job, ...]}
    return response

def get_filtered_data(raw_data):
    """
    원본 JSON에서 주요 필드만 추출해 DataFrame으로 반환
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
