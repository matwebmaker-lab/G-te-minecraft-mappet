"""Gevær for Dødsfjellet: pistol, hagle, automatgevær og snikskyttergevær.

Modellene er bygget av klosser (Minecraft-modellelementer, med vilkårlig rotasjon) og brukes til:
  1. item-modellene i hånda (assets/dodsfjellet/models/item/<navn>_3d.json) med et felles 128x128 materialatlas
  2. Blender (blender_gevaer.py via Blender MCP), som rendrer realistiske ikoner med metall, tre og avrundede kanter

Koordinater: x = bredde (midt = 8), y = opp, z = langs løpet (munningen mot -z / nord). Grense: -16..32.

Kjør:  python verktoy/gevaer3d.py
"""
import json
import math
import random
from pathlib import Path

from PIL import Image

HER = Path(__file__).resolve().parent.parent
ASSETS = HER / "src" / "main" / "resources" / "assets" / "dodsfjellet"
UT_JSON = HER / "verktoy" / "gevaer3d.json"

# navn -> (palett mørk..lys, lys-utslipp, blender: (metallisk, ruhet))
MAT = {
    "svart": ([(14, 14, 16), (26, 26, 29), (38, 38, 42), (52, 52, 57)], 0, (0.0, 0.55)),       # polymer
    "stal": ([(16, 17, 21), (30, 32, 38), (48, 51, 59), (72, 76, 86)], 0, (1.0, 0.38)),       # blånert stål
    "slede": ([(30, 31, 34), (46, 47, 51), (62, 63, 68), (84, 85, 90)], 0, (0.9, 0.45)),      # parkerisert
    "hull": ([(3, 3, 4), (7, 7, 8), (10, 10, 11), (14, 14, 15)], 0, (0.5, 0.8)),
    "tre": ([(58, 28, 14), (86, 44, 22), (112, 62, 32), (140, 82, 46)], 0, (0.0, 0.45)),      # valnøtt
    "tre_mork": ([(32, 16, 8), (48, 26, 14), (64, 36, 20), (82, 48, 28)], 0, (0.0, 0.5)),
    "messing": ([(110, 74, 24), (160, 118, 42), (206, 164, 70), (240, 210, 120)], 0, (1.0, 0.3)),
    "gummi": ([(10, 10, 10), (17, 17, 18), (24, 24, 26), (32, 32, 34)], 0, (0.0, 0.9)),
    "linse": ([(10, 22, 40), (24, 52, 90), (50, 100, 150), (120, 180, 230)], 3, (0.2, 0.05)),
    "gronn": ([(40, 180, 60), (80, 230, 90), (150, 255, 140), (210, 255, 200)], 12, (0.0, 0.3)),
    "oliven": ([(36, 40, 26), (52, 57, 38), (68, 74, 50), (86, 92, 64)], 0, (0.0, 0.7)),
    "magasin": ([(22, 22, 25), (34, 34, 38), (48, 48, 53), (64, 64, 70)], 0, (0.8, 0.5)),
    "hylse": ([(90, 10, 10), (130, 18, 16), (170, 32, 26), (205, 60, 46)], 0, (0.0, 0.4)),     # haglpatron
    "bakelitt": ([(52, 22, 12), (76, 34, 18), (100, 48, 26), (124, 64, 36)], 0, (0.0, 0.35)),
    "sikte": ([(200, 30, 20), (240, 60, 40), (255, 110, 80), (255, 190, 160)], 14, (0.0, 0.3)),
    "kobber": ([(90, 40, 20), (150, 70, 36), (200, 110, 64), (235, 160, 110)], 0, (1.0, 0.3)),
}
MAT_INDEKS = {m: i for i, m in enumerate(MAT)}
assert len(MAT) <= 16


def b(fra, til, mat, rot=None):
    """rot = (akse, vinkel, origo)"""
    e = {"from": [round(v, 3) for v in fra], "to": [round(v, 3) for v in til], "mat": mat}
    if rot:
        e["rot"] = {"axis": rot[0], "angle": rot[1], "origin": list(rot[2])}
    return e


def bred(x, y1, y2, z1, z2, mat, rot=None, x0=8.0):
    """Symmetrisk klosse rundt midtlinja x0 med halv bredde x."""
    return b((x0 - x, y1, z1), (x0 + x, y2, z2), mat, rot)


