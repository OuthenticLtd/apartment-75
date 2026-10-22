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
out = os.environ["GLB"]
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', use_visible=True, export_extras=True, export_apply=True,
    export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
    export_image_format='JPEG', export_jpeg_quality=80, export_lights=False, export_cameras=False, export_yup=True)
print("GLB", os.path.getsize(out) / 1e6, "MB")
