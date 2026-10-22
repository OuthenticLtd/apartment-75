# Interiors + opening rigs for every cabinet. Run inside the live Blender (exec).
import bpy, bmesh, math
from mathutils import Vector, Matrix
H = {}; exec(bpy.data.texts["apt_helpers.py"].as_string(), H)
box, kill, coll = H["box"], H["kill"], H["coll"]
O = bpy.data.objects; M = bpy.data.materials
INT = "Interiors"
def mat(name, rgb, rough=0.5, metal=0.0, alpha=1.0):
    m = H["mat"](name, rgb, rough, metal)
    return m
CARC, OAK, OAKL, WW = M["Carcass"], M["Oak solid"], M["Oak light"], M["Wardrobe warm white"]
STEEL, BLACK, GLASS, CER = M["Brushed steel"], M["Black matte"], M["Glass"], M["Ceramic white gloss"]
PLATE = mat("INT plate", (0.92, 0.91, 0.88), 0.2); BOWLM = mat("INT bowl sage", (0.55, 0.62, 0.52), 0.3)
BOXM = mat("INT storage box", (0.80, 0.75, 0.66), 0.8); BINM = mat("INT bin grey", (0.30, 0.31, 0.32), 0.6)
POT = mat("INT pot steel", (0.75, 0.75, 0.75), 0.25, 1.0); CLOTH = mat("INT linen", (0.82, 0.80, 0.74), 0.9)
TOWEL = mat("INT towel", (0.70, 0.66, 0.58), 0.95); SHOE = mat("INT shoe", (0.20, 0.17, 0.15), 0.6)
BOTTLE = M.get("Amber glass") or GLASS

def bb(o):
    bpy.context.view_layer.update()
    c = [o.matrix_world @ v.co for v in o.data.vertices]
    return [min(p[i] for p in c) for i in range(3)], [max(p[i] for p in c) for i in range(3)]

def shell(name, x0, x1, y0, y1, z0, z1, open_face, t=0.018, dividers=(), shelves=(), keep_mat=True):
    """Rebuild object `name` (or create) as a carcass open on `open_face` ('+x','-x','+y','-y','+z').
    dividers: list of (axis, pos); shelves: list of (z, a0, a1) spans along the long horizontal axis."""
    o = O.get(name)
    m = (o.active_material if o and o.active_material else CARC)
    bm = bmesh.new()
    def add(a0, a1, b0, b1, c0, c1):
        if a1 - a0 <= 1e-4 or b1 - b0 <= 1e-4 or c1 - c0 <= 1e-4: return
        r = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(a1-a0, b1-b0, c1-c0), verts=r["verts"])
        bmesh.ops.translate(bm, vec=((a0+a1)/2 - cx, (b0+b1)/2 - cy, (c0+c1)/2 - cz), verts=r["verts"])
    cx, cy, cz = (x0+x1)/2, (y0+y1)/2, (z0+z1)/2
    faces = {"-x": (x0, x0+t, y0, y1, z0, z1), "+x": (x1-t, x1, y0, y1, z0, z1), "-y": (x0, x1, y0, y0+t, z0, z1),
             "+y": (x0, x1, y1-t, y1, z0, z1), "-z": (x0, x1, y0, y1, z0, z0+t), "+z": (x0, x1, y0, y1, z1-t, z1)}
    for k, f in faces.items():
        if k != open_face: add(*f)
    for axis, p in dividers:
        if axis == "x": add(p - t/2, p + t/2, y0, y1, z0, z1)
        else: add(x0, x1, p - t/2, p + t/2, z0, z1)
    for z, a0, a1 in shelves:
        if open_face in ("+y", "-y"): add(a0, a1, y0 + t, y1 - t, z - t/2, z + t/2)
        else: add(x0 + t, x1 - t, a0, a1, z - t/2, z + t/2)
    if o is None:
        me = bpy.data.meshes.new(name); o = bpy.data.objects.new(name, me); coll(INT).objects.link(o); o.data.materials.append(m)
    o.parent = None; o.rotation_euler = (0, 0, 0); o.scale = (1, 1, 1)
    for mod in list(o.modifiers): o.modifiers.remove(mod)
    bm.to_mesh(o.data); bm.free(); o.location = (cx, cy, cz)
    return o

