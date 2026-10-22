"""Shared helpers for the 'dining' group product scripts (Blender 5.2, headless)."""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix

ASSETS = r"C:\Users\vasil\AppData\Local\Temp\claude\C--Users-vasil\6a4d89ac-a284-4cf7-80fb-7d2d8a72f875\scratchpad\assets"


def srgb(c):
    """0-255 sRGB triple -> linear RGBA."""
    out = []
    for v in c:
        v = v / 255.0
        out.append(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4)
    return (*out, 1.0)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def root(key):
    e = bpy.data.objects.new(f"PROD_{key}", None)
    e.empty_display_type = 'PLAIN_AXES'
    e.empty_display_size = 0.2
    bpy.context.scene.collection.objects.link(e)
    return e


def mat(name, rgb255=None, rough=0.5, metal=0.0, lin=None, image=None, sheen=0.0, emission=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    col = lin if lin is not None else srgb(rgb255)
    b.inputs["Base Color"].default_value = col
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emission is not None:
        b.inputs["Emission Color"].default_value = emission[0]
        b.inputs["Emission Strength"].default_value = emission[1]
    if image is not None:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = image
        nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    m.diffuse_color = col
    return m


def obj_from_bm(bm, name, parent, material=None, smooth=False):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    o.parent = parent
    if material is not None:
        me.materials.append(material)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    return o


def box(name, parent, size, loc, material=None, bevel=0.0, segs=2, rot=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if rot is not None:
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rot[1], 3, rot[0]), verts=bm.verts)
    bmesh.ops.translate(bm, vec=Vector(loc), verts=bm.verts)
    o = obj_from_bm(bm, name, parent, material)
    if bevel > 0:
        add_bevel(o, bevel, segs)
    return o


def add_bevel(o, width, segs=2, angle=None):
    m = o.modifiers.new("Bevel", 'BEVEL')
    m.width = width
    m.segments = segs
    m.limit_method = 'ANGLE'
    m.angle_limit = math.radians(angle if angle else 30)
    m.harden_normals = False
    return m


def cyl_between(name, parent, p1, p2, r1, r2=None, material=None, verts=16, caps=True):
    """Tapered cylinder (cone) from p1 (radius r1) to p2 (radius r2)."""
    r2 = r1 if r2 is None else r2
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    L = d.length
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=verts, radius1=r1, radius2=r2, depth=L)
    bmesh.ops.translate(bm, vec=Vector((0, 0, L / 2)), verts=bm.verts)
    q = Vector((0, 0, 1)).rotation_difference(d.normalized())
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=q.to_matrix(), verts=bm.verts)
    bmesh.ops.translate(bm, vec=p1, verts=bm.verts)
    o = obj_from_bm(bm, name, parent, material)
    smooth_by_angle(o, 40)
    return o


def shade_smooth_auto(o, angle=35):
    for p in o.data.polygons:
        p.use_smooth = True
    try:
        m = o.modifiers.new("Smooth", 'SMOOTH_BY_ANGLE')
    except Exception:
        m = None
    if m is None:
        try:
            with bpy.context.temp_override(object=o, active_object=o, selected_objects=[o], selected_editable_objects=[o]):
                bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angle))
        except Exception as ex:
            print("smooth by angle failed", ex)


def smooth_by_angle(o, angle=35):
    """Mark sharp edges by angle and use smooth shading (export-safe)."""
    me = o.data
    bm = bmesh.new()
    bm.from_mesh(me)
    for e in bm.edges:
        if len(e.link_faces) == 2:
            a = e.link_faces[0].normal.angle(e.link_faces[1].normal, 0)
            e.smooth = a < math.radians(angle)
        else:
            e.smooth = True
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(me)
    bm.free()


def stats(root_obj):
    """Return evaluated world bbox (min,max) and triangle count of all child meshes."""
    dg = bpy.context.evaluated_depsgraph_get()
    mn = Vector((1e9,) * 3)
    mx = Vector((-1e9,) * 3)
    tris = 0
    for o in bpy.data.objects:
        if o.type != 'MESH':
            continue
        oe = o.evaluated_get(dg)
        me = oe.to_mesh()
        me.calc_loop_triangles()
        tris += len(me.loop_triangles)
        for v in me.vertices:
            w = oe.matrix_world @ v.co
            mn = Vector(map(min, mn, w))
            mx = Vector(map(max, mx, w))
        oe.to_mesh_clear()
    return mn, mx, tris


