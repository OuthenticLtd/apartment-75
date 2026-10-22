"""GROHE Tempesta System 250 shower system with thermostat, matt black (26671 2431 / 266712431)."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bc_common as C
from mathutils import Vector

KEY = "shower_tempesta"
C.reset(KEY)

blk = C.mat("matt black", (0.03, 0.03, 0.032), rough=0.45, metal=0.35)
hosem = C.mat("hose", (0.03, 0.03, 0.03), rough=0.55, metal=0.2)
face = C.mat("spray face", (0.015, 0.015, 0.016), rough=0.7)
nozz = C.mat("nozzles", (0.06, 0.06, 0.065), rough=0.6)
red = C.mat("temp mark", (0.75, 0.08, 0.05), rough=0.5)
logo = C.mat("logo", (0.35, 0.35, 0.36), rough=0.35, metal=0.8)

ZM = 0.455          # mixer axis above the origin (lowest point of the hose loop)
YM = -0.068         # mixer / riser axis distance from wall
# ---------------- thermostatic bar mixer (298 mm with handles)
C.cyl("mixer_body", 0.026, 0.178, (0, YM, ZM), blk, axis='X', verts=40, bev=0.002)
for s, nm in ((-1, "flow"), (1, "temp")):
    C.cyl(f"handle_{nm}", 0.030, 0.060, (s * (0.089 + 0.030), YM, ZM), blk, axis='X', verts=40, bev=0.004)
    # grip ring groove
    C.cyl(f"handle_{nm}_ring", 0.0305, 0.004, (s * (0.089 + 0.006), YM, ZM), face, axis='X', verts=40)
C.box("temp_mark", (0.003, 0.0012, 0.010), (0.112, YM - 0.0302, ZM + 0.004), red)
C.box("logo", (0.024, 0.0008, 0.004), (0.0, YM - 0.0262, ZM + 0.010), logo)
# S-unions + escutcheons (150 mm c/c)
for s in (-1, 1):
    x = s * 0.075
    C.cyl(f"escutcheon_{'l' if s < 0 else 'r'}", 0.035, 0.012, (x, -0.006, ZM), blk, axis='Y', verts=40, bev=0.003)
    C.cyl(f"union_{'l' if s < 0 else 'r'}", 0.012, -YM - 0.01, (x, (YM - 0.01) / 2 - 0.004, ZM), blk, axis='Y', verts=24)
# bottom outlet (to hose) and top outlet (to riser)
C.cyl("outlet_hose", 0.011, 0.030, (0, YM, ZM - 0.026 - 0.012), blk, axis='Z', verts=24, bev=0.001)
# ---------------- riser rail with top bend into the shower arm (1120 mm to top of arm)
r_riser = 0.0125
ZTOP = ZM + 1.120 - r_riser
YH = -0.408          # head centre from wall
pts = [(0, YM, ZM + 0.02), (0, YM, ZTOP), (0, YH, ZTOP)]
C.tube("riser_and_arm", C.fillet(pts, 0.085, 12), r_riser, blk, res=24)
# top wall bracket (1010 mm above mixer axis)
ZB = ZM + 1.010
C.cyl("bracket_rosette", 0.026, 0.012, (0, -0.006, ZB), blk, axis='Y', verts=32, bev=0.003)
C.cyl("bracket_arm", 0.010, -YM - 0.012, (0, (YM - 0.012) / 2 - 0.004, ZB), blk, axis='Y', verts=20)
C.cyl("bracket_collar", 0.020, 0.040, (0, YM, ZB), blk, axis='Z', verts=32, bev=0.003)
# ---------------- head shower 250 mm, slim disc hanging from the arm via ball joint
ZHtop = ZTOP - 0.022
C.sphere("head_joint", 0.016, (0, YH, ZTOP - 0.012), blk, segs=24, rings=12)
C.cyl("head_neck", 0.012, 0.018, (0, YH, ZHtop - 0.004), blk, axis='Z', verts=24)
prof = [(0.0, -0.016), (0.10, -0.016), (0.121, -0.0145), (0.125, -0.010), (0.125, -0.006), (0.115, 0.0),
        (0.05, 0.007), (0.016, 0.010), (0.0, 0.010)]
C.lathe("head", [(r, h) for (r, h) in prof], blk, loc=(0, YH, ZHtop - 0.016), segs=64)
C.cyl("head_spray_face", 0.104, 0.0015, (0, YH, ZHtop - 0.016 - 0.0164 - 0.0007), face, axis='Z', verts=64)
# nozzle rings (merged into one mesh of small studs)
import bmesh
bm = bmesh.new()
for ring_r, n in ((0.03, 10), (0.055, 18), (0.08, 26)):
    for k in range(n):
        a = 2 * math.pi * k / n
        cx, cy = ring_r * math.cos(a), YH + ring_r * math.sin(a)
        geom = bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.0028, radius2=0.0028, depth=0.002)
        bmesh.ops.translate(bm, vec=Vector((cx, cy, ZHtop - 0.016 - 0.018)), verts=geom['verts'])
C.from_bm("head_nozzles", bm, nozz)
# ---------------- slider + hand shower 110 mm
ZS = ZM + 0.600
C.cyl("slider", 0.019, 0.042, (0, YM, ZS), blk, axis='Z', verts=32, bev=0.004)
C.box("slider_cradle", (0.030, 0.040, 0.034), (0.0, YM - 0.038, ZS), blk, bev=0.008, segs=3)
# hand shower: handle in cradle, tilted forward; head disc at top facing front
hb = Vector((0.0, YM - 0.050, ZS - 0.095))    # handle bottom (hose connection)
ht = Vector((0.0, YM - 0.072, ZS + 0.090))    # top of handle / head centre
C.tube("hand_handle", [hb, hb.lerp(ht, 0.5) + Vector((0, -0.002, 0)), ht], 0.0135, blk, res=24)
C.cyl("hand_handle_end", 0.0105, 0.016, (hb.x, hb.y, hb.z - 0.006), blk, axis='Z', verts=20)
# head: ellipsoid-ish disc 110 mm, axis tilted ~20 deg down toward -Y
hc = ht + Vector((0, -0.006, 0.040))
headob = C.lathe("hand_head", [(0.0, -0.012), (0.045, -0.012), (0.055, -0.006), (0.055, 0.004), (0.045, 0.012), (0.0, 0.014)],
                 blk, loc=(0, 0, 0), segs=48, axis='Y')
faceob = C.cyl("hand_spray_face", 0.044, 0.002, (0, -0.0125, 0), face, axis='Y', verts=48)
for ob in (headob, faceob):
    from mathutils import Matrix
    M = Matrix.Translation(hc) @ Matrix.Rotation(math.radians(-18), 4, 'X')
    ob.data.transform(M)
# ---------------- hose 1750 mm: from mixer bottom outlet, loop down, up in front of the mixer to the handle
def catmull(ctrl, n=10):
    P = [Vector(p) for p in ctrl]
    P = [P[0] + (P[0] - P[1])] + P + [P[-1] + (P[-1] - P[-2])]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-2])
    return out
r_h = 0.0085
hose_ctrl = [(0, YM, ZM - 0.050), (-0.012, YM - 0.010, ZM - 0.20), (-0.030, YM - 0.030, ZM - 0.36),
             (0.010, YM - 0.045, r_h), (0.055, YM - 0.050, 0.07), (0.045, YM - 0.058, ZM - 0.15),
             (0.022, YM - 0.060, ZM + 0.10), (0.008, YM - 0.054, ZM + 0.35), (hb.x, hb.y, hb.z - 0.014)]
C.tube("hose", catmull(hose_ctrl, 10), r_h, hosem, res=14)

C.recenter("wall")
C.finish(KEY, "GROHE Tempesta System 250 shower system with Grohtherm thermostat, matt black (266712431)", (0.298, 0.533, ZM + 1.120), "wall",
         "Origin = centre of back face at the lowest point of the hanging hose loop; thermostat mixer axis is 0.455 m above origin (S-unions 150 mm c/c), top of arm 1.12 m above mixer axis, head d250 centred 408 mm from wall, hand shower d110 on slider (1750 mm hose). Heights per GROHE dimension drawing.",
         views=[((0.9, -1.0, 0.35), "")])
