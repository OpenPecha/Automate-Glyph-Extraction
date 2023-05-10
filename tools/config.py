import configparser
import os
import boto3

BDRC_ARCHIVE_BUCKET = "archive.tbrc.org"
OCR_OUTPUT_BUCKET = "ocr.bdrc.io"

aws_credentials_file = os.path.expanduser("~/.aws/credentials")
config = configparser.ConfigParser()
config.read(aws_credentials_file)


s3_session = boto3.Session(
    aws_access_key_id= config.get("archive_tbrc_org", "aws_access_key_id"),
    aws_secret_access_key= config.get("archive_tbrc_org", "aws_secret_access_key")
)
s3_client = s3_session.client('s3')
s3_resource = s3_session.resource('s3')
images_bucket = s3_resource.Bucket(BDRC_ARCHIVE_BUCKET)
ocr_bucket = s3_resource.Bucket(OCR_OUTPUT_BUCKET)