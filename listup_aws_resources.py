import os
import json
import pandas as pd
import boto3
from datetime import datetime, timezone, date
import argparse

from resources.ec2 import get_raw_data as ec2_raw, get_filtered_data as ec2_filtered
from resources.vpc import get_raw_data as vpc_raw, get_filtered_data as vpc_filtered
from resources.vpc_endpoint import get_raw_data as vpc_endpoint_raw, get_filtered_data as vpc_endpoint_filtered
from resources.rds import get_raw_data as rds_raw, get_filtered_data as rds_filtered
from resources.eks import get_raw_data as eks_raw, get_filtered_data as eks_filtered
from resources.subnets import get_raw_data as subnets_raw, get_filtered_data as subnets_filtered
from resources.s3_buckets import get_raw_data as s3_raw, get_filtered_data as s3_filtered
from resources.global_accelerator import get_raw_data as ga_raw, get_filtered_data as ga_filtered
from resources.dynamodb import get_raw_data as dynamodb_raw, get_filtered_data as dynamodb_filtered
from resources.elb import get_raw_data as elb_raw, get_filtered_data as elb_filtered
from resources.elasticache import get_raw_data as elasticache_raw, get_filtered_data as elasticache_filtered
from resources.ebs import get_raw_data as ebs_raw, get_filtered_data as ebs_filtered
from resources.ebs_snapshot import get_raw_data as ebs_snapshot_raw, get_filtered_data as ebs_snapshot_filtered
from resources.amis import get_raw_data as amis_raw, get_filtered_data as amis_filtered
from resources.nat_gateway import get_raw_data as nat_gateway_raw, get_filtered_data as nat_gateway_filtered
from resources.kinesis_streams import get_raw_data as kinesis_streams_raw, get_filtered_data as kinesis_streams_filtered
from resources.kinesis_firehose import get_raw_data as kinesis_firehose_raw, get_filtered_data as kinesis_firehose_filtered
from resources.glue_job import get_raw_data as glue_job_raw, get_filtered_data as glue_job_filtered
from resources.route53_hostedzone import get_raw_data as route53_raw, get_filtered_data as route53_filtered
from resources.secrets_manager import get_raw_data as secrets_raw, get_filtered_data as secrets_filtered
from resources.eip import get_raw_data as eip_raw, get_filtered_data as eip_filtered
from resources.internet_gateway import get_raw_data as internet_gateway_raw, get_filtered_data as internet_gateway_filtered
from resources.security_groups import get_raw_data as security_groups_raw, get_filtered_data as security_groups_filtered
from resources.ecr import get_raw_data as ecr_raw, get_filtered_data as ecr_filtered
from resources.security_group_rules import get_raw_data as security_group_rules_raw, get_filtered_data as security_group_rules_filtered
from resources.auto_scaling_groups import get_raw_data as auto_scaling_groups_raw, get_filtered_data as auto_scaling_groups_filtered


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

