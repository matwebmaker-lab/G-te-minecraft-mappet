"""Dødsfjellet-grafikk: en innebygd ressurspakke som gir HELE spillet et nytt, lyst og glad utseende.

1. Ressurspakken (src/main/resources/resourcepacks/dodsgrafikk, slås på automatisk, kan slås av i Ressurspakker):
   - alle blokkteksturer males om i 32x32: ny, lys fargepalett per materiale (lys blågrå stein, gyllen sand,
     varm jord), mykere piksler, avfasede kanter og solfylte høylys
   - nye fargekart: frodig grønt gress, trær i vårgrønt, gyllent og rosa blomstring
   - varm gyllen sol med glorie, sølvblå måne, hvite skyer
2. Data (src/main/resources/data/minecraft): klar blå himmel, lys dis og turkis vann i alle biomene.

Kjør:  python verktoy/grafikk.py      (trenger vanilla-filene fra 26.3-jaren, se KILDE_JAR)
"""
import colorsys
import json
import math
import re
import shutil
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HER = Path(__file__).resolve().parent.parent
PAKKE = HER / "src" / "main" / "resources" / "resourcepacks" / "dodsgrafikk"
TEX_UT = PAKKE / "assets" / "minecraft" / "textures"
DATA_UT = HER / "src" / "main" / "resources" / "data" / "minecraft"
KILDE_JAR = Path.home() / "curseforge" / "minecraft" / "Install" / "versions" / "26.3" / "26.3.jar"
SKALA = 2   # 16 -> 32 piksler

rng = np.random.default_rng(1313)


def hx(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=float) / 255


# ---------------------------------------------------------------- fargepaletter (mørk -> lys)
PALETTER = {
    "stein": ["#4a5164", "#646d82", "#808aa0", "#9ea8bd", "#bec7d8", "#dde3ee"],
    "dypstein": ["#262b3a", "#363d50", "#4a5268", "#606a82", "#7a849c", "#97a0b6"],
    "jord": ["#4a2c1c", "#6a4128", "#8a5835", "#a87045", "#c58b5a", "#dfa877"],
    "sand": ["#b98d4a", "#d2a75e", "#e5be76", "#f2d293", "#fae4b3", "#fff3d6"],
    "rodsand": ["#9a4632", "#b85a3e", "#d2734e", "#e69064", "#f4ad80", "#ffcba4"],
    "grus": ["#5f5b66", "#77737e", "#918d98", "#aba7b1", "#c5c1ca", "#dedbe2"],
    "sno": ["#a9c2e6", "#c2d5f0", "#d7e4f7", "#e7effb", "#f3f7fe", "#ffffff"],
    "tre": None,       # beholder fargen, men varmere og litt lysere
    "netherrack": ["#5a1a22", "#7a2630", "#9a3540", "#b84a52", "#d26468", "#e8848a"],
}
GRADIENT = {k: np.array([hx(c) for c in v]) for k, v in PALETTER.items() if v}

