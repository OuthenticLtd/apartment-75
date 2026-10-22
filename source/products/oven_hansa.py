import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kitlib as K

K.reset('oven_hansa')
W, H = 0.594, 0.595
FT = 0.024            # front (door / fascia) thickness, back face at y = 0
PZ0 = 0.474           # control panel bottom
DZ1 = 0.471           # door top

glass = K.mat('black glass', '#050505', rough=0.04, coat=0.0)
trim = K.mat('frame', '#151516', rough=0.45, metal=0.2)

# fascia / control panel: frame + glass with printed graphics (display, symbols, logo)
K.box2('panel_frame', -W / 2, W / 2, -FT + 0.004, 0, PZ0, H, trim, bev=0.0015)
pg = K.box2('panel_glass', -W / 2 + 0.0005, W / 2 - 0.0005, -FT, -FT + 0.004, PZ0 + 0.0005, H - 0.0005,
            K.mat('panel glass', '#060606', rough=0.05, img=os.path.join(K.TEX, 'oven_panel.png')))
K.bevel(pg, 0.0012, 2)
K.uv_box_project(pg, 'Y', ((-W / 2, W / 2), (PZ0, H)))

# door: frame + full glass front (dark window shows the cavity)
K.box2('door_frame', -W / 2, W / 2, -FT + 0.004, 0, 0.0, DZ1, trim, bev=0.0015)
dg = K.box2('door_glass', -W / 2 + 0.0005, W / 2 - 0.0005, -FT, -FT + 0.004, 0.0005, DZ1 - 0.0005,
            K.mat('door glass', '#000000', rough=0.04, img=os.path.join(K.TEX, 'oven_door.png')))
K.bevel(dg, 0.0012, 2)
K.uv_box_project(dg, 'Y', ((-W / 2, W / 2), (0.0, DZ1 - 0.0125)))  # top 12 mm of glass = plain black

# vent slot between panel and door
K.box2('vent', -W / 2 + 0.01, W / 2 - 0.01, -FT + 0.006, -0.002, DZ1, PZ0, K.mat('vent', '#000000', rough=0.9))

# stainless bar handle with end brackets
steel = K.mat('handle steel', '#c9cbcd', rough=0.33, metal=1.0)
HZ = 0.428
HL = 0.552
hy = -FT - 0.030
pts = K.rrect_pts(0.020, 0.013, 0.004, 4)            # (y, z) section
K.prism('handle', [(hy + a, HZ + b) for a, b in pts], -HL / 2, HL / 2, steel, axis='X', bev=0.0015)
for sx in (-1, 1):
    x = sx * (HL / 2 - 0.022)
    K.prism(f'handle_post_{"l" if sx < 0 else "r"}', [(a, HZ + b) for a, b in K.rrect_pts(0.034, 0.010, 0.004, 3, cx=-FT - 0.017)],
            x - 0.008, x + 0.008, steel, axis='X')

# push-pop knobs (shown popped out)
knob_m = K.mat('knob', '#c4c6c8', rough=0.35, metal=1.0)
bezel = K.mat('knob ring', '#0c0c0c', rough=0.2, metal=0.3)
for nm, x in (('l', -0.090), ('r', 0.090)):
    z = 0.521
    K.lathe(f'knob_ring_{nm}', [(0.0, 0), (0.0235, 0), (0.0235, 0.002), (0.0215, 0.0035), (0.0195, 0.0035)], bezel,
            loc=(0, 0, 0), verts=48)
    ring = bpy_obj = K.bpy.data.objects[f'oven_hansa_knob_ring_{nm}']
    ring.rotation_euler = (math.radians(90), 0, 0)
    ring.location = (x, -FT, z)
    k = K.lathe(f'knob_{nm}', [(0.0, 0), (0.0185, 0), (0.0188, 0.004), (0.0188, 0.016), (0.0178, 0.0185), (0.012, 0.0195), (0.0, 0.0198)],
                knob_m, verts=48)
    k.rotation_euler = (math.radians(90), 0, 0)
    k.location = (x, -FT - 0.002, z)
    # indicator groove
    K.box(f'knob_mark_{nm}', (0.0018, 0.0012, 0.010), (x, -FT - 0.002 - 0.0196, z + 0.009), K.mat('knob mark', '#2a2a2a', rough=0.6))

# 2 cm of oven body behind the front (cavity housing, slightly narrower than the front)
body = K.mat('body', '#4a4b4d', rough=0.5, metal=0.6)
K.box2('body', -0.278, 0.278, 0.0, 0.020, 0.010, 0.585, body)

K.finish('oven_hansa', [('', dict(view=(-0.5, -1.0, 0.25))), ('_front', dict(view=(0, -1, 0.0), lens=80))])
