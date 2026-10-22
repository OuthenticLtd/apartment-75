import sys, glob, os, math
from PIL import Image, ImageDraw
refs, out, prefix = sys.argv[1], sys.argv[2], sys.argv[3]
files = sorted(glob.glob(os.path.join(refs, prefix + '_*.jpg')), key=lambda f: int(''.join(c for c in os.path.basename(f).split('_')[-1] if c.isdigit()) or 0))
n = len(files); cols = 4 if n > 4 else n; rows = math.ceil(n / cols); S = 300
sheet = Image.new('RGB', (cols*S, rows*S), 'white'); d = ImageDraw.Draw(sheet)
for i, f in enumerate(files):
    im = Image.open(f).convert('RGB'); im.thumbnail((S, S))
    x, y = (i % cols)*S, (i//cols)*S
    sheet.paste(im, (x, y)); d.text((x+4, y+4), os.path.basename(f), fill='red')
sheet.save(out)
