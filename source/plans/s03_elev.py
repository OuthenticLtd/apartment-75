# -*- coding: utf-8 -*-
"""Sheets 03.2 (kitchen) and 03.3 (TV/desk unit, wardrobe, arched bookcase) – elevations 1:25."""
from common import *
import geom as G
from shapely.geometry import box as sbox
from matplotlib.patches import Rectangle, Arc

S25 = 40.0
OAK = '#E9D8BC'; WHITE = '#FAF7F0'; STONE = '#E3DED6'; CARC = '#F2F2F2'; DARK = '#555555'


class E:
    """Elevation helper on a Sheet: u horizontal (m), z vertical (m)."""
    def __init__(self, S, ox, oy, title, sub=None, sc=S25):
        self.S = S; self.ox, self.oy = ox, oy
        self.title, self.sub = title, sub
        self.sc = sc

    def on(self):
        self.S.ox, self.S.oy, self.S.S = self.ox, self.oy, self.sc

    def r(self, u0, z0, u1, z1, fc='white', lw=0.35, ls='-', hatch=None, z=6, ec='k'):
        self.on(); return self.S.rect(min(u0, u1), z0, max(u0, u1), z1, lw=lw, fc=fc, ls=ls, hatch=hatch, z=z, ec=ec)

    def l(self, pts, lw=0.3, ls='-', color='k', z=7):
        self.on(); self.S.line(pts, lw=lw, ls=ls, color=color, z=z)

    def t(self, u, v, s, fs=5.0, **k):
        self.on(); return self.S.text(u, v, s, fs=fs, **k)

    def call(self, u, z, tu, tz, s, fs=4.8, ha='left'):
        self.on()
        self.S.line([(u, z), (tu, tz)], lw=0.2, color='0.2', z=12)
        self.S.circle(u, z, 0.008, lw=0.3, fc='k', z=12)
        self.S.text(tu + (0.03 if ha == 'left' else -0.03), tz, s, fs=fs, ha=ha, va='center', color='0.1',
                    bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='none'))

    def dimc(self, vals, axis, at, ref=None, side=1, fs=5.0, labels=None):
        self.on(); self.S.dim_chain(vals, axis, at, ref=ref, side=side, fs=fs, labels=labels)

    def head(self, u0, u1, ztop, letter=''):
        self.on()
        x0, y = self.S.P(u0, ztop)
        self.S.ax.text(x0, y + 12, self.title, fontsize=7.5, weight='bold', va='bottom', zorder=20)
        if self.sub:
            self.S.ax.text(x0, y + 8.5, self.sub, fontsize=5.3, color='0.3', va='bottom', zorder=20)
        self.S.ax.plot([x0, x0 + 70], [y + 11.3, y + 11.3], 'k', lw=0.5, zorder=20)

    def floor_ceiling(self, u0, u1, h=2.60, ceil=True):
        self.l([(u0 - 0.12, 0), (u1 + 0.12, 0)], lw=0.8)
        self.on()
        for i in range(int((u1 - u0 + 0.24) / 0.05)):
            uu = u0 - 0.12 + i * 0.05
            self.S.line([(uu, 0), (uu - 0.04, -0.04)], lw=0.2, color='0.3', z=6)
        if ceil:
            self.l([(u0 - 0.12, h), (u1 + 0.12, h)], lw=0.6)
            for i in range(int((u1 - u0 + 0.24) / 0.05)):
                uu = u0 - 0.12 + i * 0.05
                self.S.line([(uu, h), (uu + 0.04, h + 0.04)], lw=0.2, color='0.3', z=6)


def drawers(e, u0, u1, zs, fc=OAK, pull=True):
    for (a, b) in zs:
        e.r(u0, a, u1, b, fc=fc, lw=0.3)
    if pull:
        e.l([(u0 + 0.01, zs[-1][1] - 0.025), (u1 - 0.01, zs[-1][1] - 0.025)], lw=0.15, color='0.4')


def door(e, u0, u1, z0, z1, fc, hinge=None, z=6):
    e.r(u0, z0, u1, z1, fc=fc, lw=0.3, z=z)
    if hinge:  # opening triangle (dashed) – apex on hinge side
        m = (z0 + z1) / 2
        hu, ou = (u0, u1) if hinge == 'L' else (u1, u0)
        e.l([(ou, z0), (hu, m), (ou, z1)], lw=0.15, ls=(0, (3, 2)), color='0.45', z=z + 0.1)



USE_BG = {'cutlery': 'прибори', 'utensils': 'прибори за готвене', 'plates': 'чинии', 'spices/tea': 'подправки / чай',
          'corner side': 'ъглов шкаф', 'dish drainer rack (over sink)': 'сушилник за съдове',
          'glasses (over DW)': 'чаши', 'everyday plates': 'чинии всеки ден'}


def rz(e, name, fc, U=None, axis=0, z=6, lw=0.3, ls='-', ec='k'):
    """draw export object `name` in an elevation: axis 0 -> u from x, 1 -> u from y; U maps model coord -> u."""
    b = G.b3(name)
    a0, a1 = b[axis], b[axis + 3]
    u0, u1 = (U(a0), U(a1)) if U else (a0, a1)
    return e.r(min(u0, u1), b[2], max(u0, u1), b[5], fc=fc, lw=lw, z=z, ls=ls, ec=ec)


def uc(U, name, axis):
    b = G.b3(name); return U((b[axis] + b[axis + 3]) / 2)


