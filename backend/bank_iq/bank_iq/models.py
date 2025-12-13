from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class PublicS3Boto3Storage(S3Boto3Storage):
    def url(self, name, *args, **kwargs):
        public_endpoint = settings.MINIO_PUBLIC_ENDPOINT.rstrip('/')
        return f"{public_endpoint}/{self.bucket_name}/{name}"
