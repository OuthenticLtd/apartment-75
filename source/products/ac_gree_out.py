"""Gree GWHD(18)NK6LOO multi-split outdoor unit (Free Match), 899 x 378 x 596."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bc_common as C

KEY = "ac_gree_out"
C.reset(KEY)
W, D, H = 0.899, 0.378, 0.596

case = C.mat("casing", (0.88, 0.885, 0.875), rough=0.45)
grille = C.mat("grille", (0.80, 0.80, 0.79), rough=0.5)
dark = C.mat("fan opening", (0.05, 0.05, 0.055), rough=0.7)
fan = C.mat("fan", (0.12, 0.12, 0.13), rough=0.6)
coil = C.mat("coil", (0.55, 0.57, 0.58), rough=0.4, metal=0.6)
feetm = C.mat("feet", (0.80, 0.80, 0.79), rough=0.5)
blue = C.mat("logo blue", (0.01, 0.07, 0.36), rough=0.4)
red = C.mat("logo red", (0.75, 0.10, 0.03), rough=0.4)
valve = C.mat("valves", (0.70, 0.62, 0.40), rough=0.35, metal=0.9)
screw = C.mat("screws", (0.5, 0.5, 0.5), rough=0.3, metal=0.8)

FOOT_H = 0.028
CW = 0.860            # casing width (service cover adds to the right)
CD = 0.330            # casing depth
x0 = -W / 2           # casing spans x0 .. x0+CW
cx = x0 + CW / 2
yc = -0.024 - CD / 2  # casing centred so feet stick out at back/front
# feet: two pressed-steel rails across the depth (they set the overall depth 378)
for i, fx in enumerate((x0 + 0.13, x0 + CW - 0.16)):
    C.box(f"foot_{i}", (0.055, D, FOOT_H), (fx, -D / 2, FOOT_H / 2), feetm, bev=0.003, segs=1)
    # bolt slots at ends
# casing
C.box("casing", (CW, CD, H - FOOT_H - 0.004), (cx, yc, FOOT_H + 0.002 + (H - FOOT_H - 0.004) / 2), case, bev=0.008, segs=3)
yfront = yc - CD / 2
ytop = H - 0.002
# top lid (slight overhang)
C.box("top_lid", (CW - 0.001, CD + 0.004, 0.012), (cx, yc, H - 0.006), case, bev=0.004, segs=2)

# front: large square fan grille on the left
gx0, gx1 = x0 + 0.040, x0 + 0.040 + 0.575
gz0, gz1 = FOOT_H + 0.040, H - 0.050
gcx, gcz = (gx0 + gx1) / 2, (gz0 + gz1) / 2
# recessed dark fan opening (circle) behind grille
C.cyl("fan_opening", 0.245, 0.006, (gcx, yfront + 0.001, gcz), dark, axis='Y', verts=48)
# fan hub + 3 blades
C.cyl("fan_hub", 0.055, 0.03, (gcx, yfront + 0.03, gcz), fan, axis='Y', verts=24)
for k in range(3):
    a = 2 * math.pi * k / 3 + 0.4
    pts = []
    for j in range(9):
        t = j / 8
        r = 0.06 + 0.17 * t
        ang = a + 0.9 * math.sin(math.pi * t) * 0.6 + t * 0.5
        w = 0.05 + 0.06 * math.sin(math.pi * t)
        pts.append((r, ang, w))
    # blade as thin quad strip extruded slightly
    import bmesh
    from mathutils import Vector
    bm = bmesh.new()
    top, bot = [], []
    for (r, ang, w) in pts:
        for s, lst in ((1, top), (-1, bot)):
            aa = ang + s * w / max(r, 0.05) * 0.5
            lst.append(bm.verts.new(Vector((gcx + r * math.cos(aa), yfront + 0.035 + s * 0.008, gcz + r * math.sin(aa)))))
    for j in range(len(pts) - 1):
        bm.faces.new((top[j], top[j + 1], bot[j + 1], bot[j]))
    C.from_bm(f"fan_blade_{k}", bm, fan)
# grille frame + wire grid (vertical and horizontal wires)
fr = 0.012
C.box("grille_frame_t", (gx1 - gx0, 0.008, fr), (gcx, yfront - 0.004, gz1 - fr / 2), grille, bev=0.002, segs=1)
C.box("grille_frame_b", (gx1 - gx0, 0.008, fr), (gcx, yfront - 0.004, gz0 + fr / 2), grille, bev=0.002, segs=1)
C.box("grille_frame_l", (fr, 0.008, gz1 - gz0), (gx0 + fr / 2, yfront - 0.004, gcz), grille, bev=0.002, segs=1)
C.box("grille_frame_r", (fr, 0.008, gz1 - gz0), (gx1 - fr / 2, yfront - 0.004, gcz), grille, bev=0.002, segs=1)
nv = 44
for i in range(1, nv):
    x = gx0 + (gx1 - gx0) * i / nv
    C.box(f"grille_v_{i:02d}", (0.0028, 0.0028, gz1 - gz0 - 0.004), (x, yfront - 0.007, gcz), grille)
nh = 22
for i in range(1, nh):
    z = gz0 + (gz1 - gz0) * i / nh
    C.box(f"grille_h_{i:02d}", (gx1 - gx0 - 0.004, 0.0028, 0.0028), (gcx, yfront - 0.0042, z), grille)
# join grid wires into one object to keep the outliner clean
import bpy
wires = [o for o in bpy.data.objects if o.name.startswith(KEY + "_grille_")]
ctx = {"active_object": wires[0], "selected_editable_objects": wires}
with bpy.context.temp_override(active_object=wires[0], selected_editable_objects=wires, selected_objects=wires):
    bpy.ops.object.join()
wires[0].name = KEY + "_grille"; wires[0].data.name = KEY + "_grille"

# front right panel: Gree logo (blue disc with red/white swoosh) + wordmark
lx = x0 + 0.040 + 0.575 + (CW - 0.615 - 0.04) / 2 + 0.02
C.cyl("logo_disc", 0.034, 0.002, (lx, yfront - 0.001, H - 0.150), blue, axis='Y', verts=32)
C.box("logo_swoosh", (0.040, 0.0025, 0.014), (lx + 0.004, yfront - 0.0016, H - 0.150), red, bev=0.003, segs=1)
for i, lw in enumerate((0.015, 0.014, 0.013, 0.013)):
    C.box(f"logo_letter_{i}", (lw, 0.0015, 0.022), (lx - 0.033 + i * 0.022, yfront - 0.0008, H - 0.215), blue, bev=0.002, segs=1)
# subtle front panel seam (right panel is a separate cover)
C.box("front_seam", (0.003, 0.0015, H - FOOT_H - 0.08), (x0 + 0.640, yfront - 0.0008, (H + FOOT_H) / 2), dark)

# screws along top front edge
for sx_ in (x0 + 0.12, x0 + 0.43, x0 + 0.76):
    C.cyl(f"screw_{sx_:.2f}", 0.004, 0.002, (sx_, yfront - 0.001, H - 0.025), screw, axis='Y', verts=12)

# right side: service (valve) cover protruding from the side, lower-rear area
sc_x = x0 + CW
C.box("service_cover", (W - CW, 0.17, 0.20), (sc_x + (W - CW) / 2, yc + 0.02, FOOT_H + 0.20), case, bev=0.008, segs=3)
C.box("service_cover_top", (W - CW - 0.004, 0.16, 0.12), (sc_x + (W - CW) / 2 - 0.002, yc + 0.02, FOOT_H + 0.355), case, bev=0.010, segs=3)
# valves visible under the cover
for i in range(2):
    C.cyl(f"valve_{i}", 0.009, 0.03, (sc_x + 0.012, yc - 0.04 + i * 0.05, FOOT_H + 0.075), valve, axis='X', verts=16)

# back: exposed condenser coil (fin grid colour)
C.box("coil_back", (CW - 0.06, 0.004, H - FOOT_H - 0.10), (cx - 0.02, yc + CD / 2 + 0.001, (H + FOOT_H) / 2), coil)
# left side coil window
C.box("coil_left", (0.002, CD - 0.08, H - FOOT_H - 0.12), (x0 + 0.0005, yc + 0.02, (H + FOOT_H) / 2), coil)

C.recenter("floor")
C.finish(KEY, "Gree GWHD(18)NK6LOO multi-split outdoor unit (Free Match), white", (W, D, H), "floor",
         "Origin = centre of footprint at floor (bottom of feet). Front (fan grille, left) faces -Y. Width includes the right-side valve/service cover; depth includes the foot rails. Back and left side show the condenser coil.")
