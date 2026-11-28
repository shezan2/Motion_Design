#!/usr/bin/env python3
"""Nick R.L. intro film: one continuous 600-frame Lottie comp, 16:9 (1920 x 1080, 30 fps).

  python tools/build_film.py        -> public/projects/nickrl-intro-16x9/scene-1/lottie.json + audio/cues.json

Beats (PLAN.md): 1 hook (counter to 180 days) - 2 sold in 1 month - 3 Right advice/strategy/execution/home
- 4 the house becomes his name card - 5 scale cut, WhatsApp pill, cursor press, end hold.
All copy and facts are Nick's own (see PLAN.md sources). Retime with the T table below.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lottie_kit as lk  # noqa: E402
from lottie_kit import Comp, anim, hexc, static  # noqa: E402
import nk  # noqa: E402
from nk import C, H, W, col, ease  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BRAND = ROOT / "brand"
SCENE = ROOT / "public" / "projects" / "nickrl-intro-16x9" / "scene-1"
FRAMES = 600

# ----------------------------------------------------------------------------------------------- copy (one place)
COPY = {
    "count_label": "days on the market",
    "sold": "Sold",
    "sold_rest": "in 1 month.",
    "case": "Blk 123 Yishun · 4-room HDB",
    "right": "Right",
    "keywords": ["advice.", "strategy.", "execution.", "home."],
    "name": "NICK R.L.",
    "tagline": "Your trusted agent",
    "title": "Associate Division Director",
    "chips": ["20+ years", "HDB", "Condo", "New launch"],
    "cta": "WhatsApp 9859 9857",
    "legal1": "Nick R.L. · CEA Reg. No. R002622D",
    "legal2": "PropNex Realty Pte Ltd · CEA Licence No. L3008022J",
}
DAYS = 180

# ----------------------------------------------------------------------------------------------- timeline (frames)
T = {
    # beat 1: hook
    "count_end": 60, "pause_end": 78,
    # beat 2: sold
    "dot_in": 78, "arc_a": 84, "arc_b": 94, "digits_out": 82, "sold_in": 88, "sold_land": 97,
    "month_in": 100, "case_in": 112, "b2_out": 158, "complete_a": 160, "complete_b": 171,
    "fly_a": 170, "fly_b": 186,
    # beat 3: promise
    "inner_a": 182, "inner_b": 194, "dot_pop": 190, "arrow_a": 186, "arrow_hit": 193,
    "right_in": 188,
    "kw_in": [192, 226, 268, 310], "kw_out": [222, 264, 306, 344],
    "target_out": 220,
    "knight_a": 224, "knight_b": 238, "knight_land": 241, "knight_out": 262,
    "check_circle_a": 266, "check_circle_b": 278, "check_a": 276, "check_b": 282, "check_out": 304,
    "roof_a": 308, "roof_b": 318, "walls_a": 312, "walls_b": 324, "door_a": 318, "door_b": 326,
    "right_out": 344,
    # beat 4: card
    "morph_a": 348, "morph_b": 366,
    "nick_in": 358, "name_in": 370, "tag_in": 377, "rule_in": 381, "title_in": 385, "badge_in": 390,
    "chips_in": 395, "legal_in": 405,
    # beat 5: cta
    "cut": 480, "pill_in": 484, "cursor_in": 516, "cursor_park": 548, "press": 558, "sweep_a": 562, "sweep_b": 580,
    "sweep0_a": 432, "sweep0_b": 452,
}

# geometry
RC = (960, 500)       # ring centre
RR = 310              # ring radius
IC = (960, 318)       # icon centre
IS = 10.5             # icon scale (Tabler 24-unit grid -> 252 px)
ICON_W = 7.0          # icon stroke width (px)
CARD = dict(cx=960, cy=540, w=1440, h=760, r=32)
COLX = 868            # card text column
cues = []


def cue(frame, kind, gain_db=0.0, note=""):
    cues.append({"frame": int(frame), "t": round(frame / 30, 4), "kind": kind, "gain_db": gain_db, "note": note})


def vis(c, name, items, **kw):
    return c.shape(name, items, **kw)


def stroke_c(color, width, opacity=100):
    s = lk.stroke(hexc(color) if isinstance(color, str) else color, width, opacity)
    s["lc"], s["lj"] = 2, 2
    return s


# ----------------------------------------------------------------------------------------------- beat 1 + 2: ring
def build_ring(c: Comp):
    circ = nk.circle_shape(RC[0], RC[1], RR)
    # track
    vis(c, "ring track", [lk.group([nk.sh(circ), stroke_c(C["track"], 4)])],
        o=anim([(0, 100, "hold"), (T["arc_a"], 100, "softInOut"), (T["arc_a"] + 12, 45, "hold"), (T["b2_out"], 45, "accelExit"), (T["b2_out"] + 8, 0, "hold")]),
        op=T["b2_out"] + 10)
    # grey progress: time on the market, decelerating (days drag on)
    grey_trim = lk.trim(0, anim([(0, 0.6, "glide"), (T["count_end"], 100, "hold")]))
    vis(c, "ring grey", [lk.group([nk.sh(circ), stroke_c(C["grey"], 8), grey_trim])],
        o=anim([(0, 100, "hold"), (T["arc_a"], 100, "softInOut"), (T["arc_a"] + 12, 28, "hold"), (T["b2_out"], 28, "accelExit"), (T["b2_out"] + 8, 0, "hold")]),
        op=T["b2_out"] + 10)

    # gold ring: 1 month = a sixth of the circle, then completes and flies into the target's outer circle
    sixth = 100 / 6
    ring_end = anim([(T["arc_a"], 0, "snapSettle"), (T["arc_b"], sixth, "hold"), (T["complete_a"], sixth, "gentleIn"),
                     (T["complete_b"], 100, "hold")])
    gap_s, gap_o = 78.56, 83.6        # Tabler target outer arc: gap from 6.4 deg to 83.6 deg clockwise from 12
    ring_end_k = ring_end["k"]
    ring_end_k[-1]["o"] = {"x": [0.3], "y": [0.0]}
    ring_end_k[-1]["i"] = {"x": [0.2], "y": [1.0]}
    ring_end_k[-1].pop("h", None)
    ring_end_k.append({"t": T["fly_b"] + 2, "s": [gap_s]})
    ring_off = anim([(T["fly_a"] + 6, 0, "softLand"), (T["fly_b"] + 2, gap_o, "hold")])
    trim_gold = {"ty": "tm", "s": static(0), "e": ring_end, "o": ring_off, "m": 1}
    # stroke baked per frame so the visible width goes 8 -> ICON_W while the layer scales 1 -> 0.252
    s_end = (9 * IS) / RR
    sw_keys, sc_keys, p_keys = [], [], []
    for f in range(T["fly_a"], T["fly_b"] + 1):
        e = ease("snapSettle", (f - T["fly_a"]) / (T["fly_b"] - T["fly_a"]))
        s = 1 + (s_end - 1) * e
        sw_keys.append((f, (8 + (ICON_W - 8) * e) / s, "cruise"))
    sw = anim([(0, 8, "hold")] + sw_keys)
    sc = anim([(T["fly_a"], [100, 100], "snapSettle"), (T["fly_b"], [s_end * 100, s_end * 100], "hold")])
    pos = anim([(T["fly_a"], [RC[0], RC[1]], "snapSettle"), (T["fly_b"], [IC[0], IC[1]], "hold")])
    gold = vis(c, "ring gold", [lk.group([nk.sh(circ), stroke_c(C["gold"], 8), trim_gold])], ip=T["arc_a"] - 1,
               op=T["target_out"] + 10, a=RC, p=pos, s=sc)
    nk.layer(c, gold)["shapes"][0]["it"][1]["w"] = sw
    nk.with_fx(c, gold, nk.gblur(anim([(T["fly_a"], 0, "glide"), (T["fly_a"] + 5, 5, "softInOut"), (T["fly_b"] - 2, 0, "hold")])))
    # the target's outer arc un-draws when the knight arrives
    trim_gold["s"] = anim([(T["target_out"], 0, "accelExit"), (T["target_out"] + 8, gap_s, "hold")])
    # soft glow under the gold arc (same trims), only while it is large
    glow_trim = {"ty": "tm", "s": static(0), "e": json.loads(json.dumps(ring_end)), "o": static(0), "m": 1}
    gl = vis(c, "ring gold glow", [lk.group([nk.sh(circ), stroke_c(C["gold"], 18), glow_trim])], ip=T["arc_a"] - 1,
             op=T["fly_a"], o=anim([(T["arc_a"], 0, "glide"), (T["arc_b"], 55, "hold"), (T["complete_a"] - 4, 55, "gentleIn"), (T["complete_a"] + 6, 0, "hold")]))
    nk.with_fx(c, gl, nk.gblur(22))

    # gold dot at the arc head (the carrier), 12 o'clock -> 60 deg, then rides to the top and dissolves
    poly = nk.shape_polyline(circ, 64)
    dot_keys = [(T["dot_in"], list(nk.point_at(poly, 0.0)), "hold")]
    for f in range(T["arc_a"], T["arc_b"] + 1):
        fr = sixth / 100 * ease("snapSettle", (f - T["arc_a"]) / (T["arc_b"] - T["arc_a"]))
        dot_keys.append((f, list(nk.point_at(poly, fr)), "cruise"))
    dot_keys.append((T["complete_a"], list(nk.point_at(poly, sixth / 100)), "cruise"))
    for f in range(T["complete_a"] + 1, T["complete_b"] + 1):
        e = ease("gentleIn", (f - T["complete_a"]) / (T["complete_b"] - T["complete_a"]))
        fr = sixth / 100 + (1 - sixth / 100) * e
        dot_keys.append((f, list(nk.point_at(poly, min(fr, 0.9999))), "cruise"))
    dot = vis(c, "gold dot", [lk.group([lk.ellipse(18, 18), lk.fill(col("gold"))])],
              p=anim(dot_keys),
              s=anim([(T["dot_in"], [0, 0], "snapSettle"), (T["dot_in"] + 5, [100, 100], "hold"),
                      (T["complete_b"] - 3, [100, 100], "accelExit"), (T["complete_b"] + 2, [0, 0], "hold")]),
              ip=T["dot_in"], op=T["complete_b"] + 3)
    nk.with_fx(c, dot, nk.drop_shadow(C["gold"], 0.9, 0, 0, 24))

    # ticks for the counter: every 15 days crossed (dense early, sparse as time drags)
    last = 0
    for f in range(0, T["count_end"] + 1):
        v = day_value(f)
        if v // 15 > last // 15:
            cue(f, "tick", -2.0 if v < 150 else -4.0, f"day {v}")
        last = v
    cue(T["arc_a"] + 2, "whoosh_short", -3.0, "gold arc shoots a sixth of the ring (whoosh peak at max speed)")
    cue(T["sold_land"], "hit_sold", 0.0, "Sold lands (the one big hit)")
    # texture (real-sfx texture layer): quiet real sounds on picture moves that sit in the long hold
    cue(T["sold_land"] + 3, "shimmer", -15.0, "texture: the light turns warm")
    cue(T["month_in"] + 5, "pop", -5.0, "texture: 'in 1 month.' lands")
    cue(T["case_in"] + 5, "pop", -9.0, "texture: case line lands")
    cue(T["b2_out"] + 2, "whoosh_short", -15.0, "texture: words leave")
    cue(T["fly_a"] + 2, "whoosh_deep", -4.0, "gold ring completes and flies into the target (peak)")


def build_notches(c: Comp):
    """Six month marks around the ring: each lights as the grey time passes it; the gold arc lights one."""
    import math as _m
    r0, r1 = RR + 22, RR + 44
    for k in range(6):
        ang = _m.radians(60 * k)
        sx, sy = _m.sin(ang), -_m.cos(ang)
        p0 = (RC[0] + r0 * sx, RC[1] + r0 * sy)
        p1 = (RC[0] + r1 * sx, RC[1] + r1 * sy)
        line = nk.shape_from_points([(p0, (0, 0), (0, 0)), (p1, (0, 0), (0, 0))], False)
        # frame when the grey arc reaches this month
        f_lit = next((f for f in range(0, T["count_end"] + 1) if ease("glide", f / T["count_end"]) >= k / 6 - 1e-6), 0)
        out = T["b2_out"]
        vis(c, f"notch {k}", [lk.group([nk.sh(line), stroke_c(C["track"], 5)])],
            o=anim([(0, 100, "hold"), (out, 100, "accelExit"), (out + 8, 0, "hold")]), op=out + 9)
        vis(c, f"notch lit {k}", [lk.group([nk.sh(line), stroke_c(C["grey"], 5)])],
            o=anim([(max(0, f_lit - 1), 0, "glide"), (f_lit + 4, 100, "hold"), (T["arc_a"], 100, "softInOut"), (T["arc_a"] + 12, 40, "hold"),
                    (out, 40, "accelExit"), (out + 8, 0, "hold")]), ip=max(0, f_lit - 1), op=out + 9)
        if k in (0, 1):
            g_on = T["arc_a"] if k == 0 else T["arc_b"] - 1
            gl = vis(c, f"notch gold {k}", [lk.group([nk.sh(line), stroke_c(C["gold"], 5)])],
                     o=anim([(g_on, 0, "glide"), (g_on + 5, 100, "hold"), (out, 100, "accelExit"), (out + 8, 0, "hold")]), ip=g_on, op=out + 9)


def day_value(f):
    p = ease("glide", min(1.0, f / T["count_end"]))
    return 1 + round((DAYS - 1) * p)


def build_counter(c: Comp):
    size = 250
    fam = "NK Sans Light"
    adv = max(nk.fonts.width(fam, size, d) for d in "0123456789")
    xs = [RC[0] + (k - 1) * adv for k in range(3)]
    base_y = 534
    out_a = T["digits_out"]
    for k in range(3):
        docs = []
        prev = None
        for f in range(0, T["count_end"] + 1):
            v = day_value(f)
            s = f"{v:03d}"
            lead = len(str(v))
            dim = k < 3 - lead
            key = (s[k], dim)
            if key != prev:
                docs.append((f, nk.tdoc(s[k], fam, size, C["dim_digit"] if dim else C["ink"], justify=2)))
                prev = key
        ind = c.text(f"digit {k}", docs[0][1], keyed_docs=docs,
                     p=anim([(0, [xs[k], base_y], "hold"), (out_a, [xs[k], base_y], "accelExit"), (out_a + 6, [xs[k], base_y - 56], "hold")]),
                     o=anim([(0, 100, "hold"), (out_a, 100, "gentleIn"), (out_a + 6, 0, "hold")]), op=out_a + 7)
        nk.with_fx(c, ind, nk.gblur(anim([(0, 0, "hold"), (out_a, 0, "gentleIn"), (out_a + 6, 16, "hold")])))
    lab = c.text("count label", nk.tdoc(COPY["count_label"], "NK Sans", 46, C["grey"], justify=2),
                 p=anim([(0, [RC[0], 612], "hold"), (out_a, [RC[0], 612], "accelExit"), (out_a + 6, [RC[0], 570], "hold")]),
                 o=anim([(0, 100, "hold"), (out_a, 100, "gentleIn"), (out_a + 6, 0, "hold")]), op=out_a + 7)
    nk.with_fx(c, lab, nk.gblur(anim([(0, 0, "hold"), (out_a, 0, "gentleIn"), (out_a + 6, 14, "hold")])))


def build_sold(c: Comp):
    out = T["b2_out"]
    nk.blur_word(c, "Sold", COPY["sold"], "NK Serif Italic", 240, C["gold"], RC[0], 538, T["sold_in"], dur=9, rise=40,
                 blur=16, t_out=out, out_dy=44, out_dur=8)
    nk.blur_word(c, "in 1 month", COPY["sold_rest"], "NK Sans", 70, C["ink"], RC[0], 630, T["month_in"], dur=12, rise=24,
                 t_out=out, out_dy=44, out_dur=8)
    nk.blur_word(c, "case", COPY["case"], "NK Sans", 42, C["grey"], RC[0], 900, T["case_in"], dur=12, rise=18,
                 t_out=out - 2, out_dy=40, out_dur=8)


# ----------------------------------------------------------------------------------------------- beat 3: icons + words
def icon_paths(name):
    return [nk.svg_subpaths(d, nk.icon_tx(IC[0], IC[1], IS)) for d in nk.read_icon(BRAND / "icons" / f"{name}.svg")]


def draw_layer(c: Comp, name, shapes, draw, undraw=None, ip=0, op=None, width=ICON_W, color=None, extra=None, **kw):
    """Gold line icon part: trim end 0 -> 100 over `draw` (a, b, ease); retract with trim start over `undraw`."""
    a, b, e = draw
    tr_e = anim([(a, 0, e), (b, 100, "hold")])
    tr_s = anim([(undraw[0], 0, "accelExit"), (undraw[1], 100, "hold")]) if undraw else static(0)
    items = [nk.sh(s) for s in shapes] + [stroke_c(color or C["gold"], width), {"ty": "tm", "s": tr_s, "e": tr_e, "o": static(0), "m": 2}]
    if extra:
        items += extra
    return vis(c, name, [lk.group(items)], ip=ip, op=op, **kw)


def build_icons(c: Comp):
    # --- target: inner arc, centre dot, arrow (outer arc = the flown ring)
    inner = nk.circle_shape(IC[0], IC[1], 5 * IS)
    vis(c, "target inner", [lk.group([nk.sh(inner), stroke_c(C["gold"], ICON_W),
        {"ty": "tm", "s": anim([(T["target_out"], 0, "accelExit"), (T["target_out"] + 8, 75, "hold")]),
         "e": anim([(T["inner_a"], 0, "glide"), (T["inner_b"], 75, "hold")]), "o": static(90), "m": 1}])],
        ip=T["inner_a"] - 1, op=T["target_out"] + 9)
    vis(c, "target dot", [lk.group([lk.ellipse(13, 13), lk.fill(col("gold"))])], p=IC,
        s=anim([(T["dot_pop"], [0, 0], "snapSettle"), (T["dot_pop"] + 6, [100, 100], "hold"), (T["target_out"] + 2, [100, 100], "accelExit"), (T["target_out"] + 7, [0, 0], "hold")]),
        ip=T["dot_pop"], op=T["target_out"] + 8)
    arrow = [s for group in icon_paths("target-arrow")[3:] for s in group]
    rot = anim([(T["arrow_hit"], 0, "softInOut"), (T["arrow_hit"] + 2, -7, "softInOut"), (T["arrow_hit"] + 5, 4.5, "softInOut"),
                (T["arrow_hit"] + 8, -2, "softInOut"), (T["arrow_hit"] + 11, 0.8, "softInOut"), (T["arrow_hit"] + 14, 0, "hold")])
    off = 92
    vis(c, "arrow", [lk.group([nk.sh(s) for s in arrow] + [stroke_c(C["gold"], ICON_W)])], a=IC,
        p=anim([(T["arrow_a"], [IC[0] + off, IC[1] - off], "whip"), (T["arrow_hit"], [IC[0], IC[1]], "hold"),
                (T["target_out"], [IC[0], IC[1]], "accelExit"), (T["target_out"] + 7, [IC[0] + 30, IC[1] - 30], "hold")]),
        r=rot, o=anim([(T["arrow_a"], 0, "cruise"), (T["arrow_a"] + 3, 100, "hold"), (T["target_out"], 100, "gentleIn"), (T["target_out"] + 7, 0, "hold")]),
        ip=T["arrow_a"], op=T["target_out"] + 8)
    cue(T["arrow_hit"], "arrow", -1.0, "arrow hits the target: Right advice")

    # --- knight: head draws, base draws, the piece is set down
    kn = icon_paths("chess-knight")
    land = T["knight_land"]
    kpos = anim([(T["knight_a"], [0, -16], "hold"), (land - 5, [0, -16], "softLand"), (land, [0, 0], "hold")])
    draw_layer(c, "knight head", kn[1], (T["knight_a"], T["knight_b"], "glide"), (T["knight_out"], T["knight_out"] + 8),
               ip=T["knight_a"] - 1, op=T["knight_out"] + 9, p=kpos)
    draw_layer(c, "knight base", kn[0], (T["knight_a"] + 6, T["knight_b"] + 2, "glide"), (T["knight_out"], T["knight_out"] + 8),
               ip=T["knight_a"] + 5, op=T["knight_out"] + 9, p=kpos)
    cue(land, "chess", -1.0, "knight set down: Right strategy")

    # --- check in a circle
    cc = icon_paths("circle-check")
    draw_layer(c, "check circle", cc[0], (T["check_circle_a"], T["check_circle_b"], "glide"), (T["check_out"], T["check_out"] + 8),
               ip=T["check_circle_a"] - 1, op=T["check_out"] + 9)
    draw_layer(c, "check mark", cc[1], (T["check_a"], T["check_b"], "snapSettle"), (T["check_out"], T["check_out"] + 8),
               ip=T["check_a"] - 1, op=T["check_out"] + 9)
    cue(T["check_b"] - 1, "check", -2.0, "check drawn: Right execution")

    # --- house: roof, walls, door; the door lights up
    hp = icon_paths("home")
    m_a = T["morph_a"]
    draw_layer(c, "house roof", hp[0], (T["roof_a"], T["roof_b"], "glide"), None, ip=T["roof_a"] - 1, op=m_a + 1)
    draw_layer(c, "house walls", hp[1], (T["walls_a"], T["walls_b"], "glide"), None, ip=T["walls_a"] - 1, op=m_a + 1)
    door_o = anim([(T["door_a"], 100, "hold"), (m_a, 100, "accelExit"), (m_a + 6, 0, "hold")])
    # warm light inside the door, behind its outline
    x0, x1 = IC[0] + (9 - 12) * IS, IC[0] + (15 - 12) * IS
    y0, y1 = IC[1] + (13 - 12) * IS, IC[1] + (21 - 12) * IS
    lit = vis(c, "door light", [lk.group([lk.rect(x1 - x0, y1 - y0 + 14, (x0 + x1) / 2, (y0 + y1) / 2 + 7, 2 * IS),
                                          lk.fill(col("gold_light"))])],
              o=anim([(T["door_b"], 0, "glide"), (T["door_b"] + 12, 70, "hold"), (m_a - 3, 70, "accelExit"), (m_a + 2, 0, "hold")]),
              ip=T["door_b"], op=m_a + 3)
    nk.with_fx(c, lit, nk.gblur(4))
    draw_layer(c, "house door", hp[2], (T["door_a"], T["door_b"], "glide"), None, ip=T["door_a"] - 1, op=m_a + 7, o=door_o)
    dg = nk.glow(c, "door glow", (x0 + x1) / 2, (y0 + y1) / 2, 120, C["gold"], 0.5,
                 o=anim([(T["door_b"], 0, "glide"), (T["door_b"] + 14, 100, "hold"), (m_a - 3, 100, "accelExit"), (m_a + 3, 0, "hold")]),
                 ip=T["door_b"], op=m_a + 4)
    cue(T["door_b"], "key", -1.0, "door drawn and lit: Right home")


def build_words(c: Comp):
    nk.blur_word(c, "Right", COPY["right"], "NK Sans", 64, C["ink"], 960, 590, T["right_in"], dur=12, rise=20,
                 t_out=T["right_out"], out_dy=36, out_dur=8)
    band = (628, 836)
    for k, word in enumerate(COPY["keywords"]):
        a, z = T["kw_in"][k], T["kw_out"][k]
        last = k == len(COPY["keywords"]) - 1
        out_dy = 80 if last else -110
        keys_p = [(a, [960, 766 + 110], "softLand"), (a + 11, [960, 766], "hold"), (z, [960, 766], "accelExit"), (z + (8 if last else 7), [960, 766 + out_dy], "hold")]
        keys_b = [(a, 14, "glide"), (a + 8, 0, "hold"), (z, 0, "gentleIn"), (z + 7, 12, "hold")]
        ind = c.text(f"kw {word}", nk.tdoc(word, "NK Serif Italic", 176, C["gold"], justify=2), p=anim(keys_p),
                     o=anim([(a, 0, "cruise"), (a + 5, 100, "hold"), (z + 3, 100, "cruise"), (z + 8, 0, "hold")]),
                     ip=a - 1, op=z + 9, matted=True)
        nk.with_fx(c, ind, nk.gblur(anim(keys_b)))
        c.shape(f"kw slot matte {k}", [lk.group([lk.rect(1400, band[1] - band[0], 960, (band[0] + band[1]) / 2), lk.fill(hexc("#ffffff"))])],
                ip=a - 1, op=z + 9, matte_for_next=True)
        if 0 < k:
            cue(a + 3, "whoosh_short", -14.0, f"keyword swap to {word}")


# ----------------------------------------------------------------------------------------------- beat 4: the card
def house_outline():
    p = lambda x, y: (IC[0] + (x - 12) * IS, IC[1] + (y - 12) * IS)  # noqa: E731
    k = 0.5523 * 2 * IS
    pts = [(p(12, 3), (0, 0), (0, 0)), (p(21, 12), (0, 0), (0, 0)), (p(19, 12), (0, 0), (0, 0)),
           (p(19, 19), (0, 0), (0, k)), (p(17, 21), (k, 0), (0, 0)), (p(7, 21), (0, 0), (-k, 0)),
           (p(5, 19), (0, k), (0, 0)), (p(5, 12), (0, 0), (0, 0)), (p(3, 12), (0, 0), (0, 0))]
    return nk.shape_from_points(pts, True)


def card_outline(cx=CARD["cx"], cy=CARD["cy"], w=CARD["w"], h=CARD["h"], r=CARD["r"]):
    hw, hh, k = w / 2, h / 2, 0.5523 * r
    L, R, Tp, B = cx - hw, cx + hw, cy - hh, cy + hh
    pts = [((cx, Tp), (0, 0), (0, 0)), ((R - r, Tp), (0, 0), (k, 0)), ((R, Tp + r), (0, -k), (0, 0)),
           ((R, B - r), (0, 0), (0, k)), ((R - r, B), (k, 0), (0, 0)), ((L + r, B), (0, 0), (-k, 0)),
           ((L, B - r), (0, k), (0, 0)), ((L, Tp + r), (0, 0), (0, -k)), ((L + r, Tp), (-k, 0), (0, 0))]
    return nk.shape_from_points(pts, True)


def build_card(c: Comp):
    a, b = T["morph_a"], T["morph_b"]
    house, card = house_outline(), card_outline()
    morph = nk.sh_anim([(a, house, "snapSettle"), (b, card, "hold")])
    L, Tp = CARD["cx"] - CARD["w"] / 2, CARD["cy"] - CARD["h"] / 2
    R, B = L + CARD["w"], Tp + CARD["h"]

    # card body (follows the morph), drop shadow
    grad = lk.gradient([(0, C["card_top"]), (1, C["card_bot"])], [960, Tp], [960, B])
    body = vis(c, "card body", [lk.group([json.loads(json.dumps(morph)), grad])],
               o=anim([(a, 0, "hold"), (a + 7, 0, "glide"), (b, 100, "hold")]), ip=a)
    nk.with_fx(c, body, nk.drop_shadow("#000000", 0.6, 180, 28, 110))

    # warm doorway light inside the card's photo panel (matted to the card)
    gl = nk.glow(c, "panel light", 520, 900, 620, C["gold"], 0.42, sy=0.92,
                 o=anim([(b - 6, 0, "glide"), (b + 14, 100, "hold")]), ip=b - 6)
    nk.layer(c, gl)["tt"] = 1
    vis(c, "panel light matte", [lk.group([nk.sh(card), lk.fill(hexc("#ffffff"))])], ip=b - 6, matte_for_next=True)
    gl2 = nk.glow(c, "panel light high", 520, 300, 420, C["gold_light"], 0.10,
                  o=anim([(b - 2, 0, "glide"), (b + 16, 100, "hold")]), ip=b - 2)
    nk.layer(c, gl2)["tt"] = 1
    vis(c, "panel light matte 2", [lk.group([nk.sh(card), lk.fill(hexc("#ffffff"))])], ip=b - 2, matte_for_next=True)

    hg = nk.glow(c, "head light", 520, 360, 300, C["gold"], 0.20, o=anim([(b - 4, 0, "glide"), (b + 18, 100, "hold")]), ip=b - 4)
    nk.layer(c, hg)["tt"] = 1
    vis(c, "head light matte", [lk.group([nk.sh(card), lk.fill(hexc("#ffffff"))])], ip=b - 4, matte_for_next=True)

    # Nick rises into the light (matted to the card so he is cut by its bottom edge)
    img_w, img_h = 534, 1135
    sc = 80
    cx, cy = 520, 196 + img_h * sc / 100 / 2
    n_in = T["nick_in"]
    nick = c.image("nick", "nick-cutout.png", img_w, img_h,
                   p=anim([(n_in, [cx, cy + 120], "softLand"), (n_in + 22, [cx, cy], "hold")]),
                   s=anim([(n_in, [sc * 1.03, sc * 1.03], "softLand"), (n_in + 22, [sc, sc], "hold")]),
                   o=anim([(n_in, 0, "cruise"), (n_in + 6, 100, "hold")]), ip=n_in, matted=True)
    nk.with_fx(c, nick, nk.gblur(anim([(n_in, 14, "glide"), (n_in + 9, 0, "hold")])))
    vis(c, "nick matte", [lk.group([nk.sh(card), lk.fill(hexc("#ffffff"))])], ip=n_in, matte_for_next=True)

    # gold outline: the house outline that became the card's border
    sw = anim([(a, ICON_W, "snapSettle"), (b, 2.4, "hold")])
    st = lk.stroke(col("gold"), 2.4, anim([(a, 100, "hold"), (b - 4, 100, "softInOut"), (b + 12, 55, "hold")]))
    st["w"], st["lc"], st["lj"] = sw, 2, 2
    vis(c, "card outline", [lk.group([morph, st])], ip=a)
    cue(a + 4, "whoosh_morph", -2.0, "house opens into the card (peak)")
    cue(b, "thud_card", -5.0, "card settles")

    # ---- right column
    name_y = 318
    nm_t = T["name_in"]
    name_doc = nk.tdoc(COPY["name"], "NK Serif", 104, C["ink"], justify=0, tracking=80)
    name_w = nk.fonts.width("NK Serif", 104, COPY["name"], 80)
    name_p = anim([(nm_t, [COLX, name_y + 26], "softLand"), (nm_t + 13, [COLX, name_y], "hold")])
    gr = lk.gradient([(0, C["gold_light"]), (0.5, C["gold"]), (1, C["gold_deep"])], [0, name_y - 76], [0, name_y + 4])
    gname = vis(c, "name gold", [lk.group([lk.rect(name_w + 60, 130, COLX + name_w / 2, name_y - 36), gr])],
                o=anim([(nm_t, 0, "cruise"), (nm_t + 7, 100, "hold")]), ip=nm_t, matted=True)
    nm = c.text("name matte", name_doc, p=name_p, ip=nm_t)
    nk.layer(c, nm)["td"] = 1
    # light sweep across the name at the end (its own copy of the name as matte)
    sw_a, sw_b = T["sweep_a"], T["sweep_b"]
    band = lk.gradient([(0, "#ffffff"), (1, "#ffffff")], [-90, 0], [90, 0], alpha_stops=[(0, 0.0), (0.5, 0.85), (1, 0.0)])
    swp = vis(c, "name sweep", [lk.group([lk.rect(180, 220, 0, 0), band], r=18)],
              p=anim([(sw_a, [COLX - 140, name_y - 36], "softInOut"), (sw_b, [COLX + name_w + 140, name_y - 36], "hold")]),
              ip=sw_a, op=sw_b + 1, matted=True)
    nm2 = c.text("name sweep matte", name_doc, p=[COLX, name_y], ip=sw_a, op=sw_b + 1)
    nk.layer(c, nm2)["td"] = 1
    cue(sw_a + 2, "shimmer", -8.0, "light sweeps the name")
    s0a, s0b = T["sweep0_a"], T["sweep0_b"]
    swp0 = vis(c, "name sweep early", [lk.group([lk.rect(180, 220, 0, 0), json.loads(json.dumps(band))], r=18)],
               p=anim([(s0a, [COLX - 140, name_y - 36], "softInOut"), (s0b, [COLX + name_w + 140, name_y - 36], "hold")]),
               ip=s0a, op=s0b + 1, matted=True)
    nm0 = c.text("name sweep early matte", name_doc, p=[COLX, name_y], ip=s0a, op=s0b + 1)
    nk.layer(c, nm0)["td"] = 1
    cue(s0a + 2, "shimmer", -12.0, "light sweeps the name (settle)")

    nk.blur_word(c, "tagline", COPY["tagline"], "NK Serif Italic", 54, C["ink"], COLX, 390, T["tag_in"], justify=0, dur=12, rise=18, o=92)
    rule = vis(c, "rule", [lk.group([nk.sh(nk.shape_from_points([((COLX, 434), (0, 0), (0, 0)), ((1620, 434), (0, 0), (0, 0))], False)),
                                       stroke_c(C["gold"], 2), lk.trim(0, anim([(T["rule_in"], 0, "glide"), (T["rule_in"] + 16, 100, "hold")]))])],
               o=45, ip=T["rule_in"])
    nk.blur_word(c, "title", COPY["title"], "NK Sans", 44, C["ink"], COLX, 502, T["title_in"], justify=0, dur=12, rise=16)

    # PropNex badge: the official logo on a white plate (its wordmark is dark), top-right of the card
    plate_w, plate_h = 228, 64
    px, py = R - 36 - plate_w / 2, Tp + 36 + plate_h / 2
    bo = anim([(T["badge_in"], 0, "cruise"), (T["badge_in"] + 8, 100, "hold")])
    vis(c, "propnex plate", [lk.group([lk.rect(plate_w, plate_h, px, py, 12), lk.fill(hexc("#ffffff"))])], o=bo, ip=T["badge_in"])
    lg_h = 44
    c.image("propnex logo", "propnex-logo.png", 569, 150, p=(px, py), s=(lg_h / 150 * 100, lg_h / 150 * 100), o=bo, ip=T["badge_in"])

    # chips
    x = COLX
    cy_ = 568
    for k, label in enumerate(COPY["chips"]):
        tw = nk.fonts.width("NK Sans", 34, label)
        cw = tw + 40
        t0 = T["chips_in"] + 3 * k
        g = vis(c, f"chip {label}", [lk.group([lk.rect(cw, 56, 0, 0, 28), lk.fill(hexc("#ffffff"), 4), stroke_c(C["gold"], 2, 60)])],
                p=(x + cw / 2, cy_), s=anim([(t0, [90, 90], "softLand"), (t0 + 9, [100, 100], "hold")]),
                o=anim([(t0, 0, "cruise"), (t0 + 5, 100, "hold")]), ip=t0)
        c.text(f"chip text {label}", nk.tdoc(label, "NK Sans", 34, C["ink"], justify=2), p=(x + cw / 2, cy_ + 12),
               o=anim([(t0 + 1, 0, "cruise"), (t0 + 6, 100, "hold")]), ip=t0)
        x += cw + 14
    cue(T["chips_in"], "tick", -10.0, "first chip")
    cue(T["chips_in"] + 9, "tick", -12.0, "last chip")

    # legal line (CEA advertising requirements): name + reg no, agency + licence no
    lo = anim([(T["legal_in"], 0, "glide"), (T["legal_in"] + 10, 100, "hold")])
    c.text("legal 1", nk.tdoc(COPY["legal1"], "NK Sans", 24, C["muted"], justify=0), p=(COLX, 846), o=lo, ip=T["legal_in"])
    c.text("legal 2", nk.tdoc(COPY["legal2"], "NK Sans", 24, C["muted"], justify=0), p=(COLX, 880), o=lo, ip=T["legal_in"])


# ----------------------------------------------------------------------------------------------- beat 5: CTA
def build_cta(c: Comp):
    t = T["pill_in"]
    pill_h = 88
    tw = nk.fonts.width("NK Sans Semi", 44, COPY["cta"])
    icon_sz = 42
    pill_w = 40 + icon_sz + 18 + tw + 46
    pcx, pcy = COLX + pill_w / 2, 692
    press = T["press"]
    psc = anim([(t, [94, 94], "snapSettle"), (t + 12, [100, 100], "hold"), (press + 1, [100, 100], "cruise"),
                (press + 3, [96.5, 96.5], "hold"), (press + 4, [96.5, 96.5], "softLand"), (press + 10, [100, 100], "hold")])
    ppos = anim([(t, [pcx, pcy + 34], "snapSettle"), (t + 12, [pcx, pcy], "hold")])
    po = anim([(t, 0, "cruise"), (t + 5, 100, "hold")])
    pill = c.null("pill", p=ppos, s=psc, ip=t)
    g = vis(c, "pill body", [lk.group([lk.rect(pill_w, pill_h, 0, 0, pill_h / 2),
                                        lk.gradient([(0, C["gold_light"]), (0.55, C["gold"]), (1, C["gold_deep"])], [0, -pill_h / 2], [0, pill_h / 2])])],
            o=po, ip=t, parent=pill)
    nk.with_fx(c, g, nk.drop_shadow("#000000", 0.45, 180, 10, 30))
    # pressed brightening: the target answers one frame after the press
    vis(c, "pill flash", [lk.group([lk.rect(pill_w, pill_h, 0, 0, pill_h / 2), lk.fill(hexc("#ffffff"))])],
        o=anim([(press + 1, 0, "cruise"), (press + 3, 22, "hold"), (press + 4, 22, "softInOut"), (press + 14, 0, "hold")]),
        ip=press, op=press + 16, parent=pill)
    # chat icon (Tabler message-circle) and label, navy on gold
    ic_x = -pill_w / 2 + 40 + icon_sz / 2
    shapes = [s for d in nk.read_icon(BRAND / "icons" / "message-circle.svg") for s in nk.svg_subpaths(d, nk.icon_tx(ic_x, 0, icon_sz / 24))]
    vis(c, "pill icon", [lk.group([nk.sh(s) for s in shapes] + [stroke_c(C["navy_text"], 3.4)])], o=po, ip=t, parent=pill)
    c.text("pill label", nk.tdoc(COPY["cta"], "NK Sans Semi", 44, C["navy_text"], justify=0),
           p=(ic_x + icon_sz / 2 + 18, 15), o=po, ip=t, parent=pill)
    cue(t + 4, "tick", -6.0, "pill lands")

    # cursor: enters large, shrinks while travelling, parks, presses (squash 2-3 f), small rebound
    a, park = T["cursor_in"], T["cursor_park"]
    tip = (pcx + pill_w / 2 - 30, pcy + 16)
    cp = anim([(a, [1980, 1130], "glide"), (park, list(tip), "hold")])
    cs = anim([(a, [260, 260], "glide"), (park, [100, 100], "hold"), (press, [100, 100], "cruise"), (press + 2, [82, 82], "hold"),
               (press + 3, [82, 82], "softLand"), (press + 8, [100, 100], "hold")])
    cur = vis(c, "cursor", [lk.group([nk.sh(nk.cursor_shape()), lk.fill(hexc("#ffffff")), stroke_c("#0A1628", 2.2)])],
              p=cp, s=cs, ip=a)
    nk.with_fx(c, cur, nk.drop_shadow("#000000", 0.5, 160, 8, 18))
    cue(a + 4, "whoosh_short", -16.0, "cursor glides in (peak)")
    cue(press, "click", -3.0, "WhatsApp pressed")


# ----------------------------------------------------------------------------------------------- ground life
def motes(c: Comp):
    """Out-of-focus light motes drifting slowly left and up (the current), so held frames stay alive."""
    import random
    rnd = random.Random(7)
    for k in range(16):
        depth = rnd.random()
        r = 7 + 17 * depth
        x0, y0 = rnd.uniform(80, 1840), rnd.uniform(120, 980)
        dx, dy = -(20 + 70 * depth), -(8 + 30 * depth)
        warm = rnd.random() < 0.6
        colr = C["gold_light"] if warm else "#9FB7DA"
        peak = (6 + 9 * depth) if warm else (5 + 7 * depth)
        # the cold motes fade as the film warms; the warm ones arrive with "Sold"
        if warm:
            o = anim([(0, 0, "hold"), (T["sold_land"], 0, "glide"), (T["sold_land"] + 30, peak, "hold")])
        else:
            o = anim([(0, peak, "hold"), (T["sold_land"], peak, "softInOut"), (T["sold_land"] + 30, 0, "hold")])
        ind = c.shape(f"mote {k}", [lk.group([lk.ellipse(r * 2, r * 2), lk.fill(hexc(colr))])],
                      p=anim([(0, [x0, y0], "cruise"), (FRAMES, [x0 + dx * 2.2, y0 + dy * 2.2], "hold")]), o=o)
        nk.with_fx(c, ind, nk.gblur(7 + 12 * depth))
        c.no_camera.add(ind)


# ----------------------------------------------------------------------------------------------- film
def build():
    c = Comp("Nick R.L. intro 16x9", W, H, FRAMES)
    nk.ground(c)
    # one light logic: cold at first, warm once it sells
    nk.glow(c, "cold glow", RC[0], RC[1] - 10, 680, C["cold_glow"], 0.42,
            o=anim([(0, 100, "hold"), (T["sold_land"], 100, "softInOut"), (T["sold_land"] + 26, 0, "hold")]), op=T["sold_land"] + 27)
    nk.glow(c, "warm glow", RC[0], RC[1], 760, C["gold"], 0.17,
            p=anim([(T["fly_a"], [RC[0], RC[1]], "snapSettle"), (T["fly_b"], [IC[0], IC[1] + 60], "hold"),
                    (T["morph_a"], [IC[0], IC[1] + 60], "snapSettle"), (T["morph_b"], [560, 700], "hold")]),
            o=anim([(T["sold_land"] - 2, 0, "glide"), (T["sold_land"] + 26, 100, "hold"), (T["morph_a"], 100, "softInOut"), (T["morph_b"] + 10, 45, "hold")]),
            ip=T["sold_land"] - 2)
    # camera: one slow push for the whole film, a scale cut into the CTA
    cut = T["cut"]
    kw = T["kw_in"]
    cam = [(0, 100, "glide"), (T["pause_end"], 103.5, "cruise"), (T["sold_land"] - 1, 103.8, "softLand"),
           (T["sold_land"] + 26, 107.0, "cruise"), (T["b2_out"], 107.6, "softInOut"), (T["fly_b"] + 4, 101.0, "hold"),
           (kw[0], 101.0, "softLand"), (kw[0] + 14, 102.0, "hold"), (kw[1], 102.0, "softLand"), (kw[1] + 14, 103.0, "hold"),
           (kw[2], 103.0, "softLand"), (kw[2] + 14, 104.0, "hold"), (kw[3], 104.0, "softLand"), (kw[3] + 14, 105.2, "hold"),
           (T["morph_a"], 105.2, "snapSettle"), (T["morph_b"], 100.0, "cruise"), (cut - 1, 103.6, "hold"),
           (cut, 121.0, "cruise"), (FRAMES, 122.6, "hold")]
    c.camera(p=(960, 540), a=(960, 540), s=anim([(f, [v, v], e) for f, v, e in cam]))
    cue(cut, "tick", -4.0, "scale cut into the CTA")

    motes(c)
    build_ring(c)
    build_notches(c)
    build_counter(c)
    # the light turns warm when it sells: one soft bloom from the ring
    bl = T["sold_land"]
    nk.glow(c, "sold bloom", RC[0], RC[1], 880, C["gold"], 0.19,
            o=anim([(bl - 1, 0, "snapSettle"), (bl + 4, 100, "softInOut"), (bl + 28, 0, "hold")]), ip=bl - 1, op=bl + 29)
    build_sold(c)
    build_icons(c)
    build_words(c)
    build_card(c)
    build_cta(c)
    nk.vignette(c, o=anim([(0, 100, "hold"), (T["morph_a"], 100, "softInOut"), (T["morph_b"] + 14, 45, "hold")]))
    return c


SCREEN_GLOWS = {"warm glow", "sold bloom", "door glow", "panel light", "panel light high", "head light"}


def main():
    c = build()
    for lyr in c._layers:
        if lyr.get("nm") in SCREEN_GLOWS:
            lyr["bm"] = 2  # screen: light adds, never greys the navy
    SCENE.mkdir(parents=True, exist_ok=True)
    doc = c.build(nk.fonts)
    (SCENE / "lottie.json").write_text(json.dumps(doc, separators=(",", ":")))
    for f in ["nk-sans-light.ttf", "nk-sans.ttf", "nk-sans-semi.ttf", "nk-serif.ttf", "nk-serif-italic.ttf"]:
        shutil.copy(BRAND / "fonts" / f, SCENE / f)
    shutil.copy(BRAND / "photos" / "nick-cutout.png", SCENE / "nick-cutout.png")
    shutil.copy(BRAND / "logo" / "propnex-logo.png", SCENE / "propnex-logo.png")
    (ROOT / "audio").mkdir(exist_ok=True)
    cues.sort(key=lambda q: q["frame"])
    (ROOT / "audio" / "cues.json").write_text(json.dumps({"fps": 30, "frames": FRAMES, "cues": cues}, indent=1))
    events = [{"type": "cut", "t": T["cut"] / 30, "frame": T["cut"], "note": "scale cut 1.03x -> 1.21x into the CTA"}]
    (ROOT / "audio" / "events.json").write_text(json.dumps(events, indent=1))
    print(f"wrote {SCENE / 'lottie.json'} ({len(doc['layers'])} layers), {len(cues)} cues")


if __name__ == "__main__":
    main()
