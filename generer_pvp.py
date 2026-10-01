"""Genererer datapacken "PvP-øya" (Minecraft 26.3) – øvingsverden i dimensjonen dodsfjellet:pvp.

Hub med teleportplater + stasjoner:
  Duell-arena (kits)   x=100   Bot-trening   x=200   Buebane     x=300
  Bridge (tidtaking)   x=400   MLG-tårnet    x=500   Parkour     x=600   Alle mot alle  x=700
Teleport skjer via /trigger df_reise (håndteres av Dødsfjellet-modden), så det virker for alle spillere.
Kjør:  python generer_pvp.py  ->  pvp_26/ og pvp_26.zip      Bygg i spillet:  /function pvp:bygg
"""
import json
import shutil
from pathlib import Path

ROT = Path(__file__).parent
PACK = ROT / "pvp_26"
NS = "pvp"
DIM = "dodsfjellet:pvp"

STEIN, MUR, POLERT, GLOD = ("dodsfjellet:dodsstein", "dodsfjellet:dodsstein_murstein",
                            "dodsfjellet:polert_dodsstein", "dodsfjellet:sjeleglod")
Y = 100   # gulvnivå

bygg, tick, filer = [], [], {}


def fill(x1, y1, z1, x2, y2, z2, blokk, modus=""):
    bygg.append(f"fill {x1} {y1} {z1} {x2} {y2} {z2} {blokk}{' ' + modus if modus else ''}")


def setb(x, y, z, blokk):
    bygg.append(f"setblock {x} {y} {z} {blokk}")


def tekst(x, y, z, t, farge="white", skala=1.0, tag="pvp_tekst"):
    bygg.append(f"summon minecraft:text_display {x} {y} {z} {{Tags:[\"{tag}\"],billboard:\"center\",alignment:\"center\","
                f"text:{{text:\"{t}\",color:\"{farge}\",bold:true}},background:1426063360,"
                f"transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],"
                f"scale:[{skala}f,{skala}f,{skala}f]}}}}")


def plattform(x1, z1, x2, z2, y=Y, lys=True):
    fill(x1, y - 1, z1, x2, y - 1, z2, STEIN)
    fill(x1, y, z1, x2, y, z2, POLERT)
    fill(x1, y, z1, x2, y, z1, MUR)
    fill(x1, y, z2, x2, y, z2, MUR)
    fill(x1, y, z1, x1, y, z2, MUR)
    fill(x2, y, z1, x2, y, z2, MUR)
    fill(x1, y + 1, z1, x2, y + 12, z2, "minecraft:air")
    if lys:
        for (x, z) in [(x1, z1), (x2, z1), (x1, z2), (x2, z2)]:
            fill(x, y + 1, z, x, y + 2, z, MUR)
            setb(x, y + 3, z, GLOD)


def sone(x1, y1, z1, x2, y2, z2):
    x1, x2 = sorted((x1, x2)); y1, y2 = sorted((y1, y2)); z1, z2 = sorted((z1, z2))
    return f"@a[x={x1},y={y1},z={z1},dx={x2 - x1},dy={y2 - y1},dz={z2 - z1},gamemode=!spectator]"


def plate(x, z, mal, navn, farge_blokk, farge):
    """3x3 teleportplate: står du på den, sender modden deg til mål (df_reise)."""
    fill(x - 1, Y, z - 1, x + 1, Y, z + 1, farge_blokk)
    setb(x, Y, z, GLOD)
    tekst(x + 0.5, Y + 2.6, z + 0.5, navn, farge, 0.9)
    tick.append(f"execute as {sone(x - 1, Y + 1, z - 1, x + 1, Y + 2, z + 1)} run scoreboard players set @s df_reise {mal}")