# =============================================================================== 03.2 KITCHEN
def kitchen():
    S = Sheet('03.2', 'Кухня – план и изгледи', scale='1:25, 1:50')
    bb, bz = G.bb, G.bz
    sx0, sy0, sx1, sy1 = G.SINK
    sxc = (sx0 + sx1) / 2
    hx0, hy0, hx1, hy1 = G.HOB
    fr = G.FRIDGE; fp = bb('K_fridge_panel'); run_end = fp[0]
    ep = bb('K_end_panel')
    # ---------------- plan 1:50
    S.ox, S.oy, S.S = 62, 34, 20.0
    clip = sbox(-0.25, -0.25, 3.47, 2.05)
    ext, part = G.wall_polys()
    S.shp(ext.intersection(clip), fc='white', ec='k', lw=0.0, hatch='//////', z=6)
    S.shp(ext.intersection(clip), fc='none', ec='k', lw=0.7, z=6.1)
    S.shp(part.intersection(clip), fc='0.72', ec='k', lw=0.55, z=6)
    for it in G.FURN:
        if it['key'] in (1, 2, 3):
            for sh in it['shapes']:
                S._shape(sh, 'k', 0.4, False)
    od = bb('K_oven_door'); dl = bb('K_drawerL0')
    S.rect(0.04, od[1], od[0] - 0.02, od[3], lw=0.25, ls=(0, (2, 1)), z=8.3)
    S.text(0.30, 0.30, 'ъгъл\nLeMans', fs=4.4); S.text((fr[0] + fr[2]) / 2, 0.45, 'ХЛ', fs=5.0,
                                                    bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='none'))
    S.text(0.86, (dl[1] + dl[3]) / 2, '← 18', fs=4.4)
    S.text(0.86, 0.80, '← фурна\nпод\nкотлона', fs=4.2, ha='left')
    for nm in ('KitchenDown0', 'KitchenDown1', 'KitchenDown2', 'KitchenDown3', 'KitchenDown4'):
        x, y = G.lpos(nm)[:2]
        S.circle(x, y, 0.04, lw=0.4, ec='#7A4A00', z=12)
        S.circle(x, y, 0.015, lw=0.3, ec='#7A4A00', fc='#7A4A00', z=12)
    S.text(2.05, 0.92, 'луни на тавана (лист 06)', fs=4.2, color='#7A4A00')
    for (x, y, a, t) in ((1.70, 1.35, 270, 'A'), (1.05, 1.15, 180, 'Б')):
        px, py = S.P(x, y)
        S.ax.add_patch(Circle((px, py), 2.6, fc='white', ec='k', lw=0.5, zorder=14))
        S.ax.text(px, py, t, fontsize=6.5, ha='center', va='center', weight='bold', zorder=15)
        dx, dy = math.cos(math.radians(a)) * 4.6, math.sin(math.radians(a)) * 4.6
        S.ax.annotate('', xy=(px + dx, py + dy), xytext=(px + dx * 0.62, py + dy * 0.62),
                      arrowprops=dict(arrowstyle='-|>', color='k', lw=0.6), zorder=15)
    fx = [bb(n) for n, _ in G.K_FRONTS_B]
    S.dim_chain([0, fx[0][0] - 0.003, fx[1][0] - 0.003, fx[2][0] - 0.003, fx[3][0] - 0.003, run_end, fr[0], fr[2], G.X_LIV1],
                'x', -0.60, ref=-0.25, side=-1, fs=4.2)
    S.dim_chain([0, sxc, run_end], 'x', -0.95, ref=-0.25, side=-1, fs=4.6, labels=[f'ос мивка {cm(sxc)}', None])
    S.dim_chain([0, hy0, hy1, ep[3]], 'y', -0.65, ref=-0.25, fs=4.6)
    S.dim_chain([0, od[1] - 0.003, dl[1] - 0.003, ep[1]], 'y', -1.00, ref=-0.25, fs=4.4)
    S.ax.text(42, 34 + 2.05 * 20 + 6, 'ПЛАН КУХНЯ  М 1:50 (ключ към изгледите)', fontsize=7.0, weight='bold', zorder=20)

    # ---------------- elevation A: wall y=0, looking -y (u = 3.35 - x)
    A = E(S, 74, 150, 'ИЗГЛЕД А – стена при входа (y = 0)', 'М 1:25; гледано от трапезарията към стената; Г-частта в разрез')
    U = lambda x: G.X_LIV1 - x
    A.floor_ceiling(0, 3.35)
    A.l([(0, 0), (0, 2.60)], lw=0.8); A.l([(3.35, 0), (3.35, 2.60)], lw=0.8)
    fz = bz('K_fridge')
    rz(A, 'K_fridge', '#3C3C3C', U, lw=0.45)
    gz = bz('K_fridge_gap'); A.l([(U(fr[2]), gz[0]), (U(fr[0]), gz[0])], lw=0.4, color='0.75')
    for nm in ('K_fridge_handle_b', 'K_fridge_handle_t'):
        rz(A, nm, '0.15', U, z=7, lw=0.2)
    rz(A, 'K_fridge_feet', '0.2', U, lw=0.2)
    rz(A, 'K_fridge_panel', OAK, U, z=6.5, lw=0.45)
    rz(A, 'K_fridge_upper_front', WHITE, U)
    rz(A, 'K_plinth_B', DARK, U, lw=0.2)
    rz(A, 'K_plinth_step', '0.45', U, z=6.2, lw=0.25)
    for n, _ in G.K_FRONTS_B[:3]:
        rz(A, n, OAK, U)
    for i in range(3):
        rz(A, f'K_front_drawer{i}', OAK, U)
    rz(A, 'K_pull_B', '0.25', U, z=6.4, lw=0.15)
    rz(A, 'K_end_panel', OAK, U, z=6.6, lw=0.45)
    A.r(U(ep[2]), 0.10, U(0.0), 0.86, fc='white', hatch='////', lw=0.4, z=6.55)
    A.r(U(ep[2]), 0.0, U(0.0), 0.10, fc=DARK, lw=0.2, z=6.55)
    A.r(U(ep[2]), 0.86, U(0.0), 0.90, fc=STONE, hatch='xxxx', lw=0.4, z=6.7)
    A.r(U(run_end), 0.86, U(ep[2]), 0.90, fc=STONE, lw=0.45)
    rz(A, 'K_splash_B', STONE, U, z=5, lw=0.25)
    A.r(U(sx1), 0.69, U(sx0), 0.86, fc='none', ls=(0, (3, 1.5)), lw=0.3, z=7)
    rz(A, 'K_faucet', 'k', U, z=7.2, lw=0.2); rz(A, 'K_faucet_spout', 'k', U, z=7.2, lw=0.2)
    rz(A, 'K_coffee', '#3A3A3A', U, z=7, lw=0.3)
    for nm in ('K_socket_prep', 'K_socket_coffee', 'K_switch_led'):
        rz(A, nm, 'k', U, z=7.2, lw=0.2)
    for nm in ('K_conn_dw', 'K_conn_fridge'):
        rz(A, nm, 'none', U, z=9, lw=0.5, ls=(0, (2, 1.2)))
    for i in range(5):
        rz(A, f'K_upper_front_B{i}', WHITE, U)
    A.r(U(0.35), 1.45, U(0.0), 2.598, fc='white', hatch='////', lw=0.4)
    lb = bb('K_led_B'); A.l([(U(lb[2]), 1.44), (U(lb[0]), 1.44)], lw=1.4, color='#E0A030')
    L = -0.36
    A.call(uc(U, 'K_fridge', 0), 1.30, L, 1.20, 'хладилник свободностоящ, тъмен инокс\nSamsung RB38C650EB1/EF;\nзад него щранг + водомер', ha='right', fs=4.2)
    A.call(uc(U, 'K_fridge_upper', 0), 2.34, L, 2.45, f'шкаф над хладилника,\nh {cm(bz("K_fridge_upper")[0])}–260; контакт ХЛ вътре', ha='right', fs=4.2)
    A.call(uc(U, 'K_fridge_panel', 0), 1.85, L, 1.85, 'дъбов панел до тавана', ha='right', fs=4.2)
    A.call(uc(U, 'K_plinth_step', 0), 0.05, L, 0.05, 'сгъваемо стъпало в цокъла', ha='right', fs=4.2)
    A.call(uc(U, 'K_front_drawer0', 0), 0.78, U(2.25), -0.30, 'чекмеджета 55: прибори / за готвене / чинии', fs=4.2)
    A.call(uc(U, 'K_front_dw', 0), 0.45, U(1.92), -0.48, 'съдомиялна 45, вградена; контакт зад долното чекм.', fs=4.2)
    A.call(uc(U, 'K_front_sink_bins', 0), 0.40, U(1.40), -0.66, 'шкаф мивка 60: кошове 2×18 + 8 л', fs=4.2)
    A.call(uc(U, 'K_front_corner_door', 0), 0.40, U(0.85), -0.84, 'ъгъл: LeMans II 450 зад врата 50', fs=4.2)
    A.call(uc(U, 'K_socket_prep', 0), 1.11, 2.60, 1.36, 'контакт 2× + ключ LED, h 111', fs=4.0)
    A.call(uc(U, 'K_socket_coffee', 0), 1.11, 1.30, 1.20, 'контакт 2×, h 111', fs=4.0)
    A.call(uc(U, 'K_coffee', 0), 1.20, 0.95, 1.37, 'кафемашина', fs=4.0)
    A.call(U(sxc), 1.30, 2.02, 1.37, f'черна мивка, ос x {cm(sxc)}', fs=4.0)
    for i in range(5):
        n = f'K_upper_front_B{i}'
        A.t(uc(U, n, 0), 2.05, USE_BG.get(G.prop(n, 'use'), '').replace(' ', '\n', 1), fs=4.0, color='0.35', z=8)
    us = [U(v) for v in (run_end, 2.153, 1.703, 1.103, 0.603)]
    A.dimc([0, U(run_end), U(2.150), U(1.700), U(1.100), U(ep[2]), 3.35], 'x', -1.10, ref=0, side=-1, fs=4.2)
    A.dimc([0, U(run_end), U(2.150), U(1.700), U(1.100), U(0.600), U(0.35), 3.35], 'x', 2.75, ref=2.60, fs=4.2)
    A.dimc([0, 0.10, 0.86, 0.90, 1.45, 2.60], 'y', 3.55, ref=3.35, side=-1, fs=4.6)
    A.dimc([0, fz[1], bz('K_fridge_upper')[0], 2.60], 'y', -0.22, ref=0, fs=4.4)
    A.head(0, 3.35, 2.75)

    # ---------------- elevation Б: wall x=0, looking -x (u = y)
    B = E(S, 268, 150, 'ИЗГЛЕД Б – стена с котлона (x = 0)', 'М 1:25; ъгълът (y 0–60) е в разрез')
    B.floor_ceiling(0, 1.42)
    B.l([(0, 0), (0, 2.60)], lw=0.8)
    B.r(0.0, 0.10, 0.60, 0.86, fc='white', hatch='////', lw=0.4)
    B.r(0.0, 0.0, 0.50, 0.10, fc=DARK, lw=0.2)
    B.r(0.0, 0.86, 0.62, 0.90, fc=STONE, hatch='xxxx', lw=0.4)
    B.r(0.0, 1.45, 0.35, 2.598, fc='white', hatch='////', lw=0.4)
    rz(B, 'K_plinth_L', DARK, axis=1, lw=0.2)
    rz(B, 'K_oven_drawer', OAK, axis=1)
    rz(B, 'K_oven_door', '#2E2E2E', axis=1, lw=0.35)
    od = bb('K_oven_door'); odz = bz('K_oven_door')
    B.r(od[1] + 0.05, odz[0] + 0.08, od[3] - 0.05, odz[1] - 0.10, fc='#4A4A4A', lw=0.2, z=6.2)
    rz(B, 'K_oven_panel', '#2E2E2E', axis=1)
    rz(B, 'K_oven_handle', '0.75', axis=1, z=6.3, lw=0.2)
    rz(B, 'K_drawerL0', OAK, axis=1)
    rz(B, 'K_top_L', STONE, axis=1, lw=0.45)
    rz(B, 'K_hob', 'k', axis=1, lw=0.2, z=6.5)
    rz(B, 'K_splash_L', STONE, axis=1, lw=0.25, z=5)
    rz(B, 'K_end_panel', OAK, axis=1, lw=0.4)
    for nm in ('K_conn_hob', 'K_conn_oven', 'K_conn_hood'):
        rz(B, nm, 'none', axis=1, z=9, lw=0.5, ls=(0, (2, 1.2)))
    for nm in ('K_upper_front_L0', 'K_upper_front_L1', 'K_upper_front_L2'):
        rz(B, nm, WHITE, axis=1)
    rz(B, 'K_hood', '#3A3A3A', axis=1, lw=0.35)
    for nm in ('K_led_L0', 'K_led_L1'):
        b_ = bb(nm); B.l([(b_[1], 1.44), (b_[3], 1.44)], lw=1.4, color='#E0A030')
    hc = (hy0 + hy1) / 2
    CU = 1.60
    B.call(hc, 1.575, CU, 1.66, 'абсорбатор телескопичен 60\nHansa OTP 6243 BGH, черен;\nрециркулация (въгл. филтър)', fs=4.2)
    B.call(hc, 0.905, CU, 1.06, f'индукционен котлон\ny {cm(hy0)}–{cm(hy1)}', fs=4.2)
    B.call(hc, 0.50, CU, 0.66, 'фурна Hansa BOES68465\nпод котлона', fs=4.2)
    B.call(hc, 0.17, CU, 0.40, 'чекмедже под фурната', fs=4.2)
    B.call(uc(None or (lambda v: v), 'K_drawerL0', 1), 0.30, CU, 0.18, 'изтеглящ се шкаф 18;\nзад него контакт фурна h 30', fs=4.2)
    B.call(uc(lambda v: v, 'K_conn_hob', 1), 0.55, CU, -0.08, 'кутия котлон 400 V / 32 A, h 55', fs=4.2)
    B.call(uc(lambda v: v, 'K_conn_hood', 1), 1.90, CU, 2.05, 'контакт абсорбатор\nв горния шкаф, h 190', fs=4.2)
    B.call(hc, 2.30, CU, 2.40, 'шкаф над абсорбатора', fs=4.2)
    B.call(0.20, 0.45, -0.14, -0.30, 'разрез през ъгъла', fs=4.4, ha='left')
    B.dimc([0, 0.60, dl[1] - 0.003, ep[1], ep[3]], 'x', -0.55, ref=0, side=-1, fs=4.4)
    B.dimc([0, hy0, hy1, ep[3]], 'x', -0.80, ref=0, side=-1, fs=4.4)
    B.dimc([0.35, bb('K_upper_carc_L1')[1], bb('K_upper_carc_L1')[3], bb('K_upper_carc_L2')[3]], 'x', 2.75, ref=2.60, fs=4.6)
    B.dimc([0, 0.10, odz[0], odz[1], 0.90, 1.45, 1.60, 2.60], 'y', -0.25, ref=0, fs=4.0)
    B.head(0, 1.42, 2.75)

    X = 232; y = 112
    S.ptext(X, y, 'Изпълнение / материали:', 6, weight='bold', va='top')
    S.ptext(X, y - 4.5,
            '• Корпуси ПДЧ/МДФ 18 mm, влагоустойчиви под мивката; крака регулируеми, цокъл 10 cm със сгъваемо стъпало.\n'
            '• Долни фронтове светъл дъб, каналова дръжка под плота; горни – топло бяло мат, до тавана.\n'
            f'• Заден ред от ъгъла: ъгъл LeMans II 450 зад врата 50 | мивка 60 с кошове | СМ 45 | чекмеджета 55; край x {cm(run_end)}.\n'
            f'• Г-част: фурна Hansa BOES68465 под котлона (y {cm(od[1])}–{cm(od[3])}), изтеглящ се шкаф 18; краят е при y {cm(ep[3])} (линия на касата).\n'
            f'• Мивка Teka Stone 50 B-TG, черна композитна, корито {cm(sx1 - sx0)}×{cm(sy1 - sy0)}, ос x = {cm(sxc)}. Котлон y {cm(hy0)}–{cm(hy1)}.\n'
            '• Хладилник Samsung RB38C650EB1/EF (59,5×203×65,8), свободностоящ – зад него щранг и водомер (лист 05);\n'
            '  дъбов панел до тавана; шкаф горе с контакта на хладилника; 5 cm вентилация.\n'
            '• Плот и гръб: светъл топъл камък/кварц, плот 4 cm, гръб до h 145; черни контакти h 111 (лист 04).\n'
            '• Абсорбатор Hansa OTP 6243 BGH, телескопичен 60, черен, в шкаф 60 над котлона; само рециркулация – без шахта.\n'
            '• Всички размери на уредите да се проверят по избраните модели и на място.',
            4.9, va='top', linespacing=1.5)
    S.S = 40.0; S.scale_bar(320, 60, n=2, label='М 1:25 (изгледи)'); S.S = 20.0; S.scale_bar(160, 20, n=2, label='М 1:50 (план)')
    S.title_block()
    S.save('03.2 Кухня - план и изгледи')


