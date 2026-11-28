"""Parts for the Nick R.L. intro film, on top of lottie_kit (Outtakes toolkit).

Adds what the film needs and the kit lacks: the Ozen craft eases as cubic-beziers, Skottie
effects (Gaussian blur, drop shadow), SVG path -> Lottie path conversion (Tabler icons),
path sampling (carrier positions), blur-in type, an odometer counter, glows, the cursor.
Frames are at 30 fps; positions are in comp pixels (1920 x 1080).
"""
from __future__ import annotations

import math
from pathlib import Path

from svgelements import Arc, Close, CubicBezier, Line, Move, Path as SvgPath, QuadraticBezier

import lottie_kit as lk
from lottie_kit import Comp, anim, hexc, static, text_doc

# --------------------------------------------------------------------------- eases (craft.md section 3)
lk.ANCHORS.update({
    "cruise": (0.0, 0.0, 1.0, 1.0),
    "glide": (0.40, 0.67, 0.76, 1.00),
    "softInOut": (0.35, 0.06, 0.65, 0.94),
    "softLand": (0.28, 1.00, 0.72, 0.93),
    "snapSettle": (0.14, 1.00, 0.24, 0.95),
    "whip": (0.28, 0.67, 0.50, 1.00),
    "gentleIn": (0.58, 0.00, 0.96, 0.95),
    "accelExit": (0.40, 0.00, 0.67, 0.16),
    "crashOut": (0.56, 0.00, 0.71, 0.00),
    "popOver": (0.29, 0.12, 0.29, 1.41),
})
ease = lk.ease_value

W, H, FPS = 1920, 1080, 30

# --------------------------------------------------------------------------- palette (brand sheet in PLAN.md)
C = {
    "bg_deep": "#050B16",
    "bg": "#0A1628",
    "bg_lift": "#15305A",
    "track": "#1A2A44",
    "grey": "#8494AE",
    "muted": "#8494AE",
    "ink": "#F3EFE7",
    "gold": "#E9B44C",
    "gold_light": "#F7D58E",
    "gold_deep": "#B9852F",
    "card_top": "#13284A",
    "card_bot": "#0B1A31",
    "cold_glow": "#2B4A73",
    "navy_text": "#0A1628",
    "dim_digit": "#2E4262",
}


def col(name, a=1.0):
    return hexc(C[name], a)


# --------------------------------------------------------------------------- effects (Skottie renders both)
def gblur(blurriness, dims=1):
    """Gaussian Blur. blurriness: number or anim(); dims 1 = both, 2 = horizontal, 3 = vertical."""
    v = blurriness if isinstance(blurriness, dict) else static(blurriness)
    return {"ty": 29, "nm": "Gaussian Blur", "np": 5, "mn": "ADBE Gaussian Blur 2", "ix": 1, "en": 1, "ef": [
        {"ty": 0, "nm": "Blurriness", "mn": "ADBE Gaussian Blur 2-0001", "ix": 1, "v": v},
        {"ty": 7, "nm": "Blur Dimensions", "mn": "ADBE Gaussian Blur 2-0002", "ix": 2, "v": static(dims)},
        {"ty": 7, "nm": "Repeat Edge Pixels", "mn": "ADBE Gaussian Blur 2-0003", "ix": 3, "v": static(0)},
    ]}


def drop_shadow(color="#000000", opacity=0.5, direction=180, distance=20, softness=60):
    r, g, b, _ = hexc(color)
    return {"ty": 25, "nm": "Drop Shadow", "np": 8, "mn": "ADBE Drop Shadow", "ix": 2, "en": 1, "ef": [
        {"ty": 2, "nm": "Shadow Color", "mn": "ADBE Drop Shadow-0001", "ix": 1, "v": static([r, g, b, 1])},
        {"ty": 0, "nm": "Opacity", "mn": "ADBE Drop Shadow-0002", "ix": 2,
         "v": opacity if isinstance(opacity, dict) else static(opacity * 255)},
        {"ty": 0, "nm": "Direction", "mn": "ADBE Drop Shadow-0003", "ix": 3, "v": static(direction)},
        {"ty": 0, "nm": "Distance", "mn": "ADBE Drop Shadow-0004", "ix": 4, "v": static(distance)},
        {"ty": 0, "nm": "Softness", "mn": "ADBE Drop Shadow-0005", "ix": 5, "v": static(softness)},
        {"ty": 7, "nm": "Shadow Only", "mn": "ADBE Drop Shadow-0006", "ix": 6, "v": static(0)},
    ]}


def with_fx(c: Comp, ind, *effects):
    for lyr in c._layers:
        if lyr["ind"] == ind:
            lyr.setdefault("ef", []).extend(effects)
            return ind
    raise KeyError(ind)


