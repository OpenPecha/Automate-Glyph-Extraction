import os

root_directory = '../data/batched_glyphs/derge'
output_file_path = '../data/found_glyphs_list/F1_found_glyphs_list.txt'
exclude_directories = ['.git'] 

def list_folders(root_dir, output_file, exclude_dirs=None):
    all_folders = []
    exclude_dirs = exclude_dirs or []  
    
    for subdir in os.listdir(root_dir):
        subdir_path = os.path.join(root_dir, subdir)
        if os.path.isdir(subdir_path) and subdir not in exclude_dirs:
            for folder in os.listdir(subdir_path):
                folder_path = os.path.join(subdir_path, folder)
                if os.path.isdir(folder_path) and folder not in exclude_dirs:
                    all_folders.append(folder)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_folders))




def main():
    list_folders(root_directory, output_file_path, exclude_dirs=exclude_directories)


