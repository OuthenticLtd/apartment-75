# -*- coding: utf-8 -*-
"""Sheet 05 – water supply and drainage (ВиК). Fixture positions from the export; heights per the design brief."""
from common import *
import geom as G
from matplotlib.patches import Rectangle, Circle

CW = '#1F5FA8'; HW = '#C0392B'; DR = '#2E7D32'; CO = '#7B3FA0'

SX = G.SINK_DRAIN[0]                                # kitchen sink strainer axis (1.40)
R1 = (3.03, 0.13)                                   # assumed kitchen stack (behind the fridge) – verify
R2 = (6.53, 0.10)                                   # assumed bathroom stack (WC boxing) – verify
BX = (G.BASIN[0] + G.BASIN[2]) / 2                  # basin axis 5.3175
TAP = G.ctr('Vanity_tap_body')
WASTE = G.ctr('Vanity_drain')                       # (5.53, 1.47)
MIX = G.SHOWER['mixer']
DRN = G.SHOWER['drain']
DRN_OUT = (6.45, (DRN[1] + DRN[3]) / 2)             # linear-drain outlet at x 6.45
WCX = G.bb('WC_boxing')
WASH = G.WASHER
WV = ((WASH[0] + WASH[2]) / 2 - 0.08, G.Y_BATH1)    # washer valve on the rear wall
TRAP = ((WASH[2] + WASTE[0]) / 2 + 0.02, G.Y_BATH1)  # combined basin + machine trap (HL) in the wall
BO = G.bb('Boiler')
BOC = ((BO[0] + BO[2]) / 2 + 0.06, (BO[1] + BO[3]) / 2)


def pt(S, x, y, kind):
    px, py = S.P(x, y); ax = S.ax
    if kind == 'cw':
        ax.add_patch(Circle((px, py), 0.95, fc=CW, ec='white', lw=0.3, zorder=30))
    elif kind == 'hw':
        ax.add_patch(Circle((px, py), 0.95, fc=HW, ec='white', lw=0.3, zorder=30))
    elif kind == 'dr':
        ax.add_patch(Circle((px, py), 1.35, fc='white', ec=DR, lw=0.8, zorder=30))
        ax.add_patch(Circle((px, py), 0.55, fc='white', ec=DR, lw=0.6, zorder=30.1))
    elif kind == 'riser':
        ax.add_patch(Circle((px, py), 2.3, fc='white', ec='k', lw=0.7, zorder=30))
        ax.plot([px - 1.6, px + 1.6], [py - 1.6, py + 1.6], color='k', lw=0.6, zorder=30.2)
        ax.plot([px - 1.6, px + 1.6], [py + 1.6, py - 1.6], color='k', lw=0.6, zorder=30.2)


def box(S, x, y, t, color='k', dx=0, dy=0):
    px, py = S.P(x, y); px += dx; py += dy
    S.ax.add_patch(Rectangle((px - 1.7, py - 1.3), 3.4, 2.6, fc='white', ec=color, lw=0.55, zorder=31))
    S.ax.text(px, py, t, fontsize=4.2, ha='center', va='center', zorder=31.1, color=color, weight='bold')


def pipe(S, pts, kind, lw=None):
    sty = {'cw': (CW, '-', 0.7), 'hw': (HW, '-', 0.7), 'dr': (DR, (0, (4, 1.6)), 1.0),
           'co': (CO, (0, (1.2, 1.2)), 0.7), 'opt': (CW, (0, (2, 1.5)), 0.5)}[kind]
    S.line(pts, lw=lw or sty[2], color=sty[0], ls=sty[1], z=25)


def tag(S, x, y, t, dx=0, dy=0):
    px, py = S.P(x, y)
    tx, ty = px + dx, py + dy
    if dx or dy:
        S.ax.plot([px, tx], [py, ty], color='0.25', lw=0.25, zorder=31)
    S.ax.text(tx, ty, t, fontsize=4.8, ha='center', va='center', weight='bold', zorder=33,
              bbox=dict(boxstyle='round,pad=0.18', fc='white', ec='k', lw=0.4))


