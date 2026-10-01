"""Genererer alle egne teksturer for Dødsfjellet-modden (Minecraft 26.3).

Alt er prosedyrisk pikselkunst i samme stemning som kartet: dyp svart-lilla stein,
aske, døde trær, glødende sjelekrystaller (lilla/cyan), karmosinrødt og gull.
Kjør:  python verktoy/teksturer.py
"""
import io
import math
import random
import zipfile
from pathlib import Path

from PIL import Image

HER = Path(__file__).resolve().parent.parent
TEX = HER / "src" / "main" / "resources" / "assets" / "dodsfjellet" / "textures"
JAR = next((HER / ".gradle" / "loom-cache" / "minecraftMaven" / "net" / "minecraft").rglob("minecraft-merged-*-26.3.jar"))

R = random.Random(1337)


def klamp(v):
    return max(0, min(255, int(v)))


def farge(c, d=0):
    return tuple(klamp(x + d) for x in c[:3]) + ((c[3],) if len(c) > 3 else (255,))


def støy(w, h, skala, frø):
    """Enkel verdi-støy (glatt), 0..1."""
    r = random.Random(frø)
    gw, gh = w // skala + 2, h // skala + 2
    g = [[r.random() for _ in range(gw)] for _ in range(gh)]
    ut = [[0.0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            fx, fy = x / skala, y / skala
            x0, y0 = int(fx), int(fy)
            tx, ty = fx - x0, fy - y0
            tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
            a = g[y0][x0] * (1 - tx) + g[y0][x0 + 1] * tx
            b = g[y0 + 1][x0] * (1 - tx) + g[y0 + 1][x0 + 1] * tx
            ut[y][x] = a * (1 - ty) + b * ty
    return ut


def palett(pal, t):
    t = max(0.0, min(0.9999, t)) * (len(pal) - 1)
    i = int(t)
    f = t - i
    a, b = pal[i], pal[i + 1]
    return tuple(klamp(a[k] + (b[k] - a[k]) * f) for k in range(3)) + (255,)


def nytt(w=16, h=16, c=(0, 0, 0, 0)):
    return Image.new("RGBA", (w, h), c)


def lagre(img, sti):
    p = TEX / sti
    p.parent.mkdir(parents=True, exist_ok=True)
    img.save(p)


# ---------------------------------------------------------------- paletter
STEIN = [(14, 11, 20), (28, 23, 36), (42, 35, 52), (58, 49, 70), (76, 66, 90)]
ASKE = [(40, 38, 44), (62, 59, 66), (84, 80, 88), (104, 99, 106), (126, 120, 126)]
VED = [(18, 12, 16), (34, 24, 30), (50, 36, 44), (66, 50, 58), (84, 66, 74)]
PLANKE = [(30, 20, 30), (48, 33, 46), (66, 46, 62), (84, 60, 78), (100, 74, 92)]
SJEL = [(40, 10, 70), (90, 30, 160), (150, 80, 230), (120, 220, 255), (235, 250, 255)]
BLOD = [(30, 2, 6), (70, 6, 14), (115, 14, 24), (160, 30, 36), (205, 70, 60)]
GULL = [(70, 45, 5), (140, 95, 15), (210, 160, 40), (250, 215, 100), (255, 245, 190)]
ISBLÅ = [(14, 22, 30), (40, 72, 92), (70, 140, 165), (150, 220, 235), (235, 252, 255)]


def stein_tekstur(frø, pal=STEIN, sprekker=True, flekker=None):
    img = nytt()
    n = støy(16, 16, 4, frø)
    n2 = støy(16, 16, 2, frø + 1)
    px = img.load()
    for y in range(16):
        for x in range(16):
            t = n[y][x] * 0.65 + n2[y][x] * 0.35
            px[x, y] = palett(pal, t * 0.85 + 0.08)
    if sprekker:
        r = random.Random(frø + 7)
        for _ in range(3):
            x, y = r.randrange(16), r.randrange(16)
            for _ in range(r.randint(3, 7)):
                px[x % 16, y % 16] = palett(pal, 0.0)
                x += r.choice((-1, 0, 1))
                y += r.choice((0, 1))
    if flekker:
        r = random.Random(frø + 11)
        for _ in range(flekker[1]):
            x, y = r.randrange(16), r.randrange(16)
            px[x, y] = farge(flekker[0], r.randint(-20, 20))
    return img


def murstein(pal, frø):
    img = stein_tekstur(frø, pal, sprekker=False)
    px = img.load()
    mørtel = palett(pal, 0.02)
    for y in range(16):
        for x in range(16):
            rad = y // 4
            forsk = 4 if rad % 2 else 0
            if y % 4 == 3 or (x + forsk) % 8 == 7:
                px[x, y] = mørtel
            elif y % 4 == 0:
                px[x, y] = farge(px[x, y], 14)
    return img


def polert(pal, frø):
    img = stein_tekstur(frø, pal, sprekker=False)
    px = img.load()
    for y in range(16):
        for x in range(16):
            if x in (0, 15) or y in (0, 15):
                px[x, y] = palett(pal, 0.05)
            elif x in (1, 14) or y in (1, 14):
                px[x, y] = palett(pal, 0.7)
            else:
                px[x, y] = farge(px[x, y], 6)
    return img


def stamme_side(frø):
    img = nytt()
    px = img.load()
    n = støy(16, 16, 3, frø)
    for y in range(16):
        for x in range(16):
            stripe = 0.35 * math.sin(x * 1.7 + n[y][x] * 3)
            px[x, y] = palett(VED, 0.45 + stripe * 0.6 + (n[y][x] - 0.5) * 0.4)
    r = random.Random(frø)
    for _ in range(4):   # glødende sjeleårer i barken
        x = r.randrange(16)
        y = r.randrange(16)
        for _ in range(r.randint(2, 5)):
            px[x % 16, y % 16] = palett(SJEL, 0.45 + r.random() * 0.2)
            y += 1
    return img


def stamme_topp(frø):
    img = nytt()
    px = img.load()
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            if d > 7.3:
                px[x, y] = palett(VED, 0.15)
            else:
                ring = 0.5 + 0.4 * math.sin(d * 1.9)
                px[x, y] = palett(PLANKE, ring * 0.8 + 0.1)
    px[7, 7] = px[8, 8] = palett(SJEL, 0.6)
    return img


def planker(frø):
    img = nytt()
    px = img.load()
    n = støy(16, 16, 4, frø)
    for y in range(16):
        for x in range(16):
            bord = y // 4
            t = 0.5 + 0.25 * math.sin(x * 0.9 + bord * 2.1) + (n[y][x] - 0.5) * 0.4
            px[x, y] = palett(PLANKE, t)
            if y % 4 == 3:
                px[x, y] = palett(PLANKE, 0.05)
            if (x + bord * 5) % 16 == 0:
                px[x, y] = palett(PLANKE, 0.12)
    return img


def sjeleglod(frø):
    img = nytt()
    px = img.load()
    n = støy(16, 16, 3, frø)
    for y in range(16):
        for x in range(16):
            d = min(abs(x - 7.5), abs(y - 7.5))
            t = 0.35 + n[y][x] * 0.45 + (0.25 if (x + y) % 5 == 0 else 0) - d * 0.015
            px[x, y] = palett(SJEL, t)
    for y in range(16):
        for x in range(16):
            if x in (0, 15) or y in (0, 15):
                px[x, y] = palett(SJEL, 0.12)
    return img


def malm(frø):
    img = stein_tekstur(frø)
    px = img.load()
    r = random.Random(frø + 3)
    for _ in range(4):
        cx, cy = r.randrange(2, 14), r.randrange(2, 14)
        for dx, dy, t in [(0, 0, 0.95), (1, 0, 0.7), (0, 1, 0.7), (-1, 0, 0.55), (0, -1, 0.6), (1, 1, 0.4)]:
            px[(cx + dx) % 16, (cy + dy) % 16] = palett(SJEL, t)
    return img


def smie_side():
    img = murstein(STEIN, 41)
    px = img.load()
    # glødende rune i midten
    rune = ["..XX..", ".X..X.", "XXXXXX", ".X..X.", ".X..X.", "XX..XX"]
    for j, rad in enumerate(rune):
        for i, ch in enumerate(rad):
            if ch == "X":
                px[5 + i, 4 + j] = palett(SJEL, 0.75)
    return img


def smie_topp():
    img = polert(STEIN, 43)
    px = img.load()
    for y in range(4, 12):
        for x in range(3, 13):
            px[x, y] = palett(BLOD, 0.5 + 0.4 * math.sin(x * 1.3 + y))
    for x in range(4, 12):
        px[x, 7] = palett(GULL, 0.85)
    return img


def portal(frø):
    img = nytt()
    px = img.load()
    for y in range(16):
        for x in range(16):
            t = 0.5 + 0.5 * math.sin((x + y * 0.5) * 0.8 + frø)
            px[x, y] = palett(SJEL, 0.15 + t * 0.6)[:3] + (200,)
    return img


# ---------------------------------------------------------------- gjenstander (16x16)
def tegn(rader, palett_map):
    img = nytt()
    px = img.load()
    for y, rad in enumerate(rader):
        for x, ch in enumerate(rad):
            if ch in palett_map:
                px[x, y] = palett_map[ch]
    return img


def krystall():
    rader = [
        "................",
        "........a.......",
        ".......aba......",
        "......abcba.....",
        ".....abccdba....",
        ".....bccddcb....",
        "....abcddeccb...",
        "....bcddeedcb...",
        "....bcddedccb...",
        ".....bcdddcb....",
        ".....abcdcba....",
        "......abcba.....",
        ".......aba......",
        "........a.......",
        "................",
        "................"]
    return tegn(rader, {"a": SJEL[0] + (255,), "b": SJEL[1] + (255,), "c": SJEL[2] + (255,),
                        "d": SJEL[3] + (255,), "e": SJEL[4] + (255,)})


def nøkkel():
    rader = [
        "................",
        "...bbbb.........",
        "..bcddcb........",
        "..bd..db........",
        "..bd.edb........",
        "..bcddcb........",
        "...bbbbb........",
        "......bcb.......",
        ".......bcb......",
        "........bcb.....",
        ".........bcb....",
        "........bbcbb...",
        "........b.bcb...",
        "...........bcbb.",
        "...........b.b..",
        "................"]
    return tegn(rader, {"b": (40, 32, 26, 255), "c": (210, 200, 175, 255), "d": GULL[2] + (255,),
                        "e": SJEL[3] + (255,)})


def rune(glyf, pal):
    base = [
        "................",
        "....aaaaaaaa....",
        "...abbbbbbbba...",
        "..abbbbbbbbbba..",
        "..abbbbbbbbbba..",
        "..abbbbbbbbbba..",
        "..abbbbbbbbbba..",
        "..abbbbbbbbbba..",
        "..abbbbbbbbbba..",
        "..abbbbbbbbbba..",
        "..abbbbbbbbbba..",
        "..abbbbbbbbbba..",
        "..abbbbbbbbbba..",
        "...abbbbbbbba...",
        "....aaaaaaaa....",
        "................"]
    img = tegn(base, {"a": STEIN[0] + (255,), "b": STEIN[2] + (255,)})
    px = img.load()
    n = støy(16, 16, 3, len(glyf) * 7)
    for y in range(16):
        for x in range(16):
            if px[x, y][3] and px[x, y][:3] == STEIN[2]:
                px[x, y] = palett(STEIN, 0.35 + n[y][x] * 0.4)
    for j, rad in enumerate(glyf):
        for i, ch in enumerate(rad):
            if ch == "X":
                px[4 + i, 4 + j] = palett(pal, 0.75)
            elif ch == "o":
                px[4 + i, 4 + j] = palett(pal, 0.45)
    return img


GLYFER = {
    "rune_skyggesprang": (["...XXXXX", "..XX....", ".XX.....", "XXXXXXXX", ".....XX.", "....XX..", "XXXXX..."], SJEL),
    "rune_sjeleskjold": (["..XXXX..", ".X....X.", "X..XX..X", "X.XXXX.X", "X..XX..X", ".X....X.", "..XXXX.."], ISBLÅ),
    "rune_dodsnova": (["X..X..X.", ".X.X.X..", "..XXX...", "XXXoXXXX", "..XXX...", ".X.X.X..", "X..X..X."], SJEL),
    "rune_blodhost": (["...XX...", "..XXXX..", ".XXXXXX.", ".XXooXX.", ".XXXXXX.", "..XXXX..", "...XX..."], BLOD),
    "rune_andesprang": (["...XX...", "..XXXX..", ".X.XX.X.", "...XX...", "...XX...", "..X..X..", ".X....X."], ISBLÅ),
    "rune_vokterkall": (["XX....XX", "X.X..X.X", "X..XX..X", "X..XX..X", ".X.XX.X.", "..XXXX..", "...XX..."], GULL),
}


def kompass():
    rader = [
        "................",
        ".....aaaaaa.....",
        "...aabbbbbbaa...",
        "..abbccccccbba..",
        "..abccccdcccba..",
        ".abcccccdccccba.",
        ".abccccdecccba..",
        ".abcccdeecccba..",
        ".abcccfeeccccba.",
        ".abcccfcccccba..",
        "..abccfcccccba..",
        "..abbcccccccba..",
        "...aabbbbbbaa...",
        ".....aaaaaa.....",
        "................",
        "................"]
    return tegn(rader, {"a": STEIN[0] + (255,), "b": GULL[2] + (255,), "c": STEIN[1] + (255,),
                        "d": SJEL[3] + (255,), "e": SJEL[4] + (255,), "f": BLOD[3] + (255,)})


# ---------------------------------------------------------------- recolor fra vanilla (rustning)
def fra_jar(sti):
    with zipfile.ZipFile(JAR) as z:
        return Image.open(io.BytesIO(z.read(f"assets/minecraft/textures/{sti}.png"))).convert("RGBA")


def fargelegg(img, pal):
    img = img.copy()
    px = img.load()
    lys = [0.299 * r + 0.587 * g + 0.114 * b for r, g, b, a in img.getdata() if a > 0]
    lo, hi = min(lys), max(lys)
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a:
                t = ((0.299 * r + 0.587 * g + 0.114 * b) - lo) / max(1, hi - lo)
                px[x, y] = palett(pal, t)[:3] + (a,)
    return img


SKATT = [(10, 4, 6), (60, 8, 16), (130, 20, 30), (200, 150, 40), (255, 235, 150)]   # sjeleplate: svart/karmosin/gull


def main():
    blokker = {
        "dodsstein": stein_tekstur(1, flekker=((90, 40, 140), 4)),
        "dodsstein_murstein": murstein(STEIN, 2),
        "polert_dodsstein": polert(STEIN, 3),
        "askejord": stein_tekstur(4, ASKE, sprekker=False, flekker=((20, 18, 22), 10)),
        "dodsved_stamme": stamme_side(5),
        "dodsved_stamme_topp": stamme_topp(6),
        "dodsved_planker": planker(7),
        "sjeleglod": sjeleglod(8),
        "dodskrystall_malm": malm(9),
        "blodmose": stein_tekstur(10, BLOD, sprekker=False, flekker=((240, 120, 90), 5)),
        "oppgraderingssmie_side": smie_side(),
        "oppgraderingssmie_topp": smie_topp(),
        "oppgraderingssmie_bunn": polert(STEIN, 44),
    }
    for navn, img in blokker.items():
        lagre(img, f"block/{navn}.png")

    gjenstander = {"dodskrystall": krystall(), "dodsnokkel": nøkkel(), "reisekompass": kompass()}
    for navn, (glyf, pal) in GLYFER.items():
        gjenstander[navn] = rune(glyf, pal)
    for navn, img in gjenstander.items():
        lagre(img, f"item/{navn}.png")

    # Fjellvokter (fra versjon 1) og den nye Sjeleplate-rustningen
    for sett, pal in (("fjellvokter", ISBLÅ), ("sjeleplate", SKATT)):
        for del_, van in (("hjelm", "helmet"), ("brynje", "chestplate"), ("bukser", "leggings"), ("stovler", "boots")):
            lagre(fargelegg(fra_jar(f"item/netherite_{van}"), pal), f"item/{sett}_{del_}.png")
        lagre(fargelegg(fra_jar("entity/equipment/humanoid/netherite"), pal), f"entity/equipment/humanoid/{sett}.png")
        lagre(fargelegg(fra_jar("entity/equipment/humanoid_leggings/netherite"), pal),
              f"entity/equipment/humanoid_leggings/{sett}.png")
    print("Teksturer laget i", TEX)


if __name__ == "__main__":
    main()
