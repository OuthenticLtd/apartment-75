import sys, os, math, bpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bedhall_common as C
from mathutils import Vector
C.reset("pendant_oracle")
body = C.mat("body white", C.hexcol("F2F2F0"), rough=0.4, metal=0.0)
# 2700 K warm white
diff = C.mat("diffuser", C.hexcol("FBF8F2"), rough=0.35, emission=(1.0, 0.68, 0.40), estrength=6.0)
steel = C.mat("steel cable", (0.7, 0.7, 0.72), rough=0.3, metal=1.0)
cordm = C.mat("cord", C.hexcol("EDEDED"), rough=0.6)
RO, RI = 0.250, 0.228          # ring outer / inner radius (50 cm)
ZB, HT = -0.220, 0.025         # bottom 22 cm below ceiling, profile height 25 mm
ZT = ZB + HT
c = 0.002
# aluminium profile (U shape open at the bottom, diffuser closes it)
prof = [(RI + 0.0015, ZB + 0.0015), (RI, ZB + 0.002), (RI, ZT - c), (RI + c, ZT), (RO - c, ZT), (RO, ZT - c),
        (RO, ZB + 0.002), (RO - 0.0015, ZB + 0.0015)]
C.lathe("ring", prof, body, segs=128)
C.lathe("diffuser", [(RO - 0.0015, ZB + 0.0015), (RO - 0.002, ZB), (RI + 0.002, ZB), (RI + 0.0015, ZB + 0.0015)][::-1], diff, segs=128)
# canopy (driver box) 230 x 65 mm, at the ceiling over the origin
C.box("canopy", (0.230, 0.065, 0.030), (0, 0, -0.015), body, bevel=0.003, segs=3)
# two steel suspension cables to small ceiling anchors at the ring's left/right
rm = (RO + RI) / 2
for sx in (-1, 1):
    C.cyl(f"anchor_{'l' if sx<0 else 'r'}", 0.007, 0.018, (sx*rm, 0, -0.009), body, verts=16)
    C.tube_path(f"cable_{'l' if sx<0 else 'r'}", [Vector((sx*rm, 0, -0.018)), Vector((sx*rm, 0, ZT))], 0.0006, steel, sides=6)
    C.cyl(f"gripper_{'l' if sx<0 else 'r'}", 0.0028, 0.012, (sx*rm, 0, ZT + 0.006), steel, verts=10)
# power cord: from the canopy along the ceiling to an anchor above the ring's back, then down
C.cyl("anchor_cord", 0.007, 0.018, (0, rm, -0.009), body, verts=16)
C.tube_path("cord", [Vector((0, 0.0325, -0.004)), Vector((0, 0.06, -0.0035)), Vector((0, rm - 0.012, -0.0035)), Vector((0, rm - 0.007, -0.006))], 0.002, cordm, sides=8)
C.tube_path("cord_drop", [Vector((0, rm, -0.018)), Vector((0, rm, ZT))], 0.0012, cordm, sides=6)


def light(h):
    pass


C.preview(floor=False, azim=-30, elev=-18, target=(0, 0, -0.12))
C.save()
