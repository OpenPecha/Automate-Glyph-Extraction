import configparser
import os
import boto3

BDRC_ARCHIVE_BUCKET = "archive.tbrc.org"

aws_credentials_file = os.path.expanduser("~/.aws/credentials")

config = configparser.ConfigParser()
config.read(aws_credentials_file)


if "archive_tbrc_org" not in config:
    print("Error: 'archive_tbrc_org' section not found in AWS credentials file.")
    exit(1)

if "aws_access_key_id" not in config["archive_tbrc_org"]:
    print("Error: 'aws_access_key_id' not found in 'archive_tbrc_org' section.")
    exit(1)

if "aws_secret_access_key" not in config["archive_tbrc_org"]:
    print("Error: 'aws_secret_access_key' not found in 'archive_tbrc_org' section.")
    exit(1)

bdrc_archive_session = boto3.Session(
    aws_access_key_id=config["archive_tbrc_org"]["aws_access_key_id"],
    aws_secret_access_key=config["archive_tbrc_org"]["aws_secret_access_key"]
)

bdrc_archive_s3_client = bdrc_archive_session.client('s3')
bdrc_archive_s3_resource = bdrc_archive_session.resource('s3')

bdrc_archive_bucket = bdrc_archive_s3_resource.Bucket(BDRC_ARCHIVE_BUCKET)
ocr_output_bucket = bdrc_archive_s3_resource.Bucket("ocr.bdrc.io")
