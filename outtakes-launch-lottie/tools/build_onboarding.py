"""Outtakes photographer onboarding film, an Ozen Flow production (made with the ozen-motion-design skill).

    python3 tools/build_onboarding.py                       # portrait  -> public/projects/outtakes-onboarding/
    OT_FORMAT=landscape python3 tools/build_onboarding.py   # landscape -> public/projects/outtakes-onboarding-16x9/

Three acts, each one composition (rendered in parallel chunks by tools/export_onboarding.sh):
  A  dark   TOO MANY SHOTS. / DMS.  scattered shots and DMs converge into the green "Join as Photographer" pill;
            the press floods the frame and the flood becomes the Studio's light ground
  B  light  the Studio's real 10-step tour, carried by one card: each step's card arrives from the right (the film's
            current), and a press on Next grows it into the feature it describes (profile, portfolio, packages,
            availability, payouts); the checklist ticks to 8 of 8; Preview profile (press and cut)
  C  light -> dark  the profile page; a booking request lands; Accept blooms green into the dark; BOOKED.;
            GET IN THE FRAME.; OUTTAKES, outtakes.sg

Copy on the tour cards is the Studio's own (site recordings, 23 Nov 2026). Illustrative: "Your name", the bio, the
package and the booking request.
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
import build_film as bf  # noqa: E402  (shared fonts, photos, profile page, wordmark crash)
import film_parts as fp  # noqa: E402
from lottie_kit import CAP, Comp, anim, ease_value, ellipse, gradient, group, path, rect, static, text_doc  # noqa: E402
from parts4 import (Plane, brackets, button, col, drop_shadow, fl, fl_anim, gblur, ground, group3d,  # noqa: E402
                    soft_vignette, st, statement, with_fx)

W, H, LANDSCAPE = fp.W, fp.H, fp.LANDSCAPE
ROOT, PHOTOS, FONTS_DIR = bf.ROOT, bf.PHOTOS, bf.FONTS_DIR
OUT = ROOT / "public" / "projects" / ("outtakes-onboarding-16x9" if LANDSCAPE else "outtakes-onboarding")
fonts, SIZES = bf.fonts, bf.SIZES
STATE, TITLE, BODY, MED = "OT Wordmark", "OT Display", "OT Body", "OT Body Medium"
NIGHT = "#0f0f11"
DASH_OFF = "#dde1e4"
SHADOW = dict(opacity=55, distance=30, softness=120, color="#1d2a33")

if LANDSCAPE:
    UI_X, UI_Y, UI_S = 960, 662, 0.88
    ST_Y, ST_W, ST_MAX = 150, 1560, 110
else:
    UI_X, UI_Y, UI_S = 540, 1060, 1.0
    ST_Y, ST_W, ST_MAX = 420, 860, 150
CW, CH = 880, 480           # the tour card
CUR = None                  # cursor path helper (set per comp)


# =========================================================================== small helpers
def photo(name, w, h):
    """Centre-cropped copy of a brand photo at w x h (kept small so scenes stay light)."""
    out = PHOTOS / f"ob-{name}-{w}x{h}.jpg"
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


def gblur_dir(amount, dims=1):
    """Gaussian blur with a direction (1 both, 2 horizontal, 3 vertical); amount is a number or anim()."""
    e = gblur(amount)
    e["ef"][1]["v"] = {"a": 0, "k": dims}
    return e


def layers_since(c, n0):
    return c._layers[n0:]


def set_opacity(layers, keys):
    for lyr in layers:
        if lyr["ty"] in (2, 4, 5):
            lyr["ks"]["o"] = anim(keys)


def add_fx(layers, *fx):
    for lyr in layers:
        if lyr["ty"] in (2, 4, 5):
            lyr["ef"] = list(lyr.get("ef", [])) + [json.loads(json.dumps(e)) for e in fx]


def screen(lx, ly, w, h, cx=None, cy=None):
    """Screen position of a point (lx, ly) on a w x h card resting flat at the UI centre."""
    cx = UI_X if cx is None else cx
    cy = UI_Y if cy is None else cy
    return cx + (lx - w / 2) * UI_S, cy + (ly - h / 2) * UI_S


def rect_anim(size_keys, r=30):
    s = anim([(k[0], list(k[1])) + tuple(k[2:]) for k in size_keys]) if len(size_keys) > 1 else static(list(size_keys[0][1]))
    return {"ty": "rc", "d": 1, "s": s, "p": static([0, 0]), "r": static(r) if not isinstance(r, dict) else r}


def say(c, lines, start, exit_at=None, colors=None, dark=False):
    """The beat's statement in the site's condensed italic, in the top band (one line in landscape, where the
    last word keeps its accent colour as a second run on the same baseline)."""
    if LANDSCAPE and len(lines) > 1:
        runs = [" ".join(lines[:-1]) + " ", lines[-1]]
        size = fonts.fit(STATE, ["".join(runs)], ST_W, ST_MAX)
        x = W / 2 - fonts.width(STATE, size, "".join(runs)) / 2
        base = ST_Y + CAP * size / 2
        cols_ = ["white", "green"] if dark else ["ink", "gtext"]
        for i, run in enumerate(runs):
            fp.rise_line(c, fonts, run, STATE, size, col(cols_[i]), x, base, j=0, start=start + i * 6,
                         exit_at=None if exit_at is None else exit_at + i * 2)
            x += fonts.width(STATE, size, run)
        c.cue(start, "tick", 0.5)
        return size
    if LANDSCAPE:
        lines = [" ".join(lines)]
    if colors is None:
        colors = (["white"] * (len(lines) - 1) + ["green"]) if dark else (["ink"] * (len(lines) - 1) + ["gtext"])
        if LANDSCAPE and len(colors) == 1:
            colors = ["green" if dark else "ink"]
    return statement(c, fonts, lines, start, colors=colors, center_y=ST_Y, max_w=ST_W, max_size=ST_MAX,
                     stagger=6, exit_at=exit_at)


def cursor_track(c, keys, presses=(), op=None, enter=None):
    """The film's pointer (black arrow, white edge). keys = [(frame, (x, y), ease), ...] in screen space.
    It enters oversize only when `enter` is a frame; otherwise it is already on screen (continuing a path)."""
    pk = [(k[0], [k[1][0], k[1][1], 0], k[2] if len(k) > 2 else "entrance-sharp") for k in keys]
    size = 1.25 if not LANDSCAPE else 1.05
    s = [[size * 100, size * 100, 100]]
    sk = []
    if enter is not None:
        sk += [(enter, [size * 190, size * 190, 100], "entrance-sharp"), (enter + 9, s[0], "hold")]
    else:
        sk += [(keys[0][0], s[0], "hold")]
    for pf in presses:
        sk += [(pf - 2, s[0], "settle-soft"), (pf, [size * 80, size * 80, 100], "settle-soft"), (pf + 4, s[0], "hold")]
        c.cue(pf, "tap", 0.9)
    sk.sort(key=lambda k: k[0])
    shp = [group([path([list(p) for p in [(0, 0), (0, 46), (11.5, 35), (20, 54), (28.5, 50.5), (20, 32), (35, 32)]],
                       closed=True), fl("ink"), st("white", 3.2)])]
    o = anim([(enter, 0, "settle-soft"), (enter + 4, 100)]) if enter is not None else 100
    ind = c.shape("cursor", shp, p=anim(pk), s=anim(sk) if len(sk) > 1 else s[0], o=o,
                  ip=enter if enter is not None else 0, op=op)
    c.no_camera.add(ind)
    return ind


# =========================================================================== the tour card
TOUR = {
    1: ("Welcome to your Studio", ["A quick tour of everything you need", "to start getting booked."], "Start"),
    2: ("Bookings", ["Requests from clients land here.", "Accept or decline, message them."], "Next"),
    3: ("Your profile", ["Add a photo, banner, bio and highlights.", "This is the page clients see."], "Next"),
    4: ("Portfolio", ["Upload at least 6 photos and tag each", "with its sport. Star up to 6 as featured."], "Next"),
    5: ("Packages", ["Set what you offer and what it costs.", "Clients book a package and pay on the site."], "Next"),
    6: ("Availability", ["Mark the days you're free so clients", "can find you for their date."], "Next"),
    7: ("Payouts", ["Connect Stripe to get paid automatically", "once a client confirms their photos arrived."], "Next"),
    8: ("Stories", ["Write about a shoot. Outtakes features", "the best ones on the Community page."], "Next"),
    9: ("Hire a photographer", ["Need a second shooter, or someone to", "shoot you? Book any photographer."], "Next"),
    10: ("Help is here", ["Ask the help chat or open a request.", "Take this tour again any time."], "Finish"),
}
NEXT_BTN = (652, 356, 180, 88)      # x, y, w, h on the card


def next_xy(w=CW, h=CH, cx=None, cy=None):
    x, y, bw, bh = NEXT_BTN
    return screen(x + bw * 0.55, y + bh * 0.6, w, h, cx, cy)


def tour_content(ch, step, press=None):
    """Draw tour step `step` on a content group whose origin is the card's top-left."""
    title, lines, label = TOUR[step]
    ch.text(f"{step} of 10", BODY, 28, "grey", 48, 74)
    ch.text(title, MED, 50, "ink", 48, 146)
    bsize = 34
    while max(fonts.width(BODY, bsize, ln) for ln in lines) > CW - 96 and bsize > 26:
        bsize -= 1
    for i, ln in enumerate(lines):
        ch.text(ln, BODY, bsize, "grey", 48, 208 + i * 46)
    gap = 12
    seg = (CW - 96 - gap * 9) / 10
    for k in range(10):
        ch.box(48 + k * (seg + gap), 292, seg, 8, "orange" if k < step else DASH_OFF, r=4)
    ch.text("Skip tour", BODY, 32, "grey", 48, 412)
    x, y, w, h = NEXT_BTN
    if step > 1:
        ch.box(x - 166, y, 150, h, "#e9ecef", r=h * 0.22)
        ch.text("Back", BODY, 32, "ink", x - 166 + 75, y + h / 2 + CAP * 32 / 2, j=2)
    button(ch, fonts, label, x, y, w, h, style="orange", size=34, arrow=False, press=press)