def ibox(name, x0, x1, y0, y1, z0, z1, m): kill((name,)); return box(name, x0, x1, y0, y1, z0, z1, m, INT)
def cyl(name, r, x, y, z0, h, m, verts=24):
    kill((name,)); bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=verts, location=(x, y, z0 + h/2))
    o = bpy.context.active_object; o.name = name; o.data.materials.append(m); H["link"](o, INT); return o
def plates(name, x, y, z, n=8, r=0.13): return cyl(name, r, x, y, z, 0.012 * n, PLATE, 40)
def drawer_box(name, x0, x1, y0, y1, z0, z1, open_face, m=CARC):
    """thin-walled drawer box open at the top"""
    return shell(name, x0, x1, y0, y1, z0, z1, "+z", t=0.012)

PIV = "Cabinet pivots"
def rig(fronts, kind, pivot, axis, amount, attach=(), label=""):
    """kind 'rot' (axis 0/1/2, amount radians) or 'move' (axis, amount metres)."""
    fronts = [f for f in fronts if f in O]
    if not fronts: return None
    name = "CAB_" + fronts[0]
    old = O.get(name)
    if old:
        for c in list(old.children):
            mw = c.matrix_world.copy(); c.parent = None; c.matrix_world = mw
        bpy.data.objects.remove(old, do_unlink=True)
    e = bpy.data.objects.new(name, None); coll(PIV).objects.link(e)
    e.empty_display_type = 'PLAIN_AXES'; e.empty_display_size = 0.05; e.location = pivot
    e["cab_kind"], e["cab_axis"], e["cab_amount"], e["cab_open"], e["cab_label"] = kind, axis, amount, 0, label or fronts[0]
    bpy.context.view_layer.update()
    for n in list(fronts) + [a for a in attach if a in O]:
        c = O[n]; mw = c.matrix_world.copy(); c.parent = e; c.matrix_parent_inverse = e.matrix_world.inverted(); c.matrix_world = mw
        c["cab_pivot"] = name
    return e

def hinge_angle(front, hinge_xy, normal_xy, deg=100):
    """rotation about z (radians) that swings the door from its plane out toward normal"""
    mn, mx = bb(O[front]); cxy = Vector(((mn[0]+mx[0])/2, (mn[1]+mx[1])/2))
    v = cxy - Vector(hinge_xy); n = Vector(normal_xy)
    s = v.x * n.y - v.y * n.x
    return math.radians(deg) * (1 if s > 0 else -1)

def door(front, hinge_side, normal, deg=100, attach=()):
    """vertical-hinge door; hinge_side 'min'/'max' along the door's width axis"""
    mn, mx = bb(O[front])
    if normal[0] != 0:   # door plane is YZ, width along y
        hx = mn[0] if normal[0] < 0 else mx[0]; hy = mn[1] if hinge_side == "min" else mx[1]
    else:
        hy = mn[1] if normal[1] < 0 else mx[1]; hx = mn[0] if hinge_side == "min" else mx[0]
    ang = hinge_angle(front, (hx, hy), normal, deg)
    return rig([front], "rot", (hx, hy, (mn[2]+mx[2])/2), 2, ang, attach)

def flap(front, edge, normal, deg=90, attach=()):
    """horizontal hinge: edge 'bottom' (drops down) or 'top' (lifts up)"""
    mn, mx = bb(O[front])
    z = mn[2] if edge == "bottom" else mx[2]
    if normal[0] != 0:
        x = mn[0] if normal[0] < 0 else mx[0]; p = (x, (mn[1]+mx[1])/2, z); axis = 1
        sgn = (1 if normal[0] > 0 else -1) * (1 if edge == "bottom" else -1)
    else:
        y = mn[1] if normal[1] < 0 else mx[1]; p = ((mn[0]+mx[0])/2, y, z); axis = 0
        sgn = (-1 if normal[1] > 0 else 1) * (1 if edge == "bottom" else -1)
    return rig([front], "rot", p, axis, math.radians(deg) * sgn, attach)

