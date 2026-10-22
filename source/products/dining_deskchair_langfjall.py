"""IKEA LÅNGFJÄLL conference/swivel chair, Gunnared dark grey / black (s79177642).
IKEA: width 68, depth 68, max height 104, seat width 53, seat depth 41, seat height 43-53 (modelled at MAX).
One-piece upholstered shell (seat + tall back, tombstone top, slim dark edge seam, black plastic under-shell),
black 5-star base with twin-wheel castors, gas lift, mechanism with height lever on the chair's right (-X)."""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import bpy, bmesh, numpy as np
from mathutils import Vector, Matrix
import dining_common as C

KEY = "deskchair_langfjall"
C.reset()
R = C.root(KEY)

# ---------- Gunnared melange texture ----------
N = 512
rng = np.random.default_rng(11)
a = rng.random((N, N))
# woven melange: mix of near-black and light grey yarn flecks, slightly elongated horizontally
k = np.ones(3) / 3
a = np.apply_along_axis(lambda r: np.convolve(r, k, mode='same'), 1, a)
light = (a > 0.62).astype(float)
dark = (a < 0.36).astype(float)
base = np.full((N, N, 3), np.array([72, 72, 74]) / 255.0)
col = base + light[..., None] * (np.array([140, 138, 138]) / 255 - base) * 0.6 + dark[..., None] * (np.array([45, 44, 46]) / 255 - base) * 0.6
col = np.clip(col, 0, 1)
img = bpy.data.images.new("deskchair_langfjall_gunnared", N, N, alpha=False)
img.pixels.foreach_set(np.concatenate([col, np.ones((N, N, 1))], axis=2).astype(np.float32).ravel())
img.filepath_raw = os.path.join(C.ASSETS, "refs", "d_deskchair_langfjall_gunnared.png")
img.file_format = 'PNG'; img.save(); img.pack()

m_fab = C.mat("deskchair_langfjall fabric", (72, 72, 74), rough=0.95, image=img)
m_shell = C.mat("deskchair_langfjall shell", (30, 30, 32), rough=0.55)
m_seam = C.mat("deskchair_langfjall seam", (38, 38, 40), rough=0.8)
m_base = C.mat("deskchair_langfjall base", (34, 34, 36), rough=0.45, metal=0.1)
m_tyre = C.mat("deskchair_langfjall castor rim", (150, 150, 152), rough=0.5)

# ---------- shell: loft along side-profile spine ----------
# (y, z, width, thickness, curl)   y<0 = front.  seat front -> back top
CP = [
    (-0.263, 0.492, 0.30, 0.014, 0.000),
    (-0.256, 0.494, 0.43, 0.052, 0.000),
    (-0.232, 0.496, 0.505, 0.072, 0.004),
    (-0.190, 0.497, 0.53, 0.076, 0.008),
    (-0.110, 0.494, 0.53, 0.074, 0.012),
    (-0.010, 0.492, 0.52, 0.068, 0.018),
    ( 0.075, 0.505, 0.48, 0.056, 0.035),
    ( 0.122, 0.545, 0.445, 0.046, 0.040),
]
# back: straight tapering sides 0.40 -> 0.53, then a rounded (superellipse) top, ~8 deg lean with slight forward roll at top
def back_y(z):
    return 0.145 + (z - 0.62) * 0.15 - max(0.0, z - 0.97) ** 2 * 1.5
ZT0, ZTOP = 0.915, 1.036
for z in (0.62, 0.70, 0.78, 0.86, 0.915):
    w = 0.435 + (0.375 - 0.435) * (z - 0.62) / (ZT0 - 0.62)
    CP.append((back_y(z), z, w, 0.038 - 0.012 * (z - 0.62) / 0.4, 0.055))
for q in (0.25, 0.5, 0.7, 0.85, 0.95, 1.0):
    z = ZT0 + (ZTOP - ZT0) * q
    w = 0.375 * max(0.0, 1 - q ** 2.4) ** (1 / 2.4)
    w = max(w, 0.08)
    t = 0.025 * (0.4 + 0.6 * max(0.0, 1 - q ** 4) ** 0.25)
    CP.append((back_y(z), z, w, t, 0.055 * w / 0.375))
CP_END = [
]

def catmull(points, n):
    P = [np.array(p, float) for p in points]
    P = [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(n):
            t = j / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-2])
    return out

