# -*- coding: utf-8 -*-
from common import *
import geom as G
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch

CW = '#1F5FA8'   # cold
HW = '#C0392B'   # hot
DR = '#2E7D32'   # drain
CO = '#2E7D32'   # condensate


def pt(S, x, y, kind):
    px, py = S.P(x, y)
    ax = S.ax
    if kind == 'cw':
        ax.add_patch(Circle((px, py), 0.95, fc=CW, ec='white', lw=0.3, zorder=30))
    elif kind == 'hw':
        ax.add_patch(Circle((px, py), 0.95, fc=HW, ec='white', lw=0.3, zorder=30))
    elif kind == 'dr':
        ax.add_patch(Circle((px, py), 1.35, fc='white', ec=DR, lw=0.8, zorder=30))
        ax.add_patch(Circle((px, py), 0.45, fc=DR, ec=DR, lw=0.3, zorder=30.1))
    elif kind == 'riser':
        ax.add_patch(Circle((px, py), 2.3, fc='white', ec='k', lw=0.7, zorder=30))
        ax.add_patch(Circle((px, py), 1.4, fc='white', ec=DR, lw=0.9, zorder=30.1))
        ax.plot([px - 1.0, px + 1.0], [py - 1.0, py + 1.0], color='k', lw=0.5, zorder=30.2)
        ax.plot([px - 1.0, px + 1.0], [py + 1.0, py - 1.0], color='k', lw=0.5, zorder=30.2)


def pipe(S, pts, kind, lw=None):
    sty = {'cw': (CW, '-', 0.7), 'hw': (HW, '-', 0.7), 'dr': (DR, (0, (4, 1.6)), 1.0),
           'co': (CO, (0, (1.2, 1.2)), 0.7), 'opt': (CW, (0, (2, 1.5)), 0.5)}[kind]
    S.line(pts, lw=lw or sty[2], color=sty[0], ls=sty[1], z=25)


def tag(S, x, y, t, dx=0, dy=0, lead=True):
    px, py = S.P(x, y)
    tx, ty = px + dx, py + dy
    if lead and (dx or dy):
        S.ax.plot([px, tx], [py, ty], color='0.25', lw=0.25, zorder=31)
    S.ax.text(tx, ty, t, fontsize=4.8, ha='center', va='center', weight='bold', zorder=33,
              bbox=dict(boxstyle='round,pad=0.18', fc='white', ec='k', lw=0.4))


def slope(S, x, y, txt, rot=0, color=DR):
    S.text(x, y, txt, fs=4.0, color=color, rotation=rot, z=32,
           bbox=dict(boxstyle='square,pad=0.05', fc='white', ec='none', alpha=0.9))


POINTS = [
    ('В1', 'Мивка кухня', 'СВ + ТВ (ъглови вентили 1/2")', '0,50', 'К Ø50, h 0,45'),
    ('В2', 'Съдомиялна', 'СВ от В1 (двоен ъглов вентил)', '0,50', 'към сифона на мивката'),
    ('В3', 'Перална машина', 'СВ, вентил 3/4" с възвратна клапа', '0,55', 'К Ø50 със сифон в стената, h 0,50'),
    ('В4', 'Хладилник (опция)', 'СВ PE 1/4" от В1, вентил + филтър', '—', '—'),
    ('В5', 'Щранг кухня*', 'СВ / ТВ (+ТЦ), водомери, СК', '—', 'К Ø110 (щранг)'),
    ('В6', 'Кондензна вода КЛ-В', '—', '—', 'Ø20, мин. 1 %, сух сифон към К'),
    ('В7', 'Мивка баня (ENHET)', 'СВ + ТВ (ъглови вентили 1/2")', '0,55', 'К Ø40, h 0,50'),
    ('В8', 'WC окачена, рамка', 'СВ в рамката (казанче)', '~1,00', 'К Ø110 (Ø90), ос h 0,23'),
    ('В9', 'Душ – вграден смесител', 'СВ + ТВ (термостатен)', '1,10', '—'),
    ('В10', 'Дъждовна глава', 'от смесителя В9 (в стената)', '2,20', 'рамо от стената y = 168'),
    ('В11', 'Линеен трап 80 cm', '—', '—', 'изход Ø50, под 1,5–2 % към трапа'),
    ('В12', 'Щранг баня*', 'СВ / ТВ / ТЦ, водомери, СК', '—', 'К Ø110 (щранг)'),
    ('В13', 'Бойлер (опция) над WC', 'СВ (предп. клапан) / ТВ изход', '1,30', 'клапан → в К (през фуния)'),
    ('В14', 'Балкон – отводнител*', '—', '—', 'съществуващ (?); кондензна КЛ-Н'),
]


