import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kitlib as K
import bmesh
from mathutils import Vector
bpy = K.bpy

# Teka Stone 50 B-TG 1B 1D, black metallic granite, 860 x 510 mm, inset.
# Origin = rim underside centre (z = 0 = worktop top). Bowl on the left, drainer on the right, front = -Y.
K.reset('sink_teka')
W, D = 0.860, 0.510
T = 0.012                      # rim / wall thickness
ZT = T                         # rim top
BX0, BX1 = -W / 2 + 0.0445, -W / 2 + 0.4275     # bowl opening x
BY0, BY1 = -D / 2 + 0.052, D / 2 - 0.049         # bowl opening y
bcx, bcy = (BX0 + BX1) / 2, (BY0 + BY1) / 2
bw, bd = BX1 - BX0, BY1 - BY0
DEPTH = 0.190                  # bowl depth below the rim top (inner floor)
N = 6

gran = K.mat('black metallic granite', '#ffffff', rough=0.42, img=os.path.join(K.TEX, 'sink_granite.png'), nonrepeat=False)

bm = bmesh.new()


def ring(w, h, r, z, cx, cy):
    return [bm.verts.new((x, y, z)) for x, y in K.rrect_pts(w, h, r, N, cx, cy)]


outer = ring(W, D, 0.012, ZT, 0, 0)
lip = ring(bw, bd, 0.040, ZT, bcx, bcy)
# top deck between outer edge and bowl opening
for i in range(len(outer)):
    j = (i + 1) % len(outer)
    bm.faces.new((outer[i], outer[j], lip[j], lip[i]))
# bowl: rounded lip then tapering walls, rounded bottom corner, flat floor
rings = [lip,
         ring(bw - 0.006, bd - 0.006, 0.037, ZT - 0.005, bcx, bcy),
         ring(bw - 0.012, bd - 0.012, 0.034, ZT - 0.014, bcx, bcy),
         ring(bw - 0.030, bd - 0.030, 0.030, ZT - DEPTH + 0.012, bcx, bcy),
         ring(bw - 0.042, bd - 0.042, 0.026, ZT - DEPTH + 0.002, bcx, bcy),
         ring(bw - 0.056, bd - 0.056, 0.020, ZT - DEPTH, bcx, bcy)]
for a, b in zip(rings[:-1], rings[1:]):
    for i in range(len(a)):
        j = (i + 1) % len(a)
        bm.faces.new((a[i], a[j], b[j], b[i]))
bm.faces.new(rings[-1])
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
# make all normals point up/into the bowl (towards the user)
for f in bm.faces:
    f.normal_update()
sink = K.mesh_obj('body', bm, gran)
# orient normals upward consistently
me = sink.data
up = sum((p.normal.z for p in me.polygons), 0.0)
if up < 0:
    for p in me.polygons:
        p.flip()
s = sink.modifiers.new('Solid', 'SOLIDIFY')
s.thickness = T
s.offset = -1.0
s.use_even_offset = True
K.smooth(sink, 40)
K.uv_cube(sink, 0.12)

# outer rim edge rounding: thin bevel ring band (visual)
# drainer ribs (4 grooves rendered as subtle raised beads)
rib = K.mat('drainer rib', '#2a2a2c', rough=0.3)
for y in (0.110, 0.052, -0.052, -0.110):
    K.box2(f'rib_{int(y * 1000)}', BX1 + 0.012, W / 2 - 0.085, y - 0.002, y + 0.002, ZT - 0.0005, ZT + 0.0008, rib, bev=0.0006, seg=2)
# drainer slight dish edge lines (soft depression outline)
for nm, (a, b, c, d) in {'f': (BX1 + 0.01, W / 2 - 0.03, -D / 2 + 0.03, -D / 2 + 0.033), 'b': (BX1 + 0.01, W / 2 - 0.03, D / 2 - 0.033, D / 2 - 0.03),
                         'r': (W / 2 - 0.033, W / 2 - 0.03, -D / 2 + 0.03, D / 2 - 0.03)}.items():
    K.box2(f'drainer_edge_{nm}', a, b, c, d, ZT - 0.0005, ZT + 0.0004, rib)

# chrome strainer waste + overflow
chrome = K.mat('chrome', '#d7d9db', rough=0.12, metal=1.0)
dx, dy = -W / 2 + 0.285, bcy
zf = ZT - DEPTH
K.lathe('strainer', [(0.0, zf + 0.0005), (0.034, zf + 0.0005), (0.045, zf + 0.0015), (0.045, zf + 0.003), (0.036, zf + 0.0035), (0.030, zf - 0.006), (0.0, zf - 0.006)],
        chrome, loc=(dx, dy, 0), verts=40)
K.lathe('strainer_basket', [(0.0, zf - 0.0045), (0.030, zf - 0.0045), (0.030, zf - 0.0035), (0.0, zf - 0.0035)], K.mat('basket', '#8d9093', rough=0.35, metal=0.9), loc=(dx, dy, 0), verts=32)
K.cyl('strainer_cap', 0.010, 0.004, (dx, dy, zf + 0.001), material=chrome, verts=24)
for i in range(12):
    a = 2 * math.pi * i / 12
    ob = K.box(f'strainer_slot_{i}', (0.012, 0.0025, 0.0006), (0.021, 0, zf - 0.0030), K.mat('slot', '#0c0c0c', rough=0.9))
    ob.location = (dx, dy, 0)
    ob.rotation_euler = (0, 0, a)
K.box2('overflow', BX1 - 0.010, BX1 - 0.006, dy - 0.012, dy + 0.012, ZT - 0.045, ZT - 0.030, chrome, bev=0.0015)
# Teka badge on the drainer (right)
K.box2('badge', W / 2 - 0.058, W / 2 - 0.050, -0.022, 0.022, ZT - 0.0003, ZT + 0.0007, chrome, bev=0.0004)

K.finish('sink_teka', [('', dict(view=(-0.35, -1.0, 1.0), floor=False)), ('_top', dict(view=(0, -0.01, 1), lens=60, floor=False))])