def kile(x, z0, z1, topp0, topp1, bunn0, bunn1, mat):
    """Skrå kolbe: trapes i sideprofil (topp- og bunnlinje), laget av to roterte klosser som overlapper."""
    tykk = min(topp0 - bunn0, topp1 - bunn1) * 0.98
    ut = []
    for kant, slutt, ned in ((topp0, topp1, True), (bunn0, bunn1, False)):
        stigning = (slutt - kant) / (z1 - z0)
        vinkel = -math.degrees(math.atan(stigning))
        lengde = (z1 - z0) / math.cos(math.radians(vinkel))
        y1, y2 = (kant - tykk, kant) if ned else (kant, kant + tykk)
        ut.append(bred(x if ned else x - 0.03, y1, y2, z0, z0 + lengde, mat, ("x", round(vinkel, 2), (8, kant, z0))))   # ingen like flater
    return ut


# ===================================================================== PISTOL (Glock-aktig, 1 enhet ≈ 1 cm)
def pistol():
    g = []
    gr = ("x", -18, (8, 8.2, 15))                                   # grepvinkel
    g += [bred(1.3, 9.6, 12.8, 0, 18.5, "slede"),                   # sleden
          b((9.3, 11.3, 4.8), (9.34, 12.5, 8.6), "hull"),           # utkastport (høyre)
          bred(0.6, 10.5, 11.9, -0.3, 0, "stal"),                   # løpsmunning
          bred(0.3, 10.9, 11.5, -0.35, -0.3, "hull"),
          bred(0.3, 12.8, 13.5, 1.0, 2.0, "svart"),                 # siktekorn
          bred(0.15, 13.1, 13.4, 0.95, 1.0, "gronn"),
          b((6.9, 12.8, 16.4), (7.6, 13.6, 18.0), "svart"),         # bakre sikte, to tapper
          b((8.4, 12.8, 16.4), (9.1, 13.6, 18.0), "svart"),
          b((7.6, 12.8, 16.4), (8.4, 13.1, 18.0), "svart"),
          b((7.05, 13.15, 16.38), (7.35, 13.45, 16.4), "gronn"),
          b((8.65, 13.15, 16.38), (8.95, 13.45, 16.4), "gronn")]
    for z in (14.4, 15.2, 16.0, 16.8):                              # grep-riller på sleden
        g.append(bred(1.36, 10.0, 12.3, z, z + 0.35, "stal"))
    g += [bred(1.1, 8.2, 9.6, 1.0, 17.5, "svart"),                  # ramme
          bred(1.0, 7.6, 8.2, 1.5, 6.5, "svart"),                   # skinne
          bred(1.05, 7.65, 7.85, 2.5, 3.0, "gummi"),
          bred(1.05, 7.65, 7.85, 4.0, 4.5, "gummi"),
          bred(0.7, 5.4, 6.0, 6.5, 11.6, "svart"),                  # avtrekkerbøyle
          bred(0.7, 5.4, 8.2, 6.0, 6.6, "svart"),
          bred(0.3, 6.2, 8.2, 9.0, 9.6, "stal", ("x", 15, (8, 8.2, 9.3))),   # avtrekker
          bred(1.15, -2.6, 9.4, 12.6, 17.3, "svart", gr),            # grep
          bred(1.2, -1.6, 6.6, 13.1, 16.8, "gummi", gr),           # rubbet grepflate
          bred(1.0, 8.0, 9.0, 17.5, 18.6, "svart"),                 # bakstropp
          bred(1.25, -3.3, -2.6, 12.3, 17.5, "svart", gr),           # magasinbunn
          b((9.3, 9.0, 9.0), (9.45, 9.6, 12.0), "stal"),            # sledestopper
          b((9.1, 8.6, 7.0), (9.2, 9.2, 8.5), "stal"),
          b((9.2, 7.4, 11.5), (9.35, 8.2, 12.5), "svart")]          # magasinutløser
    return g


