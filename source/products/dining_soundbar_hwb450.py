"""Samsung HW-B450F soundbar (main unit), titan black.  Samsung spec: 858.8 x 59 x 75 mm (WxHxD), 1.8 kg.
Wraparound black speaker mesh on front and ends, chamfered (45 deg) front corners in plan, glossy hairline
'titan black' top cap with SAMSUNG logo at the front-left.  The wireless subwoofer (184x343x295) is a
separate box and is NOT part of this model.  Sits on the console: origin = centre of footprint at its bottom."""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import bpy, bmesh, numpy as np
from mathutils import Vector
import dining_common as C

KEY = "soundbar_hwb450"
C.reset()
R = C.root(KEY)
W, D, H = 0.8588, 0.075, 0.059

# fine perforated-mesh texture (tiles every 1 cm)
N = 128
yy, xx = np.mgrid[0:N, 0:N]
cell = 8
dx = (xx % cell) - cell / 2 + 0.5; dy = (yy % cell) - cell / 2 + 0.5
dots = (dx ** 2 + dy ** 2) < 5.0
col = np.where(dots[..., None], np.array([14, 14, 16]) / 255, np.array([44, 45, 50]) / 255)
img = bpy.data.images.new("soundbar_hwb450_mesh", N, N, alpha=False)
img.pixels.foreach_set(np.concatenate([col, np.ones((N, N, 1))], axis=2).astype(np.float32).ravel())
img.filepath_raw = os.path.join(C.ASSETS, "refs", "d_soundbar_hwb450_mesh.png")
img.file_format = 'PNG'; img.save(); img.pack()

m_grille = C.mat("soundbar_hwb450 grille", (36, 37, 41), rough=0.85, image=img)
m_top = C.mat("soundbar_hwb450 top", (36, 37, 42), rough=0.22, metal=0.3)
m_logo = C.mat("soundbar_hwb450 logo", (170, 172, 178), rough=0.3, metal=0.6)
m_foot = C.mat("soundbar_hwb450 foot", (18, 18, 18), rough=0.9)

CH = 0.020   # front corner chamfer in plan
plan = [(-W / 2, D / 2), (-W / 2, -D / 2 + CH), (-W / 2 + CH, -D / 2), (W / 2 - CH, -D / 2), (W / 2, -D / 2 + CH), (W / 2, D / 2)]

def prism(name, z0, z1, inset, mat, bevel):
    bm = bmesh.new()
    pts = []
    for x, y in plan:
        sx = -1 if x < 0 else 1; sy = -1 if y < 0 else 1
        pts.append((x - sx * inset, y - sy * inset))
    vs = [bm.verts.new((x, y, z0)) for x, y in pts]
    f = bm.faces.new(vs)
    if f.normal.z > 0:
        f.normal_flip()
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    nv = [g for g in r["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0, 0, z1 - z0), verts=nv)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = C.obj_from_bm(bm, name, R, mat)
    if bevel:
        C.add_bevel(o, bevel, 3, angle=30)
    # box-projected UVs, 1 cm tiles
    uvl = o.data.uv_layers.new(name="UVMap")
    for p in o.data.polygons:
        n = p.normal
        for li in p.loop_indices:
            co = o.data.vertices[o.data.loops[li].vertex_index].co
            if abs(n.z) > 0.7:
                uv = (co.x, co.y)
            elif abs(n.x) > abs(n.y):
                uv = (co.y, co.z)
            else:
                uv = (co.x + co.y, co.z)
            uvl.data[li].uv = (uv[0] / 0.01, uv[1] / 0.01)
    return o

ZF = 0.002   # rubber feet
prism(f"{KEY}_grille", ZF, H - 0.011, 0.0008, m_grille, 0.004)
prism(f"{KEY}_topcap", H - 0.0115, H, 0.0, m_top, 0.003)
for sx in (-1, 1):
    C.box(f"{KEY}_foot_{'L' if sx < 0 else 'R'}", R, (0.10, 0.04, ZF), (sx * 0.30, 0.005, ZF / 2), m_foot, bevel=0.0008, segs=1)
# SAMSUNG wordmark on the top cap, front-left (as on the Samsung close-up)
C.box(f"{KEY}_logo", R, (0.028, 0.0035, 0.0002), (-W / 2 + 0.05, -D / 2 + 0.010, H + 0.0001), m_logo)
# top button strip (centre), slightly different finish
C.box(f"{KEY}_buttons", R, (0.085, 0.012, 0.0003), (0, 0.008, H + 0.0001), C.mat("soundbar_hwb450 buttons", (28, 29, 33), rough=0.5))

C.finish(KEY, R, preview_kwargs=dict(target=(0, 0, 0.03), dist=1.5, elev=20, azim=30),
         extra_views=[dict(target=(-0.38, -0.02, 0.03), dist=0.3, elev=25, azim=-40, floor=False)])
