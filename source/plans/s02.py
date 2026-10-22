# -*- coding: utf-8 -*-
from common import *
import geom as G
from geom import bb, bz, wdh, c as C


def legend_rows():
    tb, tl = G.TOP_B, G.TOP_L
    R = lambda v: str(int(round(v * 100)))
    k_run = f'{R(tb[2] - tb[0])}+{R(bb("K_end_panel")[3])}×{R(tb[3] - tb[1])}×{R(bz("K_top_a")[1])}'
    ub = bb('K_upper_carc_B'); ul = bb(prefix='K_upper_carc_L')
    up = f'{R(ub[2] - ub[0])}+{R(ul[3] - ul[1])}×{R(ub[3] - ub[1])}×{R(bz("K_upper_carc_B")[1] - bz("K_upper_carc_B")[0])}'
    wu = bb(prefix='WU_end'); wu_s = f'{R(wu[3] - wu[1])}×{R(wu[2] - wu[0])}×{R(G.CEIL)}'
    dk = bb('WU_desk_slab')
    tw = bb(prefix='BW_t0')
    return [
        (1, 'Кухня – долни шкафове + плот (фурна под котлона)', 'по поръчка (лист 03.2)', k_run),
        (2, 'Хладилник свободностоящ + дъбов панел + шкаф', 'Samsung RB38C650EB1/EF, тъмен инокс', wdh('K_fridge', 'K_fridge_feet')),
        (3, 'Горни шкафове до тавана + абсорбатор телескопичен', 'по поръчка; Hansa OTP 6243 BGH', up),
        (4, 'Маса трапезна', 'JYSK AABENRAA, дъб/черни крака', wdh('Dining_top', 'Dining_leg0')),
        (5, 'Стол трапезен (×4)', 'IKEA HÖGVED, бреза, с вретена', wdh('DChair_S1')),
        (6, f'ТВ модул + бюро {C(dk[3] - dk[1])}×{C(dk[2] - dk[0])}', 'по поръчка (лист 03.3)', wu_s),
        (7, 'Телевизор 65" + саундбар', 'на стената', wdh('TV_body', along='y')),
        (8, 'Работен стол (бюро)', 'IKEA LÅNGFJÄLL', wdh('LvChair')),
        (9, 'Диван-легло 3-местен', 'IKEA LANDSKRONA – НАЛИЧЕН', wdh('Sofa', along='y')),
        (10, 'Холна маса', 'IKEA LISTERBY, дъбов фурнир', wdh('Coffee', along='y')),
        (11, 'Килим дневна', 'вълна, кремав', wdh('Rug_living', z=False)),
        (12, f'Кресло, завъртяно на {abs(round(G.LOUNGE_ANG))}°', 'IKEA EKENÄSET', '65×74×' + R(bz('Lounge')[1])),
        (13, 'Лампион', 'IKEA HEKTAR, тъмносив', 'h ' + R(bz(prefix='floorlamp_')[1])),
        (14, 'Библиотека дъб, 3 рафта, 2 чекмеджета в базата', 'по поръчка (лист 03.4)', wdh(prefix='BC_', along='y')),
        (15, 'Воал + релса (LED ниша); щора ПП1', 'IKEA TERESIA / RÄCKA', f'{C(bb("Curtain_track")[2] - bb("Curtain_track")[0])} релса'),
        (16, 'Климатик вътр. тяло, над Д2', 'Gree Pular II GWH12AGCXB/I (12k)', wdh('AC_indoor', along='y')),
        (17, 'Легло с повдигащ се матрак, ракла ~0,7 m³', 'по поръчка + матрак 160×200 (без табла)', wdh('Bed_platform', along='y')),
        (18, 'Стена зад леглото: 2 колони, мост, табла', 'дъб, ламели в нишите и зад леглото + бял мост (03.4)', f'{R(G.Y_BED1 - tw[1])}×{R(tw[2] - tw[0])}×{R(G.CEIL)}'),
        (19, 'Гардероб, 2 плъзгащи врати + панел', 'по поръчка (лист 03.4)', wdh('Wardrobe_carc', 'Wardrobe_track_bot', 'Wardrobe_filler')),
        (20, 'Тоалетка окачена + LED огледало Ø80', 'дъб, 3 чекм. + чекм. над коленете', wdh('Desk_top', along='y', z=False) + f', h {C(bz("Desk_top")[1])}'),
        (21, 'Табуретка (под тоалетката)', 'IKEA KYRRE, бреза', wdh('Desk_stool')),
        (22, 'Килим спалня, плоскотъкан', 'овес', wdh('Rug_bedroom', z=False)),
        (23, 'Кош за пране', 'JYSK DAN, морска трева', f'Ø{R(bb("Laundry_basket")[2] - bb("Laundry_basket")[0])}×{R(bz("Laundry_basket")[1])}'),
        (24, 'Щори blackout + воал (балк. врата / прозорец)', 'по размер', f'{R(bb("Blind_door_fabric")[2] - bb("Blind_door_fabric")[0])} / {R(bb("Blind_window_fabric")[2] - bb("Blind_window_fabric")[0])}'),
        (25, 'Климатик вътр. тяло, над Д3', 'Gree Pular GWH09AGBXB/I (9k)', wdh('AC_bed_indoor')),
        (26, 'Шкаф за обувки', 'IKEA STÄLL', wdh('Shoe_STALL_body', along='y')),
        (27, 'Огледало в цял ръст = вратата на банята (Д4)', 'алум. черна рамка + огледало', f'{C(bb("Hall_mirror_frame")[3] - bb("Hall_mirror_frame")[1])}×{C(bz("Hall_mirror_frame")[1] - bz("Hall_mirror_frame")[0])}'),
        (28, 'Мебел за антре: пейка, закачалки, колона', 'по поръчка (лист 03.3)', wdh(prefix='Hall_unit_', along='y')),
        (29, 'Изтривалка', 'кокос', wdh('Doormat', z=False)),
        (30, 'Плот с интегриран умивалник + шкаф препарати', 'по поръчка, solid surface', wdh('Vanity_top', 'Vanity_cab')),
        (31, 'Пералня-сушилня под плота (зад врата)', 'Electrolux EW7W368SI', wdh('Washer_body')),
        (32, 'Огледален шкаф с LED (над 30)', 'Inter Ceramic Монца', wdh('Mirror_cab')),
        (33, 'Душ без праг: страничен панел + сгъваема врата', 'REA Bler 90 + REA Rapid Fold 90, черно', wdh('Shower_floor', 'Shower_panel', 'Shower_door')),
        (34, 'Окачена тоалетна + вградено казанче', 'Cersanit Moduo; Geberit Duofix + Delta50', wdh('WC_bowl', z=False)),
        (35, 'Сушилник за кърпи, електрически', 'Atlantic Doris, черен', wdh(prefix='Towel_rail_')),
        (36, 'Бойлер 60 л, вертикален, над WC', 'Eldom Galant DU060W', wdh('Boiler', along='y')),
        (37, 'Кош за отпадъци + четка WC', 'Vinoks 5 л педал + IKEA GANSJÖN', wdh('Bath_bin')),
        (38, 'Маса + 2 сгъваеми стола', 'IKEA TÄRNÖ', wdh('Tarno_top', 'Tarno_leg0')),
        (39, 'Климатик външно тяло multi-split, на конзоли', 'Gree GWHD(18)NK6LOO', wdh('AC_outdoor', along='y')),
        (40, 'Растения в саксии', '—', '—'),
        (41, 'Сушилник за дрехи, сгъваем (зад Д3)', 'Leifheit Pegasus 150 Solid', wdh('Drying_rack', along='y')),
    ]


