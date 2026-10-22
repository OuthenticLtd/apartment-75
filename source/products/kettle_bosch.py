import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kitlib as K
bpy = K.bpy

# Bosch TWK70B03 glass kettle 1.7 l : 210 W (spout..handle) x 140 D x 265 H mm
# spout to -X, handle to +X, BOSCH logo faces -Y (front)
K.reset('kettle_bosch')
c = -0.015            # jug axis x
R = 0.070             # jug radius
blk = K.mat('black gloss', '#0c0c0d', rough=0.12)
blk_m = K.mat('black matt', '#161617', rough=0.5)
steel = K.mat('steel ring', '#c8cacc', rough=0.18, metal=1.0)
glass = K.mat('glass', '#ffffff', rough=0.02, transmission=1.0, ior=1.5, alpha=0.18)

# power base (360 deg) + chrome ring
K.lathe('base', [(0, 0.0), (R - 0.004, 0.0), (R, 0.004), (R, 0.020), (0.0, 0.020)], blk_m, loc=(c, 0, 0), verts=64)
K.lathe('ring', [(R - 0.001, 0.020), (R + 0.0005, 0.021), (R + 0.0005, 0.027), (R - 0.001, 0.028), (0.0, 0.028)], steel, loc=(c, 0, 0), verts=64)
# lower black collar
K.lathe('lower_collar', [(R - 0.001, 0.028), (R, 0.030), (R, 0.080), (R - 0.004, 0.083), (0.0, 0.083)], blk, loc=(c, 0, 0), verts=64)
# glass jug wall (open tube with thickness)
K.lathe('glass', [(R - 0.004, 0.081), (R - 0.0035, 0.232), (R - 0.0065, 0.232), (R - 0.007, 0.083)], glass, loc=(c, 0, 0), verts=64, close=False)
# stainless heating floor seen through the glass
K.lathe('floor', [(0.0, 0.0835), (R - 0.007, 0.0835), (R - 0.007, 0.0845), (0.0, 0.0845)], K.mat('heating plate', '#a4a6a9', rough=0.35, metal=0.3), loc=(c, 0, 0), verts=48)
# top black collar + lid
K.lathe('top_collar', [(R - 0.006, 0.230), (R - 0.001, 0.230), (R, 0.233), (R, 0.252), (R - 0.006, 0.256), (R - 0.012, 0.256)], blk, loc=(c, 0, 0), verts=64)
K.lathe('lid', [(R - 0.012, 0.255), (R - 0.016, 0.262), (R - 0.024, 0.265), (0.0, 0.265)], blk, loc=(c, 0, 0), verts=64)
K.lathe('lid_disc', [(0.0, 0.2652), (0.038, 0.2652), (0.038, 0.2656), (0.0, 0.2656)], K.mat('lid insert', '#8e9094', rough=0.25, metal=0.8), loc=(c, 0, 0), verts=48)

# spout (wedge on the top collar, -X)
sp = [(c - R + 0.004, 0.232), (c - R - 0.020, 0.250), (c - R - 0.020, 0.257), (c - R + 0.004, 0.256)]
s = K.prism('spout', sp, -0.020, 0.020, blk, axis='Y', bev=0.003)

# handle: D-shaped loop on +X, swept rounded section
cu = bpy.data.curves.new('kettle_handle', 'CURVE')
cu.dimensions = '3D'
pl = cu.splines.new('BEZIER')
pts = [(c + R - 0.004, 0.248), (c + R + 0.026, 0.248), (c + R + 0.036, 0.228), (c + R + 0.036, 0.095), (c + R + 0.028, 0.072), (c + R - 0.004, 0.060)]
pl.bezier_points.add(len(pts) - 1)
for bp, (x, z) in zip(pl.bezier_points, pts):
    bp.co = (x, 0, z)
    bp.handle_left_type = bp.handle_right_type = 'AUTO'
cu.bevel_depth = 0.0085
cu.bevel_resolution = 3
cu.resolution_u = 8
ho = bpy.data.objects.new('kettle_bosch_handle', cu)
K.link(ho)
ho.scale = (1, 1.6, 1)
bpy.context.view_layer.objects.active = ho
ho.select_set(True)
bpy.ops.object.convert(target='MESH')
ho = bpy.context.active_object
ho.data.materials.clear()
ho.data.materials.append(blk)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
ho.select_set(False)
# handle details: lid release button on top, on/off switch with red light on the outer back
K.box2('lid_button', c + R + 0.006, c + R + 0.026, -0.009, 0.009, 0.2525, 0.2565, K.mat('button', '#1f1f21', rough=0.3), bev=0.002)
K.box2('switch', c + R + 0.0435, c + R + 0.0465, -0.007, 0.007, 0.175, 0.205, K.mat('switch', '#1d1d1f', rough=0.3), bev=0.0012)
K.cyl('switch_led', 0.0028, 0.002, (c + R + 0.045, 0, 0.214), rot=(0, math.pi / 2, 0), material=K.mat('led', '#e8202a', rough=0.2, emission='#ff2020', estrength=3), verts=16)

# logo + water scale decals
K.decal('logo', os.path.join(K.TEX, 'kettle_logo.png'), 0.040, 0.009, (c, -R - 0.0004, 0.052), alpha=True, rough=0.3)
sc = K.decal('scale', os.path.join(K.TEX, 'kettle_scale.png'), 0.024, 0.100, (c, -R + 0.0037, 0.160), alpha=True, rough=0.3)

K.finish('kettle_bosch', [('', dict(view=(-0.2, -1.0, 0.35)))])
