import io
import botocore
from PIL import Image as PillowImage
from pathlib import Path
# from wand.image import Image as WandImage


def crop_image(source_image_path, vertices, rotate_image=False):
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

    expand_percentage = 0.2
    expand_width = int(width * expand_percentage)
    expand_height = int(height * expand_percentage)

    expanded_left = max(left - expand_width, 0)
    expanded_top = max(top - expand_height, 0)
    expanded_right = right + expand_width
    expanded_bottom = bottom + expand_height

    expanded_height = expanded_bottom - expanded_top

    expand_bottom_percentage = 0.3
    expand_bottom_height = int(expanded_height * expand_bottom_percentage)
    expanded_bottom = bottom + expand_bottom_height

    cropped_image = image.crop((expanded_left, expanded_top, expanded_right, expanded_bottom))
    if rotate_image:
        rotated_image = cropped_image.rotate(270, expand=True)
        final_image = rotated_image
    else:
        final_image = cropped_image

    return final_image

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