def render_preview(key, target=(0, 0, 0.4), dist=2.6, elev=18, azim=35, lens=50, ortho=None, out=None, res=800, floor=True, wall=False):
    sc = bpy.context.scene
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x = res
    sc.render.resolution_y = res
    sc.render.film_transparent = False
    sc.view_settings.view_transform = 'Standard'
    # world
    w = bpy.data.worlds.new("dining_preview_world")
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs[0].default_value = (0.9, 0.9, 0.9, 1)
    bg.inputs[1].default_value = 0.7
    sc.world = w
    tmp = []
    # light
    ld = bpy.data.lights.new("dining_prev_sun", 'SUN')
    ld.energy = 2.6
    ld.angle = math.radians(20)
    lo = bpy.data.objects.new("dining_prev_sun", ld)
    lo.rotation_euler = (math.radians(40), 0, math.radians(30))
    sc.collection.objects.link(lo)
    tmp += [lo]
    if floor:
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=6)
        fo = obj_from_bm(bm, "dining_prev_floor", None, mat("dining_prev_floor", (235, 235, 235), 0.8))
        tmp.append(fo)
    if wall:
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=6)
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'X'), verts=bm.verts)
        bmesh.ops.translate(bm, vec=(0, 0.001, 0), verts=bm.verts)
        wo = obj_from_bm(bm, "dining_prev_wall", None, mat("dining_prev_wall", (225, 222, 216), 0.9))
        tmp.append(wo)
    cd = bpy.data.cameras.new("dining_prev_cam")
    cd.lens = lens
    if ortho:
        cd.type = 'ORTHO'
        cd.ortho_scale = ortho
    co = bpy.data.objects.new("dining_prev_cam", cd)
    sc.collection.objects.link(co)
    t = Vector(target)
    a, e = math.radians(azim), math.radians(elev)
    # front is -Y; azim measured from -Y toward +X
    co.location = t + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
    co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = co
    tmp.append(co)
    sc.render.filepath = out or os.path.join(ASSETS, "previews", f"{key}.png")
    bpy.ops.render.render(write_still=True)
    # cleanup helpers so they are not saved
    for o in tmp:
        data = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if data is not None:
            if isinstance(data, bpy.types.Mesh):
                for m in list(data.materials):
                    if m and m.name.startswith("dining_prev"):
                        bpy.data.materials.remove(m)
                bpy.data.meshes.remove(data)
            elif isinstance(data, bpy.types.Light):
                bpy.data.lights.remove(data)
            elif isinstance(data, bpy.types.Camera):
                bpy.data.cameras.remove(data)
    sc.world = None
    bpy.data.worlds.remove(w)


def finish(key, root_obj, preview_kwargs=None, extra_views=None):
    mn, mx, tris = stats(root_obj)
    print(f"[{key}] bbox min {tuple(round(v,4) for v in mn)} max {tuple(round(v,4) for v in mx)} size {tuple(round(v,4) for v in (mx-mn))} tris {tris}")
    for o in bpy.data.objects:
        if o.type == 'MESH' and o.parent is None:
            print("WARNING unparented mesh", o.name)
    path = os.path.join(ASSETS, f"{key}.blend")
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=path, compress=True)
    if preview_kwargs is not None:
        render_preview(key, **preview_kwargs)
        for i, kw in enumerate(extra_views or []):
            render_preview(key, out=os.path.join(ASSETS, "previews", f"d_{key}_view{i+1}.png"), **kw)
        # reload saved file state is unchanged (render helpers removed), resave not needed
    return mn, mx, tris


def clip_below(o, z=0.0):
    """Cut a mesh flat at height z (removes everything below, fills the cut)."""
    me = o.data
    bm = bmesh.new()
    bm.from_mesh(me)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    r = bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, 0, z), plane_no=(0, 0, 1), clear_inner=True)
    cut_edges = [e for e in r["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
    if cut_edges:
        f = bmesh.ops.edgenet_fill(bm, edges=cut_edges)
        for face in f["faces"]:
            face.smooth = False
    bm.to_mesh(me)
    bm.free()


def lathe(name, parent, profile, material=None, segs=48, smooth_angle=40, closed=True):
    """Revolve a 2D profile [(r, z), ...] around Z. closed=True treats it as a closed loop."""
    bm = bmesh.new()
    vs = [bm.verts.new((r, 0, z)) for r, z in profile]
    es = [bm.edges.new((vs[i], vs[i + 1])) for i in range(len(vs) - 1)]
    if closed:
        es.append(bm.edges.new((vs[-1], vs[0])))
    bmesh.ops.spin(bm, geom=vs + es, cent=(0, 0, 0), axis=(0, 0, 1), angle=math.radians(360), steps=segs, use_duplicate=False)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = obj_from_bm(bm, name, parent, material)
    smooth_by_angle(o, smooth_angle)
    return o


def sweep_tube(name, parent, pts, radius, material=None, verts=16, caps=True):
    """Round tube along a polyline of points (parallel-transport frames)."""
    pts = [Vector(p) for p in pts]
    bm = bmesh.new()
    rings = []
    prev_n = None
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        if prev_n is None:
            a = Vector((1, 0, 0)) if abs(t.x) < 0.9 else Vector((0, 1, 0))
            n = t.cross(a).normalized()
        else:
            n = (prev_n - t * prev_n.dot(t)).normalized()
        prev_n = n
        b = t.cross(n)
        r = radius(i / (len(pts) - 1)) if callable(radius) else radius
        rings.append([bm.verts.new(p + (n * math.cos(2 * math.pi * k / verts) + b * math.sin(2 * math.pi * k / verts)) * r) for k in range(verts)])
    for A, B in zip(rings[:-1], rings[1:]):
        for k in range(verts):
            bm.faces.new((A[k], A[(k + 1) % verts], B[(k + 1) % verts], B[k]))
    if caps:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = obj_from_bm(bm, name, parent, material)
    smooth_by_angle(o, 50)
    return o
