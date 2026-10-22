from PIL import Image, ImageDraw, ImageFont
import os
T=os.path.join(os.path.dirname(os.path.abspath(__file__)),'tex')
F='C:/Windows/Fonts/'
# visor front 598 x 43 mm -> 1024 x 74 (2x supersampled then reduced)
S=2; im=Image.new('RGB',(1024*S,74*S),(6,6,7)); d=ImageDraw.Draw(im)
f=ImageFont.truetype(F+'arialbd.ttf',27*S)
x0=48*S; y0=37*S
for dx in (0,9):
    for dy in (-5,4):
        d.ellipse((x0+dx*S-3.4*S,y0+dy*S-3.4*S,x0+dx*S+3.4*S,y0+dy*S+3.4*S),fill=(235,235,235))
d.text((x0+20*S,y0),'Hansa',font=f,fill=(235,235,235),anchor='lm')
im=im.resize((1024,74),Image.LANCZOS); im.save(os.path.join(T,'hood_visor.png'))
# expanded-metal grease filter tile (repeat)
N=128; im=Image.new('RGB',(N,N),(178,180,183)); d=ImageDraw.Draw(im)
for (cx,cy) in [(0,0),(N,0),(0,N),(N,N),(N/2,N/2)]:
    d.polygon([(cx-N/2+10,cy),(cx,cy-N/2+10),(cx+N/2-10,cy),(cx,cy+N/2-10)],fill=(95,97,100))
    d.line([(cx-N/2+10,cy),(cx,cy-N/2+10)],fill=(185,187,190),width=4)
im.save(os.path.join(T,'hood_filter.png'))
print('ok')
