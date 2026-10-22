import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bedhall_common as C
from mathutils import Vector
C.reset("stool_kyrre")
H = 0.45; ST = 0.02
wood = C.mat("birch", C.hexcol("DABE9F"), rough=0.55)
edge = C.mat("ply edge", C.hexcol("D2B48F"), rough=0.6)
ANG = [0, 120, 240]          # leg directions (deg from +X); one corner points to +X
# seat: soft triangle, corners toward legs
def seat_r(t):
    return 0.168 * (1 + 0.13 * math.cos(3 * t)) / (1 + 0.13) * 1.13
pts = []
for i in range(120):
    t = 2 * math.pi * i / 120
    pts.append((seat_r(t) * math.cos(t), seat_r(t) * math.sin(t)))
seat = C.extrude_outline("seat", pts, H - ST, H, wood)
seat.data.materials.append(edge)
for p in seat.data.polygons:
    p.material_index = 1 if abs(p.normal.z) < 0.5 else 0
    p.use_smooth = abs(p.normal.z) < 0.5
C.add_bevel(seat, 0.004, 3)
# legs: bent plywood strips
LW, LT = 0.042, 0.019
for k, a in enumerate(ANG):
    u = Vector((math.cos(math.radians(a)), math.sin(math.radians(a)), 0))
    side = Vector((-u.y, u.x, 0))
    ztop = H - ST - LT / 2
    r0, r1, rb = 0.035, 0.150, 0.045       # start radius, bend start, bend radius
    rf = 0.2585                             # foot centre radius
    # direction of the straight leg from bend end to foot
    p = [u * r0 + Vector((0, 0, ztop)), u * (r1 * 0.5) + Vector((0, 0, ztop)), u * r1 + Vector((0, 0, ztop))]
    # bend: rotate from horizontal (u) to down-and-out direction
    foot = u * rf + Vector((0, 0, LT * 0.0))
    # iterate to find leg direction tangent to bend circle
    dirv = (foot - (u * (r1 + rb) + Vector((0, 0, ztop)))).normalized()
    for _ in range(20):
        ang = math.atan2(-dirv.z, dirv.dot(u))     # angle below horizontal
        cen = u * r1 + Vector((0, 0, ztop - rb))
        endp = cen + rb * (u * math.sin(ang) + Vector((0, 0, math.cos(ang))))
        dirv = (foot - endp).normalized()
    n = 8
    for i in range(1, n + 1):
        b = ang * i / n
        p.append(cen + rb * (u * math.sin(b) + Vector((0, 0, math.cos(b)))))
    p.append(endp + (foot - endp) * 0.5)
    p.append(foot + (foot - endp).normalized() * 0.012)
    leg = C.sweep_rect(f"leg{k+1}", p, side, LW, LT, wood)
    C.add_bevel(leg, 0.003, 2)
    # trim foot flat to floor: extend last point slightly below and clamp z
    for v in leg.data.vertices:
        if v.co.z < 0.0:
            v.co.z = 0.0
C.apply_all()
C.center_xy()
C.preview(azim=-30, elev=20)
C.save()
