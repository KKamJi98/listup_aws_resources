from typing import Any, Dict, List

import pandas as pd

from utils.datetime_format import format_datetime


def get_raw_data(session: Any, region: str) -> Dict[str, Any]:
    """
    SES Identity 전체 목록 및 상세 정보를 조회하여 반환

    1. list_identities로 이메일 자격 증명 목록 조회
    2. get_identity_verification_attributes로 각 자격 증명의 확인 상태 조회
    3. get_identity_dkim_attributes로 DKIM 상태 조회
    4. get_identity_notification_attributes로 알림 설정 조회
    """
    ses_client = session.client("ses", region_name=region)

    # 이메일 자격 증명 목록 조회
    response = ses_client.list_identities(IdentityType="EmailAddress")
    identities = response.get("Identities", [])

    if not identities:
        return {
            "Identities": [],
            "VerificationAttributes": {},
            "DkimAttributes": {},
            "NotificationAttributes": {},
        }

    # 확인 상태 조회
    verification_attributes = ses_client.get_identity_verification_attributes(
        Identities=identities
    ).get("VerificationAttributes", {})

    # DKIM 상태 조회
    dkim_attributes = ses_client.get_identity_dkim_attributes(
        Identities=identities
    ).get("DkimAttributes", {})

    # 알림 설정 조회
    notification_attributes = ses_client.get_identity_notification_attributes(
        Identities=identities
    ).get("NotificationAttributes", {})

    return {
        "Identities": identities,
        "VerificationAttributes": verification_attributes,
        "DkimAttributes": dkim_attributes,
        "NotificationAttributes": notification_attributes,
    }


def get_filtered_data(raw_data: Dict[str, Any]) -> pd.DataFrame:
    """
    원본 JSON에서 주요 필드만 추출해 DataFrame으로 반환

    - Identity: 이메일 주소
    - VerificationStatus: 확인 상태 (Success, Pending, Failed, NotStarted, TemporaryFailure)
    - DkimEnabled: DKIM 활성화 여부
    - DkimVerificationStatus: DKIM 확인 상태
    - BounceNotifications: 반송 알림 주제
    - ComplaintNotifications: 수신 거부 알림 주제
    - DeliveryNotifications: 전송 알림 주제
    - CreatedDate: 생성 날짜 (확인 시작 날짜)
    """
    rows: List[Dict[str, Any]] = []
    identities = raw_data.get("Identities", [])
    verification_attrs = raw_data.get("VerificationAttributes", {})
    dkim_attrs = raw_data.get("DkimAttributes", {})
    notification_attrs = raw_data.get("NotificationAttributes", {})

    for identity in identities:
        verification_info = verification_attrs.get(identity, {})
        dkim_info = dkim_attrs.get(identity, {})
        notification_info = notification_attrs.get(identity, {})

        row = {
            "Identity": identity,
            "VerificationStatus": verification_info.get(
                "VerificationStatus", "Unknown"
            ),
            "DkimEnabled": "Yes" if dkim_info.get("DkimEnabled", False) else "No",
            "DkimVerificationStatus": dkim_info.get(
                "DkimVerificationStatus", "NotStarted"
            ),
            "BounceNotifications": notification_info.get(
                "BounceTopic", "Not configured"
            ),
            "ComplaintNotifications": notification_info.get(
                "ComplaintTopic", "Not configured"
            ),
            "DeliveryNotifications": notification_info.get(
                "DeliveryTopic", "Not configured"
            ),
            "CreatedDate": format_datetime(
                verification_info.get("VerificationStartDate", "Unknown")
            ),
        }

        rows.append(row)

    return pd.DataFrame(rows)