def main():
    S = Sheet('05', 'ВиК', ox=50, oy=84)
    S.walls('solid')
    S.openings(swing=True, labels=False, color='0.45')
    S.furniture('faint')
    # ---------------- kitchen
    R1 = (3.25, 0.12)
    pipe(S, [(3.22, 0.03), (1.17, 0.03)], 'cw')
    pipe(S, [(3.22, 0.06), (1.33, 0.06)], 'hw')
    pipe(S, [(1.25, 0.09), (3.20, 0.09)], 'dr')
    pipe(S, [(2.30, 0.03), (2.30, 0.03)], 'cw')
    pipe(S, [(1.17, 0.14), (1.40, 0.14), (1.40, 0.50)], 'opt')     # DW from В1
    pipe(S, [(1.17, 0.18), (2.95, 0.18), (2.95, 0.30)], 'opt')     # fridge (option)
    for (x, k) in ((1.17, 'cw'), (1.33, 'hw'), (2.30, 'cw')):
        pt(S, x, 0.03 if k == 'cw' else 0.06, k)
    pt(S, 1.25, 0.10, 'dr'); pt(S, 2.45, 0.10, 'dr')
    pt(S, *R1, 'riser')
    slope(S, 2.05, 0.17, 'Ø50 i ≥ 2 % →')
    # condensate from AC indoor down the wall to the kitchen stack
    pipe(S, [(3.30, 1.85), (3.30, 0.20)], 'co')
    S.rect(3.10, 1.45, 3.35, 2.25, lw=0.5, ec='#7B3FA0', fc='white', ls=(0, (3, 1.5)), z=24)
    S.text(3.225, 1.85, 'КЛ-В', fs=4.0, color='#7B3FA0', rotation=90, weight='bold', z=26)
    tag(S, 1.25, 0.10, 'В1', dx=0, dy=9)
    tag(S, 1.40, 0.50, 'В2', dx=3, dy=6)
    tag(S, 2.38, 0.08, 'В3', dx=0, dy=9)
    tag(S, 2.95, 0.30, 'В4', dx=-2, dy=8)
    tag(S, *R1, 'В5', dx=7, dy=7)
    tag(S, 3.30, 1.10, 'В6', dx=-6, dy=0)
    # ---------------- bathroom
    R2 = (6.55, 0.12)
    pt(S, *R2, 'riser')
    pipe(S, [(6.50, 0.03), (4.93, 0.03), (4.93, 1.62), (5.13, 1.62)], 'cw')
    pipe(S, [(6.50, 0.06), (4.96, 0.06), (4.96, 1.58), (5.31, 1.58), (5.31, 1.62)], 'hw')
    pipe(S, [(6.60, 0.20), (6.60, 1.25)], 'cw')
    pipe(S, [(6.63, 0.20), (6.63, 1.21)], 'hw')
    pipe(S, [(6.62, 1.25), (6.62, 1.66), (6.10, 1.66)], 'cw', lw=0.5)     # to rain head (mixed)
    pt(S, 5.13, 1.62, 'cw'); pt(S, 5.31, 1.62, 'hw')
    pt(S, 6.60, 1.25, 'cw'); pt(S, 6.63, 1.21, 'hw')
    pt(S, 6.10, 1.66, 'cw')
    pt(S, 6.60, 0.42, 'cw')       # WC cistern
    pt(S, 6.60, 0.28, 'cw'); pt(S, 6.62, 0.60, 'hw')   # boiler option
    # drains
    pipe(S, [(5.22, 1.645), (6.40, 1.645)], 'dr')
    pipe(S, [(6.40, 1.60), (6.52, 1.60), (6.52, 0.24)], 'dr')
    pipe(S, [(6.45, 0.40), (6.53, 0.40)], 'dr', lw=1.8)
    pt(S, 5.22, 1.62, 'dr'); pt(S, 6.40, 1.60, 'dr'); pt(S, 6.45, 0.40, 'dr')
    slope(S, 6.40, 0.95, 'Ø50 i ≥ 2 % ↓', rot=90)
    slope(S, 5.80, 1.52, 'Ø40 i ≥ 2 % →')
    tag(S, 5.22, 1.62, 'В7', dx=-6, dy=-3)
    tag(S, 6.45, 0.40, 'В8', dx=-9, dy=-1)
    tag(S, 6.60, 1.25, 'В9', dx=-7, dy=-3)
    tag(S, 6.10, 1.66, 'В10', dx=-4, dy=-6)
    tag(S, 5.90, 1.60, 'В11', dx=-3, dy=-9)
    tag(S, *R2, 'В12', dx=-2, dy=-6.5)
    tag(S, 6.62, 0.60, 'В13', dx=7, dy=4)
    # ---------------- balcony
    pt(S, 6.40, 5.80, 'dr')
    pipe(S, [(6.33, 5.92), (6.40, 5.82)], 'co')
    tag(S, 6.40, 5.80, 'В14', dx=-7, dy=2)
    # ---------------- texts on plan
    S.text(3.25, -0.62, 'щранг – да се провери на място', fs=4.3, color='k',
           bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='none'))
    S.line([(3.25, 0.12), (3.25, -0.52)], lw=0.25, color='0.3', z=31)
    S.text(6.55, -0.62, 'щранг – да се провери на място', fs=4.3, color='k',
           bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='none'))
    S.line([(6.55, 0.12), (6.55, -0.52)], lw=0.25, color='0.3', z=31)
    S.text(5.25, 0.55, 'хидроизолация: под + стени\nдуш до h 2,00, останалото h 0,30', fs=3.9, color='0.25', z=31,
           bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='none', alpha=0.85))

    right(S)
    notes(S)
    S.scale_bar(52, 70)
    S.title_block()
    S.save('05 ВиК')


