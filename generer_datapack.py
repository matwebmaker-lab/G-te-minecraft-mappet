"""Genererer datapacken "Dodstrappa" – en sykt dødelig felle-trapp inn i et fjell.

Kjør:  python generer_datapack.py            (Minecraft 1.21.9+ / 26.x)
       python generer_datapack.py --mc 1.21.1  (Minecraft 1.21 - 1.21.4)
Lager mappen  dodstrappa/  og  dodstrappa.zip  (legg zip-en i world/datapacks).

Alt bygges i et lokalt koordinatsystem:
  f = fremover (retningen spilleren ser), r = til høyre, y = opp
og oversettes til ~x ~y ~z for hver av de fire himmelretningene.
"""
import json
import pathlib
import shutil
import sys

# 1.21-1.21.4 bruker JSON-tekst i skilt og clickEvent; 1.21.5+ bruker SNBT-tekst og click_event
GAMMEL = "--mc" in sys.argv and sys.argv[sys.argv.index("--mc") + 1].startswith("1.21.") \
    and int(sys.argv[sys.argv.index("--mc") + 1].split(".")[2] or 0) < 5
ROT = pathlib.Path(__file__).parent
PACK = ROT / ("dodstrappa_1.21.1" if GAMMEL else "dodstrappa")
NS = "dt"

SKALL = "minecraft:deepslate_bricks"
GULV = "minecraft:polished_blackstone_bricks"
TRAPP = "minecraft:polished_blackstone_brick_stairs"
PILER = (
    '{Items:[' + ",".join(
        f'{{Slot:{s}b,id:"minecraft:tipped_arrow",count:64,'
        'components:{"minecraft:potion_contents":{potion:"minecraft:strong_harming"}}}'
        for s in range(3)
    ) + ']}'
)

# navn, yaw, fremover-vektor (x, z), høyre-vektor (x, z)
RETNINGER = {
    "sor": (0, (0, 1), (-1, 0)),
    "vest": (90, (-1, 0), (0, -1)),
    "nord": (180, (0, -1), (1, 0)),
    "ost": (-90, (1, 0), (0, 1)),
}
KARDINAL = {(1, 0): "east", (-1, 0): "west", (0, 1): "south", (0, -1): "north"}

# Nøkkelmål (lokale koordinater)
TRAPP1_START = 5     # f for første trinn i trapp 1 (trinn i: f=5+i, y=i)
AVSATS = (15, 19)    # falltrappa (avsats) f-område, gulv y=9
TRAPP2_START = 20    # trinn j: f=20+j, y=10+j
ROM = (30, 38)       # skattekammer, gulv y=19


def skilt_linjer(*linjer):
    if GAMMEL:
        return ",".join("'" + json.dumps(l, ensure_ascii=False) + "'" for l in linjer)
    return ",".join(json.dumps(l, ensure_ascii=False) for l in linjer)


class Bygger:
    def __init__(self, yaw, fwd, hoyre):
        self.yaw, self.fwd, self.hoyre = yaw, fwd, hoyre
        self.cmd = []

    def pos(self, r, y, f):
        x = f * self.fwd[0] + r * self.hoyre[0]
        z = f * self.fwd[1] + r * self.hoyre[1]
        return f"~{x} ~{y} ~{z}"

    def retning(self, navn):
        v = {"fwd": self.fwd, "bak": (-self.fwd[0], -self.fwd[1]),
             "hoyre": self.hoyre, "venstre": (-self.hoyre[0], -self.hoyre[1])}[navn]
        return KARDINAL[v]

    def fill(self, r1, y1, f1, r2, y2, f2, blokk, modus=""):
        self.cmd.append(f"fill {self.pos(r1, y1, f1)} {self.pos(r2, y2, f2)} {blokk}{' ' + modus if modus else ''}")

    def setblock(self, r, y, f, blokk):
        self.cmd.append(f"setblock {self.pos(r, y, f)} {blokk}")

    def marker(self, r, y, f, tag):
        x = f * self.fwd[0] + r * self.hoyre[0] + 0.5
        z = f * self.fwd[1] + r * self.hoyre[1] + 0.5
        self.cmd.append(f'summon minecraft:marker ~{x} ~{y} ~{z} {{Tags:["dt","{tag}"],Rotation:[{self.yaw}f,0f]}}')

    def trinn(self, f, y, bredde=1, lykt=None):
        """Ett trappetrinn med skall rundt: trappeblokk på høyde y, luft over."""
        self.fill(-bredde - 1, y - 1, f, bredde + 1, y + 5, f, SKALL)
        self.fill(-bredde, y + 1, f, bredde, y + 4, f, "minecraft:air")
        self.fill(-bredde, y, f, bredde, y, f, f"{TRAPP}[facing={self.retning('fwd')}]")
        if lykt:
            self.setblock(0, y + 4, f, f"minecraft:{lykt}[hanging=true]")