class Card:
    """A 3D card centred at its plane's origin. The box can grow into a feature view (container morph) and the
    whole card can whip in from the right or out to the left (the film's current)."""

    def __init__(self, c, name, enter, leave=None, rise=False, op=None, morph=None, x=None, y=None):
        self.c, self.n0, self.rise = c, len(c._layers), rise
        cx, cy = (UI_X if x is None else x), (UI_Y if y is None else y)
        self.cx, self.cy = cx, cy
        if rise:
            keys = [(enter, [cx, cy + (H * 0.42), 240], "settle-soft"), (enter + 22, [cx, cy, 0], "linear")]
            rx = anim([(enter, 16, "settle-soft"), (enter + 22, 0)])
            ry = 0
        else:
            keys = [(enter, [cx + W * 0.78, cy, 0], "crash"), (enter + 11, [cx, cy, 0], "linear")]
            rx = 0
            ry = anim([(enter, -14, "settle-soft"), (enter + 16, 0)])
        end = leave if leave is not None else (op if op is not None else c.frames)
        keys.append((end, [cx, cy - 18, 0]))
        if leave is not None:
            keys[-1] = (leave, [cx, cy - 18, 0], "exit-accelerate")
            keys.append((leave + 10, [cx - W * 0.98, cy - 18, 0]))
        self.enter, self.leave = enter, leave
        self.pl = Plane(c, name, 0, 0, anim(keys), rx=rx, ry=ry, s=(UI_S * 100, UI_S * 100, 100), ip=enter,
                        op=(leave + 11) if leave is not None else op)
        size_keys = [(enter, (CW, CH), "hold")]
        prev = (CW, CH)
        for a_, b_, size in (morph or []):      # grow from frame a_ to b_ into `size`
            size_keys.append((a_, prev, "entrance-sharp"))
            size_keys.append((b_, size, "hold"))
            prev = size
        ind = self.pl.shape(f"{name} box", [group([rect_anim(size_keys, r=30), fl("card")])])
        with_fx(c, ind, drop_shadow(**SHADOW))

    def content(self, name, w, h, ip, op, fade_in=None, fade_out=None):
        """A content group laid out on a w x h card (origin = its top-left). Fades are 4-frame helpers."""
        g = group3d(self.pl, name, Comp.ks3(p=(-w / 2, -h / 2, 0)), ip=ip, op=op)
        g.fade_in, g.fade_out, g.n0 = fade_in, fade_out, len(self.c._layers)
        return g

    def close(self, g):
        keys = []
        if g.fade_in is not None:
            keys += [(g.fade_in, 0, "settle-soft"), (g.fade_in + 4, 100, "hold")]
        if g.fade_out is not None:
            keys += [(g.fade_out, 100, "settle-soft"), (g.fade_out + 4, 0)]
        if keys:
            set_opacity(layers_since(self.c, g.n0), keys)

    def finish(self):
        """Horizontal smear on everything in the card while it whips."""
        keys = [(self.enter, [0 if self.rise else 46], "settle-soft"), (self.enter + 7, [0], "hold")]
        if self.leave is not None:
            keys += [(self.leave + 2, [0], "exit-accelerate"), (self.leave + 10, [56])]
        add_fx(layers_since(self.c, self.n0), gblur_dir(anim(keys), 2))


def tour_card(c, step, enter, leave, press, rise=False, morph=None, until=None):
    """A whole tour step card. `until` ends the tour content (when the card grows into a feature)."""
    card = Card(c, f"card {step}", enter, leave, rise=rise, morph=morph)
    g = card.content(f"tour {step}", CW, CH, enter, (until + 5) if until else None,
                     fade_out=until if until else None)
    tour_content(g, step, press=press)
    card.close(g)
    return card


# =========================================================================== act A: the hook
HOOK_PHOTOS = [  # name, orientation, rest (x, y) portrait, width, rotation, depth (0 near .. 2 far)
    ("tackle-night", "l", (190, 330), 330, -8, 0), ("basketball", "p", (560, 270), 250, 4, 1),
    ("celebrate-run", "l", (900, 400), 320, 10, 0), ("heart-hands", "p", (110, 700), 230, 7, 2),
    ("sepak-takraw", "l", (430, 600), 280, -5, 2), ("number-10", "p", (860, 690), 260, -9, 1),
    ("point-orange", "l", (1010, 990), 260, 12, 1), ("kids-duel", "l", (60, 1040), 280, -12, 1),
    ("motion-blur", "l", (270, 1330), 330, 7, 0), ("team-backs", "p", (640, 1290), 230, -6, 2),
    ("smile-orange", "l", (930, 1370), 320, 9, 0), ("portrait-flare", "p", (430, 1590), 250, -4, 1),
    ("stretch-ball", "l", (820, 1640), 300, 6, 1), ("celebrate-fists", "l", (140, 1720), 300, -10, 0),
]
DMS = [("them", "how much for saturday's match?", 70, (90, 470)), ("me", "$70 for the full game", 80, (990, 600)),
       ("them", "can do $30?", 92, (90, 1290)), ("them", "game cancelled, no need to pay ya", 104, (90, 1430))]
