# -*- coding: utf-8 -*-
"""Geometry of Apartment 75 (model metres; x right, y toward the facade, z up, ceiling 2.60).
EVERYTHING is read from ..\\scene_export_now.json (current 3D model). No hard-coded furniture
positions: only the grouping of export objects into drawing items lives here."""
import json as _json, os as _os, re as _re
from shapely.geometry import box
from shapely.ops import unary_union

SCENE = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), 'scene_export_now.json')
_J = _json.load(open(SCENE, encoding='utf-8'))
OBJS = [o for o in _J['objects'] if not o['name'].startswith(('INT_', 'CAB_'))]
OBJ = {o['name']: o for o in OBJS}
LIGHT = {l['name']: l for l in _J['lights']}
CEIL = 2.60


def _sel(names=(), prefix=None, rx=None):
    out = [OBJ[n] for n in names]
    if prefix:
        out += [o for o in OBJS if o['name'].startswith(prefix)]
    if rx:
        out += [o for o in OBJS if _re.match(rx, o['name'])]
    if not out:
        raise KeyError((names, prefix, rx))
    return out


def bb(*names, prefix=None, rx=None):
    """plan bbox (x0, y0, x1, y1)."""
    os_ = _sel(names, prefix, rx)
    return (min(o['min'][0] for o in os_), min(o['min'][1] for o in os_),
            max(o['max'][0] for o in os_), max(o['max'][1] for o in os_))


def bz(*names, prefix=None, rx=None):
    os_ = _sel(names, prefix, rx)
    return (min(o['min'][2] for o in os_), max(o['max'][2] for o in os_))


def b3(name):
    o = OBJ[name]; return tuple(o['min']) + tuple(o['max'])


def ctr(*a, **k):
    x0, y0, x1, y1 = bb(*a, **k)
    return ((x0 + x1) / 2, (y0 + y1) / 2)


def zc(*a, **k):
    z0, z1 = bz(*a, **k); return (z0 + z1) / 2


def lpos(name):
    return tuple(LIGHT[name]['loc'])


def prop(name, key, default=''):
    return (OBJ[name].get('props') or {}).get(key, default)


def c(v):
    """metres -> cm string (Bulgarian decimal comma)."""
    r = round(v * 100, 1)
    return str(int(round(r))) if abs(r - round(r)) < 0.05 else f'{r:.1f}'.replace('.', ',')


def wdh(*names, along='x', prefix=None, rx=None, z=True):
    """'W×D×H' in cm; W along the given plan axis."""
    x0, y0, x1, y1 = bb(*names, prefix=prefix, rx=rx)
    w, d = (x1 - x0, y1 - y0) if along == 'x' else (y1 - y0, x1 - x0)
    r = lambda v: str(int(round(v * 100)))
    s = f'{r(w)}×{r(d)}'
    if z:
        z0, z1 = bz(*names, prefix=prefix, rx=rx); s += f'×{r(z1 - z0)}'
    return s


# ---------------------------------------------------------------- walls (from the export)
_EXT_N = ['Wall_B', 'Wall_L', 'Wall_T_a', 'Wall_T_b', 'Wall_R_c', 'Wall_R_b_thick', 'W2_B_a', 'W2_B_b_0', 'W2_B_b_1',
          'W2_BT_a', 'W2_BT_b', 'W2_ext_R_0', 'W2_ext_R_1', 'Bal_wall_R']
_PART_N = ['Wall_R_a', 'Wall_R_b_0', 'Wall_R_b_1', 'W2_CT_a', 'W2_CT_b', 'W2_CB_a', 'W2_CB_b', 'W2_bath_T']
EXT_RECTS = [bb(n) for n in _EXT_N]
PART_RECTS = [bb(n) for n in _PART_N]


def wall_polys():
    ext = unary_union([box(*r) for r in EXT_RECTS])
    part = unary_union([box(*r) for r in PART_RECTS]).difference(ext)
    return ext, part


