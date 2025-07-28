#!/usr/bin/env python3
"""
AWS Security Groups 전용 조회 스크립트

이 스크립트는 AWS Security Groups만을 조회하여 상세 정보를 제공합니다.
- 보안 그룹 기본 정보
- 인바운드/아웃바운드 규칙
- AnyOpen (0.0.0.0/0, ::/0) 규칙 감지
- Excel 및 JSON 형식으로 결과 저장
- 특정 리전 또는 모든 리전 조회 지원
"""

import argparse
import json
import os
from datetime import datetime
from typing import Any

import boto3
import pandas as pd
from botocore.exceptions import NoCredentialsError

from resources.security_groups import get_filtered_data, get_raw_data


def get_all_regions() -> list[str]:
    """
    사용 가능한 모든 AWS 리전을 조회합니다.

    Returns:
        List[str]: AWS 리전 목록
    """
    try:
        ec2 = boto3.client("ec2")
        response = ec2.describe_regions()
        return [region["RegionName"] for region in response["Regions"]]
    except Exception as e:
        print(f"Error getting regions: {e}")
        return ["us-east-1", "us-west-2", "ap-northeast-2"]  # 기본 리전


def collect_security_groups_data(
    regions: list[str] = None,
) -> tuple[list[dict[str, Any]], pd.DataFrame]:
    """
    지정된 리전들에서 Security Groups 데이터를 수집합니다.

    Args:
        regions: 조회할 리전 목록 (None이면 모든 리전)

    Returns:
        tuple: (원시 데이터, 필터링된 데이터프레임)
    """
    if regions is None:
        print("🌍 사용 가능한 모든 리전을 조회합니다...")
        regions = get_all_regions()
        print(f"📍 총 {len(regions)}개 리전을 발견했습니다.")

    all_raw_data = []
    all_filtered_data = []

    session = boto3.Session()

    print("\n🔍 Security Groups 조회 중...")
    print(f"📊 조회 대상 리전: {len(regions)}개")

    successful_regions = 0
    total_security_groups = 0

    for i, region in enumerate(regions, 1):
        print(f"  📍 [{i}/{len(regions)}] {region} 리전 조회 중...")

        try:
            # 원시 데이터 수집
            raw_data = get_raw_data(session, region)

            if raw_data:
                # 리전 정보 추가
                for item in raw_data:
                    item["Region"] = region

                all_raw_data.extend(raw_data)

                # 필터링된 데이터 생성
                filtered_df = get_filtered_data(raw_data)
                if not filtered_df.empty:
                    filtered_df["Region"] = region
                    all_filtered_data.append(filtered_df)

                # AnyOpen 규칙이 있는 Security Groups 수 계산
                any_open_count = len(
                    filtered_df[filtered_df["AnyOpenInbound"] == "⚠️ YES"]
                )
                any_open_text = (
                    f" (⚠️ {any_open_count}개 AnyOpen)" if any_open_count > 0 else ""
                )

                print(f"    ✅ {len(raw_data)}개 Security Groups 발견{any_open_text}")
                successful_regions += 1
                total_security_groups += len(raw_data)
            else:
                print("    ℹ️  Security Groups 없음")
                successful_regions += 1

        except Exception as e:
            print(f"    ❌ {region} 리전 조회 실패: {e}")

    # 결과 요약
    print("\n📈 조회 완료 요약:")
    print(f"  ✅ 성공한 리전: {successful_regions}/{len(regions)}")
    print(f"  🛡️  총 Security Groups: {total_security_groups}개")

    # 모든 필터링된 데이터 결합
    if all_filtered_data:
        combined_df = pd.concat(all_filtered_data, ignore_index=True)
        # 컬럼 순서 조정
        columns_order = [
            "Region",
            "SecurityGroupId",
            "SecurityGroupName",
            "VpcId",
            "Description",
            "AnyOpenInbound",
            "InboundRules",
            "OutboundRules",
            "Tags",
        ]
        combined_df = combined_df.reindex(columns=columns_order)
    else:
        combined_df = pd.DataFrame()

    return all_raw_data, combined_df


