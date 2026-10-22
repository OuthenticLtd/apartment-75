# -*- coding: utf-8 -*-
"""Shared drawing helpers: A3 sheet in page millimetres, title block, walls, openings,
dimensions, furniture outlines."""
import math, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Circle, Ellipse, Arc, PathPatch, FancyBboxPatch
from matplotlib.path import Path
from shapely.geometry import box as sbox
import geom as G

plt.rcParams.update({'pdf.fonttype': 42, 'ps.fonttype': 42, 'font.family': 'DejaVu Sans',
                     'hatch.linewidth': 0.35, 'lines.solid_capstyle': 'butt'})

OUT = r'C:\Users\vasil\OneDrive - Outhentic Foundation\DOCUMENTS\Apartments\Mladost 4\Apartment 75 - 3D design\Plans'
HERE = os.path.dirname(os.path.abspath(__file__))
PREV = os.path.join(HERE, 'prev')
os.makedirs(OUT, exist_ok=True); os.makedirs(PREV, exist_ok=True)
DATE = '22.10.2026'
PW, PH = 420.0, 297.0
MM = 72 / 25.4          # points per mm
PT2MM = 25.4 / 72

def fmt(v, nd=2):
    s = f'{v:.{nd}f}'
    return s.replace('.', ',')

def cm(v):
    c = round(v * 100, 1)
    return str(int(round(c))) if abs(c - round(c)) < 0.05 else fmt(c, 1)


