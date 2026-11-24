# Ozen motion brief

Two forms. Send Part 1 to the client as is (WhatsApp or email), or fill it from a call. Paste the answers and the files into Claude with one line such as "Make this video" and nothing else needs explaining. Part 2 is for revision requests.

Blank answers are fine: Claude picks something sensible and says what it assumed. The starred questions are the ones that can't be guessed.

---

## Part 1: new video

```
OZEN MOTION BRIEF

1. Brand / company name *:
2. What is this video for, in one line? (launch, explain the product, promote an offer, event, brand intro...)
3. Who will watch it?
4. The one thing they must remember after watching *:
5. What should they do after watching? (visit a link, DM a word, book, download, buy) *:
6. Length: 15 / 20 / 30 / 45 / 60 / 90 seconds
7. Where will it be posted? Instagram Reels / TikTok / LinkedIn / YouTube / website / paid ads / WhatsApp
8. Formats: 9:16 vertical (default) / 1:1 square / 4:5 feed / 16:9 landscape
9. Exact words, prices, dates, product names, website, handles that must appear (copy them exactly) *:
10. Must show: product screens, app UI, photos, footage, a person, the logo moment:
11. Brand: logo file (SVG or a large PNG) *, colours (hex if you have them), fonts, website, brand guide:
12. Look and feel in three words (e.g. clean, bold, playful):
13. Videos you like (links or screen recordings) and what you like about each:
14. Sound: music mood (calm / upbeat / cinematic / none) and voiceover: none / female / deep male / your own recording / script attached
15. Language and captions:
16. Anything to avoid (colours, words, competitors, styles):
17. Deadline:
```

Internal lines Shezan adds before pasting (the client never sees these):

```
Plan: Starter / Growth / Pro / one-off up to 30, 60 or 90 s / custom quote
Video number this month: _ of _
Rush (12 hours, +S$40): yes / no
White-label (no Ozen credit anywhere): yes / no
Portfolio use allowed: yes / no / ask later
Notes from the call:
```

---

## Part 2: revision request

```
OZEN REVISION
Client / video / version: (e.g. Acme / launch-teaser / v1)
Round: 1 of 1 (Starter) / 1 of 2 or 2 of 2 (Growth, Pro) / extra round (+S$15)
Changes, one per line, with the time in the video:
- 0:04  ...
- 0:12  ...
Anything that must NOT change:
```

How Claude handles it: changes only what is listed, re-renders only the scenes that changed, delivers as the next version (v2, v3), and logs the round in the job's STATE.md. A new script or a new idea counts as a new video, and Claude says so before starting.
