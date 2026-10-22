from PIL import Image, ImageDraw, ImageFont
import os
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','refs')
T=os.path.join(os.path.dirname(os.path.abspath(__file__)),'tex')
im=Image.open(os.path.join(R,'coffee_delonghi_1.jpg')).convert('RGB')
h=im.crop((248,138,832,405)).copy()
d=ImageDraw.Draw(h)
# fill dial (3D) area with panel silver so the 3D dial sits on a clean base
h=h.resize((1024,int(1024*267/584)),Image.LANCZOS); h.save(os.path.join(T,'coffee_head.png'))
# badge
b=im.crop((400,410,690,468)).resize((512,102),Image.LANCZOS); b.save(os.path.join(T,'coffee_badge.png'))
# drip tray grille: stainless with dot rows, 248 x 70 mm -> 1024 x 290
g=Image.new('RGB',(1024,290),(196,198,201)); d=ImageDraw.Draw(g)
import random
for x in range(1024):
    v=196+((x*7)%5)-2
    d.line((x,0,x,289),fill=(v,v+2,v+5))
for sec in (0,1,2):
    x0=20+sec*335
    d.rectangle((x0-12,8,x0+318,282),outline=(150,152,155),width=3)
for col in list(range(70,300,46))+list(range(400,640,46))+list(range(730,1000,46)):
    for row in range(40,270,38):
        d.ellipse((col-6,row-6,col+6,row+6),fill=(40,41,43))
for cx in (120,470,560):
    d.ellipse((cx-24,145-24,cx+24,145+24),fill=(25,25,27))
g.save(os.path.join(T,'coffee_tray.png'))
print('ok')
