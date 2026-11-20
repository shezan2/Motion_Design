"""Author the Outtakes launch film as Lottie scenes for the text-to-lottie player.

    python3 tools/build_film.py                        # portrait  -> public/projects/outtakes-launch/scene-1..13
    OT_FORMAT=landscape python3 tools/build_film.py    # landscape -> public/projects/outtakes-launch-16x9/scene-1..13

v3 - rebuilt to the LIVE website interface (outtakes.ozendigital.co, Nov 2026) and its
signature animations:
  * hero: giant wordmark over a warm panning-blur photo, "STORIES TOLD THROUGH FRAMES",
    then the page scrolls into the next section (continuous carry, no cut)
  * "EVERY SIDELINE SHOT STARTS WITH A SEARCH": tilted 3D photo cards orbiting while the
    headline loads letter by letter, on the cream -> green -> black glow
  * the photographer profile page (hero, stats, featured), packages + availability calendar
  * "HOW A BOOKING GOES": 3D carousel of the green step cards ONE..FOUR (site copy)
  * "GET IN THE FRAME": 3D corridor of photo panels + the two site buttons, then the footer
    with the giant green OUTTAKES

Chapters (skills/text-to-lottie/references/chapterization-transition-grammar.md):
hook -> problem -> hero -> sideline -> six feature proofs -> booking steps -> dates -> frame.
Seams: camera-shutter occlusion wipes, except hero -> sideline -> clients, which scroll like
the site. Also writes cues.json (sound-effect cues in film frames).
"""
from __future__ import annotations

import calendar
import json
import math
import shutil
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from lottie_kit import (CAP, Comp, Fonts, anim, ease_value, ellipse, gradient, group, hexc, letter_reveal,  # noqa: E402
                        path, rect, static, stroke, text_doc, trim)
from film_parts import (BOTTOM, COL, CW, H, L, LANDSCAPE, R, W, armature_headline, background, box,  # noqa: E402
                        c_, check_icon, curtain_close, curtain_open, drift, fade_line, feature_glow, flash, glow,
                        label_text, lock_icon, photo, rise_line, rise_pair, search_icon, site_button, site_gradient,
                        tag, tap)

ROOT = Path(__file__).resolve().parent.parent
PHOTOS = ROOT / "brand" / "photos"
FONTS_DIR = ROOT / "brand" / "fonts"
OUT = ROOT / "public" / "projects" / ("outtakes-launch-16x9" if LANDSCAPE else "outtakes-launch")
fonts = Fonts(FONTS_DIR)

STATE = "OT Wordmark"   # statements: the site's condensed italic display face
TITLE = "OT Display"    # small titles: Archivo Expanded

SIZES = {p.name: Image.open(p).size for p in PHOTOS.glob("*.jpg")}
FOCUS = {
    "celebrate-fists": (0.5, 0.4), "kids-duel": (0.40, 0.5), "sepak-takraw": (0.42, 0.4),
    "celebrate-run": (0.44, 0.45), "basketball": (0.5, 0.4), "smile-orange": (0.48, 0.4),
    "point-orange": (0.46, 0.4), "stretch-ball": (0.42, 0.45), "heart-hands": (0.5, 0.4),
    "number-10": (0.45, 0.5), "team-backs": (0.5, 0.5), "portrait-flare": (0.5, 0.32),
    "tackle-night": (0.5, 0.5), "floodlight-profile": (0.45, 0.32), "motion-blur": (0.52, 0.5),
    "team-talk": (0.6, 0.5),
}
GREY = hexc("#8d8996")
INK55 = hexc("#6f6a64")
PANEL = "#e8e2d9"  # the profile page's package / calendar panels (one step darker than cream)

# sample job used across the film (illustrative): $70, Saturday 21 Nov 2026
PRICE = "S$70"
PRICE_DEC = "S$70.00"
JOB_DATE = "Sat 21 Nov"


def P(name):
    return f"{name}.jpg", SIZES[f"{name}.jpg"]


PANEL_W, PANEL_H = 800, 1000


def panel_photo(name):
    """4:5 cover crop of a photo around its focus, baked next to the photos (git-ignored, rebuilt on demand)."""
    out = PHOTOS / f"panel-{name}.jpg"
    if not out.exists():
        im = Image.open(PHOTOS / f"{name}.jpg").convert("RGB")
        iw, ih = im.size
        k = max(PANEL_W / iw, PANEL_H / ih)
        cw, chh = PANEL_W / k, PANEL_H / k
        fx, fy = FOCUS.get(name, (0.5, 0.5))
        x0 = min(max(fx * iw - cw / 2, 0), iw - cw)
        y0 = min(max(fy * ih - chh / 2, 0), ih - chh)
        im.crop((round(x0), round(y0), round(x0 + cw), round(y0 + chh))).resize(
            (PANEL_W, PANEL_H), Image.LANCZOS).save(out, quality=86)
    SIZES[out.name] = (PANEL_W, PANEL_H)
    return out.name


def pic(c, name, x, y, w, h, **kw):
    file, size = P(name)
    photo(c, name, file, size, x, y, w, h, focus=kw.pop("focus", FOCUS.get(name, (0.5, 0.5))), **kw)


def members_opacity(layers, keys):
    for lyr in layers:
        lyr["ks"]["o"] = anim(keys)


def layers_since(c, start_index):
    return c._layers[start_index:]


def fill_(color, opacity=100):
    col = c_(color) if isinstance(color, str) else color
    return {"ty": "fl", "c": {"a": 0, "k": col[:3] + [1]}, "o": {"a": 0, "k": opacity}, "r": 1}


def wordmark_crash(c, text, family, size, cx, cy, crash, end, color="white", streaks=4, start_scale=350,
                   parent=None, settle_end_scale=94, slot=None, label=None, op=None):
    """Arrival from oversize with decaying streak copies (the reveal / the date hit)."""
    cap = CAP * size
    doc = text_doc(text, family, size, c_(color), justify=2)
    k_main = [(crash, [start_scale, start_scale, 100], "crash"), (crash + 14, [100, 100, 100], "linear"),
              (end, [settle_end_scale, settle_end_scale, 100])]
    for k in range(streaks, 0, -1):
        at6 = start_scale + (100 - start_scale) * ease_value("crash", 6 / 14)
        sc0 = start_scale * (1 + 0.16 * k)
        c.text(f"streak {k}", doc, p=(cx, cy), a=(0, -cap / 2), ip=crash, op=crash + 7, parent=parent,
               s=anim([(crash, [sc0, sc0, 100], "crash"), (crash + 6, [at6, at6, 100])]),
               o=anim([(crash, 22, "settle-soft"), (crash + 6, 0)]))
    return c.text(f"crash: {text}", doc, p=(cx, cy), a=(0, -cap / 2), ip=crash, op=op, parent=parent,
                  s=anim(k_main), slot=slot, label=label)


def statement(c, line1, line2, start, slots=("s1", "s2"), labels=("Line 1", "Line 2"), exit_at=None,
              port_max=260, land_max=250, center_y=None, port_lines=True):
    """Two-colour statement in the condensed display face: two centred lines (portrait) or one line (landscape)."""
    cy = H / 2 if center_y is None else center_y
    if LANDSCAPE or not port_lines:
        size = fonts.fit(STATE, [f"{line1} {line2}"], 1560 if LANDSCAPE else 860, land_max if LANDSCAPE else port_max)
        rise_pair(c, fonts, line1, line2, STATE, size, W / 2, cy + CAP * size / 2, start=start, gap_frames=9,
                  exit_at=exit_at, slot1=slots[0], slot2=slots[1], label1=labels[0], label2=labels[1])
    else:
        size = fonts.fit(STATE, [line1, line2], 860, port_max)
        b1 = cy - size * 0.98 / 2 + CAP * size / 2
        rise_line(c, fonts, line1, STATE, size, "white", W / 2, b1, j=2, start=start, exit_at=exit_at,
                  slot=slots[0], label=labels[0])
        rise_line(c, fonts, line2, STATE, size, "green", W / 2, b1 + size * 0.98, j=2, start=start + 9,
                  exit_at=None if exit_at is None else exit_at + 2, slot=slots[1], label=labels[1])
    c.cue(start, "tick", 0.55)
    return size