A_FR = 186


def hook_layout():
    """Rest positions for the format (portrait as designed; landscape spreads them across the width)."""
    out = []
    for name, ori, (x, y), w, r, d in HOOK_PHOTOS:
        if LANDSCAPE:
            x, y = 80 + x / 1080 * 1760, 60 + (y - 260) / 1500 * 960
            w *= 0.82
        out.append((name, ori, x, y, w, r, d))
    return out


def act_a():
    c = Comp("A Hook - too many shots, too many DMs", W, H, A_FR)
    ground(c, NIGHT)
    gh = H * 0.55
    c.shape("glow", [group([rect(W, gh, W / 2, H - gh / 2),
                            gradient([(0, "#0f0f11"), (0.62, "#163f12"), (1, "#3fd31f")], [W / 2, H - gh], [W / 2, H],
                                     alpha_stops=[(0, 0), (0.6, 0.6), (1, 0.9)])])],
            o=anim([(0, 55, "linear"), (120, 85, "exit-accelerate"), (150, 30)]))
    cx, cy = W / 2, H / 2
    conv0 = 126  # convergence begins
    starts = [0, 2, 3, 5, 6, 8, 10, 11, 13, 15, 17, 19, 21, 23]
    for i, (name, ori, x, y, w, r, d) in enumerate(hook_layout()):
        iw, ih = (420, 280) if ori == "l" else (280, 420)
        f = photo(name, iw, ih)
        k = w / iw * 100 * (1 - 0.12 * d)
        t0 = starts[i]
        ang = math.atan2(y - cy, x - cx)
        sx, sy = x + math.cos(ang) * 700, y + math.sin(ang) * 700
        dist = math.hypot(x - cx, y - cy)
        tc = conv0 + int(max(0, 8 - dist / 140))          # outer shots leave first
        drift = ((x - cx) * 0.03, (y - cy) * 0.03)
        p = anim([(t0, [sx, sy, 0], "crash"), (t0 + 12, [x, y, 0], "linear"),
                  (tc, [x + drift[0], y + drift[1], 0], "exit-accelerate"), (tc + 16, [cx, cy, 0])])
        s = anim([(t0, [k * 1.25, k * 1.25, 100], "crash"), (t0 + 12, [k, k, 100], "linear"),
                  (tc, [k * 1.03, k * 1.03, 100], "exit-accelerate"), (tc + 16, [k * 0.06, k * 0.06, 100])])
        rr = anim([(t0, r + 24, "crash"), (t0 + 12, r, "linear"), (tc, r + 1.5, "exit-accelerate"), (tc + 16, r + 40)])
        ind = c.image(f"shot {name}", f, iw, ih, p=p, s=s, r=rr, ip=t0, op=tc + 16,
                      o=100 if d < 2 else 70)
        base = [0, 4, 9][d]
        with_fx(c, ind, gblur(anim([(t0, [26], "settle-soft"), (t0 + 6, [base], "hold"),
                                    (tc, [base], "exit-accelerate"), (tc + 16, [18])])))
        c.cue(t0 + 3, "shutter", 0.22 + 0.03 * (i % 4))
    # DMs over the pile
    size = 38 if not LANDSCAPE else 34
    for who, text, at, (x, y) in DMS:
        if LANDSCAPE:
            x = 140 if who == "them" else W - 140
            y = 60 + (y - 260) / 1500 * 960
        tw = fonts.width(BODY, size, text)
        bw, bh = tw + 64, size * 1.25 + 46
        bx = x if who == "them" else x - bw
        bcx, bcy = bx + bw / 2, y
        tc = conv0 + 2
        g = c.null(f"dm {text[:12]}", p=anim([(at, [bcx, bcy + 26, 0], "entrance-sharp"), (at + 9, [bcx, bcy, 0], "linear"),
                                             (tc, [bcx, bcy - 6, 0], "exit-accelerate"), (tc + 14, [cx, cy, 0])]),
                   a=(bcx, bcy), s=anim([(at, [86, 86, 100], "expressive-pop"), (at + 8, [100, 100, 100], "linear"),
                                         (tc, [100, 100, 100], "exit-accelerate"), (tc + 14, [6, 6, 100])]),
                   ip=at, op=tc + 14)
        n0 = len(c._layers)
        c.shape("dm bubble", [group([rect(bw, bh, bcx, bcy, bh / 2), fl("green" if who == "me" else "strip")])],
                parent=g, ip=at, op=tc + 14)
        c.text("dm text", text_doc(text, BODY, size, col("ink" if who == "me" else "white"), justify=0),
               p=(bx + 32, bcy + CAP * size / 2), parent=g, ip=at, op=tc + 14)
        set_opacity(layers_since(c, n0), [(at, 0, "settle-soft"), (at + 4, 100)])
        c.cue(at, "blip_out" if who == "me" else "blip_in", 0.8)
    # the statement: TOO MANY / [SHOTS. -> DMS.] (the keyword swaps inside a fixed slot)
    blur_out = 120
    if LANDSCAPE:
        size = fonts.fit(STATE, ["TOO MANY SHOTS."], 1300, 190)
        left = cx - (fonts.width(STATE, size, "TOO MANY ") + fonts.width(STATE, size, "SHOTS.")) / 2
        l1x, l1y, j1 = left, cy + CAP * size / 2, 0
        slot_x, l2y, j2 = left + fonts.width(STATE, size, "TOO MANY "), l1y, 0
    else:
        size = fonts.fit(STATE, ["TOO MANY", "SHOTS."], 860, 200)
        l1x, l1y, j1 = cx, cy - size * 0.48 + CAP * size / 2, 2
        slot_x, l2y, j2 = cx, cy + size * 0.48 + CAP * size / 2, 2

    def word(text, colour, x, y, j, t_in, t_out=None, up=False, matted=False):
        keys = [(t_in, [x, y + 46, 0], "entrance-sharp"), (t_in + 12, [x, y, 0], "linear")]
        sk = (100, 100)
        end = A_FR
        if up:                    # leaves upward out of the slot
            keys += [(t_out, [x, y, 0], "exit-accelerate"), (t_out + 8, [x, y - size * 1.1, 0])]
            end = t_out + 9
        elif t_out is not None:   # converges into the centre with everything else
            keys += [(t_out, [x, y, 0], "exit-accelerate"), (t_out + 10, [cx, cy, 0])]
            sk = anim([(t_in, [100, 100, 100], "hold"), (t_out, [100, 100, 100], "exit-accelerate"),
                       (t_out + 10, [30, 30, 100])])
            end = t_out + 11
        ind = c.text(f"word {text}", text_doc(text, STATE, size, col(colour), justify=j), p=anim(keys),
                     ip=t_in, op=end, s=sk, matted=matted)
        bk = [(t_in, [18], "settle-soft"), (t_in + 7, [0], "hold")]
        if t_out is not None and not up:
            bk += [(t_out, [0], "exit-accelerate"), (t_out + 8, [22])]
        with_fx(c, ind, gblur(anim(bk)))
        if not matted:
            c._layers[-1]["ks"]["o"] = anim([(t_in, 0, "settle-soft"), (t_in + 5, 100)])
        return ind

    def slot_matte(t_in, t_out):
        """Added right after its word, so it sits directly above it (Lottie track matte)."""
        top, bot = l2y - size * 1.02, l2y + size * 0.3
        c.shape("slot matte", [group([rect(W, bot - top, cx, (top + bot) / 2), fl("white")])], ip=t_in,
                op=t_out, matte_for_next=True)

    word("TOO MANY", "white", l1x, l1y, j1, 6, blur_out)
    word("SHOTS.", "green", slot_x, l2y, j2, 14, 66, up=True, matted=True)
    slot_matte(14, 75)
    word("DMS.", "green", slot_x, l2y, j2, 66, blur_out, matted=True)
    slot_matte(66, blur_out + 11)
    c.cue(6, "tick", 0.45)
    c.cue(66, "tick", 0.5)
    c.cue(60, "riser:66", 0.5)
    c.cue(conv0, "whoosh", 0.75)
    # the convergence point becomes the green pill
    t_dot, t_pill, press, t_flood = 142, 150, 168, 171
    pw, ph = (640, 124) if not LANDSCAPE else (560, 108)
    dot = c.shape("join pill", [group([rect_anim([(t_dot, (40, 40), "crash"), (t_pill, (40, 40), "crash"),
                                                  (t_pill + 12, (pw, ph), "hold"), (t_flood, (pw, ph), "exit-accelerate"),
                                                  (t_flood + 12, (W * 1.4, H * 1.4))],
                                                 r=anim([(t_dot, [ph / 2], "hold"), (t_flood, [ph / 2], "exit-accelerate"),
                                                         (t_flood + 12, [0])])),
                                       fl_anim([(t_dot, "green", "hold"), (t_flood + 6, "green", "settle-soft"),
                                                (A_FR - 1, "light")])])],
                  p=(cx, cy), s=anim([(t_dot, [170, 170, 100], "crash"), (t_dot + 6, [100, 100, 100], "hold"),
                                      (press, [100, 100, 100], "settle-soft"), (press + 2, [94, 94, 100], "settle-soft"),
                                      (press + 5, [100, 100, 100])]),
                  ip=t_dot)
    lsize = 40 if not LANDSCAPE else 36
    lab = "Join as Photographer"
    lw = fonts.width(MED, lsize, lab)
    n0 = len(c._layers)
    c.text("join label", text_doc(lab, MED, lsize, col("ink"), justify=0), p=(cx - (lw + 54) / 2, cy + CAP * lsize / 2),
           ip=t_pill + 6, op=t_flood + 4)
    c.shape("join arrow", [group([path([[0, 0], [26, 0]]), st("ink", 4)]),
                           group([path([[14, -11], [26, 0], [14, 11]]), st("ink", 4)])],
            p=(cx + (lw + 54) / 2 - 26, cy), ip=t_pill + 6, op=t_flood + 4)
    set_opacity(layers_since(c, n0), [(t_pill + 6, 0, "settle-soft"), (t_pill + 11, 100, "hold"),
                                      (t_flood, 100, "settle-soft"), (t_flood + 3, 0)])
    c.cue(t_dot, "pop", 0.7)
    c.cue(t_flood, "whoosh", 0.8)
    c.cue(t_flood + 4, "boom_small", 0.45)
    # pointer enters, parks on the pill, presses
    px, py = cx + pw * 0.24, cy + ph * 0.22
    cursor_track(c, [(t_pill - 2, (px + 240, py + 420)), (press - 8, (px, py)), (press + 4, (px, py), "settle-soft"),
                     (A_FR, (px + 10, py + 14))], presses=[press], enter=t_pill - 2)
    return c


