"""Lager generer_dodsfjellet_26.py (Minecraft 26.3) fra 1.21.1-generatoren.

Hver erstatning sjekkes – feiler skriptet, betyr det at kilden har endret seg og porten må oppdateres.
"""
from pathlib import Path

HER = Path(__file__).parent
kilde = (HER / "generer_dodsfjellet.py").read_text(encoding="utf-8")

ERSTATT = [
    # utdata
    ('PACK = ROT / "dodsfjellet_1.21.1"', 'PACK = ROT / "dodsfjellet_26"'),
    ('"""Genererer datapacken "Dødsfjellet" (Minecraft 1.21.1)', '"""Genererer datapacken "Dødsfjellet" (Minecraft 26.3)'),
    ('Kjør:  python generer_dodsfjellet.py   ->  dodsfjellet_1.21.1/  og  dodsfjellet_1.21.1.zip',
     'Kjør:  python generer_dodsfjellet_26.py   ->  dodsfjellet_26/  og  dodsfjellet_26.zip  (generert fra generer_dodsfjellet.py av verktoy_port26.py)'),
    # skilt: meldinger er tekstkomponenter (SNBT), ikke JSON-strenger
    ("msg = \",\".join(\"'\" + json.dumps(l, ensure_ascii=False) + \"'\" for l in linjer)",
     "msg = \",\".join(json.dumps(l, ensure_ascii=False) for l in linjer)"),
    # egendefinert navn = komponent
    ("return '\"minecraft:custom_name\":\\'{\"text\":\"' + tekst + '\",\"color\":\"' + farge + '\",\"italic\":false}\\''",
     "return '\"minecraft:custom_name\":{text:\"' + tekst + '\",color:\"' + farge + '\",italic:false}'"),
    # can_break: ett predikat direkte
    (',"minecraft:can_break":{predicates:[{blocks:"minecraft:cracked_deepslate_bricks"}]}',
     ',"minecraft:can_break":{blocks:"minecraft:cracked_deepslate_bricks"}'),
    # fortryllelser: direkte kart
    ('"minecraft:enchantments":{levels:{"minecraft:sharpness":5,"minecraft:unbreaking":3,"minecraft:fire_aspect":2}}',
     '"minecraft:enchantments":{"minecraft:sharpness":5,"minecraft:unbreaking":3,"minecraft:fire_aspect":2}'),
    ('"minecraft:enchantments":{levels:{"minecraft:protection":4,"minecraft:unbreaking":3}}',
     '"minecraft:enchantments":{"minecraft:protection":4,"minecraft:unbreaking":3}'),
    # fallende blokker: BlockState bruker id
    ('{BlockState:{Name:"minecraft:anvil"}', '{BlockState:{id:"minecraft:anvil"}'),
    # bossen: komponent-navn, attributter uten generic., equipment i stedet for HandItems/ArmorItems
    (",CustomName:'{\\\"text\\\":\\\"Skattevokteren\\\",\\\"color\\\":\\\"dark_red\\\",\\\"bold\\\":true}',Health:150f,",
     ",CustomName:{text:\\\"Skattevokteren\\\",color:\\\"dark_red\\\",bold:true},Health:150f,"),
    ("minecraft:generic.max_health", "minecraft:max_health"),
    ("minecraft:generic.attack_damage", "minecraft:attack_damage"),
    ("minecraft:generic.movement_speed", "minecraft:movement_speed"),
    ("minecraft:generic.knockback_resistance", "minecraft:knockback_resistance"),
    ('"HandItems:[{id:\\"minecraft:netherite_sword\\",count:1},{}],"\n'
     '            "ArmorItems:[{id:\\"minecraft:netherite_boots\\",count:1},{id:\\"minecraft:netherite_leggings\\",count:1},"\n'
     '            "{id:\\"minecraft:netherite_chestplate\\",count:1},{id:\\"minecraft:netherite_helmet\\",count:1}],Epler:4")',
     '"equipment:{mainhand:{id:\\"minecraft:netherite_sword\\",count:1},feet:{id:\\"minecraft:netherite_boots\\",count:1},"\n'
     '            "legs:{id:\\"minecraft:netherite_leggings\\",count:1},chest:{id:\\"minecraft:netherite_chestplate\\",count:1},"\n'
     '            "head:{id:\\"minecraft:netherite_helmet\\",count:1}},Epler:4")'),
    # tekstskjermer: tekst som komponent
    ("f\"text:'{{\\\"text\\\":\\\"{tekst}\\\",\\\"color\\\":\\\"{farge}\\\"}}',background:1711276032,\"",
     "f\"text:{{text:\\\"{tekst}\\\",color:\\\"{farge}\\\"}},background:1711276032,\""),
    # spilleregler har nye navn
    ('"gamerule keepInventory true"', '"gamerule keep_inventory true"'),
    ('"gamerule doMobSpawning false"', '"gamerule spawn_mobs true"'),
    # Dødsriket trenger naturlig spawning – i stedet fjernes vanlige monstre inne i fangehullet hvert halve sekund
    ('"tick": ["scoreboard players add #klokke df_t 1",',
     '"tick": ["scoreboard players add #klokke df_t 1", *[f"execute if score #klokke df_t matches 0 run kill @e[x=-935,y=20,z=340,dx=105,dy=81,dz=109,type={t}]" for t in ("#minecraft:undead", "minecraft:creeper", "minecraft:spider", "minecraft:cave_spider", "minecraft:enderman", "minecraft:witch", "minecraft:slime", "minecraft:silverfish")],'),
    # klikk-hendelser
    ('"clickEvent":{"action":"run_command","value":"/tp @s \' + p + \'"}}',
     '"click_event":{"action":"run_command","command":"/tp @s \' + p + \'"}}'),
    # predikat: 'type' i stedet for 'condition', og flags med navnerom
    ('"predicate": {"flags": {"is_sneaking": True}}', '"predicate": {"minecraft:flags": {"is_sneaking": True}}'),
    ('{"condition": "minecraft:entity_properties"', '{"type": "minecraft:entity_properties"'),
    # pack.mcmeta
    ('"description": "§4Dødsfjellet§r – gigantisk felle-fangehull", "pack_format": 48}}',
     '"description": "§4Dødsfjellet§r – gigantisk felle-fangehull (26.3)", "min_format": 121, "max_format": 200}}'),
    # etter restart: reisekompasset tilbake
    ('        "clear @a[tag=df_deltaker]",\n',
     '        "clear @a[tag=df_deltaker]",\n        "give @a[tag=df_deltaker] dodsfjellet:reisekompass",\n'),
]

ut = kilde
for gammel, ny in ERSTATT:
    if gammel not in ut:
        raise SystemExit(f"FANT IKKE:\n{gammel}")
    ut = ut.replace(gammel, ny)

# Skatten: Dødsnøkkelen (åpner Dødsriket) og et oppgradert våpen fra Dødsriket
ut = ut.replace('    item(22, "nether_star", 1, navn("Beviset: du overlevde", "light_purple")),\n]',
                '    item(22, "nether_star", 1, navn("Beviset: du overlevde", "light_purple")),\n'
                '    \'{Slot:21b,id:"dodsfjellet:dodsnokkel",count:1}\',\n'
                '    \'{Slot:23b,id:"dodsfjellet:dodskrystall",count:32}\',\n]')
assert "dodsfjellet:dodsnokkel" in ut

(HER / "generer_dodsfjellet_26.py").write_text(ut, encoding="utf-8")
print("generer_dodsfjellet_26.py skrevet")
