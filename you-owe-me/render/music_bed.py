import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
TOTAL = 30.1
BPM = 118
BEAT = 60 / BPM
E8 = BEAT / 2
HOOK_T, Q_T = 3.4, 4.5
N = int(SR * (TOTAL + 1))
mix = np.zeros((N, 2))
rng = np.random.default_rng(7)

def hz(n):  # midi -> Hz
    return 440 * 2 ** ((n - 69) / 12)

def env(length, decay, attack=0.004):
    t = np.arange(int(SR * length)) / SR
    a = np.minimum(1, t / attack)
    return a * np.exp(-t / decay), t

def add(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N: return
    sig = sig[: N - i]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    mix[i:i + len(sig), 0] += sig * gain * l * 1.41
    mix[i:i + len(sig), 1] += sig * gain * r * 1.41

def lp(x, fc, order=2):
    b, a = butter(order, fc / (SR / 2), "low"); return lfilter(b, a, x)
def hp(x, fc, order=2):
    b, a = butter(order, fc / (SR / 2), "high"); return lfilter(b, a, x)
def bp(x, lo, hi):
    b, a = butter(2, [lo / (SR / 2), hi / (SR / 2)], "band"); return lfilter(b, a, x)

def kick():
    e, t = env(0.35, 0.12, 0.001)
    f = 45 + 110 * np.exp(-t / 0.03)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * e + 0.3 * np.sin(ph) * np.exp(-t / 0.01)

def clap():
    out = np.zeros(int(SR * 0.25))
    for k, d in enumerate([0, 0.011, 0.022]):
        e, t = env(0.25 - d, 0.012 if k < 2 else 0.09, 0.001)
        n = bp(rng.standard_normal(len(e)), 900, 3500) * e
        i = int(d * SR); out[i:i + len(n)] += n
    return out * 0.9

def hat(open_=False):
    e, t = env(0.2 if open_ else 0.06, 0.05 if open_ else 0.015, 0.001)
    return hp(rng.standard_normal(len(e)), 7000) * e

def snap():
    e, t = env(0.08, 0.012, 0.0005)
    return bp(rng.standard_normal(len(e)), 2000, 6000) * e

def bass(note, length):
    e, t = env(length, 0.18, 0.005)
    f = hz(note)
    s = sum(np.sin(2 * np.pi * f * k * t) / k ** 1.6 for k in range(1, 6))
    return lp(s, 900) * e

def pluck(notes, length=0.3):
    e, t = env(length, 0.09, 0.003)
    s = np.zeros(len(t))
    for n in notes:
        f = hz(n) * (1 + rng.uniform(-0.002, 0.002))
        s += sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, 9))
    return lp(s / len(notes), 2600) * e

def marimba(note, length=0.45):
    e, t = env(length, 0.16, 0.002)
    f = hz(note)
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t / 0.03)) * e

def tick():
    e, t = env(0.05, 0.01, 0.0005)
    return np.sin(2 * np.pi * 1900 * t) * e + 0.5 * np.sin(2 * np.pi * 3100 * t) * e

def ding():
    e, t = env(1.4, 0.45, 0.002)
    return (np.sin(2 * np.pi * 1318.5 * t) + 0.6 * np.sin(2 * np.pi * 1975.5 * t) + 0.3 * np.sin(2 * np.pi * 2637 * t)) * e

def whoosh(length=0.5):
    t = np.arange(int(SR * length)) / SR
    n = rng.standard_normal(len(t))
    shape = np.sin(np.pi * t / length) ** 2
    return bp(n, 600, 5000) * shape

# I - vi - IV - V in C
CHORDS = [(48, [72, 76, 79]), (45, [69, 72, 76]), (41, [69, 72, 77]), (43, [71, 74, 79])]
MEL = [
    [76, 79, None, 84, None, 79, 76, None],
    [76, 81, None, 84, None, 81, 76, None],
    [77, 81, None, 84, None, 81, 77, None],
    [74, 79, None, 83, None, 86, None, None],
]
bar_len = 4 * BEAT
bars = int(TOTAL / bar_len) + 1
end_start = HOOK_T + 5 * Q_T

for b in range(bars):
    t0 = b * bar_len
    root, triad = CHORDS[b % 4]
    for beat in range(4):
        tb = t0 + beat * BEAT
        if tb > TOTAL: break
        add(kick(), tb, 0.95)
        if beat in (1, 3): add(clap(), tb, 0.32, 0.05)
        add(hat(), tb + E8, 0.09, 0.35)
        add(hat(), tb, 0.04, 0.35)
        add(snap(), tb + E8 * 1.5, 0.07, -0.3) if beat % 2 == 0 else None
        add(pluck(triad), tb + E8, 0.28, -0.25)
        for k in range(2):
            n = root + (12 if (beat * 2 + k) % 4 == 3 else 0)
            add(bass(n - 12, E8 * 0.95), tb + k * E8, 0.55)
    if t0 >= HOOK_T - bar_len * 0.1:
        for k, n in enumerate(MEL[b % 4]):
            if n is not None:
                add(marimba(n), t0 + k * E8, 0.32, 0.2)

# game-show sound design on top of the beat
add(whoosh(0.4), 0.15, 0.15)
add(whoosh(0.35), 1.45, 0.18)
for q in range(5):
    qs = HOOK_T + q * Q_T
    add(whoosh(0.35), qs - 0.15, 0.16)
    for s in (1.5, 2.5, 3.5):
        add(tick(), qs + s, 0.22, 0.4)
add(ding(), end_start + 0.05, 0.4)

# fade out, glue, normalise
out = mix[: int(SR * TOTAL)]
fade = int(SR * 0.6)
out[-fade:] *= np.linspace(1, 0, fade)[:, None]
out /= np.max(np.abs(out)); out = np.tanh(out * 1.1) / np.tanh(1.1)
out /= np.max(np.abs(out)) / 0.89
wavfile.write(__import__("os").path.join(__import__("os").path.dirname(__file__), "..", "assets", "music_bed.wav"), SR, (out * 32767).astype(np.int16))
print("ok", out.shape[0] / SR)
