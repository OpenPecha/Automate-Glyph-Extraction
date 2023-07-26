from pathlib import Path
import yaml
from openpecha.utils import load_yaml, dump_yaml

def get_images_path(top, bottom):
    interleaved_list = []
    min_len = min(len(top), len(bottom))

    for i in range(min_len):
        interleaved_list.append(top[i])
        interleaved_list.append(bottom[i])

    # Append any remaining elements from the longer list
    interleaved_list.extend(top[min_len:])
    interleaved_list.extend(bottom[min_len:])

    return interleaved_list

def get_image_paths_order(images_yml):
    final_images_path = []
    assending_order = sorted(images_yml.keys())
    descending_order = sorted(images_yml.keys(), reverse=True)
    for num in range(int((len(assending_order))/2)):
        top = images_yml[assending_order[num]]
        bottom = images_yml[descending_order[num]]
        images_path = get_images_path(top, bottom)
        final_images_path.extend(images_path)
    return final_images_path

if __name__ == "__main__":
    images_yml = load_yaml(Path("./data/tengyur_pecing_images_info.yml"))
    image_paths = get_image_paths_order(images_yml)
    dump_yaml(image_paths, Path("./data/sorted_images.yml"))