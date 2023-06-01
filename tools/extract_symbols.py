import json
import gzip
import re
from pathlib import Path
from utils import crop_image


def is_symbol(text):
    return True

def get_bounding_poly_for_symbol(ocr_path):
    curr = []
    bounding_polys = []
    ocr_objects = json.load(gzip.open(str(ocr_path), "rb"))
    if ocr_objects == {}:
        return
    if "fullTextAnnotation" not in ocr_objects:
        return
    for blocks in ocr_objects["fullTextAnnotation"]["pages"][0]['blocks']:
        for bounding_box in blocks["paragraphs"][0]['words']:
            symbols_dict = bounding_box["symbols"]
            for symbol_dict in symbols_dict:
                text = symbol_dict["text"]
                vertices = symbol_dict["boundingBox"]["vertices"]
                curr = [{
                    'text': text,
                    'vertices': vertices
                    }]
                bounding_polys.append(curr)
                curr = {}
    return bounding_polys


def get_image_name(output_paths, text):
    if any(output_paths.iterdir()) == False:
        return f"{text}_1"
    else:
        for output_path in output_paths.iterdir():
            curr_name = output_path.stem
            name = int(curr_name.split("_")[1])
            image_name = f"{text}_"+str(name + 1)
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
        for value in bounding_polys:
            text = value[0]['text']
            vertices = value[0]['vertices']
            output_path = Path(f"{output_image_path}/{text}")
            print(output_path)
            if text in [".", "/", "_", "-", "(", ")", ",", "&", ":", "}", "{", "»", "—",
                         "།", "@", "[", "]", "-", "+", "=", "་"]:
                continue
            elif re.match(r"[a-zA-Z0-9\u4e00-\u9fff]", text):
                continue
            output_path.mkdir(parents=True, exist_ok=True)
            cropped_image = crop_image(source_image_path, vertices)
            image_name = get_image_name(output_path, text)
            try:
                cropped_image.save(f"{output_path}/{image_name}.jpg")
            except:
                continue

if __name__ == "__main__":
    work_id = "W1KG13126-I1KG13170"
    ocr_path = Path(f"./data/ocr_output/{work_id}")
    source_image_path = Path(f"./data/source_images/{work_id}")
    output_image_path = Path(f"./data/cropped_image/")
    extract_symbols(ocr_path, source_image_path, output_image_path)