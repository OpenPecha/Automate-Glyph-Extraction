import hashlib
import json
import boto3
from pathlib import Path


def get_hash(work_id):
    md5 = hashlib.md5(str.encode(work_id))
    two = md5.hexdigest()[:2]
    return two


def download_images_from_s3(work_id, json_file, bucket_name, download_dir):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    s3 = boto3.client('s3')
    hash_two = get_hash(work_id)
    for entry in data:
        image_group_id = entry['image_group_id']

        if not (image_group_id[2].isalpha() or image_group_id[3].isalpha()):
            image_group_id = image_group_id[1:]

        for image_filename in entry['references']:
            s3_key = f"Works/{hash_two}/{work_id}/images/{work_id}-{image_group_id}/{image_filename}"
            try:
                download_path = Path(download_dir) / \
                    f"{work_id}" / image_filename
                download_path.parent.mkdir(parents=True, exist_ok=True)
                s3.download_file(bucket_name, s3_key, str(download_path))
                print(f"Downloaded {s3_key} to {download_path}")
            except Exception as e:
                print(f"Failed to download {s3_key}: {e}")


def main():
    work_id = "W22084"
    json_file = "span.json"
    bucket_name = "archive.tbrc.org"
    download_dir = "../data/required_images/derge"
    download_images_from_s3(work_id, json_file, bucket_name, download_dir)


if __name__ == "__main__":
    main()