def knapp(x, y, z, facing, navn, funksjon, sign_facing=None):
    """Knapp med skilt over. Stigende kant + nærmeste spiller kjører funksjonen."""
    nr = len([f for f in filer if f.startswith("k/")])
    setb(x, y, z, f"minecraft:polished_blackstone_button[face=wall,facing={facing}]")
    setb(x, y + 1, z, f"minecraft:dark_oak_wall_sign[facing={sign_facing or facing}]{{front_text:{{has_glowing_text:1b,"
                      f"color:\"magenta\",messages:[\"\",\"{navn}\",\"\",\"\"]}}}}")
    tick.append(f"execute if block {x} {y} {z} minecraft:polished_blackstone_button[powered=true] unless score #k{nr} pvp_t matches 1 "
                f"run function {NS}:k/{nr}")
    tick.append(f"execute if block {x} {y} {z} minecraft:polished_blackstone_button[powered=false] run scoreboard players set #k{nr} pvp_t 0")
    filer[f"k/{nr}"] = [f"scoreboard players set #k{nr} pvp_t 1",
                        f"execute positioned {x} {y} {z} as @p[distance=..6] at @s run function {NS}:{funksjon}"]


# =========================================================================== kits
def gi(item, antall=1):
    return f"give @s {item} {antall}"


KIT_START = ["clear @s", "effect clear @s", "effect give @s minecraft:instant_health 1 20 true",
             "effect give @s minecraft:saturation 1 20 true"]
NETH_RUST = [gi(f"minecraft:netherite_{d}[enchantments={{\"minecraft:protection\":4,\"minecraft:unbreaking\":3}}]")
             for d in ("helmet", "chestplate", "leggings", "boots")]
DIA_RUST = [gi(f"minecraft:diamond_{d}[enchantments={{\"minecraft:protection\":3}}]") for d in ("helmet", "chestplate", "leggings", "boots")]
KITS = {
    "sverd": KIT_START + [gi("minecraft:netherite_sword[enchantments={\"minecraft:sharpness\":5,\"minecraft:unbreaking\":3}]")]
             + NETH_RUST + [gi("minecraft:golden_apple", 8), gi("minecraft:shield")],
    "oks": KIT_START + [gi("minecraft:netherite_axe[enchantments={\"minecraft:sharpness\":5}]"),
                        gi("minecraft:netherite_sword[enchantments={\"minecraft:sharpness\":3}]"), gi("minecraft:shield")]
           + DIA_RUST + [gi("minecraft:golden_apple", 4)],
    "bue": KIT_START + [gi("minecraft:bow[enchantments={\"minecraft:power\":5,\"minecraft:infinity\":1,\"minecraft:punch\":1}]"),
                        gi("minecraft:arrow"), gi("minecraft:crossbow[enchantments={\"minecraft:quick_charge\":3}]"),
                        gi("minecraft:arrow", 32), gi("minecraft:iron_sword")] + DIA_RUST + [gi("minecraft:golden_apple", 4)],
    "mace": KIT_START + [gi("minecraft:mace[enchantments={\"minecraft:density\":5,\"minecraft:wind_burst\":1}]"),
                         gi("minecraft:wind_charge", 32), gi("minecraft:diamond_sword")] + DIA_RUST + [gi("minecraft:golden_apple", 6)],
    "pot": KIT_START + [gi("minecraft:netherite_sword[enchantments={\"minecraft:sharpness\":5}]")] + NETH_RUST
           + [gi("minecraft:splash_potion[potion_contents=\"minecraft:strong_healing\"]", 1) for _ in range(10)]
           + [gi("minecraft:potion[potion_contents=\"minecraft:strong_swiftness\"]", 1) for _ in range(2)]
           + [gi("minecraft:ender_pearl", 8)],
    "dodsrike": KIT_START + [gi("dodsfjellet:sjelesigd"), gi("dodsfjellet:dodsklinge"), gi("dodsfjellet:rune_skyggesprang"),
                             gi("dodsfjellet:rune_dodsnova"), gi("dodsfjellet:rune_sjeleskjold")]
                + [gi(f"dodsfjellet:sjeleplate_{d}") for d in ("hjelm", "brynje", "bukser", "stovler")] + [gi("minecraft:golden_apple", 6)],
}
for navn, cmds in KITS.items():
    filer[f"kit/{navn}"] = cmds + [f'title @s actionbar {{text:"Kit: {navn}",color:"gold"}}',
                                   "playsound minecraft:item.armor.equip_netherite player @s ~ ~ ~ 1 1"]

