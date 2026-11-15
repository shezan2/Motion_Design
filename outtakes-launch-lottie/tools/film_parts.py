"""Reusable parts for the Outtakes launch film (portrait 1080x1920, 30 fps).

Design system = the new Outtakes website ("Outtakes Dark"): near-black ground,
one green accent, cream sections, night->violet->sky->cream gradient, white
condensed-italic wordmark, Archivo Expanded headlines, Archivo body text.

Portrait safe zones (Reels/TikTok UI): keep copy and proof between y=260 and
y=1500 and inside x=80..940.
"""
from __future__ import annotations

from lottie_kit import (CAP, Comp, Fonts, anim, ellipse, fill, gradient, group, hexc, path, rect,
                        static, stroke, text_doc, trim)

W, H = 1080, 1920
L, R = 80, 940            # content column (clear of the right-hand app buttons)
CW = R - L
TOP, BOTTOM = 260, 1500   # vertical safe area

COL = {
    "bg": "#111113", "surface": "#23202a", "green": "#74f260", "cream": "#f0ebe4",
    "ink": "#111113", "white": "#ffffff", "violetDeep": "#2f2973", "violet": "#5a55d3",
    "sky": "#9bc3f4", "track": "#ff9cb8", "football": "#b9f5a3", "rugby": "#ffda74",
    "swimming": "#b5f2ff",
}


def c_(name, a=1.0):
    return hexc(COL.get(name, name), a)


# --------------------------------------------------------------------------- ground
def background(c: Comp, color="bg", label="Background"):
    c.color_slot("bgColor", c_(color), label)
    c.no_camera.add(c.shape("background", [group([rect(W, H, W / 2, H / 2), fill(c_(color), sid="bgColor")])]))


def glow(c: Comp, cx, cy, radius, colors=None, alphas=(0.55, 0.3, 0.0), ip=0, op=None, o=100):
    """Soft radial light from the brand gradient (no blur effects needed)."""
    colors = colors or [(0, COL["violet"]), (0.5, COL["violetDeep"]), (1, COL["bg"])]
    stops_a = [(0, alphas[0]), (0.5, alphas[1]), (1, alphas[2])]
    # only paint the pixels the light actually reaches (big gradient fills are the costliest thing in Skottie)
    y0, y1 = max(0, cy - radius), min(H, cy + radius)
    x0, x1 = max(0, cx - radius), min(W, cx + radius)
    return _lock(c, c.shape("glow", [group([rect(x1 - x0, y1 - y0, (x0 + x1) / 2, (y0 + y1) / 2),
                                    gradient(colors, [cx, cy], [cx + radius, cy], kind=2, alpha_stops=stops_a)])],
                   ip=ip, op=op, o=o))


def _lock(c, ind):
    c.no_camera.add(ind)
    return ind


def brand_gradient_rect(c: Comp, y0=0, y1=H, ip=0, op=None, parent=None, o=100):
    stops = [(0, COL["bg"]), (0.22, "#1c1a3a"), (0.38, COL["violetDeep"]), (0.55, COL["violet"]),
             (0.68, "#7f95f8"), (0.8, COL["sky"]), (0.9, "#cfe3ea"), (1, COL["cream"])]
    return _lock(c, c.shape("brand gradient", [group([rect(W, y1 - y0, W / 2, (y0 + y1) / 2),
                                                      gradient(stops, [W / 2, y0], [W / 2, y1])])], ip=ip, op=op,
                            parent=parent, o=o))


def grain(c: Comp, opacity=9):
    """Animated film grain as a Lottie layer. NOT used by default: a full-frame overlay-blended
    image is very expensive in Skottie (~330 ms/frame on CPU), so the MP4 export adds grain at
    encode time instead (tools/render.mjs). Kept for anyone who wants it inside the Lottie."""
    keys = []
    for f in range(0, c.frames + 2, 2):
        jx = ((f * 7919) % 200) - 100
        jy = ((f * 104729) % 300) - 150
        keys.append((f, [W / 2 + jx, H / 2 + jy, 0], "hold"))
    c.image("grain", "grain.jpg", 1300, 2300, p=anim(keys), o=opacity, blend=3)


def vignette(c: Comp, strength=0.45, ip=0, op=None):
    c.shape("vignette", [group([rect(W, H, W / 2, H / 2),
                                 gradient([(0, "#000000"), (1, "#000000")], [W / 2, H / 2], [W / 2 + 1250, H / 2], kind=2,
                                          alpha_stops=[(0, 0), (0.55, 0), (1, strength)])])], ip=ip, op=op)


