"""v4 parts: the redesigned Outtakes site (Nov 2026) as a motion design system.

Ground is the site's cool light grey with black condensed-italic statements; dark sections and the film-strip
band for contrast; one neon green for actions; orange only inside the photographer Studio. Product UI is built
as 3D planes (a Lottie camera + ddd layers) so it can be presented with real perspective and soft shadows, and a
custom cursor drives the interactions.
"""
from __future__ import annotations

import math

import film_parts as fp
from lottie_kit import (CAP, Comp, anim, ease_value, ellipse, gradient, group, hexc, path, rect, static, stroke,
                        text_doc, trim)

W, H, LANDSCAPE = fp.W, fp.H, fp.LANDSCAPE

C = {
    "light": "#e5e9ec", "panel": "#d8dde1", "card": "#f4f6f7", "ink": "#121214", "grey": "#7f8488",
    "pill": "#b6babd", "line": "#c5cacd", "green": "#4bff2c", "gtext": "#1f9e10", "strip": "#2b2b2e",
    "orange": "#f77128", "white": "#ffffff", "dark": "#121214", "mute": "#a8adb1",
}


def col(x, a=1.0):
    if isinstance(x, list):
        return x
    return hexc(C.get(x, x), a)


def fl(color, opacity=100):
    cc = col(color)
    return {"ty": "fl", "c": {"a": 0, "k": cc[:3] + [1]}, "o": {"a": 0, "k": opacity}, "r": 1}


def fl_anim(keys):
    """Animated fill colour: keys [(frame, colour, ease), ...]."""
    return {"ty": "fl", "c": anim([(k[0], col(k[1])[:3] + [1]) + tuple(k[2:]) for k in keys]), "o": static(100), "r": 1}


def st(color, width, opacity=100):
    cc = col(color)
    return {"ty": "st", "c": {"a": 0, "k": cc[:3] + [1]}, "o": {"a": 0, "k": opacity}, "w": {"a": 0, "k": width},
            "lc": 2, "lj": 2}


# --------------------------------------------------------------------------- effects (Skottie supports these)
def drop_shadow(opacity=60, distance=28, softness=110, direction=180, color="#0b1a24"):
    v = lambda k: {"a": 0, "k": k}
    return {"ty": 25, "nm": "Drop Shadow", "np": 8, "mn": "ADBE Drop Shadow", "ix": 1, "en": 1, "ef": [
        {"ty": 2, "nm": "Shadow Color", "mn": "ADBE Drop Shadow-0001", "ix": 1, "v": v(col(color))},
        {"ty": 0, "nm": "Opacity", "mn": "ADBE Drop Shadow-0002", "ix": 2, "v": v(opacity)},
        {"ty": 0, "nm": "Direction", "mn": "ADBE Drop Shadow-0003", "ix": 3, "v": v(direction)},
        {"ty": 0, "nm": "Distance", "mn": "ADBE Drop Shadow-0004", "ix": 4, "v": v(distance)},
        {"ty": 0, "nm": "Softness", "mn": "ADBE Drop Shadow-0005", "ix": 5, "v": v(softness)},
        {"ty": 7, "nm": "Shadow Only", "mn": "ADBE Drop Shadow-0006", "ix": 6, "v": v(0)}]}


def gblur(amount):
    """Gaussian blur; `amount` is a number or an anim() of [value] keys."""
    v = amount if isinstance(amount, dict) else {"a": 0, "k": amount}
    return {"ty": 29, "nm": "Gaussian Blur", "np": 5, "mn": "ADBE Gaussian Blur 2", "ix": 2, "en": 1, "ef": [
        {"ty": 0, "nm": "Blurriness", "mn": "ADBE Gaussian Blur 2-0001", "ix": 1, "v": v},
        {"ty": 7, "nm": "Blur Dimensions", "mn": "ADBE Gaussian Blur 2-0002", "ix": 2, "v": {"a": 0, "k": 1}},
        {"ty": 7, "nm": "Repeat Edge Pixels", "mn": "ADBE Gaussian Blur 2-0003", "ix": 3, "v": {"a": 0, "k": 1}}]}


def last(c):
    return c._layers[-1]


def with_fx(c, ind, *effects):
    for lyr in c._layers:
        if lyr["ind"] == ind:
            lyr["ef"] = list(lyr.get("ef", [])) + list(effects)
            return lyr
    raise KeyError(ind)


