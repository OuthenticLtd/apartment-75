"""Samsung 65" Mini LED M72H (UE65M72HAUXXH).  Samsung datasheet: 1444.1 x 831.2 x 76.8 mm without stand,
VESA 400x300.  Slim black bezel (~7 mm top/sides, ~11 mm bottom), thin upper panel (~2.6 cm) that tapers into
a deeper rear electronics housing in the lower half (side profile from Samsung image).
Wall-mounted: origin = centre of the back face at its bottom edge, back on y = 0, front toward -Y."""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import bpy, bmesh
from mathutils import Vector
import dining_common as C

KEY = "tv_samsung65"
C.reset()
R = C.root(KEY)
W, H, D = 1.4441, 0.8312, 0.0768
m_bez = C.mat("tv_samsung65 bezel", (14, 14, 15), rough=0.6, metal=0.1)
m_scr = C.mat("tv_samsung65 screen", (20, 22, 27), rough=0.05)
m_back = C.mat("tv_samsung65 back", (38, 38, 40), rough=0.7)

def extrude_profile(name, prof, width, mat, bevel=0.0):
    bm = bmesh.new()
    vs = [bm.verts.new((-width / 2, y, z)) for y, z in prof]
    f = bm.faces.new(vs)
    bmesh.ops.recalc_face_normals(bm, faces=[f])
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    nv = [g for g in r["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(width, 0, 0), verts=nv)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = C.obj_from_bm(bm, name, R, mat)
    if bevel:
        C.add_bevel(o, bevel, 2, angle=30)
    return o

YF = -D            # front plane
PT = 0.026         # thin panel thickness
# panel body (bezel colour), front at YF + 1 mm (frame sits in front)
body = extrude_profile(f"{KEY}_panel", [(YF + 0.001, 0.0), (YF + PT, 0.0), (YF + PT, H), (YF + 0.001, H)], W, m_back, bevel=0.002)
body.data.materials.append(m_bez)
for p in body.data.polygons:
    if p.normal.y < -0.5 or abs(p.normal.x) > 0.5 or abs(p.normal.z) > 0.5:
        p.material_index = 1   # front and edges black bezel colour; only the rear stays back colour
# rear electronics housing (narrower, tapered top)
HW = 1.30
prof = [(YF + PT - 0.001, 0.035), (YF + PT - 0.001, 0.665), (-0.040, 0.585), (-0.012, 0.505), (0.0, 0.48),
        (0.0, 0.075), (-0.010, 0.050), (-0.030, 0.035)]
extrude_profile(f"{KEY}_housing", prof, HW, m_back, bevel=0.006)
# bezel frame (7 mm sides/top, 11 mm bottom), 1 mm proud of the body
BT, BB = 0.007, 0.011
fr = []
for nm, size, loc in (("top", (W, 0.001, BT), (0, YF + 0.0005, H - BT / 2)),
                      ("bot", (W, 0.001, BB), (0, YF + 0.0005, BB / 2)),
                      ("L", (BT, 0.001, H), (-W / 2 + BT / 2, YF + 0.0005, H / 2)),
                      ("R", (BT, 0.001, H), (W / 2 - BT / 2, YF + 0.0005, H / 2))):
    fr.append(C.box(f"{KEY}_bezel_{nm}", R, size, loc, m_bez))
with bpy.context.temp_override(active_object=fr[0], selected_editable_objects=fr, object=fr[0]):
    bpy.ops.object.join()
fr[0].name = f"{KEY}_bezel"
# screen glass, recessed 0.4 mm behind the frame face
C.box(f"{KEY}_screen", R, (W - 2 * BT, 0.0006, H - BT - BB), (0, YF + 0.0007, BB + (H - BT - BB) / 2), m_scr)
# small control/IR nub under the bottom bezel centre (within the bottom bezel, no protrusion)
C.box(f"{KEY}_ir", R, (0.040, 0.0012, 0.006), (0, YF + 0.0004, 0.0045), C.mat("tv_samsung65 ir", (55, 55, 58), rough=0.3))

C.finish(KEY, R, preview_kwargs=dict(target=(0, -0.04, 0.42), dist=3.4, elev=8, azim=30, floor=False, wall=True),
         extra_views=[dict(target=(0, -0.04, 0.42), dist=2.5, elev=2, azim=88, floor=False, lens=40),
                      dict(target=(0, -0.04, 0.42), dist=3.4, elev=10, azim=150, floor=False)])
