import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kitlib as K
bpy = K.bpy

K.reset('fridge_samsung')
W, D, H = 0.595, 0.658, 2.030
y0 = -D / 2                 # front plane of the doors
DT = 0.060                  # door thickness
yb = y0 + DT                # front of cabinet body

inox = K.mat('dark inox door', '#3b3c40', rough=0.32, metal=0.85)
side = K.mat('cabinet', '#2f3033', rough=0.45, metal=0.6)
black = K.mat('black plastic', '#111112', rough=0.55)
silver = K.mat('handle trim', '#a9abae', rough=0.25, metal=1.0)
recess = K.mat('dispenser recess', '#161718', rough=0.5)

# cabinet body (sides/top in dark steel), back panel
K.box2('cabinet', -W / 2, W / 2, yb, D / 2 - 0.004, 0.030, H - 0.004, side, bev=0.003)
K.box2('back', -W / 2 + 0.01, W / 2 - 0.01, D / 2 - 0.006, D / 2, 0.05, H - 0.03, black)
K.box2('top_cover', -W / 2 + 0.003, W / 2 - 0.003, yb - 0.001, D / 2 - 0.02, H - 0.006, H, side, bev=0.003)
# kick plate + feet
K.box2('kickplate', -W / 2 + 0.008, W / 2 - 0.008, yb - 0.004, yb + 0.05, 0.012, 0.030, black, bev=0.002)
for sx in (-1, 1):
    K.cyl(f'foot_front_{"l" if sx < 0 else "r"}', 0.016, 0.014, (sx * (W / 2 - 0.04), yb + 0.03, 0.007), material=black, verts=16)
    K.cyl(f'roller_back_{"l" if sx < 0 else "r"}', 0.014, 0.012, (sx * (W / 2 - 0.05), D / 2 - 0.06, 0.016), rot=(0, math.pi / 2, 0), material=black, verts=16)
K.box2('rear_base', -W / 2 + 0.02, W / 2 - 0.02, D / 2 - 0.12, D / 2 - 0.01, 0.0, 0.03, black)
# door gasket line visible between doors
K.box2('gasket', -W / 2 + 0.004, W / 2 - 0.004, yb - 0.002, yb + 0.004, 0.030, H - 0.006, K.mat('gasket', '#0d0d0e', rough=0.8))

# ---- freezer door (bottom) with top grip recess + silver lip
FZ0, FZ1 = 0.030, 0.776
fd = K.box2('freezer_door', -W / 2, W / 2, y0, yb, FZ0, FZ1 - 0.012, inox, bev=0.003)
K.box2('freezer_grip_lip', -W / 2 + 0.002, W / 2 - 0.002, y0 + 0.010, yb, FZ1 - 0.012, FZ1, silver, bev=0.002)
# ---- fridge door (top) with bottom grip recess + silver lip
RZ0, RZ1 = 0.790, H
rd = K.box2('fridge_door', -W / 2, W / 2, y0, yb, RZ0 + 0.018, RZ1, inox, bev=0.003)
K.box2('fridge_grip_lip', -W / 2 + 0.002, W / 2 - 0.002, y0 + 0.006, yb, RZ0, RZ0 + 0.018, silver, bev=0.002)
K.box2('fridge_grip_shadow', -W / 2 + 0.004, W / 2 - 0.004, y0 + 0.018, yb - 0.004, RZ0 + 0.0, RZ0 + 0.0185, black)

# hinge covers (doors hinge on the right)
K.box2('hinge_top', W / 2 - 0.07, W / 2 - 0.01, y0 + 0.01, yb + 0.03, H - 0.002, H + 0.0, black)
K.box2('hinge_mid', W / 2 - 0.035, W / 2 - 0.0, y0 + 0.02, yb, RZ0 - 0.012, RZ0, black)

# ---- water dispenser recess (178 x 244 mm, top 700 mm below the top)
DW, DH = 0.178, 0.244
dz1 = H - 0.700
dz0 = dz1 - DH
cut = K.box2('disp_cut', -DW / 2, DW / 2, y0 - 0.01, y0 + 0.038, dz0, dz1, None)
cut.display_type = 'WIRE'
bm = rd.modifiers.new('cut', 'BOOLEAN')
bm.operation = 'DIFFERENCE'
bm.object = cut
bm.solver = 'EXACT'
rd.modifiers.move(rd.modifiers.find('cut'), 0)
bpy.context.view_layer.objects.active = rd
rd.select_set(True)
bpy.ops.object.modifier_apply(modifier='cut')
bpy.data.objects.remove(cut, do_unlink=True)
# liner
t = 0.002
K.box2('disp_back', -DW / 2, DW / 2, y0 + 0.036, y0 + 0.038, dz0, dz1, recess)
K.box2('disp_left', -DW / 2, -DW / 2 + t, y0, y0 + 0.038, dz0, dz1, recess)
K.box2('disp_right', DW / 2 - t, DW / 2, y0, y0 + 0.038, dz0, dz1, recess)
K.box2('disp_top', -DW / 2, DW / 2, y0, y0 + 0.038, dz1 - t, dz1, recess)
K.box2('disp_bottom', -DW / 2, DW / 2, y0, y0 + 0.038, dz0, dz0 + t, recess)
# silver bezel frame
for nm, (a, b, c, d) in {'l': (-DW / 2 - 0.003, -DW / 2, dz0 - 0.003, dz1 + 0.003), 'r': (DW / 2, DW / 2 + 0.003, dz0 - 0.003, dz1 + 0.003),
                         't': (-DW / 2, DW / 2, dz1, dz1 + 0.003), 'b': (-DW / 2, DW / 2, dz0 - 0.003, dz0)}.items():
    K.box2(f'disp_bezel_{nm}', a, b, y0 - 0.001, y0 + 0.004, c, d, silver)
# inner raised housing with paddle
K.box2('disp_housing', -0.040, 0.040, y0 + 0.012, y0 + 0.036, dz1 - 0.150, dz1 - 0.002, K.mat('dispenser housing', '#26272a', rough=0.4, metal=0.3), bev=0.003)
K.box2('disp_paddle', -0.030, 0.030, y0 + 0.010, y0 + 0.016, dz1 - 0.145, dz1 - 0.060, K.mat('dispenser paddle', '#303134', rough=0.35, metal=0.4), bev=0.003)
K.decal('disp_label', os.path.join(K.TEX, 'fridge_disp_label.png'), 0.056, 0.014, (0, y0 + 0.0115, dz1 - 0.025), rough=0.5)
K.box2('disp_trim', -0.040, 0.040, y0 + 0.011, y0 + 0.016, dz1 - 0.006, dz1 - 0.002, silver)
K.box2('disp_tray', -DW / 2 + 0.003, DW / 2 - 0.003, y0 + 0.003, y0 + 0.036, dz0 + t, dz0 + 0.008, K.mat('drip tray', '#0f0f10', rough=0.4))

# ---- display + logo decals
K.decal('display', os.path.join(K.TEX, 'fridge_display.png'), 0.073, 0.119, (0, y0 - 0.0006, H - 0.168 - 0.0595), rough=0.08)
K.decal('logo', os.path.join(K.TEX, 'fridge_logo.png'), 0.088, 0.011, (0, y0 - 0.0006, H - 0.105), alpha=True, rough=0.3)

K.finish('fridge_samsung', [('', dict(view=(-0.55, -1.0, 0.3))), ('_front', dict(view=(0, -1, 0.0), lens=85))])
