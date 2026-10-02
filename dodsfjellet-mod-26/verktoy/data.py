"""Genererer alle JSON-ressurser og data for Dødsfjellet-modden (Minecraft 26.3, datapack-format 121).

assets: blockstates, block-/item-modeller, item-definisjoner (3D i hånda, ikon i GUI), rustningsutseende, språk
data:   loot, tagger, oppskrifter, Dødsriket-dimensjonen (biomer, terreng, features), PvP-dimensjonen
Strukturene (NBT) lages av strukturer.py.
Kjør:  python verktoy/data.py
"""
import json
import shutil
from pathlib import Path

HER = Path(__file__).resolve().parent.parent
RES = HER / "src" / "main" / "resources"
A = RES / "assets" / "dodsfjellet"
D = RES / "data" / "dodsfjellet"
MC = RES / "data" / "minecraft"
NS = "dodsfjellet"


def skriv(sti: Path, data):
    sti.parent.mkdir(parents=True, exist_ok=True)
    sti.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def m(navn):
    return f"{NS}:{navn}"


# =========================================================================== blokker
ENKLE = ["dodsstein", "dodsstein_murstein", "polert_dodsstein", "askejord", "blodmose", "dodsved_planker",
         "sjeleglod", "dodskrystall_malm"]


def blokker():
    for b in ENKLE:
        skriv(A / "blockstates" / f"{b}.json", {"variants": {"": {"model": m(f"block/{b}")}}})
        skriv(A / "models" / "block" / f"{b}.json", {"parent": "minecraft:block/cube_all", "textures": {"all": m(f"block/{b}")}})
    # stamme (søyle)
    s = "dodsved_stamme"
    skriv(A / "blockstates" / f"{s}.json", {"variants": {
        "axis=x": {"model": m(f"block/{s}_horizontal"), "x": 90, "y": 90},
        "axis=y": {"model": m(f"block/{s}")},
        "axis=z": {"model": m(f"block/{s}_horizontal"), "x": 90}}})
    tex = {"end": m(f"block/{s}_topp"), "side": m(f"block/{s}")}
    skriv(A / "models" / "block" / f"{s}.json", {"parent": "minecraft:block/cube_column", "textures": tex})
    skriv(A / "models" / "block" / f"{s}_horizontal.json", {"parent": "minecraft:block/cube_column_horizontal", "textures": tex})
    # smia
    o = "oppgraderingssmie"
    skriv(A / "blockstates" / f"{o}.json", {"variants": {"": {"model": m(f"block/{o}")}}})
    skriv(A / "models" / "block" / f"{o}.json", {"parent": "minecraft:block/cube_bottom_top", "textures": {
        "top": m(f"block/{o}_topp"), "bottom": m(f"block/{o}_bunn"), "side": m(f"block/{o}_side")}})

    # lyskorset: loddrett bjelke + tverrbjelke med lysende kjerne, dreid etter retningen
    k = "lyskors"
    skriv(A / "blockstates" / f"{k}.json", {"variants": {
        f"facing={f}": {"model": m(f"block/{k}"), "y": y} for f, y in (("north", 0), ("east", 90), ("south", 180), ("west", 270))}})
    gull, kjerne = "#g", "#k"

    def el(fra, til, t, lys=0):
        e = {"from": fra, "to": til, "faces": {f: {"texture": t} for f in ("north", "south", "east", "west", "up", "down")}}
        if lys:
            e["light_emission"] = lys
        return e
    skriv(A / "models" / "block" / f"{k}.json", {
        "parent": "minecraft:block/block", "ambientocclusion": False,
        "textures": {"g": m(f"block/{k}"), "k": m(f"block/{k}_kjerne"), "particle": m(f"block/{k}")},
        "elements": [el([6.5, 0, 6.5], [9.5, 2, 9.5], gull), el([7, 2, 7], [9, 16, 9], gull),
                     el([3, 10, 7], [13, 12, 9], gull), el([7.4, 2.5, 6.9], [8.6, 15.5, 9.1], kjerne, 15),
                     el([3.5, 10.4, 6.9], [12.5, 11.6, 9.1], kjerne, 15)],
        "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, 0, 0], "scale": [0.8, 0.8, 0.8]},
                    "ground": {"rotation": [0, 0, 0], "translation": [0, 3, 0], "scale": [0.5, 0.5, 0.5]},
                    "fixed": {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [0.8, 0.8, 0.8]},
                    "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.375, 0.375, 0.375]},
                    "firstperson_righthand": {"rotation": [0, 45, 0], "translation": [0, 0, 0], "scale": [0.4, 0.4, 0.4]},
                    "firstperson_lefthand": {"rotation": [0, 225, 0], "translation": [0, 0, 0], "scale": [0.4, 0.4, 0.4]}}})

    alle = ENKLE + [s, o, k]
    for b in alle:
        skriv(A / "items" / f"{b}.json", {"model": {"type": "minecraft:model", "model": m(f"block/{b}")}})
        # loot: dropper seg selv, unntatt malmen
        if b == "dodskrystall_malm":
            loot = {"type": "minecraft:block", "random_sequence": m(f"blocks/{b}"), "pools": [{"rolls": 1, "entries": [{
                "type": "minecraft:alternatives", "children": [
                    {"type": "minecraft:item", "condition": "minecraft:tool/can_silk_touch", "name": m(b)},
                    {"type": "minecraft:item", "name": m("dodskrystall"), "modifier": [
                        {"type": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 1, "max": 3}},
                        {"type": "minecraft:apply_bonus", "enchantment": "minecraft:fortune",
                         "formula": "minecraft:ore_drops"},
                        {"type": "minecraft:explosion_decay"}]}]}]}]}
        else:
            loot = {"type": "minecraft:block", "random_sequence": m(f"blocks/{b}"), "pools": [{
                "rolls": 1, "condition": {"type": "minecraft:survives_explosion"},
                "entries": [{"type": "minecraft:item", "name": m(b)}]}]}
        skriv(D / "loot_table" / "blocks" / f"{b}.json", loot)

    stein = ["dodsstein", "dodsstein_murstein", "polert_dodsstein", "dodskrystall_malm", "oppgraderingssmie", "sjeleglod", "lyskors"]
    skriv(MC / "tags" / "block" / "mineable" / "pickaxe.json", {"replace": False, "values": [m(b) for b in stein]})
    skriv(MC / "tags" / "block" / "mineable" / "axe.json", {"replace": False, "values": [m("dodsved_stamme"), m("dodsved_planker")]})
    skriv(MC / "tags" / "block" / "mineable" / "shovel.json", {"replace": False, "values": [m("askejord"), m("blodmose")]})
    skriv(MC / "tags" / "block" / "needs_iron_tool.json", {"replace": False, "values": [m("dodskrystall_malm")]})
    for tag in ("overworld_carver_replaceables", "nether_carver_replaceables"):
        skriv(MC / "tags" / "block" / f"{tag}.json", {"replace": False, "values": [m("dodsstein"), m("askejord"), m("blodmose")]})
    skriv(D / "tags" / "item" / "dodskrystall_reparasjon.json", {"values": [m("dodskrystall")]})
    # skadetypen til geværene (eget tilbakeslag i GevaerItem, så ingen vanlig knockback)
    skriv(D / "damage_type" / "skudd.json", {"message_id": "dodsfjellet.skudd", "scaling": "when_caused_by_living_non_player",
                                             "exhaustion": 0.1})
    skriv(MC / "tags" / "damage_type" / "no_knockback.json", {"replace": False, "values": [m("skudd")]})
    skriv(MC / "tags" / "damage_type" / "is_projectile.json", {"replace": False, "values": [m("skudd")]})


