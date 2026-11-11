import React from "react";
import { AbsoluteFill } from "remotion";
import { C, ui, wordmark } from "../brand";
import { EASE, hash, lerp, ramp, useF, useLayout } from "../anim";
import { Chip, CtaPill, Cursor, MenuIcon, Photo, SearchIcon, Words } from "../components";
import T from "../timeline.json";

// Shared geometry so the wordmark in Reveal and the docking wordmark in UI line up.
const useRevealGeo = () => {
  const { W, H, portrait } = useLayout();
  const size = portrait ? 236 : 360;
  return { cx: W / 2, cy: H * (portrait ? 0.44 : 0.42), size, tagTop: H * (portrait ? 0.44 : 0.42) + size * 0.55, W, H, portrait };
};

const crashScale = (f: number, at: number, end: number) =>
  ramp(f, at, at + 14, [3.5, 1], EASE.snap) * ramp(f, at + 14, end, [1, 0.94], EASE.linear);

// ---------------------------------------------------------------- REVEAL
// Buys: "there is now a place built for this" — the name lands on the hit after silence.
export const Reveal: React.FC = () => {
  const f = useF();
  const g = useRevealGeo();
  const r = T.reveal;
  if (f < r.crash) return <AbsoluteFill style={{ background: "#000" }} />;
  const sc = crashScale(f, r.crash, r.to);
  const decay = ramp(f, r.crash, r.crash + 6, [1, 0], EASE.land);
  const glow = 0.18 + decay * 0.5;
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse 60% 45% at 50% ${(g.cy / g.H) * 100}%, rgba(216,238,72,${0.1 + decay * 0.2}) 0%, rgba(25,66,42,0.25) 45%, rgba(13,13,15,0) 75%)`,
        }}
      />
      {[5, 4, 3, 2, 1].map((k) =>
        decay > 0.01 ? (
          <div key={k} style={streakStyle(g.cx, g.cy, g.size, sc * (1 + k * 0.16 * decay), 0.2 * decay)}>
            OUTTAKES
          </div>
        ) : null,
      )}
      <div
        style={{
          ...streakStyle(g.cx, g.cy, g.size, sc, 1),
          textShadow: `0 0 ${60 + decay * 80}px rgba(216,238,72,${glow})`,
        }}
      >
        OUTTAKES
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: g.tagTop, display: "flex", justifyContent: "center" }}>
        <Words
          text="MADE BY PHOTOGRAPHERS, / FOR PHOTOGRAPHERS."
          onsets={r.words}
          size={g.portrait ? 54 : 58}
          color={C.white}
          maxWidth={g.portrait ? 1000 : 1500}
        />
      </div>
    </AbsoluteFill>
  );
};

const streakStyle = (cx: number, cy: number, size: number, scale: number, opacity: number): React.CSSProperties => ({
  ...wordmark,
  position: "absolute",
  left: cx,
  top: cy,
  translate: "-50% -50%",
  fontSize: size,
  color: C.lime,
  scale: String(scale),
  opacity,
  whiteSpace: "nowrap",
});

// ---------------------------------------------------------------- UI
// Buys: "clients will actually find you" — the wordmark docks into the site's
// nav, a client searches, your profile is in the results, they open it.
const CARDS_L = [
  { photo: "celebrate-fists", label: "Football · Matchday" },
  { photo: "basketball", label: "Basketball · Action" },
  { photo: "floodlight-profile", label: "You", you: true },
  { photo: "sepak-takraw", label: "Sepak takraw" },
];
const CARDS_P = [
  { photo: "celebrate-fists", label: "Football · Matchday" },
  { photo: "floodlight-profile", label: "You", you: true },
  { photo: "basketball", label: "Basketball · Action" },
  { photo: "sepak-takraw", label: "Sepak takraw" },
];
const QUERY = "football photographer";
// irregular keystroke gaps (frames) for the client's typing
const KEY_GAPS = [0, 2, 2, 1, 2, 3, 1, 2, 2, 4, 2, 1, 2, 2, 1, 3, 2, 1, 2, 2, 1];

const useUiGeo = () => {
  const { W, H, portrait } = useLayout();
  if (portrait) {
    const cardW = 440;
    const cardH = 540;
    const x0 = 80;
    const y0 = 470;
    const cards = [0, 1, 2, 3].map((i) => ({
      x: x0 + (i % 2) * (cardW + 40),
      y: y0 + Math.floor(i / 2) * (cardH + 110),
      w: cardW,
      h: cardH,
    }));
    return {
      W, H, portrait,
      nav: { cx: W / 2, cy: 130, w: 760, h: 104, font: 70 },
      head: { top: 420, size: 92, maxW: 920 },
      search: { cx: W / 2, y: 980, w: 920, h: 120, font: 46, yUp: 220 },
      chipsY: 350,
      cards,
      cardLabel: 34,
    };
  }
  const cardW = 400;
  const cardH = 470;
  const x0 = (W - (4 * cardW + 3 * 40)) / 2;
  const cards = [0, 1, 2, 3].map((i) => ({ x: x0 + i * (cardW + 40), y: 360, w: cardW, h: cardH }));
  return {
    W, H, portrait,
    nav: { cx: W / 2, cy: 76, w: 660, h: 84, font: 58 },
    head: { top: 210, size: 104, maxW: 1560 },
    search: { cx: W / 2, y: 560, w: 1040, h: 116, font: 44, yUp: 168 },
    chipsY: 280,
    cards,
    cardLabel: 30,
  };
};

export const UI: React.FC = () => {
  const f = useF();
  const g = useUiGeo();
  const rg = useRevealGeo();
  const u = T.ui;
  const cards = g.portrait ? CARDS_P : CARDS_L;
  const youIdx = cards.findIndex((c) => "you" in c && c.you);
  const you = g.cards[youIdx];

  // dock: wordmark travels from the reveal position into the nav pill
  const d = ramp(f, u.dock[0], u.dock[1], [0, 1], EASE.inOut);
  const wmSize = lerp(rg.size * 0.94, g.nav.font, d);
  const wmX = lerp(rg.cx, g.nav.cx - g.nav.w / 2 + 44, d);
  const wmY = lerp(rg.cy, g.nav.cy, d);
  const pillGrow = ramp(f, u.dock[0] + 12, u.dock[1] + 6, [0, 1], EASE.land);
  const sideIn = ramp(f, u.dock[0] + 10, u.dock[1] + 10, [1, 0], EASE.land);

  // results phase
  const res = ramp(f, u.enter, u.enter + 14, [0, 1], EASE.inOut);
  const searchY = lerp(g.search.y, g.search.yUp, res);

  // typing
  let typed = 0;
  let t = u.typeStart;
  for (let i = 0; i < QUERY.length; i++) {
    t += KEY_GAPS[i % KEY_GAPS.length];
    if (f >= t) typed = i + 1;
  }
  const caretOn = Math.floor(f / 8) % 2 === 0 || (f >= u.typeStart && f < u.enter);

  // cursor: enters oversize, decelerates, parks on your card, presses
  const cx = you.x + you.w * 0.58;
  const cy = you.y + you.h * 0.52;
  const cIn = ramp(f, u.cursorIn, u.cardPress - 8, [0, 1], EASE.land);
  const curX = lerp(g.W * 0.92, cx, cIn);
  const curY = lerp(g.H * 1.1, cy, cIn);
  const curScale = lerp(3, 1, cIn) * (f >= u.cardPress && f < u.cardPress + 4 ? 0.82 : 1);
  const pressed = f >= u.cardPress + 1;

  // camera push into your card, then hard cut to the profile
  const push = ramp(f, u.push[0], u.push[1], [0, 1], EASE.leave);
  const drift = ramp(f, u.dock[1], u.push[0], [1, 1.035], EASE.linear);
  const camScale = lerp(1, 2.6, push) * drift;
  const focusX = you.x + you.w / 2;
  const focusY = you.y + you.h / 2;

  if (f >= u.profile) return <Profile />;

  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse 80% 55% at 50% 0%, rgba(25,66,42,0.55) 0%, rgba(13,13,15,0) 70%)",
        }}
      />
      {/* tagline from the reveal, leaving */}
      {f < u.dock[0] + 14 ? (
        <div style={{ position: "absolute", left: 0, right: 0, top: rg.tagTop, display: "flex", justifyContent: "center" }}>
          <Words
            text="MADE BY PHOTOGRAPHERS, / FOR PHOTOGRAPHERS."
            onsets={[-100]}
            exitAt={u.dock[0]}
            size={rg.portrait ? 54 : 58}
            color={C.white}
            maxWidth={rg.portrait ? 1000 : 1500}
          />
        </div>
      ) : null}

      <AbsoluteFill
        style={{
          scale: String(camScale),
          transformOrigin: `${focusX}px ${focusY}px`,
          translate: `${(g.W / 2 - focusX) * push}px ${(g.H / 2 - focusY) * push}px`,
        }}
      >
        {/* nav pill */}
        <div
          style={{
            position: "absolute",
            left: g.nav.cx - (g.nav.w / 2) * pillGrow - 0,
            top: g.nav.cy - g.nav.h / 2,
            width: g.nav.w * pillGrow,
            height: g.nav.h,
            borderRadius: 999,
            background: "#000",
            border: "1.5px solid rgba(255,255,255,0.08)",
            overflow: "hidden",
            opacity: pillGrow > 0.02 ? 1 : 0,
          }}
        >
          <div style={{ position: "absolute", right: 34, top: (g.nav.h - g.nav.font * 0.6) / 2, opacity: pillGrow }}>
            <MenuIcon size={g.nav.font * 0.6} />
          </div>
        </div>
        <div
          style={{
            ...wordmark,
            position: "absolute",
            left: wmX,
            top: wmY,
            translate: `${lerp(-50, 0, d)}% -50%`,
            fontSize: wmSize,
            color: lerpColor(d),
            whiteSpace: "nowrap",
          }}
        >
          OUTTAKES
        </div>

        {/* side pills (landscape), as in the Figma header */}
        {!g.portrait ? (
          <>
            <div style={{ position: "absolute", left: 120 - sideIn * 500, top: g.nav.cy - 34 }}>
              <CtaPill label="Find a photographer" size={22} />
            </div>
            <div
              style={{
                position: "absolute",
                right: 120 - sideIn * 500,
                top: g.nav.cy - 34,
                height: 68,
                padding: "0 44px",
                borderRadius: 999,
                background: C.surface,
                display: "flex",
                alignItems: "center",
                gap: 16,
                ...ui,
                fontSize: 22,
                color: C.text,
                textTransform: "uppercase",
              }}
            >
              <SearchIcon size={26} />
              Search
            </div>
          </>
        ) : null}

        {/* hero headline (Figma photographer CTA copy) */}
        {f < u.enter + 12 ? (
          <div style={{ position: "absolute", left: 0, right: 0, top: g.head.top, display: "flex", justifyContent: "center" }}>
            <Words
              text={g.portrait ? "GET FOUND BY THOSE WHO ACTUALLY NEED YOU." : "GET FOUND BY THOSE / WHO ACTUALLY NEED YOU."}
              onsets={u.words}
              exitAt={u.enter - 2}
              size={g.head.size}
              color={C.white}
              colors={{ 7: C.lime }}
              maxWidth={g.head.maxW}
              lineHeight={1.02}
            />
          </div>
        ) : null}

        {/* search field: the client's own input, so letter typing is allowed here */}
        {f >= u.words[3] ? (
          <div
            style={{
              position: "absolute",
              left: g.search.cx - g.search.w / 2,
              top: searchY,
              width: g.search.w,
              height: g.search.h,
              borderRadius: 999,
              background: "#161618",
              border: `2px solid ${f >= u.enter && f < u.enter + 6 ? C.lime : "rgba(255,255,255,0.14)"}`,
              display: "flex",
              alignItems: "center",
              gap: 26,
              padding: "0 48px",
              boxSizing: "border-box",
              translate: `0px ${ramp(f, u.words[3], u.words[3] + 12, [60, 0])}px`,
              opacity: ramp(f, u.words[3], u.words[3] + 4),
              scale: String(lerp(1, g.portrait ? 1 : 0.86, res)),
            }}
          >
            <SearchIcon size={g.search.font * 0.95} />
            <span style={{ ...ui, fontSize: g.search.font, color: typed ? C.white : C.muted, whiteSpace: "nowrap" }}>
              {typed ? QUERY.slice(0, typed) : "Search photographers"}
              <span style={{ opacity: caretOn && typed ? 1 : 0, color: C.lime }}>|</span>
            </span>
          </div>
        ) : null}

        {/* results */}
        {f >= u.enter ? (
          <>
            <div
              style={{
                position: "absolute",
                left: 0,
                right: 0,
                top: g.chipsY,
                display: "flex",
                justifyContent: "center",
                gap: 18,
              }}
            >
              {(g.portrait ? ["Football", "Basketball", "Rugby"] : ["Football", "Basketball", "Rugby", "Track"]).map((lab, i) => (
                <div
                  key={lab}
                  style={{
                    translate: `0px ${ramp(f, u.enter + 6 + i * 2, u.enter + 18 + i * 2, [40, 0])}px`,
                    opacity: ramp(f, u.enter + 6 + i * 2, u.enter + 9 + i * 2),
                  }}
                >
                  <Chip label={lab} size={g.portrait ? 26 : 22} active={i === 0} />
                </div>
              ))}
            </div>
            {cards.map((card, i) => {
              const r = g.cards[i];
              const a = u.enter + 10 + i * 3;
              const pIn = ramp(f, a, a + 12, [0, 1], EASE.land);
              const isYou = i === youIdx;
              return (
                <div
                  key={i}
                  style={{
                    position: "absolute",
                    left: r.x,
                    top: r.y,
                    width: r.w,
                    translate: `0px ${(1 - pIn) * 220}px`,
                    opacity: f >= a ? 1 : 0,
                    scale: String(isYou && pressed ? 0.97 : 1),
                  }}
                >
                  <div
                    style={{
                      position: "relative",
                      width: r.w,
                      height: r.h,
                      borderRadius: 24,
                      overflow: "hidden",
                      outline: isYou && pressed ? `5px solid ${C.lime}` : "none",
                      outlineOffset: 4,
                    }}
                  >
                    <Photo name={card.photo} scale={ramp(f, a, a + 30, [1.12, 1.02])} />
                    {isYou ? (
                      <div
                        style={{
                          position: "absolute",
                          left: 20,
                          top: 20,
                          ...ui,
                          fontSize: g.portrait ? 26 : 22,
                          fontWeight: 600,
                          textTransform: "uppercase",
                          background: C.lime,
                          color: "#0d0d0f",
                          padding: "10px 20px",
                          borderRadius: 999,
                        }}
                      >
                        Your profile
                      </div>
                    ) : null}
                  </div>
                  <div style={{ ...ui, fontSize: g.cardLabel, color: isYou ? C.lime : C.text, marginTop: 18 }}>{card.label}</div>
                </div>
              );
            })}
          </>
        ) : null}

        {f >= u.cursorIn ? <Cursor x={curX} y={curY} scale={curScale} size={g.portrait ? 76 : 64} /> : null}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const lerpColor = (t: number) => {
  // lime -> white as the wordmark becomes the nav logo
  const a = [216, 238, 72];
  const b = [255, 255, 255];
  const c = a.map((v, i) => Math.round(lerp(v, b[i], t)));
  return `rgb(${c[0]},${c[1]},${c[2]})`;
};

// ---------------------------------------------------------------- PROFILE
// Buys: "your work, your styles, one tap to reach you".
const PORTFOLIO = ["floodlight-profile", "celebrate-fists", "tackle-night", "stretch-ball", "team-backs", "celebrate-run"];

const Profile: React.FC = () => {
  const f = useF();
  const { W, H, portrait } = useLayout();
  const u = T.ui;
  const enter = ramp(f, u.profile, u.profile + 12, [1.12, 1], EASE.land);

  const geo = portrait
    ? {
        avatar: { x: 80, y: 150, s: 150 },
        name: { x: 80, y: 340, size: 96 },
        sub: { x: 80, y: 456, size: 34 },
        chips: { x: 80, y: 520, size: 24 },
        grid: { x: 80, y: 640, w: 920, cols: 2, cellH: 290 },
        cta: { x: 80, y: 1620, size: 34 },
      }
    : {
        avatar: { x: 120, y: 150, s: 150 },
        name: { x: 120, y: 340, size: 84 },
        sub: { x: 120, y: 456, size: 34 },
        chips: { x: 120, y: 530, size: 22 },
        grid: { x: 860, y: 130, w: 940, cols: 3, cellH: 400 },
        cta: { x: 120, y: 680, size: 30 },
      };
  const cellW = (geo.grid.w - (geo.grid.cols - 1) * 24) / geo.grid.cols;

  const ctaRect = { x: geo.cta.x, y: geo.cta.y, w: geo.cta.size * 9, h: geo.cta.size * 2.24 };
  const cIn = ramp(f, u.profile + 22, u.contactPress - 8, [0, 1], EASE.land);
  const curX = lerp(W / 2, ctaRect.x + ctaRect.w * 0.45, cIn);
  const curY = lerp(H / 2, ctaRect.y + ctaRect.h * 0.55, cIn);
  const press = f >= u.contactPress && f < u.contactPress + 4 ? 1 : 0;

  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse 70% 60% at 15% 10%, rgba(25,66,42,0.6) 0%, rgba(13,13,15,0) 70%)",
        }}
      />
      <AbsoluteFill style={{ scale: String(enter), transformOrigin: "50% 45%" }}>
        <div
          style={{
            position: "absolute",
            left: geo.avatar.x,
            top: geo.avatar.y,
            width: geo.avatar.s,
            height: geo.avatar.s,
            borderRadius: 999,
            overflow: "hidden",
            outline: `4px solid ${C.lime}`,
            outlineOffset: 5,
          }}
        >
          <Photo name="floodlight-profile" pos="40% 30%" scale={1.6} />
        </div>
        <div style={{ position: "absolute", left: geo.name.x, top: geo.name.y }}>
          <Words text="YOUR NAME" onsets={[u.profile + 2, u.profile + 6]} size={geo.name.size} color={C.white} align="left" />
        </div>
        <div
          style={{
            position: "absolute",
            left: geo.sub.x,
            top: geo.sub.y,
            ...ui,
            fontSize: geo.sub.size,
            color: C.muted,
            translate: `0px ${ramp(f, u.profile + 6, u.profile + 16, [30, 0])}px`,
            opacity: ramp(f, u.profile + 6, u.profile + 9),
          }}
        >
          Sports photographer · Singapore
        </div>
        <div style={{ position: "absolute", left: geo.chips.x, top: geo.chips.y, display: "flex", gap: 14 }}>
          {["Football", "Matchday", "Portraits"].map((c, i) => (
            <div
              key={c}
              style={{
                translate: `0px ${ramp(f, u.profile + 8 + i * 2, u.profile + 18 + i * 2, [30, 0])}px`,
                opacity: ramp(f, u.profile + 8 + i * 2, u.profile + 11 + i * 2),
              }}
            >
              <Chip label={c} size={geo.chips.size} active={i === 0} icon={i === 0} />
            </div>
          ))}
        </div>
        {PORTFOLIO.map((p, i) => {
          const col = i % geo.grid.cols;
          const row = Math.floor(i / geo.grid.cols);
          const a = u.profile + 4 + i * 2;
          const reveal = ramp(f, a, a + 12, [100, 0], EASE.land);
          return (
            <div
              key={p}
              style={{
                position: "absolute",
                left: geo.grid.x + col * (cellW + 24),
                top: geo.grid.y + row * (geo.grid.cellH + 24),
                width: cellW,
                height: geo.grid.cellH,
                borderRadius: 20,
                overflow: "hidden",
                clipPath: `inset(${reveal}% 0 0 0 round 20px)`,
              }}
            >
              <Photo name={p} scale={ramp(f, a, a + 40, [1.15, 1.03])} />
            </div>
          );
        })}
        <div
          style={{
            position: "absolute",
            left: geo.cta.x,
            top: geo.cta.y,
            translate: `0px ${ramp(f, u.profile + 14, u.profile + 26, [40, 0])}px`,
            opacity: ramp(f, u.profile + 14, u.profile + 17),
          }}
        >
          <CtaPill label="Contact" size={geo.cta.size} press={press} style={{ transformOrigin: "0% 50%" }} />
        </div>
        {f >= u.profile + 22 ? (
          <Cursor
            x={curX + (hash(f) - 0.5) * 0}
            y={curY}
            scale={press ? 0.82 : 1}
            size={portrait ? 76 : 64}
          />
        ) : null}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
