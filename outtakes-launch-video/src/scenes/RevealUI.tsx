import React from "react";
import { AbsoluteFill } from "remotion";
import { C, ui, wordmark } from "../brand";
import { EASE, hash, lerp, ramp, useF, useLayout } from "../anim";
import { Chip, CtaPill, Cursor, MenuIcon, Photo, SearchIcon, Tag, Tap, Words } from "../components";
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
          background: `radial-gradient(ellipse 70% 55% at 50% ${(g.cy / g.H) * 100}%, rgba(90,85,211,${0.32 + decay * 0.3}) 0%, rgba(47,41,115,0.35) 40%, rgba(17,17,19,0) 75%)`,
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
          textShadow: `0 0 ${60 + decay * 80}px rgba(127,149,248,${glow})`,
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
  color: C.white,
  scale: String(scale),
  opacity,
  whiteSpace: "nowrap",
});

// ---------------------------------------------------------------- UI
// Buys: "clients will actually find you" — the wordmark docks into the site's
// nav, a client searches, your profile is in the results, they open it.
type Sport = "track" | "football" | "rugby" | "swimming";
type Card = { photo: string; tags: Sport[]; you?: boolean };
const CARDS_L: Card[] = [
  { photo: "celebrate-fists", tags: ["football", "track"] },
  { photo: "motion-blur", tags: ["football", "rugby"] },
  { photo: "floodlight-profile", tags: ["football", "track", "rugby"], you: true },
  { photo: "stretch-ball", tags: ["football"] },
];
const CARDS_P: Card[] = [
  { photo: "celebrate-fists", tags: ["football", "track"] },
  { photo: "floodlight-profile", tags: ["football", "track", "rugby"], you: true },
  { photo: "motion-blur", tags: ["football", "rugby"] },
  { photo: "stretch-ball", tags: ["football"] },
];
const QUERY = "football photographer";
// irregular keystroke gaps (frames) for the client's typing
const KEY_GAPS = [0, 2, 2, 1, 2, 3, 1, 2, 2, 4, 2, 1, 2, 2, 1, 3, 2, 1, 2, 2, 1];

