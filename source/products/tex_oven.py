# prepares oven textures from refs/oven_hansa_4.jpg (run with system python + PIL)
from PIL import Image, ImageDraw
import os
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','refs')
T=os.path.join(os.path.dirname(os.path.abspath(__file__)),'tex')
im=Image.open(os.path.join(R,'oven_hansa_4.jpg')).convert('RGB')
p=im.crop((0,36,1198,262)).copy()
d=ImageDraw.Draw(p)
for cx in (418,780):
    d.ellipse((cx-50,177-36-50,cx+50,177-36+50),fill=(0,0,0))
p=p.resize((1024,210),Image.LANCZOS); p.save(os.path.join(T,'oven_panel.png'))
dr=im.crop((0,280,1198,1164)).copy()
d=ImageDraw.Draw(dr)
d.rectangle((0,0,1198,95),fill=(0,0,0))   # remove photographed handle & door top line
dr=dr.resize((1024,756),Image.LANCZOS); dr.save(os.path.join(T,'oven_door.png'))
print('ok')
