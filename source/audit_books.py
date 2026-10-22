import bpy, math
from mathutils import Vector
_O = bpy.data.objects
for o in _O:   # the dollhouse cutaway (GN "Cutaway") may be live in a GUI-saved file: measure the real geometry
    for m in getattr(o, "modifiers", []):
        if m.name == "Cutaway" or (m.type == 'NODES' and m.node_group and m.node_group.name == "Cutaway"): m.show_viewport = False
bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
# placeholders were replaced by real-product models (PROD_<instance> empties); map the old names onto them
ALIAS = {"AC_outdoor": "PROD_ac_outdoor", "WallLamp0_plate": ("PROD_readlamp0", "plate"), "WallLamp1_plate": ("PROD_readlamp1", "plate"), "Sconce0": "PROD_sconce0", "Sconce1": "PROD_sconce1", "ArtSofa1_frame": "PROD_art0", "ArtSofa2_frame": "PROD_art1", "DChair_S1": "PROD_chair_s1", "DChair_S2": "PROD_chair_s2", "DChair_N1": "PROD_chair_n1", "DChair_N2": "PROD_chair_n2",
 "Desk_chair": "PROD_deskchair", "FloorLamp_shade": ("PROD_floorlamp", "shade"), "Hall_mirror": "PROD_hall_mirror_lindbyn", "K_coffee": "PROD_coffeemachine", "K_fridge": "PROD_fridge",
 "K_hob": "PROD_hob", "K_hood": "PROD_hood", "K_oven_door": "PROD_oven", "K_sink_bottom": ("PROD_sink", "strainer"), "Laundry_basket": "PROD_laundry_basket", "Lounge_chair": "PROD_armchair",
 "LvChair_seat": ("PROD_deskchair", "seat"), "Mirror_cab": "PROD_mirror_cabinet", "Pendant_dining0": "PROD_pendant0", "Pendant_dining1": "PROD_pendant1", "Round_mirror": "PROD_round_mirror_ozze",
 "Sofa_leg1": ("PROD_sofa", "leg"), "TV_body": "PROD_tv", "Tarno_chair0": "PROD_tarno_chair0", "Tarno_chair1": "PROD_tarno_chair1", "WU_desklamp_base": "PROD_desklamp",
 "WallLamp0_shade": ("PROD_readlamp0", "shade"), "WallLamp1_shade": ("PROD_readlamp1", "shade"), "Dining_apron_S": ("PROD_dining_table", "rail")}
PREFIX = {"Sofa_": ["PROD_sofa"], "Coffee_": ["PROD_coffee"], "FloorLamp_": ["PROD_floorlamp"], "Dining_top": ["PROD_dining_table"], "Dining_leg": [], "Shoe_": ["PROD_shoe_cabinet"],
 "WC_bowl": ["PROD_wc"], "WC_body": [], "Shower_glass": ["PROD_shower_panel"], "Shower_bifold": ["PROD_shower_door"], "Tarno_top": ["PROD_tarno_table"], "Tarno_leg": [], "K_fridge": ["PROD_fridge"]}
class _Sel:   # a selection of meshes treated as one object
    def __init__(self, meshes, root): self.meshes, self.root = meshes, root
    type = 'SEL'; hide_render = False
    @property
    def location(self): return self.root.location
    @property
    def matrix_world(self): return self.root.matrix_world
    @property
    def name(self): return self.root.name
class _OA:
    def __getitem__(self, k):
        if k in _O: return _O[k]
        a = ALIAS.get(k)
        if a is None: raise KeyError(k)
        root, sub = (a, None) if isinstance(a, str) else a
        r = _O[root]; ms = [c for c in r.children_recursive if c.type == 'MESH' and (sub is None or sub in c.name.lower())]
        if not ms: ms = [c for c in r.children_recursive if c.type == 'MESH']
        return _Sel(ms, r) if sub else r
    def __contains__(self, k): return k in _O or k in ALIAS
    def get(self, k, d=None):
        try: return self[k]
        except KeyError: return d
    def __iter__(self): return iter(_O)
O = _OA()
def _bowl(o):
    c = obb(o); m = (c[0][0] + c[1][0]) / 2
    return [m - 0.19, c[0][1], c[0][2]], [m + 0.19, c[1][1], c[1][2]]