# =========================================================================== gjenstander
FLATE = ["dodskrystall", "dodsnokkel", "reisekompass", "vakt_spawn_egg",
         "rune_skyggesprang", "rune_sjeleskjold", "rune_dodsnova", "rune_blodhost", "rune_andesprang", "rune_vokterkall"]
RUSTNING = [f"{sett}_{d}" for sett in ("fjellvokter", "sjeleplate") for d in ("hjelm", "brynje", "bukser", "stovler")]
VAAPEN_3D = ["sjelesigd", "dodsklinge", "vokterknuser"]
GEVAER = ["pistol", "hagle", "automatgevaer", "snikskyttergevaer"]   # 3D-modeller fra gevaer3d.py
FLATE += ["kuler", "haglpatroner", "bibel"]


def gjenstander():
    for i in FLATE + RUSTNING:
        skriv(A / "models" / "item" / f"{i}.json", {"parent": "minecraft:item/generated", "textures": {"layer0": m(f"item/{i}")}})
        skriv(A / "items" / f"{i}.json", {"model": {"type": "minecraft:model", "model": m(f"item/{i}")}})
    skriv(A / "models" / "item" / "skyggedolk.json", {"parent": "minecraft:item/handheld", "textures": {"layer0": m("item/skyggedolk")}})
    skriv(A / "items" / "skyggedolk.json", {"model": {"type": "minecraft:model", "model": m("item/skyggedolk")}})
    for v in VAAPEN_3D + GEVAER:
        # 2D-ikonet (rendret i Blender) i inventaret, 3D-modellen i hånda
        skriv(A / "models" / "item" / f"{v}.json", {"parent": "minecraft:item/generated", "textures": {"layer0": m(f"item/{v}")}})
        skriv(A / "items" / f"{v}.json", {"model": {
            "type": "minecraft:select", "property": "minecraft:display_context",
            "cases": [{"when": ["gui", "ground", "fixed", "on_shelf"], "model": {"type": "minecraft:model", "model": m(f"item/{v}")}}],
            "fallback": {"type": "minecraft:model", "model": m(f"item/{v}_3d")}}})
    for sett in ("fjellvokter", "sjeleplate"):
        skriv(A / "equipment" / f"{sett}.json", {"layers": {
            "humanoid": [{"texture": m(sett)}], "humanoid_leggings": [{"texture": m(sett)}]}})


