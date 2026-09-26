"""Semua suara GEMA dibuat di sini dengan numpy. Tidak ada file suara.

Setiap fungsi mengembalikan array float di rentang -1..1, berbentuk (n,) untuk mono
atau (n, 2) untuk stereo. Suara loop dibuat periodik supaya sambungannya mulus.
"""

import numpy as np


def _t(sr, dur):
    return np.arange(int(sr * dur)) / sr


def _norm(x, peak):
    m = np.max(np.abs(x))
    return x / m * peak if m > 0 else x


def _band_noise(n, rng, sr, lo=None, hi=None, tilt=0.0):
    """Noise yang disaring lewat FFT. Hasilnya periodik sepanjang n sampel (aman untuk loop)."""
    spec = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1.0 / sr)
    f[0] = 1e-3
    mask = np.ones_like(f)
    if lo:
        mask /= 1.0 + (lo / f) ** 4
    if hi:
        mask /= 1.0 + (f / hi) ** 4
    if tilt:
        mask /= np.maximum(f, 20.0) ** tilt
    return _norm(np.fft.irfft(spec * mask, n), 1.0)


def _attack(t, seconds):
    return np.minimum(t / seconds, 1.0)


def _lowpass(x, sr, cutoff):
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1.0 / sr)
    return np.fft.irfft(spec / (1.0 + (f / cutoff) ** 4), len(x))


def drone(sr, rng, detuned=False, dur=8.0):
    t = _t(sr, dur)
    lfo = 0.75 + 0.25 * np.sin(2 * np.pi * 0.25 * t)
    tone = (
        0.55 * np.sin(2 * np.pi * 55.0 * t)
        + 0.35 * np.sin(2 * np.pi * 82.5 * t)
        + 0.12 * np.sin(2 * np.pi * 110.0 * t + 1.3)
    )
    if detuned:
        tone += 0.4 * np.sin(2 * np.pi * 58.25 * t) + 0.22 * np.sin(2 * np.pi * 87.375 * t)
    n = len(t)
    left = tone * lfo + 0.22 * _band_noise(n, rng, sr, lo=30, hi=380)
    right = tone * lfo + 0.22 * _band_noise(n, rng, sr, lo=30, hi=380)
    return _norm(np.column_stack([left, right]), 0.9)


def ping(sr, f0=1200.0, f1=800.0, detune=1.0, vibrato=0.0, dur=1.3):
    t = _t(sr, dur)
    f = (f0 + (f1 - f0) * np.clip(t / 0.25, 0, 1)) * detune
    if vibrato:
        f = f * (1.0 + vibrato * np.sin(2 * np.pi * 7.0 * t))
    phase = 2 * np.pi * np.cumsum(f) / sr
    env = _attack(t, 0.004) * np.exp(-t * 6.0)
    x = np.sin(phase) * env + 0.25 * np.sin(2 * phase) * env * np.exp(-t * 10.0)
    out = x.copy()
    for delay, gain in ((0.19, 0.35), (0.38, 0.15), (0.57, 0.06)):
        k = int(delay * sr)
        out[k:] += x[: len(x) - k] * gain
    return _norm(out, 0.85)


def mimic(sr):
    return ping(sr, f0=1150.0, f1=760.0, detune=0.97, vibrato=0.012)


def footstep(sr, rng, loud=False):
    t = _t(sr, 0.11)
    n = _band_noise(len(t), rng, sr, lo=150, hi=3200 if loud else 1600)
    env = _attack(t, 0.002) * np.exp(-t * (45 if loud else 60))
    thump = np.sin(2 * np.pi * 85 * t) * np.exp(-t * 40)
    return _norm(n * env + 0.6 * thump * env, 0.9)


def heartbeat(sr):
    t = _t(sr, 0.55)

    def thump(t0, freq, amp):
        tt = np.clip(t - t0, 0, None)
        return (t >= t0) * amp * np.sin(2 * np.pi * freq * tt) * np.exp(-tt * 26) * _attack(tt, 0.006)

    return _norm(thump(0.0, 58, 1.0) + thump(0.21, 47, 0.75), 0.95)


def other_heart(sr):
    """Detak kedua milik Pengamat: jantung yang sama dengan pemain, tapi teredam."""
    return _lowpass(heartbeat(sr), sr, 180.0)


def drag(sr, rng, dur=3.0):
    t = _t(sr, dur)
    k = 1.0 / dur
    mod = 0.55 + 0.3 * np.sin(2 * np.pi * k * t) + 0.15 * np.sin(2 * np.pi * 3 * k * t + 1.1)
    body = _band_noise(len(t), rng, sr, lo=35, hi=320)
    grit = _band_noise(len(t), rng, sr, lo=900, hi=2500) * 0.12
    return _norm((body + grit) * mod, 0.85)


