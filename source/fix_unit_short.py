import bpy, bmesh
H = {}; exec(bpy.data.texts["apt_helpers.py"].as_string(), H)
box, kill = H["box"], H["kill"]
O = bpy.data.objects; M = bpy.data.materials
def bb(o):
    bpy.context.view_layer.update()
    c = [o.matrix_world @ v.co for v in o.data.vertices]
    return [min(p[i] for p in c) for i in range(3)], [max(p[i] for p in c) for i in range(3)]
def setbox(o, x0, x1, y0, y1, z0, z1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0, calc_uvs=True)
    bmesh.ops.scale(bm, vec=(x1-x0, y1-y0, z1-z0), verts=bm.verts); bm.to_mesh(o.data); bm.free()
    o.parent = None; o.rotation_euler = (0, 0, 0); o.scale = (1, 1, 1); o.location = ((x0+x1)/2, (y0+y1)/2, (z0+z1)/2)
# Whole TV/desk unit starts 24 later: wall beside the living-room door stays free for the light switch
# (rulebook: switch on the latch side 10-30 from the frame, h 105). Desk back to 120.
D = 0.24; Y0 = 2.72                        # new start of the unit (inside face of the end panel)
mn, mx = bb(O["WU_end_L"]); setbox(O["WU_end_L"], mn[0], mx[0], Y0 - 0.03, Y0, mn[2], mx[2])
for n in ("WU_upper_body", "WU_back_back", "WU_desk_slab", "WU_shelf0", "WU_shelf1"):
    mn, mx = bb(O[n]); setbox(O[n], mn[0], mx[0], Y0, mx[1], mn[2], mx[2])
for n in ("WU_shelf0_led", "WU_shelf1_led", "WU_led_upper"):
    mn, mx = bb(O[n]); setbox(O[n], mn[0], mx[0], mn[1] + D, mx[1], mn[2], mx[2])
mn, mx = bb(O["WU_desk_side"]); setbox(O["WU_desk_side"], mn[0], mx[0], Y0, Y0 + 0.04, mn[2], mx[2])
for n in ("WU_shelf0_light", "WU_shelf1_light"): O[n].location.y += D / 2
for o in O:
    if o.parent is None and o.name.startswith(("WU_book", "WU_v2", "WU_v3", "WU_v4", "WU_desk_vase", "WU_desk_laptop")): o.location.y += D
O["Desk_chair"].location.y += 0.20
r = O["WU_back_reeds"]; print("REEDS mods", [(m.type, getattr(m, "count", None), getattr(m, "relative_offset_displace", None)[:] if hasattr(m, "relative_offset_displace") else None, getattr(m, "constant_offset_displace", None)[:] if hasattr(m, "constant_offset_displace") else None) for m in r.modifiers])
# upper doors: seams aligned with the modules below - 2 x 60 over the desk, 3 x 53.3 over the console
src = O["WU_upper_door0"]; dm, dM = bb(src)
for o in [o for o in O if o.name.startswith("WU_upper_door")]:
    if o is not src: bpy.data.objects.remove(o, do_unlink=True)
edges = [Y0, Y0 + 0.60, 3.92, 3.92 + 1.60/3, 3.92 + 3.20/3, 5.52]
for i in range(5):
    o = src if i == 0 else src.copy()
    if i: o.data = src.data.copy(); src.users_collection[0].objects.link(o)
    o.name = f"WU_upper_door{i}"; setbox(o, dm[0], dM[0], edges[i] + 0.002, edges[i+1] - 0.002, dm[2], dM[2])
# living-room light switch beside the door, latch side, 15 from the frame, h 105
kill(("Living_switch",))
box("Living_switch", 3.343, 3.35, 2.48, 2.56, 1.01, 1.09, M["Switch plate white"], src.users_collection[0].name)
bpy.ops.wm.save_mainfile()
for n in ("WU_end_L", "WU_desk_side", "WU_desk_slab", "WU_upper_body", "WU_upper_door0", "WU_upper_door4", "WU_shelf0", "WU_book0", "WU_desk_laptop", "LvStool_seat", "WU_back_reeds", "Living_switch"):
    mn, mx = bb(O[n]); print("BB", n, [round(v, 3) for v in mn], [round(v, 3) for v in mx])
