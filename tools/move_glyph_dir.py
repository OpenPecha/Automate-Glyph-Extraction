from pathlib import Path
import yaml
import os
import subprocess

def move_image_folders(source_path, destination_path):
    subprocess.run(["cp", "-r", source_path, destination_path])


if __name__ == "__main__":
    source_dirs = list(Path("./data/glyph_images/").iterdir())
    done_dirs = list(Path("./data/W1KG13126/").iterdir())
    to_upload_dir = Path(f"./data/to_upload/")
    for source_dir in source_dirs:
        present = False
        glyph = source_dir.stem
        for done_dir in done_dirs:
            if glyph == done_dir.stem:
                present = True
                break
        if present == False:
            move_image_folders(source_dir, to_upload_dir)
