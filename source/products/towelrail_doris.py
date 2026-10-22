import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bc_common as C

KEY = "towelrail_doris"
C.reset(KEY)
W, D, H = 0.50, 0.10, 1.05

blk = C.mat("frame", (0.028, 0.028, 0.03), rough=0.55)
ctrl = C.mat("control box", (0.035, 0.035, 0.038), rough=0.4)
knob = C.mat("knob", (0.06, 0.06, 0.065), rough=0.35)
mark = C.mat("markings", (0.6, 0.6, 0.6), rough=0.5)

CX = 0.034          # collector width (x)
CY = 0.030          # collector depth (y)
YC = -0.080         # collector / bar axis
Z0 = 0.075          # collector bottom
# vertical collectors (flat-oval / rounded rectangular tubes)
for side in (-1, 1):
    x = side * (W / 2 - CX / 2)
    z0 = Z0 if side < 0 else 0.040   # right collector is longer (heating element inside)
    C.box(f"collector_{'l' if side < 0 else 'r'}", (CX, CY, H - z0), (x, YC, z0 + (H - z0) / 2), blk, bev=0.010, segs=4)

# horizontal round bars, real Atlantic grouping (3 / 4 / 5 / 6 from the top)
pitch = 0.042
groups = [(1.020, 3), (0.835, 4), (0.610, 5), (0.330, 6)]
bars = []
for ztop, n in groups:
    for i in range(n):
        bars.append(ztop - i * pitch)
L = W - 2 * CX + 0.006
for i, z in enumerate(bars):
    C.cyl(f"bar_{i:02d}", 0.011, L, (0, YC, z), blk, axis='X', verts=20)

# wall brackets: 4 stand-offs with rosettes (behind collectors, at inner edge)
for sx in (-1, 1):
    for zb in (1.020 - 2 * 0.042, 0.330 - 3 * 0.042):
        x = sx * (W / 2 - CX - 0.012)
        C.cyl(f"bracket_{'l' if sx < 0 else 'r'}_{int(zb*100)}", 0.008, -YC - 0.011, (x, (YC + 0.011) / 2, zb), blk, axis='Y', verts=16)
        C.cyl(f"rosette_{'l' if sx < 0 else 'r'}_{int(zb*100)}", 0.017, 0.006, (x, -0.003, zb), blk, axis='Y', verts=24, bev=0.002)
        C.sphere(f"clamp_{'l' if sx < 0 else 'r'}_{int(zb*100)}", 0.014, (x, YC, zb), blk, segs=16, rings=8, scale=(1, 1, 0.9))

# thermostat control box at bottom right (hangs under the right collector, extends left)
cbw, cbd, cbh = 0.135, 0.050, 0.052
cbx = W / 2 - CX - cbw / 2 + 0.010
C.box("control_box", (cbw, cbd, cbh), (cbx, -D + 0.004 + cbd / 2, cbh / 2 + 0.0), ctrl, bev=0.012, segs=4)
C.cyl("knob", 0.017, 0.010, (cbx + 0.022, -D + 0.0055, 0.026), knob, axis='Y', verts=32, bev=0.002)
C.cyl("button", 0.006, 0.006, (cbx - 0.035, -D + 0.005, 0.024), knob, axis='Y', verts=16)
C.box("label", (0.020, 0.0008, 0.004), (cbx - 0.005, -D + 0.0037, 0.040), mark)
# neck joining box to collector
C.box("element_neck", (CX * 0.8, 0.026, 0.03), (W / 2 - CX / 2, YC + 0.004, 0.045), ctrl, bev=0.008, segs=3)

C.recenter("wall")
C.finish(KEY, "Atlantic Doris thermo-fluid electric towel rail 500 W, black, 50 x 105", (W, D, H), "wall",
         "Origin = centre of back face (wall rosettes), bottom edge (bottom of control box). Straight round bars grouped 3/4/5/6 from top, flat collectors, thermostat box bottom right (Atlantic layout).")
