# Shared helpers for the kitchen product models (Blender 5.2, headless)
import bpy, bmesh, math, os
from mathutils import Vector, Matrix

ASSETS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(ASSETS, 'scripts', 'tex')
os.makedirs(TEX, exist_ok=True)

ROOT = None
KEY = None


def srgb(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x / 12.92) if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c) + (1.0,)


def reset(key):
    global ROOT, KEY
    KEY = key
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ROOT = bpy.data.objects.new('PROD_' + key, None)
    ROOT.empty_display_size = 0.1
    bpy.context.scene.collection.objects.link(ROOT)
    bpy.context.scene.unit_settings.system = 'METRIC'
    return ROOT


_mats = {}


def mat(part, color='#808080', rough=0.5, metal=0.0, img=None, alpha_img=False, alpha=1.0,
        transmission=0.0, ior=1.45, emission=None, estrength=1.0, coat=0.0, nonrepeat=True):
    name = f'{KEY} {part}'
    if name in _mats and _mats[name].name in bpy.data.materials:
        return _mats[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = srgb(color) if isinstance(color, str) else color
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if transmission:
        b.inputs['Transmission Weight'].default_value = transmission
        b.inputs['IOR'].default_value = ior
    if coat:
        b.inputs['Coat Weight'].default_value = coat
        b.inputs['Coat Roughness'].default_value = 0.03
    if alpha < 1.0:
        b.inputs['Alpha'].default_value = alpha
    if emission:
        b.inputs['Emission Color'].default_value = srgb(emission)
        b.inputs['Emission Strength'].default_value = estrength
    if img:
        im = bpy.data.images.load(img, check_existing=True)
        t = nt.nodes.new('ShaderNodeTexImage')
        t.image = im
        t.extension = 'EXTEND' if nonrepeat else 'REPEAT'
        nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
        if alpha_img:
            nt.links.new(t.outputs['Alpha'], b.inputs['Alpha'])
        if emission == 'img':
            pass
    try:
        if alpha < 1.0 or alpha_img or transmission:
            m.surface_render_method = 'BLENDED' if (alpha < 1 or transmission) else 'DITHERED'
    except Exception:
        pass
    m.diffuse_color = b.inputs['Base Color'].default_value
    _mats[name] = m
    return m


def link(ob, parent=None):
    bpy.context.scene.collection.objects.link(ob)
    ob.parent = parent or ROOT
    return ob


def mesh_obj(part, bm, material=None, parent=None):
    me = bpy.data.meshes.new(f'{KEY}_{part}')
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(f'{KEY}_{part}', me)
    if material:
        if isinstance(material, (list, tuple)):
            for mm in material:
                me.materials.append(mm)
        else:
            me.materials.append(material)
    link(ob, parent)
    return ob


def smooth(ob, angle=35):
    me = ob.data
    for p in me.polygons:
        p.use_smooth = True
    try:
        ob.modifiers.new('Smooth', 'SMOOTH_BY_ANGLE')
    except Exception:
        pass
    try:
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angle))
        ob.select_set(False)
    except Exception:
        pass
    return ob


def bevel(ob, w, seg=3, limit='ANGLE', angle=30):
    m = ob.modifiers.new('Bevel', 'BEVEL')
    m.width = w
    m.segments = seg
    m.limit_method = limit
    if limit == 'ANGLE':
        m.angle_limit = math.radians(angle)
    m.harden_normals = False
    return m


def box(part, size, loc, material=None, bev=0.0, seg=3, parent=None):
    """size (x,y,z), loc = centre"""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0] + loc[0], v.co.y * size[1] + loc[1], v.co.z * size[2] + loc[2]))
    ob = mesh_obj(part, bm, material, parent)
    if bev:
        bevel(ob, bev, seg)
        smooth(ob)
    return ob