# --------------------------------------------------------------------------- seams
def curtain_open(c: Comp, at=0, dur=4):
    """Shutter curtain finishes its sweep: the top edge travels down, revealing the scene."""
    _lock(c, c.shape("curtain open", [group([rect(W, H, W / 2, H / 2), fill(c_("#000000"))])],
                     p=anim([(at, [0, 0, 0], "entrance-sharp"), (at + dur, [0, H, 0])]), ip=at, op=at + dur + 1))


def curtain_close(c: Comp, end=None, dur=3):
    """Shutter curtain starts its sweep: the bottom edge travels down, covering the scene (cut on motion)."""
    end = c.frames if end is None else end
    _lock(c, c.shape("curtain close", [group([rect(W, H, W / 2, H / 2), fill(c_("#000000"))])],
                     p=anim([(end - dur, [0, -H, 0], "exit-accelerate"), (end - 1, [0, 0, 0])]), ip=end - dur,
                     op=end))
    c.cue(end - 1, "shutter", 0.9)


def flash(c: Comp, at, peak=35, dur=3):
    _lock(c, c.shape("flash", [group([rect(W, H, W / 2, H / 2), fill(c_("#ffffff"))])],
                     o=anim([(at, peak, "settle-soft"), (at + dur, 0)]), ip=at, op=at + dur + 1))


# --------------------------------------------------------------------------- type
def rise_line(c: Comp, fonts: Fonts, text, font, size, color, x, baseline, j=0, start=0, exit_at=None,
              parent=None, slot=None, label=None, dur=12, op=None, tracking=0, o=100):
    """Statement-mask line reveal: the line rises into a static matte (no opacity fade)."""
    dist = size * 1.18
    keys = [(start, [x, baseline + dist, 0], "entrance-sharp"), (start + dur, [x, baseline, 0])]
    end = op if op is not None else c.frames
    if exit_at is not None:
        keys += [(exit_at, [x, baseline, 0], "exit-accelerate"), (exit_at + 9, [x, baseline - dist, 0])]
        end = exit_at + 10
    col = c_(color) if isinstance(color, str) else color
    c.text(f"line: {text}", text_doc(text, font, size, col, justify=j, tracking=tracking), p=anim(keys),
           ip=start, op=end, parent=parent, matted=True, slot=slot, label=label, o=o)
    tw = fonts.width(font, size, text, tracking)
    pad = size * 0.5
    if j == 0:
        mx = x - pad / 2 + (tw + pad) / 2
    elif j == 1:
        mx = x + pad / 2 - (tw + pad) / 2
    else:
        mx = x
    top, bot = baseline - size * 1.02, baseline + size * 0.32
    c.shape(f"mask: {text}", [group([rect(tw + pad * 2, bot - top, mx, (top + bot) / 2), fill(c_("white"))])],
            ip=start, op=end, parent=parent, matte_for_next=True)
    return tw


def fade_line(c: Comp, text, font, size, color, x, baseline, j=0, start=0, op=None, parent=None, o=100,
              exit_at=None, dy=26):
    keys_p = [(start, [x, baseline + dy, 0], "entrance-sharp"), (start + 12, [x, baseline, 0])]
    keys_o = [(start, 0, "settle-soft"), (start + 8, o)]
    end = op if op is not None else c.frames
    if exit_at is not None:
        keys_o += [(exit_at, o, "exit-accelerate"), (exit_at + 7, 0)]
        end = exit_at + 8
    col = c_(color) if isinstance(color, str) else color
    return c.text(f"text: {text}", text_doc(text, font, size, col, justify=j), p=anim(keys_p), o=anim(keys_o),
                  ip=start, op=end, parent=parent)


def label_text(c: Comp, text, font, size, color, x, baseline, j=0, ip=0, op=None, parent=None, o=100, slot=None,
               label=None):
    col = c_(color) if isinstance(color, str) else color
    return c.text(f"text: {text}", text_doc(text, font, size, col, justify=j), p=(x, baseline), ip=ip, op=op,
                  parent=parent, o=o, slot=slot, label=label)


# Feature-beat armature: same headline block, support line and proof area every time.
HEAD_TOP = 330


def armature_headline(c: Comp, fonts: Fonts, line1, line2, support, start=6, slot_prefix="head"):
    size = fonts.fit("OT Display", [line1, line2], CW, 98)
    cap = CAP * size
    b1 = HEAD_TOP + cap
    b2 = b1 + size * 1.04
    rise_line(c, fonts, line1, "OT Display", size, "white", L, b1, j=0, start=start, slot=f"{slot_prefix}1",
              label="Headline line 1")
    rise_line(c, fonts, line2, "OT Display", size, "green", L, b2, j=0, start=start + 8, slot=f"{slot_prefix}2",
              label="Headline line 2")
    fade_line(c, support, "OT Body", 34, "white", L, b2 + 66, j=0, start=start + 18, o=62)
    c.cue(start, "tick", 0.5)
    return b2 + 66  # support baseline