def layer(c: Comp, ind):
    for lyr in c._layers:
        if lyr["ind"] == ind:
            return lyr
    raise KeyError(ind)


# --------------------------------------------------------------------------- paths
def shape_from_points(pts, closed):
    """pts: [(v, in_rel, out_rel), ...] -> Lottie bezier shape dict."""
    return {"i": [list(p[1]) for p in pts], "o": [list(p[2]) for p in pts],
            "v": [list(p[0]) for p in pts], "c": closed}


def svg_subpaths(d, tx=lambda x, y: (x, y)):
    """Parse an SVG path into Lottie bezier shapes (one per subpath). Arcs -> cubics.
    tx maps SVG coords to comp coords (must be affine so tangents map too)."""
    path = SvgPath(d)
    subs, cur, closed = [], [], False
    start = None

    def flush():
        nonlocal cur, closed
        if cur:
            subs.append((cur, closed))
        cur, closed = [], False

    def add_cubic(p0, c1, c2, p3):
        P0, C1, C2, P3 = (tx(p.x, p.y) for p in (p0, c1, c2, p3))
        if not cur:
            cur.append([P0, (0, 0), (0, 0)])
        cur[-1][2] = (C1[0] - P0[0], C1[1] - P0[1])
        cur.append([P3, (C2[0] - P3[0], C2[1] - P3[1]), (0, 0)])

    for seg in path:
        if isinstance(seg, Move):
            flush()
            start = seg.end
            cur = [[tx(seg.end.x, seg.end.y), (0, 0), (0, 0)]]
        elif isinstance(seg, Close):
            if cur and start is not None:
                v0 = cur[0][0]
                vl = cur[-1][0]
                if abs(v0[0] - vl[0]) < 1e-6 and abs(v0[1] - vl[1]) < 1e-6 and len(cur) > 1:
                    cur[0][1] = cur[-1][1]
                    cur.pop()
            closed = True
            flush()
        elif isinstance(seg, Line):
            if (seg.start - seg.end).__abs__() < 1e-9:
                continue
            add_cubic(seg.start, seg.start, seg.end, seg.end)
        elif isinstance(seg, CubicBezier):
            add_cubic(seg.start, seg.control1, seg.control2, seg.end)
        elif isinstance(seg, QuadraticBezier):
            p0, q, p2 = seg.start, seg.control, seg.end
            c1 = p0 + (q - p0) * (2 / 3)
            c2 = p2 + (q - p2) * (2 / 3)
            add_cubic(p0, c1, c2, p2)
        elif isinstance(seg, Arc):
            for cb in seg.as_cubic_curves():
                add_cubic(cb.start, cb.control1, cb.control2, cb.end)
    flush()
    return [shape_from_points(pts, cl) for pts, cl in subs]


def icon_tx(cx, cy, scale):
    """Tabler 24-unit grid centred on (cx, cy)."""
    return lambda x, y: (cx + (x - 12) * scale, cy + (y - 12) * scale)


def read_icon(file):
    import re
    txt = Path(file).read_text()
    return [d for d in re.findall(r'<path[^>]*\sd="([^"]+)"', txt) if not d.startswith("M0 0h24v24H0z")]


def circle_shape(cx, cy, r, start_top=True):
    """Closed circle starting at 12 o'clock, clockwise on screen."""
    k = 0.5523 * r
    pts = [((cx, cy - r), (-k, 0), (k, 0)), ((cx + r, cy), (0, -k), (0, k)),
           ((cx, cy + r), (k, 0), (-k, 0)), ((cx - r, cy), (0, k), (0, -k))]
    return shape_from_points(pts, True)


def sh(shape):
    return {"ty": "sh", "ks": static(shape)}


def sh_anim(keys):
    """keys: [(frame, shape, ease), ...] -> animated path."""
    return {"ty": "sh", "ks": anim([(t, [s], e) for t, s, e in keys])}


# --------------------------------------------------------------------------- bezier sampling (for carriers)
def _cubic_pt(p0, c1, c2, p3, t):
    u = 1 - t
    return (u ** 3 * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t ** 3 * p3[0],
            u ** 3 * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t ** 3 * p3[1])


def shape_polyline(shape, steps=32):
    v, i, o, closed = shape["v"], shape["i"], shape["o"], shape["c"]
    n = len(v)
    segs = list(range(n - 1)) + ([n - 1] if closed else [])
    pts = []
    for s in segs:
        a, b = s, (s + 1) % n
        p0 = v[a]; c1 = (v[a][0] + o[a][0], v[a][1] + o[a][1])
        c2 = (v[b][0] + i[b][0], v[b][1] + i[b][1]); p3 = v[b]
        for k in range(steps):
            pts.append(_cubic_pt(p0, c1, c2, p3, k / steps))
    pts.append(v[0] if closed else v[-1])
    return pts