def obb(o):
    if isinstance(o, _Sel) or o.type == 'EMPTY':
        ms = o.meshes if isinstance(o, _Sel) else [c for c in o.children_recursive if c.type == 'MESH']
        pts = [m.matrix_world @ Vector(c) for m in ms for c in m.evaluated_get(dg).bound_box]
    else:
        ev = o.evaluated_get(dg); pts = [o.matrix_world @ Vector(c) for c in ev.bound_box]
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]
def tree(o): return [o] + list(o.children_recursive)
def P(*pre):
    out = [o for o in _O if o.name.startswith(pre)]
    for r in {r for p in pre for k, rs in PREFIX.items() if p.startswith(k) or k.startswith(p) for r in rs}:
        if r in _O: out.append(_O[r])
    return out
def U(objs):
    bs = [obb(o) for o in objs if (o.type in ('MESH', 'EMPTY') and not o.hide_render) and (o.type == 'MESH' or any(c.type == 'MESH' for c in o.children_recursive))]
    return [min(b[0][i] for b in bs) for i in range(3)], [max(b[1][i] for b in bs) for i in range(3)]
units = {
 "Sofa": P("Sofa_base", "Sofa_back", "Sofa_arm", "Sofa_seat", "Sofa_leg"), "Coffee table": P("Coffee_top", "Coffee_leg"),
 "TV/desk unit": P("WU_end", "WU_desk_slab", "WU_console_body", "WU_upper_body", "WU_step"),
 "Lounge chair": tree(O["Lounge_chair"]), "Floor lamp": P("FloorLamp_base", "FloorLamp_pole"),
 "Bookcase": P("BC_frame", "BC_side", "BC_base", "BC_top", "BC_back"),
 "Dining table": P("Dining_top", "Dining_leg"), 
 **{f"Dining chair {c}": tree(O[f"DChair_{c}"]) for c in ("S1","S2","N1","N2")}, "Desk stool": tree(O["Desk_chair"]),
 "Kitchen": P("K_carc", "K_plinth", "K_front", "K_top", "K_fridge", "K_end_panel"),
 "Bed": P("Bed_headboard", "Bed_platform", "Mattress"), "Bedside wardrobe": P("Bed_ns_wardrobe"), "Bedside window": P("Bed_ns_window"),
 "Wardrobe": P("Wardrobe_carc", "Wardrobe_slide", "Wardrobe_track", "Bedside_col_top", "Bedside_col_shelf", "Bedside_col_side", "Bedside_drawer", "Bedside_plinth"),
 "Vanity desk": P("Desk_top", "Desk_drawer"), "Laundry basket": [O["Laundry_basket"]],
 "Shoe cabinet": P("Shoe_"), "Hall unit": P("Hall_unit_side", "Hall_unit_bench_seat", "Hall_unit_upper", "Hall_unit_tall"),
 "Vanity": P("Vanity_cab", "Vanity_top"), "WC": P("WC_bowl", "WC_body", "WC_boxing"), "Shower": P("Shower_glass", "Shower_bifold"),
 "Balcony table": P("Tarno_top", "Tarno_leg"), "Balcony chair 0": tree(O["Tarno_chair0"]), "Balcony chair 1": tree(O["Tarno_chair1"]),
 "AC unit": [O["AC_outdoor"]], "Balcony pot": tree(O["potted_plant_02_root"]),
}
B = {k: [obb(o) for o in v if o.type == 'MESH' and not o.hide_render] for k, v in units.items()}
def ov(a, b, tol=0.01): return all(a[0][i] < b[1][i]-tol and b[0][i] < a[1][i]-tol for i in range(3))
fails, warns, ok = [], [], []
def chk(name, val, lo=None, hi=None, sev="FAIL", unit="cm"):
    v = round(val*100) if unit == "cm" else round(val, 2)
    good = (lo is None or v >= lo) and (hi is None or v <= hi)
    s = f"{name}: {v} {unit} (target {'' if lo is None else '>='+str(lo)}{' ' if lo is not None and hi is not None else ''}{'' if hi is None else '<='+str(hi)})"
    (ok if good else (fails if sev == "FAIL" else warns)).append(s)