# =========================================================================== 1 HOOK
def scene_hook():
    c = Comp("01 Hook - burst mode", W, H, 140)
    background(c, "#000000")
    burst = ["tackle-night", "kids-duel", "point-orange", "sepak-takraw", "number-10", "motion-blur",
             "smile-orange", "heart-hands", "stretch-ball", "portrait-flare"]
    times = [3, 14, 24, 33, 42, 50, 57, 63, 69, 74]
    land = 80
    for i, (name, t0) in enumerate(zip(burst, times)):
        t1 = times[i + 1] if i + 1 < len(times) else land
        pic(c, name, 0, 0, W, H, clip=False, ip=t0, op=t1,
            zoom=[(t0, 1.07, "settle-soft"), (t0 + 8, 1.0, "linear"), (t1, 0.995)])
        flash(c, t0, peak=28, dur=2)
        c.cue(t0, "shutter", 0.55 + 0.4 * i / len(times))
    pic(c, "celebrate-run", 0, 0, W, H, clip=False, ip=land,
        zoom=[(land, 1.14, "entrance-sharp"), (land + 8, 1.0, "linear"), (140, 1.05)])
    flash(c, land, peak=40, dur=3)
    c.cue(land, "shutter_big", 1.0)
    c.cue(land, "boom_small", 0.45)
    lh = 620 if LANDSCAPE else 1100
    c.shape("legibility", [group([rect(W, lh, W / 2, H - lh / 2),
                                   gradient([(0, "#000000"), (1, "#000000")], [W / 2, H - lh], [W / 2, H],
                                            alpha_stops=[(0, 0), (0.55, 0.55), (1, 0.8)])])], ip=land)
    if LANDSCAPE:
        size = fonts.fit(STATE, ["YOU GOT THE SHOT."], 1560, 230)
        rise_pair(c, fonts, "YOU GOT", "THE SHOT.", STATE, size, W / 2, H - 120, start=92, gap_frames=9,
                  slot1="hook1", slot2="hook2", label1="Hook line 1", label2="Hook line 2")
    else:
        size = fonts.fit(STATE, ["YOU GOT", "THE SHOT."], 860, 230)
        b2 = 1430
        rise_line(c, fonts, "YOU GOT", STATE, size, "white", W / 2, b2 - size * 0.98, j=2, start=92, slot="hook1",
                  label="Hook line 1")
        rise_line(c, fonts, "THE SHOT.", STATE, size, "green", W / 2, b2, j=2, start=101, slot="hook2",
                  label="Hook line 2")
    c.cue(92, "tick", 0.5)
    c.cue(101, "tick", 0.5)
    drift(c)
    curtain_close(c)
    return c


# =========================================================================== 2 PROBLEM
def scene_problem():
    c = Comp("02 Problem - the DMs", W, H, 195)
    background(c)
    if LANDSCAPE:
        c.image("plate", "plate-celebrate-blur-land.jpg", 1920, 1080, p=(W / 2, H / 2))
        cl, cr = (W - 900) / 2, (W + 900) / 2
    else:
        c.image("plate", "plate-celebrate-blur.jpg", 1080, 1920, p=(W / 2, H / 2))
        cl, cr = L, R
    msgs = [("them", "how much for saturday's match?", 12), ("me", "$70 for the full game", 36),
            ("them", "can do $30?", 62), ("them", "game cancelled, no need to pay ya", 92),
            ("me", "just following up on the invoice :)", 124)]
    seen_at, dim_at = 146, 160
    size = 42
    while max(fonts.width("OT Body", size, m[1]) for m in msgs) > (cr - cl) - 70:
        size -= 1
    bh = size * 1.25 + 52
    gap, seen_h = 16, 52
    YB = 930 if LANDSCAPE else 1400
    for i, (who, text, at) in enumerate(msgs):
        tw = fonts.width("OT Body", size, text)
        bw = tw + 68
        bx = cl if who == "them" else cr - bw
        ax = bx if who == "them" else cr
        keys = [(at, [ax, YB + 40, 0], "entrance-sharp"), (at + 9, [ax, YB, 0])]
        cur = 0
        pushes = [m[2] for m in msgs[i + 1:]] + [seen_at]
        deltas = [bh + gap] * (len(msgs) - i - 1) + [seen_h]
        for t, d in zip(pushes, deltas):
            keys.append((t, [ax, YB + cur, 0], "settle-soft"))
            cur -= d
            keys.append((t + 10, [ax, YB + cur, 0]))
        g = c.null(f"bubble {i}", p=anim(keys), a=(ax, YB), ip=at,
                   s=anim([(at, [92, 92, 100], "entrance-sharp"), (at + 9, [100, 100, 100])]))
        start = len(c._layers)
        c.shape(f"bubble bg {i}", [group([rect(bw, bh, bx + bw / 2, YB - bh / 2, bh / 2),
                                          fill_("green" if who == "me" else "surface")])], ip=at, parent=g)
        label_text(c, text, "OT Body", size, "ink" if who == "me" else "white", bx + 34,
                   YB - bh / 2 + CAP * size / 2, j=0, ip=at, parent=g)
        members_opacity(layers_since(c, start), [(at, 0, "settle-soft"), (at + 6, 100, "hold"),
                                                 (dim_at, 100, "travel-balanced"), (dim_at + 10, 22)])
        c.cue(at, "blip_out" if who == "me" else "blip_in", 0.9)
    s0 = len(c._layers)
    label_text(c, "Seen", "OT Body", 28, GREY, cr - 8, YB - 12, j=1, ip=seen_at + 4)
    members_opacity(layers_since(c, s0), [(seen_at + 4, 0, "settle-soft"), (seen_at + 10, 100, "hold"),
                                          (dim_at, 100, "travel-balanced"), (dim_at + 10, 22)])
    c.cue(seen_at + 4, "tick", 0.4)
    statement(c, "SOUND", "FAMILIAR?", dim_at + 4, slots=("problem1", "problem2"), port_max=260, land_max=250)
    c.cue(168, "riser:25", 0.6)
    curtain_open(c)
    drift(c)
    curtain_close(c)
    return c


# =========================================================================== 3 HERO (site)
SCROLL_A, SCROLL_B = 100, 134   # the hero page scroll lands exactly on the cut into chapter 4
GLOW_H = 1.3                     # height of the sideline-section glow, in screen heights


def sideline_headline():
    """The sideline section's headline (shared by the hero's scroll-in and chapter 4)."""
    l1, l2 = "EVERY SIDELINE SHOT", "STARTS WITH A SEARCH"
    size = fonts.fit(STATE, [l1, l2], 1500 if LANDSCAPE else 860, 175 if LANDSCAPE else 150)
    return l1, l2, size, H / 2 - size * 0.08


GHOST = 12  # opacity of the not-yet-loaded letters


