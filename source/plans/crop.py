import sys
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
f,x0,y0,x1,y1=sys.argv[1],*map(float,sys.argv[2:6])
out=sys.argv[6]; sc=float(sys.argv[7]) if len(sys.argv)>7 else 1.0
im=Image.open(f'prev/{f}_hi.png'); k=300/25.4
c=im.crop((int(x0*k),int((297-y1)*k),int(x1*k),int((297-y0)*k)))
if sc!=1: c=c.resize((int(c.width*sc),int(c.height*sc)),Image.LANCZOS)
c.save(out); print(c.size)