def bygg(retning):
    yaw, fwd, hoyre = RETNINGER[retning]
    b = Bygger(yaw, fwd, hoyre)
    b.cmd.append("# Generert av generer_datapack.py – ikke rediger for hånd")

    # 1) Inngangshall – ser trygg og innbydende ut
    b.fill(-2, -1, 1, 2, 4, 4, SKALL)
    b.fill(-1, 0, 1, 1, 3, 4, "minecraft:air")
    b.fill(-1, -1, 1, 1, -1, 4, GULV)
    b.setblock(0, 3, 3, "minecraft:lantern[hanging=true]")
    for r, linjer in ((2, ("Hemmelig skatt", "på toppen!")), (-2, ("Helt trygg", "trapp :)"))):
        b.setblock(r, 1, 0, f'minecraft:dark_oak_wall_sign[facing={b.retning("bak")}]'
                            '{front_text:{has_glowing_text:1b,color:"yellow",'
                            f'messages:[{skilt_linjer("", *linjer, "")}]}}}}')

    # 2) Trapp 1 (10 trinn) – med pilfelle på trinn 4-6
    for i in range(10):
        b.trinn(TRAPP1_START + i, i, lykt="lantern" if i in (2, 8) else None)
    for i in (4, 5, 6):
        f = TRAPP1_START + i
        b.setblock(-2, i + 1, f, f"minecraft:dispenser[facing={b.retning('hoyre')}]{PILER}")
        b.setblock(2, i + 1, f, f"minecraft:dispenser[facing={b.retning('venstre')}]{PILER}")
        b.setblock(-3, i + 1, f, SKALL)
        b.setblock(3, i + 1, f, SKALL)
    b.marker(0, 6, TRAPP1_START + 5, "dt_pil")

    # 3) Avsats – ser ut som en hvileplass, men er et falsk gulv over en lavasjakt
    a1, a2 = AVSATS
    b.fill(-2, -22, a1 - 1, 2, 7, a2 + 1, SKALL)          # sjaktvegger
    b.fill(-2, 8, a1, 2, 14, a2, SKALL)
    b.fill(-1, 10, a1, 1, 13, a2, "minecraft:air")
    b.fill(-1, -19, a1, 1, 8, a2, "minecraft:air")          # 28 blokker dyp sjakt
    b.fill(-1, -21, a1, 1, -20, a2, "minecraft:lava")
    b.fill(-1, 9, a1, 1, 9, a2, GULV)                       # det falske gulvet
    b.setblock(0, 13, 17, "minecraft:lantern[hanging=true]")
    b.marker(0, 10, 17, "dt_fall")

    # 4) Trapp 2 (10 trinn) – lavakammer på trinn 2-8, ingen lys = mørkt og ekkelt
    for j in range(10):
        b.trinn(TRAPP2_START + j, 10 + j, lykt="soul_lantern" if j == 0 else None)
    b.marker(0, 16, TRAPP2_START + 5, "dt_lava")

    # 5) Skattekammeret på toppen
    r1, r2 = ROM
    b.fill(-3, 18, r1, 3, 25, r2, SKALL)
    b.fill(-2, 20, r1, 2, 24, r2, "minecraft:air")
    b.fill(-2, 19, r1, 2, 19, r2, GULV)
    b.fill(-1, 19, 35, 1, 19, 37, "minecraft:gold_block")
    b.setblock(-1, 20, 37, "minecraft:gold_block")
    b.setblock(1, 20, 37, "minecraft:gold_block")
    b.setblock(0, 20, 37, f"minecraft:chest[facing={b.retning('bak')}]{KISTE}")
    for f in (32, 36):
        b.setblock(-2, 24, f, "minecraft:lantern[hanging=true]")
        b.setblock(2, 24, f, "minecraft:lantern[hanging=true]")
    b.marker(0, 20, 36, "dt_rom")

    b.cmd += [
        'tellraw @s ["",{"text":"[Dødstrappa] ","color":"dark_red","bold":true},'
        '{"text":"Bygget! Gå inn ... hvis du tør. ","color":"gold"},'
        '{"text":"(Creative = trygg, survival = død)","color":"gray","italic":true}]',
        "playsound minecraft:entity.wither.spawn master @s ~ ~ ~ 0.6 0.8",
    ]
    return b.cmd


