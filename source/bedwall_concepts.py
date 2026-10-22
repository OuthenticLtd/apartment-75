import bpy, bmesh, os
H = {}; exec(bpy.data.texts["apt_helpers.py"].as_string(), H)
box, kill = H["box"], H["kill"]
O = bpy.data.objects; M = bpy.data.materials; BR = "Bedroom"
C = os.environ["CONCEPT"]
def bb(o):
    bpy.context.view_layer.update()
    c = [o.matrix_world @ v.co for v in o.data.vertices]
    return [min(p[i] for p in c) for i in range(3)], [max(p[i] for p in c) for i in range(3)]
def setbox(o, x0, x1, y0, y1, z0, z1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0, calc_uvs=True)
    bmesh.ops.scale(bm, vec=(x1-x0, y1-y0, z1-z0), verts=bm.verts); bm.to_mesh(o.data); bm.free()
    o.parent = None; o.rotation_euler = (0, 0, 0); o.scale = (1, 1, 1); o.location = ((x0+x1)/2, (y0+y1)/2, (z0+z1)/2)
def setmat(o, m): o.data.materials.clear(); o.data.materials.append(m)
OAK = O["Bedside_col_top"].active_material; OAKD = O["Bedside_drawer"].active_material
WW, CARC, GAP, LED = M["Wardrobe warm white"], M["Carcass"], M["Shadow gap"], M["LED shelf warm"]
WALL, YC, YF = 6.65, 2.535, 5.34            # bed wall, wardrobe/column face, facade: symmetric about the bed axis 3.937
MY0, MY1, MZ = 3.147, 4.727, 0.53           # mattress
BZ, BX = 1.55, 6.30                          # bridge underside (mattress + 102), bridge front (35 deep)
kill(("BW_", "Bed_ns_window_gap"))
# sheer curtain parks only at the left end of the window (wall x3.47-3.87); track stops at the window edge
for n in ("BedCurtain_sheer_R",):
    if n in O: bpy.data.objects.remove(O[n], do_unlink=True)
mn, mx = bb(O["BedCurtain_track"]); setbox(O["BedCurtain_track"], mn[0], 6.20, mn[1], mx[1], mn[2], mx[2])
# the column by the wardrobe becomes part of the wardrobe (warm-white door, shelves) so the bed wall reads symmetric
for n in ("Bedside_col_open", "Bedside_col_shelf", "Bedside_col_side", "Bedside_col_niche_led", "Bedside_col_ledge", "Bedside_col_top_gap", "Bedside_drawer_gap"):
    if n in O: bpy.data.objects.remove(O[n], do_unlink=True)
setbox(O["Bedside_col_top"], 6.23, WALL, 1.92, YC - 0.02, 0.08, 2.60); setmat(O["Bedside_col_top"], CARC)
setbox(O["Bedside_drawer"], 6.232, 6.648, YC - 0.02, YC, 0.082, 2.598); setmat(O["Bedside_drawer"], WW)
box("BW_col_pull", 6.25, 6.27, YC, YC + 0.004, 0.90, 1.30, M["Oak solid"], BR)
def lamp_to(i, y, x=6.427):
    s = O[f"WallLamp{i}_shade"]; mn, mx = bb(s); dy = y - (mn[1] + mx[1]) / 2
    for sfx in ("_plate", "_arm", "_shade", "_light"): O[f"WallLamp{i}{sfx}"].location.y += dy
