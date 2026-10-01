"""Strukturene i Dødsriket: bygges prosedyrisk og lagres som NBT-maler (DataVersion 5023, Minecraft 26.3).

  Dødslandsbyen  – hus av dødsved, oppgraderingssmie, lyktestolper, vakttårn. Vakter patruljerer.
  Dødsgrotta     – skjult grottehall dypt under bakken med vakt-spawnere og skattekiste.
  Bentårnet      – høyt tårn av ben og dødsstein; runekiste på toppen.
  Sjelealteret   – lite alter med smie og en kiste med krystaller.

Skriver også worldgen/structure, structure_set, template_pool og kiste-loot.
"""
import gzip
import json
import math
import random
import struct
from pathlib import Path

HER = Path(__file__).resolve().parent.parent
D = HER / "src" / "main" / "resources" / "data" / "dodsfjellet"
NS = "dodsfjellet"
DATA_VERSION = 5023


# ---------------------------------------------------------------- minimal NBT-skriver
class Liste(list):
    def __init__(self, typ, verdier):
        super().__init__(verdier)
        self.typ = typ


class Int(int):
    pass


def _type(v):
    if isinstance(v, bool):
        return 1
    if isinstance(v, Int):
        return 3
    if isinstance(v, int):
        return 3
    if isinstance(v, float):
        return 6
    if isinstance(v, str):
        return 8
    if isinstance(v, Liste):
        return 9
    if isinstance(v, list):
        return 9
    if isinstance(v, dict):
        return 10
    raise TypeError(v)


def _skriv(v, t):
    if t == 1:
        return struct.pack(">b", int(v))
    if t == 3:
        return struct.pack(">i", v)
    if t == 6:
        return struct.pack(">d", v)
    if t == 8:
        e = v.encode("utf-8")
        return struct.pack(">H", len(e)) + e
    if t == 9:
        et = v.typ if isinstance(v, Liste) else (_type(v[0]) if v else 0)
        return struct.pack(">bi", et, len(v)) + b"".join(_skriv(x, et) for x in v)
    if t == 10:
        ut = b""
        for k, x in v.items():
            tt = _type(x)
            e = k.encode("utf-8")
            ut += struct.pack(">bH", tt, len(e)) + e + _skriv(x, tt)
        return ut + b"\x00"


def lagre_nbt(sti, rot):
    sti.parent.mkdir(parents=True, exist_ok=True)
    with open(sti, "wb") as f:
        f.write(gzip.compress(b"\x0a\x00\x00" + _skriv(rot, 10)))


# ---------------------------------------------------------------- byggeverktøy
LUFT = "minecraft:air"


class Bygg:
    def __init__(self, sx, sy, sz, frø=1):
        self.s = (sx, sy, sz)
        self.b = {}
        self.r = random.Random(frø)

    def set(self, x, y, z, blokk, props=None, nbt=None):
        if 0 <= x < self.s[0] and 0 <= y < self.s[1] and 0 <= z < self.s[2]:
            self.b[(x, y, z)] = (blokk, props or {}, nbt)

    def fyll(self, x1, y1, z1, x2, y2, z2, blokk, props=None):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    self.set(x, y, z, blokk, props)

    def hul(self, x1, y1, z1, x2, y2, z2, vegg, inni=LUFT):
        self.fyll(x1, y1, z1, x2, y2, z2, vegg)
        self.fyll(x1 + 1, y1 + 1, z1 + 1, x2 - 1, y2 - 1, z2 - 1, inni)

    def kiste(self, x, y, z, facing, loot):
        self.set(x, y, z, "minecraft:chest", {"facing": facing, "type": "single", "waterlogged": "false"},
                 {"id": "minecraft:chest", "LootTable": f"{NS}:chests/{loot}"})

    def spawner(self, x, y, z):
        self.set(x, y, z, "minecraft:spawner", None, {
            "id": "minecraft:mob_spawner", "SpawnData": {"entity": {"id": f"{NS}:vakt"}},
            "Delay": Int(20), "MinSpawnDelay": Int(300), "MaxSpawnDelay": Int(700), "SpawnCount": Int(1),
            "MaxNearbyEntities": Int(3), "RequiredPlayerRange": Int(14), "SpawnRange": Int(4)})

    def lykt(self, x, y, z, hengende=True, sjel=True):
        self.set(x, y, z, "minecraft:soul_lantern" if sjel else "minecraft:lantern",
                 {"hanging": "true" if hengende else "false", "waterlogged": "false"})

    def lagre(self, navn):
        palett, idx, blokker = [], {}, []
        for pos, (blokk, props, nbt) in sorted(self.b.items()):
            nokkel = (blokk, tuple(sorted(props.items())))
            if nokkel not in idx:
                idx[nokkel] = len(palett)
                e = {"id": blokk}
                if props:
                    e["properties"] = dict(props)
                palett.append(e)
            b = {"pos": Liste(3, [Int(p) for p in pos]), "state": Int(idx[nokkel])}
            if nbt:
                b["nbt"] = nbt
            blokker.append(b)
        rot = {"DataVersion": Int(DATA_VERSION), "size": Liste(3, [Int(v) for v in self.s]),
               "palette": Liste(10, palett), "blocks": Liste(10, blokker), "entities": Liste(10, [])}
        lagre_nbt(D / "structure" / f"{navn}.nbt", rot)
        return len(blokker)