SPRAAK = {
    "itemGroup.dodsfjellet": "Dødsfjellet",
    "block.dodsfjellet.dodsstein": "Dødsstein",
    "block.dodsfjellet.dodsstein_murstein": "Dødsstein-murstein",
    "block.dodsfjellet.polert_dodsstein": "Polert dødsstein",
    "block.dodsfjellet.askejord": "Askejord",
    "block.dodsfjellet.blodmose": "Blodmose",
    "block.dodsfjellet.dodsved_stamme": "Dødsved-stamme",
    "block.dodsfjellet.dodsved_planker": "Dødsved-planker",
    "block.dodsfjellet.sjeleglod": "Sjeleglød",
    "block.dodsfjellet.dodskrystall_malm": "Dødskrystall-malm",
    "block.dodsfjellet.oppgraderingssmie": "Oppgraderingssmie",
    "item.dodsfjellet.dodskrystall": "Dødskrystall",
    "item.dodsfjellet.dodsnokkel": "Dødsnøkkelen",
    "item.dodsfjellet.reisekompass": "Reisekompass",
    "item.dodsfjellet.skyggedolk": "Skyggedolken",
    "item.dodsfjellet.vokterknuser": "Vokterknuseren",
    "item.dodsfjellet.sjelesigd": "Sjelesigden",
    "item.dodsfjellet.dodsklinge": "Dødsklingen",
    "item.dodsfjellet.fjellvokter_hjelm": "Fjellvokter-hjelm",
    "item.dodsfjellet.fjellvokter_brynje": "Fjellvokter-brynje",
    "item.dodsfjellet.fjellvokter_bukser": "Fjellvokter-bukser",
    "item.dodsfjellet.fjellvokter_stovler": "Fjellvokter-støvler",
    "item.dodsfjellet.sjeleplate_hjelm": "Sjeleplate-hjelm",
    "item.dodsfjellet.sjeleplate_brynje": "Sjeleplate-brynje",
    "item.dodsfjellet.sjeleplate_bukser": "Sjeleplate-bukser",
    "item.dodsfjellet.sjeleplate_stovler": "Sjeleplate-støvler",
    "item.dodsfjellet.rune_skyggesprang": "Rune: Skyggesprang",
    "item.dodsfjellet.rune_sjeleskjold": "Rune: Sjeleskjold",
    "item.dodsfjellet.rune_dodsnova": "Rune: Dødsnova",
    "item.dodsfjellet.rune_blodhost": "Rune: Blodhøst",
    "item.dodsfjellet.rune_andesprang": "Rune: Åndesprang",
    "item.dodsfjellet.rune_vokterkall": "Rune: Vokterkall",
    "item.dodsfjellet.vakt_spawn_egg": "Vakt-egg",
    "item.dodsfjellet.bibel": "Bibelen",
    "block.dodsfjellet.lyskors": "Lyskors",
    "effect.dodsfjellet.glede": "Glede",
    "item.dodsfjellet.pistol": "Pistol",
    "item.dodsfjellet.hagle": "Pumpehagle",
    "item.dodsfjellet.automatgevaer": "Automatgevær",
    "item.dodsfjellet.snikskyttergevaer": "Snikskyttergevær",
    "item.dodsfjellet.kuler": "Kuler",
    "item.dodsfjellet.haglpatroner": "Haglpatroner",
    "death.attack.dodsfjellet.skudd": "%1$s ble skutt",
    "death.attack.dodsfjellet.skudd.player": "%1$s ble skutt av %2$s",
    "death.attack.dodsfjellet.skudd.item": "%1$s ble skutt av %2$s med %3$s",
    "subtitles.dodsfjellet.gevaer.pistol_skudd": "Pistolskudd",
    "subtitles.dodsfjellet.gevaer.hagle_skudd": "Haglskudd",
    "subtitles.dodsfjellet.gevaer.automatgevaer_skudd": "Automatild",
    "subtitles.dodsfjellet.gevaer.snikskyttergevaer_skudd": "Snikskytterskudd",
    "subtitles.dodsfjellet.gevaer.tom": "Tomt magasin",
    "subtitles.dodsfjellet.gevaer.omlad_pistol": "Lader om",
    "subtitles.dodsfjellet.gevaer.omlad_automat": "Lader om",
    "subtitles.dodsfjellet.gevaer.omlad_hagle": "Pumper",
    "subtitles.dodsfjellet.gevaer.omlad_snikskytter": "Bolt",
    "subtitles.dodsfjellet.gevaer.pumpe": "Pumper",
    "entity.dodsfjellet.vakt": "Vakt",
    "effect.dodsfjellet.blodhost": "Blodhøst",
    "biome.dodsfjellet.askeodet": "Askeødet",
    "biome.dodsfjellet.dodsskogen": "Dødsskogen",
    "biome.dodsfjellet.krystallmarkene": "Krystallmarkene",
    "biome.dodsfjellet.blodmyra": "Blodmyra",
    "biome.dodsfjellet.dodsgrotta": "Dødsgrotta",
}


