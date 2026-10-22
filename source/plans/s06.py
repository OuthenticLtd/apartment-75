# -*- coding: utf-8 -*-
"""Sheet 06 – lighting and ceiling: fixtures from the export lights, aligned grids, circuits and switch groups."""
from common import *
import geom as G
import elec as EL
from elec import RED, BLUE, LED, PUR
from s04 import SWITCHES, LEDS, DRIVERS, wallpt, along, led_line
from matplotlib.patches import Rectangle, Circle, PathPatch
from matplotlib.path import Path

L = lambda n: G.lpos(n)[:2]
# code, light/object, kind, group
FIX = ([('О1', f'{n}', 'down', 'a') for n in ('AisleDown0', 'AisleDown1', 'LivingDown0', 'LivingDown1', 'LivingDown2')] +
       [('О2', f'KitchenDown{i}', 'down', 'b') for i in range(5)] +
       [('О3', 'Pendant_dining0_bulb', 'ceil', 'c'), ('О3', 'Pendant_dining1_bulb', 'ceil', 'c')] +
       [('О4', 'Sconce0_up', 'wall0', 'd'), ('О4', 'Sconce1_up', 'wall0', 'd')] +
       [('О5', 'PictureLight', 'pic0', 'd'), ('О5', 'PictureLight2', 'pic0', 'd')] +
       [('О10', 'Balcony_wall_light_L', 'wall90', 'f')] +
       [('О11', 'HallDown0', 'down', 'g'), ('О11', 'HallDown1', 'down', 'g')] +
       [('О12', 'Pendant_bedroom_bulb', 'ceil', 'h')] +
       [('О14', 'WallLamp0_light', 'wall180', 'k'), ('О14', 'WallLamp1_light', 'wall180', 'l')] +
       [('О16', 'BathSpot0', 'downip', 'n'), ('О16', 'BathSpot1', 'downip', 'n'), ('О16', 'BathSpot2', 'downip', 'n')])
SW = {r[0]: r for r in SWITCHES}
GROUPS = {   # group -> (switch objects, extra target points)
    'a': (['Living_switch'], []), 'b': (['Living_switch'], []), 'c': (['Living_switch2'], []),
    'd': (['Living_switch2'], [G.ctr('WU_upper_body')]), 'e': (['K_switch_led'], []),
    'f': (['Bal_switch'], []), 'g': (['Hall_switch_entry', 'Hall_switch_living'], []),
    'h': (['Bedroom_switch', 'Bed_switch0', 'Bed_switch1'], []), 'i': (['Bedroom_switch'], [G.ctr('BW_bridge_carc')]),
    'k': (['Bed_switch0'], []), 'l': (['Bed_switch1'], []),
    'n': (['Hall_switch_bath'], [G.ctr('Bath_fan')]), 'p': (['Hall_switch_bath'], [G.ctr('Mirror_cab')]),
}
GCOL = {'a': '#C0392B', 'b': '#D35400', 'c': '#8E44AD', 'd': '#1F618D', 'e': '#B7950B', 'f': '#2E4053',
        'g': '#117A65', 'h': '#C0392B', 'i': '#6E2C00', 'k': '#1F618D', 'l': '#8E44AD', 'n': '#117A65', 'p': '#D35400'}
CIRC = {'a': 'L1', 'b': 'L1', 'c': 'L1', 'd': 'L1', 'e': 'L1', 'f': 'L1', 'g': 'L2', 'h': 'L2', 'i': 'L2', 'k': 'L2',
        'l': 'L2', 'm': 'L2', 'n': 'L3', 'p': 'L3'}

