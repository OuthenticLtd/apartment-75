import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kitlib as K
from mathutils import Vector
bpy = K.bpy

# Teka IN 934 N (53934120N) black semi-professional single-lever tap with swivel spring spout.
# Drawing: H 386, reach 192, nozzle height 260, base D50, lever 54. Origin = base centre on the worktop.
# Spout points to -Y (over the sink), lever on the right (+X).
K.reset('tap_teka')
blk = K.mat('matt black', '#151516', rough=0.38, metal=0.2)
chrome = K.mat('chrome', '#dcdee0', rough=0.07, metal=1.0)
hose_m = K.mat('hose', '#0d0d0e', rough=0.5)

# body
K.lathe('body', [(0.0, 0.0), (0.025, 0.0), (0.025, 0.006), (0.0235, 0.009), (0.0205, 0.013), (0.0200, 0.128), (0.0185, 0.131), (0.0, 0.131)], blk, verts=40)
# lever hub on the right with chrome ring + lever blade
K.cyl('lever_hub', 0.0165, 0.016, (0.020, 0, 0.055), rot=(0, math.pi / 2, 0), material=blk, verts=32)
K.cyl('lever_hub_ring', 0.0172, 0.0025, (0.0285, 0, 0.055), rot=(0, math.pi / 2, 0), material=chrome, verts=32)
K.cyl('lever_hub_cap', 0.0150, 0.003, (0.031, 0, 0.055), rot=(0, math.pi / 2, 0), material=blk, verts=32)
blade = [(0.0, 0.042), (0.038, 0.045), (0.049, 0.058), (0.054, 0.140), (0.0465, 0.143), (0.042, 0.072), (0.034, 0.065), (0.0, 0.068)]
# blade lies in the Y-Z plane offset to x = 0.032..0.040, rising forward-up
K.prism('lever', blade, 0.024, 0.034, blk, axis='X', bev=0.002)
# chrome collar + tight coil sleeve above the body
K.lathe('collar', [(0.0, 0.130), (0.0165, 0.130), (0.0165, 0.136), (0.0, 0.136)], chrome, verts=32)
prof = []
z = 0.136
for i in range(22):
    prof += [(0.0118, z), (0.0132, z + 0.0015)]
    z += 0.003
prof = [(0.0, 0.136)] + prof + [(0.0118, z), (0.0, z)]
K.lathe('coil_sleeve', prof, chrome, verts=24)
zc = z

# hose path (Y-Z plane)
def catmull(pts, n=12):
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = map(Vector, (P[i - 1], P[i], P[i + 1], P[i + 2]))
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(Vector(pts[-1]))
    return out

ang = math.radians(32)
tip = Vector((0.0, -0.192, 0.260))
axis = Vector((0.0, -math.sin(ang), -math.cos(ang)))
HL = 0.066
head_top = tip - axis * HL
ctrl = [(0, 0.0, zc - 0.01), (0, 0.0, 0.250), (0, -0.008, 0.326), (0, -0.065, 0.364), (0, -0.128, 0.346),
        tuple(head_top - axis * 0.025), tuple(head_top)]
path = catmull(ctrl, 14)

def poly_tube(name, pts, r, mat, res=8):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for p, v in zip(sp.points, pts):
        p.co = (v.x, v.y, v.z, 1)
    cu.bevel_depth = r
    cu.bevel_resolution = res // 4
    cu.use_fill_caps = True
    ob = bpy.data.objects.new(name, cu)
    K.link(ob)
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.convert(target='MESH')
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.clear()
    ob.data.materials.append(mat)
    K.smooth(ob, 60)
    ob.select_set(False)
    return ob

poly_tube('tap_teka_hose', path, 0.0078, hose_m, res=8)

# chrome spring wound around the hose
# arc-length resample
L = [0.0]
for a, b in zip(path[:-1], path[1:]):
    L.append(L[-1] + (b - a).length)
total = L[-1]
pitch = 0.016
rc = 0.0165
spts = []
steps = int(total / pitch * 14)
j = 0
for k in range(steps + 1):
    s = total * k / steps
    while j < len(L) - 2 and L[j + 1] < s:
        j += 1
    t = (s - L[j]) / max(L[j + 1] - L[j], 1e-9)
    p = path[j].lerp(path[j + 1], t)
    tan = (path[j + 1] - path[j]).normalized()
    n1 = Vector((1, 0, 0))
    n2 = tan.cross(n1).normalized()
    th = 2 * math.pi * s / pitch
    spts.append(p + rc * (math.cos(th) * n1 + math.sin(th) * n2))
# start the spring above the sleeve and stop at the head
spts = [p for p in spts]
poly_tube('tap_teka_spring', spts, 0.0024, chrome, res=4)

# spray head: black barrel + chrome tight coil at the top + chrome nozzle ring
def oriented_lathe(name, prof, mat, base, ax, verts=32):
    ob = K.lathe(name, prof, mat, verts=verts)
    ob.location = base
    ob.rotation_euler = Vector((0, 0, 1)).rotation_difference(ax).to_euler()
    return ob

up = -axis
oriented_lathe('head', [(0.0, 0.0), (0.0128, 0.0), (0.0140, 0.003), (0.0140, 0.044), (0.0128, 0.047), (0.0, 0.047)], blk, tip + up * 0.004, up)
cp = []
z = 0.0
for i in range(5):
    cp += [(0.0118, z), (0.0136, z + 0.0016)]
    z += 0.0032
oriented_lathe('head_coil', [(0.0, 0.0)] + cp + [(0.0118, z), (0.0, z)], chrome, tip + up * 0.051, up, verts=24)
oriented_lathe('nozzle', [(0.0, 0.0), (0.0105, 0.0), (0.0125, 0.0015), (0.0125, 0.0045), (0.0, 0.0045)], chrome, tip, up)
oriented_lathe('nozzle_face', [(0.0, -0.0004), (0.0085, -0.0004), (0.0085, 0.0), (0.0, 0.0)], K.mat('aerator', '#3a3b3d', rough=0.6), tip, up, verts=24)

K.finish('tap_teka', [('', dict(view=(-1.0, -0.45, 0.25))), ('_side', dict(view=(1, 0, 0.05), lens=70))])