KATEGORIER = [   # (kategori, regex) – første treff vinner
    ("hopp", r"^(destroy_stage_|debug|structure_block|jigsaw|command_block|test_|barrier|light$)"),
    ("ingen_kant", r"(water|lava|fire|portal|_flow|_still|glass|nether_portal|end_gateway|sculk_vein|vine|bubble)"),
    ("rodsand", r"^(red_sand|red_sandstone|cut_red_sandstone|chiseled_red_sandstone|smooth_red_sandstone)"),
    ("sand", r"^(sand|sandstone|cut_sandstone|chiseled_sandstone|smooth_sandstone|suspicious_sand)"),
    ("dypstein", r"(deepslate|tuff|basalt|blackstone|bedrock|obsidian)"),
    ("netherrack", r"^(netherrack|nether_bricks|cracked_nether|chiseled_nether|red_nether|nether_gold_ore|nether_quartz_ore)"),
    ("jord", r"^(dirt|coarse_dirt|rooted_dirt|podzol|mud|packed_mud|mud_bricks|farmland|dirt_path|mycelium|grass_block_side$|grass_block_snow)"),
    ("grus", r"^(gravel|suspicious_gravel|clay)$"),
    ("sno", r"^(snow|powder_snow|ice|packed_ice|blue_ice|frosted_ice)"),
    ("stein", r"(stone|cobble|andesite|diorite|granite|calcite|dripstone|stone_bricks|_ore$|smooth_stone|furnace|dispenser|dropper|observer|piston)"),
    ("tre", r"(planks|_log|_wood|stripped_|_door|trapdoor|crafting_table|bookshelf|barrel|composter|ladder|lectern|loom|cartography|fletching|smithing|_stem$|_hyphae|bamboo_block|beehive)"),
]
FAST_FARGE = {"birch_leaves": (1.0, 1.0, 0.55), "spruce_leaves": (0.9, 1.0, 1.0)}   # ganges med spillets faste farge
FARGET = re.compile(r"(grass|leaves|fern|vine|lily_pad|sugar_cane|_stem|bush|water|redstone_dust|tall_grass|pumpkin_stem|melon_stem)")


def kategori(navn):
    for k, rx in KATEGORIER:
        if re.search(rx, navn):
            return k
    return "annet"


# ---------------------------------------------------------------- bildebehandling
def lum(rgb):
    return rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114


def gradient_kart(l, grad):
    l = np.clip(l, 0, 1) * (len(grad) - 1)
    i = np.clip(np.floor(l).astype(int), 0, len(grad) - 2)
    f = (l - i)[..., None]
    return grad[i] * (1 - f) + grad[i + 1] * f


def stemning(rgb, metning=1.15, styrke=1.0):
    """Felles lys grading: friskere farger, løftede skygger, varme solfylte høylys."""
    l = lum(rgb)[..., None]
    rgb = l + (rgb - l) * metning
    skygge = np.array([0.30, 0.40, 0.62])             # kjølig blå i skyggene i stedet for svart
    lys = np.array([1.0, 0.95, 0.80])                 # varmt sollys
    rgb = rgb + (skygge - rgb) * ((1 - l) ** 3 * 0.18 * styrke) + (lys - rgb) * (l ** 2 * 0.12 * styrke)
    rgb = 0.5 + (rgb - 0.5) * 1.05
    return np.clip(rgb * 1.06 + 0.02, 0, 1)            # litt lysere totalt


def oppskaler(img):
    """16 -> 32: skarpe piksler blandet med litt mykhet og fin støy, så det ser 'malt' ut."""
    w, h = img.size
    skarp = np.asarray(img.resize((w * SKALA, h * SKALA), Image.NEAREST)).astype(float) / 255
    myk = np.asarray(img.resize((w * SKALA, h * SKALA), Image.BILINEAR)).astype(float) / 255
    a = skarp.copy()
    a[..., :3] = skarp[..., :3] * 0.62 + myk[..., :3] * 0.38
    return a


def kant(a, styrke):
    """Avfaset kant: lys øverst/venstre, mørk nederst/høyre (gir en 'kloss'-følelse i ny stil)."""
    h, w = a.shape[:2]
    m = np.zeros((h, w))
    for d, v in ((0, 1.0), (1, 0.55), (2, 0.2)):
        m[d, d:w - d] += v
        m[d:h - d, d] += v
        m[h - 1 - d, d:w - d] -= v * 1.25
        m[d:h - d, w - 1 - d] -= v * 1.25
    a[..., :3] = np.clip(a[..., :3] * (1 + m[..., None] * styrke), 0, 1)
    return a