def scene_hero():
    c = Comp("03 Hero - OUTTAKES", W, H, 135)
    background(c, "#000000")
    crash = 2
    page = c.null("page scroll", p=anim([(SCROLL_A, [0, 0, 0], "scroll"), (SCROLL_B, [0, -H, 0])]))
    plate = "plate-hero-land.jpg" if LANDSCAPE else "plate-hero.jpg"
    c.image("hero plate", plate, W, H, ip=crash, parent=page,
            p=anim([(crash, [W / 2 + 16, H / 2, 0], "linear"), (135, [W / 2 - 16, H / 2, 0])]),
            s=anim([(crash, [112, 112, 100], "settle-soft"), (crash + 30, [106, 106, 100], "linear"),
                    (135, [104, 104, 100])]))
    c.shape("hero shade", [group([rect(W, H, W / 2, H / 2),
                                   gradient([(0, "#000000"), (1, "#000000")], [W / 2, 0], [W / 2, H],
                                            alpha_stops=[(0, 0.25), (0.5, 0.05), (1, 0.45)])])], ip=crash, parent=page)
    # the wordmark crashes into its hero position
    if LANDSCAPE:
        size = fonts.fit(STATE, ["OUTTAKES"], 1000, 300)
        tw = fonts.width(STATE, size, "OUTTAKES")
        cx, cy = 110 + tw / 2, 120 + CAP * size / 2
    else:
        size = fonts.fit(STATE, ["OUTTAKES"], 900, 330)
        tw = fonts.width(STATE, size, "OUTTAKES")
        cx, cy = W / 2, 560
    wordmark_crash(c, "OUTTAKES", STATE, size, cx, cy, crash, 135, parent=page, settle_end_scale=97,
                   slot="brand", label="Wordmark")
    c.cue(crash, "boom", 1.0)
    c.cue(crash, "shutter_big", 1.0)
    ts = fonts.fit(TITLE, ["STORIES TOLD THROUGH FRAMES"], tw * 0.82, 52)
    if LANDSCAPE:
        rise_line(c, fonts, "STORIES TOLD THROUGH FRAMES", TITLE, ts, "white", cx + tw / 2 - 10,
                  cy + CAP * size / 2 + ts * 1.25, j=1, start=22, parent=page, slot="tagline", label="Tagline")
    else:
        rise_line(c, fonts, "STORIES TOLD THROUGH FRAMES", TITLE, ts, "white", W / 2,
                  cy + CAP * size / 2 + ts * 1.5, j=2, start=22, parent=page, slot="tagline", label="Tagline")
    c.cue(22, "tick", 0.5)
    # site chrome: Sign In / Menu box
    nbw, nbh = 330, 68
    nx, ny = (W - 120 - nbw, 92) if LANDSCAPE else (R - nbw, 300)
    s0 = len(c._layers)
    box(c, "nav", nx, ny, nbw, nbh, "#1a181f", r=10, parent=page, ip=28)
    box(c, "sign in", nx + 8, ny + 8, 130, nbh - 16, "white", r=6, parent=page, ip=28)
    label_text(c, "Sign In", "OT Body", 24, "ink", nx + 73, ny + nbh / 2 + CAP * 24 / 2, j=2, parent=page, ip=28)
    label_text(c, "Menu", "OT Body", 24, "white", nx + nbw - 70, ny + nbh / 2 + CAP * 24 / 2, j=1, parent=page, ip=28)
    c.shape("menu icon", [group([path([[nx + nbw - 52, ny + nbh / 2 + d], [nx + nbw - 28, ny + nbh / 2 + d]]),
                                 stroke(c_("white"), 2.4)]) for d in (-7, 0, 7)], parent=page, ip=28)
    members_opacity(layers_since(c, s0), [(28, 0, "settle-soft"), (36, 100)])
    # bottom-right block: the positioning line + the site's green button
    if LANDSCAPE:
        bx0, by0, bw = 1300, 790, 500
        fade_line(c, "Made by photographers,", "OT Body Medium", 40, "white", bx0, by0, start=36, parent=page)
        fade_line(c, "for photographers.", "OT Body Medium", 40, "white", bx0, by0 + 50, start=40, parent=page)
        bcx, bcy = bx0 + bw / 2, by0 + 140
    else:
        bw = 600
        fade_line(c, "Made by photographers,", "OT Body Medium", 46, "white", W / 2, 1210, j=2, start=36, parent=page)
        fade_line(c, "for photographers.", "OT Body Medium", 46, "white", W / 2, 1268, j=2, start=40, parent=page)
        bcx, bcy = W / 2, 1380
    s1 = len(c._layers)
    site_button(c, fonts, "Find a Photographer", bcx, bcy, width=bw, size=30, parent=page, ip=46)
    members_opacity(layers_since(c, s1), [(46, 0, "settle-soft"), (54, 100)])
    c.cue(46, "pop", 0.5)
    # the next section rises in underneath as the page scrolls (continuous carry into chapter 4)
    site_gradient(c, 0, H * GLOW_H, p=anim([(SCROLL_A, [0, H, 0], "scroll"), (SCROLL_B, [0, 0, 0])]),
                  ip=SCROLL_A)
    # ...carrying the section's headline in, still unloaded (ghost letters), exactly as chapter 4 opens
    nxt = c.null("next section", p=anim([(SCROLL_A, [0, H, 0], "scroll"), (SCROLL_B, [0, 0, 0])]), ip=SCROLL_A)
    l1, l2, hsz, hb1 = sideline_headline()
    for k, txt in enumerate((l1, l2)):
        c.text(f"ghost line {k + 1}", text_doc(txt, STATE, hsz, c_("white"), justify=2),
               p=(W / 2, hb1 + k * hsz * 0.98), o=GHOST, ip=SCROLL_A, parent=nxt)
    c.cue(SCROLL_A, "whoosh", 0.6)
    return c


# =========================================================================== 4 SIDELINE (site)
def scene_sideline():
    c = Comp("04 Every sideline shot starts with a search", W, H, 135)
    background(c)
    # the glow is where the hero's scroll left it (frame-exact carry), drifts, then scrolls away into black
    site_gradient(c, 0, H * GLOW_H, p=anim([(0, [0, 0, 0], "linear"), (104, [0, -0.08 * H, 0], "exit-accelerate"),
                                            (135, [0, -0.9 * H, 0])]))
    c.camera3d(zoom=1500 if LANDSCAPE else 1400)
    if LANDSCAPE:
        cards = [  # name, x, y, z, width, rx, ry, rz  (back to front)
            ("team-backs", 1390, 930, 260, 230, -20, -30, -10), ("heart-hands", 520, 930, 220, 210, 22, 26, 10),
            ("sepak-takraw", 1650, 250, 120, 340, -12, 38, 10), ("stretch-ball", 1760, 700, 40, 320, -16, -40, 12),
            ("kids-duel", 170, 650, -40, 320, 10, 44, -8), ("basketball", 270, 230, -120, 220, 18, -32, -14),
            ("smile-orange", 960, 110, -260, 280, 30, 0, 6)]
    else:
        cards = [
            ("team-backs", 790, 1640, 260, 260, -20, -30, -10), ("heart-hands", 300, 1580, 220, 250, 22, 26, 10),
            ("sepak-takraw", 900, 560, 120, 360, -12, 38, 10), ("stretch-ball", 960, 1270, 40, 340, -16, -40, 12),
            ("kids-duel", 110, 1190, -40, 330, 10, 44, -8), ("basketball", 190, 470, -120, 250, 18, -32, -14),
            ("smile-orange", 560, 300, -260, 300, 30, 0, 6)]
    cx0, cy0 = W / 2, H / 2
    for i, (name, x, y, z, w, rx, ry, rz) in enumerate(cards):
        file, (iw, ih) = P(name)
        sc = w * 1.25 / iw * 100
        t_in = 2 + i * 2
        phase = i * 1.3
        pk, rk = [], {"rx": [], "ry": [], "rz": []}
        # fly in from outside the frame and far away, then orbit slowly, then fly out
        pk.append((t_in, [cx0 + (x - cx0) * 1.7, cy0 + (y - cy0) * 1.7, z + 900], "entrance-sharp"))
        for f in range(t_in + 22, 105, 8):
            ph = 2 * math.pi * f / 230 + phase
            pk.append((f, [x + 46 * math.sin(ph), y + 34 * math.cos(ph * 1.1), z + 90 * math.sin(ph * 0.8)], "linear"))
        ph = 2 * math.pi * 104 / 230 + phase
        pk[-1] = (pk[-1][0], pk[-1][1], "exit-accelerate")
        pk.append((136, [cx0 + (x - cx0) * 2.2, cy0 + (y - cy0) * 1.6 - 0.9 * H, z - 300]))
        for f in [t_in] + list(range(t_in + 22, 105, 8)) + [136]:
            ph = 2 * math.pi * f / 230 + phase
            settle = 0 if f == t_in else 1
            rk["rx"].append((f, [rx + (1 - settle) * 25 + 6 * math.sin(ph)], "linear"))
            rk["ry"].append((f, [ry + (1 - settle) * 30 + 10 * math.sin(ph * 0.9)], "linear"))
            rk["rz"].append((f, [rz + 5 * math.cos(ph)], "linear"))
        ks = Comp.ks3(p=anim(pk), a=(iw / 2, ih / 2, 0), s=(sc, sc, 100), rx=anim(rk["rx"]), ry=anim(rk["ry"]),
                      rz=anim(rk["rz"]))
        c.image3d(f"card {name}", file, iw, ih, ks, ip=t_in)
    c.cue(2, "whoosh", 0.6)
    # the headline loads letter by letter (the site's Archivo opacity load)
    l1, l2, size, b1 = sideline_headline()
    up = [(104, 0, "exit-accelerate"), (135, -0.8 * H)]
    for k, (txt, s0, s1) in enumerate([(l1, 12, 62), (l2, 30, 84)]):
        b = b1 + k * size * 0.98
        c.text(f"sideline line {k + 1}", text_doc(txt, STATE, size, c_("white"), justify=2),
               p=anim([(k_[0], [W / 2, b + k_[1], 0]) + tuple(k_[2:]) for k_ in up]),
               animators=letter_reveal(s0, s1, ghost=GHOST),
               slot=f"sideline{k + 1}", label=f"Headline line {k + 1}")
        c.cue(s0, "tick", 0.5)
    c.cue(104, "whoosh", 0.5)
    curtain_close(c)   # the shutter catches the scroll mid-motion, like every other chapter seam
    return c


