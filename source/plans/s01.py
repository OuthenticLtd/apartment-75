# -*- coding: utf-8 -*-
from common import *
import geom as G
from matplotlib.patches import Rectangle


def floor_patterns(S, faint=False):
    c_t, c_l = ('0.55', '0.75') if not faint else ('0.8', '0.85')
    # bathroom tiles 60x60, grid from the bathroom corner (x 4.89, y 0)
    for (x0, y0, x1, y1) in G.TILE_ZONES:
        S.rect(x0, y0, x1, y1, lw=0, fc='0.93', z=1.5)
        gx0 = G.X_BATH0
        yy = 0.60
        while yy < y1 - 0.01:
            if yy > y0 + 0.01: S.line([(x0, yy), (x1, yy)], lw=0.15, color=c_t, z=2)
            yy += 0.60
        xx = gx0 + 0.60
        while xx < x1 - 0.01:
            if xx > x0 + 0.01: S.line([(xx, y0), (xx, y1)], lw=0.15, color=c_t, z=2)
            xx += 0.60
    # SPC vinyl: planks along y, ~22 cm wide, continuous through all doorways
    for (x0, y0, x1, y1) in G.VINYL_ZONES:
        xx = (int(x0 / 0.22) + 1) * 0.22
        while xx < x1 - 0.02:
            S.line([(xx, y0), (xx, y1)], lw=0.12, color=c_l, z=2)
            xx += 0.22
    x0, y0, x1, y1 = G.DECK_ZONE
    S.rect(x0, y0, x1, y1, lw=0, fc='0.86', z=1.5)
    xx = x0 + 0.30
    while xx < x1:
        S.line([(xx, y0), (xx, y1)], lw=0.15, color='0.5', z=2); xx += 0.30
    yy = y0 + 0.30
    while yy < y1:
        S.line([(x0, yy), (x1, yy)], lw=0.15, color='0.5', z=2); yy += 0.30
    for (p, q) in G.PROFILES:
        S.line([p, q], lw=1.2, color='0.25', z=3)


def room_label(S, k, x, y, fin, extra=None, fs=7.2, name=None):
    r = G.ROOMS[k]
    a = G.room_area(k)
    S.text(x, y + 0.20 + (0.08 if name else 0), name or r['name'], fs=fs, weight='bold',
           bbox=dict(boxstyle='square,pad=0.25', fc='white', ec='none', alpha=0.9))
    S.text(x, y - 0.02, f'П = {fmt(a)} m²', fs=fs - 0.6,
           bbox=dict(boxstyle='square,pad=0.2', fc='white', ec='none', alpha=0.9))
    S.text(x, y - 0.22, fin + ('' if k == 'balc' else f'   h = {fmt(r["h"])}'), fs=fs - 1.8, color='0.25',
           bbox=dict(boxstyle='square,pad=0.2', fc='white', ec='none', alpha=0.9))




def built_ins(S):
    """Fixed kitchen, joinery and sanitary items, faint, for orientation."""
    S.furniture('faint', skip=[k for k in G.KEYS if k not in (1, 2, 6, 14, 18, 19, 28, 30, 33, 34)])