# --------------------------------------------------------------------------- ground
def ground(c, color="light", label="Background"):
    c.color_slot("bgColor", col(color), label)
    ind = c.shape("background", [group([rect(W, H, W / 2, H / 2), {**fl(color), "sid": "bgColor"}])])
    c.no_camera.add(ind)
    return ind


def soft_vignette(c, strength=0.10, ip=0, op=None, color="#9aa3aa"):
    """A barely-there falloff toward the corners so the light ground reads as lit, not flat."""
    r = math.hypot(W, H) * 0.62
    c.no_camera.add(c.shape("light falloff", [group([
        rect(W, H, W / 2, H / 2),
        gradient([(0, color), (1, color)], [W / 2, H * 0.45], [W / 2 + r, H * 0.45], kind=2,
                 alpha_stops=[(0, 0), (0.6, strength * 0.4), (1, strength)])])], ip=ip, op=op))


# --------------------------------------------------------------------------- 2D text
def txt(c, text, font, size, color, x, baseline, j=0, tracking=0, ip=0, op=None, parent=None, o=100, slot=None,
        label=None, p=None, s=(100, 100)):
    doc = text_doc(text, font, size, col(color), justify=j, tracking=tracking)
    return c.text(f"t: {text[:28]}", doc, p=p if p is not None else (x, baseline), ip=ip, op=op, parent=parent, o=o,
                  slot=slot, label=label, s=s)


def statement(c, fonts, lines, start, colors=None, cx=None, center_y=None, max_w=None, max_size=None, stagger=8,
              exit_at=None, slots=None, j=2, x=None):
    """Condensed-italic statement, one masked rise per line. Returns (size, top, bottom)."""
    colors = colors or ["ink"] * len(lines)
    max_w = max_w or (1560 if LANDSCAPE else 880)
    max_size = max_size or (230 if LANDSCAPE else 230)
    size = fonts.fit("OT Wordmark", lines, max_w, max_size)
    lead = size * 0.96
    cy = H / 2 if center_y is None else center_y
    b0 = cy - lead * (len(lines) - 1) / 2 + CAP * size / 2
    xx = (W / 2 if cx is None else cx) if x is None else x
    for i, ln in enumerate(lines):
        fp.rise_line(c, fonts, ln, "OT Wordmark", size, col(colors[i]), xx, b0 + i * lead, j=j, start=start + i * stagger,
                     exit_at=None if exit_at is None else exit_at + i * 2,
                     slot=(slots[i] if slots else None), label=(f"Statement line {i + 1}" if slots else None))
    c.cue(start, "tick", 0.5)
    top = b0 - CAP * size
    return size, top, b0 + (len(lines) - 1) * lead


