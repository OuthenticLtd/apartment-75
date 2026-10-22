"""Gree PULAR indoor units (9k and 12k) - same design, scaled to each listed size."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bc_common as C

# base design defined for the 9k unit, scaled per axis for the 12k
BASE = (0.779, 0.185, 0.260)


def build(key, W, D, H, product):
    C.reset(key)
    sx, sy, sz = W / BASE[0], D / BASE[1], H / BASE[2]
    white = C.mat("casing", (0.90, 0.905, 0.91), rough=0.35)
    panel = C.mat("front panel", (0.93, 0.935, 0.94), rough=0.22, coat=0.2)
    flapm = C.mat("flap", (0.88, 0.885, 0.89), rough=0.3)
    dark = C.mat("air outlet", (0.10, 0.10, 0.11), rough=0.6)
    logo = C.mat("logo", (0.55, 0.56, 0.58), rough=0.4, metal=0.5)
    disp = C.mat("display", (0.75, 0.76, 0.78), rough=0.3, emission=(0.9, 0.95, 1.0), estr=0.6)

    # side profile of the casing (y forward negative, z up), 9k reference values
    prof = [(0.0, 0.004), (-0.090, 0.0), (-0.150, 0.030), (-0.172, 0.060), (-0.172, 0.250),
            (-0.160, 0.260), (0.0, 0.260)]
    prof = [(y * sy, z * sz) for (y, z) in prof]
    body = C.prism("casing", prof, W - 0.002 * sx, white, plane='YZ', w0=-(W - 0.002 * sx) / 2,
                   bev=0.006, segs=3, smooth_angle=35)

    # front panel (separate moulding, sits proud of casing; flat with slightly rounded edges)
    pz0, pz1 = 0.074 * sz, 0.257 * sz
    pw = W
    C.box("front_panel", (pw, 0.013 * sy, pz1 - pz0), (0, -0.1725 * sy - 0.0065 * sy + 0.0012, (pz0 + pz1) / 2),
          panel, bev=0.006, segs=3)

    # closed horizontal flap below the panel, angled down/back, nearly full width
    fw = W - 0.075 * sx
    # flap plate following the slanted bottom: from (y=-0.183,z=0.068) to (y=-0.150,z=0.022)
    fl = [(-0.1855 * sy, 0.071 * sz), (-0.1755 * sy, 0.071 * sz), (-0.1445 * sy, 0.024 * sz), (-0.1535 * sy, 0.020 * sz)]
    C.prism("flap", fl, fw, flapm, plane='YZ', w0=-fw / 2, bev=0.002, segs=2, smooth_angle=30)
    # dark outlet shadow seen at the flap ends / behind it
    ol = [(-0.170 * sy, 0.066 * sz), (-0.165 * sy, 0.066 * sz), (-0.140 * sy, 0.028 * sz), (-0.146 * sy, 0.026 * sz)]
    C.prism("air_outlet", ol, fw + 0.02 * sx, dark, plane='YZ', w0=-(fw + 0.02 * sx) / 2)

    # logo (centre, lower third of the panel) and hidden display (right)
    yfront = -0.1725 * sy - 0.013 * sy + 0.0012
    C.box("logo", (0.055 * sx, 0.0006, 0.007 * sz), (0, yfront - 0.0003, 0.118 * sz), logo)
    C.box("display", (0.030 * sx, 0.0006, 0.020 * sz), (0.255 * sx, yfront - 0.0003, 0.205 * sz), disp)

    C.finish(key, product, (W, D, H), "wall",
             "Origin = centre of back face, bottom edge (wall plate side). Flap shown closed. Front panel, angled louver flap, centre logo and hidden display on the right as on the Gree PULAR (GWH..AGA/AGB).")


build("ac_pular_in", 0.779, 0.185, 0.260, "Gree PULAR inverter indoor wall unit 9000 BTU (GWH09AGA-K6DNA1C/I)")
build("ac_pular_in12", 0.825, 0.196, 0.293, "Gree PULAR inverter indoor wall unit 12000 BTU (GWH12AGB)")
