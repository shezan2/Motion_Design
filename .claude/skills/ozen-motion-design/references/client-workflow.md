# Client workflow: scope, messages, revisions, agencies

## 1. The flow
1. **Enquiry:** send the rate card and Part 1 of `BRIEF.md`.
2. **Brief received:** check the starred answers and the logo file. Missing facts: ask once, in one message, for everything missing. Everything else: assume and say so in the draft message.
3. **Payment:** follow Shezan's terms (plans monthly; one-offs or new partners commonly part upfront). Don't start rush work before it is confirmed.
4. **First draft within 2 working days** (12 hours on rush), in the main format, with a light WhatsApp preview if that's the channel.
5. **Feedback:** one consolidated list per round (Part 2 of `BRIEF.md`).
6. **Final:** every ordered format, covers, captions if voiced.
7. **Archive:** the job folder, kept.

## 2. What counts as what
- **A video:** one idea and one script, up to the plan's length, in the ordered formats. Extra formats of the same video are part of it.
- **A revision round:** one consolidated list of changes to the existing video (timing, words, colours, swapping a shot, music choice). Starter has 1 round per video, Growth and Pro 2; an extra round is S$15.
- **Not a revision:** a new script, a new idea, a different length tier, a new language version. That's a new video or a quote. Say so kindly before starting.
- **Rush:** delivery within 12 hours for +S$40, only when Shezan confirms capacity.
- **Over 90 seconds or heavy work** (3D, long voiceover, footage editing, many versions): a custom quote from Shezan.

## 3. Message templates
Short, warm, plain English, in Shezan's voice. Fill the brackets. Never promise what the rate card doesn't.

**Missing info**
> Hi [name], thanks for the brief! Just need [the logo as SVG or a large PNG / the exact price / the launch date] before I start. Everything else I can work with.

**Draft delivery**
> Hi [name], here's the first draft of [video] ([length], [format]). [One line on the idea, e.g. "The scattered messages pull together into your logo, then we show the booking in three taps."] You have [1/2] revision round[s] on this video. Send all your changes in one message, with the time in the video for each, and I'll turn them around.

**Revision received**
> Got it, thanks. That's round [1] of [2]. I'll send v[2] by [day].

**Out of rounds**
> Happy to make these changes. This would be an extra revision round (S$15). Shall I go ahead?

**Change that is really a new video**
> This one is a new direction rather than a revision, so it would count as a new video on your plan [or: a one-off at S$X]. Want me to go ahead with it as the next video?

**Final delivery**
> Here are the final files: [list of formats], plus the cover image[s] [and captions file]. They're ready to post. Thanks for working with Ozen!

## 4. Agencies and white-label (resellers such as marketing agencies)
- Partner pricing is Shezan's call: either a partner discount or the agency adds its own margin. Never quote a partner rate that hasn't been agreed.
- **White-label:** no Ozen credit, watermark or handle anywhere in the video, file names or metadata; the delivery message goes to the agency, not the end client.
- **Portfolio use:** ask before showing white-label work anywhere, and record the answer in `STATE.md`.
- Each request still needs the brief: logo, colours, script, length, platform, deadline, voiceover yes or no, any footage.
- Agree turnaround, rounds and formats per request so the agency doesn't over-promise to its client.

## 5. Job folder and archive
```
jobs/<client>/<video>/
  STATE.md          plan, cap, formats, deadline, version, rounds used, decisions, Shezan's notes
  brief.md          the client's answers
  brand/            logo, fonts, colours, captured UI and photos
  refs-breakdown/   output of ref_breakdown.py, if references were sent
  build/            the film source (build script, scene folders)
  audio/            music (with licence note), SFX, voiceover takes, the mix
  out/              renders: <client>-<video>-<ratio>-v<N>.mp4, covers, .srt
  NOTE.md           the internal delivery note
```
Keep the source, assets, final renders, `NOTE.md` and licence records. Delete intermediate renders once a version is delivered; keep every delivered version.
