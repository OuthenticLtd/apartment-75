# Click a cabinet door/drawer in the 3D viewport to open/close it.
# Sidebar (N) > "Cabinets": Click mode on/off, Open all, Close all.
# Clicks that don't hit a cabinet pass through to Blender as usual. Everything closes before saving.
import bpy, time
from bpy_extras import view3d_utils
from bpy.app.handlers import persistent

DUR = 0.35
_anims = {}   # pivot name -> (t0, start, target)

def _pivots():
    return [o for o in bpy.data.objects if o.name.startswith("CAB_") and "cab_kind" in o]

def _value(p):
    a = p["cab_axis"]
    return p.rotation_euler[a] if p["cab_kind"] == "rot" else p.location[a]

def _set(p, v):
    a = p["cab_axis"]
    if p["cab_kind"] == "rot": p.rotation_euler[a] = v
    else: p.location[a] = v

def _closed_value(p):
    if "cab_closed" not in p: p["cab_closed"] = _value(p)
    return p["cab_closed"]

def toggle(p, state=None):
    c = _closed_value(p)
    want = (not p.get("cab_open", 0)) if state is None else state
    p["cab_open"] = 1 if want else 0
    target = c + p["cab_amount"] if want else c
    _anims[p.name] = (time.perf_counter(), _value(p), target)
    if not bpy.app.timers.is_registered(_tick): bpy.app.timers.register(_tick, first_interval=0.0)

def _tick():
    now = time.perf_counter(); done = []
    for n, (t0, a, b) in list(_anims.items()):
        p = bpy.data.objects.get(n)
        if p is None: done.append(n); continue
        k = min(1.0, (now - t0) / DUR); k = k * k * (3 - 2 * k)
        _set(p, a + (b - a) * k)
        if k >= 1.0: done.append(n)
    for n in done: _anims.pop(n, None)
    for w in bpy.context.window_manager.windows:
        for ar in w.screen.areas:
            if ar.type == 'VIEW_3D': ar.tag_redraw()
    return None if not _anims else 0.016

def _pivot_of(obj):
    o = obj
    while o is not None:
        if o.get("cab_pivot") and o["cab_pivot"] in bpy.data.objects: return bpy.data.objects[o["cab_pivot"]]
        if o.name.startswith("CAB_") and "cab_kind" in o: return o
        o = o.parent
    return None

class CAB_OT_click(bpy.types.Operator):
    bl_idname = "view3d.cabinet_click"
    bl_label = "Cabinet click mode"
    _running = False

    def modal(self, context, event):
        if not context.window_manager.cab_click_on:
            CAB_OT_click._running = False
            return {'FINISHED'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS' and not (event.shift or event.ctrl or event.alt):
            area = None
            for a in context.window.screen.areas:
                if a.type == 'VIEW_3D' and a.x <= event.mouse_x < a.x + a.width and a.y <= event.mouse_y < a.y + a.height:
                    area = a; break
            if area is None: return {'PASS_THROUGH'}
            region = next((r for r in area.regions if r.type == 'WINDOW' and r.x <= event.mouse_x < r.x + r.width and r.y <= event.mouse_y < r.y + r.height), None)
            if region is None: return {'PASS_THROUGH'}
            rv3d = area.spaces.active.region_3d
            co = (event.mouse_x - region.x, event.mouse_y - region.y)
            origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, co)
            direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, co)
            dg = context.evaluated_depsgraph_get()
            hit, loc, nrm, idx, obj, mtx = context.scene.ray_cast(dg, origin, direction)
            if hit and obj is not None:
                p = _pivot_of(bpy.data.objects.get(obj.name) or obj)
                if p is not None:
                    toggle(p); return {'RUNNING_MODAL'}
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if CAB_OT_click._running: return {'CANCELLED'}
        CAB_OT_click._running = True
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

class CAB_OT_all(bpy.types.Operator):
    bl_idname = "view3d.cabinet_all"
    bl_label = "Open / close all cabinets"
    open: bpy.props.BoolProperty(default=True)
    def execute(self, context):
        for p in _pivots(): toggle(p, self.open)
        return {'FINISHED'}

def _start(context=None):
    wm = bpy.context.window_manager
    for w in wm.windows:
        for a in w.screen.areas:
            if a.type == 'VIEW_3D':
                r = next(r for r in a.regions if r.type == 'WINDOW')
                with bpy.context.temp_override(window=w, area=a, region=r):
                    bpy.ops.view3d.cabinet_click('INVOKE_DEFAULT')
                return None
    return 1.0   # no 3D view yet - try again

def _on_toggle(self, context):
    if self.cab_click_on and not CAB_OT_click._running: bpy.app.timers.register(_start, first_interval=0.05)

class CAB_PT_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'; bl_region_type = 'UI'; bl_category = "Cabinets"; bl_label = "Cabinets"
    def draw(self, context):
        wm = context.window_manager; col = self.layout.column(align=True)
        col.prop(wm, "cab_click_on", text="Click to open/close", toggle=True, icon='HAND')
        row = col.row(align=True)
        row.operator("view3d.cabinet_all", text="Open all").open = True
        row.operator("view3d.cabinet_all", text="Close all").open = False
        self.layout.label(text="Left-click a door or drawer")

@persistent
def _close_before_save(*_):
    for p in _pivots():
        if p.get("cab_open"): _set(p, _closed_value(p)); p["cab_open"] = 0
    _anims.clear()

@persistent
def _on_load(*_):
    for p in _pivots():
        _closed_value(p)
    CAB_OT_click._running = False
    if bpy.context.window_manager.cab_click_on: bpy.app.timers.register(_start, first_interval=1.0)

classes = (CAB_OT_click, CAB_OT_all, CAB_PT_panel)
def register():
    for c in classes:
        try: bpy.utils.register_class(c)
        except ValueError:
            bpy.utils.unregister_class(getattr(bpy.types, c.__name__)); bpy.utils.register_class(c)
    bpy.types.WindowManager.cab_click_on = bpy.props.BoolProperty(name="Cabinet click mode", default=True, update=_on_toggle)
    for h, f in ((bpy.app.handlers.save_pre, _close_before_save), (bpy.app.handlers.load_post, _on_load)):
        for old in [x for x in h if getattr(x, "__name__", "") == f.__name__]: h.remove(old)
        h.append(f)
    for p in _pivots(): _closed_value(p)
    bpy.app.timers.register(_start, first_interval=0.5)

register()
