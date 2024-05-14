import os
import configparser
import boto3
from pathlib import Path
from tools.utils import get_hash, is_archived
from openpecha.buda.api import get_buda_scan_info, get_image_list
import re
from tools.config import BDRC_ARCHIVE_BUCKET as bucket_name, bdrc_archive_s3_client as s3_client

BDRC_ARCHIVE_BUCKET = "archive.tbrc.org"
OCR_OUTPUT_BUCKET = "ocr.bdrc.io"
aws_credentials_file = os.path.expanduser("~/.aws/credentials")
config = configparser.ConfigParser()
config.read(aws_credentials_file)


bdrc_archive_session = boto3.Session(
    aws_access_key_id= config.get("archive_tbrc_org", "aws_access_key_id"),
    aws_secret_access_key= config.get("archive_tbrc_org", "aws_secret_access_key")
)
bdrc_archive_s3_client = bdrc_archive_session.client('s3')
bdrc_archive_s3_resource = bdrc_archive_session.resource('s3')
bdrc_archive_bucket = bdrc_archive_s3_resource.Bucket(BDRC_ARCHIVE_BUCKET)
ocr_output_bucket = bdrc_archive_s3_resource.Bucket(OCR_OUTPUT_BUCKET)

bucket_name = BDRC_ARCHIVE_BUCKET
s3 = bdrc_archive_s3_client

def remove_non_page(images_list, work_id, image_group_id):
    s3_keys = []
    hash_two = get_hash(work_id)
    for image in images_list:
        if int(image['filename'].split(".")[-0][-3:]) <= 8:
            continue
        else:
            if re.search(r"[A-Z]", image_group_id[1:]) == None:
                image_group = image_group_id[1:]
            else:
                image_group = image_group_id
            s3_key = f"Works/{hash_two}/{work_id}/images/{work_id}-{image_group}/{image['filename']}"
            s3_keys.append(s3_key)
    return s3_keys


def get_random_images_dict(work_id, s3_client, bucket_name, random_flag=True):
    final_dict = {}
    curr_dict = {}
    scan_info = get_buda_scan_info(work_id)
    if scan_info == None:
        return None
    for image_group_id, _ in scan_info["image_groups"].items():
        images_s3_keys = []
        images_list = get_image_list(work_id, image_group_id)
        s3_keys = remove_non_page(images_list, work_id, image_group_id)
        for s3_key in s3_keys:
            if s3_key in images_s3_keys:
                continue
            if is_archived(s3_key, s3_client, bucket_name):
                images_s3_keys.append(s3_key)
        curr_dict[image_group_id] = images_s3_keys
        final_dict.update(curr_dict)
    return final_dict


def download_and_save_image(bucket_name, obj_dict, save_path):
    if obj_dict == None:
        return
    for _, obj_keys in obj_dict.items():
        for obj_key in obj_keys:
            image_name = obj_key.split("/")[-1]
            image_path = Path(f"{save_path}/{image_name}")
            if image_path.exists():
                continue
            try:
                response = s3.get_object(Bucket=bucket_name, Key=obj_key)
                image_data = response['Body'].read()
                
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                
                print(f"Image downloaded and saved as {save_path}")
            except Exception as e:
                print(f"Error: {e}")

def main():
    work_ids = Path(f"./F60000.txt").read_text(encoding='utf-8').split("\n")
    for work_id in work_ids[88:]:
        save_path = Path(f'./F60000/{work_id}')
        save_path.mkdir(exist_ok=True)
        images_dict = get_random_images_dict(work_id, s3_client, bucket_name, random_flag=False)
        download_and_save_image(bucket_name, images_dict, save_path)

if __name__ == "__main__":
    main()

