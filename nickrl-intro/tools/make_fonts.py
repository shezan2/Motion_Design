"""Cut static, uniquely named TTF instances for Skottie (it can't pick weights inside a family).

Sources: @fontsource/montserrat 5.3.0 and @fontsource/cormorant-garamond 5.3.0 (both SIL OFL 1.1),
latin subset woff2 files. Each output gets its own family name so Lottie `fonts.list[].fFamily`
can address it directly.

  python tools/make_fonts.py <fontsource_npm_dir> brand/fonts
"""
import sys
from pathlib import Path
from fontTools.ttLib import TTFont

SRC = Path(sys.argv[1])
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

INSTANCES = [
    # family name,          output file,             source package,                 source file
    ("NK Sans Light",       "nk-sans-light.ttf",     "_fontsource_montserrat",       "montserrat-latin-300-normal.woff2"),
    ("NK Sans",             "nk-sans.ttf",           "_fontsource_montserrat",       "montserrat-latin-500-normal.woff2"),
    ("NK Sans Semi",        "nk-sans-semi.ttf",      "_fontsource_montserrat",       "montserrat-latin-600-normal.woff2"),
    ("NK Serif",            "nk-serif.ttf",          "_fontsource_cormorant-garamond", "cormorant-garamond-latin-600-normal.woff2"),
    ("NK Serif Italic",     "nk-serif-italic.ttf",   "_fontsource_cormorant-garamond", "cormorant-garamond-latin-600-italic.woff2"),
]


def rename(font: TTFont, family: str):
    name = font["name"]
    for rec in list(name.names):
        if rec.nameID in (1, 2, 4, 6, 16, 17, 21, 22, 25):
            name.removeNames(nameID=rec.nameID)
    ps = family.replace(" ", "")
    for nid, val in ((1, family), (2, "Regular"), (4, family), (6, ps + "-Regular"), (16, family), (17, "Regular")):
        name.setName(val, nid, 3, 1, 0x409)
        name.setName(val, nid, 1, 0, 0)
    if "STAT" in font:
        del font["STAT"]
    # Regular style bits so Skia matches fStyle "Regular"
    font["OS/2"].fsSelection = (font["OS/2"].fsSelection & ~0b1100001) | 0b1000000
    font["head"].macStyle = 0


for family, fname, pkg, src in INSTANCES:
    f = TTFont(SRC / pkg / "package" / "files" / src)
    f.flavor = None
    rename(f, family)
    f.save(OUT / fname)
    print("wrote", fname, "->", family)