zc = lambda n: fmt(G.zc(n))
SCHED = [
    ('О1', 'Луна LED вградена, насочваема Ø8, 7 W, CRI ≥ 90', '5', 'дневна – ос x 186,5, през 120', 'таван', '2700', 'IP20', 'a ◐'),
    ('О2', 'Луна LED вградена, 7 W', '5', 'кухня – ред y 50 + 1 над Г-частта', 'таван', '2700', 'IP20', 'b'),
    ('О3', 'Висяща лампа над масата, E27 LED', '2', 'x 32 / 92, y 256', f'ръб {fmt(G.bz("Pendant_dining0")[0])}', '2700', 'IP20', 'c ◐'),
    ('О4', 'Аплик стенен up/down, 2×5 W', '2', 'до дивана', zc('Sconce0'), '2700', 'IP20', 'd'),
    ('О5', 'Картинна лампа LED ~45 cm', '2', 'над картините RÖDALM', zc('PictureLight_bar0'), '2700', 'IP20', 'd'),
    ('О6', 'LED лента в нишата на воала', f'{fmt(G.bb("Curtain_cove_led")[2] - G.bb("Curtain_cove_led")[0], 1)} m', 'фасада дневна', 'таван', '2700', 'IP20', 'd'),
    ('О7', 'LED ТВ модул: горни шкафове, конзола, рафтове', '~6 m', 'ТВ модул', '0,14–1,85', '2700', 'IP20', 'd'),
    ('О8', 'LED профил вертикален, библиотека', '2×1,6 m', 'библиотека', '0,42–2,04', '2700', 'IP20', 'd'),
    ('О9', 'LED лента под горните шкафове', '~3,3 m', 'кухня', zc('K_led_B'), '2700', 'IP20', 'e'),
    ('О10', 'Аплик фасаден LED (+ гирлянд в контакт IP44)', '1', 'балкон', zc('Balcony_wall_light'), '3000', 'IP54', 'f'),
    ('О11', 'Луна LED вградена 7 W + LED в мебелта', '2', 'коридор – ос x 395', 'таван', '3000', 'IP20', 'g ↔'),
    ('О12', 'Пендел (оризова хартия), E27 LED', '1', 'спалня', f'ръб {fmt(G.bz("Pendant_bedroom")[0])}', '2700', 'IP20', 'h ↔✕↔'),
    ('О13', 'LED в нишите на колоните и под моста', '3', 'стена зад леглото', '1,40 / 1,55', '2700', 'IP20', 'i'),
    ('О14', 'Лампа за четене на гърба на нишата', '2', 'двете колони', '~1,20', '2700', 'IP20', 'k, l'),
    ('О15', 'LED в гардероба, датчици на вратите', '2', 'гардероб A / B', '1,80 / 2,05', '3000', 'IP20', 'm'),
    ('О16', 'Луна LED 7 W (над душа IP65)', '3', 'баня – x 531,8 / 595', 'таван', '3000', 'IP44/65', 'n + ВН'),
    ('О17', 'LED огледален шкаф 60×70×17 + 2 странични', '1+2', 'баня', '1,18 / 1,56', '3000', 'IP44', 'p'),
    ('—', 'Лампион HEKTAR, настолни лампи – в контакт', '3', 'дневна, бюро, тоалетка', '—', '2700', '—', 'контакт'),
]


def curve(ax, p0, p1, color, bend=0.18, lw=0.45):
    (x0, y0), (x1, y1) = p0, p1
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    cx, cy = mx - dy * bend, my + dx * bend
    path = Path([(x0, y0), (cx, cy), (x1, y1)], [Path.MOVETO, Path.CURVE3, Path.CURVE3])
    ax.add_patch(PathPatch(path, fc='none', ec=color, lw=lw, ls=(0, (3, 1.6)), zorder=22))
    return (0.25 * x0 + 0.5 * cx + 0.25 * x1, 0.25 * y0 + 0.5 * cy + 0.25 * y1)


def fix_xy(n, kind):
    x, y = L(n)
    if kind.startswith('wall') or kind.startswith('pic'):
        ang = int(kind[4:] if kind.startswith('wall') else kind[3:])
        if ang == 0: x = 0.0
        if ang == 180: x = G.X_E
        if ang == 90: y = G.bb('Bal_slab_floor')[1]; x -= 0.10
        return x, y, ang
    return x, y, 0


