"""Shared helpers for the bedhall product group (Blender 5.2, metres)."""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix

ASSETS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = None
KEY = None


def reset(key):
    global ROOT, KEY
    KEY = key
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ROOT = bpy.data.objects.new("PROD_" + key, None)
    ROOT.empty_display_size = 0.1
    bpy.context.scene.collection.objects.link(ROOT)
    bpy.context.scene.unit_settings.system = 'METRIC'
    return ROOT


def mat(part, color, rough=0.5, metal=0.0, alpha=1.0, emission=None, estrength=0.0, transmission=0.0, ior=1.45):
    name = f"{KEY} {part}"
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    c = tuple(color) + (1.0,) if len(color) == 3 else tuple(color)
    b.inputs["Base Color"].default_value = c
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if transmission:
        b.inputs["Transmission Weight"].default_value = transmission
        b.inputs["IOR"].default_value = ior
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
        try:
            m.surface_render_method = 'BLENDED'
        except Exception:
            pass
    if emission is not None:
        b.inputs["Emission Color"].default_value = tuple(emission) + (1.0,)
        b.inputs["Emission Strength"].default_value = estrength
    m.diffuse_color = c
    return m


def hexcol(h):
    h = h.lstrip('#')
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in srgb)


def link(obj, part, material=None, parent=None, smooth=False):
    obj.name = f"{KEY}_{part}"
    if obj.data is not None:
        obj.data.name = obj.name
    if obj.name not in bpy.context.scene.collection.objects and not obj.users_collection:
        bpy.context.scene.collection.objects.link(obj)
    obj.parent = parent or ROOT
    if material is not None and obj.type == 'MESH':
        obj.data.materials.clear()
        obj.data.materials.append(material)
    if smooth and obj.type == 'MESH':
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj


def mesh_from_bm(bm, part, material=None, smooth=False, parent=None):
    me = bpy.data.meshes.new(part)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(part, me)
    bpy.context.scene.collection.objects.link(ob)
    return link(ob, part, material, parent, smooth)


