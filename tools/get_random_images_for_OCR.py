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
<<<<<<< HEAD
        if int(image['filename'].split(".")[-0][-3:]) <= 8:
            continue
        else:
            if re.search(r"[A-Z]", image_group_id[1:]) == None:
                image_group = image_group_id[1:]
            else: 
                image_group = image_group_id
            s3_key = f"Works/{hash_two}/{work_id}/images/{work_id}-{image_group}/{image['filename']}"
=======
        if int(image['filename'].split(".")[-0][-3:]) <= 5:
            continue
        else:
            if re.search(r"[A-Z]", image_group_id[1:]) == False:
                image_group_id = image_group_id[1:]
            s3_key = f"Works/{hash_two}/{work_id}/images/{work_id}-{image_group_id}/{image['filename']}"
>>>>>>> 9bf9e1677c757451c5c299dc2ba340f516f80830
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
<<<<<<< HEAD
        for s3_key in s3_keys:
            if s3_key in images_s3_keys:
                continue
            if is_archived(s3_key, s3_client, bucket_name):
                images_s3_keys.append(s3_key)
        curr_dict[image_group_id] = images_s3_keys
        final_dict.update(curr_dict)
    return final_dict
=======
        if random_flag:
            random_images = list(random.sample(s3_keys, 200))
            for random_image in random_images:
                if random_image in images_s3_keys:
                    continue
                if is_archived(random_image, s3_client, bucket_name):
                    if len(images_s3_keys) == 150:
                        break
                    else:
                        images_s3_keys.append(random_image)
        else:
            for s3_key in s3_keys:
                if s3_key in images_s3_keys:
                    continue
                if is_archived(s3_key, s3_client, bucket_name):
                    images_s3_keys.append(s3_key)
        curr_dict[image_group_id] = images_s3_keys
        final_dict.update(curr_dict)
    return final_dict



if __name__ == "__main__":
    done_list = ["W7371","W30451", "W30183","W30450", "W30178", "W23957", "W23746"]
    # # work_ids = []
    # work_ids = ["W7371"]
    # for work_id in work_ids:
    #     images_dict = get_random_images_dict(work_id)
    #     dump_yaml(images_dict, Path(f"./shul/{work_id}_images.yml"))
>>>>>>> 9bf9e1677c757451c5c299dc2ba340f516f80830
