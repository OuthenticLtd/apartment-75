# -*- coding: utf-8 -*-
"""Sheet 04 – electrical. Every point is read from the export (position + height); only the symbol
type, the circuit and the drawing direction are assigned here."""
from common import *
import geom as G
import elec as EL
from elec import RED, BLUE, LED, GRN, PUR
from shapely.geometry import Point, Polygon as SPoly, box as sbox
from matplotlib.patches import Rectangle, Circle

H = lambda n: int(round(G.zc(n) * 100))


def wallpt(n, ang):
    """plan point of a wall-mounted object on its wall face (ang = direction into the room)."""
    x0, y0, x1, y1 = G.bb(n)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if ang == 0: return (x0, cy)
    if ang == 180: return (x1, cy)
    if ang == 90: return (cx, y0)
    return (cx, y1)


# (object, symbol, ang into room, label, (dx, dy) label offset mm, ha, draw shift along wall in m)
SOCKETS = [
    ('K_socket_prep', 's2', 90, '{h}/К1', (-1.0, -8.0), 'center', 0),
    ('K_socket_coffee', 's2', 90, '{h}/К1', (0, -8.0), 'center', 0),
    ('K_conn_dw', 'box', 90, '{h}/К3 СМ', (1.0, -12.0), 'center', 0, 'СМ'),
    ('K_conn_fridge', 'box', 90, '{h}/К2 ХЛ (в шкафа)', (0, -8.0), 'center', 0, 'ХЛ'),
    ('K_conn_hood', 's1', 0, '{h}/К1 абсорб.', (4.6, 0), 'left', 0),
    ('K_conn_hob', 'box', 0, '{h}/К5 котлон 230 V / 20 A', (4.6, 2.2), 'left', 0.04, 'К'),
    ('K_conn_oven', 's1', 0, '{h}/К4 фурна', (4.6, -1.2), 'left', -0.10),
    ('Dining_socket', 's1', 0, '{h}/S1', (4.2, 0), 'left', 0),
    ('Sofa_socket_L', 's1', 0, '{h}/S1', (4.2, -1.0), 'left', 0),
    ('Sofa_socket_R', 's1', 0, '{h}/S1', (4.2, 0.8), 'left', 0),
    ('Living_socket_door', 's1', 180, '{h}/S1', (-4.6, -2.4), 'right', -0.10),
    ('Desk_socket', 's2', 180, '{h}/S2 +USB-C', (-4.4, 0), 'right', 0),
    ('TV_socket', 's2', 180, '{h}/S1 зад ТВ', (-4.4, 0.4), 'right', 0),
    ('TV_data', 'tp', 180, '{h} RJ45/ТВ', (-4.4, -0.6), 'right', 0.04, 'TP'),
    ('Media_socket', 's3', 180, '{h}/S1 конзола', (-5.6, 0), 'right', 0),
    ('Lamp_socket', 's1', 180, '{h}/S1', (-4.4, -1.8), 'right', -0.04),
    ('Lamp_socket2', 's1', 270, '{h}/S1 лампион', (0, -5.0), 'center', 0),
    ('Hall_socket_vac', 's1', 0, '{h}/S3 прахосм.', (4.2, -1.6), 'left', -0.12),
    ('Hall_cl_socket', 's1', 180, '{h}/S3 зарядно\nв шкафа', (-4.4, -3.5), 'right', 0),
    ('Bedroom_socket_door', 's1', 90, '{h}/S2', (5.0, 10.0), 'left', 0.10),
    ('Bed_socket0', 's2', 180, '{h}/S2', (-4.4, -2.0), 'right', 0),
    ('Bed_socket1', 's2', 180, '{h}/S2', (-4.4, 2.0), 'right', 0),
    ('Dresser_socket', 's2', 0, '{h}/S2 тоалетка', (4.4, -1.2), 'left', 0),
    ('Vanity_mirror_feed', 'box', 0, '{h}/S2 LED огледало\n(кутия зад огледалото)', (5.6, 1.6), 'left', 0, 'О'),
    ('Bath_socket_ip44', 's1ip', 0, '{h}/B2 IP44', (3.8, 2.4), 'left', 0),
    ('Towel_rail_conn', 'box', 90, '{h}/B2 лира IP44 (изход, без контакт)', (-1.0, -9.5), 'center', 0, 'ЛК'),
    ('Washer_socket', 's1ip', 270, '{h}/B1 IP44\nпералня', (0, -11.0), 'center', 0),
    ('Bal_socket_ip44', 's1ip', 180, '{h}/S3 IP44,\nс ключ', (-4.4, 0), 'right', 0),
    ('AC_isolator', 'box', 180, '{h} прекъсвач КЛ-Н IP65', (9.0, -1.0), 'left', 0, 'П'),
    ('AC_bed_supply', 'box', 90, '{h}/AC', (-7.0, 7.5), 'right', -0.16, 'КЛ'),
]
# switches: object, ang, kind, label, (dx, dy), ha, draw shift
SWITCHES = [
    ('Living_switch', 180, '2', '{h}: a◐ / b', (-4.8, -1.6), 'right', -0.06),
    ('Living_switch2', 180, '2', '{h}: c◐ / d', (-4.8, 1.8), 'right', 0.10),
    ('K_switch_led', 90, '1', '{h}: e', (1.5, -12.0), 'center', 0),
    ('Bal_switch', 180, '2', '{h}: f / контакт балкон', (-4.6, 1.2), 'right', 0),
    ('Hall_switch_entry', 90, 'w', '{h}: g↔ (+ звънец)', (3.0, 4.6), 'left', 0.12),
    ('Hall_switch_living', 0, 'w', '{h}: g↔', (4.4, -2.8), 'left', 0.08),
    ('Hall_switch_bath', 180, '2', '{h}: n / p', (-4.4, 8.5), 'right', 0),
    ('Bedroom_switch', 90, 'w2', '{h}: h↔ / i', (1.5, 5.6), 'left', 0),
    ('Bed_switch0', 180, 'x2', '{h}: k / h✕', (-4.6, 2.2), 'right', 0),
    ('Bed_switch1', 180, 'w2', '{h}: l / h↔', (-4.6, -2.2), 'right', 0),
]
# lights: group letter -> list of (light name or object, kind)
GROUPS = {
    'a': ([('AisleDown0', 'down'), ('AisleDown1', 'down'), ('LivingDown0', 'down'), ('LivingDown1', 'down'), ('LivingDown2', 'down')], 'L1'),
    'b': ([(f'KitchenDown{i}', 'down') for i in range(2)], 'L1'),
    'c': ([('Pendant_dining0_bulb', 'ceil'), ('Pendant_dining1_bulb', 'ceil')], 'L1'),
    'd': ([('Sconce0_up', 'wall0'), ('Sconce1_up', 'wall0'), ('PictureLight', 'pic0'), ('PictureLight2', 'pic0')], 'L1'),
    'f': ([('Balcony_wall_light_L', 'wall90')], 'L1'),
    'g': ([('HallDown0', 'down'), ('HallDown1', 'down')], 'L2'),
    'h': ([('Pendant_bedroom_bulb', 'ceil')], 'L2'),
    'k': ([('WallLamp0_light', 'wall180')], 'L2'),
    'l': ([('WallLamp1_light', 'wall180')], 'L2'),
    'n': ([('BathSpot0', 'downip'), ('BathSpot1', 'downip'), ('BathSpot2', 'downip')], 'L3'),
}
# LED strips: object -> group
LEDS = [('K_led_B', 'e'), ('K_led_L0', 'e'), ('K_led_L1', 'e'), ('WU_led_upper', 'd'), ('WU_console_led', 'd'),
        ('WU_shelf0_led', 'd'), ('Curtain_cove_led', 'd'),
        ('Hall_unit_led', 'g'), ('BW_t0_niche_led', 'i'), ('BW_t1_niche_led', 'i'), ('BW_bridge_led', 'i'),
        ('Wint_led_A', 'm'), ('Wint_led_B', 'm'), ('Mirror_side_led0', 'p'), ('Mirror_side_led1', 'p')]