# ===================================================================== HAGLE (pumpehagle, 1 enhet ≈ 2,2 cm)
def hagle():
    g = [bred(0.7, 12.2, 13.6, -16, 12, "stal"),                    # løp
         bred(0.4, 12.5, 13.3, -16.05, -16, "hull"),
         bred(0.4, 13.6, 13.8, -15, 12, "stal"),                    # ventilert skinne
         bred(0.2, 13.8, 14.2, -15, -14.4, "messing"),              # perlekorn
         bred(0.65, 10.6, 12.0, -14, 12, "stal"),                   # magasinrør
         bred(0.8, 10.4, 12.2, -15, -14, "stal"),
         bred(0.8, 10.4, 13.7, -12, -11, "stal"),                   # løpsklemme
         bred(0.4, 9.6, 10.4, -13, -12.4, "stal"),                  # reimfeste
         bred(1.2, 9.8, 12.3, -6, 4, "tre")]                        # pumpe
    for z in (-5.2, -3.4, -1.6, 0.2, 2.0):
        g.append(bred(1.25, 10.3, 11.8, z, z + 0.5, "tre_mork"))
    g += [bred(1.1, 9.4, 14.2, 12, 22, "stal"),                     # låskasse
          b((9.1, 11.5, 13.5), (9.15, 13.5, 18), "hull"),           # utkastport
          bred(0.7, 9.35, 9.4, 13, 18, "hull"),                     # ladeport
          bred(0.6, 7.0, 7.6, 16, 21, "stal"),                      # avtrekkerbøyle
          bred(0.6, 7.0, 9.4, 15.6, 16.2, "stal"),
          bred(0.25, 7.8, 9.4, 18, 18.6, "stal", ("x", 12, (8, 9.4, 18.3))),
          b((6.4, 10.0, 13), (6.9, 12.6, 18), "svart")]             # patronholder venstre side
    for z in (13.3, 14.5, 15.7, 16.9):
        g += [b((6.1, 10.4, z), (6.4, 12.2, z + 1.0), "hylse"),
              b((6.1, 10.15, z), (6.4, 10.4, z + 1.0), "messing")]
    g += kile(1.05, 21.5, 31.2, 13.4, 12.4, 9.2, 4.6, "tre")         # kolbe
    g += [bred(1.1, 4.4, 12.6, 31.0, 31.9, "gummi", ("x", -6, (8, 12.6, 31.0)))]
    return g


# ===================================================================== AUTOMATGEVÆR (AK-aktig, 1 enhet ≈ 1,85 cm)
def automatgevaer():
    g = [bred(0.75, 14.0, 15.5, -16, -13.5, "stal"),                # munningsbrems
         bred(0.8, 14.9, 15.3, -15.5, -14, "hull"),
         bred(0.45, 14.3, 15.2, -16.05, -16, "hull"),
         bred(0.55, 14.2, 15.3, -13.5, -2, "stal"),                 # løp
         bred(0.8, 13.6, 16.0, -11, -9.8, "stal"),                  # kornholder
         b((7.0, 15.5, -11), (7.3, 17.6, -10.2), "stal"),
         b((8.7, 15.5, -11), (9.0, 17.6, -10.2), "stal"),
         bred(0.15, 15.5, 17.2, -10.8, -10.4, "stal"),
         bred(0.4, 13.0, 13.6, -10.8, -9, "stal"),                  # bajonettfeste
         bred(0.7, 15.6, 16.9, -9.8, 1, "stal"),                    # gassrør
         bred(0.9, 13.8, 17.0, -9.8, -8.2, "stal"),                 # gassblokk
         bred(0.9, 15.5, 17.2, -4, 2, "tre"),                       # øvre håndvern
         bred(1.2, 12.2, 15.6, -6, 2, "tre"),                       # nedre håndvern
         bred(1.25, 12.0, 15.8, -6.6, -6, "stal"),
         bred(1.25, 13.0, 13.3, -5, 1, "tre_mork"),
         bred(1.25, 14.2, 14.5, -5, 1, "tre_mork"),
         bred(1.2, 11.0, 15.8, 2, 16, "stal"),                      # låskasse
         bred(1.0, 15.8, 16.6, 5, 16.5, "stal"),                    # støvdeksel
         bred(0.9, 15.8, 17.0, 2, 4.5, "stal"),                     # bakre sikte
         bred(0.8, 17.0, 17.4, 2.2, 4.5, "stal", ("x", 4, (8, 17, 4.5))),
         b((9.2, 14.5, 5.5), (10.3, 15.3, 6.5), "stal"),            # ladehåndtak
         b((9.2, 12.8, 8), (9.35, 14.6, 15.5), "stal"),             # velger
         b((9.2, 13.6, 6.5), (9.25, 15.4, 11.5), "hull"),           # utkastport
         bred(0.6, 8.6, 9.2, 10.5, 15, "stal"),                     # avtrekkerbøyle
         bred(0.6, 8.6, 11.0, 10.2, 10.8, "stal"),
         bred(0.25, 9.2, 11.0, 12.5, 13.1, "stal", ("x", 12, (8, 11, 12.8))),
         bred(0.9, 4.0, 11.2, 14.5, 18, "bakelitt", ("x", -20, (8, 11, 16)))]   # pistolgrep
    # bananmagasin: kjedede segmenter som krummer forover
    y, z, d = 11.0, 8.25, 3.5
    for vinkel, lengde in ((8, 3.2), (18, 3.0), (28, 3.0), (38, 2.8)):
        g.append(bred(1.0, y - lengde, y, z - d / 2, z + d / 2, "magasin", ("x", vinkel, (8, y, z))))
        g.append(bred(1.05, y - lengde + 0.6, y - lengde + 1.0, z - d / 2 + 0.3, z + d / 2 - 0.3, "stal", ("x", vinkel, (8, y, z))))
        a = math.radians(vinkel)
        y, z = y - lengde * math.cos(a), z - lengde * math.sin(a)
    g += kile(1.0, 15.5, 31.4, 15.0, 12.6, 11.0, 6.4, "tre")         # trekolbe
    g += [bred(1.08, 6.5, 12.7, 31.2, 31.9, "stal", ("x", -4, (8, 12.7, 31.2))),
          bred(0.3, 15.3, 16.4, -8.6, -8, "stal")]
    return g