# =========================================================================== act B: the Studio tour
B_FR = 836
T = {   # step: (enter, press Next, morph/feature start, leave)
    1: (0, 56, None, 58), 2: (62, 96, None, 98), 3: (102, 130, 132, 205), 4: (209, 237, 239, 345),
    5: (349, 377, 379, 462), 6: (466, 494, 496, 585), 7: (589, 617, 619, 692),
}
FEAT = {3: (880, 760), 4: (880, 900), 5: (880, 640), 6: (880, 840), 7: (880, 540)}
CHECK = (880, 920)


def feature_group(card, step, w, h, t):
    return card.content(f"feature {step}", w, h, t + 6, None, fade_in=t + 6)


def pop_group(card, g, name, t, lx, ly, dy=26, scale=None):
    """A sub-group inside a feature that rises (and optionally scales) into place at frame t."""
    s = anim([(t, [scale, scale, 100], "crash"), (t + 10, [100, 100, 100])]) if scale else (100, 100, 100)
    sub = group3d(g, name, Comp.ks3(p=anim([(t, [lx, ly + dy, 0], "entrance-sharp"), (t + 10, [lx, ly, 0])]),
                                     a=(lx, ly, 0), s=s), ip=t)
    sub.n0 = len(card.c._layers)
    return sub


def pop_close(card, sub, t):
    set_opacity(layers_since(card.c, sub.n0), [(t, 0, "settle-soft"), (t + 5, 100)])


def feat_profile(card, t):
    w, h = FEAT[3]
    g = feature_group(card, 3, w, h, t)
    b = pop_group(card, g, "banner", t + 8, 0, 0, dy=0)
    b.image(photo("celebrate-run", 880, 300), 880, 300, 0, 0, w, 300)
    pop_close(card, b, t + 8)
    a = pop_group(card, g, "avatar", t + 14, 118, 300, dy=0, scale=55)
    a.circle(118, 300, 176, "card")
    a.image("v4-avatar.png", 320, 320, 118 - 80, 300 - 80, 160, 160)
    pop_close(card, a, t + 14)
    n = pop_group(card, g, "name", t + 20, 0, 0)
    n.text("YOUR NAME", TITLE, 60, "ink", 48, 470)
    n.heart(818, 446, 46, "ink")
    pop_close(card, n, t + 20)
    bio = pop_group(card, g, "bio", t + 25, 0, 0)
    bio.text("Match days, finals and the", BODY, 36, "grey", 48, 548)
    bio.text("moments between.", BODY, 36, "grey", 48, 594)
    pop_close(card, bio, t + 25)
    tg = pop_group(card, g, "tags", t + 30, 0, 0)
    tx = 48
    for tag in ("Football", "Events", "Futsal"):
        tw = fonts.width(BODY, 30, tag) + 44
        tg.box(tx, 650, tw, 58, "panel", r=29)
        tg.text(tag, BODY, 30, "ink", tx + tw / 2, 650 + 29 + CAP * 30 / 2, j=2)
        tx += tw + 14
    pop_close(card, tg, t + 30)
    for f in (8, 14, 20, 25, 30):
        card.c.cue(t + f, "pop", 0.35)
    card.close(g)


PORTFOLIO = [("tackle-night", "Football"), ("basketball", "Basketball"), ("sepak-takraw", "Sepak takraw"),
             ("point-orange", "Futsal"), ("kids-duel", "Football"), ("celebrate-fists", "Football")]


