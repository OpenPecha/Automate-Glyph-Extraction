def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read().splitlines()

def write_to_file(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in content:
            f.write("%s\n" % item)

def main():
    essential_chars_file = '../data/Tibetan_Essential_Glyphs.txt'  
    present_chars_file = '../data/font_data/required_list/derge/present_derge_list.txt'
    output_file = '../data/font_data/required_list/derge/missing_derge_glyphs'  

    essential_chars = set(read_file(essential_chars_file))
    present_chars = set(read_file(present_chars_file))

    missing_chars = essential_chars - present_chars

    write_to_file(output_file, missing_chars)
    print(f'missing characters saved at {output_file}')

if __name__ == "__main__":
    main()