# ===================================================================== SNIKSKYTTERGEVÆR (boltrifle med kikkert)
def snikskyttergevaer():
    g = [bred(0.5, 14.2, 15.2, -16, 8, "stal"),                     # løp
         bred(0.75, 14.0, 15.4, -16, -13, "stal"),                  # munningsbrems
         bred(0.8, 14.5, 14.9, -15.4, -13.6, "hull"),
         bred(0.3, 14.4, 15.0, -16.05, -16, "hull"),
         bred(1.1, 11.0, 14.6, -6, 10, "oliven"),                   # forskjefte
         bred(0.9, 11.5, 14.4, -8, -6, "oliven"),
         bred(1.15, 12.4, 12.8, -5, 9, "svart"),
         bred(0.9, 13.6, 15.8, 6, 17, "stal"),                      # låskasse
         b((8.9, 14.4, 14), (11.2, 15.0, 14.6), "stal"),            # bolthåndtak
         b((10.8, 13.6, 13.7), (11.8, 14.8, 14.9), "svart"),
         bred(0.6, 14.0, 15.4, 17, 18.4, "stal"),
         bred(1.0, 15.6, 18.9, 7, 8, "svart"),                      # kikkertringer
         bred(1.0, 15.6, 18.9, 13.5, 14.5, "svart"),
         bred(0.7, 17.4, 18.8, 5, 16, "svart"),                     # kikkertrør
         bred(1.1, 17.0, 19.2, -1.5, 3.5, "svart"),                 # objektiv
         bred(0.9, 17.2, 19.0, 3.5, 5, "svart"),
         bred(0.9, 17.2, 19.0, -1.55, -1.5, "linse"),
         bred(0.95, 17.15, 19.05, 16, 20, "svart"),                 # okular
         bred(0.8, 17.3, 18.9, 20, 20.05, "linse"),
         bred(0.4, 18.8, 19.8, 10, 11, "svart"),                    # tårn
         b((8.7, 17.7, 10), (9.6, 18.5, 11), "svart"),
         bred(0.42, 19.6, 19.8, 10.1, 10.9, "messing"),
         bred(0.7, 9.6, 11.0, 9.5, 13, "magasin"),                  # magasin
         bred(0.6, 8.6, 9.2, 13.5, 17.5, "svart"),                  # avtrekkerbøyle
         bred(0.6, 8.6, 11.0, 13.2, 13.8, "svart"),
         bred(0.25, 9.2, 11.0, 15, 15.6, "stal", ("x", 12, (8, 11, 15.3))),
         bred(0.9, 5.5, 11.5, 17, 20, "oliven", ("x", -22, (8, 11.5, 18.5))),   # pistolgrep
         bred(1.0, 11.0, 14.0, 17, 31, "oliven"),                   # kolbe
         *kile(1.0, 23, 31, 11.5, 11.5, 9.0, 6.9, "oliven"),
         bred(0.9, 14.0, 15.2, 21, 28, "oliven"),                   # kinnstøtte
         bred(1.1, 6.8, 14.2, 31, 32, "gummi"),
         b((7.0, 10.4, -5), (7.5, 11.0, 6), "svart"),               # tobeinsstøtte, slått inn
         b((8.5, 10.4, -5), (9.0, 11.0, 6), "svart"),
         bred(0.8, 10.4, 11.0, -6, -4.5, "svart")]
    return g