KISTE = ('{Items:['
         '{Slot:13b,id:"minecraft:diamond",count:16},'
         '{Slot:12b,id:"minecraft:enchanted_golden_apple",count:1},'
         '{Slot:14b,id:"minecraft:netherite_ingot",count:2}]}')

# ---------------------------------------------------------------- feller
# Alle felle-funksjoner kjøres "as <marker> at <marker>", og markøren er rotert
# i byggeretningen, så ^venstre ^opp ^fremover fungerer uansett himmelretning.
OFFER = "@a[gamemode=!creative,gamemode=!spectator"
AKTIV = "if score #aktiv dt_t matches 1"


def felle_tick(navn, radius):
    return [
        f"execute if score @s dt_t matches 1.. run function {NS}:felle/{navn}_nedtelling",
        f"execute {AKTIV} unless score @s dt_t matches 1.. if entity {OFFER},distance=..{radius}] "
        f"run function {NS}:felle/{navn}_utlos",
    ]


def pil_punkter():
    # trinn 4,5,6 relativt til markøren på trinn 5: dy = df
    for df in (-1, 0, 1):
        for side in (3, -3):
            yield side, df, df


def dispensere():
    for df in (-1, 0, 1):
        for side in (2, -2):
            yield side, df, df


def lava_kolonner():
    # trinn 2..8 relativt til markør på trinn 5: innvendig luft fra y=df til df+3
    for df in range(-3, 4):
        yield f"^-1 ^{df} ^{df} ^1 ^{df + 3} ^{df}"


LAVA_SEGL = ["^-1 ^-4 ^-4 ^1 ^-1 ^-4", "^-1 ^4 ^4 ^1 ^7 ^4"]
ROM_DOR = "^-2 ^0 ^-6 ^2 ^4 ^-6"

