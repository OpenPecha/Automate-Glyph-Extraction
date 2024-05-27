import os


def list_folders_in_directory(directory_path):
    if not os.path.exists(directory_path):
        print(f"dir '{directory_path}' does not exist.")
        return []

    folders_list = [folder for folder in os.listdir(
        directory_path) if os.path.isdir(os.path.join(directory_path, folder))]

    return folders_list


dir_path = "D:/Works/images/F50000"
folders_list = list_folders_in_directory(dir_path)
print(f"folder name: {folders_list}")
