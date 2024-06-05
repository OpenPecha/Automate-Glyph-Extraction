import json
import gzip
from pathlib import Path
from utils import crop_and_resize

essential_list_path = Path("../data/Tibetan_Essential_Glyphs.txt")
present_list_path = Path("../data/present_list/derge_present_list.txt")
source_image_dir = Path("../data/source_images/derge")
ocr_json_dir = Path("../data/ocr_json/derge")
output_glyph_dir = Path("../data/glyphs/derge")
csv_dir = Path("../data/csv/derge")


def get_bounding_poly_for_symbol(ocr_path):
    bounding_polys = []
    with gzip.open(ocr_path, 'rt', encoding='utf-8') as f:
        ocr_objects = json.load(f)

    for block in ocr_objects.get("fullTextAnnotation", {}).get("pages", [{}])[0].get("blocks", []):
        for paragraph in block.get("paragraphs", []):
            for word in paragraph.get("words", []):
                for symbol in word.get("symbols", []):
                    text = symbol.get("text", "")
                    vertices = symbol.get(
                        "boundingBox", {}).get("vertices", [])
                    if text and vertices:
                        bounding_polys.append(
                            {'text': text, 'vertices': vertices})
    return bounding_polys


def numerical_sort(file_path):
    return int(''.join(filter(str.isdigit, str(file_path.stem))))

def get_image_name(output_dir, text):
    existing_files = list(output_dir.glob("*.png"))
    if not existing_files:
        return f"{text}_1"

    last_image_path = max(existing_files, key=numerical_sort)
    last_image_number = int(
        ''.join(filter(str.isdigit, str(last_image_path.stem))))
    return f"{text}_{last_image_number + 1}"

def get_source_image_path(ocr_path, source_img_path):
    filename = ocr_path.stem.split(".")[0]
    for image_path in source_img_path.iterdir():
        if filename == image_path.stem:
            return image_path
        
def update_csv(cropped_image_path, vertices, image_path, work_id):
    csv_path = csv_dir / f"{work_id}_glyphs.csv"
    with csv_path.open("a", encoding='utf-8') as f:
        f.write(f"{cropped_image_path.name}, {image_path}, {vertices}\n")
    print(f"glyph saved: {cropped_image_path}")


def extract_symbols(ocr_paths, source_img_path, present_list, required_glyph_list, work_id, all_found_glyphs):
    for ocr_path in ocr_paths:
        source_image_path = get_source_image_path(ocr_path, source_img_path)

        bounding_polys = get_bounding_poly_for_symbol(ocr_path)
        for value in bounding_polys:
            text = value["text"]
            if text in present_list or text not in required_glyph_list:
                continue
            if text not in all_found_glyphs:
                all_found_glyphs.append(text)

            output_path = output_glyph_dir / text
            output_path.mkdir(parents=True, exist_ok=True)

            image_name = get_image_name(output_path, text)
            if int(image_name.split("_")[-1]) > 100:
                continue

            cropped_image_path = output_path / f"{image_name}.png"
            cropped_image, new_vertices = crop_and_resize(
                source_image_path, value["vertices"])
            if cropped_image:
                cropped_image.save(cropped_image_path, 'PNG')
                update_csv(cropped_image_path, new_vertices,
                           source_image_path, work_id)


def main():
    required_glyph_list = essential_list_path.read_text(encoding='utf-8').strip().split("\n")
    present_list = present_list_path.read_text(encoding='utf-8').strip().split("\n")
    all_found_glyphs = []

    work_id_folders = [folder.name for folder in source_image_dir.iterdir() if folder.is_dir()]

    for work_id_folder in work_id_folders:
        source_img_path = source_image_dir / work_id_folder
        ocr_dir = ocr_json_dir / work_id_folder
        ocr_paths = list(ocr_dir.glob("*.json.gz"))
        extract_symbols(ocr_paths, source_img_path, present_list,required_glyph_list, work_id_folder, all_found_glyphs)

    single_output_file_path = output_glyph_dir / "all_found_glyphs.txt"
    with single_output_file_path.open("w", encoding='utf-8') as file:
        for glyph in all_found_glyphs:
            file.write(f"{glyph}\n")
    print(f"found glyphs saved at: {single_output_file_path}")


if __name__ == "__main__":
    main()