FUNKSJONER = {
    "load": [
        "scoreboard objectives add dt_t dummy",
        "execute unless score #aktiv dt_t matches 0..1 run scoreboard players set #aktiv dt_t 1",
        'tellraw @a ["",{"text":"[Dødstrappa] ","color":"dark_red","bold":true},'
        '{"text":"lastet. Skriv ","color":"gray"},'
        '{"text":"/function dt:hjelp","color":"yellow",' + (
            '"clickEvent":{"action":"suggest_command","value":"/function dt:hjelp"}}]' if GAMMEL else
            '"click_event":{"action":"suggest_command","command":"/function dt:hjelp"}}]'),
    ],
    "tick": [
        f"execute as @e[type=minecraft:marker,tag=dt_{n}] at @s run function {NS}:felle/{n}_tick"
        for n in ("pil", "fall", "lava", "rom")
    ],
    "bygg": [
        "# Bygger trappa i retningen du ser (snappes til nærmeste himmelretning)",
        "kill @e[type=minecraft:marker,tag=dt]",
        f"execute if entity @s[y_rotation=-45..44.99] at @s align xyz run function {NS}:bygg/sor",
        f"execute if entity @s[y_rotation=45..134.99] at @s align xyz run function {NS}:bygg/vest",
        f"execute if entity @s[y_rotation=-135..-45.01] at @s align xyz run function {NS}:bygg/ost",
        f"execute if entity @s[y_rotation=135..180] at @s align xyz run function {NS}:bygg/nord",
        f"execute if entity @s[y_rotation=-180..-135.01] at @s align xyz run function {NS}:bygg/nord",
    ],
    "av": [
        "scoreboard players set #aktiv dt_t 0",
        'tellraw @s {"text":"[Dødstrappa] Fellene er AV – trygt å gå.","color":"green"}',
    ],
    "paa": [
        "scoreboard players set #aktiv dt_t 1",
        'tellraw @s {"text":"[Dødstrappa] Fellene er PÅ. Lykke til...","color":"red"}',
    ],
    "reparer": [
        f"execute as @e[type=minecraft:marker,tag=dt_fall] at @s run function {NS}:felle/fall_reset",
        f"execute as @e[type=minecraft:marker,tag=dt_lava] at @s run function {NS}:felle/lava_reset",
        f"execute as @e[type=minecraft:marker,tag=dt_rom] at @s run function {NS}:felle/rom_reset",
        f"execute as @e[type=minecraft:marker,tag=dt_pil] at @s run function {NS}:felle/pil_av",
        f"execute as @e[type=minecraft:marker,tag=dt_pil] at @s run function {NS}:felle/pil_fyll",
        f"execute as @e[type=minecraft:marker,tag=dt_rom] at @s run data merge block ^ ^ ^1 {KISTE}",
        "scoreboard players set @e[type=minecraft:marker,tag=dt] dt_t 0",
        'tellraw @s {"text":"[Dødstrappa] Alle feller er reparert og ladd på nytt.","color":"gold"}',
    ],
    "fjern": [
        "kill @e[type=minecraft:marker,tag=dt]",
        'tellraw @s {"text":"[Dødstrappa] Fellene er fjernet (bygget står igjen).","color":"gray"}',
    ],
    "finn_fjell": [
        "# Skriver ut nærmeste fjelltopp – klikk på koordinatene for å teleportere",
        "locate biome minecraft:jagged_peaks",
        "locate biome minecraft:stony_peaks",
    ],
    "hjelp": [
        'tellraw @s {"text":"===== DØDSTRAPPA =====","color":"dark_red","bold":true}',
        'tellraw @s {"text":"1. /function dt:finn_fjell  – finn et fjell (klikk koordinatene)","color":"gray"}',
        'tellraw @s {"text":"2. Stå ved foten av fjellet, se mot fjellet","color":"gray"}',
        'tellraw @s {"text":"3. /function dt:bygg  – bygger trappa inn i fjellet","color":"gray"}',
        'tellraw @s {"text":"/function dt:av | dt:paa | dt:reparer | dt:fjern","color":"yellow"}',
        'tellraw @s {"text":"Creative-spillere trigger ingenting – survival-spillere dør.","color":"red"}',
    ],

    # --- Felle 1: pilregn med Harming II-piler fra veggene
    "felle/pil_tick": felle_tick("pil", 2.2),
    "felle/pil_utlos": [f"setblock ^{s} ^{y} ^{f} minecraft:redstone_block" for s, y, f in pil_punkter()] + [
        "playsound minecraft:entity.skeleton.shoot hostile @a ~ ~ ~ 1.5 0.6",
        "scoreboard players set @s dt_t 10",
    ],
    "felle/pil_nedtelling": [
        "scoreboard players remove @s dt_t 1",
        f"execute if score @s dt_t matches 8 run function {NS}:felle/pil_av",
    ],
    "felle/pil_av": [f"setblock ^{s} ^{y} ^{f} {SKALL}" for s, y, f in pil_punkter()],
    "felle/pil_fyll": [f"data merge block ^{s} ^{y} ^{f} {PILER}" for s, y, f in dispensere()],

    # --- Felle 2: avsatsen kollapser ned i en 28 blokker dyp lavasjakt
    "felle/fall_tick": felle_tick("fall", 2.4),
    "felle/fall_utlos": [
        "fill ^-1 ^-1 ^-2 ^1 ^-1 ^2 minecraft:air destroy",
        "playsound minecraft:block.deepslate_bricks.break block @a ~ ~ ~ 2 0.5",
        "playsound minecraft:entity.zombie.break_wooden_door hostile @a ~ ~ ~ 2 0.5",
        "particle minecraft:large_smoke ~ ~ ~ 1 0.2 2 0.02 60",
        f'title {OFFER},distance=..4] actionbar {{"text":"Gulvet forsvant...","color":"red"}}',
        "kill @e[type=minecraft:item,distance=..4]",
        "scoreboard players set @s dt_t 80",
    ],
    "felle/fall_nedtelling": [
        "scoreboard players remove @s dt_t 1",
        f"execute if score @s dt_t matches 0 run function {NS}:felle/fall_reset",
    ],
    "felle/fall_reset": [f"fill ^-1 ^-1 ^-2 ^1 ^-1 ^2 {GULV}"],

    # --- Felle 3: lavakammer – porter lukkes bak og foran, så fylles alt med lava
    "felle/lava_tick": felle_tick("lava", 1.8),
    "felle/lava_utlos": [f"fill {s} minecraft:obsidian replace minecraft:air" for s in LAVA_SEGL] + [
        "playsound minecraft:block.iron_door.close block @a ~ ~ ~ 2 0.5",
        "playsound minecraft:block.portal.trigger ambient @a ~ ~ ~ 1 0.5",
        f'title {OFFER},distance=..6] title {{"text":"Det finnes ingen vei ut","color":"dark_red"}}',
        "scoreboard players set @s dt_t 120",
    ],
    "felle/lava_nedtelling": [
        "scoreboard players remove @s dt_t 1",
        f"execute if score @s dt_t matches 100 run function {NS}:felle/lava_fyll",
        f"execute if score @s dt_t matches 0 run function {NS}:felle/lava_reset",
    ],
    "felle/lava_fyll": [f"fill {k} minecraft:lava replace minecraft:air" for k in lava_kolonner()] + [
        "playsound minecraft:item.bucket.empty_lava block @a ~ ~ ~ 2 0.5",
    ],
    "felle/lava_reset": [f"fill {k} minecraft:air replace minecraft:lava" for k in lava_kolonner()]
    + [f"fill {s} minecraft:air replace minecraft:obsidian" for s in LAVA_SEGL],

    # --- Felle 4: skattekammeret – døra stenges og gulvet eksploderer i evoker-hoggtenner
    "felle/rom_tick": felle_tick("rom", 2.2),
    "felle/rom_utlos": [
        f"fill {ROM_DOR} minecraft:iron_bars replace minecraft:air",
        "playsound minecraft:entity.warden.roar hostile @a ~ ~ ~ 2 0.8",
        f'title {OFFER},distance=..10] title {{"text":"GRÅDIG?","color":"dark_red","bold":true}}',
        f'title {OFFER},distance=..10] subtitle {{"text":"skatten var aldri din","color":"gray"}}',
        "scoreboard players set @s dt_t 100",
    ],
    "felle/rom_nedtelling": [
        "scoreboard players remove @s dt_t 1",
        f"execute if score @s dt_t matches ..90 as {OFFER},distance=..8] at @s run summon minecraft:evoker_fangs ~ ~ ~",
        f"execute if score @s dt_t matches ..90 as {OFFER},distance=..8] at @s run summon minecraft:evoker_fangs ~1 ~ ~",
        f"execute if score @s dt_t matches ..90 as {OFFER},distance=..8] at @s run summon minecraft:evoker_fangs ~-1 ~ ~",
        f"execute if score @s dt_t matches 0 run function {NS}:felle/rom_reset",
    ],
    "felle/rom_reset": [f"fill {ROM_DOR} minecraft:air replace minecraft:iron_bars"],
}