# =========================================================================== 5 CLIENTS CHASE YOU
def scene_clients():
    c = Comp("05 Now clients chase you", W, H, 150)
    background(c)
    feature_glow(c)
    sb = armature_headline(c, fonts, "NOW CLIENTS", "CHASE YOU.", "Clubs, brands and players search one place.")
    y0 = sb + 64
    g = c.null("search", p=anim([(16, [0, 40, 0], "entrance-sharp"), (28, [0, 0, 0])]), ip=16)
    s0 = len(c._layers)
    box(c, "search field", L, y0, CW, 110, "surface", r=16, parent=g, ip=16)
    search_icon(c, L + 52, y0 + 55, 40, parent=g, ip=16)
    query = "football photographer"
    gaps = [0, 2, 1, 1, 1, 2, 2, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1]
    tx, ty = L + 96, y0 + 55 + CAP * 40 / 2
    docs = [(16, text_doc("Search photographers", "OT Body", 40, hexc("#7d7a84"), justify=0))]
    t = 22
    for k in range(1, len(query) + 1):
        t += gaps[k - 1]
        docs.append((t, text_doc(query[:k], "OT Body", 40, c_("white"), justify=0)))
        c.cue(t, "key", 0.35)
    c.text("typed query", docs[0][1], p=(tx, ty), keyed_docs=docs, ip=16, parent=g)
    members_opacity(layers_since(c, s0), [(16, 0, "settle-soft"), (24, 100, "hold"), (84, 100, "exit-accelerate"),
                                          (92, 0)])
    y1 = y0 + 140
    y2 = y1 + 320
    ra = c.null("result A", p=anim([(50, [0, 200, 0], "entrance-sharp"), (64, [0, 0, 0], "hold"),
                                    (84, [0, 0, 0], "exit-accelerate"), (94, [0, -40, 0])]), ip=50, op=95)
    sa = len(c._layers)
    pic(c, "celebrate-fists", L, y1, CW, 300, r=18, parent=ra, ip=50, op=95)
    x = L + 22
    for sp in ("football", "track"):
        x += tag(c, fonts, sp, x, y1 + 300 - 58, 24, parent=ra, ip=50, op=95) + 10
    members_opacity(layers_since(c, sa), [(50, 100, "hold"), (84, 100, "exit-accelerate"), (92, 0)])
    rb = c.null("result B (you)", p=anim([(56, [0, 200, 0], "entrance-sharp"), (70, [0, 0, 0])]), ip=56)
    pic(c, "floodlight-profile", L, y2, CW, 300, r=18, parent=rb, ip=56, focus=(0.45, 0.3))
    box(c, "your profile chip", L + 22, y2 + 22, fonts.width("OT Body Medium", 26, "Your profile") + 36, 46, "green",
        r=8, parent=rb, ip=56)
    label_text(c, "Your profile", "OT Body Medium", 26, "ink", L + 40, y2 + 45 + CAP * 26 / 2, ip=56, parent=rb)
    x = L + 22
    for sp in ("football", "track", "rugby"):
        x += tag(c, fonts, sp, x, y2 + 300 - 58, 24, parent=rb, ip=56) + 10
    c.cue(50, "blip_in", 0.6)
    c.shape("you outline", [group([rect(CW + 16, 316, L + CW / 2, y2 + 150, 24), stroke(c_("green"), 5),
                                   {**trim(0, 100), "e": anim([(74, 0, "entrance-sharp"), (86, 100)])}])],
            ip=74, parent=rb)
    c.cue(74, "whoosh", 0.4)
    reqs = ["Sports club · season coverage?", "Brand shoot next Saturday?", "Can you shoot our final?"]
    for k, (txt, at) in enumerate(zip(reqs, (88, 102, 116))):
        yt = y0 + 10 + k * 136
        gt = c.null(f"request {k}", p=anim([(at, [0, -60, 0], "entrance-sharp"), (at + 10, [0, 0, 0])]), ip=at)
        s1 = len(c._layers)
        box(c, f"request card {k}", L, yt, CW, 112, "surface", r=22, parent=gt, ip=at,
            stroke_col=c_("white", 0.1), stroke_w=1.5)
        c.shape(f"request dot {k}", [group([ellipse(16, 16, L + 42, yt + 56), fill_("green")])], ip=at, parent=gt)
        label_text(c, txt, "OT Body Medium", 34, "white", L + 72, yt + 56 + CAP * 34 / 2, ip=at, parent=gt)
        label_text(c, "now", "OT Body", 26, GREY, R - 28, yt + 56 + CAP * 26 / 2, j=1, ip=at, parent=gt)
        members_opacity(layers_since(c, s1), [(at, 0, "settle-soft"), (at + 6, 100)])
        c.cue(at, "blip_in", 0.9)
    curtain_open(c)
    drift(c)
    curtain_close(c)
    return c


# =========================================================================== 6 PROFILE PAGE (site)
def scene_profile():
    c = Comp("06 Your portfolio, organised", W, H, 150)
    background(c)
    feature_glow(c)
    sb = armature_headline(c, fonts, "YOUR PORTFOLIO,", "ORGANISED.", "Your own page: packages, featured shots, dates.")
    y0 = sb + 60
    ph = BOTTOM - 30 - y0
    hb = ph * 0.42
    pg = c.null("profile page", p=anim([(16, [0, 300, 0], "settle-soft"), (32, [0, 0, 0])]), ip=16)
    box(c, "page", L, y0, CW, ph, "cream", r=14, parent=pg, ip=16)
    pic(c, "floodlight-profile", L, y0, CW, hb, r=14, parent=pg, ip=16, focus=(0.5, 0.3),
        zoom=[(16, 1.12, "settle-soft"), (150, 1.0)])
    c.shape("hero shade", [group([rect(CW, hb * 0.7, L + CW / 2, y0 + hb * 0.65),
                                   gradient([(0, "#000000"), (1, "#000000")], [0, y0 + hb * 0.3], [0, y0 + hb],
                                            alpha_stops=[(0, 0), (1, 0.7)])])], parent=pg, ip=16)
    av, ax, ay = 96, L + 28, y0 + hb - 226
    pic(c, "portrait-flare", ax, ay, av, av, r=av / 2, parent=pg, ip=20, focus=(0.5, 0.3))
    c.shape("avatar ring", [group([ellipse(av + 6, av + 6, ax + av / 2, ay + av / 2), stroke(c_("cream"), 4)])],
            parent=pg, ip=20)
    ns = fonts.fit(STATE, ["YOUR NAME"], CW - 60, 84)
    rise_line(c, fonts, "YOUR NAME", STATE, ns, "white", L + 28, y0 + hb - 52, j=0, start=24, parent=pg,
              slot="profileName", label="Profile name")
    fade_line(c, "Match days, finals and everything in between.", "OT Body", 24, "white", L + 28, y0 + hb - 18,
              start=30, parent=pg, o=85)
    stats = [("SPECIALISES IN", "Football"), ("PACKAGES FROM", PRICE), ("COVERS", "Island-wide")]
    for i, (lab, val) in enumerate(stats):
        sx = L + 28 + i * (CW - 56) / 3
        fade_line(c, lab, "OT Label", 18, INK55, sx, y0 + hb + 50, start=34 + i * 3, parent=pg)
        fade_line(c, val, "OT Body Medium", 32, "ink", sx, y0 + hb + 92, start=35 + i * 3, parent=pg)
    fade_line(c, "FEATURED", "OT Label", 30, "ink", L + 28, y0 + hb + 158, start=44, parent=pg)
    fy, fh = y0 + hb + 180, ph - hb - 180 - 24
    bw_ = (CW - 56 - 14) * 0.6
    sw_ = (CW - 56 - 14) - bw_
    for k, (name, x, y, w, h) in enumerate([("celebrate-fists", L + 28, fy, bw_, fh),
                                            ("tackle-night", L + 28 + bw_ + 14, fy, sw_, (fh - 12) / 2),
                                            ("stretch-ball", L + 28 + bw_ + 14, fy + (fh - 12) / 2 + 12, sw_,
                                             (fh - 12) / 2)]):
        at = 48 + k * 5
        pic(c, name, x, y, w, h, r=6, parent=pg, ip=at, rise=[(at, 60, "entrance-sharp"), (at + 14, 0)],
            zoom=[(at, 1.15, "settle-soft"), (at + 30, 1.03, "linear"), (150, 1.0)])
    c.cue(16, "whoosh", 0.5)
    c.cue(48, "whoosh", 0.3)
    curtain_open(c)
    drift(c)
    curtain_close(c)
    return c