# key coordinates (all from the export)
X_LIV1 = bb('Floor')[2]                 # 3.35 living east face
X_COR0 = bb('Floor_vinyl_corridor')[0]  # 3.47
X_COR1 = bb('Floor_vinyl_corridor')[2]  # 4.77
X_BATH0 = bb('Bath_floor')[0]           # 4.89
X_E = bb('Bath_floor')[2]               # 6.65
Y_N = bb('Floor')[3]                    # 6.65
Y_BATH1 = bb('Bath_floor')[3]           # 1.68
Y_NICHE0 = bb('Floor_niche')[1]         # 1.92
Y_BED0 = bb('Floor_bed')[1]             # 2.44
Y_BED1 = bb('Floor_bed')[3]             # 5.34
Y_COR1 = bb('Floor_vinyl_corridor')[3]  # 2.33

# ---------------------------------------------------------------- rooms
ROOMS = {
    'living': dict(name='Дневна, кухня и трапезария', rects=[bb('Floor')], h=CEIL, arch=22.01),
    'corr': dict(name='Преддверие / коридор', rects=[bb('Floor_vinyl_corridor')], h=CEIL, arch=3.03),
    'bed': dict(name='Спалня', rects=[bb('Floor_bed'), bb('Floor_niche')], h=CEIL, arch=10.37),
    'bath': dict(name='Баня с WC', rects=[bb('Bath_floor')], h=CEIL, arch=2.96),
    'balc': dict(name='Балкон', rects=[bb('Balcony_decking')], h=CEIL, arch=3.08),
}


def room_area(k):
    return sum((r[2] - r[0]) * (r[3] - r[1]) for r in ROOMS[k]['rects'])


# floor finishes: one continuous SPC vinyl except the bathroom (tiles), balcony decking
VINYL_ZONES = [bb(n) for n in ('Floor', 'Floor_bed', 'Floor_door_bal', 'Floor_door_bed', 'Floor_doorsills',
                               'Floor_niche', 'Floor_vinyl_corridor', 'Floor_vinyl_door_entry')]
TILE_ZONES = [bb('Bath_floor'), bb('Floor_tile_door_bath')]
DECK_ZONE = bb('Balcony_decking')
PROFILES = [((bb('Floor_tile_door_bath')[0], bb('Floor_tile_door_bath')[1]),
             (bb('Floor_tile_door_bath')[0], bb('Floor_tile_door_bath')[3]))]
FLOOR_VINYL = 'Ламиниран винил SPC, вид дъб, един непрекъснат под (без прагове)'
FLOOR_TILE = 'Гранитогрес Star Gres Town Antracite 60×60 (под баня и душ)'
FLOOR_DECK = 'Декинг IKEA RUNNEN 30×30, тъмно сив'

# ---------------------------------------------------------------- openings
_dl = bb('Door_leaf'); _bl = bb('BedDoor_leaf'); _el = bb('EntrDoor_leaf'); _pk = bb('BathDoor_leaf')
_gap_bath = (bb('W2_CB_a')[3], bb('W2_CB_b')[1])          # pocket door opening y 0.15–0.97
DOORS = [
    dict(id='entr', hinge=(_el[2], bb('EntrDoor_frame_R')[3]), a_closed=180, a_open=90, r=_el[2] - _el[0],
         w=round((bb('EntrDoor_frame_R')[0] - bb('EntrDoor_frame_L')[2]) * 100 + 4), h=210, tag='Д1', txt='100/210'),
    dict(id='liv', hinge=(X_LIV1, _dl[1]), a_closed=90, a_open=180, r=_dl[3] - _dl[1], tag='Д2', txt='90/200'),
    dict(id='bed', hinge=(bb('W2_CT_a')[2], Y_BED0), a_closed=0, a_open=90, r=_bl[3] - Y_BED0 + 0.0, tag='Д3', txt='80/200'),
]
POCKET = dict(gap=(bb('W2_CB_a')[0], _gap_bath[0], bb('W2_CB_a')[2], _gap_bath[1]), leaf=_pk, tag='Д4',
              txt=f'{c(_gap_bath[1] - _gap_bath[0])}/{c(bz("W2_CB_lintel")[0])}')
