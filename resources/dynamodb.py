import pandas as pd

def get_raw_data(session, region):
    """
    DynamoDB 테이블 목록과 각 테이블의 상세 정보를 조회
    {"Tables": [table_detail, ...]} 형태로 반환
    """
    client = session.client('dynamodb', region_name=region)
    
    # 모든 테이블 이름 조회 (pagination 처리)
    table_names = []
    response = client.list_tables()
    table_names.extend(response.get("TableNames", []))
    while "LastEvaluatedTableName" in response:
        response = client.list_tables(ExclusiveStartTableName=response["LastEvaluatedTableName"])
        table_names.extend(response.get("TableNames", []))
    
    tables = []
    for table_name in table_names:
        detail_response = client.describe_table(TableName=table_name)
        table_detail = detail_response.get("Table", {})
        tables.append(table_detail)
    
    return {"Tables": tables}

def get_filtered_data(raw_data):
    """
    DynamoDB 테이블 상세 정보에서 주요 필드만 추출해 DataFrame으로 반환
    """
    rows = []
    for table in raw_data.get("Tables", []):
        row = {
            "TableName": table.get("TableName"),
            "TableStatus": table.get("TableStatus"),
            "CreationDateTime": str(table.get("CreationDateTime")),
            "ItemCount": table.get("ItemCount"),
            "TableSizeBytes": table.get("TableSizeBytes"),
        }
        throughput = table.get("ProvisionedThroughput", {})
        row["ReadCapacityUnits"] = throughput.get("ReadCapacityUnits")
        row["WriteCapacityUnits"] = throughput.get("WriteCapacityUnits")
        rows.append(row)
    return pd.DataFrame(rows)