def box(part, size, loc, material=None, bevel=0.0, segs=2, rot=(0, 0, 0), parent=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    ob = mesh_from_bm(bm, part, material, parent=parent)
    ob.location = loc
    ob.rotation_euler = rot
    if bevel > 0:
        add_bevel(ob, bevel, segs)
    return ob


def add_bevel(ob, width, segs=2, limit='ANGLE', harden=True):
    md = ob.modifiers.new("Bevel", 'BEVEL')
    md.width = width
    md.segments = segs
    md.limit_method = limit
    if limit == 'ANGLE':
        md.angle_limit = math.radians(35)
    md.harden_normals = False
    for p in ob.data.polygons:
        p.use_smooth = segs > 1
    return md


def cyl(part, r, h, loc, material=None, verts=32, rot=(0, 0, 0), r2=None, cap=True, parent=None, smooth=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=verts, radius1=r,
                          radius2=r if r2 is None else r2, depth=h)
    ob = mesh_from_bm(bm, part, material, parent=parent)
    ob.location = loc
    ob.rotation_euler = rot
    if smooth:
        for p in ob.data.polygons:
            p.use_smooth = abs(p.normal.z) < 0.99
    return ob


def tube_path(part, pts, radius, material=None, sides=8, parent=None, closed=False):
    """Round tube along polyline pts (list of Vector-like)."""
    cu = bpy.data.curves.new(part, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = radius
    cu.bevel_resolution = max(1, sides // 4 - 1)
    cu.use_fill_caps = True
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts):
        p.co = (c[0], c[1], c[2], 1)
    sp.use_cyclic_u = closed
    ob = bpy.data.objects.new(part, cu)
    bpy.context.scene.collection.objects.link(ob)
    return to_mesh(ob, part, material, parent)


def to_mesh(ob, part, material=None, parent=None):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    mw = ob.matrix_world.copy()
    bpy.data.objects.remove(ob)
    o2 = bpy.data.objects.new(part, me)
    o2.matrix_world = mw
    bpy.context.scene.collection.objects.link(o2)
    for p in me.polygons:
        p.use_smooth = True
    return link(o2, part, material, parent)


def lathe(part, profile, material=None, segs=48, parent=None, loc=(0, 0, 0), smooth=True, close_axis=False):
    """profile: list of (r, z) points; revolve around Z."""
    bm = bmesh.new()
    rings = []
    for i in range(segs):
        a = 2 * math.pi * i / segs
        ca, sa = math.cos(a), math.sin(a)
        rings.append([bm.verts.new((r * ca, r * sa, z)) for r, z in profile])
    n = len(profile)
    for i in range(segs):
        r0, r1 = rings[i], rings[(i + 1) % segs]
        for j in range(n - 1):
            bm.faces.new((r0[j], r1[j], r1[j + 1], r0[j + 1]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = mesh_from_bm(bm, part, material, smooth=smooth, parent=parent)
    ob.location = loc
    return ob


def apply_all():
    """Apply modifiers on all meshes (export applies them anyway; makes counts accurate)."""
    for ob in [o for o in bpy.data.objects if o.type == 'MESH']:
        bpy.context.view_layer.objects.active = ob
        for md in list(ob.modifiers):
            try:
                with bpy.context.temp_override(object=ob, active_object=ob):
                    bpy.ops.object.modifier_apply(modifier=md.name)
            except Exception as e:
                print("apply fail", ob.name, md.name, e)


def stats():
    dg = bpy.context.evaluated_depsgraph_get()
    mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3); tris = 0
    for ob in bpy.data.objects:
        if ob.type != 'MESH':
            continue
        e = ob.evaluated_get(dg)
        me = e.to_mesh()
        me.calc_loop_triangles()
        tris += len(me.loop_triangles)
        for v in me.vertices:
            w = e.matrix_world @ v.co
            mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
        e.to_mesh_clear()
    d = mx - mn
    print(f"STATS {KEY}: min {tuple(round(x,4) for x in mn)} max {tuple(round(x,4) for x in mx)} "
          f"size {tuple(round(x,4) for x in d)} tris {tris}")
    return mn, mx, tris


def setup_render(res=800):
    sc = bpy.context.scene
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError as e:
        print(e)
    sc.render.resolution_x = res
    sc.render.resolution_y = res
    sc.render.film_transparent = False
    sc.view_settings.view_transform = 'Standard'
    try:
        sc.view_settings.look = 'None'
    except Exception:
        pass
    w = bpy.data.worlds.new("W"); sc.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs[0].default_value = (0.85, 0.85, 0.85, 1); bg.inputs[1].default_value = 0.55
    try:
        sc.eevee.use_shadows = True
        sc.eevee.taa_render_samples = 32
    except Exception:
        pass


def preview(path=None, elev=22, azim=-35, floor=True, wall=False, extra_light=None, zoom=1.0, target=None):
    """3/4 front view: front faces -Y, camera at front-left-ish (azim degrees from -Y toward -X/+X)."""
    sc = bpy.context.scene
    setup_render()
    mn, mx, _ = stats()
    c = (mn + mx) / 2 if target is None else Vector(target)
    rad = (mx - mn).length / 2
    helpers = []
    if floor:
        bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=max(2, rad * 6))
        me = bpy.data.meshes.new("_floor"); bm.to_mesh(me); bm.free()
        fl = bpy.data.objects.new("_floor", me); sc.collection.objects.link(fl); fl.location.z = mn.z - 0.0005
        fm = bpy.data.materials.new("_floor"); fm.use_nodes = True
        next(n for n in fm.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs[0].default_value = (0.7, 0.7, 0.7, 1)
        me.materials.append(fm); helpers.append(fl)
    if wall:
        bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=max(2, rad * 6))
        me = bpy.data.meshes.new("_wall"); bm.to_mesh(me); bm.free()
        wl = bpy.data.objects.new("_wall", me); sc.collection.objects.link(wl)
        wl.rotation_euler = (math.radians(90), 0, 0); wl.location = (0, 0.0005, 0)
        wm = bpy.data.materials.new("_wall"); wm.use_nodes = True
        next(n for n in wm.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs[0].default_value = (0.8, 0.8, 0.78, 1)
        me.materials.append(wm); helpers.append(wl)
    cam_d = bpy.data.cameras.new("_cam"); cam_d.lens = 70
    cam = bpy.data.objects.new("_cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
    e, a = math.radians(elev), math.radians(azim)
    dirv = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
    fov = 2 * math.atan(18 / cam_d.lens)
    dist = rad / math.sin(fov / 2) * 0.95 / zoom
    cam.location = c + dirv * dist
    cam.rotation_euler = (-dirv).to_track_quat('-Z', 'Y').to_euler()
    cam_d.clip_end = dist * 10
    sun_d = bpy.data.lights.new("_sun", 'SUN'); sun_d.energy = 1.8; sun_d.angle = math.radians(8)
    sun = bpy.data.objects.new("_sun", sun_d); sc.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(40), 0, math.radians(-30))
    ar_d = bpy.data.lights.new("_fill", 'AREA'); ar_d.energy = 12 * max(1, rad * 4) ** 2; ar_d.size = rad * 3
    ar = bpy.data.objects.new("_fill", ar_d); sc.collection.objects.link(ar)
    ar.location = c + Vector((rad * 2.5, -rad * 3, rad * 2))
    ar.rotation_euler = (-(ar.location - c)).to_track_quat('-Z', 'Y').to_euler()
    helpers += [cam, sun, ar]
    if extra_light:
        extra_light(helpers)
    sc.render.filepath = path or os.path.join(ASSETS, "previews", KEY + ".png")
    os.makedirs(os.path.dirname(sc.render.filepath), exist_ok=True)
    bpy.ops.render.render(write_still=True)
    for h in helpers:
        d = h.data
        bpy.data.objects.remove(h)
        if d is not None:
            try:
                if isinstance(d, bpy.types.Mesh): bpy.data.meshes.remove(d)
                elif isinstance(d, bpy.types.Camera): bpy.data.cameras.remove(d)
                elif isinstance(d, bpy.types.Light): bpy.data.lights.remove(d)
            except Exception:
                pass
    for m in [m for m in bpy.data.materials if m.name.startswith("_")]:
        bpy.data.materials.remove(m)
    sc.camera = None


def save(fname=None):
    for w in list(bpy.data.worlds):
        bpy.data.worlds.remove(w)
    path = os.path.join(ASSETS, (fname or KEY) + ".blend")
    try:
        bpy.ops.file.pack_all()
    except Exception as e:
        print("pack", e)
    bpy.ops.wm.save_as_mainfile(filepath=path, compress=True)
    print("SAVED", path)


def sweep_rect(part, pts, side, w, th, material=None, parent=None, caps=True, profile_round=0):
    """Sweep a w x th rectangle along polyline pts. `side` = constant Vector across width.
    Thickness direction = side x tangent."""
    side = Vector(side).normalized()
    bm = bmesh.new(); rings = []
    n = len(pts)
    for i, p in enumerate(pts):
        p = Vector(p)
        t = (Vector(pts[min(i + 1, n - 1)]) - Vector(pts[max(i - 1, 0)])).normalized()
        nv = side.cross(t).normalized()
        s = t.cross(nv).normalized()
        hw, ht = w / 2, th / 2
        rings.append([bm.verts.new(p + s * a + nv * b) for a, b in ((-hw, -ht), (hw, -ht), (hw, ht), (-hw, ht))])
    for a, b in zip(rings[:-1], rings[1:]):
        for k in range(4):
            bm.faces.new((a[k], a[(k + 1) % 4], b[(k + 1) % 4], b[k]))
    if caps:
        bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_from_bm(bm, part, material, parent=parent)


def arc_pts(center, r, a0, a1, n, axis_u, axis_v):
    """points on arc center + r*(cos a * u + sin a * v)."""
    c = Vector(center); u = Vector(axis_u); v = Vector(axis_v)
    return [c + r * (math.cos(a0 + (a1 - a0) * i / n) * u + math.sin(a0 + (a1 - a0) * i / n) * v) for i in range(n + 1)]


def extrude_outline(part, pts2d, z0, z1, material=None, parent=None):
    bm = bmesh.new()
    bot = [bm.verts.new((x, y, z0)) for x, y in pts2d]
    top = [bm.verts.new((x, y, z1)) for x, y in pts2d]
    bm.faces.new(bot[::-1]); bm.faces.new(top)
    m = len(pts2d)
    for i in range(m):
        j = (i + 1) % m
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_from_bm(bm, part, material, parent=parent)


def center_xy(only_x=False):
    mn, mx, _ = stats()
    c = (mn + mx) / 2
    for ob in ROOT.children:
        ob.location.x -= c.x
        if not only_x:
            ob.location.y -= c.y
    bpy.context.view_layer.update()


def join(objs, part):
    """Join objects (applying their modifiers) into one mesh named <key>_<part>."""
    objs = [o for o in objs if o is not None]
    dg = bpy.context.evaluated_depsgraph_get()
    bm = bmesh.new()
    mats = []
    for o in objs:
        e = o.evaluated_get(dg)
        me = e.to_mesh()
        me.transform(o.matrix_world)
        idx_map = []
        for m in (o.data.materials if o.data else []):
            if m not in mats:
                mats.append(m)
            idx_map.append(mats.index(m))
        for p in me.polygons:
            p.material_index = idx_map[p.material_index] if idx_map else 0
        n0 = len(bm.faces)
        bm.from_mesh(me)
        e.to_mesh_clear()
    for o in objs:
        bpy.data.objects.remove(o)
    me = bpy.data.meshes.new(part)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(part, me)
    bpy.context.scene.collection.objects.link(ob)
    link(ob, part, None)
    for m in mats:
        me.materials.append(m)
    return ob


def box_uv(ob, su=1.0, sv=1.0, along='X'):
    """Simple box-projection UVs in metres (u along the grain axis)."""
    me = ob.data
    uv = me.uv_layers[0] if me.uv_layers else me.uv_layers.new(name="UVMap")
    ax = {'X': 0, 'Y': 1, 'Z': 2}[along]
    for p in me.polygons:
        n = p.normal
        dom = max(range(3), key=lambda i: abs(n[i]))
        for li in p.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            if dom == ax:
                others = [i for i in range(3) if i != ax]
                u, v = co[others[0]], co[others[1]]
            else:
                o = [i for i in range(3) if i not in (ax, dom)][0]
                u, v = co[ax], co[o] + 0.37 * dom
            uv.data[li].uv = (u / su, v / sv)


def wood_image(name, base_rgb, size=(1024, 256), seed=1, streak=0.12, dark=0.18):
    """Procedural wood grain texture (numpy), grain along U. Returns packed image (<=1k)."""
    import numpy as np
    rng = np.random.default_rng(seed)
    w, h = size
    y = np.linspace(0, 1, h)[:, None]
    x = np.linspace(0, 1, w)[None, :]

    def smooth_noise(n, scale):
        a = rng.standard_normal(n)
        k = np.exp(-np.linspace(-3, 3, max(3, int(n * scale))) ** 2)
        return np.convolve(a, k / k.sum(), mode='same')
    wob = smooth_noise(w, 0.05)[None, :] * 0.03
    rows = np.zeros((h, w))
    for f, a in ((23, 1.0), (57, 0.5), (131, 0.25)):
        ph = rng.uniform(0, 6.28)
        rows += a * np.sin((y + wob * f / 23) * f * 2 * np.pi + ph + np.sin(x * 6.28 * rng.uniform(0.5, 1.5)) * 0.8)
    rows /= 1.75
    fine = rng.standard_normal((h, 1)) * 0.5 + rng.standard_normal((h, w)) * 0.08
    v = 1 + streak * rows + 0.04 * fine
    dk = (np.abs(np.sin((y + wob) * 9 * np.pi + 1.3)) < 0.06) * dark
    v = v - dk
    base = np.array(base_rgb)[None, None, :]
    lin = np.clip(base * v[..., None], 0, 1)
    srgb = np.where(lin <= 0.0031308, lin * 12.92, 1.055 * np.power(lin, 1 / 2.4) - 0.055)
    rgba = np.concatenate([srgb, np.ones((h, w, 1))], axis=2).astype(np.float32)
    im = bpy.data.images.new(name, w, h, alpha=False)
    im.colorspace_settings.name = 'sRGB'
    im.pixels.foreach_set(rgba.ravel())
    im.pack()
    return im


def mat_tex(part, image, rough=0.6, normal_image=None, nstrength=0.6):
    m = mat(part, (1, 1, 1), rough=rough)
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = image
    nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    if normal_image is not None:
        tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = normal_image
        tn.image.colorspace_settings.name = 'Non-Color'
        nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = nstrength
        nt.links.new(tn.outputs['Color'], nm.inputs['Color'])
        nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    return m
