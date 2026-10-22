import sys, os, math, bmesh
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bedhall_common as C
from mathutils import Vector
C.reset("mirror_lindbyn")
W, H, D = 0.60, 1.20, 0.025
frame = C.mat("frame", C.hexcol("1c1c1c"), rough=0.45, metal=0.3)
glass = C.mat("mirror", (0.82, 0.84, 0.85), rough=0.03, metal=1.0)
back = C.mat("back", C.hexcol("2b2b2b"), rough=0.9)

def stadium(off, n=40):
    r = W/2 - off; hs = H/2 - W/2  # half straight length
    pts = []
    for i in range(n+1):  # top arc, from right to left
        a = math.pi * i / n
        pts.append((r*math.cos(a), hs + r*math.sin(a)))
    for i in range(n+1):
        a = math.pi + math.pi * i / n
        pts.append((r*math.cos(a), -hs + r*math.sin(a)))
    return pts

def sweep(name, prof, material, n=40):
    bm = bmesh.new(); rings = []
    for off, d in prof:
        rings.append([bm.verts.new((x, -d, z + H/2)) for x, z in stadium(off, n)])
    m = len(rings[0])
    for a, b in zip(rings[:-1], rings[1:]):
        for i in range(m):
            j = (i+1) % m
            bm.faces.new((a[i], a[j], b[j], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return C.mesh_from_bm(bm, name, material, smooth=True)

def flat(name, off, d0, d1, material, n=40):
    bm = bmesh.new()
    pts = stadium(off, n)
    f0 = bm.faces.new([bm.verts.new((x, -d0, z + H/2)) for x, z in pts])
    f1 = bm.faces.new([bm.verts.new((x, -d1, z + H/2)) for x, z in reversed(pts)])
    v0 = list(f0.verts); v1 = list(reversed(list(f1.verts)))
    m = len(v0)
    for i in range(m):
        j = (i+1) % m
        bm.faces.new((v0[i], v0[j], v1[j], v1[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = C.mesh_from_bm(bm, name, material)
    for p in ob.data.polygons: p.use_smooth = abs(p.normal.y) < 0.9
    return ob

# thin black frame, ~9 mm visible face, tubular-ish rounded profile
prof = [(0.012, 0.0), (0.001, 0.0), (0.0, 0.002), (0.0, D-0.004), (0.0015, D-0.0008), (0.004, D),
        (0.0075, D-0.0005), (0.0095, D-0.003), (0.0095, D-0.007), (0.012, D-0.007), (0.012, 0.0)]
sweep("frame", prof, frame)
flat("glass", 0.0094, D-0.011, D-0.007, glass)
flat("backing", 0.012, 0.002, 0.005, back)
C.box("hanger", (0.05, 0.002, 0.015), (0, -0.001, H-0.12), C.mat("hanger", (0.6, 0.6, 0.6), 0.4, 1.0))
C.preview(wall=True, floor=False, azim=-30, elev=12)
C.save()
