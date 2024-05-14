from tools.download_images_for_glyph import download_and_save_image, get_random_images_dict
from pathlib import Path
from tools.config import BDRC_ARCHIVE_BUCKET as bucket_name, bdrc_archive_s3_client as s3_client


def main():
    work_ids = Path(f"./data/F60000.txt").read_text(encoding='utf-8').split("\n")
    for work_id in work_ids[88:]:
        save_path = Path(f'./F60000/{work_id}')
        save_path.mkdir(exist_ok=True, parents=True)
        images_dict = get_random_images_dict(work_id, s3_client, bucket_name, random_flag=False)
        download_and_save_image(bucket_name, images_dict, save_path)

if __name__ == "__main__":
    main()