def slope(S, x, y, txt, rot=0):
    S.text(x, y, txt, fs=4.0, color=DR, rotation=rot, z=32,
           bbox=dict(boxstyle='square,pad=0.05', fc='white', ec='none', alpha=0.9))


def h(v):
    return fmt(v)


POINTS = [
    ('В1', 'Мивка кухня, ос x = ' + cm(SX), 'СВ (щранг) + ТВ (от В8)', h(0.62), f'К Ø50, h {h(0.55)}'),
    ('В2', 'Съдомиялна (вградена 45)', 'СВ от двоен вентил В1', '—', 'към сифона на мивката'),
    ('В3', 'Пералня-сушилня (под плота)', 'СВ, вентил 3/4"', h(0.65), 'сифон HL в стената h 0,62–0,80'),
    ('В4', 'Умивалник, интегриран в плота', 'смесител стенен СВ + ТВ', '1,045', f'отток ({fmt(WASTE[0])}; {fmt(WASTE[1])}) → В3'),
    ('В5', 'WC окачена, вградено казанче', 'СВ в рамката', '—', f'Ø110 към щранга ≈ ({fmt(R2[0])}; {fmt(R2[1])})'),
    ('В6', 'Душ – термостатен смесител', 'СВ + ТВ, на преградата y ' + cm(G.Y_BATH1 - 0.01), h(1.09), '—'),
    ('В7', 'Линеен трап', '—', '—', f'изход x {fmt(DRN_OUT[0])}; решетка −1,6 cm; 2 %'),
    ('В8', 'Бойлер Eldom Galant DU060W 60 л (вертикален)', 'СВ вход / ТВ – баня + кухня', h(G.bz('Boiler')[0]), 'предпазен клапан → К (щранг WC)'),
    ('В9', 'Щранг кухня* (зад хладилника)', 'СВ, водомер М, СК', '—', f'К Ø110 ≈ ({fmt(R1[0])}; {fmt(R1[1])})'),
    ('В10', 'Щранг баня* (в обшивката на WC)', 'СВ, водомер М, СК', '—', f'К Ø110 ≈ ({fmt(R2[0])}; {fmt(R2[1])})'),
    ('В11', 'Кондензна вода КЛ-В1 / КЛ-В2', '—', '—', 'Ø20, мин. 1 %, към балкона'),
]


def kitchen(S, det=False):
    pt(S, *R1, 'riser')
    pipe(S, [(R1[0] - 0.05, 0.035), (SX - 0.07, 0.035)], 'cw')
    pipe(S, [(SX, 0.11), (R1[0] - 0.06, 0.11)], 'dr')
    dwx = G.ctr('K_front_dw')[0]
    pipe(S, [(SX - 0.07, 0.16), (dwx, 0.16), (dwx, 0.40)], 'opt')
    pt(S, SX - 0.07, 0.035, 'cw'); pt(S, SX + 0.07, 0.24, 'hw'); pt(S, SX, 0.13, 'dr')
    slope(S, 2.25, 0.11, 'К Ø50  i = 2 % →')
    box(S, R1[0], R1[1], 'М', dx=-1.0, dy=4.0); box(S, R1[0], R1[1], 'СК', color=CW, dx=-4.6, dy=4.0)
    box(S, R1[0], R1[1], 'Р', color=DR, dx=3.6, dy=4.0)
    tag(S, SX, 0.13, 'В1', dx=-5, dy=10)
    tag(S, dwx, 0.40, 'В2', dx=0, dy=6)
    tag(S, *R1, 'В9', dx=8, dy=9)