# =========================================================================== 7 BOOKING: availability + packages (site)
def scene_booking():
    c = Comp("07 Booked at your rate", W, H, 165)
    background(c)
    feature_glow(c)
    sb = armature_headline(c, fonts, "BOOKED AT", "YOUR RATE.", "Pick a date, pick a package. No lowball DMs.")
    y0 = sb + 60
    # the lowball DM gets struck out and thrown away
    txt = "can do $30?"
    tw = fonts.width("OT Body", 42, txt)
    bh = 42 * 1.25 + 52
    lb = c.null("lowball", p=anim([(8, [0, 40, 0], "entrance-sharp"), (16, [0, 0, 0], "hold"),
                                   (30, [0, 0, 0], "exit-accelerate"), (40, [-1100, 0, 0])]), ip=8, op=41)
    s0 = len(c._layers)
    box(c, "lowball bubble", L, y0, tw + 68, bh, "surface", r=bh / 2, parent=lb, ip=8, op=41)
    label_text(c, txt, "OT Body", 42, "white", L + 34, y0 + bh / 2 + CAP * 42 / 2, parent=lb, ip=8, op=41)
    members_opacity(layers_since(c, s0), [(8, 0, "settle-soft"), (14, 100)])
    c.shape("strike", [group([path([[L + 26, y0 + bh / 2], [L + 42 + tw, y0 + bh / 2]]), stroke(c_("green"), 5),
                              {**trim(0, 100), "e": anim([(18, 0, "entrance-sharp"), (26, 100)])}])],
            ip=18, op=41, parent=lb)
    c.cue(8, "blip_in", 0.8)
    c.cue(18, "whoosh", 0.35)
    c.cue(30, "whoosh", 0.6)
    avail = BOTTOM - 30 - y0
    ch = avail * 0.53
    ink = c_("ink")
    # availability calendar panel
    cal = c.null("availability", p=anim([(36, [0, 300, 0], "settle-soft"), (52, [0, 0, 0])]), ip=36)
    box(c, "calendar panel", L, y0, CW, ch, PANEL, r=14, parent=cal, ip=36)
    label_text(c, "AVAILABILITY", "OT Label", 28, ink, L + 28, y0 + 50, parent=cal, ip=36)
    label_text(c, "NOVEMBER 2026", "OT Body Medium", 24, ink, R - 28, y0 + 48, j=1, parent=cal, ip=36)
    gx0, gw = L + 28, CW - 56
    cw_ = gw / 7
    hy = y0 + 92
    for k, d in enumerate("MTWTFSS"):
        label_text(c, d, "OT Body", 22, INK55, gx0 + cw_ * (k + 0.5), hy, j=2, parent=cal, ip=36)
    weeks = calendar.monthcalendar(2026, 11)
    rh = (ch - 120) / len(weeks)
    available = {21, 22, 28, 29}
    pick = 21
    pick_xy = None
    for r_, week in enumerate(weeks):
        for k, day in enumerate(week):
            if not day:
                continue
            dx, dy = gx0 + cw_ * (k + 0.5), hy + 22 + rh * (r_ + 0.5)
            at = 44 + r_ * 2
            if day in available:
                dot = min(cw_, rh) * 0.86
                c.shape(f"day {day}", [group([ellipse(dot, dot, dx, dy), fill_("green")])], parent=cal, ip=at)
                if day == pick:
                    pick_xy = (dx, dy, dot)
            label_text(c, str(day), "OT Body Medium" if day in available else "OT Body", 26, ink, dx,
                       dy + CAP * 26 / 2, j=2, parent=cal, ip=at, o=100 if day in available else 45)
    # picked date: ring pops on the tap
    px, py, pd = pick_xy
    ring = c.null("picked ring", p=(px, py), a=(px, py), parent=cal, ip=97,
                  s=anim([(97, [60, 60, 100], "expressive-pop"), (104, [112, 112, 100], "settle-soft"),
                          (110, [100, 100, 100])]))
    c.shape("picked", [group([ellipse(pd + 12, pd + 12, px, py), stroke(ink, 4)])], parent=ring, ip=97)
    # packages panel
    y1 = y0 + ch + 18
    ph2 = BOTTOM - 30 - y1
    pk = c.null("packages", p=anim([(46, [0, 300, 0], "settle-soft"), (62, [0, 0, 0])]), ip=46)
    box(c, "packages panel", L, y1, CW, ph2, PANEL, r=14, parent=pk, ip=46)
    label_text(c, "PACKAGES", "OT Label", 28, ink, L + 28, y1 + 50, parent=pk, ip=46)
    label_text(c, "Full match", "OT Body Medium", 34, ink, L + 28, y1 + 104, parent=pk, ip=46)
    label_text(c, PRICE, "OT Body Medium", 34, ink, R - 28, y1 + 104, j=1, parent=pk, ip=46)
    label_text(c, "90 mins · 40 edited photos · ready in 3 days", "OT Body", 24, INK55, L + 28, y1 + 140, parent=pk,
               ip=46)
    tag(c, fonts, "football", L + 28, y1 + 156, 20, parent=pk, ip=46)
    bty = y1 + ph2 - 92
    bcx, bcy = L + CW / 2, bty + 36
    btn = c.null("book button", p=(bcx, bcy), a=(bcx, bcy), parent=pk, ip=46,
                 s=anim([(46, [100, 100, 100], "hold"), (126, [96, 96, 100], "hold"), (130, [100, 100, 100])]))
    box(c, "book", L + 28, bty, CW - 56, 72, "green", r=10, parent=btn, ip=46)
    s1 = len(c._layers)
    label_text(c, "Book", "OT Body Medium", 30, "ink", bcx, bcy + CAP * 30 / 2, j=2, parent=btn, ip=46, op=136)
    from film_parts import arrow_icon
    arrow_icon(c, R - 28 - 40, bcy, 34, "ink", parent=btn, ip=46, op=136)
    members_opacity(layers_since(c, s1), [(46, 100, "hold"), (130, 100, "exit-accelerate"), (135, 0)])
    bw = fonts.width("OT Body Medium", 30, f"Booked · {JOB_DATE}")
    check_icon(c, bcx - bw / 2 - 26, bcy, 34, "ink", draw_at=134, parent=btn, ip=134)
    s2 = len(c._layers)
    label_text(c, f"Booked · {JOB_DATE}", "OT Body Medium", 30, "ink", bcx + 18, bcy + CAP * 30 / 2, j=2, parent=btn,
               ip=134)
    members_opacity(layers_since(c, s2), [(134, 0, "settle-soft"), (140, 100)])
    tap(c, px, py, appear=89, press=97)
    tap(c, bcx + 80, bcy + 4, appear=118, press=126)
    c.cue(36, "whoosh", 0.5)
    c.cue(37, "tick", 0.45)
    c.cue(134, "chime", 0.9)
    curtain_open(c)
    drift(c)
    curtain_close(c)
    return c


