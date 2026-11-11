import React, { CSSProperties } from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { C, display, ui, wordmark } from "./brand";
import { EASE, hash, ramp, useF } from "./anim";
import T from "./timeline.json";

// Focal points so landscape photos still frame the action in 9:16.
const FOCUS: Record<string, string> = {
  "celebrate-fists": "50% 35%",
  "kids-duel": "55% 50%",
  "sepak-takraw": "40% 40%",
  "celebrate-run": "44% 45%",
  basketball: "50% 40%",
  "smile-orange": "48% 40%",
  "point-orange": "45% 40%",
  "stretch-ball": "55% 50%",
  "heart-hands": "50% 40%",
  "number-10": "45% 50%",
  "team-backs": "50% 50%",
  "portrait-flare": "50% 35%",
  "tackle-night": "50% 50%",
  "floodlight-profile": "48% 35%",
  "motion-blur": "52% 50%",
  "team-talk": "60% 50%",
};

export const photoSrc = (name: string) => staticFile(`photos/${name}.jpg`);

export const Photo: React.FC<{
  name: string;
  style?: CSSProperties;
  scale?: number;
  pos?: string;
}> = ({ name, style, scale = 1, pos }) => (
  <Img
    src={photoSrc(name)}
    style={{
      position: "absolute",
      inset: 0,
      width: "100%",
      height: "100%",
      objectFit: "cover",
      objectPosition: pos ?? FOCUS[name] ?? "50% 50%",
      scale: String(scale),
      ...style,
    }}
  />
);

// Whole words unmasked from below on a speech-like cadence; no opacity fades.
export const Words: React.FC<{
  text: string;
  onsets: number[]; // absolute frames, one per word (last value repeats)
  size: number;
  color?: string;
  colors?: Record<number, string>;
  exitAt?: number;
  maxWidth?: number;
  align?: "center" | "left";
  lineHeight?: number;
  style?: CSSProperties;
  font?: CSSProperties;
}> = ({
  text,
  onsets,
  size,
  color = C.text,
  colors = {},
  exitAt,
  maxWidth,
  align = "center",
  lineHeight = 1.0,
  style,
  font = display,
}) => {
  const frame = useF();
  // "/" is a forced line break; onsets and colors index real words only.
  const tokens = text.split(" ");
  return (
    <div
      style={{
        display: "flex",
        flexWrap: "wrap",
        justifyContent: align === "center" ? "center" : "flex-start",
        columnGap: size * 0.28,
        rowGap: size * (lineHeight - 1) * 0.5,
        maxWidth,
        ...style,
      }}
    >
      {tokens.map((w, ti) => {
        if (w === "/") return <div key={`br${ti}`} style={{ flexBasis: "100%", height: 0 }} />;
        const i = tokens.slice(0, ti).filter((t) => t !== "/").length;
        const on = onsets[Math.min(i, onsets.length - 1)];
        const enter = ramp(frame, on, on + 10, [1, 0], EASE.land);
        const leave = exitAt === undefined ? 0 : ramp(frame, exitAt + i, exitAt + i + 7, [0, 1], EASE.leave);
        return (
          <span
            key={ti}
            style={{
              display: "inline-block",
              overflow: "hidden",
              padding: `${size * 0.08}px ${size * 0.04}px`,
              margin: `${-size * 0.08}px ${-size * 0.04}px`,
            }}
          >
            <span
              style={{
                ...font,
                display: "inline-block",
                fontSize: size,
                lineHeight,
                color: colors[i] ?? color,
                translate: `0px ${(enter * 105 - leave * 110).toFixed(2)}%`,
                visibility: frame < on ? "hidden" : "visible",
                whiteSpace: "nowrap",
              }}
            >
              {w}
            </span>
          </span>
        );
      })}
    </div>
  );
};

export const Wordmark: React.FC<{ size: number; color?: string; style?: CSSProperties }> = ({
  size,
  color = C.lime,
  style,
}) => <span style={{ ...wordmark, fontSize: size, color, whiteSpace: "nowrap", ...style }}>OUTTAKES</span>;

// Focal-plane shutter between scenes (curtain sweeps down) or a one-frame flash.
export const Shutter: React.FC = () => {
  const frame = useF();
  let top = 0;
  let bottom = 0;
  let flash = 0;
  for (const c of T.cuts) {
    if (c.kind === "curtain" && frame >= c.f - 3 && frame < c.f + 4) {
      if (frame < c.f) {
        top = 0;
        bottom = ramp(frame, c.f - 3, c.f, [0, 100], EASE.inOut);
      } else {
        top = ramp(frame, c.f, c.f + 4, [0, 100], EASE.land);
        bottom = 100;
      }
    }
    if (c.kind === "flash" && frame >= c.f && frame < c.f + 3) {
      flash = [0.55, 0.22, 0.06][frame - c.f];
    }
  }
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {bottom > top ? (
        <div
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            top: `${top}%`,
            height: `${bottom - top}%`,
            background: "#000",
          }}
        />
      ) : null}
      {flash > 0 ? <AbsoluteFill style={{ background: "#fff", opacity: flash }} /> : null}
    </AbsoluteFill>
  );
};

