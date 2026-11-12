import React from "react";
import { AbsoluteFill, Sequence, staticFile } from "remotion";
import { Audio } from "@remotion/media";
import "./brand";
import { C } from "./brand";
import { FrameOffset } from "./anim";
import { Grain, Shutter } from "./components";
import { Chase, Hook } from "./scenes/HookChase";
import { Reveal, UI } from "./scenes/RevealUI";
import { Call, Community, Cta } from "./scenes/CallCommunityCta";
import T from "./timeline.json";

export type FilmProps = { withAudio: boolean };

const Scene: React.FC<{ from: number; to: number; name: string; children: React.ReactNode }> = ({
  from,
  to,
  name,
  children,
}) => (
  <Sequence from={from} durationInFrames={to - from} name={name}>
    <FrameOffset.Provider value={from}>{children}</FrameOffset.Provider>
  </Sequence>
);

export const Film: React.FC<FilmProps> = ({ withAudio }) => (
  <AbsoluteFill style={{ background: C.bg }}>
    <Scene from={T.hook.from} to={T.hook.to} name="1 Hook — burst">
      <Hook />
    </Scene>
    <Scene from={T.chase.from} to={T.chase.to} name="2 Chase — DMs">
      <Chase />
    </Scene>
    <Scene from={T.reveal.from} to={T.reveal.to} name="3 Reveal — wordmark">
      <Reveal />
    </Scene>
    <Scene from={T.ui.from} to={T.ui.to} name="4 Get found — search + profile">
      <UI />
    </Scene>
    <Scene from={T.call.from} to={T.call.to} name="5 Call">
      <Call />
    </Scene>
    <Scene from={T.community.from} to={T.community.to} name="6 Community">
      <Community />
    </Scene>
    <Scene from={T.cta.from} to={T.cta.to} name="7 CTA">
      <Cta />
    </Scene>
    <Grain opacity={0.09} />
    <Shutter />
    {withAudio ? <Audio src={staticFile("mix.wav")} /> : null}
  </AbsoluteFill>
);
