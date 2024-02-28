import os
import jsonlines
import shutil
import csv
from git import Repo
from pathlib import Path
from tools.config import MONLAM_AI_OCR_BUCKET, monlam_ai_ocr_s3_client
from tools.utils import is_archived


s3_client = monlam_ai_ocr_s3_client
bucket_name = MONLAM_AI_OCR_BUCKET

org_name = "MonlamAI"


def get_coordinates(csv_path, jsonl_path):
    _dict = {}
    final_dict = {}
    updated_csv = []
    image_ids = []
    with jsonlines.open(jsonl_path) as reader:
        for jsonl in reader:
            image_ids.append(jsonl["id"])
    with open(csv_path, newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            id = row[0]
            _dict[id]= {
                "row": row   
            }
            final_dict.update(_dict)
            _dict = {}
    for id in image_ids:
        if final_dict[id]:
            updated_csv.append(final_dict[id]["row"])
    with open('F50000_2h_coordinates.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        for new_row in updated_csv:
            writer.writerow(new_row)

       


def clone_repo(repo_name):
    repo_url = f"https://github.com/{org_name}/{repo_name}.git"
    clone_dir = f"./tmp/{repo_name}"
    Repo.clone_from(repo_url, clone_dir)
    return clone_dir


def upload_to_s3_and_return_data(repo_path, pub_type, final_jsonl):
    done_glyphs = ""
    for directories in list(Path(repo_path).iterdir()):
        dir = directories.name
        if dir == ".git":
            continue
        for image_path in directories.iterdir():
            filename = image_path.name
            local_file_path = str(image_path)
            s3_key = f"glyph/{pub_type}/{dir}/{filename}"
            if is_archived(s3_key, s3_client, bucket_name):
               continue
            with open(local_file_path, "rb") as image_file:
                s3_client.upload_fileobj(image_file, bucket_name, s3_key)
            final_jsonl.append({"id":filename, "image_url":s3_key, "text": dir})
        done_glyphs += dir + "\n"
    return final_jsonl, done_glyphs


def write_jsonl(final_jsonl, jsonl_path):
    with jsonlines.open(jsonl_path, mode="w") as writer:
        writer.write_all(final_jsonl)


def main(repo_start, repo_end, pub_type):
    final_jsonl = []
    final_glyphs = ""
    for num in range(repo_start, repo_end):
        repo_name = f"F{num:04}"
        cloned_repo_path = clone_repo(repo_name)
        image_data, done_glyphs = upload_to_s3_and_return_data(cloned_repo_path, pub_type, final_jsonl)
        final_jsonl = image_data
        final_glyphs += done_glyphs
        shutil.rmtree(cloned_repo_path)
        print(f"repo {repo_name} is done")
    jsonl_path = Path(f"./output_F50000_batch17h.jsonl")
    write_jsonl(final_jsonl, jsonl_path)
    Path(f"./F50000_glyphsh.txt").write_text(final_glyphs, encoding='utf-8')
    get_coordinates(Path("./F50000_glyphs.csv"), jsonl_path)


def cleanup(dirs):
    for dir in list(dirs.iterdir()):
        if len(list(dir.iterdir())) == 100:
            shutil.rmtree(dir)
            print(f"removed {dir}")

def get_done_glyphs():
    done_glyphs = []
    for repo_num in range (50000, 50046):
        repo_name = f"F{repo_num:04}"
        if repo_name == "F50002":
            continue
        repo_path = clone_repo(repo_name)
        for directories in list(Path(repo_path).iterdir()):
            dir = directories.name
            if dir == ".git":
                continue
            if dir not in done_glyphs:
                done_glyphs.append(dir)
        shutil.rmtree(repo_path)
        print(f"repo {repo_name} is done")
    Path(f"./F50000_glyphs.txt").write_text("\n".join(done_glyphs), encoding='utf-8')

if __name__ == "__main__":
    cleanup(Path("./data/glyphs/"))
    # repo_start = 50045
    # repo_end = 50046
    # main(repo_start, repo_end, pub_type="01_G1PD129182")
    # get_coordinates(Path("./F50000_glyphs.csv"), Path("./output.jsonl"))