"""Author the Outtakes launch film as Lottie scenes for the text-to-lottie player.

    python3 tools/build_film.py                        # portrait  -> public/projects/outtakes-launch/scene-1..12
    OT_FORMAT=landscape python3 tools/build_film.py    # landscape -> public/projects/outtakes-launch-16x9/scene-1..12

v4: rebuilt for the REDESIGNED website (Nov 2026: light editorial pages, neon green, film-strip dividers, duotone
sport cards, the new profile page, the photographer Studio, holographic step cards) and directed as one case
followed end to end instead of a feature tour:

  the shot -> the DMs -> OUTTAKES -> set up your Studio -> your profile -> clients find you -> booked at your
  rate -> paid, even if they cancel -> your shot, featured -> how a booking goes -> get in the frame -> footer

Craft notes (motionmaxxing references: ui-demo.md, transitions.md, judgment.md):
* hook = a photographer's focus point hopping subject to subject (ball, ball, ball ... face), locking green on
  each shutter; the last shot is the one that comes back as Shot of the Week (a carried object across the film)
* UI is built as 3D planes (Lottie camera + ddd layers) with real perspective and soft drop shadows, magnified
  so copy reads on a phone, and driven by a custom cursor with press physics
* each feature beat states its claim big, then a surface rises over it with the proof (occlusion), or shows the
  proof first and lands the claim after
* seams: shutter flashes, the site's film strip as a wipe, a fly-through, whips, and the site's green glow
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
import film_parts as fp  # noqa: E402
from lottie_kit import CAP, Comp, Fonts, anim, ease_value, ellipse, gradient, group, path, rect, static, text_doc  # noqa: E402
from parts4 import (Plane, brackets, button, col, cursor, film_strip, fl, gblur, ground, group3d, soft_vignette,  # noqa: E402
                    st, statement, txt, with_fx)

from parts4 import C as PALETTE  # noqa: E402
fp.COL.update(PALETTE)  # the redesign's palette (neon green, ink, greys) for the shared helpers
W, H, LANDSCAPE = fp.W, fp.H, fp.LANDSCAPE

ROOT = Path(__file__).resolve().parent.parent
PHOTOS = ROOT / "brand" / "photos"
FONTS_DIR = ROOT / "brand" / "fonts"
OUT = ROOT / "public" / "projects" / ("outtakes-launch-16x9" if LANDSCAPE else "outtakes-launch")
fonts = Fonts(FONTS_DIR)
META = json.loads((PHOTOS / "v4-meta.json").read_text())
SIZES = {p.name: Image.open(p).size for p in list(PHOTOS.glob("*.jpg")) + list(PHOTOS.glob("*.png"))}

STATE, TITLE, BODY, MED = "OT Wordmark", "OT Display", "OT Body", "OT Body Medium"
SHADOW = dict(opacity=70, distance=40, softness=150, color="#1d2a33")
SHADOW_SOFT = dict(opacity=45, distance=22, softness=90, color="#1d2a33")

# UI plane placement: designed at portrait size, scaled into the right half in landscape
if LANDSCAPE:
    UI_X, UI_Y, UI_S = 1385, 545, 0.82
    ST_X, ST_W = 120, 740
else:
    UI_X, UI_Y, UI_S = 540, 990, 1.0

YOUR = "Your name"
PRICE = "S$70"


def sz(name):
    return SIZES[name]


def flat_pt(cx, cy, w, h, lx, ly, s=None):
    """Screen position of a plane-local point while the plane is flat at z=0."""
    s = UI_S if s is None else s
    return cx + (lx - w / 2) * s, cy + (ly - h / 2) * s


def members_opacity(layers, keys):
    for lyr in layers:
        lyr["ks"]["o"] = anim(keys)


def since(c, n):
    return c._layers[n:]


def claim(c, lines, start=6, colors=None, slots=None, exit_at=None):
    """The feature's claim, big. Portrait: centred, to be covered by the rising UI. Landscape: left column."""
    colors = colors or ["ink"] * (len(lines) - 1) + ["gtext"]
    if LANDSCAPE:
        return statement(c, fonts, lines, start, colors=colors, x=ST_X, j=0, max_w=ST_W, max_size=200,
                         center_y=H / 2, slots=slots, exit_at=exit_at)
    return statement(c, fonts, lines, start, colors=colors, center_y=720, max_w=900, max_size=230, slots=slots,
                     exit_at=exit_at)


def rise_plane(c, name, w, h, t0, dur=22, ip=None, op=None, z0=260, rx0=16, drop=None, drift=34, whip=None):
    """A UI plane that rises from below with a tilt, settles flat at z=0 (UI_X, UI_Y), then keeps drifting up slowly
    so a held frame stays alive. whip = (frame, dx, dy) for an accelerating exit. pl.center_at(f) gives its centre."""
    drop = drop if drop is not None else (H * 0.75 if not LANDSCAPE else H * 0.9)
    settle = t0 + dur
    end = whip[0] if whip else c.frames
    keys = [(t0, [UI_X, UI_Y + drop, z0], "settle-soft"), (settle, [UI_X, UI_Y, 0], "linear"),
            (end, [UI_X, UI_Y - drift, 0])]
    if whip:
        keys[-1] = (end, [UI_X, UI_Y - drift, 0], "exit-accelerate")
        keys.append((end + 9, [UI_X + whip[1] * W, UI_Y - drift + whip[2] * H, 0]))
    rx = anim([(t0, rx0, "settle-soft"), (settle, 0)])
    pl = Plane(c, name, w, h, anim(keys), rx=rx, s=(UI_S * 100, UI_S * 100, 100), ip=t0 if ip is None else ip, op=op)
    pl.center_at = lambda f: (UI_X, UI_Y - drift * max(0.0, min(1.0, (f - settle) / max(1, end - settle))))
    return pl


def whip_out(plane_ind, c, t0, dx=-1.25, dy=0.0, dur=9):
    """Accelerating exit of a plane (the cut lands at peak velocity)."""
    for lyr in c._layers:
        if lyr["ind"] == plane_ind:
            p = lyr["ks"]["p"]
            keys = p["k"] if p.get("a") else None
            start = keys[-1]["s"] if keys else p["k"]
            new = [
                {"t": t0, "s": list(start), "o": {"x": [1.0] * 3, "y": [0.02] * 3}, "i": {"x": [0.54] * 3, "y": [0.42] * 3}},
                {"t": t0 + dur, "s": [start[0] + dx * W, start[1] + dy * H, start[2]]}]
            if keys:
                lyr["ks"]["p"] = {"a": 1, "k": [k for k in keys if k["t"] < t0] + new}
            else:
                lyr["ks"]["p"] = {"a": 1, "k": new}
            return


def panel_photo(name, w=800, h=1000):
    out = PHOTOS / f"panel-{name}.jpg"
    if not out.exists():
        im = Image.open(PHOTOS / f"{name}.jpg").convert("RGB")
        iw, ih = im.size
        k = max(w / iw, h / ih)
        cw, chh = w / k, h / k
        x0, y0 = (iw - cw) / 2, (ih - chh) / 2
        im.crop((round(x0), round(y0), round(x0 + cw), round(y0 + chh))).resize((w, h), Image.LANCZOS).save(
            out, quality=86)
    SIZES[out.name] = (w, h)
    return out.name


def wordmark_crash(c, text, size, cx, cy, crash, end, color="white", streaks=4, start_scale=340, parent=None,
                   settle_end=96, slot=None, label=None):
    cap = CAP * size
    doc = text_doc(text, STATE, size, col(color), justify=2)
    k_main = [(crash, [start_scale, start_scale, 100], "crash"), (crash + 14, [100, 100, 100], "linear"),
              (end, [settle_end, settle_end, 100])]
    for k in range(streaks, 0, -1):
        at6 = start_scale + (100 - start_scale) * ease_value("crash", 6 / 14)
        sc0 = start_scale * (1 + 0.16 * k)
        c.text(f"streak {k}", doc, p=(cx, cy), a=(0, -cap / 2), ip=crash, op=crash + 7, parent=parent,
               s=anim([(crash, [sc0, sc0, 100], "crash"), (crash + 6, [at6, at6, 100])]),
               o=anim([(crash, 22, "settle-soft"), (crash + 6, 0)]))
    return c.text(f"crash: {text}", doc, p=(cx, cy), a=(0, -cap / 2), ip=crash, parent=parent, s=anim(k_main),
                  slot=slot, label=label)


