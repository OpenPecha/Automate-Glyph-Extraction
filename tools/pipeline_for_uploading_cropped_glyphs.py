from pathlib import Path
import shutil
from pathlib import Path
import github_utils
import os

import os

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
    glyph_names = []
    glyph_dir_name = []
    repo_name = f"F{num:04}"    
    for glyph_dir in glyph_dirs:
        if len(glyph_dir_name) == 10:
            glyph_dir_name = []
            num += 1
            repo_name = f"F{num:04}"
        if len(list(glyph_dir.iterdir())) == 100:
            glyph_dir_name.append(glyph_dir)
            dest_folder = parent_dir / repo_name
            dest_folder.mkdir(parents=True, exist_ok=True)
            dest_dir = dest_folder / glyph_dir.name
            if not dest_dir.exists(): 
                shutil.copytree(glyph_dir, dest_dir)
                glyph_names.append(glyph_dir.name)
                print(f"Copied {glyph_dir} to {dest_dir}")
            else:
                print(f"Destination {dest_dir} already exists, skipping.")
    Path(Path(f"./{filename}")).write_text("\n".join(glyph_names), encoding='utf-8')


def create_repo_for_glyph(file_name, num):
    glyph_dirs = list(Path(f"../data/glyphs/shul").iterdir())
    parent_dir = Path("../data/batched_glyphs/")
    parent_dir.mkdir(parents=True, exist_ok=True)
    create_repo_folders(parent_dir, glyph_dirs, file_name, num)
    for repo_dir in parent_dir.iterdir():
        if int(repo_dir.name[1:]) < 20003:
            continue
        publish_repo(repo_dir)

def main():
    num = 20001
    font_name = "F20000"
    file_name = f"{font_name}_glyphs.txt"
    create_repo_for_glyph(file_name, num)


if __name__ == "__main__":
    main()
