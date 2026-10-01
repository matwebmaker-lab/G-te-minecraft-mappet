"""Genererer datapacken "Dødsfjellet" (Minecraft 1.21.1) – et gigantisk fangehull under fjellet
i verdenen Dodstrappa (seed 8675309), med feller, hemmelige ganger, gåter og en kodelås.

Kjør:  python generer_dodsfjellet.py   ->  dodsfjellet_1.21.1/  og  dodsfjellet_1.21.1.zip
Bygg i spillet (området må være lastet):  /function df:bygg

Koordinatene er absolutte og passer til verdenen der Dødstrappa-inngangen står på -892 128 452.

Ruta (hemmeligheter = [H], feller = [F]):
  Inngangshallen  [H] skjult knapp i taket åpner trapp ned
  Etasje 1 (gulv y=95)
    A Forhallen      -> vest: W Gullrommet [F knuse-tak, blindvei]
                     -> øst: Pilgangen [F trykkplater + Harming-piler]
    B Gåtehallen     [H] tre gåter, 14 spaker – tre riktige åpner nordveggen, [F] feil spak = giftgass
    C Lavasjøen      [F] gull-steiner forsvinner i lava
    D Knuseren       [F] trykkplate åpner luka ned – og taket begynner å synke
  Etasje 2 (gulv y=78)
    E Labyrinten     [F] usynlige fallgruver i blindveiene
    F Vannkammeret   [F] rommet fylles med vann, [H] knapp under vann åpner veien
    G Wardenens hule [F] går du uten å snike, kommer wardenen
    H Giftgangen     [F] giftskyer, falsk utgang med fallgruver, [H] sprukken vegg (hakke)
    I Nedgangen      [F] ambolt-regn
  Etasje 3 (gulv y=61)
    K Lavakløfta     [F] sprukne brosteiner raser, ildkuler fra veggene
    Kodelåsen        4 spaker (koden står på skilt underveis), feil kode = evoker-kjever
    V SKATTKAMMERET  voktet av Skattevokteren (boss) + vakter. Knapp tar deg tilbake til inngangen
  Inngangen lukker seg når alle spillerne er inne; når ingen er igjen nullstilles alt.
"""
import json
import random
import shutil
from pathlib import Path

ROT = Path(__file__).parent
PACK = ROT / "dodsfjellet_1.21.1"
NS = "df"
SPAWN = "-894 128 452 -90 0"
OMRADE = "-935 340 -830 456"

SKALL = "minecraft:deepslate_bricks"
GULV = "minecraft:polished_blackstone_bricks"
LYS = "minecraft:lantern[hanging=true]"

# --------------------------------------------------------------------------- bygging
skall, luft, detaljer = [], [], []


def box(a, b):
    (x1, y1, z1), (x2, y2, z2) = a, b
    return f"{min(x1,x2)} {min(y1,y2)} {min(z1,z2)} {max(x1,x2)} {max(y1,y2)} {max(z1,z2)}"


def fill(liste, a, b, blokk, modus=""):
    liste.append(f"fill {box(a, b)} {blokk}{' ' + modus if modus else ''}")


def setb(x, y, z, blokk):
    detaljer.append(f"setblock {x} {y} {z} {blokk}")


def rom(x1, z1, x2, z2, gulv, h=5, vegg=SKALL, gulvblokk=GULV, lys=True):
    """Innvendige mål x1..x2, z1..z2. Gulvblokk på y=gulv, luft gulv+1..gulv+h."""
    fill(skall, (x1 - 1, gulv - 1, z1 - 1), (x2 + 1, gulv + h + 1, z2 + 1), vegg)
    fill(luft, (x1, gulv + 1, z1), (x2, gulv + h, z2), "minecraft:air")
    fill(luft, (x1, gulv, z1), (x2, gulv, z2), gulvblokk)
    if lys:
        cx, cz = (x1 + x2) // 2, (z1 + z2) // 2
        for dx in (-4, 4):
            for dz in (-4, 4):
                setb(cx + dx, gulv + h, cz + dz, LYS)


def gang(x1, z1, x2, z2, gulv, h=3, lys=True):
    """Korridor med innvendige mål (tar også hull i veggene den overlapper)."""
    fill(skall, (x1 - 1, gulv - 1, z1 - 1), (x2 + 1, gulv + h + 1, z2 + 1), SKALL)
    fill(luft, (x1, gulv + 1, z1), (x2, gulv + h, z2), "minecraft:air")
    fill(luft, (x1, gulv, z1), (x2, gulv, z2), GULV)
    if lys:
        lang_x = abs(x2 - x1) >= abs(z2 - z1)
        cx, cz = (x1 + x2) // 2, (z1 + z2) // 2
        for t in range(min(x1, x2) + 2, max(x1, x2) - 1, 4) if lang_x else range(min(z1, z2) + 2, max(z1, z2) - 1, 4):
            setb(t, gulv + h, cz, LYS) if lang_x else setb(cx, gulv + h, t, LYS)


def hull(a, b):
    fill(luft, a, b, "minecraft:air")


SKILTFARGE = {"aqua": "cyan", "dark_aqua": "cyan", "gold": "orange", "dark_red": "red", "dark_green": "green",
              "light_purple": "magenta", "dark_purple": "purple", "blue": "light_blue", "dark_blue": "blue",
              "dark_gray": "gray", "green": "lime"}


def skilt(x, y, z, facing, *linjer, farge="white"):
    farge = SKILTFARGE.get(farge, farge)   # skilt godtar bare fargestoff-farger
    linjer = list(linjer) + [""] * (4 - len(linjer))
    msg = ",".join("'" + json.dumps(l, ensure_ascii=False) + "'" for l in linjer)
    setb(x, y, z, f"minecraft:dark_oak_wall_sign[facing={facing}]"
                  f"{{front_text:{{has_glowing_text:1b,color:\"{farge}\",messages:[{msg}]}}}}")


def stige(x, z, y1, y2, facing="south"):
    for y in range(y1, y2 + 1):
        setb(x, y, z, f"minecraft:ladder[facing={facing}]")


def kiste(facing, items):
    return f"minecraft:chest[facing={facing}]{{Items:[{','.join(items)}]}}"


def item(slot, id_, count=1, comp=None):
    c = f",components:{{{comp}}}" if comp else ""
    return f'{{Slot:{slot}b,id:"minecraft:{id_}",count:{count}{c}}}'


def navn(tekst, farge="gold"):
    return '"minecraft:custom_name":\'{"text":"' + tekst + '","color":"' + farge + '","italic":false}\''


PILER = "{Items:[" + ",".join(item(s, "tipped_arrow", 64, '"minecraft:potion_contents":{potion:"minecraft:strong_harming"}') for s in range(3)) + "]}"
ILD = "{Items:[" + ",".join(item(s, "fire_charge", 64) for s in range(3)) + "]}"
HAKKE = item(0, "iron_pickaxe", 1, navn("Hakke for svake vegger") +
             ',"minecraft:can_break":{predicates:[{blocks:"minecraft:cracked_deepslate_bricks"}]}')
A_KISTE = [HAKKE, item(1, "iron_pickaxe", 1, navn("Hakke for svake vegger") +
                       ',"minecraft:can_break":{predicates:[{blocks:"minecraft:cracked_deepslate_bricks"}]}'),
           item(4, "bread", 32), item(8, "cooked_beef", 16)]
SKATT = [
    item(0, "netherite_sword", 1, navn("Dødsfjellets sverd", "dark_red") + ',"minecraft:enchantments":{levels:{"minecraft:sharpness":5,"minecraft:unbreaking":3,"minecraft:fire_aspect":2}}'),
    item(1, "netherite_chestplate", 1, '"minecraft:enchantments":{levels:{"minecraft:protection":4,"minecraft:unbreaking":3}}'),
    item(2, "elytra", 1), item(3, "totem_of_undying", 2),
    item(4, "enchanted_golden_apple", 8), item(9, "diamond", 64), item(10, "diamond", 64),
    item(11, "netherite_ingot", 16), item(12, "emerald", 64), item(13, "experience_bottle", 64),
    item(22, "nether_star", 1, navn("Beviset: du overlevde", "light_purple")),
]


# --------------------------------------------------------------------------- feller og hemmeligheter
OFFER = "gamemode=!creative,gamemode=!spectator"


def sone(x1, y1, z1, x2, y2, z2, offer=True):
    x1, x2 = sorted((x1, x2)); y1, y2 = sorted((y1, y2)); z1, z2 = sorted((z1, z2))
    return f"@a[x={x1},y={y1},z={z1},dx={x2-x1},dy={y2-y1},dz={z2-z1}{',' + OFFER if offer else ''}]"


filer = {}      # funksjonsnavn -> linjer
tick = []       # linjer i tick
reparer = []    # linjer i reparer


def admin_logg(tekst, farge="yellow"):
    """En chat-linje som bare admins (i kontrollrommet) ser."""
    return ('tellraw @a[tag=df_admin] ["",{"text":"[Admin] ","color":"gold","bold":true},'
            f'{{"text":"{tekst}","color":"{farge}"}}]')


def felle(id_, trigger, varighet, start, hendelser=None, slutt=None, alltid=False, pre=None, navn_=None):
    """Tidsstyrt felle. hendelser: {tidsverdi-eller-område: [kommandoer]} (nedtelling)."""
    s = f"#{id_}"
    tick.extend(pre or [])
    tick.append(f"execute if score {s} df_t matches 1.. run function {NS}:f/{id_}/ned")
    aktiv = "" if alltid else "if score #aktiv df_t matches 1 "
    tick.append(f"execute {aktiv}unless score {s} df_t matches 1.. {trigger} run function {NS}:f/{id_}/start")
    logg = [admin_logg(f"Felle utløst: {navn_ or id_}", "red")] if not alltid else []
    filer[f"f/{id_}/start"] = start + logg + [f"scoreboard players set {s} df_t {varighet}"]
    ned = [f"scoreboard players remove {s} df_t 1"]
    for i, (t, cmds) in enumerate((hendelser or {}).items()):
        filer[f"f/{id_}/e{i}"] = cmds
        ned.append(f"execute if score {s} df_t matches {t} run function {NS}:f/{id_}/e{i}")
    if slutt:
        filer[f"f/{id_}/slutt"] = slutt
        ned.append(f"execute if score {s} df_t matches 0 run function {NS}:f/{id_}/slutt")
    filer[f"f/{id_}/ned"] = ned
    reparer.append(f"scoreboard players set {s} df_t 0")
    if slutt:
        reparer.append(f"function {NS}:f/{id_}/slutt")