def bearbeid(navn, img):
    kat = kategori(navn)
    if kat == "hopp":
        return None
    img = img.convert("RGBA")
    w, h = img.size
    rammer = h // w if h % w == 0 and h > w else 1
    bit = []
    for r in range(rammer):
        ramme = img.crop((0, r * w, w, (r + 1) * w)) if rammer > 1 else img
        bit.append(bearbeid_ramme(navn, kat, ramme))
    if rammer == 1:
        return bit[0]
    ut = Image.new("RGBA", (w * SKALA, h * SKALA))
    for r, b in enumerate(bit):
        ut.paste(b, (0, r * w * SKALA))
    return ut


def bearbeid_ramme(navn, kat, ramme):
    a = oppskaler(ramme)
    rgb = a[..., :3]
    alfa = a[..., 3]
    synlig = alfa > 0.5
    c = rgb[synlig] if synlig.any() else rgb.reshape(-1, 3)
    metning = float((c.max(1) - c.min(1)).mean()) if len(c) else 0
    farges = metning < 0.03 and FARGET.search(navn)       # gråskala som spillet farger (gress, løv, vann)

    if farges:
        l = lum(rgb)
        rgb = np.repeat(np.clip(0.5 + (l - 0.5) * 1.25, 0, 1)[..., None], 3, axis=2)   # mer kontrast i mønsteret
        if navn in FAST_FARGE:      # bjørk og gran har fast farge i koden: forhåndsfarg teksturen så resultatet blir høst/mauve
            rgb = np.clip(rgb * np.array(FAST_FARGE[navn]), 0, 1)
    elif kat in GRADIENT:
        l = lum(rgb)
        lo, hi = np.percentile(l[synlig], 3) if synlig.any() else 0, np.percentile(l[synlig], 97) if synlig.any() else 1
        rel = (l - lo) / max(1e-3, hi - lo)
        ll = np.clip(0.55 * l + 0.45 * rel, 0, 1)
        ny = gradient_kart(ll, GRADIENT[kat])
        bland = 0.8
        if navn.endswith("_ore") or "_ore" in navn:      # malmflekkene: behold farge, men la dem gløde
            pm = rgb.max(-1) - rgb.min(-1)
            flekk = np.clip((pm - 0.12) * 4, 0, 1)[..., None]
            gloed = np.clip(rgb * 1.25 + 0.05, 0, 1)
            rgb = ny * (1 - flekk) + gloed * flekk
        else:
            rgb = ny * bland + stemning(rgb) * (1 - bland)
    elif kat == "tre":
        hsv = np.array([colorsys.rgb_to_hsv(*p) for p in rgb.reshape(-1, 3)]).reshape(rgb.shape)
        hsv[..., 0] = (hsv[..., 0] + 0.008) % 1.0          # litt mot gyllent
        hsv[..., 1] = np.clip(hsv[..., 1] * 1.1, 0, 1)
        hsv[..., 2] = np.clip(hsv[..., 2] * 1.08 + 0.03, 0, 1)
        rgb = np.array([colorsys.hsv_to_rgb(*p) for p in hsv.reshape(-1, 3)]).reshape(rgb.shape)
        rgb = stemning(rgb, 1.0, 0.7)
    elif re.search(r"leaves", navn):                       # ufargede løv (kirsebær, asalea): ekstra friske
        rgb = stemning(rgb, 1.25)
    else:
        rgb = stemning(rgb)

    # fin malerisk støy på naturlige flater
    if kat in ("stein", "dypstein", "jord", "sand", "rodsand", "grus", "netherrack") or farges:
        rgb = np.clip(rgb * (1 + rng.normal(0, 0.025, rgb.shape[:2])[..., None]), 0, 1)
    a[..., :3] = rgb
    hel = bool((alfa > 0.99).all())
    if hel and kat != "ingen_kant" and not FARGET.search(navn):
        a = kant(a, 0.16 if kat in ("stein", "dypstein", "tre", "netherrack", "annet") else 0.12)
    elif hel and farges and "grass_block_top" in navn:
        a = kant(a, 0.06)
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), "RGBA")


