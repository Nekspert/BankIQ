import logging

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


logger = logging.getLogger(__name__)


def get_s3_client():
    """
    Возвращает настроенный boto3 client, учитывая endpoint, region и addressing style.
    """
    aws_endpoint = getattr(settings, "AWS_S3_ENDPOINT_URL", None)
    aws_region = getattr(settings, "AWS_S3_REGION_NAME", None) or getattr(settings, "AWS_S3_REGION", None)
    addressing_style = getattr(settings, "AWS_S3_ADDRESSING_STYLE", None)

    botocore_config = {}
    if addressing_style:
        botocore_config["s3"] = {"addressing_style": addressing_style}

    config = BotoConfig(signature_version="s3v4", **botocore_config) if botocore_config else BotoConfig(
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
    return S3Boto3Storage(
            bucket_name=settings.AWS_STORAGE_BUCKET_NAME,
            access_key=settings.AWS_ACCESS_KEY_ID,
            secret_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=getattr(settings, "AWS_S3_ENDPOINT_URL", None),
            querystring_auth=getattr(settings, "AWS_QUERYSTRING_AUTH", False),
            file_overwrite=False,
            location='',
            addressing_style=getattr(settings, 'AWS_S3_ADDRESSING_STYLE', 'auto'))