def breath(sr, rng, dur=4.0):
    t = _t(sr, dur)
    env = np.where(t < 1.6, np.sin(np.pi * t / 1.6), 0.0)
    env += np.where((t > 2.0) & (t < 3.8), 0.8 * np.sin(np.pi * (t - 2.0) / 1.8), 0.0)
    env = np.clip(env, 0, None) ** 1.5
    return _norm(_band_noise(len(t), rng, sr, lo=300, hi=1600) * env, 0.8)


def hum(sr, dur=2.0):
    t = _t(sr, dur)
    trem = 0.6 + 0.4 * np.sin(2 * np.pi * 5.0 * t)
    x = np.sin(2 * np.pi * 220 * t) + 0.6 * np.sin(2 * np.pi * 330 * t) + 0.2 * np.sin(2 * np.pi * 440 * t)
    return _norm(x * trem, 0.7)


def exit_hum(sr, dur=4.0):
    t = _t(sr, dur)
    x = np.sin(2 * np.pi * 41.25 * t) + 0.6 * np.sin(2 * np.pi * 82.5 * t) + 0.25 * np.sin(2 * np.pi * 123.75 * t)
    return _norm(x * (0.8 + 0.2 * np.sin(2 * np.pi * 0.5 * t)), 0.8)


def door(sr, rng):
    t = _t(sr, 2.4)
    boom = np.sin(2 * np.pi * 38 * t) * np.exp(-t * 2.2) * _attack(t, 0.02)
    rumble = _band_noise(len(t), rng, sr, hi=200) * np.exp(-t * 3.0) * 0.6
    creak = np.sin(2 * np.pi * (180 + 40 * np.sin(2 * np.pi * 3 * t)) * t) * np.exp(-((t - 0.5) ** 2) / 0.05) * 0.15
    return _norm(boom + rumble + creak, 0.85)


def chime(sr):
    t = _t(sr, 1.6)
    env = _attack(t, 0.006) * np.exp(-t * 3.0)
    x = np.sin(2 * np.pi * 880 * t) + 0.5 * np.sin(2 * np.pi * 1318.5 * t) + 0.2 * np.sin(2 * np.pi * 1760 * t)
    return _norm(x * env, 0.7)


def click(sr, rng, low=False):
    t = _t(sr, 0.05 if low else 0.03)
    n = rng.standard_normal(len(t)) * np.exp(-t * 400)
    tone = np.sin(2 * np.pi * (600 if low else 2000) * t) * np.exp(-t * (150 if low else 300))
    return _norm(n * 0.5 + tone, 0.8)


def dead_flashlight(sr, rng):
    """Seseorang mencoba menyalakan senter yang baterainya habis: klik... klik-klik."""
    one = click(sr, rng, low=True)
    room = np.zeros(int(0.25 * sr))
    room[: len(one)] = one
    for delay, gain in ((0.07, 0.3), (0.15, 0.12)):
        k = int(delay * sr)
        room[k:k + len(one)] += one * gain
    out = np.zeros(int(1.3 * sr))
    for t0, amp in ((0.0, 1.0), (0.72, 0.85), (0.95, 1.0)):
        k = int(t0 * sr)
        out[k:k + len(room)] += room[: len(out) - k] * amp
    return _norm(out, 0.8)


def stone(sr, rng):
    """Kerikil jatuh: tok, lalu memantul sekali-dua kali."""
    t = _t(sr, 0.5)

    def knock(t0, amp):
        tt = np.clip(t - t0, 0, None)
        env = (t >= t0) * np.exp(-tt * 70) * _attack(tt, 0.001)
        return amp * env * (0.6 * np.sin(2 * np.pi * 1300 * tt) + np.sin(2 * np.pi * 620 * tt))

    tok = knock(0.0, 1.0) + knock(0.16, 0.45) + knock(0.27, 0.2)
    grit = _band_noise(len(t), rng, sr, lo=600, hi=4000) * (
        np.exp(-t * 60) + 0.45 * (t >= 0.16) * np.exp(-np.clip(t - 0.16, 0, None) * 60)
    )
    return _norm(tok + 0.35 * grit, 0.8)


def crumble(sr, rng):
    """Dinding runtuh: dentum berat, lalu bebatuan berjatuhan."""
    t = _t(sr, 1.6)
    thud = np.sin(2 * np.pi * 45 * t + 2.0 * np.exp(-t * 20)) * np.exp(-t * 5) * _attack(t, 0.004)
    env = np.zeros_like(t)
    for _ in range(14):
        t0 = rng.uniform(0.05, 1.1)
        env += rng.uniform(0.2, 0.8) * (t >= t0) * np.exp(-np.clip(t - t0, 0, None) * 30)
    rubble = _band_noise(len(t), rng, sr, lo=120, hi=2500) * np.clip(env, 0, 1.2) * np.exp(-t * 1.2)
    return _norm(thud + 0.5 * rubble, 0.85)