_gz = bb('Glz_frame_bot'); _bw = bb('BedWin_fB'); _bd = bb('BedBalDoor_fB'); _bf = bb('Bal_frame_bot')
WINDOWS = [
    dict(id='livfac', gap=(bb('Wall_T_a')[2], Y_N, bb('Wall_T_b')[0], bb('Wall_T_a')[3]), frame=(_gz[1], _gz[3]), ori='h',
         mulls=[ctr('Glz_mullion1')[0], ctr('Glz_mullion2')[0]], tag='ПП3',
         leaf=dict(hinge=(bb('Glz_frame_L')[2], _gz[1]), a_closed=0, a_open=270,
                   r=bb('Glz_mullion1')[0] - bb('Glz_frame_L')[2])),
    dict(id='bedwin', gap=(bb('W2_BT_a')[2] + 0.80, Y_BED1, bb('W2_BT_b')[0], bb('W2_BT_b')[3]), frame=(_bw[1], _bw[3]),
         ori='h', mulls=[ctr('BedWin_mul5.43')[0]], tag='ПП4'),
]
WINDOWS[1]['gap'] = (_bw[0], Y_BED1, _bw[2], bb('W2_BT_b')[3])
GLZ_DOOR_GAPS = [dict(gap=(X_LIV1, _bf[1], bb('Wall_R_c')[2], _bf[3]), frame=(_bf[0], _bf[2]), ori='v'),
                 dict(gap=(_bd[0], Y_BED1, _bd[2], bb('W2_BT_a')[3]), frame=(_bd[1], _bd[3]), ori='h')]
BAL_DOORS = [dict(hinge=(_bf[0], _bf[3]), a_closed=270, a_open=180, r=_bf[3] - _bf[1], tag='ПП1'),
             dict(hinge=(_bd[0], _bd[1]), a_closed=0, a_open=270, r=_bd[2] - _bd[0], tag='ПП2')]
RAIL = bb('Bal_rail_base')
BAL_SLAB = bb('Bal_slab_floor')

# ---------------------------------------------------------------- furniture items
FURN = []


def F(key, name, shapes, room, anchor, **kw):
    FURN.append(dict(key=key, name=name, shapes=shapes, room=room, anchor=anchor, **kw))


# ---- kitchen
TOP_B = bb('K_top_a', 'K_top_b', 'K_top_c', 'K_top_d')
TOP_L = bb('K_top_L')
SINK = bb('K_sink_bottom')
HOB = bb('K_hob')
HOOD = bb('K_hood')
FRIDGE = bb('K_fridge')
K_FRONTS_B = [('K_front_corner_door', 'LeMans'), ('K_front_sink_bins', 'кошове'), ('K_front_dw', 'СМ45'),
              ('K_front_drawer0', 'чекм.')]
F(1, 'Кухня по поръчка – долни шкафове с плот', [
    ('poly', [(TOP_B[0], TOP_B[1]), (TOP_B[2], TOP_B[1]), (TOP_B[2], TOP_B[3]), (TOP_L[2], TOP_B[3]),
              (TOP_L[2], TOP_L[3]), (TOP_L[0], TOP_L[3])], 'solid'),
    ('rect', bb('K_end_panel'), 'solid'),
    ('sink', SINK), ('hob', HOB),
] + [('rect', (bb(n)[0], 0.04, bb(n)[2], bb(n)[1] - 0.02), 'thin', t) for n, t in K_FRONTS_B[1:]],
  'living', anchor=(0.30, 0.30))
F(2, 'Хладилник свободностоящ 60 + дъбов панел + шкаф горе', [
    ('tall', FRIDGE), ('rect', bb('K_fridge_panel'), 'solid'),
    ('rect', bb('K_fridge_upper', 'K_fridge_upper_front'), 'over')], 'living', anchor=ctr('K_fridge'))
_UB = bb('K_upper_carc_B', prefix='K_upper_front_B')
_UL = bb(prefix='K_upper_carc_L')
F(3, 'Горни шкафове кухня + абсорбатор', [
    ('rect', (_UB[0], _UB[1], _UB[2], _UB[3]), 'over'), ('rect', _UL, 'over'), ('rect', HOOD, 'over')],
  'living', anchor=(1.90, 0.80), leader=(1.90, 0.34))
DINING = bb('Dining_top')
F(4, 'Маса трапезна', [('rect', DINING, 'solid')], 'living', anchor=ctr('Dining_top'))
CHAIRS = []
for _s, _back in (('DChair_S_seat', 'DChair_S_backrail'), ('DChair_E_seat.001', 'DChair_E_backrail.001'),
                  ('DChair_E_seat', 'DChair_E_backrail'), ('DChair_E_seat.002', 'DChair_E_backrail.002')):
    _x0, _y0, _x1, _y1 = bb(_s)
    _ang = 0 if ctr(_back)[1] < ctr(_s)[1] else 180
    CHAIRS.append(('chair', ((_x0 + _x1) / 2, (_y0 + _y1) / 2, _x1 - _x0, _y1 - _y0, _ang)))