DRIVERS = [('K_upper_carc_B', 'e', 0.5), ('WU_upper_body', 'd', 0.5), ('Hall_unit_upper', 'g', 0.5),
           ('BW_bridge_carc', 'i', 0.5), ('Wardrobe_carc', 'm', 0.75)]


def led_line(n):
    x0, y0, x1, y1 = G.bb(n)
    if x1 - x0 >= y1 - y0:
        return [(x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2)]
    return [((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1)]


def light_xy(n):
    if n in G.LIGHT:
        return G.lpos(n)[:2]
    return G.ctr(n)


def draw_light(ax, S, n, kind):
    x, y = light_xy(n)
    if kind.startswith('wall') or kind.startswith('pic'):
        ang = int(kind[4:] if kind.startswith('wall') else kind[3:])
        # snap to the wall face
        if ang == 0: x = 0.0
        if ang == 180: x = G.X_E if x > 4 else G.X_LIV1
        if ang == 90: y = G.bb('Bal_slab_floor')[1]; x -= 0.10   # symbol shifted clear of the isolator
        px, py = S.P(x, y)
        EL.light(ax, px, py, 'wall' if kind.startswith('wall') else 'pic', ang=ang, stem=1.9)
    else:
        px, py = S.P(x, y)
        EL.light(ax, px, py, kind)
    return S.P(x, y)


def zones(S):
    """Bathroom zones per HD 60364-7-701 (shower without tray, fixed side glass + bi-fold door)."""
    SH = G.SHOWER
    fx0, fy0, fx1, fy1 = SH['side'][0], SH['door'][1], G.X_E, G.Y_BATH1
    z0 = sbox(fx0, fy0, fx1, fy1)
    head = SH['head']
    circ = Point(head).buffer(1.20, 64)
    far = 3.0
    def ext(px, py):
        dx, dy = px - head[0], py - head[1]
        L = math.hypot(dx, dy)
        return (head[0] + dx / L * far, head[1] + dy / L * far)
    o0, o1 = SH['bf0'][0], SH['bf1'][2]
    wedge = SPoly([head, ext(o0, fy0), ext(o1, fy0)])
    z1_out = circ.intersection(wedge).intersection(sbox(G.X_BATH0, 0.0, G.X_E, fy0))
    S.shp(z0, fc='#CFE3F7', ec='none', lw=0, z=3)
    S.shp(z1_out, fc='none', ec='#1F5FA8', lw=0.0, hatch='....', z=3)
    S.shp(z1_out, fc='none', ec='#1F5FA8', lw=0.5, z=3.1)
    S.text(fx1 - 0.15, fy1 - 0.42, '0/1', fs=5.5, color='#1F5FA8', weight='bold', z=4)
    S.text((o0 + o1) / 2 - 0.12, fy0 - 0.14, '1', fs=5.5, color='#1F5FA8', weight='bold', z=4)


def lab(ax, px, py, dx, dy, t, ha, col, fs=4.4):
    if abs(dx) > 6 or abs(dy) > 6:
        ax.plot([px, px + dx], [py, py + dy * 0.85], color='0.3', lw=0.25, zorder=31)
    ax.text(px + dx, py + dy, t, fontsize=fs, ha=ha, va='center', zorder=32, color=col,
            bbox=dict(boxstyle='square,pad=0.05', fc='white', ec='none', alpha=0.85), linespacing=1.1)


def along(ang, d):
    return (0, d) if ang in (0, 180) else (d, 0)


def main():
    S = Sheet('04', 'Електро', ox=50, oy=84)
    S.walls('solid')
    S.openings(swing=True, labels=False, color='0.45')
    S.furniture('faint')
    zones(S)
    ax = S.ax
    for n, g in LEDS:
        S.line(led_line(n), lw=1.6, color=LED, ls=(0, (3, 1.2)), z=25)
    for (n, g, f) in DRIVERS:
        x0, y0, x1, y1 = G.bb(n)
        px, py = S.P(x0 + (x1 - x0) * f, (y0 + y1) / 2) if (x1 - x0) > (y1 - y0) else S.P((x0 + x1) / 2, y0 + (y1 - y0) * f)
        EL.driver(ax, px, py)
        ax.text(px + 2.0, py + 1.4, g, fontsize=4.6, color='#8A5A00', zorder=31, weight='bold')
    # AC indoor units + refrigerant / condensate route to the outdoor unit
    for n in ('AC_indoor', 'AC_bed_indoor'):
        S.rect(*G.bb(n), lw=0.6, ec=PUR, fc='white', ls=(0, (3, 1.5)), z=24)
    ai = G.bb('AC_indoor'); ab = G.bb('AC_bed_indoor'); ao = G.AC_OUT
    S.text((ai[0] + ai[2]) / 2, (ai[1] + ai[3]) / 2, 'КЛ-В1', fs=4.0, color=PUR, rotation=90, weight='bold', z=26)
    S.text((ab[0] + ab[2]) / 2, (ab[1] + ab[3]) / 2, 'КЛ-В2', fs=4.0, color=PUR, weight='bold', z=26)
    px, py = S.P(G.X_LIV1, 2.15); EL.outlet_box(ax, px, py, 180, 'КЛ')
    ax.text(px - 3.6, py - 3.2, f'{int(round(2.37 * 100))}/AC', fontsize=4.2, ha='right', color=PUR, zorder=32,
            bbox=dict(boxstyle='square,pad=0.05', fc='white', ec='none'))
    yb = G.bb('Bal_frame_bot')[1]
    route1 = [(G.X_LIV1 - 0.06, ai[3]), (G.X_LIV1 - 0.06, yb + 0.30), (3.62, yb + 0.30), (3.62, 6.62), (ao[0], 6.62)]
    route2 = [((ab[0] + ab[2]) / 2, ab[3]), (3.56, ab[3] + 0.05), (3.56, G.Y_BED1 - 0.05), (3.62, G.Y_BED1 + 0.10)]
    for r in (route1, route2):
        S.line(r, lw=0.8, color=PUR, ls=(0, (6, 2, 1, 2)), z=24)
    S.text(2.78, 6.12, 'фреон + дренаж КЛ-В1\n(в ъгъла, ГК обшивка)', fs=4.0, color=PUR, z=26,
           bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='none'))
    S.text(4.30, 6.62, 'трасе към КЛ-Н (по тавана на балкона)', fs=4.0, color=PUR, z=26,
           bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='none'))
    S.text((ao[0] + ao[2]) / 2 - 0.03, ao[1] + 0.68, 'КЛ-Н', fs=4.6, color=PUR, weight='bold', z=26,
           bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='none'))
    # board (flush, drawn in the wall), intercom, bell, router, smoke alarm
    eb = G.bb('Elec_board')
    px, py = S.P(eb[0], (eb[1] + eb[3]) / 2); EL.board(ax, px, py, 180)
    ax.text(px - 3.0, py + 4.6, f'ЕТ (вграден)\nh {int(round(G.bz("Elec_board")[0]*100))}–{int(round(G.bz("Elec_board")[1]*100))}',
            fontsize=4.2, ha='right', va='center', zorder=31, weight='bold',
            bbox=dict(boxstyle='square,pad=0.05', fc='white', ec='none'))
    px, py = S.P(*wallpt('Hall_intercom', 0)); EL.box(ax, px + 2.0, py, 'ДФ', w=3.6, h=2.4, color=BLUE)
    db = G.bb('Door_bell'); px, py = S.P((db[0] + db[2]) / 2, db[1]); EL.box(ax, px, py - 1.8, 'З', w=2.6, h=2.4, color=BLUE)
    ax.text(px + 2.0, py - 1.8, f'бутон звънец {H("Door_bell")} (отвън)', fontsize=3.9, color=BLUE, ha='left', va='center', zorder=31)
    px, py = S.P(*G.ctr('Media_router')); EL.box(ax, px - 3.0, py - 4.0, 'Р', w=3.0, h=2.6, color=BLUE)
    S.line([(3.55, eb[1]), (3.55, G.Y_COR1 - 0.10), (3.25, G.Y_COR1 - 0.10), (3.25, 4.40)], lw=0.6, color=BLUE, ls=(0, (1.5, 1.2)), z=23)
    S.text(2.35, 3.90, 'тръба Ø25: интернет / КТВ\nот шахтата до конзолата', fs=3.9, color=BLUE, z=26,
           bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='none'))
    px, py = S.P(*G.ctr('Hall_smoke_alarm')); EL.box(ax, px, py, 'ДД', w=3.6, h=2.6, color=RED)
    px, py = S.P(*G.ctr('Bath_fan')); EL.fan(ax, px, py)
    ax.text(px + 2.2, py + 2.0, 'ВН', fontsize=4.2, ha='left', va='bottom', zorder=31, weight='bold',
            bbox=dict(boxstyle='square,pad=0.05', fc='white', ec='none', alpha=0.85))
    # boiler outlet (B3) at the boiler, on the wall x = 6.65
    bo = G.bb('Boiler')
    H_ = lambda _b: f"{int(round(G.bz('Boiler')[0] * 100))}–{int(round(G.bz('Boiler')[1] * 100))}"
    px, py = S.P(G.X_E, bo[3] - 0.12); EL.outlet_box(ax, px, py, 180, 'Б')
    lab(ax, px, py, 9.0, 0, f'B3 бойлер\n(верт., h {H_(bo)})', 'left', 'k')

    for row in SOCKETS:
        n, k, ang, t, (dx, dy), ha, sh = row[:7]
        x, y = wallpt(n, ang); ox, oy = along(ang, sh)
        px, py = S.P(x + ox, y + oy)
        if k == 's1': EL.socket(ax, px, py, ang, 1)
        elif k == 's2': EL.socket(ax, px, py, ang, 2)
        elif k == 's3': EL.socket(ax, px, py, ang, 3)
        elif k == 's1ip': EL.socket(ax, px, py, ang, 1, ip=True)
        elif k == 'box': EL.outlet_box(ax, px, py, ang, row[7])
        elif k == 'tp': EL.data_out(ax, px, py, ang, row[7])
        lab(ax, px, py, dx, dy, t.format(h=H(n)), ha, BLUE if k == 'tp' else 'k')
    for g, (items, circ) in GROUPS.items():
        for (n, kind) in items:
            px, py = draw_light(ax, S, n, kind)
        # group letter next to the first fixture
        i0 = {'b': 1}.get(g, 0)
        px, py = draw_light(ax, S, items[i0][0], items[i0][1])
        off = {'a': (2.6, 2.2), 'b': (2.6, 2.6), 'c': (0, 3.6), 'd': (5.6, 2.4), 'f': (-5.5, 1.8), 'g': (2.6, 1.8),
               'h': (2.8, 2.0), 'k': (-7.0, 2.4), 'l': (-7.0, -2.4), 'n': (2.4, 2.4)}[g]
        ax.text(px + off[0], py + off[1], g, fontsize=5.0, color='#7A4A00', weight='bold', zorder=33, ha='center', va='center',
                bbox=dict(boxstyle='circle,pad=0.1', fc='white', ec='#7A4A00', lw=0.35))
    for (n, ang, kind, t, (dx, dy), ha, sh) in SWITCHES:
        x, y = wallpt(n, ang); ox, oy = along(ang, sh)
        px, py = S.P(x + ox, y + oy)
        EL.switch(ax, px, py, ang, 'x' if kind == 'x2' else kind)
        lab(ax, px, py, dx, dy, t.format(h=H(n)), ha, RED)

    legend(S)
    circuits(S)
    notes(S)
    S.scale_bar(140, 68, n=4)
    S.title_block()
    S.save('04 Електро')


