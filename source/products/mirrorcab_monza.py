import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bc_common as C

KEY = "mirrorcab_monza"
C.reset(KEY)
W, D, H = 0.60, 0.17, 0.70

white = C.mat("carcass", (0.90, 0.90, 0.89), rough=0.3)
doorm = C.mat("door edge", (0.92, 0.92, 0.91), rough=0.25)
mirror = C.mat("mirror", (0.92, 0.93, 0.94), rough=0.03, metal=1.0)
led = C.mat("led", (1.0, 1.0, 1.0), rough=0.4, emission=(1.0, 0.97, 0.92), estr=6.0)
inner = C.mat("led housing", (0.75, 0.75, 0.75), rough=0.4)

CAN_T = 0.018          # top canopy board
CW, CD = 0.586, 0.146  # carcass
CH = H - CAN_T
# carcass (back at y=0)
C.box("carcass", (CW, CD, CH), (0, -CD / 2, CH / 2), white, bev=0.0015, segs=2)
# top canopy: full width and depth, overhangs carcass + doors
C.box("top_canopy", (W, D, CAN_T), (0, -D / 2, H - CAN_T / 2), white, bev=0.002, segs=2)
# doors: big left mirror door (~2/3) and narrow right mirror door, 18 mm PVC + 3 mm mirror
DT = 0.016
gap = 0.003
xl0, xr1 = -CW / 2, CW / 2
split = xl0 + 0.392
for name, a, b in (("door_left", xl0, split - gap / 2), ("door_right", split + gap / 2, xr1)):
    C.box(name, (b - a, DT, CH - 0.004), ((a + b) / 2, -CD - DT / 2, (CH - 0.004) / 2 + 0.001), doorm, bev=0.0015, segs=2)
    C.box(name + "_mirror", (b - a - 0.003, 0.003, CH - 0.008), ((a + b) / 2, -CD - DT - 0.0015, (CH - 0.004) / 2 + 0.001), mirror, bev=0.0008, segs=1)
# LED light under the canopy overhang (above the big door)
C.box("led_housing", (0.30, 0.012, 0.004), (xl0 + 0.196, -D + 0.008, H - CAN_T - 0.002), inner)
C.box("led", (0.28, 0.008, 0.001), (xl0 + 0.196, -D + 0.008, H - CAN_T - 0.0045), led)

C.finish(KEY, "Inter Ceramic Монца (Monza) PVC mirror cabinet with LED, white, 60x17x70", (W, D, H), "wall",
         "Origin = centre of back face, bottom edge. Large left mirror door (hinged left) + narrow right mirror door, overhanging top board with LED strip underneath, per masterhaus.bg drawing (600x700x170).")