def feat_portfolio(card, t):
    w, h = FEAT[4]
    g = feature_group(card, 4, w, h, t)
    hd = pop_group(card, g, "head", t + 6, 0, 0)
    hd.text("Portfolio", MED, 46, "ink", 48, 96)
    hd.keyed_text([(0, "0 photos", BODY, 32, "grey", 1)] +
                  [(t + 16 + 4 * k, f"{k + 1} photo{'s' if k else ''}", BODY, 32, "grey", 1) for k in range(6)], w - 48, 96)
    pop_close(card, hd, t + 6)
    cw_, chh, gap = 250, 316, 17
    x0, y0 = 48, 140
    for k, (name, tag) in enumerate(PORTFOLIO):
        r, ccol = divmod(k, 3)
        lx, ly = x0 + ccol * (cw_ + gap), y0 + r * (chh + gap)
        tk = t + 14 + 4 * k
        # each photo flies in from the left (where the pile was) and lands in its cell
        sub = group3d(g, f"cell {k}", Comp.ks3(
            p=anim([(tk, [lx - 900 - 120 * k, ly - 300 + 60 * (k % 3), 0], "crash"), (tk + 12, [lx, ly, 0])]),
            rz=anim([(tk, -16 + 6 * k, "crash"), (tk + 12, 0)]),
            s=anim([(tk, [70, 70, 100], "crash"), (tk + 12, [100, 100, 100])])), ip=tk)
        sub.n0 = len(card.c._layers)
        sub.image(photo(name, 360, 455), 360, 455, 0, 0, cw_, chh)
        pop_close(card, sub, tk)
        add_fx(layers_since(card.c, sub.n0), gblur_dir(anim([(tk, [30], "settle-soft"), (tk + 8, [0])]), 2))
        card.c.cue(tk + 6, "tick", 0.35)
        # sport tag
        tt = t + 50 + 3 * k
        tg = pop_group(card, g, f"tag {k}", tt, lx, ly, dy=14)
        tw = fonts.width(BODY, 24, tag) + 30
        tg.box(lx + 12, ly + chh - 56, tw, 44, "white", r=22)
        tg.text(tag, BODY, 24, "ink", lx + 12 + tw / 2, ly + chh - 34 + CAP * 24 / 2, j=2)
        pop_close(card, tg, tt)
        if k in (0, 2, 3):
            ts = t + 70 + 3 * k
            sb = pop_group(card, g, f"star {k}", ts, lx + cw_ - 36, ly + 36, dy=0, scale=40)
            sb.circle(lx + cw_ - 36, ly + 36, 52, "orange")
            sb.star(lx + cw_ - 36, ly + 37, 30, "white")
            pop_close(card, sb, ts)
            card.c.cue(ts, "pop", 0.4)
    card.close(g)


def feat_packages(card, t):
    w, h = FEAT[5]
    g = feature_group(card, 5, w, h, t)
    hd = pop_group(card, g, "head", t + 6, 0, 0)
    hd.text("Packages", MED, 46, "ink", 48, 96)
    pop_close(card, hd, t + 6)
    pk = pop_group(card, g, "package", t + 10, 0, 0)
    pk.box(28, 132, w - 56, 352, "panel", r=22)
    pk.text("Full match", MED, 46, "ink", 64, 212)
    pk.text("2 hrs · 60 edited photos · ready in 3 days", BODY, 30, "grey", 64, 262)
    pk.text("Price", BODY, 28, "grey", 64, 340)
    pk.box(64, 362, 300, 88, "white", r=16, line="line", line_w=2)
    pop_close(card, pk, t + 10)
    ty = t + 26
    docs = [(0, "S$", MED, 42, "pill", 0), (ty, "S$", MED, 42, "ink", 0), (ty + 5, "S$7", MED, 42, "ink", 0),
            (ty + 9, "S$70", MED, 42, "ink", 0)]
    g.keyed_text(docs, 92, 420, ip=t + 10)
    card.c.cue(ty + 5, "key", 0.5)
    card.c.cue(ty + 9, "key", 0.5)
    # caret
    cx_k = [(t + 10, [92 + fonts.width(MED, 42, "S$") + 6, 0, 0], "hold"),
            (ty + 5, [92 + fonts.width(MED, 42, "S$7") + 6, 0, 0], "hold"),
            (ty + 9, [92 + fonts.width(MED, 42, "S$70") + 6, 0, 0], "hold")]
    car = group3d(g, "caret", Comp.ks3(p=anim(cx_k)), ip=t + 10, op=ty + 30)
    car.box(0, 380, 4, 52, "ink")
    for lyr in layers_since(card.c, len(card.c._layers) - 1):
        lyr["ks"]["o"] = anim([(t + 10, 100, "hold"), (t + 18, 0, "hold"), (t + 26, 100, "hold"), (ty + 22, 0, "hold")])
    # Active toggle
    ta = ty + 20
    pk2 = pop_group(card, g, "active", t + 12, 0, 0)
    pk2.text("Active", BODY, 32, "ink", 470, 418)
    pop_close(card, pk2, t + 12)
    tgx, tgy, tgw, tgh = 610, 376, 120, 64
    g.box(tgx, tgy, tgw, tgh, None, r=32, fill_keys=[(t + 12, "pill", "hold"), (ta, "pill", "settle-soft"),
                                                     (ta + 6, "orange")])
    kn = group3d(g, "knob", Comp.ks3(p=anim([(ta, [0, 0, 0], "entrance-sharp"), (ta + 8, [tgw - tgh, 0, 0])])),
                 ip=t + 12)
    kn.circle(tgx + tgh / 2, tgy + tgh / 2, tgh - 12, "white")
    card.c.cue(ta, "tap", 0.5)
    # the tooltip's second line, kept as the beat's proof line
    ln = pop_group(card, g, "line", t + 36, 0, 0)
    ln.text("Clients book a package and pay on the site.", BODY, 32, "grey", 48, 560)
    pop_close(card, ln, t + 36)
    card.close(g)
    return ty, ta


TAPS = [26, 28, 29]   # days after onboarding opens (24 Nov); the request comes for Sat 28


def feat_availability(card, t):
    w, h = FEAT[6]
    g = feature_group(card, 6, w, h, t)
    hd = pop_group(card, g, "head", t + 6, 0, 0)
    hd.text("AVAILABILITY", BODY, 28, "ink", 48, 80, tracking=140)
    hd.text("NOVEMBER 2026", MED, 34, "ink", 48, 136)
    pop_close(card, hd, t + 6)
    gx, gw = 48, w - 96
    cwd = gw / 7
    cal = pop_group(card, g, "calendar", t + 10, 0, 0)
    for k, d in enumerate("MTWTFSS"):
        cal.text(d, BODY, 28, "grey", gx + cwd * (k + 0.5), 206, j=2)
    weeks = calendar.monthcalendar(2026, 11)
    rh = 88
    pos = {}
    for r_, week in enumerate(weeks):
        for k, day in enumerate(week):
            if day:
                pos[day] = (gx + cwd * (k + 0.5), 262 + rh * r_)
    pop_close(card, cal, t + 10)
    taps = {}
    for i, day in enumerate(TAPS):
        dx, dy = pos[day]
        tt = t + 30 + i * 11
        taps[day] = tt
        ring = group3d(g, f"day {day}", Comp.ks3(p=(dx, dy, 0), a=(dx, dy, 0),
                                                 s=anim([(tt, [40, 40, 100], "expressive-pop"),
                                                         (tt + 7, [112, 112, 100], "settle-soft"),
                                                         (tt + 13, [100, 100, 100])])), ip=tt)
        ring.circle(dx, dy, 72, "green")
        card.c.cue(tt, "tick", 0.55)
    for day, (dx, dy) in pos.items():
        on = day in taps
        g.text(str(day), MED if on else BODY, 32, "ink", dx, dy + CAP * 32 / 2, j=2, o=100 if on else 45)
    leg = pop_group(card, g, "legend", t + 14, 0, 0)
    leg.circle(gx + 14, 790, 24, "green")
    leg.text("Available, tap to pick", BODY, 28, "grey", gx + 42, 800)
    pop_close(card, leg, t + 14)
    card.close(g)
    return {d: (pos[d], taps[d]) for d in TAPS}