def legend(S):
    ax = S.ax
    X, Y, W, H_ = 230, 222, 180, 64
    S.legend_box(X, Y, W, H_, 'Легенда (БДС EN 60617)')
    items = [
        ('s1', 'Контакт със ЗК, 16 A (единичен)'), ('s2', 'Контакт двоен / троен'), ('s1ip', 'Контакт IP44 с капак'),
        ('box', 'Изход за директно свързване (уред, LED огледало)'), ('tp', 'Розетка RJ45 cat. 6 / ТВ'),
        ('sw1', 'Ключ еднополюсен / сериен'), ('sww', 'Ключ девиаторен (↔)'), ('swx', 'Ключ кръстат (✕)'),
        ('brd', 'Ел. табло (ЕТ), вградено'), ('ceil', 'Таванно тяло / пендел'), ('down', 'Луна LED (с пръстен – IP44/65)'),
        ('wall', 'Аплик / лампа за четене'), ('pic', 'Картинна лампа'), ('led', 'LED лента 24 V, 2700 K'),
        ('drv', 'Захранващ блок LED'), ('fan', 'Вентилатор баня'), ('dbx', 'Домофон / звънец / рутер / датчик дим'),
        ('ac', 'Климатик вътр./външно, трасе'),
    ]
    for i, (k, t) in enumerate(items):
        c, r = divmod(i, 9)
        x = X + 4 + c * W / 2
        y = Y + H_ - 11 - r * 5.6
        if k == 's1': EL.socket(ax, x, y - 1, 90, 1)
        elif k == 's2': EL.socket(ax, x - 2.4, y - 1, 90, 2); EL.socket(ax, x + 3.4, y - 1, 90, 3, r=0.9)
        elif k == 's1ip': EL.socket(ax, x, y - 1, 90, 1, ip=True)
        elif k == 'box': EL.outlet_box(ax, x - 1.5, y, 0, 'К')
        elif k == 'tp': EL.data_out(ax, x - 2.8, y, 0, 'TP')
        elif k == 'sw1': EL.switch(ax, x - 2, y - 1.2, 90, '1'); EL.switch(ax, x + 2.5, y - 1.2, 90, '2')
        elif k == 'sww': EL.switch(ax, x, y - 1.2, 90, 'w')
        elif k == 'swx': EL.switch(ax, x, y - 1.2, 90, 'x')
        elif k == 'brd': EL.board(ax, x - 1.2, y, 0)
        elif k == 'ceil': EL.light(ax, x, y, 'ceil')
        elif k == 'down': EL.light(ax, x - 2, y, 'down'); EL.light(ax, x + 2.2, y, 'downip')
        elif k == 'wall': EL.light(ax, x - 1.5, y, 'wall', ang=0)
        elif k == 'pic': EL.light(ax, x - 1.5, y, 'pic', ang=0)
        elif k == 'led': ax.plot([x - 3, x + 3.5], [y, y], color=LED, lw=1.6, ls=(0, (3, 1.2)), zorder=30)
        elif k == 'drv': EL.driver(ax, x, y)
        elif k == 'fan': EL.fan(ax, x, y)
        elif k == 'dbx': EL.box(ax, x - 1.5, y, 'ДФ', w=3.6, h=2.4, color=BLUE); EL.box(ax, x + 2.6, y, 'З', w=2.4, h=2.4, color=BLUE)
        elif k == 'ac':
            ax.add_patch(Rectangle((x - 3.5, y - 1.3), 4, 2.6, fc='white', ec=PUR, lw=0.6, ls=(0, (3, 1.5)), zorder=30))
            ax.plot([x + 1, x + 4], [y, y], color=PUR, lw=0.8, ls=(0, (6, 2, 1, 2)), zorder=30)
        ax.text(x + 7.5, y, t, fontsize=4.7, va='center', zorder=31)
    ax.text(X + 3, Y + 2.8, 'Надписи: „111/К1“ = височина до оста, cm / токов кръг; a … p = група осветление (лист 06); '
            '0, 1 = зони в банята.', fontsize=4.2, va='center', zorder=31, color='0.2')