# =========================================================================== 1 HOOK: the photographer's eye
def scene_hook():
    c = Comp("01 Hook - the photographer's eye", W, H, 150)
    ground(c, "#000000")
    shots = META["landscape" if LANDSCAPE else "portrait"]
    cuts = [3, 17, 29, 40, 50, 59, 67, 74, 80]
    end = 150
    shot_at = 93  # the decisive frame on the last subject
    pos, scl, colk = [], [], []
    prev = None
    for i, sh in enumerate(shots):
        t0 = cuts[i]
        t1 = cuts[i + 1] if i + 1 < len(cuts) else end
        last = i == len(shots) - 1
        sx, sy = sh["subject"]
        base = 100 / 1.1
        push = 1.07 if last else 1.03
        ind = c.image(f"shot {sh['name']}", sh["file"], sh["w"], sh["h"], p=(sx, sy), a=(sx * 1.1, sy * 1.1),
                      s=anim([(t0, [base, base, 100], "settle-soft" if last else "linear"),
                              (t1, [base * push, base * push, 100])]), ip=t0, op=t1)
        with_fx(c, ind, gblur(anim([(t0, [18], "settle-soft"), (t0 + 3, [0])])))
        fp.flash(c, t0, peak=18, dur=2)
        c.cue(t0, "shutter", 0.42 + 0.4 * i / len(shots))
        S = max(130, min(330, sh["subject_size"] * 1.3))
        dur = t1 - t0
        if last:
            arrive, lock, contract = t0 + 3, t0 + 9, t0 + 11
        elif dur >= 9:
            arrive, lock, contract = t0 + 3, t0 + 5, t0 + 7
        else:
            arrive, lock, contract = t0 + 2, t0 + 2, t0 + 3
        if prev is None:
            pos.append((t0, [sx, sy, 0], "hold"))
            scl.append((t0, [S * 1.6, S * 1.6, 100], "crash"))
        else:
            pos.append((t0 - 2, prev[0], "crash"))
            pos.append((arrive, [sx, sy, 0], "hold"))
            scl.append((t0 - 2, [prev[1] * 0.9, prev[1] * 0.9, 100], "crash"))
            scl.append((arrive, [S * 1.18, S * 1.18, 100], "hold" if lock > arrive else "crash"))
        if lock > arrive or prev is None:
            scl.append((lock, [S * 1.18, S * 1.18, 100], "crash"))
        scl.append((contract, [S * 0.9, S * 0.9, 100], "hold"))
        colk.append((lock, "green", "hold"))
        if not last:
            colk.append((t1 - 2, "white", "hold"))
        c.cue(lock, "af", 0.5)
        prev = ([sx, sy, 0], S)
    pos.append((end, prev[0]))
    scl.append((end, [prev[1] * 0.9, prev[1] * 0.9, 100]))
    colk.insert(0, (cuts[0], "white", "hold"))
    fb = brackets(c, pos, scl, colk, ip=cuts[0], op=shot_at + 12)
    for lyr in c._layers:
        if lyr["ind"] == fb:
            lyr["ks"]["o"] = anim([(shot_at + 2, 100, "exit-accelerate"), (shot_at + 10, 0)])
    # the decisive frame
    fp.flash(c, shot_at, peak=38, dur=3)
    c.cue(shot_at, "shutter_big", 1.0)
    c.cue(shot_at, "boom_small", 0.4)
    lh = 620 if LANDSCAPE else 1000
    c.shape("legibility", [group([rect(W, lh, W / 2, H - lh / 2),
                                   gradient([(0, "#000000"), (1, "#000000")], [W / 2, H - lh], [W / 2, H],
                                            alpha_stops=[(0, 0), (0.55, 0.5), (1, 0.82)])])], ip=shot_at)
    if LANDSCAPE:
        size = fonts.fit(STATE, ["YOU GOT THE SHOT."], 1500, 220)
        fp.rise_pair(c, fonts, "YOU GOT", "THE SHOT.", STATE, size, W / 2, H - 110, start=shot_at + 9,
                     gap_frames=9, slot1="hook1", slot2="hook2", label1="Hook line 1", label2="Hook line 2")
    else:
        size = fonts.fit(STATE, ["YOU GOT", "THE SHOT."], 860, 240)
        b2 = 1440
        fp.rise_line(c, fonts, "YOU GOT", STATE, size, "white", W / 2, b2 - size * 0.96, j=2, start=shot_at + 9,
                     slot="hook1", label="Hook line 1")
        fp.rise_line(c, fonts, "THE SHOT.", STATE, size, "green", W / 2, b2, j=2, start=shot_at + 18,
                     slot="hook2", label="Hook line 2")
    c.cue(shot_at + 9, "tick", 0.5)
    c.cue(shot_at + 18, "tick", 0.5)
    fp.curtain_close(c)
    return c


# =========================================================================== 2 PROBLEM: the DMs
def scene_problem():
    c = Comp("02 Problem - the DMs", W, H, 180)
    ground(c, "#000000")
    if LANDSCAPE:
        c.image("plate", "plate-celebrate-blur-land.jpg", 1920, 1080, p=(W / 2, H / 2))
        cl, cr = (W - 940) / 2, (W + 940) / 2
    else:
        c.image("plate", "plate-celebrate-blur.jpg", 1080, 1920, p=(W / 2, H / 2))
        cl, cr = 80, 1000
    msgs = [("them", "how much for saturday's match?", 14), ("me", "$70 for the full game", 40),
            ("them", "can do $30?", 66), ("them", "game cancelled, no need to pay ya", 94),
            ("me", "just following up on the invoice :)", 124)]
    seen_at, dim_at = 146, 156
    size = 46
    while max(fonts.width(BODY, size, m[1]) for m in msgs) > (cr - cl) - 76:
        size -= 1
    bh = size * 1.25 + 54
    gap, seen_h = 16, 54
    YB = 930 if LANDSCAPE else 1400
    for i, (who, text, at) in enumerate(msgs):
        tw = fonts.width(BODY, size, text)
        bw = tw + 72
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
        n0 = len(c._layers)
        c.shape(f"bubble bg {i}", [group([rect(bw, bh, bx + bw / 2, YB - bh / 2, bh / 2),
                                          fl("green" if who == "me" else "strip")])], ip=at, parent=g)
        txt(c, text, BODY, size, "ink" if who == "me" else "white", bx + 36, YB - bh / 2 + CAP * size / 2,
            ip=at, parent=g)
        members_opacity(since(c, n0), [(at, 0, "settle-soft"), (at + 6, 100, "hold"),
                                       (dim_at, 100, "travel-balanced"), (dim_at + 10, 20)])
        c.cue(at, "blip_out" if who == "me" else "blip_in", 0.9)
    n0 = len(c._layers)
    txt(c, "Seen", BODY, 28, "#9aa0a6", cr - 8, YB - 12, j=1, ip=seen_at + 4)
    members_opacity(since(c, n0), [(seen_at + 4, 0, "settle-soft"), (seen_at + 10, 100, "hold"),
                                   (dim_at, 100, "travel-balanced"), (dim_at + 10, 20)])
    c.cue(seen_at + 4, "tick", 0.4)
    if LANDSCAPE:
        s2 = fonts.fit(STATE, ["SOUND FAMILIAR?"], 1500, 250)
        fp.rise_pair(c, fonts, "SOUND", "FAMILIAR?", STATE, s2, W / 2, H / 2 + CAP * s2 / 2, start=dim_at + 4,
                     gap_frames=9, slot1="problem1", slot2="problem2", label1="Line 1", label2="Line 2")
    else:
        statement(c, fonts, ["SOUND", "FAMILIAR?"], dim_at + 4, colors=["white", "green"], center_y=H / 2,
                  max_w=860, max_size=260, stagger=9, slots=["problem1", "problem2"])
    c.cue(dim_at + 8, "riser:20", 0.55)
    fp.curtain_open(c)
    fp.drift(c, scale=104, dy=-18)
    fp.curtain_close(c)
    return c