# =========================================================================== 8 HOW A BOOKING GOES (site 3D carousel)
def scene_steps():
    c = Comp("08 How a booking goes", W, H, 135)
    background(c)
    sb = armature_headline(c, fonts, "HOW A BOOKING", "GOES.", "Four steps, all on Outtakes.")
    c.camera3d(zoom=1500 if LANDSCAPE else 1400)
    steps = [("ONE", "1", "Call the photographer\rand agree on the shoot"),
             ("TWO", "2", "Book their package\rand date on Outtakes"),
             ("THREE", "3", "Pay once\rthey accept"),
             ("FOUR", "4", "Get shot, then get\ryour photos")]
    if LANDSCAPE:
        cw3, chh, ccx, ccy, spacing = 480, 600, (L + R) / 2, H / 2 + 10, 560
    else:
        top = sb + 70
        cw3, chh, spacing = 600, 700, 660
        ccx, ccy = W / 2, (top + BOTTOM) / 2 + 10
    # carousel position k(t): slide in, then advance one card at a time
    kk = [(0, -1.3, "travel-balanced"), (14, 0, "linear"), (40, 0.06, "travel-balanced"), (52, 1, "linear"),
          (70, 1.06, "travel-balanced"), (82, 2, "linear"), (100, 2.06, "travel-balanced"), (112, 3, "linear"),
          (135, 3.1, "linear")]
    for f in (0, 40, 70, 100):
        c.cue(f, "whoosh", 0.45)
    bright, dark = hexc("#74f260"), hexc("#3e9a37")
    for i, (word, num, body) in enumerate(steps):
        def at_k(k):
            d = i - k
            return d
        pk, ryk, colk, ok = [], [], [], []
        for f, k, e in kk:
            d = i - k
            pk.append((f, [ccx + d * spacing, ccy, abs(d) * 260], e))
            ryk.append((f, [max(-70, min(70, -d * 38))], e))
            m = min(1, abs(d))
            colk.append((f, [bright[j] + (dark[j] - bright[j]) * m for j in range(3)] + [1], e))
            vis = 0 if (LANDSCAPE and d <= -0.8) else (100 if (not LANDSCAPE or d >= -0.2) else 100 * (d + 0.8) / 0.6)
            ok.append((f, [max(0, min(100, vis))], e))
        n = c.null3d(f"card {word}", Comp.ks3(p=anim(pk), ry=anim(ryk)))
        s0 = len(c._layers)
        c.shape3d(f"card {word} face", [group([rect(cw3, chh, 0, 0, 14),
                                                {"ty": "fl", "c": anim(colk), "o": static(100), "r": 1}])],
                  Comp.ks3(), parent=n)
        c.text3d(f"card {word} numeral", text_doc(num, STATE, chh * 0.95, hexc("#111113"), justify=2),
                 Comp.ks3(p=(cw3 * 0.18, chh * 0.42, 0), o=8), parent=n)
        c.text3d(f"card {word} word", text_doc(word, STATE, cw3 * 0.2, hexc("#111113"), justify=0),
                 Comp.ks3(p=(-cw3 / 2 + 26, -chh / 2 + cw3 * 0.2 * 0.95, 0)), parent=n)
        c.text3d(f"card {word} body", text_doc(body, "OT Body", cw3 * 0.058, hexc("#111113"), justify=2,
                                               lh=cw3 * 0.058 * 1.25), Comp.ks3(p=(0, 0, 0)), parent=n)
        members = layers_since(c, s0)
        members_opacity(members, [(f, v[0], e) for f, v, e in ok])
        members[1]["ks"]["o"] = anim([(f, v[0] * 0.09, e) for f, v, e in ok])
    curtain_open(c)
    curtain_close(c)
    return c


# =========================================================================== 9 INVOICES
def scene_invoices():
    c = Comp("09 Invoices, done for you", W, H, 120)
    background(c)
    feature_glow(c)
    sb = armature_headline(c, fonts, "INVOICES,", "DONE FOR YOU.", "Proper invoices for every client, big or small.")
    y0 = sb + 56
    ph = min(760, BOTTOM - 20 - y0)
    pcx, pcy = W / 2 if not LANDSCAPE else (L + R) / 2, y0 + ph / 2
    paper = c.null("invoice", p=anim([(16, [pcx, pcy + 320, 0], "settle-soft"), (32, [pcx, pcy, 0])]), a=(pcx, pcy),
                   r=anim([(16, -5, "settle-soft"), (32, 0)]), ip=16)
    box(c, "paper", L, y0, CW, ph, "cream", r=12, parent=paper, ip=16)
    ink = c_("ink")
    rows = [("INVOICE", TITLE, 54, ink, L + 50, 100, 26, 0), ("#OT-0142", "OT Body", 28, INK55, R - 50, 94, 28, 1),
            ("BILLED TO", "OT Label", 24, INK55, L + 50, 176, 34, 0), ("Sports club", "OT Body Medium", 36, ink, L + 50, 222, 35, 0),
            ("DATE", "OT Label", 24, INK55, L + 480 if not LANDSCAPE else L + 440, 176, 36, 0),
            ("21 Nov 2026", "OT Body Medium", 36, ink, L + 480 if not LANDSCAPE else L + 440, 222, 37, 0),
            ("Full match coverage", "OT Body", 32, ink, L + 50, 334, 44, 0), (PRICE_DEC, "OT Body Medium", 32, ink, R - 50, 334, 45, 1),
            ("Edited photos (40)", "OT Body", 32, ink, L + 50, 396, 48, 0), ("Included", "OT Body Medium", 32, ink, R - 50, 396, 49, 1),
            ("Total", "OT Body Medium", 36, ink, L + 50, 524, 56, 0), (PRICE_DEC, TITLE, 50, ink, R - 50, 528, 58, 1),
            ("PAYMENT", "OT Label", 24, INK55, L + 50, 620, 62, 0), ("Due on booking", "OT Body", 32, ink, L + 50, 664, 64, 0)]
    for text, font, size, col, x, dy, st, j in rows:
        fade_line(c, text, font, size, col, x, y0 + dy, j=j, start=st, parent=paper)
    box(c, "rule 1", L + 50, y0 + 266, CW - 100, 2, hexc("#111113", 0.14), parent=paper, ip=40)
    box(c, "rule 2", L + 50, y0 + 444, CW - 100, 2, hexc("#111113", 0.14), parent=paper, ip=52)
    sx, sy = R - 150, y0 + 640
    stamp = c.null("sent stamp", p=(sx, sy), a=(sx, sy), parent=paper, ip=86,
                   s=anim([(86, [55, 55, 100], "expressive-pop"), (94, [108, 108, 100], "settle-soft"),
                           (100, [100, 100, 100])]))
    box(c, "sent pill", sx - 95, sy - 36, 190, 72, "green", r=36, parent=stamp, ip=86)
    check_icon(c, sx - 46, sy, 34, "ink", draw_at=89, parent=stamp, ip=86)
    label_text(c, "Sent", "OT Body Medium", 34, "ink", sx + 20, sy + CAP * 34 / 2, j=2, parent=stamp, ip=86)
    c.cue(16, "whoosh", 0.5)
    c.cue(86, "chime", 0.9)
    curtain_open(c)
    drift(c)
    curtain_close(c)
    return c