def main():
    if PACK.exists():
        shutil.rmtree(PACK)
    fdir = PACK / "data" / NS / "function"
    for navn, linjer in FUNKSJONER.items():
        sti = fdir / f"{navn}.mcfunction"
        sti.parent.mkdir(parents=True, exist_ok=True)
        sti.write_text("\n".join(linjer) + "\n", encoding="utf-8")
    for retning in RETNINGER:
        sti = fdir / "bygg" / f"{retning}.mcfunction"
        sti.parent.mkdir(parents=True, exist_ok=True)
        sti.write_text("\n".join(bygg(retning)) + "\n", encoding="utf-8")

    tags = PACK / "data" / "minecraft" / "tags" / "function"
    tags.mkdir(parents=True)
    (tags / "load.json").write_text(json.dumps({"values": [f"{NS}:load"]}, indent=2))
    (tags / "tick.json").write_text(json.dumps({"values": [f"{NS}:tick"]}, indent=2))

    beskrivelse = "§4Dødstrappa§r – en sykt dødelig felle-trapp inn i fjellet"
    format_ = ({"pack_format": 48, "supported_formats": [48, 61]} if GAMMEL
               else {"min_format": 88, "max_format": 200})
    (PACK / "pack.mcmeta").write_text(json.dumps({"pack": {"description": beskrivelse, **format_}},
                                                 indent=2, ensure_ascii=False), encoding="utf-8")

    zip_sti = shutil.make_archive(str(PACK), "zip", PACK)
    antall = sum(1 for _ in fdir.rglob("*.mcfunction"))
    print(f"Laget {antall} funksjoner -> {zip_sti}")


if __name__ == "__main__":
    main()