def hemmelighet(id_, trigger, apne, lukk, navn_=None, lyd=True):
    s = f"#{id_}"
    tick.append(f"execute unless score {s} df_s matches 1 {trigger} run function {NS}:h/{id_}/apne")
    filer[f"h/{id_}/apne"] = apne + (["playsound minecraft:block.piston.extend block @a ~ ~ ~ 1 0.5"] if lyd else []) + [
        admin_logg(f"Løst: {navn_ or id_}", "green"),
        f"scoreboard players set {s} df_s 1"]
    filer[f"h/{id_}/lukk"] = lukk + [f"scoreboard players set {s} df_s 0"]
    reparer.append(f"function {NS}:h/{id_}/lukk")


def kollaps(id_, omrade, materiale, erstatning, posisjoner, gjenoppbygg=100, lyd="minecraft:block.stone.break"):
    """Blokker av `materiale` forsvinner når en spiller står på dem."""
    s = f"#{id_}"
    tick.append(f"execute if score #aktiv df_t matches 1 as {omrade} at @s if block ~ ~-1 ~ {materiale} "
                f"run function {NS}:k/{id_}/knus")
    tick.append(f"execute if score {s} df_t matches 1.. run function {NS}:k/{id_}/ned")
    filer[f"k/{id_}/knus"] = [f"setblock ~ ~-1 ~ {erstatning}", f"playsound {lyd} block @a ~ ~ ~ 1.5 0.6",
                              f"scoreboard players set {s} df_t {gjenoppbygg}"]
    filer[f"k/{id_}/ned"] = [f"scoreboard players remove {s} df_t 1",
                             f"execute if score {s} df_t matches 0 run function {NS}:k/{id_}/bygg"]
    filer[f"k/{id_}/bygg"] = [f"execute unless block {x} {y} {z} {materiale} run setblock {x} {y} {z} {materiale}"
                              for x, y, z in posisjoner]
    reparer.append(f"function {NS}:k/{id_}/bygg")


romnavn = []
ROM = []   # (etasje, navn, koordinater) – brukes av kontrollpanelet i admin-rommet


def romnavn_sone(tekst, *koord, farge="gold", etasje=None):
    romnavn.append(f'title {sone(*koord, offer=False)} actionbar {{"text":"{tekst}","color":"{farge}"}}')
    if etasje is None:
        y = koord[1]
        etasje = 1 if y >= 94 else 2 if y >= 77 else 3 if y >= 60 else 4 if y >= 43 else 5
    ROM.append((etasje, tekst, koord))


def belonning(item_id, sone_, tekst):
    """Gir en Dødsfjellet-gjenstand til alle spillerne i rommet."""
    return [f"give {sone_} dodsfjellet:{item_id}",
            f'title {sone_} subtitle {{"text":"Du fikk: {tekst}!","color":"aqua"}}',
            "playsound minecraft:ui.toast.challenge_complete master @a ~ ~ ~ 1 1.2",
            admin_logg(f"Belønning delt ut: {tekst}", "aqua")]


# =========================================================================== INNGANGEN
# Den gamle hallen: innv. x -891..-888, y 128..131, z 451..453, nordvegg z=450.
setb(-891, 130, 451, "minecraft:polished_blackstone_button[face=wall,facing=south]")
skilt(-889, 129, 453, "north", "Den ekte veien", "er skjult.", "", "Se opp...", farge="light_gray")
hemmelighet("s_inngang", "unless score #lukket df_s matches 1 "
                         "if block -891 130 451 minecraft:polished_blackstone_button[powered=true]",
            ["fill -890 128 450 -890 129 450 minecraft:air",
             'title @a[x=-892,y=126,z=449,dx=5,dy=6,dz=6] title {"text":"Noe klikket i veggen...","color":"gray"}'],
            [f"fill -890 128 450 -890 129 450 {SKALL}"])

# Når ALLE spillerne (ikke creative/spectator) er inne i fangehullet, lukker inngangen seg bak dem.
# Den som dør havner ute. Når ingen er igjen inne, nullstilles hele fangehullet til neste runde.
# "Inne" = innsiden av trappetunnelen (nøyaktige bokser, så spillere ute på fjellet ikke teller)
# + hele det underjordiske fangehullet (y 20..101, under fjelloverflaten som her ligger på y >= 102).
INNE_BOKSER = ["@a[x=-891,y=128,z=447,dx=2,dy=3,dz=2]"] + [
    f"@a[x=-891,y={127 - k},z={446 - k},dx=2,dy=3,dz=0]" for k in range(31)
] + ["@a[x=-935,y=20,z=340,dx=105,dy=81,dz=109]"]
tick += [
    "tag @a remove df_inne",
] + [f"tag {b} add df_inne" for b in INNE_BOKSER] + [
    # Deltakere = spillere (ikke creative/spectator) som har vært inne i fjellet denne runden.
    f"tag @a[tag=df_inne,{OFFER}] add df_deltaker",
    # Dør en deltaker, starter HELE mapet på nytt for alle.
    "scoreboard players reset @a[tag=!df_deltaker] df_dod",
    f"execute if entity @a[tag=df_deltaker,scores={{df_dod=1..}}] run function {NS}:restart",
    f"execute if score #s_inngang df_s matches 1 unless score #lukket df_s matches 1 "
    f"if entity @a[tag=df_inne,{OFFER}] unless entity @a[tag=!df_inne,{OFFER}] run function {NS}:inngang/lukk",
    f"execute if score #lukket df_s matches 1 unless entity @a[tag=df_inne,{OFFER}] run function {NS}:inngang/runde_slutt",
]
filer["inngang/lukk"] = [
    f"fill -890 128 450 -890 129 450 {SKALL}",
    "scoreboard players set #lukket df_s 1",
    "playsound minecraft:block.piston.contract block @a -890 128 449 3 0.4",
    "playsound minecraft:entity.warden.sonic_boom hostile @a[tag=df_inne] ~ ~ ~ 0.6 0.5",
    'title @a[tag=df_inne] title {"text":"Inngangen lukket seg...","color":"dark_red","bold":true}',
    'title @a[tag=df_inne] subtitle {"text":"Den eneste veien ut går gjennom skatten","color":"gray"}',
    'tellraw @a[tag=!df_inne] {"text":"[Dødsfjellet] Fjellet har lukket seg rundt de modige...","color":"dark_red"}',
]
filer["inngang/lukk"].append(admin_logg("Inngangen lukket seg – runden har startet", "gold"))
filer["inngang/runde_slutt"] = [
    "scoreboard players set #lukket df_s 0",
    "tag @a remove df_deltaker",
    'tellraw @a {"text":"[Dødsfjellet] Ingen er igjen der inne. Fjellet nullstiller seg til neste runde...","color":"gray"}',
    f"function {NS}:reparer",
]


def restart(aarsak):
    return [
        aarsak,
        'title @a[tag=df_deltaker] title {"text":"DØD","color":"dark_red","bold":true}',
        'title @a[tag=df_deltaker] subtitle {"text":"Hele fjellet starter på nytt","color":"gray"}',
        "playsound minecraft:entity.wither.death master @a[tag=df_deltaker] ~ ~ ~ 0.7 0.6",
        "clear @a[tag=df_deltaker]",
        "effect clear @a[tag=df_deltaker]",
        "effect give @a[tag=df_deltaker] minecraft:instant_health 1 10 true",
        f"tp @a[tag=df_deltaker] {SPAWN}",
        "scoreboard players reset @a df_dod",
        "tag @a remove df_deltaker",
        "scoreboard players set #lukket df_s 0",
        f"function {NS}:reparer",
    ]


filer["restart"] = restart(
    'tellraw @a ["",{"text":"[Dødsfjellet] ","color":"dark_red","bold":true},'
    '{"selector":"@a[tag=df_deltaker,scores={df_dod=1..}]","color":"red"},'
    '{"text":" døde! Alle sendes tilbake til start, og fjellet nullstilles...","color":"gray"}]')
filer["restart_admin"] = restart(
    'tellraw @a ["",{"text":"[Dødsfjellet] ","color":"dark_red","bold":true},'
    '{"text":"En admin startet fjellet på nytt.","color":"gray"}]')
reparer.append("scoreboard players set #lukket df_s 0")

# Trapp ned: repos z 447..449 (gulv 127), trinn k: z=446-k, trappeblokk y=126-k
for z in range(447, 450):
    fill(skall, (-892, 126, z), (-888, 132, z), SKALL)
    fill(luft, (-891, 128, z), (-889, 131, z), "minecraft:air")
    fill(luft, (-891, 127, z), (-889, 127, z), GULV)
for k in range(31):
    z, y = 446 - k, 126 - k
    fill(skall, (-892, y - 1, z), (-888, y + 5, z), SKALL)
    fill(luft, (-891, y + 1, z), (-889, y + 4, z), "minecraft:air")
    detaljer.append(f"fill -891 {y} {z} -889 {y} {z} minecraft:polished_blackstone_brick_stairs[facing=south]")
    if k % 5 == 2:
        setb(-890, y + 4, z, "minecraft:soul_lantern[hanging=true]")
fill(skall, (-892, 94, 415), (-888, 100, 415), SKALL)
fill(luft, (-891, 96, 415), (-889, 99, 415), "minecraft:air")
fill(luft, (-891, 95, 415), (-889, 95, 415), GULV)
hull((-891, 96, 414), (-889, 98, 414))

