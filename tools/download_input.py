from pathlib import Path
import hashlib
from tools.utils import list_obj_keys, get_s3_bits, save_image, save_file
from tools.config import s3_client, BDRC_ARCHIVE_BUCKET, images_bucket, ocr_bucket


def get_hash(work_id):
    md5 = hashlib.md5(str.encode(work_id))
    two = md5.hexdigest()[:2]
    return two

def download_images(work_id, image_output_path):
    two = get_hash(work_id)
    output_path = Path(f"{image_output_path}/{work_id}")
    output_path.mkdir(parents=True, exist_ok=True)
    prefix = f"Works/{two}/{work_id}"
    obj_keys = get_keys(work_id)
    # obj_keys = list_obj_keys(prefix=prefix, s3_client=s3_client, bucket_name=BDRC_ARCHIVE_BUCKET)
    for obj_key in obj_keys:
        parts = obj_key.split("/")
        if parts[3] == "images":
            filebits = get_s3_bits(obj_key, images_bucket)
            image_name = parts[-1]
            save_image(filebits, image_name, output_path)


def download_OCR(work_id, OCR_output_path):
    two = get_hash(work_id)
    output_path = Path(f"{OCR_output_path}/{work_id}")
    output_path.mkdir(parent=True, exist_ok=True)
    prefix = f"Works/{two}/{work_id}"
    obj_keys = list_obj_keys(prefix=prefix, s3_client=s3_client, bucket_name=BDRC_ARCHIVE_BUCKET)
    for obj_key in obj_keys:
        parts = obj_key.split("/")
        if parts[3] == "images-web":
            filebits = get_s3_bits(obj_key, ocr_bucket)
            filename = parts[-1]
            save_file(filebits, filename, output_path)

def get_keys(work_id):
    s3_keys = []
    two = get_hash(work_id)
    prefix = f"Works/{two}/{work_id}"
    obj_keys = list_obj_keys(prefix=prefix, s3_client=s3_client, bucket_name=BDRC_ARCHIVE_BUCKET)
    for obj_key in obj_keys:
        parts = obj_key.split("/")
        if parts[3] == "images":
            if parts[4] == "W1KG13126-I1KG13170":
                s3_keys.append(obj_key)
    return s3_keys



if __name__ == "__main__":
    work_id = "W1KG13126"
    image_output_path = Path("./data/source_images")
    OCR_output_path = Path(f"./data/ocr_output")
    download_images(work_id,image_output_path)
    download_OCR(work_id, OCR_output_path)
