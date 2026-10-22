# Shared helpers for the "bathclimate" product group (Blender 5.2, headless).
import bpy, bmesh, math, os, json
from mathutils import Vector, Matrix

ASSETS = r"C:\Users\vasil\AppData\Local\Temp\claude\C--Users-vasil\6a4d89ac-a284-4cf7-80fb-7d2d8a72f875\scratchpad\assets"
META_DIR = os.path.join(ASSETS, "scripts", "bc_tools", "meta")

_ROOT = None
_KEY = None
_MATS = {}


def reset(key):
    global _ROOT, _KEY, _MATS
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _KEY = key
    _MATS = {}
    _ROOT = bpy.data.objects.new("PROD_" + key, None)
    _ROOT.empty_display_type = 'PLAIN_AXES'
    _ROOT.empty_display_size = 0.1
    bpy.context.scene.collection.objects.link(_ROOT)
    return _ROOT


def mat(part, color, rough=0.5, metal=0.0, alpha=1.0, transmission=0.0,
        emission=None, estr=0.0, ior=1.5, coat=0.0):
    name = f"{_KEY} {part}"
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    col = tuple(color) + (1.0,) if len(color) == 3 else tuple(color)
    p.inputs["Base Color"].default_value = col
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["IOR"].default_value = ior
    if coat:
        p.inputs["Coat Weight"].default_value = coat
    if transmission:
        p.inputs["Transmission Weight"].default_value = transmission
    if alpha < 1.0:
        p.inputs["Alpha"].default_value = alpha
        try:
            m.surface_render_method = 'BLENDED'
        except Exception:
            pass
        try:
            m.use_transparency_overlap = True
        except Exception:
            pass
    if emission is not None:
        p.inputs["Emission Color"].default_value = tuple(emission) + (1.0,)
        p.inputs["Emission Strength"].default_value = estr
    m.diffuse_color = (col[0], col[1], col[2], alpha)
    m.roughness = rough
    m.metallic = metal
    _MATS[name] = m
    return m