# =========================================================================== HUB
plattform(-13, -13, 13, 13)
fill(-3, Y, -3, 3, Y, 3, MUR)
fill(-2, Y, -2, 2, Y, 2, GLOD)
tekst(0.5, Y + 6, 0.5, "PvP-ØYA", "light_purple", 3.0)
tekst(0.5, Y + 4.6, 0.5, "Gå på en plate for å reise  •  /reise viser menyen", "gray", 0.8)
PLATER = [(1, "Dødsfjellet", "minecraft:red_concrete", "red"), (2, "Dødsriket", "minecraft:purple_concrete", "dark_purple"),
          (4, "Duell", "minecraft:orange_concrete", "gold"), (5, "Bot-trening", "minecraft:gray_concrete", "gray"),
          (6, "Buebane", "minecraft:yellow_concrete", "yellow"), (7, "Bridge", "minecraft:light_blue_concrete", "aqua"),
          (8, "MLG-tårnet", "minecraft:blue_concrete", "blue"), (9, "Parkour", "minecraft:lime_concrete", "green"),
          (10, "Alle mot alle", "minecraft:crimson_planks", "dark_red")]
import math
for i, (mal, navn, blokk, farge) in enumerate(PLATER):
    v = i / len(PLATER) * 2 * math.pi
    plate(round(math.cos(v) * 9), round(math.sin(v) * 9), mal, navn, blokk, farge)


def tilbake(x, z):
    plate(x, z, 3, "Til huben", "minecraft:purple_concrete", "light_purple")


# =========================================================================== DUELL (x=100)
plattform(84, -16, 116, 16)
for (x1, z1, x2, z2) in [(84, -16, 116, -16), (84, 16, 116, 16), (84, -16, 84, 16), (116, -16, 116, 16)]:
    fill(x1, Y + 1, z1, x2, Y + 4, z2, MUR)
fill(84, Y + 5, -16, 116, Y + 5, -16, GLOD)
fill(84, Y + 5, 16, 116, Y + 5, 16, GLOD)
for (x, z) in [(94, -6), (106, 6), (94, 6), (106, -6)]:      # dekning
    fill(x, Y + 1, z, x + 1, Y + 3, z + 1, STEIN)
tekst(100.5, Y + 8, 0.5, "DUELL-ARENA", "gold", 2.0)
for side, z, facing in (("A", -15, "south"), ("B", 15, "north")):
    for i, kit in enumerate(["sverd", "oks", "bue", "mace", "pot", "dodsrike"]):
        knapp(95 + i * 2, Y + 2, z, facing, kit.capitalize(), f"kit/{kit}")
tilbake(100, -12)
tilbake(100, 12)

# =========================================================================== BOT-TRENING (x=200)
plattform(186, -14, 214, 14)
fill(186, Y + 1, -14, 214, Y + 4, -14, MUR)
fill(186, Y + 1, -2, 214, Y + 3, -2, "minecraft:iron_bars")
fill(199, Y + 1, -2, 201, Y + 3, -2, "minecraft:air")
tekst(200.5, Y + 8, 0.5, "BOT-TRENING", "gray", 2.0)
BOT_SPAWN = "200 101 8"
BOTS = {
    "lett": ',CustomName:{text:"Lett bot",color:"green"},Health:14f,attributes:[{id:"minecraft:max_health",base:14d}],'
            'equipment:{mainhand:{id:"minecraft:stone_sword",count:1},head:{id:"minecraft:leather_helmet",count:1},'
            'chest:{id:"minecraft:leather_chestplate",count:1},legs:{id:"minecraft:leather_leggings",count:1},feet:{id:"minecraft:leather_boots",count:1}},Epler:0',
    "normal": ',equipment:{mainhand:{id:"minecraft:iron_sword",count:1},head:{id:"minecraft:iron_helmet",count:1},'
              'chest:{id:"minecraft:iron_chestplate",count:1},legs:{id:"minecraft:iron_leggings",count:1},feet:{id:"minecraft:iron_boots",count:1}}',
    "vanskelig": ',Health:30f,attributes:[{id:"minecraft:max_health",base:30d},{id:"minecraft:movement_speed",base:0.33d}],'
                 'equipment:{mainhand:{id:"minecraft:diamond_sword",count:1},head:{id:"minecraft:diamond_helmet",count:1},'
                 'chest:{id:"minecraft:diamond_chestplate",count:1},legs:{id:"minecraft:diamond_leggings",count:1},feet:{id:"minecraft:diamond_boots",count:1}},Epler:4',
    "mester": ',CustomName:{text:"Treningsmesteren",color:"dark_red",bold:true},Health:80f,'
              'attributes:[{id:"minecraft:max_health",base:80d},{id:"minecraft:movement_speed",base:0.34d},{id:"minecraft:attack_damage",base:3d}],'
              'equipment:{mainhand:{id:"dodsfjellet:dodsklinge",count:1},head:{id:"dodsfjellet:sjeleplate_hjelm",count:1},'
              'chest:{id:"dodsfjellet:sjeleplate_brynje",count:1},legs:{id:"dodsfjellet:sjeleplate_bukser",count:1},feet:{id:"dodsfjellet:sjeleplate_stovler",count:1}},Epler:6',
}
for i, (navn, nbt) in enumerate(BOTS.items()):
    filer[f"bot/{navn}"] = [f"execute in {DIM} run summon dodsfjellet:vakt {BOT_SPAWN} "
                            f"{{Tags:[\"pvp_bot\",\"df_vakt\"],PersistenceRequired:1b{nbt}}}",
                            "playsound minecraft:entity.evoker.prepare_summon hostile @s ~ ~ ~ 1 1"]
    knapp(196 + i * 2, Y + 2, -13, "south", navn.capitalize(), f"bot/{navn}")
