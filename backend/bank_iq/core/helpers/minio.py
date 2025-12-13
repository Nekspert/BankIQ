import logging

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError
from django.conf import settings

from bank_iq.models import PublicS3Boto3Storage


logger = logging.getLogger(__name__)


def get_s3_client():
    """
    Возвращает настроенный boto3 client, учитывая endpoint, region и addressing style.
    """
    aws_endpoint = getattr(settings, "AWS_S3_ENDPOINT_URL", None)
    aws_region = getattr(settings, "AWS_S3_REGION_NAME", None) or getattr(settings, "AWS_S3_REGION", None)
    addressing_style = getattr(settings, "AWS_S3_ADDRESSING_STYLE", None)
    signature_version = getattr(settings, "AWS_S3_SIGNATURE_VERSION", None)

    botocore_config = {}
    if addressing_style:
        botocore_config["s3"] = {"addressing_style": addressing_style}

    config = BotoConfig(signature_version=signature_version, **botocore_config) if botocore_config else BotoConfig(
            signature_version="s3v4")

    client = boto3.client(
            "s3",
            endpoint_url=aws_endpoint,
            aws_access_key_id=getattr(settings, "AWS_ACCESS_KEY_ID", None),
            aws_secret_access_key=getattr(settings, "AWS_SECRET_ACCESS_KEY", None),
            region_name=aws_region,
            config=config,
            verify=getattr(settings, "AWS_S3_VERIFY", True),
    )
    return client


import json


PUBLIC_READ_POLICY_TEMPLATE = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"AWS": ["*"]},
            "Action": ["s3:GetObject"],
            "Resource": []
        }
    ]
}


def ensure_bucket_policy_public(bucket_name: str) -> bool:
    client = get_s3_client()
    policy = PUBLIC_READ_POLICY_TEMPLATE.copy()
    policy["Statement"][0]["Resource"] = [f"arn:aws:s3:::{bucket_name}/*"]
    try:
        client.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(policy))
        logger.info("Applied public-read policy to bucket %s", bucket_name)
        return True
    except ClientError as e:
        logger.error("Failed to apply bucket policy for %s: %s", bucket_name, e, exc_info=True)
        return False


def ensure_bucket_exists(bucket_name: str) -> bool:
    """
    Проверяет наличие бакета и создаёт его при отсутствии.
    Возвращает True — если бакет существует (либо был успешно создан).
    """
    client = get_s3_client()
    aws_region = getattr(settings, "AWS_S3_REGION_NAME", None) or getattr(settings, "AWS_S3_REGION", None)

    try:
        client.head_bucket(Bucket=bucket_name)
        logger.info("Bucket exists: %s", bucket_name)
        ensure_bucket_policy_public(bucket_name)
        return True
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code", "")
        logger.info("Bucket head_bucket error code=%s for %s", code, bucket_name)
        # если бакета нет — попытаемся создать
        try:
            create_kwargs = {"Bucket": bucket_name}
            if aws_region and aws_region != "us-east-1":
                create_kwargs["CreateBucketConfiguration"] = {"LocationConstraint": aws_region}

            logger.info("Creating bucket %s with kwargs: %s", bucket_name, create_kwargs)
            client.create_bucket(**create_kwargs)
            # подождём/проверим
            client.head_bucket(Bucket=bucket_name)
            logger.info("Bucket created: %s", bucket_name)
            ensure_bucket_policy_public(bucket_name)
            return True
        except ClientError as ce:
            logger.error("Failed to create bucket %s: %s", bucket_name, ce, exc_info=True)
            return False
    except Exception as e:
        logger.error("Unexpected error while checking/creating bucket %s: %s", bucket_name, e, exc_info=True)
        return False


def get_s3_storage():
    """
    Создает и возвращает экземпляр S3Storage с явными настройками
    """
    storage = PublicS3Boto3Storage(
            bucket_name=settings.AWS_STORAGE_BUCKET_NAME,
            access_key=settings.AWS_ACCESS_KEY_ID,
            secret_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=getattr(settings, "AWS_S3_ENDPOINT_URL", None),
            querystring_auth=getattr(settings, "AWS_QUERYSTRING_AUTH", False),
            file_overwrite=getattr(settings, "AWS_S3_FILE_OVERWRITE", False),
            default_acl=getattr(settings, "AWS_DEFAULT_ACL", False),
            location='',
            addressing_style=getattr(settings, 'AWS_S3_ADDRESSING_STYLE', 'auto'))
    return storage
