"""Instance mask of Nick (not Rina) with rembg's SAM session and point prompts."""
import sys, time
from pathlib import Path
from PIL import Image
from rembg import new_session, remove

d = Path(sys.argv[1])
src = Image.open(d / "nick_src.png").convert("RGB")   # 700 x 1200 crop of the banner
pos = [(300, 160), (300, 330), (250, 520), (330, 700), (200, 900), (450, 900), (520, 600), (560, 470)]
neg = [(660, 300), (680, 560), (660, 800), (650, 1000), (690, 1150), (60, 200), (40, 700)]
prompt = [{"type": "point", "data": list(p), "label": 1} for p in pos] + \
         [{"type": "point", "data": list(p), "label": 0} for p in neg]
t0 = time.time()
sess = new_session("sam")
m = remove(src, session=sess, only_mask=True, sam_prompt=prompt)
m.save(d / "mask_sam.png")
print("sam done", round(time.time() - t0, 1), "s", m.size, m.mode)