# --------------------------------------------------------------------------- 3D UI planes
class Plane:
    """A flat UI surface in 3D. Children are drawn in plane coordinates (0,0 = top-left); the plane is placed by its
    centre. Opacity does not inherit through parenting, so children carry their own fades."""

    def __init__(self, c, name, w, h, p, rx=0, ry=0, rz=0, s=(100, 100, 100), ip=0, op=None):
        self.c, self.w, self.h, self.ip, self.op = c, w, h, ip, op
        self.ind = c.null3d(name, Comp.ks3(p=p, a=(w / 2, h / 2, 0), s=s, rx=rx, ry=ry, rz=rz), ip=ip, op=op)

    def _ks(self, p=(0, 0, 0), a=(0, 0, 0), s=(100, 100, 100), o=100, rz=0):
        return Comp.ks3(p=p, a=a, s=s, o=o, rz=rz)

    def shape(self, name, shapes, p=(0, 0, 0), a=(0, 0, 0), s=(100, 100, 100), o=100, ip=None, op=None, rz=0):
        return self.c.shape3d(name, shapes, self._ks(p, a, s, o, rz), ip=self.ip if ip is None else ip,
                              op=self.op if op is None else op, parent=self.ind)

    def box(self, x, y, w, h, color, r=0, o=100, line=None, line_w=1.5, shadow=None, ip=None, op=None, name=None,
            p=(0, 0, 0), s=(100, 100, 100), a=None, fill_keys=None):
        items = [rect(w, h, x + w / 2, y + h / 2, r)]
        if fill_keys:
            items.append(fl_anim(fill_keys))
        elif color is not None:
            items.append(fl(color))
        if line:
            items.append(st(line, line_w))
        ind = self.shape(name or f"box {x:.0f},{y:.0f}", [group(items)], p=p, s=s, o=o, ip=ip, op=op,
                         a=a if a is not None else (0, 0, 0))
        if shadow:
            with_fx(self.c, ind, drop_shadow(**shadow))
        return ind

    def circle(self, cx, cy, d, color, o=100, line=None, line_w=2, ip=None, op=None, p=(0, 0, 0), s=(100, 100, 100),
               a=(0, 0, 0)):
        items = [ellipse(d, d, cx, cy)]
        if color:
            items.append(fl(color))
        if line:
            items.append(st(line, line_w))
        return self.shape(f"circle {cx:.0f},{cy:.0f}", [group(items)], p=p, s=s, a=a, o=o, ip=ip, op=op)

    def line(self, x1, y1, x2, y2, color, width=2, o=100, ip=None, op=None):
        return self.shape("rule", [group([path([[x1, y1], [x2, y2]]), st(color, width)])], o=o, ip=ip, op=op)

    def text(self, text, font, size, color, x, baseline, j=0, tracking=0, o=100, ip=None, op=None, slot=None,
             label=None, p=None, s=(100, 100, 100), lh=None):
        doc = text_doc(text, font, size, col(color), justify=j, tracking=tracking, lh=lh)
        c = self.c
        c.fonts_used.add(doc["f"])
        layer = c._3d(c._base(5, f"t3: {text[:24]}", self._ks(p=p if p is not None else (x, baseline, 0), s=s, o=o),
                              self.ip if ip is None else ip, self.op if op is None else op, self.ind))
        layer["t"] = {"d": {"k": [{"s": doc, "t": 0}]}, "p": {}, "m": {"g": 1, "a": static([0, 0])}, "a": []}
        if slot:
            layer["t"]["d"]["sid"] = slot
            import json as _json
            c.slots[slot] = {"p": {"a": 1, "k": [{"t": 0, "s": _json.loads(_json.dumps(doc))}]}}
            c.controls.append({"sid": slot, "label": label or slot})
        return c.add(layer)

    def keyed_text(self, docs, x, baseline, ip=None, op=None, o=100):
        """Hold-keyed text documents [(frame, text, font, size, colour, justify), ...] (counters, typing)."""
        c = self.c
        k = []
        for f, t, font, size, color, j in docs:
            d = text_doc(t, font, size, col(color), justify=j)
            c.fonts_used.add(font)
            k.append({"s": d, "t": f})
        layer = c._3d(c._base(5, f"t3k: {docs[0][1][:20]}", self._ks(p=(x, baseline, 0), o=o),
                              self.ip if ip is None else ip, self.op if op is None else op, self.ind))
        layer["t"] = {"d": {"k": k}, "p": {}, "m": {"g": 1, "a": static([0, 0])}, "a": []}
        return c.add(layer)

    def image(self, file, iw, ih, x, y, w, h, o=100, ip=None, op=None, p=None, s=None, a=None):
        sx, sy = w / iw * 100, h / ih * 100
        ks = self._ks(p=p if p is not None else (x, y, 0), a=a if a is not None else (0, 0, 0),
                      s=s if s is not None else (sx, sy, 100), o=o)
        return self.c.image3d(f"img {file}", file, iw, ih, ks, ip=self.ip if ip is None else ip,
                              op=self.op if op is None else op, parent=self.ind)

    # ---- icons, drawn in plane coordinates
    def arrow(self, x, y, size, color="ink", o=100, ip=None, op=None):
        s = size / 40
        return self.shape("arrow", [group([path([[x - 12 * s, y], [x + 12 * s, y]]), st(color, 3.4 * s)]),
                                    group([path([[x + 3 * s, y - 9 * s], [x + 12 * s, y], [x + 3 * s, y + 9 * s]]),
                                           st(color, 3.4 * s)])], o=o, ip=ip, op=op)

    def check(self, x, y, size, color="ink", draw_at=None, width=None, ip=None, op=None):
        s = size / 48
        pts = [[x - 17 * s, y + 1 * s], [x - 5 * s, y + 13 * s], [x + 19 * s, y - 12 * s]]
        items = [path(pts), st(color, width or 6.5 * s)]
        if draw_at is not None:
            items.append({**trim(0, 100), "e": anim([(draw_at, 0, "entrance-sharp"), (draw_at + 8, 100)])})
        return self.shape("check", [group(items)], ip=ip, op=op)

    def heart(self, cx, cy, size, color="ink", filled=False, ip=None, op=None, s=(100, 100, 100), a=None):
        k = size / 40
        pts = [[0, 14], [-16, -1], [-16, -10], [-9, -16], [0, -10], [9, -16], [16, -10], [16, -1]]
        pts = [[cx + x * k, cy + y * k] for x, y in pts]
        ins = [[0, 0], [0, 0], [0, -5 * k], [-6 * k, 0], [0, 0], [-4 * k, 0], [0, -5 * k], [0, 0]]
        outs = [[0, 0], [0, 0], [0, -4 * k], [4 * k, 0], [0, 0], [6 * k, 0], [0, 5 * k], [0, 0]]
        shp = {"ty": "sh", "ks": {"a": 0, "k": {"i": ins, "o": outs, "v": pts, "c": True}}}
        items = [shp, fl(color) if filled else st(color, 3 * k)]
        return self.shape("heart", [group(items)], ip=ip, op=op, s=s, a=(cx, cy, 0), p=(cx, cy, 0))

    def star(self, cx, cy, size, color="ink", ip=None, op=None):
        r1, r2 = size / 2, size / 4.6
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            rr = r1 if i % 2 == 0 else r2
            pts.append([cx + rr * math.cos(ang), cy + rr * math.sin(ang)])
        return self.shape("star", [group([path(pts, closed=True), fl(color)])], ip=ip, op=op)


