import sys, os, math, bpy, bmesh
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bedhall_common as C
from mathutils import Vector
C.reset("basket_dan")

# ---------------- procedural braided seagrass texture (1024 x 512, packed) ----------------
TU, TV = 0.096, 0.057      # metres covered by one texture tile (6 braid cells x 3 rows)
CELLS, ROWS = 6, 3
W_, H_ = 1024, 512
rng = np.random.default_rng(7)
u = (np.arange(W_) + 0.5) / W_
v = (np.arange(H_) + 0.5) / H_
U, V = np.meshgrid(u, v)
X = U * TU; Y = V * TV
Lc, Lr = TU / CELLS, TV / ROWS
height = np.zeros_like(X); fibre_ph = np.zeros_like(X); tonev = np.zeros_like(X)
ANG = math.radians(38)
La, Lb = Lc * 0.78, Lr * 0.30
for r in range(ROWS):
    ph = rng.uniform(0, 1)
    for hsign, tc, off in ((1, 0.70, 0.0), (-1, 0.30, 0.5)):
        ca, sa = math.cos(hsign * ANG), math.sin(hsign * ANG)
        cy = (r + tc) * Lr
        for j in range(CELLS):
            cx = (j + 0.5 + off + ph) * Lc
            jit = rng.normal(0, 0.06, 2)
            dx = np.mod(X - cx - jit[0] * Lc + TU / 2, TU) - TU / 2
            dy = np.mod(Y - cy - jit[1] * Lr + TV / 2, TV) - TV / 2
            a1 = dx * ca + dy * sa
            a2 = -dx * sa + dy * ca
            sc = rng.uniform(0.9, 1.15)
            d2 = (a1 / (La * sc)) ** 2 + (a2 / Lb) ** 2
            dome = np.sqrt(np.clip(1 - d2, 0, 1))
            m = dome > height
            height = np.where(m, dome, height)
            fibre_ph = np.where(m, a2 / Lb + rng.uniform(0, 3), fibre_ph)
            tonev = np.where(m, rng.uniform(-0.07, 0.07), tonev)
fib = rng.standard_normal((H_, W_))
from numpy.fft import fft2, ifft2
ky = np.fft.fftfreq(H_)[:, None]; kx = np.fft.fftfreq(W_)[None, :]
noise = np.real(ifft2(fft2(fib) * np.exp(-((kx * 30) ** 2 + (ky * 30) ** 2))))
noise /= (np.abs(noise).max() + 1e-6)
fibre = 0.6 * np.sin(fibre_ph * 9.0 + noise * 4) + 0.4 * noise
base = np.array(C.hexcol("A88F6A"))
tr = np.mod(Y / Lr, 1.0)
groove = 1 - 0.35 * np.exp(-(np.minimum(tr, 1 - tr) ** 2) / 0.006)
shade = (0.50 + 0.60 * height ** 0.6) * (1 + 0.12 * fibre) * groove + tonev
lin = np.clip(base[None, None, :] * shade[..., None], 0, 1)
srgb = np.where(lin <= 0.0031308, lin * 12.92, 1.055 * np.power(lin, 1 / 2.4) - 0.055)
img = bpy.data.images.new("basket_dan seagrass", W_, H_, alpha=False)
img.pixels.foreach_set(np.concatenate([srgb, np.ones((H_, W_, 1))], 2)[::-1].astype(np.float32).ravel()[::1] if False else
                       np.concatenate([srgb, np.ones((H_, W_, 1))], 2).astype(np.float32).ravel())
img.pack()
# normal map from height
hh = height ** 0.6 * groove + 0.05 * fibre
gy, gx = np.gradient(hh)
st = 6.0
nx, ny, nz = -gx * st, -gy * st, np.ones_like(hh)
ln = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
nrm = np.stack([nx / ln * 0.5 + 0.5, ny / ln * 0.5 + 0.5, nz / ln * 0.5 + 0.5, np.ones_like(hh)], 2)
nimg = bpy.data.images.new("basket_dan seagrass normal", W_, H_, alpha=False)
nimg.colorspace_settings.name = 'Non-Color'
nimg.pixels.foreach_set(nrm.astype(np.float32).ravel())
nimg.pack()
grass = C.mat_tex("seagrass", img, rough=0.85, normal_image=nimg, nstrength=0.8)

# ---------------- body ----------------
HB = 0.465                   # rim top
AX0, AX1 = 0.163, 0.1836      # half width X bottom/top (wall outer)
AY0, AY1 = 0.165, 0.1845      # half width Y bottom/top
NEXP = 2.8                   # superellipse exponent (rounded square)
WT = 0.010                   # wall thickness
NS = 96


def half(z, a0, a1):
    return a0 + (a1 - a0) * (z / HB)


def ring(z, inset=0.0):
    ax, ay = half(z, AX0, AX1) - inset, half(z, AY0, AY1) - inset
    pts = []
    for i in range(NS):
        th = 2 * math.pi * i / NS
        c, s_ = math.cos(th), math.sin(th)
        pts.append(Vector((ax * math.copysign(abs(c) ** (2 / NEXP), c), ay * math.copysign(abs(s_) ** (2 / NEXP), s_), z)))
    return pts


_mid = ring(HB / 2)
NTILE = max(1, round(sum((b - a).length for a, b in zip(_mid, _mid[1:] + _mid[:1])) / TU))


