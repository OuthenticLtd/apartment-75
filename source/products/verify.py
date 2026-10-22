import bpy, os
from mathutils import Vector
key=os.path.basename(bpy.data.filepath)[:-6]
r=bpy.data.objects.get("PROD_"+key)
bad=[o.name for o in bpy.data.objects if o.type=='MESH' and (o.parent!=r or not o.name.startswith(key+"_"))]
other=[o.name for o in bpy.data.objects if o.type not in('MESH',) and o!=r]
dg=bpy.context.evaluated_depsgraph_get(); mn=Vector((1e9,)*3); mx=-mn; t=0
for o in bpy.data.objects:
    if o.type!='MESH': continue
    e=o.evaluated_get(dg); me=e.to_mesh(); me.calc_loop_triangles(); t+=len(me.loop_triangles)
    for v in me.vertices:
        w=e.matrix_world@v.co; mn=Vector(map(min,mn,w)); mx=Vector(map(max,mx,w))
    e.to_mesh_clear()
imgs=[(i.name,tuple(i.size),bool(i.packed_file)) for i in bpy.data.images if i.users]
mats=[m.name for m in bpy.data.materials if m.users and not m.name.startswith(key)]
print("VER",key,"root",r is not None and tuple(r.matrix_world.translation)==(0,0,0),"badparent",bad,"extra",other,"min",tuple(round(a,3) for a in mn),"max",tuple(round(a,3) for a in mx),"tris",t,"imgs",imgs,"badmats",mats)
