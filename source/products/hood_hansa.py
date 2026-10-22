import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kitlib as K

# Visible part of the Hansa OTP 6243 BGH telescopic hood, closed position.
# Origin: x centred, back face on y = 0, z = 0 at the top of the visible unit
# (= underside of the 60 cm wall cabinet). Front (visor) faces -Y.
K.reset('hood_hansa')
W = 0.598
BD = 0.284     # fixed lower frame depth
BH = 0.040     # fixed lower frame height
VT = 0.016     # visor thickness
VH = 0.043     # visor height

blk = K.mat('black steel', '#141415', rough=0.45, metal=0.4)
# fixed lower frame (black painted steel tray)
K.box2('frame', -W / 2, W / 2, -BD, 0.0, -BH, 0.0, blk, bev=0.0015)
# rocker switches on the frame front (hidden behind the visor when closed)
sw = K.mat('switch', '#0a0a0a', rough=0.35)
for nm, x in (('l', -W / 2 + 0.03), ('r', W / 2 - 0.03)):
    K.box2(f'switch_{nm}', x - 0.010, x + 0.010, -BD - 0.003, -BD, -0.030, -0.012, sw, bev=0.001)

# underside: grease filter (expanded aluminium mesh in a light frame) + 2 lights
filt = K.mat('grease filter', '#ffffff', rough=0.45, metal=0.35, img=os.path.join(K.TEX, 'hood_filter.png'), nonrepeat=False)
f = K.box2('filter', -0.262, 0.262, -0.205, -0.020, -BH - 0.0015, -BH + 0.0005, filt)
K.uv_box_project(f, 'Z', ((0, 0.010), (0, 0.010)))
fr = K.mat('filter frame', '#a7a9ac', rough=0.3, metal=1.0)
for nm, (a, b, c, d) in {'f': (-0.268, 0.268, -0.211, -0.205), 'b': (-0.268, 0.268, -0.020, -0.014),
                         'l': (-0.268, -0.262, -0.211, -0.014), 'r': (0.262, 0.268, -0.211, -0.014)}.items():
    K.box2(f'filter_frame_{nm}', a, b, c, d, -BH - 0.002, -BH + 0.0005, fr)
# filter latch tabs
for nm, x in (('l', -0.16), ('r', 0.16)):
    K.box2(f'filter_latch_{nm}', x - 0.018, x + 0.018, -0.215, -0.199, -BH - 0.0028, -BH - 0.0015, K.mat('latch', '#9a9ca0', rough=0.4, metal=0.6), bev=0.001)
# LED spots (front strip)
lens = K.mat('light lens', '#f4f2ea', rough=0.15, emission='#fff6e0', estrength=2.0)
ring = K.mat('light ring', '#b8babd', rough=0.25, metal=1.0)
for nm, x in (('l', -0.15), ('r', 0.15)):
    K.cyl(f'light_ring_{nm}', 0.026, 0.003, (x, -0.245, -BH - 0.0015), material=ring, verts=32)
    K.cyl(f'light_{nm}', 0.020, 0.0012, (x, -0.245, -BH - 0.0031), material=lens, verts=32)

# pull-out visor: black glass strip with Hansa logo
vis = K.mat('visor glass', '#ffffff', rough=0.05, img=os.path.join(K.TEX, 'hood_visor.png'))
v = K.box2('visor', -W / 2, W / 2, -BD - VT, -BD, -VH, 0.0, vis, bev=0.0012)
K.uv_box_project(v, 'Y', ((-W / 2, W / 2), (-VH, 0.0)))

K.finish('hood_hansa', [('', dict(view=(-0.55, -1.0, 0.45))), ('_under', dict(view=(-0.4, -1.0, -0.8), floor=False))])