CIRC = [
    ('L1', 'Осветление дневна, кухня, трапезария, балкон (a–f)', 'B10', '3×1,5', 'ДТЗ1'),
    ('L2', 'Осветление коридор, спалня, гардероб (g–m)', 'B10', '3×1,5', 'ДТЗ2'),
    ('L3', 'Осветление баня + вентилатор (n, p)', 'B10', '3×1,5', 'ДТЗ3'),
    ('S1', 'Контакти дневна: трапезария, диван, ТВ, конзола, лампион', 'B16', '3×2,5', 'ДТЗ1'),
    ('S2', 'Контакти бюро + спалня (ниши, тоалетка, LED огледало, врата)', 'B16', '3×2,5', 'ДТЗ2'),
    ('S3', 'Контакти коридор (прахосм., зарядно) + балкон IP44', 'B16', '3×2,5', 'ДТЗ2'),
    ('К1', 'Кухня: контакти над плота + абсорбатор', 'B16', '3×2,5', 'ДТЗ1'),
    ('К2', 'Хладилник', 'B16', '3×2,5', 'собств. RCBO'),
    ('К3', 'Съдомиялна', 'B16', '3×2,5', 'ДТЗ2'),
    ('К4', 'Фурна', 'B16', '3×2,5', 'ДТЗ3'),
    ('К5', 'Котлон индукционен домино 3 kW', 'B20', '3×2,5', 'ДТЗ 25 A'),
    ('B1', 'Пералня-сушилня', 'B16', '3×2,5', 'ДТЗ3'),
    ('B2', 'Контакт баня IP44 + сушилник за кърпи (изход IP44)', 'B16', '3×2,5', 'ДТЗ3'),
    ('B3', 'Бойлер Eldom Galant DU060W 60 л', 'B16', '3×2,5', 'ДТЗ3'),
    ('AC', 'Климатик multi-split (КЛ-Н + КЛ-В1, КЛ-В2)', 'C20', '3×2,5', 'собств. RCBO'),
]


