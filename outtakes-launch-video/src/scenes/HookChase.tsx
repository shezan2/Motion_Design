import React from "react";
import { AbsoluteFill } from "remotion";
import { C, display, ui } from "../brand";
import { EASE, lerp, ramp, useF, useLayout } from "../anim";
import { Photo, Words } from "../components";
import T from "../timeline.json";

// Burst order: alternate night/day, wide/close, so each click reads as a new frame.
const BURST = [
  "tackle-night",
  "kids-duel",
  "point-orange",
  "sepak-takraw",
  "number-10",
  "motion-blur",
  "smile-orange",
  "basketball",
  "stretch-ball",
  "team-backs",
  "celebrate-fists",
  "heart-hands",
  "portrait-flare",
  "team-talk",
  "floodlight-profile",
  "tackle-night",
  "point-orange",
];
export const HERO = "celebrate-run";

// ---------------------------------------------------------------- HOOK
// Buys: "these are our photographers' shots" — burst mode, cut on every shutter click.
export const Hook: React.FC = () => {
  const f = useF();
  const { portrait } = useLayout();
  const h = T.hook;
  const landed = f >= h.land;

  let idx = -1;
  for (let i = 0; i < h.burst.length; i++) if (f >= h.burst[i]) idx = i;

  const start = landed ? h.land : h.burst[Math.max(0, idx)];
  const flash = f - start < 2 ? (f - start === 0 ? 0.35 : 0.12) : 0;

  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {idx >= 0 && !landed ? (
        <Photo name={BURST[idx]} scale={ramp(f, start, start + 8, [1.07, 1.0])} />
      ) : null}
      {landed ? (
        <>
          <Photo
            name={HERO}
            scale={ramp(f, h.land, h.land + 8, [1.14, 1.0], EASE.snap) * ramp(f, h.land + 8, h.to, [1, 1.05], EASE.linear)}
          />
          <AbsoluteFill
            style={{
              background: "linear-gradient(180deg, rgba(0,0,0,0) 45%, rgba(0,0,0,0.72) 100%)",
            }}
          />
          <AbsoluteFill
            style={{
              justifyContent: "flex-end",
              alignItems: "center",
              paddingBottom: portrait ? 300 : 120,
            }}
          >
            <Words
              text="YOU GOT THE SHOT."
              onsets={h.words}
              size={portrait ? 108 : 128}
              color={C.white}
              colors={{ 3: C.lime }}
              maxWidth={portrait ? 900 : 1700}
            />
          </AbsoluteFill>
        </>
      ) : null}
      {flash > 0 ? <AbsoluteFill style={{ background: "#fff", opacity: flash }} /> : null}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- CHASE
// Buys: "the work part sucks" — the shot becomes a sent photo, then the
// invoice follow-ups pile up unanswered. Performed, not captioned.
const MESSAGES = [
  "invoice for saturday's match",
  "just following up :)",
  "hello?",
  "hellooo??",
];

export const Chase: React.FC = () => {
  const f = useF();
  const { W, H, portrait } = useLayout();
  const c = T.chase;

  const cw = portrait ? 940 : 1160;
  const x0 = (W - cw) / 2;
  const font = portrait ? 56 : 58;
  const bubbleH = font * 1.22 + 2 * 28;
  const gap = 18;
  const imgW = cw * (portrait ? 0.8 : 0.62);
  const imgH = imgW / 1.5;
  const baseline = portrait ? H - 380 : H - 110;
  const seenH = 48;

  const p = c.bubbles.map((a) => ramp(f, a, a + 9, [0, 1], EASE.land));
  const pSeen = ramp(f, c.seen, c.seen + 8);

  // bottom edge of each message, pushed up by everything that arrived after it
  const stackAbove = (i: number) => {
    let off = pSeen * seenH;
    for (let j = i + 1; j < MESSAGES.length; j++) off += p[j] * (bubbleH + gap);
    return off;
  };
  const imgBottom = baseline - stackAbove(-1);

  // photo shrinks from full-bleed into the image bubble
  const s = ramp(f, c.shrink[0], c.shrink[1], [0, 1], EASE.inOut);
  const target = { x: x0 + cw - imgW, y: imgBottom - imgH, w: imgW, h: imgH };
  const rect = {
    x: lerp(0, target.x, s),
    y: lerp(0, target.y, s),
    w: lerp(W, target.w, s),
    h: lerp(H, target.h, s),
  };

  const dim = ramp(f, c.words[0] - 4, c.words[0] + 6, [0, 1]);

  return (
    <AbsoluteFill style={{ background: C.bg }}>
      {/* ground: the same shot, defocused, so the chat lives in the photographer's world */}
      <AbsoluteFill style={{ opacity: s * 0.9 }}>
        <Photo name={HERO} style={{ filter: "blur(36px) brightness(0.32) saturate(1.2)" }} scale={1.15} />
      </AbsoluteFill>

      <AbsoluteFill
        style={{
          opacity: 1 - dim * 0.72,
          scale: String(1 - dim * 0.06),
          filter: dim > 0 ? `blur(${dim * 6}px)` : undefined,
        }}
      >
        <div
          style={{
            position: "absolute",
            left: rect.x,
            top: rect.y,
            width: rect.w,
            height: rect.h,
            borderRadius: lerp(0, 30, s),
            overflow: "hidden",
          }}
        >
          <Photo name={HERO} />
        </div>

        {MESSAGES.map((m, i) => {
          if (f < c.bubbles[i]) return null;
          const bottom = baseline - stackAbove(i);
          return (
            <div
              key={i}
              style={{
                position: "absolute",
                right: x0,
                top: bottom - bubbleH,
                height: bubbleH,
                translate: `0px ${(1 - p[i]) * 50}px`,
                scale: String(0.9 + 0.1 * p[i]),
                transformOrigin: "100% 100%",
                ...ui,
                fontSize: font,
                lineHeight: 1.22,
                color: "#0d0d0f",
                background: C.lime,
                padding: `28px 38px`,
                borderRadius: `${bubbleH / 2}px ${bubbleH / 2}px 10px ${bubbleH / 2}px`,
                whiteSpace: "nowrap",
                boxSizing: "border-box",
              }}
            >
              {m}
            </div>
          );
        })}
        {f >= c.seen ? (
          <div
            style={{
              position: "absolute",
              right: x0 + 12,
              top: baseline - seenH + 12,
              ...ui,
              fontSize: portrait ? 30 : 30,
              color: C.muted,
              translate: `0px ${(1 - pSeen) * 16}px`,
            }}
          >
            Seen
          </div>
        ) : null}
      </AbsoluteFill>

      {f >= c.words[0] ? (
        <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
          <ChasingLine />
        </AbsoluteFill>
      ) : null}
    </AbsoluteFill>
  );
};

// "CHASING PAYMENTS." — then the second word flips to "BOOKINGS." (the other pain).
const ChasingLine: React.FC = () => {
  const f = useF();
  const { portrait } = useLayout();
  const c = T.chase;
  const size = portrait ? 116 : 124;
  const out = ramp(f, c.swap, c.swap + 7, [0, 1], EASE.leave);
  const inn = ramp(f, c.swap + 4, c.swap + 14, [1, 0], EASE.land);
  const word: React.CSSProperties = { ...display, fontSize: size, display: "inline-block", whiteSpace: "nowrap" };
  return (
    <div
      style={{
        display: "flex",
        flexDirection: portrait ? "column" : "row",
        alignItems: "center",
        gap: portrait ? size * 0.12 : size * 0.3,
      }}
    >
      <Words text="CHASING" onsets={[c.words[0]]} size={size} color={C.white} />
      <span style={{ position: "relative", overflow: "hidden", display: "inline-block", padding: "0.08em 0.04em", margin: "-0.08em -0.04em" }}>
        <span
          style={{
            ...word,
            color: C.lime,
            translate: `0px ${(ramp(f, c.words[1], c.words[1] + 10, [1, 0]) * 105 - out * 110).toFixed(2)}%`,
            visibility: f < c.words[1] ? "hidden" : "visible",
          }}
        >
          PAYMENTS.
        </span>
        <span
          style={{
            ...word,
            position: "absolute",
            left: "0.04em",
            top: "0.08em",
            color: C.lime,
            translate: `0px ${(inn * 105).toFixed(2)}%`,
            visibility: f < c.swap + 4 ? "hidden" : "visible",
          }}
        >
          BOOKINGS.
        </span>
      </span>
    </div>
  );
};
