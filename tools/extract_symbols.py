import json
import gzip
import re
from openpecha.utils import load_yaml
from pathlib import Path
from utils import crop_and_resize, pre_process_image

essential_list = Path(f"./data/tibetan_essential_list.txt").read_text().split("\n")


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


def get_image_name(output_dir, text):
    if any(output_dir.iterdir()) == False:
        return f"{text}_1"
    else:
        for output_path in output_dir.iterdir():
            curr_name = output_path.stem
            name = int(curr_name.split("_")[1])
            image_name = f"{text}_"+str(name + 1)
            if Path(f"{output_dir}/{image_name}.jpg").exists():
                continue
            else:
                return image_name

def get_source_image_path(ocr_path, source_dir_path):
    filename = (ocr_path.stem).split(".")[0]
    for image_path in source_dir_path.iterdir():
        image_name = image_path.stem
        if filename == image_name:
            return image_path


def extract_symbols(ocr_paths, source_dir_path, output_image_path, done_list):
    for num, ocr_path in enumerate(ocr_paths, 1):
        print(num)
        source_image_path = get_source_image_path(ocr_path, source_dir_path)
        bounding_polys = get_bounding_poly_for_symbol(ocr_path)
        if bounding_polys == None:
            continue
        for value in bounding_polys:
            text = value[0]['text']
            if text in done_list:
                continue
            vertices = value[0]['vertices']
            output_path = Path(f"{output_image_path}/{text}")
            if text in essential_list:
                output_path.mkdir(parents=True, exist_ok=True)
                image_name = get_image_name(output_path, text)
                if int(image_name.split("_")[-1]) > 100 :
                    continue
                cropped_image_path = f"{output_path}/{image_name}.jpg"
                cropped_image = crop_and_resize(source_image_path, vertices)
                if cropped_image.width <= 0 or cropped_image.height <= 0:
                    continue
                cropped_resized_image = cropped_image.resize((cropped_image.width*2, cropped_image.height*2))
                try:
                    cropped_resized_image.save(cropped_image_path)
                    pre_process_image(cropped_image_path)
                except:
                    continue
                

if __name__ == "__main__":
    # folder_names = ["W23957", "W30178", "W30183"]
    folder_names = ["W30451", "W7371", "W23746", "W30450"]
    for folder_name in folder_names:
        source_image_path = Path(f"./data/images/{folder_name}")
        output_image_path = Path(f"./data/cropped_image/")
        tengyur_images_yml = load_yaml(Path(f"./shul/{folder_name}_images.yml"))
        ocr_dir = Path(f"./data/ocr/{folder_name}")
        ocr_paths = list(Path(f"./data/ocr/").iterdir())
        extract_symbols(ocr_paths, source_image_path, output_image_path, essential_list)