def feat_payouts(card, t):
    w, h = FEAT[7]
    g = feature_group(card, 7, w, h, t)
    hd = pop_group(card, g, "head", t + 6, 0, 0)
    hd.text("Payouts", MED, 46, "ink", 48, 96)
    hd.text("Connect Stripe to get paid automatically", BODY, 33, "grey", 48, 160)
    hd.text("once a client confirms their photos arrived.", BODY, 33, "grey", 48, 206)
    pop_close(card, hd, t + 6)
    press = t + 36
    bx, by, bw, bh = 48, 268, 440, 100
    btn = pop_group(card, g, "connect", t + 12, 0, 0)
    pop_close(card, btn, t + 12)
    button(btn, fonts, "Connect Stripe", bx, by, bw, bh, style="ink", size=36, op=press + 3, press=press)
    done = group3d(g, "connected", Comp.ks3(p=(bx + bw / 2, by + bh / 2, 0), a=(bx + bw / 2, by + bh / 2, 0),
                                            s=anim([(press + 3, [92, 92, 100], "settle-soft"),
                                                    (press + 12, [100, 100, 100])])), ip=press + 3)
    done.box(bx, by, bw, bh, "green", r=bh * 0.22)
    done.check(bx + 64, by + bh / 2 + 1, 36, "ink", draw_at=press + 6)
    done.text("Connected", MED, 36, "ink", bx + bw / 2 + 30, by + bh / 2 + CAP * 36 / 2, j=2)
    card.c.cue(press + 4, "chime", 0.8)
    ft = pop_group(card, g, "earnings", t + 18, 0, 0)
    ft.line(48, 420, w - 48, 420, "line", 2)
    ft.text("Earnings this month", BODY, 30, "grey", 48, 478)
    ft.text("S$0.00", MED, 34, "ink", w - 48, 478, j=1)
    pop_close(card, ft, t + 18)
    card.close(g)
    return press, (bx + bw * 0.5, by + bh * 0.55)


STEPS8 = ["Display name", "Profile photo", "At least one specialty", "WhatsApp or Telegram",
          "At least one active package", "At least 6 portfolio photos", "Set your availability", "Set up payouts"]


def act_b():
    global CUR
    c = Comp("B Studio - the tour", W, H, B_FR)
    ground(c, "light")
    soft_vignette(c)
    c.camera3d(zoom=1400)
    nx, ny = next_xy()
    cur = []          # cursor keys
    presses = []
    # 1 + 2: welcome and bookings
    say(c, ["SET IT UP", "ONCE."], 6, exit_at=96)
    e1, p1, _, l1 = T[1]
    c1 = tour_card(c, 1, e1, l1, press=p1, rise=True)
    c1.finish()
    e2, p2, _, l2 = T[2]
    c2 = tour_card(c, 2, e2, l2, press=p2)
    c2.finish()
    cur += [(0, (nx - 150, ny - 260)), (p1 - 10, (nx, ny)), (p1 + 6, (nx + 8, ny + 6), "settle-soft"),
            (p2 - 10, (nx, ny)), (p2 + 6, (nx + 8, ny + 6), "settle-soft")]
    presses += [p1, p2]
    # 3: your profile
    e3, p3, m3, l3 = T[3]
    say(c, ["THE PAGE", "CLIENTS SEE."], e3 + 4, exit_at=l3 - 6)
    c3 = tour_card(c, 3, e3, l3, press=p3, morph=[(m3, m3 + 14, FEAT[3])], until=m3)
    feat_profile(c3, m3)
    c3.finish()
    cur += [(p3 - 10, (nx, ny)), (p3 + 10, (nx + 90, ny + 220), "settle-soft"), (l3 - 2, (nx + 40, ny + 120))]
    presses.append(p3)
    # 4: portfolio
    e4, p4, m4, l4 = T[4]
    say(c, ["SIX SHOTS.", "TAGGED BY SPORT."], e4 + 4, exit_at=l4 - 6)
    c4 = tour_card(c, 4, e4, l4, press=p4, morph=[(m4, m4 + 14, FEAT[4])], until=m4)
    feat_portfolio(c4, m4)
    c4.finish()
    cur += [(p4 - 10, (nx, ny)), (p4 + 12, (nx + 110, ny + 300), "settle-soft"), (l4 - 2, (nx + 60, ny + 160))]
    presses.append(p4)
    # 5: packages
    e5, p5, m5, l5 = T[5]
    say(c, ["SET", "YOUR PRICE."], e5 + 4, exit_at=l5 - 6)
    c5 = tour_card(c, 5, e5, l5, press=p5, morph=[(m5, m5 + 14, FEAT[5])], until=m5)
    ty, ta = feat_packages(c5, m5)
    c5.finish()
    fx_, fy_ = screen(200, 406, *FEAT[5])
    tx_, ty_ = screen(670, 412, *FEAT[5])
    cur += [(p5 - 10, (nx, ny)), (ty - 6, (fx_, fy_)), (ta - 6, (tx_, ty_)), (ta + 12, (tx_ + 30, ty_ + 50), "settle-soft"),
            (l5 - 2, (nx, ny + 40))]
    presses += [p5, ty - 2, ta]
    # 6: availability
    e6, p6, m6, l6 = T[6]
    say(c, ["MARK YOUR", "FREE DAYS."], e6 + 4, exit_at=l6 - 6)
    c6 = tour_card(c, 6, e6, l6, press=p6, morph=[(m6, m6 + 14, FEAT[6])], until=m6)
    taps = feat_availability(c6, m6)
    c6.finish()
    cur += [(p6 - 10, (nx, ny))]
    presses.append(p6)
    for d in TAPS:
        (dx, dy), tt = taps[d]
        sx_, sy_ = screen(dx, dy, *FEAT[6])
        cur += [(tt - 6, (sx_ + 6, sy_ + 8)), (tt + 3, (sx_ + 6, sy_ + 8), "settle-soft")]
        presses.append(tt)
    cur += [(l6 - 2, (nx, ny + 60))]
    # 7: payouts
    e7, p7, m7, l7 = T[7]
    say(c, ["PAID WHEN", "PHOTOS ARRIVE."], e7 + 4, exit_at=l7 - 6)
    c7 = tour_card(c, 7, e7, l7, press=p7, morph=[(m7, m7 + 14, FEAT[7])], until=m7)
    pp, (bxl, byl) = feat_payouts(c7, m7)
    c7.finish()
    bsx, bsy = screen(bxl, byl, *FEAT[7])
    cur += [(p7 - 10, (nx, ny)), (pp - 8, (bsx, bsy)), (pp + 10, (bsx + 20, bsy + 40), "settle-soft"),
            (l7 - 2, (nx - 40, ny + 80))]
    presses += [p7, pp]
    # 8, 9, 10: the rest of the tour flicks by, then Finish grows into the checklist
    e8 = 696
    t9, t10, fin = 720, 738, 756
    card = Card(c, "card 8-10", e8, None, morph=[(fin + 2, fin + 16, CHECK)], op=B_FR)
    for step, a, b_ in ((8, e8, t9), (9, t9, t10), (10, t10, fin + 2)):
        g = card.content(f"tour {step}", CW, CH, a, b_ + 1)
        tour_content(g, step, press=(b_ - 2) if step < 10 else fin)
        if step > 8:
            c.cue(a, "tick", 0.5)
    card.finish()
    cur += [(e8 + 8, (nx, ny)), (t9 - 2, (nx, ny), "hold"), (t10 - 2, (nx + 4, ny + 2), "hold")]
    presses += [t9 - 2, t10 - 2, fin]
    say(c, ["ALMOST", "THERE."], e8 + 4, exit_at=fin - 2)
    say(c, ["ALL", "SET."], fin + 10)
    # the checklist
    w, h = CHECK
    g = card.content("checklist", w, h, fin + 4, None, fade_in=fin + 4)
    g.text("Set up your profile", MED, 50, "ink", 48, 112)
    t_tick0, pitch = fin + 14, 3
    done_at = [t_tick0 + i * pitch for i in range(8)]
    g.keyed_text([(0, "1 of 8 steps done.", BODY, 30, "grey", 0)] +
                 [(f, f"{i + 1} of 8 steps done.", BODY, 30, "grey", 0) for i, f in enumerate(done_at) if i >= 1],
                 48, 162)
    g.box(48, 196, 784, 12, DASH_OFF, r=6)
    bar = group3d(g, "progress", Comp.ks3(p=(48, 202, 0), a=(48, 202, 0),
                                          s=anim([(fin, [12.5, 100, 100], "hold")] +
                                                 [(f, [100 * (i + 1) / 8, 100, 100], "settle-soft") for i, f in enumerate(done_at) if i >= 1] +
                                                 [(done_at[-1] + 6, [100, 100, 100])])))
    bar.box(48, 196, 784, 12, "orange", r=6)
    for i, label in enumerate(STEPS8):
        y = 236 + i * 68
        f = done_at[i]
        g.box(48, y + 67, 784, 1.5, "line")
        g.circle(80, y + 32, 46, None, line="line", line_w=2)
        row = group3d(g, f"row {i}", Comp.ks3(p=(80, y + 32, 0), a=(80, y + 32, 0),
                                              s=anim([(f, [60, 60, 100], "expressive-pop"), (f + 6, [100, 100, 100])])),
                      ip=f)
        row.circle(80, y + 32, 46, "orange")
        row.check(80, y + 33, 28, "white", draw_at=f, width=5)
        g.text(label, BODY, 34, "ink", 126, y + 32 + CAP * 34 / 2)
        if i >= 6:
            g.text("recommended", BODY, 26, "grey", 126 + fonts.width(BODY, 34, label) + 14, y + 32 + CAP * 26 / 2)
        c.cue(f, "tick", 0.4)
    c.cue(done_at[-1] + 2, "chime_soft", 0.8)
    t_prev = done_at[-1] + 10
    press_prev = 830
    pv = pop_group(card, g, "preview", t_prev, 0, 0)
    pop_close(card, pv, t_prev)
    button(pv, fonts, "Preview profile", 48, 790, 784, 96, style="ink", size=36, press=press_prev)
    card.close(g)
    vx, vy = screen(48 + 784 * 0.62, 790 + 56, w, h)
    cur += [(t_prev + 4, (nx + 30, ny + 120)), (press_prev - 8, (vx, vy)), (B_FR, (vx + 6, vy + 6), "settle-soft")]
    presses.append(press_prev)
    cur.sort(key=lambda k: k[0])
    cursor_track(c, cur, presses=presses)
    CUR = (vx + 6, vy + 6)
    c.cue(press_prev + 3, "whoosh", 0.6)
    return c


