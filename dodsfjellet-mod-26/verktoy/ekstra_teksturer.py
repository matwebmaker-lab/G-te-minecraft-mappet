"""Ekstra teksturer: vakt-egg, Blodhøst-ikon, Skyggedolken og ikonene til 3D-våpnene (rendret i Blender)."""
import colorsys
from pathlib import Path

from PIL import Image

HER = Path(__file__).resolve().parent.parent
TEX = HER / "src" / "main" / "resources" / "assets" / "dodsfjellet" / "textures"
IKONER = HER / "verktoy" / "ikoner"          # 32x32-ikoner fra Blender-renderne
V1 = HER.parent / "dodsfjellet-mod" / "src" / "main" / "resources" / "assets" / "dodsfjellet" / "textures" / "item"


def egg():
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = img.load()
    for y in range(16):
        for x in range(16):
            dx, dy = (x - 7.5) / 5.6, (y - 8.8) / 6.9
            if dy < 0:
                dx *= 1.0 + dy * 0.25
            if dx * dx + dy * dy <= 1.0:
                kant = dx * dx + dy * dy > 0.72
                px[x, y] = (18, 16, 26, 255) if kant else (43, 40, 56, 255)
    for (x, y) in [(5, 6), (9, 5), (7, 9), (10, 10), (5, 11), (8, 12)]:
        px[x, y] = (176, 32, 32, 255)
        px[x + 1, y] = (120, 20, 24, 255)
    px[6, 4] = (90, 86, 110, 255)
    return img


def effektikon():
    img = Image.new("RGBA", (18, 18), (0, 0, 0, 0))
    px = img.load()
    for y in range(18):
        for x in range(18):
            dx, dy = (x - 8.5) / 6.5, (y - 9.5) / 7.5
            if dy < -0.2:
                dx = abs(dx) - (dy + 0.2) * 0.9
            if dx * dx + dy * dy <= 1.0:
                px[x, y] = (150, 15, 25, 255) if dx * dx + dy * dy > 0.5 else (215, 40, 45, 255)
    px[7, 7] = px[7, 8] = (255, 160, 150, 255)
    return img


def metning(img, faktor):
    img = img.convert("RGBA")
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a:
                h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
                r2, g2, b2 = colorsys.hls_to_rgb(h, l * 0.85, min(1.0, s * faktor))
                px[x, y] = (int(r2 * 255), int(g2 * 255), int(b2 * 255), a)
    return img


def main():
    (TEX / "item").mkdir(parents=True, exist_ok=True)
    (TEX / "mob_effect").mkdir(parents=True, exist_ok=True)
    egg().save(TEX / "item" / "vakt_spawn_egg.png")
    effektikon().save(TEX / "mob_effect" / "blodhost.png")
    if (V1 / "skyggedolk.png").exists():
        Image.open(V1 / "skyggedolk.png").save(TEX / "item" / "skyggedolk.png")
    for navn in ("sjelesigd", "dodsklinge", "vokterknuser"):
        kilde = IKONER / f"ikon32_{navn}.png"
        if kilde.exists():
            metning(Image.open(kilde), 1.6).save(TEX / "item" / f"{navn}.png")
    print("Ekstra teksturer laget")


if __name__ == "__main__":
    main()
