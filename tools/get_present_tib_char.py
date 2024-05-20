import os

directory_path = "../data/font_data/pecing_font/svg"

files_list = os.listdir(directory_path)

tibetan_names = [file.split('_')[0] for file in files_list]

output_file_path = "../data/present_list/pecing_present_list.txt"

with open(output_file_path, 'w', encoding='utf-8') as f:
    for name in tibetan_names:
        f.write(name + '\n')

print(f'List saved to {output_file_path}')
