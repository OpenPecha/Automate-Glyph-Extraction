from pathlib import Path

if __name__ == "__main__":
    keys = []
    glyph_dirs = Path(f"./data/glyphs")
    for glyph_dir in glyph_dirs.iterdir():
        for image_path in glyph_dir.iterdir():
            image_key = image_path.name
            keys.append(image_key)
    Path(f"./derge_glyph_keys.txt").write_text("\n".join(keys))