def main():
    S = Sheet('01', 'Разпределение', ox=50, oy=84)
    floor_patterns(S)
    built_ins(S)
    S.walls('hatch')
    S.openings(swing=True)
    bb = G.bb
    tags = [(2.80, 2.05, 'Д2 90/200'), (4.05, 2.70, 'Д3 80/200'), (4.20, -0.55, 'Д1 100/210'),
            (4.30, 1.02, f"{G.POCKET['tag']} {G.POCKET['txt']}\nплъзгаща"),
            (2.62, 6.06, 'ПП1 80/238'), (4.27, 4.86, 'ПП2 80/238'),
            (1.70, 7.12, 'ПП3 261/238'), (5.43, 4.86, 'ПП4 151/238')]
    for (x, y, t) in tags:
        S.text(x, y, t, fs=5.0, color='0.15', bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none'), z=13)

    room_label(S, 'living', 1.65, 4.15, 'под: Н1')
    room_label(S, 'corr', 4.05, 1.68, 'под: Н1', fs=5.5, name='Преддверие /\nкоридор')
    room_label(S, 'bed', 5.25, 3.95, 'под: Н1')
    room_label(S, 'bath', 5.33, 0.64, 'под: Н2', fs=5.6)
    room_label(S, 'balc', 4.65, 6.33, 'под: Н3', fs=6.0)

    X1, Y1 = G.X_E, G.Y_N
    S.dim_chain([0, G.X_LIV1, G.X_COR0, G.X_COR1, G.X_BATH0, X1], 'x', -0.85, ref=-0.25, side=-1)
    S.dim_chain([-0.25, bb('W2_B_a')[2], bb('W2_B_b_0')[0], 6.90], 'x', -1.35, ref=-0.25, side=-1)
    S.dim_chain([-0.25, 6.90], 'x', -1.85, ref=-0.25, side=-1)
    S.dim_chain([0, bb('Wall_T_a')[2], bb('Wall_T_b')[0], G.X_LIV1, bb('Wall_R_c')[2], G.RAIL[2]], 'x', 7.45, ref=6.99)
    S.dim_chain([-0.25, bb('Wall_R_c')[2], G.RAIL[2], 6.90], 'x', 7.95, ref=6.99)
    S.dim_chain([-0.25, 6.90], 'x', 8.45, ref=6.99)
    S.dim_chain([-0.25, 0, Y1, 6.90], 'y', -0.80, ref=-0.25)
    S.dim_chain([-0.25, 6.90], 'y', -1.30, ref=-0.25)
    S.dim_chain([0, G.Y_BATH1, G.Y_NICHE0, G.Y_BED0, G.Y_BED1, bb('Bal_slab_floor')[1], G.RAIL[1]], 'y', 7.40, ref=6.99, side=-1)
    S.dim_chain([-0.25, bb('Bal_slab_floor')[1], 6.99], 'y', 7.90, ref=6.99, side=-1)
    S.dim_chain([-0.25, 6.99], 'y', 8.40, ref=6.99, side=-1)
    S.dim_chain([0, G.X_LIV1], 'x', 5.25, fs=5.3)
    S.dim_chain([0, bb('Wall_R_a')[3], bb('Wall_R_b_0')[1], bb('Wall_R_b_1')[3], bb('Wall_R_c')[1], Y1], 'y', 3.12, fs=5.0, side=1)
    S.dim_chain([G.X_COR0, G.X_COR1], 'x', 2.05, fs=5.0)
    S.dim_chain([0, G.Y_COR1], 'y', 4.40, fs=5.0, side=-1)
    S.dim_chain([0, G.POCKET['gap'][1], G.POCKET['gap'][3], G.Y_COR1], 'y', 4.62, fs=4.8, side=1)
    S.dim_chain([G.X_COR0, X1], 'x', 2.78, fs=5.3)
    S.dim_chain([G.Y_BED0, G.Y_BED1], 'y', 4.15, fs=5.3)
    S.dim_chain([G.Y_NICHE0, G.Y_BED0], 'y', 6.45, fs=4.8, side=-1)
    S.dim_chain([G.X_BATH0, X1], 'x', 1.85, fs=5.0, side=1)
    S.dim_chain([G.X_COR0, bb('BedBalDoor_fB')[0], bb('BedBalDoor_fB')[2], bb('BedWin_fB')[2], X1], 'x', 5.12, fs=4.8, side=-1)
    S.dim_chain([0, G.Y_BATH1], 'y', 6.47, fs=4.8, side=-1)
    S.dim_chain([bb('Bal_slab_floor')[1], G.RAIL[1]], 'y', 6.22, fs=5.0, side=1)

    X = 236; W = 174
    ax = S.ax
    y = 252; h = 34
    S.legend_box(X, y, W, h, 'Легенда')
    def sw(x, yy, **k):
        ax.add_patch(Rectangle((x, yy), 10, 4.5, zorder=17, **k))
    sw(X + 3, y + 21, fc='white', ec='k', lw=0.6, hatch='//////')
    S.ptext(X + 15, y + 23.2, 'Външни и носещи стени', 5.6, va='center', zorder=17)
    sw(X + 3, y + 14.5, fc='0.72', ec='k', lw=0.5)
    S.ptext(X + 15, y + 16.7, 'Преградни стени (12 cm; 24 cm към нишата)', 5.6, va='center', zorder=17)
    ax.plot([X + 3, X + 13], [y + 10.2, y + 10.2], color='0.25', lw=1.2, zorder=17)
    S.ptext(X + 15, y + 10.2, 'Лайсна винил/плочки (само при Д4)', 5.4, va='center', zorder=17)
    S.ptext(X + 3, y + 4.2, 'Размери в cm, светли (до готова стена) по 3D модела – да се проверят на място.',
            5.0, va='center', zorder=17, color='0.25')
    X2 = X + 92
    for i, (code, txt, kind) in enumerate([
            ('Н1', 'SPC винил, вид дъб – един непрекъснат\nпод навсякъде без банята, без прагове', 'lam'),
            ('Н2', 'Гранитогрес Star Gres Town\nAntracite 60×60 (баня и душ)', 'tile'),
            ('Н3', 'Декинг IKEA RUNNEN 30×30,\nтъмно сив (сух монтаж)', 'deck')]):
        yy = y + 20.5 - i * 8.0
        ax.add_patch(Rectangle((X2, yy), 10, 6, fc='0.86' if kind == 'deck' else ('0.93' if kind == 'tile' else 'white'),
                               ec='k', lw=0.4, zorder=17))
        if kind == 'tile':
            ax.plot([X2 + 5, X2 + 5], [yy, yy + 6], color='0.5', lw=0.3, zorder=17.1)
            ax.plot([X2, X2 + 10], [yy + 3, yy + 3], color='0.5', lw=0.3, zorder=17.1)
        elif kind == 'lam':
            for k in range(1, 5):
                ax.plot([X2 + 2 * k, X2 + 2 * k], [yy, yy + 6], color='0.6', lw=0.3, zorder=17.1)
        else:
            for k in (2, 4):
                ax.plot([X2, X2 + 10], [yy + k * 1.5 - 0.5, yy + k * 1.5 - 0.5], color='0.4', lw=0.3, zorder=17.1)
            for k in (3.3, 6.6):
                ax.plot([X2 + k, X2 + k], [yy, yy + 6], color='0.4', lw=0.3, zorder=17.1)
        S.ptext(X2 + 12, yy + 3, code, 6.0, weight='bold', va='center', zorder=17)
        S.ptext(X2 + 19, yy + 3, txt, 4.9, va='center', zorder=17, linespacing=1.15)

    y = 184; h = 64
    S.legend_box(X, y, W, h, 'Площи (нето, по 3D модела)')
    cols = [X + 3, X + 74, X + 104, X + 132, X + 152]
    ty = y + h - 10.5
    for cx, t in zip(cols, ['Помещение', 'Площ, m²', 'по арх. план', 'Под', 'h, m']):
        S.ptext(cx, ty, t, 5.4, weight='bold', va='center', zorder=17)
    rows = [('1', 'living', 'Н1'), ('2', 'corr', 'Н1'), ('3', 'bed', 'Н1'), ('4', 'bath', 'Н2')]
    tot = 0
    for i, (n, k, fin) in enumerate(rows):
        yy = ty - 6.2 * (i + 1)
        a = G.room_area(k); tot += a
        S.ptext(cols[0], yy, f'{n}. {G.ROOMS[k]["name"]}', 5.4, va='center', zorder=17)
        S.ptext(cols[1] + 14, yy, fmt(a), 5.4, va='center', ha='right', zorder=17)
        S.ptext(cols[2] + 14, yy, fmt(G.ROOMS[k]['arch']), 5.4, va='center', ha='right', zorder=17, color='0.35')
        S.ptext(cols[3], yy, fin, 5.4, va='center', zorder=17)
        S.ptext(cols[4], yy, fmt(G.ROOMS[k]['h']), 5.4, va='center', zorder=17)
    yy = ty - 6.2 * 5
    ax.plot([X + 2, X + W - 2], [yy + 3.1, yy + 3.1], 'k', lw=0.3, zorder=17)
    S.ptext(cols[0], yy, 'Общо жилищна площ', 5.4, va='center', zorder=17, weight='bold')
    S.ptext(cols[1] + 14, yy, fmt(tot), 5.4, va='center', ha='right', zorder=17, weight='bold')
    S.ptext(cols[2] + 14, yy, fmt(sum(G.ROOMS[k]['arch'] for _, k, _ in rows)), 5.4, va='center', ha='right', zorder=17, color='0.35')
    yy -= 6.2
    S.ptext(cols[0], yy, '5. Балкон (нето, до парапета)', 5.4, va='center', zorder=17)
    S.ptext(cols[1] + 14, yy, fmt(G.room_area('balc')), 5.4, va='center', ha='right', zorder=17)
    S.ptext(cols[2] + 14, yy, fmt(G.ROOMS['balc']['arch']), 5.4, va='center', ha='right', zorder=17, color='0.35')
    S.ptext(cols[3], yy, 'Н3', 5.4, va='center', zorder=17)
    S.ptext(X + 3, y + 9.5, 'Разликите спрямо архитектурния план идват от ниши, первази и дебелина на парапета;\n'
            'площта на спалнята включва нишата на гардероба.',
            4.7, va='center', zorder=17, color='0.3', linespacing=1.3)

    y = 104; h = 76
    S.legend_box(X, y, W, h, 'Врати и прозорци (ширина/височина на отвора, cm)')
    pk = G.POCKET
    rows = [('Д1', '100/210', 'Входна врата, блиндирана, отваряне навътре; бутон звънец отвън'),
            ('Д2', '90/200', 'Интериорна врата дневна, към дневната; над нея вътр. тяло климатик'),
            ('Д3', '80/200', 'Интериорна врата спалня, към спалнята; над нея вътр. тяло климатик'),
            ('Д4', pk['txt'], 'Баня: плъзгаща врата в стената (касета Eclisse / Scrigno), крило алуминиева черна рамка + огледало от двете страни,'),
            ('', '', 'крило 82×205, светъл отвор ~80, прибира се в преградата към коридора'),
            ('ПП1', '80/238', 'Балконска врата от дневната, обръщаемо-наклоняема'),
            ('ПП2', '80/238', 'Балконска врата от спалнята, обръщаемо-наклоняема'),
            ('ПП3', '261/238', 'Витрина дневна, 3 полета, едно обръщаемо-наклоняемо крило'),
            ('ПП4', '151/238', 'Витрина спалня, неотваряема, 2 полета')]
    for i, (t, d, txt) in enumerate(rows):
        yy = y + h - 11 - i * 6.9
        S.ptext(X + 3, yy, t, 5.6, weight='bold', va='center', zorder=17)
        S.ptext(X + 15, yy, d, 5.6, va='center', zorder=17)
        S.ptext(X + 33, yy, txt, 5.1, va='center', zorder=17)

    S.ptext(X, 97, 'Бележки:', 6, weight='bold', va='top')
    S.ptext(X, 92.5,
            '1. Геометрията е по текущия 3D модел на интериора, сверена с архитектурния план (Ап. 75 А).\n'
            '2. Отворите на прозорците/балконските врати (ПП) са съществуващи – да не се променят.\n'
            '3. Таванът е 2,60 m навсякъде (по модела) – да се измери на място.\n'
            '4. Банята и душът са без праг (линеен трап) – вижте лист 05 ВиК.\n'
            '5. Преградата баня/коридор (касета на Д4) се приема за неносеща – ДА СЕ ПРОВЕРИ на място.\n'
            '6. Подът Н1 е един непрекъснат винил без прагове; единствената лайсна е при Д4.',
            5.1, va='top', linespacing=1.45)
    S.scale_bar(52, 27)
    S.title_block()
    return S.save('01 Разпределение')


if __name__ == '__main__':
    main()
