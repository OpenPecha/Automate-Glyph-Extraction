from pathlib import Path
from collections import OrderedDict



def remove_duplicates(file_path):
    with open(file_path, 'r') as file:
        glyphs = file.readlines()
    unique_glyphs = list(OrderedDict.fromkeys(glyphs))
    
    # Write the unique glyphs back to the file
    with open(file_path, 'w') as file:
        file.writelines(unique_glyphs)

if __name__ == '__main__':
    remove_duplicates(Path("./data/tibetan_list.txt"))
