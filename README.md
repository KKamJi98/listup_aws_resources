# listup_aws_resources

AWS 리소스를 나열하고 정리하는 스크립트입니다. 특정 AWS 계정에서 자주 사용하는 리소스의 상태를 조회하여 엑셀 및 JSON 형태로 데이터를 내보냅니다.

추가하고 싶은 AWS 리소스가 있다면, `resources` 폴더에 새로운 리소스를 정의할 수 있습니다. (PR 환영합니다!)

## 기능

- 다양한 AWS 리소스(EKS, EC2, S3, RDS, DynamoDB, Route53, EIP, Internet Gateway, Security Group 등)를 손쉽게 조회할 수 있습니다.
- 조회된 결과는 Excel 및 JSON 형식으로 저장됩니다.
- Security Group 리소스에서 0.0.0.0/0 또는 ::/0 AnyOpen된 Inbound Rule을 가진 항목은 '⚠️ YES'로 표시됩니다.
- IPv6 범위, Prefix List ID, 보안 그룹 참조 등 모든 유형의 보안 그룹 규칙을 완전히 지원합니다.
- SES Identity 리소스에서 이메일 자격 증명의 확인 상태, DKIM 상태, 알림 설정 등을 확인할 수 있습니다.
- 강력한 에러 처리와 타입 힌트로 안정성과 가독성을 보장합니다.

## 프로젝트 구조

```shell
listup_aws_resources/
├── data/
│   ├── aws_resources_{timestamp}.xlsx
│   ├── aws_resources_raw_{timestamp}.json
│   └── aws_resources_filtered_{timestamp}.json
├── resources/
│   ├── amis.py
│   ├── auto_scaling_groups.py
│   ├── dynamodb.py
│   ├── ebs.py
│   ├── ebs_snapshot.py
│   ├── ec2.py
│   ├── ecr.py
│   ├── eip.py
│   ├── eks.py
│   ├── elasticache.py
│   ├── elb.py
│   ├── glue_job.py
│   ├── global_accelerator.py
│   ├── internet_gateway.py
│   ├── kinesis_firehose.py
│   ├── kinesis_streams.py
│   ├── nat_gateway.py
│   ├── rds.py
│   ├── route53_hostedzone.py
│   ├── s3_buckets.py
│   ├── secrets_manager.py
│   ├── security_groups.py
│   ├── ses_identity.py
│   ├── subnets.py
│   ├── vpc.py
│   └── vpc_endpoint.py
├── tests/
│   ├── test_datetime_format.py
│   ├── test_ec2.py
│   ├── test_listup_aws_resources.py
│   ├── test_s3_buckets.py
│   ├── test_security_groups.py
│   └── test_ses_identity.py
├── utils/
│   ├── datetime_format.py
│   └── name_tag.py
├── listup_aws_resources.py
├── pyproject.toml
├── uv.lock
└── README.md
```

## 설치 및 실행 방법

1. 저장소를 클론합니다.

```bash
git clone https://github.com/KKamJi98/listup_aws_resources.git
cd listup_aws_resources
```

2. `uv` 가상 환경을 생성하고 활성화합니다.

```bash
uv venv
source .venv/bin/activate
```

3. 의존성을 설치합니다.

```bash
uv sync
```

4. AWS 자격증명(credential)을 환경에 설정합니다.

```bash
export AWS_ACCESS_KEY_ID=<your_access_key>
export AWS_SECRET_ACCESS_KEY=<your_secret_key>
export AWS_DEFAULT_REGION=<your_region>
```

5. 프로그램을 실행합니다.

```bash
python listup_aws_resources.py
```

## 개발 및 테스트

### 테스트 실행

```bash
# 모든 테스트 실행
uv run pytest -v

# 특정 모듈 테스트
uv run pytest tests/test_security_groups.py -v
```

### 코드 품질 검사

```bash
# 코드 포맷팅 검사
uv run black --check .

# Import 정렬 검사
uv run isort --check-only .

# 코드 포맷팅 적용
uv run black .
uv run isort .
```

### 모든 검사 실행

```bash
# 테스트, 포맷팅, Import 정렬을 모두 확인
uv run pytest -v && uv run isort --check-only . && uv run black --check .
```

## 결과물

- 조회된 리소스 목록은 `data` 폴더 내에 Excel 및 JSON 형식으로 저장됩니다.
- **Excel 파일**: 가공된 데이터 (읽기 쉬운 형태로 변환)
- **Raw JSON 파일**: AWS API에서 받은 원본 데이터 그대로
- **Filtered JSON 파일**: 가공되고 필터링된 데이터 (Excel과 동일한 내용)

## 주요 개선사항

### Security Groups 모듈
- IPv4 (0.0.0.0/0) 및 IPv6 (::/0) AnyOpen 규칙 감지
- IPv6 범위, Prefix List ID, 보안 그룹 참조 완전 지원
- 향상된 에러 처리 및 타입 힌트
- 포괄적인 테스트 커버리지

### 공통 개선사항
- 모든 모듈에 타입 힌트 추가
- 강화된 에러 처리 (ClientError 및 일반 예외)
- 표준화된 datetime 포맷팅 유틸리티 사용
- 포괄적인 단위 테스트 작성

## TODO

- [x] 공통되게 사용되는 DateTime Format을 (%Y-%m-%d)로 수정하는 코드를 함수화
- [x] Security Groups에서 IPv6 및 Prefix List 지원 추가
- [x] 모든 모듈에 타입 힌트 및 에러 처리 개선
- [x] 포괄적인 테스트 커버리지 구현

## 기여

이슈를 생성하거나 PR을 보내 기여할 수 있습니다. 모든 PR은 다음 조건을 만족해야 합니다:

- `pytest`, `isort`, `black` 모든 검사 통과
- 새로운 기능에 대한 테스트 포함
- 타입 힌트 및 적절한 에러 처리 포함

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 버전

현재 버전은 1.2.0입니다.

## 작성자

- 이메일: rlaxowl5460@gmail.com
- GitHub: [KKamJi98](https://github.com/KKamJi98)
