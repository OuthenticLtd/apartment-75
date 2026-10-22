import sys
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
src, out, x0, y0, x1, y1 = sys.argv[1], sys.argv[2], *map(float, sys.argv[3:7])
im = Image.open(src); W, H = im.size
s = W / 420.0
im.crop((int(x0*s), int(H - y1*s), int(x1*s), int(H - y0*s))).save(out)
