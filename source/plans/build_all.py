import subprocess, sys, os
from pypdf import PdfWriter
from common import OUT
for s in ['s01.py', 's02.py', 's03_1.py', 's03_elev.py', 's04.py', 's05.py', 's06.py']:
    subprocess.run([sys.executable, s], check=True)
order = ['01 Разпределение', '02 Мебелировка', '03.1 Мебели - спецификация', '03.2 Кухня - план и изгледи',
         '03.3 ТВ модул, бюро и антре', '03.4 Гардероб, спалня и библиотека', '04 Електро', '05 ВиК', '06 Осветление и таван']
w = PdfWriter()
for n in order:
    w.append(os.path.join(OUT, n + '.pdf'), outline_item=n)
w.add_metadata({'/Title': 'Апартамент 75, Младост 4 – Комплект чертежи', '/Author': 'Интериорен проект'})
with open(os.path.join(OUT, 'Апартамент 75 - Комплект чертежи.pdf'), 'wb') as f:
    w.write(f)
print('done')
