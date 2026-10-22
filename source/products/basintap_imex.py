import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bc_common as C

KEY = "basintap_imex"
C.reset(KEY)

blk = C.mat("body", (0.035, 0.035, 0.037), rough=0.42, metal=0.6)
knurl = C.mat("knurled grip", (0.03, 0.03, 0.032), rough=0.7, metal=0.4)
logo = C.mat("logo", (0.55, 0.42, 0.22), rough=0.4, metal=0.8)
aer = C.mat("aerator", (0.02, 0.02, 0.02), rough=0.8)

ZA = 0.092          # axis height of spout + mixer above the lever tip (origin)
SP = 0.120          # spout <-> mixer centre distance (Imex drawing)
xs, xm = -SP / 2, SP / 2
RR = 0.030          # rosette radius (d60)

for nm, x in (("spout", xs), ("mixer", xm)):
    C.cyl(f"rosette_{nm}", RR, 0.008, (x, -0.004, ZA), blk, axis='Y', verts=48, bev=0.0015)

# spout: d23 tube, 194 mm from the wall, down-turned outlet with slanted end
r = 0.0115
pts = [(xs, -0.006, ZA), (xs, -0.170, ZA), (xs, -0.1825, ZA - 0.010), (xs, -0.1825, ZA - 0.026)]
C.tube("spout", C.fillet(pts, 0.012, 8), r, blk, res=24)
C.cyl("spout_collar", 0.0135, 0.016, (xs, -0.014, ZA), blk, axis='Y', verts=32, bev=0.001)
C.cyl("aerator", 0.0085, 0.002, (xs, -0.1825, ZA - 0.0265), aer, axis='Z', verts=24)

# mixer: plain sleeve + knurled cylindrical handle (d35), front cap with IMEX logo
C.cyl("mixer_sleeve", 0.0185, 0.034, (xm, -0.008 - 0.017, ZA), blk, axis='Y', verts=40, bev=0.001)
C.cyl("mixer_handle", 0.0178, 0.038, (xm, -0.042 - 0.019, ZA), knurl, axis='Y', verts=40, bev=0.0012)
C.cyl("mixer_cap", 0.0172, 0.003, (xm, -0.080 - 0.0015, ZA), blk, axis='Y', verts=40, bev=0.0008)
C.box("logo", (0.014, 0.0005, 0.004), (xm, -0.0833, ZA), logo)
# slim lever pin hanging down from the handle, knurled tip
lx, ly = xm, -0.060
C.cyl("lever", 0.0025, ZA - 0.016 - 0.024, (lx, ly, 0.024 + (ZA - 0.016 - 0.024) / 2), blk, axis='Z', verts=16)
C.cyl("lever_tip", 0.0032, 0.026, (lx, ly, 0.013), knurl, axis='Z', verts=16, bev=0.0008)

C.recenter("wall")
C.finish(KEY, "Imex Line built-in (2-hole) basin mixer GLD038, matt black", (0.180, 0.194, 0.122), "wall",
         "Origin = centre of back face, bottom edge = tip of the lever. Spout (left) and mixer (right) on separate d60 rosettes, 120 mm apart; spout/mixer axis at z=0.092 above origin, spout reach 194 mm, d23. Concealed body not modelled.")
