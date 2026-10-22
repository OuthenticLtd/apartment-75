s = open('s05.py', encoding='utf-8').read()
lines = s.split('\n')
# extract bathroom block (lines 95..121, 1-based) into a function
i0 = 94; i1 = 121
block = lines[i0:i1]
body = []
for ln in block:
    body.append(ln)
func = ['def bath(S, det=False):'] + [ln for ln in body if 'tag(' not in ln and 'slope(' not in ln] + [
    '    if not det:',
] + ['    ' + ln for ln in body if 'tag(' in ln or 'slope(' in ln] + ['']
new_lines = lines[:i0] + ['    bath(S)'] + lines[i1:]
s = '\n'.join(new_lines)
s = s.replace('\ndef right(S):', '\n' + '\n'.join(func) + '\n\ndef right(S):')
# riser texts higher, notes ВиК moved to the left block, detail added on the right
s = s.replace("S.text(3.25, -0.62, 'щранг", "S.text(3.25, -0.42, 'щранг").replace("S.text(6.55, -0.62, 'щранг", "S.text(6.55, -0.42, 'щранг")
s = s.replace("S.line([(3.25, 0.12), (3.25, -0.52)]", "S.line([(3.25, 0.12), (3.25, -0.35)]").replace("S.line([(6.55, 0.12), (6.55, -0.52)]", "S.line([(6.55, 0.12), (6.55, -0.35)]")
a = s.index("    # notes\n    Y3 = Y2 - H2 - 5")
b = s.index("def bath(S, det=False):")
s = s[:a] + "    detail(S, Y2 - H2 - 4)\n\n\n" + s[b:]
s = s.replace("    X2, Y2 = 22, 64\n", "    X2, Y2 = 22, 66\n")
s = s.replace("""            '4. Схемата е интериорно задание; окончателното трасе, диаметрите и материалите – от ВиК проектант/изпълнител.',""",
"""            '4. Топлата вода е от Топлофикация (абонатна станция на сградата): ТВ + циркулация ТЦ по щранга; водомери СВ/ТВ\\n'
            '   с дистанционно отчитане при щранговете, с ревизионни капаци. Бойлер В13 – само ако няма ТВ или като резерва\\n'
            '   (50 л вертикален над WC вместо шкафа; ел. захранване К12, лист 04).\\n'
            '5. Тръби: PPR PN20 / PE-Xa в изолация (ТВ – 9 mm); канал PP-HT. Мин. наклони: Ø40/Ø50 – 2 %; Ø110 – 1,5–2 %;\\n'
            '   кондензна Ø20 – 1 %. Душ без праг: подова конструкция ≥ 9–10 cm за трапа и наклона (или понижение на плочата).\\n'
            '6. Схемата е интериорно задание; окончателното трасе, диаметрите и материалите – от ВиК проектант/изпълнител.',""")
s = s.replace("    S.scale_bar(52, 70)\n", "    S.scale_bar(150, 24)\n")
s += '''

def detail(S, ytop):
    """Bathroom enlarged at 1:25 with heights."""
    from shapely.geometry import box as sbox
    ax = S.ax
    keep = (S.ox, S.oy, S.S)
    S.S = 40.0
    S.ox = 236 - 4.75 * 40
    S.oy = ytop - 8 - 1.95 * 40
    ax.text(232, ytop - 1, 'БАНЯ – детайл М 1:25', fontsize=6.5, weight='bold', va='top', zorder=31)
    clip = sbox(4.66, -0.18, 6.80, 1.98)
    ext, part = G.wall_polys()
    S.shp(ext.intersection(clip), fc='0.25', ec='k', lw=0.5, z=6)
    S.shp(part.intersection(clip), fc='0.55', ec='k', lw=0.45, z=6)
    for it in G.FURN:
        if it['key'] in (29, 30, 31, 32, 33, 34):
            for sh in it['shapes']:
                S._shape(sh, '0.6', 0.25, True)
    S.line([(4.89, 0.27), (5.55, 0.27)], lw=0.4, color='0.5')
    S.arc(4.89, 0.27, 0.66, 0, 90, ls=(0, (2, 1.2)), color='0.5')
    bath(S, det=True)
    H = lambda x, y, t, dx, dy, ha='left': (ax.plot([S.P(x, y)[0], S.P(x, y)[0] + dx], [S.P(x, y)[1], S.P(x, y)[1] + dy],
                                                   color='0.3', lw=0.25, zorder=31),
                                           ax.text(S.P(x, y)[0] + dx + (0.8 if ha == 'left' else -0.8), S.P(x, y)[1] + dy, t,
                                                   fontsize=4.5, ha=ha, va='center', zorder=33,
                                                   bbox=dict(boxstyle='square,pad=0.08', fc='white', ec='none')))
    H(5.13, 1.62, 'В7 СВ/ТВ h 0,55;  К Ø40 h 0,50', -3, 10, 'left')
    H(6.10, 1.66, 'В10 глава h 2,20', 2, 9, 'left')
    H(6.60, 1.25, 'В9 смесител h 1,10', 8, 3, 'left')
    H(6.62, 0.60, 'В13 бойлер СВ/ТВ h 1,30 (опц.)', 8, 0, 'left')
    H(6.60, 0.42, 'В8 WC: СВ ~1,00; К Ø110 h 0,23', 8, -4, 'left')
    H(6.55, 0.12, 'В12 щранг*', 8, -8, 'left')
    H(5.90, 1.60, 'В11 трап 80, изход Ø50', -14, -12, 'right')
    ax.text(S.P(5.28, 0.62)[0], S.P(5.28, 0.62)[1], 'наклон 1,5–2 %\\nкъм трапа', fontsize=4.2, ha='center', va='center',
            zorder=33, color=DR)
    S.ox, S.oy, S.S = keep
'''
open('s05.py', 'w', encoding='utf-8').write(s)
