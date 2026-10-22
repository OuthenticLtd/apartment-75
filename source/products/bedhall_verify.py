import bpy, sys, os
from mathutils import Vector
key = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
root = bpy.data.objects.get("PROD_" + key)
errs = []
if root is None or root.type != 'EMPTY':
    errs.append("no root")
else:
    if root.location.length > 1e-6 or any(abs(a) > 1e-6 for a in root.rotation_euler) or any(abs(s - 1) > 1e-6 for s in root.scale):
        errs.append("root transform")
dg = bpy.context.evaluated_depsgraph_get()
mn = Vector((1e9,) * 3); mx = -mn; tris = 0
for ob in bpy.data.objects:
    if ob == root:
        continue
    if ob.parent != root:
        errs.append(f"unparented {ob.name}")
    if not ob.name.startswith(key + "_"):
        errs.append(f"bad name {ob.name}")
    if ob.type != 'MESH':
        errs.append(f"non-mesh {ob.name} {ob.type}")
        continue
    if ob.hide_render or ob.hide_get():
        errs.append(f"hidden {ob.name}")
    e = ob.evaluated_get(dg); me = e.to_mesh(); me.calc_loop_triangles(); tris += len(me.loop_triangles)
    for v in me.vertices:
        w = e.matrix_world @ v.co
        mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
    e.to_mesh_clear()
    for m in ob.data.materials:
        if m is None or not m.name.startswith(key + " "):
            errs.append(f"bad mat {ob.name}:{m.name if m else None}")
for m in bpy.data.materials:
    if m.users and m.node_tree:
        for n in m.node_tree.nodes:
            if n.type not in ('BSDF_PRINCIPLED', 'OUTPUT_MATERIAL', 'TEX_IMAGE', 'NORMAL_MAP'):
                errs.append(f"node {m.name}:{n.type}")
for im in bpy.data.images:
    if im.users and im.source == 'FILE' or (im.users and im.packed_file is None and im.source != 'VIEWER'):
        if im.packed_file is None:
            errs.append(f"unpacked image {im.name}")
    if max(im.size) > 1024:
        errs.append(f"image too big {im.name} {tuple(im.size)}")
d = mx - mn
print(f"VERIFY {key}: size {tuple(round(x, 4) for x in d)} min {tuple(round(x, 4) for x in mn)} tris {tris} objs {len(bpy.data.objects)} errs {errs}")