F(5, 'Стол трапезен', CHAIRS, 'living', anchor=CHAIRS[1][1][:2], qty=4)
WU = dict(endL=bb('WU_end_L'), endR=bb('WU_end_R'), desk=bb('WU_desk_slab'), cons=bb('WU_console_top'),
          upper=bb('WU_upper_body', prefix='WU_upper_door'), step=bb('WU_step'), side=bb('WU_desk_side'),
          back=bb('WU_back_back', 'WU_back_reeds'), shelf=bb('WU_shelf0'))
F(6, 'ТВ модул и бюро по поръчка', [
    ('rect', WU['back'], 'thin', ''), ('rect', WU['desk'], 'solid'), ('rect', WU['cons'], 'solid'),
    ('rect', WU['endL'], 'solid'), ('rect', WU['endR'], 'solid'),
    ('rect', WU['shelf'], 'over'), ('rect', WU['upper'], 'over')],
  'living', anchor=(3.08, 4.15))
F(7, 'Телевизор 65"', [('rect', bb('TV_body'), 'solid')], 'living', anchor=(3.06, 5.25), leader=(3.26, 5.25))
_cs = bb('LvChair_seat'); _cb = bb('LvChair_back')
F(8, 'Работен стол с облегалка', [('taskchair', _cs, _cb)], 'living', anchor=ctr('LvChair_seat'))
SOFA = bb('Sofa_back', 'Sofa_armL', 'Sofa_armR', 'Sofa_base')
F(9, 'Диван IKEA LANDSKRONA (наличен)', [('sofa', SOFA, 3, bb('Sofa_back')[2] - SOFA[0], bb('Sofa_armL')[3] - SOFA[1])],
  'living', anchor=ctr('Sofa_seat1'))
COFFEE = bb('Coffee_top')
F(10, 'Холна маса', [('rect', COFFEE, 'solid')], 'living', anchor=ctr('Coffee_top'))
RUG_L = bb('Rug_living')
F(11, 'Килим дневна', [('rect', RUG_L, 'rug')], 'living', anchor=(RUG_L[2] - 0.22, RUG_L[1] + 0.20))
_lc = ctr('Lounge_seat')
_a1, _a2 = ctr('Lounge_arm+0.3'), ctr('Lounge_arm-0.3')
import math as _m
LOUNGE_ANG = _m.degrees(_m.atan2(_a1[1] - _a2[1], _a1[0] - _a2[0]))
LOUNGE_W = _m.dist(_a1, _a2) + 0.045   # arm-centre distance + arm width (IKEA EKENÄSET 65×74)
F(12, 'Кресло IKEA EKENÄSET', [('lounge', (_lc[0], _lc[1], LOUNGE_W, 0.74, LOUNGE_ANG))], 'living', anchor=_lc)
_fp = ctr('FloorLamp_pole'); _fs = bb('FloorLamp_shade'); _fbb = bb('FloorLamp_base')
F(13, 'Лампион', [('circ', (_fp[0], _fp[1], (_fbb[2] - _fbb[0]) / 2)),
                  ('circ_d', ((_fs[0] + _fs[2]) / 2, (_fs[1] + _fs[3]) / 2, (_fs[2] - _fs[0]) / 2))],
  'living', anchor=(_fp[0] + 0.22, _fp[1] - 0.25), leader=_fp)
BC = bb('BC_back', 'BC_sideL', 'BC_sideR', 'BC_frame')
F(14, 'Библиотека с арка по поръчка', [('rect', BC, 'solid'), ('rect', bb('BC_base'), 'thin', '')], 'living',
  anchor=ctr('BC_back', 'BC_frame'))
_ct = bb('Curtain_track'); _cr = bb('Curtain_R')
F(15, 'Воал на таванна релса', [('track', ((_ct[0], (_ct[1] + _ct[3]) / 2), (_ct[2], (_ct[1] + _ct[3]) / 2))),
                                 ('rect', _cr, 'thin', '')], 'living', anchor=(2.55, (_ct[1] + _ct[3]) / 2))