# --------------------------------------------------------------------------- UI pieces
def box(c: Comp, name, x, y, w, h, color, r=0, parent=None, ip=0, op=None, o=100, stroke_col=None, stroke_w=0,
        matte_for_next=False):
    items = [rect(w, h, x + w / 2, y + h / 2, r)]
    # Lottie ignores the alpha channel of fill/stroke colours: move it into opacity.
    if stroke_col:
        sc = c_(stroke_col) if isinstance(stroke_col, str) else list(stroke_col)
        items.append(stroke(sc[:3] + [1], stroke_w, opacity=round(sc[3] * 100) if len(sc) > 3 else 100))
    if color is not None:
        fc = c_(color) if isinstance(color, str) else list(color)
        items.append(fill(fc[:3] + [1], opacity=round(fc[3] * 100) if len(fc) > 3 else 100))
    return c.shape(name, [group(items)], ip=ip, op=op, parent=parent, o=o, matte_for_next=matte_for_next)


def photo(c: Comp, name, file, size, x, y, w, h, focus=(0.5, 0.5), r=0, ip=0, op=None, parent=None, zoom=None,
          rise=None, o=100, clip=True):
    """Image cropped to a box (cover fit) by a rounded-rect track matte.

    zoom: [(frame, factor, ease), ...] multiplies the cover scale (Ken Burns / settle).
    rise: [(frame, dy, ease), ...] offsets the image inside the static matte (unmask reveal).
    """
    iw, ih = size
    s = max(w / iw, h / ih)
    fx, fy = focus
    ox = max(-(iw * s - w) / 2, min((iw * s - w) / 2, (0.5 - fx) * iw * s))
    oy = max(-(ih * s - h) / 2, min((ih * s - h) / 2, (0.5 - fy) * ih * s))
    cx, cy = x + w / 2 + ox, y + h / 2 + oy
    zoom = [k if len(k) == 3 else (*k, "linear") for k in (zoom or [])]
    rise = [k if len(k) == 3 else (*k, "linear") for k in (rise or [])]
    if zoom:
        scale = anim([(f, [s * 100 * z, s * 100 * z, 100], e) for f, z, e in zoom])
    else:
        scale = [s * 100, s * 100]
    if rise:
        pos = anim([(f, [cx, cy + dy, 0], e) for f, dy, e in rise])
    else:
        pos = (cx, cy)
    c.image(name, file, iw, ih, p=pos, s=scale, ip=ip, op=op, parent=parent, matted=clip, o=o)
    if clip:
        box(c, f"crop: {name}", x, y, w, h, "white", r=r, ip=ip, op=op, parent=parent, matte_for_next=True)


def tag(c: Comp, fonts: Fonts, sport, x, y, size=24, parent=None, ip=0, op=None):
    text = sport.capitalize()
    tw = fonts.width("OT Body", size, text)
    pad = size * 0.75
    h = size * 1.5
    w = tw + pad * 2
    box(c, f"tag {sport}", x, y, w, h, sport, r=h / 2, parent=parent, ip=ip, op=op)
    label_text(c, text, "OT Body", size, "ink", x + w / 2, y + h / 2 + CAP * size / 2, j=2, ip=ip, op=op,
               parent=parent)
    return w


def chip(c: Comp, fonts: Fonts, text, x, y, size=26, active=False, parent=None, ip=0, op=None, o=100):
    tw = fonts.width("OT Body", size, text)
    w, h = tw + size * 1.9, size * 1.9
    if active:
        box(c, f"chip {text}", x, y, w, h, "white", r=size * 0.35, parent=parent, ip=ip, op=op, o=o)
    else:
        box(c, f"chip {text}", x, y, w, h, None, r=size * 0.35, parent=parent, ip=ip, op=op, o=o,
            stroke_col=c_("white", 0.75), stroke_w=2)
    label_text(c, text, "OT Body", size, "ink" if active else "white", x + w / 2, y + h / 2 + CAP * size / 2, j=2,
               ip=ip, op=op, parent=parent, o=o)
    return w