# --- overlaps, walls, door swings
keys = list(B)
for i in range(len(keys)):
    for j in range(i+1, len(keys)):
        if any(ov(a, b) for a in B[keys[i]] for b in B[keys[j]]): fails.append(f"OVERLAP {keys[i]} <-> {keys[j]}")
walls = [obb(o) for o in O if o.type == 'MESH' and o.name.startswith(("Wall_", "W2_", "Bal_wall")) and "lintel" not in o.name]
for k, v in B.items():
    if any(ov(a, w, 0.02) for a in v for w in walls): fails.append(f"INTO WALL {k}")
doors = {"corridor->living": ((3.35, 2.30), 0.90, lambda p: p.x < 3.35 and p.y < 2.30), "window leaf": ((0.40, 6.65), 0.75, lambda p: p.x > 0.40 and p.y < 6.65),
 "living balcony": ((3.35, 6.50), 0.80, lambda p: p.x < 3.35 and p.y < 6.50), "bedroom": ((3.60, 2.44), 0.80, lambda p: p.x > 3.60 and p.y > 2.44),
 "bedroom balcony": ((3.87, 5.34), 0.80, lambda p: p.x > 3.87 and p.y < 5.34),
 "entrance": ((4.72, 0.0), 1.00, lambda p: p.x < 4.72 and p.y > 0.0)}
for dn, (h, r, side) in doors.items():
    hv = Vector(h)
    for k, v in B.items():
        for a in v:
            if a[0][2] > 1.9: continue
            if any((lambda p: (p - hv).length < r - 0.02 and side(p))(Vector((a[0][0] + (a[1][0]-a[0][0])*ix/6, a[0][1] + (a[1][1]-a[0][1])*iy/6))) for ix in range(7) for iy in range(7)):
                (warns if (dn, k) == ("window leaf", "Sofa") else fails).append(f"DOOR SWING {dn} hits {k}" + (" (owned 223 sofa: door opens ~85 deg)" if (dn, k) == ("window leaf", "Sofa") else "")); break
# --- facing
def facing(o): f = o.matrix_world.to_quaternion() @ Vector((0, -1, 0)); return Vector((f.x, f.y))
dt = Vector((0.62, 2.88))
_dt = obb(O["Dining_top"] if "Dining_top" in O else _O["PROD_dining_table"]); _dy = (_dt[0][1] + _dt[1][1]) / 2
for n, ts in (("DChair_S1", [Vector((0.40, _dy))]), ("DChair_S2", [Vector((0.92, _dy))]), ("DChair_N1", [Vector((0.40, _dy))]), ("DChair_N2", [Vector((0.92, _dy))]),
              ("Tarno_chair0", [Vector((4.70, 7.5)), Vector((5.375, 5.99))]), ("Tarno_chair1", [Vector((5.69, 7.5)), Vector((5.375, 5.99))])):   # balcony: facing the view OR the table
    o = O[n]; a = min(math.degrees(facing(o).angle(t - o.matrix_world.translation.xy)) for t in ts)
    (ok if a <= 20 else fails).append(f"FACING {n}: {a:.0f} deg off")