def point_at(polyline, frac):
    d = [0.0]
    for a, b in zip(polyline, polyline[1:]):
        d.append(d[-1] + math.dist(a, b))
    target = frac * d[-1]
    for k in range(1, len(d)):
        if d[k] >= target:
            seg = d[k] - d[k - 1] or 1
            t = (target - d[k - 1]) / seg
            a, b = polyline[k - 1], polyline[k]
            return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    return polyline[-1]


# --------------------------------------------------------------------------- simple layers
def ground(c: Comp):
    """Deep navy radial ground, locked to the frame (no camera)."""
    g = lk.gradient([(0, C["bg_lift"]), (0.55, C["bg"]), (1, C["bg_deep"])], [W / 2, H * 0.46], [W * 0.62, H * 1.05], kind=2)
    ind = c.shape("ground", [lk.group([lk.rect(W * 1.4, H * 1.4, W / 2, H / 2), g])])
    c.no_camera.add(ind)
    return ind


def vignette(c: Comp, strength=0.55, o=100):
    """Radial darkening that reaches full strength only in the frame corners."""
    g = lk.gradient([(0, "#000000"), (1, "#000000")], [W / 2, H / 2], [W, H], kind=2,
                    alpha_stops=[(0, 0.0), (0.58, 0.0), (1, strength)])
    ind = c.shape("vignette", [lk.group([lk.rect(W * 1.6, H * 1.6, W / 2, H / 2), g])], o=o)
    c.no_camera.add(ind)
    return ind


def glow(c: Comp, name, cx, cy, radius, color, peak_alpha, o=100, ip=0, op=None, parent=None, sy=1.0, p=None):
    g = lk.gradient([(0, color), (1, color)], [0, 0], [radius, 0], kind=2,
                    alpha_stops=[(0, peak_alpha), (0.45, peak_alpha * 0.42), (1, 0.0)])
    return c.shape(name, [lk.group([lk.ellipse(radius * 2, radius * 2), g], s=(100, 100 * sy))],
                   p=p if p is not None else (cx, cy), o=o, ip=ip, op=op, parent=parent)


# --------------------------------------------------------------------------- type
FONTS_DIR = Path(__file__).resolve().parent.parent / "brand" / "fonts"
fonts = lk.Fonts(FONTS_DIR)


def tdoc(text, font, size, color, justify=2, tracking=0):
    return text_doc(text, font, size, hexc(color) if isinstance(color, str) else color, justify=justify, tracking=tracking)


def blur_word(c: Comp, name, text, font, size, color, x, y, t_in, justify=2, rise=26, blur=14, dur=12,
              t_out=None, out_dy=-30, out_dur=8, out_blur=12, parent=None, tracking=0, ease_in="softLand",
              op=None, o=100):
    """Blur-in word build (move 1): resolves from blur while rising; exits up with blur, accelerating."""
    keys_p = [(t_in, [x, y + rise], ease_in), (t_in + dur, [x, y], "hold")]
    keys_o = [(t_in, 0, "cruise"), (t_in + max(4, dur // 2), o, "hold")]
    keys_b = [(t_in, blur, "glide"), (t_in + max(5, int(dur * 0.65)), 0, "hold")]
    if t_out is not None:
        keys_p[-1] = (t_out, [x, y], "accelExit")
        keys_p.append((t_out + out_dur, [x, y + out_dy], "hold"))
        keys_o.append((t_out, o, "gentleIn"))
        keys_o.append((t_out + out_dur, 0, "hold"))
        keys_b[-1] = (t_out, 0, "gentleIn")
        keys_b.append((t_out + out_dur, out_blur, "hold"))
    ind = c.text(name, tdoc(text, font, size, color, justify, tracking), p=anim(keys_p), o=anim(keys_o),
                 ip=max(0, t_in - 1), op=op if op is not None else ((t_out + out_dur + 1) if t_out is not None else None),
                 parent=parent)
    with_fx(c, ind, gblur(anim(keys_b)))
    return ind


# --------------------------------------------------------------------------- cursor (moves.md 25, craft.md 10)
def cursor_shape():
    """Arrow pointer, tip at (0, 0), about 46 px tall at 100 %."""
    pts = [(0, 0), (0, 40), (10, 31), (17, 46), (24, 43), (17, 28.5), (30, 28.5)]
    return shape_from_points([(p, (0, 0), (0, 0)) for p in pts], True)
