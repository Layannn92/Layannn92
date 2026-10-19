"""Mixe voix + bruitages + petite musique de fond : python3 tools/audio.py plan.json sortie.wav"""
import json, subprocess, sys, wave
import numpy as np

SR = 44100
SFX_BY_SCENE = ['pop', None, 'rumble', 'blip', 'thud', None, 'chalk', 'roar', 'siren',
                'boom', 'laugh', 'shine', 'wind', 'blip', None, 'xp', 'levelup']
rng = np.random.default_rng(7)


def env(n, attack=0.005):
    e = np.exp(np.linspace(0, -7, n))
    a = max(1, int(attack * SR))
    e[:a] *= np.linspace(0, 1, a)
    return e


def tone(f1, f2, dur, kind='square', vol=.12):
    n = int(dur * SR)
    f = f1 * (f2 / f1) ** (np.arange(n) / n)
    ph = 2 * np.pi * np.cumsum(f) / SR
    w = {'sine': np.sin(ph), 'square': np.sign(np.sin(ph)),
         'saw': 2 * ((ph / (2 * np.pi)) % 1) - 1,
         'tri': 2 * np.abs(2 * ((ph / (2 * np.pi)) % 1) - 1) - 1}[kind]
    return w * env(n) * vol


def noise(dur, vol=.4, cutoff=800):
    n = int(dur * SR)
    x = rng.uniform(-1, 1, n)
    a = np.exp(-2 * np.pi * cutoff / SR)          # passe-bas 1 pôle
    y = np.empty(n); acc = 0.0
    for i in range(n):
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    y /= max(1e-6, np.abs(y).max())
    return y * env(n) * vol


def at(buf, sig, t):
    i = int(t * SR)
    j = min(len(buf), i + len(sig))
    if i < len(buf):
        buf[i:j] += sig[:j - i]


def sfx(name, buf, t):
    if name == 'pop':     at(buf, tone(300, 900, .15, 'sine', .3), t + .6)
    if name == 'blip':    at(buf, tone(880, 880, .08, 'square', .08), t); at(buf, tone(1320, 1320, .08, 'square', .08), t + .1)
    if name == 'rumble':  at(buf, noise(2.5, .5, 160), t)
    if name == 'thud':    at(buf, noise(.5, .6, 220), t + .9); at(buf, tone(120, 40, .4, 'sine', .5), t + .9)
    if name == 'chalk':
        for k in range(4): at(buf, noise(.12, .12, 3000), t + .3 + k * .3)
    if name == 'roar':    at(buf, noise(1, .5, 500), t + .5); at(buf, tone(160, 70, 1, 'saw', .15), t + .5)
    if name == 'siren':
        for k in range(4): at(buf, tone(600, 1100, .5, 'saw', .06), t + k); at(buf, tone(1100, 600, .5, 'saw', .06), t + k + .5)
    if name == 'boom':    at(buf, noise(1.8, .9, 400), t); at(buf, tone(90, 30, 1.5, 'sine', .7), t)
    if name == 'laugh':
        for k in (0, .18, .36): at(buf, tone(500, 380, .14, 'tri', .12), t + k)
    if name == 'shine':
        for k in range(4): at(buf, tone(1200 + k * 300, 1600 + k * 300, .25, 'sine', .08), t + .6 + k * .08)
    if name == 'wind':    at(buf, noise(4, .15, 600), t)
    if name == 'xp':
        for k in range(10): at(buf, tone(400 + k * 60, 420 + k * 60, .07, 'square', .05), t + 1.2 + k * .22)
    if name == 'levelup':
        for k, f in enumerate((523, 659, 784, 1047)): at(buf, tone(f, f, .22, 'square', .1), t + 1.4 + k * .14)
        at(buf, tone(1047, 1568, .6, 'tri', .14), t + 2)


def music(total):
    """Boucle chiptune discrète à 132 bpm (basse + charleston)."""
    buf = np.zeros(int(total * SR))
    beat = 60 / 132
    bass = [110, 110, 131, 147, 110, 110, 165, 147]
    t, k = 0.0, 0
    while t < total:
        at(buf, tone(bass[k % 8], bass[k % 8], beat * .9, 'tri', .10), t)
        at(buf, noise(.04, .025, 6000), t + beat / 2)
        if k % 2 == 0: at(buf, tone(150, 45, .18, 'sine', .25), t)
        t += beat; k += 1
    return buf


def load(path):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def main(plan_path, out):
    plan = json.load(open(plan_path))
    total = plan[-1]['start'] + plan[-1]['dur']
    fx = np.zeros(int(total * SR) + SR)
    vo = np.zeros_like(fx)
    for sc in plan:
        if sc['i'] > 0: at(fx, noise(.25, .08, 2500), sc['start'] - .05)   # whoosh de transition
        if SFX_BY_SCENE[sc['i']]: sfx(SFX_BY_SCENE[sc['i']], fx, sc['start'])
        if sc['voice']: at(vo, load(sc['voice']) * 1.0, sc['start'] + 0.45)
    bg = np.zeros_like(fx); m = music(total); bg[:len(m)] = m
    # la musique baisse quand quelqu'un parle
    talk = np.convolve(np.abs(vo) > .02, np.ones(SR // 5) / (SR // 5), 'same')
    bg *= 1 - .6 * np.clip(talk * 4, 0, 1)
    mix = vo * 1.1 + fx * .8 + bg * .7
    mix = mix[:int(total * SR)]
    mix /= max(1.0, np.abs(mix).max() / .95)
    with wave.open(out, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype('<i2').tobytes())


if __name__ == '__main__':
    main(*sys.argv[1:3])