def zc(*a):
    return G.zc(*a)


# =============================================================================== 03.3 TV UNIT / DESK / HALL
def others():
    S = Sheet('03.3', 'ТВ модул, бюро и антре', scale='1:25')
    bb, bz = G.bb, G.bz
    ds = (0, (2, 1.2))
    T = E(S, 40, 128, 'ТВ МОДУЛ И БЮРО – изглед (стена x = 335)', 'М 1:25; гледано от дивана към стената')
    U = lambda y: 5.55 - y
    eL, eR = bb('WU_end_L'), bb('WU_end_R')
    W0 = U(eL[1])
    T.floor_ceiling(-0.15, 3.10)
    rz(T, 'WU_end_R', OAK, U, axis=1, lw=0.4); rz(T, 'WU_end_L', OAK, U, axis=1, lw=0.4)
    rb = bb('WU_back_reeds'); rz0, rz1 = bz('WU_back_reeds')
    T.r(U(rb[3]), rz0, U(rb[1]), rz1, fc=OAK, lw=0.3, z=5)
    yy = rb[1] + 0.02
    while yy < rb[3]:
        T.l([(U(yy), rz0), (U(yy), rz1)], lw=0.12, color='#A08060', z=5.1); yy += 0.03
    doors = []
    for i in range(5):
        n = f'WU_upper_door{i}'; d = bb(n); doors.append(d)
        door(T, U(d[3]), U(d[1]), bz(n)[0], bz(n)[1], WHITE, hinge='R' if i % 2 == 0 else 'L')
    lu = bb('WU_led_upper'); T.l([(U(lu[3]), 1.845), (U(lu[1]), 1.845)], lw=1.4, color='#E0A030', z=8)
    dk = bb('WU_desk_slab'); dz = bz('WU_desk_slab')
    rz(T, 'WU_desk_slab', OAK, U, axis=1, z=7, lw=0.45)
    rz(T, 'WU_desk_side', OAK, U, axis=1, z=7, lw=0.4)
    rz(T, 'WU_step', OAK, U, axis=1, z=7, lw=0.4)
    ct = bb('WU_console_top'); cz = bz('WU_console_top')
    rz(T, 'WU_console_top', OAK, U, axis=1, z=7, lw=0.45)
    for i in range(3):
        rz(T, f'WU_console_door{i}', OAK, U, axis=1, z=6.8)
    cbz = bz('WU_console_body')
    cl = bb('WU_console_led'); T.l([(U(cl[3]), cbz[0] - 0.005), (U(cl[1]), cbz[0] - 0.005)], lw=1.2, color='#E0A030', z=8)
    shz = []
    for i in (0, 1):
        rz(T, f'WU_shelf{i}', OAK, U, axis=1, z=7, lw=0.35); z_ = bz(f'WU_shelf{i}'); shz.append(z_)
        sl = bb(f'WU_shelf{i}_led'); T.l([(U(sl[3]), z_[0] - 0.004), (U(sl[1]), z_[0] - 0.004)], lw=1.0, color='#E0A030', z=8)
    tv = bb('TV_body'); tz = bz('TV_body')
    rz(T, 'TV_body', '#2B2B2B', U, axis=1, z=7.5, lw=0.4)
    rz(T, 'WU_soundbar', '#444444', U, axis=1, z=7.6)
    tvc = (tz[0] + tz[1]) / 2
    T.t(U((tv[1] + tv[3]) / 2), tvc + 0.12, 'ТВ 65"', fs=6, color='white', z=9)
    for nm, col in (('TV_socket', 'white'), ('TV_data', 'white'), ('Media_socket', 'k'), ('Media_router', '0.3')):
        rz(T, nm, 'none', U, axis=1, z=9, lw=0.45, ls=ds, ec=col)
    for nm in ('Lamp_socket', 'Living_switch', 'Living_switch2', 'Living_socket_door'):
        rz(T, nm, 'white', U, axis=1, z=7, lw=0.4)
    rz(T, 'Desk_socket', 'k', U, axis=1, z=7.2, lw=0.2)
    lb = bb('WU_desklamp_base'); ls_ = bb('WU_desklamp_shade'); lsz = bz('WU_desklamp_shade')
    rz(T, 'WU_desklamp_base', 'k', U, axis=1, z=8, lw=0.2)
    lp = G.ctr('WU_desklamp_pole')
    T.l([(U(lp[1]), 0.755), (U(lp[1]), lsz[0] + 0.05)], lw=0.6, color='k', z=8)
    T.r(U(ls_[3]), lsz[0], U(ls_[1]), lsz[1], fc='#F1EBDD', lw=0.35, z=8)
    # task chair (dashed, in front)
    cs = bb('LvChair_seat'); csz = bz('LvChair_seat'); cbk = bz('LvChair_back')
    T.r(U(cs[3]), csz[0], U(cs[1]), csz[1], fc='none', lw=0.3, ls=ds, z=8)
    T.r(U(cs[3]) + 0.04, cbk[0], U(cs[1]) - 0.04, cbk[1], fc='none', lw=0.3, ls=ds, z=8)
    pc = U((cs[1] + cs[3]) / 2)
    T.l([(pc, 0.06), (pc, csz[0])], lw=0.3, ls=ds, color='k', z=8)
    T.l([(pc - 0.27, 0.03), (pc + 0.27, 0.03)], lw=0.3, ls=ds, color='k', z=8)
    du = [U(d[1]) - U(d[3]) for d in doors]
    T.call(U(4.70), 2.30, 0.20, 2.45, f'5 горни врати на панти, soft-close 110°: 2×{cm(du[0])} + 3×{cm(du[2])}', fs=4.4)
    T.call(U(3.60), 1.70, 2.10, 1.95, 'рифелован дъбов гръб h 50–185', fs=4.4)
    T.call(U(3.05), 1.30, 2.30, 1.62, 'рафтове дъб + LED', fs=4.4)
    T.call(uc(U, 'WU_desklamp_shade', 1), 1.10, 2.10, 1.30, 'настолна лампа', fs=4.4)
    T.call(U(3.50), 0.72, 2.05, 0.81, f'бюро {cm(dk[3] - dk[1])}×{cm(dk[2] - dk[0])}, плот 4 cm', fs=4.4, ha='right')
    T.call(uc(U, 'WU_step', 1), 0.35, 1.55, 0.58, 'крак-панел при стъпалото', fs=4.4)
    T.call(uc(U, 'WU_desk_side', 1), 0.20, 2.62, 0.30, 'страница бюро', fs=4.4)
    T.call(uc(U, 'Desk_socket', 1), 0.86, 2.36, 0.95, 'контакт 2× + USB-C, h 86', fs=4.2, ha='right')
    T.call(uc(U, 'LvChair_seat', 1), 0.43, 2.62, 0.10, 'работен стол (пунктир)', fs=4.2)
    T.call(U(4.70), 0.53, 1.20, 0.60, 'саундбар', fs=4.4)
    T.call(U(4.70), 0.30, 1.20, 0.33, 'конзола окачена, 3 врати', fs=4.4)
    T.call(uc(U, 'TV_socket', 1), 0.99, 0.20, 1.62, 'зад ТВ: контакт + RJ45/ТВ h 99', fs=4.4)
    T.call(uc(U, 'Media_socket', 1), 0.28, 0.20, -0.30, 'в конзолата: контакти h 28, рутер', fs=4.4)
    T.call(uc(U, 'Lamp_socket', 1), 0.30, -0.15, -0.50, 'контакт h 30', fs=4.4, ha='right')
    T.call(uc(U, 'Living_switch2', 1), 1.05, 3.45, 1.22, 'ключове h 105 (лист 06)', fs=4.2)
    T.call(uc(U, 'Living_socket_door', 1), 0.30, 3.20, -0.30, 'контакт h 30', fs=4.2)
    T.dimc([U(y) for y in (eR[3], eR[1], tv[3], tv[1], ct[1], dk[1], eL[1])], 'x', -0.70, ref=0, side=-1, fs=4.4)
    T.dimc([U(y) for y in (eR[3], ct[1], dk[1], eL[1])], 'x', -0.95, ref=0, side=-1, fs=4.6,
           labels=[f'конзола {cm(ct[3] - ct[1])}', f'бюро {cm(dk[3] - dk[1])}', None])
    T.dimc([0, W0], 'x', -1.20, ref=0, side=-1)
    xs = sorted(set(round(v, 4) for v in [U(eR[3]), U(eR[1])] + [U(d[1]) for d in doors] + [U(eL[1])]))
    labs = [None] + [cm(b - a) for a, b in zip(xs[1:-2], xs[2:-1])] + [None]
    T.dimc(xs, 'x', 2.75, ref=2.60, fs=4.4, labels=labs)
    T.dimc([0, cbz[0], cz[0], tz[0], tz[1], 1.85, 2.60], 'y', -0.25, ref=0, fs=4.2)
    T.dimc([0, dz[0], dz[1], shz[0][0], shz[1][0], 1.85, 2.60], 'y', 3.35, ref=W0, side=-1, fs=4.4)
    T.t(U((tv[1] + tv[3]) / 2), -1.42, f'ос ТВ: y = {cm((tv[1] + tv[3]) / 2)}, h = {cm(tvc)}', fs=4.4, color='0.3')
    T.head(0, 3.10, 2.75)
    for zz, va in ((-0.12, 'top'), (2.68, 'bottom')):
        T.l([(U(4.45), zz), (U(4.45), zz + (0.06 if va == 'top' else -0.06))], lw=1.2)
        T.t(U(4.45) + 0.06, zz, '1', fs=6.5, weight='bold', va=va)

    # ---------------- section 1-1 through the console (u = 3.35 - x)
    Q = E(S, 200, 128, 'РАЗРЕЗ 1-1', 'М 1:25, през конзолата')
    V = lambda x: 3.35 - x
    Q.floor_ceiling(0, 0.62)
    Q.l([(0, 0), (0, 2.60)], lw=0.9)
    rz(Q, 'WU_upper_body', WHITE, V, lw=0.4)
    rz(Q, 'WU_upper_door3', WHITE, V, lw=0.3)
    Q.r(0.0, rz0, V(rb[0]), rz1, fc=OAK, lw=0.3)
    rz(Q, 'WU_console_top', OAK, V, lw=0.4)
    rz(Q, 'WU_console_body', CARC, V, lw=0.3)
    rz(Q, 'WU_console_door1', OAK, V, lw=0.3)
    Q.r(V(dk[2]), dz[0], V(dk[0]), dz[1], fc='none', lw=0.35, ls=(0, (3, 1.5)))
    rz(Q, 'TV_body', '#2B2B2B', V, lw=0.3)
    rz(Q, 'WU_soundbar', '#444444', V, lw=0.3)
    Q.call(V(dk[0]) - 0.02, 0.72, 0.70, 0.90, 'бюро (зад разреза)', fs=4.2)
    cb = bb('WU_console_body'); ub = bb('WU_upper_body')
    Q.dimc([0, V(cb[0]), V(ct[0])], 'x', -0.35, ref=0, side=-1, fs=4.4)
    Q.dimc([0, V(dk[0])], 'x', -0.60, ref=0, side=-1, fs=4.4, labels=[f'бюро {cm(dk[2] - dk[0])}'])
    Q.dimc([0, V(bb('WU_upper_door3')[0])], 'x', 2.75, ref=2.60, fs=4.4)
    Q.head(0, 0.6, 2.75)

    # ---------------- hall unit elevation (looking +x at wall x = 4.77): u = 2.33 - y
    H = E(S, 290, 128, 'МЕБЕЛ ЗА АНТРЕ – изглед', 'М 1:25; колоната за почистване – без вратите')
    W_ = lambda y: 2.33 - y
    H.floor_ceiling(0, 1.22)
    H.l([(0, 0), (0, 2.60)], lw=0.8)
    sd = bb('Hall_unit_side'); rz(H, 'Hall_unit_side', WHITE, W_, axis=1, lw=0.4)
    tl = bb('Hall_unit_tall')
    d0, d1 = bb('Hall_unit_tall_door0'), bb('Hall_unit_tall_door1')
    H.r(W_(tl[3]), 0, W_(tl[1]), 2.60, fc='#F6F4EF', lw=0.45, z=5)
    for i in range(3):
        rz(H, f'Hall_cl_shelf{i}', WHITE, W_, axis=1, z=6, lw=0.35)
    def box(nm, fc, z=6.4, ls='-', ec='k', lw=0.3):
        rz(H, nm, fc, W_, axis=1, z=z, lw=lw, ls=ls, ec=ec)
    box('Hall_cl_products', '#E9E2D2'); box('Hall_cl_iron', '#9AA3A8')
    box('Hall_cl_vac_dock', '0.25'); box('Hall_cl_vac_body', '0.55'); box('Hall_cl_vac_tube', '0.45'); box('Hall_cl_vac_head', '0.35')
    box('Hall_cl_socket', 'white', z=6.6, lw=0.4)
    box('Hall_cl_mop', '#C9C2B4')
    for nm in ('Hall_cl_stick0', 'Hall_cl_stick1'):
        b_ = bb(nm); z_ = bz(nm); H.l([(W_((b_[1] + b_[3]) / 2), z_[0]), (W_((b_[1] + b_[3]) / 2), z_[1])], lw=0.8, color='0.3', z=6.3)
    box('Hall_cl_ironing', '#DCD3C2', z=6.8, lw=0.6)
    bs = bb('Hall_unit_bench_seat')
    rz(H, 'Hall_unit_bench_back', OAK, W_, axis=1, z=5)
    rz(H, 'Hall_unit_bench_seat', OAK, W_, axis=1, z=6, lw=0.4)
    rz(H, 'Hall_unit_seat_pad', '#CDBFA8', W_, axis=1, z=6.1)
    rz(H, 'Hall_unit_shoe_shelf', OAK, W_, axis=1, z=6)
    rz(H, 'Hall_unit_plinth', '0.35', W_, axis=1, z=5.5, lw=0.2)
    rz(H, 'Hall_unit_hatshelf', OAK, W_, axis=1, z=6, lw=0.35)
    ud = bb('Hall_unit_upper_door'); up = bz('Hall_unit_upper_door')
    door(H, W_(ud[3]), W_(ud[1]), up[0], up[1], WHITE, hinge='L')
    for i in range(4):
        rz(H, f'Hall_unit_hook{i}', 'k', W_, axis=1, z=7, lw=0.2)
    hl = bb('Hall_unit_led'); H.l([(W_(hl[3]), 1.975), (W_(hl[1]), 1.975)], lw=1.2, color='#E0A030', z=7)
    H.call(W_(1.43), 2.30, 1.40, 2.45, 'шкаф горе, врата на панти', fs=4.3)
    H.call(W_(1.43), 1.965, 1.40, 2.08, f'рафт за шапки h {cm(bz("Hall_unit_hatshelf")[0])}–{cm(bz("Hall_unit_hatshelf")[1])} + LED', fs=4.3)
    H.call(W_(1.40), 1.71, 1.40, 1.70, f'4 закачалки h {cm(G.zc("Hall_unit_hook0"))}', fs=4.3)
    H.call(W_(1.43), 1.20, 1.40, 1.25, 'дъбов гръб', fs=4.3)
    H.call(W_(1.43), 0.435, 1.40, 0.55, f'пейка h {cm(bz("Hall_unit_seat_pad")[1])}', fs=4.3)
    H.call(W_(1.43), 0.11, 1.40, 0.18, 'рафт за обувки', fs=4.3)
    L_ = -0.40
    H.call(W_(2.02), 2.26, L_, 2.40, 'рафтове h 150 / 190 / 225', fs=4.2, ha='right')
    H.call(W_(1.93), 1.62, L_, 1.85, 'препарати, ютия', fs=4.2, ha='right')
    H.call(W_(1.99), 1.24, L_, 1.40, f'зарядно, контакт h {cm(G.zc("Hall_cl_socket"))}', fs=4.2, ha='right')
    H.call(W_(1.85), 0.95, L_, 1.00, 'прахосмукачка (стик)', fs=4.2, ha='right')
    H.call(W_(2.09), 0.65, L_, 0.62, 'дъска за гладене', fs=4.2, ha='right')
    H.call(W_(2.17), 0.05, L_, 0.20, 'моп + метла', fs=4.2, ha='right')
    H.call(W_(2.17), 2.50, L_, 2.75, f'2 врати {cm(d0[3] - d0[1])} (лявата огледална)', fs=4.2, ha='right')
    H.dimc([W_(y) for y in (2.33, tl[3], tl[1], sd[3], sd[1])], 'x', -0.35, ref=0, side=-1, fs=4.2,
           labels=[None, f'колона {cm(tl[3] - tl[1])}', f'пейка {cm(bs[3] - bs[1])}', None])
    H.dimc([0, W_(sd[1])], 'x', -0.60, ref=0, side=-1, fs=4.4)
    H.dimc([0, 0.45, 1.50, 1.90, 1.98, 2.25, 2.60], 'y', -0.16, ref=0, fs=4.0)
    H.head(0, 1.22, 2.75)

    S.ptext(40, 66, 'Изпълнение / материали:', 6, weight='bold', va='top')
    S.ptext(40, 61.5,
            f'• ТВ модул y {cm(eL[1])}–{cm(eR[3])}, лице x {cm(dk[0])}; бордови панели WU_end_L / WU_end_R до тавана; 5 горни врати на панти (soft-close, 110°),\n'
            f'  топло бяло мат; рифелован дъбов гръб (ламели ~3 cm) h 50–185.\n'
            f'• Бюро {cm(dk[3] - dk[1])}×{cm(dk[2] - dk[0])} (y {cm(dk[1])}–{cm(dk[3])}): дъбов плот 4 cm, собствена страница до пода при y {cm(bb("WU_desk_side")[1])} и крак-панел при стъпалото\n'
            f'  (y {cm(bb("WU_step")[1])}); отвор за кабели; черен контакт 2× + USB-C h 86 на стената над плота. Работен стол с облегалка.\n'
            f'• Рафтове над бюрото h {cm(shz[0][1])} и {cm(shz[1][1])}, LED отдолу. Конзола окачена h {cm(cbz[0])}–{cm(cz[1])}, дълб. {cm(ct[2] - ct[0])}, 3 вентилирани врати;\n'
            '  вътре контакти + данни h 28 (рутер / ТВ бокс). ТВ 65" на стенна стойка, зад него контакт + RJ45/ТВ h 99.\n'
            '• LED 24 V: под горните шкафове, под конзолата, под рафтовете; захранващите блокове – в горния шкаф (лист 04/06).\n'
            f'• Мебел за антре x {cm(bb("Hall_unit_side")[0])}–{cm(G.X_COR1)}: пейка с дъбов гръб, закачалки, рафт за шапки с LED, шкаф горе с врата на панти;\n'
            '  колона за почистване с 2 врати (едната огледална): рафтове, стик прахосмукачка със зарядно (контакт вътре), дъска, моп и метла.',
            4.8, va='top', linespacing=1.5)
    S.S = 40.0; S.scale_bar(330, 60, n=2, label='М 1:25')
    S.title_block()
    S.save('03.3 ТВ модул, бюро и антре')