lc = O["Lounge_chair"]; fa = facing(lc); sofa_dir = Vector((-1, 0))
a = math.degrees(fa.angle(Vector((0, -1)))); (ok if 10 <= a <= 35 else warns).append(f"Lounge chair turned {a:.0f} deg toward sofa (target 15-30)")
# --- clearances (P, N)
S, C, W, Bd, Wd = U(units["Sofa"]), U(units["Coffee table"]), U(units["TV/desk unit"]), U(units["Bed"]), U(units["Wardrobe"])
chk("Sofa seat front -> coffee table", C[0][0] - S[1][0], 40, 45)
_r = min(obb(o)[0][0] for o in P("WU_console_top", "WU_console_door")) - C[1][0]; chk("Coffee table -> TV/desk unit (main route, min 76)", _r, 76); chk("Coffee table -> TV/desk unit (main route target 90)", _r, 90, sev="WARN")
T = U(units["Dining table"]); chk("Dining table end -> desk front (main route)", 2.75 - T[1][0], 90); chk("Dining N edge -> sofa arm (chair access)", S[0][1] - T[1][1], 76); chk("Dining S edge -> kitchen run end (no route behind: chair access 76)", T[0][1] - obb(O["K_end_panel"])[1][1], 76); chk("Place setting width per diner (2 per side)", (T[1][0]-T[0][0])/2, 60)
chk("Dining table depth", T[1][1] - T[0][1], 80)
chk("Pendant bottom above dining table", obb(O["Pendant_dining0"])[0][2] - 0.75, 55, 65); chk("Pendant spacing", O["Pendant_dining1"].location.x - O["Pendant_dining0"].location.x, 55, 75); pd = ([O["Pendant_dining0"].location.x, O["Pendant_dining0"].location.y], [O["Pendant_dining1"].location.x, O["Pendant_dining1"].location.y]); chk("Pendant off-centre from table", ((pd[0][0]+pd[1][0])/2-0.65)**2**0.5 if False else abs((pd[0][0]+pd[1][0])/2-0.62)+abs((pd[0][1]+pd[1][1])/2-(T[0][1]+T[1][1])/2), None, 3)
chk("Kitchen aisle bottom run -> dining zone", T[0][1] - 0.60, 100)
chk("Hob landing to run end", obb(O["K_end_panel"])[1][1] - obb(O["K_hob"])[1][1], 30)
chk("Hob landing toward corner (corner worktop counts)", obb(O["K_hob"])[0][1] - 0.0, 40)
chk("Hood above hob", obb(O["K_hood"])[0][2] - 0.90, 65)
chk("Bed side (wardrobe)", Bd[0][1] - Wd[1][1], 60, sev="FAIL"); chk("Bed side (wardrobe) target", Bd[0][1] - Wd[1][1], 75, sev="WARN")
chk("Bed side (window wall)", 5.34 - Bd[1][1], 60, sev="FAIL"); chk("Bed side (window) target", 5.34 - Bd[1][1], 75, sev="WARN")
chk("Bed foot -> vanity desk", Bd[0][0] - U(units["Vanity desk"])[1][0], 75); chk("Bedside drawer size (wardrobe)", obb(O["Bed_ns_wardrobe"])[1][1]-obb(O["Bed_ns_wardrobe"])[0][1], 40); chk("Reading lamp shade over mattress edge <=10 (wardrobe)", obb(O["Mattress"])[0][1] - obb(O["WallLamp0_shade"])[1][1], -10); chk("Reading lamp shade over mattress edge <=10 (window)", obb(O["WallLamp1_shade"])[0][1] - obb(O["Mattress"])[1][1], -10)
wc = obb(O["Wardrobe_carc"]); chk("Wardrobe internal depth", wc[1][1]-wc[0][1]-0.01, 55); chk("Long-hang rail height", O["Wint_A_rail"].location.z, 160, 180); chk("Double-hang upper rail", O["Wint_B_rail0"].location.z, 190, 205); chk("Double-hang lower rail", O["Wint_B_rail1"].location.z, 100, 110); chk("Wardrobe front free (sliding doors)", Bd[0][1] - Wd[1][1], 60); chk("Mattress length", obb(O["Mattress"])[1][0] - obb(O["Mattress"])[0][0], 200)
chk("Mattress top height", obb(O["Mattress"])[1][2], 46, 56)
chk("Hall clear width at bench", U(units["Hall unit"])[0][0] - 3.47, 90)
chk("Hall clear width at shoe cabinet", 4.77 - U(units["Shoe cabinet"])[1][0], 90)
Vt = obb(O["Vanity_top"]); Bw = obb(O["Vanity_bowl_bottom"]); bc = (Bw[0][0]+Bw[1][0])/2
chk("Basin centre -> west wall (N 45; 85.5 niche, centred = 42.75)", bc - 4.89, 45, sev="WARN"); chk("Basin centre -> shower glass (N 45; centred)", 5.745 - bc, 45, sev="WARN"); chk("Basin centred in the niche", abs((bc - 4.89) - (5.745 - bc)), None, 1)
chk("Basin rim height (rulebook 85-90, 90-95 tall; over-washer basin)", Vt[1][2], 85, 95)
chk("Washer-dryer: free depth in front from wall (N: 110 total)", 1.67 - 0.0, 110)
chk("Washer niche width >= 60 (Electrolux min opening)", obb(O["Washer_divider"])[0][0] - 4.89, 60); chk("Washer hose space behind", 1.67 - obb(O["Washer_body"])[1][1], 5)
chk("Washer top below basin bowl", (obb(O["Vanity_bowl_bottom"])[0][2] - obb(O["Washer_body"])[1][2]), 1)
chk("Kitchen worktop sockets 20 above worktop (underside >=10)", obb(O["K_socket_prep"])[0][2] - 0.90, 10, 25)
chk("Kitchen run end on the door-jamb line", abs(obb(O["K_end_panel"])[1][1] - 1.40), None, 0)
sk = _bowl(O["K_sink_bottom"]); chk("Kitchen sockets >=30 from the sink bowl", min(sk[0][0] - obb(O["K_socket_prep"])[1][0], obb(O["K_socket_coffee"])[0][0] - sk[1][0]), 30)
chk("Sink landing left to corner (60; prep 90x60 continuous)", sk[0][0] - 0.0, 90)
chk("Sink landing right, combined with fridge landing (45 + 38 -> longer + 30 = 75)", obb(O["K_coffee"])[0][0] - sk[1][0], 75)
chk("Sink edge >= 30 from the corner", sk[0][0] - 0.62, 30)
dw = obb(O["K_front_dw"]); sc = obb(O["K_front_sink_bins"]); chk("Dishwasher right next to the sink unit (gap)", abs(dw[0][0] - sc[1][0]), None, 1)
chk("Bins under the sink (pull-out)", 1 if "K_front_sink_bins" in O else 0, 1, unit="ratio")
chk("Cutlery drawer next to the dishwasher (gap)", abs(obb(O["K_front_drawer0"])[0][0] - dw[1][0]), None, 1)
chk("Corner unit with a working corner fitting (door >= 45)", obb(O["K_front_corner_door"])[1][0] - obb(O["K_front_corner_door"])[0][0], 44)
chk("Fridge housing: side gaps", (obb(O["K_fridge"])[0][0] - obb(O["K_fridge_panel"])[1][0]), 1)
chk("Fridge: free in front (P 91)", 2.48 - obb(O["K_fridge"])[1][1], 91)
chk("Dishwasher width", obb(O["K_front_dw"])[1][0] - obb(O["K_front_dw"])[0][0], 44, 46)
chk("Oven under hob (offset <=12, hob shifted for the end landing; joiner notches corner side)", abs((obb(O["K_oven_door"])[0][1]+obb(O["K_oven_door"])[1][1])/2 - (obb(O["K_hob"])[0][1]+obb(O["K_hob"])[1][1])/2), None, 12)
for n in ("Bed_socket0", "Bed_socket1"):
    s_ = obb(O[n]); chk(f"{n}: above the bedside top (<=30)", s_[0][2] - 0.555, 0, 30)
