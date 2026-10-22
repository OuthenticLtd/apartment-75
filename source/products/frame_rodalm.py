import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
from mathutils import Vector
import plib
import wallprev  # noqa: preview colour management tweak
from plib import mat, obj_from_bm, box

KEY = "frame_rodalm"
TEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tex")
plib.reset()
R = plib.root(KEY)

# IKEA RÖDALM 61x91, oak effect: frame 63 x 93, depth 3 cm (IKEA measurements tab)
OW, OH, DEP = 0.63, 0.93, 0.03
F = 0.018            # visible moulding face width (from 61x91 room photo, ~1.8 cm)
MAT_REC = 0.010      # mat sits 1 cm behind the front face (box-frame look)
OPEN_W, OPEN_H = 0.49, 0.69  # mat opening
PRINT_W, PRINT_H = 0.52, 0.72
CZ = OH / 2


def tex_mat(name, img_path, rough, rgb_fallback):
    m = mat(name, rgb_fallback, rough=rough)
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    t = nt.nodes.new('ShaderNodeTexImage')
    t.image = bpy.data.images.load(img_path)
    t.location = (-400, 200)
    nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    return m


OAK = tex_mat(KEY + " oak", os.path.join(TEX, "frame_rodalm_oak.png"), 0.6, (210, 178, 138))
MAT = mat(KEY + " mat", (246, 245, 241), rough=0.9)
PRINT = tex_mat(KEY + " print", os.path.join(TEX, "frame_rodalm_print.png"), 0.85, (236, 226, 208))
BACK = mat(KEY + " backing", (120, 100, 80), rough=0.9)

hw, ih = OW / 2, OH
iw = hw - F
# members as mitred prisms: 2D corner points in (x, z), outer edge first
members = {
    "top":    [(-hw, OH), (hw, OH), (iw, OH - F), (-iw, OH - F)],
    "bottom": [(hw, 0), (-hw, 0), (-iw, F), (iw, F)],
    "left":   [(-hw, 0), (-hw, OH), (-iw, OH - F), (-iw, F)],
    "right":  [(hw, OH), (hw, 0), (iw, F), (iw, OH - F)],
}
for name, pts in members.items():
    bm = bmesh.new()
    front = [bm.verts.new((x, -DEP, z)) for x, z in pts]
    back = [bm.verts.new((x, 0.0, z)) for x, z in pts]
    bm.faces.new(front)
    bm.faces.new(list(reversed(back)))
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((front[i], back[i], back[j], front[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    horiz = name in ("top", "bottom")
    uv = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        nrm = f.normal
        for l in f.loops:
            co = l.vert.co
            u = (co.x if horiz else co.z) / 0.6
            if abs(nrm.y) > 0.5:          # front / back face
                v = (co.z if horiz else co.x) / 0.15
            else:                          # sides
                v = co.y / 0.15 + 0.37
            l[uv].uv = (u, v)
    ob = obj_from_bm(f"{KEY}_moulding_{name}", bm, R, OAK, smooth=False)
    md = plib.add_bevel(ob, 0.0007, 1, angle=30)

# mat board with opening (1.5 mm), spanning the inner opening
bm = bmesh.new()
y0, y1 = -DEP + MAT_REC, -DEP + MAT_REC + 0.0015
ow2, oh2 = iw + 0.001, (OH - 2 * F) / 2 + 0.001
pw, ph = OPEN_W / 2, OPEN_H / 2
outer = [(-ow2, -oh2), (ow2, -oh2), (ow2, oh2), (-ow2, oh2)]
inner = [(-pw, -ph), (pw, -ph), (pw, ph), (-pw, ph)]
def ring(y):
    o = [bm.verts.new((x, y, CZ + z)) for x, z in outer]
    i = [bm.verts.new((x, y, CZ + z)) for x, z in inner]
    return o, i
fo, fi = ring(y0)
bo, bi = ring(y1)
for k in range(4):
    j = (k + 1) % 4
    bm.faces.new((fo[k], fo[j], fi[j], fi[k]))     # front
    bm.faces.new((bo[j], bo[k], bi[k], bi[j]))     # back
    bm.faces.new((fi[k], fi[j], bi[j], bi[k]))     # opening edge
    bm.faces.new((fo[j], fo[k], bo[k], bo[j]))     # outer edge
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
obj_from_bm(f"{KEY}_mat", bm, R, MAT, smooth=False)

# print (plane facing -Y) just behind the mat
bm = bmesh.new()
yp = y1 + 0.0003
vs = [bm.verts.new((x, yp, CZ + z)) for x, z in
      [(-PRINT_W / 2, -PRINT_H / 2), (PRINT_W / 2, -PRINT_H / 2), (PRINT_W / 2, PRINT_H / 2), (-PRINT_W / 2, PRINT_H / 2)]]
f = bm.faces.new(vs)
f.normal_update()
if f.normal.y > 0:
    f.normal_flip()
uv = bm.loops.layers.uv.new("UVMap")
for l in f.loops:
    l[uv].uv = ((l.vert.co.x + PRINT_W / 2) / PRINT_W, (l.vert.co.z - CZ + PRINT_H / 2) / PRINT_H)
obj_from_bm(f"{KEY}_print", bm, R, PRINT, smooth=False)

# hardboard back (closes the back)
box(f"{KEY}_backboard", R, (-iw - 0.001, -0.004, F - 0.001), (iw + 0.001, -0.001, OH - F + 0.001), BACK)

plib.stats(KEY)
plib.save(KEY)
plib.preview(KEY, (0.95, -1.75, 0.75), (0.0, 0.0, 0.465), lens=50, wall=True)
plib.preview(KEY, (0.12, -0.32, 0.86), (0.25, 0.0, 0.80), lens=35, wall=True,
             out=os.path.join(plib.ASSETS, "previews", KEY + "_corner.png"))