def button(plane, fonts, label, x, y, w, h, style="green", size=None, ip=None, op=None, arrow=True, press=None,
           name=None):
    """The site's button: one rounded rect (green / ink / white outline), label centred, arrow at the right.
    `press`: frame of a click -> the button squashes about its centre (0.93) and releases."""
    size = size or h * 0.36
    fillc = {"green": "green", "ink": "ink", "white": "white", "orange": "orange"}[style]
    txtc = "white" if style == "ink" else "ink"
    cx, cy = x + w / 2, y + h / 2
    s = (100, 100, 100)
    if press is not None:
        s = anim([(press, [100, 100, 100], "settle-soft"), (press + 2, [93, 93, 100], "hold"),
                  (press + 4, [93, 93, 100], "settle-soft"), (press + 12, [100, 100, 100])])
    g = plane.c.null3d(name or f"btn {label}", Comp.ks3(p=(cx, cy, 0), a=(cx, cy, 0), s=s),
                       ip=plane.ip if ip is None else ip, op=plane.op if op is None else op, parent=plane.ind)
    sub = _Child(plane, g, ip=ip, op=op)
    sub.box(x, y, w, h, fillc, r=h * 0.22, line="line" if style == "white" else None)
    tx = cx - (size * 0.6 if arrow else 0)
    sub.text(label, "OT Body Medium", size, txtc, tx, cy + CAP * size / 2, j=2)
    if arrow:
        sub.arrow(x + w - h * 0.55, cy, size * 1.15, txtc)
    return g


class _Child(Plane):
    """Plane-like helper that parents to an existing 3D null (for grouped, animatable sub-parts)."""

    def __init__(self, plane, parent_ind, ip=None, op=None):
        self.c, self.w, self.h = plane.c, plane.w, plane.h
        self.ip = plane.ip if ip is None else ip
        self.op = plane.op if op is None else op
        self.ind = parent_ind


def group3d(plane, name, ks=None, ip=None, op=None):
    """A 3D null inside a plane, for animating a cluster of children together. Returns a Plane-like helper."""
    ind = plane.c.null3d(name, ks or Comp.ks3(), ip=plane.ip if ip is None else ip,
                         op=plane.op if op is None else op, parent=plane.ind)
    return _Child(plane, ind, ip, op)


# --------------------------------------------------------------------------- cursor (screen space, on top)
ARROW = [(0, 0), (0, 46), (11.5, 35), (20, 54), (28.5, 50.5), (20, 32), (35, 32)]


