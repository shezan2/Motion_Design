import { createContext, useContext } from "react";
import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

// One motion system for the whole film: land decelerates, leave accelerates.
export const EASE = {
  land: Easing.bezier(0.16, 1, 0.3, 1),
  snap: Easing.bezier(0.05, 0.7, 0.1, 1),
  leave: Easing.bezier(0.7, 0, 0.84, 0),
  inOut: Easing.bezier(0.65, 0, 0.35, 1),
  linear: Easing.linear,
};

export const ramp = (
  f: number,
  from: number,
  to: number,
  out: [number, number] = [0, 1],
  easing: (t: number) => number = EASE.land,
) =>
  interpolate(f, [from, to], out, {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing,
  });

export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

export const useLayout = () => {
  const { width: W, height: H, fps } = useVideoConfig();
  const portrait = H > W;
  return { W, H, fps, portrait, pad: portrait ? 80 : 120 };
};

// Deterministic pseudo-random in [0,1) for jitter that is identical every render.
export const hash = (n: number) => {
  const x = Math.sin(n * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};

// Scenes are mounted inside <Sequence>s, but every timing value in
// timeline.json is an absolute film frame. useF() returns the absolute frame.
export const FrameOffset = createContext(0);
export const useF = () => useCurrentFrame() + useContext(FrameOffset);
