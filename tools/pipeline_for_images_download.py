from tools.get_random_images_for_OCR import get_random_images_dict
from tools.download_images_for_glyph import download_and_save_image
from pathlib import Path
from tools.config import BDRC_ARCHIVE_BUCKET as bucket_name, bdrc_archive_s3_client as s3_client


# ["W7371","W30451", "W30183","W30450", "W30178", "W23957", "W23746","W8LS73589" ]

def main():
    work_ids = ["W1KG13105"]
    for work_id in work_ids:
        save_path = Path(f'./{work_id}')
        save_path.mkdir(exist_ok=True)
        images_dict = get_random_images_dict(work_id, s3_client, bucket_name, random_flag=False)
        download_and_save_image(bucket_name, images_dict, save_path)

if __name__ == "__main__":
    main()