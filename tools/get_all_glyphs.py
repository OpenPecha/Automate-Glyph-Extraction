from pathlib import Path


def main():
    glyphs = []
    glyph_dirs = (Path(f"./data/glyphs/").iterdir())
    for glyph_dir in glyph_dirs:
        if len(list(glyph_dir.iterdir())) == 100:
            glyphs.append(glyph_dir.name)
    Path(f"./data/glyphs_100.txt").write_text("\n".join(glyphs), encoding='utf-8')



if __name__ == "__main__":
    main()