S = catmull(CP, 4)
M = 40            # points per cross-section
PEXP = 3.2        # superellipse exponent (rounded rectangle section)
bm = bmesh.new()
rings = []
for i, sp in enumerate(S):
    y, z, w, t, c = sp
    a_ = S[max(0, i - 1)]; b_ = S[min(len(S) - 1, i + 1)]
    T = Vector((0, b_[0] - a_[0], b_[1] - a_[1])).normalized()
    Nv = Vector((0, -T.z, T.y))     # occupant side (up on seat, forward on back)
    ring = []
    for j in range(M):
        th = 2 * math.pi * j / M
        cs, sn = math.cos(th), math.sin(th)
        x = (w / 2) * math.copysign(abs(cs) ** (2 / PEXP), cs)
        n = (t / 2) * math.copysign(abs(sn) ** (2 / PEXP), sn)
        n += c * (x / (w / 2)) ** 2 if w > 0 else 0
        p = Vector((x, y, z)) + Nv * n
        ring.append(bm.verts.new(p))
    rings.append(ring)
faces = []
for ri in range(len(rings) - 1):
    A, B = rings[ri], rings[ri + 1]
    for j in range(M):
        jj = (j + 1) % M
        f = bm.faces.new((A[j], A[jj], B[jj], B[j]))
        # material: seam band at the section extremes, black under-shell on the seat underside
        mid = (j + 0.5) / M * 2 * math.pi
        sn = math.sin(mid); cs = math.cos(mid)
        if abs(sn) < 0.12:
            f.material_index = 2
        elif sn < 0 and ri < len(rings) * 0.36:
            f.material_index = 1
        else:
            f.material_index = 0
        faces.append(f)
cap0 = bm.faces.new(list(reversed(rings[0])))
cap1 = bm.faces.new(rings[-1])
bmesh.ops.poke(bm, faces=[cap0, cap1])
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
shell = C.obj_from_bm(bm, f"{KEY}_shell", R)
for m in (m_fab, m_shell, m_seam):
    shell.data.materials.append(m)
for p in shell.data.polygons:
    p.use_smooth = True
# UVs: u along width, v along spine length (fabric texture repeats ~every 12 cm)
uvl = shell.data.uv_layers.new(name="UVMap")
for p in shell.data.polygons:
    for li in p.loop_indices:
        vi = shell.data.loops[li].vertex_index
        ri, j = divmod(vi, M) if vi < len(rings) * M else (len(rings) - 1, 0)
        co = shell.data.vertices[vi].co
        uvl.data[li].uv = (co.x / 0.12, ri * 0.018 / 0.12 * 1.0)
sub = shell.modifiers.new("Subdivision", 'SUBSURF'); sub.levels = 1; sub.render_levels = 1

# ---------- under-seat mechanism, gas lift, lever ----------
C.box(f"{KEY}_mechanism", R, (0.20, 0.22, 0.035), (0, -0.02, 0.445), m_base, bevel=0.01, segs=2)
C.cyl_between(f"{KEY}_gaslift_inner", R, (0, 0, 0.27), (0, 0, 0.43), 0.014, 0.014, m_base, verts=20)
C.cyl_between(f"{KEY}_gaslift_outer", R, (0, 0, 0.10), (0, 0, 0.29), 0.025, 0.025, m_base, verts=24)
C.cyl_between(f"{KEY}_gaslift_cover", R, (0, 0, 0.285), (0, 0, 0.30), 0.025, 0.017, m_base, verts=24)
lever = C.cyl_between(f"{KEY}_lever", R, (-0.08, -0.03, 0.445), (-0.225, -0.05, 0.445), 0.005, 0.005, m_base, verts=10)
C.box(f"{KEY}_lever_paddle", R, (0.06, 0.022, 0.010), (-0.245, -0.052, 0.445), m_base, bevel=0.004, segs=2)

# ---------- 5-star base ----------
RC = 0.68 / 2 / math.sin(math.radians(72))   # castor outer radius so that the X width = 68 cm
HUB_R, HUB_Z0, HUB_Z1 = 0.040, 0.090, 0.185
C.lathe(f"{KEY}_hub", R, [(0, HUB_Z0), (HUB_R - 0.006, HUB_Z0), (HUB_R, HUB_Z0 + 0.008), (HUB_R, HUB_Z1 - 0.006),
                          (HUB_R - 0.006, HUB_Z1), (0, HUB_Z1)], m_base, segs=32)
