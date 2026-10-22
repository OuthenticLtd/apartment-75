import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
import numpy as np
from mathutils import Vector
import plib
from plib import box, cylinder, mat, obj_from_bm

KEY = "coffee_listerby"
cm = 0.01
plib.reset()
R = plib.root(KEY)

# ---------- oak veneer grain texture (procedural, 1024 px, packed) ----------
def oak_image(name, base=(214, 172, 124), size=1024, seed=3):
    rng = np.random.default_rng(seed)
    H = W = size
    v = np.linspace(0, 1, H)[:, None]
    u = np.linspace(0, 1, W)[None, :]
    # grain lines run along u (x of image); variation across v
    warp = 0.004 * np.sin(u * 2 * np.pi * 3 + 1.3) + 0.002 * np.sin(u * 2 * np.pi * 7)
    vv = v + warp
    g = np.zeros((H, W))
    for f, a in ((70, 0.35), (160, 0.35), (330, 0.3), (700, 0.2)):
        ph = rng.uniform(0, 6.28)
        g += a * np.sin(vv * 2 * np.pi * f + ph + 2.0 * np.sin(vv * 2 * np.pi * 3 + ph))
    n = rng.normal(0, 1, (H, 1)) * 0.25
    g = g + n
    # occasional ray flecks
    fl = (rng.random((H, W)) > 0.9993).astype(float)
    g = g / np.abs(g).max()
    shade = 1.0 + 0.08 * g - 0.08 * fl
    img = np.zeros((H, W, 4))
    for i in range(3):
        img[..., i] = np.clip(base[i] / 255.0 * shade, 0, 1)
    img[..., 3] = 1
    # srgb image
    im = bpy.data.images.new(name, W, H, alpha=False)
    im.pixels = img[::-1].ravel()
    p = os.path.join(plib.ASSETS, "scripts", name + ".png")
    im.filepath_raw = p
    im.file_format = 'PNG'
    im.save()
    im.pack()
    return im


IMG = oak_image("coffee_listerby_oak_grain")


def oak_mat(name, tint=(1, 1, 1), rough=0.45):
    m = mat(name, (214, 176, 138), rough=rough)
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    t = nt.nodes.new('ShaderNodeTexImage')
    t.image = IMG
    nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    return m


OAK = oak_mat(KEY + " oak veneer")
SOLID = oak_mat(KEY + " solid oak", rough=0.5)
FELT = mat(KEY + " glide", (235, 235, 230), rough=0.6)


def uv_project(ob, axis_u, axis_v, scale=1.0, off=(0.5, 0.5)):
    me = ob.data
    uvl = me.uv_layers.new(name="UVMap")
    for poly in me.polygons:
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            uvl.data[li].uv = (co[axis_u] * scale + off[0], co[axis_v] * scale + off[1])


def uv_cyl(ob, axis=2, scale=1.0):
    """grain along cylinder axis: u = axial, v = angle."""
    me = ob.data
    uvl = me.uv_layers.new(name="UVMap")
    others = [i for i in range(3) if i != axis]
    for poly in me.polygons:
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            ang = math.atan2(co[others[1]], co[others[0]]) * 0.03
            uv = (co[axis] * scale + 0.3, ang + 0.5)
            uvl.data[li].uv = uv


# ---------- dimensions (cm) ----------
L, Wd, H = 140.0, 60.0, 37.0
TOP_T = 3.6
RC = 15.0          # corner radius of the top (soft rounded ends)

# ---------- table top: rounded rectangle slab ----------
bm = bmesh.new()
pts = []
hx, hy = L / 2, Wd / 2
for cx, cy, a0 in ((hx - RC, hy - RC, 0), (-hx + RC, hy - RC, 90), (-hx + RC, -hy + RC, 180), (hx - RC, -hy + RC, 270)):
    for k in range(17):
        a = math.radians(a0 + 90 * k / 16)
        pts.append((cx + RC * math.cos(a), cy + RC * math.sin(a)))
z0, z1 = H - TOP_T, H
vb = [bm.verts.new((x * cm, y * cm, z0 * cm)) for x, y in pts]
vt = [bm.verts.new((x * cm, y * cm, z1 * cm)) for x, y in pts]
n = len(pts)
for i in range(n):
    j = (i + 1) % n
    bm.faces.new((vb[i], vb[j], vt[j], vt[i]))
