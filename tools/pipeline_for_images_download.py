import os
import re
import configparser
import boto3
import random
from pathlib import Path
from utils import get_hash, is_archived
from openpecha.buda.api import get_buda_scan_info, get_image_list
from config import BDRC_ARCHIVE_BUCKET as bucket_name, bdrc_archive_s3_client as s3_client

def download_and_save_image(bucket_name, obj_dict, save_path):
    if obj_dict is None:
        return
    for image_group_id, obj_keys in obj_dict.items():
        for obj_key in obj_keys:
            image_name = obj_key.split("/")[-1]
            image_path = Path(f"{save_path}/{image_name}")
            if image_path.exists():
                print(f"Image already exists: {image_path}")
                continue
            try:
                print(f"Downloading image from {obj_key}")
                response = s3_client.get_object(Bucket=bucket_name, Key=obj_key)
                image_data = response['Body'].read()
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                print(f"Image downloaded and saved as {image_path}")
            except Exception as e:
                print(f"Error downloading {obj_key}: {e}")

def remove_non_page(images_list, work_id, image_group_id):
    s3_keys = []
    hash_two = get_hash(work_id)
    if not re.match(r"[A-Z]", image_group_id[1:]):
        image_group_id = image_group_id[1:]
    for image in images_list:
        if int(image['filename'].split(".")[-1][-3:]) <= 5:  # Corrected indexing for file extension
            continue
        else:
            s3_key = f"Works/{hash_two}/{work_id}/images/{work_id}-{image_group_id}/{image['filename']}"
            s3_keys.append(s3_key)
    return s3_keys

def get_random_images_dict(work_id, s3_client, bucket_name, random_flag=True):
    final_dict = {}
    scan_info = get_buda_scan_info(work_id)
    if scan_info is None:
        return None
    for image_group_id, _ in scan_info["image_groups"].items():
        images_list = get_image_list(work_id, image_group_id)
        s3_keys = remove_non_page(images_list, work_id, image_group_id)
        if random_flag:
            random_images = random.sample(s3_keys, min(len(s3_keys), 200))  
            images_s3_keys = [key for key in random_images if is_archived(key, s3_client, bucket_name)]
        else:
            images_s3_keys = [key for key in s3_keys if is_archived(key, s3_client, bucket_name)]
        final_dict[image_group_id] = images_s3_keys
    return final_dict

def main():
    work_ids = Path("../data/work_ids/derge_works.txt").read_text(encoding='utf-8').split("\n")
    for work_id in work_ids[88:]:
        print(f"Processing work ID: {work_id}")
        save_path = Path(f'../data/images/{work_id}')
        save_path.mkdir(exist_ok=True, parents=True)
        images_dict = get_random_images_dict(work_id, s3_client, bucket_name, random_flag=False)
        print(f"Images dictionary for work ID {work_id}: {images_dict}")
        download_and_save_image(bucket_name, images_dict, save_path)
        print(f"Download complete for work ID: {work_id}")

if __name__ == "__main__":
    main()