# =========================================================================== ETASJE 1 (gulv 95)
G1 = 95
# A Forhallen
rom(-896, 401, -884, 413, G1)
romnavn_sone("Forhallen", -896, 96, 401, -884, 100, 413)
skilt(-890, 97, 401, "south", "DØDSFJELLET", "Skatten ligger", "dypt der nede.", "Lykke til...", farge="red")
skilt(-893, 97, 401, "south", "Kode 1:", "PÅ", farge="aqua")
skilt(-884, 97, 405, "west", "Pilgangen →", "Tråkk ALDRI", "på platene!", farge="yellow")
skilt(-896, 97, 405, "east", "← Skattkammeret", "(helt sant)", farge="gold")
setb(-887, 96, 401, kiste("south", A_KISTE))
skilt(-887, 97, 401, "south", "Utstyr", "Du får bruk", "for hakka...", farge="gray")

# W Gullrommet (blindvei med knuse-tak)
gang(-908, 406, -897, 408, G1)
rom(-921, 401, -909, 413, G1)
romnavn_sone("Gullrommet", -921, 96, 401, -909, 100, 413, farge="yellow")
for (x, z) in [(-919, 403), (-919, 411), (-913, 403), (-913, 411), (-916, 407)]:
    fill(detaljer, (x - 1, 96, z - 1), (x + 1, 96, z + 1), "minecraft:gold_block")
setb(-916, 97, 407, "minecraft:gold_block")
setb(-920, 96, 407, kiste("east", [item(13, "gold_nugget", 1, navn("Grådighet", "yellow"))]))
felle("gull", f"if entity {sone(-921, 96, 401, -913, 97, 413)}", 220,
      ["fill -908 96 406 -908 98 408 minecraft:iron_bars replace minecraft:air",
       "playsound minecraft:block.iron_door.close block @a -915 97 407 2 0.5",
       f'title {sone(-921, 96, 401, -909, 100, 413)} title {{"text":"Grådig?","color":"gold","bold":true}}',
       f'title {sone(-921, 96, 401, -909, 100, 413)} subtitle {{"text":"Taket kommer...","color":"gray"}}'],
      {200 - 15 * i: [f"fill -921 {100 - i} 401 -909 {100 - i} 413 minecraft:polished_blackstone replace minecraft:air",
                      "playsound minecraft:block.piston.contract block @a -915 97 407 2 0.5"] for i in range(5)},
      ["fill -921 96 401 -909 100 413 minecraft:air replace minecraft:polished_blackstone",
       "fill -908 96 406 -908 98 408 minecraft:air replace minecraft:iron_bars"])

# Pilgangen (A -> B)
gang(-883, 406, -872, 408, G1)
romnavn_sone("Pilgangen", -882, 96, 406, -873, 98, 408, farge="red")
sti = {(-882, 407), (-881, 407), (-880, 407), (-880, 406), (-879, 406), (-878, 406), (-878, 407),
       (-878, 408), (-877, 408), (-876, 408), (-876, 407), (-875, 407), (-874, 407), (-873, 407)}
for x in range(-881, -873):
    for z in range(406, 409):
        if (x, z) not in sti:
            setb(x, 96, z, "minecraft:stone_pressure_plate")
PIL_X = (-880, -877, -874)
for x in PIL_X:
    setb(x, 97, 405, f"minecraft:dispenser[facing=south]{PILER}")
    setb(x, 97, 409, f"minecraft:dispenser[facing=north]{PILER}")
    setb(x, 97, 404, SKALL)
    setb(x, 97, 410, SKALL)
felle("piler", "if score #plate df_t matches 1", 10,
      [f"setblock {x} 97 {z} minecraft:redstone_block" for x in PIL_X for z in (404, 410)]
      + ["playsound minecraft:entity.skeleton.shoot hostile @a -877 97 407 2 0.6"],
      {8: [f"setblock {x} 97 {z} {SKALL}" for x in PIL_X for z in (404, 410)]},
      pre=["scoreboard players set #plate df_t 0",
           f"execute as {sone(-882, 96, 406, -873, 97, 408)} at @s if block ~ ~ ~ minecraft:stone_pressure_plate "
           "run scoreboard players set #plate df_t 1"])
reparer += [f"data merge block {x} 97 {z} {PILER}" for x in PIL_X for z in (405, 409)]

# B Gåtehallen – tre gåter på tre vegger, 14 spaker. Alle tre riktige må stå på.
rom(-871, 401, -859, 413, G1)
romnavn_sone("Gåtehallen", -871, 96, 401, -859, 100, 413)
# (x, z, retning spaken peker, ord, riktig?)
GATE_SPAKER = (
    [(-859, z, "west", o, o == "Kam") for z, o in zip((403, 405, 407, 409, 411), ("Hai", "Kam", "Ulv", "Hund", "Slange"))] +
    [(x, 413, "north", o, o == "Fotspor") for x, o in zip((-869, -867, -865, -863, -861), ("Penger", "Fotspor", "Tid", "Mat", "Steiner"))] +
    [(-871, z, "east", o, o == "Ekko") for z, o in zip((402, 404, 410, 412), ("Spøkelse", "Ekko", "Vind", "Radio"))]
)
for x, z, f, ord_, _ in GATE_SPAKER:
    setb(x, 97, z, f"minecraft:lever[face=wall,facing={f},powered=false]")
    skilt(x, 98, z, f, "", ord_, farge="yellow")
skilt(-859, 99, 407, "west", "Gåte 1:", "Jeg har tenner,", "men biter", "aldri.", farge="aqua")
skilt(-865, 99, 413, "north", "Gåte 2:", "Jo mer du tar,", "jo mer lar du", "bli igjen.", farge="aqua")
skilt(-871, 99, 407, "east", "Gåte 3:", "Jeg snakker", "uten munn og", "hører uten ører", farge="aqua")
skilt(-869, 97, 401, "south", "GÅTEHALLEN", "Tre gåter.", "Tre riktige spaker", "åpner veien.", farge="gold")
skilt(-861, 97, 401, "south", "Én feil spak", "= giftgass,", "og alt starter", "på nytt.", farge="red")
NULLSTILL_GATE = [f"setblock {x} 97 {z} minecraft:lever[face=wall,facing={f},powered=false]" for x, z, f, _, _ in GATE_SPAKER]
filer["b/feil"] = [f"execute if block {x} 97 {z} minecraft:lever[powered=true] run scoreboard players set #feilspak df_t 1"
                   for x, z, _, _, ok in GATE_SPAKER if not ok]
felle("spak_feil", "if score #feilspak df_t matches 1", 40,
      [f"execute as {sone(-871, 96, 401, -859, 100, 413)} at @s run summon minecraft:area_effect_cloud ~ ~ ~ "
       '{Radius:3f,Duration:60,WaitTime:5,RadiusPerTick:0f,potion_contents:{potion:"minecraft:strong_harming"}}',
       "playsound minecraft:entity.creeper.primed hostile @a -865 97 407 2 0.5",
       f'title {sone(-871, 96, 401, -859, 100, 413, offer=False)} title {{"text":"FEIL SPAK","color":"dark_green","bold":true}}',
       f'title {sone(-871, 96, 401, -859, 100, 413, offer=False)} subtitle {{"text":"Alle spakene nullstilles...","color":"gray"}}'],
      {30: NULLSTILL_GATE},
      pre=["scoreboard players set #feilspak df_t 0", f"function {NS}:b/feil"])
# Hver gåte gir sin egen belønning (én gang per runde), selv om døra først åpner når alle tre er riktige.
B_SONE = sone(-871, 96, 401, -859, 100, 413)
for nr, (ord_, item_id, tekst) in enumerate([("Kam", "skyggedolk", "Skyggedolken"),
                                             ("Fotspor", "fjellvokter_hjelm", "Fjellvokter-hjelm"),
                                             ("Ekko", "fjellvokter_brynje", "Fjellvokter-brynje")], start=1):
    x, z, *_ = next(s for s in GATE_SPAKER if s[3] == ord_)
    hemmelighet(f"g{nr}", f"if block {x} 97 {z} minecraft:lever[powered=true]",
                [f'title {B_SONE} title {{"text":"Gåte {nr} løst!","color":"green"}}'] + belonning(item_id, B_SONE, tekst),
                [], navn_=f"Gåte {nr} ({ord_})", lyd=False)
alle_riktige = " ".join(f"if block {x} 97 {z} minecraft:lever[powered=true]" for x, z, _, _, ok in GATE_SPAKER if ok)
hemmelighet("s_spak", f"unless score #spak_feil df_t matches 1.. {alle_riktige}",
            ["fill -866 96 400 -864 98 400 minecraft:air",
             "playsound minecraft:ui.toast.challenge_complete master @a -865 97 407 1.5 1.2",
             f'title {sone(-871, 96, 401, -859, 100, 413, offer=False)} title {{"text":"Alle tre gåtene løst!","color":"green"}}',
             f'title {sone(-871, 96, 401, -859, 100, 413, offer=False)} subtitle {{"text":"Nordveggen åpnet seg...","color":"gray"}}'],
            [f"fill -866 96 400 -864 98 400 {SKALL}"] + NULLSTILL_GATE)

# B -> C (gangen bak den hemmelige døra)
gang(-866, 389, -864, 399, G1)
# C Lavasjøen
rom(-871, 376, -859, 388, G1)
romnavn_sone("Lavasjøen", -871, 96, 376, -859, 100, 388, farge="red")
fill(detaljer, (-871, 95, 378), (-859, 95, 386), "minecraft:lava")
EKTE = {385: -863, 383: -865, 381: -867, 379: -865}
FALSKE = []
for z, ekte_x in EKTE.items():
    for x in (-867, -865, -863):
        if x == ekte_x:
            setb(x, 95, z, "minecraft:polished_blackstone")
        else:
            setb(x, 95, z, "minecraft:gilded_blackstone")
            FALSKE.append((x, 95, z))
skilt(-868, 97, 388, "north", "Gull frister", "de grådige.", "Hold deg til", "det mørke.", farge="yellow")
skilt(-860, 97, 376, "south", "Kode 2:", "AV", farge="aqua")
kollaps("steiner", sone(-871, 95, 377, -859, 99, 387), "minecraft:gilded_blackstone", "minecraft:lava", FALSKE,
        lyd="minecraft:block.lava.extinguish")

