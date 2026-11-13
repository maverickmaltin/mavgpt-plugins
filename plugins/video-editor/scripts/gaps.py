"""Measure the silence between words on the audio itself (not on the transcript's word times).

Shared by tighten.py (sets every cut so no word is clipped and no dead space is left),
checkcuts.py (proves an export has neither) and analyze.py (measures how tightly a
finished video you like is cut, so your style can copy it).

How a word's edges are found: the audio is turned into a level every 2 ms. A word lasts
while it stays within 30 dB of its OWN loudest moment, so a quiet word keeps its quiet
ending even when the next word is loud. The level of a frame is the louder of the full band
and the 3.5-12 kHz band (+6 dB), so an "s", "f" or a "t" release counts as part of the word.

Needs numpy (it comes with faster-whisper).
"""
import re
import subprocess
import sys
from pathlib import Path

try:
    import numpy as np
except ImportError:  # pragma: no cover - reported by check_setup.py
    np = None

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vtools  # noqa: E402

SR = 32000      # sample rate used for measuring
FR = 500        # level frames per second (2 ms)
WIN = 0.012     # level window (12 ms)
D_WORD = 30.0   # a word lasts while it is within this many dB of its own peak

STOPS = set("pbtdkgc")
FRICATIVES = ("sh", "th", "ch", "s", "f", "z", "x", "j", "v")


def need_numpy():
    if np is None:
        sys.exit("This step needs numpy. Install it with: python3 -m pip install --user numpy "
                 "(it also comes with faster-whisper).")


def load_audio(path, ffmpeg=None, sr=SR):
    """Mono float32 samples of a video or audio file."""
    need_numpy()
    if ffmpeg is None:
        ffmpeg, _, _ = vtools.need_ffmpeg()
    p = subprocess.run([ffmpeg, "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", str(sr),
                        "-f", "f32le", "-"], capture_output=True)
    if p.returncode != 0:
        tail = p.stderr.decode("utf-8", "replace").strip().splitlines()[-3:]
        sys.exit(f"Couldn't read the audio of {path}: {' '.join(tail)}")
    return np.frombuffer(p.stdout, dtype=np.float32).copy()


def _rms_db(x, sr, fr, win):
    hop = sr / fr
    n = int(len(x) / hop) + 1
    half = max(1, int(win * sr / 2))
    cs = np.concatenate([[0.0], np.cumsum(x.astype(np.float64) ** 2)])
    centers = (np.arange(n) * hop).astype(np.int64)
    lo = np.clip(centers - half, 0, len(x))
    hi = np.clip(centers + half, 0, len(x))
    width = np.maximum(1, hi - lo)
    power = (cs[hi] - cs[lo]) / width
    return 10.0 * np.log10(power + 1e-12)


def _band(x, sr, lo_hz, hi_hz, chunk_s=30.0, pad_s=0.1):
    """Band-pass by FFT in chunks (no scipy needed)."""
    out = np.zeros_like(x)
    step = int(chunk_s * sr)
    pad = int(pad_s * sr)
    for start in range(0, len(x), step):
        a = max(0, start - pad)
        b = min(len(x), start + step + pad)
        seg = x[a:b]
        spec = np.fft.rfft(seg)
        freqs = np.fft.rfftfreq(len(seg), 1.0 / sr)
        spec[(freqs < lo_hz) | (freqs > hi_hz)] = 0
        y = np.fft.irfft(spec, n=len(seg)).astype(np.float32)
        out[start:min(len(x), start + step)] = y[start - a:start - a + min(step, len(x) - start)]
    return out


def levels(x, sr=SR, fr=FR, win=WIN):
    """Level in dB every 1/fr seconds: max(full band, 3.5-12 kHz + 6 dB)."""
    need_numpy()
    if len(x) == 0:
        return np.array([-120.0])
    full = _rms_db(x, sr, fr, win)
    hi = _rms_db(_band(x, sr, 3500, min(12000, sr / 2 - 1)), sr, fr, win)
    n = min(len(full), len(hi))
    return np.maximum(full[:n], hi[:n] + 6.0)


def audio_levels(path, ffmpeg=None):
    return levels(load_audio(path, ffmpeg))


def punct(text):
    t = (text or "").strip().strip('"\'”’)')
    if not t:
        return ""
    if t[-1] in ".?!":
        return "." if t[-1] == "." else t[-1]
    if t[-1] in ",;:—-":
        return ","
    return ""


def first_sound(text):
    t = re.sub(r"[^a-z]", "", (text or "").lower())
    if not t:
        return "vowel"
    if t[0] == "h":
        return "h"
    if t.startswith(FRICATIVES) or t[0] in "sfzxjv":
        return "fricative"
    if t[0] in STOPS or t[0] == "q":
        return "stop"
    return "vowel"


