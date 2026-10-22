# Replace placeholders with the real-product models from assets/<key>.blend.
# Product convention: origin = footprint centre at floor (wall items: back-face bottom centre), front faces -Y.
# rot = rotation about Z so that the product front faces the wanted direction: 0 -> -Y, 90 -> +X, -90 -> -X, 180 -> +Y.
import bpy, math, os
from mathutils import Vector
A = r"C:\Users\vasil\AppData\Local\Temp\claude\C--Users-vasil\6a4d89ac-a284-4cf7-80fb-7d2d8a72f875\scratchpad\assets"
O = bpy.data.objects
CY = 4.835
P = [
 # key, instance name, (x, y, z), rot_deg, placeholders to remove (prefixes / exact names)
 ("sofa_landskrona", "sofa", (0.46, CY, 0.0), 90, ["Sofa_armL", "Sofa_armR", "Sofa_back", "Sofa_base", "Sofa_seat", "Sofa_backcush", "Sofa_leg", "Sofa_throw"]),
 ("armchair_ekenaset", "armchair", (1.92, 6.10, 0.0), -14, ["Lounge_chair"]),
 ("coffee_listerby", "coffee", (1.62, CY, 0.0), 90, ["Coffee_top", "Coffee_leg"]),
 ("floorlamp_hektar", "floorlamp", (1.30, 6.48, 0.0), 58, ["FloorLamp_base", "FloorLamp_pole", "FloorLamp_arm", "FloorLamp_shade"]),
 ("sconce_lagos", "sconce0", (0.0, 3.81, 1.47), 90, ["Sconce0"]),
 ("sconce_lagos", "sconce1", (0.0, 5.86, 1.47), 90, ["Sconce1"]),
 ("picturelight_arvi", "picturelight0", (0.0, CY - 0.415, 2.02), 90, ["PictureLight_bar0", "PictureLight_arm0"]),
 ("picturelight_arvi", "picturelight1", (0.0, CY + 0.415, 2.02), 90, ["PictureLight_bar1", "PictureLight_arm1"]),
 ("frame_rodalm", "art0", (0.0, CY - 0.415, 1.06), 90, ["ArtSofa1_frame", "ArtSofa1_mat", "ArtSofa1_print"]),
 ("frame_rodalm", "art1", (0.0, CY + 0.415, 1.06), 90, ["ArtSofa2_frame", "ArtSofa2_mat", "ArtSofa2_print"]),
 # kitchen
 ("fridge_samsung", "fridge", (3.0355, 0.349, 0.0), 180, ["K_fridge"]),
 ("oven_hansa", "oven", (0.56, 0.90, 0.253), 90, ["K_oven_panel", "CAB_K_oven_door", "K_oven_door", "K_oven_handle"]),
 ("hob_bosch", "hob", (0.31, 0.79, 0.90), 90, ["K_hob"]),
 ("hood_hansa", "hood", (0.0, 0.79, 1.603), 90, ["K_hood"]),
 ("coffee_delonghi", "coffeemachine", (2.563, 0.24, 0.90), 180, ["K_coffee", "K_coffee_tray"]),
 ("sink_teka", "sink", (1.40, 0.33, 0.90), 180, ["K_sink_"]),
 ("tap_teka", "tap", (1.40, 0.04, 0.90), 180, ["K_faucet"]),
 # dining / desk / TV
 ("table_aabenraa", "dining_table", (0.62, 2.56, 0.0), 90, ["Dining_top", "Dining_leg", "Dining_apron"]),
 ("chair_hogved", "chair_s1", (0.40, 1.92, 0.0), 180, ["DChair_S1"]),
 ("chair_hogved", "chair_s2", (0.92, 1.92, 0.0), 180, ["DChair_S2"]),
 ("chair_hogved", "chair_n1", (0.40, 3.20, 0.0), 0, ["DChair_N1"]),
 ("chair_hogved", "chair_n2", (0.92, 3.20, 0.0), 0, ["DChair_N2"]),
 ("pendant_zuma", "pendant0", (0.32, 2.56, 2.60), 0, ["Pendant_dining0", "Pendant_dining0_cord"]),
 ("pendant_zuma", "pendant1", (0.92, 2.56, 2.60), 0, ["Pendant_dining1", "Pendant_dining1_cord"]),
 ("deskchair_langfjall", "deskchair", (2.47, 3.32, 0.0), 90, ["Desk_chair"]),
 ("desklamp_skurup", "desklamp", (3.16, 3.72, 0.74), -90, ["WU_desklamp_base", "WU_desklamp_pole", "WU_desklamp_shade"]),
 ("tv_samsung65", "tv", (3.308, 4.725, 0.635), -90, ["TV_body", "TV_screen", "TV_stand", "TV_frame"]),
 ("soundbar_hwb450", "soundbar", (3.05, 4.725, 0.50), -90, ["WU_soundbar", "Soundbar"]),
 # bedroom / hall / balcony
 ("pendant_oracle", "bed_pendant", (4.85, 3.94, 2.60), 0, ["Pendant_bedroom"]),
 ("walllamp_ranarp", "readlamp0", (6.625, 2.821, 1.17), -90, ["WallLamp0_plate", "WallLamp0_arm", "WallLamp0_shade"]),
 ("walllamp_ranarp", "readlamp1", (6.625, 5.054, 1.17), -90, ["WallLamp1_plate", "WallLamp1_arm", "WallLamp1_shade"]),
 ("mirror_ozze", "round_mirror_ozze", (3.47, 3.90, 1.10), 90, ["Round_mirror_frame"]),
 ("stool_kyrre", "vanity_stool", (3.62, 3.90, 0.0), 90, ["Desk_stool"]),
 ("basket_dan", "laundry_basket", (3.665, 5.035, 0.0), 90, ["Laundry_basket"]),
 ("shoecab_stall", "shoe_cabinet", (3.47, 0.58, 0.0), 90, ["Shoe_STALL"]),
 ("mirror_lindbyn", "hall_mirror_lindbyn", (3.47, 0.58, 1.00), 90, ["Hall_mirror_frame"]),
 ("tarno_table", "tarno_table", (5.375, 5.99, 0.0), 0, ["Tarno_top", "Tarno_leg"]),
 ("tarno_chair", "tarno_chair0", (4.86, 5.99, 0.0), 90, ["Tarno_chair0"]),
 ("tarno_chair", "tarno_chair1", (5.89, 5.99, 0.0), -90, ["Tarno_chair1"]),
 ("lantern_borrby", "lantern", (5.43, 6.04, 0.70), 0, ["Balcony_lantern", "Lantern"]),
 # bathroom / climate
 ("wc_moduo", "wc", (6.44, 0.40, 0.0), -90, ["WC_bowl", "WC_seat", "WC_body"]),
 ("flush_delta50", "flush_plate", (6.44, 0.40, 0.94), -90, ["WC_flush_plate"]),
 ("shower_tempesta", "shower_system", (6.35, 1.68, 0.645), 0, ["Shower_mixer", "Shower_head", "Shower_arm", "Shower_rail", "Shower_hand"]),
 ("towelrail_doris", "towel_rail", (5.35, 0.0, 0.35), 180, ["Towel_rail"]),
 ("mirrorcab_monza", "mirror_cabinet", (5.34, 1.67, 1.18), 0, ["Mirror_cab", "Mirror_front", "Mirror_led", "Mirror_side_led"]),
 ("boiler_galant", "boiler", (6.65, 0.439, 2.05), -90, ["Boiler", "Boiler_panel", "Boiler_display"]),
 ("showerdoor_rea", "shower_door", (6.20, 0.81, 0.0), 0, ["Shower_bifold", "Shower_glass_fixed", "Shower_frame_top", "Shower_handle"]),
 ("showerpanel_rea", "shower_panel", (5.75, 1.235, 0.0), 90, ["Shower_glass_side", "Shower_frame_side"]),
 ("ac_pular_in12", "ac_living", (3.35, 1.85, 2.235), -90, ["AC_indoor", "AC_indoor_vent"]),
 ("ac_pular_in", "ac_bedroom", (4.01, 2.44, 2.27), 180, ["AC_bed_indoor", "AC_bed_vent"]),
 ("ac_gree_out", "ac_outdoor", (6.311, 6.25, 1.70), -90, ["AC_outdoor", "AC_grille"]),
 ("basintap_imex", "basin_tap", (5.3175, 1.67, 1.00), 0, ["Vanity_tap_body", "Vanity_tap_spout", "Vanity_tap_lever"]),
]
COL = bpy.data.collections.get("Products") or bpy.data.collections.new("Products")
if COL.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(COL)
def remove_tree(o):
    for c in list(o.children_recursive): bpy.data.objects.remove(c, do_unlink=True)
    bpy.data.objects.remove(o, do_unlink=True)