def wall(name, inset, zs, flip=False):
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap")
    rings = []
    for z in zs:
        pts = ring(z, inset)
        L = [0.0]
        for a, b in zip(pts, pts[1:] + pts[:1]):
            L.append(L[-1] + (b - a).length)
        per = L[-1]; ntile = NTILE
        rings.append(([bm.verts.new(p) for p in pts], [l / per * ntile for l in L], z))
    for (va, ua, za), (vb, ub, zb) in zip(rings[:-1], rings[1:]):
        for i in range(NS):
            j = (i + 1) % NS
            quad = [va[i], va[j], vb[j], vb[i]]
            uvs = [(ua[i], za / TV), (ua[i + 1], za / TV), (ub[i + 1], zb / TV), (ub[i], zb / TV)]
            if flip:
                quad = quad[::-1]; uvs = uvs[::-1]
            f = bm.faces.new(quad)
            for lp, uv in zip(f.loops, uvs):
                lp[uvl].uv = uv
    return C.mesh_from_bm(bm, name, grass, smooth=True)


zs = [HB * i / 24 for i in range(25)]
wall("wall_outer", 0.0, [z for z in zs][:-1] + [HB - 0.004])
wall("wall_inner", WT, [0.012] + [z for z in zs[1:-1]] + [HB - 0.004], flip=True)
# bottom (outer underside + inner floor) with planar UVs
for name, z, inset, up in (("bottom", 0.0, 0.0, False), ("floor", 0.012, WT, True)):
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap")
    vs = [bm.verts.new(p) for p in ring(z, inset)]
    f = bm.faces.new(vs if up else vs[::-1])
    for lp in f.loops:
        lp[uvl].uv = (lp.vert.co.x / TU, lp.vert.co.y / TV)
    C.mesh_from_bm(bm, name, grass)
# rolled braided rim along the top edge
rim_pts = ring(HB - 0.008, WT / 2)
bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap")
RR, NSEG = 0.006, 10
rings = []
L = 0.0
for i, p in enumerate(rim_pts):
    q = rim_pts[(i + 1) % NS]; pr = rim_pts[i - 1]
    tng = (q - pr).normalized(); out = Vector((tng.y, -tng.x, 0)).normalized()
    if i > 0:
        L += (p - rim_pts[i - 1]).length
    rings.append(([bm.verts.new(p + RR * (math.cos(a) * out + math.sin(a) * Vector((0, 0, 1)))) for a in [2 * math.pi * k / NSEG for k in range(NSEG)]], L))
per = L + (rim_pts[0] - rim_pts[-1]).length; nt = round(per / TU)
for i in range(NS):
    (va, la), (vb, lb) = rings[i], rings[(i + 1) % NS]
    if i == NS - 1:
        lb = per
    for k_ in range(NSEG):
        k2 = (k_ + 1) % NSEG
        f = bm.faces.new((va[k_], vb[k_], vb[k2], va[k2]))
        for lp, uv in zip(f.loops, [(la / per * nt, k_ / NSEG * 0.67), (lb / per * nt, k_ / NSEG * 0.67), (lb / per * nt, (k_ + 1) / NSEG * 0.67), (la / per * nt, (k_ + 1) / NSEG * 0.67)]):
            lp[uvl].uv = uv
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
C.mesh_from_bm(bm, "rim", grass, smooth=True)

# ---------------- handles: braided straps down the +-X faces, looping above the rim ----------------
SW, STK = 0.028, 0.011       # strap width (in face plane), thickness
YL = 0.088                   # strap leg centre offset along Y
ZTOP = 0.55 - SW / 2         # loop centreline top


def wall_x(z, y):
    ax, ay = half(z, AX0, AX1), half(z, AY0, AY1)
    return ax * (1 - (abs(y) / ay) ** NEXP) ** (1 / NEXP)


def strap(sx):
    pts = []
    zb = 0.035
    for i in range(14):           # leg 1 going up
        z = zb + (HB - zb) * i / 13
        pts.append(Vector((sx * (wall_x(z, YL) + STK / 2 - 0.001), -YL, z)))
    # loop: half-ellipse from -YL to +YL above rim
    hz = ZTOP - HB
    xt = sx * (wall_x(HB, YL) + STK / 2 - 0.001)
    for i in range(1, 24):
        a = math.pi * i / 24
        pts.append(Vector((xt, -YL * math.cos(a), HB + hz * math.sin(a) ** 0.85)))
    for i in range(14):
        z = HB - (HB - zb) * i / 13
        pts.append(Vector((sx * (wall_x(z, YL) + STK / 2 - 0.001), YL, z)))
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap")
    side = Vector((1, 0, 0))
    rings = []; L = 0.0
    n = len(pts)
    for i, p in enumerate(pts):
        if i:
            L += (p - pts[i - 1]).length
        tg = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        nv = side.cross(tg).normalized()
        corners = [(-STK / 2, -SW / 2), (STK / 2, -SW / 2), (STK / 2, SW / 2), (-STK / 2, SW / 2)]
        rings.append(([bm.verts.new(p + side * a + nv * b) for a, b in corners], L))
    vac = [0.0, 0.25, 0.5, 0.75, 1.0]
    for (va, la), (vb, lb) in zip(rings[:-1], rings[1:]):
        for k_ in range(4):
            k2 = (k_ + 1) % 4
            f = bm.faces.new((va[k_], va[k2], vb[k2], vb[k_]))
            for lp, uv in zip(f.loops, [(la / TU, vac[k_] * 0.75), (la / TU, vac[k_ + 1] * 0.75), (lb / TU, vac[k_ + 1] * 0.75), (lb / TU, vac[k_] * 0.75)]):
                lp[uvl].uv = uv
    bm.faces.new(rings[0][0][::-1]); bm.faces.new(rings[-1][0])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = C.mesh_from_bm(bm, f"handle_{'l' if sx < 0 else 'r'}", grass, smooth=False)
    C.add_bevel(ob, 0.003, 2)


strap(-1); strap(1)
C.apply_all()
C.center_xy()
C.preview(azim=-28, elev=18)
C.save()