def pull(front, normal, dist, attach=()):
    mn, mx = bb(O[front]); axis = 0 if normal[0] != 0 else 1
    return rig([front], "move", ((mn[0]+mx[0])/2, (mn[1]+mx[1])/2, (mn[2]+mx[2])/2), axis, dist * (normal[0] or normal[1]), attach)

# =====================================================================================================
# KITCHEN - base, back run (fronts face +y, carcass y 0..0.56, z 0.10..0.86)
shell("K_carc_corner", 0.0, 0.60, 0.0, 0.60, 0.10, 0.86, "+x", shelves=())
shell("K_carc_B", 0.60, 2.703, 0.0, 0.56, 0.10, 0.86, "+y", dividers=(("x", 1.10), ("x", 1.70), ("x", 2.15)))
# corner: LeMans II - two kidney trays swing out with the door
for i, z in enumerate((0.16, 0.48)):
    ibox(f"INT_K_lemans_tray{i}", 0.62, 1.08, 0.08, 0.50, z, z + 0.012, STEEL)
    ibox(f"INT_K_lemans_rim{i}", 0.62, 1.08, 0.49, 0.50, z, z + 0.05, STEEL)
cyl("INT_K_pot0", 0.11, 0.75, 0.30, 0.172, 0.14, POT); cyl("INT_K_pot1", 0.09, 0.97, 0.28, 0.172, 0.11, POT)
cyl("INT_K_pan0", 0.13, 0.80, 0.29, 0.492, 0.05, BLACK); cyl("INT_K_pot2", 0.10, 0.99, 0.30, 0.492, 0.16, POT)
door("K_front_corner_door", "max", (0, 1), 95, attach=[f"INT_K_lemans_tray{i}" for i in (0, 1)] + [f"INT_K_lemans_rim{i}" for i in (0, 1)] + ["INT_K_pot0", "INT_K_pot1", "INT_K_pan0", "INT_K_pot2"])
# sink: pull-out waste sorting (2 x 18 L + 8 L organic), siphon stays
drawer_box("INT_K_bin_frame", 1.13, 1.67, 0.10, 0.54, 0.12, 0.50, "+z")
ibox("INT_K_bin0", 1.15, 1.34, 0.12, 0.52, 0.13, 0.48, BINM); ibox("INT_K_bin1", 1.36, 1.55, 0.12, 0.52, 0.13, 0.48, BINM)
ibox("INT_K_bin2", 1.57, 1.65, 0.20, 0.52, 0.13, 0.40, M.get("Linen sage", BINM))
cyl("INT_K_siphon", 0.03, 1.40, 0.10, 0.52, 0.17, BLACK)
pull("K_front_sink_bins", (0, 1), 0.42, attach=["INT_K_bin_frame", "INT_K_bin0", "INT_K_bin1", "INT_K_bin2"])
# dishwasher: tub + two racks, door drops down
ibox("INT_K_dw_tub", 1.72, 2.13, 0.02, 0.54, 0.12, 0.84, M.get("Brushed steel"))
ibox("INT_K_dw_rack0", 1.74, 2.11, 0.04, 0.52, 0.20, 0.22, BLACK); ibox("INT_K_dw_rack1", 1.74, 2.11, 0.04, 0.52, 0.52, 0.54, BLACK)
for i in range(6): ibox(f"INT_K_dw_plate{i}", 1.78 + i * 0.05, 1.79 + i * 0.05, 0.12, 0.40, 0.22, 0.46, PLATE)
O["INT_K_dw_tub"].hide_set(False)
shell("INT_K_dw_tub", 1.72, 2.13, 0.02, 0.54, 0.12, 0.84, "+y", t=0.01)
flap("K_front_dw", "bottom", (0, 1), 88)
# drawer stack: cutlery / utensils / plates
DR = [("K_front_drawer0", 0.71, 0.84, 0.46), ("K_front_drawer1", 0.47, 0.68, 0.43), ("K_front_drawer2", 0.12, 0.43, 0.40)]
for f, z0, z1, d in DR:
    drawer_box(f"INT_{f}_box", 2.17, 2.68, 0.06, 0.55, z0, z1, "+z")
