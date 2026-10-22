import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
from mathutils import Vector, Matrix
import plib
from plib import box, mat, obj_from_bm, rounded_box_bm, add_bevel

KEY = "armchair_ekenaset"
cm = 0.01
plib.reset()
R = plib.root(KEY)

FAB = mat(KEY + " fabric", (192, 182, 168), rough=0.95)
OAK = mat(KEY + " oak", (186, 140, 90), rough=0.5)

W, D, H = 65.0, 74.0, 75.0
SEAT_H = 44.0
ARM_TOP = 57.5
ARM_T = 2.4
ARM_W = 5.6
XF = W / 2 - ARM_W / 2          # frame centre-line x
LEG_W, LEG_D = 3.4, 4.0          # leg section (x, along-member)


def beam(name, p0, p1, sx, sy, material, bev=0.6, up=Vector((1, 0, 0))):
    """Rectangular member from p0 to p1 (cm); sx along 'up' (x), sy the other side."""
    p0, p1 = Vector(p0), Vector(p1)
    ax = (p1 - p0)
    L = ax.length
    zt = ax.normalized()
    xt = (up - up.dot(zt) * zt).normalized()
    yt = zt.cross(xt)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * sx, v.co.y * sy, (v.co.z + 0.5) * L))
    M = Matrix((xt, yt, zt)).transposed().to_4x4()
    M.translation = p0
    bm.transform(Matrix.Scale(cm, 4) @ M)
    ob = obj_from_bm(name, bm, R, material)
    add_bevel(ob, bev * cm, 3, angle=30)
    return ob


def clip_floor(ob):
    """Cut a beam flat at z=0 and at a given top plane via bisect (applied in mesh)."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 0),
                           plane_no=(0, 0, -1), clear_outer=True)
    bmesh.ops.holes_fill(bm, edges=bm.edges[:], sides=0)
    bm.to_mesh(ob.data)
    bm.free()


def arm_board(name, x, y0, y1, z_top):
    """Flat armrest with rounded front end (plan view), slight flare at the front."""
    bm = bmesh.new()
    r = ARM_W / 2
    n = 12
    pts = [(x + r * 0.9, y1), (x - r * 0.9, y1)]
    for i in range(n + 1):
        a = math.pi - math.pi * i / n  # 180 -> 0 : left to right through the front (-y)
        pts.append((x + r * math.cos(a), y0 + r - r * math.sin(a)))
    verts_b = [bm.verts.new(((px) * cm, py * cm, (z_top - ARM_T) * cm)) for px, py in pts]
    verts_t = [bm.verts.new(((px) * cm, py * cm, z_top * cm)) for px, py in pts]
    m = len(pts)
    bm.faces.new(list(reversed(verts_b)))
    bm.faces.new(verts_t)
    for i in range(m):
        j = (i + 1) % m
        bm.faces.new((verts_b[i], verts_b[j], verts_t[j], verts_t[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    ob = obj_from_bm(name, bm, R, OAK)
    md = add_bevel(ob, 0.6 * cm, 3, angle=50)
    return ob


# ---------------- side frames ----------------
for side, s in (("L", -1), ("R", 1)):
    x = s * XF
    # front leg: slightly splayed forward at the foot
    beam(f"{KEY}_leg_front_{side}", (x, -29.3, -2.0), (x, -25.3, ARM_TOP - ARM_T + 0.3), LEG_W, LEG_D, OAK)
    # rear leg: foot well back, top under the rear end of the arm
    beam(f"{KEY}_leg_rear_{side}", (x, 35.0, -2.0), (x, 25.2, 30.5), LEG_W, LEG_D, OAK)
    # angled rear arm support: from the side-rail joint up to the arm's back end
    beam(f"{KEY}_arm_support_{side}", (x, 26.2, 25.0), (x, 19.8, ARM_TOP - ARM_T + 0.3), LEG_W, LEG_D * 0.9, OAK)
    # side seat rail
    beam(f"{KEY}_rail_side_{side}", (x, -26.0, 27.5), (x, 26.0, 27.5), 2.6, 6.0, OAK, up=Vector((1, 0, 0)))
    # armrest
    arm_board(f"{KEY}_arm_{side}", x, -D / 2, 22.5, ARM_TOP)

# floor cut for leg feet
for ob in list(R.children):
    if "leg" in ob.name:
        clip_floor(ob)

# front & back rails (under the seat)
xin = XF - 2.6 / 2
beam(f"{KEY}_rail_front", (-xin - 0.5, -24.5, 27.0), (xin + 0.5, -24.5, 27.0), 2.4, 7.0, OAK, up=Vector((0, 1, 0)))
beam(f"{KEY}_rail_back", (-xin - 0.5, 24.0, 27.5), (xin + 0.5, 24.0, 27.5), 2.4, 6.0, OAK, up=Vector((0, 1, 0)))

# ---------------- seat cushion ----------------
SW = 2 * (XF - LEG_W / 2) - 0.6     # between the side frames
ST = 13.5
SD = 47.5


def cushion(sx, sy, sz, r, bulge, res):
    bm = rounded_box_bm(sx, sy, sz, r, *res)
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    for v in bm.verts:
        if v.co.z > 0:
            ex = max(0.0, 1 - (abs(v.co.x) / hx) ** 4)
            ey = max(0.0, 1 - (abs(v.co.y) / hy) ** 4)
            w = max(0.0, min(1.0, (v.co.z - (hz - r)) / r))
            v.co.z += bulge * ex * ey * w
    return bm


bm = cushion(SW * cm, SD * cm, ST * cm, 3.6 * cm, 1.0 * cm, (26, 24, 6))
seat = obj_from_bm(f"{KEY}_seat_cushion", bm, R, FAB)
seat.location = (0, (-27.0 + SD / 2) * cm, (SEAT_H - 0.8 - ST / 2) * cm)

# ---------------- backrest ----------------
BH, BT = 41.1, 15.0
tilt = math.radians(14)
bm = cushion(SW * cm, BH * cm, BT * cm, 4.2 * cm, 1.6 * cm, (26, 22, 6))
back = obj_from_bm(f"{KEY}_back_cushion", bm, R, FAB)
Rm = Matrix.Rotation(-tilt, 4, 'X') @ Matrix.Rotation(math.radians(90), 4, 'X')
local_bf = Vector((0, -BH / 2 * cm, BT / 2 * cm))   # bottom-front edge
target = Vector((0, 12.9 * cm, 36.0 * cm))
back.matrix_world = Matrix.Translation(target - Rm.to_3x3() @ local_bf) @ Rm

mn, mx, tris = plib.stats(KEY)
plib.save(KEY)
plib.preview(KEY, (-1.3, -1.75, 1.05), (0.0, 0.0, 0.37), lens=50)
plib.preview(KEY, (-2.0, 0.0, 0.45), (0.0, 0.0, 0.38), lens=50,
             out=os.path.join(plib.ASSETS, "previews", KEY + "_side.png"))