bm.faces.new(vt)
bm.faces.new(list(reversed(vb)))
bm.normal_update()
top = obj_from_bm(f"{KEY}_top", bm, R, OAK)
md = top.modifiers.new("Bevel", 'BEVEL')
md.width = 0.5 * cm
md.segments = 3
md.limit_method = 'ANGLE'
md.angle_limit = math.radians(30)
uv_project(top, 0, 1, scale=0.62)
# side edge-band normals look better with weighted normals
top.modifiers.new("WN", 'WEIGHTED_NORMAL').keep_sharp = True

# ---------- legs (solid oak, round, glide at foot) ----------
LEG_R = 2.0
LX = hx - 13.0     # leg centre x
LY = hy - 4.5      # leg centre y
for sx in (-1, 1):
    for sy in (-1, 1):
        nm = ("L" if sx < 0 else "R") + ("F" if sy < 0 else "B")
        lg = cylinder(f"{KEY}_leg_{nm}", R, LEG_R * cm, LEG_R * cm, 0.4 * cm, z0 * cm,
                      sx * LX * cm, sy * LY * cm, seg=24, material=SOLID)
        plib.add_bevel(lg, 0.25 * cm, 2, angle=60)
        uv_cyl(lg)
        cylinder(f"{KEY}_glide_{nm}", R, 1.6 * cm, 1.6 * cm, 0, 0.4 * cm, sx * LX * cm, sy * LY * cm,
                 seg=16, material=FELT)

# ---------- apron frame under the top ----------
AP_H, AP_T = 4.0, 2.2
za0, za1 = (z0 - AP_H) * cm, z0 * cm
for sy in (-1, 1):  # long aprons, set inside the legs
    yc = sy * (LY - 0.3)
    ap = box(f"{KEY}_apron_{'F' if sy < 0 else 'B'}", R, (-(LX - LEG_R) * cm, (yc - AP_T / 2) * cm, za0),
             ((LX - LEG_R) * cm, (yc + AP_T / 2) * cm, za1), SOLID, bevel=0.2 * cm, seg=2)
    uv_project(ap, 0, 2, scale=0.62)
for sx in (-1, 1):  # end cross rails
    xc = sx * LX
    ap = box(f"{KEY}_apron_{'L' if sx < 0 else 'R'}", R, ((xc - AP_T / 2) * cm, -(LY - LEG_R) * cm, za0),
             ((xc + AP_T / 2) * cm, (LY - LEG_R) * cm, za1), SOLID, bevel=0.2 * cm, seg=2)
    uv_project(ap, 1, 2, scale=0.62)

# ---------- lower shelf: round rails + dowel slats ----------
RAIL_R = 1.5
ZR = 12.0 + RAIL_R  # rail underside at 12 cm (IKEA: 12 cm under shelf)
for sy in (-1, 1):
    c = cylinder(f"{KEY}_shelfrail_{'F' if sy < 0 else 'B'}", R, RAIL_R * cm, RAIL_R * cm,
                 -(LX) * cm, (LX) * cm, seg=16, material=SOLID)
    c.rotation_euler = (0, math.radians(90), 0)
    c.location = (0, sy * LY * cm, ZR * cm)
    uv_cyl(c)
for sx in (-1, 1):
    c = cylinder(f"{KEY}_shelfrail_{'L' if sx < 0 else 'R'}", R, RAIL_R * cm, RAIL_R * cm,
                 -(LY) * cm, (LY) * cm, seg=16, material=SOLID)
    c.rotation_euler = (math.radians(90), 0, 0)
    c.location = (sx * LX * cm, 0, ZR * cm)
    uv_cyl(c)
N_SLAT = 15
SLAT_R = 1.0
span = 2 * LX - 2 * LEG_R - 8.0
for i in range(N_SLAT):
    x = -span / 2 + span * i / (N_SLAT - 1)
    c = cylinder(f"{KEY}_slat_{i:02d}", R, SLAT_R * cm, SLAT_R * cm, -(LY) * cm, (LY) * cm,
                 seg=12, material=SOLID)
    c.rotation_euler = (math.radians(90), 0, 0)
    c.location = (x * cm, 0, (ZR + RAIL_R * 0.55) * cm)
    uv_cyl(c)

plib.stats(KEY)
plib.save(KEY)
plib.preview(KEY, (1.7, -2.2, 1.15), (0.0, 0.0, 0.17), lens=50)
plib.preview(KEY, (0.0, -2.8, 0.25), (0.0, 0.0, 0.2), lens=50,
             out=os.path.join(plib.ASSETS, "previews", KEY + "_front.png"))