def bath(S, det=False):
    pt(S, *R2, 'riser')
    # supply: CW from the stack to the boiler and fixtures; HW from the boiler
    xe = G.X_E - 0.05
    pipe(S, [(R2[0], R2[1] + 0.04), (xe, R2[1] + 0.04), (xe, G.Y_BATH1 - 0.05), (WV[0], G.Y_BATH1 - 0.05)], 'cw')
    pipe(S, [(BOC[0], BOC[1]), (xe - 0.03, BOC[1]), (xe - 0.03, G.Y_BATH1 - 0.08), (TAP[0] + 0.04, G.Y_BATH1 - 0.08)], 'hw')
    pipe(S, [(xe, BOC[1] - 0.06), (BOC[0], BOC[1] - 0.06)], 'cw', lw=0.5)
    pt(S, BOC[0], BOC[1], 'hw'); pt(S, BOC[0], BOC[1] - 0.06, 'cw')
    pt(S, TAP[0] - 0.04, G.Y_BATH1 - 0.05, 'cw'); pt(S, TAP[0] + 0.04, G.Y_BATH1 - 0.08, 'hw')
    pt(S, MIX[0] - 0.05, G.Y_BATH1 - 0.05, 'cw'); pt(S, MIX[0] + 0.05, G.Y_BATH1 - 0.08, 'hw')
    pt(S, WV[0], G.Y_BATH1 - 0.05, 'cw')
    wcx = (WCX[0] + WCX[2]) / 2
    pt(S, wcx, 0.55, 'cw')
    pipe(S, [(xe, 0.55), (wcx, 0.55)], 'cw', lw=0.5)
    # drains: basin waste -> combined in-wall trap (with the washer) -> along the partition -> stack
    pipe(S, [WASTE, (WASTE[0], G.Y_BATH1 - 0.02), (TRAP[0], G.Y_BATH1 - 0.02)], 'dr', lw=0.7)
    pipe(S, [(TRAP[0], G.Y_BATH1 - 0.02), (6.58, G.Y_BATH1 - 0.02), (6.58, R2[1] + 0.06)], 'dr')
    pipe(S, [DRN_OUT, (6.58, DRN_OUT[1])], 'dr')
    pipe(S, [(6.40, 0.40), (R2[0], 0.40), (R2[0], R2[1] + 0.05)], 'dr', lw=1.8)
    pt(S, *WASTE, 'dr'); pt(S, TRAP[0], G.Y_BATH1 - 0.02, 'dr'); pt(S, *DRN_OUT, 'dr'); pt(S, 6.40, 0.40, 'dr')
    for i_, (t_, c_) in enumerate((('М', 'k'), ('СК', CW), ('Р', DR))):
        box(S, R2[0], R2[1], t_, color=c_, dx=9.0 + 4.2 * i_, dy=1.0)
    S.ax.plot([S.P(*R2)[0] + 2.3, S.P(*R2)[0] + 7.3], [S.P(*R2)[1] + 1.0] * 2, color='0.3', lw=0.25, zorder=30.5)
    px, py = S.P(*BOC); S.ax.text(px - 1.0, py + 6.0, 'Б', fontsize=5.0, weight='bold', zorder=33,
                                  bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='k', lw=0.4))
    px, py = S.P(*G.ctr('Bath_fan')); S.ax.text(px - 4.0, py + 6.0, 'ВН', fontsize=4.4, weight='bold', zorder=33, ha='center', va='center',
                                                 bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='k', lw=0.4))
    if not det:
        slope(S, 6.42, 1.05, 'К Ø50 i=2 % ↓', rot=90)
        tag(S, TRAP[0], G.Y_BATH1 - 0.02, 'В3', dx=-9, dy=-3)
        tag(S, TAP[0], G.Y_BATH1 - 0.05, 'В4', dx=-2, dy=-7)
        tag(S, 6.40, 0.40, 'В5', dx=-8, dy=0)
        tag(S, MIX[0], G.Y_BATH1 - 0.06, 'В6', dx=-6, dy=-6)
        tag(S, *DRN_OUT, 'В7', dx=-14, dy=-2)
        tag(S, *BOC, 'В8', dx=10, dy=4)
        tag(S, *R2, 'В10', dx=9, dy=-6)