def tap(c: Comp, x, y, appear, press, size=120):
    """Fingertip touch: appears oversize, settles, presses (shrinks), ring ripples out."""
    c.shape("tap ring", [group([ellipse(size, size), stroke(c_("white"), 4)])], p=(x, y),
            s=anim([(press, [100, 100, 100], "settle-soft"), (press + 14, [240, 240, 100])]),
            o=anim([(press, 80, "settle-soft"), (press + 14, 0)]), ip=press, op=press + 15)
    c.shape("tap finger", [group([ellipse(size, size), fill(c_("white", 1), 55), stroke(c_("white"), 3, 90)])],
            p=(x, y),
            s=anim([(appear, [160, 160, 100], "entrance-sharp"), (appear + 8, [100, 100, 100], "hold"),
                    (press, [78, 78, 100], "hold"), (press + 5, [100, 100, 100])]),
            o=anim([(appear, 0, "settle-soft"), (appear + 6, 100, "hold"), (press + 8, 100, "exit-accelerate"),
                    (press + 14, 0)]),
            ip=appear, op=press + 15)
    c.cue(press, "tap", 0.8)


def check_icon(c: Comp, x, y, size, color, draw_at, parent=None, ip=0, op=None, width=None):
    s = size / 48
    pts = [[x - 18 * s, y + 1 * s], [x - 5 * s, y + 14 * s], [x + 20 * s, y - 13 * s]]
    c.shape("check", [group([path(pts), stroke(c_(color) if isinstance(color, str) else color, width or 7 * s),
                             {**trim(0, 100), "e": anim([(draw_at, 0, "entrance-sharp"), (draw_at + 10, 100)])}])],
            ip=ip if ip else draw_at, op=op, parent=parent)


def search_icon(c: Comp, x, y, size, color="white", parent=None, ip=0, op=None):
    s = size / 40
    c.shape("search icon", [group([ellipse(26 * s, 26 * s, x - 3 * s, y - 3 * s), stroke(c_(color), 3.2 * s)]),
                            group([path([[x + 7 * s, y + 7 * s], [x + 16 * s, y + 16 * s]]), stroke(c_(color), 3.2 * s)])],
            ip=ip, op=op, parent=parent)


def lock_icon(c: Comp, x, y, size, color="ink", parent=None, ip=0, op=None):
    s = size / 40
    body = group([rect(26 * s, 20 * s, x, y + 6 * s, 4 * s), fill(c_(color))])
    k = 0.5523 * 9 * s
    shackle = path([[x - 9 * s, y + 2 * s], [x - 9 * s, y - 7 * s], [x, y - 16 * s], [x + 9 * s, y - 7 * s],
                    [x + 9 * s, y + 2 * s]],
                   ins=[[0, 0], [0, k], [-k, 0], [0, -k], [0, 0]],
                   outs=[[0, 0], [0, -k], [k, 0], [0, k], [0, 0]])
    c.shape("lock icon", [body, group([shackle, stroke(c_(color), 4 * s)])], ip=ip, op=op, parent=parent)


def arrow_icon(c: Comp, x, y, size, color="ink", parent=None, ip=0, op=None):
    s = size / 40
    c.shape("arrow", [group([path([[x - 12 * s, y], [x + 12 * s, y]]), stroke(c_(color), 3.6 * s)]),
                      group([path([[x + 3 * s, y - 9 * s], [x + 12 * s, y], [x + 3 * s, y + 9 * s]]),
                             stroke(c_(color), 3.6 * s)])], ip=ip, op=op, parent=parent)


def cta_button(c: Comp, fonts: Fonts, label, cx, cy, size=40, parent=None, ip=0, op=None, slot=None):
    """Green button + separate arrow block, as on the new site ("Find a Photographer ->")."""
    tw = fonts.width("OT Body Medium", size, label)
    h = size * 2.3
    w = tw + size * 2.4
    gap = 6
    total = w + gap + h
    x0 = cx - total / 2
    box(c, "cta", x0, cy - h / 2, w, h, "green", r=size * 0.35, parent=parent, ip=ip, op=op)
    box(c, "cta arrow block", x0 + w + gap, cy - h / 2, h, h, "green", r=size * 0.35, parent=parent, ip=ip, op=op)
    label_text(c, label, "OT Body Medium", size, "ink", x0 + w / 2, cy + CAP * size / 2, j=2, ip=ip, op=op,
               parent=parent, slot=slot, label="Button label" if slot else None)
    arrow_icon(c, x0 + w + gap + h / 2, cy, size * 1.15, "ink", parent=parent, ip=ip, op=op)
    return x0, total, h


def drift(c: Comp, scale=103.5, dy=-16, anchor=(W / 2, 1000)):
    """Slow push-in for the whole scene: camera calmer than the objects, keeps holds alive."""
    ax, ay = anchor
    c.camera(p=anim([(0, [ax, ay, 0], "linear"), (c.frames, [ax, ay + dy, 0])]), a=(ax, ay),
             s=anim([(0, [100, 100, 100], "linear"), (c.frames, [scale, scale, 100])]))