def spraak():
    for lang in ("en_us", "nb_no", "no_no", "nn_no"):
        skriv(A / "lang" / f"{lang}.json", SPRAAK)


# =========================================================================== oppskrifter
def oppskrifter():
    r = D / "recipe"
    skriv(r / "dodsved_planker.json", {"type": "minecraft:crafting_shapeless", "category": "building",
                                       "ingredients": [m("dodsved_stamme")], "result": {"count": 4, "id": m("dodsved_planker")}})
    skriv(r / "dodsstein_murstein.json", {"type": "minecraft:crafting_shaped", "category": "building",
                                          "key": {"#": m("dodsstein")}, "pattern": ["##", "##"],
                                          "result": {"count": 4, "id": m("dodsstein_murstein")}})
    skriv(r / "polert_dodsstein.json", {"type": "minecraft:crafting_shaped", "category": "building",
                                        "key": {"#": m("dodsstein_murstein")}, "pattern": ["##", "##"],
                                        "result": {"count": 4, "id": m("polert_dodsstein")}})
    skriv(r / "sjeleglod.json", {"type": "minecraft:crafting_shaped", "category": "building",
                                 "key": {"#": m("dodskrystall"), "s": "minecraft:soul_sand"}, "pattern": ["#s#", "s#s", "#s#"],
                                 "result": {"count": 4, "id": m("sjeleglod")}})
    skriv(r / "oppgraderingssmie.json", {"type": "minecraft:crafting_shaped", "category": "misc",
                                         "key": {"#": m("dodsstein_murstein"), "k": m("dodskrystall"), "a": "minecraft:anvil"},
                                         "pattern": ["kkk", "#a#", "###"], "result": {"id": m("oppgraderingssmie")}})
    skriv(r / "reisekompass.json", {"type": "minecraft:crafting_shaped", "category": "misc",
                                    "key": {"k": m("dodskrystall"), "c": "minecraft:compass"}, "pattern": [" k ", "kck", " k "],
                                    "result": {"id": m("reisekompass")}})
    skriv(r / "dodsnokkel.json", {"type": "minecraft:crafting_shaped", "category": "misc",
                                  "key": {"k": m("dodskrystall"), "b": "minecraft:bone", "g": "minecraft:gold_ingot"},
                                  "pattern": ["kgk", " b ", " b "], "result": {"id": m("dodsnokkel")}})
    for sett, kjerne in (("sjeleplate", "minecraft:netherite_ingot"),):
        for del_, monster in (("hjelm", ["kKk", "k k"]), ("brynje", ["k k", "kKk", "kkk"]),
                              ("bukser", ["kKk", "k k", "k k"]), ("stovler", ["k k", "K K"])):
            skriv(r / f"{sett}_{del_}.json", {"type": "minecraft:crafting_shaped", "category": "equipment",
                                             "key": {"k": m("dodskrystall"), "K": kjerne}, "pattern": monster,
                                             "result": {"id": m(f"{sett}_{del_}")}})
    # glede
    skriv(r / "bibel.json", {"type": "minecraft:crafting_shapeless", "category": "misc",
                             "ingredients": ["minecraft:book", "minecraft:gold_ingot"], "result": {"id": m("bibel")}})
    skriv(r / "lyskors.json", {"type": "minecraft:crafting_shaped", "category": "building",
                               "key": {"g": "minecraft:gold_ingot", "l": "minecraft:glowstone_dust"},
                               "pattern": [" g ", "glg", " g "], "result": {"count": 2, "id": m("lyskors")}})
    # gevær og ammunisjon
    skriv(r / "kuler.json", {"type": "minecraft:crafting_shapeless", "category": "equipment",
                             "ingredients": ["minecraft:copper_ingot", "minecraft:gunpowder", "minecraft:iron_nugget"],
                             "result": {"count": 16, "id": m("kuler")}})
    skriv(r / "haglpatroner.json", {"type": "minecraft:crafting_shapeless", "category": "equipment",
                                    "ingredients": ["minecraft:paper", "minecraft:gunpowder", "minecraft:iron_nugget", "minecraft:copper_ingot"],
                                    "result": {"count": 8, "id": m("haglpatroner")}})
    for v, monster, key in (
            ("pistol", ["iii", " gk", "  i"], {"i": "minecraft:iron_ingot", "g": "minecraft:gunpowder", "k": m("dodskrystall")}),
            ("hagle", ["iii", "  t", "  w"], {"i": "minecraft:iron_ingot", "t": "minecraft:tripwire_hook", "w": "#minecraft:planks"}),
            ("automatgevaer", ["iii", "kgt", " iw"], {"i": "minecraft:iron_ingot", "g": "minecraft:gunpowder", "k": m("dodskrystall"),
                                                      "t": "minecraft:tripwire_hook", "w": "#minecraft:planks"}),
            ("snikskyttergevaer", ["ssi", "iki", "ddi"], {"i": "minecraft:iron_ingot", "s": "minecraft:spyglass", "k": m("dodskrystall"),
                                                          "d": "minecraft:diamond"})):
        skriv(r / f"{v}.json", {"type": "minecraft:crafting_shaped", "category": "equipment", "key": key, "pattern": monster,
                                "result": {"id": m(v)}})
    for v, kjerne in (("sjelesigd", "minecraft:netherite_hoe"), ("dodsklinge", "minecraft:netherite_sword")):
        skriv(r / f"{v}.json", {"type": "minecraft:crafting_shaped", "category": "equipment",
                                "key": {"k": m("dodskrystall"), "v": kjerne, "s": m("sjeleglod")},
                                "pattern": ["ksk", "kvk", "ksk"], "result": {"id": m(v)}})