def d(n):
    return f"{NS}:{n}"


STEIN, MUR, POLERT = d("dodsstein"), d("dodsstein_murstein"), d("polert_dodsstein")
PLANKE, STAMME, GLOD, ASKE, MALM = d("dodsved_planker"), d("dodsved_stamme"), d("sjeleglod"), d("askejord"), d("dodskrystall_malm")
SMIE = d("oppgraderingssmie")


# ---------------------------------------------------------------- Dødslandsbyen
def hus(b, x0, z0, dor_side, frø):
    r = random.Random(frø)
    w, d_, h = 7, 7, 5
    b.fyll(x0, 1, z0, x0 + w - 1, 1, z0 + d_ - 1, PLANKE)                     # gulv
    b.hul(x0, 1, z0, x0 + w - 1, h, z0 + d_ - 1, PLANKE)
    b.fyll(x0 + 1, 2, z0 + 1, x0 + w - 2, h - 1, z0 + d_ - 2, LUFT)
    for (x, z) in [(x0, z0), (x0 + w - 1, z0), (x0, z0 + d_ - 1), (x0 + w - 1, z0 + d_ - 1)]:
        b.fyll(x, 1, z, x, h, z, STAMME, {"axis": "y"})
    for t in range(4):                                                          # trappetak av murstein
        b.fyll(x0 - 1 + t, h + 1 + t, z0 - 1 + t, x0 + w - t, h + 1 + t, z0 + d_ - t, MUR if t < 3 else GLOD)
        b.fyll(x0 + t, h + 1 + t, z0 + t, x0 + w - 1 - t, h + 1 + t, z0 + d_ - 1 - t, MUR if t < 3 else GLOD)
    # vinduer
    for (x, z) in [(x0 + 2, z0), (x0 + 4, z0), (x0 + 2, z0 + d_ - 1), (x0 + 4, z0 + d_ - 1),
                   (x0, z0 + 3), (x0 + w - 1, z0 + 3)]:
        b.set(x, 3, z, "minecraft:purple_stained_glass_pane")
    # dør
    dx, dz = {"north": (x0 + 3, z0), "south": (x0 + 3, z0 + d_ - 1), "west": (x0, z0 + 3), "east": (x0 + w - 1, z0 + 3)}[dor_side]
    b.set(dx, 2, dz, LUFT)
    b.set(dx, 3, dz, LUFT)
    # innbo
    b.lykt(x0 + 3, h - 1, z0 + 3)
    motsatt = {"north": "south", "south": "north", "west": "east", "east": "west"}[dor_side]
    kx, kz = {"north": (x0 + 1, z0 + 5), "south": (x0 + 1, z0 + 1), "west": (x0 + 5, z0 + 1), "east": (x0 + 1, z0 + 1)}[dor_side]
    b.kiste(kx, 2, kz, dor_side, "landsby")
    b.set(x0 + 5, 2, z0 + 5 if dor_side != "south" else z0 + 1, "minecraft:crafting_table")
    if r.random() < 0.5:
        b.set(x0 + 5, 2, z0 + 3, "minecraft:cauldron")