def main():
    S = Sheet('06', 'Осветление и таван', ox=50, oy=84)
    ax = S.ax
    S.walls('solid')
    S.openings(swing=False, labels=False, color='0.45')
    for it in G.FURN:   # tall / ceiling-height joinery only
        if it['key'] in (2, 3, 6, 14, 16, 18, 19, 25, 28, 32, 36):
            for sh in it['shapes']:
                S._shape(sh, '0.7', 0.22, True)
    for n, g in LEDS:
        S.line(led_line(n), lw=1.6, color=LED, ls=(0, (3, 1.2)), z=25)
    for (n, g, f) in DRIVERS:
        x0, y0, x1, y1 = G.bb(n)
        px, py = S.P(x0 + (x1 - x0) * f, (y0 + y1) / 2) if (x1 - x0) > (y1 - y0) else S.P((x0 + x1) / 2, y0 + (y1 - y0) * f)
        EL.driver(ax, px, py)
    pos = {}
    for code, n, kind, g in FIX:
        x, y, ang = fix_xy(n, kind)
        px, py = S.P(x, y)
        EL.light(ax, px, py, 'wall' if kind.startswith('wall') else ('pic' if kind.startswith('pic') else kind), ang=ang, stem=1.9)
        pos.setdefault(g, []).append((px, py))
    px, py = S.P(*G.ctr('Bath_fan')); EL.fan(ax, px, py)
    for (n, ang, kind, t, d, ha, sh) in SWITCHES:
        x, y = wallpt(n, ang); ox, oy = along(ang, sh)
        px, py = S.P(x + ox, y + oy)
        EL.switch(ax, px, py, ang, 'x' if kind == 'x2' else kind)
    # group connections: switch -> nearest fixture, then chain the fixtures
    for g, (sws, extra) in GROUPS.items():
        col = GCOL[g]
        pts = pos.get(g, []) + [S.P(*e) for e in extra]
        if g == 'e':
            pts = [S.P(*G.ctr('K_led_B'))]
        for sn in sws:
            n, ang, kind, t, d, ha, sh = SW[sn]
            x, y = wallpt(n, ang); ox, oy = along(ang, sh)
            sx, sy = S.P(x + ox, y + oy)
            a = math.radians(ang)
            sp = (sx + 2.4 * math.cos(a), sy + 2.4 * math.sin(a))
            near = min(pts, key=lambda p: math.hypot(p[0] - sp[0], p[1] - sp[1]))
            m = curve(ax, sp, near, col)
            if sn == sws[0]:
                ax.text(m[0], m[1], g, fontsize=5.0, color=col, weight='bold', ha='center', va='center', zorder=29,
                        bbox=dict(boxstyle='circle,pad=0.12', fc='white', ec=col, lw=0.4))
        order = sorted(pts, key=lambda p: (p[0], p[1]))
        for p0, p1 in zip(order[:-1], order[1:]):
            curve(ax, p0, p1, col, bend=0.10)
    # codes next to fixtures
    seen = set()
    offs = {'О1': (0, -3.4), 'О2': (0, -3.6), 'О3': (0, -3.8), 'О4': (6.0, 2.0), 'О5': (5.4, -2.2), 'О10': (-6.0, 2.4),
            'О11': (3.8, 0), 'О12': (0, -3.8), 'О14': (-9.5, 0), 'О16': (0, 3.4)}
    for code, n, kind, g in FIX:
        x, y, ang = fix_xy(n, kind)
        px, py = S.P(x, y)
        dx, dy = offs[code]
        ax.text(px + dx, py + dy, code, fontsize=4.3, ha='center', va='center', zorder=32, color='k', weight='bold',
                bbox=dict(boxstyle='square,pad=0.05', fc='white', ec='none', alpha=0.85))
    for (x, y, t) in ((1.70, 0.36, 'О9'), (2.62, 4.20, 'О7'), (2.00, 6.42, 'О6'), (0.62, 6.20, 'О8'), (5.20, 2.12, 'О15'),
                      (6.10, 4.05, 'О13'), (5.34, 1.42, 'О17')):
        S.text(x, y, t, fs=4.4, color='#8A5A00', weight='bold', z=28,
               bbox=dict(boxstyle='square,pad=0.08', fc='white', ec='none', alpha=0.9))
    # aligned grids – dimension chains
    kx = sorted(L(f'KitchenDown{i}')[0] for i in range(1, 5))
    S.dim_chain([0] + kx + [G.X_LIV1], 'x', -0.55, ref=-0.25, side=-1, fs=4.6, color='#7A4A00')
    ly = sorted([L('AisleDown0')[1], L('AisleDown1')[1], L('LivingDown0')[1], L('LivingDown1')[1], L('LivingDown2')[1]])
    S.dim_chain([0, L('KitchenDown1')[1]] + ly + [G.Y_N], 'y', -0.55, ref=-0.25, fs=4.4, color='#7A4A00')
    S.dim_chain([0, L('AisleDown0')[0], G.X_LIV1], 'x', 7.15, ref=6.99, fs=4.6, color='#7A4A00')
    hy = sorted([L('HallDown0')[1], L('HallDown1')[1]])
    S.dim_chain([0] + hy + [G.Y_COR1], 'y', 4.55, fs=4.2, color='#7A4A00', side=-1)
    S.dim_chain([G.X_COR0, L('HallDown0')[0], G.X_COR1], 'x', 2.20, fs=4.2, color='#7A4A00')
    S.dim_chain([G.X_BATH0, L('BathSpot0')[0], L('BathSpot2')[0], G.X_E], 'x', -0.55, ref=-0.25, side=-1, fs=4.4, color='#7A4A00')
    S.dim_chain([0, L('BathSpot0')[1], L('BathSpot1')[1], G.Y_BATH1], 'y', 7.15, ref=6.90, side=-1, fs=4.4, color='#7A4A00')
    S.dim_chain([0, L('KitchenDown0')[0], G.TOP_L[2]], 'x', 1.62, fs=4.0, color='#7A4A00')
    S.text(2.00, 0.75, f'ред луни y = {cm(L("KitchenDown1")[1])}', fs=4.2, color='#7A4A00', z=27,
           bbox=dict(boxstyle='square,pad=0.08', fc='white', ec='none'))
    S.text(1.20, 6.30, f'ос x = {cm(L("LivingDown0")[0])}, през {cm(ly[1] - ly[0])}', fs=4.2, color='#7A4A00', z=27,
           bbox=dict(boxstyle='square,pad=0.08', fc='white', ec='none'))
    for (n, lab_) in (('AC_indoor', 'КЛ-В1'), ('AC_bed_indoor', 'КЛ-В2')):
        S.rect(*G.bb(n), lw=0.5, ec=PUR, fc='white', ls=(0, (3, 1.5)), z=24)
    for (x, y, t) in ((1.10, 3.05, 'таван +2,60'), (5.70, 3.20, '+2,60'), (4.12, 0.95, '+2,60'), (5.30, 0.95, '+2,60'),
                      (4.95, 6.30, 'балкон +2,60')):
        S.text(x, y, t, fs=4.4, color='0.15', bbox=dict(boxstyle='square,pad=0.15', fc='white', ec='0.4', lw=0.3), z=27)
    schedule(S)
    legend(S)
    S.scale_bar(40, 16)
    S.title_block()
    S.save('06 Осветление и таван')


