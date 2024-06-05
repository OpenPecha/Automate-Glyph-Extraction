import os
import io
import json
import logging
import gzip
from pathlib import Path
from google.cloud import vision
from google.cloud.vision import AnnotateImageResponse

vision_client = vision.ImageAnnotatorClient()

def check_google_credentials():
    if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
        raise EnvironmentError("set the GAC environment variable.")

def google_ocr(image, lang_hint=None):
    check_google_credentials()
    if isinstance(image, (str, Path)):
        with io.open(image, "rb") as image_file:
            content = image_file.read()
    else:
        content = image
    ocr_image = vision.Image(content=content)

    features = [
        {
            "type_": vision.Feature.Type.DOCUMENT_TEXT_DETECTION,
            "model": "builtin/weekly",
        }
    ]
    image_context = {}
    if lang_hint:
        image_context["language_hints"] = [lang_hint]

    response = vision_client.annotate_image(
        {"image": ocr_image, "features": features, "image_context": image_context}
    )
    response_json = AnnotateImageResponse.to_json(response)
    response = json.loads(response_json)
    return response

def gzip_str(string_):
    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode="w") as fo:
        fo.write(string_.encode())
    bytes_obj = out.getvalue()
    return bytes_obj

def apply_ocr_on_image(image_path, OCR_dir, lang=None):
    image_name = image_path.stem
    result_fn = OCR_dir / f"{image_name}.json.gz"
    if result_fn.is_file():
        return
    try:
        result = google_ocr(str(image_path), lang_hint=lang)
    except Exception as e:
        logging.exception(f"Google OCR issue: {result_fn} with error: {e}")
        return
    result = json.dumps(result)
    gzip_result = gzip_str(result)
    result_fn.write_bytes(gzip_result)
    print(f"OCR completed and saved for image: {image_path}")

def ocr_images(images_dir):
    OCR_output_root = Path("../data/ocr_json/derge")
    OCR_output_root.mkdir(parents=True, exist_ok=True)

    processed_folders = [sub_dir.name for sub_dir in OCR_output_root.iterdir() if sub_dir.is_dir()]

    for sub_dir in images_dir.iterdir():
        if not sub_dir.is_dir():
            continue

        OCR_output_path = OCR_output_root / sub_dir.name

        if sub_dir.name in processed_folders:
            print(f"skipping already processed folder: {sub_dir}")
            continue

        OCR_output_path.mkdir(parents=True, exist_ok=True)

        for img_fn in sub_dir.iterdir():
            if img_fn.is_file():
                if img_fn.suffix.lower() in [".tiff", ".tif", ".jpg", ".jpeg"]:
                    image_type = img_fn.suffix.lower()[1:]
                    apply_ocr_on_image(img_fn, OCR_output_path, lang=image_type)
                else:
                    logging.warning(f"Unsupported image format: {img_fn.name}")
            else:
                logging.warning(f"{img_fn.name} is not a file, skipping.")

def main():
    images_dir = Path("../data/images/derge")
    ocr_images(images_dir)

if __name__ == "__main__":
    main()
