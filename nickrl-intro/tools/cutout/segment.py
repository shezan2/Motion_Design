"""Segment Nick from his YouTube banner with rembg (BiRefNet) and save the raw matte."""
import sys, os, time
from pathlib import Path
from PIL import Image
import numpy as np
from rembg import new_session, remove

src = Path(sys.argv[1]); out = Path(sys.argv[2]); model = sys.argv[3]
out.mkdir(parents=True, exist_ok=True)
im = Image.open(src).convert("RGB")
# Nick's region in the 2560x1440 banner (plus margin); Rina starts on the right edge
box = (1400, 240, 2100, 1440)
crop = im.crop(box)
crop.save(out / "nick_src.png")
t0 = time.time()
sess = new_session(model)
mask = remove(crop, session=sess, only_mask=True)
mask.save(out / f"mask_{model}.png")
print(model, "done in", round(time.time() - t0, 1), "s", mask.size, flush=True)
