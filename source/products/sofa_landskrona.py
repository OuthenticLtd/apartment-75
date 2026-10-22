import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
from mathutils import Vector, Matrix
import plib
from plib import box, cylinder, mat, obj_from_bm, rounded_box_bm

KEY = "sofa_landskrona"
cm = 0.01
plib.reset()
R = plib.root(KEY)

FAB = mat(KEY + " fabric", (72, 73, 76), rough=0.95)
OAK = mat(KEY + " oak", (196, 156, 116), rough=0.55)
BLK = mat(KEY + " castor", (25, 25, 26), rough=0.4)


def tufted_cushion(name, sx, sy, sz, r, ncols, nrows, bulge, chan, dimple, res,
                   seam_from_top=None, plain_band_bulge=0.0):
    """Cushion centred at origin, tufted face = +z. sx,sy face size, sz thickness."""
    nx, ny, nz = res
    bm = rounded_box_bm(sx, sy, sz, r, nx, ny, nz)
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    # quilt area (y range)
    y_top = hy - seam_from_top if seam_from_top else hy
    xs = [-hx + sx * i / ncols for i in range(1, ncols)]
    ys_rows = [-hy + (y_top + hy) * j / nrows for j in range(1, nrows)]
    hlines = list(ys_rows) + ([y_top] if seam_from_top else [])
    wc = 1.4 * cm      # channel half width
    wd = 2.6 * cm      # dimple radius
    for v in bm.verts:
        x, y, z = v.co
        if z <= 0:
            continue
        # weight: 1 on flat top, fading on the rounded band / sides
        w = max(0.0, min(1.0, (z - (hz - r * 1.2)) / (r * 1.2)))
        w = w * w * (3 - 2 * w)
        ex = max(0.0, 1 - (abs(x) / hx) ** 6)
        ey = max(0.0, 1 - (abs(y) / hy) ** 6)
        d = bulge * ex * ey
        # channels
        c = 0.0
        if -hy + 1.5 * cm < y < y_top + wc:
            for xl in xs:
                c = max(c, math.exp(-((x - xl) / wc) ** 2))
        for yl in hlines:
            if abs(x) < hx - 1.0 * cm:
                c = max(c, math.exp(-((y - yl) / wc) ** 2) * (1.0 if yl != y_top else 0.8))
        dd = 0.0
        for xl in xs:
            for yl in hlines:
                dd = max(dd, math.exp(-(((x - xl) ** 2 + (y - yl) ** 2) / wd ** 2)))
        # puff of each square: pillows rise between channels
        d -= chan * c + dimple * dd
        if seam_from_top and y > y_top:
            d += plain_band_bulge * math.sin(min(1, (y - y_top) / (hy - y_top)) * math.pi) * ex
        v.co.z += d * w
    # hidden flat bottom: replace dense grid by one n-gon (saves triangles)
    flat = [f for f in bm.faces if all(v.co.z < -hz + 1e-6 for v in f.verts)]
    bmesh.ops.delete(bm, geom=flat, context='FACES')
    bmesh.ops.holes_fill(bm, edges=bm.edges[:], sides=0)
    return bm


def place(ob, M):
    ob.matrix_world = M  # parent has identity transform


# ---------------- dimensions (cm) ----------------
W, D, H = 223, 92, 84
ARM_W = 13
ARM_H = 67
LEG_H = 15
xi = W / 2 - ARM_W  # inner face of arm = 98.5
y_front, y_back = -D / 2, D / 2

# ---------------- arms ----------------
for side, sx in (("L", -1), ("R", 1)):
    x0, x1 = sorted((sx * xi, sx * W / 2))
    a = box(f"{KEY}_arm_{side}", R, (x0 * cm, y_front * cm, LEG_H * cm), (x1 * cm, y_back * cm, ARM_H * cm),
            FAB, bevel=1.6 * cm, seg=4)
    # vertical stitched panels on the outer face (three channels, as in the IKEA drawing)