ibox("INT_K_cutlery_tray", 2.19, 2.66, 0.10, 0.53, 0.72, 0.76, OAKL)
for i in range(6): ibox(f"INT_K_cutlery{i}", 2.22 + i * 0.07, 2.235 + i * 0.07, 0.15, 0.40, 0.76, 0.768, STEEL)
for i in range(4): ibox(f"INT_K_utensil{i}", 2.22 + i * 0.11, 2.25 + i * 0.11, 0.10, 0.50, 0.48, 0.51, (OAK, BLACK, STEEL, OAK)[i])
plates("INT_K_plates0", 2.33, 0.30, 0.13, 10); plates("INT_K_plates1", 2.55, 0.30, 0.13, 8, 0.11)
cyl("INT_K_bowls", 0.08, 2.33, 0.30, 0.252, 0.10, BOWLM)
pull("K_front_drawer0", (0, 1), 0.46, attach=["INT_K_front_drawer0_box", "INT_K_cutlery_tray"] + [f"INT_K_cutlery{i}" for i in range(6)])
pull("K_front_drawer1", (0, 1), 0.43, attach=["INT_K_front_drawer1_box"] + [f"INT_K_utensil{i}" for i in range(4)])
pull("K_front_drawer2", (0, 1), 0.40, attach=["INT_K_front_drawer2_box", "INT_K_plates0", "INT_K_plates1", "INT_K_bowls"])
# L run (fronts face +x): oven + warming drawer + 18 pull-out
shell("K_carc_L", 0.0, 0.56, 0.60, 1.38, 0.10, 0.86, "+x", dividers=(("y", 1.20),))
ibox("INT_K_oven_cavity", 0.06, 0.54, 0.65, 1.15, 0.27, 0.74, BLACK)
ibox("INT_K_oven_rack", 0.08, 0.52, 0.67, 1.13, 0.45, 0.455, STEEL)
flap("K_oven_door", "bottom", (1, 0), 88)
drawer_box("INT_K_oven_drawer_box", 0.06, 0.55, 0.62, 1.18, 0.11, 0.24, "+z")
pull("K_oven_drawer", (1, 0), 0.38, attach=["INT_K_oven_drawer_box"])
drawer_box("INT_K_spice_box", 0.04, 0.55, 1.215, 1.365, 0.12, 0.84, "+z")
for i, z in enumerate((0.13, 0.45)):
    ibox(f"INT_K_spice_shelf{i}", 0.04, 0.55, 1.215, 1.365, z, z + 0.01, STEEL)
    for j in range(4): cyl(f"INT_K_oil{i}{j}", 0.03, 0.10 + j * 0.12, 1.29, z + 0.01, 0.24 if i == 0 else 0.12, BOTTLE)
pull("K_drawerL0", (1, 0), 0.45, attach=["INT_K_spice_box"] + [f"INT_K_spice_shelf{i}" for i in (0, 1)] + [f"INT_K_oil{i}{j}" for i in (0, 1) for j in range(4)])
# wall units (+y): shelves, drying rack over the sink, glasses over the DW, plates
shell("K_upper_carc_B", 0.35, 2.703, 0.0, 0.33, 1.45, 2.598, "+y", dividers=(("x", 0.60), ("x", 1.10), ("x", 1.70), ("x", 2.15)),
      shelves=((1.83, 0.35, 1.10), (2.21, 0.35, 2.703), (1.83, 1.70, 2.703)))
for i in range(12): ibox(f"INT_K_rack_rod{i}", 1.12 + i * 0.047, 1.125 + i * 0.047, 0.04, 0.30, 1.56, 1.80, STEEL)
for i in range(6): ibox(f"INT_K_rack_plate{i}", 1.14 + i * 0.09, 1.15 + i * 0.09, 0.06, 0.28, 1.57, 1.82, PLATE)
for i in range(4):
    for j in range(2): cyl(f"INT_K_glass{i}{j}", 0.035, 1.76 + i * 0.10, 0.10 + j * 0.12, 1.84, 0.12, GLASS)
