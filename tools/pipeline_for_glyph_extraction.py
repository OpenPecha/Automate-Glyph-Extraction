from tools.extract_symbols import extract_symbols
from pathlib import Path
from tools.create_repo import publish_repo, create_repo_folders
from tools.pipeline_for_glyph_jsonl import clone_repo

def extract_glyph(folder_names, font_name):
    done_list = Path(f"./data/{font_name}_glyphs.txt").read_text(encoding='utf-8').split("\n")
    for folder_name in folder_names:
        print(folder_name)
        source_dir_path = Path(f"./data/images/{font_name}/{folder_name}")
        ocr_dir = Path(f"./data/ocr/{font_name}/{folder_name}")
        if ocr_dir.exists() == False:
            continue
        ocr_paths = list(ocr_dir.iterdir())
        extract_symbols(ocr_paths, source_dir_path, done_list, font_name)


def create_repo_for_glyph(file_name, num):
    glyph_dirs = list(Path(f"./data/glyphs/").iterdir())
    parent_dir = Path("./data/fonts/")
    parent_dir.mkdir(parents=True, exist_ok=True)
    create_repo_folders(parent_dir, glyph_dirs, file_name, num)
    for repo_dir in parent_dir.iterdir():
        if int(repo_dir.name[1:]) < 50046:
            continue
        publish_repo(repo_dir)


def publish_unpublished_repos():
    parent_dir = Path("./data/fonts/")
    for repo_dir in parent_dir.iterdir():
        if repo_dir.name in ["F50036", "F50037", "F50038", "F50039", "F50040", "F50041"]:
            publish_repo(repo_dir)

def main():
    num = 50046
    font_name = "F50000"
    folder_names = Path(f"./{font_name}.txt").read_text(encoding='utf-8').split("\n")
    file_name = f"{font_name}_glyphs.txt"
    extract_glyph(folder_names, font_name)
    create_repo_for_glyph(file_name, num)



if __name__ == "__main__":
    main()