filer["bot/fjern"] = [f"execute in {DIM} run kill @e[type=dodsfjellet:vakt,tag=pvp_bot]"]
knapp(206, Y + 2, -13, "south", "Fjern bots", "bot/fjern")
knapp(208, Y + 2, -13, "south", "Kit", "kit/sverd")
tilbake(200, -10)

# =========================================================================== BUEBANE (x=300)
plattform(288, -8, 344, 8)
tekst(316.5, Y + 9, 0.5, "BUEBANE", "yellow", 2.0)
fill(288, Y + 1, -8, 296, Y + 4, -8, MUR)
BLINKER = [(310, Y + 2, 0), (320, Y + 3, -5), (320, Y + 3, 5), (332, Y + 4, 0), (342, Y + 6, -6), (342, Y + 6, 6)]
for n, (x, y, z) in enumerate(BLINKER):
    fill(x, Y + 1, z, x, y - 1, z, MUR)
    setb(x, y, z, "minecraft:target")
    setb(x, y + 1, z, GLOD)
    tick.append(f"execute unless score #b{n} pvp_t matches 1 unless block {x} {y} {z} minecraft:target[power=0] "
                f"run function {NS}:bue/treff{n}")
    tick.append(f"execute if block {x} {y} {z} minecraft:target[power=0] run scoreboard players set #b{n} pvp_t 0")
    filer[f"bue/treff{n}"] = [
        f"scoreboard players set #b{n} pvp_t 1",
        f"execute positioned 292 101 0 as @p[distance=..20] run scoreboard players add @s pvp_treff 1",
        f"playsound minecraft:block.note_block.bell player @a 292 101 0 1 {1.0 + n * 0.1:.1f}",
        f"execute positioned 292 101 0 as @p[distance=..20] run title @s actionbar [{{text:\"Treff! \",color:\"gold\"}},"
        f"{{score:{{name:\"@s\",objective:\"pvp_treff\"}},color:\"yellow\"}}]"]
filer["bue/null"] = ["scoreboard players set @s pvp_treff 0", 'title @s actionbar {text:"Poeng nullstilt",color:"gray"}']
knapp(290, Y + 2, -7, "south", "Bue-kit", "kit/bue")
knapp(292, Y + 2, -7, "south", "Nullstill", "bue/null")
tilbake(292, 5)

