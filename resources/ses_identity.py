from typing import Any, Dict, List

import pandas as pd


def get_raw_data(session: Any, region: str) -> Dict[str, Any]:
    """
    SES Identity 전체 목록 및 상세 정보를 조회하여 반환

    1. list_identities로 모든 자격 증명 목록 조회
    2. get_identity_verification_attributes로 각 자격 증명의 확인 상태 조회
    3. 각 자격 증명의 태그 정보 조회
    """
    ses_client = session.client("ses", region_name=region)

    # 모든 자격 증명 목록 조회 (이메일 및 도메인)
    response = ses_client.list_identities()
    identities = response.get("Identities", [])

    if not identities:
        return {
            "Identities": [],
            "VerificationAttributes": {},
            "Tags": {},
        }

    # 확인 상태 조회
    verification_attributes = ses_client.get_identity_verification_attributes(
        Identities=identities
    ).get("VerificationAttributes", {})

    # 태그 정보 조회
    tags = {}
    for identity in identities:
        try:
            tag_response = ses_client.list_tags_for_resource(
                ResourceArn=f"arn:aws:ses:{region}:{session.client('sts').get_caller_identity().get('Account')}:identity/{identity}"
            )
            tags[identity] = tag_response.get("Tags", [])
        except Exception:
            tags[identity] = []

    return {
        "Identities": identities,
        "VerificationAttributes": verification_attributes,
        "Tags": tags,
    }


def get_filtered_data(raw_data: Dict[str, Any]) -> pd.DataFrame:
    """
    원본 JSON에서 주요 필드만 추출해 DataFrame으로 반환

    - Identity: 이메일 또는 도메인 주소
    - IdentityType: 자격 증명 유형 (Email 또는 Domain)
    - IdentityStatus: 확인 상태 (Success, Pending, Failed, NotStarted, TemporaryFailure)
    - Tags: 태그 정보
    """
    rows: List[Dict[str, Any]] = []
    identities = raw_data.get("Identities", [])
    verification_attrs = raw_data.get("VerificationAttributes", {})
    tags_data = raw_data.get("Tags", {})

    for identity in identities:
        verification_info = verification_attrs.get(identity, {})

        # 이메일 또는 도메인 유형 판별
        identity_type = "Email" if "@" in identity else "Domain"

        # 태그 정보 형식화
        tags = tags_data.get(identity, [])
        tags_str = (
            ", ".join([f"{tag.get('Key')}:{tag.get('Value')}" for tag in tags])
            if tags
            else "No tags"
        )

        row = {
            "Identity": identity,
            "IdentityType": identity_type,
            "IdentityStatus": verification_info.get("VerificationStatus", "Unknown"),
            "Tags": tags_str,
        }

        rows.append(row)

    return pd.DataFrame(rows)