def right(S):
    ax = S.ax
    X, W = 230, 180
    # points table
    top = 285
    rh = 4.4
    H = 9 + rh * len(POINTS) + 9
    S.legend_box(X, top - H, W, H)
    cols = [X + 2, X + 12, X + 46, X + 100, X + 113]
    for cx, t in zip(cols, ['№', 'Прибор / точка', 'Захранване', 'h, m', 'Канал / бележка']):
        ax.text(cx, top - 4.4, t, fontsize=5.2, weight='bold', va='center', zorder=31)
    ax.plot([X, X + W], [top - 8, top - 8], 'k', lw=0.35, zorder=31)
    for i, r in enumerate(POINTS):
        y = top - 8 - rh * (i + 0.5) - 0.5
        if i % 2:
            ax.add_patch(Rectangle((X + 0.3, y - rh / 2), W - 0.6, rh, fc='0.94', ec='none', zorder=15.5))
        for cx, v in zip(cols, r):
            ax.text(cx, y, v, fontsize=4.55, va='center', zorder=31, weight='bold' if cx == cols[0] else 'normal')
    for cx in cols[1:]:
        ax.plot([cx - 1.2, cx - 1.2], [top - H + 9, top], 'k', lw=0.2, zorder=31)
    ax.plot([X, X + W], [top - H + 9, top - H + 9], 'k', lw=0.35, zorder=31)
    ax.text(X + 2, top - H + 4.5, '* Положението на щранговете и балконския отводнител е прието по архитектурния план – да се провери на място.',
            fontsize=4.3, va='center', zorder=31)
    # legend
    Y2 = top - H - 4
    H2 = 44
    S.legend_box(X, Y2 - H2, W, H2, 'Легенда')
    rows = [('cw', 'Студена вода (СВ) – тръба / изход'), ('hw', 'Топла вода (ТВ) – тръба / изход'),
            ('dr', 'Канализация (К) – тръба / изход, Ø и наклон'), ('co', 'Кондензна вода от климатика'),
            ('opt', 'Захранване по избор (СМ, хладилник)'), ('riser', 'Щранг (СВ/ТВ/ТЦ + К Ø110)')]
    for i, (k, t) in enumerate(rows):
        c, r = divmod(i, 3)
        x = X + 4 + c * 90
        y = Y2 - 11 - r * 9
        if k in ('cw', 'hw', 'dr', 'co', 'opt'):
            col = {'cw': CW, 'hw': HW, 'dr': DR, 'co': CO, 'opt': CW}[k]
            ls = {'cw': '-', 'hw': '-', 'dr': (0, (4, 1.6)), 'co': (0, (1.2, 1.2)), 'opt': (0, (2, 1.5))}[k]
            ax.plot([x - 2, x + 7], [y, y], color=col, ls=ls, lw=1.0, zorder=31)
            if k in ('cw', 'hw'):
                ax.add_patch(Circle((x + 10, y), 0.95, fc=col, ec='white', lw=0.3, zorder=31))
            if k == 'dr':
                ax.add_patch(Circle((x + 10, y), 1.35, fc='white', ec=DR, lw=0.8, zorder=31))
                ax.add_patch(Circle((x + 10, y), 0.45, fc=DR, ec=DR, lw=0.3, zorder=31.1))
        else:
            ax.add_patch(Circle((x + 3, y), 2.3, fc='white', ec='k', lw=0.7, zorder=31))
            ax.add_patch(Circle((x + 3, y), 1.4, fc='white', ec=DR, lw=0.9, zorder=31.1))
            ax.plot([x + 2, x + 4], [y - 1, y + 1], 'k', lw=0.5, zorder=31.2)
            ax.plot([x + 2, x + 4], [y + 1, y - 1], 'k', lw=0.5, zorder=31.2)
        ax.text(x + 14, y, t, fontsize=4.8, va='center', zorder=31)
    ax.text(X + 3, Y2 - H2 + 4, 'В1…В14 – номер на точката (таблицата горе); h – височина на оста на изхода от готов под.',
            fontsize=4.4, va='center', zorder=31, color='0.25')
    # notes
    Y3 = Y2 - H2 - 5
    ax.text(X, Y3, 'Бележки ВиК:', fontsize=5.6, weight='bold', va='top', zorder=31)
    ax.text(X, Y3 - 4.2,
            '1. Топлата вода е от Топлофикация (абонатна станция на сградата): ТВ + циркулация ТЦ по щранга;\n'
            '   водомери СВ/ТВ с дистанционно отчитане при щранговете, с ревизионни капаци в обшивката.\n'
            '2. Бойлер (В13) – само ако няма ТВ от Топлофикация или като резерва: 50 л вертикален над WC\n'
            '   вместо шкафа; захранване ел. – лист 04 (К12).\n'
            '3. Тръби: захранване PPR PN20 / PE-Xa в изолация (ТВ – топлоизолация 9 mm); канал PP-HT.\n'
            '4. Наклони (мин.): Ø40/Ø50 – 2 %; Ø110 – 1,5–2 %; кондензна Ø20 – 1 %. Ревизии при чупките.\n'
            '5. Душ без праг: подова конструкция ≥ 9–10 cm над плочата за трапа и наклона, или понижение.',
            fontsize=4.4, va='top', zorder=31, linespacing=1.4)


