import json
from pathlib import Path
from utils import get_hash, is_archived
from openpecha.buda.api import get_buda_scan_info, get_image_list
from config import BDRC_ARCHIVE_BUCKET as bucket_name, bdrc_archive_s3_client as s3_client


def create_s3_key(images_list, work_id, image_group_id):
    s3_keys = []
    hash_two = get_hash(work_id)

    if not (image_group_id[2].isalpha() or image_group_id[3].isalpha()):
        image_group_id = image_group_id[1:]

    for image in images_list:
        filename_part = image['filename'].split(".")[0][-3:]

        if filename_part.isdigit() and int(filename_part) > 5:
            s3_key = f"Works/{hash_two}/{work_id}/images/{work_id}-{image_group_id}/{image['filename']}"
            s3_keys.append(s3_key)

    return s3_keys


def get_images_from_references(json_file_path, work_id):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    image_references = []
    for entry in data:
        if entry["text_file"].split(".")[0] == work_id:
            image_references.extend(entry["references"])

    return image_references


def get_specific_images(work_id, s3_client, bucket_name, image_references):
    final_dict = {}
    curr_dict = {}
    scan_info = get_buda_scan_info(work_id)
    if scan_info is None:
        return None
    for image_group_id, _ in scan_info["image_groups"].items():
        images_s3_keys = []
        images_list = get_image_list(work_id, image_group_id)
        s3_keys = create_s3_key(images_list, work_id, image_group_id)

        for s3_key in s3_keys:
            image_name = s3_key.split("/")[-1]
            if image_name in image_references:
                try:
                    if is_archived(s3_key, s3_client, bucket_name):
                        images_s3_keys.append(s3_key)
                except Exception as e:
                    pass

        curr_dict[image_group_id] = images_s3_keys
        final_dict.update(curr_dict)
    return final_dict


def download_and_save_image(bucket_name, obj_dict, save_path):
    if obj_dict is None:
        return
    for _, obj_keys in obj_dict.items():
        for obj_key in obj_keys:
            image_name = obj_key.split("/")[-1]
            image_path = Path(f"{save_path}/{image_name}")
            if image_path.exists():
                continue
            try:
                response = s3_client.get_object(
                    Bucket=bucket_name, Key=obj_key)
                image_data = response['Body'].read()
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                print(f"Image downloaded and saved as {image_path}")
            except Exception as e:
                pass


def main():
    json_file_path = "span.json"
    work_ids = Path(
        "../data/work_ids/derge_works.txt").read_text(encoding='utf-8').split("\n")
    for work_id in work_ids:
        save_path = Path(f'../data/images/derge/required_images/{work_id}')
        save_path.mkdir(exist_ok=True, parents=True)
        image_references = get_images_from_references(json_file_path, work_id)
        if image_references:
            images_dict = get_specific_images(
                work_id, s3_client, bucket_name, image_references)
            if images_dict:
                print(f"Downloading images for work_id: {work_id}")
                download_and_save_image(bucket_name, images_dict, save_path)


if __name__ == "__main__":
    main()