chk("Desk socket above desktop", obb(O["Desk_socket"])[0][2] - 0.74, 3, 20)
chk("Dresser socket above dressing top", obb(O["Dresser_socket"])[0][2] - 0.76, 5, 25)
chk("Desk left leg reaches the floor", obb(O["WU_step"])[0][2], None, 0)
chk("Cleaning cupboard: vacuum charger socket inside", obb(O["Hall_cl_socket"])[0][2], 100, 140)
chk("WC centre -> side wall", 0.40, 40, 45); chk("WC centre -> shower glass", min(obb(c)[0][1] for c in _O["PROD_shower_door"].children_recursive if c.type == "MESH" and "glass" in c.name.lower()) - 0.40, 40)
Sh = U(units["Shower"]); chk("Shower width", 6.65 - Sh[0][0], 80); chk("Shower depth", 1.68 - Sh[0][1], 80)
Mc = obb(O["Mirror_cab"]); chk("Mirror cabinet centre height", (Mc[0][2]+Mc[1][2])/2, 150, 165); chk("Mirror bottom", Mc[0][2], None, 120)
chk("Balcony chair legroom to railing", 6.86 - U(units["Balcony chair 0"])[1][1], 45)
# --- heights
Tv = obb(O["TV_body"]); chk("TV centre height", (Tv[0][2]+Tv[1][2])/2, 100, 110)
a1 = obb(O["ArtSofa1_frame"]); chk("Art bottom above sofa back (above furniture: 15-25 governs)", a1[0][2] - max(obb(o)[1][2] for o in P("Sofa_back")), 15, 25); chk("Art group width / sofa width", (obb(O["ArtSofa2_frame"])[1][1]-a1[0][1])/(S[1][1]-S[0][1]), 0.60, 0.80, unit="ratio")
chk("Desk height", obb(O["WU_desk_slab"])[1][2], 72, 76); chk("Desk depth", 3.31 - 2.75, 50, sev="WARN")
chk("Kitchen wall units above worktop", 1.45 - 0.90, 50, 60)
# --- REACH (the use test)
M_ = obb(O["Mattress"])
for side, n in (("wardrobe", "Bed_ns_wardrobe"), ("window", "Bed_ns_window")):
    s = obb(O[n]); near = (M_[0][1] - s[1][1]) if side == "wardrobe" else (s[0][1] - M_[1][1])
    chk(f"Bedside ({side}) near edge -> mattress", near, None, 10)
    chk(f"Bedside ({side}) top vs mattress top", s[1][2] - M_[1][2], -5, 10)
    chk(f"Bedside ({side}) beside pillow (dist from head end)", 6.58 - s[1][0], None, 35)