TIP_R = RC - 0.053        # arm tip (castor stem) radius
arms = []
castors = []
for k in range(5):
    ang = math.radians(-90 + 72 * k)      # first arm points to the front (-Y)
    d = Vector((math.cos(ang), math.sin(ang), 0))
    side = Vector((-d.y, d.x, 0))
    # tapered arm: hub (h 5 cm, w 4.2 cm) -> tip (h 2.4 cm, w 2.8 cm), sloping down
    bm = bmesh.new()
    secs = []
    NS = 8
    for i in range(NS + 1):
        u = i / NS
        r = HUB_R - 0.01 + (TIP_R - HUB_R + 0.01) * u
        ztop = HUB_Z1 - 0.004 - (HUB_Z1 - 0.004 - 0.104) * (u ** 0.8)
        h = 0.056 + (0.030 - 0.056) * u
        wdt = 0.050 + (0.032 - 0.050) * u
        c0 = d * r + Vector((0, 0, ztop))
        sec = [bm.verts.new(c0 + side * sx * wdt / 2 + Vector((0, 0, -h * sz))) for sx, sz in ((-1, 0), (1, 0), (1, 1), (-1, 1))]
        secs.append(sec)
    for A, B in zip(secs[:-1], secs[1:]):
        for q in range(4):
            bm.faces.new((A[q], A[(q + 1) % 4], B[(q + 1) % 4], B[q]))
    bm.faces.new(list(reversed(secs[0]))); bm.faces.new(secs[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    arm = C.obj_from_bm(bm, f"{KEY}_arm{k+1}", R, m_base)
    C.add_bevel(arm, 0.006, 2, angle=40)
    arms.append(arm)
    tip = d * TIP_R
    # castor socket boss under the arm tip
    castors.append(C.cyl_between(f"{KEY}_boss{k+1}", R, tip + Vector((0, 0, 0.064)), tip + Vector((0, 0, 0.100)), 0.015, 0.017, m_base, verts=16))
    # twin-wheel castor, wheels trailing outward, axle tangential
    wc = tip + d * 0.020 + Vector((0, 0, 0.028))
    for sx in (-1, 1):
        o1 = wc + side * sx * 0.005; o2 = wc + side * sx * 0.019
        castors.append(C.cyl_between(f"{KEY}_wheel{k+1}{sx}", R, o1, o2, 0.028, 0.028, m_base, verts=20))
        o3 = wc + side * sx * 0.0188; o4 = wc + side * sx * 0.0200
        castors.append(C.cyl_between(f"{KEY}_rim{k+1}{sx}", R, o3, o4, 0.024, 0.024, m_tyre, verts=20))
        o5 = wc + side * sx * 0.0199; o6 = wc + side * sx * 0.0206
        castors.append(C.cyl_between(f"{KEY}_cap{k+1}{sx}", R, o5, o6, 0.016, 0.016, m_base, verts=16))
    # castor hood connecting stem to the wheel axle
    castors.append(C.cyl_between(f"{KEY}_hood{k+1}", R, wc - side * 0.006, wc + side * 0.006, 0.027, 0.027, m_base, verts=16))
    castors.append(C.cyl_between(f"{KEY}_stem{k+1}", R, tip + Vector((0, 0, 0.045)), tip + Vector((0, 0, 0.068)), 0.010, 0.010, m_base, verts=12))

def join(objs, name):
    with bpy.context.temp_override(active_object=objs[0], selected_editable_objects=objs, object=objs[0]):
        bpy.ops.object.join()
    objs[0].name = name; objs[0].data.name = name
    return objs[0]
join(arms, f"{KEY}_starbase")
join(castors, f"{KEY}_castors")

C.finish(KEY, R, preview_kwargs=dict(target=(0, 0, 0.52), dist=3.0, elev=15, azim=-35),
         extra_views=[dict(target=(0, 0, 0.52), dist=3.0, elev=3, azim=90, lens=55),
                      dict(target=(0, 0, 0.52), dist=3.0, elev=3, azim=0, lens=55),
                      dict(target=(0, 0, 0.6), dist=3.0, elev=20, azim=150)])