def box2(part, x0, x1, y0, y1, z0, z1, material=None, bev=0.0, seg=3, parent=None):
    return box(part, (x1 - x0, y1 - y0, z1 - z0), ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), material, bev, seg, parent)


def cyl(part, r, depth, loc, rot=(0, 0, 0), material=None, verts=32, r2=None, bev=0.0, seg=2, parent=None, cap=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=verts, radius1=r,
                          radius2=r if r2 is None else r2, depth=depth)
    R = Matrix.Translation(loc) @ (Matrix.Rotation(rot[2], 4, 'Z') @ Matrix.Rotation(rot[1], 4, 'Y') @ Matrix.Rotation(rot[0], 4, 'X'))
    bmesh.ops.transform(bm, matrix=R, verts=bm.verts)
    ob = mesh_obj(part, bm, material, parent)
    smooth(ob)
    if bev:
        bevel(ob, bev, seg)
    return ob


def rrect_pts(w, h, r, n=6, cx=0.0, cy=0.0):
    """rounded rectangle outline (CCW), centred"""
    pts = []
    r = min(r, w / 2 - 1e-5, h / 2 - 1e-5)
    corners = [(w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)]
    for (x, y, a0) in corners:
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + x + r * math.cos(a), cy + y + r * math.sin(a)))
    return pts


def prism(part, pts, z0, z1, material=None, axis='Z', parent=None, bev=0.0, seg=2, offset=(0, 0, 0)):
    """extrude 2D polygon pts along axis between z0 and z1.
    axis 'Z': pts are (x,y). axis 'Y': pts are (x,z), extruded along y from z0..z1.
    axis 'X': pts are (y,z), extruded along x."""
    bm = bmesh.new()

    def mk(p, d):
        a, b_ = p
        if axis == 'Z':
            return Vector((a, b_, d))
        if axis == 'Y':
            return Vector((a, d, b_))
        return Vector((d, a, b_))
    bot = [bm.verts.new(mk(p, z0)) for p in pts]
    top = [bm.verts.new(mk(p, z1)) for p in pts]
    n = len(pts)
    f0 = bm.faces.new(bot[::-1])
    f1 = bm.faces.new(top)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.translate(bm, vec=Vector(offset), verts=bm.verts)
    ob = mesh_obj(part, bm, material, parent)
    if bev:
        bevel(ob, bev, seg)
    smooth(ob)
    return ob


def lathe(part, prof, material=None, verts=48, loc=(0, 0, 0), parent=None, scale_xy=(1, 1), close=True):
    """prof: list of (r, z) from bottom to top. revolve around Z."""
    bm = bmesh.new()
    rings = []
    for (r, z) in prof:
        ring = []
        for i in range(verts):
            a = 2 * math.pi * i / verts
            ring.append(bm.verts.new((loc[0] + r * math.cos(a) * scale_xy[0], loc[1] + r * math.sin(a) * scale_xy[1], loc[2] + z)))
        rings.append(ring)
    for k in range(len(rings) - 1):
        for i in range(verts):
            j = (i + 1) % verts
            bm.faces.new((rings[k][i], rings[k][j], rings[k + 1][j], rings[k + 1][i]))
    if close:
        if prof[0][0] > 1e-6:
            bm.faces.new(rings[0][::-1])
        if prof[-1][0] > 1e-6:
            bm.faces.new(rings[-1])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = mesh_obj(part, bm, material, parent)
    smooth(ob)
    return ob