# =========================================================================== Dødsriket
FARGER = {   # biom: (tåke, himmel, vann, gress/løv, partikkel, sannsynlighet)
    "askeodet": ("#2a1d33", "#1c1026", "#3a1030", "#4a3a44", "minecraft:white_ash", 0.035),
    "dodsskogen": ("#1d1426", "#140b1d", "#2a0f3a", "#3a2a3a", "minecraft:ash", 0.02),
    "krystallmarkene": ("#2a1f4f", "#1a1240", "#3f1a8f", "#6a4aa0", "minecraft:reverse_portal", 0.012),
    "blodmyra": ("#3a0a12", "#24060c", "#6e0a14", "#5a1a20", "minecraft:crimson_spore", 0.03),
    "dodsgrotta": ("#120a18", "#0a0610", "#1a0a20", "#2a1a2a", "minecraft:soul", 0.004),
}


def dodsriket():
    skriv(D / "dimension_type" / "dodsriket.json", {
        "has_fixed_time": True, "has_skylight": True, "has_ceiling": False, "has_ender_dragon_fight": False,
        "coordinate_scale": 1.0, "min_y": -64, "height": 384, "logical_height": 384,
        "infiniburn": "#minecraft:infiniburn_overworld", "ambient_light": 0.14,
        "monster_spawn_light_level": {"type": "minecraft:uniform", "min_inclusive": 0, "max_inclusive": 7},
        "monster_spawn_block_light_limit": 0, "skybox": "overworld", "cardinal_light": "default",
        "timelines": [],
        "attributes": {
            "minecraft:visual/sky_color": "#3a1f55",
            "minecraft:visual/fog_color": "#4a2a5e",
            "minecraft:visual/fog_start_distance": 6.0,
            "minecraft:visual/fog_end_distance": 150.0,
            "minecraft:visual/sky_fog_end_distance": 140.0,
            "minecraft:visual/sun_angle": 92.0,
            "minecraft:visual/moon_angle": 300.0,
            "minecraft:visual/moon_phase": "full_moon",
            "minecraft:visual/sunrise_sunset_color": "#aab0204e",
            "minecraft:visual/star_brightness": 0.45,
            "minecraft:visual/sky_light_color": "#8a5cc2",
            "minecraft:visual/sky_light_factor": 0.7,
            "minecraft:visual/ambient_light_color": "#241430",
            "minecraft:visual/block_light_tint": "#ffd0f0",
            "minecraft:gameplay/sky_light_level": 10.0,
            "minecraft:audio/background_music": {"default": {"sound": "minecraft:music.nether.soul_sand_valley",
                                                             "min_delay": 6000, "max_delay": 18000}},
            "minecraft:gameplay/bed_rule": {"can_set_spawn": "never", "can_sleep": "never", "destroy_on_use": True},
            "minecraft:gameplay/respawn_anchor_works": True,
            "minecraft:gameplay/can_start_raid": False,
            "minecraft:gameplay/monsters_burn": False,
        }})

    # terreng: oververdenens form, men dødsstein, askejord og lavahav
    ow = json.loads((Path(r"D:\mc-data-26.3\data\minecraft\worldgen\noise_settings\overworld.json")).read_text())
    ow["default_block"] = m("dodsstein")
    ow["default_fluid"] = {"id": "minecraft:lava", "properties": {"level": "0"}}
    ow["sea_level"] = 44
    ow["material_rule"] = m("dodsriket")
    ow.pop("debug_functions", None)
    skriv(D / "worldgen" / "noise_settings" / "dodsriket.json", ow)

    def blokk(b):
        return {"type": "minecraft:block", "result_state": b}

    def biom_er(*b):
        return {"type": "minecraft:biome", "biome_is": [m(x) for x in b]}

    overflate = {"type": "minecraft:sequence", "sequence": [
        {"type": "minecraft:condition", "if_true": biom_er("blodmyra"), "then_run": {"type": "minecraft:sequence", "sequence": [
            {"type": "minecraft:condition", "if_true": "minecraft:on_floor", "then_run": blokk(m("blodmose"))},
            {"type": "minecraft:condition", "if_true": "minecraft:under_floor", "then_run": blokk(m("askejord"))}]}},
        {"type": "minecraft:condition", "if_true": biom_er("krystallmarkene"), "then_run": {"type": "minecraft:sequence", "sequence": [
            {"type": "minecraft:condition", "if_true": "minecraft:on_floor", "then_run": blokk(m("polert_dodsstein"))}]}},
        {"type": "minecraft:condition", "if_true": "minecraft:on_floor", "then_run": blokk(m("askejord"))},
        {"type": "minecraft:condition", "if_true": "minecraft:under_floor", "then_run": blokk(m("askejord"))},
    ]}
    skriv(D / "worldgen" / "material_rule" / "dodsriket.json", {"type": "minecraft:sequence", "sequence": [
        "minecraft:bedrock_floor",
        {"type": "minecraft:condition", "if_true": {"type": "minecraft:above_preliminary_surface"}, "then_run": overflate},
        {"type": "minecraft:condition", "if_true": {"type": "minecraft:not", "invert": {"type": "minecraft:y_above",
                                                                                        "anchor": {"absolute": 0}, "surface_depth_multiplier": 0, "add_stone_depth": False}},
         "then_run": blokk("minecraft:deepslate")},
    ]})

    # features
    f = D / "worldgen" / "feature"
    pf = D / "worldgen" / "placed_feature"
    skriv(f / "dodskrystall_malm.json", {"type": "minecraft:ore", "discard_chance_on_air_exposure": 0.0, "size": 7, "targets": [
        {"state": m("dodskrystall_malm"), "target": {"predicate_type": "minecraft:block_match", "block": m("dodsstein")}},
        {"state": m("dodskrystall_malm"), "target": {"predicate_type": "minecraft:block_match", "block": "minecraft:deepslate"}}]})
    skriv(pf / "dodskrystall_malm.json", {"feature": m("dodskrystall_malm"), "placement": [
        {"type": "minecraft:count", "count": 14}, {"type": "minecraft:in_square"},
        {"type": "minecraft:height_range", "height": {"type": "minecraft:trapezoid", "min_inclusive": {"above_bottom": 0},
                                                      "max_inclusive": {"absolute": 90}}},
        {"type": "minecraft:biome"}]})

    def soyle(navn, blokk_, hoyde):
        skriv(f / f"{navn}.json", {"type": "minecraft:block_column", "allowed_placement": {"type": "minecraft:matching_block_tag", "tag": "minecraft:air"},
                                   "direction": "up", "prioritize_tip": False, "layers": [
            {"height": {"type": "minecraft:uniform", "min_inclusive": hoyde[0], "max_inclusive": hoyde[1]},
             "provider": blokk_}]})

    soyle("dod_stamme", {"id": m("dodsved_stamme"), "properties": {"axis": "y"}}, (3, 8))
    soyle("sjelekrystall", {"id": m("sjeleglod")}, (1, 4))
    skriv(f / "blodmose_flekk.json", {"type": "minecraft:simple_block", "to_place": {"id": m("blodmose")}})
    skriv(f / "sjelebal.json", {"type": "minecraft:simple_block", "to_place": {"id": "minecraft:soul_fire"}})

    def plassert(navn, feature, antall, gulv, flekk=False):
        p = [{"type": "minecraft:count", "count": antall}, {"type": "minecraft:in_square"},
             {"type": "minecraft:heightmap", "heightmap": "MOTION_BLOCKING_NO_LEAVES"}]
        if flekk:
            p += [{"type": "minecraft:count", "count": 24},
                  {"type": "minecraft:offset", "x": {"type": "minecraft:trapezoid", "min": -6, "max": 6, "plateau": 0},
                   "y": {"type": "minecraft:trapezoid", "min": -2, "max": 2, "plateau": 0},
                   "z": {"type": "minecraft:trapezoid", "min": -6, "max": 6, "plateau": 0}}]
        p += [{"type": "minecraft:block_predicate_filter", "predicate": {"type": "minecraft:all_of", "predicates": [
            {"type": "minecraft:matching_blocks", "blocks": "minecraft:air"},
            {"type": "minecraft:matching_blocks", "blocks": gulv, "offset": [0, -1, 0]}]}},
              {"type": "minecraft:biome"}]
        skriv(pf / f"{navn}.json", {"feature": m(feature), "placement": p})

    plassert("dode_traer", "dod_stamme", {"type": "minecraft:uniform", "min_inclusive": 3, "max_inclusive": 8},
             [m("askejord"), m("blodmose")])
    plassert("spredte_stammer", "dod_stamme", {"type": "minecraft:uniform", "min_inclusive": 0, "max_inclusive": 1},
             [m("askejord")])
    plassert("sjelekrystaller", "sjelekrystall", {"type": "minecraft:uniform", "min_inclusive": 4, "max_inclusive": 10},
             [m("polert_dodsstein"), m("askejord")])
    plassert("sjelekrystaller_spredt", "sjelekrystall", {"type": "minecraft:uniform", "min_inclusive": 0, "max_inclusive": 1},
             [m("askejord"), m("blodmose")])
    plassert("sjeleild", "sjelebal", {"type": "minecraft:uniform", "min_inclusive": 0, "max_inclusive": 2},
             ["minecraft:soul_sand", m("askejord")], flekk=False)

    # biomer
    def biom(navn, features9, monstre, has_precip=False):
        taake, himmel, vann, gress, partikkel, sanns = FARGER[navn]
        skriv(D / "worldgen" / "biome" / f"{navn}.json", {
            "has_precipitation": has_precip, "temperature": 1.2, "downfall": 0.0,
            "attributes": {
                "minecraft:visual/fog_color": taake,
                "minecraft:visual/sky_color": himmel,
                "minecraft:visual/water_fog_color": vann,
                "minecraft:visual/ambient_particles": {"modifier": "append", "argument": [
                    {"particle": {"type": partikkel}, "probability": sanns}]},
                "minecraft:audio/ambient_sounds": {"mood": {"block_search_extent": 8, "offset": 2.0,
                                                            "sound": "minecraft:ambient.soul_sand_valley.mood", "tick_delay": 6000},
                                                   "additions": {"sound": "minecraft:ambient.soul_sand_valley.additions", "tick_chance": 0.0111}},
                "minecraft:gameplay/natural_mob_spawns": {"modifier": "overlay", "argument": {
                    "spawn_costs": {}, "spawns_by_category": {"monster": monstre}}},
            },
            "effects": {"water_color": vann, "grass_color": gress, "foliage_color": gress},
            "carvers": ["minecraft:cave", "minecraft:cave_extra_underground", "minecraft:canyon"],
            "features": [[], [], [], [], [], [], [m("dodskrystall_malm")], [], [], features9, []],
        })

    vakt = {"type": m("vakt"), "count": 1, "weight": 6}
    biom("askeodet", [m("spredte_stammer"), m("sjelekrystaller_spredt"), m("sjeleild")],
         [{"type": "minecraft:skeleton", "count": 3, "weight": 60}, {"type": "minecraft:husk", "count": 3, "weight": 40}, vakt])
    biom("dodsskogen", [m("dode_traer"), m("sjelekrystaller_spredt")],
         [{"type": "minecraft:wither_skeleton", "count": 2, "weight": 30}, {"type": "minecraft:skeleton", "count": 3, "weight": 40}, vakt])
    biom("krystallmarkene", [m("sjelekrystaller")],
         [{"type": "minecraft:enderman", "count": 2, "weight": 40}, {"type": "minecraft:vex", "count": 2, "weight": 10}, vakt])
    biom("blodmyra", [m("spredte_stammer"), m("sjelekrystaller_spredt")],
         [{"type": "minecraft:bogged", "count": 3, "weight": 50}, {"type": "minecraft:zombie", "count": 3, "weight": 40}, vakt])
    biom("dodsgrotta", [m("sjelekrystaller_spredt")],
         [{"type": "minecraft:skeleton", "count": 3, "weight": 50}, {"type": "minecraft:cave_spider", "count": 2, "weight": 30},
          {"type": m("vakt"), "count": 1, "weight": 10}])

    def p(t, h, c, e, d, w):
        return {"temperature": t, "humidity": h, "continentalness": c, "erosion": e, "depth": d, "weirdness": w, "offset": 0.0}

    skriv(D / "dimension" / "dodsriket.json", {"type": m("dodsriket"), "generator": {
        "type": "minecraft:noise", "settings": m("dodsriket"), "biome_source": {"type": "minecraft:multi_noise", "biomes": [
            {"biome": m("askeodet"), "parameters": p([-1.0, 0.2], [-1.0, -0.1], [-0.2, 1.0], [-1.0, 1.0], 0.0, [-1.0, 1.0])},
            {"biome": m("dodsskogen"), "parameters": p([-1.0, 1.0], [0.1, 1.0], [-0.1, 1.0], [-1.0, 0.5], 0.0, [-1.0, 0.5])},
            {"biome": m("krystallmarkene"), "parameters": p([0.2, 1.0], [-1.0, 0.1], [0.0, 1.0], [-1.0, 0.0], 0.0, [0.3, 1.0])},
            {"biome": m("blodmyra"), "parameters": p([-1.0, 1.0], [-1.0, 1.0], [-1.2, -0.2], [0.0, 1.0], 0.0, [-1.0, 1.0])},
            {"biome": m("dodsgrotta"), "parameters": p([-1.0, 1.0], [-1.0, 1.0], [-1.2, 1.0], [-1.0, 1.0], [0.25, 1.0], [-1.0, 1.0])},
        ]}}})


