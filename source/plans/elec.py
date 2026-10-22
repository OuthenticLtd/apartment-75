# -*- coding: utf-8 -*-
"""Electrical symbols (page mm) and point list (model m)."""
import math
from matplotlib.patches import Circle, Wedge, Rectangle, Polygon, FancyBboxPatch

RED = '#C0392B'; BLUE = '#1F5FA8'; LED = '#E39B17'; GRN = '#2E7D32'; PUR = '#7B3FA0'


def _rot(cx, cy, ang):
    a = math.radians(ang); ca, sa = math.cos(a), math.sin(a)
    return lambda u, v: (cx + u * ca - v * sa, cy + u * sa + v * ca)


def socket(ax, px, py, ang, n=1, ip=False, color='k', r=1.25, z=30, earth=True):
    """ang = direction pointing INTO the room (stem towards the wall). n = 1/2/3."""
    T = _rot(px, py, ang)
    stem = 0.9
    offs = [0] if n == 1 else ([-r, r] if n == 2 else [-2 * r, 0, 2 * r])
    for o in offs:
        cx, cy = T(stem, o)
        w = Wedge((cx, cy), r, ang - 90, ang + 90, fc=(color if ip else 'white'), ec=color, lw=0.5, zorder=z)
        ax.add_patch(w)
        a, b = T(stem, o - r), T(stem, o + r)
        ax.plot([a[0], b[0]], [a[1], b[1]], color=color, lw=0.5, zorder=z + 0.1)
        if earth:
            a, b = T(stem + r + 0.35, o - r * 0.8), T(stem + r + 0.35, o + r * 0.8)
            ax.plot([a[0], b[0]], [a[1], b[1]], color=color, lw=0.5, zorder=z + 0.1)
    a, b = T(0, 0), T(stem, 0)
    ax.plot([a[0], b[0]], [a[1], b[1]], color=color, lw=0.5, zorder=z)


def outlet_box(ax, px, py, ang, txt='', color='k', s=2.6, z=30):
    """Fixed connection / dedicated outlet: square with diagonal, offset into the room."""
    T = _rot(px, py, ang)
    pts = [T(0.3, -s / 2), T(0.3 + s, -s / 2), T(0.3 + s, s / 2), T(0.3, s / 2)]
    ax.add_patch(Polygon(pts, closed=True, fc='white', ec=color, lw=0.55, zorder=z))
    ax.plot([pts[0][0], pts[2][0]], [pts[0][1], pts[2][1]], color=color, lw=0.45, zorder=z + 0.1)
    if txt:
        c = T(0.3 + s / 2, 0)
        ax.text(c[0], c[1], txt, fontsize=3.6, ha='center', va='center', zorder=z + 0.2, color=color, weight='bold',
                bbox=dict(boxstyle='square,pad=0.05', fc='white', ec='none'))


def switch(ax, px, py, ang, kind='1', color='k', z=30):
    """kind: '1' single, '2' two-gang, 'w' two-way, 'x' intermediate, 'w2' two-way+single."""
    r = 0.9
    T = _rot(px, py, ang)
    c = T(1.6, 0)
    ax.add_patch(Circle(c, r, fc='white', ec=color, lw=0.55, zorder=z))
    ax.plot([px, c[0]], [py, c[1]], color=color, lw=0.4, zorder=z - 0.1)
    L = 3.0; tk = 0.9

    def arm(a_rel, both=False, ticks=1):
        a = math.radians(ang + a_rel)
        ux, uy = math.cos(a), math.sin(a)
        s0 = (-L if both else 0)
        p0 = (c[0] + ux * (r if not both else -L), c[1] + uy * (r if not both else -L))
        p1 = (c[0] + ux * L, c[1] + uy * L)
        if not both:
            p0 = (c[0] + ux * r, c[1] + uy * r)
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=color, lw=0.5, zorder=z)
        ends = [p1] + ([p0] if both else [])
        for k, e in enumerate(ends):
            sgn = 1 if k == 0 else -1
            for t in range(ticks):
                bx, by = e[0] - ux * sgn * t * 0.7, e[1] - uy * sgn * t * 0.7
                ax.plot([bx, bx + (-uy) * tk * sgn], [by, by + ux * tk * sgn], color=color, lw=0.5, zorder=z)

    if kind == '1':
        arm(45)
    elif kind == '2':
        arm(45, ticks=2)
    elif kind == 'w':
        arm(45, both=True)
    elif kind == 'x':
        arm(45, both=True); arm(-45, both=True)
    elif kind == 'w2':
        arm(45, both=True); arm(-45, ticks=1)


