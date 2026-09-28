# You Owe Me — TikTok quiz video series (canonical spec)

Read this first. This file plus the code in this folder is everything needed to
rebuild, extend and schedule the series from a fresh chat or a different model.
Chat is where decisions are made; this file is where they live. Update it when a
decision changes.

Last updated: 28 Sep 2026. Episodes 1–14 built and scheduled (4–17 Oct 2026).

---

## 1. What it is

A daily faceless TikTok quiz for the **CoupleIn** account (@coupleinapp).
The viewer tags their partner; the partner answers 5 questions *about the viewer*
in the comments; the viewer marks them; under 4/5 = the partner owes a forfeit.

Why it works (from research on 1M+ view couple posts, Sep 2026):
- Scripted dare in the hook ("Send this to your man and say 'prove it'" hit 1,869x median).
- "Difficulty / score" challenge framing (couples quiz, 441x median, faceless).
- "Drop your answers in the comments and tag your partner" (3.7M, faceless list).
- The game is played **in the comments**, so every couple creates 3–5 public
  comments (tag → partner's letters → viewer's score → argument). Offline
  arguments and DMs are invisible to TikTok; comments are not.

### Viewer flow
1. Hook: "Tag your partner. Under 4/5 = they owe you {forfeit}".
2. Viewer comments "@partner" (comment 1 + tag).
3. Partner comments their letters, e.g. "B D A C A" (comment 2).
4. Viewer replies with the score + "you owe me" (comment 3), then argument.
5. Pinned comment + end card: "They'll 'forget'. Log it in CoupleIn." → bio link.

### CoupleIn tie-in (why it converts, not just entertains)
"You owe me" = CoupleIn's **Brownie Points / gestures** feature (a debt of
gestures between partners). The joke is that losers never pay, so the app is
the answer: *log it in CoupleIn so they can't get out of it.*
- Question 4 of every episode is a CoupleIn-feature question (wishlist, mood,
  calendar, conflict, gestures, love language quiz, attachment quiz).
- Caption line 2 matches that feature.
- Bio link: https://www.coupleinapp.com/love-with-intentionality (Brownie Points page).
- Never promise content that doesn't exist (an earlier "full 50 questions in
  bio" line was removed for this reason).

---

## 2. Episode structure (fixed)

| Part | Time | Content |
|---|---|---|
| Hook | 0–3.4s | "YOU OWE ME #n" red pill → "Tag your partner." → "Under 4/5 = they owe you" + forfeit in yellow + emoji (🍦 if ice cream, else 😏) → yellow tilted sticker "All questions are about ME" |
| Q1–Q5 | 4.5s each (3.4–25.9s) | Timer bar, "QUESTION n/5", question, four answer bars A–D, countdown 4-3-2-1 circle |
| End card | 25.9–30.1s | Pink bg: "Comment your letters" / "B D A C A" / 👇 / "They mark you." / "Loser pays: {forfeit}" / "They'll 'forget'." / "Log it in CoupleIn" button |

Total ≈ 30.1s, 1080×1920, 30fps, H.264 + AAC.

### Question slots (always this order)
1. **Warm-up** — everyday life (easy start)
2. **Food**
3. **Taste** — films, TV, music, holidays, style
4. **CoupleIn** 💗 — tied to an app feature (label shows a pink heart)
5. **Finale** 🌶️ — spicy-funny question about the partner ("FINAL QUESTION 5/5" in red + chilli)

A reserve bank of 20 **Habits** questions is kept for swapping in when a question flops.