plates("INT_K_up_plates", 2.42, 0.17, 1.84, 12, 0.13); cyl("INT_K_up_bowls", 0.08, 2.42, 0.17, 2.22, 0.12, BOWLM)
for i in range(3): ibox(f"INT_K_jar{i}", 0.66 + i * 0.13, 0.76 + i * 0.13, 0.08, 0.20, 1.84, 2.02, GLASS)
for i in range(3): cyl(f"INT_K_tea{i}", 0.04, 0.42 + i * 0.06, 0.15, 1.46, 0.14, (OAKL, BOWLM, PLATE)[i])
UP = [("K_upper_front_B0", "min"), ("K_upper_front_B1", "min"), ("K_upper_front_B2", "min"), ("K_upper_front_B3", "max"), ("K_upper_front_B4", "max")]
for f, h in UP: door(f, h, (0, 1), 105)
shell("K_upper_carc_L0", 0.0, 0.33, 0.0, 0.50, 1.45, 2.598, "+x", shelves=((1.83, 0.33, 0.50), (2.21, 0.33, 0.50)))
shell("K_upper_carc_L1", 0.0, 0.33, 0.50, 1.08, 1.603, 2.598, "+x", shelves=((2.10, 0.50, 1.08),))
shell("K_upper_carc_L2", 0.0, 0.33, 1.08, 1.40, 1.45, 2.598, "+x", shelves=((1.83, 1.08, 1.40), (2.21, 1.08, 1.40)))
door("K_upper_front_L0", "min", (1, 0), 105); door("K_upper_front_L1", "min", (1, 0), 105); door("K_upper_front_L2", "max", (1, 0), 105)
shell("K_fridge_upper", 2.723, 3.35, 0.0, 0.60, 2.08, 2.60, "+y")
ibox("INT_K_trays", 2.80, 3.25, 0.05, 0.55, 2.10, 2.13, STEEL)
flap("K_fridge_upper_front", "top", (0, 1), 85)
# =====================================================================================================
# LIVING - TV/desk wall unit (fronts face -x)
shell("WU_upper_body", 2.83, 3.35, 2.72, 5.52, 1.85, 2.60, "-x", dividers=(("y", 3.32), ("y", 3.92), ("y", 4.453), ("y", 4.987)), shelves=((2.22, 2.72, 5.52),))
for i, (y, n) in enumerate(((2.95, 6), (3.55, 5), (4.15, 6), (4.70, 4), (5.25, 6))):
    for j in range(n): ibox(f"INT_WU_file{i}{j}", 2.95, 3.25, y + j * 0.035, y + j * 0.035 + 0.03, 1.87, 2.15, (BOXM, CLOTH, OAKL)[j % 3])
    ibox(f"INT_WU_box{i}", 2.92, 3.30, y - 0.05, y + 0.20, 2.23, 2.45, BOXM)
for i, h in enumerate(("min", "max", "min", "min", "max")): door(f"WU_upper_door{i}", h, (-1, 0), 105)
shell("WU_console_body", 2.83, 3.31, 3.92, 5.52, 0.14, 0.47, "-x", dividers=(("y", 4.453), ("y", 4.987)))
ibox("INT_WU_games", 2.90, 3.20, 4.00, 4.40, 0.16, 0.22, BLACK); ibox("INT_WU_albums", 2.90, 3.25, 4.50, 4.95, 0.16, 0.36, BOXM)
for i in range(3): flap(f"WU_console_door{i}", "bottom", (-1, 0), 85, attach=[])
# bookcase base -> two drawers
shell("BC_base", 0.02, 0.35, 5.90, 6.60, 0.0, 0.40, "+x")
kill(("BC_drawer", "BC_base_gap"))
for i, (z0, z1) in enumerate(((0.012, 0.198), (0.207, 0.398))):
    box(f"BC_drawer{i}", 0.33, 0.35, 5.902, 6.598, z0, z1, OAK, "Living")
    drawer_box(f"INT_BC_drawer{i}_box", 0.04, 0.33, 5.92, 6.58, z0 + 0.02, z1 - 0.02, "+z")
    ibox(f"INT_BC_stuff{i}", 0.08, 0.30, 6.00, 6.45, z0 + 0.03, z0 + 0.10, (BOXM, CLOTH)[i])
    pull(f"BC_drawer{i}", (1, 0), 0.26, attach=[f"INT_BC_drawer{i}_box", f"INT_BC_stuff{i}"])
