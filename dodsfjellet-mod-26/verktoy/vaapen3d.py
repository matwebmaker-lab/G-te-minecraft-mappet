"""3D-våpen for Dødsfjellet: definert som klosser (Minecraft-modellelementer).

Samme data brukes til:
  1. Minecraft item-modeller (assets/dodsfjellet/models/item/<navn>_3d.json) med eget teksturatlas
  2. Forhåndsvisning og ikon-render i Blender (via Blender MCP, se blender_bygg.py)

Kjør:  python verktoy/vaapen3d.py
"""
import json
import math
import random
from pathlib import Path

from PIL import Image

HER = Path(__file__).resolve().parent.parent
ASSETS = HER / "src" / "main" / "resources" / "assets" / "dodsfjellet"
UT_JSON = HER / "verktoy" / "vaapen3d.json"   # leses av Blender-skriptet

# Materialer: navn -> (palett mørk..lys, lys-utslipp 0..15)
MATERIALER = {
    "ved": ([(20, 13, 16), (40, 27, 32), (62, 44, 52), (80, 60, 68)], 0),
    "laer": ([(25, 10, 12), (55, 20, 22), (85, 34, 32), (110, 50, 44)], 0),
    "stal": ([(18, 16, 24), (36, 33, 46), (58, 55, 72), (88, 86, 104)], 0),
    "egg": ([(120, 130, 150), (170, 185, 205), (210, 225, 240), (245, 250, 255)], 0),
    "gull": ([(90, 55, 8), (160, 110, 20), (220, 170, 50), (255, 225, 120)], 0),
    "sjel": ([(70, 20, 130), (130, 70, 220), (130, 220, 255), (235, 250, 255)], 15),
    "blod": ([(60, 4, 10), (120, 12, 24), (190, 40, 40), (240, 110, 80)], 9),
    "ben": ([(150, 140, 120), (190, 182, 160), (220, 214, 195), (245, 240, 225)], 0),
}
MAT_INDEKS = {m: i for i, m in enumerate(MATERIALER)}   # rute i et 4x4-rutenett (64x64 px)


def boks(fra, til, mat):
    return {"from": list(fra), "to": list(til), "mat": mat}


# ---------------------------------------------------------------- modellene (enheter: 16 = én blokk)
def sjelesigd():
    b = [
        boks((7.25, -6, 7.25), (8.75, 26, 8.75), "ved"),          # skaft
        boks((7.0, 2, 7.0), (9.0, 4.5, 9.0), "laer"),             # grep
        boks((7.0, 8, 7.0), (9.0, 10, 9.0), "laer"),
        boks((7.0, -7, 7.0), (9.0, -5.5, 9.0), "gull"),           # endeknott
        boks((6.75, 26, 6.75), (9.25, 27.5, 9.25), "gull"),       # topphette
        boks((6.4, 22.5, 7.4), (9.6, 25.5, 8.6), "sjel"),         # sjelekrystall i leddet
    ]
    # bladet: buer seg utover og nedover til venstre
    segmenter = [((1.0, 23.0), (7.25, 25.5)), ((-3.5, 22.0), (1.0, 24.6)), ((-7.5, 20.4), (-3.5, 23.2)),
                 ((-10.5, 18.4), (-7.5, 21.4)), ((-12.8, 16.2), (-10.5, 19.0)), ((-14.2, 14.2), (-12.8, 16.6))]
    for (x1, y1), (x2, y2) in segmenter:
        b.append(boks((x1, y1 + 0.6, 7.6), (x2, y2, 8.4), "stal"))
        b.append(boks((x1, y1, 7.75), (x2, y1 + 0.6, 8.25), "egg"))   # skarp egg på undersiden
    b.append(boks((-3.0, 23.3, 7.5), (0.5, 23.9, 8.5), "sjel"))      # glødende rune i bladet
    return b


def dodsklinge():
    b = [
        boks((7.0, 12, 7.5), (9.0, 30.5, 8.5), "stal"),           # blad
        boks((6.3, 12, 7.7), (7.0, 30, 8.3), "egg"),
        boks((9.0, 12, 7.7), (9.7, 30, 8.3), "egg"),
        boks((7.5, 30.5, 7.6), (8.5, 32, 8.4), "egg"),            # spiss
        boks((7.75, 13, 7.4), (8.25, 28.5, 8.6), "sjel"),         # glødende rille
        boks((3.0, 10.5, 7.0), (13.0, 12.0, 9.0), "gull"),        # parerstang
        boks((1.8, 10.0, 6.8), (3.2, 12.6, 9.2), "blod"),
        boks((12.8, 10.0, 6.8), (14.2, 12.6, 9.2), "blod"),
        boks((7.4, 5.0, 7.4), (8.6, 10.5, 8.6), "laer"),          # grep
        boks((7.0, 3.4, 7.0), (9.0, 5.0, 9.0), "sjel"),           # krystall-knott
    ]
    return b