def clearances(S):
    d = lambda p, q, **k: S.dim_free(p, q, fs=4.8, color='#B03A2E', **k)
    tb = G.TOP_B; dn = G.DINING; sofa = G.SOFA; cof = G.COFFEE; cons = G.WU['cons']; tv = bb('TV_body')
    ch = bb('DChair_S2')
    d((ch[0] + 0.12, tb[3]), (ch[0] + 0.12, ch[1]))                      # worktop -> chair
    d((0.62, dn[3]), (0.62, sofa[1]), tside=-1)                         # table -> sofa arm
    d((sofa[2], 4.62), (cof[0], 4.62))                                  # sofa -> coffee
    d((cof[2], 4.62), (cons[0], 4.62))                                  # coffee -> console
    d((sofa[2], 5.58), (tv[0], 5.58), s=f'{C(tv[0] - sofa[2])} (диван – ТВ)')
    d((dn[2], 2.50), (G.WU['desk'][0], 2.50))                           # table -> desk
    fr = G.FRIDGE
    d((3.20, fr[3]), (3.20, bb('Wall_R_a')[3]), tside=-1)               # fridge -> door
    van = G.VAN; bed = G.BED
    d((van[2], 3.70), (bed[0], 3.70))
    d((5.20, bb('Wardrobe_filler')[3]), (5.20, bed[1]), tside=-1)
    d((5.60, bed[3]), (5.60, G.Y_BED1))
    d((bb('Shoe_STALL_body')[2], 1.60), (G.HALL['bench'][0], 1.60))
    d((G.X_COR0, 2.12), (G.HALL['d0'][0], 2.12))
    wc = bb('WC_bowl')
    d((G.X_BATH0, 0.52), (wc[0], 0.52))
    d((6.25, 0.0), (6.25, wc[1]), tside=-1)
    d((bb('Bal_frame_bot')[0] + 0.18, 6.32), (bb(prefix='Tarno_chair0')[0], 6.32))
    d((4.80, bb(prefix='Tarno_chair0')[3]), (4.80, G.RAIL[1]), tside=-1)