# legs (under arms) : fabric sleeve + oak foot, tapered
for side, sx in (("L", -1), ("R", 1)):
    for fb, sy in (("F", -1), ("B", 1)):
        x = sx * (W / 2 - ARM_W / 2)
        y = sy * (D / 2 - 8.0)
        r_bot, r_top = 1.75, 2.3
        r_mid = r_bot + (r_top - r_bot) * 0.5
        cylinder(f"{KEY}_leg_{side}{fb}_sleeve", R, r_mid * cm, r_top * cm, 7.2 * cm, LEG_H * cm,
                 x * cm, y * cm, seg=20, material=FAB)
        cylinder(f"{KEY}_leg_{side}{fb}_oak", R, r_bot * cm, r_mid * cm * 0.97, 0, 7.2 * cm,
                 x * cm, y * cm, seg=20, material=OAK)

# ---------------- sofa-bed base (pull-out box) + back frame ----------------
BASE_Z0, BASE_Z1 = 6.0, 33.5
box(f"{KEY}_bedbase", R, (-xi * cm + 0.002, (y_front + 1.2) * cm, BASE_Z0 * cm),
    (xi * cm - 0.002, 28 * cm, BASE_Z1 * cm), FAB, bevel=1.8 * cm, seg=4)
box(f"{KEY}_backframe", R, (-xi * cm + 0.002, 27 * cm, 9 * cm), (xi * cm - 0.002, y_back * cm, 63 * cm),
    FAB, bevel=2.0 * cm, seg=4)
# castors under the bed front
for i, x in enumerate((-80, 80)):
    for j, y in enumerate((-38,)):
        c = cylinder(f"{KEY}_castor_{i}", R, 2.4 * cm, 2.4 * cm, -0.9 * cm, 0.9 * cm, 0, 0, seg=16, material=BLK)
        c.rotation_euler = (0, math.radians(90), 0)
        c.location = (x * cm, y * cm, 2.6 * cm)
        box(f"{KEY}_castorfork_{i}", R, ((x - 1.2) * cm, (y - 1.5) * cm, 3.0 * cm), ((x + 1.2) * cm, (y + 1.5) * cm, BASE_Z0 * cm), BLK)

# ---------------- seat cushions ----------------
gap = 0.6
cw = (2 * xi - gap) / 2
SEAT_D = 71
SEAT_T = 11.5
for i, sxn in enumerate((-1, 1)):
    bm = tufted_cushion("seat", cw * cm, SEAT_D * cm, SEAT_T * cm, 3.2 * cm, 5, 3,
                        bulge=1.8 * cm, chan=1.6 * cm, dimple=1.4 * cm, res=(64, 44, 5))
    ob = obj_from_bm(f"{KEY}_seat_cushion_{'L' if sxn < 0 else 'R'}", bm, R, FAB)
    ob.location = (sxn * (cw + gap) / 2 * cm, (y_front + SEAT_D / 2 + 0.3) * cm, (BASE_Z1 + SEAT_T / 2 - 0.3) * cm)

# ---------------- back cushions ----------------
BK_H, BK_T = 42.3, 17.0
tilt = math.radians(13)
for i, sxn in enumerate((-1, 1)):
    bm = tufted_cushion("back", cw * cm, BK_H * cm, BK_T * cm, 4.0 * cm, 5, 3,
                        bulge=2.0 * cm, chan=1.6 * cm, dimple=1.4 * cm, res=(64, 30, 5),
                        seam_from_top=9.0 * cm, plain_band_bulge=0.6 * cm)
    ob = obj_from_bm(f"{KEY}_back_cushion_{'L' if sxn < 0 else 'R'}", bm, R, FAB)
    Rm = Matrix.Rotation(-tilt, 4, 'X') @ Matrix.Rotation(math.radians(90), 4, 'X')
    # bottom-front edge of cushion (local (0,-hy,+hz)) goes to target
    local_bf = Vector((0, -BK_H / 2 * cm, BK_T / 2 * cm))
    target = Vector((sxn * (cw + gap) / 2 * cm, 13.0 * cm, (BASE_Z1 + SEAT_T - 1.5) * cm))
    loc = target - (Rm.to_3x3() @ local_bf)
    ob.matrix_world = Matrix.Translation(loc) @ Rm

mn, mx, tris = plib.stats(KEY)
plib.save(KEY)
# ---------------- preview ----------------
plib.preview(KEY, (2.6, -3.3, 1.55), (0.05, 0.0, 0.40), lens=50)
plib.preview(KEY, (0.0, -4.2, 0.55), (0.0, 0.0, 0.42), lens=50,
             out=os.path.join(plib.ASSETS, "previews", KEY + "_front.png"))
