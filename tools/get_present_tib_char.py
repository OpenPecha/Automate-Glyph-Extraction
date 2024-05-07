import os

directory_path = "../data/font_data/derge_font/svg"

files_list = os.listdir(directory_path)

tibetan_names = [file.split('_')[0] for file in files_list]

output_file_path = "../data/font_data/required_list/derge/present_derge_list.txt"

with open(output_file_path, 'w', encoding='utf-8') as f:
    for name in tibetan_names:
        f.write(name + '\n')

print(f'List saved to {output_file_path}')
