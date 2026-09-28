import json, os, re, subprocess, sys, datetime
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
FB = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
FM = "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
INK = (17, 17, 17); WHITE = (255, 255, 255); YELLOW = (255, 214, 10); RED = (255, 45, 85)
OPT = [((255, 77, 109), WHITE), ((58, 134, 255), WHITE), ((255, 214, 10), INK), ((131, 56, 236), WHITE)]
PINK = (255, 77, 109)
L = "ABCD"
HOOK_T, Q_T, END_T = 3.4, 4.5, 4.2

EMO_RE = re.compile("[\U0001F000-\U0001FFFF☀-➿️‍]")
def clean(s): return EMO_RE.sub("", s).replace("  ", " ").strip()

_fc = {}
def font(path, size):
    k = (path, int(size))
    if k not in _fc: _fc[k] = ImageFont.truetype(path, max(8, int(size)))
    return _fc[k]
_ec = {}
def emoji(ch, size):
    k = (ch, int(size))
    if k not in _ec:
        im = Image.new("RGBA", (180, 180), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((10, 10), ch, font=ImageFont.truetype(EMOJI, 109), embedded_color=True)
        im = im.crop(im.getbbox()); r = size / im.height
        _ec[k] = im.resize((max(1, int(im.width * r)), int(size)), Image.LANCZOS)
    return _ec[k]
def paste_emoji(img, ch, cx, top, size):
    e = emoji(ch, size); img.paste(e, (int(cx - e.width / 2), int(top)), e)

def ease(t): t = max(0, min(1, t)); return 1 - (1 - t) ** 3
def back(t): t = max(0, min(1, t)); c = 1.9; return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2

def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def fit(d, text, path, size, maxw, maxlines):
    while True:
        f = font(path, size); ls = wrap(d, text, f, maxw)
        if len(ls) <= maxlines or size <= 30: return f, ls, size
        size -= 4

def block(img, text, cx, cy, size, fill=WHITE, maxw=920, path=FB, maxlines=4, hl=None, align="c", x0=0):
    d = ImageDraw.Draw(img)
    f, ls, size = fit(d, text, path, size, maxw, maxlines)
    lh = size * 1.14; y = cy - lh * len(ls) / 2
    for ln in ls:
        x = cx - d.textlength(ln, font=f) / 2 if align == "c" else x0
        if hl and hl in ln:
            pre, post = ln.split(hl, 1)
            for seg, col in ((pre, fill), (hl, YELLOW), (post, fill)):
                d.text((x, y), seg, font=f, fill=col); x += d.textlength(seg, font=f)
        else:
            d.text((x, y), ln, font=f, fill=fill)
        y += lh
    return cy + lh * len(ls) / 2

def boxed(img, text, cx, cy, size, bg, fg, maxw=860, scale=1.0, angle=0, path=FB):
    tmp = ImageDraw.Draw(img)
    f, ls, size = fit(tmp, text, path, size * scale, maxw * scale, 3)
    lh = size * 1.18
    tw = max(tmp.textlength(l, font=f) for l in ls)
    pw, ph = tw + 64 * scale, lh * len(ls) + 36 * scale
    layer = Image.new("RGBA", (int(pw) + 20, int(ph) + 20), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.rounded_rectangle((10, 10, 10 + pw, 10 + ph), radius=min(ph / 2, 36 * scale), fill=bg)
    y = 10 + 18 * scale
    for l in ls:
        ld.text((10 + pw / 2 - ld.textlength(l, font=f) / 2, y), l, font=f, fill=fg); y += lh
    if angle: layer = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    img.paste(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)), layer)

def hook(t, ep):
    img = Image.new("RGB", (W, H), INK)
    stake = clean(ep["stake"])
    boxed(img, f"YOU OWE ME #{ep['n']}", W / 2, 300, 40, RED, WHITE)
    p = ease(t / 0.35)
    bottom = block(img, "Tag your partner.", W / 2, 560 - 30 * (1 - p), 110 * (0.85 + 0.15 * p))
    if t > 0.5:
        q = back((t - 0.5) / 0.35)
        b1 = block(img, "Under 4/5 = they owe you", W / 2, 840, 64 * (0.7 + 0.3 * q), WHITE, maxw=980, maxlines=1)
        bottom = block(img, stake, W / 2, b1 + 110, 92 * (0.7 + 0.3 * q), YELLOW, maxlines=3)
        paste_emoji(img, "\U0001F366" if "ice cream" in stake else "\U0001F60F", W / 2, bottom + 30, 140)
    if t > 1.6:
        s = 1.7 - 0.7 * back((t - 1.6) / 0.3)
        boxed(img, "All questions are about ME", W / 2, 1360, 50, YELLOW, INK, scale=s, angle=-3)
    return img

