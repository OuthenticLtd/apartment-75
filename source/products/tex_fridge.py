from PIL import Image, ImageDraw, ImageFont
import os
T=os.path.join(os.path.dirname(os.path.abspath(__file__)),'tex')
F='C:/Windows/Fonts/'
def font(n,s): return ImageFont.truetype(F+n,s)
# SAMSUNG logo, white-grey on transparent, 88 x 11 mm -> 640 x 80
im=Image.new('RGBA',(640,80),(0,0,0,0)); d=ImageDraw.Draw(im)
f=font('arialbd.ttf',62); txt='SAMSUNG'; sp=18
w=sum(d.textlength(c,font=f) for c in txt)+sp*(len(txt)-1); x=(640-w)/2
for c in txt:
    d.text((x,8),c,font=f,fill=(225,225,228,255)); x+=d.textlength(c,font=f)+sp
im.save(os.path.join(T,'fridge_logo.png'))
# display 73 x 119 mm -> 300 x 490
im=Image.new('RGB',(300,490),(8,9,11)); d=ImageDraw.Draw(im)
d.rounded_rectangle((2,2,297,487),18,outline=(55,57,60),width=4)
c=(150,205,235)
fb=font('arialbd.ttf',78); fs=font('arial.ttf',26)
# fridge temp row
d.rectangle((40,70,64,110),outline=c,width=3); d.line((40,85,64,85),fill=c,width=3)
d.text((86,46),'3',font=fb,fill=c); d.text((140,52),'°C',font=fs,fill=c)
# freezer row
d.rectangle((40,190,64,230),outline=c,width=3); d.line((40,200,64,200),fill=c,width=3)
d.text((80,166),'-19',font=fb,fill=c); d.text((200,172),'°C',font=fs,fill=c)
# touch buttons row
g=(170,172,176)
for i,lab in enumerate(['Fridge','Freezer','Lock']):
    x=52+i*98; d.ellipse((x-10,330,x+10,350),outline=g,width=3)
    d.text((x,372),lab,font=font('arial.ttf',20),fill=g,anchor='mm')
d.line((40,420,260,420),fill=(60,62,66),width=2)
d.text((150,450),'Hold 3 sec',font=font('arial.ttf',18),fill=(120,122,126),anchor='mm')
im.save(os.path.join(T,'fridge_display.png'))
# dispenser label strip
im=Image.new('RGB',(400,100),(28,29,31)); d=ImageDraw.Draw(im)
d.text((200,35),'Easy Access',font=font('arial.ttf',26),fill=(200,200,204),anchor='mm')
d.text((200,68),'Dispenser',font=font('arial.ttf',26),fill=(200,200,204),anchor='mm')
im.save(os.path.join(T,'fridge_disp_label.png'))
print('ok')
