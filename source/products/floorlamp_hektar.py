import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
from mathutils import Vector, Matrix
import plib
from plib import mat, obj_from_bm, cylinder

KEY = "floorlamp_hektar"
cm = 0.01
plib.reset()
R = plib.root(KEY)

GREY = mat(KEY + " dark grey metal", (42, 43, 44), rough=0.5, metal=0.0)
INNER = mat(KEY + " shade inside", (232, 230, 225), rough=0.6)
CORD = mat(KEY + " cord", (20, 20, 20), rough=0.5)
BULB = mat(KEY + " bulb", (245, 243, 236), rough=0.3)


def lathe(name, prof, mats, seg=48, smooth=True):
    """prof: list of (r, z, matindex) in cm, ordered; closed loop not assumed.
    Faces between consecutive points use the material of the first point."""
    bm = bmesh.new()
    rings = []
    for r, z, _ in prof:
        if r < 1e-6:
            rings.append([bm.verts.new((0, 0, z * cm))])
        else:
            rings.append([bm.verts.new((r * cm * math.cos(2 * math.pi * k / seg),
                                        r * cm * math.sin(2 * math.pi * k / seg), z * cm)) for k in range(seg)])
    for i in range(len(prof) - 1):
        a, b = rings[i], rings[i + 1]
        mi = prof[i][2]
        for k in range(seg):
            k2 = (k + 1) % seg
            if len(a) == 1 and len(b) == 1:
                continue
            if len(a) == 1:
                f = bm.faces.new((a[0], b[k], b[k2]))
            elif len(b) == 1:
                f = bm.faces.new((a[k], b[0], a[k2]))
            else:
                f = bm.faces.new((a[k], b[k], b[k2], a[k2]))
            f.material_index = mi
    bm.normal_update()
    ob = obj_from_bm(name, bm, R, None, smooth)
    for m in mats:
        ob.data.materials.append(m)
    return ob


