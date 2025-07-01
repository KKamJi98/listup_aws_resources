# listup_aws_resources

AWS 리소스를 나열하고 정리하는 스크립트입니다. 특정 AWS 계정에서 자주 사용하는 리소스의 상태를 조회하여 엑셀 및 JSON 형태로 데이터를 내보냅니다.

추가하고 싶은 AWS 리소스가 있다면, `resources` 폴더에 새로운 리소스를 정의할 수 있습니다. (PR 환영합니다!)

## 기능

- 다양한 AWS 리소스(EKS, EC2, S3, RDS, DynamoDB, Route53, EIP, Internet Gateway, Security Group 등)를 손쉽게 조회할 수 있습니다.
- 조회된 결과는 Excel 및 JSON 형식으로 저장됩니다.
- Security Group 리소스에서 0.0.0.0/0 AnyOpen된 Inbound Rule을 가진 항목은 '⚠️ YES'로 표시됩니다.

## 프로젝트 구조

```shell
listup_aws_resources/
├── data/
│   ├── aws_resources_{timestamp}.xlsx
│   └── aws_resources_raw_{timestamp}.json
├── resources/
│   ├── amis.py
│   ├── dynamodb.py
│   ├── ebs.py
│   ├── ebs_snapshot.py
│   ├── ec2.py
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
│   ├── subnets.py
│   ├── vpc.py
│   └── vpc_endpoint.py
├── listup_aws_resources.py
├── pyproject.toml
├── poetry.lock
└── README.md
```

## 설치 및 실행 방법

1. 저장소를 클론합니다.

```bash
git clone https://github.com/KKamJi98/listup_aws_resources.git
cd listup_aws_resources
```

2. 가상 환경을 생성하고 활성화합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. 의존성을 설치합니다.

```bash
pip install uv
uv pip install -r requirements.txt
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

## 결과물

- 조회된 리소스 목록은 `data` 폴더 내에 Excel 및 JSON 형식으로 저장됩니다.

JSON -> 원본
Excel -> 가공된 데이터


## TODO

- [ ] 공통되게 사용되는 DateTime 포맷을 (%Y-%m-%d)로 수정하는 코드를 함수화