def light(ax, px, py, kind='ceil', color='k', z=30, ang=0, stem=1.9):
    if kind == 'ceil':      # ceiling lighting outlet / pendant
        r = 2.0
        ax.add_patch(Circle((px, py), r, fc='white', ec=color, lw=0.6, zorder=z))
        d = r * 0.707
        ax.plot([px - d, px + d], [py - d, py + d], color=color, lw=0.6, zorder=z)
        ax.plot([px - d, px + d], [py + d, py - d], color=color, lw=0.6, zorder=z)
    elif kind == 'down':    # recessed downlight
        r = 1.3
        ax.add_patch(Circle((px, py), r, fc='white', ec=color, lw=0.6, zorder=z))
        ax.add_patch(Circle((px, py), 0.55, fc=color, ec=color, lw=0.3, zorder=z + 0.1))
    elif kind == 'downip':
        r = 1.3
        ax.add_patch(Circle((px, py), r, fc='white', ec=color, lw=0.6, zorder=z))
        ax.add_patch(Circle((px, py), 0.55, fc=color, ec=color, lw=0.3, zorder=z + 0.1))
        ax.add_patch(Circle((px, py), r + 0.45, fc='none', ec=color, lw=0.4, zorder=z))
    elif kind == 'wall':    # wall light: cross in circle + stem to the wall
        T = _rot(px, py, ang)
        c = T(stem, 0)
        ax.plot([px, T(stem - 1.3, 0)[0]], [py, T(stem - 1.3, 0)[1]], color=color, lw=0.5, zorder=z)
        r = 1.3
        ax.add_patch(Circle(c, r, fc='white', ec=color, lw=0.6, zorder=z))
        d = r * 0.707
        ax.plot([c[0] - d, c[0] + d], [c[1] - d, c[1] + d], color=color, lw=0.5, zorder=z)
        ax.plot([c[0] - d, c[0] + d], [c[1] + d, c[1] - d], color=color, lw=0.5, zorder=z)
        a, b = T(0.6, -1.3), T(0.6, 1.3)
        ax.plot([a[0], b[0]], [a[1], b[1]], color=color, lw=0.7, zorder=z)
    elif kind == 'pic':     # picture light (linear wall luminaire)
        T = _rot(px, py, ang)
        pts = [T(0.3, -2.4), T(1.5, -2.4), T(1.5, 2.4), T(0.3, 2.4)]
        ax.add_patch(Polygon(pts, closed=True, fc='white', ec=color, lw=0.6, zorder=z))
        a, b = T(0.3, -2.4), T(1.5, 2.4); ax.plot([a[0], b[0]], [a[1], b[1]], color=color, lw=0.4, zorder=z)
        a, b = T(0.3, 2.4), T(1.5, -2.4); ax.plot([a[0], b[0]], [a[1], b[1]], color=color, lw=0.4, zorder=z)


def box(ax, px, py, txt, w=4.0, h=2.6, color='k', fc='white', z=30, fs=3.8, tc=None):
    ax.add_patch(Rectangle((px - w / 2, py - h / 2), w, h, fc=fc, ec=color, lw=0.55, zorder=z))
    ax.text(px, py, txt, fontsize=fs, ha='center', va='center', zorder=z + 0.1, color=tc or color, weight='bold')


def board(ax, px, py, ang, z=30):
    T = _rot(px, py, ang)
    pts = [T(0, -3.0), T(2.4, -3.0), T(2.4, 3.0), T(0, 3.0)]
    ax.add_patch(Polygon(pts, closed=True, fc='white', ec='k', lw=0.7, zorder=z))
    tri = [T(0, -3.0), T(2.4, 3.0), T(0, 3.0)]
    ax.add_patch(Polygon(tri, closed=True, fc='k', ec='k', lw=0.3, zorder=z + 0.1))


def data_out(ax, px, py, ang, txt='TP', color=BLUE, z=30):
    T = _rot(px, py, ang)
    pts = [T(0.3, -1.3), T(2.6, -1.3), T(2.6, 1.3), T(0.3, 1.3)]
    ax.add_patch(Polygon(pts, closed=True, fc='white', ec=color, lw=0.55, zorder=z))
    a, b = T(0.3, 0), T(0, 0)
    c = T(1.45, 0)
    ax.text(c[0], c[1], txt, fontsize=3.3, ha='center', va='center', color=color, zorder=z + 0.1, weight='bold')


def driver(ax, px, py, z=30):
    ax.add_patch(Rectangle((px - 1.6, py - 1.0), 3.2, 2.0, fc='#FFF4DC', ec=LED, lw=0.6, zorder=z))
    ax.text(px, py, 'Д', fontsize=3.8, ha='center', va='center', color='#8A5A00', zorder=z + 0.1, weight='bold')


def fan(ax, px, py, z=30):
    ax.add_patch(Circle((px, py), 1.8, fc='white', ec='k', lw=0.6, zorder=z))
    for a in (0, 120, 240):
        ax.add_patch(Wedge((px, py), 1.5, a, a + 40, fc='k', ec='none', zorder=z + 0.1))
