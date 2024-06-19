import csv
import os
import boto3

MONLAM_AI_OCR_BUCKET = "monlam.ai.ocr"

aws_credentials_file = os.path.join(os.getenv('USERPROFILE'), '.aws', 'credential', 'tenkal_accessKeys.csv')

with open(aws_credentials_file, 'r', encoding='utf-8-sig') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        aws_access_key_id = row.get('Access key ID')
        aws_secret_access_key = row.get('Secret access key')
        if aws_access_key_id and aws_secret_access_key:
            break

monlam_ai_ocr_session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)
monlam_ai_ocr_s3_client = monlam_ai_ocr_session.client('s3')
monlam_ai_ocr_s3_resource = monlam_ai_ocr_session.resource('s3')
monlam_ai_ocr_bucket = monlam_ai_ocr_s3_resource.Bucket(MONLAM_AI_OCR_BUCKET)