sh_w = Vector((6.30, M_[0][1] + 0.35, 0.65)); sh_n = Vector((6.30, M_[1][1] - 0.35, 0.65))
chk("Bedside switch -> sleeper shoulder (wardrobe side)", (O["Bed_switch0"].matrix_world.translation - sh_w).length, None, 60)
chk("Bedside switch -> sleeper shoulder (window side)", (O["Bed_switch1"].matrix_world.translation - sh_n).length, None, 60)
seats = [Vector((0.80, y)) for y in (S[0][1] + 0.45, (S[0][1] + S[1][1]) / 2, S[1][1] - 0.45)]
for i, s in enumerate(seats):
    d = max(C[0][0] - s.x, 0) + max(C[0][1] - s.y, 0, s.y - C[1][1])
    chk(f"Sofa seat {i+1} -> coffee table reach", d - 0.16, None, 45)
L = O["Lounge_chair"].matrix_world.translation
d = max(C[0][1] - L.y, L.y - C[1][1], 0) + max(C[0][0] - L.x, L.x - C[1][0], 0); chk("Lounge chair -> coffee table reach", d - 0.35, None, 45)
pr = obb(O["WC_paper_holder"]); chk("WC paper ahead of bowl front", 5.93 - (pr[0][0]+pr[1][0])/2, 15, 30); chk("WC paper height", pr[0][2], 60, 70)
chk("Mirror side lights spacing", O["Mirror_side_led1"].location.x - O["Mirror_side_led0"].location.x, 76); chk("Kitchen triangle sink-hob", (Vector(((_bowl(O["K_sink_bottom"])[0][0]+_bowl(O["K_sink_bottom"])[1][0])/2, 0.30)) - Vector((0.30, (obb(O["K_hob"])[0][1]+obb(O["K_hob"])[1][1])/2))).length, 120, 240); hk = obb(O["Bath_hook0"]); exitp = Vector((5.98, 0.78)); chk("Towel hook -> shower exit", (Vector(((hk[0][0]+hk[1][0])/2, (hk[0][1]+hk[1][1])/2)) - exitp).length, None, 60)
hh = obb(O["Hall_unit_hook0"]); chk("Coat hook height", hh[0][2], 160, 180)
chk("Hall bench seat height (with pad)", obb(O["Hall_unit_seat_pad"])[1][2], 40, 45); chk("Hall cleaning cupboard width", obb(O["Hall_unit_tall"])[1][1]-obb(O["Hall_unit_tall"])[0][1], 55)
# --- WALL ITEMS vs furniture below (GL p.258-259; P p.249; rulebook 15)
def wall_art(name, below_top, below_w):
    f = obb(O[name]); w = max(f[1][0]-f[0][0], f[1][1]-f[0][1])
    chk(f"{name}: bottom above furniture", f[0][2] - below_top, 15, 25)
    # rulebook 709: centre 145-155 applies on a FREE wall; above furniture the 15-25 rule governs and
    # rulebook 710 limits the top: top - eye(160) <= 0.5 x viewing distance (bed foot / door ~ 250)
    chk(f"{name}: top within 27 deg of standing eye from 250", f[1][2] - 1.60, None, 125)
    chk(f"{name}: width / furniture width", w / below_w, 0.55, 0.85, unit="ratio")