# How far before the level threshold a word really starts (its soft first sound), seconds.
ONSET_BACK = {"h": 0.060, "fricative": 0.035, "stop": 0.025, "vowel": 0.010}


class Track:
    """Levels of one audio track with helpers in seconds."""

    def __init__(self, lvl, fr=FR, floor=None):
        self.lvl = lvl
        self.fr = fr
        self.n = len(lvl)
        # The room (or music bed) level: words end where they fade under their own peak - D,
        # but never below the room + 6 dB, so noisy footage still gets sensible edges.
        real = lvl[lvl > -110]
        if floor is not None:
            self.floor = float(floor)  # e.g. the room level of the uncut original
        else:
            self.floor = float(np.percentile(real, 1)) if len(real) else -120.0

    def thr(self, peak, D=D_WORD):
        return max(peak - D, self.floor + 3.0)

    def k(self, t):
        return int(max(0, min(self.n - 1, round(t * self.fr))))

    def t(self, k):
        return k / float(self.fr)

    def peak(self, a, b):
        ka, kb = self.k(a), self.k(b)
        if kb <= ka:
            kb = min(self.n - 1, ka + 1)
        return float(self.lvl[ka:kb + 1].max())

    def word_end(self, w, limit, D=D_WORD):
        """Where word w has faded D dB under its own peak, searching up to `limit` seconds.
        Keeps a stop release ("project.") that comes back after a short silent closure."""
        p = self.peak(w["start"], max(w["start"] + 0.03, min(w["end"], limit)))
        thr = self.thr(p, D)
        ka = self.k(w["start"])
        kl = self.k(limit)
        if kl <= ka:
            return w["end"]
        seg = self.lvl[ka:kl + 1]
        loud = np.nonzero(seg >= thr)[0]
        if len(loud) == 0:
            return min(w["end"], limit)
        # Walk from the start of the word: the word ends at the first quiet stretch longer
        # than 140 ms, or at the limit. Short dips (closures before a t/k/p release) stay inside.
        last = loud[0]
        for idx in loud[1:]:
            if idx - last > int(0.140 * self.fr):
                break
            last = idx
        return self.t(ka + last + 1)

    def has_pause(self, w1, w2, D=D_WORD):
        """True when the sound really drops between two words (a place a cut can go)."""
        a = self.k(w1["start"] + 0.5 * max(0.0, w1["end"] - w1["start"]))
        b = self.k(w2["start"] + 0.5 * max(0.0, w2["end"] - w2["start"]))
        if b - a < 3:
            return False
        lo = float(self.lvl[a:b + 1].min())
        p1 = self.peak(w1["start"], max(w1["start"] + 0.03, w1["end"]))
        p2 = self.peak(w2["start"], max(w2["start"] + 0.03, w2["end"]))
        return lo < self.thr(p1, D) and lo < self.thr(p2, D)

    def word_start(self, w, earliest, D=D_WORD):
        """Where word w first rises within D dB of its own peak (searching forward from `earliest`,
        or 0.3 s before whisper's start), backed up over its soft first sound. Use between() for a
        word that follows another word: it's more reliable."""
        p = self.peak(w["start"], max(w["start"] + 0.05, w["end"]))
        thr = self.thr(p, D)
        k0 = self.k(max(earliest, w["start"] - 0.3))
        k1 = self.k(max(w["end"], w["start"] + 0.05))
        if k1 <= k0:
            return max(earliest, w["start"])
        loud = np.nonzero(self.lvl[k0:k1 + 1] >= thr)[0]
        if len(loud) == 0:
            return max(earliest, w["start"])
        onset = self.t(k0 + loud[0]) - ONSET_BACK[first_sound(w["text"])]
        return max(earliest, onset)

    def between(self, w1, w2, D=D_WORD):
        """The pause between two neighbouring words: returns (end_of_w1, start_of_w2, has_pause, quiet_s),
        quiet_s being the full quiet stretch (before backing up over w2's soft first sound).

        end_of_w1: the first moment after w1's loudest point where the sound stays 30 dB under
        w1's own peak for 40 ms (a t/k/p release that comes back within 140 ms stays with w1).
        start_of_w2: the last moment before w2's loudest point where the sound had been that quiet
        for 40 ms, backed up over w2's soft first sound (h, s, f, a stop's burst).
        Anything between them (silence, a breath, a lip smack, room noise) is pause."""
        lvl = self.lvl
        t1 = self.thr(self.peak(w1["start"], max(w1["start"] + 0.03, w1["end"])), D)
        t2 = self.thr(self.peak(w2["start"], max(w2["start"] + 0.03, w2["end"])), D)
        k1a, k1b = self.k(w1["start"]), self.k(max(w1["end"], w1["start"] + 0.03))
        k2a, k2b = self.k(w2["start"]), self.k(max(w2["end"], w2["start"] + 0.03))
        kp1 = k1a + int(np.argmax(lvl[k1a:k1b + 1]))
        kp2 = k2a + int(np.argmax(lvl[k2a:k2b + 1]))
        midt = (w1["end"] + w2["start"]) / 2
        if kp2 <= kp1 + 2:
            return midt, midt, False, 0.0
        need = max(2, int(0.04 * self.fr))
        e, run = None, 0
        for i in range(kp1, kp2):
            if lvl[i] < t1:
                run += 1
                if run >= need:
                    e = i - run + 1
                    break
            else:
                run = 0
        if e is None:
            return midt, midt, False, 0.0
        # A short loud blip right after the quiet start is a stop release: it belongs to w1.
        j = e
        while j < kp2 and lvl[j] < t1:
            j += 1
        if j < kp2 and (j - e) <= int(0.14 * self.fr):
            b = j
            while b < kp2 and lvl[b] >= t1:
                b += 1
            q, run2 = b, 0
            while q < kp2 and lvl[q] < t1 and run2 < need:
                run2 += 1
                q += 1
            if (b - j) <= int(0.08 * self.fr) and run2 >= need:
                e = b
        o, run, top = None, 0, None
        for i in range(kp2 - 1, e - 1, -1):
            if lvl[i] < t2:
                if run == 0:
                    top = i
                run += 1
                if run >= need:
                    o = top + 1
                    break
            else:
                run = 0
        if o is None or o <= e:
            return self.t(e), self.t(e), False, 0.0
        end1 = self.t(e)
        start2 = max(end1, self.t(o) - ONSET_BACK[first_sound(w2["text"])])
        return end1, start2, True, self.t(o) - end1


