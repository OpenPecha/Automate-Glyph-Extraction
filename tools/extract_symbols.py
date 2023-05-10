import json
import gzip
from pathlib import Path
from utils import crop_image


def is_symbol(text):
    return True

def get_bounding_poly_for_symbol(ocr_path):
    bounding_polys = []
    ocr_objects = json.load(gzip.open(str(ocr_path), "rb"))
    for ocr_object in ocr_objects["fullTextAnnotation"]["pages"][0]["blocks"]:
        for bounding_box in ocr_object["paragraphs"][0]["words"]:
            symbols_dict = bounding_box["symbols"]
            for symbol_dict in symbols_dict:
                text = symbol_dict["text"]
                vertices = symbol_dict["boundingBox"]["vertices"]
                bounding_polys.append(vertices)
    return bounding_polys


def extract_symbols(ocr_path, source_image_path, output_image_path):
    bounding_polys = get_bounding_poly_for_symbol(ocr_path)
    for num, vertices in enumerate(bounding_polys, 1):
        cropped_image = crop_image(source_image_path, vertices)
        cropped_image.save(f"{output_image_path}/{num}.jpg")

if __name__ == "__main__":
    ocr_path = Path(f"./data/ocr_output/0140.json.gz")
    source_image_path = Path(f"./data/source_images/0140.jpg")
    output_image_path = Path(f"./data/cropped_image/")
    extract_symbols(ocr_path, source_image_path, output_image_path)