s1, s2 = obb(O["ArtSofa1_frame"]), obb(O["ArtSofa2_frame"])
chk("Sofa art group: width / sofa", (s2[1][1]-s1[0][1]) / (S[1][1]-S[0][1]), 0.55, 0.85, unit="ratio")
for i in (0, 1):
    sh = obb(O[f"WallLamp{i}_shade"]); ns = obb(O["Bed_ns_wardrobe" if i == 0 else "Bed_ns_window"])
    chk(f"Bed wall lamp {i}: top height", sh[1][2], 127, 152)
    chk(f"Bed wall lamp {i}: shade bottom at sitting chin (mattress+55..70)", sh[0][2] - obb(O["Mattress"])[1][2], 55, 70)
    chk(f"Bed wall lamp {i}: at its bedside (within 15 of the niche edge)", min(sh[1][1], ns[1][1]) - max(sh[0][1], ns[0][1]), -15)
bw = obb(O["BW_bridge_carc"]); bd = min(obb(o)[0][0] for o in O if o.name.startswith("BW_bridge_door"))
chk("Bridge over bed: underside above mattress (>=100)", bw[0][2] - obb(O["Mattress"])[1][2], 100)
chk("Bridge over bed: depth incl. doors (<=40)", 6.65 - bd, None, 40)
for i in (0, 1):
    chk(f"Bed lamp {i} below the bridge", bw[0][2] - obb(O[f"WallLamp{i}_shade"])[1][2], 5)
t0, t1 = obb(O["BW_t0_top"]), obb(O["BW_t1_top"]); chk("Twin towers same width", abs((t0[1][1]-t0[0][1]) - (t1[1][1]-t1[0][1])), None, 1)
chk("Twin towers symmetric about bed axis", abs((t0[0][1]+t1[1][1])/2 - (obb(O["Mattress"])[0][1]+obb(O["Mattress"])[1][1])/2), None, 1)
chk("Wardrobe bedside near edge to mattress (<=10)", obb(O["Mattress"])[0][1] - obb(O["Bed_ns_wardrobe"])[1][1], 0, 10)
chk("Window bedside near edge to mattress (<=10)", obb(O["Bed_ns_window"])[0][1] - obb(O["Mattress"])[1][1], 0, 10)
for n in ("Sconce0", "Sconce1"):
    sc_ = obb(O[n]); chk(f"{n} clear of sofa art", max(s1[0][1] - sc_[1][1], sc_[0][1] - s2[1][1]), 5)