def sweep(name, path, radius, material, seg=16):
    """Tube along a polyline path (list of Vectors, metres); open ends capped."""
    bm = bmesh.new()
    rings = []
    prev_n = None
    for i, p in enumerate(path):
        if i == 0:
            t = (path[1] - path[0]).normalized()
        elif i == len(path) - 1:
            t = (path[-1] - path[-2]).normalized()
        else:
            t = ((path[i + 1] - path[i]).normalized() + (path[i] - path[i - 1]).normalized()).normalized()
        if prev_n is None:
            ref = Vector((1, 0, 0)) if abs(t.x) < 0.9 else Vector((0, 1, 0))
            n = t.cross(ref).normalized()
        else:
            n = (prev_n - t * prev_n.dot(t)).normalized()
        prev_n = n
        b = t.cross(n)
        rings.append([bm.verts.new(p + radius * (math.cos(2 * math.pi * k / seg) * n + math.sin(2 * math.pi * k / seg) * b))
                      for k in range(seg)])
    for i in range(len(rings) - 1):
        for k in range(seg):
            k2 = (k + 1) % seg
            bm.faces.new((rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bm.normal_update()
    return obj_from_bm(name, bm, R, material)


# ---------------- base: Ø34 cast plate with a lower flange ----------------
base_prof = [
    (0, 0.0, 0), (16.6, 0.0, 0), (17.0, 0.15, 0), (17.0, 0.55, 0), (16.6, 0.7, 0),
    (16.1, 0.75, 0), (16.1, 1.0, 0),            # recess between flange and plate
    (16.5, 1.1, 0), (16.6, 1.6, 0), (16.5, 2.2, 0), (16.1, 2.6, 0), (15.4, 2.85, 0), (14.0, 2.95, 0),
    (2.0, 3.05, 0), (1.3, 3.2, 0), (1.3, 3.6, 0), (0, 3.6, 0)]
lathe(f"{KEY}_base", base_prof, [GREY], seg=64)

# ---------------- shade geometry (local, rim at z=0, axis +z) ----------------
SH_R = 31.5 / 2
shade_prof = [
    # outer surface, rim to top
    (SH_R - 0.25, -0.05, 0), (SH_R, 0.15, 0), (SH_R, 0.6, 0),
    (15.45, 2.5, 0), (14.85, 5.0, 0), (13.95, 7.5, 0), (12.7, 10.0, 0), (11.2, 12.3, 0),
    (9.7, 14.2, 0), (8.6, 15.4, 0), (8.3, 16.0, 0),
    (8.3, 16.6, 0), (7.4, 17.3, 0), (7.1, 17.6, 0),        # stepped shoulder ring
    (7.1, 27.2, 0), (6.9, 27.75, 0), (6.4, 28.0, 0), (0, 28.0, 0)]
inner_prof = [
    (0, 16.4, 1), (6.9, 16.4, 1), (8.0, 15.3, 1), (9.4, 13.9, 1), (10.9, 12.0, 1), (12.4, 9.8, 1),
    (13.65, 7.4, 1), (14.55, 4.9, 1), (15.15, 2.4, 1), (15.45, 0.15, 1), (SH_R - 0.25, -0.05, 1)]
shade = lathe(f"{KEY}_shade", shade_prof + inner_prof, [GREY, INNER], seg=56)
# lamp socket + bulb visible inside the shade
sock = cylinder(f"{KEY}_socket", R, 2.0 * cm, 2.0 * cm, 11.0 * cm, 16.4 * cm, seg=20, material=INNER)
bulb_prof = [(0, 1.0, 0), (1.4, 1.2, 0), (2.6, 2.3, 0), (3.0, 4.0, 0), (2.6, 5.7, 0), (1.6, 6.6, 0), (1.3, 8.0, 0),
             (1.3, 11.0, 0), (0, 11.0, 0)]
bulb = lathe(f"{KEY}_bulb", bulb_prof, [BULB], seg=24)

# pivot frame: pivot on neck axis at z=22 (local)
PIV_Z = 22.0
TILT = math.radians(18)      # shade tilted forward (rim facing down/forward)
SHADE_Y = -25.0              # shade axis offset in front of the stem
TOP_Z = 181.22
# highest point of tilted shade = top rim of neck (back edge rises)
top_local_rel = Vector((0, -7.1, 28.0 - PIV_Z))      # front-top edge of neck relative to pivot
rot = Matrix.Rotation(-TILT, 4, 'X')                 # tilt rim toward -y (front)
rise = (rot.to_3x3() @ top_local_rel).z
PIV_H = TOP_Z - rise
M_shade = Matrix.Translation(Vector((0, SHADE_Y, PIV_H)) * cm) @ rot @ Matrix.Translation(Vector((0, 0, -PIV_Z)) * cm)
for ob in (shade, sock, bulb):
    ob.matrix_world = M_shade @ ob.matrix_world

# ---------------- yoke strap around the neck + pivot knobs ----------------
STRAP_R = 8.1
bm = bmesh.new()
segs = 28
w, t = 2.4, 0.35
verts = []
for i in range(segs + 1):
    a = math.pi * i / segs   # from +x through +y (back) to -x
    c, s = math.cos(a), math.sin(a)
    ring = [bm.verts.new((rr * c * cm, rr * s * cm, zz * cm)) for rr, zz in
            ((STRAP_R, -w / 2), (STRAP_R + t, -w / 2), (STRAP_R + t, w / 2), (STRAP_R, w / 2))]
    verts.append(ring)
for i in range(segs):
    for k in range(4):
        k2 = (k + 1) % 4
        bm.faces.new((verts[i][k], verts[i][k2], verts[i + 1][k2], verts[i + 1][k]))
bm.faces.new(list(reversed(verts[0])))
bm.faces.new(verts[-1])
bm.normal_update()
strap = obj_from_bm(f"{KEY}_yoke", bm, R, GREY)
strap.location = (0, SHADE_Y * cm, PIV_H * cm)
# strap hugs a slightly tilted neck: tilt with the shade a little for contact
for sx in (-1, 1):
    k = cylinder(f"{KEY}_knob_{'L' if sx < 0 else 'R'}", R, 1.3 * cm, 1.1 * cm, 0, 1.0 * cm, seg=16, material=GREY)
    k.rotation_euler = (0, math.radians(90 * sx), 0)
    k.location = (sx * (STRAP_R + t) * cm, SHADE_Y * cm, PIV_H * cm)

# ---------------- stem: vertical tube, bends over to the yoke ----------------
TUBE_R = 1.1
ARC_R = 9.0
y_strap_back = SHADE_Y + STRAP_R + t       # back of the yoke strap
z_arm = PIV_H
path = [Vector((0, 0, 3.4)) * cm]
z_bend = z_arm - ARC_R
path.append(Vector((0, 0, z_bend)) * cm)
for i in range(1, 13):
    a = math.radians(90 * i / 12)
    path.append(Vector((0, -ARC_R * (1 - math.cos(a)), z_bend + ARC_R * math.sin(a))) * cm)
# straight horizontal to the yoke
path.append(Vector((0, y_strap_back + 2.4, z_arm)) * cm)
path.append(Vector((0, y_strap_back - 0.1, z_arm)) * cm)
stem = sweep(f"{KEY}_stem", path, TUBE_R * cm, GREY, seg=18)
# joint collar where the arm meets the yoke
col = cylinder(f"{KEY}_collar", R, 1.35 * cm, 1.35 * cm, 0, 2.6 * cm, seg=18, material=GREY)
col.rotation_euler = (math.radians(90), 0, 0)
col.location = (0, (y_strap_back + 2.6) * cm, z_arm * cm)

# ---------------- cable loop from shade top into the arm ----------------
top_c = M_shade @ Vector((0, 0, 28.0 * cm, 1)) if False else (M_shade @ Vector((0, 0, 28.0 * cm)))
p_end = Vector((0, (y_strap_back + 3.5) * cm, (z_arm + 0.9) * cm))
cp = [top_c]
for i in range(1, 16):
    u = i / 15
    # quadratic bezier with control above and behind
    c1 = Vector((0, (top_c.y + p_end.y) / 2 + 0.02, max(top_c.z, p_end.z) + 0.035))
    cp.append((1 - u) ** 2 * top_c + 2 * (1 - u) * u * c1 + u ** 2 * p_end)
sweep(f"{KEY}_cable", cp, 0.28 * cm, CORD, seg=8)

plib.stats(KEY)
plib.save(KEY)
plib.preview(KEY, (1.5, -2.9, 1.6), (0.0, -0.1, 0.93), lens=40)
plib.preview(KEY, (3.6, 0.0, 1.0), (0.0, -0.08, 0.92), lens=45,
             out=os.path.join(plib.ASSETS, "previews", KEY + "_side.png"))