# =====================================================================================================
# HALL
shell("Hall_unit_upper", 4.44, 4.77, 1.13, 1.73, 1.98, 2.60, "-x")
ibox("INT_H_hats", 4.48, 4.74, 1.18, 1.68, 2.00, 2.20, BOXM)
door("Hall_unit_upper_door", "min", (-1, 0), 100)
shell("Hall_unit_tall", 4.44, 4.77, 1.73, 2.31, 0.0, 2.60, "-x")
door("Hall_unit_tall_door0", "min", (-1, 0), 100); door("Hall_unit_tall_door1", "max", (-1, 0), 100)
shell("Shoe_STALL_body", 3.47, 3.64, 0.10, 1.06, 0.0, 0.90, "+x", dividers=(("y", 0.579),), shelves=((0.455, 0.10, 1.06),))
for k, f in enumerate(("Shoe_STALL_door00", "Shoe_STALL_door01", "Shoe_STALL_door10", "Shoe_STALL_door11")):
    mn, mx = bb(O[f])
    ibox(f"INT_shoe{k}a", 3.50, 3.62, mn[1] + 0.05, mn[1] + 0.20, mn[2] + 0.05, mn[2] + 0.13, SHOE)
    ibox(f"INT_shoe{k}b", 3.50, 3.62, mn[1] + 0.25, mn[1] + 0.40, mn[2] + 0.05, mn[2] + 0.13, SHOE)
    flap(f, "bottom", (1, 0), 35, attach=[f"INT_shoe{k}a", f"INT_shoe{k}b"])
# =====================================================================================================
# BEDROOM
# wardrobe: the column joins the wardrobe (its door was blocked by the bedside tower); long rail runs behind the tower
for n in ("Bedside_col_top", "Bedside_drawer", "BW_col_pull"):
    if n in O: bpy.data.objects.remove(O[n], do_unlink=True)
shell("Wardrobe_carc", 4.89, 6.65, 1.92, 2.48, 0.0, 2.60, "+y")
for n in ("Wint_B_rail0", "Wint_B_rail1"):
    z = O[n].location.z; y = O[n].location.y; bpy.data.objects.remove(O[n], do_unlink=True)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=6.63 - 5.585, location=((5.585 + 6.63) / 2, y, z), rotation=(0, math.pi / 2, 0))
    r = bpy.context.active_object; r.name = n; r.data.materials.append(M["Brushed steel"]); H["link"](r, "Wardrobe interior"); r["cutaway_hide"] = True
for n, x0 in (("Wint_B_shelf", 5.575), ("Wint_led_B", 5.60)):
    o = O[n]; mn, mx = bb(o); setb = H.get("setbox")
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=(6.63 - x0, mx[1] - mn[1], mx[2] - mn[2]), verts=bm.verts); bm.to_mesh(o.data); bm.free()
    o.rotation_euler = (0, 0, 0); o.scale = (1, 1, 1); o.location = ((x0 + 6.63) / 2, (mn[1] + mx[1]) / 2, (mn[2] + mx[2]) / 2)
