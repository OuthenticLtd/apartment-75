"""JYSK AABENRAA dining table 80x120, warm oak / black.  Dimensions from JYSK manual 3670323:
top 1200x800x30, leg frames 750 (Y) x 718 (Z) x 40 (X) of 40x20 tube, rails 1044x50x15,
inner leg distance 1020 / 710, under-table height 668, felt pads 35x35x3."""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import bpy, bmesh, numpy as np
from mathutils import Vector
import dining_common as C

KEY = "table_aabenraa"
C.reset()
R = C.root(KEY)

# ---------- oak decor texture (1024x512, grain along X / table length) ----------
W, H = 1024, 512
rng = np.random.default_rng(7)
u = np.linspace(0, 1, W, endpoint=False)[None, :]
v = np.linspace(0, 1, H, endpoint=False)[:, None]

def smooth_noise_1d(n, k, scale):
    x = rng.standard_normal(n + 2 * k)
    ker = np.hanning(2 * k + 1); ker /= ker.sum()
    return np.convolve(x, ker, mode='same')[k:k + n] * scale

warp = (0.004 * np.sin(u * 2 * np.pi * 1.3 + 0.7) + 0.003 * np.sin(u * 2 * np.pi * 3.1 + 2.0)
        + smooth_noise_1d(W, 80, 0.03)[None, :])
# cathedral arches (flat-sawn oak) in two bands, straight grain elsewhere
band1 = np.exp(-((v - 0.42) / 0.12) ** 2)
band2 = np.exp(-((v - 0.80) / 0.08) ** 2)
arch1 = 0.10 * np.exp(-((u - 0.30) / 0.22) ** 2)
arch2 = 0.06 * np.exp(-((u - 0.75) / 0.15) ** 2)
f = (v + warp - arch1 * band1 - arch2 * band2) * 150
ring = np.abs(np.sin(np.pi * f)) ** 12          # thin dark late-wood lines
ring = ring * (0.6 + 0.4 * np.abs(np.sin(np.pi * f / 3.7)))
# fine pores: per-row random values stretched along u
rows = rng.random((H, 1))
pores = np.repeat(rows, W, axis=1)
pn = np.cumsum(rng.standard_normal((H, W)) * 0.02, axis=1)
pores = np.clip(pores + pn * 0.2, 0, 1)
pores = (pores > 0.82).astype(float) * 0.5 + rng.random((H, W)) * 0.08
tone = 0.5 + 0.5 * np.sin(v * 2 * np.pi * 2.3 + warp * 8)  # broad light/dark bands
base = np.array([196, 157, 103], float) / 255
dark = np.array([150, 108, 60], float) / 255
light = np.array([214, 178, 124], float) / 255
t = (0.55 * ring + 0.35 * pores)[..., None]
col = base * (1 - t) + dark * t
col = col * (1 - 0.25 * tone[..., None]) + light * (0.25 * tone[..., None])
col = np.clip(col, 0, 1)
img = bpy.data.images.new("table_aabenraa_oak", W, H, alpha=False)
px_s = np.concatenate([col, np.ones((H, W, 1))], axis=2)[::-1].astype(np.float32)
img.pixels.foreach_set(px_s.ravel())
img.filepath_raw = os.path.join(C.ASSETS, "refs", "d_table_aabenraa_oak.png")
img.file_format = 'PNG'
img.save()
img.pack()

m_top = C.mat("table_aabenraa top", (194, 154, 100), rough=0.55, image=img)
m_steel = C.mat("table_aabenraa steel", (38, 39, 39), rough=0.55, metal=0.3)
m_felt = C.mat("table_aabenraa felt", (60, 60, 60), rough=1.0)
m_bolt = C.mat("table_aabenraa bolt", (20, 20, 20), rough=0.35, metal=0.6)

