import { CSSProperties } from "react";
import { continueRender, delayRender, staticFile } from "remotion";

// Tokens sampled from the new Outtakes website/branding ("Outtakes Dark", Nov 2026).
export const C = {
  bg: "#111113",
  surface: "#23202a", // nav / panels
  black: "#000000",
  white: "#ffffff",
  ink: "#111113", // text on cream
  cream: "#f0ebe4",
  text: "rgba(255,255,255,0.92)",
  muted: "rgba(255,255,255,0.62)",
  green: "#74f260", // the one accent: buttons, "on", "you"
  violetDeep: "#2f2973",
  violet: "#5a55d3",
  sky: "#9bc3f4",
  tag: { track: "#ff9cb8", football: "#b9f5a3", rugby: "#ffda74", swimming: "#b5f2ff" },
};

// The site's signature gradient (footer / "Every sideline" section): night -> violet -> sky -> cream.
export const brandGradient = (dir = "180deg") =>
  `linear-gradient(${dir}, ${C.bg} 0%, #1c1a3a 22%, ${C.violetDeep} 38%, ${C.violet} 55%, #7f95f8 68%, ${C.sky} 80%, #cfe3ea 90%, ${C.cream} 100%)`;

// Fonts: Archivo (variable width + weight) for headlines and the wordmark,
// Archivo also sets body/UI text on the new site (Geist kept as a fallback). Loaded from /public so renders
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

// Body/UI text: the new site sets body copy in Archivo at normal width.
export const ui: CSSProperties = {
  fontFamily: "Archivo, sans-serif",
  fontWeight: 450,
  fontStretch: "100%",
  letterSpacing: "-0.015em",
};

// Section labels on the site: italic, uppercase, regular weight ("DISCOVER YOUR FRAME").
export const label: CSSProperties = {
  fontFamily: "Archivo, sans-serif",
  fontStyle: "italic",
  fontWeight: 400,
  fontStretch: "100%",
  textTransform: "uppercase",
  letterSpacing: "-0.02em",
};