kill(("Wardrobe_filler",)); box("Wardrobe_filler", 6.23, 6.65, 2.48, 2.535, 0.0, 2.60, WW, "Bedroom")
for i in range(7): ibox(f"INT_W_shirtA{i}", 4.95 + i * 0.08, 4.97 + i * 0.08, 2.00, 2.42, 0.95, 1.74, (CLOTH, TOWEL, BOWLM)[i % 3])
for i in range(9): ibox(f"INT_W_shirtB{i}", 5.62 + i * 0.11, 5.64 + i * 0.11, 2.00, 2.42, 1.35, 1.99, (CLOTH, TOWEL, PLATE)[i % 3])
for i in range(8): ibox(f"INT_W_trousers{i}", 5.62 + i * 0.12, 5.64 + i * 0.12, 2.05, 2.37, 0.55, 1.06, (BOXM, CLOTH)[i % 2])
for i in range(3): ibox(f"INT_W_shoebox{i}", 4.93 + i * 0.21, 5.12 + i * 0.21, 1.97, 2.40, 0.17, 0.29, BOXM)
for i in range(3): ibox(f"INT_W_suitcase{i}", 4.95 + i * 0.20, 5.13 + i * 0.20, 1.97, 2.40, 1.82, 2.08, (BLACK, BOXM, BLACK)[i])
# sliding doors: each slides over the other
mn, mx = bb(O["Wardrobe_slide_back"]); rig(["Wardrobe_slide_back"], "move", (mn[0], mn[1], mn[2]), 0, 0.62, label="wardrobe left")
mn, mx = bb(O["Wardrobe_slide_front"]); rig(["Wardrobe_slide_front", "Wardrobe_pull1"], "move", (mn[0], mn[1], mn[2]), 0, -0.62, label="wardrobe right")
# bedside towers: drawer + 2-door cupboard above the niche (doors face -x, hinge on the side away from the bed)
for s, (y0, y1, hinge) in (("t0", (2.535, 3.087, "min")), ("t1", (4.787, 5.34, "max"))):
    drawer_box(f"INT_BW_{s}_drawer_box", 6.25, 6.61, y0 + 0.02, y1 - 0.02, 0.10, 0.44, "+z")
    ibox(f"INT_BW_{s}_drawer_stuff", 6.28, 6.55, y0 + 0.05, y1 - 0.05, 0.11, 0.18, CLOTH)
    pull(f"BW_{s}_drawer", (-1, 0), 0.34, attach=[f"INT_BW_{s}_drawer_box", f"INT_BW_{s}_drawer_stuff"])
    shell(f"BW_{s}_top", 6.25, 6.625, y0, y1, 1.40, 2.60, "-x", shelves=((1.75, y0, y1), (2.18, y0, y1)))
    O[f"BW_{s}_top"].data.materials.clear(); O[f"BW_{s}_top"].data.materials.append(CARC)
    for n in (f"BW_{s}_top_gap",):
        if n in O: bpy.data.objects.remove(O[n], do_unlink=True)
    for k, (z0, z1) in enumerate(((1.402, 1.748), (1.752, 2.598))):
        kill((f"BW_{s}_door{k}",)); box(f"BW_{s}_door{k}", 6.23, 6.25, y0 + 0.002, y1 - 0.002, z0, z1, OAK, "Bedroom")
        door(f"BW_{s}_door{k}", hinge, (-1, 0), 105)
    ibox(f"INT_BW_{s}_linen0", 6.30, 6.58, y0 + 0.05, y1 - 0.05, 1.42, 1.60, CLOTH)
    ibox(f"INT_BW_{s}_linen1", 6.30, 6.58, y0 + 0.05, y1 - 0.05, 1.76, 1.95, TOWEL)
# bridge over the bed: lift-up doors (no head-bump), shelf + bedding boxes
shell("BW_bridge_carc", 6.32, 6.65, 3.087, 4.787, 1.55, 2.60, "-x", dividers=(("y", 3.654), ("y", 4.22)), shelves=((2.05, 3.087, 4.787),))
for i, y in enumerate((3.12, 3.69, 4.25)):
    ibox(f"INT_BW_bridge_box{i}", 6.36, 6.62, y, y + 0.50, 1.57, 1.80, BOXM)
    ibox(f"INT_BW_bridge_duvet{i}", 6.36, 6.62, y, y + 0.50, 2.07, 2.30, CLOTH)
