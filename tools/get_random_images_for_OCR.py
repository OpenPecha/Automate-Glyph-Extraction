import random
from pathlib import Path
from tools.utils import get_hash, is_archived
from openpecha.utils import dump_yaml, load_yaml
from openpecha.buda.api import get_buda_scan_info, get_image_list
import re

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
