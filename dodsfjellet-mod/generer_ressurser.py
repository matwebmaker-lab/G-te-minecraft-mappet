"""Lager teksturer, item-modeller og språkfiler for Dødsfjellet-modden.

Teksturene lages ved å fargelegge vanilla-teksturer (fra din egen Minecraft 1.21.1-jar) på nytt:
lysstyrken i hver piksel slås opp i en egen fargepalett.
"""
import io
import json
import os
import zipfile
from pathlib import Path

from PIL import Image

HER = Path(__file__).parent
RES = HER / "src" / "main" / "resources" / "assets" / "dodsfjellet"
JAR = Path(os.environ["APPDATA"]) / ".minecraft" / "versions" / "1.21.1" / "1.21.1.jar"

PALETTER = {
    "skygge": [(10, 4, 18), (45, 15, 70), (110, 50, 170), (190, 140, 255), (240, 225, 255)],
    "glod": [(30, 0, 0), (110, 10, 15), (200, 45, 20), (255, 150, 40), (255, 235, 140)],
    "fjell": [(14, 22, 30), (40, 72, 92), (70, 140, 165), (150, 220, 235), (235, 252, 255)],
}

ITEMS = {  # navn: (vanilla-tekstur, palett, modell-forelder)
    "skyggedolk": ("item/iron_sword", "skygge", "item/handheld"),
    "vokterknuser": ("item/netherite_sword", "glod", "item/handheld"),
    "fjellvokter_hjelm": ("item/netherite_helmet", "fjell", "item/generated"),
    "fjellvokter_brynje": ("item/netherite_chestplate", "fjell", "item/generated"),
    "fjellvokter_bukser": ("item/netherite_leggings", "fjell", "item/generated"),
    "fjellvokter_stovler": ("item/netherite_boots", "fjell", "item/generated"),
}
RUSTNING = {"fjellvokter_layer_1": "models/armor/netherite_layer_1",
            "fjellvokter_layer_2": "models/armor/netherite_layer_2"}

NAVN = {
    "item.dodsfjellet.skyggedolk": "Skyggedolken",
    "item.dodsfjellet.vokterknuser": "Vokterknuseren",
    "item.dodsfjellet.fjellvokter_hjelm": "Fjellvokter-hjelm",
    "item.dodsfjellet.fjellvokter_brynje": "Fjellvokter-brynje",
    "item.dodsfjellet.fjellvokter_bukser": "Fjellvokter-bukser",
    "item.dodsfjellet.fjellvokter_stovler": "Fjellvokter-støvler",
    "item.dodsfjellet.vakt_spawn_egg": "Vakt-egg",
    "entity.dodsfjellet.vakt": "Vakt",
}


def palett_farge(pal, t):
    t = max(0.0, min(1.0, t)) * (len(pal) - 1)
    i = min(int(t), len(pal) - 2)
    f = t - i
    a, b = pal[i], pal[i + 1]
    return tuple(round(a[k] + (b[k] - a[k]) * f) for k in range(3))


def fargelegg(bilde, pal):
    bilde = bilde.convert("RGBA")
    px = bilde.load()
    lys = [0.299 * r + 0.587 * g + 0.114 * b for r, g, b, a in bilde.getdata() if a > 0]
    lo, hi = min(lys), max(lys)
    for y in range(bilde.height):
        for x in range(bilde.width):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            t = ((0.299 * r + 0.587 * g + 0.114 * b) - lo) / max(1.0, hi - lo)
            px[x, y] = (*palett_farge(pal, t), a)
    return bilde


def main():
    with zipfile.ZipFile(JAR) as z:
        def les(sti):
            return Image.open(io.BytesIO(z.read(f"assets/minecraft/textures/{sti}.png")))

        (RES / "textures" / "item").mkdir(parents=True, exist_ok=True)
        (RES / "textures" / "models" / "armor").mkdir(parents=True, exist_ok=True)
        (RES / "models" / "item").mkdir(parents=True, exist_ok=True)
        (RES / "lang").mkdir(parents=True, exist_ok=True)

        for navn, (kilde, pal, forelder) in ITEMS.items():
            fargelegg(les(kilde), PALETTER[pal]).save(RES / "textures" / "item" / f"{navn}.png")
            (RES / "models" / "item" / f"{navn}.json").write_text(json.dumps(
                {"parent": f"minecraft:{forelder}", "textures": {"layer0": f"dodsfjellet:item/{navn}"}}, indent=2))
        for navn, kilde in RUSTNING.items():
            fargelegg(les(kilde), PALETTER["fjell"]).save(RES / "textures" / "models" / "armor" / f"{navn}.png")

    (RES / "models" / "item" / "vakt_spawn_egg.json").write_text(
        json.dumps({"parent": "minecraft:item/template_spawn_egg"}, indent=2))
    for lang in ("en_us", "nb_no", "no_no", "nn_no"):
        (RES / "lang" / f"{lang}.json").write_text(json.dumps(NAVN, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Ressurser laget i", RES)


if __name__ == "__main__":
    main()
