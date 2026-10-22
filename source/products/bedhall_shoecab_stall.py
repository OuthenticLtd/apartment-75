import sys, os, math, bpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bedhall_common as C
C.reset("shoecab_stall")
W, D, H = 0.96, 0.17, 0.90
white = C.mat("body white", C.hexcol("F1F1EE"), rough=0.45)
door_m = C.mat("door white", C.hexcol("F3F3F0"), rough=0.4)
cup = C.mat("handle", C.hexcol("7d7e7f"), rough=0.4, metal=0.8)
cupin = C.mat("handle inner", C.hexcol("1d1d1d"), rough=0.6, metal=0.3)
dark = C.mat("interior", C.hexcol("2a2a2a"), rough=0.8)
T = 0.016          # board thickness
ZB = 0.105         # carcass bottom
y0, y1 = -D/2, D/2
# carcass
C.box("top", (W, D, 0.018), (0, 0, H - 0.009), white, bevel=0.0015)
for s in (-1, 1):
    C.box(f"side_{'l' if s<0 else 'r'}", (T, D - 0.001, H - 0.018 - ZB), (s*(W/2 - T/2), 0.0005, (ZB + H - 0.018)/2), white, bevel=0.001)
C.box("bottom", (W - 2*T, D - 0.002, T), (0, 0.001, ZB + T/2), white, bevel=0.001)
C.box("divider", (T, D - 0.004, H - 0.018 - ZB - T), (0, 0.002, (ZB + T + H - 0.018)/2), white, bevel=0.001)
C.box("back", (W - 0.004, 0.004, H - 0.018 - ZB), (0, D/2 - 0.002, (ZB + H - 0.018)/2), white)
C.box("inside", (W - 2*T, 0.01, H - 0.02 - ZB - T), (0, 0.04, (ZB + T + H - 0.02)/2), dark)
# doors (inset, flush with front), 2x2
g = 0.003
zlo, zhi = ZB + T, H - 0.018
zm = (zlo + zhi) / 2
cw = (W - 3*T) / 2
DT = 0.016
handles = []
for col, cx in (("l", -(T/2 + cw/2)), ("r", T/2 + cw/2)):
    for row, (za, zb) in (("bottom", (zlo, zm)), ("top", (zm, zhi))):
        h = zb - za - 2*g if row == "top" else zb - za - 2*g
        dz = (za + zb)/2
        d = C.box(f"door_{row}_{col}", (cw - 2*g, DT, zb - za - 2*g), (cx, y0 + DT/2 + 0.0005, dz), door_m, bevel=0.0012)
        # recessed grip slot near top of the door
        hz = zb - g - 0.03
        cut = C.box("_cut", (0.110, 0.05, 0.024), (cx, y0, hz), None, bevel=0.0)
        bv = cut.modifiers.new("bv", 'BEVEL'); bv.width = 0.0075; bv.segments = 4; bv.limit_method = 'ANGLE'
        import bmesh as _b
        bv.limit_method = 'WEIGHT'
        attr = cut.data.attributes.new("bevel_weight_edge", 'FLOAT', 'EDGE')
        for e in cut.data.edges:
            v0, v1 = (cut.data.vertices[i].co for i in e.vertices)
            if abs(v0.x - v1.x) < 1e-6 and abs(v0.z - v1.z) < 1e-6 and v0.z < 0:
                attr.data[e.index].value = 1.0
        with bpy.context.temp_override(object=cut, active_object=cut):
            bpy.ops.object.modifier_apply(modifier="bv")
        bm_ = d.modifiers.new("cut", 'BOOLEAN'); bm_.object = cut; bm_.operation = 'DIFFERENCE'; bm_.solver = 'EXACT'
        d.modifiers.move(d.modifiers.find("cut"), 0)
        handles.append((cut, cx, hz))
# apply booleans, remove cutters
C.apply_all()
for cut, cx, hz in handles:
    bpy.data.objects.remove(cut)
for ob in [o for o in bpy.data.objects if o.type == 'MESH' and '_door_' in o.name]:
    for p in ob.data.polygons:
        p.material_index = 0
    while len(ob.data.materials) > 1:
        ob.data.materials.pop(index=len(ob.data.materials) - 1)
for i, (_, cx, hz) in enumerate(handles):
    # metal grip cup: back plate + rounded lip, sits inside the slot
    C.box(f"grip{i+1}", (0.112, 0.010, 0.026), (cx, y0 + DT + 0.004, hz), cupin)
    C.box(f"grip{i+1}_lip", (0.100, 0.012, 0.002), (cx, y0 + DT/2 + 0.003, hz - 0.011), cup)
# base: rails + tapered legs
LX = 0.87/2 - 0.0175; LY = 0.12/2 - 0.0175
for sx in (-1, 1):
    for sy in (-1, 1):
        import bmesh
        bm = bmesh.new()
        top_s, bot_s = 0.035, 0.026
        vs = []
        for z, s in ((0.0, bot_s), (ZB, top_s)):
            for (a, b) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                # outer faces stay vertical, inner faces taper
                ox = sx*LX + (a*s/2 if a == sx else a*s/2) if False else sx*LX + a*s/2 + (sx*(top_s - s)/2)
                oy = sy*LY + b*s/2 + (sy*(top_s - s)/2)
                vs.append(bm.verts.new((ox, oy, z)))
        bm.faces.new(vs[:4][::-1]); bm.faces.new(vs[4:])
        for k in range(4):
            bm.faces.new((vs[k], vs[(k+1)%4], vs[4+(k+1)%4], vs[4+k]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        leg = C.mesh_from_bm(bm, f"leg_{'f' if sy<0 else 'b'}{'l' if sx<0 else 'r'}", white)
        C.add_bevel(leg, 0.002, 2)
RH = 0.026
for sy in (-1, 1):
    C.box(f"rail_{'f' if sy<0 else 'b'}", (2*LX, 0.018, RH), (0, sy*(LY + 0.0085), ZB - RH/2), white, bevel=0.001)
for sx in (-1, 1):
    C.box(f"rail_{'l' if sx<0 else 'r'}", (0.018, 2*LY, RH), (sx*(LX + 0.0085), 0, ZB - RH/2), white, bevel=0.001)
C.preview(azim=-32, elev=15)
C.save()
