"""Final Nick cut-out: BiRefNet matte for edges, SAM's right boundary to remove Rina,
foreground colour estimation (pymatting) to kill the composite halo."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
from pymatting import estimate_foreground_ml

d = Path(sys.argv[1]); out = Path(sys.argv[2])
src = np.asarray(Image.open(d / "nick_src.png").convert("RGB")).astype(np.float64) / 255
bir = np.asarray(Image.open(d / "mask_birefnet-portrait.png").convert("L")).astype(np.float64) / 255
sam = np.asarray(Image.open(d / "mask_sam.png").convert("L")) > 127
H, W = bir.shape

lab, n = ndimage.label(sam)
sizes = ndimage.sum(sam, lab, range(1, n + 1))
nick = lab == (1 + int(np.argmax(sizes)))
nick = ndimage.binary_closing(nick, iterations=6)
nick = ndimage.binary_fill_holes(nick)

right = np.full(H, -1.0)
for y in range(H):
    xs = np.nonzero(nick[y])[0]
    if xs.size:
        right[y] = xs.max()
valid = right >= 0
ys = np.arange(H)
right = np.interp(ys, ys[valid], right[valid])
right = ndimage.median_filter(right, size=41, mode="nearest")
right = ndimage.uniform_filter1d(right, size=21, mode="nearest")

cut = np.zeros((H, W))
xx = np.arange(W)[None, :]
edge = right[:, None] + 2.0            # keep 2 px of SAM's edge
cut = np.clip((edge - xx) / 3.0 + 0.5, 0, 1)   # 3 px feather across the boundary
alpha = bir * cut
alpha[alpha < 0.02] = 0

fg = estimate_foreground_ml(src, alpha)
rgba = np.dstack([np.clip(fg, 0, 1), alpha])
img = Image.fromarray((rgba * 255 + 0.5).astype(np.uint8), "RGBA")
bbox = img.getbbox()
img = img.crop(bbox)
out.parent.mkdir(parents=True, exist_ok=True)
img.save(out)
print("saved", out, img.size, "bbox in crop", bbox)
np.save(d / "right_boundary.npy", right)
