import json
import gzip
import re
from pathlib import Path
from utils import crop_and_resize

def load_required_glyphs():
    glyph_list_path = Path("../data/tibetan_essential_list.txt")
    return glyph_list_path.read_text(encoding='utf-8').split("\n")

def get_bounding_poly_for_symbol(ocr_path):
    bounding_polys = []
    try:
        ocr_objects = json.load(gzip.open(str(ocr_path), "rb"))
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {ocr_path}: {e}")
        return bounding_polys
    
    if "fullTextAnnotation" not in ocr_objects:
        return bounding_polys
    
    for block in ocr_objects["fullTextAnnotation"]["pages"][0]['blocks']:
        for paragraph in block.get("paragraphs", []):
            for word in paragraph['words']:
                for symbol in word["symbols"]:
                    text = symbol["text"]
                    vertices = symbol["boundingBox"]["vertices"]
                    bounding_polys.append([{'text': text, 'vertices': vertices}])
    return bounding_polys

def numerical_sort(file_path):
    numbers = re.findall(r'\d+', str(file_path))
    return int(numbers[0]) if numbers else 0

def get_image_name(output_dir, text):
    existing_files = list(output_dir.iterdir())
    if not existing_files:
        return f"{text}_1"
    
    last_image_path = sorted(existing_files, key=numerical_sort)[-1]
    last_image_number = int(last_image_path.stem.split("_")[-1])
    return f"{text}_{last_image_number + 1}"

def get_source_image_path(ocr_path, source_img_path):
    filename = ocr_path.stem.split(".")[0]
    print(f"Looking for source image with base filename: {filename}")
    for image_path in source_img_path.iterdir():
        print(f"Checking image file: {image_path.stem}")
        if filename == image_path.stem:
            print(f"Found matching image: {image_path}")
            return image_path
    raise FileNotFoundError(f"source image not found for OCR file: {ocr_path}")

def update_csv(cropped_image_path, vertices, image_path, work_id):
    filename = cropped_image_path.name
    csv_path = Path(f"../data/csv/pecing/{work_id}_glyphs.csv")
    with csv_path.open("a", encoding='utf-8') as f:
        f.write(f"{filename}, {image_path}, {vertices}\n")

def extract_symbols(ocr_paths, source_img_path, done_list, required_glyph_list, work_id):
    for num, ocr_path in enumerate(ocr_paths, 1):
        print(num)
        try:
            source_image_path = get_source_image_path(ocr_path, source_img_path)
        except FileNotFoundError as e:
            print(e)
            continue
        
        bounding_polys = get_bounding_poly_for_symbol(ocr_path)
        if not bounding_polys:
            continue
        
        for value in bounding_polys:
            text = value[0]['text']
            if text in done_list or text not in required_glyph_list:
                continue
            
            vertices = value[0]['vertices']
            output_path = Path(f"../data/glyphs/pecing/{text}")
            output_path.mkdir(parents=True, exist_ok=True)
            
            image_name = get_image_name(output_path, text)
            if int(image_name.split("_")[-1]) > 100:
                continue
            
            cropped_image_path = output_path / f"{image_name}.png"
            try:
                cropped_image, new_vertices = crop_and_resize(source_image_path, vertices)
            except Exception as e:
                print(f"Error cropping and resizing image {source_image_path}: {e}")
                continue
            
            if cropped_image is None:
                continue
            
            cropped_image.save(cropped_image_path, 'PNG')
            update_csv(cropped_image_path, new_vertices, source_image_path, work_id)

def main():
    required_glyph_list = load_required_glyphs()
    done_list = Path("../data/present_list/pecing_present_list.txt").read_text(encoding='utf-8').split("\n")
    
    folder_names = ["W1KG13126"]
    for folder_name in folder_names:
        source_img_path = Path(f"../data/source_images/pecing/{folder_name}")
        ocr_dir = Path(f"../data/ocr_json/pecing/{folder_name}")
        ocr_paths = [p for p in ocr_dir.iterdir() if p.is_file() and not p.name.startswith('.')]
        extract_symbols(ocr_paths, source_img_path, done_list, required_glyph_list, folder_name)

if __name__ == "__main__":
    main()
