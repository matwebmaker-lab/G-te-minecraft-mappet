"""Blender-skript (kjøres i Blender 5.x, f.eks. via Blender MCP): bygger 3D-våpnene fra verktoy/vaapen3d.json
og rendrer diagonale ikoner (256 px, gjennomsiktig bakgrunn) til verktoy/ikoner/.

Etterpå lager ekstra_teksturer.py 32x32-ikonene som brukes i inventaret.
"""
import json
import math
from pathlib import Path

import bpy
import mathutils

HER = Path(r"D:\Projects\minecraft mods\claude lag en trap i minecraft\dodsfjellet-mod-26\verktoy")
data = json.loads((HER / "vaapen3d.json").read_text())

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
scene = bpy.context.scene


def materiale(farge, lys):
    navn = "m_%d_%d_%d_%d" % (int(farge[0] * 255), int(farge[1] * 255), int(farge[2] * 255), lys)
    m = bpy.data.materials.get(navn)
    if m:
        return m
    m = bpy.data.materials.new(navn)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*farge, 1)
    b.inputs["Roughness"].default_value = 0.6
    if lys:
        b.inputs["Emission Color"].default_value = (*farge, 1)
        b.inputs["Emission Strength"].default_value = 4.0
    return m


offset = {"sjelesigd": -30, "dodsklinge": 0, "vokterknuser": 30}
for navn, bokser in data.items():
    for i, b in enumerate(bokser):
        f, t = b["from"], b["to"]
        bpy.ops.mesh.primitive_cube_add(size=1)
        o = bpy.context.active_object
        o.name = f"{navn}_{i}"
        o.scale = (t[0] - f[0], t[2] - f[2], t[1] - f[1])                       # Minecraft y opp -> Blender z opp
        o.location = ((f[0] + t[0]) / 2 - 8 + offset[navn], (f[2] + t[2]) / 2 - 8, (f[1] + t[1]) / 2)
        o.data.materials.append(materiale(b["farge"], b["lys"]))

bpy.ops.object.camera_add(location=(0, -90, 12), rotation=(math.radians(90), 0, 0))
cam = bpy.context.active_object
cam.data.type = "ORTHO"
scene.camera = cam
bpy.ops.object.light_add(type="SUN", location=(10, -20, 40))
sol = bpy.context.active_object
sol.data.energy = 1.8
sol.rotation_euler = (math.radians(55), math.radians(15), math.radians(-25))
scene.view_settings.view_transform = "Standard"
scene.render.film_transparent = True
scene.render.resolution_x = scene.render.resolution_y = 256

for navn in offset:
    objs = [o for o in bpy.data.objects if o.name.startswith(navn + "_")]
    for o in bpy.data.objects:
        if o.type == "MESH":
            o.hide_render = o not in objs
    pts = [o.matrix_world @ mathutils.Vector(v) for o in objs for v in o.bound_box]
    mnx, mxx = min(p.x for p in pts), max(p.x for p in pts)
    mnz, mxz = min(p.z for p in pts), max(p.z for p in pts)
    cam.location = ((mnx + mxx) / 2, -90, (mnz + mxz) / 2)
    cam.rotation_euler = (math.radians(90), math.radians(-45), 0)        # diagonalt, som vanilla-sverd
    cam.data.ortho_scale = ((mxx - mnx) + (mxz - mnz)) / math.sqrt(2) * 1.04
    scene.render.filepath = str(HER / "ikoner" / f"ikon_{navn}.png")
    bpy.ops.render.render(write_still=True)
