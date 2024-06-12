import os
import jsonlines
import shutil
import csv
from git import Repo
from pathlib import Path
from config import MONLAM_AI_OCR_BUCKET, monlam_ai_ocr_s3_client
from utils import is_archived

s3_client = monlam_ai_ocr_s3_client
bucket_name = MONLAM_AI_OCR_BUCKET

org_name = "MonlamAI"

def clone_repo(repo_name):
    repo_url = f"https://github.com/{org_name}/{repo_name}.git"
    clone_dir = Path(f"./tmp/{repo_name}")
    if not clone_dir.exists():
        clone_dir.mkdir(parents=True)
    Repo.clone_from(repo_url, clone_dir)
    return clone_dir

def upload_to_s3_and_return_data(repo_path, pub_type, final_jsonl):
    done_glyphs = ""
    for directories in repo_path.iterdir():
        if directories.name == ".git":
            continue
        for image_path in directories.iterdir():
            filename = image_path.name
            local_file_path = image_path
            s3_key = f"glyph/shul_test/{pub_type}/{directories.name}/{filename}"
            if is_archived(s3_key, s3_client, bucket_name):
                continue
            with open(local_file_path, "rb") as image_file:
                s3_client.upload_fileobj(image_file, bucket_name, s3_key)
            final_jsonl.append({"id": filename, "image_url": s3_key, "text": directories.name})
            print(f"Uploaded {filename} to S3")
        done_glyphs += directories.name + "\n"
    print("All files uploaded to S3")
    return final_jsonl, done_glyphs

def write_jsonl(final_jsonl, jsonl_path):
    with jsonlines.open(jsonl_path, mode="w") as writer:
        writer.write_all(final_jsonl)
    print(f"JSON Lines file created at {jsonl_path}")

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
            _dict[id] = {"row": row}
            final_dict.update(_dict)
    for id in image_ids:
        if id in final_dict:
            updated_csv.append(final_dict[id]["row"])
    output_csv_path = Path(f'F{csv_path.stem}_coordinates.csv')
    with open(output_csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        for new_row in updated_csv:
            writer.writerow(new_row)
    print(f"CSV file with coordinates created at {output_csv_path}")

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
    jsonl_path = Path(f"../data/jsonl/output_F{repo_start}.jsonl")
    write_jsonl(final_jsonl, jsonl_path)
    Path(f"./F{repo_start}_glyphs.txt").write_text(final_glyphs, encoding='utf-8')
    csv_input_path = Path(f"../data/jsonl/F{repo_start}_glyphs.csv")
    get_coordinates(csv_input_path, jsonl_path)


if __name__ == "__main__":
    main(20000, 20001, "shul")
