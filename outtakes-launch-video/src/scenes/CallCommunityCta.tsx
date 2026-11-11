import React from "react";
import { AbsoluteFill } from "remotion";
import { C, display, ui, wordmark } from "../brand";
import { EASE, hash, lerp, ramp, useF, useLayout } from "../anim";
import { CtaPill, Cursor, PhoneIcon, Photo, Words, Wordmark } from "../components";
import T from "../timeline.json";

// ---------------------------------------------------------------- CALL
// Buys: "and then your phone rings" — the payoff of being found (Figma:
// "Call the photographer and agree on the shoot").
export const Call: React.FC = () => {
  const f = useF();
  const { portrait } = useLayout();
  const k = T.call;
  const pIn = ramp(f, k.from, k.from + 12, [0, 1], EASE.land);
  // ring pattern: buzz 16f, rest 8f
  const ringing = f >= k.from + 8 && (f - k.from - 8) % 24 < 16;
  const shakeR = ringing ? (hash(f) - 0.5) * 3.2 : 0;
  const shakeX = ringing ? (hash(f + 7) - 0.5) * 10 : 0;
  const cardW = portrait ? 900 : 860;
  const btn = portrait ? 150 : 132;

  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <Photo name="motion-blur" scale={ramp(f, k.from, k.to, [1.12, 1.0], EASE.linear)} style={{ filter: "brightness(0.38) saturate(1.1)" }} />
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0.2), rgba(0,0,0,0.65))" }} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div
          style={{
            width: cardW,
            padding: portrait ? "80px 70px 90px" : "64px 70px 72px",
            boxSizing: "border-box",
            borderRadius: 56,
            background: "rgba(18,18,20,0.92)",
            border: "1.5px solid rgba(255,255,255,0.1)",
            boxShadow: "0 40px 120px rgba(0,0,0,0.6)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            translate: `${shakeX}px ${(1 - pIn) * 380}px`,
            rotate: `${shakeR}deg`,
            scale: String(lerp(1.18, 1, pIn)),
          }}
        >
          <div style={{ ...ui, fontSize: portrait ? 34 : 30, color: C.muted }}>Incoming call</div>
          <div style={{ ...display, fontSize: portrait ? 104 : 96, color: C.white, marginTop: 26 }}>NEW CLIENT</div>
          <div style={{ display: "flex", alignItems: "baseline", gap: 14, marginTop: 22 }}>
            <span style={{ ...ui, fontSize: portrait ? 40 : 36, color: C.text }}>found you on</span>
            <Wordmark size={portrait ? 58 : 52} />
          </div>
          <div style={{ display: "flex", gap: portrait ? 200 : 180, marginTop: portrait ? 90 : 64, position: "relative" }}>
            <div style={{ width: btn, height: btn, borderRadius: 999, background: "#ff453a", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <PhoneIcon size={btn * 0.46} color="#fff" rotate={135} />
            </div>
            <div style={{ position: "relative", width: btn, height: btn }}>
              {[0, 1, 2].map((i) => {
                const t = ((f - k.from + i * 10) % 30) / 30;
                return (
                  <div
                    key={i}
                    style={{
                      position: "absolute",
                      inset: 0,
                      borderRadius: 999,
                      border: `3px solid ${C.lime}`,
                      scale: String(1 + t * 0.9),
                      opacity: (1 - t) * 0.6 * pIn,
                    }}
                  />
                );
              })}
              <div style={{ position: "absolute", inset: 0, borderRadius: 999, background: C.lime, display: "flex", alignItems: "center", justifyContent: "center" }}>
                <PhoneIcon size={btn * 0.46} color="#0d0d0f" />
              </div>
            </div>
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- COMMUNITY
// Buys: "you join a crew, not a marketplace" — Figma About copy, one word per cut.
const COMMUNITY = [
  { photo: "team-talk", word: "CAMARADERIE", from: 810, to: 840 },
  { photo: "team-backs", word: null, from: 825, to: 840 },
  { photo: "heart-hands", word: "OVER", from: 840, to: 855 },
  { photo: "number-10", word: "RIVALRY.", from: 855, to: 870 },
];

export const Community: React.FC = () => {
  const f = useF();
  const { W, portrait } = useLayout();
  const m = T.community;
  if (f >= m.sotw) return <ShotOfTheWeek />;

  let shot = COMMUNITY[0];
  for (const c of COMMUNITY) if (f >= c.from) shot = c;
  const word = COMMUNITY.filter((c) => c.word && f >= c.from && f < c.to).pop();
  const size = portrait ? 104 : 176;

  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <Photo name={shot.photo} scale={ramp(f, shot.from, shot.from + 15, [1.1, 1.02], EASE.land)} />
      <AbsoluteFill style={{ background: "rgba(0,0,0,0.38)" }} />
      {word ? (
        <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
          <Words
            key={word.word}
            text={word.word as string}
            onsets={[word.from + 2]}
            size={word.word === "CAMARADERIE" && portrait ? Math.min(size, (W - 200) / 8.6) : size}
            color={word.word === "RIVALRY." ? C.lime : C.white}
          />
        </AbsoluteFill>
      ) : null}
    </AbsoluteFill>
  );
};

// Buys: "your best frame gets the spotlight" (Figma: Shot of the week + nominees).
const ShotOfTheWeek: React.FC = () => {
  const f = useF();
  const { portrait } = useLayout();
  const s = T.community.sotw;
  const pIn = ramp(f, s, s + 14, [0, 1], EASE.land);
  const photo = portrait ? { w: 720, h: 900 } : { w: 600, h: 750 };
  const thumbs = ["point-orange", "kids-duel", "stretch-ball"];

  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse 70% 60% at 35% 50%, rgba(87,113,39,0.45) 0%, rgba(25,66,42,0.25) 40%, rgba(13,13,15,0) 75%)",
        }}
      />
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
          flexDirection: portrait ? "column" : "row",
          gap: portrait ? 70 : 100,
        }}
      >
        <div
          style={{
            position: "relative",
            width: photo.w,
            height: photo.h,
            borderRadius: 28,
            overflow: "hidden",
            scale: String(lerp(1.25, 1, pIn)),
            rotate: `${lerp(-4, 0, pIn)}deg`,
            boxShadow: "0 40px 120px rgba(0,0,0,0.55)",
          }}
        >
          <Photo name="portrait-flare" scale={ramp(f, s, s + 60, [1.08, 1.0], EASE.linear)} />
        </div>
        <div style={{ display: "flex", flexDirection: "column", alignItems: portrait ? "center" : "flex-start", gap: 34 }}>
          <Words
            text="SHOT OF THE WEEK"
            onsets={[s + 4, s + 8, s + 11, s + 15]}
            size={portrait ? 96 : 96}
            color={C.white}
            colors={{ 3: C.lime }}
            maxWidth={portrait ? 900 : 640}
            align={portrait ? "center" : "left"}
          />
          <div style={{ display: "flex", flexDirection: "column", gap: 18, alignItems: portrait ? "center" : "flex-start" }}>
            <div
              style={{
                ...ui,
                fontSize: portrait ? 32 : 28,
                color: C.muted,
                textTransform: "uppercase",
                opacity: ramp(f, s + 18, s + 21),
              }}
            >
              Nominees this week
            </div>
            <div style={{ display: "flex", gap: 18 }}>
              {thumbs.map((t, i) => (
                <div
                  key={t}
                  style={{
                    width: portrait ? 170 : 150,
                    height: portrait ? 212 : 188,
                    borderRadius: 16,
                    overflow: "hidden",
                    position: "relative",
                    translate: `0px ${ramp(f, s + 20 + i * 3, s + 32 + i * 3, [80, 0])}px`,
                    opacity: f >= s + 20 + i * 3 ? 1 : 0,
                  }}
                >
                  <Photo name={t} />
                </div>
              ))}
            </div>
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- CTA
// Buys: "it's free, here's when, here's where".
export const Cta: React.FC = () => {
  const f = useF();
  const { W, H, portrait } = useLayout();
  const c = T.cta;
  const copy = T.copy;
  const breathe = 0.5 + 0.5 * Math.sin(f / 18);

  const ground = (
    <>
      <AbsoluteFill style={{ background: C.bg }} />
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse 90% 55% at 50% 105%, rgba(216,238,72,${0.16 + breathe * 0.05}) 0%, rgba(87,113,39,0.28) 35%, rgba(13,13,15,0) 72%)`,
        }}
      />
    </>
  );

  if (f >= c.final) return <Final />;

  // "20.11" crash, then shrinks up to make room for the button
  const dateIn = f >= c.crash;
  const dateSc = ramp(f, c.crash, c.crash + 14, [3.2, 1], EASE.snap) * ramp(f, c.crash + 14, c.pill, [1, 0.96], EASE.linear);
  const up = ramp(f, c.pill - 4, c.pill + 10, [0, 1], EASE.inOut);
  const decay = ramp(f, c.crash, c.crash + 6, [1, 0]);
  const dateSize = portrait ? 270 : 330;

  const pillY = portrait ? H * 0.62 : H * 0.66;
  const pillSize = portrait ? 40 : 46;
  const pillW = pillSize * 0.62 * 26; // rough width of the label pill + arrow, for cursor parking
  const cIn = ramp(f, c.pill + 6, c.press - 6, [0, 1], EASE.land);
  const curX = lerp(W * 0.95, W / 2 + pillW * 0.18, cIn);
  const curY = lerp(H * 1.15, pillY + pillSize * 1.2, cIn);
  const pressed = f >= c.press && f < c.press + 4;

  return (
    <AbsoluteFill>
      {ground}
      {f < c.profiles ? (
        <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
          <Words
            text="SIGN UP FREE."
            onsets={[c.free, c.free + 5, c.free + 11]}
            exitAt={c.profiles - 8}
            size={portrait ? 150 : 200}
            color={C.white}
            colors={{ 2: C.lime }}
            maxWidth={portrait ? 920 : 1800}
          />
        </AbsoluteFill>
      ) : null}
      {f >= c.profiles && f < c.riser[1] ? (
        <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
          <Words
            text={portrait ? `SET UP YOUR / PROFILE FROM / ${copy.profilesOpen}.` : `SET UP YOUR PROFILE / FROM ${copy.profilesOpen}.`}
            onsets={[c.profiles, c.profiles + 4, c.profiles + 8, c.profiles + 12, c.profiles + 18, c.profiles + 23, c.profiles + 27]}
            exitAt={c.riser[0]}
            size={portrait ? 96 : 104}
            color={C.white}
            colors={{ 5: C.lime, 6: C.lime }}
            maxWidth={portrait ? 900 : 1500}
            lineHeight={1.02}
          />
        </AbsoluteFill>
      ) : null}
      {dateIn ? (
        <>
          {[4, 3, 2, 1].map((k) =>
            decay > 0.01 ? (
              <div key={k} style={dateStyle(W, H, dateSize, dateSc * (1 + k * 0.14 * decay), 0.2 * decay, 0)}>
                {copy.liveDate}
              </div>
            ) : null,
          )}
          <div
            style={{
              ...dateStyle(W, H, dateSize, dateSc * lerp(1, portrait ? 0.62 : 0.5, up), 1, lerp(0, portrait ? -H * 0.17 : -H * 0.2, up)),
              textShadow: `0 0 ${50 + decay * 80}px rgba(216,238,72,${0.2 + decay * 0.4})`,
            }}
          >
            {copy.liveDate}
          </div>
          <div
            style={{
              position: "absolute",
              left: 0,
              right: 0,
              top: H / 2 + dateSize * 0.5 + lerp(0, portrait ? -H * 0.17 - dateSize * 0.2 : -H * 0.2 - dateSize * 0.26, up),
              display: "flex",
              justifyContent: "center",
            }}
          >
            <Words
              text={`WE GO LIVE · ${copy.liveTime}`}
              onsets={[c.crash + 8, c.crash + 12, c.crash + 16, c.crash + 20, c.crash + 24]}
              size={portrait ? 60 : 64}
              color={C.white}
              colors={{ 3: C.lime, 4: C.lime }}
              maxWidth={portrait ? 900 : 1600}
            />
          </div>
        </>
      ) : null}
      {f >= c.pill ? (
        <div
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            top: pillY,
            display: "flex",
            justifyContent: "center",
            translate: `0px ${ramp(f, c.pill, c.pill + 12, [80, 0])}px`,
            opacity: ramp(f, c.pill, c.pill + 3),
          }}
        >
          <CtaPill label={`Sign up free · ${copy.url.toLowerCase()}`} size={pillSize} press={pressed ? 1 : 0} />
        </div>
      ) : null}
      {f >= c.pill + 6 ? <Cursor x={curX} y={curY} scale={lerp(3, 1, cIn) * (pressed ? 0.82 : 1)} size={portrait ? 76 : 64} /> : null}
    </AbsoluteFill>
  );
};

const dateStyle = (W: number, H: number, size: number, scale: number, opacity: number, dy: number): React.CSSProperties => ({
  ...display,
  position: "absolute",
  left: W / 2,
  top: H / 2 + dy,
  translate: "-50% -60%",
  fontSize: size,
  fontWeight: 900,
  color: C.lime,
  scale: String(scale),
  opacity,
  whiteSpace: "nowrap",
});

// End: the name, the address, the date. Contracts the whole hold, then the shutter closes.
const Final: React.FC = () => {
  const f = useF();
  const { portrait } = useLayout();
  const c = T.cta;
  const sc = ramp(f, c.final, c.final + 10, [1.12, 1], EASE.land) * ramp(f, c.final + 10, c.to, [1, 0.95], EASE.linear);
  const close = ramp(f, c.to - 6, c.to - 1, [0, 100], EASE.inOut);
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse 60% 45% at 50% 50%, rgba(25,66,42,0.55) 0%, rgba(13,13,15,0) 70%)",
        }}
      />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", gap: portrait ? 34 : 30, scale: String(sc) }}>
        <span style={{ ...wordmark, fontSize: portrait ? 230 : 250, color: C.lime }}>OUTTAKES</span>
        <span style={{ ...ui, fontSize: portrait ? 44 : 40, color: C.white, letterSpacing: "0.01em" }}>
          {T.copy.url.toLowerCase()} · {T.copy.liveDate} · {T.copy.liveTime}
        </span>
      </AbsoluteFill>
      {close > 0 ? <div style={{ position: "absolute", left: 0, right: 0, top: 0, height: `${close}%`, background: "#000" }} /> : null}
    </AbsoluteFill>
  );
};
