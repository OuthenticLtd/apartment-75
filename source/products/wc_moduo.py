"""Cersanit Moduo CleanOn wall-hung rimless WC (K116-007 family) with slim soft-close seat."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bc_common as C
import bpy, bmesh
from mathutils import Vector, Matrix

KEY = "wc_moduo"
C.reset(KEY)
W, D, H = 0.36, 0.525, 0.40
PAN_H = 0.365

cer = C.mat("ceramic", (0.93, 0.935, 0.94), rough=0.12, coat=0.4)
seatm = C.mat("seat", (0.92, 0.925, 0.93), rough=0.22)
hinge = C.mat("hinge", (0.75, 0.76, 0.77), rough=0.25, metal=0.8)


def outline(a, ab, F, b, rc=0.012):
    """Plan outline at one level: back on y=0, width 2*ab at back, 2*a at the start of the
    elliptical front (semi-axes a x b), front-most point at y=-F. Fixed sample counts per segment."""
    ys = -(F - b)                       # where the front ellipse starts
    pts = []
    # back edge, centre -> right corner
    for k in range(4):
        pts.append((ab * k / 4 * (1 - rc / ab), 0.0))
    # rear right corner (small radius)
    for k in range(4):
        t = (math.pi / 2) * k / 4
        pts.append((ab - rc + rc * math.sin(t), -rc + rc * math.cos(t)))
    # right side: ab at the back -> a at ys (smooth step)
    for k in range(10):
        f = k / 10
        s = f * f * (3 - 2 * f)
        pts.append((ab + (a - ab) * s, -rc + (ys + rc) * f))
    # front ellipse right -> left
    for k in range(41):
        t = math.pi * k / 40
        pts.append((a * math.cos(t), ys - b * math.sin(t)))
    # left side
    for k in range(1, 11):
        f = 1 - k / 10
        s = f * f * (3 - 2 * f)
        pts.append((-(ab + (a - ab) * s), -rc + (ys + rc) * f))
    for k in range(1, 4):
        t = (math.pi / 2) * (1 - k / 4)
        pts.append((-(ab - rc + rc * math.sin(t)), -rc + rc * math.cos(t)))
    for k in range(4, 0, -1):
        pts.append((-ab * k / 4 * (1 - rc / ab), 0.0))
    return pts

# levels: (z, a, ab, F, b)  - read from the Cersanit 3D spin + side/front photos
levels = [
    (0.000, 0.098, 0.140, 0.355, 0.230),
    (0.004, 0.104, 0.142, 0.366, 0.240),
    (0.012, 0.110, 0.144, 0.380, 0.250),
    (0.035, 0.120, 0.147, 0.405, 0.262),
    (0.080, 0.137, 0.152, 0.445, 0.278),
    (0.140, 0.154, 0.160, 0.482, 0.290),
    (0.200, 0.166, 0.167, 0.505, 0.298),
    (0.260, 0.175, 0.174, 0.518, 0.302),
    (0.310, 0.179, 0.178, 0.524, 0.304),
    (0.345, 0.180, 0.180, 0.525, 0.305),
    (0.357, 0.178, 0.179, 0.523, 0.304),
    (0.363, 0.172, 0.176, 0.517, 0.300),
    (PAN_H, 0.165, 0.172, 0.510, 0.296),
]
rings = []
for (z, a, ab, F, b) in levels:
    rings.append([Vector((x, y, z)) for (x, y) in outline(a, ab, F, b)])
pan = C.loft("pan", rings, cer)

# sculpted triangular side recesses at the back (one each side), boolean-cut 14 mm deep
cutters = []
for s in (-1, 1):
    tri = [(-0.022, 0.330), (-0.022, 0.045), (-0.205, 0.330)]   # (y, z)
    bm = bmesh.new()
    x_in, x_out = s * 0.160, s * 0.30
    va = [bm.verts.new((x_in, y, z)) for (y, z) in tri]
    vb = [bm.verts.new((x_out, y, z)) for (y, z) in tri]
    bm.faces.new(va); bm.faces.new(list(reversed(vb)))
    for i in range(3):
        j = (i + 1) % 3
        bm.faces.new((va[i], vb[i], vb[j], va[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("cut"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("cut", me); bpy.context.scene.collection.objects.link(ob)
    cutters.append(ob)
for ob in cutters:
    md = pan.modifiers.new("Bool", 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = ob; md.solver = 'EXACT'
dg = bpy.context.evaluated_depsgraph_get()
me = bpy.data.meshes.new_from_object(pan.evaluated_get(dg))
old = pan.data; pan.modifiers.clear(); pan.data = me; me.name = old.name
for ob in cutters:
    bpy.data.objects.remove(ob)
me.materials.clear(); me.materials.append(cer)
for p_ in me.polygons:
    p_.material_index = 0
C.smooth_by_angle(pan, 38)

# ---- slim seat + lid (closed), follows the rim outline in front of the hinge line
YH = -0.100
top = outline(0.163, 0.170, 0.508, 0.295)
pts = [(x, y) for (x, y) in top if y < YH]
# close at the hinge line with straight edge
a_h = max(abs(x) for (x, y) in pts if y > YH - 0.02)
seat_out = [(a_h, YH)] + [p for p in pts if p[0] < 0 or True]
# order: points of `top` are back->right->front->left->back; filter keeps right side..front..left side
right = [p for p in pts if p[0] >= 0 and p[1] > -0.2]
seat_poly = [(a_h, YH)] + pts + [(-a_h, YH)]
seat_poly = C.resample(seat_poly, 120)
def slab(name, poly, z0, z1, inset, material, bev):
    ob = C.prism(name, [(x * (1 - inset), y if y > YH - 0.001 else y) for (x, y) in poly], z1 - z0, material, plane='XY', w0=z0, bev=bev, segs=4, smooth_angle=40)
    return ob
seat = slab("seat_ring", seat_poly, PAN_H, PAN_H + 0.016, 0.012, seatm, 0.005)
lid = slab("lid", seat_poly, PAN_H + 0.016, H, 0.0, seatm, 0.008)
# hinge posts (soft-close)
for s in (-1, 1):
    C.cyl(f"hinge_{'l' if s < 0 else 'r'}", 0.012, 0.030, (s * 0.085, YH + 0.012, PAN_H + 0.015), seatm, axis='X', verts=24, bev=0.003)
    C.cyl(f"hinge_bolt_{'l' if s < 0 else 'r'}", 0.008, 0.004, (s * 0.085, -0.075, PAN_H + 0.002), hinge, axis='Z', verts=20)

C.recenter("wall")
C.finish(KEY, "Cersanit Moduo CleanOn rimless wall-hung WC with slim soft-close duroplast seat, white", (W, D, H), "wall",
         "Origin = centre of the pan's back face at its bottom edge (back on y=0). Pan 360x525x365 (Cersanit), seat+lid closed adds 35 mm -> 400. Egg-shaped plan with straight back, tapering cup-shaped bowl, sculpted triangular side recesses at the back.",
         views=[((0.75, -1.0, 0.5), ""), ((1.0, -0.15, 0.25), "_side")])
