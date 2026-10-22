"""Shared helpers for product modelling (living group)."""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix

ASSETS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.unit_settings.system = 'METRIC'
    s.unit_settings.scale_length = 1.0
    return s


def root(key):
    e = bpy.data.objects.new("PROD_" + key, None)
    e.empty_display_type = 'PLAIN_AXES'
    e.empty_display_size = 0.2
    bpy.context.scene.collection.objects.link(e)
    return e


def srgb2lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def mat(name, rgb255, rough=0.5, metal=0.0, lin=None, alpha=1.0, emission=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    col = lin if lin is not None else [srgb2lin(v) for v in rgb255]
    b.inputs['Base Color'].default_value = (*col, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if alpha < 1:
        b.inputs['Alpha'].default_value = alpha
        try:
            m.surface_render_method = 'BLENDED'
        except Exception:
            pass
    if emission:
        b.inputs['Emission Color'].default_value = (*emission[0], 1)
        b.inputs['Emission Strength'].default_value = emission[1]
    m.diffuse_color = (*col, alpha)
    return m


def obj_from_bm(name, bm, parent, material=None, smooth=True):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.parent = parent
    if material:
        me.materials.append(material)
    for p in me.polygons:
        p.use_smooth = smooth
    return ob


def add_bevel(ob, width, segments=3, angle=40, harden=False):
    md = ob.modifiers.new("Bevel", 'BEVEL')
    md.width = width
    md.segments = segments
    md.limit_method = 'ANGLE'
    md.angle_limit = math.radians(angle)
    md.harden_normals = harden
    return md


def add_subsurf(ob, levels=1):
    md = ob.modifiers.new("Subdiv", 'SUBSURF')
    md.levels = levels
    md.render_levels = levels
    return md


def box(name, parent, mn, mx, material=None, bevel=None, seg=3, smooth=True):
    """Axis aligned box from min to max corner (metres)."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    c = [(a + b) / 2 for a, b in zip(mn, mx)]
    s = [(b - a) for a, b in zip(mn, mx)]
    for v in bm.verts:
        v.co = Vector((c[0] + v.co.x * s[0], c[1] + v.co.y * s[1], c[2] + v.co.z * s[2]))
    ob = obj_from_bm(name, bm, parent, material, smooth)
    if bevel:
        add_bevel(ob, bevel, seg)
        ob.data.polygons.foreach_set('use_smooth', [True] * len(ob.data.polygons))
    return ob


def cylinder(name, parent, r_bot, r_top, z0, z1, x=0, y=0, seg=24, material=None,
             cap_top=True, cap_bot=True, smooth=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                          radius1=r_bot, radius2=r_top, depth=z1 - z0)
    bmesh.ops.translate(bm, verts=bm.verts, vec=Vector((x, y, (z0 + z1) / 2)))
    ob = obj_from_bm(name, bm, parent, material, smooth)
    return ob


def surface_grid_box(hx, hy, hz, nx, ny, nz):
    """Closed quad mesh of a box surface [-h,h]^3 with nx,ny,nz segments per axis."""
    bm = bmesh.new()
    vmap = {}

    def V(i, j, k):
        key = (i, j, k)
        if key not in vmap:
            vmap[key] = bm.verts.new((-hx + 2 * hx * i / nx, -hy + 2 * hy * j / ny, -hz + 2 * hz * k / nz))
        return vmap[key]

    def face(a, b, c, d):
        bm.faces.new((a, b, c, d))

    for i in range(nx):
        for j in range(ny):
            face(V(i, j, nz), V(i + 1, j, nz), V(i + 1, j + 1, nz), V(i, j + 1, nz))  # top
            face(V(i, j + 1, 0), V(i + 1, j + 1, 0), V(i + 1, j, 0), V(i, j, 0))  # bottom
    for i in range(nx):
        for k in range(nz):
            face(V(i, 0, k), V(i + 1, 0, k), V(i + 1, 0, k + 1), V(i, 0, k + 1))  # -y
            face(V(i, ny, k + 1), V(i + 1, ny, k + 1), V(i + 1, ny, k), V(i, ny, k))  # +y
    for j in range(ny):
        for k in range(nz):
            face(V(0, j, k + 1), V(0, j + 1, k + 1), V(0, j + 1, k), V(0, j, k))  # -x
            face(V(nx, j, k), V(nx, j + 1, k), V(nx, j + 1, k + 1), V(nx, j, k + 1))  # +x
    bm.normal_update()
    return bm


def graded(n_edge, n_mid, h, r):
    """Not used: placeholder for graded spacing."""
    return None


def rounded_box_bm(sx, sy, sz, r, nx, ny, nz, rz=None):
    """Rounded box (full size sx,sy,sz) centred at origin; r edge radius.
    Vertices are redistributed so the rounded bands get enough loops."""
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    bm = surface_grid_box(1, 1, 1, nx, ny, nz)
    rz = r if rz is None else rz

    def remap(t, h, rr, n):
        # t in [-1,1] uniform -> position with ~3 segments inside each rounded band
        band = min(3.0 / n * 2, 0.45)  # fraction of [-1,1] used for band (each side)
        a = abs(t)
        sgn = 1 if t >= 0 else -1
        inner = h - rr
        if a <= 1 - band:
            return sgn * (a / (1 - band)) * inner
        u = (a - (1 - band)) / band
        return sgn * (inner + u * rr)

    for v in bm.verts:
        x = remap(v.co.x, hx, r, nx)
        y = remap(v.co.y, hy, r, ny)
        z = remap(v.co.z, hz, rz, nz)
        ix = max(-(hx - r), min(hx - r, x))
        iy = max(-(hy - r), min(hy - r, y))
        iz = max(-(hz - rz), min(hz - rz, z))
        d = Vector((x - ix, y - iy, (z - iz) * (r / rz if rz else 1)))
        if d.length > 1e-9:
            d = d.normalized() * r
            d.z *= (rz / r)
        v.co = Vector((ix, iy, iz)) + d
    return bm


def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def setup_render(res=800, engine='EEVEE'):
    s = bpy.context.scene
    ok = False
    for e in (['BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'] if engine == 'EEVEE' else ['BLENDER_WORKBENCH']):
        try:
            s.render.engine = e
            ok = True
            break
        except TypeError:
            pass
    s.render.resolution_x = res
    s.render.resolution_y = res
    s.render.film_transparent = False
    try:
        s.view_settings.view_transform = 'AgX'
    except Exception:
        pass
    w = bpy.data.worlds.new("W")
    s.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs['Color'].default_value = (0.9, 0.9, 0.9, 1)
    bg.inputs['Strength'].default_value = 0.55
    try:
        s.eevee.taa_render_samples = 32
        s.eevee.use_shadows = True
    except Exception:
        pass
    # floor
    if "preview_floor" not in bpy.data.objects:
        bpy.ops.mesh.primitive_plane_add(size=20)
        f = bpy.context.active_object
        f.name = "preview_floor"
        f.data.materials.append(mat("preview floor", (235, 235, 235), 0.8))
    return s


def preview(key, cam_loc, target, lens=50, wall=False, out=None, sun_rot=(50, 10, 30), extra_lights=True,
            ortho_scale=None):
    for n in ("preview_cam", "preview_sun", "preview_fill"):
        if n in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[n], do_unlink=True)
    s = setup_render()
    if wall:
        f = bpy.data.objects["preview_floor"]
        f.rotation_euler = (math.radians(90), 0, 0)
        f.location = (0, 0.0005, 0)
    cam_d = bpy.data.cameras.new("cam")
    cam_d.lens = lens
    if ortho_scale:
        cam_d.type = 'ORTHO'
        cam_d.ortho_scale = ortho_scale
    cam = bpy.data.objects.new("preview_cam", cam_d)
    s.collection.objects.link(cam)
    cam.location = cam_loc
    look_at(cam, target)
    s.camera = cam
    sd = bpy.data.lights.new("sun", 'SUN')
    sd.energy = 2.2
    sd.angle = math.radians(8)
    sun = bpy.data.objects.new("preview_sun", sd)
    s.collection.objects.link(sun)
    sun.rotation_euler = [math.radians(a) for a in sun_rot]
    if extra_lights:
        ad = bpy.data.lights.new("fill", 'AREA')
        ad.energy = 300
        ad.size = 3
        fl = bpy.data.objects.new("preview_fill", ad)
        s.collection.objects.link(fl)
        fl.location = (cam_loc[0] * 0.6 - 1.5, cam_loc[1] * 0.8, cam_loc[2] + 1.5)
        look_at(fl, target)
    s.render.filepath = out or os.path.join(ASSETS, "previews", key + ".png")
    bpy.ops.render.render(write_still=True)


def cleanup_preview():
    for n in list(bpy.data.objects):
        if n.name.startswith("preview_"):
            bpy.data.objects.remove(n, do_unlink=True)
    for c in list(bpy.data.cameras):
        bpy.data.cameras.remove(c)
    for l in list(bpy.data.lights):
        bpy.data.lights.remove(l)
    m = bpy.data.materials.get("preview floor")
    if m:
        bpy.data.materials.remove(m)
    for me in list(bpy.data.meshes):
        if me.users == 0:
            bpy.data.meshes.remove(me)


def stats(key):
    dg = bpy.context.evaluated_depsgraph_get()
    mn = Vector((1e9,) * 3)
    mx = Vector((-1e9,) * 3)
    tris = 0
    for ob in bpy.data.objects:
        if ob.type != 'MESH' or ob.name.startswith("preview_"):
            continue
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        me.calc_loop_triangles()
        tris += len(me.loop_triangles)
        for v in me.vertices:
            w = ev.matrix_world @ v.co
            mn = Vector(map(min, mn, w))
            mx = Vector(map(max, mx, w))
        ev.to_mesh_clear()
    print("STATS %s bbox min %s max %s size %s tris %d" % (
        key, tuple(round(a, 4) for a in mn), tuple(round(a, 4) for a in mx),
        tuple(round(a, 4) for a in (mx - mn)), tris))
    return mn, mx, tris


def save(key):
    bpy.ops.file.pack_all()
    p = os.path.join(ASSETS, key + ".blend")
    bpy.ops.wm.save_as_mainfile(filepath=p, compress=True)
    print("SAVED", p)