# =========================================================================== BRIDGE (x=400)
plattform(395, -4, 405, 4)
plattform(452, -4, 460, 4)
tekst(400.5, Y + 7, 0.5, "BRIDGE", "aqua", 2.0)
tekst(456.5, Y + 6, 0.5, "MÅL", "green", 2.0)
filer["bridge/start"] = [
    f"execute in {DIM} run fill 406 90 -4 451 110 4 minecraft:air",
    "clear @s",
    f"give @s {MUR} 64", f"give @s {MUR} 64", "give @s minecraft:netherite_pickaxe",
    "tag @s add pvp_bridge", "scoreboard players set @s pvp_tid 0",
    "tp @s 403.5 101 0.5 -90 0",
    'title @s title {text:"GO!",color:"green",bold:true}']
fill(395, Y + 1, -4, 401, Y + 4, -4, MUR)
knapp(398, Y + 2, -3, "south", "Start", "bridge/start")
tick.append("scoreboard players add @a[tag=pvp_bridge] pvp_tid 1")
tick.append(f"execute as {sone(452, Y + 1, -4, 460, Y + 3, 4)}[tag=pvp_bridge] run function {NS}:bridge/maal".replace("][", ","))
filer["bridge/maal"] = [
    "tag @s remove pvp_bridge",
    "scoreboard players operation @s pvp_sek = @s pvp_tid",
    "scoreboard players operation @s pvp_sek /= #20 pvp_t",
    'tellraw @a [{selector:"@s",color:"aqua"},{text:" klarte bridge-banen på ",color:"gray"},'
    '{score:{name:"@s",objective:"pvp_sek"},color:"gold"},{text:" sekunder!",color:"gray"}]',
    "playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1"]
tilbake(400, 3)

# =========================================================================== MLG-TÅRNET (x=500)
plattform(478, -22, 522, 22)
fill(497, 179, -3, 503, 179, 3, MUR)
fill(498, 180, -2, 502, 180, 2, POLERT)
for (x, z) in [(497, -3), (503, -3), (497, 3), (503, 3)]:
    setb(x, 180, z, GLOD)
fill(499, Y + 1, -1, 501, 178, 1, "minecraft:air")
tekst(500.5, 184, 0.5, "MLG-TÅRNET", "blue", 2.0)
tekst(500.5, Y + 6, 10.5, "Plate = tilbake til toppen", "gray", 0.8)
filer["mlg/botte"] = ["clear @s", "give @s minecraft:water_bucket", 'title @s actionbar {text:"Hopp! Plasser vann før du lander",color:"aqua"}']
filer["mlg/hoy"] = ["clear @s", "give @s minecraft:hay_block", 'title @s actionbar {text:"Høyballe-MLG",color:"gold"}']
filer["mlg/slim"] = ["clear @s", "give @s minecraft:slime_block", 'title @s actionbar {text:"Slim-MLG",color:"green"}']
filer["mlg/fiende"] = ["clear @s", "give @s minecraft:cobweb", 'title @s actionbar {text:"Spindelvev-MLG",color:"white"}']
fill(497, 181, -3, 503, 183, -3, MUR)
for i, (navn, f) in enumerate([("Vannbøtte", "mlg/botte"), ("Høyballe", "mlg/hoy"), ("Slim", "mlg/slim"), ("Spindelvev", "mlg/fiende")]):
    knapp(498 + i, 181, -2, "south", navn, f)
plate(500, 12, 8, "Til toppen", "minecraft:blue_concrete", "blue")
tilbake(500, -12)
tick.append(f"execute if score #klokke pvp_t matches 0 unless entity @a[x=478,y=101,z=-22,dx=44,dy=78,dz=44,gamemode=!spectator] "
            f"run fill 478 101 -22 522 104 22 minecraft:air replace minecraft:water")
tick.append(f"execute if score #klokke pvp_t matches 0 run fill 478 101 -22 522 104 22 minecraft:air replace minecraft:hay_block")
tick.append(f"execute if score #klokke pvp_t matches 0 run fill 478 101 -22 522 104 22 minecraft:air replace minecraft:slime_block")
tick.append(f"execute if score #klokke pvp_t matches 0 run fill 478 101 -22 522 104 22 minecraft:air replace minecraft:cobweb")

# =========================================================================== PARKOUR (x=600)
plattform(596, -3, 602, 3)
tekst(599.5, Y + 6, 0.5, "PARKOUR", "green", 2.0)
import random
r = random.Random(600)
x, y, z = 602, Y, 0
HOPP = []
for n in range(26):
    x += r.choice([2, 3, 3, 4])
    y = max(Y - 2, min(Y + 14, y + r.choice([0, 0, 1, 1, -1])))
    z = max(-4, min(4, z + r.choice([-2, -1, 0, 1, 2])))
    HOPP.append((x, y, z))