# =========================================================================== 10 SECURE PAYMENTS
def scene_payments():
    c = Comp("10 Paid, even if they cancel", W, H, 135)
    background(c)
    feature_glow(c)
    sb = armature_headline(c, fonts, "PAID. EVEN IF", "THEY CANCEL.", "Secure payments make sure you get paid.")
    y0 = sb + 56
    c1 = c.null("payment card", p=anim([(16, [0, 260, 0], "settle-soft"), (30, [0, 0, 0])]), ip=16)
    box(c, "card 1", L, y0, CW, 350, "surface", r=28, parent=c1, ip=16)
    c.shape("lock badge", [group([ellipse(96, 96, L + 96, y0 + 84), fill_("green")])], parent=c1, ip=16)
    lock_icon(c, L + 96, y0 + 86, 44, "ink", parent=c1, ip=16)
    label_text(c, "Payment secured", "OT Body Medium", 40, "white", L + 170, y0 + 84 + CAP * 40 / 2, parent=c1, ip=16)
    fade_line(c, PRICE_DEC, TITLE, 84, "white", L + 48, y0 + 250, start=26, parent=c1)
    fade_line(c, f"{JOB_DATE} · Jalan Besar Stadium", "OT Body", 28, GREY, L + 48, y0 + 306, start=30, parent=c1)
    c.cue(16, "whoosh", 0.5)
    c.cue(26, "chime_soft", 0.6)
    yb = y0 + 380
    c2 = c.null("cancel card", p=anim([(56, [0, 260, 0], "settle-soft"), (70, [0, 0, 0])]), ip=56)
    box(c, "card 2", L, yb, CW, 330, "surface", r=28, parent=c2, ip=56)
    label_text(c, "Client cancelled the booking", "OT Body", 34, "white", L + 48, yb + 76, parent=c2, ip=56, o=75)
    box(c, "card 2 rule", L + 48, yb + 118, CW - 96, 1.5, c_("white", 0.1), parent=c2, ip=56)
    c.shape("check badge", [group([ellipse(80, 80, L + 88, yb + 216), fill_("green")])], parent=c2, ip=56)
    check_icon(c, L + 88, yb + 217, 40, "ink", draw_at=84, parent=c2, ip=84)
    label_text(c, "Cancellation fee", "OT Body Medium", 40, "white", L + 152, yb + 206, parent=c2, ip=56)
    fade_line(c, "Paid to you", "OT Body Medium", 34, "green", L + 152, yb + 256, start=86, parent=c2)
    c.cue(56, "blip_in", 0.7)
    c.cue(86, "chime", 0.9)
    curtain_open(c)
    drift(c)
    curtain_close(c)
    return c


# =========================================================================== 11 EXPOSURE
def scene_exposure():
    c = Comp("11 Free exposure, built in", W, H, 135)
    background(c)
    feature_glow(c)
    sb = armature_headline(c, fonts, "FREE EXPOSURE,", "BUILT IN.", "Shot of the Week puts you in front of clients.")
    y0 = sb + 56
    mh = 520
    pic(c, "portrait-flare", L, y0, CW, mh, r=8, ip=16, focus=(0.5, 0.3),
        rise=[(16, 90, "entrance-sharp"), (30, 0, "linear")], zoom=[(16, 1.12, "settle-soft"), (135, 1.0)])
    c.shape("photo shade", [group([rect(CW, 260, L + CW / 2, y0 + mh - 130),
                                    gradient([(0, "#000000"), (1, "#000000")], [0, y0 + mh - 260], [0, y0 + mh],
                                             alpha_stops=[(0, 0), (1, 0.65)])])], ip=16)
    rise_line(c, fonts, "SHOT OF THE WEEK", TITLE, 46, "white", L + 36, y0 + mh - 40, j=0, start=26,
              slot="sotw", label="Feature title")
    fx, fy = L + 36, y0 + 34
    fw = fonts.width("OT Body Medium", 28, "Featured") + 40
    feat = c.null("featured chip", p=(fx + fw / 2, fy + 24), a=(fx + fw / 2, fy + 24), ip=84,
                  s=anim([(84, [55, 55, 100], "expressive-pop"), (92, [108, 108, 100], "settle-soft"),
                          (98, [100, 100, 100])]))
    box(c, "featured", fx, fy, fw, 48, "green", r=8, parent=feat, ip=84)
    label_text(c, "Featured", "OT Body Medium", 28, "ink", fx + fw / 2, fy + 24 + CAP * 28 / 2, j=2, parent=feat, ip=84)
    ys = y0 + mh + 20
    sh = BOTTOM - 70 - ys
    strip = c.null("nominees strip", p=anim([(44, [0, 220, 0], "settle-soft"), (58, [0, 0, 0])]), ip=44)
    box(c, "cream strip", L, ys, CW, sh, "cream", r=8, parent=strip, ip=44)
    label_text(c, "SHOT OF THE WEEK NOMINEES", "OT Label", 24, "ink", L + 30, ys + 46, parent=strip, ip=44)
    tw_ = (CW - 60 - 2 * 16) / 3
    th = sh - 120
    for i, (name, title) in enumerate([("point-orange", "MATCH POINT"), ("kids-duel", "FINALS"),
                                       ("stretch-ball", "TOUCH")]):
        at = 54 + i * 4
        tx = L + 30 + i * (tw_ + 16)
        pic(c, name, tx, ys + 66, tw_, th, ip=at, parent=strip, rise=[(at, 60, "entrance-sharp"), (at + 12, 0)])
        label_text(c, title, TITLE, 20, "ink", tx, ys + 66 + th + 30, parent=strip, ip=at)
    c.cue(16, "whoosh", 0.5)
    c.cue(44, "whoosh", 0.35)
    c.cue(84, "chime", 0.8)
    curtain_open(c)
    drift(c)
    curtain_close(c)
    return c


# =========================================================================== 12 DATES
def scene_dates():
    c = Comp("12 Sign up free - 16 Nov - 22.11 5PM", W, H, 165)
    background(c)
    glow(c, W / 2, H + 260, 1300 if not LANDSCAPE else 1150, colors=[(0, COL["green"]), (0.5, "#1d4a20"), (1, COL["bg"])],
         alphas=(0.42, 0.2, 0.0))
    statement(c, "SIGN UP", "FREE.", 6, slots=("cta1", "cta2"), labels=("Sign-up line 1", "Sign-up line 2"),
              exit_at=46, port_max=300, land_max=300)
    if LANDSCAPE:
        s2 = fonts.fit(STATE, ["SET UP YOUR PROFILE", "FROM 16 NOV."], 1560, 210)
        b1 = H / 2 - s2 * 0.08
        rise_line(c, fonts, "SET UP YOUR PROFILE", STATE, s2, "white", W / 2, b1, j=2, start=54, exit_at=100,
                  slot="setup1", label="Setup line 1")
        rise_pair(c, fonts, "FROM", "16 NOV.", STATE, s2, W / 2, b1 + s2 * 0.98, start=62, exit_at=102,
                  slot1="setup2", slot2="profilesOpen", label1="Setup line 2", label2="Profiles-open date")
    else:
        lines = ["SET UP YOUR", "PROFILE FROM", "16 NOV."]
        s2 = fonts.fit(STATE, lines, 860, 220)
        b0 = H / 2 - s2 * 0.98 + CAP * s2 / 2
        for i, ln in enumerate(lines):
            rise_line(c, fonts, ln, STATE, s2, "green" if i == 2 else "white", W / 2, b0 + i * s2 * 0.98, j=2,
                      start=54 + i * 7, exit_at=100 + i * 2, slot="profilesOpen" if i == 2 else f"setup{i + 1}",
                      label="Profiles-open date" if i == 2 else f"Setup line {i + 1}")
    c.cue(54, "tick", 0.6)
    c.cue(100, "riser:14", 0.7)
    crash = 114
    dsize = fonts.fit(STATE, ["22.11"], 900 if LANDSCAPE else 840, 440)
    dcy = H / 2 - (40 if LANDSCAPE else 80)
    wordmark_crash(c, "22.11", STATE, dsize, W / 2, dcy, crash, 165, color="green", start_scale=320,
                   settle_end_scale=95, slot="liveDate", label="Live date")
    rise_line(c, fonts, "WE GO LIVE · 5PM SGT", "OT Body Medium", 56, "white", W / 2, dcy + CAP * dsize / 2 + 110, j=2,
              start=124, slot="liveLine", label="Live time line")
    flash(c, crash, peak=25, dur=3)
    c.cue(crash, "boom", 1.0)
    c.cue(crash, "shutter_big", 0.9)
    curtain_open(c)
    drift(c)
    curtain_close(c)
    return c


