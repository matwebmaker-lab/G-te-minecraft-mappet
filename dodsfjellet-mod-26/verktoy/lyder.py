"""Syntetiserer gevær-lydene (skudd, omlading, tomt magasin) og koder dem til mono .ogg med ffmpeg.

    python verktoy/lyder.py

Skudd = skarpt smell (filtrert støy) + dyp trykkbølge (synkende sinus) + rom-ekko (lang, mørk støyhale).
"""
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

HER = Path(__file__).resolve().parent.parent
LYD = HER / "src" / "main" / "resources" / "assets" / "dodsfjellet" / "sounds"
SR = 44100
FFMPEG = shutil.which("ffmpeg") or r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\ffmpeg.exe"


def t(sek):
    return np.arange(int(SR * sek)) / SR


def lavpass(x, fc):
    """Enkel 2-polet lavpass (to ganger én-polet)."""
    a = np.exp(-2 * np.pi * fc / SR)
    for _ in range(2):
        y = np.empty_like(x)
        s = 0.0
        for i, v in enumerate(x):
            s = (1 - a) * v + a * s
            y[i] = s
        x = y
    return x


def hoypass(x, fc):
    return x - lavpass(x, fc)


def skudd(rng, smell=1.0, boom=1.0, boom_hz=(140, 45), hale=0.6, hale_fc=900, klang=2500, lengde=1.4, ekko=0.0):
    n = t(lengde)
    stoy = rng.standard_normal(len(n))
    # 1) smellet: bredbåndet støy som dør ut på ~8 ms, med litt skarpere "crack"
    smell_env = np.exp(-n / 0.008)
    crack = hoypass(stoy, klang) * smell_env * 1.6 * smell
    kropp = lavpass(stoy, 3500) * np.exp(-n / 0.025) * 1.2 * smell
    # 2) trykkbølgen: synkende sinus
    f = boom_hz[1] + (boom_hz[0] - boom_hz[1]) * np.exp(-n / 0.05)
    fase = 2 * np.pi * np.cumsum(f) / SR
    trykk = np.sin(fase) * np.exp(-n / 0.12) * boom * 1.4
    # 3) halen: rommet/landskapet som svarer
    hale_s = lavpass(rng.standard_normal(len(n)), hale_fc) * np.exp(-n / (lengde * 0.28)) * hale
    hale_s *= np.clip(n / 0.015, 0, 1)
    sig = crack + kropp + trykk + hale_s
    if ekko:
        d = int(SR * 0.23)
        sig[d:] += sig[:-d] * ekko
        d2 = int(SR * 0.51)
        sig[d2:] += lavpass(sig[:-d2], 1200) * ekko * 0.6
    sig = np.tanh(sig * 1.6)                    # metning som et ekte opptak
    return sig


def klikk(rng, hz=3200, tid=0.004, styrke=1.0, metall=True, lengde=0.12):
    n = t(lengde)
    s = hoypass(rng.standard_normal(len(n)), 1500) * np.exp(-n / tid)
    if metall:
        for h, d in ((hz, 0.02), (hz * 1.47, 0.015), (hz * 2.3, 0.01)):
            s += np.sin(2 * np.pi * h * n) * np.exp(-n / d) * 0.35
    return s * styrke


def glid(rng, lengde=0.18, fc=2500, styrke=0.5):
    n = t(lengde)
    env = np.sin(np.pi * n / lengde) ** 0.6
    return lavpass(hoypass(rng.standard_normal(len(n)), 900), fc) * env * styrke


def sett_sammen(deler, total):
    ut = np.zeros(int(SR * total))
    for tid, lyd in deler:
        i = int(SR * tid)
        j = min(len(ut), i + len(lyd))
        ut[i:j] += lyd[:j - i]
    return ut


def normaliser(x, topp=0.9):
    x = x - np.mean(x)
    return x / (np.max(np.abs(x)) + 1e-9) * topp