def cursor(c, keys, presses=(), size=1.25, ip=None, op=None):
    """Custom pointer: black arrow, white edge. keys = [(frame, (x, y)), ...] arrival points (eased);
    it enters oversize and settles; `presses` squash it about the tip."""
    f0 = keys[0][0]
    pk = []
    for i, (f, (x, y)) in enumerate(keys):
        e = "entrance-sharp" if i < len(keys) - 1 else "linear"
        pk.append((f, [x, y, 0], e))
    sk = [(f0, [size * 190, size * 190, 100], "entrance-sharp"), (f0 + 9, [size * 100, size * 100, 100], "hold")]
    for pf in presses:
        sk += [(pf - 2, [size * 100, size * 100, 100], "settle-soft"), (pf, [size * 80, size * 80, 100], "settle-soft"),
               (pf + 4, [size * 100, size * 100, 100], "hold")]
        c.cue(pf, "tap", 0.9)
    sk.sort(key=lambda k: k[0])
    shp = [group([path([list(p) for p in ARROW], closed=True), fl("ink"), st("white", 3.2)])]
    ind = c.shape("cursor", shp, p=anim(pk), s=anim(sk),
                  o=anim([(f0, 0, "settle-soft"), (f0 + 4, 100)]), ip=f0 if ip is None else ip, op=op)
    c.no_camera.add(ind)
    return ind


# --------------------------------------------------------------------------- film strip (the site's divider)
def film_strip(c, y_keys, height, photos=None, fonts=None, title=None, ip=0, op=None, scroll=(0, 0), x_frames=None,
               ground_below=None, name="film strip"):
    """Dark band with sprocket holes on both edges; optional photo frames inside, scrolling sideways.
    y_keys: anim keys for the band's centre y. ground_below: colour of a field attached under the band
    (used as a wipe that reveals the next scene's ground)."""
    band = c.null(name, p=anim([(k[0], [0, k[1], 0]) + tuple(k[2:]) for k in y_keys]) if len(y_keys) > 1
                  else (0, y_keys[0][1]), ip=ip, op=op)
    c.no_camera.add(band)
    if ground_below:
        c.shape("strip ground", [group([rect(W * 1.2, H * 1.4, W / 2, height / 2 + H * 0.7), fl(ground_below)])],
                parent=band, ip=ip, op=op)
    c.shape("strip band", [group([rect(W * 1.2, height, W / 2, 0), fl("strip")])], parent=band, ip=ip, op=op)
    hole_w, hole_h, pitch = height * 0.075, height * 0.055, height * 0.135
    n = int(W * 1.3 / pitch) + 4
    xs = anim([(scroll[0] if isinstance(scroll[0], int) else 0, [0, 0, 0], "linear"),
               (c.frames if op is None else op, [-scroll[1], 0, 0])]) if scroll[1] else (0, 0)
    for edge in (-1, 1):
        yy = edge * (height / 2 - hole_h * 1.1)
        holes = [group([rect(hole_w, hole_h, -W * 0.1 + i * pitch, yy, hole_h * 0.28), fl("white", 92)])
                 for i in range(n)]
        c.shape(f"sprockets {edge}", holes, parent=band, p=xs, ip=ip, op=op)
    if photos:
        fh = height * 0.62
        gap = fh * 0.12
        x = -W * 0.05
        group_ind = c.null("strip frames", p=anim([(ip, [0, 0, 0], "linear"), (c.frames if op is None else op,
                                                                               [-scroll[1] * 1.6, 0, 0])])
                           if scroll[1] else (0, 0), parent=band, ip=ip, op=op)
        for file, (iw, ih) in photos:
            fw = fh * iw / ih
            c.image(f"frame {file}", file, iw, ih, p=(x + fw / 2, 0), s=(fw / iw * 100, fh / ih * 100),
                    parent=group_ind, ip=ip, op=op)
            x += fw + gap
    return band


# --------------------------------------------------------------------------- focus point (hook)
def brackets(c, pos_keys, scale_keys, color_keys, ip, op, width=4.5):
    L = 26
    items = []
    ck = sorted(color_keys, key=lambda k: k[0])
    for sx in (-1, 1):
        for sy in (-1, 1):
            g = [path([[sx * 50, sy * (50 - L)], [sx * 50, sy * 50], [sx * (50 - L), sy * 50]])]
            if ck:
                g.append({"ty": "st", "c": anim([(f, col(cc)[:3] + [1], e) for f, cc, e in ck]), "o": static(100),
                          "w": static(width), "lc": 2, "lj": 2})
            else:
                g.append(st("white", width))
            items.append(group(g))
    ind = c.shape("focus point", items, p=anim(pos_keys), s=anim(scale_keys), ip=ip, op=op)
    c.no_camera.add(ind)
    return ind
