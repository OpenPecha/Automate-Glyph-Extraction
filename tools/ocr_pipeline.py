import os
import io
import json
import logging
import gzip
from pathlib import Path
from PIL import Image
from google.cloud import vision
from google.cloud.vision import AnnotateImageResponse

if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    raise EnvironmentError("environment variable for GAC is not set.")

print(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])


vision_client = vision.ImageAnnotatorClient()



def google_ocr(image, lang_hint=None):
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

def apply_ocr_on_folder(images_dir, OCR_dir, lang=None):
    if not images_dir.is_dir():
        return
    for img_fn in list(images_dir.iterdir()):
        result_fn = OCR_dir / f"{img_fn.stem}.json.gz"
        if result_fn.is_file():
            continue
        try:
            result = google_ocr(str(img_fn), lang_hint=lang)
        except Exception as e:
            logging.exception(f"Google OCR issue: {result_fn} with error: {e}")
            continue
        result = json.dumps(result)
        gzip_result = gzip_str(result)
        result_fn.write_bytes(gzip_result)

def ocr_images(images_path):
    OCR_output_path = Path(f"../data/ocr_json/{images_path.stem}/")
    OCR_output_path.mkdir(parents=True, exist_ok=True)
    apply_ocr_on_folder(
            images_dir = images_path,
            OCR_dir = OCR_output_path
        )

def OCR_tiff_images(tiff_dir):
    title = tiff_dir.name
    tiff_paths = tiff_dir.iterdir()
    for tiff_path in tiff_paths:
        image_name = tiff_path.stem
        output_path = Path(f"../data/source_images/jpeg/{title}/")
        output_path.mkdir(parents=True, exist_ok=True)
        try:
            tiff_image = Image.open(tiff_path)
            if tiff_image.mode == 'CMYK':
                tiff_image = tiff_image.convert('RGB')
            result_fn = Path(f"{output_path}/{image_name}.jpg")
            if result_fn.is_file():
                continue
            tiff_image.save(result_fn, 'JPEG')
        except Exception as e:
            print(f"Error converting TIFF to JPEG: {e}")
    jpeg_path = Path(f"../data/source_images/jpeg/{title}")
    ocr_images(jpeg_path)

def main(type):
    if type == "tiff":
        tiff_dirs = list(Path(f"../data/source_images/tiff/").iterdir())
        for tiff_dir in tiff_dirs:
            OCR_tiff_images(tiff_dir)
    elif type == "jpeg":
        images_paths = sorted(Path(f"../data/source_images/jpeg/").iterdir())
        for images_path in images_paths:
            ocr_images(images_path)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2 or sys.argv[1] not in ["tiff", "jpeg"]:
        print("Usage: python script.py [tiff|jpeg]")
        sys.exit(1)
    main(sys.argv[1])
