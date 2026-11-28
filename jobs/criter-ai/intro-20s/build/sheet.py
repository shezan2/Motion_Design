#!/usr/bin/env python3
"""Contact sheet of stills: python3 sheet.py <dir> <out.jpg> [cols] [tile_width]"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

src = Path(sys.argv[1]); out = sys.argv[2]
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 4
tw = int(sys.argv[4]) if len(sys.argv) > 4 else 480
files = sorted(src.glob('*.png'))
if not files:
    sys.exit('no stills')
first = Image.open(files[0]); th = round(tw * first.height / first.width)
rows = (len(files) + cols - 1) // cols
sheet = Image.new('RGB', (cols * tw + (cols + 1) * 6, rows * (th + 26) + 6), (40, 40, 40))
d = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
except OSError:
    font = ImageFont.load_default()
for i, f in enumerate(files):
    im = Image.open(f).convert('RGB').resize((tw, th), Image.LANCZOS)
    x = 6 + (i % cols) * (tw + 6); y = 6 + (i // cols) * (th + 26)
    sheet.paste(im, (x, y + 20))
    d.text((x + 2, y + 1), f.stem, fill=(230, 230, 230), font=font)
sheet.save(out, quality=88)
print(out, sheet.size)
