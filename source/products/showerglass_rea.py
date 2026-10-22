"""Rea Rapid Fold 90 bi-fold door (black) and Rea Bler fixed panel 90 (black), flat in the XZ plane."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bc_common as C


def glass_mat():
    return C.mat("glass", (0.80, 0.88, 0.88), rough=0.04, alpha=0.25, ior=1.5)


# ---------------------------------------------------------------- Rapid Fold 90
def rapid_fold():
    KEY = "showerdoor_rea"
    C.reset(KEY)
    W, H, G = 0.90, 1.90, 0.006
    blk = C.mat("profiles", (0.025, 0.025, 0.027), rough=0.45, metal=0.3)
    gl = glass_mat()
    WP_W, WP_D = 0.022, 0.034    # wall profiles (adjustable U channels) both sides
    FR = 0.016                   # leaf frame profile width
    FD = 0.020                   # leaf frame depth
    # wall profiles
    for s, nm in ((-1, "wall_profile_l"), (1, "wall_profile_r")):
        C.box(nm, (WP_W, WP_D, H), (s * (W / 2 - WP_W / 2), 0, H / 2), blk, bev=0.002, segs=1)
    inner0, inner1 = -W / 2 + WP_W + 0.002, W / 2 - WP_W - 0.002
    gap = 0.004
    mid = (inner0 + inner1) / 2
    leaves = [(inner0, mid - gap / 2), (mid + gap / 2, inner1)]
    zb, zt = 0.004, H - 0.004
    for i, (a, b) in enumerate(leaves):
        lw = b - a
        cx = (a + b) / 2
        # frame: top, bottom, left, right profiles around the glass
        C.box(f"leaf{i}_top", (lw, FD, FR), (cx, 0, zt - FR / 2), blk, bev=0.0015, segs=1)
        C.box(f"leaf{i}_bottom", (lw, FD, FR), (cx, 0, zb + FR / 2), blk, bev=0.0015, segs=1)
        C.box(f"leaf{i}_side_a", (FR, FD, zt - zb - 2 * FR), (a + FR / 2, 0, (zb + zt) / 2), blk, bev=0.0015, segs=1)
        C.box(f"leaf{i}_side_b", (FR, FD, zt - zb - 2 * FR), (b - FR / 2, 0, (zb + zt) / 2), blk, bev=0.0015, segs=1)
        C.box(f"leaf{i}_glass", (lw - 2 * FR + 0.006, G, zt - zb - 2 * FR + 0.006), (cx, 0, (zb + zt) / 2), gl)
    # central folding hinge profile (slightly wider)
    C.box("hinge_profile", (0.010, FD + 0.006, zt - zb - 0.02), (mid, 0, (zb + zt) / 2), blk, bev=0.002, segs=1)
    # rectangular through-glass handle on the second leaf, near the fold
    hx = mid + 0.075
    hz0, hz1 = 0.93, 1.21
    hw, ht, hd = 0.040, 0.012, 0.024
    for s in (-1, 1):
        y = s * (G / 2 + hd / 2)
        C.box(f"handle_{'out' if s < 0 else 'in'}_l", (0.008, hd, hz1 - hz0), (hx - hw / 2 + 0.004, y, (hz0 + hz1) / 2), blk, bev=0.0015, segs=1)
        C.box(f"handle_{'out' if s < 0 else 'in'}_r", (0.008, hd, hz1 - hz0), (hx + hw / 2 - 0.004, y, (hz0 + hz1) / 2), blk, bev=0.0015, segs=1)
        C.box(f"handle_{'out' if s < 0 else 'in'}_t", (hw, hd, 0.008), (hx, y, hz1 - 0.004), blk, bev=0.0015, segs=1)
        C.box(f"handle_{'out' if s < 0 else 'in'}_b", (hw, hd, 0.008), (hx, y, hz0 + 0.004), blk, bev=0.0015, segs=1)
    C.recenter("floor")
    C.finish(KEY, "Rea Rapid Fold 90 bi-fold shower door, black frame, 6 mm clear glass (REA-K6419 black)", (W, 2 * (G / 2 + hd), H), "floor",
             "Flat assembly in the XZ plane (glass plane y=0), shown closed; origin = centre of footprint at floor. Two equal leaves with full black frames, central fold profile, wall profiles both sides, rectangular through-glass handle near the fold. Glass alpha 0.25.",
             views=[((0.75, -1.0, 0.35), "")])


# ---------------------------------------------------------------- Bler 90 fixed panel
def bler():
    KEY = "showerpanel_rea"
    C.reset(KEY)
    W, H, G = 0.90, 1.95, 0.008
    blk = C.mat("profiles", (0.025, 0.025, 0.027), rough=0.45, metal=0.3)
    paint = C.mat("black frame print", (0.02, 0.02, 0.022), rough=0.5)
    gl = glass_mat()
    WP_W, WP_D = 0.022, 0.030
    # wall profile (left end)
    C.box("wall_profile", (WP_W, WP_D, H), (-W / 2 + WP_W / 2, 0, H / 2), blk, bev=0.002, segs=1)
    gx0, gx1 = -W / 2 + WP_W - 0.008, W / 2
    gw = gx1 - gx0
    C.box("glass", (gw, G, H - 0.004), ((gx0 + gx1) / 2, 0, H / 2), gl)
    # black screen-printed frame band around the glass edge (both faces)
    B = 0.020
    for s in (-1, 1):
        y = s * (G / 2 + 0.0002)
        C.box(f"frame_{'f' if s < 0 else 'b'}_top", (gw - 0.006, 0.0004, B), ((gx0 + gx1) / 2 - 0.003, y, H - 0.002 - B / 2), paint)
        C.box(f"frame_{'f' if s < 0 else 'b'}_bottom", (gw - 0.006, 0.0004, B), ((gx0 + gx1) / 2 - 0.003, y, 0.002 + B / 2), paint)
        C.box(f"frame_{'f' if s < 0 else 'b'}_free", (B, 0.0004, H - 0.004), (gx1 - B / 2, y, H / 2), paint)
    # stabiliser bar: round 16 mm black bar from the top of the free end, at 90 deg to the glass
    # toward the back wall (+Y); default 500 mm, cut to length on site
    SL = 0.50
    sx = gx1 - 0.10
    sz = H - 0.035
    C.cyl("stabiliser_clamp", 0.014, 0.034, (sx, 0, sz), blk, axis='Y', verts=24, bev=0.003)
    C.cyl("stabiliser", 0.008, SL, (sx, SL / 2 + 0.01, sz), blk, axis='Y', verts=20)
    C.cyl("stabiliser_wall_mount", 0.016, 0.012, (sx, SL + 0.01 + 0.006, sz), blk, axis='Y', verts=24, bev=0.002)
    # origin: centre of the glass panel footprint (glass plane y = 0), stabiliser sticks out to +Y
    C.finish(KEY, "Rea Bler 90 walk-in fixed panel, black, 8 mm clear glass, with wall profile and stabiliser bar", (W, 0.034 / 2 + SL + 0.022, H), "floor",
             "Flat assembly in the XZ plane, glass plane at y=0; origin = centre of the PANEL footprint (x centre, y on glass) at floor. Wall profile on the -X end; black screen-printed frame band on the other three edges; black stabiliser bar (500 mm, cut-to-length, separate object 'showerpanel_rea_stabiliser') runs from the top of the free end toward +Y to the back wall - scale/shorten it in Y on placement. Glass alpha 0.25.",
             views=[((0.75, -1.0, 0.35), "")])


rapid_fold()
bler()