# =========================================================================== 3 HERO: OUTTAKES (the new site)
def scene_hero():
    c = Comp("03 Hero - OUTTAKES", W, H, 141)
    ground(c, "#000000")
    crash = 2
    plate = "v4-hero-l.jpg" if LANDSCAPE else "v4-hero-p.jpg"
    c.image("hero plate", plate, W, H, ip=crash,
            p=anim([(crash, [W / 2 + 16, H / 2, 0], "linear"), (150, [W / 2 - 16, H / 2, 0])]),
            s=anim([(crash, [112, 112, 100], "settle-soft"), (crash + 30, [106, 106, 100], "linear"),
                    (150, [104, 104, 100])]))
    c.shape("hero shade", [group([rect(W, H, W / 2, H / 2),
                                   gradient([(0, "#000000"), (1, "#000000")], [W / 2, 0], [W / 2, H],
                                            alpha_stops=[(0, 0.30), (0.45, 0.05), (1, 0.55)])])], ip=crash)
    if LANDSCAPE:
        size = fonts.fit(STATE, ["OUTTAKES"], 1000, 300)
        tw = fonts.width(STATE, size, "OUTTAKES")
        cx, cy = 110 + tw / 2, 120 + CAP * size / 2
    else:
        size = fonts.fit(STATE, ["OUTTAKES"], 900, 330)
        tw = fonts.width(STATE, size, "OUTTAKES")
        cx, cy = W / 2, 560
    wordmark_crash(c, "OUTTAKES", size, cx, cy, crash, 150, slot="brand", label="Wordmark")
    c.cue(crash, "boom", 1.0)
    c.cue(crash, "shutter_big", 0.9)
    ts = fonts.fit(TITLE, ["STORIES TOLD THROUGH FRAMES"], tw * 0.8, 50)
    fp.rise_line(c, fonts, "STORIES TOLD THROUGH FRAMES", TITLE, ts, "white", cx + tw / 2 - 8,
                 cy + CAP * size / 2 + ts * 1.3, j=1, start=20, slot="tagline", label="Tagline")
    c.cue(20, "tick", 0.5)
    # site chrome: Sign In / Menu
    nbw, nbh = 330, 70
    nx, ny = (W - 110 - nbw, 92) if LANDSCAPE else (1000 - nbw, 300)
    n0 = len(c._layers)
    fp.box(c, "nav", nx, ny, nbw, nbh, "#151517", r=10, ip=26)
    fp.box(c, "sign in", nx + 8, ny + 8, 130, nbh - 16, "white", r=6, ip=26)
    txt(c, "Sign In", BODY, 24, "ink", nx + 73, ny + nbh / 2 + CAP * 24 / 2, j=2, ip=26)
    txt(c, "Menu", BODY, 24, "white", nx + nbw - 70, ny + nbh / 2 + CAP * 24 / 2, j=1, ip=26)
    c.shape("menu icon", [group([path([[nx + nbw - 52, ny + nbh / 2 + d], [nx + nbw - 28, ny + nbh / 2 + d]]),
                                 st("white", 2.4)]) for d in (-6, 6)], ip=26)
    members_opacity(since(c, n0), [(26, 0, "settle-soft"), (34, 100)])
    # Shot of the Week credit (bottom left) + positioning line and the site's button
    if LANDSCAPE:
        sx0, sy0 = 110, 820
        bx0, by0, bw = 1310, 760, 500
        lines = ["A platform where photographers", "and athletes can meet in one", "searchable place."]
        ls = 34
    else:
        sx0, sy0 = 80, 1110
        bx0, by0, bw = 80, 1230, 920
        lines = ["A platform where photographers and", "athletes can meet in one searchable", "place."]
        ls = 38
    fp.fade_line(c, "SHOT OF THE WEEK", TITLE, 30 if LANDSCAPE else 32, "white", sx0, sy0, start=32)
    fp.fade_line(c, "Kallang Stadium", BODY, 26, "white", sx0, sy0 + 50, start=35, o=88)
    fp.fade_line(c, "21.11.2026", BODY, 26, "white", sx0 + (260 if LANDSCAPE else 300), sy0 + 50, start=36, o=88)
    for k, ln in enumerate(lines):
        fp.fade_line(c, ln, MED, ls, "white", bx0, by0 + k * ls * 1.22, start=38 + 2 * k)
    btn_y = by0 + len(lines) * ls * 1.22 + 40
    n1 = len(c._layers)
    fp.site_button(c, fonts, "Find a Photographer", bx0 + bw / 2, btn_y + 46, width=bw, size=30)
    members_opacity(since(c, n1), [(46, 0, "settle-soft"), (54, 100)])
    c.cue(46, "pop", 0.45)
    # the site's film strip passes up the frame and wipes to the light pages
    sh = 300 if not LANDSCAPE else 230
    photos = [(f"{n}.jpg", sz(f"{n}.jpg")) for n in ("stretch-ball", "kids-duel", "sepak-takraw", "tackle-night",
                                                        "number-10", "smile-orange", "team-backs", "heart-hands",
                                                        "celebrate-fists", "point-orange")]
    film_strip(c, [(112, H + sh / 2, "exit-accelerate"), (140, -sh / 2)], sh, photos=photos, ip=112,
               scroll=(112, 260), ground_below="light")
    c.cue(112, "whoosh", 0.7)
    c.cue(126, "shutter", 0.5)
    return c


# =========================================================================== 4 STUDIO: set up once
STEPS = ["Display name", "Profile photo", "At least one specialty", "WhatsApp or Telegram",
         "At least one active package", "At least 6 portfolio photos", "Set your availability", "Set up payouts"]


def scene_studio():
    c = Comp("04 Set up your Studio", W, H, 140)
    ground(c, "light")
    soft_vignette(c)
    c.camera3d(zoom=1400)
    claim(c, ["SET UP ONCE.", "GET BOOKED."], start=0, slots=["studio1", "studio2"], exit_at=None if LANDSCAPE else 34)
    pw, ph = 960, 1190
    t_in = 30
    pl = rise_plane(c, "studio card", pw, ph, t_in, op=140)
    pl.box(0, 0, pw, ph, "card", r=30, shadow=SHADOW)
    pl.text("Set up your profile", MED, 50, "ink", 56, 112)
    tick0, pitch_t = 52, 6
    done_at = [tick0 + i * pitch_t for i in range(len(STEPS))]
    docs = [(0, "0 of 8 steps done.", BODY, 30, "grey", 0)] + [
        (f, f"{i + 1} of 8 steps done.", BODY, 30, "grey", 0) for i, f in enumerate(done_at)]
    pl.keyed_text(docs, 56, 162)
    pl.box(56, 196, 848, 12, "#e2e6e9", r=6)
    bar = group3d(pl, "progress", Comp.ks3(p=(56, 202, 0), a=(56, 202, 0),
                                            s=anim([(0, [3, 100, 100], "hold")] +
                                                   [(f, [100 * (i + 1) / 8, 100, 100], "settle-soft")
                                                    for i, f in enumerate(done_at)] +
                                                   [(done_at[-1] + 6, [100, 100, 100])])))
    bar.box(56, 196, 848, 12, "orange", r=6)
    y0, pitch = 262, 98
    for i, label in enumerate(STEPS):
        y = y0 + i * pitch
        f = done_at[i]
        row = group3d(pl, f"row {i}", Comp.ks3(p=anim([(f - 1, [0, 0, 0], "entrance-sharp"), (f + 2, [14, 0, 0], "settle-soft"),
                                                       (f + 9, [0, 0, 0])])))
        row.circle(84, y + 34, 50, None, line="#c9ced2", line_w=2.5, op=f)
        row.text(str(i + 1), BODY, 26, "grey", 84, y + 34 + CAP * 26 / 2, j=2, op=f)
        row.circle(84, y + 34, 50, "orange", ip=f)
        row.check(84, y + 35, 30, "white", draw_at=f, width=5, ip=f)
        row.text(label, BODY, 38, "ink", 134, y + 34 + CAP * 38 / 2)
        if i >= 6:
            row.text("recommended", BODY, 26, "grey", 134 + fonts.width(BODY, 38, label) + 16, y + 34 + CAP * 26 / 2)
        if i < len(STEPS) - 1:
            pl.line(134, y + pitch - 16, 904, y + pitch - 16, "#e5e8ea", 2)
        c.cue(f, "tick", 0.55)
    swap = done_at[-1] + 6
    by = ph - 150
    button(pl, fonts, "Continue: Profile photo", 56, by, 848, 100, style="orange", size=34, op=swap)
    press = 116
    g = button(pl, fonts, "Preview profile", 56, by, 848, 100, style="ink", size=34, ip=swap, press=press)
    c.cue(swap, "pop", 0.5)
    # fly-through: the card drifts while you work, then rushes past the camera into the profile
    d4 = 30
    for lyr in c._layers:
        if lyr["ind"] == pl.ind:
            lyr["ks"]["p"] = anim([(t_in, [UI_X, UI_Y + (H * 0.75 if not LANDSCAPE else H * 0.9), 260], "settle-soft"),
                                   (t_in + 22, [UI_X, UI_Y, 0], "linear"), (press + 6, [UI_X, UI_Y - d4, 0], "exit-accelerate"),
                                   (140, [UI_X, UI_Y - d4 + 120, -1150])])
    cy_at = lambda f: UI_Y - d4 * max(0.0, min(1.0, (f - t_in - 22) / (press + 6 - t_in - 22)))
    tx, ty = flat_pt(UI_X, cy_at(press), pw, ph, 56 + 848 * 0.62, by + 54)
    cursor(c, [(swap + 2, (tx + 260, ty + 420)), (press - 6, (tx, ty)), (140, (tx, ty))], presses=[press], op=140)
    c.cue(press + 8, "whoosh", 0.7)
    return c