if C == "A":
    # twin oak towers 55 x 42 in the two bedside zones; bedside = niche floor 5 from the mattress, open to the bed
    for side, (y0, y1, open_y) in enumerate(((YC, MY0 - 0.06, MY0 - 0.06), (MY1 + 0.06, YF, MY1 + 0.06))):
        t = f"BW_t{side}_"
        box(t + "drawer", 6.23, WALL, y0, y1, 0.08, 0.47, OAKD, BR)
        box(t + "drawer_gap", 6.228, 6.23, y0 + 0.02, y1 - 0.02, 0.26, 0.262, GAP, BR)
        box(t + "plinth", 6.25, WALL, y0 + 0.02, y1 - 0.02, 0.0, 0.08, GAP, BR)
        setbox(O["Bed_ns_wardrobe" if side == 0 else "Bed_ns_window"], 6.23, WALL, y0, y1, 0.47, 0.555)   # niche floor = bedside surface
        # identical towers: niche open to the room AND to the pillow, closed only on the side away from the bed
        by = (y0, y0 + 0.02) if side == 0 else (y1 - 0.02, y1)
        box(t + "niche_back", 6.25, WALL, by[0], by[1], 0.555, 1.20, M["Oak light"], BR)
        box(t + "shelf", 6.23, WALL, y0, y1, 0.85, 0.87, OAK, BR, bevel=0.002)
        box(t + "niche_led", 6.27, WALL - 0.04, open_y - 0.06 if side == 0 else open_y + 0.04, open_y - 0.04 if side == 0 else open_y + 0.06, 1.195, 1.20, LED, BR)
        box(t + "top", 6.23, WALL, y0, y1, 1.20, 2.60, OAK, BR)
        box(t + "top_gap", 6.228, 6.23, y0 + 0.01, y1 - 0.01, 1.75, 1.752, GAP, BR)
    if "Bed_ns_wardrobe_gap" in O: bpy.data.objects.remove(O["Bed_ns_wardrobe_gap"], do_unlink=True)
    BY0, BY1 = MY0 - 0.06, MY1 + 0.06
    setbox(O["Bed_wall_panel"], WALL - 0.025, WALL, BY0, BY1, 0.0, BZ)
    lamp_to(0, BY0 + 0.075); lamp_to(1, BY1 - 0.075)
    setbox(O["Bed_socket0"], 6.42, 6.57, YC + 0.02, YC + 0.027, 0.62, 0.70)   # on the niche back, beside the phone   # inside the niches, on the closed side
    setbox(O["Bed_socket1"], 6.42, 6.57, YF - 0.027, YF - 0.02, 0.62, 0.70)
    setbox(O["Bed_switch0"], WALL - 0.032, WALL - 0.025, BY0 + 0.01, BY0 + 0.09, 0.71, 0.79)
    setbox(O["Bed_switch1"], WALL - 0.032, WALL - 0.025, BY1 - 0.09, BY1 - 0.01, 0.71, 0.79)
    O["NS_book"].location.y += (2.84 - (bb(O["NS_book"])[0][1] + bb(O["NS_book"])[1][1]) / 2)
    for n, y in (("NS_carafe", 5.00), ("NS_glass", 5.10)):
        o = O[n]; mn, mx = bb(o); o.location.y += y - (mn[1] + mx[1]) / 2
else:
    # B: full-width bridge column-face to facade, identical floating bedside drawers both sides
    BY0, BY1 = YC, YF
    setbox(O["Bed_ns_wardrobe"], 6.225, WALL - 0.025, MY0 - 0.06 - 0.45, MY0 - 0.06, 0.47, 0.555)
    setbox(O["Bed_ns_wardrobe_gap"], 6.223, 6.225, MY0 - 0.50, MY0 - 0.07, 0.50, 0.503)
    setbox(O["Bed_ns_window"], 6.225, WALL - 0.025, MY1 + 0.06, MY1 + 0.51, 0.47, 0.555)
    box("BW_ns_window_gap", 6.223, 6.225, MY1 + 0.07, MY1 + 0.50, 0.50, 0.503, GAP, BR)
    setbox(O["Bed_wall_panel"], WALL - 0.025, WALL, YC, YF, 0.0, BZ)
    lamp_to(0, MY0 - 0.06 - 0.225); lamp_to(1, MY1 + 0.06 + 0.225)
    setbox(O["Bed_socket0"], WALL - 0.032, WALL - 0.025, MY0 - 0.48, MY0 - 0.33, 0.61, 0.69)
    setbox(O["Bed_socket1"], WALL - 0.032, WALL - 0.025, MY1 + 0.33, MY1 + 0.48, 0.61, 0.69)
    setbox(O["Bed_switch0"], WALL - 0.032, WALL - 0.025, MY0 - 0.15, MY0 - 0.07, 0.71, 0.79)
    setbox(O["Bed_switch1"], WALL - 0.032, WALL - 0.025, MY1 + 0.07, MY1 + 0.15, 0.71, 0.79)
    for n, y in (("NS_carafe", 4.98), ("NS_glass", 5.08)):
        o = O[n]; mn, mx = bb(o); o.location.y += y - (mn[1] + mx[1]) / 2
# bridge over the bed between BY0 and BY1, warm-white push doors (~57 each)
box("BW_bridge_carc", BX + 0.02, WALL, BY0, BY1, BZ, 2.60, CARC, BR)
n = max(1, round((BY1 - BY0) / 0.57)); w = (BY1 - BY0) / n
for i in range(n):
    box(f"BW_bridge_door{i}", BX, BX + 0.02, BY0 + i * w + 0.002, BY0 + (i + 1) * w - 0.002, BZ + 0.002, 2.598, WW, BR)
box("BW_bridge_led", BX + 0.03, BX + 0.05, BY0 + 0.03, BY1 - 0.03, BZ - 0.004, BZ, LED, BR)
bpy.ops.wm.save_mainfile()
print("BUILT", C, "bridge", round(BY1 - BY0, 3), "doors", n)