class Sheet:
    def __init__(self, num, name, scale='1:50', ox=52.0, oy=80.0, S=20.0):
        self.num, self.name, self.scale = num, name, scale
        self.fig = plt.figure(figsize=(PW / 25.4, PH / 25.4))
        ax = self.fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, PW); ax.set_ylim(0, PH); ax.set_aspect('equal'); ax.axis('off')
        self.ax = ax
        self.ox, self.oy, self.S = ox, oy, S
        self.frame()

    # model -> page
    def P(self, x, y):
        return (self.ox + x * self.S, self.oy + y * self.S)

    def L(self, d):  # model length -> page mm
        return d * self.S

    # ------------------------------------------------------------ frame / title block
    def frame(self):
        ax = self.ax
        ax.add_patch(Rectangle((20, 10), PW - 30, PH - 20, fill=False, lw=0.9, ec='k'))
        ax.add_patch(Rectangle((5, 5), PW - 10, PH - 10, fill=False, lw=0.2, ec='0.6'))

    def title_block(self, x0=PW - 10 - 185, y0=10.0, w=185.0, h=38.0, extra=None):
        ax = self.ax
        ax.add_patch(Rectangle((x0, y0), w, h, fill=True, fc='white', lw=0.8, ec='k', zorder=20))
        # rows
        def hl(y, xa=x0, xb=x0 + w, lw=0.4):
            ax.plot([xa, xb], [y, y], 'k', lw=lw, zorder=21)
        def vl(x, ya, yb, lw=0.4):
            ax.plot([x, x], [ya, yb], 'k', lw=lw, zorder=21)
        T = lambda x, y, s, **k: ax.text(x, y, s, zorder=22, **k)
        hl(y0 + 26); hl(y0 + 14)
        T(x0 + 2.5, y0 + h - 4.2, 'АПАРТАМЕНТ 75, ж.к. МЛАДОСТ 4, гр. СОФИЯ', fontsize=6.2, color='0.25', va='center')
        T(x0 + 2.5, y0 + h - 8.6, f'Апартамент 75, Младост 4 – {self.name}', fontsize=10.5,
          weight='bold', va='center')
        T(x0 + 2.5, y0 + 20, 'Интериорен проект – работни чертежи', fontsize=6.3, va='center')
        T(x0 + 2.5, y0 + 16.3, 'Част: интериор / ориентировъчни схеми за ЕЛ и ВиК', fontsize=5.2,
          va='center', color='0.3')
        vl(x0 + 112, y0 + 14, y0 + 26)
        T(x0 + 114, y0 + 22.5, 'Възложител:', fontsize=5.2, color='0.3', va='center')
        T(x0 + 114, y0 + 17.5, 'Проектант:', fontsize=5.2, color='0.3', va='center')
        ax.plot([x0 + 133, x0 + w - 3], [y0 + 21, y0 + 21], color='0.6', lw=0.3, zorder=21)
        ax.plot([x0 + 133, x0 + w - 3], [y0 + 16, y0 + 16], color='0.6', lw=0.3, zorder=21)
        # bottom row cells
        cells = [('Мащаб', self.scale, 36), ('Дата', DATE, 32), ('Фаза', 'РП', 22),
                 ('Ревизия', '0', 22), ('Размери', 'cm (кота в m)', 40), ('Лист', self.num, 33)]
        x = x0
        for i, (lab, val, cw) in enumerate(cells):
            if i: vl(x, y0, y0 + 14)
            T(x + 1.8, y0 + 11, lab, fontsize=4.8, color='0.35', va='center')
            big = lab == 'Лист'
            T(x + cw / 2, y0 + 5, val, fontsize=11 if big else 7.2, weight='bold' if big else 'normal',
              ha='center', va='center')
            x += cw

    # ------------------------------------------------------------ primitives
    def line(self, pts, lw=0.3, color='k', ls='-', z=5, **k):
        xs, ys = zip(*[self.P(*p) for p in pts])
        self.ax.plot(xs, ys, lw=lw, color=color, ls=ls, zorder=z, solid_capstyle='butt', **k)

    def rect(self, x0, y0, x1, y1, lw=0.3, ec='k', fc='none', ls='-', z=5, hatch=None, alpha=1):
        (a, b) = self.P(x0, y0)
        p = Rectangle((a, b), self.L(x1 - x0), self.L(y1 - y0), lw=lw, ec=ec, fc=fc, ls=ls,
                      zorder=z, hatch=hatch, alpha=alpha)
        self.ax.add_patch(p); return p

    def poly(self, pts, lw=0.3, ec='k', fc='none', ls='-', z=5, hatch=None, closed=True):
        p = Polygon([self.P(*q) for q in pts], closed=closed, lw=lw, ec=ec, fc=fc, ls=ls, zorder=z,
                    hatch=hatch)
        self.ax.add_patch(p); return p

    def circle(self, cx, cy, r, lw=0.3, ec='k', fc='none', ls='-', z=5):
        p = Circle(self.P(cx, cy), self.L(r), lw=lw, ec=ec, fc=fc, ls=ls, zorder=z)
        self.ax.add_patch(p); return p

    def text(self, x, y, s, fs=6, ha='center', va='center', z=12, page=False, **k):
        if not page:
            x, y = self.P(x, y)
        return self.ax.text(x, y, s, fontsize=fs, ha=ha, va=va, zorder=z, **k)

    def shp(self, geom_, fc='none', ec='k', lw=0.5, hatch=None, z=6):
        polys = [geom_] if geom_.geom_type == 'Polygon' else list(geom_.geoms)
        for pg in polys:
            verts, codes = [], []
            for ring in [pg.exterior] + list(pg.interiors):
                cs = [self.P(*c) for c in ring.coords]
                verts += cs; codes += [Path.MOVETO] + [Path.LINETO] * (len(cs) - 2) + [Path.CLOSEPOLY]
            self.ax.add_patch(PathPatch(Path(verts, codes), fc=fc, ec=ec, lw=lw, hatch=hatch, zorder=z))

    # ------------------------------------------------------------ architecture
    def walls(self, style='hatch', z=6):
        ext, part = G.wall_polys()
        if style == 'hatch':
            self.shp(ext, fc='white', ec='k', lw=0.0, hatch='//////', z=z)
            self.shp(ext, fc='none', ec='k', lw=0.7, z=z + 0.1)
            self.shp(part, fc='0.72', ec='k', lw=0.55, z=z)
        else:  # solid poche for MEP / furniture sheets
            self.shp(ext, fc='0.25', ec='k', lw=0.5, z=z)
            self.shp(part, fc='0.55', ec='k', lw=0.45, z=z)

    def openings(self, swing=True, labels=False, lw=0.3, color='k'):
        S = self
        def gapframe(x0, y0, x1, y1, f0, f1, ori):
            if ori == 'h':
                S.rect(x0, f0, x1, f1, lw=0.35, ec=color, fc='white', z=7)
                S.line([(x0, (f0 + f1) / 2), (x1, (f0 + f1) / 2)], lw=0.25, color=color, z=7.1)
                S.line([(x0, y0), (x1, y0)], lw=0.2, color=color, z=7)
                S.line([(x0, y1), (x1, y1)], lw=0.2, color=color, z=7)
            else:
                S.rect(f0, y0, f1, y1, lw=0.35, ec=color, fc='white', z=7)
                S.line([((f0 + f1) / 2, y0), ((f0 + f1) / 2, y1)], lw=0.25, color=color, z=7.1)
                S.line([(x0, y0), (x0, y1)], lw=0.2, color=color, z=7)
                S.line([(x1, y0), (x1, y1)], lw=0.2, color=color, z=7)
        for w in G.WINDOWS:
            x0, y0, x1, y1 = w['gap']; f0, f1 = w['frame']
            gapframe(x0, y0, x1, y1, f0, f1, 'h')
            for m in w.get('mulls', []):
                S.rect(m - 0.03, f0, m + 0.03, f1, lw=0.3, ec=color, fc='white', z=7.2)
            if swing and 'leaf' in w:
                lf = w['leaf']; hx, hy = lf['hinge']
                S.line([(hx, hy), (hx, hy - lf['r'])], lw=0.35, color=color, z=7)
                self.arc(hx, hy, lf['r'], 270, 360, ls=(0, (2, 1.2)), color=color)
        for g in G.GLZ_DOOR_GAPS:
            x0, y0, x1, y1 = g['gap']; f0, f1 = g['frame']
            gapframe(x0, y0, x1, y1, f0, f1, g['ori'])
        doors = list(G.DOORS) + list(G.BAL_DOORS)
        for d in doors:
            hx, hy = d['hinge']; r = d['r']
            a0, a1 = d['a_closed'], d['a_open']
            if swing:
                ex, ey = hx + r * math.cos(math.radians(a1)), hy + r * math.sin(math.radians(a1))
                S.line([(hx, hy), (ex, ey)], lw=0.55, color=color, z=7.5)
                lo, hi = sorted([a0, a1])
                if hi - lo > 180: lo, hi = hi, lo + 360
                self.arc(hx, hy, r, lo, hi, ls=(0, (2, 1.2)), color=color)
        # pocket door (bathroom): opening + leaf in the pocket (dashed)
        P = G.POCKET
        x0, y0, x1, y1 = P['gap']; lf = P['leaf']
        S.line([(x0, y0), (x1, y0)], lw=0.2, color=color, z=7)
        S.line([(x0, y1), (x1, y1)], lw=0.2, color=color, z=7)
        xm = (x0 + x1) / 2
        S.rect(xm - 0.02, y1, xm + 0.02, lf[3], lw=0.3, ec=color, fc='white', ls=(0, (2, 1)), z=7.6)
        S.line([(xm, y0 + 0.02), (xm, y1)], lw=0.25, ls=(0, (2, 1.2)), color=color, z=7.5)
        if swing:
            self.ax.annotate('', xy=self.P(xm + 0.09, y1 + 0.30), xytext=self.P(xm + 0.09, y1 - 0.05),
                             arrowprops=dict(arrowstyle='->', lw=0.35, color=color), zorder=7.6)
        x0, y0, x1, y1 = G.RAIL
        S.rect(x0, y0, x1, y1, lw=0.3, ec=color, fc='white', z=7)
        S.line([(x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2)], lw=0.2, color=color, z=7)
        sx0, sy0, sx1, sy1 = G.BAL_SLAB
        S.line([(x0, y1), (x0, sy1), (sx1, sy1)], lw=0.25, color=color, z=6)

    def arc(self, cx, cy, r, a0, a1, lw=0.25, ls='-', color='k', z=7):
        self.ax.add_patch(Arc(self.P(cx, cy), 2 * self.L(r), 2 * self.L(r), theta1=a0, theta2=a1,
                              lw=lw, ls=ls, color=color, zorder=z))

    # ------------------------------------------------------------ dimensions
    def dim_chain(self, vals, axis, at, ref=None, fs=5.3, color='k', lw=0.3, tick=0.9, side=1,
                  labels=None, ext_gap=0.6, stag=True, z=9, small_out=True):
        """vals: model coords along axis ('x' or 'y'); at: model coordinate of the dimension line;
        ref: model coordinate where extension lines start (None => short ticks only).
        side: +1 text on +side of line (above / left for vertical)."""
        ax = self.ax
        pts = []
        for v in vals:
            pts.append(self.P(v, at) if axis == 'x' else self.P(at, v))
        if axis == 'x':
            ax.plot([pts[0][0], pts[-1][0]], [pts[0][1]] * 2, color=color, lw=lw, zorder=z)
        else:
            ax.plot([pts[0][0]] * 2, [pts[0][1], pts[-1][1]], color=color, lw=lw, zorder=z)
        for i, (v, p) in enumerate(zip(vals, pts)):
            # tick
            ax.plot([p[0] - tick, p[0] + tick], [p[1] - tick, p[1] + tick], color=color, lw=0.7, zorder=z)
            if ref is not None:
                if axis == 'x':
                    r = self.P(v, ref)[1]
                    sgn = 1 if p[1] > r else -1
                    ax.plot([p[0], p[0]], [r + sgn * ext_gap, p[1] + sgn * 1.2], color=color, lw=0.18, zorder=z)
                else:
                    r = self.P(ref, v)[0]
                    sgn = 1 if p[0] > r else -1
                    ax.plot([r + sgn * ext_gap, p[0] + sgn * 1.2], [p[1], p[1]], color=color, lw=0.18, zorder=z)
        # texts
        last_hi = -1e9
        for i in range(len(vals) - 1):
            a, b = vals[i], vals[i + 1]
            s = labels[i] if labels else cm(abs(b - a))
            if s is None: continue
            seg = abs(self.L(b - a))
            tw = len(s) * fs * 0.6 * PT2MM + 0.6
            mid = (a + b) / 2
            off = 1.1 + fs * PT2MM * 0.5
            if axis == 'x':
                x, y = self.P(mid, at)
                if seg < tw and small_out:
                    # push outward: alternate level
                    y2 = y + side * (off + fs * PT2MM * 1.15)
                    ax.text(x, y2, s, fontsize=fs, ha='center', va='center', color=color, zorder=z)
                    ax.plot([x, x], [y + side * 0.4, y2 - side * fs * PT2MM * 0.55], color=color, lw=0.15, zorder=z)
                else:
                    ax.text(x, y + side * off, s, fontsize=fs, ha='center', va='center', color=color, zorder=z)
            else:
                x, y = self.P(at, mid)
                if seg < tw and small_out:
                    x2 = x - side * (off + fs * PT2MM * 1.15)
                    ax.text(x2, y, s, fontsize=fs, ha='center', va='center', color=color, rotation=90, zorder=z)
                    ax.plot([x - side * 0.4, x2 + side * fs * PT2MM * 0.55], [y, y], color=color, lw=0.15, zorder=z)
                else:
                    ax.text(x - side * off, y, s, fontsize=fs, ha='center', va='center', color=color,
                            rotation=90, zorder=z)

    def dim_free(self, p1, p2, s=None, fs=5.0, color='0.1', off=0.0, z=11, tick=0.8, bg=True, rot=None,
                 tside=1):
        """Dimension between two model points (horizontal or vertical) drawn directly (no extension)."""
        (x1, y1), (x2, y2) = self.P(*p1), self.P(*p2)
        ax = self.ax
        ax.plot([x1, x2], [y1, y2], color=color, lw=0.3, zorder=z)
        for (x, y) in ((x1, y1), (x2, y2)):
            ax.plot([x - tick, x + tick], [y - tick, y + tick], color=color, lw=0.6, zorder=z)
        if s is None:
            s = cm(math.hypot(p2[0] - p1[0], p2[1] - p1[1]))
        vert = abs(x2 - x1) < abs(y2 - y1)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        d = 1.0 + fs * PT2MM * 0.5
        if vert:
            mx -= tside * d
        else:
            my += tside * d
        kw = dict(boxstyle='square,pad=0.08', fc='white', ec='none') if bg else None
        ax.text(mx, my, s, fontsize=fs, ha='center', va='center', color=color, zorder=z + 0.5,
                rotation=(90 if vert else 0) if rot is None else rot, bbox=kw)

    # ------------------------------------------------------------ furniture
    def furniture(self, mode='full', keys=True, color='k', lwf=0.35, skip=()):
        """mode 'full' (furniture plan) or 'faint' (background on MEP sheets)."""
        faint = mode == 'faint'
        c = '0.62' if faint else color
        lw = 0.22 if faint else lwf
        for it in G.FURN:
            if it['key'] in skip: continue
            for sh in it['shapes']:
                self._shape(sh, c, lw, faint)
            if keys and not faint:
                ax, ay = it['anchor']
                if 'leader' in it:
                    self.line([it['anchor'], it['leader']], lw=0.2, color='k', z=13)
                self.key(ax, ay, it['key'])

    def key(self, x, y, n, r=2.0, fs=5.6):
        px, py = self.P(x, y)
        self.ax.add_patch(Circle((px, py), r, fc='white', ec='k', lw=0.45, zorder=14))
        self.ax.text(px, py, str(n), fontsize=fs, ha='center', va='center', zorder=15, weight='bold')

    def _rrect(self, cx, cy, w, h, ang):
        a = math.radians(ang); ca, sa = math.cos(a), math.sin(a)
        def T(u, v): return (cx + u * ca - v * sa, cy + u * sa + v * ca)
        return T

    def _shape(self, sh, c, lw, faint):
        k = sh[0]
        fillw = 'white' if not faint else 'none'
        if k == 'rect' or k == 'poly':
            style = sh[2] if len(sh) > 2 else 'solid'
            pts = sh[1] if k == 'poly' else None
            ls = '-'; l = lw; ec = c; fc = fillw; hatch = None; z = 8
            if style == 'over': ls = (0, (3, 1.5)); fc = 'none'; l = lw * 0.8; z = 9
            if style == 'thin': l = lw * 0.6; fc = 'none'
            if style == 'rug': ls = (0, (6, 1.5, 1, 1.5)); fc = 'none'; l = lw * 0.7; z = 7.5
            if style == 'hatch': hatch = '////' if not faint else None; fc = 'none'
            if style == 'ac': fc = 'none'; ls = (0, (3, 1.5)); z = 9
            if style == 'ac_in': fc = 'none'; ls = (0, (3, 1.5)); z = 9; l = lw * 1.1
            if k == 'poly':
                self.poly(pts, lw=l, ec=ec, fc=fc, ls=ls, z=z)
            else:
                x0, y0, x1, y1 = sh[1]
                self.rect(x0, y0, x1, y1, lw=l, ec=ec, fc=fc, ls=ls, z=z, hatch=hatch)
                if style == 'ac':
                    r_ = min(x1 - x0, y1 - y0) * 0.36
                    self.circle((x0 + x1) / 2, y0 + (y1 - y0) * 0.38, r_, lw=l * 0.7, ec=c, ls=(0, (2, 1.2)), z=z)
                if style == 'ac_in':
                    self.line([(x0, y0), (x1, y1)], lw=l * 0.5, color=c, ls=(0, (2, 1.2)), z=z)
                    self.line([(x0, y1), (x1, y0)], lw=l * 0.5, color=c, ls=(0, (2, 1.2)), z=z)
                if style == 'thin' and len(sh) > 3 and sh[3]:
                    self.text((x0 + x1) / 2, (y0 + y1) / 2, sh[3], fs=4.6, color=c)
        elif k == 'tall':
            x0, y0, x1, y1 = sh[1]
            self.rect(x0, y0, x1, y1, lw=lw, ec=c, fc=fillw, z=8)
            self.line([(x0, y0), (x1, y1)], lw=lw * 0.6, color=c, z=8.1)
            self.line([(x0, y1), (x1, y0)], lw=lw * 0.6, color=c, z=8.1)
        elif k == 'sink':
            x0, y0, x1, y1 = sh[1]
            (a, b) = self.P(x0, y0)
            self.ax.add_patch(FancyBboxPatch((a, b), self.L(x1 - x0), self.L(y1 - y0),
                                             boxstyle='round,pad=0,rounding_size=0.8', lw=lw, ec=c, fc='none', zorder=8.2))
            self.circle((x0 + x1) / 2, (y0 + y1) / 2, 0.03, lw=lw * 0.7, ec=c, z=8.2)
            self.circle((x0 + x1) / 2, y0 - 0.06, 0.02, lw=lw * 0.7, ec=c, z=8.2)
        elif k == 'hob':
            x0, y0, x1, y1 = sh[1]
            self.rect(x0, y0, x1, y1, lw=lw * 0.8, ec=c, z=8.2)
            w, h = x1 - x0, y1 - y0
            for (u, v, r) in ((0.30, 0.27, 0.08), (0.30, 0.73, 0.10), (0.72, 0.27, 0.10), (0.72, 0.73, 0.08)):
                self.circle(x0 + u * w, y0 + v * h, r, lw=lw * 0.6, ec=c, z=8.2)
        elif k == 'circ':
            cx, cy, r = sh[1]
            self.circle(cx, cy, r, lw=lw, ec=c, fc=fillw, z=8)
        elif k == 'circ_d':
            cx, cy, r = sh[1]
            self.circle(cx, cy, r, lw=lw * 0.7, ec=c, ls=(0, (2, 1.2)), z=8)
        elif k == 'ell':
            cx, cy, w, h = sh[1]
            self.ax.add_patch(Ellipse(self.P(cx, cy), self.L(w), self.L(h), lw=lw, ec=c, fc=fillw, zorder=8))
        elif k == 'chair':
            cx, cy, w, h, ang = sh[1]
            T = self._rrect(cx, cy, w, h, ang)
            pts = [T(-w / 2, -h / 2), T(w / 2, -h / 2), T(w / 2, h / 2), T(-w / 2, h / 2)]
            self.poly(pts, lw=lw, ec=c, fc=fillw, z=8.5)
            self.poly([T(-w / 2, -h / 2), T(w / 2, -h / 2), T(w / 2, -h / 2 + 0.06), T(-w / 2, -h / 2 + 0.06)],
                      lw=lw * 0.8, ec=c, fc='none', z=8.6)
        elif k == 'lounge':
            cx, cy, w, h, ang = sh[1]
            T = self._rrect(cx, cy, w, h, ang)
            self.poly([T(-w / 2, -h / 2), T(w / 2, -h / 2), T(w / 2, h / 2), T(-w / 2, h / 2)], lw=lw, ec=c, fc=fillw, z=8.5)
            self.poly([T(-w / 2, h / 2 - 0.16), T(w / 2, h / 2 - 0.16), T(w / 2, h / 2), T(-w / 2, h / 2)],
                      lw=lw * 0.8, ec=c, z=8.6)
            for s in (-1, 1):
                self.poly([T(s * w / 2, -h / 2), T(s * (w / 2 - 0.1), -h / 2), T(s * (w / 2 - 0.1), h / 2 - 0.16),
                           T(s * w / 2, h / 2 - 0.16)], lw=lw * 0.6, ec=c, z=8.6)
        elif k == 'sofa':      # bbox, n seats, back depth, arm width (back on the -x side)
            x0, y0, x1, y1 = sh[1]
            n = sh[2]; bd = sh[3]; aw = sh[4]
            self.rect(x0, y0, x1, y1, lw=lw, ec=c, fc=fillw, z=8)
            self.rect(x0, y0 + aw, x0 + bd, y1 - aw, lw=lw * 0.7, ec=c, z=8.1)
            self.rect(x0, y0, x1, y0 + aw, lw=lw * 0.7, ec=c, z=8.1)
            self.rect(x0, y1 - aw, x1, y1, lw=lw * 0.7, ec=c, z=8.1)
            L = (y1 - y0 - 2 * aw) / n
            for i in range(1, n):
                self.line([(x0 + bd, y0 + aw + i * L), (x1, y0 + aw + i * L)], lw=lw * 0.6, color=c, z=8.1)
        elif k == 'taskchair':  # seat bbox + back bbox, 5-star base
            x0, y0, x1, y1 = sh[1]
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            for i in range(5):
                a = math.radians(90 + i * 72)
                self.line([(cx, cy), (cx + 0.30 * math.cos(a), cy + 0.30 * math.sin(a))], lw=lw * 0.5, color=c, z=8.4)
            (a_, b_) = self.P(x0, y0)
            self.ax.add_patch(FancyBboxPatch((a_, b_), self.L(x1 - x0), self.L(y1 - y0),
                              boxstyle='round,pad=0,rounding_size=1.2', lw=lw, ec=c, fc=fillw, zorder=8.5))
            bx0, by0, bx1, by1 = sh[2]
            self.rect(bx0, by0, bx1, by1, lw=lw, ec=c, fc=fillw, z=8.6)
        elif k == 'bed':
            x0, y0, x1, y1 = sh[1]
            mx0, my0, mx1, my1 = sh[2] if len(sh) > 2 else (x0 + 0.04, y0 + 0.02, x1 - 0.06, y1 - 0.02)
            self.rect(x0, y0, x1, y1, lw=lw, ec=c, fc=fillw, z=8)
            self.rect(mx1, y0, x1, y1, lw=lw * 0.8, ec=c, z=8.1)          # headboard
            self.rect(mx0, my0, mx1, my1, lw=lw * 0.5, ec=c, z=8.1)       # mattress
            for (a_, b_) in ((y0 + 0.10, (y0 + y1) / 2 - 0.04), ((y0 + y1) / 2 + 0.04, y1 - 0.10)):
                (px, py) = self.P(mx1 - 0.42, a_)
                self.ax.add_patch(FancyBboxPatch((px, py), self.L(0.32), self.L(b_ - a_),
                                                 boxstyle='round,pad=0,rounding_size=1.2', lw=lw * 0.6, ec=c, fc='none', zorder=8.2))
            self.line([(mx1 - 0.56, my0), (mx1 - 0.56, my1)], lw=lw * 0.5, color=c, z=8.1)
        elif k == 'wardrobe':
            x0, y0, x1, y1 = sh[1]
            cb = G.bb('Wardrobe_carc')[3]
            self.rect(x0, y0, x1, cb, lw=lw, ec=c, fc=fillw, z=8)
            db, df = G.bb('Wardrobe_slide_back'), G.bb('Wardrobe_slide_front')
            self.line([(db[0], (db[1] + db[3]) / 2), (db[2], (db[1] + db[3]) / 2)], lw=lw * 1.4, color=c, z=8.2)
            self.line([(df[0], (df[1] + df[3]) / 2), (df[2], (df[1] + df[3]) / 2)], lw=lw * 1.4, color=c, z=8.2)
            fl = G.bb('Wardrobe_filler')
            self.rect(*fl, lw=lw * 0.8, ec=c, fc=fillw, z=8.2)
            dv = G.bb('Wint_divider')
            self.line([((dv[0] + dv[2]) / 2, y0), ((dv[0] + dv[2]) / 2, cb)], lw=lw * 0.6, color=c, z=8.1)
            ym = (y0 + cb) / 2
            for (u0, u1) in ((x0 + 0.04, dv[0] - 0.04), (dv[2] + 0.04, x1 - 0.04)):
                self.line([(u0, ym), (u1, ym)], lw=lw * 0.5, ls=(0, (4, 1.5)), color=c, z=8.2)
        elif k == 'tower':      # oak tower: bbox, niche back bbox (niche cut at h 0.555–1.40)
            x0, y0, x1, y1 = sh[1]
            self.rect(x0, y0, x1, y1, lw=lw, ec=c, fc=fillw, z=8)
            nb = sh[2]
            self.rect(x0, y0 + 0.02, nb[0], y1 - 0.02, lw=lw * 0.5, ec=c, ls=(0, (2, 1.2)), z=8.1)
            self.line([(nb[0], y0), (nb[0], y1)], lw=lw * 0.7, color=c, z=8.1)
        elif k == 'hallunit':
            H = sh[1]
            self.rect(*H['side'], lw=lw, ec=c, fc=fillw, z=8)
            bx0, by0, bx1, by1 = H['bench']
            self.rect(bx0, by0, H['back'][2], by1, lw=lw, ec=c, fc=fillw, z=8)       # bench seat
            self.rect(*H['back'], lw=lw * 0.7, ec=c, z=8.1)                           # back panel / hooks
            self.rect(*H['upper'], lw=lw * 0.8, ec=c, ls=(0, (3, 1.5)), z=9)
            tx0, ty0, tx1, ty1 = H['tall']
            self.rect(H['d0'][0], ty0, tx1, ty1, lw=lw, ec=c, fc=fillw, z=8)
            self.line([(H['d0'][0], ty0), (tx1, ty1)], lw=lw * 0.35, color=c, z=8.1)
            self.line([(H['d0'][0], ty1), (tx1, ty0)], lw=lw * 0.35, color=c, z=8.1)
            if not faint:
                xf = H['d0'][0]
                for (dd, hy, a0, a1) in ((H['d0'], H['d0'][1], 90, 180), (H['d1'], H['d1'][3], 180, 270)):
                    r = dd[3] - dd[1]
                    self.line([(xf, hy), (xf - r, hy)], lw=lw * 0.6, color=c, z=8.1)
                    self.arc(xf, hy, r, a0, a1, lw=0.18, ls=(0, (2, 1.2)), color=c)
        elif k == 'vanity':
            x0, y0, x1, y1 = sh[1]
            bx0, by0, bx1, by1 = sh[2]
            self.rect(x0, y0, x1, y1, lw=lw, ec=c, fc=fillw, z=8)
            (a_, b_) = self.P(bx0, by0)
            self.ax.add_patch(FancyBboxPatch((a_, b_), self.L(bx1 - bx0), self.L(by1 - by0),
                              boxstyle='round,pad=0,rounding_size=1.0', lw=lw * 0.7, ec=c, fc='none', zorder=8.2))
            d = G.bb('Vanity_drain')
            self.circle((d[0] + d[2]) / 2, (d[1] + d[3]) / 2, 0.02, lw=lw * 0.5, ec=c, z=8.2)
        elif k == 'shower':
            D = sh[1]
            fx0, fy0, fx1, fy1 = D['floor']
            self.rect(fx0, fy0, fx1, fy1, lw=lw * 0.5, ec=c, z=7.8)
            s = D['side']; self.line([((s[0] + s[2]) / 2, s[1]), ((s[0] + s[2]) / 2, s[3])], lw=lw * 1.8, color=c, z=8.3)
            f = D['fixed']; self.line([(f[0], (f[1] + f[3]) / 2), (f[2], (f[1] + f[3]) / 2)], lw=lw * 1.8, color=c, z=8.3)
            # bi-fold door 2 x 30, hinged at the side panel, folding inward: drawn half open
            b0, b1 = D['bf0'], D['bf1']
            hx, hy = b0[0], (b0[1] + b0[3]) / 2
            L1 = b0[2] - b0[0]
            ang = math.radians(50)
            p1 = (hx + L1 * math.cos(ang), hy + L1 * math.sin(ang))
            p2 = (p1[0] + L1 * math.cos(ang), hy)
            self.line([(hx, hy), p1, p2], lw=lw * 1.4, color=c, z=8.3)
            self.line([(hx, hy), (b1[2], hy)], lw=lw * 0.4, color=c, ls=(0, (2, 1.2)), z=8.25)
            d = D['drain']
            self.rect(d[0], d[1], d[2], d[3], lw=lw * 0.6, ec=c, z=8.2, hatch=None if faint else '||||||')
            hx_, hy_ = D['head']
            self.circle(hx_, hy_, 0.15, lw=lw * 0.6, ec=c, ls=(0, (2, 1.2)), z=8.2)
            if not faint:
                for xx in (fx0 + 0.20, fx1 - 0.20):
                    self.ax.annotate('', xy=self.P(xx, d[1] - 0.02), xytext=self.P(xx, fy0 + 0.30),
                                     arrowprops=dict(arrowstyle='->', lw=0.3, color=c), zorder=8.3)
        elif k == 'wc':
            x0, y0, x1, y1 = sh[1]
            cy = (y0 + y1) / 2
            # bowl: rounded front (toward -x), straight back at the wall
            pts = []
            for i in range(0, 181, 10):
                a = math.radians(90 + i)
                pts.append((x0 + 0.27 + 0.27 * math.cos(a), cy + (y1 - y0) / 2 * math.sin(a)))
            pts += [(x1, y0), (x1, y1)]
            self.poly(pts, lw=lw, ec=c, fc=fillw, z=8)
            self.ax.add_patch(Ellipse(self.P(x0 + 0.24, cy), self.L(0.30), self.L(0.24), lw=lw * 0.6, ec=c, fc='none', zorder=8.2))
        elif k == 'plant':
            cx, cy, r = sh[1]
            self.circle(cx, cy, r * 0.75, lw=lw * 0.8, ec=c, fc=fillw, z=8)
            for i in range(8):
                a = math.radians(i * 45 + 10)
                self.line([(cx + 0.3 * r * math.cos(a), cy + 0.3 * r * math.sin(a)),
                           (cx + 1.25 * r * math.cos(a), cy + 1.25 * r * math.sin(a))], lw=lw * 0.5, color=c, z=8.1)
        elif k == 'track':
            (p, q) = sh[1]
            self.line([p, q], lw=lw * 1.2, color=c, ls=(0, (8, 1.5, 1.5, 1.5)), z=8.5)

    # ------------------------------------------------------------ misc
    def legend_box(self, x, y, w, h, title=None, fs=6.8):
        self.ax.add_patch(Rectangle((x, y), w, h, fill=True, fc='white', ec='k', lw=0.5, zorder=15))
        if title:
            self.ax.text(x + 2, y + h - 3.2, title, fontsize=fs, weight='bold', va='center', zorder=16)
            self.ax.plot([x, x + w], [y + h - 6.2, y + h - 6.2], 'k', lw=0.35, zorder=16)

    def ptext(self, x, y, s, fs=6, **k):
        k.setdefault('zorder', 16)
        return self.ax.text(x, y, s, fontsize=fs, **k)

    def scale_bar(self, x, y, n=5, label=None):
        ax = self.ax
        for i in range(n):
            ax.add_patch(Rectangle((x + i * self.S, y), self.S, 1.4, fc='k' if i % 2 == 0 else 'white',
                                   ec='k', lw=0.3, zorder=15))
            ax.text(x + i * self.S, y - 2.2, str(i), fontsize=4.8, ha='center', zorder=15)
        ax.text(x + n * self.S, y - 2.2, f'{n} m', fontsize=4.8, ha='center', zorder=15)
        ax.text(x, y + 3.5, label or f'М {self.scale}', fontsize=6, weight='bold', zorder=15)

    def save(self, fname):
        pdf = os.path.join(OUT, fname + '.pdf')
        png = os.path.join(OUT, fname + '.png')
        self.fig.savefig(pdf)
        self.fig.savefig(png, dpi=150)
        self.fig.savefig(os.path.join(PREV, fname + '_hi.png'), dpi=300)
        plt.close(self.fig)
        return pdf


def std_plan(S, walls='hatch', furn=None, openings=True, swing=True, labels=False):
    S.walls(walls)
    if openings:
        S.openings(swing=swing, labels=labels)
    if furn:
        S.furniture(furn)