def main():
    S = Sheet('05', 'ВиК', ox=50, oy=84)
    S.walls('solid')
    S.openings(swing=True, labels=False, color='0.45')
    S.furniture('faint')
    kitchen(S)
    bath(S)
    # kitchen hot water from the bathroom boiler: insulated PPR, ~6 m, at high level through the corridor
    hw_route = [(BOC[0] - 0.04, BOC[1] - 0.20), (BOC[0] - 0.04, 0.45), (G.X_BATH0 - 0.06, 0.45), (G.X_LIV1 + 0.02, 0.45),
                (SX + 0.07, 0.45), (SX + 0.07, 0.24)]
    S.line(hw_route, lw=0.8, color=HW, ls=(0, (5, 1.5, 1, 1.5)), z=25)
    L_ = sum(math.dist(a, b) for a, b in zip(hw_route[:-1], hw_route[1:])) + (2.05 - 0.62)
    S.text(4.12, 0.64, f'ТВ към кухнята ≈ {fmt(L_, 1)} m\n(под тавана, изолирана)', fs=3.9, color=HW, z=31,
           bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='none', alpha=0.9))
    # condensate from both AC units to the balcony
    ai = G.bb('AC_indoor'); ab = G.bb('AC_bed_indoor')
    for (a, b) in (((ai[0] + 0.04, ai[3]), None), (((ab[0] + ab[2]) / 2, ab[3]), None)):
        pass
    pipe(S, [(G.X_LIV1 - 0.08, ai[3]), (G.X_LIV1 - 0.08, 5.95), (3.62, 5.95), (3.62, 6.20)], 'co')
    pipe(S, [((ab[0] + ab[2]) / 2, ab[3]), (3.56, ab[3] + 0.05), (3.56, G.Y_BED1 - 0.05), (3.62, G.Y_BED1 + 0.10), (3.62, 6.20)], 'co')
    S.rect(*ai, lw=0.5, ec=CO, fc='white', ls=(0, (3, 1.5)), z=24)
    S.rect(*ab, lw=0.5, ec=CO, fc='white', ls=(0, (3, 1.5)), z=24)
    tag(S, 3.62, 6.20, 'В11', dx=6, dy=4)
    S.text(2.55, 4.05, 'кондензна КЛ-В1 → балкон\n(Ø20, i ≥ 1 %, в ъгъла)', fs=4.0, color=CO, z=31,
           bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='none', alpha=0.9))
    # stack remarks
    for (x, y) in (R1, R2):
        S.text(x, -0.48, 'щранг – да се провери на място', fs=4.2, color='k',
               bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='none'))
        S.line([(x, y), (x, -0.40)], lw=0.25, color='0.3', z=31)
    S.text(5.30, 0.62, 'хидроизолация: под + стени,\nдуш до h 2,00', fs=3.9, color='0.25', z=31,
           bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='none', alpha=0.85))
    right(S)
    notes(S)
    S.scale_bar(40, 16)
    S.title_block()
    S.save('05 ВиК')