# C -> D
gang(-866, 364, -864, 375, G1)
# D Knuseren
rom(-871, 351, -859, 363, G1)
romnavn_sone("Knuseren", -871, 96, 351, -859, 100, 363, farge="red")
setb(-865, 96, 357, "minecraft:stone_pressure_plate")
skilt(-869, 97, 363, "north", "Platen åpner", "luka i hjørnet.", "Så kommer taket.", "LØP!", farge="red")
felle("knuser", "if block -865 96 357 minecraft:stone_pressure_plate[powered=true]", 300,
      ["setblock -869 95 351 minecraft:ladder[facing=south]",
       "playsound minecraft:block.iron_trapdoor.open block @a -869 96 351 2 0.5",
       f'title {sone(-871, 96, 351, -859, 100, 363)} title {{"text":"LØP!","color":"red","bold":true}}'],
      {300 - 20 - 12 * i: [f"fill -871 {100 - i} 351 -859 {100 - i} 363 minecraft:polished_blackstone replace minecraft:air",
                           "playsound minecraft:block.piston.contract block @a -865 98 357 2 0.5"] for i in range(5)},
      ["fill -871 96 351 -859 100 363 minecraft:air replace minecraft:polished_blackstone",
       f"setblock -869 95 351 {GULV}"])

# Stigesjakt D -> E  (x=-869, z=351, festet til veggen på z=350)
fill(skall, (-870, 84, 350), (-868, 95, 352), SKALL)
hull((-869, 79, 351), (-869, 94, 351))

# =========================================================================== ETASJE 2 (gulv 78)
G2 = 78
# E Labyrinten (13x13, celler på partalls-koordinater)
rom(-871, 351, -859, 363, G2, vegg=SKALL, gulvblokk="minecraft:stone_bricks", lys=False)
romnavn_sone("Labyrinten", -871, 79, 351, -859, 83, 363, farge="dark_green")
fill(detaljer, (-871, 79, 351), (-859, 83, 363), "minecraft:mossy_stone_bricks")
rng = random.Random(7)
besokt, kanter = {(1, 0)}, {}
stakk = [(1, 0)]
while stakk:
    c = stakk[-1]
    nab = [(c[0] + dx, c[1] + dz) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))
           if 0 <= c[0] + dx <= 6 and 0 <= c[1] + dz <= 6 and (c[0] + dx, c[1] + dz) not in besokt]
    if nab:
        n = rng.choice(nab)
        besokt.add(n); kanter.setdefault(c, []).append(n); kanter.setdefault(n, []).append(c)
        stakk.append(n)
    else:
        stakk.pop()
for (i, j), ns in kanter.items():
    fill(detaljer, (-871 + 2 * i, 79, 351 + 2 * j), (-871 + 2 * i, 83, 351 + 2 * j), "minecraft:air")
    for (a, b) in ns:
        fill(detaljer, (-871 + i + a, 79, 351 + j + b), (-871 + i + a, 83, 351 + j + b), "minecraft:air")
# finn løsningen (start (1,0) -> utgang (0,6)) og blindveier
forrige, ko = {(1, 0): None}, [(1, 0)]
while ko:
    c = ko.pop(0)
    for n in kanter[c]:
        if n not in forrige:
            forrige[n] = c; ko.append(n)
losning, c = set(), (0, 6)
while c:
    losning.add(c); c = forrige[c]
blindveier = [c for c, ns in kanter.items() if len(ns) == 1 and c not in losning]
rng.shuffle(blindveier)
GROPER = []
for (i, j) in blindveier[:6]:
    x, z = -871 + 2 * i, 351 + 2 * j
    GROPER.append((x, 78, z))
    fill(skall, (x - 1, 72, z - 1), (x + 1, 77, z + 1), SKALL)
    detaljer.append(f"fill {x} 74 {z} {x} 77 {z} minecraft:air")
    detaljer.append(f"setblock {x} 73 {z} minecraft:lava")
    setb(x, 78, z, "minecraft:infested_stone_bricks")   # ser helt lik ut som gulvet ...
for n, (i, j) in enumerate(sorted(kanter)):
    if n % 5 == 0:
        setb(-871 + 2 * i, 83, 351 + 2 * j, "minecraft:soul_lantern[hanging=true]")
kollaps("groper", sone(-871, 78, 351, -859, 83, 363), "minecraft:infested_stone_bricks", "minecraft:air", GROPER,
        gjenoppbygg=80)
stige(-869, 351, 79, 94)
hull((-872, 79, 363), (-872, 81, 363))       # utgang vest

# E -> F
gang(-882, 361, -873, 363, G2)
hull((-883, 79, 361), (-883, 81, 363))
skilt(-874, 80, 361, "south", "Kode 3:", "AV", farge="aqua")

# F Vannkammeret
rom(-896, 351, -884, 363, G2, vegg="minecraft:prismarine_bricks", gulvblokk="minecraft:dark_prismarine")
romnavn_sone("Vannkammeret", -896, 79, 351, -884, 83, 363, farge="aqua")
setb(-896, 80, 357, "minecraft:stone_button[face=wall,facing=east]")
setb(-897, 82, 357, "minecraft:sea_lantern")
skilt(-884, 80, 353, "west", "Pust dypt...", farge="aqua")
felle("vann", f"unless score #s_vann df_s matches 1 if entity {sone(-893, 79, 351, -884, 83, 363)}", 700,
      ["fill -883 79 361 -883 81 363 minecraft:glass replace minecraft:air",
       "playsound minecraft:block.iron_door.close block @a -890 80 357 2 0.5",
       f'title {sone(-896, 79, 351, -884, 83, 363)} title {{"text":"Pust dypt...","color":"aqua"}}'],
      {660: ["fill -896 79 351 -884 83 363 minecraft:water replace minecraft:air",
             "playsound minecraft:ambient.underwater.enter block @a -890 80 357 2 0.5"]},
      ["fill -896 79 351 -884 83 363 minecraft:air replace minecraft:water",
       "fill -883 79 361 -883 81 363 minecraft:air replace minecraft:glass"])
hemmelighet("s_vann", "if block -896 80 357 minecraft:stone_button[powered=true]",
            ["fill -896 79 351 -884 83 363 minecraft:air replace minecraft:water",
             "fill -883 79 361 -883 81 363 minecraft:air replace minecraft:glass",
             "scoreboard players set #vann df_t 0",
             "fill -897 79 356 -897 81 358 minecraft:air"],
            ["fill -897 79 356 -897 81 358 minecraft:prismarine_bricks",
             "setblock -897 82 357 minecraft:sea_lantern"])

# F -> G
gang(-908, 356, -898, 358, G2)
# G Wardenens hule
rom(-921, 351, -909, 363, G2, gulvblokk="minecraft:sculk", lys=False)
romnavn_sone("Wardenens hule", -921, 79, 351, -909, 83, 363, farge="dark_aqua")
for (x, z) in [(-918, 354), (-912, 354), (-918, 360), (-912, 360)]:
    setb(x, 83, z, "minecraft:soul_lantern[hanging=true]")
for (x, z) in [(-917, 353), (-913, 357), (-919, 361), (-911, 362), (-915, 355), (-910, 352)]:
    setb(x, 79, z, "minecraft:sculk_vein[down=true]")
skilt(-909, 80, 355, "west", "Ssssh...", "Den som sover", "skal ikke vekkes.", "SNIK deg gjennom!", farge="dark_aqua")
G_SONE = sone(-921, 79, 351, -909, 83, 363)
tick += [
    f"execute if score #aktiv df_t matches 1 unless score #warden df_t matches 1.. if entity @a[x=-921,y=79,z=351,dx=12,dy=4,dz=12,{OFFER},predicate=!{NS}:sniker] run scoreboard players add #sint df_t 1",
    f"execute unless entity {G_SONE} run scoreboard players set #sint df_t 0",
    f'execute if score #sint df_t matches 1 run title {G_SONE} title {{"text":"SSSSH!","color":"dark_aqua","bold":true}}',
    f"execute if score #sint df_t matches 1 run playsound minecraft:entity.warden.heartbeat hostile @a -915 80 357 2 1",
]
felle("warden", "if score #sint df_t matches 40..", 600,
      ["summon minecraft:warden -915 79 357 {Tags:[\"df_w\"],PersistenceRequired:1b}",
       "playsound minecraft:entity.warden.emerge hostile @a -915 80 357 3 1",
       "scoreboard players set #sint df_t 0"],
      slutt=["kill @e[type=minecraft:warden,tag=df_w]"])

# G -> H
gang(-916, 364, -914, 375, G2)
# H Giftgangen
rom(-921, 376, -909, 388, G2)
romnavn_sone("Giftgangen", -921, 79, 376, -909, 83, 388, farge="dark_green")
H_SONE = sone(-921, 79, 376, -909, 83, 388)
felle("gass", f"if entity {H_SONE}", 80,
      [f"execute as {H_SONE} at @s run summon minecraft:area_effect_cloud ~ ~ ~ "
       '{Radius:2.5f,Duration:120,WaitTime:25,RadiusPerTick:0f,potion_contents:{potion:"minecraft:harming"}}',
       "playsound minecraft:block.fire.extinguish hostile @a -915 80 382 1.5 0.5"])
skilt(-919, 80, 376, "south", "Utgangen er", "rett frem ←", farge="yellow")
skilt(-909, 80, 379, "west", "Noen vegger er", "svakere enn", "andre...", farge="gray")
skilt(-909, 80, 386, "west", "Kode 4:", "PÅ", farge="aqua")
# Falsk utgang vest (fallgruver over lava)
gang(-932, 381, -922, 383, G2)
FALSK = [(x, 78, z) for x in range(-930, -923) for z in range(381, 384)]
fill(skall, (-931, 72, 380), (-923, 77, 384), SKALL)
fill(detaljer, (-930, 74, 381), (-924, 77, 383), "minecraft:air")
fill(detaljer, (-930, 73, 381), (-924, 73, 383), "minecraft:lava")
fill(detaljer, (-930, 78, 381), (-924, 78, 383), "minecraft:infested_stone_bricks")
kollaps("falskgang", sone(-932, 78, 381, -922, 82, 383), "minecraft:infested_stone_bricks", "minecraft:air", FALSK,
        gjenoppbygg=80)
