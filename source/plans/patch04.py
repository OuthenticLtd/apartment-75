s = open('s04.py', encoding='utf-8').read()
rep = [
    ("'200/К12 бойлер\\n(резерва, опция)', (-5.0, -3.4), 'right'", "'200/К12 бойлер\\n(резерва, опция)', (9.0, 1.5), 'left'"),
    ("('downip', 5.25, 1.35, 0, 'o IP44', (2.4, 0.4), 'left')", "('downip', 5.25, 1.35, 0, 'o IP44', (2.4, 2.0), 'left')"),
    ("('wall', 0.0, 3.88, 0, 'd 162', (4.0, -2.4), 'left')", "('wall', 0.0, 3.88, 0, 'd 162', (4.0, 2.6), 'left')"),
    ("('wall', 0.0, 5.57, 0, 'd 162', (4.0, 2.4), 'left')", "('wall', 0.0, 5.57, 0, 'd 162', (4.0, -2.6), 'left')"),
    ("(3.10, 5.32, 'g')", "(2.98, 5.47, 'g')"),
    ("(5.75, 2.05, 'm')", "(6.25, 2.04, 'm')"),
    ("S.text(5.72, 2.15, 'фреон + дренаж (предложение)'", "S.text(5.05, 2.15, 'фреон + дренаж (предложение)'"),
    ("S.text(6.30, 6.31, 'КЛ-Н'", "S.text(6.33, 6.66, 'КЛ-Н'"),
    ("ax.text(px - 2.0, py - 2.6, 'рутер в\\nконзолата', fontsize=3.8, color=BLUE, ha='right', va='top'",
     "ax.text(px - 2.0, py, 'рутер', fontsize=4.0, color=BLUE, ha='right', va='center'"),
    ("ax.text(px - 2.4, py - 2.2, 'В (o, таймер)', fontsize=3.9, ha='right', va='top', zorder=31)",
     "ax.text(px - 2.4, py + 2.2, 'В (o, таймер)', fontsize=4.2, ha='right', va='bottom', zorder=31,\n"
     "            bbox=dict(boxstyle='square,pad=0.05', fc='white', ec='none', alpha=0.85))"),
    ("'50 ТВ коакс.'", "'50 ТВ'"),
    ("""        col = BLUE if k == 'tp' else 'k'
        ax.text(px + dx, py + dy, lab, fontsize=4.0,""", """        col = BLUE if k == 'tp' else 'k'
        if abs(dx) > 6 or abs(dy) > 6:
            ax.plot([px, px + dx], [py, py + dy], color='0.3', lw=0.25, zorder=31)
        ax.text(px + dx, py + dy, lab, fontsize=4.4,"""),
    ("ax.text(px + dx, py + dy, lab, fontsize=4.2, ha=ha, va='center', zorder=32, color='#7A4A00'",
     "ax.text(px + dx, py + dy, lab, fontsize=4.5, ha=ha, va='center', zorder=32, color='#7A4A00'"),
    ("ax.text(px + dx, py + dy, lab, fontsize=4.0, ha=ha, va='center', zorder=32, color=RED",
     "ax.text(px + dx, py + dy, lab, fontsize=4.4, ha=ha, va='center', zorder=32, color=RED"),
]
for a, b in rep:
    assert a in s, a[:50]
    s = s.replace(a, b)
open('s04.py', 'w', encoding='utf-8').write(s)
