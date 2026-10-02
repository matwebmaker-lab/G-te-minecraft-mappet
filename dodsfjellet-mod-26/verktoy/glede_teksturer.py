"""Teksturer for de glade tingene: Bibelen, Lyskorset og Glede-ikonet (32x32 pikselkunst)."""
import math
from pathlib import Path

from PIL import Image

HER = Path(__file__).resolve().parent.parent
TEX = HER / "src" / "main" / "resources" / "assets" / "dodsfjellet" / "textures"


def bibel():
    """Lys bok med gullkors og gullsnitt, sett litt på skrå."""
    s = 32
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    px = img.load()
    for y in range(3, 29):
        for x in range(6, 26):
            skyv = (28 - y) // 6                     # litt skrå
            xx = x + skyv - 2
            if not 4 <= xx < 28:
                continue
            if x >= 23:                               # sidene (gullsnitt)
                px[xx, y] = (246, 214, 120, 255) if y % 2 else (232, 196, 96, 255)
            elif x <= 7:                               # ryggen
                px[xx, y] = (122, 30, 38, 255)
            else:                                      # omslaget: dyp rød med lysere kant
                kant = y in (3, 28) or x == 22
                px[xx, y] = (176, 48, 58, 255) if kant else (150, 36, 46, 255)
    # gullkors på omslaget
    for y in range(8, 23):
        for x in range(14, 16):
            xx = x + (28 - y) // 6 - 2
            px[xx, y] = (255, 226, 120, 255)
    for x in range(11, 19):
        for y in range(12, 14):
            xx = x + (28 - y) // 6 - 2
            px[xx, y] = (255, 226, 120, 255)
    # bokmerkebånd
    for y in range(28, 31):
        px[19, y] = (255, 210, 60, 255)
    return img


def lyskors():
    """Gull med lys kjerne."""
    s = 16
    img = Image.new("RGBA", (s, s), (0, 0, 0, 255))
    px = img.load()
    for y in range(s):
        for x in range(s):
            d = min(x, y, s - 1 - x, s - 1 - y)
            g = 0.7 + 0.3 * min(1.0, d / 4) + 0.05 * math.sin(x * 1.3 + y * 0.7)
            px[x, y] = (min(255, int(255 * g)), min(255, int(214 * g)), min(255, int(110 * g)), 255)
    return img


def lyskors_kjerne():
    s = 16
    img = Image.new("RGBA", (s, s), (0, 0, 0, 255))
    px = img.load()
    for y in range(s):
        for x in range(s):
            px[x, y] = (255, 250, 220 + (x + y) % 3 * 10, 255)
    return img


def glede_ikon():
    """Liten sol med et hjerte."""
    s = 18
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    px = img.load()
    for y in range(s):
        for x in range(s):
            d = math.hypot(x - 8.5, y - 8.5)
            if d < 6:
                px[x, y] = (255, 214, 74, 255)
            elif d < 8.5 and (round(math.degrees(math.atan2(y - 8.5, x - 8.5))) // 30) % 2 == 0:
                px[x, y] = (255, 188, 60, 255)
    for (x, y) in [(6, 7), (7, 7), (10, 7), (11, 7), (5, 8), (6, 8), (7, 8), (8, 8), (9, 8), (10, 8), (11, 8), (12, 8),
                   (6, 9), (7, 9), (8, 9), (9, 9), (10, 9), (11, 9), (7, 10), (8, 10), (9, 10), (10, 10), (8, 11), (9, 11)]:
        px[x, y] = (232, 54, 84, 255)
    return img


def main():
    for d in ("item", "block", "mob_effect"):
        (TEX / d).mkdir(parents=True, exist_ok=True)
    bibel().save(TEX / "item" / "bibel.png")
    lyskors().save(TEX / "block" / "lyskors.png")
    lyskors_kjerne().save(TEX / "block" / "lyskors_kjerne.png")
    glede_ikon().save(TEX / "mob_effect" / "glede.png")
    print("Glede-teksturer laget")


if __name__ == "__main__":
    main()