def schedule(S):
    ax = S.ax
    X, W = 230, 180
    top = 285
    rh = 4.4
    H = 9 + rh * len(SCHED) + 3
    S.legend_box(X, top - H, W, H)
    cols = [X + 1.5, X + 10, X + 82, X + 92, X + 132, X + 147, X + 158, X + 170]
    for cx, t in zip(cols, ['Код', 'Тип / описание', 'Бр.', 'Място', 'h, m', 'K', 'IP', 'Гр.']):
        ax.text(cx, top - 4.4, t, fontsize=5.0, weight='bold', va='center', zorder=31)
    ax.plot([X, X + W], [top - 8, top - 8], 'k', lw=0.35, zorder=31)
    for i, r in enumerate(SCHED):
        y = top - 8 - rh * (i + 0.5) - 0.5
        if i % 2:
            ax.add_patch(Rectangle((X + 0.3, y - rh / 2), W - 0.6, rh, fc='0.94', ec='none', zorder=15.5))
        for j, (cx, v) in enumerate(zip(cols, r)):
            ax.text(cx, y, v, fontsize=4.1 if j in (1, 3) else 4.3, va='center', zorder=31, weight='bold' if j == 0 else 'normal')
    for cx in cols[1:]:
        ax.plot([cx - 1.0, cx - 1.0], [top - H, top], 'k', lw=0.2, zorder=31)


