from pathlib import Path
from pipeline_for_glyph_extraction import extract_symbols
import shutil
from pathlib import Path
from tools import github_utils
import os


def publish_repo(local_repo):
    token = os.environ.get("GITHUB_TOKEN")
    github_utils.github_publish(
        local_repo,
        message="initial commit",
        not_includes=[],
        org="MonlamAI",
        token=token,
        description=local_repo.name
       )

def create_repo_folders(parent_dir, glyph_dirs, filename, num):
    glyph_names = ""
    
    glyph_dir_name = []
    repo_name = f"F{num:04}"    
    for glyph_dir in glyph_dirs:
        if len(glyph_dir_name) == 10:
            glyph_dir_name = []
            num += 1
            repo_name = f"F{num:04}"
        if len(list(glyph_dir.iterdir())) == 80:
            glyph_dir_name.append(glyph_dir)
            dest_folder = parent_dir / repo_name
            dest_folder.mkdir(parents=True, exist_ok=True)
            dest_dir = dest_folder / glyph_dir.name
            shutil.copytree(glyph_dir, dest_dir)
            glyph_names.append(glyph_dir.name)
            print(f"Copied {glyph_dir} to {dest_dir}")
    Path(Path(f"./{filename}")).write_text("\n".join(glyph_names), encoding='utf-8')

def extract_glyph(folder_names, font_name):
    done_list = Path(
        f"./data/{font_name}_glyphs.txt").read_text(encoding='utf-8').split("\n")
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


# def publish_unpublished_repos():
#     parent_dir = Path("./data/fonts/")
#     for repo_dir in parent_dir.iterdir():
#         if repo_dir.name in ["F50036", "F50037", "F50038", "F50039", "F50040", "F50041"]:
#             publish_repo(repo_dir)


def main():
    num = 50046
    font_name = "F10000"
    file_name = f"{font_name}_glyphs.txt"
    create_repo_for_glyph(file_name, num)


if __name__ == "__main__":
    main()
