import bpy, json, os
O = bpy.data.objects
for o in O:
    for m in getattr(o, "modifiers", []):
        if m.type == 'NODES' and m.node_group and m.node_group.name == "Cutaway": m.show_viewport = False
bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
out = {"objects": [], "lights": []}
for o in O:
    if o.name.startswith(("CAB_",)) or o.name.startswith("INT_"): continue
    if o.type == 'MESH' and o.data.vertices:
        ev = o.evaluated_get(dg); from mathutils import Vector
        pts = [o.matrix_world @ Vector(c) for c in ev.bound_box]
        out["objects"].append({"name": o.name, "collection": o.users_collection[0].name if o.users_collection else "", "min": [round(min(p[i] for p in pts),3) for i in range(3)], "max": [round(max(p[i] for p in pts),3) for i in range(3)], "material": o.active_material.name if o.active_material else None, "props": {k: (v if isinstance(v, (int, float, str)) else str(v)) for k, v in o.items() if not k.startswith("_")}})
    elif o.type == 'LIGHT':
        out["lights"].append({"name": o.name, "type": o.data.type, "loc": [round(v,3) for v in o.matrix_world.translation], "energy": o.data.energy, "props": {k: str(v) for k, v in o.items()}})
json.dump(out, open(os.path.join(os.environ["OUTDIR"], "scene_full.json"), "w"), indent=0)
print("N", len(out["objects"]), len(out["lights"]))
