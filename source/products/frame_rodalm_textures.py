"""Generate the procedural print (terracotta/oat abstract) and an oak-effect grain texture."""
import os, math, random
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tex")
os.makedirs(OUT, exist_ok=True)
random.seed(7)

# ---------- print: 49x69 visible opening; print a bit larger (52x72) ----------
W, H = 724, 1002   # aspect 52:72
S = 2  # supersample
im = Image.new("RGB", (W * S, H * S), (236, 226, 208))  # oat paper
d = ImageDraw.Draw(im)
def P(x, y):
    return (x * W * S, y * H * S)
terracotta = (190, 98, 66)
rust = (160, 72, 46)
sand = (214, 182, 140)
blush = (226, 170, 140)
umber = (110, 70, 52)
oat_dark = (205, 186, 158)
# large sand rectangle block (lower)
d.rectangle([P(0.14, 0.56), P(0.86, 0.86)], fill=oat_dark)
# terracotta arch
cx, cy, r = 0.40, 0.56, 0.24
d.rectangle([P(cx - r, cy - 0.0), P(cx + r, 0.86)], fill=terracotta)
d.pieslice([(P(cx - r, 0)[0], (cy * H - r * W) * S), (P(cx + r, 0)[0], (cy * H + r * W) * S)], 180, 360, fill=terracotta)
# sun circle (rust)
cx2, cy2, r2 = 0.66, 0.30, 0.13
d.ellipse([((cx2 - r2) * W * S, (cy2 * H - r2 * W) * S), ((cx2 + r2) * W * S, (cy2 * H + r2 * W) * S)], fill=rust)
# blush half circle overlapping arch
cx3, cy3, r3 = 0.66, 0.70, 0.16
d.pieslice([((cx3 - r3) * W * S, (cy3 * H - r3 * W) * S), ((cx3 + r3) * W * S, (cy3 * H + r3 * W) * S)], 0, 180, fill=blush)
# sand semicircle top-left
cx4, cy4, r4 = 0.28, 0.24, 0.12
d.pieslice([((cx4 - r4) * W * S, (cy4 * H - r4 * W) * S), ((cx4 + r4) * W * S, (cy4 * H + r4 * W) * S)], 180, 360, fill=sand)
# thin umber line and small dot
d.line([P(0.14, 0.50), P(0.86, 0.50)], fill=umber, width=3 * S)
d.ellipse([((0.80 - 0.025) * W * S, (0.62 * H - 0.025 * W) * S), ((0.80 + 0.025) * W * S, (0.62 * H + 0.025 * W) * S)], fill=umber)
im = im.resize((W, H), Image.LANCZOS)
# subtle paper grain
px = im.load()
for y in range(H):
    for x in range(W):
        n = random.randint(-5, 5)
        r_, g_, b_ = px[x, y]
        px[x, y] = (max(0, min(255, r_ + n)), max(0, min(255, g_ + n)), max(0, min(255, b_ + n)))
im.save(os.path.join(OUT, "frame_rodalm_print.png"))

# ---------- oak grain: 1024 x 256, grain along U ----------
GW, GH = 1024, 256
g = Image.new("RGB", (GW, GH))
gp = g.load()
base = (210, 178, 138)
phases = [random.uniform(0, 6.28) for _ in range(6)]
for y in range(GH):
    for x in range(GW):
        u = x / GW * 2 * math.pi
        # wavy longitudinal grain lines
        yy = y + 2.5 * math.sin(u * 2 + phases[0]) + 1.2 * math.sin(u * 5 + phases[1])
        line = math.sin(yy * 0.35 + 4.0 * math.sin(yy * 0.045 + phases[2]) + 1.5 * math.sin(yy * 0.13 + phases[4]))
        fine = math.sin(yy * 2.3 + phases[3])
        t = 0.5 + 0.5 * line
        k = 1.0 - 0.10 * (t ** 6) - 0.035 * fine + random.uniform(-0.03, 0.03)
        gp[x, y] = tuple(max(0, min(255, int(c * k))) for c in base)
g = g.filter(ImageFilter.GaussianBlur(0.6))
g.save(os.path.join(OUT, "frame_rodalm_oak.png"))
print("textures written", OUT)
