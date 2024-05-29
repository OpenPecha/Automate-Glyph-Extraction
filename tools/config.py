import configparser
import os
import boto3

BDRC_ARCHIVE_BUCKET = "archive.tbrc.org"

aws_credentials_file = os.path.expanduser("~/.aws/credentials")
config = configparser.ConfigParser()
config.read(aws_credentials_file)

bdrc_archive_session = boto3.Session(
    aws_access_key_id=config.get("archive_tbrc_org", "aws_access_key_id"),
    aws_secret_access_key=config.get("archive_tbrc_org", "aws_secret_access_key")
)
bdrc_archive_s3_client = bdrc_archive_session.client('s3')
bdrc_archive_s3_resource = bdrc_archive_session.resource('s3')
bdrc_archive_bucket = bdrc_archive_s3_resource.Bucket(BDRC_ARCHIVE_BUCKET)
ocr_output_bucket = bdrc_archive_s3_resource.Bucket("ocr.bdrc.io")
