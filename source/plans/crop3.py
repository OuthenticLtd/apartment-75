import sys
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
# usage: crop3.py name x0 y0 x1 y1 (page mm, origin bottom-left) out
n,x0,y0,x1,y1,out=sys.argv[1],*map(float,sys.argv[2:6]),sys.argv[6]
im=Image.open(rf'prev\{n}_hi.png'); W,H=im.size; k=W/420
c=im.crop((int(x0*k),int(H-y1*k),int(x1*k),int(H-y0*k)))
c.thumbnail((2000,2000)); c.save(out)