# =========================================================================== 5 PROFILE: your page
def profile_page(pl, fonts):
    """The redesigned photographer profile page, mobile layout, 1000 wide."""
    pl.box(0, 0, pl.w, pl.h, "light", r=0, shadow=SHADOW)
    pl.text("Photographers", BODY, 30, "grey", 40, 70)
    x = 40 + fonts.width(BODY, 30, "Photographers") + 18
    pl.text("›", BODY, 30, "grey", x, 70)
    pl.text("Football", BODY, 30, "grey", x + 30, 70)
    x2 = x + 30 + fonts.width(BODY, 30, "Football") + 18
    pl.text("›", BODY, 30, "grey", x2, 70)
    pl.text(YOUR, BODY, 30, "ink", x2 + 30, 70)
    pl.image("v4-avatar.png", 320, 320, 40, 110, 116, 116)
    pl.text(YOUR.upper(), TITLE, 70, "ink", 180, 194, slot="profileName", label="Photographer name")
    pl.heart(944, 166, 44, "ink")
    pl.image("celebrate-run.jpg", *sz("celebrate-run.jpg"), 0, 266, 1000, 666)
    thumbs = ["stretch-ball", "tackle-night", "kids-duel", "sepak-takraw"]
    for k, n in enumerate(thumbs):
        tx = 40 + k * 236
        pl.image(f"{n}.jpg", *sz(f"{n}.jpg"), tx, 952, 220, 147)
    pl.box(37, 949, 226, 153, None, r=2, line="green", line_w=6)
    py = 1132
    pl.box(0, py, 1000, 700, "panel")
    pl.text("Match days, finals and the", MED, 44, "ink", 40, py + 86)
    pl.text("moments between.", MED, 44, "ink", 40, py + 138)
    rows = [("REVIEWS", "5.0 (3)"), ("PACKAGES FROM", PRICE), ("NEXT FREE DATE", "Sat 28 Nov"),
            ("COVERS", "North, Central"), ("EXPERIENCE", "3 years")]
    for k, (lab, val) in enumerate(rows):
        yy = py + 226 + k * 64
        pl.text(lab, BODY, 26, "grey", 40, yy, tracking=120)
        vx = 380
        if lab == "REVIEWS":
            pl.star(vx + 14, yy - 11, 30, "ink")
            vx += 38
        pl.text(val, MED if lab == "PACKAGES FROM" else BODY, 34, "ink", vx, yy)
        if lab == "NEXT FREE DATE":
            pl.line(vx, yy + 10, vx + fonts.width(BODY, 34, val), yy + 10, "ink", 2)
    tx = 40
    for t in ("Football", "Events"):
        tw = fonts.width(BODY, 26, t) + 40
        pl.box(tx, py + 548, tw, 46, "pill", r=23)
        pl.text(t, BODY, 26, "ink", tx + tw / 2, py + 579, j=2)
        tx += tw + 12
    return py


def scene_profile():
    c = Comp("05 Your portfolio, organised", W, H, 150)
    ground(c, "light")
    soft_vignette(c)
    c.camera3d(zoom=1400)
    pw, ph = 1000, 1832
    if LANDSCAPE:
        top_c, bot_c, s = (1385, 960), (1385, 120), 0.62
    else:
        top_c, bot_c, s = (540, 1110), (540, 760), 1.0
    p = anim([(0, [top_c[0], top_c[1], -260], "settle-soft"), (26, [top_c[0], top_c[1], 0], "hold"),
              (34, [top_c[0], top_c[1], 0], "scroll"), (96, [bot_c[0], bot_c[1], 0], "settle-soft"),
              (150, [bot_c[0], bot_c[1] - 30, 0])])
    pl = Plane(c, "profile page", pw, ph, p, rx=anim([(0, 9, "settle-soft"), (26, 0)]),
               ry=anim([(0, -6, "settle-soft"), (30, 0)]), s=(s * 100, s * 100, 100))
    py = profile_page(pl, fonts)
    button(pl, fonts, "See packages", 40, py + 616, 920, 96, style="green", size=34)
    c.cue(34, "whoosh", 0.4)
    # claim lands after the proof: the page eases back under a light veil
    t_claim = 104
    for lyr in c._layers:
        if lyr["ind"] == pl.ind:
            lyr["ks"]["p"] = anim([(0, [top_c[0], top_c[1], -260], "settle-soft"), (26, [top_c[0], top_c[1], 0], "hold"),
                                   (34, [top_c[0], top_c[1], 0], "scroll"), (96, [bot_c[0], bot_c[1], 0], "hold"),
                                   (t_claim - 4, [bot_c[0], bot_c[1], 0], "settle-soft"),
                                   (150, [bot_c[0], bot_c[1] - 40, 700])])
    if LANDSCAPE:
        statement(c, fonts, ["YOUR PORTFOLIO,", "ORGANISED."], 8, colors=["ink", "gtext"], x=ST_X, j=0,
                  max_w=ST_W, max_size=170, center_y=H / 2, slots=["profile1", "profile2"])
    else:
        c.shape("veil", [group([rect(W, H, W / 2, H / 2), fl("light")])],
                o=anim([(t_claim - 4, 0, "settle-soft"), (t_claim + 8, 82)]), ip=t_claim - 4)
        statement(c, fonts, ["YOUR PORTFOLIO,", "ORGANISED."], t_claim, colors=["ink", "gtext"],
                  center_y=H / 2 - 40, max_w=900, max_size=200, slots=["profile1", "profile2"], exit_at=138)
    return c


# =========================================================================== 6 SEARCH: clients find you
SPORTS = [("BASKETBALL", "v4-sport-basketball.jpg", "basketball"), ("SEPAK TAKRAW", "v4-sport-sepak-takraw.jpg", "takraw"),
          ("FUTSAL", "v4-sport-point-orange.jpg", "football"), ("FOOTBALL", "v4-sport-tackle-night.jpg", "football")]


def sport_icon(plane_like, cx, cy, d, kind):
    plane_like.circle(cx, cy, d, None, line="white", line_w=4)
    r = d / 2
    if kind == "basketball":
        plane_like.line(cx - r, cy, cx + r, cy, "white", 4)
        plane_like.line(cx, cy - r, cx, cy + r, "white", 4)
        plane_like.shape("bb curve", [group([path([[cx - r * 0.62, cy - r * 0.78], [cx - r * 0.25, cy], [cx - r * 0.62, cy + r * 0.78]]),
                                             st("white", 4)]),
                                      group([path([[cx + r * 0.62, cy - r * 0.78], [cx + r * 0.25, cy], [cx + r * 0.62, cy + r * 0.78]]),
                                             st("white", 4)])])
    elif kind == "takraw":
        for k in (-0.45, 0, 0.45):
            plane_like.line(cx - r * 0.86, cy + k * r, cx + r * 0.86, cy + k * r, "white", 3)
            plane_like.line(cx + k * r, cy - r * 0.86, cx + k * r, cy + r * 0.86, "white", 3)
    else:
        pts = [[cx + r * 0.42 * math.cos(-math.pi / 2 + i * 2 * math.pi / 5), cy + r * 0.42 * math.sin(-math.pi / 2 + i * 2 * math.pi / 5)]
               for i in range(5)]
        plane_like.shape("pentagon", [group([path(pts, closed=True), st("white", 4)])])
        for (px, py) in pts:
            plane_like.line(px, py, cx + (px - cx) * 2.3, cy + (py - cy) * 2.3, "white", 3)