# ===================================================================== ammunisjon (bare ikoner, rendret i Blender)
def kuler():
    g = []
    for i, (dx, dz) in enumerate(((-3.2, 0), (0, -1.5), (3.2, 0))):
        x0 = 8 + dx
        g += [bred(0.9, 0, 0.5, dz - 0.9, dz + 0.9, "messing", x0=x0),     # kant
              bred(0.8, 0.5, 7.5, dz - 0.8, dz + 0.8, "messing", x0=x0),   # hylse
              bred(0.6, 7.5, 8.5, dz - 0.6, dz + 0.6, "messing", x0=x0),   # hals
              bred(0.5, 8.5, 10.5, dz - 0.5, dz + 0.5, "kobber", x0=x0),   # prosjektil
              bred(0.3, 10.5, 11.3, dz - 0.3, dz + 0.3, "kobber", x0=x0)]
    return g


def haglpatroner():
    g = []
    for i, (dx, dz) in enumerate(((-2.8, 0), (0, -1.5), (2.8, 0))):
        x0 = 8 + dx
        g += [bred(1.25, 0, 0.4, dz - 1.25, dz + 1.25, "messing", x0=x0),
              bred(1.2, 0.4, 2.2, dz - 1.2, dz + 1.2, "messing", x0=x0),
              bred(1.15, 2.2, 8.5, dz - 1.15, dz + 1.15, "hylse", x0=x0),
              bred(0.6, 8.5, 8.6, dz - 0.6, dz + 0.6, "hull", x0=x0)]
    return g


AMMUNISJON = {"kuler": kuler(), "haglpatroner": haglpatroner()}

def innenfor(bokser):
    """Minecraft godtar bare -16..32: skyv modellen inn om noe stikker utenfor."""
    for akse in range(3):
        lav = min(e["from"][akse] for e in bokser)
        hoy = max(e["to"][akse] for e in bokser)
        d = (-16 - lav) if lav < -16 else (32 - hoy) if hoy > 32 else 0
        if d:
            for e in bokser:
                e["from"][akse] = round(e["from"][akse] + d, 3)
                e["to"][akse] = round(e["to"][akse] + d, 3)
                if "rot" in e:
                    e["rot"]["origin"][akse] = round(e["rot"]["origin"][akse] + d, 3)
    for e in bokser:                     # det som fortsatt stikker ut (bittesmå biter) kuttes
        e["from"] = [min(32.0, max(-16.0, v)) for v in e["from"]]
        e["to"] = [min(32.0, max(-16.0, v)) for v in e["to"]]
    return bokser


GEVAER = {n: innenfor(f()) for n, f in (("pistol", pistol), ("hagle", hagle), ("automatgevaer", automatgevaer),
                                         ("snikskyttergevaer", snikskyttergevaer))}

# Visning i hånda. Modellen peker mot nord (-z); i første person ser vi langs -z, så løpet peker framover.
VISNING = {   # testet i spillet (F3+T): kolben nede til høyre, løpet mot siktekorset
    "pistol": {
        "thirdperson_righthand": {"rotation": [0, 0, 0], "translation": [0, 1, 0], "scale": [0.55, 0.55, 0.55]},
        "thirdperson_lefthand": {"rotation": [0, 0, 0], "translation": [0, 1, 0], "scale": [0.55, 0.55, 0.55]},
        "firstperson_righthand": {"rotation": [0, 8, 0], "translation": [-1, 3.5, -2], "scale": [0.38, 0.38, 0.38]},
        "firstperson_lefthand": {"rotation": [0, -8, 0], "translation": [-1, 3.5, -2], "scale": [0.38, 0.38, 0.38]},
    },
    "hagle": {
        "thirdperson_righthand": {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [0.4, 0.4, 0.4]},
        "thirdperson_lefthand": {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [0.4, 0.4, 0.4]},
        "firstperson_righthand": {"rotation": [0, 8, 0], "translation": [1, 2.5, -7], "scale": [0.4, 0.4, 0.4]},
        "firstperson_lefthand": {"rotation": [0, -8, 0], "translation": [1, 2.5, -7], "scale": [0.4, 0.4, 0.4]},
    },
}
VISNING["automatgevaer"] = VISNING["hagle"]
VISNING["snikskyttergevaer"] = VISNING["hagle"]
FELLES_VISNING = {
    "ground": {"rotation": [0, 0, 0], "translation": [0, 2, 0], "scale": [0.3, 0.3, 0.3]},
    "fixed": {"rotation": [0, 90, 0], "translation": [0, 0, 0], "scale": [0.5, 0.5, 0.5]},
    "head": {"rotation": [0, 90, 0], "translation": [0, 8, 0], "scale": [0.6, 0.6, 0.6]},
}