def vokterknuser():
    b = [
        boks((7.3, -2, 7.3), (8.7, 22, 8.7), "ved"),              # skaft
        boks((7.1, 3, 7.1), (8.9, 9.5, 8.9), "laer"),             # grep
        boks((7.0, -3.5, 7.0), (9.0, -2, 9.0), "gull"),
        boks((7.1, 14, 7.1), (8.9, 15.2, 8.9), "gull"),
        boks((2.0, 21.0, 5.0), (14.0, 27.0, 11.0), "stal"),       # hammerhode
        boks((1.4, 21.6, 5.6), (2.0, 26.4, 10.4), "gull"),        # slagflater
        boks((14.0, 21.6, 5.6), (14.6, 26.4, 10.4), "gull"),
        boks((2.0, 23.4, 4.6), (14.0, 24.6, 11.4), "blod"),       # glødende kjerne rundt hodet
        boks((7.0, 27.0, 7.0), (9.0, 29.0, 9.0), "ben"),          # pigger
        boks((4.0, 27.0, 7.4), (5.2, 28.2, 8.6), "ben"),
        boks((10.8, 27.0, 7.4), (12.0, 28.2, 8.6), "ben"),
    ]
    return b


VAAPEN = {"sjelesigd": sjelesigd(), "dodsklinge": dodsklinge(), "vokterknuser": vokterknuser()}

VISNING = {   # hvordan våpnet holdes; store våpen skaleres ned
    "thirdperson_righthand": {"rotation": [0, -90, 55], "translation": [0, 6.5, 1.2], "scale": [0.62, 0.62, 0.62]},
    "thirdperson_lefthand": {"rotation": [0, 90, -55], "translation": [0, 6.5, 1.2], "scale": [0.62, 0.62, 0.62]},
    "firstperson_righthand": {"rotation": [0, -90, 25], "translation": [1.13, 3.4, 1.13], "scale": [0.34, 0.34, 0.34]},
    "firstperson_lefthand": {"rotation": [0, 90, -25], "translation": [1.13, 3.4, 1.13], "scale": [0.34, 0.34, 0.34]},
    "ground": {"rotation": [0, 0, 0], "translation": [0, 2, 0], "scale": [0.3, 0.3, 0.3]},
    "fixed": {"rotation": [0, 180, 0], "translation": [0, 0, 0], "scale": [0.5, 0.5, 0.5]},
    "head": {"rotation": [0, 180, 0], "translation": [0, 13, 7], "scale": [0.6, 0.6, 0.6]},
}


def atlas(frø):
    """64x64 tekstur: én 16x16-rute per materiale med skygge og støy."""
    r = random.Random(frø)
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    px = img.load()
    for mat, (pal, _) in MATERIALER.items():
        i = MAT_INDEKS[mat]
        ox, oy = (i % 4) * 16, (i // 4) * 16
        for y in range(16):
            for x in range(16):
                t = 0.55 + 0.25 * math.sin((x + y * 0.6) * 0.7) + (r.random() - 0.5) * 0.35
                if mat in ("ved", "laer"):
                    t = 0.5 + 0.35 * math.sin(y * 1.3 + r.random()) + (r.random() - 0.5) * 0.2
                if x in (0, 15) or y in (0, 15):
                    t -= 0.25
                t = max(0.0, min(0.999, t)) * (len(pal) - 1)
                k = int(t)
                f = t - k
                a, b = pal[k], pal[k + 1]
                px[ox + x, oy + y] = tuple(int(a[c] + (b[c] - a[c]) * f) for c in range(3)) + (255,)
    return img


def modell_json(navn, bokser):
    elementer = []
    for b in bokser:
        i = MAT_INDEKS[b["mat"]]
        u, v = (i % 4) * 4, (i // 4) * 4
        uv = [u + 0.25, v + 0.25, u + 3.75, v + 3.75]
        e = {"from": b["from"], "to": b["to"],
             "faces": {f: {"uv": uv, "texture": "#t"} for f in ("north", "east", "south", "west", "up", "down")}}
        lys = MATERIALER[b["mat"]][1]
        if lys:
            e["light_emission"] = lys
        elementer.append(e)
    return {"texture_size": [64, 64],
            "textures": {"t": f"dodsfjellet:item/{navn}_atlas", "particle": f"dodsfjellet:item/{navn}_atlas"},
            "elements": elementer, "display": VISNING}


def main():
    (ASSETS / "models" / "item").mkdir(parents=True, exist_ok=True)
    (ASSETS / "textures" / "item").mkdir(parents=True, exist_ok=True)
    blender = {}
    for n, (navn, bokser) in enumerate(VAAPEN.items()):
        tekstur = atlas(100 + n)
        tekstur.save(ASSETS / "textures" / "item" / f"{navn}_atlas.png")
        (ASSETS / "models" / "item" / f"{navn}_3d.json").write_text(json.dumps(modell_json(navn, bokser), indent=1))
        blender[navn] = [{"from": b["from"], "to": b["to"], "farge": [c / 255 for c in MATERIALER[b["mat"]][0][2]],
                          "lys": MATERIALER[b["mat"]][1]} for b in bokser]
    UT_JSON.write_text(json.dumps(blender))
    print("Modeller:", ", ".join(VAAPEN), "->", UT_JSON)


if __name__ == "__main__":
    main()