# =========================================================================== act C: booked, then the brand
def new_profile_page(pl):
    """The profile page as a brand-new photographer's (no reviews yet: nothing invented), mobile layout, 1000 wide."""
    YOUR, PRICE = bf.YOUR, bf.PRICE
    pl.box(0, 0, pl.w, pl.h, "light", r=0, shadow=SHADOW)
    pl.text("Photographers", BODY, 30, "grey", 40, 70)
    x = 40 + fonts.width(BODY, 30, "Photographers") + 18
    pl.text("›", BODY, 30, "grey", x, 70)
    pl.text("Football", BODY, 30, "grey", x + 30, 70)
    x2 = x + 30 + fonts.width(BODY, 30, "Football") + 18
    pl.text("›", BODY, 30, "grey", x2, 70)
    pl.text(YOUR, BODY, 30, "ink", x2 + 30, 70)
    pl.image("v4-avatar.png", 320, 320, 40, 110, 116, 116)
    pl.text(YOUR.upper(), TITLE, 70, "ink", 180, 194)
    pl.heart(944, 166, 44, "ink")
    pl.image("celebrate-run.jpg", *bf.sz("celebrate-run.jpg"), 0, 266, 1000, 666)
    for k, n in enumerate(["tackle-night", "basketball", "sepak-takraw", "point-orange"]):
        f = photo(n, 330, 220)
        pl.image(f, 330, 220, 40 + k * 236, 952, 220, 147)
    pl.box(37, 949, 226, 153, None, r=2, line="green", line_w=6)
    py = 1132
    pl.box(0, py, 1000, 700, "panel")
    pl.text("Match days, finals and the", MED, 44, "ink", 40, py + 86)
    pl.text("moments between.", MED, 44, "ink", 40, py + 138)
    rows = [("PACKAGES FROM", PRICE), ("NEXT FREE DATE", "Thu 26 Nov"), ("COVERS", "North, Central"),
            ("SPECIALTY", "Football"), ("LANGUAGES", "English")]
    for k, (lab, val) in enumerate(rows):
        yy = py + 226 + k * 64
        pl.text(lab, BODY, 26, "grey", 40, yy, tracking=120)
        pl.text(val, MED if lab == "PACKAGES FROM" else BODY, 34, "ink", 380, yy)
        if lab == "NEXT FREE DATE":
            pl.line(380, yy + 10, 380 + fonts.width(BODY, 34, val), yy + 10, "ink", 2)
    tx = 40
    for t in ("Football", "Events"):
        tw = fonts.width(BODY, 26, t) + 40
        pl.box(tx, py + 548, tw, 46, "pill", r=23)
        pl.text(t, BODY, 26, "ink", tx + tw / 2, py + 579, j=2)
        tx += tw + 12
    return py


C_FR = 252


