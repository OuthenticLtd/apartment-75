import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
from mathutils import Vector, Matrix
import plib
import wallprev  # noqa: preview colour management tweak
from plib import mat, obj_from_bm, box, cylinder

KEY = "sconce_lagos"
plib.reset()
R = plib.root(KEY)

# Sollux SL.0330 LAGOS 2 (maker drawing): tube Ø6 cm, height 30 cm, projection 8 cm
H = 0.30
RO = 0.030          # outer radius
T = 0.0012          # wall thickness
GAP = 0.020         # wall-to-tube gap (bracket depth) -> 8 cm projection
YC = -(GAP + RO)
REC = 0.024         # bulb recess at each end

BODY = mat(KEY + " body", (30, 30, 32), rough=0.55)
INNER = mat(KEY + " inner", (18, 18, 19), rough=0.7)
LENS = mat(KEY + " lens", (236, 236, 230), rough=0.25)


def lathe(name, prof, material, seg=40):
    bm = bmesh.new()
    vs = [bm.verts.new((r, 0, z)) for r, z in prof]
    es = [bm.edges.new((vs[i], vs[i + 1])) for i in range(len(vs) - 1)]
    bmesh.ops.spin(bm, geom=vs + es, cent=(0, 0, 0), axis=(0, 0, 1), angle=2 * math.pi, steps=seg, use_duplicate=False)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.translate(bm, verts=bm.verts, vec=Vector((0, YC, 0)))
    return obj_from_bm(name, bm, R, material)


# tube shell with rolled rims (outer + inner wall)
prof = [(RO - T, REC + 0.004), (RO - T, 0.0006), (RO - 0.0004, 0.0), (RO, 0.0006),
        (RO, H - 0.0006), (RO - 0.0004, H), (RO - T, H - 0.0006), (RO - T, H - REC - 0.004)]
tube = lathe(f"{KEY}_tube", prof, BODY, 40)
# sharp edges stay crisp: mark smooth only on the barrel
# inner black lamp holders + GU10 lenses (down and up)
for nm, z_face, sgn in (("down", REC, 1), ("up", H - REC, -1)):
    # dark reflector cup closing the tube
    lathe(f"{KEY}_reflector_{nm}", [(0.0, z_face + sgn * 0.006), (0.024, z_face + sgn * 0.006),
                                    (RO - T, z_face - sgn * 0.004), (RO - T, z_face + sgn * 0.004)], INNER, 32)
    lathe(f"{KEY}_lens_{nm}", [(0.0, z_face), (0.0215, z_face), (0.0235, z_face + sgn * 0.003),
                               (0.0235, z_face + sgn * 0.0055)], LENS, 32)

# wall bracket: narrow vertical plate between tube and wall
BZ0, BZ1 = 0.105, 0.185
b = box(f"{KEY}_bracket", R, (-0.0085, YC + RO - 0.004, BZ0), (0.0085, 0.0, BZ1), BODY, bevel=0.0012, seg=2)

plib.stats(KEY)
plib.save(KEY)
plib.preview(KEY, (0.42, -0.62, 0.30), (0.0, -0.04, 0.15), lens=50, wall=True)
plib.preview(KEY, (0.10, -0.45, -0.18), (0.0, -0.05, 0.05), lens=50, wall=True,
             out=os.path.join(plib.ASSETS, "previews", KEY + "_below.png"))
