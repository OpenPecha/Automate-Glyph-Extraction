from tools.extract_symbols import extract_symbols
from pathlib import Path



def main():
    folder_names = ["W7371", "W8LS73589"]
    done_list = Path(f"./data/F30000_glyphs.txt").read_text(encoding='utf-8').split("\n")
    output_image_path = Path(f"./data/cropped_image/")
    for folder_name in folder_names:
        source_dir_path = Path(f"./data/images/{folder_name}")
        ocr_dir = Path(f"./data/ocr/{folder_name}")
        ocr_paths = list(ocr_dir.iterdir())
        extract_symbols(ocr_paths, source_dir_path, output_image_path, done_list)
    


if __name__ == "__main__":
    main()