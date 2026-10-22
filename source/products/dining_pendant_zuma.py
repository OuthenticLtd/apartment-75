"""Sollux SL.1326 ZUMA pendant, black steel, E27.  Maker/shop spec: 30/30/76 cm (Ø30, height 76 at the
supplied cord length).  The real shade is a straight CONE (not a dome) with a rolled rim, small top cap,
cord grip, 3 mm black cord and a conical Ø11 ceiling canopy (proportions measured from the product photo,
scaled by the 30 cm shade diameter).
Origin = centre of the ceiling canopy top (ceiling plane z = 0); lamp hangs toward -Z.
CORD_LEN = distance ceiling -> shade bottom (parameter, default 1.10 m)."""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import bpy, bmesh
from mathutils import Vector
import dining_common as C

KEY = "pendant_zuma"
CORD_LEN = 1.10
for a in sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []:
    if a.startswith('cord='):
        CORD_LEN = float(a[5:])

C.reset()
R = C.root(KEY)
R["cord_length_m"] = CORD_LEN
R["cord_length_note"] = "ceiling to shade bottom; origin = canopy centre at ceiling"

m_black = C.mat("pendant_zuma black steel", (28, 28, 28), rough=0.55, metal=0.25)
m_in = C.mat("pendant_zuma inside", (34, 34, 34), rough=0.6, metal=0.2)
m_cord = C.mat("pendant_zuma cord", (20, 20, 20), rough=0.7)
m_sock = C.mat("pendant_zuma socket", (15, 15, 15), rough=0.45)

zb = -CORD_LEN   # shade bottom
# --- canopy Ø11, 7.4 cm high, conical underside ---
C.lathe(f"{KEY}_canopy", R, [(0.0, 0.0), (0.050, 0.0), (0.0545, -0.003), (0.0555, -0.009), (0.052, -0.016),
                              (0.0045, -0.072), (0.0, -0.074)], m_black, segs=40)
# --- shade: cone Ø6 -> Ø30 over 13.5 cm, rolled rim, 0.6 mm sheet shown as 1.5 mm ---
H = 0.135
outer = [(0.031, zb + H), (0.1485, zb + 0.008), (0.1500, zb + 0.004), (0.1495, zb + 0.0005), (0.1475, zb)]
inner = [(0.1455, zb + 0.0015), (0.0300, zb + H - 0.0025)]
shade_outer = C.lathe(f"{KEY}_shade", R, outer + inner, m_black, segs=64, smooth_angle=50)
shade_outer.data.materials.append(m_in)
# assign inner faces (normals pointing down-inward) to inside material
for p in shade_outer.data.polygons:
    if p.normal.z < -0.3:
        p.material_index = 1
# --- top cap (small cone collar) ---
C.lathe(f"{KEY}_cap", R, [(0.0, zb + 0.152), (0.012, zb + 0.152), (0.024, zb + H + 0.006), (0.032, zb + H + 0.002),
                          (0.032, zb + H - 0.004), (0.0, zb + H - 0.004)], m_black, segs=40)
# --- E27 socket inside the shade (visible from below) ---
C.lathe(f"{KEY}_socket", R, [(0.0, zb + H - 0.004), (0.026, zb + H - 0.004), (0.026, zb + H - 0.012), (0.020, zb + H - 0.014),
                             (0.020, zb + H - 0.055), (0.0, zb + H - 0.055)], m_sock, segs=32)
# --- cord grip (tapered tube) ---
C.lathe(f"{KEY}_grip", R, [(0.0, zb + 0.152), (0.0075, zb + 0.152), (0.0062, zb + 0.175), (0.0055, zb + 0.205),
                           (0.0045, zb + 0.208), (0.0, zb + 0.208)], m_black, segs=20)
# --- cord 3 mm ---
C.cyl_between(f"{KEY}_cord", R, (0, 0, zb + 0.208), (0, 0, -0.072), 0.0016, 0.0016, m_cord, verts=8)

C.finish(KEY, R, preview_kwargs=dict(target=(0, 0, -0.55), dist=2.6, elev=8, azim=30, floor=False),
         extra_views=[dict(target=(0, 0, zb + 0.08), dist=0.9, elev=8, azim=30, floor=False),
                      dict(target=(0, 0, zb + 0.08), dist=0.9, elev=-35, azim=30, floor=False)])
