import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bc_common as C
from mathutils import Vector

KEY = "boiler_galant"
C.reset(KEY)
W, D, H = 0.511, 0.300, 0.838

white = C.mat("body", (0.92, 0.92, 0.91), rough=0.25, coat=0.3)
grey = C.mat("top cap", (0.045, 0.045, 0.05), rough=0.18)
black = C.mat("bottom cap", (0.012, 0.012, 0.013), rough=0.12)
frame = C.mat("display frame", (0.03, 0.03, 0.035), rough=0.3)
screen = C.mat("display", (0.01, 0.012, 0.015), rough=0.1, emission=(0.9, 0.35, 0.25), estr=0.0)
lcd = C.mat("display digits", (0.9, 0.3, 0.2), rough=0.4, emission=(1.0, 0.35, 0.2), estr=1.5)
btnm = C.mat("buttons", (0.55, 0.56, 0.58), rough=0.3, metal=0.6)
logom = C.mat("logo", (0.55, 0.42, 0.30), rough=0.5)

BODY_D = 0.288      # body depth incl. front bulge
BULGE = 0.012       # front convexity (plan)
RF, RB = 0.085, 0.02  # plan corner radii front/back
N = 72

def plan(inset):
    """Closed plan outline (x,y) of the flat body, inset by `inset` (for rounded top/bottom edges)."""
    w = W / 2 - inset
    d0 = -inset          # back plane (slightly inset too)
    d1 = -(BODY_D - BULGE) + inset  # front plane at sides
    rf = max(0.005, RF - inset * 0.5); rb = max(0.003, RB - inset * 0.3)
    pts = []
    # back edge from right to left (y = d0)
    pts += [(w - rb, d0), (-w + rb, d0)]
    for k in range(1, 6):
        a = math.pi / 2 + k * (math.pi / 2) / 6
        pts.append((-w + rb + rb * math.cos(a), d0 - rb + rb * math.sin(a)))
    pts += [(-w, d1 + rf)]
    for k in range(1, 8):
        a = math.pi + k * (math.pi / 2) / 8
        pts.append((-w + rf + rf * math.cos(a), d1 + rf + rf * math.sin(a)))
    # bulged front from left to right
    xs = [-w + rf + (2 * (w - rf)) * k / 16 for k in range(17)]
    for x in xs:
        f = x / (w - rf) if w - rf > 0 else 0
        pts.append((x, d1 - (BULGE - inset * 0.1) * (1 - f * f)))
    for k in range(1, 8):
        a = 1.5 * math.pi + k * (math.pi / 2) / 8
        pts.append((w - rf + rf * math.cos(a), d1 + rf + rf * math.sin(a)))
    pts += [(w, d0 - rb)]
    for k in range(1, 6):
        a = 0 + k * (math.pi / 2) / 6
        pts.append((w - rb + rb * math.cos(a), d0 - rb + rb * math.sin(a)))
    # make CCW and start at back centre
    pts = C.resample(pts, N)
    return pts

def ring(z, inset):
    return [Vector((x, y, z)) for (x, y) in plan(inset)]

# vertical profile: rounded top (radius 0.05) and bottom (0.03)
RT, RBt = 0.05, 0.03
z0, z1 = 0.035, H
def profile(za, zb, n):
    out = []
    for k in range(n + 1):
        z = za + (zb - za) * k / n
        ins = 0.0
        if z > z1 - RT:
            u = (z - (z1 - RT)) / RT
            ins = RT * (1 - math.sqrt(max(0, 1 - u * u)))
        if z < z0 + RBt:
            u = ((z0 + RBt) - z) / RBt
            ins = RBt * (1 - math.sqrt(max(0, 1 - u * u)))
        out.append((z, ins))
    return out

def zs_round_top(za):
    out = [za]
    for k in range(1, 9):
        a = (math.pi / 2) * k / 8
        z = (z1 - RT) + RT * math.sin(a)
        if z > za:
            out.append(z)
    return out

# --- black bottom band (z0 .. 0.118), rounded bottom edge
zb = [z0 + RBt * (1 - math.cos((math.pi / 2) * k / 6)) for k in range(7)] + [0.118]
rings_b = []
for z in zb:
    u = ((z0 + RBt) - z) / RBt if z < z0 + RBt else 0
    ins = RBt * (1 - math.sqrt(max(0, 1 - u * u))) if u > 0 else 0
    rings_b.append(ring(z, ins))
C.loft("bottom_cap", rings_b, black)

# --- white body 0.118 .. 0.800
zw = [0.118, 0.30, 0.55, 0.79, 0.800]
rings_w = []
for z in zw:
    u = (z - (z1 - RT)) / RT if z > z1 - RT else 0
    ins = RT * (1 - math.sqrt(max(0, 1 - u * u))) if u > 0 else 0
    rings_w.append(ring(z, ins))
C.loft("body", rings_w, white)

# --- dark top cap 0.800 .. H (rounded)
zt = [0.800] + [z for z in zs_round_top(0.8005)]
rings_t = []
for z in zt:
    u = (z - (z1 - RT)) / RT if z > z1 - RT else 0
    ins = RT * (1 - math.sqrt(max(0, 1 - min(1, u) ** 2))) if u > 0 else 0
    ins = min(ins, RT * 0.92)
    rings_t.append(ring(z, ins))
C.loft("top_cap", rings_t, grey)

# --- central pod under the bottom band (houses display), protrudes below and in front
pod = C.box("control_pod", (0.25, 0.272, 0.125), (0, -0.155, 0.0625), black, bev=0.035, segs=5)

# display bezel + screen + buttons on pod front
yf = -0.291
C.box("display_bezel", (0.066, 0.009, 0.098), (0, yf - 0.0045 + 0.004, 0.066), frame, bev=0.004, segs=2)
C.box("display_screen", (0.046, 0.002, 0.034), (0, yf - 0.006, 0.088), screen)
C.box("display_digits", (0.026, 0.0015, 0.009), (0, yf - 0.0068, 0.090), lcd)
for i in range(4):
    C.cyl(f"button_{i}", 0.0042, 0.003, (-0.0165 + i * 0.011, yf - 0.0063, 0.050), btnm, axis='Y', verts=16)

# ELDOM logo (left lower front of white body)
C.box("logo", (0.07, 0.0008, 0.012), (-0.135, -(BODY_D - BULGE) - 0.0068, 0.205), logom)

C.finish(KEY, "Eldom Galant DU060W flat electric water heater 60 L, white (universal mount)", (W, D, H), "wall",
         "Modelled upright as sold (control pod at the bottom). Will be installed horizontally: rotate 90 deg about Y after placing. Origin = centre of back face, bottom edge. Pipe stubs omitted (they hang below the pod).")
