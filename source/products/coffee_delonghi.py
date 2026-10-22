import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kitlib as K

# De'Longhi Magnifica S ECAM22.110.SB  238 W x 430 D x 351 H mm
K.reset('coffee_delonghi')
W, D, H = 0.238, 0.430, 0.351
yf = -D / 2           # front of drip tray
hw = W / 2
mm = 0.001

silver = K.mat('silver front', '#c3c5c8', rough=0.3, metal=0.75)
silver_d = K.mat('silver recess', '#a9abaf', rough=0.35, metal=0.7)
black = K.mat('black body', '#1b1b1d', rough=0.4)
chrome = K.mat('chrome', '#e2e3e5', rough=0.08, metal=1.0)
blk_gl = K.mat('black gloss', '#0b0b0c', rough=0.12)

# main black body (sides, back)
K.box2('body', -hw, hw, yf + 0.085, D / 2, 0.020, 0.318, black, bev=0.012, seg=4)
# silver side pillars at the front corners
for nm, sx in (('l', -1), ('r', 1)):
    x0, x1 = sorted((sx * hw, sx * (hw - 0.056)))
    K.box2(f'pillar_{nm}', x0, x1, yf + 0.022, yf + 0.090, 0.030, 0.215, silver, bev=0.006)
# centre recess column
K.box2('centre_column', -0.062, 0.062, yf + 0.050, yf + 0.090, 0.030, 0.215, silver_d)
# coffee grounds drawer front
K.box2('grounds_door', -0.0605, 0.0605, yf + 0.040, yf + 0.052, 0.034, 0.113, silver, bev=0.003)
K.box2('grounds_door_slot', -0.0605, 0.0605, yf + 0.045, yf + 0.052, 0.113, 0.116, black)

# upper head (control unit) with photo-matched fascia
head_z0, head_z1 = 0.209, 0.316
K.box2('head', -hw, hw, yf + 0.0105, yf + 0.110, head_z0, head_z1, silver, bev=0.004)
K.decal('head_fascia', os.path.join(K.TEX, 'coffee_head.png'), W - 0.006, head_z1 - head_z0 - 0.004, (0, yf + 0.0102, (head_z0 + head_z1) / 2 + 0.001), rough=0.3, metal=0.4)
# buttons (6) and dial
for nm, x in (('l', -0.044), ('r', 0.041)):
    for i, z in enumerate((0.261, 0.242, 0.222)):
        K.box2(f'button_{nm}{i}', x - 0.0068, x + 0.0068, yf + 0.0075, yf + 0.0102, z - 0.0068, z + 0.0068, blk_gl, bev=0.0012)
K.cyl('dial', 0.0185, 0.012, (-0.002, yf + 0.004, 0.246), rot=(math.pi / 2, 0, 0), material=silver, verts=40, bev=0.001)
K.decal('dial_face', os.path.join(K.TEX, 'coffee_dial.png'), 0.037, 0.037, (-0.002, yf - 0.0021, 0.246), alpha=True, rough=0.3, metal=0.5)
# steam knob (top-left)
K.cyl('steam_knob_base', 0.006, 0.006, (-0.104, yf + 0.008, 0.292), rot=(math.pi / 2, 0, 0), material=chrome, verts=20)
K.box2('steam_knob_lever', -0.106, -0.102, yf + 0.0, yf + 0.006, 0.283, 0.296, chrome, bev=0.0015)

# DeLonghi badge housing + spout unit
bd = K.box2('badge_housing', -0.059, 0.059, yf + 0.030, yf + 0.060, 0.186, 0.209, silver, bev=0.004)
K.decal('badge', os.path.join(K.TEX, 'coffee_badge.png'), 0.112, 0.021, (0, yf + 0.0295, 0.1975), rough=0.3, metal=0.5)
K.box2('spout', -0.028, 0.027, yf + 0.040, yf + 0.072, 0.140, 0.186, blk_gl, bev=0.004)
K.box2('spout_bridge', -0.022, 0.021, yf + 0.046, yf + 0.058, 0.134, 0.141, chrome, bev=0.002)
for nm, x in (('l', -0.014), ('r', 0.014)):
    K.cyl(f'nozzle_{nm}', 0.0042, 0.016, (x, yf + 0.052, 0.128), material=chrome, verts=16, r2=0.0034)

# steam wand (Panarello): chrome elbow + black sleeve + chrome tip
K.cyl('wand_elbow', 0.004, 0.022, (-0.104, yf + 0.020, 0.205), rot=(math.pi / 2, 0, 0), material=chrome, verts=16)
K.cyl('wand_pipe', 0.0035, 0.025, (-0.104, yf + 0.010, 0.192), material=chrome, verts=16)
K.cyl('wand_sleeve', 0.0085, 0.080, (-0.104, yf + 0.010, 0.140), material=blk_gl, verts=24, bev=0.0015)
K.cyl('wand_tip', 0.0055, 0.014, (-0.104, yf + 0.010, 0.094), material=chrome, verts=20)

# top: silver cup-warmer frame + black bean-container lid
K.box2('top_frame', -hw + 0.002, hw - 0.002, yf + 0.010, D / 2 - 0.004, 0.316, 0.326, silver, bev=0.004)
K.box2('cup_tray', -hw + 0.012, hw - 0.012, yf + 0.016, yf + 0.100, 0.325, 0.329, K.mat('cup warmer', '#b8babd', rough=0.25, metal=1.0))
K.box2('lid', -0.106, 0.106, yf + 0.105, D / 2 - 0.015, 0.320, H, K.mat('lid', '#232325', rough=0.25), bev=0.012, seg=4)
K.box2('lid_window', -0.050, 0.050, yf + 0.120, yf + 0.150, H - 0.001, H + 0.0, blk_gl)

# drip tray with stainless grille
K.box2('drip_tray', -hw + 0.002, hw - 0.002, yf, yf + 0.150, 0.000, 0.030, silver, bev=0.006)
gr = K.box2('tray_grille', -hw + 0.008, hw - 0.008, yf + 0.004, yf + 0.074, 0.030, 0.033,
            K.mat('tray grille', '#ffffff', rough=0.25, metal=0.8, img=os.path.join(K.TEX, 'coffee_tray.png')))
K.uv_box_project(gr, 'Z', ((-hw + 0.008, hw - 0.008), (yf + 0.004, yf + 0.074)))
K.box2('tray_front_lip', -hw + 0.003, hw - 0.003, yf - 0.0, yf + 0.006, 0.026, 0.033, chrome, bev=0.002)
K.box2('feet', -hw + 0.02, hw - 0.02, yf + 0.16, D / 2 - 0.02, 0.0, 0.020, black)

K.finish('coffee_delonghi', [('', dict(view=(-0.6, -1.0, 0.45))), ('_front', dict(view=(0, -1, 0.1), lens=85))])