done, missing = [], []
for key, inst, loc, rot, ph in P:
    path = os.path.join(A, key + ".blend")
    if not os.path.exists(path): missing.append(key); continue
    old = O.get("PROD_" + inst)
    if old: remove_tree(old)
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        dst.objects = list(src.objects)
    root = None; new = []
    for ob in dst.objects:
        if ob is None: continue
        COL.objects.link(ob); new.append(ob)
        if ob.name.startswith("PROD_") and ob.parent is None: root = ob
    if root is None: missing.append(key + " (no root)"); continue
    root.name = "PROD_" + inst
    for ob in new:
        if ob.type == 'MESH': ob.name = inst + "_" + ob.name.split("_", 1)[-1] if not ob.name.startswith(inst) else ob.name
    root.location = loc; root.rotation_euler = (0, 0, math.radians(rot)); root["product"] = key
    if key == "boiler_galant":                      # sold upright, mounted horizontally above the WC
        root.rotation_euler = (math.radians(90), 0, math.radians(-90)); bpy.context.view_layer.update()
        pts = [c.matrix_world @ Vector(v) for c in root.children_recursive if c.type == 'MESH' for v in c.bound_box]
        mn = Vector([min(p[i] for p in pts) for i in range(3)]); mx = Vector([max(p[i] for p in pts) for i in range(3)])
        root.location += Vector((6.65 - mx.x, 0.439 - (mn.y + mx.y) / 2, 2.05 - mn.z))
    SNAP = {"basin_tap": dict(y1=1.67, zc=1.045), "shower_system": dict(y1=1.68), "mirror_cabinet": dict(y1=1.67), "towel_rail": dict(y0=0.0),
            "wc": dict(x1=6.44), "flush_plate": dict(x1=6.44), "ac_living": dict(x1=3.35), "ac_bedroom": dict(y0=2.44), "tv": dict(x1=3.308),
            "readlamp0": dict(x1=6.625), "readlamp1": dict(x1=6.625), "round_mirror_ozze": dict(x0=3.47), "hall_mirror_lindbyn": dict(x0=3.47),
            "art0": dict(x0=0.0), "art1": dict(x0=0.0), "sconce0": dict(x0=0.0), "sconce1": dict(x0=0.0), "picturelight0": dict(x0=0.0), "picturelight1": dict(x0=0.0),
            "shoe_cabinet": dict(x0=3.47), "hood": dict(x0=0.0, z1=1.603), "oven": dict(x1=0.58), "fridge": dict(y0=0.02), "ac_outdoor": dict(x1=6.50, z0=1.70)}
    if inst in SNAP:
        bpy.context.view_layer.update()
        pts = [c.matrix_world @ Vector(v) for c in root.children_recursive if c.type == 'MESH' for v in c.bound_box]
        mn = Vector([min(p[i] for p in pts) for i in range(3)]); mx = Vector([max(p[i] for p in pts) for i in range(3)]); t = SNAP[inst]
        for i, a in enumerate("xyz"):
            if a + "0" in t: root.location[i] += t[a + "0"] - mn[i]
            if a + "1" in t: root.location[i] += t[a + "1"] - mx[i]
            if a + "c" in t: root.location[i] += t[a + "c"] - (mn[i] + mx[i]) / 2
    if inst == "shower_panel":
        for c in list(root.children_recursive):
            if "stab" in c.name.lower(): bpy.data.objects.remove(c, do_unlink=True)
    newnames = {c.name for c in root.children_recursive} | {root.name}
    for p in ph:
        PROTECT = ("K_fridge_panel", "K_fridge_upper", "Towel_rail_conn", "_bulb", "_down", "_up", "_light", "Sofa_socket", "Dining_socket", "Dining_vase", "TV_socket", "TV_data", "CAB_K_fridge")
        names = [o.name for o in O if (o.name == p or o.name.startswith(p)) and not o.name.startswith("PROD_") and o.name not in newnames and not any(k in o.name for k in PROTECT) and o.type != 'LIGHT']
        for nm in names:
            o = O.get(nm)
            if o is None: continue
            if o.type == 'EMPTY': remove_tree(o)
            else: bpy.data.objects.remove(o, do_unlink=True)
    done.append(inst)
bpy.ops.outliner.orphans_purge(do_recursive=True) if bpy.context.area else None
bpy.ops.wm.save_mainfile()
print("PLACED", len(done), done); print("MISSING", missing)
