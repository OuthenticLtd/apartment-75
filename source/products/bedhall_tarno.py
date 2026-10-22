import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bedhall_common as C
from mathutils import Vector
cm = 0.01
ACACIA = C.hexcol("7E6650")
WHICH = os.environ.get("TARNO", "both")


def steel():
    return C.mat("black steel", C.hexcol("161616"), rough=0.4, metal=0.5)


def caps_m():
    return C.mat("foot caps", C.hexcol("111111"), rough=0.8)


def bar(name, pts, m, w=0.7*cm, t=1.7*cm):
    """flat steel bar: thin across X (w), wide in the YZ plane (t)."""
    return C.sweep_rect(name, [Vector(p) for p in pts], Vector((1, 0, 0)), w, t, m)


def rod(name, a, b, r, m):
    return C.tube_path(name, [a, b], r, m, sides=8)


def onseg(a, b, z):
    t = (z - a.z) / (b.z - a.z)
    return a + (b - a) * t


# ---------------- TABLE ----------------
def table():
    C.reset("tarno_table")
    st = steel(); cp = caps_m()
    img = C.wood_image("tarno_table acacia", ACACIA, seed=3, streak=0.22, dark=0.3)
    wood = C.mat_tex("acacia slats", img, rough=0.6)
    TX, TY, H = 0.55, 0.54, 0.70
    ns = 8; sl_t = 1.6*cm; gap = 0.9*cm
    sw = (TY - (ns - 1) * gap) / ns
    for i in range(ns):
        y = -TY/2 + sw/2 + i * (sw + gap)
        s = C.box(f"slat{i+1}", (TX, sw, sl_t), (0, y, H - sl_t/2), wood, bevel=0.002, segs=2)
        C.box_uv(s, 0.6, 0.15, 'X')
    zf = H - sl_t
    parts = []
    FX = 0.215 - 0.35*cm          # leg plane x (feet span 43)
    for sx in (-1, 1):
        parts.append(C.box("rail", (0.5*cm, 0.50, 2.2*cm), (sx*(FX + 0.6*cm), 0, zf - 1.1*cm), st))
    for sy in (-1, 1):
        parts.append(C.box("xrail", (2*FX + 1.2*cm, 0.4*cm, 1.6*cm), (0, sy*0.235, zf - 0.8*cm), st))
    FY = 0.24 - 1.3*cm
    ytop = 0.215
    zp = 0.40
    legs = {}
    for sx in (-1, 1):
        x = sx*FX
        for sy in (-1, 1):
            top = Vector((x, sy*ytop, zf - 1.5*cm))
            foot = Vector((x, -sy*FY, 1.1*cm))
            legs[(sx, sy)] = (top, foot)
            kink = foot + Vector((0, -sy*1.3*cm, -0.25*cm))
            parts.append(bar("leg", [top, foot, kink], st))
        parts.append(C.cyl("bolt", 0.55*cm, 2.0*cm, (x, 0, zp), st, verts=10, rot=(0, math.radians(90), 0)))
    caps = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            caps.append(C.box("cap", (1.2*cm, 2.4*cm, 0.9*cm), (sx*FX, sy*(FY + 1.3*cm), 0.45*cm), cp, bevel=0.002))
    # bottom stretchers along X at 7 cm, one on each leg set
    for sy in (-1, 1):
        top, foot = legs[(1, sy)]
        p = onseg(top, foot, 0.07)
        parts.append(rod("stretcher", Vector((-FX, p.y, 0.07)), Vector((FX, p.y, 0.07)), 0.5*cm, st))
    # locking struts from the top centre down to the pivots
    for sx in (-1, 1):
        parts.append(rod("strut", Vector((sx*0.03, 0.0, zf - 1.6*cm)), Vector((sx*FX, 0.0, zp + 0.6*cm)), 0.3*cm, st))
    C.join(parts, "frame")
    C.join(caps, "feet")
    C.center_xy()
    C.preview(azim=-30, elev=20)
    C.save()