for i in range(3): flap(f"BW_bridge_door{i}", "top", (-1, 0), 95)
# lift-up bed: frame + mattress + bedding rotate up on gas struts (hinge at the foot)
mn, mx = bb(O["Bed_platform"])
shell("Bed_platform", mn[0], mx[0], mn[1], mx[1], mn[2], mx[2], "+z", t=0.025)
kill(("Bed_slats",)); box("Bed_slats", mn[0] + 0.03, mx[0] - 0.03, mn[1] + 0.03, mx[1] - 0.03, mx[2] - 0.02, mx[2], OAKL, "Bedroom")
for i in range(3): ibox(f"INT_bed_box{i}", 4.75 + i * 0.60, 5.30 + i * 0.60, 3.25, 4.62, 0.06, 0.26, (BOXM, CLOTH, BOXM)[i])
bed_parts = ["Mattress", "Duvet", "Duvet_fold", "Throw", "Bed_sheet_top", "Pillow_euro0", "Pillow_euro1", "Pillow_lumbar", "Pillow_std0", "Pillow_std1"]
rig(["Bed_slats"], "rot", (mn[0] + 0.03, (mn[1] + mx[1]) / 2, mx[2]), 1, -math.radians(38), attach=bed_parts, label="bed lift")
# dressing table drawer (+x)
drawer_box("INT_dresser_box", 3.48, 3.74, 3.47, 4.33, 0.645, 0.72, "+z")
ibox("INT_dresser_stuff", 3.50, 3.70, 3.55, 4.20, 0.65, 0.68, BOWLM)
pull("Desk_drawer", (1, 0), 0.25, attach=["INT_dresser_box", "INT_dresser_stuff"])
# =====================================================================================================
# BATHROOM
shell("Mirror_cab", 5.04, 5.64, 1.50, 1.67, 1.18, 1.93, "-y", shelves=((1.42, 5.04, 5.64), (1.66, 5.04, 5.64)))
for i in range(5): cyl(f"INT_B_bottle{i}", 0.025, 5.12 + i * 0.11, 1.58, 1.43 + (0.24 if i % 2 else 0), 0.14, (BOTTLE, PLATE, GLASS)[i % 3])
door("Mirror_front0", "min", (0, -1), 100); door("Mirror_front1", "max", (0, -1), 100)
mn, mx = bb(O["WC_cabinet"])
shell("WC_cabinet", 6.52, 6.65, 0.10, 0.70, 1.30, 2.00, "-x", shelves=((1.65, 0.10, 0.70),))
kill(("WC_cab_door",)); box("WC_cab_door", 6.50, 6.52, 0.102, 0.698, 1.302, 1.998, OAKL, "Bathroom")
for i in range(3): cyl(f"INT_B_roll{i}", 0.055, 6.585, 0.20 + i * 0.12, 1.32, 0.10, PLATE)
for i in range(2): ibox(f"INT_B_towel{i}", 6.53, 6.64, 0.15 + i * 0.27, 0.40 + i * 0.27, 1.66, 1.78, TOWEL)
door("WC_cab_door", "min", (-1, 0), 100)
door("Washer_front", "min", (0, -1), 100)
shell("Vanity_cab", 5.525, 5.745, 1.05, 1.67, 0.0, 0.86, "-y")
drawer_box("INT_B_pullout_box", 5.54, 5.73, 1.07, 1.60, 0.04, 0.84, "+z")
for i, z in enumerate((0.05, 0.45)):
    ibox(f"INT_B_pullout_shelf{i}", 5.54, 5.73, 1.07, 1.60, z, z + 0.01, CARC)
    for j in range(3): cyl(f"INT_B_det{i}{j}", 0.045, 5.635, 1.16 + j * 0.15, z + 0.01, 0.26 if i == 0 else 0.18, (BOWLM, PLATE, BINM)[j])
pull("Vanity_pullout_front", (0, -1), 0.45, attach=["Vanity_pullout_handle", "INT_B_pullout_box"] + [f"INT_B_pullout_shelf{i}" for i in (0, 1)] + [f"INT_B_det{i}{j}" for i in (0, 1) for j in range(3)])
# keep the washer handle with its door
if "Washer_handle" in O and "CAB_Washer_front" in O:
    c = O["Washer_handle"]; mw = c.matrix_world.copy(); c.parent = O["CAB_Washer_front"]; c.matrix_parent_inverse = O["CAB_Washer_front"].matrix_world.inverted(); c.matrix_world = mw; c["cab_pivot"] = "CAB_Washer_front"
for o in O:
    if o.name.startswith("INT_"): o["cutaway_hide"] = True
print("BUILT", len([o for o in O if o.name.startswith("CAB_")]), "pivots,", len([o for o in O if o.name.startswith("INT_")]), "interior parts")
