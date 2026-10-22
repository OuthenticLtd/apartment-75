import bpy, sys, os
key = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
probs = []
roots = [o for o in bpy.data.objects if o.parent is None]
if [o.name for o in roots] != [f"PROD_{key}"]: probs.append(f"roots {[o.name for o in roots]}")
r = bpy.data.objects.get(f"PROD_{key}")
if r and (r.type != 'EMPTY' or r.location.length > 1e-6 or r.rotation_euler.to_quaternion().angle > 1e-6 or (r.scale - r.scale.__class__((1,1,1))).length > 1e-6): probs.append("root transform")
for o in bpy.data.objects:
    if o is r: continue
    if not o.name.startswith(key + "_"): probs.append("name " + o.name)
    if o.type != 'MESH': probs.append("type " + o.name)
    if o.hide_render or o.hide_viewport or o.hide_get(): probs.append("hidden " + o.name)
    for s in o.material_slots:
        if s.material is None: probs.append("empty slot " + o.name)
    if len(o.material_slots) == 0: probs.append("no material " + o.name)
for m in bpy.data.materials:
    if m.users == 0: probs.append("orphan mat " + m.name); continue
    if not m.name.startswith(key + " "): probs.append("mat name " + m.name)
    types = {n.type for n in m.node_tree.nodes}
    if types - {"BSDF_PRINCIPLED", "OUTPUT_MATERIAL", "TEX_IMAGE"}: probs.append(f"nodes {m.name} {types}")
for im in bpy.data.images:
    if im.users == 0: continue
    if not im.packed_file: probs.append("unpacked " + im.name)
    if max(im.size) > 1024: probs.append("big image " + im.name)
for coll in (bpy.data.cameras, bpy.data.lights, bpy.data.worlds):
    for x in coll: probs.append("leftover " + x.name)
out = os.path.join(os.environ.get("TMP", "."), f"d_{key}.glb")
bpy.ops.export_scene.gltf(filepath=out, export_apply=True)
print(f"CHECK {key}: {'OK' if not probs else probs}  glb {os.path.getsize(out)//1024} KB")