def _link(name, me, material, smooth=True):
    full = f"{_KEY}_{name}"
    me.name = full
    ob = bpy.data.objects.new(full, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.parent = _ROOT
    if material is not None:
        if isinstance(material, (list, tuple)):
            for mm in material:
                me.materials.append(mm)
        else:
            me.materials.append(material)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    return ob


def from_bm(name, bm, material, smooth=True, autosmooth=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = _link(name, me, material, smooth)
    if autosmooth is not None:
        smooth_by_angle(ob, autosmooth)
    return ob


def smooth_by_angle(ob, deg=35):
    me = ob.data
    for p in me.polygons:
        p.use_smooth = True
    # mark sharp edges by angle
    bm = bmesh.new(); bm.from_mesh(me)
    for e in bm.edges:
        if len(e.link_faces) == 2:
            a = e.link_faces[0].normal.angle(e.link_faces[1].normal, 0)
            e.smooth = a < math.radians(deg)
        else:
            e.smooth = False
    bm.to_mesh(me); bm.free()


def bevel(ob, width, segs=3, limit='ANGLE', angle=40, harden=True):
    md = ob.modifiers.new("Bevel", 'BEVEL')
    md.width = width
    md.segments = segs
    md.limit_method = limit
    if limit == 'ANGLE':
        md.angle_limit = math.radians(angle)
    md.harden_normals = False
    try:
        md.miter_outer = 'MITER_ARC'
    except Exception:
        pass
    return md


def subsurf(ob, levels=1):
    md = ob.modifiers.new("Subd", 'SUBSURF')
    md.levels = levels
    md.render_levels = levels
    return md


def box(name, size, loc, material, bev=0.0, segs=3, rot=None, smooth=False):
    """size=(sx,sy,sz) centred at loc."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if rot is not None:
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rot[1], 3, rot[0]), verts=bm.verts)
    bmesh.ops.translate(bm, vec=Vector(loc), verts=bm.verts)
    ob = from_bm(name, bm, material, smooth=smooth)
    if bev > 0:
        bevel(ob, bev, segs)
        smooth_shade_flat_fix(ob)
    return ob


def smooth_shade_flat_fix(ob):
    # bevelled boxes: smooth shading with sharp marks so flat faces stay flat
    for p in ob.data.polygons:
        p.use_smooth = True
    try:
        md = ob.modifiers.new("WN", 'WEIGHTED_NORMAL')
        md.keep_sharp = True
    except Exception:
        pass


def cyl(name, r, depth, loc, material, axis='Z', verts=32, r2=None, bev=0.0, segs=2, smooth=True, cap=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=verts,
                          radius1=r, radius2=(r if r2 is None else r2), depth=depth)
    if axis == 'X':
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, 'Y'), verts=bm.verts)
    elif axis == 'Y':
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, 'X'), verts=bm.verts)
    bmesh.ops.translate(bm, vec=Vector(loc), verts=bm.verts)
    ob = from_bm(name, bm, material, smooth=smooth)
    if bev > 0:
        bevel(ob, bev, segs)
        smooth_by_angle(ob, 50)
    elif smooth:
        smooth_by_angle(ob, 50)
    return ob


def sphere(name, r, loc, material, segs=24, rings=12, scale=(1, 1, 1)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=r)
    bmesh.ops.scale(bm, vec=Vector(scale), verts=bm.verts)
    bmesh.ops.translate(bm, vec=Vector(loc), verts=bm.verts)
    return from_bm(name, bm, material)


def fillet(points, radius, n=8):
    """Round the inner corners of a 3D polyline with arcs of given radius."""
    pts = [Vector(p) for p in points]
    if len(pts) < 3 or radius <= 0:
        return pts
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        p0, p1, p2 = pts[i - 1], pts[i], pts[i + 1]
        d1 = (p0 - p1).normalized(); d2 = (p2 - p1).normalized()
        ang = d1.angle(d2, math.pi)
        if ang > math.pi - 1e-3:
            out.append(p1); continue
        t = radius / math.tan(ang / 2)
        t = min(t, (p0 - p1).length * 0.49 if i > 1 else (p0 - p1).length * 0.98,
                (p2 - p1).length * 0.49 if i < len(pts) - 2 else (p2 - p1).length * 0.98)
        a = p1 + d1 * t; b = p1 + d2 * t
        bis = (d1 + d2).normalized()
        rr = t * math.tan(ang / 2)
        c = p1 + bis * (rr / math.sin(ang / 2))
        va = a - c; vb = b - c
        for k in range(n + 1):
            f = k / n
            # slerp between va and vb
            om = va.angle(vb, 0)
            if om < 1e-6:
                v = va
            else:
                v = (math.sin((1 - f) * om) * va + math.sin(f * om) * vb) / math.sin(om)
            out.append(c + v)
    out.append(pts[-1])
    return out


def tube(name, points, radius, material, res=12, caps=True, smooth=True, closed=False):
    """Sweep a circle along a polyline (already filleted)."""
    pts = [Vector(p) for p in points]
    bm = bmesh.new()
    rings = []
    n = len(pts)
    prev_side = None
    for i, p in enumerate(pts):
        if closed:
            t = (pts[(i + 1) % n] - pts[i - 1]).normalized()
        elif i == 0:
            t = (pts[1] - pts[0]).normalized()
        elif i == n - 1:
            t = (pts[-1] - pts[-2]).normalized()
        else:
            t = ((pts[i] - pts[i - 1]).normalized() + (pts[i + 1] - pts[i]).normalized()).normalized()
        if prev_side is None:
            up = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
            side = t.cross(up).normalized()
        else:
            side = (prev_side - t * prev_side.dot(t)).normalized()
        prev_side = side
        up2 = side.cross(t).normalized()
        # miter scale
        sc = 1.0
        if 0 < i < n - 1:
            d = (pts[i + 1] - pts[i]).normalized()
            cosh = max(0.3, t.dot(d))
            sc = 1.0 / cosh
        ring = []
        for k in range(res):
            a = 2 * math.pi * k / res
            off = side * math.cos(a) * radius + up2 * math.sin(a) * radius
            # stretch along miter
            ring.append(bm.verts.new(p + off * 1.0))
        rings.append(ring)
    for i in range(len(rings) - (0 if closed else 1)):
        r1 = rings[i]; r2 = rings[(i + 1) % len(rings)]
        for k in range(res):
            bm.faces.new((r1[k], r1[(k + 1) % res], r2[(k + 1) % res], r2[k]))
    if caps and not closed:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = from_bm(name, bm, material, smooth=smooth)
    if caps:
        smooth_by_angle(ob, 60)
    return ob


def plane_matrix(plane):
    # maps (u, v, w) -> world xyz
    if plane == 'XY':
        return lambda u, v, w: Vector((u, v, w))
    if plane == 'XZ':   # extrude toward -Y for positive w
        return lambda u, v, w: Vector((u, -w, v))
    if plane == 'YZ':
        return lambda u, v, w: Vector((w, u, v))
    raise ValueError(plane)


def prism(name, outline, depth, material, plane='XZ', w0=0.0, bev=0.0, segs=3, smooth_angle=40):
    """Extrude a 2D outline (list of (u,v), CCW) by depth along the plane normal starting at w0."""
    f = plane_matrix(plane)
    bm = bmesh.new()
    a = [bm.verts.new(f(u, v, w0)) for (u, v) in outline]
    b = [bm.verts.new(f(u, v, w0 + depth)) for (u, v) in outline]
    n = len(outline)
    bm.faces.new(a)
    bm.faces.new(list(reversed(b)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], b[i], b[j], a[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = from_bm(name, bm, material)
    smooth_by_angle(ob, smooth_angle)
    if bev > 0:
        bevel(ob, bev, segs)
    return ob


def rrect(w, h, r, n=6, cx=0.0, cy=0.0, radii=None):
    """Rounded rectangle outline CCW (u,v). radii per corner (bl, br, tr, tl)."""
    if radii is None:
        radii = (r, r, r, r)
    pts = []
    corners = [(cx - w / 2, cy - h / 2, math.pi, 1.5 * math.pi, radii[0]),
               (cx + w / 2, cy - h / 2, 1.5 * math.pi, 2 * math.pi, radii[1]),
               (cx + w / 2, cy + h / 2, 0, 0.5 * math.pi, radii[2]),
               (cx - w / 2, cy + h / 2, 0.5 * math.pi, math.pi, radii[3])]
    for (x, y, a0, a1, rr) in corners:
        sx = -1 if x < cx else 1
        sy = -1 if y < cy else 1
        ccx = x - sx * rr; ccy = y - sy * rr
        if rr <= 0:
            pts.append((x, y)); continue
        for k in range(n + 1):
            a = a0 + (a1 - a0) * k / n
            pts.append((ccx + rr * math.cos(a), ccy + rr * math.sin(a)))
    return pts


def circle_pts(r, n=32, cx=0.0, cy=0.0):
    return [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def lathe(name, profile, material, loc=(0, 0, 0), segs=32, axis='Z', smooth=True):
    """profile = list of (r, h) from bottom to top; revolve around axis."""
    bm = bmesh.new()
    rings = []
    for (r, h) in profile:
        ring = []
        for k in range(segs):
            a = 2 * math.pi * k / segs
            if axis == 'Z':
                v = Vector((r * math.cos(a), r * math.sin(a), h))
            elif axis == 'Y':
                v = Vector((r * math.cos(a), h, r * math.sin(a)))
            else:
                v = Vector((h, r * math.cos(a), r * math.sin(a)))
            ring.append(bm.verts.new(v + Vector(loc)))
        rings.append(ring)
    for i in range(len(rings) - 1):
        for k in range(segs):
            bm.faces.new((rings[i][k], rings[i][(k + 1) % segs], rings[i + 1][(k + 1) % segs], rings[i + 1][k]))
    if profile[0][0] > 1e-6:
        bm.faces.new(list(reversed(rings[0])))
    if profile[-1][0] > 1e-6:
        bm.faces.new(rings[-1])
    bmesh.remove_doubles if False else None
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = from_bm(name, bm, material, smooth=smooth)
    smooth_by_angle(ob, 50)
    return ob


def loft(name, rings, material, cap_bottom=True, cap_top=True, smooth=True):
    """rings: list of lists of Vector with equal count (closed loops)."""
    bm = bmesh.new()
    R = [[bm.verts.new(Vector(p)) for p in ring] for ring in rings]
    n = len(rings[0])
    for i in range(len(R) - 1):
        for k in range(n):
            bm.faces.new((R[i][k], R[i][(k + 1) % n], R[i + 1][(k + 1) % n], R[i + 1][k]))
    if cap_bottom:
        bm.faces.new(list(reversed(R[0])))
    if cap_top:
        bm.faces.new(R[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return from_bm(name, bm, material, smooth=smooth)


def resample(pts2, n, closed=True):
    """Resample a polyline of (x,y) to n points evenly by arc length."""
    P = [Vector((p[0], p[1])) for p in pts2]
    if closed:
        P = P + [P[0]]
    L = [0.0]
    for i in range(1, len(P)):
        L.append(L[-1] + (P[i] - P[i - 1]).length)
    tot = L[-1]
    out = []
    cnt = n if closed else n - 1
    j = 0
    for k in range(n):
        s = tot * k / cnt
        while j < len(L) - 2 and L[j + 1] < s:
            j += 1
        seg = L[j + 1] - L[j]
        f = 0 if seg < 1e-12 else (s - L[j]) / seg
        q = P[j].lerp(P[j + 1], f)
        out.append((q.x, q.y))
    return out


def apply_all_modifiers():
    dg = bpy.context.evaluated_depsgraph_get()
    for ob in list(bpy.data.objects):
        if ob.type != 'MESH' or not ob.modifiers:
            continue
        ev = ob.evaluated_get(dg)
        me = bpy.data.meshes.new_from_object(ev)
        old = ob.data
        ob.modifiers.clear()
        ob.data = me
        me.name = old.name
        bpy.data.meshes.remove(old)


def stats():
    dg = bpy.context.evaluated_depsgraph_get()
    mn = Vector((1e9, 1e9, 1e9)); mx = Vector((-1e9, -1e9, -1e9))
    tris = 0
    for ob in bpy.data.objects:
        if ob.type != 'MESH':
            continue
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        me.calc_loop_triangles()
        tris += len(me.loop_triangles)
        M = ob.matrix_world
        for v in me.vertices:
            w = M @ v.co
            mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
        ev.to_mesh_clear()
    return mn, mx, tris


def render_preview(key, view=(0.75, -1.0, 0.5), ortho=False, lens=60, margin=1.15, extra_name=""):
    sc = bpy.context.scene
    mn, mx, tris = stats()
    c = (mn + mx) / 2
    size = (mx - mn)
    rad = 0.5 * size.length
    cam_d = Vector(view).normalized()
    cd = bpy.data.cameras.new("PreviewCam")
    cd.lens = lens
    cam = bpy.data.objects.new("PreviewCam", cd)
    sc.collection.objects.link(cam)
    fov = 2 * math.atan(36 / (2 * lens))
    dist = rad * margin / math.sin(fov / 2)
    cam.location = c + cam_d * dist
    cam.rotation_euler = (-cam_d).to_track_quat('-Z', 'Y').to_euler()
    cd.clip_start = 0.01; cd.clip_end = dist * 4
    sc.camera = cam
    # lights
    ld = bpy.data.lights.new("PrevKey", 'AREA'); ld.energy = 30 * dist ** 2; ld.size = max(0.3, rad * 1.5)
    lo = bpy.data.objects.new("PrevKey", ld); sc.collection.objects.link(lo)
    kd = Vector((-0.6, -1.0, 1.1)).normalized()
    lo.location = c + kd * dist; lo.rotation_euler = (-kd).to_track_quat('-Z', 'Y').to_euler()
    ld2 = bpy.data.lights.new("PrevFill", 'AREA'); ld2.energy = 10 * dist ** 2; ld2.size = max(0.3, rad * 1.5)
    lo2 = bpy.data.objects.new("PrevFill", ld2); sc.collection.objects.link(lo2)
    kd2 = Vector((1.0, -0.6, 0.4)).normalized()
    lo2.location = c + kd2 * dist; lo2.rotation_euler = (-kd2).to_track_quat('-Z', 'Y').to_euler()
    world = bpy.data.worlds.new("PrevWorld")
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs[0].default_value = (0.82, 0.83, 0.85, 1)
    bg.inputs[1].default_value = 0.4
    sc.world = world
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        pass
    sc.render.resolution_x = 800; sc.render.resolution_y = 800
    sc.render.film_transparent = False
    try:
        sc.view_settings.view_transform = 'AgX'
    except Exception:
        pass
    try:
        sc.eevee.taa_render_samples = 32
    except Exception:
        pass
    os.makedirs(os.path.join(ASSETS, "previews"), exist_ok=True)
    out = os.path.join(ASSETS, "previews", f"{key}{extra_name}.png")
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
    # clean preview helpers
    for o in (cam, lo, lo2):
        bpy.data.objects.remove(o)
    bpy.data.cameras.remove(cd); bpy.data.lights.remove(ld); bpy.data.lights.remove(ld2)
    sc.world = None
    bpy.data.worlds.remove(world)
    return out


def finish(key, product, dims, mount, notes, views=None, apply=True):
    """Check, save .blend, render preview(s), write meta json."""
    mn, mx, tris = stats()
    size = mx - mn
    print(f"[{key}] bbox min {tuple(round(v,4) for v in mn)} max {tuple(round(v,4) for v in mx)}")
    print(f"[{key}] size {tuple(round(v,4) for v in size)} target {dims} tris {tris}")
    errs = [abs(size[i] - dims[i]) for i in range(3)]
    print(f"[{key}] size error mm: {[round(e*1000,1) for e in errs]}")
    # purge orphan data
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.curves):
        for d in list(coll):
            if d.users == 0:
                coll.remove(d)
    bpy.context.scene.cursor.location = (0, 0, 0)
    blend = os.path.join(ASSETS, f"{key}.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True)
    outs = []
    views = views or [((0.75, -1.0, 0.5), "")]
    for v, suffix in views:
        outs.append(render_preview(key, view=v, extra_name=suffix))
    # re-save without preview junk (render_preview cleans up itself)
    bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True)
    os.makedirs(META_DIR, exist_ok=True)
    meta = {"key": key, "file": f"assets/{key}.blend", "product": product,
            "dims_m": [round(d, 4) for d in dims], "mount": mount, "notes": notes,
            "_measured": [round(s, 4) for s in size], "_tris": tris}
    with open(os.path.join(META_DIR, f"{key}.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=1)
    print(f"[{key}] saved {blend} previews {outs}")


def translate_all(vec):
    from mathutils import Matrix
    M = Matrix.Translation(Vector(vec))
    for ob in bpy.data.objects:
        if ob.type == 'MESH':
            ob.data.transform(M)


def recenter(mode='floor'):
    """floor: footprint centre at origin, min z = 0. wall: back face (max y) at y=0, centre x, min z=0."""
    mn, mx, _ = stats()
    if mode == 'floor':
        translate_all((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))
    else:
        translate_all((-(mn.x + mx.x) / 2, -mx.y, -mn.z))
