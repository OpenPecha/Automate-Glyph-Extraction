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
    OCR_output_path = Path("../data/ocr_jso/derge") / images_dir.name
    OCR_output_path.mkdir(parents=True, exist_ok=True)
    for img_fn in list(images_dir.iterdir()):
        if img_fn.suffix.lower() == ".tiff" or img_fn.suffix.lower() == ".tif":
            image_type = "tiff"
        elif img_fn.suffix.lower() == ".jpg" or img_fn.suffix.lower() == ".jpeg":
            image_type = "jpeg"
        else:
            logging.warning(f"Unsupported image format: {img_fn.name}")
            continue
        apply_ocr_on_image(img_fn, OCR_output_path, lang=image_type)
