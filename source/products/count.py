import bpy
dg=bpy.context.evaluated_depsgraph_get()
for ob in bpy.data.objects:
    if ob.type!='MESH': continue
    me=ob.evaluated_get(dg).to_mesh(); me.calc_loop_triangles()
    print("CNT",ob.name,len(me.loop_triangles), len(ob.data.polygons))
