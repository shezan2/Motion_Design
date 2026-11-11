import { CSSProperties } from "react";
import { continueRender, delayRender, staticFile } from "remotion";

// Tokens pulled from the Outtakes Figma design system (node 1283:73).
export const C = {
  bg: "#0d0d0f",
  surface: "#222222",
  black: "#000000",
  white: "#ffffff",
  text: "rgba(255,255,255,0.9)",
  muted: "rgba(255,255,255,0.62)",
  lime: "#d8ee48",
  limeLight: "#ecffb7",
  olive: "#577127",
  oliveInk: "#405904",
  forest: "#19422a",
};

// Fonts: Archivo (variable width + weight) for headlines and the wordmark,
// Geist for UI text, matching the Figma file. Loaded from /public so renders
// never depend on a font CDN.
const fontHandle = delayRender("Loading brand fonts");
const faces = [
  new FontFace("Archivo", `url(${staticFile("fonts/archivo.woff2")}) format('woff2')`, {
    weight: "100 900",
    stretch: "62% 125%",
    style: "normal",
  }),
  new FontFace("Archivo", `url(${staticFile("fonts/archivo-italic.woff2")}) format('woff2')`, {
    weight: "100 900",
    stretch: "62% 125%",
    style: "italic",
  }),
  new FontFace("Geist", `url(${staticFile("fonts/geist.woff2")}) format('woff2')`, {
    weight: "100 900",
  }),
];
Promise.all(faces.map((f) => f.load()))
  .then((loaded) => {
    loaded.forEach((f) => document.fonts.add(f));
    continueRender(fontHandle);
  })
  .catch((err) => {
    console.error(err);
    continueRender(fontHandle);
  });

export const display: CSSProperties = {
  fontFamily: "Archivo, sans-serif",
  fontWeight: 800,
  fontStretch: "125%",
  textTransform: "uppercase",
  letterSpacing: "-0.02em",
  lineHeight: 0.98,
};

export const wordmark: CSSProperties = {
  fontFamily: "Archivo, sans-serif",
  fontStyle: "italic",
  fontWeight: 900,
  fontStretch: "62%",
  textTransform: "uppercase",
  letterSpacing: "-0.01em",
  lineHeight: 1,
};

export const ui: CSSProperties = {
  fontFamily: "Geist, sans-serif",
  fontWeight: 500,
  letterSpacing: "-0.02em",
};
