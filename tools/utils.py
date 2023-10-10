import io
import botocore
from PIL import Image as PillowImage, ImageOps
from pathlib import Path
import hashlib
import os
import cv2
from PIL import Image, ImageOps, ImageFilter
# from wand.image import Image as WandImage

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


    return expanded_image

# used for tengyur pecing
def pre_process_image(filepath):
    filename = filepath.split("/")[-1]
    glyph = filename.split("_")[0]
    output_dir = Path(f"./data/glyphs/{glyph}")
    # Check if output directory exists and if not, create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    img = Image.open(filepath)
    img = ImageOps.autocontrast(img)
    # Convert image to grayscale and then to black and white for binarization
    img = img.convert('L').convert('1', dither=Image.NONE)

    base_filename = os.path.splitext(filename)[0]
    output_file_path = Path(f"{output_dir}/{base_filename}.png")
    if not os.path.exists(output_file_path.parent):
        os.makedirs(output_file_path.parent)
    img.save(output_file_path, 'PNG')


# def pre_process_image(filepath):
#     filename = os.path.basename(filepath)
#     glyph = filename.split("_")[0]
#     output_dir = f"./data/glyphs/{glyph}"
    
#     # Check if output directory exists and if not, create it
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)
    
#     # Read the image
#     img = cv2.imread(filepath)
    
#     # Auto contrast adjustment
#     lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
#     l, a, b = cv2.split(lab)
#     clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
#     cl = clahe.apply(l)
#     limg = cv2.merge((cl, a, b))
#     img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    
#     # Convert to grayscale
#     img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
#     # Thresholding to convert the image to black and white
#     _, img_bw = cv2.threshold(img_gray, 128, 255, cv2.THRESH_BINARY)
    
#     # Save the image as PNG
#     base_filename = os.path.splitext(filename)[0]
#     output_file_path = f"{output_dir}/{base_filename}.png"
#     cv2.imwrite(output_file_path, img_bw)


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

def save_with_wand(bits, output_fn):
    try:
         with WandImage(blob=bits.getvalue()) as img:
            img.format = "png"
            img.save(filename=str(output_fn))
    except Exception as e:
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
        if bits.getvalue():
            save_with_wand(bits, output_fn)
        return

    try:
        img.save(str(output_fn))
    except:
        del img
        save_with_wand(bits, output_fn)
    

def save_file(bits, filename, output_path):
    output_fn = output_path / filename
    if output_fn.is_file():
        return
    output_fn.write_bytes(bits.getvalue())

def is_archived(s3_key, s3_client, Bucket):
    try:
        s3_client.head_object(Bucket=Bucket, Key=s3_key)
    except Exception as e:
        print(f"error {e}")
        return False
    return True