# =========================================================================== PvP-dimensjonen (tom himmelverden)
def pvp():
    skriv(D / "dimension_type" / "pvp.json", {
        "has_fixed_time": True, "has_skylight": True, "has_ceiling": False, "has_ender_dragon_fight": False,
        "coordinate_scale": 1.0, "min_y": 0, "height": 256, "logical_height": 256,
        "infiniburn": "#minecraft:infiniburn_overworld", "ambient_light": 0.4,
        "monster_spawn_light_level": 0, "monster_spawn_block_light_limit": 0,
        "skybox": "overworld", "cardinal_light": "default", "timelines": [],
        "attributes": {
            "minecraft:visual/sky_color": "#3a2a5a",
            "minecraft:visual/fog_color": "#4a3466",
            "minecraft:visual/fog_start_distance": 60.0,
            "minecraft:visual/fog_end_distance": 260.0,
            "minecraft:visual/sun_angle": 75.0,
            "minecraft:visual/sunrise_sunset_color": "#88d0406e",
            "minecraft:visual/star_brightness": 0.3,
            "minecraft:visual/sky_light_color": "#d8c0ff",
            "minecraft:visual/cloud_color": "#66b090d0",
            "minecraft:visual/cloud_height": 140.0,
            "minecraft:gameplay/sky_light_level": 15.0,
            "minecraft:gameplay/bed_rule": {"can_set_spawn": "never", "can_sleep": "never", "destroy_on_use": False},
        }})
    skriv(D / "dimension" / "pvp.json", {"type": m("pvp"), "generator": {"type": "minecraft:flat", "settings": {
        "biome": "minecraft:the_void", "features": False, "lakes": False,
        "layers": [{"block": "minecraft:air", "height": 1}], "structure_overrides": []}}})


def main():
    for d in (A / "blockstates", A / "models", A / "items", A / "equipment", A / "lang", D):
        if d.exists():
            shutil.rmtree(d)
    if MC.exists():
        shutil.rmtree(MC)
    blokker()
    gjenstander()
    spraak()
    oppskrifter()
    dodsriket()
    pvp()
    n = sum(1 for _ in RES.rglob("*.json"))
    print(f"{n} JSON-filer skrevet")


if __name__ == "__main__":
    main()