def right(S):
    ax = S.ax
    X, W = 230, 180
    top = 285
    rh = 4.4
    H = 9 + rh * len(POINTS) + 9
    S.legend_box(X, top - H, W, H)
    cols = [X + 2, X + 13, X + 66, X + 113, X + 125]
    for cx, t in zip(cols, ['№', 'Прибор / точка', 'Захранване', 'h, m', 'Канал / бележка']):
        ax.text(cx, top - 4.4, t, fontsize=5.2, weight='bold', va='center', zorder=31)
    ax.plot([X, X + W], [top - 8, top - 8], 'k', lw=0.35, zorder=31)
    for i, r in enumerate(POINTS):
        y = top - 8 - rh * (i + 0.5) - 0.5
        if i % 2:
            ax.add_patch(Rectangle((X + 0.3, y - rh / 2), W - 0.6, rh, fc='0.94', ec='none', zorder=15.5))
        for cx, v in zip(cols, r):
            ax.text(cx, y, v, fontsize=4.4, va='center', zorder=31, weight='bold' if cx == cols[0] else 'normal')
    for cx in cols[1:]:
        ax.plot([cx - 1.2, cx - 1.2], [top - H + 9, top], 'k', lw=0.2, zorder=31)
    ax.plot([X, X + W], [top - H + 9, top - H + 9], 'k', lw=0.35, zorder=31)
    ax.text(X + 2, top - H + 4.5, '* Щранговете са приети (кухня зад хладилника, баня в обшивката на WC) – ДА СЕ ПРОВЕРЯТ на място. '
            'h – от готов под.', fontsize=4.2, va='center', zorder=31)
    # legend
    Y2 = top - H - 4
    H2 = 42
    S.legend_box(X, Y2 - H2, W, H2, 'Легенда')
    rows = [('cw', 'СВ – студена вода (синьо)'), ('hw', 'ТВ – топла вода (червено)'), ('dr', 'К – канализация, изход'),
            ('drl', 'тръба К, наклон „i = 2 %“'), ('riser', 'щранг (да се провери)'), ('trap', 'линеен трап'),
            ('b', 'Б – бойлер;  ВН – вентилатор'), ('m', 'М – водомер (радио);  СК – спирателен кран'),
            ('r', 'Р – ревизия;  кондензна КЛ (лилаво)')]
    for i, (k, t) in enumerate(rows):
        c, r = divmod(i, 5)
        x = X + 6 + c * 90
        y = Y2 - 11 - r * 6.0
        if k == 'cw': ax.add_patch(Circle((x, y), 0.95, fc=CW, ec='white', lw=0.3, zorder=31))
        elif k == 'hw': ax.add_patch(Circle((x, y), 0.95, fc=HW, ec='white', lw=0.3, zorder=31))
        elif k == 'dr':
            ax.add_patch(Circle((x, y), 1.35, fc='white', ec=DR, lw=0.8, zorder=31))
            ax.add_patch(Circle((x, y), 0.55, fc='white', ec=DR, lw=0.6, zorder=31.1))
        elif k == 'drl': ax.plot([x - 3, x + 5], [y, y], color=DR, ls=(0, (4, 1.6)), lw=1.0, zorder=31)
        elif k == 'riser':
            ax.add_patch(Circle((x, y), 2.0, fc='white', ec='k', lw=0.7, zorder=31))
            ax.plot([x - 1.4, x + 1.4], [y - 1.4, y + 1.4], 'k', lw=0.6, zorder=31.2)
            ax.plot([x - 1.4, x + 1.4], [y + 1.4, y - 1.4], 'k', lw=0.6, zorder=31.2)
        elif k == 'trap': ax.add_patch(Rectangle((x - 3, y - 0.6), 7, 1.2, fc='white', ec='k', lw=0.5, hatch='||||', zorder=31))
        elif k == 'b': ax.text(x, y, 'Б', fontsize=5, weight='bold', ha='center', va='center', zorder=31,
                               bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='k', lw=0.4))
        elif k == 'm':
            ax.add_patch(Rectangle((x - 1.7, y - 1.3), 3.4, 2.6, fc='white', ec='k', lw=0.55, zorder=31))
            ax.text(x, y, 'М', fontsize=4.2, ha='center', va='center', weight='bold', zorder=31.1)
        elif k == 'r':
            ax.add_patch(Rectangle((x - 1.7, y - 1.3), 3.4, 2.6, fc='white', ec=DR, lw=0.55, zorder=31))
            ax.text(x, y, 'Р', fontsize=4.2, ha='center', va='center', weight='bold', zorder=31.1, color=DR)
            ax.plot([x + 3, x + 8], [y, y], color=CO, ls=(0, (1.2, 1.2)), lw=0.8, zorder=31)
        ax.text(x + (11 if k == 'r' else 8), y, t, fontsize=4.8, va='center', zorder=31)
    ax.text(X + 3, Y2 - H2 + 3.5, 'В1 … В11 – номер на точката (таблицата горе).', fontsize=4.3, va='center', zorder=31, color='0.25')
    detail(S, Y2 - H2 - 4)


