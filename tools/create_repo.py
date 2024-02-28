import shutil
from pathlib import Path
from tools import github_utils
<<<<<<< HEAD
import os

def publish_repo(local_repo):
    token = "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"
=======

parent_dir = Path("./font/")

def publish_repo(local_repo):
    token = ""
>>>>>>> 9bf9e1677c757451c5c299dc2ba340f516f80830
    github_utils.github_publish(
        local_repo,
        message="initial commit",
        not_includes=[],
        org="MonlamAI",
        token=token,
        description=local_repo.name
       )

<<<<<<< HEAD
def create_repo_folders(parent_dir, glyph_dirs, filename, num):
    glyph_names = ""
    
    glyph_dir_name = []
    repo_name = f"F{num:04}"    
    for glyph_dir in glyph_dirs:
=======
def create_repo_folders(glyph_dirs):
    num = 30021
    glyph_names = ""
    
    glyph_dir_name = []
    repo_name = f"F{num:04}"
    glyph_names = list(Path(f"./data/F30000_glyphs.txt").read_text(encoding='utf-8').split("\n"))
    
    for glyph_dir in glyph_dirs:
        if glyph_dir.name in glyph_names:
            continue
>>>>>>> 9bf9e1677c757451c5c299dc2ba340f516f80830
        if len(glyph_dir_name) == 10:
            glyph_dir_name = []
            num += 1
            repo_name = f"F{num:04}"
<<<<<<< HEAD
        if len(list(glyph_dir.iterdir())) == 80:
=======
        if len(list(glyph_dir.iterdir())) == 100:
>>>>>>> 9bf9e1677c757451c5c299dc2ba340f516f80830
            glyph_dir_name.append(glyph_dir)
            dest_folder = parent_dir / repo_name
            dest_folder.mkdir(parents=True, exist_ok=True)
            dest_dir = dest_folder / glyph_dir.name
            shutil.copytree(glyph_dir, dest_dir)
            glyph_names.append(glyph_dir.name)
            print(f"Copied {glyph_dir} to {dest_dir}")
<<<<<<< HEAD
    Path(Path(f"./{filename}")).write_text("\n".join(glyph_names), encoding='utf-8')

=======
    Path(f"./F30000_glyphs.txt").write_text("\n".join(glyph_names), encoding='utf-8')

if __name__ == "__main__":
    glyph_dirs = list(Path(f"./data/glyphs/").iterdir())
    create_repo_folders(glyph_dirs)
    for repo_dir in parent_dir.iterdir():
        if int(repo_dir.name[1:]) < 30021:
            continue
        publish_repo(repo_dir)
>>>>>>> 9bf9e1677c757451c5c299dc2ba340f516f80830

