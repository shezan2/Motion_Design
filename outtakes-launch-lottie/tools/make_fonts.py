"""Cut static Archivo instances (Skottie can't select variable-font axes).

Each instance gets its own family name so Lottie `fonts.list[].fFamily` can
address it directly.
"""
import sys
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

SRC = Path(sys.argv[1])  # folder with archivo-latin-standard-{normal,italic}.woff2
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

INSTANCES = [
    # family name,            file,                    italic?, wdth, wght
    ("OT Display",            "ot-display.ttf",        False, 125, 800),  # site headlines (Archivo Expanded ExtraBold)
    ("OT Wordmark",           "ot-wordmark.ttf",       True,  62,  900),  # OUTTAKES logo style (condensed black italic)
    ("OT Body",               "ot-body.ttf",           False, 100, 420),  # body / UI
    ("OT Body Medium",        "ot-body-medium.ttf",    False, 100, 560),  # buttons, names
    ("OT Label",              "ot-label.ttf",          True,  100, 400),  # italic section labels
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

for family, fname, italic, wdth, wght in INSTANCES:
    src = SRC / ("archivo-latin-standard-italic.woff2" if italic else "archivo-latin-standard-normal.woff2")
    f = TTFont(src)
    f.flavor = None
    inst = instantiateVariableFont(f, {"wdth": wdth, "wght": wght}, inplace=False, updateFontNames=False)
    rename(inst, family)
    inst.save(OUT / fname)
    print("wrote", fname, family)