def scene_search():
    c = Comp("06 Now clients find you", W, H, 180)
    ground(c, "light")
    soft_vignette(c)
    c.camera3d(zoom=1400)
    claim(c, ["NOW CLIENTS", "FIND YOU."], start=0, slots=["search1", "search2"], exit_at=40)
    CX = W / 2 if LANDSCAPE else UI_X  # the claim clears, so the browse row and results take the centre
    # Browse by sport: the row whips in and stops on Football (the stop is the choice)
    cw_, ch_ = 400, 560
    gap = 26
    row_w = len(SPORTS) * (cw_ + gap) - gap
    rw, rh = row_w, ch_ + 110
    stop_x = (UI_X - (row_w - cw_ / 2 - (cw_ + gap) * 0 - cw_ / 2) * UI_S) if False else None
    # plane centre so that the Football card (last) is centred on UI_X
    fb_center_local = row_w - cw_ / 2
    final_cx = CX - (fb_center_local - rw / 2) * UI_S
    start_cx = final_cx + 1.6 * W
    row_in, row_stop, row_out = 40, 72, 100
    p = anim([(row_in, [start_cx, UI_Y - 40, 0], "scroll"), (row_stop, [final_cx, UI_Y - 40, 0], "hold"),
              (row_out, [final_cx, UI_Y - 40, 0], "exit-accelerate"), (row_out + 10, [final_cx, UI_Y - 40 - H, 0])])
    pl = Plane(c, "sports row", rw, rh, p, s=(UI_S * 100, UI_S * 100, 100), ip=row_in, op=row_out + 11)
    for k, (label, file, kind) in enumerate(SPORTS):
        x = k * (cw_ + gap)
        is_fb = label == "FOOTBALL"
        card = group3d(pl, f"card {label}", Comp.ks3(p=(x + cw_ / 2, 110 + ch_ / 2, 0), a=(x + cw_ / 2, 110 + ch_ / 2, 0),
                                                       s=anim([(row_stop + 2, [100, 100, 100], "settle-soft"),
                                                               (row_stop + 10, [106, 106, 100] if is_fb else [94, 94, 100])])))
        card.image(file, *sz(file), x, 110, cw_, ch_)
        card.shape("card shade", [group([rect(cw_, ch_ * 0.5, x + cw_ / 2, 110 + ch_ * 0.75),
                                         gradient([(0, "#000000"), (1, "#000000")], [0, 110 + ch_ * 0.5], [0, 110 + ch_],
                                                  alpha_stops=[(0, 0), (1, 0.55)])])])
        sport_icon(card, x + cw_ / 2, 110 + ch_ * 0.36, 128, kind)
        card.text(label, STATE, 62 if len(label) < 10 else 52, "white", x + 24, 110 + ch_ - 36)
        if not is_fb:
            card.box(x, 110, cw_, ch_, "light", o=anim([(row_stop + 2, 0, "settle-soft"), (row_stop + 10, 45)]))
    c.cue(row_in, "whoosh", 0.7)
    tl_x = 80 if not LANDSCAPE else UI_X - (rw / 2) * UI_S * 0.55
    title_y0 = UI_Y - 40 - (rh / 2 - 60) * UI_S
    n_t = len(c._layers)
    futsal_left = final_cx + ((cw_ + gap) * 2 - rw / 2) * UI_S
    txt(c, "BROWSE BY SPORT", TITLE, 40 if not LANDSCAPE else 34, "ink", max(80, futsal_left), title_y0,
        ip=row_stop - 10, op=row_out + 4)
    members_opacity(since(c, n_t), [(row_stop - 10, 0, "settle-soft"), (row_stop, 100, "hold"), (row_out - 2, 100, "exit-accelerate"),
                                    (row_out + 4, 0)])
    fx, fy = flat_pt(final_cx, UI_Y - 40, rw, rh, row_w - cw_ / 2, 110 + ch_ / 2)
    click_fb = row_stop + 16
    c.cue(row_stop, "tick", 0.5)
    # Featured photographers: the site's film strip rises with the result cards
    sh = 980 if not LANDSCAPE else 720
    t_strip = row_out + 2
    band_y = UI_Y + (20 if not LANDSCAPE else 0)
    film_strip(c, [(t_strip, band_y + H, "settle-soft"), (t_strip + 18, band_y)], sh, ip=t_strip, scroll=(t_strip, 120))
    c.cue(t_strip, "whoosh", 0.6)
    # result cards in screen space, scrolling sideways and stopping on yours
    cards = [("kids-duel", "Farhan Ismail", "From S$120", "Football · Events"),
             ("celebrate-run", YOUR, f"From {PRICE}", "Football · Events"),
             ("tackle-night", "Marcus Lim", "From S$150", "Football · Night games"),
             ("stretch-ball", "Aisyah Rahman", "From S$110", "Football · Youth")]
    cwr = 720 if not LANDSCAPE else 520
    chr_ = cwr * 0.66
    gapr = 40
    you_idx = 1
    track_final = CX - (you_idx * (cwr + gapr) + cwr / 2)
    lift = 0.58 if LANDSCAPE else 0.38
    track_drift = 40
    track = c.null("result track", p=anim([(t_strip + 4, [track_final + 900, band_y - chr_ * lift, 0], "settle-soft"),
                                           (t_strip + 30, [track_final, band_y - chr_ * lift, 0], "linear"),
                                           (180, [track_final - track_drift, band_y - chr_ * lift, 0])]), ip=t_strip)
    c.no_camera.add(track)
    title_y = band_y - sh / 2 + 120
    fp.fade_line(c, "FEATURED PHOTOGRAPHERS", TITLE, 38 if not LANDSCAPE else 32, "white",
                 80 if not LANDSCAPE else CX - 640, title_y, start=t_strip + 10)
    heart_t = t_strip + 40
    for k, (photo, name, price, sub) in enumerate(cards):
        x = k * (cwr + gapr)
        mine = name == YOUR
        fp.photo(c, f"result {photo}", f"{photo}.jpg", sz(f"{photo}.jpg"), x, 0, cwr, chr_, r=12, parent=track,
                 ip=t_strip)
        hx, hy = x + cwr - 46, 46
        c.shape(f"heart bg {k}", [group([ellipse(64, 64, hx, hy), fl("white", 92)])], parent=track, ip=t_strip)
        c.image("avatar", "v4-avatar.png", 320, 320, p=(x + 32, chr_ + 62), s=(64 / 320 * 100, 64 / 320 * 100),
                parent=track, ip=t_strip) if mine else c.shape(
            f"avatar {k}", [group([ellipse(64, 64, x + 32, chr_ + 62), fl("#5b5f63")])], parent=track, ip=t_strip)
        txt(c, name, MED, 32, "white", x + 80, chr_ + 58, parent=track, ip=t_strip)
        txt(c, price, BODY, 28, "white", x + cwr, chr_ + 58, j=1, parent=track, ip=t_strip, o=85)
        txt(c, sub, BODY, 26, "#a9aeb2", x + 80, chr_ + 96, parent=track, ip=t_strip)
        if mine:
            c.shape("your outline", [group([rect(cwr + 14, chr_ + 14, x + cwr / 2, chr_ / 2, 16), st("green", 6)])],
                    parent=track, ip=t_strip + 32, o=anim([(t_strip + 32, 0, "settle-soft"), (t_strip + 38, 100)]))
            heart = c.null("your heart", p=(hx, hy), a=(hx, hy), parent=track, ip=t_strip,
                           s=anim([(heart_t, [100, 100, 100], "expressive-pop"), (heart_t + 6, [130, 130, 100], "settle-soft"),
                                   (heart_t + 14, [100, 100, 100])]))
            hk = 30 / 40
            pts = [[0, 14], [-16, -1], [-16, -10], [-9, -16], [0, -10], [9, -16], [16, -10], [16, -1]]
            shp = lambda filled: [group([{"ty": "sh", "ks": {"a": 0, "k": {
                "i": [[0, 0], [0, 0], [0, -5 * hk], [-6 * hk, 0], [0, 0], [-4 * hk, 0], [0, -5 * hk], [0, 0]],
                "o": [[0, 0], [0, 0], [0, -4 * hk], [4 * hk, 0], [0, 0], [6 * hk, 0], [0, 5 * hk], [0, 0]],
                "v": [[hx + px * hk, hy + py * hk] for px, py in pts], "c": True}}},
                fl("green") if filled else st("ink", 3)])]
            c.shape("heart line", shp(False), parent=heart, ip=t_strip, op=heart_t)
            c.shape("heart fill", shp(True), parent=heart, ip=heart_t)
            c.cue(heart_t, "pop", 0.6)
        else:
            hk = 30 / 40
            pts = [[0, 14], [-16, -1], [-16, -10], [-9, -16], [0, -10], [9, -16], [16, -10], [16, -1]]
            c.shape(f"heart {k}", [group([{"ty": "sh", "ks": {"a": 0, "k": {
                "i": [[0, 0], [0, 0], [0, -5 * hk], [-6 * hk, 0], [0, 0], [-4 * hk, 0], [0, -5 * hk], [0, 0]],
                "o": [[0, 0], [0, 0], [0, -4 * hk], [4 * hk, 0], [0, 0], [6 * hk, 0], [0, 5 * hk], [0, 0]],
                "v": [[hx + px * hk, hy + py * hk] for px, py in pts], "c": True}}}, st("ink", 3)])], parent=track, ip=t_strip)
    # the client's pointer: picks Football, then hearts your card
    you_hx = CX + cwr / 2 - 46 - track_drift * (heart_t - t_strip - 30) / (180 - t_strip - 30)
    you_hy = band_y - chr_ * lift + 46
    cursor(c, [(row_stop + 2, (fx + 220, fy + 380)), (click_fb - 4, (fx, fy)), (row_out - 2, (fx, fy)),
               (heart_t - 6, (you_hx, you_hy)), (heart_t + 8, (you_hx, you_hy)), (180, (you_hx + 40, you_hy + 120))],
           presses=[click_fb, heart_t], op=180)
    return c


