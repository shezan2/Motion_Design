#!/usr/bin/env python3
"""ref_breakdown.py - turn reference videos (or screen recordings of reels) into contact sheets and timing numbers.

Use it whenever a client or Shezan sends reference videos. One command per batch replaces watching every file
frame by frame: it finds the creative inside the recording (a reel inside an iPad/phone screen recording, a 16:9
film letterboxed inside a reel), then measures cuts, how long moves last, how far apart beats are, reading
holds, and roughly how the picture sits on the music.

    python3 ref_breakdown.py ref1.mp4 ref2.mov ... [--out refs-breakdown] [--fps 3] [--crop W:H:X:Y]

Writes into --out (default ./refs-breakdown):
    <name>_box.jpg        one frame with the detected content box drawn on it: check it, and pass --crop if wrong
    <name>_sheet.jpg      contact sheet of the cropped creative at --fps (time burned into each tile);
                          long videos get _sheet2.jpg, _sheet3.jpg ...
    breakdown.md          table of every video plus per-video numbers (paste into your reference notes)
    breakdown.json        the same numbers for scripts

What the numbers mean (all frame counts are at 30 fps):
    cuts / ASL            hard cuts (a big one-frame picture change) and average shot length. Premium SaaS reels often
                          run 15-20 s with only 1-3 hard cuts: scenes morph into each other instead of cutting.
    move length           how long each big motion burst lasts (median and IQR). Snappy work sits around 4-9 f.
    beat spacing          seconds between big motion bursts: how often something new happens.
    holds                 stretches of 0.4 s or more where the picture is almost still: reading time.
    moving share          share of frames where something visibly moves.
    audio                 rough tempo (may be half or double the real one), onsets per second, and the share of motion
                          bursts that land within 100 ms of a sound onset, next to the share you would get by chance.

Needs ffmpeg/ffprobe and numpy only. Your own eyes still decide: look at every sheet before you trust a number.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

ANALYSIS_FPS = 30
ASPECTS = {"9:16": 9 / 16, "4:5": 4 / 5, "1:1": 1.0, "16:9": 16 / 9}


def probe(path: str) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration:stream=codec_type,width,height,r_frame_rate", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    info = json.loads(out)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    return {"w": int(v["width"]), "h": int(v["height"]), "dur": float(info["format"]["duration"]),
            "audio": any(s["codec_type"] == "audio" for s in info["streams"])}


def gray_frames(path: str, fps: float, w: int, h: int, crop: str | None = None) -> np.ndarray:
    vf = f"fps={fps}" + (f",crop={crop}" if crop else "") + f",scale={w}:{h},format=gray"
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", vf, "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)


def longest_run(mask: np.ndarray):
    idx = np.where(mask)[0]
    if len(idx) == 0:
        return None
    best, start, prev = None, idx[0], idx[0]
    for v in list(idx[1:]) + [None]:
        if v is None or v != prev + 1:
            if best is None or prev - start > best[1] - best[0]:
                best = (start, prev)
            if v is not None:
                start = v
        if v is not None:
            prev = v
    return best


def detect_box(path: str, W: int, H: int) -> tuple[int, int, int, int, str]:
    """Content box (w, h, x, y) and its aspect label.

    The creative is the part of the recording that is both sharp and changing: app chrome and captions are sharp but
    static, the blurred "ambient" fill some apps paint around a video changes but is soft, a progress bar is a thin
    band. Columns give the width; rows give the span the creative ever uses; the box is then the smallest common
    aspect (16:9, 1:1, 4:5, 9:16) of that width that contains the span.
    """
    q = 4
    sw, sh = max(16, W // q // 2 * 2), max(16, H // q // 2 * 2)
    fr = gray_frames(path, 4, sw, sh)
    sx, sy = W / sw, H / sh
    sd = fr.std(axis=0)
    cols = longest_run((sd > 15).mean(axis=0) > 0.10) or longest_run((sd > 6).mean(axis=0) > 0.10)
    if cols is None:
        return W, H, 0, 0, "full"
    x0, x1 = int(cols[0] * sx), int((cols[1] + 1) * sx)
    sub = fr[:, :, cols[0]:cols[1] + 1]
    if sub.shape[2] < 3:
        return W, H, 0, 0, "full"
    # per frame: pixels that are on a sharp edge AND changed since the previous frame. A row belongs to the creative
    # when it has such events in a good share of the frames (a reel scrolling in for half a second does not count).
    gx = np.abs(np.diff(sub, axis=2))[:, :-1, :]           # (T, sh-1, cw-1)
    gy = np.abs(np.diff(sub, axis=1))[:, :, :-1]           # (T, sh-1, cw-1)
    dt = np.abs(np.diff(sub, axis=0))[:, :-1, :-1]         # (T-1, sh-1, cw-1)
    evt = (np.maximum(gx, gy)[1:] > 20) & (dt > 8)
    rowmask = (evt.mean(axis=2) > 0.005).mean(axis=0) > 0.08
    # drop thin bands (progress bars, hairlines): keep runs at least 4 analysis rows tall
    keep = np.zeros_like(rowmask)
    i = 0
    while i < len(rowmask):
        if rowmask[i]:
            j = i
            while j + 1 < len(rowmask) and rowmask[j + 1]:
                j += 1
            if j - i + 1 >= 4:
                keep[i:j + 1] = True
            i = j + 1
        else:
            i += 1
    ys = np.where(keep)[0]
    if len(ys) == 0:
        ys = np.array([0, sh - 1])
    y0, y1 = int(ys[0] * sy), int((ys[-1] + 1) * sy)
    bw, span = x1 - x0, y1 - y0
    if bw > 0.9 * W and span > 0.9 * H:
        return W, H, 0, 0, "full"
    # smallest common aspect of this width whose height still contains the span (allow 6% slack)
    fits = [(k, r) for k, r in sorted(ASPECTS.items(), key=lambda kv: -kv[1]) if bw / r >= span * 0.94]
    label, ratio = fits[0] if fits else ("9:16", ASPECTS["9:16"])
    # A short span inside a tall column is either a letterboxed film (hard edges at its top and bottom in many
    # frames) or a tall creative that only uses its middle. When unsure, keep the taller box: cropping bars wastes
    # a little sheet space, cropping content loses the reference.
    if label != "9:16" and bw / ASPECTS["9:16"] <= H * 1.02:
        def edge_share(yq: int) -> float:
            a, b = max(0, yq - 2), min(sh - 1, yq + 2)
            jump = np.abs(sub[:, b, :] - sub[:, a, :]) > 25
            return float((jump.mean(axis=1) > 0.5).mean())
        if min(edge_share(int(ys[0])), edge_share(int(ys[-1]) + 1)) < 0.25:
            label, ratio = "9:16", ASPECTS["9:16"]
    th = min(H, int(round(bw / ratio)))
    cy = (y0 + y1) / 2
    ny0 = int(round(min(max(cy - th / 2, 0), H - th)))
    bw -= bw % 2
    th -= th % 2
    return bw, th, x0, ny0, label


def peaks(sig: np.ndarray, height: float, distance: int) -> np.ndarray:
    cand = [i for i in range(1, len(sig) - 1) if sig[i] > height and sig[i] > sig[i - 1] and sig[i] >= sig[i + 1]]
    cand.sort(key=lambda i: -sig[i])
    taken: list[int] = []
    for i in cand:
        if all(abs(i - j) >= distance for j in taken):
            taken.append(i)
    return np.array(sorted(taken), dtype=int)


def motion_numbers(path: str, crop: str, aspect: str) -> dict:
    w, h = {"9:16": (54, 96), "4:5": (64, 80), "1:1": (72, 72), "16:9": (96, 54)}.get(aspect, (96, 54))
    fr = gray_frames(path, ANALYSIS_FPS, w, h, crop)
    d = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))
    dur = len(fr) / ANALYSIS_FPS
    cuts = []
    for j in range(len(d)):
        nb = np.delete(d[max(0, j - 6):j + 7], j - max(0, j - 6))
        if d[j] > 12 and d[j] > 3 * np.median(nb) + 4 and (not cuts or j - cuts[-1] > 4):
            cuts.append(j)
    pk = peaks(d, max(3.0, float(np.percentile(d, 85))), 6)
    widths = []
    for p in pk:
        thr, a, b = 0.25 * d[p], p, p
        while a > 0 and d[a - 1] > thr:
            a -= 1
        while b < len(d) - 1 and d[b + 1] > thr:
            b += 1
        widths.append(b - a + 1)
    holds, run = [], 0
    for v in list(d) + [99]:
        if v <= 0.6:
            run += 1
        else:
            if run >= 12:
                holds.append(round(run / ANALYSIS_FPS, 2))
            run = 0
    gaps = np.diff(pk) / ANALYSIS_FPS if len(pk) > 1 else np.array([])
    q = lambda arr, p: round(float(np.percentile(arr, p)), 2) if len(arr) else None
    return {
        "duration_s": round(dur, 2),
        "cuts_s": [round((c + 1) / ANALYSIS_FPS, 2) for c in cuts],
        "asl_s": round(dur / (len(cuts) + 1), 2),
        "moving_share": round(float((d > 1.0).mean()), 2),
        "bursts": int(len(pk)),
        "burst_frames_median": q(widths, 50), "burst_frames_p25": q(widths, 25), "burst_frames_p75": q(widths, 75),
        "beat_spacing_s_median": q(gaps, 50), "beat_spacing_s_p25": q(gaps, 25), "beat_spacing_s_p75": q(gaps, 75),
        "holds_s": holds,
        "burst_times_s": [round((p + 1) / ANALYSIS_FPS, 2) for p in pk],
    }


def audio_numbers(path: str, burst_times: list[float]) -> dict:
    sr, hop, n_fft = 22050, 220, 1024
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32)
    if len(x) < sr:
        return {}
    level = 20 * math.log10(float(np.sqrt(np.mean(x ** 2))) + 1e-9)
    n = (len(x) - n_fft) // hop
    win = np.hanning(n_fft)
    spec = np.abs(np.fft.rfft(np.stack([x[k * hop:k * hop + n_fft] * win for k in range(n)]), axis=1))
    flux = np.maximum(0, np.diff(np.log1p(spec * 10), axis=0)).sum(axis=1)
    flux = (flux - flux.mean()) / (flux.std() + 1e-9)
    ac = np.correlate(flux, flux, "full")[len(flux) - 1:]
    lags = np.arange(len(ac))
    bpm = 6000 / np.maximum(lags, 1)
    ok = (bpm >= 70) & (bpm <= 180)
    tempo = round(float(6000 / lags[ok][np.argmax(ac[ok])]), 1) if ok.any() else None
    onsets = peaks(flux, 1.5, 8) / 100.0
    rate = len(onsets) / (len(x) / sr)
    near = [float(np.min(np.abs(onsets - t))) for t in burst_times] if len(onsets) else []
    hit = round(float(np.mean(np.array(near) <= 0.1)), 2) if near else None
    return {"level_dbfs": round(level, 1), "tempo_bpm_rough": tempo, "onsets_per_s": round(rate, 2),
            "bursts_on_onset": hit, "chance_on_onset": round(1 - math.exp(-rate * 0.2), 2)}


def sheets(path: str, crop: str, aspect: str, dur: float, fps: float, out: Path, stem: str) -> list[str]:
    tw, cols = {"9:16": (176, 9), "4:5": (220, 7), "1:1": (240, 7), "16:9": (320, 5)}.get(aspect, (320, 5))
    per = cols * (6 if aspect in ("9:16", "4:5") else 9)
    total = max(1, math.ceil(dur * fps))
    files = []
    for part, start in enumerate(range(0, total, per)):
        count = min(per, total - start)
        rows = math.ceil(count / cols)
        name = out / (f"{stem}_sheet.jpg" if part == 0 else f"{stem}_sheet{part + 1}.jpg")
        vf = (f"fps={fps},select='gte(n\\,{start})',crop={crop},scale={tw}:-2,"
              "drawtext=text='%{eif\\:t\\:d}.%{eif\\:(t-trunc(t))*10\\:d}':x=4:y=4:fontsize=18:"
              f"fontcolor=yellow:box=1:boxcolor=black@0.7,tile={cols}x{rows}:padding=3:color=red")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vf", vf, "-frames:v", "1", "-q:v", "3", str(name)],
                       check=True)
        files.append(name.name)
    return files


def box_preview(path: str, dur: float, box: tuple, out: Path, stem: str) -> str:
    w, h, x, y, _ = box
    name = out / f"{stem}_box.jpg"
    vf = f"drawbox=x={x}:y={y}:w={w}:h={h}:color=red@0.9:t=8,scale=640:-2"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{dur * 0.5:.2f}", "-i", path, "-frames:v", "1",
                    "-vf", vf, "-q:v", "4", str(name)], check=True)
    return name.name


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("videos", nargs="+")
    ap.add_argument("--out", default="refs-breakdown")
    ap.add_argument("--fps", type=float, default=3.0, help="contact sheet frames per second (default 3)")
    ap.add_argument("--crop", help="force the content box W:H:X:Y for every video (pixels of the source)")
    ap.add_argument("--no-sheet", action="store_true")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    results = []
    for i, v in enumerate(a.videos, 1):
        stem = f"r{i:02d}"
        info = probe(v)
        if a.crop:
            cw, ch, cx, cy = (int(t) for t in a.crop.split(":"))
            r = cw / ch
            label = min(ASPECTS, key=lambda k: abs(ASPECTS[k] - r))
            box = (cw, ch, cx, cy, label)
        else:
            box = detect_box(v, info["w"], info["h"])
        crop = f"{box[0]}:{box[1]}:{box[2]}:{box[3]}"
        aspect = box[4] if box[4] != "full" else min(ASPECTS, key=lambda k: abs(ASPECTS[k] - info["w"] / info["h"]))
        m = motion_numbers(v, crop, aspect)
        au = audio_numbers(v, m["burst_times_s"]) if info["audio"] else {}
        res = {"id": stem, "file": os.path.basename(v), "source_size": f"{info['w']}x{info['h']}",
               "content_box": crop, "content_aspect": aspect, **m, "audio": au}
        res["box_preview"] = box_preview(v, info["dur"], box, out, stem)
        if not a.no_sheet:
            res["sheets"] = sheets(v, crop, aspect, info["dur"], a.fps, out, stem)
        results.append(res)
        print(f"{stem} {res['file'][:40]:40s} {aspect:>5} {m['duration_s']:5.1f}s cuts {len(m['cuts_s']):2d} "
              f"ASL {m['asl_s']:5.2f}s moves {m['burst_frames_median']} f, beat every {m['beat_spacing_s_median']} s")
    (out / "breakdown.json").write_text(json.dumps(results, indent=1))
    md = ["# Reference breakdown", "",
          "| id | file | aspect | length | hard cuts | ASL | move length (f@30, median) | beat spacing (s) | holds >= 0.4 s | moving | tempo (rough) | moves on a sound onset (chance) |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in results:
        au = r["audio"] or {}
        holds = r["holds_s"]
        md.append(f"| {r['id']} | {r['file'][:28]} | {r['content_aspect']} | {r['duration_s']} s | {len(r['cuts_s'])} | "
                  f"{r['asl_s']} s | {r['burst_frames_median']} ({r['burst_frames_p25']}-{r['burst_frames_p75']}) | "
                  f"{r['beat_spacing_s_median']} ({r['beat_spacing_s_p25']}-{r['beat_spacing_s_p75']}) | "
                  f"{len(holds)} (median {round(float(np.median(holds)), 2) if holds else '-'} s) | {int(r['moving_share'] * 100)}% | "
                  f"{au.get('tempo_bpm_rough', '-')} | {au.get('bursts_on_onset', '-')} ({au.get('chance_on_onset', '-')}) |")
    md += ["", "Cuts per video (s):", ""] + [f"- {r['id']}: {r['cuts_s']}" for r in results]
    md += ["", "Sheets: " + ", ".join(s for r in results for s in r.get("sheets", [])),
           "", "Check every *_box.jpg first. If a box is wrong, rerun that file with --crop W:H:X:Y."]
    (out / "breakdown.md").write_text("\n".join(md) + "\n")
    print(f"\nwrote {out}/breakdown.md, breakdown.json, sheets and box previews")


if __name__ == "__main__":
    sys.exit(main())
