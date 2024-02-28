from pathlib import Path
import jsonlines


def create_jsonl(glyph_list):
    final_jsonl = []
    for image_path in glyph_list:
        image_name = image_path.split("/")[-1]
        image_id = image_name.split(".")[0]
        text = image_name.split("_")[0]
        image_url = image_path
        final_jsonl.append({"id":image_id, "image_url": image_url, "text": text})
    return final_jsonl

def write_jsonl(final_jsonl, jsonl_path):
    with jsonlines.open(jsonl_path, mode="w") as writer:
        writer.write_all(final_jsonl)

def get_not_annotated_list(glyph_list):
    glyphs_done = []
    glyph_to_do = []
    jsonl_path = Path(f"./glyphs.jsonl")
    with jsonlines.open(jsonl_path, mode="r") as reader:
        for line in reader:
            imagename = line["image_url"].split("/")[-1]
            glyphs_done.append(imagename)
    for glyph in glyph_list:
        image_name = glyph.split("/")[-1]
        if image_name in glyphs_done:
            continue
        else:
            glyph_to_do.append(glyph)
    return glyph_to_do

if __name__ == "__main__":
    glyph_list = Path(f"./s3_keys.txt").read_text().split("\n")
    # not_annotated_list = get_not_annotated_list(glyph_list)
    final_jsonl = create_jsonl(glyph_list)
    write_jsonl(final_jsonl, f"./glyphs_to_do.jsonl")