SJEKK = {7, 14, 20}
for n, (hx, hy, hz) in enumerate(HOPP):
    blokk = "minecraft:gold_block" if n in SJEKK else (GLOD if n % 4 == 0 else POLERT)
    setb(hx, hy, hz, blokk)
mx, my, mz = HOPP[-1]
fill(mx + 2, my, mz - 2, mx + 6, my, mz + 2, POLERT)
tekst(mx + 4.5, my + 4, mz + 0.5, "MÅL!", "green", 2.0)
CP = [(599.5, 101, 0.5)] + [(HOPP[n][0] + 0.5, HOPP[n][1] + 1, HOPP[n][2] + 0.5) for n in sorted(SJEKK)]
for i, n in enumerate(sorted(SJEKK), start=1):
    hx, hy, hz = HOPP[n]
    tick.append(f"execute as @a[x={hx},y={hy + 1},z={hz},dx=0,dy=1,dz=0,scores={{pvp_cp=..{i - 1}}}] run function {NS}:parkour/cp{i}")
    filer[f"parkour/cp{i}"] = [f"scoreboard players set @s pvp_cp {i}", f'title @s actionbar {{text:"Sjekkpunkt {i}!",color:"gold"}}',
                               "playsound minecraft:block.note_block.pling player @s ~ ~ ~ 1 1.5"]
filer["parkour/tilbake"] = [f"execute if score @s pvp_cp matches {i} run tp @s {cx} {cy} {cz}" for i, (cx, cy, cz) in enumerate(CP)] + [
    "execute unless score @s pvp_cp matches 0.. run tp @s 599.5 101 0.5"]
tick.append(f"execute as @a[x={mx + 2},y={my + 1},z={mz - 2},dx=4,dy=2,dz=4,tag=!pvp_parkour_ferdig] run function {NS}:parkour/maal")
filer["parkour/maal"] = ["tag @s add pvp_parkour_ferdig",
                         'tellraw @a [{selector:"@s",color:"green"},{text:" klarte parkouren!",color:"gray"}]',
                         "playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1",
                         "summon minecraft:firework_rocket ~ ~1 ~ {LifeTime:20,FireworksItem:{id:\"minecraft:firework_rocket\",count:1,"
                         "components:{\"minecraft:fireworks\":{explosions:[{shape:\"star\",colors:[I;65280,16766720]}]}}}}"]
tick.append(f"tag @a[x=590,y=95,z=-8,dx=10,dy=10,dz=16] remove pvp_parkour_ferdig")
tick.append(f"scoreboard players set @a[x=596,y=101,z=-3,dx=6,dy=2,dz=6] pvp_cp 0")
tilbake(599, -2)

# =========================================================================== ALLE MOT ALLE (x=700)
plattform(678, -22, 722, 22)
for (x1, z1, x2, z2) in [(678, -22, 722, -22), (678, 22, 722, 22), (678, -22, 678, 22), (722, -22, 722, 22)]:
    fill(x1, Y + 1, z1, x2, Y + 3, z2, MUR)
for (x, z) in [(690, -10), (710, 10), (690, 10), (710, -10), (700, 0)]:
    fill(x - 1, Y + 1, z - 1, x + 1, Y + 4, z + 1, STEIN)
    setb(x, Y + 5, z, GLOD)
tekst(700.5, Y + 9, 0.5, "ALLE MOT ALLE", "dark_red", 2.0)
FFA = sone(679, Y + 1, -21, 721, Y + 10, 21)
tick.append(f"execute as {FFA}[tag=!pvp_ffa] run function {NS}:kit/sverd".replace("][", ","))
tick.append(f"tag {FFA} add pvp_ffa")
tick.append(f"tag @a[tag=pvp_ffa,x=679,y={Y + 1},z=-21,dx=42,dy=9,dz=42] add pvp_ffa_inne")
tick.append("tag @a[tag=pvp_ffa,tag=!pvp_ffa_inne] remove pvp_ffa")
tick.append("tag @a remove pvp_ffa_inne")
tilbake(700, 18)