def boundary_gaps(track, words, D=D_WORD):
    """For each pair of neighbouring words (on the track's timeline): the silence in ms from
    where the first word fades D dB under its own peak to where the next word rises within D dB
    of its peak."""
    lvl, fr = track.lvl, track.fr
    res = []
    for i, (w1, w2) in enumerate(zip(words[:-1], words[1:])):
        lo = min(w1["end"], w2["start"]) - 0.15
        hi = max(w1["end"], w2["start"]) + 0.15
        a, b = track.k(lo), track.k(hi)
        if b - a < 5:
            continue
        m = a + int(np.argmin(lvl[a:b]))
        p1 = track.peak(w1["start"], max(w1["start"] + 0.03, w1["end"]))
        p2 = track.peak(w2["start"], max(w2["start"] + 0.03, w2["end"]))
        t1, t2 = track.thr(p1, D), track.thr(p2, D)
        e = m
        kw1 = track.k(w1["start"])
        while e > kw1 and lvl[e - 1] < t1:
            e -= 1
        o = m
        kw2 = track.k(w2["end"])
        while o < kw2 and lvl[o] < t2:
            o += 1
        res.append({"t": round(e / fr, 3), "before": w1["text"], "after": w2["text"],
                    "punct": punct(w1["text"]), "ms": max(0, int(round((o - e) / fr * 1000))), "i": i,
                    "min_db": round(float(lvl[m]), 1)})
    return res


def summarize(res):
    out = {}
    groups = (("sentence", lambda r: r["punct"] in (".", "?", "!")),
              ("comma", lambda r: r["punct"] == ","),
              ("other", lambda r: not r["punct"]))
    for name, sel in groups:
        a = [r["ms"] for r in res if sel(r)]
        if a:
            out[name] = {"n": len(a), "median": float(np.median(a)), "p90": float(np.percentile(a, 90)),
                         "max": int(max(a))}
    return out


def describe(summary):
    s = summary.get("sentence")
    if not s:
        return "not enough sentences to measure"
    med = s["median"]
    if med <= 30:
        feel = "very tight (next sentence starts almost instantly)"
    elif med <= 80:
        feel = "tight"
    elif med <= 160:
        feel = "natural"
    else:
        feel = "relaxed (lots of air between sentences)"
    return f"{feel}: sentence gaps median {med:.0f} ms, p90 {s['p90']:.0f} ms, max {s['max']} ms"


def words_out(words, keep):
    """Map source-timeline words to an edited timeline made of the kept parts."""
    segs, t = [], 0.0
    for a, b in keep:
        segs.append((a, b, t))
        t += b - a
    out = []
    for w in words:
        ws, we = float(w["start"]), float(w["end"])
        if we - ws < 0.05:
            we = ws + 0.08  # whisper sometimes gives a word no length
        mid = (ws + we) / 2
        for a, b, off in segs:
            if a <= mid <= b:
                s = max(a, ws) - a + off
                e = min(b, we) - a + off
                if e > s:
                    out.append(dict(w, start=s, end=e))
                break
    return out, segs
