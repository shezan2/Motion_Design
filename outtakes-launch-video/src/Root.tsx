import React from "react";
import { Composition } from "remotion";
import { Film, FilmProps } from "./Film";
import T from "./timeline.json";

export const RemotionRoot: React.FC = () => {
  const defaults: FilmProps = { withAudio: true };
  return (
    <>
      <Composition
        id="Outtakes-16x9"
        component={Film}
        durationInFrames={T.total}
        fps={T.fps}
        width={1920}
        height={1080}
        defaultProps={defaults}
      />
      <Composition
        id="Outtakes-9x16"
        component={Film}
        durationInFrames={T.total}
        fps={T.fps}
        width={1080}
        height={1920}
        defaultProps={defaults}
      />
    </>
  );
};