# =========================================================================== 7 BOOK: at your rate
def scene_book():
    c = Comp("07 Booked at your rate", W, H, 165)
    ground(c, "light")
    soft_vignette(c)
    c.camera3d(zoom=1400)
    t_in = 32
    claim(c, ["BOOKED AT", "YOUR RATE."], start=0, slots=["book1", "book2"], exit_at=None if LANDSCAPE else t_in + 4)
    pw, ph = 960, 1230
    pl = rise_plane(c, "booking", pw, ph, t_in, op=165, whip=(152, -1.3, 0))
    pl.text("BOOK " + YOUR.upper(), TITLE, 50, "ink", 0, 50)
    # package
    pl.box(0, 90, pw, 330, "panel", r=18, shadow=SHADOW_SOFT)
    pl.text("Full match", MED, 46, "ink", 40, 166)
    pl.text("2 hrs · 60 edited photos ·", BODY, 30, "grey", 40, 214)
    pl.text("ready in 3 days", BODY, 30, "grey", 40, 252)
    pl.text(PRICE, MED, 50, "ink", 40, 378)
    press_book = 120
    bx, byy, bw_, bh_ = 470, 300, 450, 96
    book = button(pl, fonts, "Book", bx, byy, bw_, bh_, style="green", size=36, op=press_book + 3, press=press_book)
    booked = group3d(pl, "booked", Comp.ks3(p=(bx + bw_ / 2, byy + bh_ / 2, 0), a=(bx + bw_ / 2, byy + bh_ / 2, 0),
                                            s=anim([(press_book + 3, [92, 92, 100], "settle-soft"),
                                                    (press_book + 12, [100, 100, 100])])), ip=press_book + 3)
    booked.box(bx, byy, bw_, bh_, "ink", r=bh_ * 0.22)
    booked.check(bx + 62, byy + bh_ / 2 + 1, 34, "green", draw_at=press_book + 6)
    booked.text("Booked · Sat 28 Nov", MED, 32, "white", bx + bw_ / 2 + 26, byy + bh_ / 2 + CAP * 32 / 2, j=2)
    # availability
    ay = 460
    pl.box(0, ay, pw, 760, "card", r=18, shadow=SHADOW_SOFT)
    pl.text("AVAILABILITY", BODY, 28, "ink", 40, ay + 70, tracking=140)
    pl.text("NOVEMBER 2026", MED, 30, "ink", 40, ay + 124)
    gx, gw = 40, pw - 80
    cwd = gw / 7
    for k, d in enumerate("MTWTFSS"):
        pl.text(d, BODY, 26, "grey", gx + cwd * (k + 0.5), ay + 186, j=2)
    weeks = calendar.monthcalendar(2026, 11)
    rh = 82
    avail = {25, 26, 28, 29}
    pick, pick_t = 28, 88
    pick_xy = None
    for r_, week in enumerate(weeks):
        for k, day in enumerate(week):
            if not day:
                continue
            dx, dy = gx + cwd * (k + 0.5), ay + 236 + rh * r_
            if day in avail:
                pl.circle(dx, dy, 66, "green")
                if day == pick:
                    pick_xy = (dx, dy)
            pl.text(str(day), MED if day in avail else BODY, 30, "ink", dx, dy + CAP * 30 / 2, j=2,
                    o=100 if day in avail else 40)
    px_, py_ = pick_xy
    ring = group3d(pl, "pick ring", Comp.ks3(p=(px_, py_, 0), a=(px_, py_, 0),
                                              s=anim([(pick_t, [60, 60, 100], "expressive-pop"), (pick_t + 7, [112, 112, 100], "settle-soft"),
                                                      (pick_t + 13, [100, 100, 100])])), ip=pick_t)
    ring.circle(px_, py_, 84, None, line="ink", line_w=4)
    pl.circle(gx + 14, ay + 712, 22, "green")
    pl.text("Available, tap to pick", BODY, 26, "grey", gx + 40, ay + 721)
    tpx, tpy = flat_pt(*pl.center_at(pick_t), pw, ph, px_, py_)
    tbx, tby = flat_pt(*pl.center_at(press_book), pw, ph, bx + bw_ * 0.5, byy + bh_ * 0.55)
    cursor(c, [(66, (tpx + 300, tpy + 380)), (pick_t - 6, (tpx, tpy)), (pick_t + 10, (tpx, tpy)),
               (press_book - 7, (tbx, tby)), (165, (tbx + 30, tby + 40))], presses=[pick_t, press_book], op=165)
    c.cue(pick_t, "tick", 0.6)
    c.cue(press_book + 4, "chime", 0.9)
    c.cue(152, "whoosh", 0.6)
    return c


# =========================================================================== 8 PAID: even if they cancel
def scene_paid():
    c = Comp("08 Paid, even if they cancel", W, H, 165)
    ground(c, "light")
    soft_vignette(c)
    c.camera3d(zoom=1400)
    t_in = 32
    claim(c, ["PAID.", "EVEN IF THEY CANCEL."], start=0, slots=["paid1", "paid2"], exit_at=None if LANDSCAPE else t_in + 4)
    pw, ph = 960, 1110
    pl = rise_plane(c, "studio money", pw, ph, t_in, op=165, whip=(154, 0, -1.1))
    # earnings card
    pl.box(0, 0, pw, 300, "card", r=24, shadow=SHADOW_SOFT)
    pl.text("Earnings this month", BODY, 32, "grey", 44, 76)
    t_deliver, t_count = 74, 80
    vals = [0, 4, 11, 19, 28, 37, 45, 52, 58, 63, 66, 68, 69, 70]
    docs = [(0, "S$0.00", MED, 112, "ink", 0)]
    f = t_count
    for k, v in enumerate(vals[1:], start=1):
        f += 1 if k < 7 else 2
        docs.append((f, f"S${v}.00", MED, 112, "ink", 0))
    pl.keyed_text(docs, 44, 216)
    c.cue(f, "chime_soft", 0.7)
    up = group3d(pl, "plus", Comp.ks3(p=anim([(t_count, [0, 20, 0], "entrance-sharp"), (t_count + 12, [0, 0, 0])]),
                                       o=anim([(t_count, 0, "settle-soft"), (t_count + 6, 100), (t_count + 40, 100), (t_count + 50, 0)])),
                 ip=t_count)
    up.text("+" + PRICE + ".00", MED, 36, "orange", pw - 44, 220, j=1)
    # bookings
    by0 = 340
    pl.box(0, by0, pw, ph - by0, "card", r=24, shadow=SHADOW_SOFT)
    pl.text("Bookings", MED, 42, "ink", 44, by0 + 84)

    def chip(g, x, y, label, colour, text_col="ink", line=None):
        w = fonts.width(MED, 28, label) + 44
        g.box(x, y, w, 52, colour, r=26, line=line)
        g.text(label, MED, 28, text_col, x + w / 2, y + 36, j=2)
        return w

    rows = [("Sat 28 Nov · Full match", "Sports club", t_deliver), ("Sun 6 Dec · Full match", "Brand shoot", 112)]
    for k, (title, client, t_flip) in enumerate(rows):
        ry = by0 + 130 + k * 330
        row = group3d(pl, f"booking {k}", Comp.ks3(p=anim([(t_in + 10 + 8 * k, [0, 40, 0], "entrance-sharp"),
                                                           (t_in + 22 + 8 * k, [0, 0, 0])])))
        if k == 1:
            row = group3d(pl, "booking 2", Comp.ks3(p=anim([(98, [0, 60, 0], "entrance-sharp"), (110, [0, 0, 0])]),
                                                     o=anim([(98, 0, "settle-soft"), (104, 100)])), ip=98)
        if k == 0:
            pl.line(44, ry - 20, pw - 44, ry - 20, "#e5e8ea", 2)
        row.text(title, MED, 38, "ink", 44, ry + 46)
        row.text(client, BODY, 30, "grey", 44, ry + 92)
        if k == 0:
            g1 = group3d(row, "awaiting", op=t_flip)
            chip(g1, 44, ry + 128, "Awaiting photos", "#e7eaec")
            g2 = group3d(row, "delivered", Comp.ks3(p=(44, ry + 154, 0), a=(44, ry + 154, 0),
                                                    s=anim([(t_flip, [80, 80, 100], "expressive-pop"), (t_flip + 8, [100, 100, 100])])),
                         ip=t_flip)
            w = chip(g2, 44, ry + 128, "Photos delivered", "green")
            g2.check(44 + w + 26, ry + 155, 30, "ink", draw_at=t_flip + 2)
            g3 = group3d(row, "invoice", Comp.ks3(o=anim([(t_flip + 14, 0, "settle-soft"), (t_flip + 20, 100)])), ip=t_flip + 14)
            chip(g3, 44 + w + 70, ry + 128, "Invoice #OT-0142 sent", "white", line="line")
            c.cue(t_flip, "pop", 0.6)
            c.cue(t_flip + 14, "blip_in", 0.5)
        else:
            g1 = group3d(row, "cancelled", Comp.ks3(o=anim([(t_flip, 0, "settle-soft"), (t_flip + 6, 100)])), ip=t_flip)
            chip(g1, 44, ry + 128, "Cancelled by client", "white", text_col="#c2410c", line="#f2b28c")
            t_fee = t_flip + 16
            g2 = group3d(row, "fee", Comp.ks3(p=(44, ry + 224, 0), a=(44, ry + 224, 0),
                                               s=anim([(t_fee, [80, 80, 100], "expressive-pop"), (t_fee + 8, [100, 100, 100])])),
                         ip=t_fee)
            w = chip(g2, 44, ry + 198, "Cancellation fee paid to you", "green")
            g2.check(44 + w + 26, ry + 225, 30, "ink", draw_at=t_fee + 2)
            c.cue(t_flip, "blip_in", 0.6)
            c.cue(t_fee, "chime", 0.85)
    c.cue(154, "whoosh", 0.6)
    return c