def dodslandsbyen():
    S = 37
    b = Bygg(S, 18, S, 11)
    b.fyll(0, 0, 0, S - 1, 0, S - 1, ASKE)
    b.fyll(0, 1, 0, S - 1, 17, S - 1, LUFT)
    # stier
    b.fyll(16, 0, 0, 20, 0, S - 1, POLERT)
    b.fyll(0, 0, 16, S - 1, 0, 20, POLERT)
    # torget
    b.fyll(13, 0, 13, 23, 0, 23, MUR)
    b.fyll(14, 0, 14, 22, 0, 22, POLERT)
    b.set(18, 1, 18, SMIE)
    for (x, z) in [(14, 14), (22, 14), (14, 22), (22, 22)]:
        b.fyll(x, 1, z, x, 3, z, STAMME, {"axis": "y"})
        b.set(x, 4, z, GLOD)
    # brønn med lava
    b.hul(17, 0, 25, 19, 1, 27, MUR)
    b.set(18, 1, 26, "minecraft:lava")
    # hus
    hus(b, 3, 3, "south", 1)
    hus(b, 27, 3, "south", 2)
    hus(b, 3, 27, "north", 3)
    hus(b, 27, 27, "north", 4)
    hus(b, 3, 15, "east", 5)
    # vakttårn
    b.hul(28, 1, 14, 32, 13, 18, MUR)
    b.fyll(29, 1, 15, 31, 12, 17, LUFT)
    b.set(30, 2, 14, LUFT)
    b.set(30, 3, 14, LUFT)
    for y in range(1, 13):
        b.set(30, y, 17, "minecraft:ladder", {"facing": "north", "waterlogged": "false"})
    b.fyll(28, 13, 14, 32, 13, 18, POLERT)
    b.set(30, 13, 17, "minecraft:ladder", {"facing": "north", "waterlogged": "false"})
    for (x, z) in [(28, 14), (32, 14), (28, 18), (32, 18)]:
        b.fyll(x, 14, z, x, 15, z, MUR)
    b.kiste(29, 14, 15, "south", "tarn")
    b.lykt(30, 16, 16, hengende=False)
    # lyktestolper langs stiene
    for (x, z) in [(15, 4), (21, 9), (15, 30), (21, 33), (4, 21), (9, 15), (30, 21), (34, 15)]:
        b.fyll(x, 1, z, x, 3, z, STAMME, {"axis": "y"})
        b.lykt(x, 4, z, hengende=False)
    return b.lagre("dodslandsbyen")


# ---------------------------------------------------------------- Dødsgrotta
def dodsgrotta():
    S, H = 31, 15
    b = Bygg(S, H, S, 22)
    c = (S - 1) / 2
    for x in range(S):
        for y in range(H):
            for z in range(S):
                dx, dy, dz = (x - c) / 14.5, (y - 6.5) / 7.0, (z - c) / 14.5
                r2 = dx * dx + dy * dy + dz * dz
                if r2 <= 0.78:
                    b.set(x, y, z, LUFT)
                elif r2 <= 1.0:
                    b.set(x, y, z, MALM if b.r.random() < 0.08 else STEIN)
    for x in range(S):                                                         # gulv
        for z in range(S):
            for y in range(H):
                if b.b.get((x, y, z), (None,))[0] == LUFT:
                    b.set(x, y, z, ASKE if b.r.random() < 0.7 else d("blodmose"))
                    break
    rr = random.Random(5)
    for _ in range(40):                                                        # krystaller i taket
        x, z = rr.randrange(4, S - 4), rr.randrange(4, S - 4)
        for y in range(H - 1, 0, -1):
            if b.b.get((x, y, z), (None,))[0] == LUFT:
                for k in range(rr.randint(1, 3)):
                    b.set(x, y - k, z, GLOD)
                break
    b.spawner(9, 3, 15)
    b.spawner(21, 3, 15)
    b.fyll(14, 2, 14, 16, 2, 16, POLERT)
    b.kiste(15, 3, 15, "south", "grotte")
    b.lykt(15, 4, 14, hengende=False)
    return b.lagre("dodsgrotta")