def notes(S):
    ax = S.ax
    X2, Y2 = 22, 64
    ax.text(X2, Y2, 'Нормативна основа и указания:', fontsize=5.6, weight='bold', va='top', zorder=31)
    ax.text(X2, Y2 - 4.2,
            '1. Наредба № 4 от 2005 г. за проектиране, изграждане и експлоатация на сградни водопроводни и канализационни инсталации;\n'
            '   БДС EN 806 (питейна вода); БДС EN 12056 (гравитачна канализация в сгради).\n'
            '2. Да не се правят канали (щрайхване) в носещите стоманобетонни панели – тръбите минават в преградите, в обшивки ГК\n'
            '   или в подовата замазка. Минимални наклони: Ø40/Ø50 – 2 %; Ø110 – 1,5–2 %; кондензна Ø20 – 1 %.\n'
            '3. Пералнята и умивалникът – общ сифон HL в стената, h 0,62–0,80 (с ревизия); вентил на пералнята h 0,65.\n'
            '4. Хидроизолация (течна мембрана + ленти в ъглите): целият под на банята; стените на душа до h 2,00, останалите до h 0,30.\n'
            '   Линеен трап: решетка −1,6 cm спрямо пода, наклон 2 % към трапа, изход x 6,45 към щранга.\n'
            '5. Хладилникът е свободностоящ – зад него щранг и радио-водомер с достъп; СК дублиран под мивката.\n'
            '   ТВ за кухнята е от бойлера в банята: PPR в изолация ≥ 9 mm, ~6 m, под тавана през коридора (в обшивка /\n'
            '   над горните шкафове), спуск до В1. Без рециркулация – кратко изчакване на топлата вода.\n'
            '6. Схемата е интериорно задание; окончателното трасе, диаметрите и материалите – от ВиК проектант / изпълнител.',
            fontsize=4.4, va='top', zorder=31, linespacing=1.4)


def detail(S, ytop):
    """Bathroom enlarged at 1:25 with heights."""
    from shapely.geometry import box as sbox
    ax = S.ax
    keep = (S.ox, S.oy, S.S)
    S.S = 40.0
    S.ox = 252 - 4.75 * 40
    S.oy = ytop - 12 - 1.95 * 40
    ax.text(232, ytop - 1, 'БАНЯ – детайл М 1:25 (височини от готов под)', fontsize=6.5, weight='bold', va='top', zorder=31)
    clip = sbox(4.66, -0.18, 6.80, 1.98)
    ext, part = G.wall_polys()
    S.shp(ext.intersection(clip), fc='0.25', ec='k', lw=0.5, z=6)
    S.shp(part.intersection(clip), fc='0.55', ec='k', lw=0.45, z=6)
    for it in G.FURN:
        if it['key'] in (30, 31, 32, 33, 34, 36):
            for sh in it['shapes']:
                S._shape(sh, '0.6', 0.25, True)
    bath(S, det=True)
    def Hh(x, y, t, dx, dy, ha='left'):
        px, py = S.P(x, y)
        ax.plot([px, px + dx], [py, py + dy], color='0.3', lw=0.25, zorder=31)
        ax.text(px + dx + (0.8 if ha == 'left' else -0.8), py + dy, t, fontsize=4.4, ha=ha, va='center', zorder=33,
                bbox=dict(boxstyle='square,pad=0.08', fc='white', ec='none'))
    Hh(TAP[0], G.Y_BATH1 - 0.05, 'В4 смесител СВ/ТВ h 1,045', -6, 12, 'right')
    Hh(*WASTE, f'В4 отток ({fmt(WASTE[0])}; {fmt(WASTE[1])})', -10, -8, 'right')
    Hh(TRAP[0], G.Y_BATH1 - 0.02, 'В3 сифон HL h 0,62–0,80; вентил h 0,65', -6, 18, 'right')
    Hh(MIX[0], G.Y_BATH1 - 0.06, f'В6 смесител h {h(1.09)}', 4, 10, 'left')
    Hh(*DRN_OUT, 'В7 трап, изход x 6,45', 14, 3, 'left')
    Hh(*BOC, f'В8 бойлер СВ/ТВ h {h(G.bz("Boiler")[0])}', 14, 0, 'left')
    Hh(6.40, 0.40, 'В5 WC Ø110', 14, -2, 'left')
    Hh(*R2, 'В10 щранг*', 14, -6, 'left')
    S.text(5.20, 0.45, 'наклон 2 %\nкъм трапа', fs=4.0, color=DR, z=33)
    S.ox, S.oy, S.S = keep


if __name__ == '__main__':
    main()
