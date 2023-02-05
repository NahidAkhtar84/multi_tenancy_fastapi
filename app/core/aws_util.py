import boto3
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.log_config import logger

def the_bucket_list():
    print("key id: " + settings.AWS_ACCESS_KEY_ID)
    print("access key: " + settings.AWS_SECRET_ACCESS_KEY)
    s3 = boto3.resource("s3",
                        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    # Checking connection by printing out bucket names
    for bucket in s3.buckets.all():
        print(bucket.name)
    print("done")


def download():
    s3 = boto3.client("s3")
    s3.download_file(
        Bucket="vivasoft-ats",
        Key="APIs.txt",
        Filename="APIs.txt"
    )


def upload(key, path):
    s3 = boto3.client("s3",
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    s3.upload_file(
        Filename=path,
        Bucket=settings.AWS_BUCKET_NAME,
        Key=key,
    )


def boto3_client(resource: str = "s3"):
    return boto3.client(
        resource,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )


def verify_s3_url(s3_url):
    if f"s3://{settings.AWS_BUCKET_NAME}" in s3_url:
        try:
            s3 = boto3_client(resource="s3")
            key = s3_url.split(f"{settings.AWS_BUCKET_NAME}")[1].lstrip("/")
            s3.head_object(Bucket=settings.AWS_BUCKET_NAME, Key=key)
            return True, "success"
        except Exception:
            print("error while verifying s3 url")
            return False, "Unable to fetch file from provided url"
    return False, "Unsupported s3 url"


def read_file_from_s3(s3_url: str):
    if f"s3://{settings.AWS_BUCKET_NAME}" in s3_url:
        try:
            s3 = boto3_client(resource="s3")
            key = s3_url.split(f"{settings.AWS_BUCKET_NAME}")[1].lstrip("/")
            file_ = s3.get_object(Bucket=settings.AWS_BUCKET_NAME, Key=key)["Body"]
            return file_, key

        except Exception:
            print("error while read file from s3 bucket")


def aws_generate_presigned_url(file_key: str) -> str:
    file_key = file_key.split("/")[-1]
    s3_client = boto3.client(
        's3',
        region_name=settings.AWS_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
    try:
        url = s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': f'{settings.AWS_BUCKET_NAME}', 'Key': f'test/{file_key}'},
            ExpiresIn=3600,
        )
    except Exception as e:
        logger.error(f"{e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{e}",
        )
    return url