const useUiGeo = () => {
  const { W, H, portrait } = useLayout();
  if (portrait) {
    // phone-native: the mobile site, one column of big cards that scrolls
    const cardW = 920;
    const cardH = 600;
    const x0 = 80;
    const y0 = 700;
    const cards = [0, 1, 2, 3].map((i) => ({ x: x0, y: y0 + i * (cardH + 110), w: cardW, h: cardH }));
    return {
      W, H, portrait,
      nav: { x: 80, cy: 300, font: 104, boxW: 210, boxH: 76 },
      head: { top: 480, size: 100, maxW: 940 },
      search: { cx: W / 2, y: 1060, w: 920, h: 130, font: 46, yUp: 430 },
      chipsY: 600,
      cards,
      cardLabel: 34,
    };
  }
  const cardW = 400;
  const cardH = 440;
  const x0 = (W - (4 * cardW + 3 * 40)) / 2;
  const cards = [0, 1, 2, 3].map((i) => ({ x: x0 + i * (cardW + 40), y: 400, w: cardW, h: cardH }));
  return {
    W, H, portrait,
    nav: { x: 120, cy: 100, font: 112, boxW: 400, boxH: 66 },
    head: { top: 270, size: 96, maxW: 1760 },
    search: { cx: W / 2, y: 610, w: 1040, h: 110, font: 40, yUp: 200 },
    chipsY: 318,
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
  const wmX = lerp(rg.cx, g.nav.x, d);
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

  // portrait: the results page scrolls until your card is centred, then a finger taps it
  const scroll = g.portrait ? ramp(f, u.enter + 22, u.cursorIn + 6, [0, -(you.y + you.h / 2 - g.H * 0.5)], EASE.inOut) : 0;

  // cursor: enters oversize, decelerates, parks on your card, presses
  const cx = you.x + you.w * 0.58;
  const cy = you.y + you.h * 0.52 + scroll;
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
  const focusY = you.y + you.h / 2 + scroll;

  if (f >= u.profile) return <Profile />;

  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse 90% 60% at 50% 115%, rgba(90,85,211,0.42) 0%, rgba(47,41,115,0.28) 40%, rgba(17,17,19,0) 75%)",
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
        {/* site header: big white logo top-left (docked), nav box top-right */}
        {g.portrait ? (
          <div
            style={{
              position: "absolute",
              left: 0,
              right: 0,
              top: 0,
              height: g.nav.cy + 150,
              zIndex: 2,
              background: `linear-gradient(180deg, ${C.bg} 82%, rgba(17,17,19,0) 100%)`,
              opacity: ramp(f, u.enter + 18, u.enter + 24),
            }}
          />
        ) : null}
        <div
          style={{
            ...wordmark,
            zIndex: 3,
            position: "absolute",
            left: wmX,
            top: wmY,
            translate: `${lerp(-50, 0, d)}% -50%`,
            fontSize: wmSize,
            color: C.white,
            whiteSpace: "nowrap",
          }}
        >
          OUTTAKES
        </div>
        <div
          style={{
            position: "absolute",
            right: (g.portrait ? 80 : 120) - sideIn * 600,
            top: g.nav.cy - g.nav.boxH / 2,
            width: g.nav.boxW,
            height: g.nav.boxH,
            borderRadius: 10,
            zIndex: 3,
            background: C.surface,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "0 8px 0 8px",
            boxSizing: "border-box",
            opacity: pillGrow > 0.02 ? 1 : 0,
          }}
        >
          {!g.portrait ? (
            <div style={{ ...ui, background: C.white, color: C.ink, fontSize: 24, height: g.nav.boxH - 16, display: "flex", alignItems: "center", padding: "0 34px", borderRadius: 6 }}>
              Sign In
            </div>
          ) : null}
          <div style={{ ...ui, color: C.white, fontSize: g.portrait ? 30 : 24, display: "flex", alignItems: "center", gap: 18, padding: "0 18px", marginLeft: "auto" }}>
            Menu <MenuIcon size={g.portrait ? 34 : 28} />
          </div>
        </div>

        <div style={{ position: "absolute", inset: 0, translate: `0px ${scroll}px` }}>
        {/* hero headline (Figma photographer CTA copy) */}
        {f < u.enter + 12 ? (
          <div style={{ position: "absolute", left: 0, right: 0, top: g.head.top, display: "flex", justifyContent: "center" }}>
            <Words
              text={g.portrait ? "EVERY SIDELINE SHOT STARTS WITH A SEARCH." : "EVERY SIDELINE SHOT / STARTS WITH A SEARCH."}
              onsets={u.words}
              exitAt={u.enter - 2}
              size={g.head.size}
              color={C.white}
              colors={{ 6: C.green }}
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
              borderRadius: 12,
              background: C.surface,
              border: `2px solid ${f >= u.enter && f < u.enter + 6 ? C.green : "rgba(255,255,255,0.14)"}`,
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
              <span style={{ opacity: caretOn && typed ? 1 : 0, color: C.green }}>|</span>
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
              {(g.portrait ? ["Popular", "Under $60", "$60 to $70"] : ["Popular", "Under $60", "$60 to $70", "Highlight", "Matches", "Track"]).map((lab, i) => (
                <div
                  key={lab}
                  style={{
                    translate: `0px ${ramp(f, u.enter + 6 + i * 2, u.enter + 18 + i * 2, [40, 0])}px`,
                    opacity: ramp(f, u.enter + 6 + i * 2, u.enter + 9 + i * 2),
                  }}
                >
                  <Chip label={lab} size={g.portrait ? 30 : 24} active={i === 0} />
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
                      borderRadius: 4,
                      overflow: "hidden",
                      outline: isYou && pressed ? `5px solid ${C.green}` : "none",
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
                          fontSize: g.portrait ? 32 : 22,
                          fontWeight: 500,
                          background: C.green,
                          color: C.ink,
                          padding: "10px 20px",
                          borderRadius: 6,
                        }}
                      >
                        Your profile
                      </div>
                    ) : null}
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 16 }}>
                    {isYou ? <span style={{ ...ui, fontSize: g.cardLabel, color: C.green, marginRight: 8 }}>You</span> : null}
                    {card.tags.map((t) => (
                      <Tag key={t} sport={t} size={g.portrait ? 30 : 22} />
                    ))}
                  </div>
                </div>
              );
            })}
          </>
        ) : null}

        </div>
        {f >= u.cursorIn && !g.portrait ? <Cursor x={curX} y={curY} scale={curScale} size={64} /> : null}
        {g.portrait ? <Tap x={cx} y={cy} appear={u.cursorIn + 8} press={u.cardPress} /> : null}
      </AbsoluteFill>
    </AbsoluteFill>
  );
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
        // kept between the Reels/TikTok top bar (~250 px) and caption zone (~420 px)
        avatar: { x: 80, y: 280, s: 150 },
        name: { x: 80, y: 462, size: 100 },
        sub: { x: 80, y: 582, size: 36 },
        chips: { x: 80, y: 648, size: 26 },
        grid: { x: 80, y: 850, w: 920, cols: 3, cellH: 196 },
        cta: { x: 80, y: 730, size: 34 },
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
          background: "radial-gradient(ellipse 80% 60% at 10% 110%, rgba(90,85,211,0.4) 0%, rgba(47,41,115,0.25) 40%, rgba(17,17,19,0) 75%)",
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
            outline: `4px solid ${C.green}`,
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
          {(["football", "track", "rugby"] as const).map((c, i) => (
            <div
              key={c}
              style={{
                translate: `0px ${ramp(f, u.profile + 8 + i * 2, u.profile + 18 + i * 2, [30, 0])}px`,
                opacity: ramp(f, u.profile + 8 + i * 2, u.profile + 11 + i * 2),
              }}
            >
              <Tag sport={c} size={geo.chips.size * 1.15} />
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
                borderRadius: 4,
                overflow: "hidden",
                clipPath: `inset(${reveal}% 0 0 0)`,
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
        {portrait ? (
          <Tap x={ctaRect.x + ctaRect.w * 0.3} y={ctaRect.y + ctaRect.h * 0.5} appear={u.contactPress - 14} press={u.contactPress} />
        ) : null}
        {f >= u.profile + 22 && !portrait ? (
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