def circuits(S):
    ax = S.ax
    X, W = 230, 180
    top = 218
    rh = 4.15
    H_ = 9 + rh * len(CIRC) + 14
    Y = top - H_
    S.legend_box(X, Y, W, H_)
    cols = [X + 2, X + 12, X + 104, X + 132, X + 156]
    for cx, t in zip(cols, ['Кръг', 'Предназначение', 'Защита', 'Кабел, mm²', 'ДТЗ']):
        ax.text(cx, top - 4.4, t, fontsize=5.2, weight='bold', va='center', zorder=31)
    ax.plot([X, X + W], [top - 8, top - 8], 'k', lw=0.35, zorder=31)
    for i, r in enumerate(CIRC):
        y = top - 8 - rh * (i + 0.5) - 0.5
        if i % 2:
            ax.add_patch(Rectangle((X + 0.3, y - rh / 2), W - 0.6, rh, fc='0.94', ec='none', zorder=15.5))
        for cx, v in zip(cols, r):
            ax.text(cx, y, v, fontsize=4.6, va='center', zorder=31, weight='bold' if cx == cols[0] else 'normal')
    for cx in cols[1:]:
        ax.plot([cx - 1.2, cx - 1.2], [Y + 14, top], 'k', lw=0.2, zorder=31)
    ax.plot([X, X + W], [Y + 14, Y + 14], 'k', lw=0.35, zorder=31)
    ax.text(X + 2, Y + 12,
            'ЕТ (вграден, 2×12 модула): главен прекъсвач 3×25 A; катодна защита (SPD) тип 2; ДТЗ1–ДТЗ3: 40 A / 30 mA, тип A;\n'
            'К5 – ДТЗ 25 A / 30 mA + автомат 20 A, 3×2,5 mm² (домино котлон 3,6 kW, монофазно); К2 и AC – собствени RCBO 30 mA.\n'
            'Кабели NYM/СВТ (Cu) в гофрирани тръби; система TN-S, PE във всеки кръг. Слаботокови: UTP cat. 6, RG6.',
            fontsize=4.2, va='top', zorder=31, linespacing=1.4)