TILE = 32        # piksler per materialrute
ATLAS = 128      # 4x4 ruter
PX_PER_ENHET = 2


def atlas():
    r = random.Random(4242)
    img = Image.new("RGBA", (ATLAS, ATLAS), (0, 0, 0, 0))
    px = img.load()
    for mat, (pal, _, _) in MAT.items():
        i = MAT_INDEKS[mat]
        ox, oy = (i % 4) * TILE, (i // 4) * TILE
        korn = [r.random() * 6.28 for _ in range(4)]
        for y in range(TILE):
            for x in range(TILE):
                if mat in ("tre", "tre_mork"):          # årer langs z (u-retningen)
                    t = 0.55 + 0.22 * math.sin(y * 0.9 + 1.6 * math.sin(x * 0.12 + korn[0])) + (r.random() - 0.5) * 0.12
                elif mat in ("stal", "slede", "magasin"):   # børstet metall med slitasje
                    t = 0.5 + 0.12 * math.sin(y * 2.1 + korn[1]) + (r.random() - 0.5) * 0.18
                    if r.random() < 0.02:
                        t += 0.45
                elif mat in ("svart", "gummi", "oliven", "bakelitt"):   # matt, kornete
                    t = 0.5 + (r.random() - 0.5) * 0.35
                else:
                    t = 0.6 + 0.2 * math.sin((x + y) * 0.3) + (r.random() - 0.5) * 0.1
                t = max(0.0, min(0.999, t)) * (len(pal) - 1)
                k = int(t)
                f = t - k
                a, c = pal[k], pal[min(k + 1, len(pal) - 1)]
                px[ox + x, oy + y] = tuple(int(a[n] + (c[n] - a[n]) * f) for n in range(3)) + (255,)
    return img


def uv_for(mat, w, h):
    """UV-område (0..16-skala) med fast teksturtetthet, innenfor materialets rute."""
    i = MAT_INDEKS[mat]
    skala = 16 / ATLAS
    u0 = (i % 4) * TILE + 1
    v0 = (i // 4) * TILE + 1
    du = min(TILE - 2, max(0.5, w * PX_PER_ENHET))
    dv = min(TILE - 2, max(0.5, h * PX_PER_ENHET))
    return [round(u0 * skala, 4), round(v0 * skala, 4), round((u0 + du) * skala, 4), round((v0 + dv) * skala, 4)]


def modell_json(navn, bokser):
    elementer = []
    for e in bokser:
        (x1, y1, z1), (x2, y2, z2) = e["from"], e["to"]
        dx, dy, dz = x2 - x1, y2 - y1, z2 - z1
        flater = {"north": (dx, dy), "south": (dx, dy), "east": (dz, dy), "west": (dz, dy), "up": (dx, dz), "down": (dx, dz)}
        el = {"from": e["from"], "to": e["to"],
              "faces": {f: {"uv": uv_for(e["mat"], *wh), "texture": "#t"} for f, wh in flater.items()}}
        if "rot" in e:
            el["rotation"] = e["rot"]
        lys = MAT[e["mat"]][1]
        if lys:
            el["light_emission"] = lys
        elementer.append(el)
    return {"texture_size": [ATLAS, ATLAS],
            "textures": {"t": "dodsfjellet:item/gevaer_atlas", "particle": "dodsfjellet:item/gevaer_atlas"},
            "elements": elementer, "display": {**VISNING[navn], **FELLES_VISNING}}


def main():
    (ASSETS / "models" / "item").mkdir(parents=True, exist_ok=True)
    (ASSETS / "textures" / "item").mkdir(parents=True, exist_ok=True)
    atlas().save(ASSETS / "textures" / "item" / "gevaer_atlas.png")
    blender = {"materialer": {m: {"farge": [c / 255 for c in pal[2]], "lys": lys, "metall": bl[0], "ruhet": bl[1]}
                              for m, (pal, lys, bl) in MAT.items()}, "modeller": {}}
    for navn, bokser in GEVAER.items():
        (ASSETS / "models" / "item" / f"{navn}_3d.json").write_text(json.dumps(modell_json(navn, bokser), indent=1))
        blender["modeller"][navn] = bokser
        print(f"{navn}: {len(bokser)} klosser")
    blender["modeller"].update(AMMUNISJON)
    UT_JSON.write_text(json.dumps(blender))


if __name__ == "__main__":
    main()
