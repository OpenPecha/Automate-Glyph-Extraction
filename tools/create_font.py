from pathlib import Path
from tools.config import MONLAM_AI_OCR_BUCKET, monlam_ai_ocr_s3_client
from PIL import Image, ImageDraw
import subprocess
import urllib.parse
import os
import svgwrite
import base64
from PIL import Image, ImageFont
from fontTools.ufoLib import UFOWriter
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from PIL import Image
import numpy as np
import jsonlines
import logging

s3 = monlam_ai_ocr_s3_client
bucket_name = MONLAM_AI_OCR_BUCKET

logging.basicConfig(filename='skppied_glyph.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

def png_to_svg(input_png, output_svg):
    image = Image.open(input_png).convert('1')
    pbm_path = "temp.pbm"
    image.save(pbm_path)
    subprocess.run(["potrace", pbm_path, "-s", "--scale", "5.5", "-o", output_svg])
    os.remove(pbm_path)

def create_into_desired_format():
    # Define the input and output file paths
    image_name = cleaned_image_path.split("/")[-1]
    input_dir = f"./cleaned_images"
    output_ufo = f"./ufo/{image_name}.ufo"
    output_ttf = f"./ttf/{image_name}.ttf"
    font_file = "./font/font.ttf"
    font_size = 12
    font_name = "My Font"

    # Create a new UFO font object
    font = UFOWriter(font_file)

    # Load the TrueType font file and create a font object
    ttf_font = ImageFont.truetype(font_file, font_size)

    # Iterate through all the PNG files in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".png"):
            # Extract the metadata from the filename
            unicode_value, width, lsb, rsb = filename[:-4].split("-")
            unicode_value = int(unicode_value, 16)
            width = int(width)
            lsb = int(lsb)
            rsb = int(rsb)

            # Load the PNG file
            image = Image.open(os.path.join(input_dir, filename))

            # Create a new glyph for the PNG file
            glyph_pen = TTGlyphPen(font)
            glyph_pen.moveTo((0, 0))
            glyph_pen.lineTo((width, 0))
            glyph_pen.lineTo((width, image.height))
            glyph_pen.lineTo((0, image.height))
            glyph_pen.closePath()
            glyph = glyph_pen.glyph()
            glyph.width = width
            glyph.leftMargin = lsb
            glyph.rightMargin = rsb
            glyph.font = font_name
            glyph.font_size = font_size

            # Add the glyph to the UFO font object
            font.newGlyph(hex(unicode_value)[2:].upper())
            font.glyphs[hex(unicode_value)[2:].upper()].fromTTGlyph(glyph)

    # Set the font name and other metadata in the TTF font object
    ttf_font_metadata = {"name": {"fontFamily": font_name}}
    ttf_font.set(**ttf_font_metadata)

    # Write the UFO file to disk
    font.writeToFile(output_ufo)

    # Create a new TTF font object from the UFO font object
    ttf_font = TTFont(output_ufo)

    # Write the TTF file to disk
    ttf_font.save(output_ttf)


def get_headlines(baselines_coord):
    min_x = min(coord[0] for coord in baselines_coord)
    max_x = max(coord[0] for coord in baselines_coord)
    headlines = {
        "top_left_x": min_x,
        "top_right_x": max_x
    }
    return headlines

def get_edges(image):
    if image.mode != 'L':
        image = image.convert('L')
    image_array = np.array(image)
    left_edge = None
    right_edge = None
    # Loop through each x value, then each y value to find the left edge
    for x in range(image_array.shape[1]):
            for y in range(image_array.shape[0]):
                if image_array[y, x] == 0:  # Assuming black is represented by 0
                    left_edge = x
                    break
            if left_edge is not None:
                break

    # Loop through each x value in reverse, then each y value to find the right edge
    for x in range(image_array.shape[1] - 1, -1, -1):
        for y in range(image_array.shape[0]):
            if image_array[y, x] == 0:  # Assuming black is represented by 0
                right_edge = x
                break
        if right_edge is not None:
            break
    return left_edge, right_edge

def get_image_output_path(image, image_name, output_path, headlines):
    image_width = image.width
    top_left_x = headlines["top_left_x"]
    top_right_x = headlines["top_right_x"]
    
    glyph_name = (image_name.split(".")[0]).split("_")[0]

    left_edge, right_edge = get_edges(image)
    if left_edge == None:
        return None
    # <Unicode>-<PNG width - margins>-<baseline start - left glyph edge>-<right glyph edge - baseline end>.png
    new_image_name = f"{glyph_name}_{int(image_width - (left_edge + right_edge))}_{int(top_left_x - left_edge)}_{int(top_right_x - right_edge)}.png"
    image_output_path = f"{output_path}/{new_image_name}"
    return image_output_path


def convert_outside_polygon_to_white(image_path, span, output_path):
    baselines_coord = None
    polygon_points = None
    for info in span:
        if info["label"] == "Base Line":
            baselines_coord = info["points"]
        if info["label"] == "Glyph":
            polygon_points = [(x, y) for x, y in info["points"]]
    if baselines_coord == None:
        return None
    elif polygon_points == None:
        return None
    image = Image.open(image_path)
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.polygon(polygon_points, fill=255)
    result_image = Image.new("RGB", image.size, (255, 255, 255))
    result_image.paste(image, mask=mask)
    headlines = get_headlines(baselines_coord)
    image_output_path = f"{output_path}/{image_path.split('/')[-1]}"
    # image_output_path = get_image_output_path(result_image, image_path.split("/")[-1], output_path, headlines)
    if image_output_path is not None:
        result_image.save(image_output_path)
        return image_output_path


def get_image_path(image_url):
    image_parts = (image_url.split("?")[0]).split("/")
    obj_key = "/".join(image_parts[4:])
    decoded_key = urllib.parse.unquote(obj_key)
    image_name = decoded_key.split("/")[-1]

    try:
        response = s3.get_object(Bucket=bucket_name, Key=decoded_key)
        image_data = response['Body'].read()
        with open(f"./downloaded_glyph/{image_name}", 'wb') as f:
            f.write(image_data)

    except Exception as e:
        print(f"Error while downloading {image_name} due to {e}")
    return f"./downloaded_glyph/{image_name}"


def find_glyph_bbox(image):
    # Convert the image to grayscale for simplicity (if needed)
    gray_image = image.convert('L')
    
    # Get the pixel data
    pixels = gray_image.load()
    
    width, height = image.size
    left, upper, right, lower = width, height, 0, 0
    
    for y in range(height):
        for x in range(width):
            if pixels[x, y] != 255:  # Non-white pixel (considering transparency)
                left = min(left, x)
                upper = min(upper, y)
                right = max(right, x)
                lower = max(lower, y)
    
    return left, upper, right + 1, lower + 1

def create_svg_with_glyph(png_path, output_svg_path):
    # Load the PNG image
    with Image.open(png_path) as img:
        # Get width and height from the PNG image
        width, height = img.size
        
        # Find the bounding box of the glyph
        left, upper, right, lower = find_glyph_bbox(img)

        # Convert the PNG data to Base64 encoding
        png_base64 = base64.b64encode(img.tobytes()).decode('utf-8')

        # Create an SVG document
        dwg = svgwrite.Drawing(output_svg_path, profile='tiny', size=(f'{width}px', f'{height}px'))

        # Create an image element using the Base64-encoded PNG data
        image = svgwrite.image.Image(href=f'data:image/png;base64,{png_base64}')
        image['x'] = f'{left}px'
        image['y'] = f'{upper}px'
        image['width'] = f'{right - left}px'
        image['height'] = f'{lower - upper}px'
        dwg.add(image)

        # Save the SVG file
        dwg.save()

def main():
    jsonl_paths = list(Path("./data/jsonl/").iterdir())
    for jsonl_path in jsonl_paths:
        with jsonlines.open(jsonl_path) as reader:
            for line in reader:
                if line["answer"] == "accept":             
                    image_span = line["spans"]
                    image_path = get_image_path(line["image"])
                    cleaned_image_path = convert_outside_polygon_to_white(image_path, image_span, Path(f"./cleaned_images"))
                    if cleaned_image_path is None:
                        logging.info(f"Skipping {image_path} ")
                        continue
                    filename = (cleaned_image_path.split("/")[-1]).split(".")[0]
                    output_path = Path(f"./svg/{filename}.svg")
                    png_to_svg(cleaned_image_path, output_path)


if __name__ == "__main__":
    jsonl_paths = list(Path("./data/jsonl/").iterdir())
    for jsonl_path in jsonl_paths:
        with jsonlines.open(jsonl_path) as reader:
            for line in reader:
                if line["id"].split("_")[0] != "ཨ":
                    continue
                if line["answer"] == "accept":             
                    image_span = line["spans"]
                    image_path = get_image_path(line["image"])
                    cleaned_image_path = convert_outside_polygon_to_white(image_path, image_span, Path(f"./cleaned_image"))
                    # if cleaned_image_path is None:
                    #     logging.info(f"Skipping {image_path} ")
                    #     continue
                    # filename = (cleaned_image_path.split("/")[-1]).split(".")[0]
                    # output_path = Path(f"./glyph_images/{filename}.svg")
                    # png_to_svg(cleaned_image_path, output_path)