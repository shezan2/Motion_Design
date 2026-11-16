"""Author the Outtakes launch film as Lottie scenes for the text-to-lottie player.

    python3 tools/build_film.py                        # portrait  -> public/projects/outtakes-launch/scene-1..10
    OT_FORMAT=landscape python3 tools/build_film.py    # landscape -> public/projects/outtakes-launch-16x9/scene-1..10

Each scene = one chapter (skills/text-to-lottie/references/chapterization-transition-grammar.md):
hook -> problem -> reveal -> six feature proofs (repeated armature) -> CTA.
Seams are a camera-shutter occlusion wipe: each chapter ends with the curtain
starting to close (cut on motion) and the next opens with it finishing.

Also writes public/projects/outtakes-launch/cues.json (sound-effect cues in film frames).
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from lottie_kit import CAP, Comp, Fonts, anim, ease_value, group, hexc, path, rect, stroke, text_doc, trim  # noqa: E402
from film_parts import (BOTTOM, COL, CW, H, L, LANDSCAPE, R, W, armature_headline, background, box,  # noqa: E402
                        brand_gradient_rect, c_, chip, check_icon, cta_button, curtain_close, curtain_open, drift,
                        fade_line, feature_glow, flash, glow, label_text, lock_icon, photo, rise_line, rise_pair,
                        search_icon, tag, tap)

ROOT = Path(__file__).resolve().parent.parent
PHOTOS = ROOT / "brand" / "photos"
FONTS_DIR = ROOT / "brand" / "fonts"
OUT = ROOT / "public" / "projects" / ("outtakes-launch-16x9" if LANDSCAPE else "outtakes-launch")
fonts = Fonts(FONTS_DIR)

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


def P(name):
    return f"{name}.jpg", SIZES[f"{name}.jpg"]


def pic(c, name, x, y, w, h, **kw):
    file, size = P(name)
    photo(c, name, file, size, x, y, w, h, focus=kw.pop("focus", FOCUS.get(name, (0.5, 0.5))), **kw)


def members_opacity(layers, keys):
    for lyr in layers:
        lyr["ks"]["o"] = anim(keys)


def layers_since(c, start_index):
    return c._layers[start_index:]


# =========================================================================== 1 HOOK
def scene_hook():
    c = Comp("01 Hook - burst mode", W, H, 180)
    background(c, "#000000")
    burst = ["tackle-night", "kids-duel", "point-orange", "sepak-takraw", "number-10", "motion-blur",
             "smile-orange", "heart-hands", "stretch-ball", "portrait-flare"]
    times = [3, 16, 28, 39, 49, 58, 66, 73, 80, 86]
    land = 92
    for i, (name, t0) in enumerate(zip(burst, times)):
        t1 = times[i + 1] if i + 1 < len(times) else land
        pic(c, name, 0, 0, W, H, clip=False, ip=t0, op=t1,
            zoom=[(t0, 1.07, "settle-soft"), (t0 + 8, 1.0, "linear"), (t1, 0.995)])
        flash(c, t0, peak=28, dur=2)
        c.cue(t0, "shutter", 0.55 + 0.4 * i / len(times))
    pic(c, "celebrate-run", 0, 0, W, H, clip=False, ip=land,
        zoom=[(land, 1.14, "entrance-sharp"), (land + 8, 1.0, "linear"), (180, 1.05)])
    flash(c, land, peak=40, dur=3)
    c.cue(land, "shutter_big", 1.0)
    c.cue(land, "boom_small", 0.45)
    from lottie_kit import gradient
    lh = 620 if LANDSCAPE else 1100
    c.shape("legibility", [group([rect(W, lh, W / 2, H - lh / 2),
                                   gradient([(0, "#000000"), (1, "#000000")], [W / 2, H - lh], [W / 2, H],
                                            alpha_stops=[(0, 0), (0.55, 0.55), (1, 0.8)])])], ip=land)
    if LANDSCAPE:
        size = fonts.fit("OT Display", ["YOU GOT THE SHOT."], 1500, 150)
        rise_pair(c, fonts, "YOU GOT", "THE SHOT.", "OT Display", size, W / 2, H - 130, start=108, gap_frames=9,
                  slot1="hook1", slot2="hook2", label1="Hook line 1", label2="Hook line 2")
    else:
        size = fonts.fit("OT Display", ["YOU GOT", "THE SHOT."], 920, 132)
        b2 = 1420
        b1 = b2 - size * 1.02
        rise_line(c, fonts, "YOU GOT", "OT Display", size, "white", W / 2, b1, j=2, start=108, slot="hook1",
                  label="Hook line 1")
        rise_line(c, fonts, "THE SHOT.", "OT Display", size, "green", W / 2, b2, j=2, start=117, slot="hook2",
                  label="Hook line 2")
    c.cue(108, "tick", 0.5)
    c.cue(117, "tick", 0.5)
    drift(c)
    curtain_close(c)
    return c


# =========================================================================== 2 PROBLEM
def scene_problem():
    c = Comp("02 Problem - the DMs", W, H, 240)
    background(c)
    if LANDSCAPE:
        c.image("plate", "plate-celebrate-blur-land.jpg", 1920, 1080, p=(W / 2, H / 2))
        cl, cr = (W - 900) / 2, (W + 900) / 2  # chat column centred in the wide frame
    else:
        c.image("plate", "plate-celebrate-blur.jpg", 1080, 1920, p=(W / 2, H / 2))
        cl, cr = L, R
    msgs = [("them", "how much for saturday's match?", 14), ("me", "$70 for the full game", 42),
            ("them", "can do $30?", 72), ("them", "game cancelled, no need to pay ya", 108),
            ("me", "just following up on the invoice :)", 146)]
    seen_at, dim_at = 172, 192
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
        fillc = "green" if who == "me" else "surface"
        rr = bh / 2
        c.shape(f"bubble bg {i}", [group([rect(bw, bh, bx + bw / 2, YB - bh / 2, rr),
                                          {"ty": "fl", "c": {"a": 0, "k": c_(fillc)}, "o": {"a": 0, "k": 100}, "r": 1}])],
                ip=at, parent=g)
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
    if LANDSCAPE:
        size2 = fonts.fit("OT Display", ["SOUND FAMILIAR?"], 1560, 170)
        rise_pair(c, fonts, "SOUND", "FAMILIAR?", "OT Display", size2, W / 2, H / 2 + CAP * size2 / 2, start=dim_at + 4,
                  gap_frames=9, slot1="problem1", slot2="problem2", label1="Line 1", label2="Line 2")
    else:
        size2 = fonts.fit("OT Display", ["SOUND", "FAMILIAR?"], 920, 150)
        b1 = 880
        rise_line(c, fonts, "SOUND", "OT Display", size2, "white", W / 2, b1, j=2, start=dim_at + 4, slot="problem1",
                  label="Line 1")
        rise_line(c, fonts, "FAMILIAR?", "OT Display", size2, "green", W / 2, b1 + size2 * 1.04, j=2,
                  start=dim_at + 13, slot="problem2", label="Line 2")
    c.cue(dim_at + 4, "tick", 0.6)
    c.cue(204, "riser:33", 0.6)
    curtain_open(c)
    drift(c)
    curtain_close(c)
    return c


# =========================================================================== 3 REVEAL
def wordmark_crash(c, text, family, size, cx, cy, crash, end, color="white", streaks=4, start_scale=350,
                   parent=None, settle_end_scale=94, slot=None, label=None):
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
    return c.text(f"crash: {text}", doc, p=(cx, cy), a=(0, -cap / 2), ip=crash, parent=parent, s=anim(k_main),
                  slot=slot, label=label)


def scene_reveal():
    c = Comp("03 Reveal - OUTTAKES", W, H, 135)
    background(c)
    crash = 2  # with the previous chapter's closed curtain this makes exactly 3 black frames
    wy = H / 2 - 50 if LANDSCAPE else 860
    glow(c, W / 2, wy, 1100 if LANDSCAPE else 950, alphas=(0.6, 0.32, 0.0), ip=crash)
    size = fonts.fit("OT Wordmark", ["OUTTAKES"], 1000 if LANDSCAPE else 820, 300 if LANDSCAPE else 270)
    wordmark_crash(c, "OUTTAKES", "OT Wordmark", size, W / 2, wy, crash, 135)
    c.cue(crash, "boom", 1.0)
    c.cue(crash, "shutter_big", 1.0)
    ts = fonts.fit("OT Display", ["MADE BY PHOTOGRAPHERS,", "FOR PHOTOGRAPHERS."], 920, 56)
    tb = (wy + CAP * size / 2 + 120) if LANDSCAPE else 1030
    rise_line(c, fonts, "MADE BY PHOTOGRAPHERS,", "OT Display", ts, "white", W / 2, tb, j=2, start=40,
              slot="tag1", label="Tagline line 1")
    rise_line(c, fonts, "FOR PHOTOGRAPHERS.", "OT Display", ts, "white", W / 2, tb + ts * 1.25, j=2, start=50,
              slot="tag2", label="Tagline line 2")
    c.cue(40, "tick", 0.5)
    c.cue(50, "tick", 0.5)
    c.shape("black open", [group([rect(W, H, W / 2, H / 2), {"ty": "fl", "c": {"a": 0, "k": [0, 0, 0, 1]},
                                                              "o": {"a": 0, "k": 100}, "r": 1}])], ip=0, op=crash)
    drift(c)
    curtain_close(c)
    return c


# =========================================================================== 4 CLIENTS CHASE YOU
def scene_clients():
    c = Comp("04 Now clients chase you", W, H, 165)
    background(c)
    feature_glow(c)
    sb = armature_headline(c, fonts, "NOW CLIENTS", "CHASE YOU.", "Clubs, brands and players search one place.")
    y0 = sb + 64
    # search field (the client's own input -> typing is allowed here)
    g = c.null("search", p=anim([(18, [0, 40, 0], "entrance-sharp"), (30, [0, 0, 0])]), ip=18)
    s0 = len(c._layers)
    box(c, "search field", L, y0, CW, 110, "surface", r=16, parent=g, ip=18)
    search_icon(c, L + 52, y0 + 55, 40, parent=g, ip=18)
    query = "football photographer"
    gaps = [0, 2, 1, 2, 1, 2, 3, 1, 2, 1, 2, 1, 1, 2, 3, 1, 2, 1, 1, 2, 1]
    tx, ty = L + 96, y0 + 55 + CAP * 40 / 2
    docs = [(18, text_doc("Search photographers", "OT Body", 40, hexc("#7d7a84"), justify=0))]
    t = 26
    for k in range(1, len(query) + 1):
        t += gaps[k - 1]
        docs.append((t, text_doc(query[:k], "OT Body", 40, c_("white"), justify=0)))
        c.cue(t, "key", 0.35)
    c.text("typed query", docs[0][1], p=(tx, ty), keyed_docs=docs, ip=18, parent=g)
    members_opacity(layers_since(c, s0), [(18, 0, "settle-soft"), (26, 100, "hold"), (96, 100, "exit-accelerate"),
                                          (104, 0)])
    # results
    y1 = y0 + 140
    y2 = y1 + 320
    ra = c.null("result A", p=anim([(58, [0, 200, 0], "entrance-sharp"), (72, [0, 0, 0], "hold"),
                                    (96, [0, 0, 0], "exit-accelerate"), (106, [0, -40, 0])]), ip=58, op=107)
    sa = len(c._layers)
    pic(c, "celebrate-fists", L, y1, CW, 300, r=18, parent=ra, ip=58, op=107)
    x = L + 22
    for sp in ("football", "track"):
        x += tag(c, fonts, sp, x, y1 + 300 - 58, 24, parent=ra, ip=58, op=107) + 10
    members_opacity(layers_since(c, sa), [(58, 100, "hold"), (96, 100, "exit-accelerate"), (104, 0)])
    rb = c.null("result B (you)", p=anim([(64, [0, 200, 0], "entrance-sharp"), (78, [0, 0, 0])]), ip=64)
    pic(c, "floodlight-profile", L, y2, CW, 300, r=18, parent=rb, ip=64, focus=(0.45, 0.3))
    box(c, "your profile chip", L + 22, y2 + 22, fonts.width("OT Body Medium", 26, "Your profile") + 36, 46, "green",
        r=8, parent=rb, ip=64)
    label_text(c, "Your profile", "OT Body Medium", 26, "ink", L + 40, y2 + 45 + CAP * 26 / 2, ip=64, parent=rb)
    x = L + 22
    for sp in ("football", "track", "rugby"):
        x += tag(c, fonts, sp, x, y2 + 300 - 58, 24, parent=rb, ip=64) + 10
    c.cue(58, "blip_in", 0.6)
    # your card gets the green outline (drawn on)
    c.shape("you outline", [group([rect(CW + 16, 316, L + CW / 2, y2 + 150, 24), stroke(c_("green"), 5),
                                   {**trim(0, 100), "e": anim([(84, 0, "entrance-sharp"), (98, 100)])}])],
            ip=84, parent=rb)
    c.cue(84, "whoosh", 0.4)
    # the search and the other result clear away; the requests land above YOUR card
    reqs = ["Sports club · season coverage?", "Brand shoot next Saturday?", "Can you shoot our final?"]
    for k, (txt, at) in enumerate(zip(reqs, (100, 116, 132))):
        yt = y0 + 10 + k * 136
        gt = c.null(f"request {k}", p=anim([(at, [0, -60, 0], "entrance-sharp"), (at + 10, [0, 0, 0])]), ip=at)
        s1 = len(c._layers)
        box(c, f"request card {k}", L, yt, CW, 112, "surface", r=22, parent=gt, ip=at,
            stroke_col=c_("white", 0.1), stroke_w=1.5)
        c.shape(f"request dot {k}", [group([{"ty": "el", "d": 1, "s": {"a": 0, "k": [16, 16]},
                                             "p": {"a": 0, "k": [L + 42, yt + 56]}},
                                            {"ty": "fl", "c": {"a": 0, "k": c_("green")}, "o": {"a": 0, "k": 100},
                                             "r": 1}])], ip=at, parent=gt)
        label_text(c, txt, "OT Body Medium", 34, "white", L + 72, yt + 56 + CAP * 34 / 2, ip=at, parent=gt)
        label_text(c, "now", "OT Body", 26, GREY, R - 28, yt + 56 + CAP * 26 / 2, j=1, ip=at, parent=gt)
        members_opacity(layers_since(c, s1), [(at, 0, "settle-soft"), (at + 6, 100)])
        c.cue(at, "blip_in", 0.9)
    curtain_open(c)
    drift(c)
    curtain_close(c)
    return c


# =========================================================================== 5 PORTFOLIO
def scene_portfolio():
    c = Comp("05 Portfolio, organised", W, H, 135)
    background(c)
    feature_glow(c)
    sb = armature_headline(c, fonts, "YOUR PORTFOLIO,", "ORGANISED.", "Every shot in one place, sorted by sport.")
    y0 = sb + 60
    g = c.null("profile header", p=anim([(18, [0, 50, 0], "entrance-sharp"), (32, [0, 0, 0])]), ip=18)
    s0 = len(c._layers)
    pic(c, "floodlight-profile", L, y0, 112, 112, r=56, parent=g, ip=18, focus=(0.42, 0.3))
    label_text(c, "YOUR NAME", "OT Body Medium", 42, "white", L + 136, y0 + 46, parent=g, ip=18, slot="profileName",
               label="Profile name")
    x = L + 136
    for sp in ("football", "rugby", "track"):
        x += tag(c, fonts, sp, x, y0 + 66, 22, parent=g, ip=18) + 10
    members_opacity(layers_since(c, s0), [(18, 0, "settle-soft"), (26, 100)])
    # filter chips (site style)
    cy = y0 + 150
    x = L
    chip_x = {}
    for i, lab in enumerate(["All", "Football", "Rugby", "Track"]):
        at = 28 + i * 3
        gc = c.null(f"chip {lab}", p=anim([(at, [0, 30, 0], "entrance-sharp"), (at + 10, [0, 0, 0])]), ip=at)
        s1 = len(c._layers)
        w = chip(c, fonts, lab, x, cy, 26, active=(lab == "All"), parent=gc, ip=at, op=97 if lab in ("All", "Football") else None)
        members_opacity(layers_since(c, s1), [(at, 0, "settle-soft"), (at + 6, 100)])
        chip_x[lab] = (x, w)
        x += w + 14
    # state change after the tap: Football becomes active, All goes outlined
    chip(c, fonts, "All", chip_x["All"][0], cy, 26, active=False, ip=97)
    chip(c, fonts, "Football", chip_x["Football"][0], cy, 26, active=True, ip=97)
    fx, fw = chip_x["Football"]
    tap(c, fx + fw / 2, cy + 26 * 0.95, appear=88, press=96)
    # portfolio grid assembles (unmask from below, settle)
    gy = cy + 104
    cw2 = (CW - 18) / 2
    rh = (BOTTOM - 40 - gy - 2 * 18) / 3
    shots = ["celebrate-fists", "tackle-night", "stretch-ball", "point-orange", "team-backs", "kids-duel"]
    for i, name in enumerate(shots):
        col, row = i % 2, i // 2
        at = 40 + i * 4
        pic(c, name, L + col * (cw2 + 18), gy + row * (rh + 18), cw2, rh, r=10, ip=at,
            rise=[(at, 80, "entrance-sharp"), (at + 14, 0, "linear")],
            zoom=[(at, 1.15, "settle-soft"), (at + 30, 1.03, "linear"), (135, 1.0)])
    c.cue(40, "whoosh", 0.4)
    curtain_open(c)
    drift(c)
    curtain_close(c)
    return c


# =========================================================================== 6 BOOKING
def scene_booking():
    c = Comp("06 Booked at your rate", W, H, 150)
    background(c)
    feature_glow(c)
    sb = armature_headline(c, fonts, "BOOKED AT", "YOUR RATE.", "Systemised bookings. No lowball DMs.")
    y0 = sb + 60
    # the lowball DM gets struck out and thrown away
    txt = "can do $30?"
    tw = fonts.width("OT Body", 42, txt)
    bh = 42 * 1.25 + 52
    lb = c.null("lowball", p=anim([(14, [0, 40, 0], "entrance-sharp"), (23, [0, 0, 0], "hold"),
                                   (44, [0, 0, 0], "exit-accelerate"), (54, [-1100, 0, 0])]), ip=14, op=55)
    s0 = len(c._layers)
    box(c, "lowball bubble", L, y0, tw + 68, bh, "surface", r=bh / 2, parent=lb, ip=14, op=55)
    label_text(c, txt, "OT Body", 42, "white", L + 34, y0 + bh / 2 + CAP * 42 / 2, parent=lb, ip=14, op=55)
    members_opacity(layers_since(c, s0), [(14, 0, "settle-soft"), (20, 100)])
    c.shape("strike", [group([path([[L + 26, y0 + bh / 2], [L + 42 + tw, y0 + bh / 2]]), stroke(c_("green"), 5),
                              {**trim(0, 100), "e": anim([(28, 0, "entrance-sharp"), (37, 100)])}])],
            ip=28, op=55, parent=lb)
    c.cue(14, "blip_in", 0.8)
    c.cue(28, "whoosh", 0.35)
    c.cue(44, "whoosh", 0.6)
    # booking request card
    yc = y0
    card = c.null("booking card", p=anim([(48, [0, 320, 0], "settle-soft"), (64, [0, 0, 0])]), ip=48)
    rows = [("Date", "Sat 22 Nov · 4:00 PM"), ("Venue", "Jalan Besar Stadium"),
            ("Coverage", "Full match + edited photos"), ("Rate", "$70 · your rate")]
    ry0 = yc + 168
    step = 114
    bty = ry0 + len(rows) * step + 4
    card_h = bty + 100 + 44 - yc
    box(c, "card", L, yc, CW, card_h, "surface", r=28, parent=card, ip=48)
    label_text(c, "Booking request", "OT Body Medium", 44, "white", L + 48, yc + 90, parent=card, ip=48)
    for i, (lab, val) in enumerate(rows):
        yr = ry0 + i * step
        st = 60 + i * 4
        fade_line(c, lab.upper(), "OT Label", 27, GREY, L + 48, yr, start=st, parent=card)
        fade_line(c, val, "OT Body Medium", 40, "green" if lab == "Rate" else "white", L + 48, yr + 48, start=st + 1,
                  parent=card)
        if i < len(rows) - 1:
            box(c, f"hairline {i}", L + 48, yr + 78, CW - 96, 1.5, c_("white", 0.1), parent=card, ip=st)
    # button: tap -> pressed -> Booked
    bcx, bcy = L + CW / 2, bty + 50
    btn = c.null("button", p=(bcx, bcy), a=(bcx, bcy), parent=card, ip=56,
                 s=anim([(56, [100, 100, 100], "hold"), (104, [96, 96, 100], "hold"), (108, [100, 100, 100])]))
    box(c, "confirm", L + 40, bty, CW - 80, 100, "green", r=16, parent=btn, ip=56)
    s1 = len(c._layers)
    label_text(c, "Confirm booking", "OT Body Medium", 38, "ink", bcx, bcy + CAP * 38 / 2, j=2, parent=btn, ip=56, op=114)
    members_opacity(layers_since(c, s1), [(56, 100, "hold"), (108, 100, "exit-accelerate"), (113, 0)])
    bw = fonts.width("OT Body Medium", 38, "Booked")
    check_icon(c, bcx - bw / 2 - 26, bcy, 40, "ink", draw_at=112, parent=btn, ip=112)
    s2 = len(c._layers)
    label_text(c, "Booked", "OT Body Medium", 38, "ink", bcx + 22, bcy + CAP * 38 / 2, j=2, parent=btn, ip=112)
    members_opacity(layers_since(c, s2), [(112, 0, "settle-soft"), (118, 100)])
    tap(c, bcx + 60, bcy + 6, appear=96, press=104)
    c.cue(112, "chime", 0.9)
    c.cue(48, "whoosh", 0.5)
    curtain_open(c)
    drift(c)
    curtain_close(c)
    return c


# =========================================================================== 7 INVOICES
def scene_invoices():
    c = Comp("07 Invoices, done for you", W, H, 135)
    background(c)
    feature_glow(c)
    sb = armature_headline(c, fonts, "INVOICES,", "DONE FOR YOU.", "Proper invoices for every client, big or small.")
    y0 = sb + 56
    ph = 760
    pcx, pcy = W / 2, y0 + ph / 2
    paper = c.null("invoice", p=anim([(18, [pcx, pcy + 320, 0], "settle-soft"), (36, [pcx, pcy, 0])]), a=(pcx, pcy),
                   r=anim([(18, -5, "settle-soft"), (36, 0)]), ip=18)
    box(c, "paper", L, y0, CW, ph, "cream", r=12, parent=paper, ip=18)
    ink = c_("ink")
    ink55 = hexc("#6f6a64")
    fade_line(c, "INVOICE", "OT Display", 54, ink, L + 50, y0 + 100, start=30, parent=paper)
    fade_line(c, "#OT-0142", "OT Body", 28, ink55, R - 50, y0 + 94, j=1, start=32, parent=paper)
    fade_line(c, "BILLED TO", "OT Label", 24, ink55, L + 50, y0 + 176, start=40, parent=paper)
    fade_line(c, "Sports club", "OT Body Medium", 36, ink, L + 50, y0 + 222, start=41, parent=paper)
    fade_line(c, "DATE", "OT Label", 24, ink55, L + 480, y0 + 176, start=42, parent=paper)
    fade_line(c, "22 Nov 2026", "OT Body Medium", 36, ink, L + 480, y0 + 222, start=43, parent=paper)
    box(c, "rule 1", L + 50, y0 + 266, CW - 100, 2, hexc("#111113", 0.14), parent=paper, ip=46)
    fade_line(c, "Full match coverage", "OT Body", 32, ink, L + 50, y0 + 334, start=50, parent=paper)
    fade_line(c, "$70.00", "OT Body Medium", 32, ink, R - 50, y0 + 334, j=1, start=51, parent=paper)
    fade_line(c, "Edited photos (40)", "OT Body", 32, ink, L + 50, y0 + 396, start=55, parent=paper)
    fade_line(c, "Included", "OT Body Medium", 32, ink, R - 50, y0 + 396, j=1, start=56, parent=paper)
    box(c, "rule 2", L + 50, y0 + 444, CW - 100, 2, hexc("#111113", 0.14), parent=paper, ip=60)
    fade_line(c, "Total", "OT Body Medium", 36, ink, L + 50, y0 + 524, start=64, parent=paper)
    fade_line(c, "$70.00", "OT Display", 50, ink, R - 50, y0 + 528, j=1, start=66, parent=paper)
    fade_line(c, "PAYMENT", "OT Label", 24, ink55, L + 50, y0 + 620, start=72, parent=paper)
    fade_line(c, "Due on booking", "OT Body", 32, ink, L + 50, y0 + 664, start=74, parent=paper)
    # "Sent" stamp pops in (one flourish per beat)
    sx, sy = R - 150, y0 + 640
    stamp = c.null("sent stamp", p=(sx, sy), a=(sx, sy), parent=paper, ip=98,
                   s=anim([(98, [55, 55, 100], "expressive-pop"), (106, [108, 108, 100], "settle-soft"),
                           (112, [100, 100, 100])]))
    box(c, "sent pill", sx - 95, sy - 36, 190, 72, "green", r=36, parent=stamp, ip=98)
    check_icon(c, sx - 46, sy, 34, "ink", draw_at=101, parent=stamp, ip=98)
    label_text(c, "Sent", "OT Body Medium", 34, "ink", sx + 20, sy + CAP * 34 / 2, j=2, parent=stamp, ip=98)
    c.cue(18, "whoosh", 0.5)
    c.cue(98, "chime", 0.9)
    curtain_open(c)
    drift(c)
    curtain_close(c)
    return c


# =========================================================================== 8 SECURE PAYMENTS
def scene_payments():
    c = Comp("08 Paid, even if they cancel", W, H, 150)
    background(c)
    feature_glow(c)
    sb = armature_headline(c, fonts, "PAID. EVEN IF", "THEY CANCEL.", "Secure payments make sure you get paid.")
    y0 = sb + 56
    c1 = c.null("payment card", p=anim([(18, [0, 260, 0], "settle-soft"), (34, [0, 0, 0])]), ip=18)
    box(c, "card 1", L, y0, CW, 350, "surface", r=28, parent=c1, ip=18)
    c.shape("lock badge", [group([{"ty": "el", "d": 1, "s": {"a": 0, "k": [96, 96]}, "p": {"a": 0, "k": [L + 96, y0 + 84]}},
                                  {"ty": "fl", "c": {"a": 0, "k": c_("green")}, "o": {"a": 0, "k": 100}, "r": 1}])],
            parent=c1, ip=18)
    lock_icon(c, L + 96, y0 + 86, 44, "ink", parent=c1, ip=18)
    label_text(c, "Payment secured", "OT Body Medium", 40, "white", L + 170, y0 + 84 + CAP * 40 / 2, parent=c1, ip=18)
    fade_line(c, "$70.00", "OT Display", 84, "white", L + 48, y0 + 250, start=30, parent=c1)
    fade_line(c, "Sat 22 Nov · Jalan Besar Stadium", "OT Body", 28, GREY, L + 48, y0 + 306, start=34, parent=c1)
    c.cue(18, "whoosh", 0.5)
    c.cue(30, "chime_soft", 0.6)
    yb = y0 + 380
    c2 = c.null("cancel card", p=anim([(64, [0, 260, 0], "settle-soft"), (80, [0, 0, 0])]), ip=64)
    box(c, "card 2", L, yb, CW, 330, "surface", r=28, parent=c2, ip=64)
    label_text(c, "Client cancelled the booking", "OT Body", 34, "white", L + 48, yb + 76, parent=c2, ip=64, o=75)
    box(c, "card 2 rule", L + 48, yb + 118, CW - 96, 1.5, c_("white", 0.1), parent=c2, ip=64)
    c.shape("check badge", [group([{"ty": "el", "d": 1, "s": {"a": 0, "k": [80, 80]},
                                    "p": {"a": 0, "k": [L + 88, yb + 216]}},
                                   {"ty": "fl", "c": {"a": 0, "k": c_("green")}, "o": {"a": 0, "k": 100}, "r": 1}])],
            parent=c2, ip=64)
    check_icon(c, L + 88, yb + 217, 40, "ink", draw_at=96, parent=c2, ip=96)
    label_text(c, "Cancellation fee", "OT Body Medium", 40, "white", L + 152, yb + 206, parent=c2, ip=64)
    fade_line(c, "Paid to you", "OT Body Medium", 34, "green", L + 152, yb + 256, start=98, parent=c2)
    c.cue(64, "blip_in", 0.7)
    c.cue(98, "chime", 0.9)
    curtain_open(c)
    drift(c)
    curtain_close(c)
    return c


# =========================================================================== 9 EXPOSURE
def scene_exposure():
    c = Comp("09 Free exposure, built in", W, H, 150)
    background(c)
    feature_glow(c)
    sb = armature_headline(c, fonts, "FREE EXPOSURE,", "BUILT IN.", "Shot of the Week puts you in front of clients.")
    y0 = sb + 56
    mh = 520
    pic(c, "portrait-flare", L, y0, CW, mh, r=8, ip=18, focus=(0.5, 0.3),
        rise=[(18, 90, "entrance-sharp"), (32, 0, "linear")], zoom=[(18, 1.12, "settle-soft"), (150, 1.0)])
    from lottie_kit import gradient
    c.shape("photo shade", [group([rect(CW, 260, L + CW / 2, y0 + mh - 130),
                                    gradient([(0, "#000000"), (1, "#000000")], [0, y0 + mh - 260], [0, y0 + mh],
                                             alpha_stops=[(0, 0), (1, 0.65)])])], ip=18)
    rise_line(c, fonts, "SHOT OF THE WEEK", "OT Display", 46, "white", L + 36, y0 + mh - 40, j=0, start=30,
              slot="sotw", label="Feature title")
    fx, fy = L + 36, y0 + 34
    fw = fonts.width("OT Body Medium", 28, "Featured") + 40
    feat = c.null("featured chip", p=(fx + fw / 2, fy + 24), a=(fx + fw / 2, fy + 24), ip=96,
                  s=anim([(96, [55, 55, 100], "expressive-pop"), (104, [108, 108, 100], "settle-soft"),
                          (110, [100, 100, 100])]))
    box(c, "featured", fx, fy, fw, 48, "green", r=8, parent=feat, ip=96)
    label_text(c, "Featured", "OT Body Medium", 28, "ink", fx + fw / 2, fy + 24 + CAP * 28 / 2, j=2, parent=feat, ip=96)
    ys = y0 + mh + 20
    sh = BOTTOM - 70 - ys
    strip = c.null("nominees strip", p=anim([(50, [0, 220, 0], "settle-soft"), (66, [0, 0, 0])]), ip=50)
    box(c, "cream strip", L, ys, CW, sh, "cream", r=8, parent=strip, ip=50)
    label_text(c, "SHOT OF THE WEEK NOMINEES", "OT Label", 24, "ink", L + 30, ys + 46, parent=strip, ip=50)
    tw_ = (CW - 60 - 2 * 16) / 3
    th = sh - 120
    for i, (name, title) in enumerate([("point-orange", "MATCH POINT"), ("kids-duel", "FINALS"),
                                       ("stretch-ball", "TOUCH")]):
        at = 62 + i * 4
        tx = L + 30 + i * (tw_ + 16)
        pic(c, name, tx, ys + 66, tw_, th, ip=at, parent=strip, rise=[(at, 60, "entrance-sharp"), (at + 12, 0)])
        label_text(c, title, "OT Display", 20, "ink", tx, ys + 66 + th + 30, parent=strip, ip=at)
    c.cue(18, "whoosh", 0.5)
    c.cue(50, "whoosh", 0.35)
    c.cue(96, "chime", 0.8)
    curtain_open(c)
    drift(c)
    curtain_close(c)
    return c


# =========================================================================== 10 CTA
def scene_cta():
    c = Comp("10 Sign up free - 20.11 5PM", W, H, 240)
    background(c)
    glow(c, W / 2, 2100, 1300, colors=[(0, COL["sky"]), (0.45, COL["violet"]), (1, COL["violetDeep"])],
         alphas=(0.55, 0.42, 0.0))
    if LANDSCAPE:
        s1 = fonts.fit("OT Display", ["SIGN UP FREE."], 1500, 200)
        rise_pair(c, fonts, "SIGN UP", "FREE.", "OT Display", s1, W / 2, H / 2 + CAP * s1 / 2, start=8, exit_at=56,
                  slot1="cta1", slot2="cta2", label1="Sign-up line 1", label2="Sign-up line 2")
        c.cue(8, "tick", 0.6)
        s2 = fonts.fit("OT Display", ["SET UP YOUR PROFILE", "FROM 16 NOV."], 1500, 130)
        b1 = H / 2 - s2 * 0.12
        rise_line(c, fonts, "SET UP YOUR PROFILE", "OT Display", s2, "white", W / 2, b1, j=2, start=66, exit_at=116,
                  slot="setup1", label="Setup line 1")
        rise_pair(c, fonts, "FROM", "16 NOV.", "OT Display", s2, W / 2, b1 + s2 * 1.08, start=74, exit_at=118,
                  slot1="setup2", slot2="profilesOpen", label1="Setup line 2", label2="Profiles-open date")
    else:
        s1 = fonts.fit("OT Display", ["SIGN UP", "FREE."], 920, 180)
        b1 = 860
        rise_line(c, fonts, "SIGN UP", "OT Display", s1, "white", W / 2, b1, j=2, start=8, exit_at=56, slot="cta1",
                  label="Sign-up line 1")
        rise_line(c, fonts, "FREE.", "OT Display", s1, "green", W / 2, b1 + s1 * 1.02, j=2, start=16, exit_at=58,
                  slot="cta2", label="Sign-up line 2")
        lines = ["SET UP YOUR", "PROFILE FROM", "16 NOV."]
        s2 = fonts.fit("OT Display", lines, 920, 112)
        for i, ln in enumerate(lines):
            rise_line(c, fonts, ln, "OT Display", s2, "green" if i == 2 else "white", W / 2, 760 + i * s2 * 1.08, j=2,
                      start=66 + i * 8, exit_at=116 + i * 2, slot="profilesOpen" if i == 2 else f"setup{i + 1}",
                      label="Profiles-open date" if i == 2 else f"Setup line {i + 1}")
        c.cue(8, "tick", 0.6)
    c.cue(66, "tick", 0.6)
    c.cue(112, "riser:16", 0.7)
    # the date hits
    crash = 128
    dy_up = -150 if LANDSCAPE else -230
    dcy = H / 2 - 60 if LANDSCAPE else 860
    dg = c.null("date group", p=anim([(172, [0, 0, 0], "travel-balanced"), (188, [0, dy_up, 0])]), ip=crash, op=206)
    dsize = fonts.fit("OT Display", ["20.11"], 900 if LANDSCAPE else 860, 300 if LANDSCAPE else 320)
    wordmark_crash(c, "20.11", "OT Display", dsize, W / 2, dcy, crash, 206, color="green", start_scale=320,
                   parent=dg, settle_end_scale=96, slot="liveDate", label="Live date")
    rise_line(c, fonts, "WE GO LIVE · 5PM SGT", "OT Body Medium", 52, "white", W / 2,
              dcy + CAP * dsize / 2 + (96 if LANDSCAPE else 112),
              j=2, start=138, parent=dg, op=206, slot="liveLine", label="Live time line")
    flash(c, crash, peak=25, dur=3)
    c.cue(crash, "boom", 1.0)
    c.cue(crash, "shutter_big", 0.9)
    # the button, pressed by a finger
    bcy = (H / 2 + 270) if LANDSCAPE else 1050
    btn = c.null("cta button", p=(W / 2, bcy), a=(W / 2, bcy), ip=180, op=206,
                 s=anim([(180, [70, 70, 100], "expressive-pop"), (190, [104, 104, 100], "settle-soft"),
                         (196, [100, 100, 100], "hold"), (200, [95, 95, 100], "hold"), (205, [100, 100, 100])]))
    x0, total, bh = cta_button(c, fonts, "Sign up free · outtakes.sg", W / 2, bcy, 40, parent=btn, ip=180, op=206,
                               slot="ctaButton")
    c.cue(180, "pop", 0.6)
    tap(c, x0 + total - bh / 2, bcy + 4, appear=192, press=200)
    # end card on the site's signature gradient
    fin = 206
    brand_gradient_rect(c, -120 if LANDSCAPE else -200, H + (160 if LANDSCAPE else 260), ip=fin)
    wsize = fonts.fit("OT Wordmark", ["OUTTAKES"], 900 if LANDSCAPE else 760, 260 if LANDSCAPE else 240)
    cap = CAP * wsize
    wy = H / 2 - 40 if LANDSCAPE else 880
    c.text("end wordmark", text_doc("OUTTAKES", "OT Wordmark", wsize, c_("white"), justify=2), p=(W / 2, wy),
           a=(0, -cap / 2), ip=fin, s=anim([(fin, [110, 110, 100], "entrance-sharp"), (fin + 10, [100, 100, 100], "linear"),
                                           (240, [96, 96, 100])]), slot="endBrand", label="End brand")
    fade_line(c, "outtakes.sg · 20.11 · 5PM SGT", "OT Body Medium", 40, "white", W / 2,
              (wy + cap / 2 + 100) if LANDSCAPE else 1000, j=2, start=fin + 8)
    flash(c, fin, peak=30, dur=3)
    c.cue(fin, "shutter_big", 0.9)
    c.cue(fin, "boom_small", 0.5)
    curtain_open(c)
    drift(c)
    curtain_close(c, dur=6)
    return c


SCENES = [scene_hook, scene_problem, scene_reveal, scene_clients, scene_portfolio, scene_booking, scene_invoices,
          scene_payments, scene_exposure, scene_cta]


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
        print(f"scene-{n}: {c.name:34s} {c.frames:4d}f  layers={len(doc['layers']):3d}  assets={len(c.assets)}")
        offset += c.frames
    (OUT / "cues.json").write_text(json.dumps({"fps": 30, "total": offset, "scenes": meta,
                                               "cues": sorted(cues, key=lambda x: x["frame"])}, indent=1))
    print(f"total {offset} frames = {offset / 30:.1f}s")


if __name__ == "__main__":
    main()
