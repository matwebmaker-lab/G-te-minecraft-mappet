"""Blender-skript (Blender 5.x, kjøres via Blender MCP): bygger geværene fra verktoy/gevaer3d.json med
avrundede kanter og fysiske materialer (metall, tre, polymer), og rendrer ikoner med gjennomsiktig bakgrunn
til verktoy/ikoner/ikon_<navn>.png. Etterpå lager ekstra_teksturer.py inventar-ikonene av dem.

Koordinater: Minecraft (x, y, z) -> Blender (x, -z, y), en ekte rotasjon, så elementrotasjonene blir like.
"""
import json
import math
from pathlib import Path

import bpy
import mathutils

HER = Path(r"D:\Projects\minecraft mods\claude lag en trap i minecraft\dodsfjellet-mod-26\verktoy")
data = json.loads((HER / "gevaer3d.json").read_text())
SAMPLES = 96
OPPLOSNING = 512

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.materials):
    if m.name.startswith("gv_"):
        bpy.data.materials.remove(m)
scene = bpy.context.scene


def materiale(navn, d):
    m = bpy.data.materials.new("gv_" + navn)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*[c ** 2.2 for c in d["farge"]], 1)
    bsdf.inputs["Metallic"].default_value = d["metall"]
    bsdf.inputs["Roughness"].default_value = d["ruhet"]
    if d["lys"]:
        bsdf.inputs["Emission Color"].default_value = (*[c ** 2.2 for c in d["farge"]], 1)
        bsdf.inputs["Emission Strength"].default_value = d["lys"] / 3
    # litt støy i ruheten og fargen så overflatene ikke ser plastiske ut
    stoy = nt.nodes.new("ShaderNodeTexNoise")
    stoy.inputs["Scale"].default_value = 18.0 if navn not in ("tre", "tre_mork") else 3.0
    if navn in ("tre", "tre_mork"):             # årer langs løpet (Blender Y)
        stoy.inputs["Detail"].default_value = 6
        stoy.inputs["Distortion"].default_value = 2.5
        koord = nt.nodes.new("ShaderNodeTexCoord")
        kart = nt.nodes.new("ShaderNodeMapping")
        kart.inputs["Scale"].default_value = (5.0, 0.35, 5.0)
        nt.links.new(koord.outputs["Object"], kart.inputs["Vector"])
        nt.links.new(kart.outputs["Vector"], stoy.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeMapRange")
    ramp.inputs["To Min"].default_value = d["ruhet"] * 0.8
    ramp.inputs["To Max"].default_value = min(1.0, d["ruhet"] * 1.25)
    nt.links.new(stoy.outputs["Fac"], ramp.inputs["Value"])
    nt.links.new(ramp.outputs["Result"], bsdf.inputs["Roughness"])
    if navn in ("tre", "tre_mork", "bakelitt"):
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.inputs["A"].default_value = (*[(c * 0.55) ** 2.2 for c in d["farge"]], 1)
        mix.inputs["B"].default_value = (*[min(1, c * 1.2) ** 2.2 for c in d["farge"]], 1)
        nt.links.new(stoy.outputs["Fac"], mix.inputs["Factor"])
        nt.links.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
    return m


MATERIALER = {n: materiale(n, d) for n, d in data["materialer"].items()}


def bygg(navn, bokser):
    deler = []
    for i, e in enumerate(bokser):
        f, t = e["from"], e["to"]
        bpy.ops.mesh.primitive_cube_add(size=1)
        o = bpy.context.active_object
        o.name = f"{navn}_{i}"
        o.scale = (t[0] - f[0], t[2] - f[2], t[1] - f[1])
        o.location = ((f[0] + t[0]) / 2, -(f[2] + t[2]) / 2, (f[1] + t[1]) / 2)
        o.data.materials.append(MATERIALER[e["mat"]])
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        if "rot" in e:
            r = e["rot"]
            ox, oy, oz = r["origin"]
            piv = mathutils.Vector((ox, -oz, oy))
            akse = {"x": (1, 0, 0), "y": (0, 0, 1), "z": (0, -1, 0)}[r["axis"]]
            M = (mathutils.Matrix.Translation(piv) @ mathutils.Matrix.Rotation(math.radians(r["angle"]), 4, akse)
                 @ mathutils.Matrix.Translation(-piv))
            o.matrix_world = M @ o.matrix_world
        minst = min(t[0] - f[0], t[1] - f[1], t[2] - f[2])
        if minst > 0.12:
            bev = o.modifiers.new("kant", "BEVEL")
            bev.width = min(0.12, minst * 0.18)
            bev.segments = 2
        deler.append(o)
    return deler


ALLE = {navn: bygg(navn, bokser) for navn, bokser in data["modeller"].items()}

# lys og kamera
bpy.ops.object.light_add(type="AREA", location=(40, -20, 40))
nokkel = bpy.context.active_object
nokkel.data.energy = 60000
nokkel.data.size = 30
nokkel.rotation_euler = (math.radians(40), math.radians(35), math.radians(30))
bpy.ops.object.light_add(type="AREA", location=(-30, 10, 25))
fyll = bpy.context.active_object
fyll.data.energy = 15000
fyll.data.size = 40
fyll.rotation_euler = (math.radians(-40), math.radians(-40), 0)
bpy.ops.object.light_add(type="AREA", location=(0, 40, 5))
kant = bpy.context.active_object
kant.data.energy = 25000
kant.data.size = 20
kant.rotation_euler = (math.radians(-90), 0, 0)

verden = scene.world or bpy.data.worlds.new("Verden")
scene.world = verden
verden.use_nodes = True
verden.node_tree.nodes["Background"].inputs["Color"].default_value = (0.35, 0.36, 0.4, 1)
verden.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6

bpy.ops.object.camera_add()
cam = bpy.context.active_object
cam.data.type = "ORTHO"
scene.camera = cam
scene.render.engine = "CYCLES"
scene.cycles.samples = SAMPLES
scene.cycles.use_denoising = True
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.render.film_transparent = True
scene.render.resolution_x = scene.render.resolution_y = OPPLOSNING

VINKEL = 28   # ikonet: munningen opp mot høyre


def render(navn, sti):
    for n, deler in ALLE.items():
        for o in deler:
            o.hide_render = n != navn
    deler = ALLE[navn]
    # kamera fra høyre side (Minecraft øst = Blender +X), litt ovenfra og forfra, rullet så våpenet ligger på skrå
    ammo = navn in ("kuler", "haglpatroner")
    retning = mathutils.Vector((1.0, -0.5, 0.35) if ammo else (1.0, -0.18, 0.22)).normalized()
    pts = [o.matrix_world @ mathutils.Vector(v) for o in deler for v in o.bound_box]
    midt = sum(pts, mathutils.Vector()) / len(pts)
    cam.location = midt + retning * 120
    rot = (-retning).to_track_quat("-Z", "Z")
    rull = mathutils.Quaternion((-retning), math.radians(-12 if ammo else -VINKEL))
    cam.rotation_mode = "QUATERNION"
    cam.rotation_quaternion = rull @ rot
    bpy.context.view_layer.update()
    inv = cam.matrix_world.inverted()
    lok = [inv @ p for p in pts]
    bredde = max(p.x for p in lok) - min(p.x for p in lok)
    hoyde = max(p.y for p in lok) - min(p.y for p in lok)
    cx = (max(p.x for p in lok) + min(p.x for p in lok)) / 2
    cy = (max(p.y for p in lok) + min(p.y for p in lok)) / 2
    cam.location = cam.matrix_world @ mathutils.Vector((cx, cy, 0))
    cam.data.ortho_scale = max(bredde, hoyde) * 1.06
    scene.render.filepath = str(sti)
    bpy.ops.render.render(write_still=True)


for navn in ALLE:
    render(navn, HER / "ikoner" / f"ikon_{navn}.png")