# ---------------------------------------------------------------- Bentårnet
def bentarnet():
    b = Bygg(11, 30, 11, 33)
    b.fyll(0, 0, 0, 10, 0, 10, MUR)
    for y in range(1, 26):
        for x in range(1, 10):
            for z in range(1, 10):
                d_ = max(abs(x - 5), abs(z - 5))
                if d_ == 4:
                    b.set(x, y, z, "minecraft:bone_block" if (y // 3) % 2 == 0 else STEIN, {"axis": "y"} if (y // 3) % 2 == 0 else None)
                elif d_ < 4:
                    b.set(x, y, z, LUFT)
    for y in range(4, 25, 5):                                                  # vinduer
        for (x, z) in [(5, 1), (5, 9), (1, 5), (9, 5)]:
            b.set(x, y, z, "minecraft:iron_bars")
    b.set(5, 1, 1, LUFT)
    b.set(5, 2, 1, LUFT)
    for y in range(1, 25):                                                     # stige
        b.set(5, y, 8, "minecraft:ladder", {"facing": "north", "waterlogged": "false"})
    for y in range(6, 25, 6):                                                  # mellomgulv
        b.fyll(2, y, 2, 8, y, 7, PLANKE)
        b.lykt(3, y - 1, 3)
    b.fyll(1, 25, 1, 9, 25, 9, POLERT)
    b.set(5, 25, 8, "minecraft:ladder", {"facing": "north", "waterlogged": "false"})
    for (x, z) in [(1, 1), (9, 1), (1, 9), (9, 9)]:
        b.fyll(x, 26, z, x, 28, z, "minecraft:bone_block", {"axis": "y"})
        b.set(x, 29, z, GLOD)
    b.kiste(5, 26, 4, "south", "tarn")
    b.spawner(5, 1, 5)
    return b.lagre("bentarnet")


# ---------------------------------------------------------------- Sjelealteret
def sjelealteret():
    b = Bygg(11, 8, 11, 44)
    b.fyll(0, 0, 0, 10, 0, 10, MUR)
    b.fyll(1, 0, 1, 9, 0, 9, POLERT)
    b.fyll(0, 1, 0, 10, 7, 10, LUFT)
    for (x, z) in [(1, 1), (9, 1), (1, 9), (9, 9)]:
        b.fyll(x, 1, z, x, 4, z, MUR)
        b.set(x, 5, z, GLOD)
    b.set(5, 1, 5, SMIE)
    b.kiste(5, 1, 3, "north", "alter")
    b.set(4, 1, 5, "minecraft:soul_lantern", {"hanging": "false", "waterlogged": "false"})
    b.set(6, 1, 5, "minecraft:soul_lantern", {"hanging": "false", "waterlogged": "false"})
    return b.lagre("sjelealteret")


# ---------------------------------------------------------------- worldgen-definisjoner og loot
def skriv(sti, data):
    sti.parent.mkdir(parents=True, exist_ok=True)
    sti.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def struktur(navn, biomer, overflate, spacing, separation, salt, monstre=None, hoyde=None):
    skriv(D / "worldgen" / "template_pool" / f"{navn}.json", {"fallback": "minecraft:empty", "elements": [
        {"weight": 1, "element": {"element_type": "minecraft:single_pool_element", "location": d(navn),
                                  "processors": "minecraft:empty", "projection": "rigid"}}]})
    s = {"type": "minecraft:jigsaw", "biomes": [d(b) for b in biomer],
         "step": "surface_structures" if overflate else "underground_structures",
         "spawn_overrides": {}, "start_pool": d(navn), "size": 1, "max_distance_from_center": 80,
         "use_expansion_hack": False}
    if overflate:
        s.update({"terrain_adaptation": "beard_thin", "start_height": {"absolute": 0},
                  "project_start_to_heightmap": "WORLD_SURFACE_WG"})
    else:
        s.update({"terrain_adaptation": "none", "start_height": hoyde})
    if monstre:
        s["spawn_overrides"] = {"monster": {"bounding_box": "full", "spawns": monstre}}
    skriv(D / "worldgen" / "structure" / f"{navn}.json", s)
    skriv(D / "worldgen" / "structure_set" / f"{navn}.json", {
        "placement": {"type": "minecraft:random_spread", "salt": salt, "spacing": spacing, "separation": separation},
        "structures": [{"structure": d(navn), "weight": 1}]})


RUNER = ["skyggesprang", "sjeleskjold", "dodsnova", "blodhost", "andesprang", "vokterkall"]


def item(navn, vekt, antall=None, mod=None):
    e = {"type": "minecraft:item", "name": navn, "weight": vekt}
    mods = []
    if antall:
        mods.append({"type": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": antall[0], "max": antall[1]}})
    if mod:
        mods += mod
    if mods:
        e["modifier"] = mods
    return e


def loot():
    krystall = d("dodskrystall")
    runer = [item(d(f"rune_{r}"), 1) for r in RUNER]
    plate = [item(d(f"sjeleplate_{x}"), 1) for x in ("hjelm", "brynje", "bukser", "stovler")]
    tabeller = {
        "landsby": [{"rolls": {"type": "minecraft:uniform", "min": 3, "max": 6}, "entries": [
            item(krystall, 30, (2, 6)), item("minecraft:golden_apple", 10, (1, 2)), item("minecraft:bread", 15, (2, 5)),
            item("minecraft:iron_ingot", 12, (2, 5)), item("minecraft:diamond", 4, (1, 2)), item(d("reisekompass"), 2),
            item(d("dodsnokkel"), 1), item("minecraft:arrow", 10, (6, 16))] + [dict(r, weight=2) for r in runer]
                     + [dict(p, weight=1) for p in plate]}],
        "grotte": [{"rolls": {"type": "minecraft:uniform", "min": 4, "max": 7}, "entries": [
            item(krystall, 25, (4, 10)), item("minecraft:enchanted_golden_apple", 3), item("minecraft:diamond", 8, (1, 4)),
            item(d("sjelesigd"), 2), item(d("dodsklinge"), 2)] + [dict(r, weight=5) for r in runer]
                    + [dict(p, weight=4) for p in plate]}],
        "tarn": [{"rolls": 1, "entries": runer},
                 {"rolls": {"type": "minecraft:uniform", "min": 2, "max": 4}, "entries": [
                     item(krystall, 20, (2, 5)), item("minecraft:golden_apple", 6), item("minecraft:ender_pearl", 6, (1, 3))]}],
        "alter": [{"rolls": {"type": "minecraft:uniform", "min": 2, "max": 4}, "entries": [
            item(krystall, 30, (1, 4)), item("minecraft:golden_apple", 8), item("minecraft:experience_bottle", 10, (2, 6))]}],
    }
    for navn, pools in tabeller.items():
        skriv(D / "loot_table" / "chests" / f"{navn}.json",
              {"type": "minecraft:chest", "pools": pools, "random_sequence": d(f"chests/{navn}")})


def main():
    vakt = [{"type": d("vakt"), "count": 1, "weight": 1}]
    print("Dødslandsbyen:", dodslandsbyen(), "blokker")
    print("Dødsgrotta:", dodsgrotta(), "blokker")
    print("Bentårnet:", bentarnet(), "blokker")
    print("Sjelealteret:", sjelealteret(), "blokker")
    struktur("dodslandsbyen", ["askeodet", "dodsskogen", "krystallmarkene"], True, 36, 12, 70451231, monstre=vakt)
    struktur("dodsgrotta", ["dodsgrotta"], False, 24, 8, 88213311,
             hoyde={"type": "minecraft:uniform", "min_inclusive": {"absolute": -40}, "max_inclusive": {"absolute": 10}})
    struktur("bentarnet", ["askeodet", "krystallmarkene", "dodsskogen"], True, 30, 10, 51234987)
    struktur("sjelealteret", ["askeodet", "dodsskogen", "krystallmarkene", "blodmyra"], True, 18, 6, 31337001)
    loot()


if __name__ == "__main__":
    main()