# ---------- top 1200 x 800 x 30 ----------
Z0, ZF, ZT = 0.003, 0.720, 0.750
top = C.box(f"{KEY}_top", R, (1.2, 0.8, 0.03), (0, 0, (ZF + ZT) / 2), m_top, bevel=0.0015, segs=2)
# planar UVs: top/bottom faces by (x, y); sides by (x|y, z) with grain running along edge
me = top.data
uvl = me.uv_layers.new(name="UVMap")
for p in me.polygons:
    n = p.normal
    for li in p.loop_indices:
        co = me.vertices[me.loops[li].vertex_index].co
        if abs(n.z) > 0.5:
            uv = (co.x / 1.2 + 0.5, co.y / 0.8 * 0.66 + 0.5)
        elif abs(n.y) > 0.5:   # ABS edge band: straight fine grain
            uv = (co.x / 1.2 + 0.5, 0.05 + (co.z - ZF) * 0.25)
        else:
            uv = (co.y / 1.2 + 0.5, 0.95 + (co.z - ZF) * 0.25)
        uvl.data[li].uv = uv

# ---------- two closed leg frames: 40 (X) x 20 (Y/Z) tube ----------
TX, TT = 0.040, 0.020
FY = 0.750 / 2
for side, sx in (("L", -1), ("R", 1)):
    xc = sx * (0.510 + TX / 2)
    bm = bmesh.new()
    parts = [
        ((TX, TT, ZF - Z0), (xc, -FY + TT / 2, (Z0 + ZF) / 2)),   # front leg
        ((TX, TT, ZF - Z0), (xc, FY - TT / 2, (Z0 + ZF) / 2)),    # back leg
        ((TX, 2 * FY - 2 * TT, TT), (xc, 0, ZF - TT / 2)),        # top bar
        ((TX, 2 * FY - 2 * TT, TT), (xc, 0, Z0 + TT / 2)),        # floor bar
    ]
    for size, loc in parts:
        g = bmesh.ops.create_cube(bm, size=1.0)
        vs = g["verts"]
        bmesh.ops.scale(bm, vec=Vector(size), verts=vs)
        bmesh.ops.translate(bm, vec=Vector(loc), verts=vs)
    o = C.obj_from_bm(bm, f"{KEY}_frame_{side}", R, m_steel)
    C.add_bevel(o, 0.0015, 2)
    # felt pads under the floor bar ends (35x35x3)
    for sy in (-1, 1):
        C.box(f"{KEY}_pad_{side}{'F' if sy < 0 else 'B'}", R, (0.035, 0.035, Z0),
              (xc, sy * (FY - 0.0175), Z0 / 2), m_felt)

# ---------- long rails 1044 x 50 x 15, flush under the top, inside the leg line ----------
for side, sy in (("F", -1), ("B", 1)):
    yc = sy * (FY - TT - 0.0075)
    C.box(f"{KEY}_rail_{side}", R, (1.044, 0.015, 0.050), (0, yc, ZF - 0.025), m_steel, bevel=0.001, segs=1)
    # two hex-socket bolt heads at each rail end (visible on JYSK detail photo)
    bm_all = []
    for ex in (-1, 1):
        for zz in (ZF - 0.014, ZF - 0.036):
            p1 = Vector((ex * 0.488, yc + sy * 0.0075, zz))
            p2 = p1 + Vector((0, sy * 0.003, 0))
            b = C.cyl_between(f"{KEY}_bolt_{side}{'L' if ex < 0 else 'R'}{int(zz*1000)}", R, p1, p2, 0.0065, 0.006, m_bolt, verts=12)
            bm_all.append(b)
    # join bolts of this rail into one object
    with bpy.context.temp_override(active_object=bm_all[0], selected_editable_objects=bm_all, object=bm_all[0]):
        bpy.ops.object.join()
    bm_all[0].name = f"{KEY}_bolts_{side}"
    bm_all[0].data.name = bm_all[0].name

C.finish(KEY, R, preview_kwargs=dict(target=(0, 0, 0.38), dist=2.9, elev=20, azim=35),
         extra_views=[dict(target=(-0.5, -0.36, 0.68), dist=0.5, elev=8, azim=40, floor=False)])
