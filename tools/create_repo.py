import shutil
from pathlib import Path
from tools import github_utils
import os

def publish_repo(local_repo):
    token = "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"
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


