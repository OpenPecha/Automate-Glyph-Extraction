import os
import jsonlines
import shutil
import csv
from git import Repo
from pathlib import Path
from local_config import MONLAM_AI_OCR_BUCKET, monlam_ai_ocr_s3_client
import stat

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
            s3_key = f"glyph/batch_2/{pub_type}/{directories.name}/{filename}"

            with open(local_file_path, "rb") as image_file:
                s3_client.upload_fileobj(image_file, bucket_name, s3_key)
            final_jsonl.append(
                {"id": filename, "image_url": s3_key, "text": directories.name})
            print(f"{filename} uploaded to S3")
        done_glyphs += directories.name + "\n"
    print("All files uploaded to S3")
    with open('data/done_list_for_s3/F70000_done_glyphs.txt', 'w', encoding='utf-8') as file:
        file.write(done_glyphs)
    return final_jsonl, done_glyphs


def write_jsonl(final_jsonl, jsonl_path):
    with jsonlines.open(jsonl_path, mode="w") as writer:
        writer.write_all(final_jsonl)
    print(f"JSONL file created at {jsonl_path}")


def get_coordinates(csv_dir, jsonl_path, output_csv_name):
    final_dict = {}
    image_ids = []
    combined_csv_data = []

    with jsonlines.open(jsonl_path) as reader:
        for jsonl in reader:
            image_ids.append(jsonl["id"])

    for csv_path in Path(csv_dir).glob("*.csv"):
        with open(csv_path, newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                id = row[0]
                final_dict[id] = row

    for id in image_ids:
        if id in final_dict:
            combined_csv_data.append(final_dict[id])

    output_csv_path = Path(csv_dir) / output_csv_name

    with open(output_csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(combined_csv_data)

    print(f"csv file created at {output_csv_path}")


def on_rm_error(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def main(repo_start, repo_end, pub_type):
    final_jsonl = []
    for num in range(repo_start, repo_end + 1):
        repo_name = f"F{num:04}"
        cloned_repo_path = clone_repo(repo_name)
        final_jsonl, _ = upload_to_s3_and_return_data(
            cloned_repo_path, pub_type, final_jsonl)
        shutil.rmtree(cloned_repo_path, onerror=on_rm_error)
        print(f"Repo {repo_name} is done")

    jsonl_path = Path(f"data/jsonl/F70000.jsonl")
    write_jsonl(final_jsonl, jsonl_path)

    csv_input_path = Path(f"data/csv/shul")
    get_coordinates(csv_input_path, jsonl_path, f"{repo_name}_coordinates.csv")


if __name__ == "__main__":
    main(70000, 70045, "shul")