# =============================================================================== 03.4 WARDROBE / BED WALL / BOOKCASE
def others2():
    S = Sheet('03.4', 'Гардероб, спалня и библиотека', scale='1:25, 1:30')
    bb, bz = G.bb, G.bz
    ds = (0, (2, 1.2))
    # ---------------- wardrobe interior (doors removed), looking -y: u = 6.65 - x
    W = E(S, 84, 152, 'ГАРДЕРОБ В НИШАТА – изглед без вратите',
          'М 1:25; 2 плъзгащи врати (задна огледална) + запълващ панел пред колоната')
    U = lambda x: G.X_E - x
    cw = bb('Wardrobe_carc'); Wd = U(cw[0])
    W.floor_ceiling(0, Wd)
    W.l([(0, 0), (0, 2.60)], lw=0.8); W.l([(Wd, 0), (Wd, 2.60)], lw=0.8)
    W.r(0, 0.04, Wd, 2.54, fc='#F6F4EF', lw=0.35, z=5)
    W.r(0, 2.54, Wd, 2.60, fc='0.85', lw=0.3); W.r(0, 0, Wd, 0.04, fc='0.3', lw=0.2)
    rz(W, 'Wint_divider', WHITE, U, lw=0.35, z=6)
    for n in ('Wint_A_shelf', 'Wint_A_topbox', 'Wint_A_shoes', 'Wint_B_shelf'):
        rz(W, n, WHITE, U, lw=0.35, z=6.2)
    for n in ('Wint_A_rail', 'Wint_B_rail0', 'Wint_B_rail1'):
        b_ = bb(n); W.l([(U(b_[2]), G.zc(n)), (U(b_[0]), G.zc(n))], lw=1.3, color='0.25', z=6.4)
    rz(W, 'Wint_B_drawer_carc', WHITE, U, lw=0.35, z=6.1)
    for n in ('Wint_B_drawer0', 'Wint_B_drawer1'):
        rz(W, n, WHITE, U, lw=0.4, z=6.3)
    for nm in ('Wint_led_A', 'Wint_led_B'):
        b_ = bb(nm); z_ = bz(nm)
        W.l([(U(b_[2]), z_[0] - 0.01), (U(b_[0]), z_[0] - 0.01)], lw=1.4, color='#E0A030', z=7)
    fl = bb('Wardrobe_filler')
    W.r(U(fl[2]), 0, U(fl[0]), 2.60, fc='none', ec='0.3', lw=0.5, ls=(0, (4, 1.5)), z=7.5)
    W.l([(U(fl[2]), 0), (U(fl[0]), 2.60)], lw=0.25, ls=ds, color='0.4', z=7.5)
    for (n0, n1, zt, zb) in (('Wint_A_rail', None, 1.70, 0.55),):
        b_ = bb(n0); W.r(U(b_[2]) + 0.03, zb, U(b_[0]) - 0.03, zt, fc='none', lw=0.25, ls=ds, z=6.1, ec='0.55')
    br = bb('Wint_B_rail0')
    W.r(U(br[2]) + 0.03, 1.15, U(br[0]) - 0.03, 1.95, fc='none', lw=0.25, ls=ds, z=6.1, ec='0.55')
    W.r(U(br[2]) + 0.03, 0.47, U(br[0]) - 0.03, 1.03, fc='none', lw=0.25, ls=ds, z=6.1, ec='0.55')
    ax_ = U((bb('Wint_A_rail')[0] + bb('Wint_A_rail')[2]) / 2)
    W.t(ax_, 1.10, 'A\nдълги дрехи', fs=4.6, color='0.3', z=8)
    W.t(U(5.90), 1.55, 'B\nдвойно\nзакачване', fs=4.6, color='0.3', z=8)
    CU = Wd + 0.22
    dvx = bb('Wint_divider')
    W.call(U(5.0), 2.57, CU, 2.82, 'двоен релсов механизъм, таванен', fs=4.4)
    W.call(ax_, G.zc('Wint_A_topbox'), CU, 2.40, f'A: рафт за кутии h {cm(bz("Wint_A_topbox")[1])}', fs=4.4)
    W.call(ax_ + 0.15, G.zc('Wint_A_shelf'), CU, 2.10, f'A: рафт h {cm(bz("Wint_A_shelf")[1])} + LED', fs=4.4)
    W.call(ax_ + 0.20, G.zc('Wint_A_rail'), CU, 1.80, f'A: лост h {cm(G.zc("Wint_A_rail"))}', fs=4.4)
    W.call(ax_, G.zc('Wint_A_shoes'), CU, 0.20, f'A: рафт за обувки h {cm(bz("Wint_A_shoes")[1])}', fs=4.4)
    W.call(U(dvx[0]), 0.80, CU, 0.75, 'преграда', fs=4.4)
    W.call(U(5.80), G.zc('Wint_B_shelf'), -0.20, 2.40, f'B: рафт h {cm(bz("Wint_B_shelf")[1])} + LED', fs=4.4, ha='right')
    W.call(U(5.80), G.zc('Wint_B_rail0'), -0.20, 2.10, f'B: лост h {cm(G.zc("Wint_B_rail0"))}', fs=4.4, ha='right')
    W.call(U(5.80), G.zc('Wint_B_rail1'), -0.20, 1.10, f'B: лост h {cm(G.zc("Wint_B_rail1"))}', fs=4.4, ha='right')
    W.call(U(5.90), G.zc('Wint_B_drawer1'), -0.20, 0.30, f'B: 2 чекмеджета под долния лост\nh {cm(bz("Wint_B_drawer_carc")[0])}–{cm(bz("Wint_B_drawer_carc")[1])}', fs=4.4, ha='right')
    W.call(U(6.44), 1.60, -0.20, 1.60, 'запълващ панел (отпред,\nпред дъбовата колона)', fs=4.2, ha='right')
    W.dimc([0, U(fl[0]), U(dvx[2]), U(dvx[0]), Wd], 'x', 2.82, ref=2.60, fs=4.4)
    W.dimc([0, U(bb('Wardrobe_track_bot')[2]), Wd], 'x', -0.42, ref=0, side=-1, fs=4.6,
           labels=[None, 'плъзгащи врати 2×~70 (общо 176)'])
    zs = sorted(set(round(v, 3) for v in [0, bz('Wint_A_shoes')[1], G.zc('Wint_A_rail'), bz('Wint_A_shelf')[1],
                                           bz('Wint_A_topbox')[1], 2.54, 2.60]))
    W.dimc(zs, 'y', Wd + 0.12, ref=Wd, side=-1, fs=4.0)
    zb = sorted(set(round(v, 3) for v in [0, bz('Wint_B_drawer_carc')[1], G.zc('Wint_B_rail1'), G.zc('Wint_B_rail0'),
                                           bz('Wint_B_shelf')[1], 2.60]))
    W.dimc(zb, 'y', -0.10, ref=0, fs=4.0)
    W.head(0, Wd, 2.75)

    # ---------------- section through an oak tower (looking -y, u = 6.65 - x)
    A = E(S, 232, 152, 'КОЛОНА ДО ЛЕГЛОТО – разрез', 'М 1:25; двете колони са еднакви; леглото – пунктир')
    V = lambda x: G.X_E - x
    A.floor_ceiling(0, 1.20)
    A.l([(0, 0), (0, 2.60)], lw=0.8)
    t = 't0'
    rz(A, 'Bed_wall_panel', OAK, V, lw=0.4, z=6)
    rz(A, f'BW_{t}_plinth', '0.35', V, lw=0.3, z=6)
    rz(A, f'BW_{t}_drawer', OAK, V, lw=0.45, z=6)
    rz(A, 'Bed_ns_wardrobe', OAK, V, lw=0.45, z=6.1)
    rz(A, f'BW_{t}_top', CARC, V, lw=0.4, z=6)
    rz(A, f'BW_{t}_door0', OAK, V, lw=0.4, z=6.2)
    rz(A, f'BW_{t}_door1', OAK, V, lw=0.4, z=6.2)
    nb = bb(f'BW_{t}_niche_back')
    A.r(V(nb[2]), bz('Bed_ns_wardrobe')[1], V(nb[0]), 1.40, fc='#F3E8D3', lw=0.25, z=5.8)
    rz(A, f'BW_{t}_niche_led', '#E0A030', V, lw=0.3, z=6.4, ec='#E0A030')
    rz(A, 'WallLamp0_plate', 'k', V, lw=0.2, z=6.5)
    rz(A, 'WallLamp0_arm', 'k', V, lw=0.2, z=6.5)
    sh = bb('WallLamp0_shade'); shz = bz('WallLamp0_shade')
    A.r(V(sh[2]), shz[0], V(sh[0]), shz[1], fc='#F1EBDD', lw=0.35, z=6.6)
    rz(A, 'Bed_socket0', 'white', V, lw=0.35, z=6.5)
    br = bb('BW_bridge_carc'); brz = bz('BW_bridge_carc')
    A.r(V(br[2]), brz[0], V(br[0]), brz[1], fc='none', lw=0.3, ls=ds, z=6.7)
    for n_ in ('Bed_platform', 'Mattress'):
        b_ = G.b3(n_); A.r(V(b_[3]), b_[2], 1.15, b_[5], fc='none', lw=0.35, z=6.7, ls=ds)
    tz0 = bz(f'BW_{t}_drawer'); top0 = bz(f'BW_{t}_top')[0]
    A.t(V(6.43), 0.98, 'ниша', fs=4.4, color='0.3', z=8)
    A.t(V(6.43), 2.15, 'шкаф', fs=4.4, color='0.3', z=8)
    A.t(V(6.43), 0.24, 'чекм.', fs=4.4, color='0.3', z=8)
    CU = 0.78
    A.call(V(6.50), 1.21, CU, 1.45, 'лампа за четене на гърба\nна нишата, h ~120', fs=4.2)
    A.call(V(6.62), 0.66, CU, 0.85, 'контакт h 66 (до него ключ)', fs=4.2)
    A.call(V(6.40), 1.397, CU, 1.70, 'LED под шкафа', fs=4.2)
    A.call(V(6.40), 2.0, CU, 2.20, 'мост над леглото (зад разреза)', fs=4.2)
    A.call(V(6.636), 1.00, CU, 0.60, f'дъбов панел-табла h {cm(bz("Bed_wall_panel")[1])}', fs=4.2)
    A.call(V(5.80), 0.42, CU, 0.18, 'легло (пунктир)', fs=4.2)
    t0 = bb(prefix='BW_t0')
    A.dimc([0, V(nb[0]), V(t0[0])], 'x', -0.42, ref=0, side=-1, fs=4.4)
    A.dimc([0, 0.08, tz0[1], bz('Bed_ns_wardrobe')[1], top0, bz(f'BW_{t}_door0')[1], 2.60], 'y', -0.10, ref=0, fs=4.2)
    A.head(0, 1.20, 2.75)

    # ---------------- bed wall elevation (looking +x at wall x = 6.65), u = 5.34 - y, 1:30
    S30 = 1000 / 30
    K = E(S, 58, 26, 'СТЕНА ЗАД ЛЕГЛОТО – изглед', 'М 1:30; 2 еднакви дъбови колони 55×42, мост с 3 врати, дъбов панел-табла h 155',
          sc=S30)
    R = lambda y: G.Y_BED1 - y
    span = R(bb('Bed_wall_panel')[1])
    K.floor_ceiling(0, span)
    K.l([(0, 0), (0, 2.60)], lw=0.8); K.l([(span, 0), (span, 2.60)], lw=0.8)
    rz(K, 'Bed_wall_panel', OAK, R, axis=1, lw=0.4, z=5)
    for t in ('t0', 't1'):
        tb = bb(prefix=f'BW_{t}')
        K.r(R(tb[3]), 0, R(tb[1]), 2.60, fc='#F3E8D3', lw=0.45, z=5.5)
        rz(K, f'BW_{t}_plinth', '0.35', R, axis=1, lw=0.2, z=5.6)
        rz(K, f'BW_{t}_drawer', OAK, R, axis=1, lw=0.4, z=5.7)
        K.l([(R(tb[3]) + 0.02, bz(f'BW_{t}_drawer_gap')[0]), (R(tb[1]) - 0.02, bz(f'BW_{t}_drawer_gap')[0])], lw=0.2, color='0.4', z=5.8)
        rz(K, 'Bed_ns_' + ('wardrobe' if t == 't0' else 'window'), OAK, R, axis=1, lw=0.4, z=5.7)
        rz(K, f'BW_{t}_door0', OAK, R, axis=1, lw=0.4, z=5.7)
        rz(K, f'BW_{t}_door1', OAK, R, axis=1, lw=0.4, z=5.7)
        nl = bb(f'BW_{t}_niche_led'); K.l([(R(nl[3]), 1.398), (R(nl[1]), 1.398)], lw=1.2, color='#E0A030', z=5.9)
    for i in range(3):
        n = f'BW_bridge_door{i}'
        door(K, R(bb(n)[3]), R(bb(n)[1]), bz(n)[0], bz(n)[1], WHITE, hinge='L' if i < 2 else 'R')
    bl = bb('BW_bridge_led'); K.l([(R(bl[3]), 1.546), (R(bl[1]), 1.546)], lw=1.2, color='#E0A030', z=6)
    rz(K, 'Bed_headboard', '#D9C29E', R, axis=1, lw=0.45, z=6)
    rz(K, 'Bed_platform', OAK, R, axis=1, lw=0.45, z=6.5)
    pl = bb('Bed_platform_plinth'); K.r(R(pl[3]), 0, R(pl[1]), 0.03, fc='0.35', lw=0.3, z=6.4)
    rz(K, 'Mattress', 'white', R, axis=1, lw=0.4, z=6.6)
    for i in (0, 1):
        rz(K, f'WallLamp{i}_plate', 'k', R, axis=1, lw=0.2, z=7)
        sh_ = G.ctr(f'WallLamp{i}_shade'); sz = bz(f'WallLamp{i}_shade')
        K.on(); S.circle(R(sh_[1]), (sz[0] + sz[1]) / 2, 0.065, lw=0.4, fc='#F1EBDD', z=7.1)
        for nm in (f'Bed_switch{i}', f'Bed_socket{i}'):
            rz(K, nm, 'white', R, axis=1, lw=0.35, z=7)
    t0, t1 = bb(prefix='BW_t0'), bb(prefix='BW_t1')
    CR = span + 0.12
    K.call(R(t0[1] + 0.25), 2.00, CR, 2.25, 'колона: шкаф с 2 врати', fs=4.2)
    K.call(R(t0[1] + 0.25), 1.00, CR, 1.30, 'ниша h 55,5–140 + лампа', fs=4.2)
    K.call(R(t0[1] + 0.25), 0.28, CR, 0.40, 'чекмедже h 8–47', fs=4.2)
    K.call(R(3.90), 2.10, CR, 1.95, 'мост над леглото: 3 врати + LED отдолу', fs=4.2)
    K.call(R(3.40), 1.30, CR, 1.62, f'дъбов панел-табла h {cm(bz("Bed_wall_panel")[1])}', fs=4.2)
    K.call(R(3.60), 0.40, CR, 0.75, 'легло с повдигащ се матрак, ракла', fs=4.2)
    K.call(R(G.ctr('Bed_switch1')[1]), 0.66, -0.45, 0.30, 'ключ: лампа + кръстат\n/ девиаторен (таван), h 66', fs=4.2, ha='right')
    K.call(R(G.ctr('Bed_socket1')[1]), 0.66, -0.45, 0.75, 'контакт 2×, h 66', fs=4.2, ha='right')
    K.call(R(G.ctr('WallLamp1_shade')[1]), 1.20, -0.45, 1.25, 'лампа за четене', fs=4.2, ha='right')
    ys = [G.Y_BED1, t1[1], bb('Bed_platform')[3], bb('Bed_platform')[1], t0[3], t0[1]]
    K.dimc([R(y) for y in ys], 'x', -0.40, ref=0, side=-1, fs=4.0)
    K.dimc([0, 0.08, 0.47, 0.555, 1.40, bz('Bed_wall_panel')[1], 2.60], 'y', -0.12, ref=0, fs=4.0)
    K.dimc([0, bz('Bed_platform')[1], bz('Mattress')[1], 2.60], 'y', span + 1.60, ref=span, side=-1, fs=4.0)
    K.head(0, span, 2.75)

    # ---------------- bookcase: wall x = 0, looking -x, u = y - y0
    bc = bb('BC_back', 'BC_sideL', 'BC_sideR'); y0b = bc[1]
    B = E(S, 318, 152, 'БИБЛИОТЕКА С АРКА – изглед', 'М 1:25; гипс + дъб; база с 2 чекмеджета')
    Wb = bc[3] - bc[1]
    Vb = lambda y: y - y0b
    B.floor_ceiling(0, Wb)
    B.on()
    B.r(0, 0, Wb, 2.60, fc='#EFEAE2', lw=0.45, z=5)
    i0, i1 = Vb(bb('BC_sideL')[3]), Vb(bb('BC_sideR')[1])
    rr = (i1 - i0) / 2; ztop = bz('BC_top')[0]
    pts = [(i0, 0.0), (i0, ztop - rr)]
    for k in range(0, 181, 6):
        a = math.radians(180 - k)
        pts.append(((i0 + i1) / 2 + rr * math.cos(a), ztop - rr + rr * math.sin(a)))
    pts += [(i1, ztop - rr), (i1, 0.0)]
    S.poly(pts, lw=0.35, ec='k', fc='#F8F5EF', z=5.2, closed=False)
    rz(B, 'BC_base', OAK, Vb, axis=1, lw=0.35, z=6)
    for n in ('BC_drawer0', 'BC_drawer1'):
        rz(B, n, OAK, Vb, axis=1, lw=0.4, z=6.1)
    for n in ('BC_shelf0.8', 'BC_shelf1.18', 'BC_shelf1.56'):
        rz(B, n, OAK, Vb, axis=1, lw=0.35, z=6)
    for n in ('BC_led_L', 'BC_led_R'):
        b_ = bb(n); z_ = bz(n); B.l([(Vb((b_[1] + b_[3]) / 2), z_[0]), (Vb((b_[1] + b_[3]) / 2), z_[1])], lw=1.0, color='#E0A030', z=7)
    CB = Wb + 0.15
    B.call(Wb / 2, 2.30, CB, 2.35, 'гипсова рамка, варова мазилка', fs=4.4)
    B.call(Wb / 2, 0.30, CB, 0.30, 'дъбова база, 2 чекмеджета', fs=4.4)
    B.call(i1 - 0.01, 1.30, CB, 1.30, 'LED профил вертикален', fs=4.4)
    B.call(Wb / 2, 0.815, CB, 0.82, 'рафтове дъб 3 cm', fs=4.4)
    B.call(Wb / 2, ztop - 0.05, CB, 2.0, f'арка R ≈ {cm(rr)}, връх h {cm(ztop)}', fs=4.4)
    B.dimc([0, i0, i1, Wb], 'x', -0.55, ref=0, side=-1, fs=4.4)
    B.dimc([0, bz('BC_drawer0')[1], bz('BC_base')[1], bz('BC_shelf0.8')[0], bz('BC_shelf1.18')[0], bz('BC_shelf1.56')[0],
            ztop - rr, ztop, 2.60], 'y', -0.25, ref=0, fs=4.0)
    B.t(Wb / 2, -0.85, f'y {cm(bc[1])}–{cm(bc[3])}; дълбочина {cm(bb("BC_frame")[2])} cm', fs=4.6, color='0.2')
    B.head(0, Wb, 2.75)

    S.ptext(240, 120, 'Изпълнение / материали:', 6, weight='bold', va='top')
    S.ptext(240, 115.5,
            f'• Гардероб в нишата x {cm(cw[0])}–{cm(cw[2])}: корпус ПДЧ 18 mm; 2 плъзгащи врати по долна/горна\n'
            f'  релса до x {cm(bb("Wardrobe_track_bot")[2])} (задната огледална), запълващ панел x {cm(fl[0])}–{cm(fl[2])} пред колоната.\n'
            '• A: лост, рафт с LED, рафт за кутии, рафт за обувки. B: 2 лоста, рафт с LED,\n'
            '  2 чекмеджета под долния лост; LED с контакт на вратата.\n'
            '• Стена зад леглото: 2 еднакви дъбови колони 55×42 – чекмедже h 8–47, плот h 47–55,5,\n'
            '  отворена ниша h 55,5–140 с лампа за четене на гърба и LED отгоре, шкаф h 140–260 с 2 врати.\n'
            '• Мост над леглото h 155–260 с 3 врати (топло бяло), LED отдолу; дъбов панел-табла h 155\n'
            '  по цялата стена; контакт и ключ h 66 във всяка ниша (кръстат и девиаторен – лист 04/06).\n'
            '• Легло с повдигащ се матрак (газови амортисьори) и ракла ~0,7 m³; матрак 160×200.\n'
            f'• Библиотека y {cm(bc[1])}–{cm(bc[3])}: ГК/дървена конструкция, варова мазилка; рафтове масивен дъб 3 cm;\n'
            '  база h 40 с 2 чекмеджета; вертикален LED профил 2700 K в бордовете. Формата на арката – по детайл.\n'
            '• Всички размери да се проверят на място след шпакловка.',
            4.8, va='top', linespacing=1.5)
    S.S = 40.0; S.scale_bar(300, 64, n=2, label='М 1:25'); S.S = 1000 / 30; S.scale_bar(240, 64, n=1, label='М 1:30')
    S.title_block()
    S.save('03.4 Гардероб, спалня и библиотека')


if __name__ == '__main__':
    import sys
    fns = {'k': kitchen, 't': others, 'w': others2}
    for c_ in (sys.argv[1] if len(sys.argv) > 1 else 'ktw'):
        fns[c_]()