# =========================================================================== 13 GET IN THE FRAME (site 3D wall) + footer
def scene_frame():
    c = Comp("13 Get in the frame", W, H, 165)
    background(c)
    Z = 1500 if LANDSCAPE else 1300
    c.camera3d(zoom=Z)
    fin = 104   # footer cut
    names = ["tackle-night", "basketball", "sepak-takraw", "celebrate-fists", "motion-blur", "team-talk",
             "heart-hands", "number-10", "kids-duel", "point-orange", "smile-orange", "stretch-ball"]
    D = 1150 if LANDSCAPE else 600      # wall distance from the centre line (world px)
    PWW, PHW = 700, 875                 # panel size in the world (4:5)
    YAW = 72                            # 90 = flat along the wall, 0 = facing the camera
    rows = (-940, 0, 940)
    step, slots = 760, 8
    travel = 1.3 * step                 # how far the walls glide toward the camera before the footer
    speed = travel / fin
    panels = []
    for side, sgn in (("L", -1), ("R", 1)):
        for k in range(slots):
            z0 = -150 + k * step + (0 if side == "L" else step / 2)
            for r_, dy in enumerate(rows):
                panels.append((z0, side, sgn, dy, k, r_))
    panels.sort(key=lambda q: -q[0])   # farthest first (Skottie draws 3D layers in layer order)

    def fog(z):  # far panels fade in out of the dark
        return max(0.0, min(100.0, (4900 - z) / 1100 * 100))

    for z0, side, sgn, dy, k, r_ in panels:
        name = names[(k * 5 + r_ * 4 + (0 if side == "L" else 6)) % len(names)]
        file = panel_photo(name)
        # retire a panel once it has slid past the frame edge, well before the camera plane
        f_out = fin if z0 - travel > -650 else int((z0 + 650) / speed) + 1
        if f_out <= 0:
            continue
        fr = sorted(set([0, f_out] + list(range(0, f_out, 8))))
        x = W / 2 + sgn * D
        ks = Comp.ks3(p=anim([(f, [x, H / 2 + dy, z0 - speed * f], "linear") for f in fr]),
                      a=(PANEL_W / 2, PANEL_H / 2, 0), s=(PWW / PANEL_W * 100,) * 2 + (100,), ry=sgn * YAW,
                      o=anim([(f, [fog(z0 - speed * f)], "linear") for f in fr]))
        c.image3d(f"wall {side}{k} row{r_} {name}", file, PANEL_W, PANEL_H, ks, op=min(f_out, fin))
    c.shape("wall shade", [group([rect(W, H, W / 2, H / 2),
                                   gradient([(0, "#111113"), (1, "#111113")], [W / 2, H / 2], [W / 2 + W * 0.62, H / 2],
                                            kind=2, alpha_stops=[(0, 0.86), (0.5, 0.5), (1, 0)])])], op=fin)
    c.cue(0, "whoosh", 0.6)
    if LANDSCAPE:
        hs = fonts.fit(STATE, ["GET IN THE FRAME"], 1200, 220)
        rise_line(c, fonts, "GET IN THE FRAME", STATE, hs, "white", W / 2, 330, j=2, start=6, op=fin, slot="frame",
                  label="Get in the frame")
        sub_y, b1y, b2y, bw = 330 + 76, 640, 735, 470
    else:
        hs = fonts.fit(STATE, ["GET IN", "THE FRAME"], 800, 250)
        rise_line(c, fonts, "GET IN", STATE, hs, "white", W / 2, 640, j=2, start=6, op=fin, slot="frame1",
                  label="Get in the frame 1")
        rise_line(c, fonts, "THE FRAME", STATE, hs, "white", W / 2, 640 + hs * 0.98, j=2, start=14, op=fin,
                  slot="frame2", label="Get in the frame 2")
        sub_y, b1y, b2y, bw = 640 + hs * 0.98 + 90, 1240, 1350, 600
    fade_line(c, "Photographers, show your work and take bookings.", "OT Body", 32, "white", W / 2, sub_y, j=2,
              start=26, op=fin, o=88)
    fade_line(c, "Clients, find someone for your next match in minutes.", "OT Body", 32, "white", W / 2, sub_y + 42,
              j=2, start=30, op=fin, o=88)
    for lab, style, by, at in (("Join as Photographer", "green", b1y, 40), ("Look for Photographer", "white", b2y, 44)):
        g = c.null(f"{lab} btn", p=(W / 2, by), a=(W / 2, by), ip=at, op=fin,
                   s=anim([(at, [80, 80, 100], "expressive-pop"), (at + 8, [103, 103, 100], "settle-soft"),
                           (at + 14, [100, 100, 100], "hold")] +
                          ([(92, [100, 100, 100], "hold"), (93, [95, 95, 100], "hold"), (97, [100, 100, 100])]
                           if style == "green" else [(at + 15, [100, 100, 100])])))
        s0 = len(c._layers)
        site_button(c, fonts, lab, W / 2, by, width=bw, size=30, style=style, parent=g, ip=at, op=fin)
        members_opacity(layers_since(c, s0), [(at, 0, "settle-soft"), (at + 6, 100)])
    c.cue(40, "pop", 0.5)
    tap(c, W / 2 + bw / 2 - 60, b1y + 4, appear=84, press=93)
    # footer (site): cream page, giant green OUTTAKES
    c.shape("footer", [group([rect(W, H, W / 2, H / 2), fill_("cream")])], ip=fin)
    flash(c, fin, peak=30, dur=3)
    c.cue(fin, "shutter_big", 0.9)
    c.cue(fin, "boom_small", 0.5)
    ink = c_("ink")
    if LANDSCAPE:
        gs = fonts.fit(STATE, ["OUTTAKES"], W * 1.0, 700)
        gb = H + gs * 0.05
        tx, ty, j, us = 120, 200, 0, 84
    else:
        gs = fonts.fit(STATE, ["OUTTAKES"], W * 0.96, 520)
        gb = 1440
        tx, ty, j, us = W / 2, 800, 2, 84
    c.text("footer wordmark", text_doc("OUTTAKES", STATE, gs, c_("green"), justify=2), ip=fin,
           p=anim([(fin, [W / 2, gb + gs * 0.5, 0], "settle-soft"), (fin + 18, [W / 2, gb, 0], "linear"),
                   (165, [W / 2, gb - 10, 0])]), slot="endBrand", label="Footer wordmark")
    us = fonts.fit(TITLE, ["outtakes.sg"], 760, us)
    fade_line(c, "Sign up free at", "OT Body", 44, INK55, tx, ty, j=j, start=fin + 8)
    fade_line(c, "outtakes.sg", TITLE, us, ink, tx, ty + 30 + us, j=j, start=fin + 10)
    fade_line(c, "Live 22.11 · 5PM SGT", "OT Body Medium", 44, ink, tx, ty + 100 + us, j=j, start=fin + 14)
    curtain_open(c)
    curtain_close(c, dur=6)
    return c


SCENES = [scene_hook, scene_problem, scene_hero, scene_sideline, scene_clients, scene_profile, scene_booking,
          scene_steps, scene_invoices, scene_payments, scene_exposure, scene_dates, scene_frame]


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    cues, offset, meta = [], 0, []
    for n, fn in enumerate(SCENES, start=1):
        c = fn()
        doc = c.build(fonts)
        d = OUT / f"scene-{n}"
        d.mkdir()
        (d / "lottie.json").write_text(json.dumps(doc, separators=(",", ":")))
        (d / "controls.json").write_text(json.dumps({"controls": c.controls}, indent=2))
        for a in c.assets:
            shutil.copy(PHOTOS / a["p"], d / a["p"])
        for fam in c.fonts_used:
            shutil.copy(FONTS_DIR / fonts.files[fam], d / fonts.files[fam])
        for f, kind, gain in c.cues:
            cues.append({"frame": offset + f, "kind": kind, "gain": gain})
        meta.append({"scene": n, "name": c.name, "frames": c.frames, "start": offset})
        print(f"scene-{n}: {c.name:44s} {c.frames:4d}f  layers={len(doc['layers']):3d}  assets={len(c.assets)}")
        offset += c.frames
    (OUT / "cues.json").write_text(json.dumps({"fps": 30, "total": offset, "scenes": meta,
                                               "cues": sorted(cues, key=lambda x: x["frame"])}, indent=1))
    print(f"total {offset} frames = {offset / 30:.1f}s")


if __name__ == "__main__":
    main()
