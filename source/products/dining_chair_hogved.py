"""IKEA HÖGVED chair, birch veneer (90606820).  IKEA measurement drawing: total height 86, seat height 45,
seat width 40 / depth 36, back 42 above seat, top rail 45 wide, footprint 47 (D) x 40 (W), listed depth 51.
7 tapered spindles, curved top rail, 4 splayed tapered round legs, H-stretcher."""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import bpy, bmesh, numpy as np
from mathutils import Vector, Matrix
import dining_common as C

KEY = "chair_hogved"
C.reset()
R = C.root(KEY)

# ---------- subtle birch texture for seat (plywood top veneer) ----------
W, H = 512, 512
rng = np.random.default_rng(3)
u = np.linspace(0, 1, W, endpoint=False)[None, :]
v = np.linspace(0, 1, H, endpoint=False)[:, None]
def sn(n, k, s):
    x = rng.standard_normal(n + 2 * k); ker = np.hanning(2 * k + 1); ker /= ker.sum()
    return np.convolve(x, ker, mode='same')[k:k + n] * s
warp = sn(W, 50, 0.05)[None, :] + 0.03 * np.sin(u * 2 * np.pi * 1.7)
f = (v + warp * 0.5 + sn(H, 25, 0.25)[:, None] + 0.06 * np.exp(-((u - 0.5) / 0.25) ** 2) * np.exp(-((v - 0.5) / 0.2) ** 2)) * 34
ring = np.abs(np.sin(np.pi * f)) ** 8
flame = 0.5 + 0.5 * np.sin(u * 2 * np.pi * 9 + sn(H, 30, 3)[:, None])  # birch curl/flame shimmer
base = np.array([234, 207, 180]) / 255
dark = np.array([214, 178, 140]) / 255
t = (0.28 * ring + 0.10 * flame)[..., None]
col = np.clip(base * (1 - t) + dark * t, 0, 1)
img = bpy.data.images.new("chair_hogved_birch", W, H, alpha=False)
img.pixels.foreach_set(np.concatenate([col, np.ones((H, W, 1))], axis=2)[::-1].astype(np.float32).ravel())
img.filepath_raw = os.path.join(C.ASSETS, "refs", "d_chair_hogved_birch.png")
img.file_format = 'PNG'; img.save(); img.pack()

m_seat = C.mat("chair_hogved seat", (233, 206, 179), rough=0.42, image=img)
m_wood = C.mat("chair_hogved birch", (226, 196, 166), rough=0.42)

# ---------- seat ----------
YF, DEPTH = -0.255, 0.36
YB = YF + DEPTH
ZTOP_F, TILT, THK = 0.45, 0.010, 0.034