# =========================================================================== fall i tomrommet
filer["fall"] = [
    f"execute if entity @s[x=380,y=0,z=-40,dx=90,dy=100,dz=80] run function {NS}:fall_bridge",
    f"execute if entity @s[x=590,y=0,z=-40,dx=120,dy=100,dz=80] run function {NS}:parkour/tilbake",
    f"execute unless entity @s[x=380,y=0,z=-40,dx=90,dy=100,dz=80] unless entity @s[x=590,y=0,z=-40,dx=120,dy=100,dz=80] "
    f"run scoreboard players set @s df_reise 3",
]
filer["fall_bridge"] = ["tag @s remove pvp_bridge", "tp @s 400.5 101 0.5 -90 0",
                        'title @s actionbar {text:"Du falt! Trykk Start for å prøve igjen.",color:"red"}']

# =========================================================================== funksjoner
OMRADE = [("-32", "-32", "360", "32"), ("361", "-32", "740", "32")]
FUNKSJONER = {
    "load": ["scoreboard objectives add pvp_t dummy", "scoreboard objectives add pvp_treff dummy {text:\"Treff\"}",
             "scoreboard objectives add pvp_tid dummy", "scoreboard objectives add pvp_sek dummy",
             "scoreboard objectives add pvp_cp dummy", "scoreboard players set #20 pvp_t 20"],
    "tick": ["scoreboard players add #klokke pvp_t 1",
             "execute if score #klokke pvp_t matches 100.. run scoreboard players set #klokke pvp_t 0",
             f"execute in {DIM} run function {NS}:tick_pvp"],
    "tick_pvp": tick + [f"execute as @a[distance=0..,y=-64,dy=124] run function {NS}:fall"],
    "bygg": [f"execute in {DIM} run forceload add {a} {b} {c} {d}" for a, b, c, d in OMRADE]
            + ['tellraw @a {text:"[PvP-øya] Laster og bygger øvingsverdenen...",color:"gray"}', f"function {NS}:bygg_vent"],
    "bygg_vent": [f"execute if function {NS}:lastet run function {NS}:bygg_kjor",
                  f"execute unless function {NS}:lastet run schedule function {NS}:bygg_vent 20t"],
    "lastet": ["execute in " + DIM + " " + " ".join(f"if loaded {x} 100 {z}" for x in range(-32, 741, 16) for z in (-32, 0, 32))
               + " run return 1", "return 0"],
    "bygg_kjor": [f"execute in {DIM} run function {NS}:bygg_utfor"],
    "bygg_utfor": ["kill @e[type=minecraft:text_display,tag=pvp_tekst]"] + bygg + [
        f"forceload remove {a} {b} {c} {d}" for a, b, c, d in OMRADE] + [
        'tellraw @a {text:"[PvP-øya] Ferdig bygget! Skriv /reise for å dra dit.",color:"light_purple"}'],
}


def main():
    if PACK.exists():
        shutil.rmtree(PACK)
    fdir = PACK / "data" / NS / "function"
    for navn, linjer in {**FUNKSJONER, **filer}.items():
        sti = fdir / f"{navn}.mcfunction"
        sti.parent.mkdir(parents=True, exist_ok=True)
        sti.write_text("\n".join(linjer) + "\n", encoding="utf-8")
    tags = PACK / "data" / "minecraft" / "tags" / "function"
    tags.mkdir(parents=True)
    (tags / "load.json").write_text(json.dumps({"values": [f"{NS}:load"]}))
    (tags / "tick.json").write_text(json.dumps({"values": [f"{NS}:tick"]}))
    (PACK / "pack.mcmeta").write_text(json.dumps({"pack": {"description": "PvP-øya – øvingsverden for Dødsfjellet (26.3)",
                                                          "min_format": 121, "max_format": 200}}, ensure_ascii=False), encoding="utf-8")
    shutil.make_archive(str(PACK), "zip", PACK)
    print(f"{len(FUNKSJONER) + len(filer)} funksjoner, bygg = {len(bygg)} kommandoer, tick = {len(tick)} linjer")


if __name__ == "__main__":
    main()