F(16, 'Климатик – вътрешно тяло (дневна, над вратата)', [('rect', bb('AC_indoor'), 'ac_in')], 'living',
  anchor=(ctr('AC_indoor')[0] - 0.22, ctr('AC_indoor')[1]), leader=ctr('AC_indoor'))
# ---- bedroom
BED = bb('Bed_platform', 'Bed_headboard')
MATT = bb('Mattress')
F(17, 'Легло с повдигащ се матрак и ракла', [('bed', BED, MATT)], 'bed', anchor=ctr('Bed_platform'))
TW0 = bb(prefix='BW_t0'); TW1 = bb(prefix='BW_t1'); BRIDGE = bb(prefix='BW_bridge')
F(18, 'Стена зад леглото: 2 дъбови колони, мост с 3 врати, табла-панел', [
    ('tower', TW0, bb('BW_t0_niche_back')), ('tower', TW1, bb('BW_t1_niche_back')),
    ('rect', BRIDGE, 'over'), ('rect', bb('Bed_wall_panel'), 'solid')], 'bed', anchor=ctr(prefix='BW_t0'))
WARD = bb('Wardrobe_carc', 'Wardrobe_track_bot', 'Wardrobe_filler')
F(19, 'Гардероб с плъзгащи врати + запълващ панел', [('wardrobe', WARD)], 'bed',
  anchor=(ctr('Wardrobe_carc')[0] - 0.35, ctr('Wardrobe_carc')[1]))
VAN = bb('Desk_top')
F(20, 'Тоалетка окачена с чекмедже + огледало Ø60', [('rect', VAN, 'solid'), ('rect', bb('Round_mirror_frame'), 'thin', '')],
  'bed', anchor=(ctr('Desk_top')[0], VAN[1] + 0.18))
_st = bb('Desk_stool_seat')
F(21, 'Табуретка (под тоалетката)', [('rect', _st, 'over')], 'bed', anchor=(_st[2] + 0.17, ctr('Desk_stool_seat')[1]),
  leader=ctr('Desk_stool_seat'))
RUG_B = bb('Rug_bedroom')
F(22, 'Килим спалня', [('rect', RUG_B, 'rug')], 'bed', anchor=(RUG_B[0] + 0.20, RUG_B[3] - 0.20))
_lb = bb('Laundry_basket')
F(23, 'Кош за пране', [('circ', ((_lb[0] + _lb[2]) / 2, (_lb[1] + _lb[3]) / 2, (_lb[2] - _lb[0]) / 2))], 'bed',
  anchor=ctr('Laundry_basket'))
_bct = bb('BedCurtain_track')
F(24, 'Щори blackout + воал', [('track', ((_bct[0], (_bct[1] + _bct[3]) / 2), (_bct[2], (_bct[1] + _bct[3]) / 2)))],
  'bed', anchor=(5.15, (_bct[1] + _bct[3]) / 2 - 0.02))
F(25, 'Климатик – вътрешно тяло (спалня, над вратата)', [('rect', bb('AC_bed_indoor'), 'ac_in')], 'bed',
  anchor=(ctr('AC_bed_indoor')[0] + 0.05, bb('AC_bed_indoor')[3] + 0.17), leader=ctr('AC_bed_indoor'))
# ---- hall
F(26, 'Шкаф за обувки IKEA STÄLL', [('rect', bb('Shoe_STALL_body'), 'solid')], 'corr', anchor=ctr('Shoe_STALL_body'))
F(27, 'Огледало (над шкафа за обувки)', [('rect', bb('Hall_mirror_frame'), 'thin', '')], 'corr',
  anchor=(3.84, ctr('Hall_mirror_frame')[1] + 0.05), leader=(3.50, ctr('Hall_mirror_frame')[1] + 0.05))
HALL = dict(side=bb('Hall_unit_side'), bench=bb('Hall_unit_bench_seat'), back=bb('Hall_unit_bench_back'),
            tall=bb('Hall_unit_tall'), d0=bb('Hall_unit_tall_door0'), d1=bb('Hall_unit_tall_door1'),
            upper=bb('Hall_unit_upper', 'Hall_unit_upper_door'))