def legend(S):
    ax = S.ax
    X, W = 230, 180
    top = 285 - (9 + 4.4 * len(SCHED) + 3) - 4
    H = 76
    S.legend_box(X, top - H, W, H, 'Легенда, токови кръгове и групи на включване')
    y0 = top - 11
    EL.light(ax, X + 5, y0, 'down'); EL.light(ax, X + 9.5, y0, 'downip')
    ax.text(X + 14, y0, 'Луна LED (с пръстен – IP44/65)', fontsize=4.6, va='center', zorder=31)
    EL.light(ax, X + 6, y0 - 6, 'ceil'); ax.text(X + 14, y0 - 6, 'Пендел / таванно тяло', fontsize=4.6, va='center', zorder=31)
    EL.light(ax, X + 4, y0 - 12, 'wall', ang=0); ax.text(X + 14, y0 - 12, 'Аплик / лампа за четене', fontsize=4.6, va='center', zorder=31)
    ax.plot([X + 3, X + 11], [y0 - 18, y0 - 18], color=LED, lw=1.6, ls=(0, (3, 1.2)), zorder=31)
    ax.text(X + 14, y0 - 18, 'LED лента 24 V;  Д – захранващ блок', fontsize=4.6, va='center', zorder=31)
    curve(ax, (X + 3, y0 - 24), (X + 11, y0 - 24), '#C0392B', bend=0.3)
    ax.text(X + 14, y0 - 24, 'Връзка ключ → тела (a … p)', fontsize=4.6, va='center', zorder=31)
    EL.switch(ax, X + 5, y0 - 31.5, 90, 'w'); ax.text(X + 14, y0 - 30, 'Ключ (девиаторен ↔, кръстат ✕)', fontsize=4.6, va='center', zorder=31)
    EL.fan(ax, X + 6, y0 - 36); ax.text(X + 14, y0 - 36, 'Вентилатор баня (група n)', fontsize=4.6, va='center', zorder=31)
    ax.text(X + 74, y0 + 0.5, 'Кръгове и групи (ключове h 1,05; в нишите h 0,66):', fontsize=4.8, weight='bold', va='center', zorder=31)
    ax.text(X + 74, y0 - 3,
            'L1 (B10, ДТЗ1) – дневна, кухня, балкон:\n'
            '  a◐ общи луни дневна + b луни кухня – ключ 2× при вратата;\n'
            '  c◐ пендели + d амбиент (аплици, картини, воал, библиотека,\n'
            '  ТВ модул) – втори ключ 2× при вратата; e LED кухня – ключ\n'
            '  в гърба на плота; f аплик балкон – ключ 2× при ПП1.\n'
            'L2 (B10, ДТЗ2) – коридор, спалня:\n'
            '  g луни коридор – девиатори при входа и при дневната;\n'
            '  h пендел спалня – 3 места: девиатор при вратата,\n'
            '  кръстат в лявата ниша, девиатор в дясната; i LED ниши\n'
            '  и мост – при вратата; k, l лампи за четене; m гардероб.\n'
            'L3 (B10, ДТЗ3) – баня: n луни + вентилатор (таймер,\n'
            '  хигростат); p LED огледало – ключ 2× в коридора.',
            fontsize=4.3, va='top', zorder=31, linespacing=1.35)
    ax.text(X + 3, top - H + 9.5,
            '◐ – с димер (LED, trailing-edge). 2700 K в жилищните зони, 3000 K в коридора, банята, гардероба и балкона; CRI ≥ 90.\n'
            'Таванът е 2,60 m (стоманобетон, по модела): вградените луни изискват кухина ≥ 8 cm – локален ГК таван или ниски\n'
            'луни за бетон; решава се преди изпълнение. Луните са подредени по оси (размерите в кафяво).',
            fontsize=4.2, va='top', zorder=31, linespacing=1.4, color='0.15')


if __name__ == '__main__':
    main()