# Den ekte veien: sprukken vegg (1x2) i østveggen
fill(detaljer, (-908, 79, 382), (-908, 80, 382), "minecraft:cracked_deepslate_bricks")
gang(-907, 381, -897, 383, G2)
reparer.append("fill -908 79 382 -908 80 382 minecraft:cracked_deepslate_bricks")

# I Nedgangen
rom(-896, 376, -884, 388, G2)
romnavn_sone("Nedgangen", -896, 79, 376, -884, 83, 388)
skilt(-890, 80, 388, "north", "Ingen vei", "tilbake nå...", farge="gray")
I_SONE = sone(-893, 79, 376, -886, 83, 388)
felle("ambolt", f"if entity {I_SONE}", 120,
      [f"execute as {I_SONE} at @s run summon minecraft:falling_block ~ 83 ~ "
       '{BlockState:{Name:"minecraft:anvil"},Time:1,DropItem:0b,HurtEntities:1b,FallHurtAmount:10f,FallHurtMax:40}',
       f"execute as {I_SONE} at @s run summon minecraft:falling_block ~1 83 ~ "
       '{BlockState:{Name:"minecraft:anvil"},Time:1,DropItem:0b,HurtEntities:1b,FallHurtAmount:10f,FallHurtMax:40}',
       f"execute as {I_SONE} at @s run summon minecraft:falling_block ~ 83 ~-1 "
       '{BlockState:{Name:"minecraft:anvil"},Time:1,DropItem:0b,HurtEntities:1b,FallHurtAmount:10f,FallHurtMax:40}',
       "playsound minecraft:block.anvil.land block @a -890 82 382 2 0.5"],
      {"60": ["fill -896 79 376 -884 83 388 minecraft:air replace #minecraft:anvil"]},
      ["fill -896 79 376 -884 83 388 minecraft:air replace #minecraft:anvil"])
# Stigesjakt I -> K  (x=-895, z=376)
fill(skall, (-896, 68, 375), (-894, 77, 377), SKALL)
hull((-895, 62, 376), (-895, 77, 376))

# =========================================================================== ETASJE 3 (gulv 61)
# K Lavakløfta
fill(skall, (-897, 51, 375), (-858, 68, 389), SKALL)
fill(luft, (-896, 53, 376), (-859, 67, 388), "minecraft:air")
fill(luft, (-896, 52, 376), (-859, 52, 388), "minecraft:lava")
fill(detaljer, (-896, 52, 376), (-893, 61, 388), GULV)
fill(detaljer, (-862, 52, 376), (-859, 61, 388), GULV)
fill(detaljer, (-892, 61, 382), (-863, 61, 382), "minecraft:stone_bricks")
SPRUKNE = [(x, 61, 382) for x in (-887, -879, -871)]
for x, y, z in SPRUKNE:
    setb(x, y, z, "minecraft:cracked_stone_bricks")
stige(-895, 376, 62, 78)
romnavn_sone("Lavakløfta", -896, 62, 376, -859, 67, 388, farge="red")
for (x, z) in [(-894, 378), (-894, 386), (-861, 378), (-861, 386)]:
    setb(x, 67, z, LYS)
skilt(-894, 63, 376, "south", "Sprukne steiner", "bærer ingen.", farge="yellow")
kollaps("bro", sone(-892, 61, 382, -863, 65, 382), "minecraft:cracked_stone_bricks", "minecraft:air", SPRUKNE,
        gjenoppbygg=100)
ILD_X = (-888, -880, -872)
for x in ILD_X:
    setb(x, 63, 375, f"minecraft:dispenser[facing=south]{ILD}")
    setb(x, 63, 389, f"minecraft:dispenser[facing=north]{ILD}")
    setb(x, 63, 374, SKALL)
    setb(x, 63, 390, SKALL)
felle("ild", f"if entity {sone(-892, 62, 381, -863, 64, 383)}", 40,
      [f"setblock {x} 63 374 minecraft:redstone_block" for x in ILD_X] +
      ["playsound minecraft:entity.blaze.shoot hostile @a -877 63 382 2 0.8"],
      {38: [f"setblock {x} 63 374 {SKALL}" for x in ILD_X],
       20: [f"setblock {x} 63 390 minecraft:redstone_block" for x in ILD_X] +
           ["playsound minecraft:entity.blaze.shoot hostile @a -877 63 382 2 0.8"],
       18: [f"setblock {x} 63 390 {SKALL}" for x in ILD_X]})
reparer += [f"data merge block {x} 63 {z} {ILD}" for x in ILD_X for z in (375, 389)]

# Vaktgangen (K -> Arenaen)
gang(-858, 381, -848, 383, 61)
hull((-847, 62, 381), (-847, 64, 383))
romnavn_sone("Vaktgangen", -857, 62, 381, -848, 64, 383, farge="red")


# --- Vaktene (Dødsfjellet-modden): ser ut og oppfører seg som spillere
def vakt(x, y, z, tags=(), extra=""):
    t = ",".join(f'"{s}"' for s in ("df_vakt", *tags))
    return f"summon dodsfjellet:vakt {x} {y} {z} {{Tags:[{t}],PersistenceRequired:1b{extra}}}"


# ARENAEN (det gamle skattkammeret i etasje 3): porten stenges bak deg, beseir vaktene for å komme videre
rom(-846, 376, -834, 388, 61, h=8, vegg="minecraft:polished_blackstone_bricks", gulvblokk="minecraft:smooth_stone", lys=False)
romnavn_sone("Arenaen", -846, 62, 376, -834, 69, 388, farge="red")
for (x, z) in [(-842, 379), (-838, 385), (-842, 385), (-838, 379)]:
    fill(detaljer, (x, 62, z), (x, 69, z), "minecraft:polished_basalt[axis=y]")
for (x, z) in [(-844, 378), (-844, 386), (-836, 378), (-836, 386), (-840, 382)]:
    setb(x, 69, z, LYS)
skilt(-846, 63, 378, "east", "ARENAEN", "Beseir alle", "vaktene for å", "komme videre.", farge="red")
ARENA = sone(-846, 62, 376, -834, 69, 388)
fill(skall, (-846, 51, 375), (-844, 59, 377), SKALL)          # stigesjakt arena -> etasje 4
hull((-845, 45, 376), (-845, 60, 376))
stige(-845, 376, 45, 60)
hemmelighet("s_arena", f"if entity {sone(-845, 62, 376, -834, 69, 388)}",
            ["fill -847 62 381 -847 64 383 minecraft:iron_bars replace minecraft:air",
             "playsound minecraft:block.iron_door.close block @a -840 63 382 2 0.5",
             f'title {ARENA} title {{"text":"ARENAEN","color":"red","bold":true}}',
             f'title {ARENA} subtitle {{"text":"Beseir alle vaktene!","color":"gray"}}'],
            ["fill -847 62 381 -847 64 383 minecraft:air replace minecraft:iron_bars"], navn_="Arenaen startet")
hemmelighet("s_arena_seier", "if score #s_arena df_s matches 1 unless entity @e[type=dodsfjellet:vakt,tag=df_arena]",
            ["setblock -845 61 376 minecraft:ladder[facing=south]",
             "fill -847 62 381 -847 64 383 minecraft:air replace minecraft:iron_bars",
             f'title {ARENA} title {{"text":"Arenaen er ryddet!","color":"gold"}}',
             f'title {ARENA} subtitle {{"text":"En luke åpnet seg i hjørnet...","color":"gray"}}'],
            [f"setblock -845 61 376 minecraft:smooth_stone"], navn_="Arenaen vunnet")

# =========================================================================== ETASJE 4 (gulv 44)
G4 = 44
# L1 Lysgåten (Lights Out): tenn alle ni lysene. Hver knapp skifter seg selv og naboene.
rom(-846, 376, -834, 388, G4)
romnavn_sone("Lysgåten", -846, 45, 376, -834, 49, 388, farge="yellow")
L1_SONE = sone(-846, 45, 376, -834, 49, 388)
PAA, AV = "minecraft:ochre_froglight", "minecraft:black_concrete"
LYS_Z, LYS_Y = (383, 382, 381), (48, 47, 46)       # kolonne 0..2 (venstre->høyre sett fra rommet), rad 0..2 (topp->bunn)


def lys_pos(r, c):
    return -833, LYS_Y[r], LYS_Z[c]


start = [[True] * 3 for _ in range(3)]
for (pr, pc) in [(0, 0), (1, 1), (2, 2), (0, 2)]:          # "trykk" fra løst tilstand -> alltid løsbar start
    for (r, c) in [(pr, pc), (pr - 1, pc), (pr + 1, pc), (pr, pc - 1), (pr, pc + 1)]:
        if 0 <= r < 3 and 0 <= c < 3:
            start[r][c] = not start[r][c]