def decal(part, img, w, h, loc, facing='-Y', material=None, alpha=False, rough=0.3, color=None, metal=0.0, emission=False, estrength=1.0):
    """textured quad (UV 0..1). facing: '-Y' front, '+Z' up, '-Z' down, '+X','-X'"""
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new('UVMap')
    hw, hh = w / 2, h / 2
    if facing == '-Y':
        co = [(-hw, 0, -hh), (hw, 0, -hh), (hw, 0, hh), (-hw, 0, hh)]
    elif facing == '+Y':
        co = [(hw, 0, -hh), (-hw, 0, -hh), (-hw, 0, hh), (hw, 0, hh)]
    elif facing == '+Z':
        co = [(-hw, -hh, 0), (hw, -hh, 0), (hw, hh, 0), (-hw, hh, 0)]
    elif facing == '-Z':
        co = [(-hw, hh, 0), (hw, hh, 0), (hw, -hh, 0), (-hw, -hh, 0)]
    elif facing == '+X':
        co = [(0, -hw, -hh), (0, hw, -hh), (0, hw, hh), (0, -hw, hh)]
    else:  # -X
        co = [(0, hw, -hh), (0, -hw, -hh), (0, -hw, hh), (0, hw, hh)]
    vs = [bm.verts.new(Vector(c) + Vector(loc)) for c in co]
    f = bm.faces.new(vs)
    for l, u in zip(f.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
        l[uv].uv = u
    if material is None:
        material = mat(part, color or '#ffffff', rough, metal, img=img, alpha_img=alpha)
        if emission:
            nt = material.node_tree
            b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
            t = next(n for n in nt.nodes if n.type == 'TEX_IMAGE')
            nt.links.new(t.outputs['Color'], b.inputs['Emission Color'])
            b.inputs['Emission Strength'].default_value = estrength
    return mesh_obj(part, bm, material)


def uv_box_project(ob, axis='Z', bounds=None):
    """planar UV projection of a mesh along axis, normalised to bounds ((u0,u1),(v0,v1)) in world units."""
    me = ob.data
    if not me.uv_layers:
        me.uv_layers.new(name='UVMap')
    uvl = me.uv_layers.active.data
    for p in me.polygons:
        for li in p.loop_indices:
            v = me.vertices[me.loops[li].vertex_index].co
            if axis == 'Z':
                a, b = v.x, v.y
            elif axis == 'Y':
                a, b = v.x, v.z
            else:
                a, b = v.y, v.z
            if bounds:
                (u0, u1), (v0, v1) = bounds
                a = (a - u0) / (u1 - u0)
                b = (b - v0) / (v1 - v0)
            uvl[li].uv = (a, b)


def apply_all_and_stats():
    dg = bpy.context.evaluated_depsgraph_get()
    tris = 0
    mn = Vector((1e9,) * 3)
    mx = Vector((-1e9,) * 3)
    for ob in bpy.data.objects:
        if ob.type != 'MESH':
            continue
        e = ob.evaluated_get(dg)
        me = e.to_mesh()
        me.calc_loop_triangles()
        tris += len(me.loop_triangles)
        for v in me.vertices:
            w = e.matrix_world @ v.co
            mn = Vector(map(min, mn, w))
            mx = Vector(map(max, mx, w))
        e.to_mesh_clear()
    return tris, mn, mx


def setup_render(res=800):
    sc = bpy.context.scene
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x = res
    sc.render.resolution_y = res
    sc.render.film_transparent = False
    try:
        sc.eevee.taa_render_samples = 32
        sc.eevee.use_raytracing = True
    except Exception:
        pass
    sc.view_settings.view_transform = 'AgX' if 'AgX' in [i.identifier for i in sc.view_settings.bl_rna.properties['view_transform'].enum_items] else 'Standard'
    w = bpy.data.worlds.new('W')
    sc.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs['Color'].default_value = (0.25, 0.25, 0.26, 1)
    bg.inputs['Strength'].default_value = 1.0


def add_light(loc, energy, size=1.0, target=(0, 0, 0)):
    ld = bpy.data.lights.new('L', 'AREA')
    ld.energy = energy
    ld.size = size
    lo = bpy.data.objects.new('L', ld)
    lo.location = loc
    d = Vector(target) - Vector(loc)
    lo.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.collection.objects.link(lo)
    return lo


def render_preview(path, view=(-0.55, -1.0, 0.45), res=800, lens=50, margin=1.12, floor=True, target_override=None, extra_lights=True, ortho=False, floor_z=None, floor_col=(0.75, 0.75, 0.75, 1)):
    setup_render(res)
    tris, mn, mx = apply_all_and_stats()
    c = (mn + mx) / 2 if target_override is None else Vector(target_override)
    size = (mx - mn)
    rad = size.length / 2
    d = Vector(view).normalized()
    cd = bpy.data.cameras.new('C')
    cd.lens = lens
    cam = bpy.data.objects.new('C', cd)
    bpy.context.scene.collection.objects.link(cam)
    fov = 2 * math.atan(18 / lens)
    dist = rad * margin / math.sin(fov / 2)
    if ortho:
        cd.type = 'ORTHO'
        cd.ortho_scale = rad * 2 * margin
        dist = rad * 4 + 1
    cam.location = c + d * dist
    cam.rotation_euler = (c - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cd.clip_start = 0.01
    cd.clip_end = dist * 4 + 10
    bpy.context.scene.camera = cam
    L = max(rad, 0.15)
    add_light(c + Vector((-1.5, -2.0, 2.2)) * L * 2, 150 * L * L * 4, size=L * 2, target=c)
    if extra_lights:
        add_light(c + Vector((2.0, -1.0, 1.0)) * L * 2, 60 * L * L * 4, size=L * 2, target=c)
        add_light(c + Vector((0.0, 1.5, 2.5)) * L * 2, 60 * L * L * 4, size=L * 2, target=c)
    tmp = []
    if floor:
        fm = bpy.data.materials.new('preview floor')
        fm.use_nodes = True
        b = next(n for n in fm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        b.inputs['Base Color'].default_value = floor_col
        b.inputs['Roughness'].default_value = 0.6
        bpy.ops.mesh.primitive_plane_add(size=rad * 20, location=(c.x, c.y, (mn.z - 0.0005) if floor_z is None else floor_z))
        fl = bpy.context.active_object
        fl.data.materials.append(fm)
        tmp.append(fl)
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    # clean up preview-only objects
    for ob in tmp + [cam] + [o for o in bpy.data.objects if o.type == 'LIGHT']:
        bpy.data.objects.remove(ob, do_unlink=True)
    for m in [m for m in bpy.data.materials if m.name == 'preview floor']:
        bpy.data.materials.remove(m)
    bpy.context.scene.camera = None
    return tris, mn, mx


def finish(key, previews=None):
    """previews: list of (suffix, kwargs). first one saved as <key>.png"""
    tris, mn, mx = apply_all_and_stats()
    print(f'### {key}: tris={tris} bbox min={tuple(round(x, 4) for x in mn)} max={tuple(round(x, 4) for x in mx)} size={tuple(round(x, 4) for x in (mx - mn))}')
    # remove orphan data
    bpy.ops.outliner.orphans_purge(do_recursive=True) if hasattr(bpy.ops.outliner, 'orphans_purge') else None
    try:
        bpy.ops.file.pack_all()
    except Exception as e:
        print('pack', e)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ASSETS, key + '.blend'), compress=True)
    previews = previews or [('', {})]
    for suf, kw in previews:
        p = os.path.join(ASSETS, 'previews', key + suf + '.png')
        render_preview(p, **kw)
    # the blend was saved before preview objects were added; nothing else to do
    return tris


def uv_cube(ob, tile=0.1):
    """per-face box projection (dominant normal axis), repeating every `tile` metres"""
    me = ob.data
    if not me.uv_layers:
        me.uv_layers.new(name='UVMap')
    uvl = me.uv_layers.active.data
    for p in me.polygons:
        n = p.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for li in p.loop_indices:
            v = me.vertices[me.loops[li].vertex_index].co
            if ax == 2:
                a, b = v.x, v.y
            elif ax == 1:
                a, b = v.x, v.z
            else:
                a, b = v.y, v.z
            uvl[li].uv = (a / tile, b / tile)