def main():
    """
    명령줄 인자로 전달된 리전 목록에 대해 AWS 리소스를 수집하여 JSON 및 Excel 파일로 저장합니다.
    글로벌 리소스(S3, Global Accelerator)는 별도 처리하며,
    각 리소스별로 추가 모듈(ElastiCache, EBS Snapshot, AMIs, NAT Gateway, VPC Endpoints)도 함께 조회합니다.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--region',
        dest='regions',
        nargs='+',
        default=['ap-northeast-2'],
        help='조회할 AWS 리전명 (여러 개 가능). 예: --region ap-northeast-2 us-west-2'
    )
    args = parser.parse_args()
    regions = args.regions

    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')

    current_dir = os.path.dirname(__file__)
    data_dir = os.path.join(current_dir, 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    all_raw_data = {}
    excel_path = os.path.join(data_dir, f'aws_resources_{timestamp}.xlsx')
    writer = pd.ExcelWriter(excel_path, engine='openpyxl')

    for region in regions:
        print(f"\n=== Collecting resources in region: {region} ===")
        session = boto3.Session(region_name=region)
        region_raw_data = {}

        # --- EC2 ---
        ec2_data_raw = ec2_raw(session, region)
        ec2_data_filtered = ec2_filtered(ec2_data_raw)
        region_raw_data['EC2'] = ec2_data_raw
        if not ec2_data_filtered.empty:
            sheet_name = f"EC2_{region}"[:31]
            ec2_data_filtered.to_excel(writer, sheet_name=sheet_name, index=False)

        # --- VPC ---
        vpc_data_raw = vpc_raw(session, region)
        vpc_data_filtered = vpc_filtered(vpc_data_raw)
        region_raw_data['VPC'] = vpc_data_raw
        if not vpc_data_filtered.empty:
            sheet_name = f"VPC_{region}"[:31]
            vpc_data_filtered.to_excel(writer, sheet_name=sheet_name, index=False)

        # --- RDS ---
        rds_data_raw = rds_raw(session, region)
        rds_data_filtered = rds_filtered(rds_data_raw)
        region_raw_data['RDS'] = rds_data_raw
        if not rds_data_filtered.empty:
            sheet_name = f"RDS_{region}"[:31]
            rds_data_filtered.to_excel(writer, sheet_name=sheet_name, index=False)

        # --- EKS ---
        eks_data_raw = eks_raw(session, region)
        eks_data_filtered = eks_filtered(eks_data_raw)
        region_raw_data['EKS'] = eks_data_raw
        if not eks_data_filtered.empty:
            sheet_name = f"EKS_{region}"[:31]
            eks_data_filtered.to_excel(writer, sheet_name=sheet_name, index=False)

        # --- Subnets ---
        subnets_data_raw = subnets_raw(session, region)
        subnets_data_filtered = subnets_filtered(subnets_data_raw)
        region_raw_data['Subnets'] = subnets_data_raw
        if not subnets_data_filtered.empty:
            sheet_name = f"Subnets_{region}"[:31]
            subnets_data_filtered.to_excel(writer, sheet_name=sheet_name, index=False)

        # --- DynamoDB ---
        dynamodb_data_raw = dynamodb_raw(session, region)
        dynamodb_data_filtered = dynamodb_filtered(dynamodb_data_raw)
        region_raw_data['DynamoDB'] = dynamodb_data_raw
        if not dynamodb_data_filtered.empty:
            sheet_name = f"DynamoDB_{region}"[:31]
            dynamodb_data_filtered.to_excel(writer, sheet_name=sheet_name, index=False)

        # --- ELB (Classic, ALB, NLB) ---
        elb_data_raw = elb_raw(session, region)
        elb_data_filtered = elb_filtered(elb_data_raw)
        region_raw_data['ELB'] = elb_data_raw
        if not elb_data_filtered.empty:
            sheet_name = f"ELB_{region}"[:31]
            elb_data_filtered.to_excel(writer, sheet_name=sheet_name, index=False)

        # --- ElastiCache ---
        elasticache_data_raw = elasticache_raw(session, region)
        elasticache_data_filtered = elasticache_filtered(elasticache_data_raw)
        region_raw_data['ElastiCache'] = elasticache_data_raw
        if not elasticache_data_filtered.empty:
            sheet_name = f"ElastiCache_{region}"[:31]
            elasticache_data_filtered.to_excel(writer, sheet_name=sheet_name, index=False)

        # --- EBS Volumes ---
        ebs_data_raw = ebs_raw(session, region)
        ebs_data_filtered = ebs_filtered(ebs_data_raw)
        region_raw_data['EBS_Volumes'] = ebs_data_raw
        if not ebs_data_filtered.empty:
            sheet_name = f"EBS_Volumes_{region}"[:31]
            ebs_data_filtered.to_excel(writer, sheet_name=sheet_name, index=False)
            
        # --- EBS Snapshot ---
        ebs_snapshot_data_raw = ebs_snapshot_raw(session, region)
        ebs_snapshot_data_filtered = ebs_snapshot_filtered(ebs_snapshot_data_raw)
        region_raw_data['EBS_Snapshot'] = ebs_snapshot_data_raw
        if not ebs_snapshot_data_filtered.empty:
            sheet_name = f"EBS_Snapshot_{region}"[:31]
            ebs_snapshot_data_filtered.to_excel(writer, sheet_name=sheet_name, index=False)

        # --- AMIs (Owner=self) ---
        amis_data_raw = amis_raw(session, region)
        amis_data_filtered = amis_filtered(amis_data_raw)
        region_raw_data['AMIs'] = amis_data_raw
        if not amis_data_filtered.empty:
            sheet_name = f"AMIs_{region}"[:31]
            amis_data_filtered.to_excel(writer, sheet_name=sheet_name, index=False)

        # --- NAT Gateway ---
        nat_gateway_data_raw = nat_gateway_raw(session, region)
        nat_gateway_data_filtered = nat_gateway_filtered(nat_gateway_data_raw)
        region_raw_data['NAT_Gateway'] = nat_gateway_data_raw
        if not nat_gateway_data_filtered.empty:
            sheet_name = f"NAT_{region}"[:31]
            nat_gateway_data_filtered.to_excel(writer, sheet_name=sheet_name, index=False)

        # --- VPC Endpoints ---
        vpc_endpoint_data_raw = vpc_endpoint_raw(session, region)
        vpc_endpoint_data_filtered = vpc_endpoint_filtered(vpc_endpoint_data_raw)
        region_raw_data['VPC_Endpoints'] = vpc_endpoint_data_raw
        if not vpc_endpoint_data_filtered.empty:
            sheet_name = f"VpcEP_{region}"[:31]
            vpc_endpoint_data_filtered.to_excel(writer, sheet_name=sheet_name, index=False)

        # --- Kinesis Data Streams ---
        kinesis_streams_data_raw = kinesis_streams_raw(session, region)
        kinesis_streams_data_filtered = kinesis_streams_filtered(kinesis_streams_data_raw)
        region_raw_data['KinesisStreams'] = kinesis_streams_data_raw
        if not kinesis_streams_data_filtered.empty:
            sheet_name = f"KinesisStreams_{region}"[:31]
            kinesis_streams_data_filtered.to_excel(writer, sheet_name=sheet_name, index=False)

        # --- Glue Job ---
        glue_job_data_raw = glue_job_raw(session, region)
        glue_job_data_filtered = glue_job_filtered(glue_job_data_raw)
        region_raw_data['GlueJob'] = glue_job_data_raw
        if not glue_job_data_filtered.empty:
            sheet_name = f"GlueJob_{region}"[:31]
            glue_job_data_filtered.to_excel(writer, sheet_name=sheet_name, index=False)

        # --- Kinesis Data Firehose ---
        kinesis_firehose_data_raw = kinesis_firehose_raw(session, region)
        kinesis_firehose_data_filtered = kinesis_firehose_filtered(kinesis_firehose_data_raw)
        region_raw_data['KinesisFirehose'] = kinesis_firehose_data_raw
        if not kinesis_firehose_data_filtered.empty:
            sheet_name = f"KinesisFirehose_{region}"[:31]
            kinesis_firehose_data_filtered.to_excel(writer, sheet_name=sheet_name, index=False)

        # --- Secrets Manager ---
        secrets_data_raw = secrets_raw(session, region)
        secrets_data_filtered = secrets_filtered(secrets_data_raw)
        region_raw_data['SecretsManager'] = secrets_data_raw
        if not secrets_data_filtered.empty:
            sheet_name = f"Secrets_{region}"[:31]
            secrets_data_filtered.to_excel(writer, sheet_name=sheet_name, index=False)

        # --- Elastic IP ---
        eip_data_raw = eip_raw(session, region)
        eip_data_filtered = eip_filtered(eip_data_raw)
        region_raw_data['EIP'] = eip_data_raw
        if not eip_data_filtered.empty:
            sheet_name = f"EIP_{region}"[:31]
            eip_data_filtered.to_excel(writer, sheet_name=sheet_name, index=False)

        # --- Internet Gateway ---
        internet_gateway_data_raw = internet_gateway_raw(session, region)
        internet_gateway_data_filtered = internet_gateway_filtered(internet_gateway_data_raw)
        region_raw_data['InternetGateway'] = internet_gateway_data_raw
        if not internet_gateway_data_filtered.empty:
            sheet_name = f"IGW_{region}"[:31]
            internet_gateway_data_filtered.to_excel(writer, sheet_name=sheet_name, index=False)

        # --- Security Groups ---
        security_groups_data_raw = security_groups_raw(session, region)
        security_groups_data_filtered = security_groups_filtered(security_groups_data_raw)
        region_raw_data['SecurityGroups'] = security_groups_data_raw
        if not security_groups_data_filtered.empty:
            sheet_name = f"SG_{region}"[:31]
            security_groups_data_filtered.to_excel(writer, sheet_name=sheet_name, index=False)

        # --- ECR ---
        ecr_data_raw = ecr_raw(session, region)
        ecr_data_filtered = ecr_filtered(ecr_data_raw)
        region_raw_data['ECR'] = ecr_data_raw
        if not ecr_data_filtered.empty:
            sheet_name = f"ECR_{region}"[:31]
            ecr_data_filtered.to_excel(writer, sheet_name=sheet_name, index=False)

        # --- Security Group Rules ---
        security_group_rules_data_raw = security_group_rules_raw(session, region)
        security_group_rules_data_filtered = security_group_rules_filtered(security_group_rules_data_raw)
        region_raw_data['SecurityGroupRules'] = security_group_rules_data_raw
        if not security_group_rules_data_filtered.empty:
            sheet_name = f"SGRules_{region}"[:31]
            security_group_rules_data_filtered.to_excel(writer, sheet_name=sheet_name, index=False)

        # --- Auto Scaling Groups ---
        auto_scaling_groups_data_raw = auto_scaling_groups_raw(session, region)
        auto_scaling_groups_data_filtered = auto_scaling_groups_filtered(auto_scaling_groups_data_raw)
        region_raw_data['AutoScalingGroups'] = auto_scaling_groups_data_raw
        if not auto_scaling_groups_data_filtered.empty:
            sheet_name = f"ASG_{region}"[:31]
            auto_scaling_groups_data_filtered.to_excel(writer, sheet_name=sheet_name, index=False)

        all_raw_data[region] = region_raw_data

    # --- S3 Buckets (Global) ---
    print("\n=== Collecting S3 Buckets (global) ===")
    s3_session = boto3.Session(region_name="us-east-1")
    s3_data_raw = s3_raw(s3_session)
    s3_data_filtered = s3_filtered(s3_data_raw)
    all_raw_data['S3'] = s3_data_raw
    if not s3_data_filtered.empty:
        s3_data_filtered.to_excel(writer, sheet_name='S3', index=False)

    # --- Global Accelerator (Global) ---
    print("\n=== Collecting Global Accelerators (global) ===")
    ga_session = boto3.Session(region_name='us-west-2')
    ga_data_raw = ga_raw(ga_session, 'us-west-2')
    ga_data_filtered = ga_filtered(ga_data_raw)
    all_raw_data['GlobalAccelerator'] = ga_data_raw
    if not ga_data_filtered.empty:
        ga_data_filtered.to_excel(writer, sheet_name='GlobalAccelerator', index=False)

    # --- Route53 HostedZone (global) ---
    print("\n=== Collecting Route53 HostedZones (global) ===")
    route53_session = boto3.Session()  # 글로벌 서비스
    route53_data_raw = route53_raw(route53_session, None)
    route53_data_filtered = route53_filtered(route53_data_raw)
    all_raw_data['Route53'] = route53_data_raw
    if not route53_data_filtered.empty:
        sheet_name = 'Route53'
        route53_data_filtered.to_excel(writer, sheet_name=sheet_name, index=False)

    writer.close()
    print(f"[Excel] {excel_path} 생성 완료")

    json_path = os.path.join(data_dir, f'aws_resources_raw_{timestamp}.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_raw_data, f, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
    print(f"[JSON] {json_path} 생성 완료")


if __name__ == '__main__':
    main()
