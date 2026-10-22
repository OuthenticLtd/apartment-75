import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bedhall_common as C
from mathutils import Vector
C.reset("walllamp_ranarp")
blk = C.mat("shade black", C.hexcol("1f1f1f"), rough=0.55, metal=0.2)
wht = C.mat("shade inside", C.hexcol("EEEDE8"), rough=0.5)
brass = C.mat("brass", C.hexcol("B08A3E"), rough=0.32, metal=1.0)
chrome = C.mat("chrome", (0.85, 0.85, 0.86), rough=0.12, metal=1.0)
rubber = C.mat("clamp rubber", C.hexcol("141414"), rough=0.7)
sock = C.mat("socket", C.hexcol("101010"), rough=0.35)
cord = C.mat("cord", C.hexcol("777777"), rough=0.75)

YC = -0.27          # shade axis (14 cm shade, front at -0.34)
ZC = 0.087          # collar ring level
# ---- shade: bell, mouth at z=0, neck at collar
outer = [(0.0700, 0.0000), (0.0703, 0.0012), (0.0672, 0.0050), (0.0640, 0.0110), (0.0612, 0.0200),
         (0.0596, 0.0320), (0.0588, 0.0440), (0.0578, 0.0530), (0.0548, 0.0620), (0.0480, 0.0705),
         (0.0390, 0.0775), (0.0310, 0.0825), (0.0280, 0.0845)]
inner = [(r - 0.0012, z + 0.0006) for r, z in outer][::-1]
sh = C.lathe("shade", outer, blk, segs=48)
si = C.lathe("shade_inside", inner, wht, segs=48)
for o in (sh, si):
    o.location = (0, YC, 0)
rim = C.tube_path("shade_rim", [Vector((0.0696*math.cos(a), YC + 0.0696*math.sin(a), 0.0012)) for a in [2*math.pi*i/48 for i in range(48)]], 0.0012, blk, closed=True)
# ---- collar ring with two screw lugs
C.tube_path("collar", [Vector((0.031*math.cos(a), YC + 0.031*math.sin(a), ZC)) for a in [2*math.pi*i/40 for i in range(40)]], 0.0028, brass, closed=True)
for sx in (-1, 1):
    C.box(f"lug_{'l' if sx<0 else 'r'}", (0.008, 0.006, 0.004), (sx*0.036, YC, ZC), brass, bevel=0.001)
# ---- socket + brass cage + knurled cap
C.cyl("socket", 0.0125, 0.034, (0, YC, 0.087), sock, verts=20)
for k, ang in enumerate((0, 90)):
    a = math.radians(ang)
    u = Vector((math.cos(a), math.sin(a), 0)); side = Vector((-math.sin(a), math.cos(a), 0))
    c = Vector((0, YC, 0))
    pts = [c + u*-0.031 + Vector((0, 0, ZC)), c + u*-0.024 + Vector((0, 0, 0.106)),
           c + u*-0.012 + Vector((0, 0, 0.107)), c + u*0.012 + Vector((0, 0, 0.107)),
           c + u*0.024 + Vector((0, 0, 0.106)), c + u*0.031 + Vector((0, 0, ZC))]
    C.sweep_rect(f"cage{k+1}", pts, side, 0.009, 0.0016, brass)
C.cyl("cap", 0.0105, 0.012, (0, YC, 0.1135), brass, verts=24)
C.cyl("cap_knurl", 0.0108, 0.006, (0, YC, 0.1125), brass, verts=12)
# ---- clevis bracket from collar (back side) to spring
yb = YC + 0.031
C.box("clevis", (0.016, 0.018, 0.010), (0, yb + 0.010, ZC), brass, bevel=0.0012)
C.cyl("clevis_bolt", 0.0035, 0.022, (0, yb + 0.006, ZC), brass, verts=10, rot=(0, math.radians(90), 0))
# ---- chrome spring (helix, axis along Y)
y0s, y1s = yb + 0.019, yb + 0.050
pts = []
turns = 4.5; n = 90
for i in range(n + 1):
    t = i / n; a = t * turns * 2 * math.pi
    pts.append(Vector((0.009*math.cos(a), y0s + (y1s - y0s)*t, ZC + 0.009*math.sin(a))))
C.tube_path("spring", pts, 0.0018, chrome, sides=6)
# ---- twin chrome arm rods to the wall bracket
yw = -0.045
for dz in (-0.0045, 0.0045):
    C.tube_path(f"rod{'a' if dz<0 else 'b'}", [Vector((0, y1s, ZC + dz*0.4)), Vector((0, yw, ZC + dz))], 0.0017, chrome, sides=8)
C.box("cord_clip", (0.006, 0.006, 0.014), (0, -0.15, ZC + 0.004), rubber, bevel=0.001)
# ---- wall bracket (slide), wall plate, clamp loop
C.box("slide", (0.014, 0.034, 0.013), (0, -0.030, ZC), brass, bevel=0.0012)
C.cyl("slide_screw", 0.0028, 0.018, (0, -0.030, ZC), brass, verts=10, rot=(0, math.radians(90), 0))
C.box("bracket", (0.018, 0.016, 0.040), (0, -0.010, ZC - 0.012), brass, bevel=0.0015)
pl = C.box("wall_plate", (0.034, 0.004, 0.078), (0, -0.002, 0.0625), brass, bevel=0.003, segs=3)
for z in (0.032, 0.093):
    C.cyl(f"plate_screw{1 if z<0.05 else 2}", 0.0032, 0.0012, (0, -0.0045, z), C.mat("screw", (0.55, 0.55, 0.55), 0.3, 1.0), verts=12, rot=(math.radians(90), 0, 0))
loop = [Vector((0.0, -0.022 + 0.017*math.cos(a), 0.058 + 0.026*math.sin(a))) for a in [2*math.pi*i/36 for i in range(36)]]
C.tube_path("clamp_loop", loop, 0.0035, rubber, sides=8, closed=True)
# ---- cord: from cap, back along the arm to the bracket, then down the plate
cpts = [Vector((0, YC, 0.1195)), Vector((0, YC + 0.02, 0.1193)), Vector((0, YC + 0.05, 0.1155)),
        Vector((0, -0.17, 0.106)), Vector((0, -0.15, 0.1)), Vector((0, -0.10, 0.1)),
        Vector((0.0, -0.05, 0.103)), Vector((0.012, -0.02, 0.10)), Vector((0.012, -0.012, 0.07)),
        Vector((0.012, -0.012, 0.004))]
C.tube_path("cord", cpts, 0.0028, cord, sides=8)
C.preview(wall=True, floor=False, azim=-55, elev=8)
C.save()