def seat_outline(n=72):
    """Rounded trapezoid: 40 wide front (slightly convex), 38 wide back, rounded corners."""
    pts = []
    wf, wb = 0.200, 0.190
    rf, rb = 0.035, 0.055
    # corners centres
    corners = [(wb - rb, YB - rb, rb), (-(wb - rb), YB - rb, rb), (-(wf - rf), YF + rf, rf), (wf - rf, YF + rf, rf)]
    angles = [(0, 90), (90, 180), (180, 270), (270, 360)]
    for (cx, cy, r), (a0, a1) in zip(corners, angles):
        for i in range(n // 4 + 1):
            a = math.radians(a0 + (a1 - a0) * i / (n // 4))
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    # front edge slight convex bulge
    out = []
    for x, y in pts:
        if y < YF + 0.05:
            y -= 0.006 * (1 - (x / 0.2) ** 2) * max(0.0, (YF + 0.05 - y) / 0.05)
        out.append((x, y))
    return out

outline = seat_outline()
cx = sum(p[0] for p in outline) / len(outline); cy = sum(p[1] for p in outline) / len(outline)

def inset(pts, d):
    # offset inward along the (mitred) vertex normals of the outline (CCW polygon)
    res = []
    n = len(pts)
    for i in range(n):
        x0, y0 = pts[i - 1]; x1, y1 = pts[i]; x2, y2 = pts[(i + 1) % n]
        e1 = Vector((x1 - x0, y1 - y0)).normalized(); e2 = Vector((x2 - x1, y2 - y1)).normalized()
        n1 = Vector((-e1.y, e1.x)); n2 = Vector((-e2.y, e2.x))   # inward for CCW
        nm = (n1 + n2).normalized()
        k = d / max(0.3, nm.dot(n1))
        res.append((x1 + nm.x * k, y1 + nm.y * k))
    return res

def ztop(y):
    return ZTOP_F - TILT * (y - YF) / DEPTH

# rings: (inset, dz relative to local top) ; top rounded edge, dish, then bottom
top_rings = [(0.0, -0.012), (0.002, -0.005), (0.006, -0.0012), (0.012, 0.0)]
dish = [(0.03, -0.0025), (0.06, -0.0055), (0.09, -0.0075), (0.12, -0.0083)]
bot_rings = [(0.0, -THK + 0.010), (0.003, -THK + 0.002), (0.008, -THK)]
bm = bmesh.new()
rings = []
# build ring list from top centre -> edge -> bottom centre
ring_defs = list(reversed(dish)) + list(reversed(top_rings)) + bot_rings
for d, dz in ring_defs:
    if d < 0.02:
        pts = inset(outline, d)
    else:  # dish rings: shrink the 12 mm-inset outline about its centroid (no swallow-tails at corners)
        base = inset(outline, 0.012); k = 1 - (d - 0.012) / 0.17
        pts = [(cx + (x - cx) * k, cy + (y - cy) * k) for x, y in base]
    ring = [bm.verts.new((x, y, ztop(y) + dz)) for x, y in pts]
    rings.append(ring)
n = len(outline)
for a, b in zip(rings[:-1], rings[1:]):
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
f_top = bm.faces.new(list(reversed(rings[0])))
f_bot = bm.faces.new(rings[-1])
r_top = bmesh.ops.poke(bm, faces=[f_top])
r_bot = bmesh.ops.poke(bm, faces=[f_bot])
for vv in r_top["verts"]:
    vv.co.z = ztop(vv.co.y) - 0.0085
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
seat = C.obj_from_bm(bm, f"{KEY}_seat", R, m_seat)
C.smooth_by_angle(seat, 50)
uvl = seat.data.uv_layers.new(name="UVMap")
for li, loop in enumerate(seat.data.loops):
    co = seat.data.vertices[loop.vertex_index].co
    uvl.data[li].uv = ((co.y - YF) / 0.45, co.x / 0.45 + 0.5)

# ---------- legs ----------
ZU = 0.432   # leg tops hidden in seat
def leg(name, top, foot, r_top=0.0185, r_foot=0.0130):
    return C.cyl_between(name, R, foot, top, r_foot, r_top, m_wood, verts=16)

FX = 0.200 - 0.0130     # foot centres -> 40 cm outer width
LF_top, LF_foot = Vector((0.150, -0.185, ZU)), Vector((FX, -0.2075, -0.006))
LB_top, LB_foot = Vector((0.145, 0.055, ZU)), Vector((FX, 0.2375, -0.006))
legs = []
for sx, s in ((-1, "L"), (1, "R")):
    m = Vector((sx, 1, 1))
    legs.append(leg(f"{KEY}_leg_F{s}", LF_top * m, LF_foot * m))
    legs.append(leg(f"{KEY}_leg_B{s}", LB_top * m, LB_foot * m))

def on_leg(top, foot, z):
    t = (z - foot.z) / (top.z - foot.z)
    return foot.lerp(top, t)

ZS = 0.215
st = []
for sx, s in ((-1, "L"), (1, "R")):
    m = Vector((sx, 1, 1))
    a = on_leg(LF_top * m, LF_foot * m, ZS); b = on_leg(LB_top * m, LB_foot * m, ZS)
    st.append(C.cyl_between(f"{KEY}_stretcher_{s}", R, a, b, 0.0095, 0.0095, m_wood, verts=12))
# cross stretcher between the side stretchers (slightly behind middle, as on the IKEA drawing)
yc = -0.02
def x_at(sx):
    m = Vector((sx, 1, 1))
    a = on_leg(LF_top * m, LF_foot * m, ZS); b = on_leg(LB_top * m, LB_foot * m, ZS)
    t = (yc - a.y) / (b.y - a.y)
    return a.lerp(b, t)
st.append(C.cyl_between(f"{KEY}_stretcher_X", R, x_at(-1), x_at(1), 0.0085, 0.0085, m_wood, verts=12))

# ---------- back: 7 spindles + curved top rail ----------
TOPZ = 0.860
RAIL_H, RAIL_T, LEAN = 0.055, 0.022, math.radians(16)
SAG = 0.030
Y_RAIL_END = 0.245 - SAG - RAIL_T / 2 - RAIL_H * math.tan(LEAN)  # rail centre-line at its ends (bottom)
def rail_y(x, z_off=0.0):
    t = x / 0.225
    return Y_RAIL_END + SAG * (1 - t * t) + z_off * math.tan(LEAN)
ZR0 = TOPZ - RAIL_H   # rail bottom
# rail mesh: sweep rectangle along arc
N = 40
bm = bmesh.new()
sections = []
for i in range(N + 1):
    x = -0.225 + 0.45 * i / N
    # normal in plan
    dydx = -2 * SAG * x / 0.225 ** 2
    nx, ny = -dydx, 1.0
    L = math.hypot(nx, ny); nx, ny = nx / L, ny / L
    sec = []
    for (o, zz) in ((-RAIL_T / 2, 0), (RAIL_T / 2, 0), (RAIL_T / 2, RAIL_H), (-RAIL_T / 2, RAIL_H)):
        yy = rail_y(x, zz)
        sec.append(bm.verts.new((x + nx * o, yy + ny * o, ZR0 + zz)))
    sections.append(sec)
for a, b in zip(sections[:-1], sections[1:]):
    for k in range(4):
        bm.faces.new((a[k], a[(k + 1) % 4], b[(k + 1) % 4], b[k]))
bm.faces.new(list(reversed(sections[0]))); bm.faces.new(sections[-1])
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
rail = C.obj_from_bm(bm, f"{KEY}_toprail", R, m_wood)
bev = C.add_bevel(rail, 0.007, 3, angle=40)
C.smooth_by_angle(rail, 45)

sp = []
for i in range(7):
    t = (i - 3) / 3.0
    xb, xt = 0.150 * t, 0.192 * t
    yb = YB - 0.022
    pb = Vector((xb, yb, ztop(yb) - 0.01))
    pt = Vector((xt, rail_y(xt, 0.0), ZR0 + 0.012))
    sp.append(C.cyl_between(f"{KEY}_spindle_{i+1}", R, pb, pt, 0.0098, 0.0072, m_wood, verts=12))

# join small turned parts to keep object count low
def join(objs, name):
    with bpy.context.temp_override(active_object=objs[0], selected_editable_objects=objs, object=objs[0]):
        bpy.ops.object.join()
    objs[0].name = name; objs[0].data.name = name
    return objs[0]
C.clip_below(join(legs, f"{KEY}_legs"), 0.0)
join(st, f"{KEY}_stretchers")
join(sp, f"{KEY}_spindles")

C.finish(KEY, R, preview_kwargs=dict(target=(0, 0, 0.42), dist=2.4, elev=22, azim=-35),
         extra_views=[dict(target=(0, 0, 0.43), dist=2.4, elev=5, azim=90, lens=60),
                      dict(target=(0, 0, 0.43), dist=2.4, elev=5, azim=0, lens=60),
                      dict(target=(0, 0, 0.43), dist=2.4, elev=25, azim=150)])