def lag_alle():
    rng = np.random.default_rng(7)
    lyder = {}
    lyder["pistol_skudd"] = [skudd(rng, smell=1.1, boom=0.7, boom_hz=(180, 70), hale=0.35, hale_fc=1400, klang=3000, lengde=0.9)
                             for _ in range(3)]
    lyder["hagle_skudd"] = [skudd(rng, smell=1.0, boom=1.6, boom_hz=(110, 38), hale=0.75, hale_fc=700, klang=1800, lengde=1.6, ekko=0.25)
                            for _ in range(3)]
    lyder["automatgevaer_skudd"] = [skudd(rng, smell=1.3, boom=1.0, boom_hz=(150, 55), hale=0.45, hale_fc=1100, klang=2600, lengde=0.8)
                                    for _ in range(4)]
    lyder["snikskyttergevaer_skudd"] = [skudd(rng, smell=1.6, boom=1.5, boom_hz=(130, 40), hale=0.9, hale_fc=800, klang=2200,
                                              lengde=2.4, ekko=0.35) for _ in range(2)]
    lyder["tom"] = [klikk(rng, 2600, 0.003, 0.8, lengde=0.1)]
    lyder["omlad_pistol"] = [sett_sammen([(0.0, klikk(rng, 2100, 0.004)), (0.05, glid(rng, 0.12, 1800, 0.3)),
                                          (0.42, klikk(rng, 1700, 0.006, 1.2)), (0.62, glid(rng, 0.1, 3000, 0.5)),
                                          (0.72, klikk(rng, 3000, 0.003, 1.3))], 0.9)]
    lyder["omlad_automat"] = [sett_sammen([(0.0, klikk(rng, 1900, 0.005)), (0.08, glid(rng, 0.2, 1500, 0.3)),
                                           (0.55, klikk(rng, 1500, 0.008, 1.3)), (0.85, glid(rng, 0.14, 2600, 0.5)),
                                           (0.98, klikk(rng, 2800, 0.004, 1.4))], 1.2)]
    lyder["omlad_hagle"] = [sett_sammen([(0.0, glid(rng, 0.12, 1600, 0.5)), (0.12, klikk(rng, 1400, 0.006, 1.1)),
                                         (0.22, glid(rng, 0.12, 1800, 0.5)), (0.33, klikk(rng, 1800, 0.005, 1.3))], 0.6)]
    lyder["omlad_snikskytter"] = [sett_sammen([(0.0, klikk(rng, 2400, 0.004, 1.0)), (0.08, glid(rng, 0.16, 2200, 0.45)),
                                               (0.3, glid(rng, 0.16, 2400, 0.45)), (0.48, klikk(rng, 2000, 0.006, 1.3))], 0.7)]
    lyder["pumpe"] = lyder["omlad_hagle"]
    return lyder


def main():
    if LYD.exists():
        shutil.rmtree(LYD)
    (LYD / "gevaer").mkdir(parents=True)
    lyder = lag_alle()
    sounds = {}
    with tempfile.TemporaryDirectory() as tmp:
        for navn, varianter in lyder.items():
            filer = []
            for i, sig in enumerate(varianter):
                wav = Path(tmp) / f"{navn}_{i}.wav"
                ogg = LYD / "gevaer" / f"{navn}_{i}.ogg"
                sf.write(wav, normaliser(sig).astype(np.float32), SR)
                subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(wav), "-ac", "1", "-c:a", "libvorbis", "-q:a", "5", str(ogg)],
                               check=True)
                filer.append(f"dodsfjellet:gevaer/{navn}_{i}")
            sounds[f"gevaer.{navn}"] = {"sounds": filer, "subtitle": f"subtitles.dodsfjellet.gevaer.{navn}"}
    (LYD.parent / "sounds.json").write_text(json.dumps(sounds, indent=1))
    print(f"{sum(len(v) for v in lyder.values())} lydfiler, {len(sounds)} lydhendelser")


if __name__ == "__main__":
    main()
