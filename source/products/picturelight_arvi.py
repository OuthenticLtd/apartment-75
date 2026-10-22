import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
from mathutils import Vector
import plib
import wallprev  # noqa: preview colour management tweak
from plib import mat, obj_from_bm, box

KEY = "picturelight_arvi"
plib.reset()
R = plib.root(KEY)

# Zuma Line ARVI W89551-40BK: 40 cm long, 9 cm projection, 4 cm high (maker drawing / zumaline.lighting)
L, DEPTH, HGT = 0.40, 0.09, 0.04
BAR = 0.015                      # square bar section (drawing ~1.2, photo ~1.6 cm)
BODY = mat(KEY + " body", (28, 28, 30), rough=0.5)
DIFF = mat(KEY + " diffuser", (245, 243, 236), rough=0.35)

# light bar at the front, top-aligned
yb1, yb0 = -DEPTH, -DEPTH + BAR
zb0, zb1 = HGT - BAR, HGT
box(f"{KEY}_bar", R, (-L / 2, yb1, zb0), (L / 2, yb0, zb1), BODY, bevel=0.0012, seg=2)
# opal diffuser strip on the underside (slightly proud of the black profile edge)
box(f"{KEY}_diffuser", R, (-L / 2 + 0.003, yb1 + 0.0015, zb0 - 0.0006), (L / 2 - 0.003, yb0 - 0.0015, zb0 + 0.001), DIFF)

# arm: D-shaped flat plate from the wall to the bar (plan: straight back, round front)
AW = 0.095
r = AW / 2
ystraight = -(DEPTH - BAR / 2 - r)   # semicircle centre so apex reaches bar centre
bm = bmesh.new()
pts = [(-r, 0.0), (r, 0.0)]
n = 24
for i in range(n + 1):
    a = -math.pi * i / n  # 0 .. -pi (front half)
    pts.append((r * math.cos(a), ystraight + r * math.sin(a)))
pts.append((-r, 0.0))
pts = pts[:-1]
# order: (-r,0) -> (r,0) -> arc from (r, yc) round to (-r, yc)
z0, z1 = HGT - BAR, HGT
bot = [bm.verts.new((x, y, z0)) for x, y in pts]
top = [bm.verts.new((x, y, z1)) for x, y in pts]
bm.faces.new(top)
bm.faces.new(list(reversed(bot)))
for i in range(len(pts)):
    j = (i + 1) % len(pts)
    bm.faces.new((bot[i], bot[j], top[j], top[i]))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
arm = obj_from_bm(f"{KEY}_arm", bm, R, BODY, smooth=False)
plib.add_bevel(arm, 0.001, 2, angle=30)
arm.data.polygons.foreach_set('use_smooth', [True] * len(arm.data.polygons))
md = arm.modifiers.new("WN", 'WEIGHTED_NORMAL')
md.keep_sharp = True

# wall plate (driver box) below the arm
box(f"{KEY}_wallplate", R, (-0.04, -0.016, 0.0), (0.04, 0.0, HGT - BAR + 0.0005), BODY, bevel=0.0015, seg=2)

plib.stats(KEY)
plib.save(KEY)
plib.preview(KEY, (0.40, -0.55, -0.12), (0.0, -0.05, 0.02), lens=50, wall=True)
plib.preview(KEY, (0.25, -0.35, 0.30), (0.0, -0.05, 0.02), lens=50, wall=True,
             out=os.path.join(plib.ASSETS, "previews", KEY + "_above.png"))
