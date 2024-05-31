import json
import gzip
import re
from pathlib import Path
from utils import crop_and_resize

DATA_DIR = Path("../data")
GLYPH_LIST_PATH = DATA_DIR / "Tibetan_Essential_Glyphs.txt"
PRESENT_LIST_PATH = DATA_DIR / "present_list/kumbum_present_list.txt"
SOURCE_IMAGES_DIR = Path(r"D:/Works/images/F50000")
OCR_JSON_DIR = Path(r"D:/Works/ocr_output/F50000")
OUTPUT_GLYPHS_DIR = DATA_DIR / "glyphs/kumbum"
CSV_DIR = DATA_DIR / "csv/kumbum"

def is_gzipped(file_path):
    try:
        with gzip.open(file_path, 'rb') as f:
            f.peek(1)
        return True
    except gzip.BadGzipFile:
        return False

def load_required_glyphs():
    return GLYPH_LIST_PATH.read_text(encoding='utf-8').split("\n")

def get_bounding_poly_for_symbol(ocr_path):
    bounding_polys = []
    if not is_gzipped(ocr_path):
        print(f"Skipping non-gzipped file: {ocr_path}")
        return bounding_polys
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
                    bounding_polys.append(
                        [{'text': text, 'vertices': vertices}])
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
    for image_path in source_img_path.iterdir():
        if filename == image_path.stem:
            return image_path
    raise FileNotFoundError(f"source image not found for OCR file: {ocr_path}")

def update_csv(cropped_image_path, vertices, image_path, work_id):
    filename = cropped_image_path.name
    csv_path = CSV_DIR / f"{work_id}_glyphs.csv"
    with csv_path.open("a", encoding='utf-8') as f:
        f.write(f"{filename}, {image_path}, {vertices}\n")

def extract_symbols(ocr_paths, source_img_path, done_list, required_glyph_list, work_id, all_found_glyphs):
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

            if text not in all_found_glyphs:
                all_found_glyphs.append(text)

            vertices = value[0]['vertices']
            output_path = OUTPUT_GLYPHS_DIR / text
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
    done_list = PRESENT_LIST_PATH.read_text(encoding='utf-8').split("\n")
    all_found_glyphs = []  

    folder_names =  ['W00EGS1017359', 'W1KG10112', 'W1KG10582', 'W1KG10769', 'W1KG22409', 'W1KG8888', 'W1KG8930', 'W1NLM1193', 'W1NLM1258', 'W1NLM1418', 'W1NLM1482', 'W1NLM2850', 'W1NLM2912', 'W1NLM3154', 'W1NLM3160', 'W1NLM3246', 'W1NLM3269', 'W1NLM3274', 'W1NLM3296', 'W1NLM3297', 'W1NLM3311', 'W1NLM3317', 'W1NLM3383', 'W1NLM3386', 'W1NLM3710', 'W1NLM3727', 'W1NLM3824', 'W1NLM385', 'W22087', 'W22317', 'W22318', 'W22319', 'W22324', 'W22325', 'W22327', 'W22345', 'W22349', 'W23462', 'W23726', 'W2CZ6759', 'W3CN22845', 'W3MS826', 'W4CZ74375', 'W4CZ74384', 'W4CZ74387', 'W4CZ74435', 'W4CZ74456', 'W4CZ74502', 'W4CZ74532', 'W4CZ74544', 'W4CZ74547', 'W739', 'W8LS17335', 'W8LS17448', 'W8LS17842', 'W8LS17845', 'W8LS17848', 'W8LS18095']

    for folder_name in folder_names:
        source_img_path = SOURCE_IMAGES_DIR / folder_name
        ocr_dir = OCR_JSON_DIR / folder_name
        ocr_paths = [p for p in ocr_dir.iterdir() if p.is_file() and not p.name.startswith('.')]
        extract_symbols(ocr_paths, source_img_path, done_list, required_glyph_list, folder_name, all_found_glyphs)
        
    single_output_file_path = OUTPUT_GLYPHS_DIR / "all_found_glyphs.txt"
    with single_output_file_path.open("w", encoding='utf-8') as file:
        for glyph in all_found_glyphs:
            file.write(f"{glyph}\n")
    print(f"found glyphs save at: {single_output_file_path}")

if __name__ == "__main__":
    main()
