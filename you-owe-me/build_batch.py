"""Build a batch of "You Owe Me" TikTok episodes end to end.

usage:  python build_batch.py FIRST_EPISODE COUNT
e.g.    python build_batch.py 15 14      -> episodes 15-28

Steps: export episodes from the planner (single source of truth for questions,
forfeits, captions) -> render silent video -> add music bed -> write
posting sheet (date, time, caption, pinned comment) for Metricool.
Requires: python3 (Pillow, numpy, scipy), node, ffmpeg, Poppins + Noto Color Emoji fonts.
"""
import csv, datetime, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PLANNER = os.path.join(ROOT, "planner", "you-owe-me-planner.html")
FIRST_POST = datetime.date(2026, 10, 4)   # episode 1 posts on this date
POST_TIME = "18:00"                        # videos: 1 a day at 18:00 UK time
HASHTAGS = "#couples #relationships #couplesquiz #boyfriend #girlfriend"

first, count = int(sys.argv[1]), int(sys.argv[2])
out = os.path.join(ROOT, "out", f"ep{first:02d}-{first + count - 1:02d}")
os.makedirs(out, exist_ok=True)

# 1. export episodes straight from the planner's own JS so video == planner
html = open(PLANNER, encoding="utf-8").read()
js = html[html.index("<script>") + 8: html.index("const dayEl")]
js += (f"\nconst out=[];for(let e={first - 1};e<{first - 1 + count};e++)out.push(episode(e));"
       "console.log(JSON.stringify({eps:out,pin:PIN}));")
data = json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout)
for ep in data["eps"]:
    d = FIRST_POST + datetime.timedelta(days=ep["n"] - 1)
    ep["post_date"] = d.strftime("%a%d%b")
    ep["post_iso"] = d.isoformat()
    ep["full_caption"] = f"{ep['caption']}\n\n{ep['feature']}\n\nYou Owe Me #{ep['n']} {HASHTAGS}"
json.dump(data, open(os.path.join(out, "episodes.json"), "w"), ensure_ascii=False, indent=1)

# 2. render silent videos
env = dict(os.environ, YOM_OUT=out)
subprocess.run([sys.executable, os.path.join(ROOT, "render", "render_video.py"),
                os.path.join(out, "episodes.json")], check=True, env=env)

# 3. add the music bed (regenerate it if missing), loudness -14 LUFS
bed = os.path.join(ROOT, "assets", "music_bed.wav")
if not os.path.exists(bed):
    subprocess.run([sys.executable, os.path.join(ROOT, "render", "music_bed.py")], check=True)
for ep in data["eps"]:
    silent = os.path.join(out, f"YouOweMe_{ep['n']:02d}_{ep['post_date']}_silent.mp4")
    final = os.path.join(out, f"YouOweMe_{ep['n']:02d}_{ep['post_date']}_sound.mp4")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", silent, "-i", bed, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=7", "-c:a", "aac", "-b:a", "192k",
                    "-ar", "44100", "-shortest", "-movflags", "+faststart", final], check=True)
    os.remove(silent)

# 4. posting sheet for Metricool
with open(os.path.join(out, "posting_sheet.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["episode", "file", "date", "time", "caption", "pinned_comment", "forfeit"])
    for ep in data["eps"]:
        w.writerow([ep["n"], f"YouOweMe_{ep['n']:02d}_{ep['post_date']}_sound.mp4", ep["post_iso"], POST_TIME,
                    ep["full_caption"], data["pin"], ep["stake"]])
print("done ->", out)