# ---------------- CHAIR ----------------
def chair():
    C.reset("tarno_chair")
    st = steel(); cp = caps_m()
    img = C.wood_image("tarno_chair acacia", ACACIA, seed=5, streak=0.22, dark=0.3)
    wood = C.mat_tex("acacia slats", img, rough=0.6)
    W, H = 0.39, 0.79
    SH = 0.45; sl_t = 1.6*cm
    yF, yR = -0.195, 0.090
    ns = 5; gap = 1.2*cm
    sd = ((yR - yF) - (ns - 1) * gap) / ns
    for i in range(ns):
        y = yF + sd/2 + i * (sd + gap)
        s = C.box(f"seat_slat{i+1}", (W, sd, sl_t), (0, y, SH - sl_t/2), wood, bevel=0.002)
        C.box_uv(s, 0.6, 0.15, 'X')
    parts = []
    UX = 0.165
    zr = SH - sl_t
    for sx in (-1, 1):
        parts.append(C.box("seat_rail", (0.5*cm, yR - yF - 1*cm, 2.0*cm), (sx*UX, (yF + yR)/2, zr - 1.0*cm), st))
    parts.append(C.box("seat_front", (2*UX, 0.4*cm, 1.4*cm), (0, yF + 1.5*cm, zr - 0.7*cm), st))
    yfF, yfR = -0.172, 0.172
    zfoot = 1.0*cm
    yback = 0.185
    kink = None
    for sx in (-1, 1):
        x = sx*(UX + 0.6*cm)
        footA = Vector((x, yfF, zfoot))
        seatR = Vector((x, yR - 0.5*cm, zr - 0.5*cm))
        kink = Vector((x, yR + 1.4*cm, 0.56))
        topA = Vector((x, yback, H - 1.0*cm))
        parts.append(bar("legA", [footA + Vector((0, -1.3*cm, -0.2*cm)), footA, seatR, kink, topA], st, t=1.6*cm))
        xb = sx*(UX - 0.7*cm)
        footB = Vector((xb, yfR, zfoot))
        seatF = Vector((xb, yF + 2.5*cm, zr - 1.0*cm))
        parts.append(bar("legB", [footB + Vector((0, 1.3*cm, -0.2*cm)), footB, seatF], st, t=1.6*cm))
        parts.append(C.cyl("bolt", 0.5*cm, 2.2*cm, (sx*UX, -0.035, 0.24), st, verts=10, rot=(0, math.radians(90), 0)))
    a0, a1 = Vector((0, yfF, zfoot)), Vector((0, yR - 0.5*cm, zr - 0.5*cm))
    b0, b1 = Vector((0, yfR, zfoot)), Vector((0, yF + 2.5*cm, zr - 1.0*cm))
    fA, fB, mB = onseg(a0, a1, 0.045), onseg(b0, b1, 0.045), onseg(b0, b1, 0.33)
    parts.append(rod("str_front", Vector((-(UX + 0.6*cm), fA.y, 0.045)), Vector(((UX + 0.6*cm), fA.y, 0.045)), 0.45*cm, st))
    parts.append(rod("str_rear", Vector((-(UX - 0.7*cm), fB.y, 0.045)), Vector(((UX - 0.7*cm), fB.y, 0.045)), 0.45*cm, st))
    parts.append(rod("str_mid", Vector((-(UX - 0.7*cm), mB.y, 0.33)), Vector(((UX - 0.7*cm), mB.y, 0.33)), 0.4*cm, st))
    C.join(parts, "frame")
    # backrest slats follow the upright slope, in front of the uprights
    k = Vector((0, yR + 1.4*cm, 0.56)); t_ = Vector((0, yback, H - 1.0*cm))
    up = (t_ - k).normalized()
    tilt = -math.atan2(up.y, up.z)
    bh = 5.4*cm
    for i, ztop in enumerate((H - 0.45*cm, H - 0.45*cm - bh - 1.8*cm)):
        zc = ztop - bh/2 * math.cos(tilt)
        p = onseg(k, t_, zc)
        s = C.box(f"back_slat{i+1}", (W, 1.6*cm, bh), (0, p.y - 1.4*cm, zc), wood, bevel=0.002, rot=(tilt, 0, 0))
        C.box_uv(s, 0.6, 0.15, 'X')
    caps = []
    for sx in (-1, 1):
        caps.append(C.box("cap", (1.2*cm, 2.2*cm, 0.9*cm), (sx*(UX + 0.6*cm), yfF - 1.1*cm, 0.45*cm), cp, bevel=0.002))
        caps.append(C.box("cap", (1.2*cm, 2.2*cm, 0.9*cm), (sx*(UX - 0.7*cm), yfR + 1.1*cm, 0.45*cm), cp, bevel=0.002))
    C.join(caps, "feet")
    C.center_xy()
    C.preview(azim=-35, elev=18)
    C.save()


if WHICH in ("both", "table"):
    table()
if WHICH in ("both", "chair"):
    chair()
