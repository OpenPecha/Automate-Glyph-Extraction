import json
import gzip
from pathlib import Path
from utils import crop_image


def is_symbol(text):
    return True

def get_bounding_poly_for_symbol(ocr_path):
    curr = {}
    bounding_polys = {}
    ocr_objects = json.load(gzip.open(str(ocr_path), "rb"))
    if ocr_objects == {}:
        return
    for blocks in ocr_objects["fullTextAnnotation"]["pages"][0]['blocks']:
        for bounding_box in blocks["paragraphs"][0]['words']:
            symbols_dict = bounding_box["symbols"]
            for num, symbol_dict in enumerate(symbols_dict, 1):
                text = symbol_dict["text"]
                vertices = symbol_dict["boundingBox"]["vertices"]
                curr[num] = {
                    'text': text,
                    'vertices': vertices
                    }
                bounding_polys.update(curr)
                curr = {}
    return bounding_polys


def get_image_name(output_paths):
    if any(output_paths.iterdir()) == False:
        return "1"
    else:
        for output_path in output_paths.iterdir():
            curr_name = int(output_path.stem)
            image_name = str(curr_name + 1)
            return image_name

def get_source_image_path(ocr_path, source_dir_path):
    filename = (ocr_path.stem).split(".")[0]
    for image_path in source_dir_path.iterdir():
        image_name = image_path.stem
        if filename == image_name:
            return image_path


def extract_symbols(ocr_paths, source_dir_path, output_image_path):
    for ocr_path in ocr_paths.iterdir():
        source_image_path = get_source_image_path(ocr_path, source_dir_path)
        bounding_polys = get_bounding_poly_for_symbol(ocr_path)
        if bounding_polys == None:
            continue
        for _, value in bounding_polys.items():
            text = value['text']
            vertices = value['vertices']
            output_path = Path(f"{output_image_path}/{text}")
            output_path.mkdir(parents=True, exist_ok=True)
            cropped_image = crop_image(source_image_path, vertices)
            image_name = get_image_name(output_path)
            cropped_image.save(f"{output_path}/{image_name}.jpg")

if __name__ == "__main__":
    work_id = "མིའི་རིགས་ཀྱི་ལོ་རྒྱུས་སྙིང་བསྡུས།"
    ocr_path = Path(f"./data/ocr_output/{work_id}")
    source_image_path = Path(f"./data/source_images/{work_id}")
    output_image_path = Path(f"./data/cropped_image/")
    extract_symbols(ocr_path, source_image_path, output_image_path)