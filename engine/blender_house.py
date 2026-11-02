"""Trusted Ferrari demonstration: create a simple conceptual house in Blender.

This makes a design visualization, NOT a structural or permit-ready building project.
Used only by blender --background --factory-startup; no user-provided Python executed.
"""
import math
from pathlib import Path
import sys
import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
if len(args) != 2:
    raise SystemExit("Expected output dir and title")
out = Path(args[0]).resolve()
out.mkdir(parents=True, exist_ok=True)
title = args[1][:100]

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 8
# Ubuntu Blender 4.0.2 builds may omit OpenImageDenoiser, so explicitly disable it.
for layer in scene.view_layers:
    if hasattr(layer, "cycles") and hasattr(layer.cycles, "use_denoising"):
        layer.cycles.use_denoising = False
if hasattr(scene.cycles, "use_denoising"):
    scene.cycles.use_denoising = False
scene.render.threads_mode = "FIXED"
scene.render.threads = 2
scene.render.resolution_x = 420
scene.render.resolution_y = 300
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.world.color = (0.1, 0.1, 0.1)

def material(name, rgb):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*rgb, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    return mat

walls = material("Ferrari walls", (0.70, 0.68, 0.62))
roof = material("Ferrari roof", (0.39, 0.17, 0.12))
ground = material("Ferrari ground", (0.16, 0.30, 0.19))
door_mat = material("Ferrari doorway", (0.12, 0.18, 0.22))
glass = material("Ferrari glass", (0.20, 0.48, 0.65))

def cube(name, location, scale, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    return obj

# Conceptual house 6m x 4m, walls 3m; pitched roof apex 4.2m.
cube("house walls (6 x 4 x 3 metres)", (0, 0, 1.5), (6, 4, 3), walls)
cube("entrance door", (0, -2.025, 1.0), (1.05, 0.04, 2.0), door_mat)
for x in (-1.7, 1.7):
    cube("front window", (x, -2.04, 1.8), (0.92, 0.04, 0.85), glass)
vertices=[(-3.2,-2.25,2.95),(3.2,-2.25,2.95),
          (-3.2,2.25,2.95),(3.2,2.25,2.95),
          (-3.2,0.0,4.25),(3.2,0.0,4.25)]
faces=[(0,1,5,4),(4,5,3,2),(0,4,2),(1,3,5)]
mesh=bpy.data.meshes.new("roof mesh")
mesh.from_pydata(vertices,[],faces)
mesh.update()
obj=bpy.data.objects.new("gable roof",mesh)
bpy.context.collection.objects.link(obj)
mesh.materials.append(roof)
cube("ground plot", (0,0,-0.13), (10.5,8.5,0.22),ground)

bpy.ops.object.camera_add(location=(9,-11,8))
camera=bpy.context.object
camera.rotation_euler=(Vector((0,0,1.8))-camera.location).to_track_quat("-Z","Y").to_euler()
scene.camera=camera
camera.data.type="ORTHO"
camera.data.ortho_scale=11.5

def light(name, pos, power):
    bpy.ops.object.light_add(type="AREA", location=pos)
    o=bpy.context.object
    o.name=name
    o.data.energy=power
    o.data.shape="DISK"
    o.data.size=8
    o.rotation_euler=(Vector((0,0,1.5))-o.location).to_track_quat("-Z","Y").to_euler()

light("studio key", (4,-6,9), 900)
light("studio fill", (-5,1,8), 550)
scene.render.filepath=str(out/"house.png")
bpy.ops.wm.save_as_mainfile(filepath=str(out/"house.blend"))
bpy.ops.export_scene.gltf(filepath=str(out/"house.glb"),export_format="GLB")
bpy.ops.render.render(write_still=True)
print("FERRARI_BLENDER_3D_EXPORT=PASS title=" + title)