# ---------------------------------------------------------------- fargekart for gress og løv
def fargekart(kald, frodig, torr):
    """Vanilla-trekanten: x = 1-temperatur, y = 1-(temperatur*nedbør)."""
    kald, frodig, torr = hx(kald), hx(frodig), hx(torr)
    ut = np.zeros((256, 256, 3))
    for y in range(256):
        for x in range(256):
            t = 1 - x / 255
            tn = 1 - y / 255
            n = min(1.0, tn / t) if t > 0 else 0
            varm = t * n * frodig + t * (1 - n) * torr
            ut[y, x] = varm + (1 - t) * kald
    return Image.fromarray((ut * 255).astype(np.uint8), "RGB")


# ---------------------------------------------------------------- himmel
def sol():
    """Varm gyllen sol med glorie."""
    s = 32
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    px = img.load()
    for y in range(s):
        for x in range(s):
            d = math.hypot(x - 15.5, y - 15.5)
            if d < 7:
                px[x, y] = (255, 250, 214, 255)
            elif d < 9:
                px[x, y] = (255, 214, 92, 255)
            elif d < 15.5:
                v = int(170 * (1 - (d - 9) / 6.5) ** 1.4)
                px[x, y] = (255, 200, 90, v)
    return img


def maane(fase):
    """fase: andel opplyst (-1..1, negativ = avtagende). Mild sølvblå måne."""
    s = 32
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    px = img.load()
    r = rng
    for y in range(s):
        for x in range(s):
            dx, dy = (x - 15.5) / 9, (y - 15.5) / 9
            if dx * dx + dy * dy > 1:
                continue
            kant_x = math.sqrt(max(0, 1 - dy * dy))
            grense = kant_x * (1 - 2 * abs(fase))
            opplyst = dx > grense if fase > 0 else dx < -grense
            if abs(fase) >= 1:
                opplyst = True
            if fase == 0:
                opplyst = False
            krater = 0.9 + 0.1 * math.sin(x * 1.7) * math.cos(y * 1.3) + r.normal(0, 0.03)
            if opplyst:
                px[x, y] = (int(225 * krater), int(232 * krater), min(255, int(250 * krater)), 255)
            else:
                px[x, y] = (70, 80, 110, 90)
    return img


MAANEFASER = {"full_moon": 1.0, "waning_gibbous": -0.75, "third_quarter": -0.5, "waning_crescent": -0.25,
              "new_moon": 0.0, "waxing_crescent": 0.25, "first_quarter": 0.5, "waxing_gibbous": 0.75}


# ---------------------------------------------------------------- biomfarger (data)
def bland(farge, mot, andel, mork=1.0):
    a = hx(farge) if isinstance(farge, str) else farge
    b = hx(mot)
    c = np.clip((a * (1 - andel) + b * andel) * mork, 0, 1)
    return "#%02x%02x%02x" % tuple(int(v * 255) for v in c)


def int_farge(v):
    return "#%06x" % (v & 0xFFFFFF)


def omfarg_biom(d):
    attr = d.get("attributes", {})
    for k, mot, andel, mork in (("minecraft:visual/sky_color", "#5fc4ff", 0.5, 1.05),
                                ("minecraft:visual/fog_color", "#e4f4ff", 0.5, 1.0),
                                ("minecraft:visual/water_fog_color", "#1e9aa8", 0.6, 1.0)):
        if isinstance(attr.get(k), str):
            attr[k] = bland(attr[k], mot, andel, mork)
    eff = d.get("effects", {})
    for k, mot, andel in (("water_color", "#2fd4d0", 0.7), ("grass_color", "#5ed36a", 0.5),
                          ("foliage_color", "#5fd062", 0.4), ("dry_foliage_color", "#e0a050", 0.5)):
        v = eff.get(k)
        if isinstance(v, int):
            v = int_farge(v)
        if isinstance(v, str):
            eff[k] = bland(v, mot, andel)
    return d