### Question-writing rules (the 10/10 bar)
- Every question is about **ME** (the viewer), so only the viewer can mark it.
- Four options; **D is always the funny, too-real one** ("Sofa, snacks, phone. Don't speak to me").
- Fun, petty, relatable, UK-flavoured (Nando's, meal deal, Gavin & Stacey, Sunday roast).
- **Never sad or heavy.** Arguments should be playful. (Sad questions were rejected.)
- Finale must start a friendly argument, never a real one.
- Gender-neutral wording ("Tag your partner", options in "you/me").

### Forfeits (rotate every episode)
Must read correctly after "they owe you …": ice cream 🍦, breakfast in bed, the next date,
a month of you picking the film, a week of doing the dishes, a 10-minute foot rub,
a video saying "you were right", a takeaway of your choice, a week of driving everywhere,
a week of no phones at dinner, a homemade dinner, a massage, a cinema trip, flowers 💐,
a week of morning coffees, a month of bin duty, a handwritten love letter, a Nando's,
a whole day of you being right, a surprise date. Episode 1 is pinned to ice cream.

### Rotation (deterministic — see planner JS `episode(e)`)
- 20 questions per slot; each slot uses a seeded shuffle per 20-episode cycle
  (seed = 1000 × slot + cycle), so each question appears once every 20 episodes
  (10 days at 2/day, 20 days at 1/day) and in new combinations each cycle.
- Forfeits use their own shuffle (seed 9000 + cycle); cycle 0 swaps ice cream into ep 1.
- Captions rotate every 4 episodes: "be honest 😭 how did yours do?" / "tag them. no excuses." /
  "loser pays. we don't make the rules." / "the comments are about to be a crime scene".
- **Changing any question text or order in the planner changes future episodes.**
  Past episode numbers are already posted — edit only questions, never reorder arrays,
  unless you accept that later episodes change.

---

## 3. Visual design

| Token | Value |
|---|---|
| Background (hook, questions) | #111111 |
| Accent yellow | #FFD60A (timer, labels, forfeit text, sticker) |
| Red | #FF2D55 (series pill, final question) |
| Answer A / B / C / D | #FF4D6D / #3A86FF / #FFD60A (ink text) / #8338EC |
| End card background | #FF4D6D; "Log it in CoupleIn" text #E6286E on white |
| Fonts | Poppins Bold (display), Poppins Medium; Noto Color Emoji for emoji |

Animations: back-out pop on headlines, answer bars slide in alternately from
left/right, countdown circle pulses each second. Emoji are stripped from
on-screen answer text (Poppins can't render them) and drawn separately.
TikTok safe zone respected: key content between y≈180 and y≈1500.

## 4. Sound

Original, royalty-free music bed made in code (`render/music_bed.py` → `assets/music_bed.wav`):
118 bpm, I–vi–IV–V in C, kick/clap/hats, bass, plucky chords, marimba melody from the first
question, whoosh into each question, tick on each countdown second, "ding" on the end card.
Mixed to **−14 LUFS, −1.5 dBTP** with ffmpeg loudnorm.

TikTok can't take a trending sound through the API, and you can't add one after posting.
Options: (a) post automatically with the built-in bed (current setup), or (b) set the Metricool
post to "notification" and add a trending sound in the TikTok app at posting time (best reach).

## 5. Posting

- Platform: TikTok, CoupleIn brand in **Metricool** (brand/blog id `7074518`, timezone Europe/London).
- Daily schedule rule: **carousels 08:00 and 12:00; videos 1 a day at 18:00.**
- Episode n posts on **4 Oct 2026 + (n−1) days at 18:00** (ep 15 → 18 Oct).
- Caption = rotating caption + blank line + feature line + blank line + "You Owe Me #n" + hashtags
  `#couples #relationships #couplesquiz #boyfriend #girlfriend`.
- Pinned comment (Metricool `firstCommentText`):
  `Losers always "forget" what they owe 👀 Log it in CoupleIn so they can't get out of it. Link in bio`
- Metricool settings: providers `[tiktok]`, `autoPublish: true`, `privacyOption: PUBLIC_TO_EVERYONE`,
  `tiktokData.title: "You Owe Me #n"`, `autoAddMusic: false` (only works on photo posts).
- **Media hosting:** Metricool needs a direct link per file. Upload MP4s to Dropbox, copy each
  file's own share link (`/scl/fi/…`), change `dl=0` to `dl=1`. Folder links (`/scl/fo/…`) and
  WeTransfer links fail. Metricool copies the file to its own storage when the post is created.

### Scheduled so far
| Episodes | Dates (18:00) | Status |
|---|---|---|
| 1–14 | Sun 4 Oct – Sat 17 Oct 2026 | Scheduled in Metricool with music |

## 6. How to make the next batch

```bash
python build_batch.py 15 14        # episodes 15–28 → out/ep15-28/
```
Produces the 14 MP4s (named `YouOweMe_NN_<post date>_sound.mp4`), `episodes.json` and
`posting_sheet.csv` (date, time, caption, pinned comment). Then: upload to Dropbox →
collect file links → create the Metricool posts from the sheet.

Before building: retire questions with the fewest comments (swap in from the reserve bank or
write new ones following the rules in §2), and update the table in §5 after scheduling.

Requirements: python3 with Pillow, numpy, scipy; node; ffmpeg; fonts Poppins (Bold, Medium)
and Noto Color Emoji at the paths in `render/render_video.py` (edit `FB`, `FM`, `EMOJI` if different).

## 7. Files

| Path | What |
|---|---|
| `planner/you-owe-me-planner.html` | **Single source of truth** for the question bank, forfeits, captions, rotation. Open in a browser to see any day's episodes. Published copy: claude.ai artifact "You Owe Me". |
| `render/render_video.py` | Frame-by-frame renderer (Pillow → ffmpeg). |
| `render/music_bed.py` | Generates `assets/music_bed.wav`. |
| `assets/music_bed.wav` | The current music bed. |
| `build_batch.py` | One-command batch build. |
| `data/week1_episodes.json` | Exact content of episodes 1–14 as scheduled. |

## 8. Decisions log

- 24 Sep: Format chosen after research: faceless, comment-played, dare hook. Earlier ideas
  (earnest carousels, "sad" questions, 2-option "Them/You" questions) rejected.
- 24 Sep: "You Owe Me" forfeit mechanic, questions about ME, four options, D = funny.
- 24 Sep: Forfeit wording fixed to read after "they owe you"; ep 1 = ice cream.
- 24 Sep: CoupleIn tie-in: slot 4 = app-feature question, "Log it in CoupleIn" end card,
  pinned comment, Brownie Points bio link. "Full 50 in bio" removed (didn't exist).
- 26 Sep: Posting = 1 video/day at 18:00 on the CoupleIn TikTok via Metricool, from 4 Oct,
  as the third daily post after the 08:00 and 12:00 carousels.
- 26 Sep: Built-in original music bed added; auto-publish kept (runs on autopilot).

## 9. Known limits / lessons

- The Claude cloud workspace can't download from most sites (vidIQ music URLs, Dropbox pages)
  and can't upload files to Metricool directly; Dropbox per-file links bridge that.
- vidIQ `generate_music` costs 25 credits and its output can't be fetched from the workspace;
  `compose` would cost ~8 credits per video. The code-made music bed avoids both.
- Rendering is done in code, not AI video generation, so it's free and exact.
- Expect weak views for the first 1–3 weeks on a new or throttled account; judge weekly, not per post.
  Track installs per episode (separate link or keyword) to learn which questions convert.
