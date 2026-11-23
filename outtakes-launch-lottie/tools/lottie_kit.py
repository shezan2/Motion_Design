"""Tiny Lottie (Bodymovin JSON) authoring kit for the Outtakes launch film.

Writes plain Lottie that the official text-to-lottie player (Skia Skottie)
renders: shape / image / native-text / null layers, track mattes, gradients,
text slots, and keyframes eased with the skill's behaviour anchors
(skills/text-to-lottie/references/motion-taste.md).

Layers are added bottom-to-top with `add()`; `build()` reverses them into
Lottie order (index 0 = top), so a matte added right after its target ends up
directly above it, as Lottie requires.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import ImageFont

# --------------------------------------------------------------------------- easing
# Behaviour anchors from motion-taste.md (cubic-bezier x1, y1, x2, y2).
ANCHORS = {
    "entrance-sharp": (0.20, 0.75, 0.34, 0.94),
    "settle-soft": (0.00, 0.65, 0.51, 0.99),
    "kinetic-ui": (0.85, 0.46, 0.14, 0.53),
    "expressive-pop": (0.94, 0.75, 0.34, 0.94),
    "travel-balanced": (1.00, 0.49, 0.00, 0.55),
    "exit-accelerate": (1.00, 0.02, 0.54, 0.42),
    "travel-cut": (0.15, 0.85, 0.95, 0.05),
    "linear": (0.0, 0.0, 1.0, 1.0),
    # crash-in from oversize: most of the travel in the first frames, long tail
    "crash": (0.05, 0.70, 0.10, 1.00),
    # the website's smooth page scroll: eases in, long settle, rests on both ends (seamless cut)
    "scroll": (0.55, 0.00, 0.15, 1.00),
}


def _ease(name: str, dims: int):
    x1, y1, x2, y2 = ANCHORS[name]
    return {"x": [x1] * dims, "y": [y1] * dims}, {"x": [x2] * dims, "y": [y2] * dims}


def ease_value(name: str, t: float) -> float:
    """Progress (0..1) of an anchor curve at normalised time t."""
    x1, y1, x2, y2 = ANCHORS[name]
    lo, hi = 0.0, 1.0
    for _ in range(50):
        m = (lo + hi) / 2
        x = 3 * (1 - m) ** 2 * m * x1 + 3 * (1 - m) * m * m * x2 + m ** 3
        lo, hi = (m, hi) if x < t else (lo, m)
    m = (lo + hi) / 2
    return 3 * (1 - m) ** 2 * m * y1 + 3 * (1 - m) * m * m * y2 + m ** 3


def static(v):
    return {"a": 0, "k": v}


def anim(keys, dims: int | None = None):
    """keys: [(frame, value, ease_to_next), ...]; ease is an anchor name or 'hold'.

    Bodymovin convention: the segment k -> k+1 is described on keyframe k by
    its `o` (out handle) and `i` (in handle toward k+1).
    """
    keys = sorted(keys, key=lambda k: k[0])
    if len(keys) == 1:
        return static(keys[0][1])
    out = []
    for idx, key in enumerate(keys):
        t, v = key[0], key[1]
        ease = key[2] if len(key) > 2 else "settle-soft"
        val = v if isinstance(v, list) else [v]
        kf = {"t": t, "s": val}
        if idx < len(keys) - 1:
            if ease == "hold":
                kf["h"] = 1
            else:
                d = dims or len(val)
                o, i = _ease(ease, d)
                kf["o"], kf["i"] = o, i
        out.append(kf)
    return {"a": 1, "k": out}


def prop(v):
    """Pass-through for already-built props, else static."""
    if isinstance(v, dict) and "a" in v:
        return v
    return static(v)


# --------------------------------------------------------------------------- colors
def hexc(h: str, a: float = 1.0):
    h = h.lstrip("#")
    return [int(h[i : i + 2], 16) / 255 for i in (0, 2, 4)] + [a]


# --------------------------------------------------------------------------- shapes
def rect(w, h, x=0, y=0, r=0):
    return {"ty": "rc", "d": 1, "s": prop([w, h]), "p": prop([x, y]), "r": prop(r)}


def ellipse(w, h, x=0, y=0):
    return {"ty": "el", "d": 1, "s": prop([w, h]), "p": prop([x, y])}


def path(points, closed=False, ins=None, outs=None):
    n = len(points)
    return {
        "ty": "sh",
        "ks": static({"i": ins or [[0, 0]] * n, "o": outs or [[0, 0]] * n, "v": points, "c": closed}),
    }


def fill(color, opacity=100, sid=None):
    c = {"sid": sid} if sid else prop(color)
    return {"ty": "fl", "c": c, "o": prop(opacity), "r": 1}


def stroke(color, width, opacity=100, cap=2, join=2):
    return {"ty": "st", "c": prop(color), "o": prop(opacity), "w": prop(width), "lc": cap, "lj": join, "ml": 4}


def trim(start=0, end=100, offset=0):
    return {"ty": "tm", "s": prop(start), "e": prop(end), "o": prop(offset), "m": 1}


def gradient(stops, start, end, kind=1, alpha_stops=None):
    """stops: [(pos, '#rrggbb'), ...]; alpha_stops: [(pos, alpha 0..1), ...]."""
    k = []
    for pos, col in stops:
        r, g, b, _ = hexc(col)
        k += [pos, r, g, b]
    for pos, a in alpha_stops or []:
        k += [pos, a]
    gf = {"ty": "gf", "o": prop(100), "r": 1, "s": prop(start), "e": prop(end), "t": kind,
          "g": {"p": len(stops), "k": static(k)}}
    if kind == 2:
        gf["h"] = prop(0)
        gf["a"] = prop(0)
    return gf


def group(items, p=(0, 0), a=(0, 0), s=(100, 100), r=0, o=100, name="g"):
    tr = {"ty": "tr", "p": prop(list(p)) if not isinstance(p, dict) else p, "a": prop(list(a)),
          "s": prop(list(s)) if not isinstance(s, dict) else s, "r": prop(r), "o": prop(o)}
    return {"ty": "gr", "nm": name, "it": list(items) + [tr]}


# --------------------------------------------------------------------------- text
class Fonts:
    def __init__(self, folder: Path):
        self.folder = folder
        self.files = {
            "OT Display": "ot-display.ttf",
            "OT Wordmark": "ot-wordmark.ttf",
            "OT Body": "ot-body.ttf",
            "OT Body Medium": "ot-body-medium.ttf",
            "OT Label": "ot-label.ttf",
        }
        self._cache = {}

    def width(self, family: str, size: float, text: str, tracking: float = 0) -> float:
        key = (family, round(size * 4))
        if key not in self._cache:
            self._cache[key] = ImageFont.truetype(str(self.folder / self.files[family]), int(round(size * 4)))
        w = self._cache[key].getlength(text) / 4
        return w + tracking / 1000 * size * max(0, len(text) - 1)

    def fit(self, family, text_lines, max_w, max_size, min_size=24):
        size = max_size
        while size > min_size and max(self.width(family, size, t) for t in text_lines) > max_w:
            size -= 1
        return size


CAP = 0.686  # Archivo cap height / em


def text_doc(text, font, size, color, justify=2, tracking=0, lh=None):
    return {"s": size, "f": font, "t": text, "j": justify, "tr": tracking, "lh": lh or size * 1.12,
            "ls": 0, "fc": color[:3]}


# --------------------------------------------------------------------------- document
class Comp:
    def __init__(self, name, w, h, frames, fps=30):
        self.name, self.w, self.h, self.frames, self.fps = name, w, h, frames, fps
        self._layers = []  # bottom -> top
        self.assets = []
        self.fonts_used = set()
        self.slots = {}
        self.controls = []
        self._ind = 0
        self.cues = []  # (frame, kind, gain) for the sound-effects pass
        self.no_camera = set()  # layer inds that must stay locked to the frame (ground, seams)
        self.camera_ind = None
        self.has3d = False

    # ---- infrastructure
    def _next(self):
        self._ind += 1
        return self._ind

    def _base(self, ty, name, ks, ip=0, op=None, parent=None):
        layer = {"ddd": 0, "ind": self._next(), "ty": ty, "nm": name, "sr": 1, "ks": ks, "ao": 0,
                 "ip": ip, "op": self.frames if op is None else op, "st": 0, "bm": 0}
        if parent is not None:
            layer["parent"] = parent
        return layer

    def add(self, layer):
        self._layers.append(layer)
        return layer["ind"]

    def cue(self, frame, kind, gain=1.0):
        self.cues.append((frame, kind, gain))

    @staticmethod
    def ks(p=(0, 0), a=(0, 0), s=(100, 100), r=0, o=100):
        def vec3(v):
            if isinstance(v, dict):
                return v
            v = list(v)
            return static(v + [0] if len(v) == 2 else v)

        def sc(v):
            if isinstance(v, dict):
                return v
            v = list(v)
            return static(v + [100] if len(v) == 2 else v)

        return {"o": prop(o), "r": prop(r), "p": vec3(p), "a": vec3(a), "s": sc(s)}

    # ---- layers
    def null(self, name, p=(0, 0), a=(0, 0), s=(100, 100), r=0, o=100, ip=0, op=None, parent=None):
        """Transform-only layer. Opacity does NOT inherit through parenting in Lottie."""
        return self.add(self._base(3, name, self.ks(p=p, a=a, s=s, r=r, o=o), ip, op, parent))

    def shape(self, name, shapes, p=(0, 0), a=(0, 0), s=(100, 100), r=0, o=100, ip=0, op=None,
              parent=None, matte_for_next=False, matted=False, blend=0):
        layer = self._base(4, name, self.ks(p=p, a=a, s=s, r=r, o=o), ip, op, parent)
        layer["shapes"] = shapes
        if matte_for_next:
            layer["td"] = 1
        if matted:
            layer["tt"] = 1
        layer["bm"] = blend
        return self.add(layer)

    def _asset(self, file, w, h):
        for a in self.assets:
            if a["p"] == file:
                return a["id"]
        aid = f"img_{len(self.assets)}_{Path(file).stem}"
        self.assets.append({"id": aid, "w": w, "h": h, "u": "", "p": file, "e": 0})
        return aid

    def image(self, name, file, w, h, p=(0, 0), s=(100, 100), r=0, o=100, ip=0, op=None,
              parent=None, matted=False, blend=0, a=None):
        aid = self._asset(file, w, h)
        layer = self._base(2, name, self.ks(p=p, a=a if a is not None else (w / 2, h / 2), s=s, r=r, o=o), ip, op,
                           parent)
        layer["refId"] = aid
        if matted:
            layer["tt"] = 1
        layer["bm"] = blend
        return self.add(layer)

    def text(self, name, doc, p=(0, 0), s=(100, 100), r=0, o=100, ip=0, op=None, parent=None,
             matted=False, slot=None, label=None, keyed_docs=None, a=(0, 0), animators=None):
        """Native text layer. `doc` from text_doc(); `slot` makes it editable in the player."""
        self.fonts_used.add(doc["f"])
        layer = self._base(5, name, self.ks(p=p, a=a, s=s, r=r, o=o), ip, op, parent)
        if keyed_docs:  # [(frame, doc), ...] hold-keyed text documents (typing etc.)
            k = [{"s": d, "t": t} for t, d in keyed_docs]
        else:
            k = [{"s": doc, "t": 0}]
        layer["t"] = {"d": {"k": k}, "p": {}, "m": {"g": 1, "a": static([0, 0])}, "a": []}
        if animators:
            layer["t"]["a"] = animators
        if slot:
            layer["t"]["d"]["sid"] = slot
            self.slots[slot] = {"p": {"a": 1, "k": [{"t": 0, "s": json.loads(json.dumps(doc))}]}}
            self.controls.append({"sid": slot, "label": label or slot})
        if matted:
            layer["tt"] = 1
        return self.add(layer)

    def color_slot(self, sid, color, label):
        self.slots[sid] = {"p": {"a": 0, "k": color}}
        self.controls.append({"sid": sid, "label": label})

    # ---- 3D (Skottie draws 3D layers in LAYER ORDER, not by depth: add far layers first)
    @staticmethod
    def ks3(p=(0, 0, 0), a=(0, 0, 0), s=(100, 100, 100), rx=0, ry=0, rz=0, o=100):
        def v3(v):
            return v if isinstance(v, dict) else static(list(v))
        return {"o": prop(o), "rx": prop(rx), "ry": prop(ry), "rz": prop(rz), "or": static([0, 0, 0]),
                "p": v3(p), "a": v3(a), "s": v3(s)}

    def camera3d(self, zoom=1400, p=None, poi=None):
        """One-node camera looking straight down -Z: z=0 layers render 1:1 with 2D layers."""
        self.has3d = True
        cx, cy = self.w / 2, self.h / 2
        layer = {"ddd": 1, "ind": self._next(), "ty": 13, "nm": "3D camera", "sr": 1, "ao": 0, "ip": 0,
                 "op": self.frames, "st": 0, "pe": static(zoom),
                 "ks": {"p": p or static([cx, cy, -zoom]), "a": poi or static([cx, cy, 0]), "or": static([0, 0, 0]),
                        "rx": static(0), "ry": static(0), "rz": static(0), "o": static(100)}}
        self._layers.append(layer)
        self.no_camera.add(layer["ind"])
        return layer["ind"]

    def _3d(self, layer):
        self.has3d = True
        layer["ddd"] = 1
        self.no_camera.add(layer["ind"])
        return layer

    def null3d(self, name, ks, ip=0, op=None, parent=None):
        layer = self._3d(self._base(3, name, ks, ip, op, parent))
        return self.add(layer)

    def shape3d(self, name, shapes, ks, ip=0, op=None, parent=None):
        layer = self._3d(self._base(4, name, ks, ip, op, parent))
        layer["shapes"] = shapes
        return self.add(layer)

    def image3d(self, name, file, w, h, ks, ip=0, op=None, parent=None):
        aid = self._asset(file, w, h)
        layer = self._3d(self._base(2, name, ks, ip, op, parent))
        layer["refId"] = aid
        return self.add(layer)

    def text3d(self, name, doc, ks, ip=0, op=None, parent=None):
        self.fonts_used.add(doc["f"])
        layer = self._3d(self._base(5, name, ks, ip, op, parent))
        layer["t"] = {"d": {"k": [{"s": doc, "t": 0}]}, "p": {}, "m": {"g": 1, "a": static([0, 0])}, "a": []}
        return self.add(layer)

    def camera(self, p, a, s):
        """One dominant, slow camera move for the whole scene (recipe-camera-scene-motion)."""
        self.camera_ind = self.null("camera", p=p, a=a, s=s)
        return self.camera_ind

    # ---- output
    def build(self, fonts: Fonts):
        if self.camera_ind is not None:
            for lyr in self._layers:
                if lyr["ind"] in self.no_camera or lyr["ind"] == self.camera_ind or "parent" in lyr:
                    continue
                lyr["parent"] = self.camera_ind
        layers = list(reversed(self._layers))
        doc = {
            "v": "5.7.0", "fr": self.fps, "ip": 0, "op": self.frames, "w": self.w, "h": self.h,
            "nm": self.name, "ddd": 1 if self.has3d else 0, "assets": self.assets, "layers": layers,
            "fonts": {"list": [
                {"fName": f, "fFamily": f, "fStyle": "Regular", "ascent": 75} for f in sorted(self.fonts_used)
            ]},
        }
        if self.slots:
            doc["slots"] = self.slots
        return doc


def letter_reveal(start, end, ghost=14, ease="linear"):
    """Text animator: characters switch from `ghost` opacity to full, one after another
    (the website's letter-by-letter opacity load). Range selector based on characters,
    square shape, its start sweeping 0 -> 100 %; characters inside the range are ghosted."""
    return [{"nm": "letter reveal",
             "s": {"t": 0, "xe": static(0), "ne": static(0), "a": static(100), "b": 1, "rn": 0, "sh": 1,
                   "s": anim([(start, [0], ease), (end, [100])]), "e": static(100), "o": static(0), "r": 1},
             "a": {"o": static(ghost)}}]
