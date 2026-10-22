from PIL import Image, ImageDraw, ImageFont
import os
T=os.path.join(os.path.dirname(os.path.abspath(__file__)),'tex')
F='C:/Windows/Fonts/'
# BOSCH logo, 40 x 9 mm on transparent
S=4; im=Image.new('RGBA',(256*S,58*S),(0,0,0,0)); d=ImageDraw.Draw(im)
c=(235,235,235,255)
d.ellipse((6*S,6*S,52*S,52*S),outline=c,width=5*S)
# stylised armature
d.line((18*S,29*S,40*S,29*S),fill=c,width=4*S); d.arc((18*S,14*S,40*S,44*S),100,260,fill=c,width=4*S); d.arc((18*S,14*S,40*S,44*S),280,80,fill=c,width=4*S)
f=ImageFont.truetype(F+'arialbd.ttf',46*S)
d.text((64*S,29*S),'BOSCH',font=f,fill=c,anchor='lm')
im.resize((256,58),Image.LANCZOS).save(os.path.join(T,'kettle_logo.png'))
# water level scale 26 x 110 mm
S=2; im=Image.new('RGBA',(120*S,500*S),(0,0,0,0)); d=ImageDraw.Draw(im)
f=ImageFont.truetype(F+'arial.ttf',20*S)
for y,a,b in ((30,'max','1.7 l'),(250,'','1.0 l'),(440,'min','0.5 l')):
    d.line((40*S,y*S,80*S,y*S),fill=(240,240,240,255),width=3*S)
    if a: d.text((60*S,(y-28)*S),a,font=f,fill=(240,240,240,235),anchor='mm')
    d.text((60*S,(y+20)*S),b,font=f,fill=(240,240,240,235),anchor='mm')
im.resize((120,500),Image.LANCZOS).save(os.path.join(T,'kettle_scale.png'))
print('ok')
