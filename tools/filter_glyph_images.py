from pathlib import Path
import subprocess
from tools.config import MONLAM_AI_OCR_BUCKET, monlam_ai_ocr_s3_client

s3 = monlam_ai_ocr_s3_client
bucket_name = MONLAM_AI_OCR_BUCKET


def filter_images(glyph_images_list, uploaded_glyphs, done_glyphs):
    images_in_uploaded = []
    for image_key in uploaded_glyphs:
        image_dir = image_key.split("/")[-2]
        if image_dir not in done_glyphs:
            image_name = image_key.split("/")[-1]
            images_in_uploaded.append(image_name)

    to_upload_images = []
    for local_image_name in glyph_images_list:
        local_image_dir = local_image_name.split("_")[0]
        if local_image_dir not in done_glyphs:
            if local_image_name not in images_in_uploaded:
                to_upload_images.append(local_image_name)
    return to_upload_images

def get_glyph_images_list(done_glyph, glyph_dirs):
    images_list = []
    glyph_dirs = Path(f"./glyph_to_do").iterdir()
    done_glyph = Path(f"./done_glyphs.txt").read_text().split("\n")
    for glyph_dir in glyph_dirs:
        glyph_name = glyph_dir.stem
        if glyph_name not in done_glyph:
            glyph_dir_path = Path(f"./glyph/{glyph_name}")
            glyph_dir_path.mkdir(parents=True, exist_ok=True)
            image_paths = list(glyph_dir.iterdir())
            for image_path in image_paths:
                images_list.append(image_path.name)
    Path(f"./glyph_images_list.txt").write_text("\n".join(images_list))

def copy_images():
    to_upload_images = Path(f"./to_upload_images.txt").read_text().split("\n")
    for image_name in to_upload_images:
        image_dir = image_name.split("_")[0]
        image_path = Path(f"./data/cropped_image/{image_dir}/{image_name}")
        to_upload_images_dir = Path(f"./glyph_to_upload/{image_dir}")
        to_upload_images_dir.mkdir(parents=True, exist_ok=True)
        to_upload_image_path = Path(f"{to_upload_images_dir}/{image_name}")
        subprocess.run(["cp", str(image_path), f"{to_upload_image_path}"])
    
def upload_images(upload_paths):
    for upload_path in upload_paths:
        file_name = upload_path.split("/")[-1]
        glyph = file_name.split("_")[0]
        s3_file_name = f"glyph/shul/{glyph}/{file_name}"
        s3.upload_file(upload_path, bucket_name, s3_file_name)

if __name__ == "__main__":
    image_names = []
    glyph_dirs = Path(f"./data/glyphs").iterdir()
    for glyph_dir in glyph_dirs:
        image_paths = list(glyph_dir.iterdir())
        for image_path in image_paths:
            image_name = image_path.name
            image_names.append(image_name)
    upload_paths = []
    filenames = []
    # s3_keys = Path(f"./s3_keys.txt").read_text().split("\n")
    # for s3_key in s3_keys:
    #     filename = s3_key.split("/")[-1]
    #     filenames.append(filename)
    for imagename in image_names:
        if imagename not in filenames:
            glyph = imagename.split("_")[0]
            upload_paths.append(f"./data/glyphs/{glyph}/{imagename}")
    Path(f"./upload_paths.txt").write_text("\n".join(upload_paths))
    upload_images(upload_paths)


    # done_glyph = Path(f"./done_glyphs.txt").read_text().split("\n")
    # glyph_dirs = Path(f"./glyph_to_do").iterdir()
    # get_glyph_images_list(done_glyph, glyph_dirs)
    # uploaded_glyphs = Path(f"./uploaded_glyphs.txt").read_text().split("\n")
    # glyph_images_list = Path(f"./glyph_images_list.txt").read_text().split("\n")
    # filtered_images = filter_images(glyph_images_list, uploaded_glyphs, done_glyph)
    # Path(f"./to_upload_images.txt").write_text("\n".join(filtered_images))
    # copy_images()
