import configparser
import os
import boto3

MONLAM_AI_OCR_BUCKET = "monlam.ai.ocr"

aws_credentials_file = os.path.expanduser("~/.aws/credentials")

config = configparser.ConfigParser()
config.read(aws_credentials_file)



monlam_ai_ocr_session = boto3.Session(
    aws_access_key_id= config.get("monlam_ai_ocr", "aws_access_key_id"),
    aws_secret_access_key= config.get("monlam_ai_ocr", "aws_secret_access_key")
)
monlam_ai_ocr_s3_client = monlam_ai_ocr_session .client('s3')
monlam_ai_ocr_s3_resource = monlam_ai_ocr_session .resource('s3')
monlam_ai_ocr_bucket = monlam_ai_ocr_s3_resource.Bucket(MONLAM_AI_OCR_BUCKET)