def question(t, idx, qd):
    img = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(img)
    spicy = qd["spicy"]; q = qd["q"]
    frac = max(0, 1 - t / Q_T)
    d.rounded_rectangle((90, 180, 990, 204), radius=12, fill=(60, 60, 60))
    d.rounded_rectangle((90, 180, 90 + 900 * frac, 204), radius=12, fill=RED if spicy else YELLOW)
    label = f"FINAL QUESTION {idx}/5" if spicy else f"QUESTION {idx}/5"
    d.text((W / 2, 262), label, font=font(FB, 44), fill=RED if spicy else YELLOW, anchor="mm")
    p = back(t / 0.35)
    qb = block(img, clean(q[0]), W / 2, 420, 80 * (0.8 + 0.2 * p), maxlines=3)
    if qd.get("app"):
        lw = d.textlength(label, font=font(FB, 44))
        paste_emoji(img, "\U0001F497", W / 2 + lw / 2 + 40, 238, 50)
    if spicy:
        lw = d.textlength(label, font=font(FB, 44))
        paste_emoji(img, "\U0001F336", W / 2 + lw / 2 + 40, 236, 54)
    y0, bh, gap = 600, 180, 22
    for k in range(4):
        pr = ease((t - 0.15 - 0.1 * k) / 0.3)
        xo = (-1 if k % 2 == 0 else 1) * W * (1 - pr)
        y = y0 + k * (bh + gap)
        bg, fg = OPT[k]
        d.rounded_rectangle((60 + xo, y, 1020 + xo, y + bh), radius=36, fill=bg)
        d.ellipse((100 + xo, y + bh / 2 - 48, 196 + xo, y + bh / 2 + 48), fill=WHITE if fg == WHITE else INK)
        d.text((148 + xo, y + bh / 2), L[k], font=font(FB, 54), fill=INK if fg == WHITE else YELLOW, anchor="mm")
        block(img, clean(q[k + 1]), 0, y + bh / 2 + 4, 58, fg, maxw=760, maxlines=2, align="l", x0=230 + xo)
    n = min(4, math.ceil(Q_T - t)) if t < Q_T else 1
    lt = (Q_T - t) % 1
    s = 1.0 + 0.3 * max(0, (lt - 0.75) / 0.25)
    cx, cy, r = W / 2, 1480, 66 * s
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=INK, outline=WHITE, width=7)
    d.text((cx, cy + 4), str(n), font=font(FB, 90 * s), fill=WHITE, anchor="mm")
    return img

def end(t, ep):
    img = Image.new("RGB", (W, H), PINK); d = ImageDraw.Draw(img)
    stake = clean(ep["stake"])
    p = back(t / 0.35)
    block(img, "Comment your letters", W / 2, 400, 100 * (0.85 + 0.15 * p), WHITE)
    d.text((W / 2, 610), "B D A C A", font=font(FB, 120), fill=INK, anchor="mm")
    paste_emoji(img, "\U0001F447", W / 2, 700, 100)
    if t > 0.6:
        s = 1.6 - 0.6 * back((t - 0.6) / 0.3)
        boxed(img, "They mark you.", W / 2, 900, 56, WHITE, INK, scale=s)
    if t > 1.1:
        s = 1.6 - 0.6 * back((t - 1.1) / 0.3)
        boxed(img, f"Loser pays: {stake}", W / 2, 1070, 60, INK, WHITE, scale=s, angle=-3)
    if t > 1.9:
        q = ease((t - 1.9) / 0.35)
        block(img, "They'll \"forget\".", W / 2, 1290 + 30 * (1 - q), 76, WHITE, maxlines=1)
        s = 1.5 - 0.5 * back((t - 2.3) / 0.3) if t > 2.3 else None
        if s: boxed(img, "Log it in CoupleIn", W / 2, 1420, 66, WHITE, (230, 40, 110), scale=s)
    return img

import math
def render(args):
    ep, day, slot = args
    total = HOOK_T + 5 * Q_T + END_T
    out = os.path.join(OUT_DIR, f"YouOweMe_{ep['n']:02d}_{day}_silent.mp4")
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-f", "lavfi", "-t", str(total), "-i", "anullsrc=r=44100:cl=stereo",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
        "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for i in range(int(total * FPS)):
        t = i / FPS
        if t < HOOK_T: img = hook(t, ep)
        elif t < HOOK_T + 5 * Q_T:
            k = int((t - HOOK_T) // Q_T); img = question(t - HOOK_T - k * Q_T, k + 1, ep["qs"][k])
        else: img = end(t - HOOK_T - 5 * Q_T, ep)
        proc.stdin.write(img.tobytes())
    proc.stdin.close(); proc.wait()
    return out

OUT_DIR = os.environ.get("YOM_OUT", "out")
if __name__ == "__main__":
    # usage: python render_video.py episodes.json   (episodes carry "post_date" like Sun04Oct)
    os.makedirs(OUT_DIR, exist_ok=True)
    data = json.load(open(sys.argv[1]))
    jobs = [(ep, ep["post_date"], "") for ep in data["eps"]]
    with Pool(4) as p:
        for o in p.imap(render, jobs): print(o, flush=True)