# =========================================================================== 9 FEATURED: your shot
def scene_featured():
    c = Comp("09 Your shot, featured", W, H, 135)
    ground(c, "light")
    soft_vignette(c)
    c.camera3d(zoom=1400)
    t_in = 30
    claim(c, ["YOUR SHOT.", "FEATURED."], start=0, slots=["sotw1", "sotw2"], exit_at=None if LANDSCAPE else t_in + 4)
    pw, ph = 960, 1240
    pl = rise_plane(c, "photos of the week", pw, ph, t_in, op=135, whip=(126, 0, -1.1))
    pl.text("PHOTOS OF THE WEEK", TITLE, 46, "ink", 0, 52)
    pl.box(0, 88, pw, 1152, "panel", r=0, shadow=SHADOW)
    iw, ih = sz("celebrate-run.jpg")
    ph_h = 640
    img = pl.image("celebrate-run.jpg", iw, ih, 0, 88, pw, ph_h, p=(pw / 2, 88 + ph_h / 2, 0), a=(iw / 2, ih / 2, 0),
                   s=anim([(t_in, [pw / iw * 100 * 1.0, ph_h / ih * 100 * 1.0, 100], "linear"),
                           (135, [pw / iw * 100 * 1.06, ph_h / ih * 100 * 1.06, 100])]))
    pl.text("FOOTBALL · 21.11.2026", BODY, 24, "white", 30, 88 + ph_h - 30, tracking=80)
    yy = 88 + ph_h + 40
    pl.image("v4-avatar.png", 320, 320, 30, yy, 90, 90)
    pl.text(YOUR.upper(), STATE, 64, "ink", 140, yy + 62)
    pl.text("Football from the touchline.", BODY, 28, "grey", 140, yy + 100)
    for k, n in enumerate(["stretch-ball", "tackle-night", "kids-duel", "sepak-takraw"]):
        pl.image(f"{n}.jpg", *sz(f"{n}.jpg"), 30 + k * 228, yy + 136, 216, 144)
    tx = 30
    for t in ("Football", "Events"):
        tw = fonts.width(BODY, 24, t) + 36
        pl.box(tx, yy + 302, tw, 42, "pill", r=21)
        pl.text(t, BODY, 24, "ink", tx + tw / 2, yy + 331, j=2)
        tx += tw + 10
    pl.text("From", BODY, 28, "ink", pw - 260, yy + 332)
    pl.text(PRICE, STATE, 52, "ink", pw - 190, yy + 336)
    pl.heart(pw - 56, yy + 320, 34, "ink")
    feat = group3d(pl, "featured chip", Comp.ks3(p=(30 + 110, 120 + 26, 0), a=(30 + 110, 120 + 26, 0),
                                                  s=anim([(78, [60, 60, 100], "expressive-pop"), (86, [106, 106, 100], "settle-soft"),
                                                          (92, [100, 100, 100])])), ip=78)
    feat.box(30, 120, 220, 54, "green", r=8)
    feat.text("Shot of the Week", MED, 26, "ink", 140, 156, j=2)
    c.cue(78, "chime", 0.8)
    fp.curtain_close(c)
    return c


# =========================================================================== 10 STEPS: how a booking goes (holographic cards)
def scene_steps():
    c = Comp("10 How a booking goes", W, H, 135)
    ground(c, "#0f0f11")
    hs = fonts.fit(TITLE, ["HOW A BOOKING GOES"], 1400 if LANDSCAPE else 940, 120 if LANDSCAPE else 78)
    fp.rise_line(c, fonts, "HOW A BOOKING GOES", TITLE, hs, "white", W / 2, (170 if LANDSCAPE else 380), j=2,
                 start=4, slot="stepsTitle", label="Steps title")
    c.camera3d(zoom=1500 if LANDSCAPE else 1400)
    steps = [("one", "1", "Call the photographer\rand agree on the shoot"),
             ("two", "2", "Book their package\rand date on Outtakes"),
             ("three", "3", "Pay once\rthey accept"),
             ("four", "4", "Get shot, then get\ryour photos")]
    if LANDSCAPE:
        cw3, chh, ccx, ccy, spacing = 470, 620, W / 2, H / 2 + 70, 560
    else:
        cw3, chh, spacing = 610, 800, 670
        ccx, ccy = W / 2, 1030
    kk = [(0, -1.3, "travel-balanced"), (14, 0, "linear"), (40, 0.06, "travel-balanced"), (52, 1, "linear"),
          (70, 1.06, "travel-balanced"), (82, 2, "linear"), (100, 2.06, "travel-balanced"), (112, 3, "linear"),
          (135, 3.1, "linear")]
    for f in (0, 40, 70, 100):
        c.cue(f, "whoosh", 0.45)
    bright, dark = col("green"), col("#2f9a1f")
    for i, (word, num, body) in enumerate(steps):
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
        n0 = len(c._layers)
        c.shape3d(f"card {word} face", [group([rect(cw3, chh, 0, 0, 22),
                                                {"ty": "fl", "c": anim(colk), "o": static(100), "r": 1}])], Comp.ks3(), parent=n)
        nf = f"v4-holo-num-{num}.png"
        nw, nh = sz(nf)
        ns = chh * 0.86 / nh
        c.image3d(f"holo {num}", nf, nw, nh, Comp.ks3(p=(cw3 * 0.5 - nw * ns * 0.5 - 18, chh * 0.5 - nh * ns * 0.5 - 14, 0),
                                                      a=(nw / 2, nh / 2, 0), s=(ns * 100, ns * 100, 100)), parent=n)
        wf = f"v4-holo-word-{word}.png"
        ww, wh = sz(wf)
        wsc = min(cw3 * 0.62 / ww, chh * 0.16 / wh)
        c.image3d(f"holo {word}", wf, ww, wh, Comp.ks3(p=(-cw3 / 2 + 28, -chh / 2 + 26, 0), a=(0, 0, 0),
                                                       s=(wsc * 100, wsc * 100, 100)), parent=n)
        c.text3d(f"card {word} body", text_doc(body, MED, cw3 * 0.062, col("ink"), justify=2,
                                               lh=cw3 * 0.062 * 1.22), Comp.ks3(p=(0, chh * 0.02, 0)), parent=n)
        members_opacity(since(c, n0), [(f, v[0], e) for f, v, e in ok])
    fp.curtain_open(c)
    return c