def melody(sr):
    """Satu-satunya musik di GEMA: kotak musik pendek di ending, dengan gema seperti sonar."""
    phrase = [  # (detik, frekuensi, lama berdenging)
        (0.0, 659.3, 1.0), (0.45, 880.0, 1.0), (0.9, 1108.7, 1.0), (1.35, 987.8, 1.0), (1.8, 880.0, 1.4),
        (2.6, 659.3, 1.0), (3.05, 740.0, 1.0), (3.5, 880.0, 1.4), (4.3, 1318.5, 3.0),
    ]
    t = _t(sr, 7.5)
    out = np.zeros_like(t)
    for t0, f, ring in phrase:
        tt = np.clip(t - t0, 0, None)
        env = (t >= t0) * _attack(tt, 0.003) * np.exp(-tt * 2.2 / ring)
        tone = (np.sin(2 * np.pi * f * tt)
                + 0.35 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt * 6)
                + 0.12 * np.sin(2 * np.pi * 3.01 * f * tt) * np.exp(-tt * 9))
        out += env * tone
    wet = out.copy()
    for delay, gain in ((0.19, 0.3), (0.38, 0.14), (0.57, 0.06)):
        k = int(delay * sr)
        wet[k:] += out[: len(out) - k] * gain
    return _norm(wet, 0.8)


def battery(sr, rng):
    one = click(sr, rng)
    gap = np.zeros(int(sr * 0.06))
    return np.concatenate([one, gap, one * 0.8])


def grind(sr, rng):
    t = _t(sr, 1.8)
    env = np.sin(np.pi * t / t[-1]) ** 2
    rough = 0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 7 * t + np.sin(2 * np.pi * 1.3 * t) * 3))
    return _norm(_band_noise(len(t), rng, sr, lo=40, hi=220) * env * rough, 0.8)


def whisper(sr, rng):
    t = _t(sr, 1.3)
    env = np.zeros_like(t)
    pos = 0.05
    while pos < 1.2:
        width = rng.uniform(0.04, 0.1)
        env += rng.uniform(0.4, 1.0) * np.exp(-((t - pos) ** 2) / (2 * width ** 2))
        pos += rng.uniform(0.08, 0.2)
    env = np.clip(env, 0, 1)
    breathy = _band_noise(len(t), rng, sr, lo=1800, hi=5200)
    formant = _band_noise(len(t), rng, sr, lo=600, hi=1100) * 0.4
    return _norm((breathy + formant) * env, 0.8)


def impact(sr, rng):
    """Hantaman tumpul saat tertangkap: nada rendah yang cepat turun, ditambah remuk pendek."""
    t = _t(sr, 1.0)
    body = np.sin(2 * np.pi * 50 * t + 3.0 * np.exp(-t * 25)) * np.exp(-t * 6) * _attack(t, 0.003)
    crunch = _band_noise(len(t), rng, sr, lo=80, hi=900) * np.exp(-t * 20) * 0.6
    return _norm(body + crunch, 0.9)


def exhale(sr, rng):
    t = _t(sr, 1.4)
    env = np.sin(np.pi * t / t[-1]) ** 2 * np.exp(-t * 0.8)
    return _norm(_band_noise(len(t), rng, sr, lo=250, hi=1200) * env, 0.7)


def build_all(sr, seed=7):
    """Semua suara, dengan nama yang dipakai di config.VOLUME."""
    rng = np.random.default_rng(seed)
    return {
        "drone": drone(sr, rng),
        "drone_bad": drone(sr, rng, detuned=True),
        "ping": ping(sr),
        "title_ping": ping(sr, f0=1000.0, f1=700.0),
        "mimic": mimic(sr),
        "step": [footstep(sr, rng) for _ in range(3)],
        "step_run": [footstep(sr, rng, loud=True) for _ in range(3)],
        "heart": heartbeat(sr),
        "drag": drag(sr, rng),
        "breath": breath(sr, rng),
        "hum": hum(sr),
        "exit_hum": exit_hum(sr),
        "door": door(sr, rng),
        "chime": chime(sr),
        "click": click(sr, rng),
        "click_dead": click(sr, rng, low=True),
        "battery": battery(sr, rng),
        "grind": grind(sr, rng),
        "whisper": [whisper(sr, rng) for _ in range(3)],
        "impact": impact(sr, rng),
        "exhale": exhale(sr, rng),
        # suara baru ditaruh di akhir supaya suara lama tetap sama (rng dipakai berurutan)
        "heart_other": other_heart(sr),
        "dead_flashlight": dead_flashlight(sr, rng),
        "stone": stone(sr, rng),
        "crumble": crumble(sr, rng),
        "melody": melody(sr),
    }