def notes(S):
    ax = S.ax
    X2, Y2 = 22, 64
    ax.text(X2, Y2, 'Нормативна основа и указания:', fontsize=5.6, weight='bold', va='top', zorder=31)
    ax.text(X2, Y2 - 4.2,
            '1. Наредба № 4 от 2005 г. за проектиране, изграждане и експлоатация на сградни водопроводни и канализационни\n'
            '   инсталации; БДС EN 806 (питейна вода в сгради); БДС EN 12056 (гравитачна канализация в сгради).\n'
            '2. Окачена тоалетна: инсталационна рамка тип Geberit Duofix h 1,12 в обшивка ГК 20×72×115 cm;\n'
            '   бутон за промиване h 1,00–1,15 (ос ~1,03), ревизия през бутона; ос на WC 40 cm от стената y = 0.\n'
            '3. Мивка кухня: подплотова, ос x = 125; съдомиялна – от ъгловия вентил на мивката и маркуч към сифона;\n'
            '   пералня – вентил 3/4" и вграден сифон зад уреда. Кондензна вода КЛ-В – в стената към щранга В5 със\n'
            '   сух (без вода) сифон тип HL; кондензна вода от външното тяло – към балконския отводнител В14.\n'
            '4. Схемата е интериорно задание; окончателното трасе, диаметрите и материалите – от ВиК проектант/изпълнител.',
            fontsize=4.4, va='top', zorder=31, linespacing=1.4)


if __name__ == '__main__':
    main()
