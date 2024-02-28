import io
import botocore
import shutil
from tools import github_utils
from PIL import Image as PillowImage, ImageOps
from pathlib import Path
import hashlib
from PIL import Image, ImageOps, ImageFilter
# from wand.image import Image as WandImage

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
    glyph_names = list(Path(f"./data/{filename}").read_text(encoding='utf-8').split("\n"))
    
    for glyph_dir in glyph_dirs:
        if glyph_dir.name in glyph_names:
            continue
        if len(glyph_dir_name) == 10:
            glyph_dir_name = []
            num += 1
            repo_name = f"F{num:04}"
        if len(list(glyph_dir.iterdir())) == 100:
            glyph_dir_name.append(glyph_dir)
            dest_folder = parent_dir / repo_name
            dest_folder.mkdir(parents=True, exist_ok=True)
            dest_dir = dest_folder / glyph_dir.name
            shutil.copytree(glyph_dir, dest_dir)
            glyph_names.append(glyph_dir.name)
            print(f"Copied {glyph_dir} to {dest_dir}")
    Path(Path(f"./{filename}")).write_text("\n".join(glyph_names), encoding='utf-8')

def get_hash(work_id):
    md5 = hashlib.md5(str.encode(work_id))
    two = md5.hexdigest()[:2]
    return two

def get_image_name_for_sentence_image(source_image_path, joined_box):
    image_name = source_image_path.stem
    first_vertex = str(joined_box[0]["x"]) + str(joined_box[0]["y"])
    last_vertex = str(joined_box[3]["x"]) + str(joined_box[3]["y"])
    line_image_name = image_name + "_" + first_vertex + "_" + last_vertex
    return line_image_name


def crop_and_resize(source_image_path, vertices, expand_percentage=4, greyscale=True, auto_contrast=True):
    image = PillowImage.open(source_image_path)

    x0, y0 = vertices[0]['x'], vertices[0]['y']
    x1, y1 = vertices[1]['x'], vertices[1]['y']
    x2, y2 = vertices[2]['x'], vertices[2]['y']
    x3, y3 = vertices[3]['x'], vertices[3]['y']

    left = min(x0, x1, x2, x3)
    top = min(y0, y1, y2, y3)
    right = max(x0, x1, x2, x3)
    bottom = max(y0, y1, y2, y3)

    width = right - left
    height = bottom - top

    expand_amount = int(expand_percentage * width)

    expanded_left = max(left - expand_amount, 0)
    expanded_top = max(top - expand_amount, 0)
    expanded_right = min(right + expand_amount, image.width)
    expanded_bottom = min(bottom + expand_amount, image.height)

    expanded_image = image.crop((expanded_left, expanded_top, expanded_right, expanded_bottom))
    new_vertices = f"{expanded_left}, {expanded_top}, {expanded_right}, {expanded_bottom}"
    if expanded_image.width <= 0 or expanded_image.height <= 0:
        return None, None
    else:
        try:
            if auto_contrast:
                img = ImageOps.autocontrast(expanded_image)
            if greyscale:
                img = img.convert('L').convert('1', dither=Image.NONE)
        except:
            return None, None
        cropped_resized_image = img.resize((img.width*2, img.height*2))
    return cropped_resized_image, new_vertices

# def pre_process_image(filepath, image):
#     filename = filepath.split("/")[-1]
#     glyph = filename.split("_")[0]
#     output_dir = Path(f"./data/glyphs/{glyph}")
#     output_dir.mkdir(parents=True, exist_ok=True)
#     img = ImageOps.autocontrast(image)
#     img = img.convert('L').convert('1', dither=Image.NONE)
#     base_filename = os.path.splitext(filename)[0]
#     output_file_path = Path(f"{output_dir}/{base_filename}.png")
#     if not os.path.exists(output_file_path.parent):
#         os.makedirs(output_file_path.parent)
#     img.save(output_file_path, 'PNG')


def list_obj_keys(prefix, s3_client, bucket_name):
    obj_keys = []
    continuation_token = None
    while True:
        if continuation_token:
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix, ContinuationToken=continuation_token)
        else:
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        if response['Contents']:
            for obj in response['Contents']:
                obj_key = obj['Key']
                obj_keys.append(obj_key)
        continuation_token = response.get("NextContinuationToken")
        if not continuation_token:
            break
        
    return obj_keys


def get_s3_bits(s3_key, s3_bucket):
    filebits = io.BytesIO()
    try:
        s3_bucket.download_fileobj(s3_key, filebits)
        return filebits
    except botocore.exceptions.ClientError as error:
        return



def _binarize(img, th=127):
    return img.convert("L").point(lambda x: 255 if x > th else 0, mode='1')


def save_image(bits, filename, output_path):
    output_fn = output_path / filename
    if Path(filename).suffix in [".tif", ".tiff", ".TIF"]:
        output_fn = output_path / f'{filename.split(".")[0]}.png'
    if output_fn.is_file():
        return
    try:
        img = PillowImage.open(bits)
    except Exception as e:
        return
    try:
        img.save(str(output_fn))
    except:
        return
    

def save_file(bits, filename, output_path):
    output_fn = output_path / filename
    if output_fn.is_file():
        return
    output_fn.write_bytes(bits.getvalue())

def is_archived(s3_key, s3_client, Bucket):
    try:
        s3_client.head_object(Bucket=Bucket, Key=s3_key)
    except:
        return False
    return True