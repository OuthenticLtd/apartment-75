import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import plib, bmesh
bm=plib.rounded_box_bm(0.98,0.71,0.115,0.032,64,44,5)
hz=0.0575
zs=sorted(set(round(v.co.z,6) for v in bm.verts))
print("DBG",zs[:8], len(bm.faces))
flat=[f for f in bm.faces if all(v.co.z < -hz+1e-6 for v in f.verts)]
print("DBG flat",len(flat))
