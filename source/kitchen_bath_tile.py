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
def resize(n, **k):
    mn, mx = bb(O[n]); v = dict(x0=mn[0], x1=mx[0], y0=mn[1], y1=mx[1], z0=mn[2], z1=mx[2]); v.update(k)
    setbox(O[n], v["x0"], v["x1"], v["y0"], v["y1"], v["z0"], v["z1"])
# ===== KITCHEN: L run, worktop and tile edge all end on the door-jamb line (1.40) =====
E = 1.40
resize("K_carc_L", y1=E - 0.02); resize("K_plinth_L", y1=E - 0.02); resize("K_top_L", y1=E - 0.02)
resize("K_end_panel", y0=E - 0.02, y1=E); resize("K_splash_L", y1=E)
for n in ("K_drawerL1", "K_drawerL2"): kill((n,))
resize("K_drawerL0", y0=1.203, y1=E - 0.023, z0=0.103, z1=0.857)            # 18 cm pull-out for oils/spices next to the hob
# hob + hood 11 toward the corner: landings 50 (corner) / 30 (end) - rule 40/30
d = 0.50 - bb(O["K_hob"])[0][1]
for o in O:
    if o.name.startswith(("K_hob", "K_hood")): o.location.y += d
hb = bb(O["K_hob"])
resize("K_upper_carc_L0", y1=hb[0][1]); resize("K_upper_carc_L1", y0=hb[0][1], y1=hb[1][1]); resize("K_upper_carc_L2", y0=hb[1][1], y1=E)
resize("K_upper_front_L0", y1=hb[0][1] - 0.003); resize("K_upper_front_L1", y0=hb[0][1] + 0.003, y1=hb[1][1] - 0.003); resize("K_upper_front_L2", y0=hb[1][1] + 0.003, y1=E - 0.003)
resize("K_led_L0", y1=hb[0][1] - 0.02); resize("K_led_L1", y0=hb[1][1] + 0.02, y1=E - 0.03)
kill(("K_socket_L",))
resize("Floor_tile_kitchen", y1=E); resize("Floor_tile_profile_kitchen", y0=E - 0.005, y1=E + 0.005)
# ===== FLOOR TILE: Star Gres Town Antracite 60x60 R10 (Praktiker), warm graphite, grout one shade lighter =====
def lin(h):
    c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
base = lin("5E5B56"); m = M["Tile floor 60x120"]; m.name = "Tile floor Town Antracite 60x60"
for nd in m.node_tree.nodes:
    if nd.type == "TEX_BRICK":
        nd.inputs["Color1"].default_value = (*base, 1); nd.inputs["Color2"].default_value = (*base, 1)
        nd.inputs["Brick Width"].default_value = 0.6; nd.inputs["Mortar"].default_value = tuple(v * 1.25 for v in base) + (1,)
    if nd.type == "MIX" and nd.name == "Mix":
        for i in nd.inputs:
            if i.name == "A" and not i.is_linked and hasattr(i.default_value, "__len__") and len(i.default_value) == 4: i.default_value = (*base, 1)
    if nd.type == "MIX" and nd.name == "Mix.001":
        for i in nd.inputs:
            if i.name == "B" and not i.is_linked and hasattr(i.default_value, "__len__") and len(i.default_value) == 4: i.default_value = tuple(v * 0.82 for v in base) + (1,)
# ===== BATHROOM: Electrolux EW7W368SI built-in washer-dryer (82 x 59.6 x 54) under a custom solid-surface top with integrated bowl =====
YF, YB = 1.03, 1.67
setbox(O["Washer_body"], 4.895, 5.491, YB - 0.05 - 0.54, YB - 0.05, 0.0, 0.819)      # 5 cm hose space behind
resize("Washer_front", x1=5.503)
kill(("Washer_divider", "Washer_vent"))
box("Washer_divider", 5.505, 5.523, YF + 0.02, YB, 0.0, 0.86, M["Carcass"], "Bathroom")
box("Washer_vent", 4.93, 5.47, YF - 0.002, YF, 0.835, 0.845, M["Black metal"], "Bathroom")    # top air slot (dryer moisture)
setbox(O["Vanity_cab"], 5.525, 5.745, YF + 0.02, YB, 0.0, 0.86)
resize("Vanity_pullout_front", x0=5.527)
setbox(O["Vanity_pullout_handle"], 5.59, 5.68, YF - 0.02, YF, 0.80, 0.815)
O["Vanity_drain"].location.x = 5.50; O["Vanity_drain"].location.y = 1.45                        # rear corner, drops behind the pull-out
for o in O:
    if o.name.startswith("Washer_") or o.name == "Vanity_cab": o["cutaway_hide"] = o.name in ("Washer_body", "Washer_socket")
bpy.ops.wm.save_mainfile(); print("SAVED", [round(v, 3) for v in hb[0]], [round(v, 3) for v in hb[1]])
