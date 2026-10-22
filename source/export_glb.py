import bpy, os
O = bpy.data.objects
for o in O:
    for m in getattr(o, "modifiers", []):
        if m.type == 'NODES' and m.node_group and m.node_group.name == "Cutaway": m.show_viewport = False; m.show_render = False
    if o.type in ('LIGHT', 'CAMERA'): o.hide_set(True)
for o in O:
    show = o.type not in ('LIGHT', 'CAMERA') and not o.hide_render
    o.hide_viewport = not show
    try: o.hide_set(not show)
    except RuntimeError: pass
# objects that only exist for renders
for o in O:
    if o.name.startswith(("Sun", "Bath_fill")): o.hide_viewport = True
for im in bpy.data.images:
    if im.size[0] > 1024 or im.size[1] > 1024:
        try:
            k = 1024 / max(im.size); im.scale(max(1, int(im.size[0] * k)), max(1, int(im.size[1] * k)))
        except Exception as e: print("skip", im.name, e)

# procedural colours don't survive glTF: replace each linked Base Color with its average colour
def est(sock, depth=0):
    if depth > 8: return None
    if not sock.is_linked:
        v = sock.default_value
        return tuple(v[:3]) if hasattr(v, "__len__") and len(v) >= 3 else None
    n = sock.links[0].from_node; t = n.type
    if t == 'TEX_IMAGE': return "IMAGE"
    if t == 'RGB': return tuple(n.outputs[0].default_value[:3])
    if t == 'VALTORGB':
        els = n.color_ramp.elements; return tuple(sum(e.color[i] for e in els) / len(els) for i in range(3))
    cols = []
    for i in n.inputs:
        if i.type == 'RGBA':
            c = est(i, depth + 1)
            if c == "IMAGE": return "IMAGE"
            if c: cols.append(c)
    if not cols: return None
    if t == 'MIX' or t == 'MIX_RGB':
        return tuple(sum(c[i] for c in cols) / len(cols) for i in range(3))
    return tuple(sum(c[i] for c in cols) / len(cols) for i in range(3))
fixed = []
for m in bpy.data.materials:
    if not m.use_nodes: continue
    b = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if not b: continue
    bc = b.inputs["Base Color"]
    if bc.is_linked:
        c = est(bc)
        if c and c != "IMAGE":
            for l in list(bc.links): m.node_tree.links.remove(l)
            bc.default_value = (*c, 1); fixed.append((m.name, [round(x, 2) for x in c]))
print("FIXED", len(fixed)); [print("  ", f) for f in fixed]
out = os.environ["GLB"]
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', use_visible=True, export_extras=True, export_apply=True,
    export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
    export_image_format='JPEG', export_jpeg_quality=80, export_lights=False, export_cameras=False, export_yup=True)
print("GLB", os.path.getsize(out) / 1e6, "MB")
