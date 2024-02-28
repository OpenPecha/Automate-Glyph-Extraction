import configparser
import os
import boto3

PAGE_CROPPING_BUCKET = "image-processing.bdrc.io"
BDRC_ARCHIVE_BUCKET = "archive.tbrc.org"
OCR_OUTPUT_BUCKET = "ocr.bdrc.io"
LAYOUT_ANALYSIS_BUCKET = "image-processing.openpecha"
MONLAM_AI_OCR_BUCKET = "monlam.ai.ocr"

aws_credentials_file = os.path.expanduser("~/.aws/credentials")
config = configparser.ConfigParser()
config.read(aws_credentials_file)


page_cropping_session = boto3.Session(
    aws_access_key_id= config.get("image_processing_bdrc_io", "aws_access_key_id"),
    aws_secret_access_key= config.get("image_processing_bdrc_io", "aws_secret_access_key")
)
page_cropping_s3_client = page_cropping_session.client('s3')
page_cropping_s3_resource = page_cropping_session.resource('s3')
page_cropping_bucket = page_cropping_s3_resource.Bucket(PAGE_CROPPING_BUCKET)


bdrc_archive_session = boto3.Session(
    aws_access_key_id= config.get("archive_tbrc_org", "aws_access_key_id"),
    aws_secret_access_key= config.get("archive_tbrc_org", "aws_secret_access_key")
)
bdrc_archive_s3_client = bdrc_archive_session.client('s3')
bdrc_archive_s3_resource = bdrc_archive_session.resource('s3')
bdrc_archive_bucket = bdrc_archive_s3_resource.Bucket(BDRC_ARCHIVE_BUCKET)
ocr_output_bucket = bdrc_archive_s3_resource.Bucket(OCR_OUTPUT_BUCKET)

layout_analysis_session = boto3.Session(
    aws_access_key_id= config.get("image_processing_openpecha", "aws_access_key_id"),
    aws_secret_access_key= config.get("image_processing_openpecha", "aws_secret_access_key")
)
layout_analysis_s3_client = layout_analysis_session .client('s3')
layout_analysis_s3_resource = layout_analysis_session .resource('s3')
layout_analysis_bucket = layout_analysis_s3_resource.Bucket(LAYOUT_ANALYSIS_BUCKET)



monlam_ai_ocr_session = boto3.Session(
    aws_access_key_id= config.get("monlam_ai_ocr", "aws_access_key_id"),
    aws_secret_access_key= config.get("monlam_ai_ocr", "aws_secret_access_key")
)
monlam_ai_ocr_s3_client = monlam_ai_ocr_session .client('s3')
monlam_ai_ocr_s3_resource = monlam_ai_ocr_session .resource('s3')
monlam_ai_ocr_bucket = monlam_ai_ocr_s3_resource.Bucket(MONLAM_AI_OCR_BUCKET)

