import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kitlib as K

K.reset('hob_bosch')
W, D = 0.592, 0.522
GT = 0.0045           # glass thickness, sits on the worktop (z=0 = glass underside)
BH = 0.051 - GT       # housing below the worktop

glass_m = K.mat('glass', '#1a1a19', rough=0.06, img=os.path.join(K.TEX, 'hob_bosch_top.png'))
g = K.box('glass', (W, D, GT), (0, 0, GT / 2), glass_m)
K.bevel(g, 0.0012, 2)
K.uv_box_project(g, 'Z', ((-W / 2, W / 2), (-D / 2, D / 2)))

# housing below the worktop (cut-out 560 x 490)
body_m = K.mat('housing', '#2b2b2c', rough=0.55, metal=0.3)
K.box('housing', (0.548, 0.482, BH - 0.004), (0, 0.004, -(BH - 0.004) / 2), body_m, bev=0.002)
# underside fan grille / bottom tray step
tray_m = K.mat('bottom', '#3a3a3c', rough=0.6, metal=0.5)
K.box('bottom', (0.50, 0.44, 0.004), (0, 0.004, -BH + 0.002), tray_m)
# seal under the glass edge
seal_m = K.mat('seal', '#111111', rough=0.8)
K.box('seal', (0.566, 0.496, 0.0015), (0, 0.004, -0.00075), seal_m)

K.finish('hob_bosch', [('', dict(view=(-0.35, -1.0, 0.9), floor_z=-0.0003, floor_col=(0.55,0.42,0.28,1))), ('_b', dict(view=(-0.6, -0.6, -0.5), floor=False))])