def main():
    S = Sheet('02', 'Мебелировка', ox=50, oy=84)
    S.walls('solid')
    S.openings(swing=True, labels=False)
    S.furniture('full')
    clearances(S)
    for k, (x, y) in {'living': (2.15, 1.30), 'corr': (4.00, 1.86), 'bed': (4.25, 3.20),
                      'bath': (5.50, 0.80), 'balc': (5.35, 6.62)}.items():
        nm = {'corr': 'Коридор', 'bath': 'Баня', 'living': 'Дневна, кухня, трапезария'}.get(k, G.ROOMS[k]['name'])
        S.text(x, y, nm.upper(), fs=5.6, weight='bold', color='0.35',
               bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='none', alpha=0.8), z=12.5)
    S.dim_chain([0, G.X_LIV1, G.X_COR0, G.X_COR1, G.X_BATH0, G.X_E], 'x', -0.75, ref=-0.25, side=-1)
    S.dim_chain([0, G.Y_N], 'y', -0.75, ref=-0.25)
    S.dim_chain([0, G.Y_BATH1, G.Y_NICHE0, G.Y_BED0, G.Y_BED1, bb('Bal_slab_floor')[1], G.RAIL[1]], 'y', 7.35, ref=6.99, side=-1)
    S.dim_chain([0, bb('Wall_T_a')[2], bb('Wall_T_b')[0], G.X_LIV1, bb('Wall_R_c')[2], G.RAIL[2]], 'x', 7.40, ref=6.99)

    LEGEND = legend_rows()
    X, W = 230, 180
    top = 284
    rh = 4.7
    h = 10 + rh * len(LEGEND) + 3
    S.legend_box(X, top - h, W, h)
    cols = [X + 2.5, X + 11, X + 92, X + 145]
    for cx, t in zip(cols, ['№', 'Наименование', 'Продукт / изпълнение', 'Ш×Д×В, cm']):
        S.ptext(cx, top - 4.5, t, 5.6, weight='bold', va='center')
    S.ax.plot([X, X + W], [top - 8, top - 8], 'k', lw=0.4, zorder=16)
    for i, (k, n, p, dims) in enumerate(LEGEND):
        y = top - 8 - rh * (i + 0.5) - 1
        if i % 2 == 1:
            S.ax.add_patch(Rectangle((X + 0.3, y - rh / 2), W - 0.6, rh, fc='0.94', ec='none', zorder=15.5))
        S.ptext(cols[0] + 2, y, str(k), 5.2, va='center', ha='center', weight='bold')
        S.ptext(cols[1], y, n, 5.0, va='center')
        S.ptext(cols[2], y, p, 4.8, va='center', color='0.2')
        S.ptext(cols[3], y, dims, 5.0, va='center')
    for cx in cols[1:]:
        S.ax.plot([cx - 1.5, cx - 1.5], [top - h, top], 'k', lw=0.25, zorder=16)
    ny = top - h - 4
    S.ptext(X, ny, 'Бележки:', 6, weight='bold', va='top')
    S.ptext(X, ny - 4.5,
            '1. Червените размери са свободни проходи/отстояния (cm) между готови повърхности.\n'
            '2. С пунктир – елементи над нивото на сечението (горни шкафове, мост над леглото, климатици, бойлер, пералня).\n'
            '3. Мебелите по поръчка се изработват по замерване на място след шпакловка/плочки. Подробно – листове 03.\n'
            '4. Ш×Д×В – ширина × дълбочина × височина, cm (по 3D модела). Диванът (9) е наличен.',
            4.9, va='top', linespacing=1.45)
    S.scale_bar(52, 27)
    S.title_block()
    return S.save('02 Мебелировка')


if __name__ == '__main__':
    main()