LYS_START = [f"setblock {' '.join(map(str, lys_pos(r, c)))} {PAA if start[r][c] else AV}" for r in range(3) for c in range(3)]
for r in range(3):
    for c in range(3):
        x, y, z = lys_pos(r, c)
        detaljer.append(f"setblock {x} {y} {z} {PAA if start[r][c] else AV}")
        setb(x - 1, y, z, "minecraft:stone_button[face=wall,facing=west]")
        knapp = f"{x - 1} {y} {z}"
        tick.append(f"execute if block {knapp} minecraft:stone_button[powered=true] unless score #lk{r}{c} df_t matches 1 "
                    f"run function {NS}:lys/trykk_{r}{c}")
        tick.append(f"execute if block {knapp} minecraft:stone_button[powered=false] run scoreboard players set #lk{r}{c} df_t 0")
        cmds = [f"scoreboard players set #lk{r}{c} df_t 1", "playsound minecraft:block.note_block.chime block @a -840 47 382 1 1.4"]
        for (rr, cc) in [(r, c), (r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]:
            if 0 <= rr < 3 and 0 <= cc < 3:
                p = " ".join(map(str, lys_pos(rr, cc)))
                cmds += [f"execute store success score #lt df_t if block {p} {PAA}",
                         f"execute if score #lt df_t matches 1 run setblock {p} {AV}",
                         f"execute if score #lt df_t matches 0 run setblock {p} {PAA}"]
        filer[f"lys/trykk_{r}{c}"] = cmds
filer["b/lys_lost"] = ["execute " + " ".join(f"if block {' '.join(map(str, lys_pos(r, c)))} {PAA}"
                                             for r in range(3) for c in range(3)) + " run return 1", "return 0"]
skilt(-834, 47, 379, "west", "LYSGÅTEN", "Tenn alle ni", "lysene.", farge="yellow")
skilt(-834, 47, 385, "west", "Hver knapp", "skifter seg selv", "og naboene", "sine.", farge="gray")
hemmelighet("s_lys", f"if function {NS}:b/lys_lost",
            ["fill -847 45 381 -847 47 383 minecraft:air",
             f'title {L1_SONE} title {{"text":"Alle lysene tent!","color":"yellow"}}']
            + belonning("fjellvokter_bukser", L1_SONE, "Fjellvokter-bukser"),
            ["fill -847 45 381 -847 47 383 " + SKALL] + LYS_START, navn_="Lysgåten")

# L1 -> L2
gang(-858, 381, -848, 383, G4)
# L2 Den usynlige broen: usynlig barriere-sti over en lavagrop. Støv viser veien.
rom(-871, 376, -859, 388, G4)
romnavn_sone("Den usynlige broen", -871, 45, 376, -859, 49, 388, farge="light_purple")
fill(skall, (-870, 39, 375), (-860, 43, 389), SKALL)
fill(luft, (-869, 41, 376), (-861, 44, 388), "minecraft:air")
fill(luft, (-869, 40, 376), (-861, 40, 388), "minecraft:lava")
USYNLIG = [(-861, 382), (-862, 382), (-863, 382), (-863, 381), (-863, 380), (-863, 379), (-864, 379), (-865, 379),
           (-865, 380), (-865, 381), (-865, 382), (-865, 383), (-865, 384), (-865, 385), (-866, 385), (-867, 385),
           (-867, 384), (-867, 383), (-867, 382), (-868, 382), (-869, 382)]
for (x, z) in USYNLIG:
    setb(x, 44, z, "minecraft:barrier")
L2_SONE = sone(-871, 41, 376, -859, 49, 388)
tick.append(f"execute if score #klokke df_t matches 0 if entity {L2_SONE} run function {NS}:bro/stov")
filer["bro/stov"] = [f"particle minecraft:dust{{color:[0.85,0.9,1.0],scale:0.9}} {x}.5 45.15 {z}.5 0.18 0.02 0.18 0 2"
                     for (x, z) in USYNLIG]
skilt(-859, 46, 379, "west", "DEN USYNLIGE", "BROEN", "Følg støvet...", farge="light_purple")

# L2 -> L3
gang(-883, 381, -872, 383, G4)
# L3 Tallgåten: 1 1 2 3 5 8 ?
rom(-896, 376, -884, 388, G4)
romnavn_sone("Tallgåten", -896, 45, 376, -884, 49, 388, farge="aqua")
L3_SONE = sone(-896, 45, 376, -884, 49, 388)
TALL = {378: "11", 380: "21", 382: "12", 384: "13", 386: "15"}
TALL_RIKTIG = 384
for z, t in TALL.items():
    setb(-896, 46, z, "minecraft:stone_button[face=wall,facing=east]")
    skilt(-896, 47, z, "east", "", t, farge="aqua")
skilt(-890, 46, 376, "south", "TALLGÅTEN", "1  1  2  3  5  8  ?", "Trykk på det", "neste tallet.", farge="aqua")
skilt(-888, 46, 376, "south", "Feil tall", "= døden...", farge="red")
hemmelighet("s_tall", f"if block -896 46 {TALL_RIKTIG} minecraft:stone_button[powered=true]",
            ["fill -891 45 389 -889 47 389 minecraft:air",
             f'title {L3_SONE} title {{"text":"Riktig: 13!","color":"aqua"}}']
            + belonning("fjellvokter_stovler", L3_SONE, "Fjellvokter-støvler"),
            ["fill -891 45 389 -889 47 389 " + SKALL], navn_="Tallgåten")
felle("tall_feil", "unless score #s_tall df_s matches 1 if function " + f"{NS}:b/tall_feil", 50,
      ["playsound minecraft:entity.evoker.prepare_attack hostile @a -890 46 382 2 0.7",
       f'title {sone(-896, 45, 376, -884, 49, 388, offer=False)} title {{"text":"FEIL TALL","color":"dark_red","bold":true}}'],
      {"1..40": [f"execute as {L3_SONE} at @s run summon minecraft:evoker_fangs ~ ~ ~"]}, navn_="Tallgåten (feil svar)")
filer["b/tall_feil"] = [f"execute if block -896 46 {z} minecraft:stone_button[powered=true] run return 1"
                        for z in TALL if z != TALL_RIKTIG] + ["return 0"]

# L3 -> L4
gang(-891, 390, -889, 400, G4)
# L4 Bølgegulvet: radene i gulvet forsvinner i en bølge som beveger seg. Tim hoppene!
rom(-896, 401, -884, 413, G4)
romnavn_sone("Bølgegulvet", -896, 45, 401, -884, 49, 413, farge="red")
L4_SONE = sone(-896, 40, 401, -884, 49, 413)
fill(skall, (-897, 38, 400), (-883, 43, 414), SKALL)
fill(luft, (-896, 40, 402), (-884, 43, 411), "minecraft:air")
fill(luft, (-896, 39, 402), (-884, 39, 411), "minecraft:lava")
RADER = list(range(402, 412))
tick.append(f"execute if score #aktiv df_t matches 1 if entity {L4_SONE} run function {NS}:bolge/tick")
filer["bolge/tick"] = ["scoreboard players add #bolge_t df_t 1",
                       f"execute if score #bolge_t df_t matches 14.. run function {NS}:bolge/skift"]
filer["bolge/skift"] = ["scoreboard players set #bolge_t df_t 0",
                        "scoreboard players add #bolge df_t 1",
                        "execute if score #bolge df_t matches 4.. run scoreboard players set #bolge df_t 0",
                        f"fill -896 44 402 -884 44 411 {GULV}",
                        "playsound minecraft:block.piston.contract block @a -890 45 407 0.8 1.4"] + [
    f"execute if score #bolge df_t matches {p} run function {NS}:bolge/p{p}" for p in range(4)]
for p in range(4):
    filer[f"bolge/p{p}"] = [f"fill -896 44 {z} -884 44 {z} minecraft:air" for i, z in enumerate(RADER) if (i + p) % 4 == 0]
reparer.append(f"fill -896 44 402 -884 44 411 {GULV}")
skilt(-894, 46, 401, "south", "BØLGEGULVET", "Gulvet beveger", "seg. Tim", "hoppene!", farge="red")
# stigesjakt L4 -> etasje 5
fill(skall, (-891, 34, 412), (-889, 42, 414), SKALL)
hull((-890, 28, 413), (-890, 43, 413))
stige(-890, 413, 28, 44, facing="north")

# =========================================================================== ETASJE 5 (gulv 27)
G5 = 27
# M1 Kodelåsen
rom(-896, 401, -884, 413, G5)
romnavn_sone("Kodelåsen", -896, 28, 401, -884, 32, 413, farge="aqua")
M1_SONE = sone(-896, 28, 401, -884, 32, 413)
SPAK_X = (-893, -891, -889, -887)
KODE = (True, False, False, True)   # PÅ AV AV PÅ
for n, x in enumerate(SPAK_X):
    setb(x, 29, 401, "minecraft:lever[face=wall,facing=south,powered=false]")
    setb(x, 30, 400, "minecraft:redstone_lamp")
    skilt(x, 28, 401, "south", "", f"{n + 1}", farge="aqua")
NULLSTILL_SPAKER = ([f"setblock {x} 29 401 minecraft:lever[face=wall,facing=south,powered=false]" for x in SPAK_X] +
                    [f"setblock {x} 30 400 minecraft:redstone_lamp[lit=false]" for x in SPAK_X])
setb(-885, 29, 401, "minecraft:stone_button[face=wall,facing=south]")
skilt(-885, 28, 401, "south", "SJEKK", "KODEN", farge="red")
skilt(-895, 29, 401, "south", "Fire koder har", "du funnet.", "PÅ = lampen lyser", "Feil = døden", farge="yellow")
fill(detaljer, (-883, 28, 406), (-883, 30, 408), "minecraft:iron_bars")
riktig_kode = " ".join(f"if block {x} 29 401 minecraft:lever[powered={'true' if p else 'false'}]"
                       for x, p in zip(SPAK_X, KODE))
KNAPP = "if block -885 29 401 minecraft:stone_button[powered=true]"
hemmelighet("s_kode", f"{KNAPP} {riktig_kode}",
            ["fill -883 28 406 -883 30 408 minecraft:air",
             f'title {M1_SONE} title {{"text":"PORTEN ÅPNES","color":"gold","bold":true}}']
            + belonning("vokterknuser", M1_SONE, "Vokterknuseren"),
            ["fill -883 28 406 -883 30 408 minecraft:iron_bars"] + NULLSTILL_SPAKER, navn_="Kodelåsen")
felle("kode_feil", f"unless score #s_kode df_s matches 1 {KNAPP} unless function {NS}:b/kode_ok", 70,
      ["playsound minecraft:entity.evoker.prepare_attack hostile @a -890 29 407 2 0.7",
       f'title {sone(-896, 28, 401, -884, 32, 413, offer=False)} title {{"text":"FEIL KODE","color":"dark_red","bold":true}}'],
      {"1..60": [f"execute as {M1_SONE} at @s run summon minecraft:evoker_fangs ~ ~ ~"]},
      NULLSTILL_SPAKER, navn_="Kodelåsen (feil kode)")
filer["b/kode_ok"] = [f"execute {riktig_kode} run return 1", "return 0"]

# M2 SKATTKAMMERET – voktet av Skattevokteren
rom(-882, 398, -858, 416, G5, h=9, vegg="minecraft:gilded_blackstone", gulvblokk="minecraft:gold_block", lys=False)
romnavn_sone("SKATTKAMMERET", -882, 28, 398, -858, 36, 416, farge="gold")
SKATT_SONE = sone(-882, 28, 398, -858, 36, 416, offer=False)
for x in (-878, -870, -862):
    for z in (402, 412):
        setb(x, 36, z, LYS)
for (x, z, b) in [(-880, 400, "diamond_block"), (-880, 414, "emerald_block"), (-860, 400, "gold_block"),
                  (-860, 414, "diamond_block")]:
    fill(detaljer, (x - 1, 28, z - 1), (x + 1, 29, z + 1), f"minecraft:{b}")
fill(detaljer, (-863, 28, 406), (-861, 28, 408), "minecraft:gold_block")
setb(-862, 29, 407, kiste("west", SKATT))
setb(-862, 28, 405, "minecraft:beacon")
setb(-858, 29, 407, "minecraft:stone_button[face=wall,facing=west]")
skilt(-858, 30, 407, "west", "Trykk for å", "komme deg ut", "levende!", farge="green")
skilt(-882, 30, 400, "east", "Du klarte", "DØDSFJELLET!", farge="gold")
felle("ut", "if block -858 29 407 minecraft:stone_button[powered=true]", 25,
      [f"execute as {SKATT_SONE} run tellraw @a "
       '["",{"selector":"@s","color":"gold","bold":true},{"text":" overlevde DØDSFJELLET!","color":"yellow"}]',
       f'title {SKATT_SONE} title {{"text":"DU OVERLEVDE!","color":"gold","bold":true}}',
       admin_logg("Noen klarte Dødsfjellet!", "gold"),
       f"tag {SKATT_SONE} remove df_deltaker",
       f"tp {SKATT_SONE} {SPAWN}",
       "summon minecraft:firework_rocket -893 130 452 {LifeTime:20,FireworksItem:{id:\"minecraft:firework_rocket\",count:1,"
       "components:{\"minecraft:fireworks\":{explosions:[{shape:\"large_ball\",colors:[I;16766720,16711680],has_twinkle:1b}]}}}}",
       "summon minecraft:firework_rocket -895 130 450 {LifeTime:30,FireworksItem:{id:\"minecraft:firework_rocket\",count:1,"
       "components:{\"minecraft:fireworks\":{explosions:[{shape:\"star\",colors:[I;65280,255],has_trail:1b}]}}}}"],
      alltid=True)

BOSS = vakt(-866, 28, 407, ("df_boss",),
            ",CustomName:'{\"text\":\"Skattevokteren\",\"color\":\"dark_red\",\"bold\":true}',Health:150f,"
            "attributes:[{id:\"minecraft:generic.max_health\",base:150d},{id:\"minecraft:generic.attack_damage\",base:4d},"
            "{id:\"minecraft:generic.movement_speed\",base:0.32d},{id:\"minecraft:generic.knockback_resistance\",base:0.6d}],"
            "HandItems:[{id:\"minecraft:netherite_sword\",count:1},{}],"
            "ArmorItems:[{id:\"minecraft:netherite_boots\",count:1},{id:\"minecraft:netherite_leggings\",count:1},"
            "{id:\"minecraft:netherite_chestplate\",count:1},{id:\"minecraft:netherite_helmet\",count:1}],Epler:4")
VAKTER = [
    BOSS,
    vakt(-872, 28, 402), vakt(-872, 28, 412), vakt(-868, 28, 404),
    vakt(-860, 30, 400), vakt(-880, 30, 414),                         # oppå skattehaugene
    vakt(-842, 62, 378, ("df_arena",)), vakt(-838, 62, 386, ("df_arena",)), vakt(-836, 62, 382, ("df_arena",)),
    vakt(-860, 62, 379), vakt(-860, 62, 385),                         # brovakter i Lavakløfta
]
reparer += ["kill @e[type=dodsfjellet:vakt]"] + VAKTER
BOSS_SONE = "@a[x=-883,y=26,z=397,dx=26,dy=12,dz=20]"
tick += [
    "execute store result bossbar df:vokter value run data get entity @e[type=dodsfjellet:vakt,tag=df_boss,limit=1] Health",
    f"bossbar set df:vokter players {BOSS_SONE}",
    "execute if entity @e[type=dodsfjellet:vakt,tag=df_boss] run bossbar set df:vokter visible true",
    "execute unless entity @e[type=dodsfjellet:vakt,tag=df_boss] run bossbar set df:vokter visible false",
]

reparer.append(f"data merge block -862 29 407 {{Items:[{','.join(SKATT)}]}}")
reparer.append(f"data merge block -887 96 401 {{Items:[{','.join(A_KISTE)}]}}")
reparer.append("kill @e[type=minecraft:area_effect_cloud,x=-935,y=20,z=340,dx=110,dy=115,dz=120]")
reparer.append("kill @e[type=#minecraft:arrows,x=-935,y=20,z=340,dx=110,dy=115,dz=120]")
reparer.append("kill @e[type=minecraft:item,x=-935,y=20,z=340,dx=110,dy=115,dz=120]")

# =========================================================================== ADMIN-ROMMET (kontrollrommet over fjellet)
# Innvendig x -885..-863, z 421..433, gulv y=200, takhøyde 10. Panelet er nordveggen (z=420).
rom(-885, 421, -863, 433, 200, h=10, vegg="minecraft:polished_deepslate", gulvblokk="minecraft:smooth_quartz", lys=False)
for x in range(-883, -863, 4):
    for z in (424, 430):
        setb(x, 211, z, "minecraft:sea_lantern")
for z in range(423, 433, 3):                       # lys i sideveggene, så rommet ikke er mørkt
    for y in (203, 207):
        setb(-886, y, z, "minecraft:sea_lantern")
        setb(-862, y, z, "minecraft:sea_lantern")
PANEL_RAD = {1: 209, 2: 207, 3: 205, 4: 203, 5: 201}
panel_tick = []
panel_tekst = ["kill @e[type=minecraft:text_display,tag=df_panel]"]


def tekst_display(x, y, z, tekst, farge="white", skala=0.4):
    return (f"summon minecraft:text_display {x} {y} {z} {{Tags:[\"df_panel\"],billboard:\"center\",alignment:\"center\","
            f"text:'{{\"text\":\"{tekst}\",\"color\":\"{farge}\"}}',background:1711276032,"
            f"transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],"
            f"translation:[0f,0f,0f],scale:[{skala}f,{skala}f,{skala}f]}}}}")


def slug(t):
    for a, b in (("ø", "o"), ("å", "a"), ("æ", "ae"), ("Ø", "O"), ("Å", "A"), ("Æ", "AE"), (" ", "_")):
        t = t.replace(a, b)
    return "rom_" + t


kol = {e: 0 for e in PANEL_RAD}
for (etasje, tekst, koord) in ROM:
    y = PANEL_RAD[etasje]
    x = -882 + 3 * kol[etasje]
    kol[etasje] += 1
    fill(detaljer, (x, y, 420), (x + 1, y, 420), "minecraft:gray_concrete")
    s = sone(*koord)
    panel_tick += [f"execute if entity {s} run fill {x} {y} 420 {x + 1} {y} 420 minecraft:lime_concrete",
                   f"execute unless entity {s} run fill {x} {y} 420 {x + 1} {y} 420 minecraft:gray_concrete",
                   f"execute store result score {slug(tekst)} df_rom if entity {s}",
                   f"execute if score {slug(tekst)} df_rom matches 0 run scoreboard players reset {slug(tekst)} df_rom",
                   f"execute if score {slug(tekst)} df_rom matches 1.. run scoreboard players display name {slug(tekst)} df_rom "
                   f'{{"text":"{tekst}","color":"yellow"}}']
    panel_tekst.append(tekst_display(x + 1.0, y - 0.55, 421.4, tekst))
for etasje, y in PANEL_RAD.items():
    panel_tekst.append(tekst_display(-884.0, y + 0.3, 421.4, f"Etasje {etasje}", "gold", 0.5))
panel_tekst.append(tekst_display(-874.0, 210.4, 421.4, "KONTROLLROMMET - grønn = spillere i rommet", "aqua", 0.5))
filer["admin/panel"] = ["scoreboard players reset * df_rom"] + panel_tick
tick.append(f"execute if score #klokke df_t matches 5 run function {NS}:admin/panel")

# Knapper på sørveggen (z=434)
ADMIN_KNAPPER = [(-882, "Følg neste", "spiller", "folg"), (-878, "Restart", "mapet", "restart"),
                 (-874, "Feller", "AV / PÅ", "feller"), (-870, "Nullstill", "feller+dører", "nullstill"),
                 (-866, "Forlat", "admin", "forlat")]
for nr, (x, l1, l2, handling) in enumerate(ADMIN_KNAPPER):
    setb(x, 202, 433, "minecraft:polished_blackstone_button[face=wall,facing=north]")
    skilt(x, 203, 433, "north", l1, l2, farge="gold")
    b = f"{x} 202 433"
    tick.append(f"execute if block {b} minecraft:polished_blackstone_button[powered=true] unless score #ab{nr} df_t matches 1 "
                f"run function {NS}:admin/knapp{nr}")
    tick.append(f"execute if block {b} minecraft:polished_blackstone_button[powered=false] run scoreboard players set #ab{nr} df_t 0")
    filer[f"admin/knapp{nr}"] = [f"scoreboard players set #ab{nr} df_t 1",
                                 f"execute positioned {x} 202 433 as @p[distance=..7] run function {NS}:admin/{handling}"]
skilt(-885, 203, 427, "east", "Tab-lista viser", "livet til alle.", "Sidebaren viser", "hvor de er.", farge="aqua")

filer["admin/folg"] = [
    "execute unless entity @a[tag=df_deltaker] run tellraw @s {\"text\":\"[Admin] Ingen spillere er inne i fjellet nå.\",\"color\":\"gray\"}",
    f"execute if entity @a[tag=df_deltaker] run function {NS}:admin/folg2"]
filer["admin/folg2"] = [
    "execute unless entity @a[tag=df_deltaker,tag=!df_sett] run tag @a remove df_sett",
    "tag @a[tag=df_deltaker,tag=!df_sett,limit=1,sort=random] add df_neste",
    "gamemode spectator @s",
    "spectate @a[tag=df_neste,limit=1] @s",
    'tellraw @s ["",{"text":"[Admin] Du følger nå ","color":"gold"},{"selector":"@a[tag=df_neste]"},'
    '{"text":". Trykk shift for å slutte, /function df:admin for å komme tilbake.","color":"gray"}]',
    "tag @a[tag=df_neste] add df_sett",
    "tag @a remove df_neste"]
filer["admin/restart"] = [f"function {NS}:restart_admin"]
filer["admin/feller"] = [
    "execute store success score #byttet df_t if score #aktiv df_t matches 1",
    "execute if score #byttet df_t matches 1 run scoreboard players set #aktiv df_t 0",
    "execute if score #byttet df_t matches 0 run scoreboard players set #aktiv df_t 1",
    'execute if score #aktiv df_t matches 1 run tellraw @a[tag=df_admin] {"text":"[Admin] Fellene er PÅ.","color":"red"}',
    'execute if score #aktiv df_t matches 0 run tellraw @a[tag=df_admin] {"text":"[Admin] Fellene er AV.","color":"green"}']
filer["admin/nullstill"] = [f"function {NS}:reparer"]
filer["admin/forlat"] = ["tag @s remove df_admin", "team leave @s", "gamemode adventure @s", f"tp @s {SPAWN}",
                         'tellraw @s {"text":"[Admin] Du har forlatt kontrollrommet.","color":"gray"}']

# =========================================================================== datapack-filer
FUNKSJONER = {
    "load": [
        "scoreboard objectives add df_t dummy",
        "scoreboard objectives add df_s dummy",
        "execute unless score #aktiv df_t matches 0..1 run scoreboard players set #aktiv df_t 1",
        'bossbar add df:vokter {"text":"Skattevokteren","color":"dark_red","bold":true}',
        "bossbar set df:vokter color red",
        "bossbar set df:vokter max 150",
        "bossbar set df:vokter style notched_10",
        "scoreboard objectives add df_dod deathCount",
        'scoreboard objectives add df_rom dummy {"text":"Hvor er spillerne?","color":"gold","bold":true}',
        'scoreboard objectives add df_liv health {"text":"Liv","color":"red"}',
        "scoreboard objectives modify df_liv rendertype hearts",
        "scoreboard objectives setdisplay list df_liv",
        "team add df_admin",
        "team modify df_admin color gold",
        'team modify df_admin prefix {"text":"[Admin] ","color":"gold"}',
        "scoreboard objectives setdisplay sidebar.team.gold df_rom",
    ],
    "tick": ["scoreboard players add #klokke df_t 1",
             "execute if score #klokke df_t matches 10.. run scoreboard players set #klokke df_t 0"]
            + tick
            + [f"execute if score #klokke df_t matches 0 run {r}" for r in romnavn]
            + [f"execute if score #klokke df_t matches 0 run effect give {G_SONE} minecraft:darkness 3 0 true"],
    "bygg": [
        f"forceload add {OMRADE}",
        'tellraw @a {"text":"[Dødsfjellet] Laster området og bygger fangehullet...","color":"gray"}',
        f"function {NS}:bygg_vent"],
    "bygg_vent": [
        f"execute if function {NS}:b/lastet run function {NS}:bygg_utfor",
        f"execute unless function {NS}:b/lastet run schedule function {NS}:bygg_vent 20t"],
    "b/lastet": ["execute " + " ".join(f"if loaded {x} 64 {z}" for x in range(-935, -829, 16) for z in range(340, 457, 16))
                 + " if loaded -830 64 456 run return 1", "return 0"],
    "bygg_utfor": ["# Generert av generer_dodsfjellet.py"] + skall + luft + detaljer + [
        f"function {NS}:reparer_utfor",
    ] + panel_tekst + [
        f"forceload remove {OMRADE}",
        "gamerule keepInventory true",
        "gamerule doMobSpawning false",
        "difficulty normal",
        "defaultgamemode adventure",
        'tellraw @a ["",{"text":"[Dødsfjellet] ","color":"dark_red","bold":true},{"text":"Fangehullet er bygget! Finn den hemmelige veien i inngangshallen... ","color":"gold"},{"text":"(/function df:hjelp)","color":"gray"}]'],
    # reparer laster området selv (vaktene og kistene må være lastet), venter litt og nullstiller alt
    "reparer": [f"forceload add {OMRADE}", f"function {NS}:reparer_vent"],
    "reparer_vent": [
        f"execute if function {NS}:b/lastet run schedule function {NS}:reparer_ferdig 40t",
        f"execute unless function {NS}:b/lastet run schedule function {NS}:reparer_vent 20t"],
    "reparer_ferdig": [f"function {NS}:reparer_utfor", f"forceload remove {OMRADE}",
                       'tellraw @a {"text":"[Dødsfjellet] Alt er nullstilt: feller, hemmeligheter, kister og vakter.","color":"gold"}'],
    "reparer_utfor": reparer,
    "admin": ["tag @s add df_admin", "team join df_admin @s", "gamemode creative @s",
              "tp @s -874 201 427 180 0",
              'tellraw @s ["",{"text":"[Admin] ","color":"gold","bold":true},{"text":"Velkommen til kontrollrommet! '
              'Panelet viser hvor spillerne er (grønn = noen der). Sidebaren teller spillere per rom, tab-lista viser livet. '
              'Hendelser kommer i chatten. Knappene står bak deg.","color":"yellow"}]'],
    "av": ["scoreboard players set #aktiv df_t 0",
           'tellraw @s {"text":"[Dødsfjellet] Fellene er AV.","color":"green"}'],
    "paa": ["scoreboard players set #aktiv df_t 1",
            'tellraw @s {"text":"[Dødsfjellet] Fellene er PÅ.","color":"red"}'],
    "hjelp": [
        'tellraw @s {"text":"===== DØDSFJELLET =====","color":"dark_red","bold":true}',
        'tellraw @s {"text":"Finn den hemmelige veien fra inngangshallen og kom deg til skatten.","color":"gray"}',
        'tellraw @s {"text":"/function df:reparer – lukker hemmeligheter, fyller kister, resetter feller","color":"yellow"}',
        'tellraw @s {"text":"/function df:av | df:paa – slå fellene av/på","color":"yellow"}',
        'tellraw @s {"text":"/function df:fasit – teleporterer deg rundt i fangehullet","color":"yellow"}',
        'tellraw @s {"text":"/function df:admin – kontrollrommet der du følger med på spillerne","color":"yellow"}',
        'tellraw @s {"text":"Dør noen, starter hele fjellet på nytt for alle.","color":"gray"}',
        'tellraw @s {"text":"Når alle er inne, lukker inngangen seg. Den som dør er ute. Når alle er ute, nullstilles fjellet.","color":"gray"}',
        'tellraw @s {"text":"Creative = trygg. Adventure/survival = død.","color":"red"}',
    ],
    "fasit": [
        'tellraw @s ["",{"text":"Rom: ","color":"gold"},'
        + ",".join('{"text":"[' + n + ']","color":"aqua","clickEvent":{"action":"run_command","value":"/tp @s ' + p + '"}}'
                   for n, p in [("Inngang", "-889 128 452"), ("A", "-890 96 411"), ("B", "-868 96 407"),
                                ("C", "-865 96 387"), ("D", "-865 96 361"), ("E", "-869 79 352"),
                                ("F", "-886 79 362"), ("G", "-910 79 357"), ("H", "-915 79 377"),
                                ("I", "-890 79 386"), ("K", "-895 62 380"), ("Arena", "-850 62 382"),
                                ("Lys", "-840 45 386"), ("Bro", "-860 45 382"), ("Tall", "-886 45 382"),
                                ("Bølge", "-890 45 401"), ("Kode", "-890 28 411"), ("Skatt", "-878 28 407"),
                                ("Admin", "-874 201 427")]) + "]",
        'tellraw @s {"text":"B: Kam, Fotspor, Ekko | C: mørke steiner | D: løp til hjørnet | F: knapp under lampa | G: snik | H: sprukken vegg | Arena: drep vaktene | Lys: tenn alle ni | Bro: følg støvet | Tall: 13 | Kode: PÅ AV AV PÅ","color":"gray"}',
    ],
}


def main():
    if PACK.exists():
        shutil.rmtree(PACK)
    fdir = PACK / "data" / NS / "function"
    alle = {**FUNKSJONER, **filer}
    for navn_, linjer in alle.items():
        sti = fdir / f"{navn_}.mcfunction"
        sti.parent.mkdir(parents=True, exist_ok=True)
        sti.write_text("\n".join(linjer) + "\n", encoding="utf-8")
    pred = PACK / "data" / NS / "predicate"
    pred.mkdir(parents=True)
    (pred / "sniker.json").write_text(json.dumps({"condition": "minecraft:entity_properties", "entity": "this",
                                                  "predicate": {"flags": {"is_sneaking": True}}}, indent=2))
    tags = PACK / "data" / "minecraft" / "tags" / "function"
    tags.mkdir(parents=True)
    (tags / "load.json").write_text(json.dumps({"values": [f"{NS}:load"]}))
    (tags / "tick.json").write_text(json.dumps({"values": [f"{NS}:tick"]}))
    (PACK / "pack.mcmeta").write_text(json.dumps({"pack": {
        "description": "§4Dødsfjellet§r – gigantisk felle-fangehull", "pack_format": 48}},
        ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.make_archive(str(PACK), "zip", PACK)
    print(f"{len(alle)} funksjoner, bygg = {len(FUNKSJONER['bygg'])} kommandoer, "
          f"groper i labyrinten: {len(GROPER)}, løsningslengde: {len(losning)} celler")


if __name__ == "__main__":
    main()
