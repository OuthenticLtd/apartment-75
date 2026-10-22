import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bedhall_common as C
C.reset("mirror_ozze")
R = 0.30; D = 0.02
frame = C.mat("frame", C.hexcol("1e1c1b"), rough=0.55)
glass = C.mat("mirror", (0.82, 0.84, 0.85), rough=0.03, metal=1.0)
back = C.mat("back", C.hexcol("3a332c"), rough=0.9)
# frame profile (r, depth toward front)
prof = [(R-0.012, 0.0), (R-0.002, 0.0), (R, 0.002), (R, D-0.003), (R-0.0015, D-0.0003), (R-0.003, D),
        (R-0.0085, D), (R-0.0095, D-0.001), (R-0.0095, 0.012), (R-0.012, 0.012), (R-0.012, 0.0)]
f = C.lathe("frame", prof, frame, segs=96)
f.location = (0, 0, R); f.rotation_euler = (math.radians(90), 0, 0)
g = C.cyl("glass", R-0.0095, 0.004, (0, -0.014, R), glass, verts=96, rot=(math.radians(90), 0, 0))
b = C.cyl("backing", R-0.012, 0.003, (0, -0.0035, R), back, verts=48, rot=(math.radians(90), 0, 0))
# hanging hook bracket on back
C.box("hanger", (0.04, 0.002, 0.012), (0, -0.0011, 2*R-0.06), C.mat("hanger", (0.6, 0.6, 0.6), 0.4, 1.0))
C.preview(wall=True, floor=False, azim=-30, elev=12)
C.save()