def data():
    with zipfile.ZipFile(KILDE_JAR) as z:
        biomer = [n for n in z.namelist() if n.startswith("data/minecraft/worldgen/biome/") and n.endswith(".json")]
        oververden = ("the_end", "end_", "nether", "soul_sand_valley", "crimson_forest", "warped_forest", "basalt_deltas", "small_end")
        n = 0
        for b in biomer:
            navn = Path(b).stem
            if any(navn.startswith(o) or o in navn for o in oververden):
                continue
            d = omfarg_biom(json.loads(z.read(b)))
            ut = DATA_UT / "worldgen" / "biome" / f"{navn}.json"
            ut.parent.mkdir(parents=True, exist_ok=True)
            ut.write_text(json.dumps(d, indent=1))
            n += 1
        dim = json.loads(z.read("data/minecraft/dimension_type/overworld.json"))
        a = dim["attributes"]
        a["minecraft:visual/sky_color"] = bland(a["minecraft:visual/sky_color"], "#5fc4ff", 0.5, 1.05)
        a["minecraft:visual/fog_color"] = bland(a["minecraft:visual/fog_color"], "#e4f4ff", 0.5, 1.0)
        a["minecraft:visual/cloud_color"] = "#f2fffbf0"
        ut = DATA_UT / "dimension_type" / "overworld.json"
        ut.parent.mkdir(parents=True, exist_ok=True)
        ut.write_text(json.dumps(dim, indent=1))
    return n


# ---------------------------------------------------------------- alt sammen
def main():
    if PAKKE.exists():
        shutil.rmtree(PAKKE)
    for sti in (DATA_UT / "worldgen" / "biome", DATA_UT / "dimension_type" / "overworld.json"):
        if sti.is_dir():
            shutil.rmtree(sti)
        elif sti.exists():
            sti.unlink()
    (TEX_UT / "block").mkdir(parents=True)
    antall = 0
    with zipfile.ZipFile(KILDE_JAR) as z:
        filer = [n for n in z.namelist() if n.startswith("assets/minecraft/textures/block/")]
        for n in filer:
            navn = Path(n).name
            if navn.endswith(".png"):
                with z.open(n) as f:
                    img = Image.open(f)
                    img.load()
                ny = bearbeid(Path(navn).stem, img)
                if ny is not None:
                    ny.save(TEX_UT / "block" / navn)
                    antall += 1
                    meta = n + ".mcmeta"
                    if meta in filer:
                        (TEX_UT / "block" / (navn + ".mcmeta")).write_bytes(z.read(meta))
    (TEX_UT / "colormap").mkdir(parents=True)
    fargekart("#86dcc0", "#5edc68", "#cfe05c").save(TEX_UT / "colormap" / "grass.png")        # kald, frodig, tørr
    fargekart("#6fe0b0", "#4cd85a", "#f0c844").save(TEX_UT / "colormap" / "foliage.png")      # mint, vårgrønt, gyllent
    fargekart("#e8b080", "#e0a050", "#f0c060").save(TEX_UT / "colormap" / "dry_foliage.png")
    (TEX_UT / "environment" / "celestial" / "moon").mkdir(parents=True)
    sol().save(TEX_UT / "environment" / "celestial" / "sun.png")
    for fase, f in MAANEFASER.items():
        maane(f).save(TEX_UT / "environment" / "celestial" / "moon" / f"{fase}.png")
    biomer = data()
    (PAKKE / "pack.mcmeta").write_text(json.dumps({"pack": {
        "description": "Dødsfjellet-grafikk: lys og glad stil for hele spillet", "min_format": 97, "max_format": 200}},
        ensure_ascii=False), encoding="utf-8")
    ikon = Image.open(TEX_UT / "block" / "grass_block_side.png").resize((128, 128), Image.NEAREST)
    ikon.save(PAKKE / "pack.png")
    print(f"{antall} blokkteksturer, {biomer} biomer omfarget")


if __name__ == "__main__":
    main()