# =========================================================================== 11 GET IN THE FRAME (light corridor)
def scene_frame():
    c = Comp("11 Get in the frame", W, H, 150)
    ground(c, "light")
    Z = 1500 if LANDSCAPE else 1300
    c.camera3d(zoom=Z)
    fin = 150
    names = ["tackle-night", "basketball", "sepak-takraw", "celebrate-fists", "motion-blur", "team-talk",
             "heart-hands", "number-10", "kids-duel", "point-orange", "smile-orange", "stretch-ball"]
    D = 1150 if LANDSCAPE else 600
    PWW = 700
    YAW = 72
    rows = (-940, 0, 940)
    step, slots = 760, 8
    travel = 1.3 * step
    speed = travel / fin
    panels = []
    for side, sgn in (("L", -1), ("R", 1)):
        for k in range(slots):
            z0 = -150 + k * step + (0 if side == "L" else step / 2)
            for r_, dy in enumerate(rows):
                panels.append((z0, side, sgn, dy, k, r_))
    panels.sort(key=lambda q: -q[0])

    def fog(z):
        return max(0.0, min(100.0, (4900 - z) / 1100 * 100))

    for z0, side, sgn, dy, k, r_ in panels:
        name = names[(k * 5 + r_ * 4 + (0 if side == "L" else 6)) % len(names)]
        file = panel_photo(name)
        f_out = fin if z0 - travel > -650 else int((z0 + 650) / speed) + 1
        if f_out <= 0:
            continue
        fr = sorted(set([0, f_out] + list(range(0, f_out, 8))))
        x = W / 2 + sgn * D
        ks = Comp.ks3(p=anim([(f, [x, H / 2 + dy, z0 - speed * f], "linear") for f in fr]),
                      a=(400, 500, 0), s=(PWW / 800 * 100,) * 2 + (100,), ry=sgn * YAW,
                      o=anim([(f, [fog(z0 - speed * f)], "linear") for f in fr]))
        c.image3d(f"wall {side}{k} row{r_} {name}", file, 800, 1000, ks, op=min(f_out, fin))
    c.shape("light veil", [group([rect(W, H, W / 2, H / 2),
                                   gradient([(0, C_LIGHT), (1, C_LIGHT)], [W / 2, H / 2], [W / 2 + W * 0.62, H / 2],
                                            kind=2, alpha_stops=[(0, 0.9), (0.5, 0.55), (1, 0)])])])
    c.cue(0, "whoosh", 0.5)
    if LANDSCAPE:
        hs = fonts.fit(STATE, ["GET IN THE FRAME"], 1200, 220)
        title_y, sub_y, b1y, b2y, bw = 360, 440, 640, 740, 470
        pill_y = 210
    else:
        hs = fonts.fit(STATE, ["GET IN", "THE FRAME"], 800, 250)
        title_y = 700
        sub_y, b1y, b2y, bw = 700 + hs * 0.96 + 96, 1250, 1370, 640
        pill_y = 470
    PILL = "Opens 24 Nov · Photographers only"
    pill_w = fonts.width(MED, 28, PILL) + 64
    n0 = len(c._layers)
    fp.box(c, "date pill", W / 2 - pill_w / 2, pill_y - 30, pill_w, 60, "white", r=30)
    txt(c, PILL, MED, 28, "ink", W / 2, pill_y + CAP * 28 / 2, j=2, slot="openPill", label="Opening date pill")
    members_opacity(since(c, n0), [(4, 0, "settle-soft"), (12, 100)])
    if LANDSCAPE:
        fp.rise_line(c, fonts, "GET IN THE FRAME", STATE, hs, "ink", W / 2, title_y, j=2, start=8, slot="frame",
                     label="Get in the frame")
    else:
        fp.rise_line(c, fonts, "GET IN", STATE, hs, "ink", W / 2, title_y, j=2, start=8, slot="frame1",
                     label="Get in the frame 1")
        fp.rise_line(c, fonts, "THE FRAME", STATE, hs, "ink", W / 2, title_y + hs * 0.96, j=2, start=16,
                     slot="frame2", label="Get in the frame 2")
    fp.fade_line(c, "Photographers, show your work and take bookings.", BODY, 32, "ink", W / 2, sub_y, j=2, start=26)
    fp.fade_line(c, "Set up your profile free from 24 November.", BODY, 32, "ink", W / 2, sub_y + 44, j=2,
                 start=30)
    press = 104
    b1y = (b1y + b2y) / 2
    for lab, style, by, at in (("Join as Photographer", "green", b1y, 40),):
        g = c.null(f"{lab} btn", p=(W / 2, by), a=(W / 2, by), ip=at,
                   s=anim([(at, [82, 82, 100], "expressive-pop"), (at + 8, [103, 103, 100], "settle-soft"),
                           (at + 14, [100, 100, 100], "hold")] +
                          ([(press, [100, 100, 100], "hold"), (press + 1, [94, 94, 100], "hold"), (press + 6, [100, 100, 100])]
                           if style == "green" else [(at + 15, [100, 100, 100])])))
        n1 = len(c._layers)
        h = 92
        fp.box(c, f"btn {lab}", W / 2 - bw / 2, by - h / 2, bw, h, col(style), r=h * 0.22, parent=g, ip=at)
        txt(c, lab, MED, 32, "white" if style == "ink" else "ink", W / 2 - 18, by + CAP * 32 / 2, j=2, parent=g, ip=at)
        fp.arrow_icon(c, W / 2 + bw / 2 - 52, by, 34, "#ffffff" if style == "ink" else "#121214", parent=g, ip=at)
        members_opacity(since(c, n1), [(at, 0, "settle-soft"), (at + 6, 100)])
    c.cue(40, "pop", 0.5)
    tx, ty = W / 2 + bw * 0.18, b1y + 6
    cursor(c, [(84, (tx + 260, ty + 360)), (press - 6, (tx, ty)), (150, (tx, ty))], presses=[press])
    # the site's green glow rises and carries us into the dark end card
    glow_wipe(c, [(press + 6, H, "travel-balanced"), (150, -GLOW_END * GLOW_H)], ip=press + 6)
    c.cue(press + 6, "riser:30", 0.5)
    return c


C_LIGHT = "#e5e9ec"


GLOW_H = H * 3.2      # tall enough that the dark tail still covers the frame when the green has passed
GLOW_END = 0.27       # gradient position at the top of the frame on the cut (the green is just leaving)


def glow_wipe(c, y_keys, ip=0, op=None):
    """The site's glow (light -> green -> near-black) as a rising band; y_keys move its top edge."""
    gh = GLOW_H
    c.no_camera.add(c.shape("glow wipe", [group([rect(W * 1.2, gh, W / 2, gh / 2),
                                                 gradient([(0, C_LIGHT), (0.10, "#b8ffa8"), (0.17, "#4bff2c"),
                                                           (0.25, "#1d5a1a"), (0.33, "#0f0f11"), (1, "#0f0f11")],
                                                          [0, 0], [0, gh])])],
                            p=anim([(k[0], [0, k[1], 0]) + tuple(k[2:]) for k in y_keys]), ip=ip, op=op))


# =========================================================================== 12 END CARD: the brand, in focus
def corner_frame(c, cx, cy, w, h, arm, width, scale_keys, colour_keys, ip, op, o=None):
    """Viewfinder corners around a w x h box (the hook's focus brackets, stretched to frame the wordmark)."""
    items = []
    ck = sorted(colour_keys, key=lambda k: k[0])
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * w / 2, sy * h / 2
            g = [path([[x, y - sy * arm], [x, y], [x - sx * arm, y]]),
                 {"ty": "st", "c": anim([(f, col(cc)[:3] + [1], e) for f, cc, e in ck]), "o": static(100),
                  "w": static(width), "lc": 2, "lj": 2}]
            items.append(group(g))
    return c.shape("viewfinder", items, p=(cx, cy), s=anim(scale_keys), ip=ip, op=op, o=o if o is not None else 100)


def scene_end():
    c = Comp("12 End card - in focus", W, H, 96)
    ground(c, "#0f0f11")
    # the glow's tail keeps rising out of frame for the first frames (the cut sits inside the wipe)
    v_end = 0.45 * (H + GLOW_END * GLOW_H) / 40
    glow_wipe(c, [(0, -GLOW_END * GLOW_H, "linear"), (12, -GLOW_END * GLOW_H - 12 * v_end)], ip=0, op=13)
    if LANDSCAPE:
        size = fonts.fit(STATE, ["OUTTAKES"], 1240, 330)
        cy = 440
    else:
        size = fonts.fit(STATE, ["OUTTAKES"], 860, 330)
        cy = 840
    tw = fonts.width(STATE, size, "OUTTAKES")
    cap = CAP * size
    lock, shot = 15, 20
    # the wordmark starts out of focus and snaps sharp as the focus point locks on it
    wm = c.text("end wordmark", text_doc("OUTTAKES", STATE, size, col("white"), justify=2), p=(W / 2, cy),
                a=(0, -cap / 2), s=anim([(0, [107, 107, 100], "settle-soft"), (lock + 3, [100, 100, 100], "linear"),
                                         (96, [97.5, 97.5, 100])]), slot="endBrand", label="End wordmark")
    with_fx(c, wm, gblur(anim([(0, [55], "settle-soft"), (lock + 1, [0])])))
    fw, fh = tw + 150, cap + 170
    corner_frame(c, W / 2, cy, fw, fh, arm=min(90, fh * 0.32), width=7,
                 scale_keys=[(0, [150, 150, 100], "crash"), (lock - 1, [104, 104, 100], "crash"),
                             (lock + 2, [99, 99, 100], "hold"), (96, [99, 99, 100])],
                 colour_keys=[(0, "white", "hold"), (lock, "green", "hold")], ip=0, op=96,
                 o=anim([(0, 0, "settle-soft"), (4, 100)]))
    c.cue(0, "whoosh", 0.5)
    c.cue(lock, "af", 0.6)
    fp.flash(c, shot, peak=26, dur=3)
    c.cue(shot, "shutter_big", 0.9)
    c.cue(shot, "boom_small", 0.35)
    ts = fonts.fit(TITLE, ["STORIES TOLD THROUGH FRAMES"], tw * 0.78, 44)
    fp.rise_line(c, fonts, "STORIES TOLD THROUGH FRAMES", TITLE, ts, "#c9ced2", W / 2 + tw / 2 - 6,
                 cy + cap / 2 + ts * 1.5, j=1, start=shot + 4, slot="endTagline", label="End tagline")
    uy = cy + cap / 2 + (330 if not LANDSCAPE else 250)
    fp.fade_line(c, "Photographer sign-ups open 24 November", BODY, 40 if not LANDSCAPE else 34, "#9aa0a6", W / 2, uy, j=2,
                 start=shot + 10)
    us = fonts.fit(TITLE, ["outtakes.sg"], 760, 84 if not LANDSCAPE else 70)
    fp.fade_line(c, "outtakes.sg", TITLE, us, "white", W / 2, uy + 26 + us, j=2, start=shot + 12)
    c.cue(shot + 12, "tick", 0.5)
    fp.drift(c, scale=103, dy=-10, anchor=(W / 2, cy))
    fp.curtain_close(c, dur=6)
    return c


SCENES = [scene_hook, scene_problem, scene_hero, scene_studio, scene_profile, scene_search, scene_book, scene_paid,
          scene_featured, scene_steps, scene_frame, scene_end]


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