def act_c():
    c = Comp("C Booked - get in the frame", W, H, C_FR)
    ground(c, "light")
    soft_vignette(c)
    c.camera3d(zoom=1400)
    # the profile page arrives from the preview press (pull-back reveal), then scrolls to the packages
    pw, ph = 1000, 1832
    s0 = 0.62 if LANDSCAPE else 1.0
    top = (UI_X, 1080) if not LANDSCAPE else (UI_X, 900)
    bot = (UI_X, 640) if not LANDSCAPE else (UI_X, 260)
    p = anim([(0, [top[0], top[1], -520], "crash"), (14, [top[0], top[1], 0], "hold"),
              (20, [top[0], top[1], 0], "scroll"), (52, [bot[0], bot[1], 0], "linear"),
              (110, [bot[0], bot[1] - 30, 0])])
    pl = Plane(c, "profile page", pw, ph, p, rx=anim([(0, 8, "crash"), (16, 0)]), s=(s0 * 100, s0 * 100, 100), op=112)
    py = new_profile_page(pl)
    button(pl, fonts, "See packages", 40, py + 616, 920, 96, style="green", size=34)
    c.cue(0, "whoosh", 0.55)
    # a booking request lands
    t_req = 56
    nw, nh = 880, 400
    ncx, ncy = (UI_X, 560) if not LANDSCAPE else (UI_X, 420)
    c.shape("focus veil", [group([rect(W, H, W / 2, H / 2), fl("ink")])],
            o=anim([(t_req - 2, 0, "settle-soft"), (t_req + 10, 30)]), ip=t_req - 2, op=112)
    nt = Plane(c, "request", nw, nh, anim([(t_req, [ncx, -nh, 0], "crash"), (t_req + 12, [ncx, ncy, 0], "linear"),
                                         (100, [ncx, ncy - 10, 0])]),
               rx=anim([(t_req, -18, "settle-soft"), (t_req + 16, 0)]), s=(UI_S * 100, UI_S * 100, 100), ip=t_req, op=112)
    nt.box(0, 0, nw, nh, "card", r=30, shadow=SHADOW)
    nt.circle(60, 70, 18, "orange")
    nt.text("Bookings", BODY, 28, "grey", 84, 80)
    nt.text("New booking request", MED, 46, "ink", 48, 156)
    nt.text("Sat 28 Nov · Full match", BODY, 34, "grey", 48, 214)
    nt.text(bf.PRICE, MED, 44, "ink", nw - 48, 214, j=1)
    press = 92
    nt.box(48, 268, 380, 96, "#e9ecef", r=21)
    nt.text("Decline", BODY, 34, "ink", 48 + 190, 316 + CAP * 34 / 2, j=2)
    button(nt, fonts, "Accept", 452, 268, 380, 96, style="green", size=36, arrow=False, press=press)
    c.cue(t_req, "blip_in", 1.0)
    c.cue(t_req + 2, "pop", 0.5)
    ax, ay = ncx + (452 + 190 - nw / 2) * UI_S, ncy + (316 - nh / 2) * UI_S
    sx0, sy0 = CUR
    cursor_track(c, [(0, (sx0, sy0)), (t_req + 14, (sx0 - 40, sy0 - 200), "settle-soft"), (press - 8, (ax + 20, ay + 14)),
                     (press + 6, (ax + 24, ay + 20), "settle-soft"), (106, (ax + 40, ay + 60))], presses=[press], op=106)
    # Accept blooms green across the frame, and the bloom settles into the dark ground with the site's glow
    t_bl = press + 2
    c.no_camera.add(c.shape("bloom", [group([ellipse(100, 100, 0, 0), fl("green")])], p=(ax, ay),
                            s=anim([(t_bl, [10, 10, 100], "exit-accelerate"), (t_bl + 12, [6200, 6200, 100])]),
                            ip=t_bl))
    c.no_camera.add(c.shape("night", [group([rect(W, H, W / 2, H / 2), fl(NIGHT)])],
                            o=anim([(t_bl + 12, 0, "settle-soft"), (t_bl + 22, 100)]), ip=t_bl + 12))
    gh = H * 0.6
    c.no_camera.add(c.shape("glow", [group([rect(W, gh, W / 2, H - gh / 2),
                                            gradient([(0, NIGHT), (0.6, "#163f12"), (1, "#3fd31f")], [W / 2, H - gh],
                                                     [W / 2, H], alpha_stops=[(0, 0), (0.6, 0.6), (1, 0.95)])])],
                            p=anim([(t_bl + 12, [0, 0, 0], "linear"), (C_FR, [0, 40, 0])]),
                            o=anim([(t_bl + 12, 0, "settle-soft"), (t_bl + 24, 100)]), ip=t_bl + 12))
    c.cue(t_bl, "boom", 0.75)
    c.cue(t_bl + 2, "chime", 1.0)
    # BOOKED.
    t_bk = t_bl + 10
    bsize = fonts.fit(STATE, ["BOOKED."], 900 if not LANDSCAPE else 1300, 300 if not LANDSCAPE else 330)
    bcy = H / 2 - (60 if not LANDSCAPE else 0)
    out_bk = 138
    bk = bf.wordmark_crash(c, "BOOKED.", bsize, W / 2, bcy, t_bk, out_bk + 9, color="white", streaks=4,
                           start_scale=330, settle_end=95)
    for lyr in c._layers:
        if lyr["ind"] == bk:
            k = lyr["ks"]["p"] = anim([(t_bk, [W / 2, bcy, 0], "hold"), (out_bk, [W / 2, bcy, 0], "exit-accelerate"),
                                       (out_bk + 9, [W / 2, bcy - H * 0.55, 0])])
            lyr["op"] = out_bk + 10
            with_fx(c, bk, gblur_dir(anim([(out_bk, [0], "exit-accelerate"), (out_bk + 9, [40])]), 3))
    c.cue(t_bk, "boom_small", 0.6)
    c.cue(out_bk, "whoosh", 0.5)
    # GET IN THE FRAME.
    t_g = out_bk + 3
    out_g = 186
    if LANDSCAPE:
        runs = ["GET IN THE ", "FRAME."]
        gsize = fonts.fit(STATE, ["".join(runs)], 1500, 170)
        x = W / 2 - fonts.width(STATE, gsize, "".join(runs)) / 2
        for i, run in enumerate(runs):
            fp.rise_line(c, fonts, run, STATE, gsize, col("green" if i else "white"), x, H / 2 + CAP * gsize / 2, j=0,
                         start=t_g + i * 6, exit_at=out_g + i * 2)
            x += fonts.width(STATE, gsize, run)
    else:
        gl = ["GET IN THE", "FRAME."]
        gsize = fonts.fit(STATE, gl, 860, 190)
        lead = gsize * 0.96
        gcy = H / 2 - 40
        b0 = gcy - lead * (len(gl) - 1) / 2 + CAP * gsize / 2
        for i, ln in enumerate(gl):
            fp.rise_line(c, fonts, ln, STATE, gsize, col("green" if i else "white"), W / 2, b0 + i * lead, j=2,
                         start=t_g + i * 6, exit_at=out_g + i * 2)
    c.cue(t_g, "tick", 0.5)
    # OUTTAKES in focus, then the address
    lock, shot = out_g + 14, out_g + 19
    wsize = fonts.fit(STATE, ["OUTTAKES"], 860 if not LANDSCAPE else 1240, 300)
    wcy = H / 2 - (90 if not LANDSCAPE else 70)
    tw = fonts.width(STATE, wsize, "OUTTAKES")
    cap = CAP * wsize
    wm = c.text("end wordmark", text_doc("OUTTAKES", STATE, wsize, col("white"), justify=2), p=(W / 2, wcy),
                a=(0, -cap / 2), ip=out_g + 2,
                s=anim([(out_g + 2, [112, 112, 100], "settle-soft"), (lock + 3, [100, 100, 100], "linear"),
                        (C_FR, [97, 97, 100])]))
    with_fx(c, wm, gblur(anim([(out_g + 2, [50], "settle-soft"), (lock + 1, [0])])))
    c._layers[-1]["ks"]["o"] = anim([(out_g + 2, 0, "settle-soft"), (out_g + 6, 100)])
    fw, fh = tw + 140, cap + 160
    bf.corner_frame(c, W / 2, wcy, fw, fh, arm=min(84, fh * 0.32), width=7,
                    scale_keys=[(out_g + 2, [150, 150, 100], "crash"), (lock - 1, [104, 104, 100], "crash"),
                                (lock + 2, [99, 99, 100], "hold"), (C_FR, [99, 99, 100])],
                    colour_keys=[(out_g + 2, "white", "hold"), (lock, "green", "hold")], ip=out_g + 2, op=C_FR,
                    o=anim([(out_g + 2, 0, "settle-soft"), (out_g + 6, 100)]))
    c.cue(lock, "af", 0.6)
    fp.flash(c, shot, peak=24, dur=3)
    c.cue(shot, "shutter_big", 0.9)
    c.cue(shot, "boom_small", 0.35)
    uy = wcy + cap / 2 + (250 if not LANDSCAPE else 190)
    us = fonts.fit(TITLE, ["outtakes.sg"], 760, 80 if not LANDSCAPE else 66)
    fp.fade_line(c, "outtakes.sg", TITLE, us, "white", W / 2, uy, j=2, start=shot + 6)
    fp.fade_line(c, "Photographers join free from 24 Nov", BODY, 40 if not LANDSCAPE else 34, "#a8adb1", W / 2,
                 uy + 40 + (60 if not LANDSCAPE else 50), j=2, start=shot + 10)
    c.cue(shot + 6, "tick", 0.5)
    return c


ACTS = [act_a, act_b, act_c]


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    cues, offset, meta = [], 0, []
    for n, fn in enumerate(ACTS, start=1):
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
    print(f"total {offset} frames = {offset / 30:.2f}s")


if __name__ == "__main__":
    main()