F(28, 'Мебел за антре по поръчка', [('hallunit', HALL)], 'corr', anchor=ctr('Hall_unit_bench_seat'))
F(29, 'Изтривалка', [('rect', bb('Doormat'), 'rug')], 'corr', anchor=ctr('Doormat'))
# ---- bathroom
VANB = bb('Vanity_top', 'Vanity_top_back', 'Vanity_top_left', 'Vanity_top_right'); BASIN = bb('Vanity_bowl_bottom')
WASHER = bb('Washer_body'); PULLOUT = bb('Vanity_cab', 'Vanity_pullout_front')
F(30, 'Плот с интегриран умивалник + изтеглящ се шкаф за препарати', [('vanity', VANB, BASIN), ('rect', PULLOUT, 'thin', '')],
  'bath', anchor=(ctr('Vanity_bowl_bottom')[0], ctr('Vanity_bowl_bottom')[1] - 0.02))
F(31, 'Пералня-сушилня Electrolux EW7W368SI (под плота)', [('rect', WASHER, 'over')], 'bath',
  anchor=(5.12, 0.84), leader=(5.12, 1.08))
F(32, 'Огледален шкаф + LED', [('rect', bb('Mirror_cab'), 'over')], 'bath', anchor=(5.34, 1.95), leader=(5.34, 1.60))
SHOWER = dict(floor=bb('Shower_floor'), side=bb('Shower_glass_side'), fixed=bb('Shower_glass_fixed'),
              bf0=bb('Shower_bifold0'), bf1=bb('Shower_bifold1'), drain=bb('Shower_drain'), head=ctr('Shower_head'),
              mixer=ctr('Shower_mixer'))
F(33, 'Душ без праг: стъкла + сгъваема врата, линеен трап', [('shower', SHOWER)], 'bath', anchor=(6.16, 1.02))
F(34, 'Окачена тоалетна + вградено казанче', [('wc', bb('WC_bowl')), ('rect', bb('WC_boxing'), 'hatch')],
  'bath', anchor=(6.12, 0.40))
F(35, 'Сушилник за кърпи', [('rect', bb(prefix='Towel_rail_'), 'solid')], 'bath', anchor=(5.35, 0.22),
  leader=(5.35, 0.06))
F(36, 'Бойлер Ariston Velis Pro 50, хоризонтален, над WC', [('rect', bb('Boiler'), 'over')], 'bath',
  anchor=(6.44, 0.98), leader=(6.50, 0.80))
F(37, 'Кош за отпадъци + четка WC', [('rect', bb('Bath_bin'), 'thin', ''),
                                      ('circ', (ctr('Bath_brush')[0], ctr('Bath_brush')[1], 0.05))], 'bath',
  anchor=(5.70, 0.30), leader=ctr('Bath_bin'))
# ---- balcony
TCH = []
for _p in ('Tarno_chair0', 'Tarno_chair1'):
    _x0, _y0, _x1, _y1 = bb(prefix=_p)
    TCH.append(('chair', ((_x0 + _x1) / 2, (_y0 + _y1) / 2, _x1 - _x0, _y1 - _y0, 0)))
F(38, 'IKEA TÄRNÖ маса + 2 сгъваеми стола', [('rect', bb('Tarno_top'), 'solid')] + TCH, 'balc', anchor=ctr('Tarno_top'))
AC_OUT = bb('AC_outdoor')
F(39, 'Климатик – външно тяло multi-split, на конзоли', [('rect', AC_OUT, 'ac')], 'balc',
  anchor=(ctr('AC_outdoor')[0], AC_OUT[1] + 0.12))
_p1 = bb('potted_plant_02_pot'); _p2 = bb('potted_plant_04_pot.005')
F(40, 'Растения в саксии', [('plant', ((_p1[0] + _p1[2]) / 2, (_p1[1] + _p1[3]) / 2, (_p1[2] - _p1[0]) / 2)),
                            ('plant', ((_p2[0] + _p2[2]) / 2, (_p2[1] + _p2[3]) / 2, (_p2[2] - _p2[0]) / 2))], 'balc',
  anchor=((_p1[0] + _p1[2]) / 2 - 0.36, (_p1[1] + _p1[3]) / 2 + 0.05), leader=((_p1[0] + _p1[2]) / 2, (_p1[1] + _p1[3]) / 2))

KEYS = {it['key']: it for it in FURN}