def save_results(
    raw_data: list[dict[str, Any]], filtered_df: pd.DataFrame, output_dir: str = "data"
):
    """
    결과를 Excel 및 JSON 파일로 저장합니다.

    Args:
        raw_data: 원시 데이터
        filtered_df: 필터링된 데이터프레임
        output_dir: 출력 디렉토리
    """
    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)

    # 타임스탬프 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 파일명 생성
    excel_file = os.path.join(output_dir, f"security_groups_{timestamp}.xlsx")
    raw_json_file = os.path.join(output_dir, f"security_groups_raw_{timestamp}.json")
    filtered_json_file = os.path.join(
        output_dir, f"security_groups_filtered_{timestamp}.json"
    )

    print("\n💾 결과 파일 저장 중...")

    try:
        # Excel 파일 저장
        if not filtered_df.empty:
            with pd.ExcelWriter(excel_file, engine="openpyxl") as writer:
                filtered_df.to_excel(writer, sheet_name="Security Groups", index=False)
            print(f"  📊 Excel 파일 저장 완료: {excel_file}")
        else:
            print("  ℹ️  데이터가 없어 Excel 파일을 생성하지 않습니다.")

        # 원시 JSON 파일 저장
        with open(raw_json_file, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, indent=2, ensure_ascii=False, default=str)
        print(f"  📄 원시 JSON 파일 저장 완료: {raw_json_file}")

        # 필터링된 JSON 파일 저장
        if not filtered_df.empty:
            filtered_json = filtered_df.to_dict("records")
            with open(filtered_json_file, "w", encoding="utf-8") as f:
                json.dump(filtered_json, f, indent=2, ensure_ascii=False, default=str)
            print(f"  📄 필터링된 JSON 파일 저장 완료: {filtered_json_file}")
        else:
            print("  ℹ️  데이터가 없어 필터링된 JSON 파일을 생성하지 않습니다.")

        # 파일 크기 정보
        if os.path.exists(excel_file):
            excel_size = os.path.getsize(excel_file) / 1024  # KB
            print(f"  📏 Excel 파일 크기: {excel_size:.1f} KB")

        raw_json_size = os.path.getsize(raw_json_file) / 1024  # KB
        print(f"  📏 원시 JSON 파일 크기: {raw_json_size:.1f} KB")

    except Exception as e:
        print(f"  ❌ 파일 저장 중 오류 발생: {e}")
        raise


def print_summary(filtered_df: pd.DataFrame):
    """
    Security Groups 조회 결과 요약을 출력합니다.

    Args:
        filtered_df: 필터링된 데이터프레임
    """
    if filtered_df.empty:
        print("\n📋 조회 결과: Security Groups가 없습니다.")
        return

    total_count = len(filtered_df)
    any_open_count = len(filtered_df[filtered_df["AnyOpenInbound"] == "⚠️ YES"])
    regions = filtered_df["Region"].nunique()

    print("\n📋 Security Groups 조회 결과 요약:")
    print(f"  🌍 조회된 리전 수: {regions}")
    print(f"  🛡️  총 Security Groups 수: {total_count}")
    print(f"  ⚠️  AnyOpen 인바운드 규칙이 있는 Security Groups: {any_open_count}")

    if any_open_count > 0:
        print("\n⚠️  보안 주의가 필요한 Security Groups:")
        any_open_sgs = filtered_df[filtered_df["AnyOpenInbound"] == "⚠️ YES"]
        for _, sg in any_open_sgs.iterrows():
            print(
                f"    - {sg['SecurityGroupId']} ({sg['SecurityGroupName']}) in {sg['Region']}"
            )

    # 리전별 통계
    print("\n📊 리전별 Security Groups 수:")
    region_counts = filtered_df["Region"].value_counts()
    for region, count in region_counts.items():
        print(f"    {region}: {count}")


def main():
    """메인 함수"""
    # 명령줄 인자 파싱
    parser = argparse.ArgumentParser(
        description="AWS Security Groups 조회 스크립트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python listup_security_groups.py                           # 모든 리전 조회
  python listup_security_groups.py --region ap-northeast-2   # 특정 리전 조회
  python listup_security_groups.py --region us-east-1 us-west-2  # 여러 리전 조회
        """,
    )
    parser.add_argument(
        "--region",
        dest="regions",
        nargs="*",
        help="조회할 AWS 리전명 (여러 개 가능). 지정하지 않으면 모든 리전을 조회합니다.",
    )

    args = parser.parse_args()
    regions = args.regions if args.regions else None

    print("🚀 AWS Security Groups 조회 스크립트 시작")
    print("=" * 50)

    if regions:
        print(f"🎯 지정된 리전: {', '.join(regions)}")
    else:
        print("🌍 모든 리전을 조회합니다.")
    print()

    try:
        # AWS 자격증명 확인
        session = boto3.Session()
        sts = session.client("sts")
        identity = sts.get_caller_identity()
        print(f"🔐 AWS 계정: {identity.get('Account', 'Unknown')}")
        print(f"👤 사용자: {identity.get('Arn', 'Unknown')}")
        print()

    except NoCredentialsError:
        print("❌ AWS 자격증명이 설정되지 않았습니다.")
        print("다음 중 하나의 방법으로 자격증명을 설정하세요:")
        print("  1. AWS CLI: aws configure")
        print("  2. 환경변수: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
        print("  3. IAM 역할 (EC2에서 실행 시)")
        return

    except Exception as e:
        print(f"❌ AWS 자격증명 확인 중 오류: {e}")
        return

    try:
        # Security Groups 데이터 수집
        raw_data, filtered_df = collect_security_groups_data(regions)

        # 결과 저장
        save_results(raw_data, filtered_df)

        # 요약 출력
        print_summary(filtered_df)

        print("\n✅ Security Groups 조회 완료!")

    except KeyboardInterrupt:
        print("\n⏹️  사용자에 의해 중단되었습니다.")

    except Exception as e:
        print(f"\n❌ 예상치 못한 오류가 발생했습니다: {e}")


if __name__ == "__main__":
    main()
