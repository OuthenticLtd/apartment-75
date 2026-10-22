import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bc_common as C
import math

KEY = "flush_delta50"
C.reset(KEY)
W, D, H = 0.246, 0.026, 0.164
black = C.mat("plate", (0.018, 0.018, 0.019), rough=0.6)
btn = C.mat("buttons", (0.022, 0.022, 0.023), rough=0.5)
logo = C.mat("logo", (0.06, 0.06, 0.06), rough=0.45)

# thickness profile t(z) of the curved Delta50 front (side drawing): thick upper third, thin bottom
prof = [(0.000, 0.0115), (0.020, 0.0150), (0.050, 0.0195), (0.080, 0.0228), (0.105, 0.0250),
        (0.125, 0.0260), (0.140, 0.0258), (0.152, 0.0245), (0.160, 0.0215), (0.164, 0.0170)]

def t_at(z):
    for (z0, t0), (z1, t1) in zip(prof, prof[1:]):
        if z0 <= z <= z1:
            f = (z - z0) / (z1 - z0)
            return t0 + (t1 - t0) * f
    return prof[-1][1]

# side outline in (u=y, v=z), CCW seen from +X
out = [(0.0, 0.0)]
out += [(0.0, H)]
for z, t in reversed(prof):
    out.append((-t, z))
# (u=y,v=z) -> we built: back bottom, back top, front top ... front bottom
plate = C.prism("plate", out, W, black, plane='YZ', w0=-W / 2, bev=0.0022, segs=3, smooth_angle=30)

# buttons: two rectangles in lower middle (large left, small right), following the curved front
zb0, zb1 = 0.025, 0.079
def button(name, x0, x1):
    pts = []
    n = 6
    zs = [zb0 + (zb1 - zb0) * k / n for k in range(n + 1)]
    for z in zs:
        pts.append((-(t_at(z) - 0.0015), z))
    for z in reversed(zs):
        pts.append((-(t_at(z) + 0.0007), z))
    # ensure CCW orientation in (u,v): recalculated normals anyway
    ob = C.prism(name, pts, x1 - x0, btn, plane='YZ', w0=x0, bev=0.0012, segs=2, smooth_angle=30)
    return ob

button("button_full", -W / 2 + 0.17 * W, -W / 2 + 0.578 * W)
button("button_half", -W / 2 + 0.587 * W, -W / 2 + 0.80 * W)

# small Geberit wordmark plate (top right), very subtle
zl = 0.145
C.box("logo", (0.022, 0.0004, 0.0035), (W / 2 - 0.026, -t_at(zl) - 0.0001, zl), logo)

C.finish(KEY, "Geberit Delta50 dual-flush plate, matt black (115.119.14.1)", (W, D, H), "wall",
         "Origin = centre of back face, bottom edge. Curved front (26 mm max at upper third, ~12 mm at bottom) per Geberit drawing; two flush buttons in lower half (large=full flush left).")
