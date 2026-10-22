"""IKEA SKURUP work lamp, black (00516782).  IKEA: height 40, shade Ø16, base Ø17, cord 2.0 m.
Round weighted base, Ø1.5 cm stem with a fixed bend, bell shade (white inside) with a cylindrical
neck the arm enters from behind; shade tilted ~25 deg forward.  Shade faces -Y.
Origin = centre of the round base (footprint) at the bottom; the shade overhangs toward -Y."""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import bpy, bmesh
from mathutils import Vector, Matrix
import dining_common as C

KEY = "desklamp_skurup"
C.reset()
R = C.root(KEY)
m_blk = C.mat("desklamp_skurup black", (38, 38, 38), rough=0.6, metal=0.3)
m_in = C.mat("desklamp_skurup shade inside", (238, 236, 230), rough=0.5)
m_bulb = C.mat("desklamp_skurup bulb", (250, 248, 240), rough=0.3)
m_cord = C.mat("desklamp_skurup cord", (25, 25, 25), rough=0.7)
m_foot = C.mat("desklamp_skurup foot", (20, 20, 20), rough=0.9)

# base Ø17
C.lathe(f"{KEY}_base", R, [(0, 0.0035), (0.083, 0.0035), (0.085, 0.006), (0.085, 0.019), (0.082, 0.0235),
                           (0.070, 0.026), (0.013, 0.0275), (0, 0.0275)], m_blk, segs=48, smooth_angle=35)
C.lathe(f"{KEY}_foot", R, [(0, 0.0), (0.072, 0.0), (0.074, 0.0036), (0, 0.0036)], m_foot, segs=40)

# shade (local: neck top at origin, axis -Z)
TILT = math.radians(25)
prof = [(0, 0), (0.0265, 0), (0.028, -0.002), (0.028, -0.024)]
for k in range(0, 13):
    a = math.radians(90 * k / 12)
    prof.append((0.031 + 0.049 * math.sin(a), -0.025 - 0.074 * (1 - math.cos(a))))
prof += [(0.0805, -0.102), (0.080, -0.1035), (0.0785, -0.1025)]
inner = []
for k in range(12, -1, -1):
    a = math.radians(90 * k / 12)
    inner.append((0.0295 + 0.0475 * math.sin(a), -0.0265 - 0.073 * (1 - math.cos(a))))
prof += inner + [(0.026, -0.028), (0, -0.028)]
shade = C.lathe(f"{KEY}_shade", R, prof, m_blk, segs=48, smooth_angle=40)
shade.data.materials.append(m_in)
for p in shade.data.polygons:
    c = p.center; rr = math.hypot(c.x, c.y)
    if rr > 1e-4 and (p.normal.x * c.x + p.normal.y * c.y) / rr < -0.05 and c.z < -0.03:
        p.material_index = 1
    if p.normal.z < -0.9 and c.z < -0.033 and rr < 0.026:
        p.material_index = 1
# E27-ish LED bulb inside
bulb = C.lathe(f"{KEY}_bulb", R, [(0, -0.034), (0.013, -0.034), (0.013, -0.050)] +
               [(0.013 + 0.010 * math.sin(math.radians(a)), -0.050 - 0.012 * (1 - math.cos(math.radians(a)))) for a in range(15, 91, 15)] +
               [(0.023 * math.cos(math.radians(a)), -0.062 - 0.023 * math.sin(math.radians(a))) for a in range(15, 91, 15)], m_bulb, segs=24, closed=False)
TARGET_BACK = Vector((0, -0.104, 0.366))
PN = TARGET_BACK - Matrix.Rotation(-TILT, 3, 'X') @ Vector((0, 0.028, 0))   # neck centre (world)
M = Matrix.Translation(PN) @ Matrix.Rotation(-TILT, 4, 'X') @ Matrix.Translation((0, 0, 0.015))
for o in (shade, bulb):
    o.data.transform(M)
# hex screw on the neck back (visible in IKEA detail photo)
neck_back = M @ Vector((0, 0.028, -0.015))
# arm Ø1.5: vertical, bend radius 7.5 cm, into the neck from behind
pts = [Vector((0, 0, 0.02))]
ZB = 0.266
for i in range(1, 9):
    pts.append(Vector((0, 0, 0.02 + (ZB - 0.02) * i / 8)))
RB = 0.100
end_y = neck_back.y + 0.002
for k in range(1, 15):
    a = math.radians(90 * k / 14)
    pts.append(Vector((0, -RB + RB * math.cos(a), ZB + RB * math.sin(a))))
pts[-1] = Vector((0, -RB, ZB + RB))
C.sweep_tube(f"{KEY}_arm", R, pts + [Vector((0, end_y + 0.004, neck_back.z))], 0.0075, m_blk, verts=16)
C.cyl_between(f"{KEY}_screw", R, neck_back + Vector((-0.012, 0, 0)), neck_back + Vector((-0.012, 0, 0)) + Vector((0, 0.003, 0.0)), 0.004, 0.004, m_foot, verts=10)
# cord leaving the base at the back (short stub, 2 m cord not modelled)
C.sweep_tube(f"{KEY}_cord", R, [Vector((0.05, 0.05, 0.010)), Vector((0.058, 0.058, 0.004)), Vector((0.060, 0.060, 0.0025))], 0.0025, m_cord, verts=8)

C.finish(KEY, R, preview_kwargs=dict(target=(0, -0.04, 0.2), dist=1.4, elev=18, azim=-55),
         extra_views=[dict(target=(0, -0.04, 0.2), dist=1.4, elev=3, azim=90, lens=60),
                      dict(target=(0, -0.04, 0.2), dist=1.0, elev=-10, azim=10)])