def notes(S):
    ax = S.ax
    X, Y = 230, 128
    ax.text(X, Y, 'Монтажни височини (до оста, от готов под) – по 3D модела:', fontsize=5.6, weight='bold', va='top', zorder=31)
    hk = lambda n: fmt(G.zc(n))
    ax.text(X, Y - 4.2,
            f'• Контакти общо {hk("Dining_socket")} m; кухня над плота {hk("K_socket_prep")} m (черни); СМ {hk("K_conn_dw")} m зад долното чекмедже;\n'
            f'  фурна {hk("K_conn_oven")} m зад изтеглящия се шкаф 18; котлон {hk("K_conn_hob")} m (230 V / 20 A, домино 3 kW); абсорбатор {hk("K_conn_hood")} m и\n'
            f'  хладилник {hk("K_conn_fridge")} m – в горните шкафове. Бюро {hk("Desk_socket")} m; ТВ {hk("TV_socket")} m; конзола {hk("Media_socket")} m;\n'
            f'  ниши до леглото {hk("Bed_socket0")} m; тоалетка {hk("Dresser_socket")} m; кутия LED огледало {hk("Vanity_mirror_feed")} m (зад огледалото);\n'
            f'  баня IP44 {hk("Bath_socket_ip44")} m; пералня {hk("Washer_socket")} m.\n'
            f'• Ключове {hk("Living_switch")} m (в нишите до леглото {hk("Bed_switch0")} m); ключът на банята – в коридора откъм\n'
            '  бравата на плъзгащата врата. Спалня таван (h): девиатор при вратата + кръстат и девиатор в нишите = 3 места.\n'
            f'• ЕТ {fmt(G.bz("Elec_board")[0])}–{fmt(G.bz("Elec_board")[1])} m, вграден в стената на коридора; домофон {hk("Hall_intercom")} m;\n'
            f'  звънец отвън {hk("Door_bell")} m; прекъсвач КЛ-Н {hk("AC_isolator")} m; захранване КЛ-В {fmt(2.37)} m; ДД – таван.\n'
            '• Символите на близки точки са леко раздалечени за четимост – меродавни са координатите в 3D модела.',
            fontsize=4.4, va='top', zorder=31, linespacing=1.4)
    X2, Y2 = 22, 64
    ax.text(X2, Y2, 'Нормативна основа и бележки:', fontsize=5.6, weight='bold', va='top', zorder=31)
    ax.text(X2, Y2 - 4.2,
            '1. Наредба № 3/2004 за устройството на електрическите уредби и електропроводните линии; БДС HD 60364-4-41 (ДТЗ ≤ 30 mA за\n'
            '   всички контакти до 32 A и всички кръгове в банята); БДС HD 60364-5-52 (сечения); БДС HD 60364-7-701 (бани).\n'
            '2. Баня (душ без корито): зона 0 – подът на душа; зона 1 – до 2,25 m, R 1,20 m от душа, ограничена от неподвижните стъкла.\n'
            '   В зони 0/1 – само фиксирани уреди SELV/IPX4+; контакти и ключове – извън зоните. Луна над душа IP65, останалите IP44.\n'
            '3. Схемата е интериорно задание. Ел. проектът, изпълнението и измерванията – от правоспособни лица.',
            fontsize=4.4, va='top', zorder=31, linespacing=1.4)


if __name__ == '__main__':
    main()