// Film grain + vignette: the world has texture, never a flat swatch.
export const Grain: React.FC<{ opacity?: number }> = ({ opacity = 0.1 }) => {
  const frame = useF();
  const x = Math.floor(hash(frame) * 512);
  const y = Math.floor(hash(frame + 99) * 512);
  const tiles = [0, 1, 2, 3, 4];
  return (
    <AbsoluteFill style={{ pointerEvents: "none", overflow: "hidden" }}>
      <AbsoluteFill style={{ mixBlendMode: "overlay", opacity, translate: `${-x}px ${-y}px` }}>
        {tiles.flatMap((r) =>
          tiles.map((c) => (
            <Img
              key={`${r}-${c}`}
              src={staticFile("noise.png")}
              style={{ position: "absolute", left: c * 512, top: r * 512, width: 512, height: 512 }}
            />
          )),
        )}
      </AbsoluteFill>
      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.45) 100%)",
        }}
      />
    </AbsoluteFill>
  );
};

export const ArrowIcon: React.FC<{ size: number; color?: string }> = ({ size, color = "#000" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <path d="M5 12h14M13 6l6 6-6 6" stroke={color} strokeWidth={2.2} strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

export const SearchIcon: React.FC<{ size: number; color?: string }> = ({ size, color = "#fff" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <circle cx="10.5" cy="10.5" r="6.5" stroke={color} strokeWidth={2.2} />
    <path d="M15.5 15.5L21 21" stroke={color} strokeWidth={2.2} strokeLinecap="round" />
  </svg>
);

export const MenuIcon: React.FC<{ size: number; color?: string }> = ({ size, color = "#fff" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <path d="M4 7h16M4 12h16M4 17h16" stroke={color} strokeWidth={2} strokeLinecap="round" />
  </svg>
);

export const BallIcon: React.FC<{ size: number; color?: string }> = ({ size, color = "#000" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <circle cx="12" cy="12" r="9" stroke={color} strokeWidth={1.8} />
    <path d="M12 7.5l3.6 2.6-1.4 4.2H9.8L8.4 10.1z" stroke={color} strokeWidth={1.6} strokeLinejoin="round" />
    <path d="M12 3v4.5M15.6 10.1l4.9-1.3M14.2 14.3l2.8 4.4M9.8 14.3L7 18.7M8.4 10.1L3.5 8.8" stroke={color} strokeWidth={1.4} />
  </svg>
);

export const PhoneIcon: React.FC<{ size: number; color?: string; rotate?: number }> = ({
  size,
  color = "#000",
  rotate = 0,
}) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" style={{ rotate: `${rotate}deg` }}>
    <path
      d="M6.6 10.8a15.1 15.1 0 006.6 6.6l2.2-2.2a1 1 0 011-.25 11.4 11.4 0 003.6.57 1 1 0 011 1V20a1 1 0 01-1 1A17 17 0 013 4a1 1 0 011-1h3.5a1 1 0 011 1c0 1.25.2 2.45.57 3.57a1 1 0 01-.25 1L6.6 10.8z"
      fill={color}
    />
  </svg>
);

// Lime CTA pill + arrow circle, as in the Figma "cta button component".
export const CtaPill: React.FC<{ label: string; size: number; press?: number; style?: CSSProperties }> = ({
  label,
  size,
  press = 0,
  style,
}) => (
  <div style={{ display: "flex", alignItems: "center", gap: size * 0.18, scale: String(1 - press * 0.06), ...style }}>
    <div
      style={{
        ...ui,
        background: C.lime,
        color: "#0d0d0f",
        fontSize: size,
        fontWeight: 600,
        letterSpacing: "-0.01em",
        textTransform: "uppercase",
        padding: `${size * 0.62}px ${size * 1.2}px`,
        borderRadius: 999,
        whiteSpace: "nowrap",
      }}
    >
      {label}
    </div>
    <div
      style={{
        width: size * 2.24,
        height: size * 2.24,
        borderRadius: 999,
        background: C.lime,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <ArrowIcon size={size * 1.2} />
    </div>
  </div>
);

export const Chip: React.FC<{ label: string; size: number; active?: boolean; icon?: boolean }> = ({
  label,
  size,
  active = false,
  icon = true,
}) => (
  <div
    style={{
      ...ui,
      display: "flex",
      alignItems: "center",
      gap: size * 0.5,
      background: active ? C.white : C.surface,
      color: active ? "#0d0d0f" : C.text,
      fontSize: size,
      textTransform: "uppercase",
      letterSpacing: "-0.01em",
      padding: `${size * 0.62}px ${size * 1.3}px`,
      borderRadius: 999,
      whiteSpace: "nowrap",
    }}
  >
    {icon ? <BallIcon size={size * 1.25} color={active ? "#0d0d0f" : C.text} /> : null}
    {label}
  </div>
);

export const Cursor: React.FC<{ x: number; y: number; scale?: number; size?: number }> = ({
  x,
  y,
  scale = 1,
  size = 64,
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    style={{
      position: "absolute",
      left: x,
      top: y,
      scale: String(scale),
      transformOrigin: "4px 3px",
      filter: "drop-shadow(0 6px 14px rgba(0,0,0,0.5))",
    }}
  >
    <path d="M4 3l15 8.5-6.6 1.6L9.6 20z" fill="#fff" stroke="#000" strokeWidth={1.4} strokeLinejoin="round" />
  </svg>
);
