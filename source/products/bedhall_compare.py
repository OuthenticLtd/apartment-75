import sys
from PIL import Image
out = sys.argv[1]; files = sys.argv[2:]
S = 450
ims = []
for f in files:
    im = Image.open(f).convert('RGB'); im.thumbnail((S, S)); ims.append(im)
sheet = Image.new('RGB', (S*len(ims), S), 'white')
for i, im in enumerate(ims): sheet.paste(im, (i*S, 0))
sheet.save(out)
