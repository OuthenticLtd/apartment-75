import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bedhall_common as C
from mathutils import Vector
C.reset("lantern_borrby")
blk = C.mat("black steel", C.hexcol("1b1b1b"), rough=0.5, metal=0.4)
gls = C.mat("glass", (0.85, 0.9, 0.9), rough=0.03, alpha=0.18)
wax = C.mat("tealight wax", C.hexcol("F4F1EA"), rough=0.6)
alu = C.mat("tealight cup", (0.8, 0.8, 0.8), rough=0.3, metal=1.0)
cm = 0.01
B = 11*cm
parts = []
# base plate with slight raised edge
parts.append(C.box("b1", (B, B, 0.4*cm), (0, 0, 0.2*cm), blk, bevel=0.0015))
parts.append(C.box("b2", (9.8*cm, 9.8*cm, 0.25*cm), (0, 0, 0.5*cm), blk, bevel=0.001))
# body
S = 9.2*cm; zb, zg = 0.6*cm, 10.6*cm
P = 0.55*cm
for sx in (-1, 1):
    for sy in (-1, 1):
        parts.append(C.box("post", (P, P, zg + 2.0*cm - zb), (sx*(S/2 - P/2), sy*(S/2 - P/2), (zb + zg + 2.0*cm)/2), blk))
# frame rails top/bottom on each side
for z in (zb + 0.25*cm, zg):
    for s in (-1, 1):
        parts.append(C.box("rail", (S, 0.25*cm, 0.5*cm), (0, s*(S/2 - 0.125*cm), z), blk))
        parts.append(C.box("rail", (0.25*cm, S, 0.5*cm), (s*(S/2 - 0.125*cm), 0, z), blk))
# front door frame (slightly proud), hinge + latch
fy = -S/2 - 0.12*cm
dz0, dz1 = zb + 0.1*cm, zg + 0.2*cm
for x in (-(S/2 - 0.45*cm), S/2 - 0.45*cm):
    parts.append(C.box("door", (0.5*cm, 0.25*cm, dz1 - dz0), (x, fy, (dz0 + dz1)/2), blk))
for z in (dz0 + 0.25*cm, dz1 - 0.25*cm):
    parts.append(C.box("door", (S - 0.4*cm, 0.25*cm, 0.5*cm), (0, fy, z), blk))
parts.append(C.box("latch", (0.35*cm, 0.15*cm, 1.4*cm), (-S/2 - 0.1*cm, fy - 0.05*cm, 5.2*cm), blk))
for z in (2.2*cm, 9.0*cm):
    parts.append(C.cyl("hinge", 0.18*cm, 1.2*cm, (S/2 + 0.05*cm, fy, z), blk, verts=8))
# vent band with vertical slots
zv0, zv1 = zg + 0.25*cm, zg + 2.0*cm
nb = 6
for s in (-1, 1):
    for i in range(nb):
        t = -S/2 + P + (S - 2*P) * (i + 0.5) / nb
        parts.append(C.box("bar", (0.42*cm, 0.2*cm, zv1 - zv0), (t, s*(S/2 - 0.1*cm), (zv0 + zv1)/2), blk))
        parts.append(C.box("bar", (0.2*cm, 0.42*cm, zv1 - zv0), (s*(S/2 - 0.1*cm), t, (zv0 + zv1)/2), blk))
# roof plate
zr = zv1
parts.append(C.box("roof", (B, B, 0.3*cm), (0, 0, zr + 0.15*cm), blk, bevel=0.001))
# chimney cap with slots
Cw = 4.9*cm; zc0, zc1 = zr + 0.3*cm, zr + 3.0*cm
for sx in (-1, 1):
    for sy in (-1, 1):
        parts.append(C.box("cpost", (0.5*cm, 0.5*cm, zc1 - zc0), (sx*(Cw/2 - 0.25*cm), sy*(Cw/2 - 0.25*cm), (zc0 + zc1)/2), blk))
for s in (-1, 1):
    for z in (zc0 + 0.25*cm, zc1 - 0.35*cm):
        parts.append(C.box("crail", (Cw, 0.2*cm, 0.5*cm), (0, s*(Cw/2 - 0.1*cm), z), blk))
        parts.append(C.box("crail", (0.2*cm, Cw, 0.5*cm), (s*(Cw/2 - 0.1*cm), 0, z), blk))
    for i in range(3):
        t = -Cw/2 + 0.5*cm + (Cw - 1.0*cm) * (i + 0.5) / 3
        parts.append(C.box("cbar", (0.4*cm, 0.2*cm, zc1 - zc0), (t, s*(Cw/2 - 0.1*cm), (zc0 + zc1)/2), blk))
        parts.append(C.box("cbar", (0.2*cm, 0.4*cm, zc1 - zc0), (s*(Cw/2 - 0.1*cm), t, (zc0 + zc1)/2), blk))
parts.append(C.box("clid", (5.5*cm, 5.5*cm, 0.25*cm), (0, 0, zc1 + 0.125*cm), blk, bevel=0.0008))
C.join(parts, "body")
# handle ring (round wire, vertical plane XZ), hinged at cap lid
R = 2.9*cm; zt = 20*cm - 0.18*cm
cz = zt - R
pts = [Vector((R*math.cos(a), 0.6*cm, cz + R*math.sin(a))) for a in [2*math.pi*i/40 for i in range(40)]]
C.tube_path("handle", pts, 0.18*cm, blk, sides=8, closed=True)
for x in (-0.8*cm, 0.8*cm):
    pass
# glass panes
gt = 0.2*cm
for s in (-1, 1):
    C.box(f"glass_{'front' if s<0 else 'back'}", (S - 0.6*cm, gt, zg - zb), (0, s*(S/2 - 0.35*cm), (zb + zg)/2), gls)
    C.box(f"glass_{'left' if s<0 else 'right'}", (gt, S - 0.6*cm, zg - zb), (s*(S/2 - 0.35*cm), 0, (zb + zg)/2), gls)
# tealight in glass cup
C.lathe("holder_glass", [(0, zb), (2.7*cm, zb), (2.9*cm, zb + 1.6*cm), (2.75*cm, zb + 1.6*cm), (2.55*cm, zb + 0.25*cm), (0, zb + 0.25*cm)], gls, segs=32)
C.cyl("tealight_cup", 1.95*cm, 1.5*cm, (0, 0, zb + 0.25*cm + 0.75*cm), alu, verts=24)
C.cyl("tealight_wax", 1.85*cm, 0.05*cm, (0, 0, zb + 0.25*cm + 1.35*cm), wax, verts=24)
C.cyl("wick", 0.05*cm, 0.5*cm, (0, 0, zb + 1.6*cm + 0.25*cm), blk, verts=6)
C.center_xy()
C.preview(azim=-28, elev=18)
C.save()