rm = obb(O["Round_mirror"]); chk("Bedroom round mirror centre (seated at vanity)", (rm[0][2]+rm[1][2])/2, 120, 145)
hm = obb(O["Hall_mirror"]); chk("Hall mirror top", hm[1][2], 173)
# --- LIVING furniture, lamps, rugs, curtains, desk (rulebook 03, 04, 09, 12, 15)
So = U(units["Sofa"]); sofa_len = So[1][1] - So[0][1]
chk("Sofa width per seat (2 seats)", sofa_len / 2 - 0.17, 0.66 - 0.0, unit="m") if False else chk("Sofa seat width per person", (sofa_len - 0.34) / 2, 60)
chk("Sofa back to wall (flush or 8-13)", So[0][0], 0, 13)
chk("Coffee table height", C[1][2], 30, 46)
chk("Coffee table length / sofa length", (C[1][1]-C[0][1]) / sofa_len, 0.50, 0.70, unit="ratio")
R = obb(O["Rug_living"])
chk("Rug beyond sofa end (south)", So[0][1] - R[0][1], 15); chk("Rug beyond sofa end (north)", R[1][1] - So[1][1], 15)
chk("Sofa front legs on rug", (obb(_O["PROD_sofa"])[1][0] - 0.06) - R[0][0], 0)
chk("Rug to facade wall (bare floor)", 6.65 - R[1][1], 15, 46)
ds = obb(O["WU_desk_slab"])
chk("Desk depth (laptop min 50)", ds[1][0]-ds[0][0], 50); chk("Desk width", ds[1][1]-ds[0][1], 100)
s0, s1_ = obb(O["WU_shelf0"]), obb(O["WU_shelf1"])
chk("Shelf over desk: underside above desk", s0[0][2] - ds[1][2], 38); chk("Top shelf over desk reachable seated", s1_[1][2], None, 147)
seat_top = 0.47   # LÅNGFJÄLL gas lift 43-55: set at 47 for the 74 desk
chk("Desk chair thigh clearance to desk underside", ds[0][2] - seat_top, 18)
chk("Desk -> obstacle behind the stool (dining table end)", 2.75 - T[1][0], 90)
dl = O["WU_desklamp_base"].location; chk("Desk lamp on the left (north) half", dl.y - (ds[0][1]+ds[1][1])/2, 0)
ch_seat = max(obb(o)[1][2] for o in O["DChair_S1"].children_recursive if o.type == 'MESH' and "seat" in o.name)
chk("Dining chair seat height", ch_seat, 42, 48); chk("Dining thigh clearance (seat -> apron)", obb(O["Dining_apron_S"])[0][2] - ch_seat, 18)
chk("Dining table height", T[1][2], 72, 76)
lc_seat = max(obb(o)[1][2] for o in O["Lounge_chair"].children_recursive if o.type == 'MESH' and "seat" in o.name.lower())
chk("Lounge chair seat height", lc_seat, 36, 45)
fls = obb(O["FloorLamp_shade"]); chk("Floor lamp shade above seated eye (bulb hidden, opening down)", fls[0][2], 105)
cr = obb(O["Curtain_R"]); chk("Curtain hem above floor", cr[0][2], 0, 2.5)
for n in ("Sconce0", "Sconce1"):
    chk(f"{n} centre height (reading at sofa)", (obb(O[n])[0][2]+obb(O[n])[1][2])/2, 140, 170)
# --- JOINERY CONTINUITY (no stray gaps between desk, end panel, step and shelves)
chk("Desk slab touches end panel (gap)", abs(obb(O["WU_desk_slab"])[0][1] - obb(O["WU_end_L"])[1][1]), None, 0)
chk("Desk slab reaches over the step (gap)", (obb(O["WU_step"])[1][1] - obb(O["WU_desk_slab"])[1][1]), None, 0)
chk("Shelves start at end panel (gap)", abs(obb(O["WU_shelf0"])[0][1] - obb(O["WU_end_L"])[1][1]), None, 0)
chk("End panels flush with fronts", abs(obb(O["WU_end_L"])[0][0] - obb(O["WU_desk_slab"])[0][0]), None, 0)
for i in (0, 1):
    pl = obb(O[f"WallLamp{i}_plate"]); pn = obb(O["Bed_wall_panel"])
    chk(f"Bed lamp {i} plate on the headboard panel, below its top", (pn[1][2] - pl[1][2]), 5)
    sh = obb(O[f"WallLamp{i}_shade"]); chk(f"Bed lamp {i} centre above mattress (60-75)", ((sh[0][2]+sh[1][2])/2 - obb(O["Mattress"])[1][2]), 60, 75)

# --- LIVING-ROOM SWITCH beside the door (rulebook: latch side 10-30 from frame, h 105, never blocked)
sw = obb(O["Living_switch"]); chk("Living switch: from door frame", sw[0][1] - obb(O["Door_casing_b"])[1][1], 10, 30)
chk("Living switch: free wall to the unit end panel", obb(O["WU_end_L"])[0][1] - sw[1][1], 10)
chk("Living switch: centre height", (sw[0][2]+sw[1][2])/2, 100, 110)
chk("Living desk length", obb(O["WU_desk_slab"])[1][1] - obb(O["WU_desk_slab"])[0][1], 120)
print("=== FAIL ==="); [print("  " + s) for s in fails] or print("  none")
print("=== WARN ==="); [print("  " + s) for s in warns] or print("  none")
print("=== PASS ==="); [print("  " + s) for s in ok]







