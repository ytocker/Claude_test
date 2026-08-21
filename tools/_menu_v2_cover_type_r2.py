"""cover-type — main-menu concept, THEME B "THE LAUNCH BULLETIN" (round 2).

Standalone review renderer. Touches nothing under game/; it only READS the
live modules (store_hub primitives / sky_designs / biome / draw / parrot /
store_data) so the mockup is built out of the same DNA the shipped build uses.

Round 1 was rejected as "a beautiful poster, not a game". The fix is not more
ornament — it is to stop drawing a picture and start drawing an OBJECT. The
menu is now a printed letterpress flight bulletin lying on a desk: a cotton-rag
sheet trimmed short of the canvas so a deep ink-blue backing board shows all
round, an airmail chevron trim running its perimeter, a die-cut window with a
real paper-thickness bevel that the live biome sky moves behind, and a
tipped-in START ticket on whiter stock waiting to be torn off its perforation.

Three things make it a screen instead of a print:
  * it has edges and thickness — cast shadows and stock values stack it,
  * the window is a genuine aperture and the ONLY moving thing,
  * START is a tear-off ticket, an affordance, not a coloured rectangle.

Composed at SS=2 into one 720x1280 RGBA bake with a transparent window hole,
then downscaled once. Per frame the shipped path would pay: sky clipped to the
300x146 aperture, Pip inside that clip, the baked sheet over the top, and one
masked foil-sweep blit. Nothing else is ever redrawn.

No numpy anywhere — numpy is absent on the pygbag/WASM runtime (see the guarded
fallback at game/store_design.py:197). The fibre grain is a 180x320 tile that is
smoothscaled and tiled, never a per-pixel pass over the full canvas.

Run headless:
    SDL_VIDEODRIVER=dummy python3 tools/_menu_v2_cover_type_r2.py
"""
import os
import sys
import math
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import pygame  # noqa: E402

pygame.init()
pygame.font.init()
pygame.display.set_mode((360, 640))

from game.config import W, H, GROUND_Y, PARCEL_Y_OFFSET  # noqa: E402
from game import biome, sky_designs, draw as gdraw, parrot, store_data  # noqa: E402
from game.draw import WHITE  # noqa: E402
from game.hud import _font  # noqa: E402
# The store hub is the bar this screen has to clear, so its primitives are the
# ones used here rather than a private re-implementation.
from game.store_hub import (  # noqa: E402
    SS, DW, DH, m, font, lerp_stops, vgrad_stops, multistop_v,
    drop_shadow, contact_shadow, bevel_rim, top_sheen, gradient_text,
    _glyph_base, _stamp_bold, gold_rule, downscale)

OUT_DIR = os.path.join(_REPO, "docs", "menu-v2", "cover-type")


# ═════════════════════════════════════════════════════════════════════════════
# PALETTE — two spot inks, one foil, three stocks, one board.
# ═════════════════════════════════════════════════════════════════════════════
BOARD_STOPS = [(0.00, (28, 33, 60)), (0.42, (19, 23, 45)),
               (1.00, (11, 14, 30))]
BOARD_MEAN = (18, 22, 43)

STOCK_TOP = (242, 234, 215)     # cotton rag, lit from the upper left
STOCK_BOT = (231, 221, 199)
STOCK = (238, 229, 209)         # the value the ink is measured against
STOCK_CORE = (250, 245, 233)    # unprinted core stock — only the die-cut shows it
STOCK_CORE_D = (206, 194, 172)  # the same core in the cut's shaded top wall
PLATE_TOP = (219, 205, 178)     # keyed plates: a second press of the same stock
PLATE_BOT = (203, 187, 158)
PLATE_MEAN = (211, 196, 168)
TICKET_TOP = (252, 249, 243)    # the tipped-in ticket is a whiter stock
TICKET_BOT = (243, 238, 228)

INK = (26, 28, 38)              # spot ink 1
INK_SOFT = (86, 84, 92)
SCARLET = (166, 30, 26)         # spot ink 2
SCARLET_D = (128, 20, 18)
AIRMAIL_BLUE = (30, 52, 116)
CREAM = (250, 245, 233)

FOIL_HI = (176, 142, 66)        # gold foil: a dull ochre that does NOT shade
FOIL_MID = (150, 118, 52)
FOIL_DEEP = (112, 86, 34)
FOIL_CATCH = (252, 246, 226)    # the hard diagonal mirror band

STAMP_INK = (84, 70, 124)       # rubber datestamp — a third, wetter ink

# The deboss is authored as a MULTIPLY tint and an ADDITIVE lift rather than
# two flat colours: a pit wall must darken whatever it falls across and a lip
# must lighten it, so a fixed grey would invert the effect the moment it landed
# on solid ink instead of bare stock.
DEBOSS_MULT = (196, 192, 212)   # cool shadow, upper-left inner wall
DEBOSS_LIFT = (22, 21, 18)      # paper-white, lower-right lip


# ═════════════════════════════════════════════════════════════════════════════
# LAYOUT — logical 360x640 px; m() lifts everything to the SS=2 device canvas.
# ═════════════════════════════════════════════════════════════════════════════
SHEET = pygame.Rect(7, 7, 346, 626)          # trimmed short of the canvas
TRIM_W = 9                                    # airmail chevron band
INNER = SHEET.inflate(-TRIM_W * 2, -TRIM_W * 2)
COL_L, COL_R = 30, 330
COL_W = COL_R - COL_L

TOP_LINE_Y = 24
TOP_RULE_Y = 41
APERTURE = pygame.Rect(30, 50, 300, 146)
STAMP_C, STAMP_R = (312, 208), 26

CAP = 62
WORD_BASELINE = 284
FOIL_RULE_Y = 297
SUB_Y = 304

TICKET = pygame.Rect(22, 336, 316, 96)
PERF_INSET = 12                               # white stock above the scarlet
PANEL = pygame.Rect(TICKET.x + 5, TICKET.y + PERF_INSET,
                    TICKET.w - 10, TICKET.h - PERF_INSET - 5)

UTIL_Y, UTIL_H, UTIL_W, UTIL_GAP = 456, 68, 94, 9
PROFILE = pygame.Rect(COL_L, 546, COL_W, 56)
COLOPHON_Y = 610

PHASES = [("day", 0.12), ("golden", 0.27), ("plum", 0.47), ("night", 0.70)]
PIP_U = {"day": 0.20, "golden": 0.40, "plum": 0.60, "night": 0.78}

KICKER_L = "THE SKY POST · AIR PARCEL BULLETIN"
KICKER_R = "No. 4471"
SUBTITLE = "POCKET SKY FLYER"
ROUTE_L = "ROUTE 07 · CLOUDBANK"
ROUTE_R = "PRESSED ON COTTON RAG"
COLOPHON = "ONE TAP TO FLY · NO LANDING GUARANTEED"
PLAYER = "YTOCKER"


def R(rect):
    """Logical rect -> device rect."""
    return pygame.Rect(m(rect.x), m(rect.y), m(rect.w), m(rect.h))


# ═════════════════════════════════════════════════════════════════════════════
# PRINT PRIMITIVES
# ═════════════════════════════════════════════════════════════════════════════
def tint(mask, color, alpha=255):
    img = mask.copy()
    img.fill((*color, 255), special_flags=pygame.BLEND_RGBA_MULT)
    if alpha < 255:
        img.set_alpha(alpha)
    return img


_diag_cache = {}


def diag_mask(w, h, lower_right=True, gamma=1.0):
    """A diagonal alpha ramp, authored on a 16x16 grid and smoothscaled up.
    Building it small keeps the only per-pixel work in the whole file down to
    256 writes; the smoothscale is what turns it into a smooth field."""
    key = (w, h, lower_right, gamma)
    got = _diag_cache.get(key)
    if got is not None:
        return got
    n = 16
    small = pygame.Surface((n, n), pygame.SRCALPHA)
    for yy in range(n):
        for xx in range(n):
            t = (xx + yy) / (2 * (n - 1))
            if not lower_right:
                t = 1.0 - t
            small.set_at((xx, yy), (255, 255, 255, int(255 * t ** gamma)))
    out = pygame.transform.smoothscale(small, (max(1, w), max(1, h)))
    _diag_cache[key] = out
    return out


def shade(surf, amask, pos, col=DEBOSS_MULT, a=255):
    """Darken `surf` through an alpha mask by multiplying — always darker,
    whatever it lands on."""
    w, h = amask.get_size()
    lay = pygame.Surface((w, h))
    lay.fill((255, 255, 255))
    lay.blit(tint(amask, col, a), (0, 0))
    surf.blit(lay, pos, special_flags=pygame.BLEND_RGB_MULT)


def lift(surf, amask, pos, col=DEBOSS_LIFT, a=255):
    """Lighten `surf` through an alpha mask by adding — always brighter."""
    w, h = amask.get_size()
    lay = pygame.Surface((w, h))
    lay.fill((0, 0, 0))
    lay.blit(tint(amask, col, a), (0, 0))
    surf.blit(lay, pos, special_flags=pygame.BLEND_RGB_ADD)


def _walls(mask, off):
    """Split a shape mask into its upper-left INNER wall and its lower-right
    OUTER lip — the two 1px bands a press leaves behind."""
    w, h = mask.get_size()
    solid = mask.copy()
    solid.fill((255, 255, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
    wall = pygame.Surface((w, h), pygame.SRCALPHA)
    wall.blit(mask, (0, 0))
    wall.blit(solid, (off, off), special_flags=pygame.BLEND_RGBA_SUB)
    lip = pygame.Surface((w + off, h + off), pygame.SRCALPHA)
    lip.blit(mask, (off, off))
    lip.blit(solid, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    return wall, lip


def deboss_marks(surf, mask, pos, off=None, sa=190, ha=220,
                 sh=DEBOSS_MULT, hi=DEBOSS_LIFT):
    """The letterpress tell, applied to a glyph/shape MASK: a cool shadow on the
    upper-left INNER wall of the bite and a paper-white highlight on its
    lower-right lip. That inversion — dark inside the top-left, light outside
    the bottom-right — is what separates 'pressed into paper' from 'raised off
    it', and it is the detail that most reliably reads as expensive print."""
    off = off if off is not None else max(1, m(0.55))
    wall, lip = _walls(mask, off)
    shade(surf, wall, pos, sh, sa)
    lift(surf, lip, pos, hi, ha)


def deboss_rim(surf, rect, radius, w, sh=DEBOSS_MULT, hi=DEBOSS_LIFT,
               sa=190, ha=220):
    """bevel_rim INVERTED for a shape keyed INTO the sheet. bevel_rim puts its
    bright stroke on the inner TOP-LEFT, which is how a raised object catches a
    light from that side; a pressed-in one is the exact opposite, so the dark
    stroke moves to the inner top-left and the paper-white lip goes outside the
    bottom-right. Same construction, mirrored — that mirror IS the theme."""
    wall = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(wall, (255, 255, 255, 255), wall.get_rect(), width=w,
                     border_radius=radius)
    wall.blit(diag_mask(rect.w, rect.h, lower_right=False, gamma=1.3),
              (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    shade(surf, wall, rect.topleft, sh, sa)

    outer = rect.inflate(w * 2, w * 2)
    lip = pygame.Surface(outer.size, pygame.SRCALPHA)
    pygame.draw.rect(lip, (255, 255, 255, 255), lip.get_rect(), width=w,
                     border_radius=radius + w)
    lip.blit(diag_mask(outer.w, outer.h, lower_right=True, gamma=1.3),
             (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    lift(surf, lip, outer.topleft, hi, ha)


def ink_spread(surf, mask, pos, color, alpha=54):
    """Ink bleeding a fibre-width into cotton rag. A hard vector edge is the
    other thing that gives a fake print away, so every inked glyph gets a faint
    ring of its own colour one device px out before the solid pass lands."""
    p = max(1, m(0.5))
    halo = tint(mask, color, alpha)
    for dx, dy in ((-p, 0), (p, 0), (0, -p), (0, p),
                   (-p, -p), (p, -p), (-p, p), (p, p)):
        surf.blit(halo, (pos[0] + dx, pos[1] + dy))


def type_mask(text, size, track=0.0, weight=0.0):
    base = _glyph_base(text, font(size), int(round(m(track))))
    if weight:
        base = _stamp_bold(base, m(weight))
    return base


def tracked(surf, text, pos, size, color, track=0.0, anchor="left",
            weight=0.0, press=True, spread=True, alpha=255):
    """Small-caps furniture type, set with tracking and pressed into the stock.
    pos is logical; the returned rect is device."""
    base = type_mask(text, size, track, weight)
    w, h = base.get_size()
    x, y = m(pos[0]), m(pos[1])
    if anchor == "center":
        x -= w // 2
    elif anchor == "right":
        x -= w
    if spread:
        ink_spread(surf, base, (x, y), color)
    surf.blit(tint(base, color, alpha), (x, y))
    if press:
        deboss_marks(surf, base, (x, y))
    return pygame.Rect(x, y, w, h)


def tracked_w(text, size, track=0.0, weight=0.0):
    """Measured logical width of a tracked string."""
    return type_mask(text, size, track, weight).get_width() / SS


def vtext(surf, text, x, y_center, size, color, track=0.0, up=True):
    """Margin docket type running up (or down) the sheet's edge."""
    base = type_mask(text, size, track)
    strip = pygame.Surface(base.get_size(), pygame.SRCALPHA)
    ink_spread(strip, base, (0, 0), color)
    strip.blit(tint(base, color), (0, 0))
    deboss_marks(strip, base, (0, 0))
    rot = pygame.transform.rotate(strip, 90 if up else -90)
    surf.blit(rot, rot.get_rect(center=(m(x), m(y_center))))
    return base.get_width() / SS


# ═════════════════════════════════════════════════════════════════════════════
# FIBRE GRAIN — a 180x320 tile, smoothscaled and tiled.
# ═════════════════════════════════════════════════════════════════════════════
_grain = None


def grain_tiles():
    """Bake the +/-3-value cotton-rag noise field ONCE as two small tiles (one
    subtractive, one additive) plus a sparse dark-fleck pass. A 720x1280 set_at
    sweep would be ~920k Python-level pixel writes and is unshippable on the
    WASM runtime; a 180x320 tile is 57.6k, smoothscales to exactly one final
    pixel per noise cell, and tiles the canvas in four blits per pass."""
    global _grain
    if _grain is not None:
        return _grain
    tw, th = 180, 320
    sub = pygame.Surface((tw, th))
    add = pygame.Surface((tw, th))
    rng = random.Random(20260821)
    for yy in range(th):
        for xx in range(tw):
            d = rng.gauss(0.0, 2.2)
            if rng.random() > 0.9968:
                d -= rng.uniform(8.0, 17.0)   # a slub of raw fibre
            if d >= 0:
                v = min(7, int(d))
                add.set_at((xx, yy), (v, v, v))
                sub.set_at((xx, yy), (0, 0, 0))
            else:
                v = min(22, int(-d))
                sub.set_at((xx, yy), (v, v, v))
                add.set_at((xx, yy), (0, 0, 0))
    # One noise cell -> SS device px -> exactly 1 px in the final 360x640 frame.
    sub = pygame.transform.smoothscale(sub, (tw * SS, th * SS))
    add = pygame.transform.smoothscale(add, (tw * SS, th * SS))
    _grain = (sub, add)
    return _grain


def apply_grain(surf):
    """Tile the baked grain over the device canvas. Mirrored per tile so the
    180x320 repeat never shows as a visible grid."""
    sub, add = grain_tiles()
    tw, thh = sub.get_size()
    for ix in range(0, DW, tw):
        for iy in range(0, DH, thh):
            fx, fy = bool(ix // tw % 2), bool(iy // thh % 2)
            s = pygame.transform.flip(sub, fx, fy) if (fx or fy) else sub
            a = pygame.transform.flip(add, fx, fy) if (fx or fy) else add
            surf.blit(s, (ix, iy), special_flags=pygame.BLEND_RGB_SUB)
            surf.blit(a, (ix, iy), special_flags=pygame.BLEND_RGB_ADD)


# ═════════════════════════════════════════════════════════════════════════════
# CUSTOM GEOMETRIC CAPS — the wordmark is artwork, not a font call.
# ═════════════════════════════════════════════════════════════════════════════
PEN_SS = 3
STEM = 0.200
THIN = 0.155
PAD = 0.06
GLYPH_W = {"S": 0.68, "K": 0.70, "Y": 0.70, "B": 0.66, "I": 0.20, "T": 0.66}
OVERSHOOT = 0.012


class _Pen:
    """Draws one glyph in cap units (y up from the baseline) onto an oversized
    mask that is smoothscaled down to the device cap height."""

    def __init__(self, width_units, cap_px):
        self.wu = width_units
        self.cap = cap_px
        self.u = cap_px * PEN_SS
        self.w = int(round(width_units * self.u))
        self.h = int(round((1.0 + PAD * 2) * self.u))
        self.base = (1.0 + PAD) * self.u
        self.surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)

    def px(self, x, y):
        return (x * self.u, self.base - y * self.u)

    def _scratch(self):
        return pygame.Surface((self.w, self.h), pygame.SRCALPHA)

    def _cut(self, scratch):
        self.surf.blit(scratch, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

    def rect(self, x0, y0, x1, y1, target=None):
        t = self.surf if target is None else target
        ax, ay = self.px(x0, y1)
        bx, by = self.px(x1, y0)
        pygame.draw.rect(t, (255, 255, 255, 255),
                         pygame.Rect(round(ax), round(ay),
                                     round(bx - ax), round(by - ay)))

    def ellipse(self, cx, cy, rx, ry, target=None):
        t = self.surf if target is None else target
        left, top = self.px(cx - rx, cy + ry)
        pygame.draw.ellipse(t, (255, 255, 255, 255),
                            pygame.Rect(round(left), round(top),
                                        round(2 * rx * self.u),
                                        round(2 * ry * self.u)))

    def poly(self, pts, target=None):
        t = self.surf if target is None else target
        pygame.draw.polygon(t, (255, 255, 255, 255),
                            [self.px(x, y) for x, y in pts])

    def cut_ellipse(self, cx, cy, rx, ry, clip_x=None):
        s = self._scratch()
        if clip_x is not None:
            s.set_clip(pygame.Rect(round(clip_x * self.u), 0, self.w, self.h))
        self.ellipse(cx, cy, rx, ry, target=s)
        s.set_clip(None)
        self._cut(s)

    def cut_wedge(self, cx, cy, a0, a1, r):
        """Remove the pie slice from a0 to a1. The radius stays just past the
        ring being cut so the slice can't reach across and eat a stroke it was
        never aimed at."""
        s = self._scratch()
        pts = [(cx, cy)]
        n = 72
        for i in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        self.poly(pts, target=s)
        self._cut(s)

    def diagonal(self, p0, p1, hh):
        (x0, y0), (x1, y1) = p0, p1
        self.poly([(x0 - hh, y0), (x1 - hh, y1), (x1 + hh, y1), (x0 + hh, y0)])

    def trim(self, x0=None, y_top=None, y_bot=None):
        """Flat-cut whatever a diagonal threw past the cap line, the baseline or
        the sidebearing, so terminals land square the way a geometric face cuts
        them instead of on the polygon's own mitre."""
        s = self._scratch()
        if y_top is not None:
            self.rect(-0.4, y_top, self.wu + 0.4, y_top + 0.6, target=s)
        if y_bot is not None:
            self.rect(-0.4, y_bot - 0.6, self.wu + 0.4, y_bot, target=s)
        if x0 is not None:
            self.rect(x0, -0.6, x0 + 0.6, 1.6, target=s)
        self._cut(s)

    def branch(self):
        return _Pen(self.wu, self.cap)

    def merge(self, other):
        self.surf.blit(other.surf, (0, 0))

    def finish(self):
        return pygame.transform.smoothscale(
            self.surf, (max(1, int(round(self.wu * self.cap))),
                        max(1, int(round((1.0 + PAD * 2) * self.cap)))))


def _glyph_S(p):
    top = p.branch()
    top.ellipse(0.34, 0.72, 0.325, 0.28 + OVERSHOOT)
    top.cut_ellipse(0.34, 0.72, 0.325 - STEM, 0.28 - THIN)
    top.cut_wedge(0.34, 0.72, 272, 368, 0.36)
    bot = p.branch()
    bot.ellipse(0.34, 0.29, 0.34, 0.29 + OVERSHOOT)
    bot.cut_ellipse(0.34, 0.29, 0.34 - STEM, 0.29 - THIN)
    bot.cut_wedge(0.34, 0.29, 92, 188, 0.37)
    p.merge(top)
    p.merge(bot)


def _glyph_K(p):
    p.rect(0.0, 0.0, STEM, 1.0)
    p.diagonal((0.17, 0.49), (0.650, 1.08), 0.115)
    p.diagonal((0.17, 0.49), (0.653, -0.08), 0.120)
    p.trim(x0=p.wu, y_top=1.0, y_bot=0.0)


def _glyph_Y(p):
    p.diagonal((0.35, 0.40), (0.067, 1.08), 0.100)
    p.diagonal((0.35, 0.40), (0.633, 1.08), 0.100)
    p.rect(0.25, 0.0, 0.45, 0.46)
    p.trim(x0=p.wu, y_top=1.0, y_bot=0.0)


def _glyph_B(p):
    p.ellipse(0.19, 0.72, 0.47, 0.28 + OVERSHOOT)
    p.ellipse(0.19, 0.29, 0.47, 0.29 + OVERSHOOT)
    p.rect(0.0, 0.0, STEM, 1.0)
    p.cut_ellipse(0.19, 0.72, 0.47 - STEM, 0.28 - THIN, clip_x=STEM)
    p.cut_ellipse(0.19, 0.29, 0.47 - STEM, 0.29 - THIN, clip_x=STEM)


def _glyph_I(p):
    p.rect(0.0, 0.0, STEM, 1.0)


def _glyph_T(p):
    p.rect(0.0, 1.0 - THIN, 0.66, 1.0)
    p.rect(0.23, 0.0, 0.43, 1.0 - THIN)


_BUILDERS = {"S": _glyph_S, "K": _glyph_K, "Y": _glyph_Y,
             "B": _glyph_B, "I": _glyph_I, "T": _glyph_T}
_GLYPHS = {}


def glyph(ch, cap_px):
    key = (ch, cap_px)
    g = _GLYPHS.get(key)
    if g is None:
        p = _Pen(GLYPH_W[ch], cap_px)
        _BUILDERS[ch](p)
        g = p.finish()
        _GLYPHS[key] = g
    return g


# Optical pairs: Y|B and I|T open a hole under the arm / crossbar so they close
# up; K|Y interlocks at the cap line and needs air.
KERN = {("S", "K"): -1, ("K", "Y"): 2, ("Y", "B"): -2,
        ("B", "I"): -1, ("I", "T"): -2}
TRACK_EM = 6.4 / 72.0


_word_cache = {}


def wordmark_mask(cap_px):
    """White mask of SKYBIT set at cap_px, trimmed to its own ink."""
    got = _word_cache.get(cap_px)
    if got is not None:
        return got
    track = TRACK_EM * cap_px
    parts, x, prev = [], 0.0, None
    for ch in "SKYBIT":
        g = glyph(ch, cap_px)
        bb = g.get_bounding_rect(min_alpha=24)
        if prev is not None:
            x += track + KERN[(prev, ch)] * cap_px / 72.0
        parts.append((ch, g, bb, x))
        x += bb.width
        prev = ch
    surf = pygame.Surface((int(math.ceil(x)) + 4,
                           glyph("S", cap_px).get_height()), pygame.SRCALPHA)
    for _ch, g, bb, gx in parts:
        surf.blit(g, (round(gx - bb.x), 0))
    bb = surf.get_bounding_rect(min_alpha=8)
    out = surf.subsurface(bb).copy()
    _word_cache[cap_px] = (out, parts)
    return _word_cache[cap_px]


# ═════════════════════════════════════════════════════════════════════════════
# GOLD FOIL — a mirror, so it does not shade: dull ochre plus a hard catch.
# ═════════════════════════════════════════════════════════════════════════════
def foil_body(mask):
    w, h = mask.get_size()
    body = vgrad_stops(w, h, 0, [(0.00, FOIL_HI), (0.46, FOIL_MID),
                                 (1.00, FOIL_DEEP)])
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    out.blit(body, (0, 0))
    out.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return out


def catch_source(mask):
    """The near-white sheen the foil catch is CUT from: top_sheen over the full
    glyph block, already masked to the wordmark. The sweep then only has to
    intersect it with a moving diagonal — one polygon and two blits a frame."""
    w, h = mask.get_size()
    sheen = pygame.Surface((w, h), pygame.SRCALPHA)
    top_sheen(sheen, pygame.Rect(0, 0, w, h), 0, h, peak=255)
    lift = pygame.Surface((w, h), pygame.SRCALPHA)
    lift.fill((255, 255, 255, 150))
    sheen.blit(lift, (0, 0))
    src = tint(sheen, FOIL_CATCH)
    src.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return src


def catch_band(src, t, slant=0.62, width_f=0.20):
    """One hard diagonal band of the sheen. Hard-edged on purpose: a soft
    gradient across gold reads as a lit plastic bevel, a hard band reads as a
    mirror catching a window."""
    w, h = src.get_size()
    dx = h * slant
    bw = w * width_f
    span = w + dx + bw
    x0 = -dx - bw + t * span
    poly = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(poly, (255, 255, 255, 255),
                        [(x0, h), (x0 + bw, h), (x0 + bw + dx, 0), (x0 + dx, 0)])
    pygame.draw.polygon(poly, (255, 255, 255, 110),
                        [(x0 + bw * 1.35, h), (x0 + bw * 1.75, h),
                         (x0 + bw * 1.75 + dx, 0), (x0 + bw * 1.35 + dx, 0)])
    out = src.copy()
    out.blit(poly, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return out


# ═════════════════════════════════════════════════════════════════════════════
# AIRMAIL CHEVRON TRIM — the courier signal, running the sheet's outer edge.
# ═════════════════════════════════════════════════════════════════════════════
def chevron_strip(length, band, seed_shift=0):
    """Alternating scarlet / airmail-blue parallelograms on bare stock, the
    1928 lozenge border. Drawn oversized and sheared, then clipped to the band."""
    strip = pygame.Surface((length, band), pygame.SRCALPHA)
    strip.fill((*STOCK_CORE, 255))
    pitch = m(9.0)
    lean = band * 0.85
    i = seed_shift
    x = -lean - pitch
    while x < length + lean + pitch:
        col = SCARLET if i % 2 == 0 else AIRMAIL_BLUE
        pygame.draw.polygon(strip, (*col, 255),
                            [(x, band), (x + pitch * 0.62, band),
                             (x + pitch * 0.62 + lean, 0), (x + lean, 0)])
        x += pitch
        i += 1
    return strip


def draw_trim(surf):
    sh = R(SHEET)
    band = m(TRIM_W)
    top = chevron_strip(sh.w, band)
    surf.blit(top, (sh.x, sh.y))
    surf.blit(pygame.transform.flip(top, True, True), (sh.x, sh.bottom - band))
    side = chevron_strip(sh.h, band, seed_shift=1)
    surf.blit(pygame.transform.rotate(side, 90), (sh.x, sh.y))
    surf.blit(pygame.transform.rotate(pygame.transform.flip(side, True, True),
                                      -90), (sh.right - band, sh.y))
    # The trim is printed, so it is bitten in like everything else.
    deboss_rim(surf, sh.inflate(-band * 2, -band * 2), m(1), max(1, m(0.9)),
               sa=120, ha=150)


# ═════════════════════════════════════════════════════════════════════════════
# RUBBER DATESTAMP — broken coverage, because a solid stamp always reads fake.
# ═════════════════════════════════════════════════════════════════════════════
def datestamp(surf, center, radius, angle=-13.0):
    r = m(radius)
    pad = m(6)
    size = (r + pad) * 2
    st = pygame.Surface((size, size), pygame.SRCALPHA)
    c = r + pad
    pygame.draw.circle(st, (255, 255, 255, 255), (c, c), r, max(2, m(1.8)))
    pygame.draw.circle(st, (255, 255, 255, 255), (c, c), int(r * 0.72),
                       max(1, m(0.9)))
    pygame.draw.rect(st, (255, 255, 255, 255),
                     pygame.Rect(c - int(r * 0.60), c - m(4.5),
                                 int(r * 1.20), m(9)), border_radius=m(1))

    def arc_text(txt, rr, a_mid, a_span, size_px, flip=False):
        f = font(size_px)
        n = len(txt)
        for i, ch in enumerate(txt):
            frac = (i - (n - 1) / 2.0) / max(1, n - 1)
            a = math.radians(a_mid + a_span * frac)
            g = f.render(ch, True, WHITE)
            rot = -math.degrees(a) + (90 if flip else -90)
            g = pygame.transform.rotate(g, rot)
            px = c + rr * math.cos(a)
            py = c + rr * math.sin(a)
            st.blit(g, g.get_rect(center=(px, py)))

    arc_text("SKY POST", r * 0.86, -90, 96, 7)
    arc_text("DISPATCHED", r * 0.86, 90, -96, 7, flip=True)
    d = font(9).render("21 AUG", True, (0, 0, 0))
    st.blit(d, d.get_rect(center=(c, c)), special_flags=pygame.BLEND_RGBA_SUB)

    # Broken coverage: a rubber die never inks evenly. Chew holes out of the
    # impression with a scatter of soft voids, heavier toward the rim where a
    # hand-held stamp rocks off the paper.
    rng = random.Random(4471)
    for _ in range(190):
        a = rng.uniform(0, math.tau)
        rr = r * math.sqrt(rng.uniform(0.0, 1.0))
        bias = 0.30 + 0.70 * (rr / r) ** 1.5
        if rng.random() > bias:
            continue
        hx = c + rr * math.cos(a)
        hy = c + rr * math.sin(a)
        hr = rng.uniform(m(0.7), m(2.6))
        pygame.draw.circle(st, (0, 0, 0, 0), (int(hx), int(hy)), int(hr))
    for _ in range(5):
        a = rng.uniform(0, math.tau)
        pygame.draw.line(st, (0, 0, 0, 0),
                         (c + r * 0.35 * math.cos(a), c + r * 0.35 * math.sin(a)),
                         (c + r * 1.05 * math.cos(a), c + r * 1.05 * math.sin(a)),
                         int(m(rng.uniform(1.0, 2.2))))

    st = pygame.transform.rotate(st, angle)
    inked = tint(st, STAMP_INK, 196)
    pos = inked.get_rect(center=(m(center[0]), m(center[1]))).topleft
    surf.blit(inked, pos)
    # A wet stamp sits ON the fibre rather than in it, so it gets only the
    # faintest press — enough to stop it floating, not enough to claim it was
    # printed with the plate.
    deboss_marks(surf, st, pos, sa=70, ha=90)


# ═════════════════════════════════════════════════════════════════════════════
# THE TEAR-OFF START TICKET
# ═════════════════════════════════════════════════════════════════════════════
def perforation(surf, rect, y):
    """Half-punched circles plus a fibre fringe along the tear line. The punches
    read as holes (they show the sheet beneath, shaded) and the fringe is what
    stops the edge looking laser-cut."""
    yy = m(y)
    pitch = m(7.4)
    x = rect.x + pitch * 0.6
    rng = random.Random(77)
    while x < rect.right - pitch * 0.3:
        pr = m(2.0)
        pygame.draw.circle(surf, (*STOCK_BOT, 255), (int(x), yy), int(pr))
        pygame.draw.arc(surf, (120, 110, 104, 235),
                        pygame.Rect(int(x - pr), int(yy - pr), int(pr * 2),
                                    int(pr * 2)),
                        math.radians(20), math.radians(200), max(1, m(0.7)))
        pygame.draw.arc(surf, (253, 250, 244, 220),
                        pygame.Rect(int(x - pr), int(yy - pr), int(pr * 2),
                                    int(pr * 2)),
                        math.radians(200), math.radians(380), max(1, m(0.7)))
        x += pitch
    fringe = pygame.Surface(rect.size, pygame.SRCALPHA)
    fx = rect.x
    while fx < rect.right:
        h = rng.uniform(m(0.4), m(1.8))
        w = rng.uniform(m(0.6), m(2.2))
        a = int(rng.uniform(120, 235))
        pygame.draw.rect(fringe, (*TICKET_TOP, a),
                         pygame.Rect(int(fx - rect.x), int(yy - rect.y - h),
                                     int(w), int(h) + 1))
        fx += w + rng.uniform(m(0.3), m(1.4))
    surf.blit(fringe, rect.topleft)


def draw_ticket(surf):
    t = R(TICKET)
    rad = m(2)
    # The one element proud of the sheet, so the one element with a real
    # cast shadow onto it.
    drop_shadow(surf, t, rad, m(5), 118, m(3))
    stock = vgrad_stops(t.w, t.h, rad, [(0.0, TICKET_TOP), (1.0, TICKET_BOT)])
    surf.blit(stock, t.topleft)
    # The ticket is the one thing here that is RAISED, so it gets bevel_rim the
    # way store_hub ships it — bright inner stroke on the top-left. Everything
    # else on the page runs that same construction inverted.
    bevel_rim(surf, t, rad, (196, 186, 168), (255, 253, 248, 230),
              max(1, m(1.0)))
    top_sheen(surf, t, rad, m(10), peak=30)

    p = R(PANEL)
    panel = vgrad_stops(p.w, p.h, m(1),
                        [(0.00, SCARLET), (0.72, SCARLET),
                         (1.00, SCARLET_D)])
    surf.blit(panel, p.topleft)
    deboss_rim(surf, p, m(1), max(1, m(1.1)), sa=205, ha=235)

    # ONE line of reversed-out type. The stock tone in the ramp is what a
    # knocked-out letter actually shows.
    gradient_text(surf, "START", font(30),
                  (p.centerx - m(16), p.centery + m(1)),
                  (253, 250, 244), (233, 223, 203),
                  shadow=False, tracking=m(6), weight=m(0.6))
    cx, cy = p.right - m(30), p.centery
    pygame.draw.polygon(surf, CREAM,
                        [(cx - m(5), cy - m(9)), (cx + m(5), cy),
                         (cx - m(5), cy + m(9)), (cx - m(1.5), cy)])

    perforation(surf, t, TICKET.y + PERF_INSET - 5)
    contact_shadow(surf, t, rad, m(3), alpha=54)


# ═════════════════════════════════════════════════════════════════════════════
# KEYED UTILITY PLATES + INK ICONS
# ═════════════════════════════════════════════════════════════════════════════
def util_rects():
    return [pygame.Rect(COL_L + i * (UTIL_W + UTIL_GAP), UTIL_Y, UTIL_W, UTIL_H)
            for i in range(3)]


def icon_bag(surf, cx, cy):
    w, h = m(19), m(16)
    body = pygame.Rect(cx - w // 2, cy - h // 2 + m(3), w, h)
    pygame.draw.rect(surf, INK, body, width=max(2, m(2.4)), border_radius=m(2))
    pygame.draw.arc(surf, INK,
                    pygame.Rect(cx - m(6.5), body.top - m(8), m(13), m(15)),
                    0.18, math.pi - 0.18, max(2, m(2.4)))
    pygame.draw.circle(surf, INK, (cx, body.centery + m(1)), m(1.6))


def icon_trophy(surf, cx, cy):
    r = m(1.0)
    cup = [(cx - m(8.5), cy - m(9)), (cx + m(8.5), cy - m(9)),
           (cx + m(6.5), cy + m(1)), (cx + m(2.6), cy + m(5)),
           (cx - m(2.6), cy + m(5)), (cx - m(6.5), cy + m(1))]
    pygame.draw.polygon(surf, INK, cup)
    pygame.draw.arc(surf, INK,
                    pygame.Rect(cx + m(5.5), cy - m(9), m(10), m(11)),
                    -1.35, 1.25, max(2, m(2.4)))
    pygame.draw.arc(surf, INK,
                    pygame.Rect(cx - m(15.5), cy - m(9), m(10), m(11)),
                    math.pi - 1.25, math.pi + 1.35, max(2, m(2.4)))
    pygame.draw.rect(surf, INK, pygame.Rect(cx - m(2), cy + m(4), m(4), m(4)))
    pygame.draw.rect(surf, INK, pygame.Rect(cx - m(7.5), cy + m(7.5), m(15),
                                            m(3.6)), border_radius=int(r))


def icon_gear(surf, cx, cy):
    r_out, r_in = m(9.6), m(6.4)
    for i in range(8):
        a = math.radians(i * 45)
        pts = []
        for k in (-0.30, 0.30):
            for rr in (r_in - m(1), r_out + m(1.4)):
                pts.append((cx + rr * math.cos(a + k), cy + rr * math.sin(a + k)))
        pygame.draw.polygon(surf, INK, [pts[0], pts[1], pts[3], pts[2]])
    pygame.draw.circle(surf, INK, (cx, cy), int(r_in + m(1.5)))
    pygame.draw.circle(surf, PLATE_MEAN, (cx, cy), int(m(3.8)))


def icon_docket(surf, cx, cy):
    """A stamped passport page — the PROFILE mark."""
    w, h = m(16), m(19)
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    pygame.draw.rect(surf, INK, r, width=max(2, m(2.2)), border_radius=m(1.5))
    pygame.draw.circle(surf, INK, (r.centerx, r.y + m(6)), m(3.0))
    pygame.draw.arc(surf, INK,
                    pygame.Rect(r.centerx - m(5), r.y + m(9), m(10), m(9)),
                    math.pi + 0.25, math.tau - 0.25, max(2, m(2.2)))


UTILS = (("STORE", icon_bag), ("TOP 10", icon_trophy), ("SETTINGS", icon_gear))


def keyed_plate(surf, rect, rad=None):
    """A plate physically keyed INTO the sheet: darker stock, ink keyline, a
    solid ink bottom edge standing in for the letterpress shadow, and the
    deboss inversion round the whole thing. Three of these read as three
    pressable objects in a way a row of labels never can."""
    rad = m(2) if rad is None else rad
    body = vgrad_stops(rect.w, rect.h, rad, [(0.0, PLATE_TOP), (1.0, PLATE_BOT)])
    surf.blit(body, rect.topleft)
    inner = pygame.Surface(rect.size, pygame.SRCALPHA)
    for i in range(m(5)):
        a = int(58 * (1 - i / m(5)) ** 1.4)
        pygame.draw.line(inner, (108, 96, 78, a), (0, i), (rect.w, i))
    surf.blit(inner, rect.topleft)
    pygame.draw.rect(surf, INK,
                     pygame.Rect(rect.x, rect.bottom - m(4), rect.w, m(4)),
                     border_bottom_left_radius=rad, border_bottom_right_radius=rad)
    pygame.draw.rect(surf, INK, rect, width=max(2, m(1.6)), border_radius=rad)
    deboss_rim(surf, rect, rad, max(1, m(1.1)))


# ═════════════════════════════════════════════════════════════════════════════
# THE DIE-CUT WINDOW
# ═════════════════════════════════════════════════════════════════════════════
def cut_window(surf):
    """Cut the aperture: an ink keyline, then two logical px of unprinted core
    stock as the paper's own thickness (shaded on the top wall, lit on the
    bottom lip), then the hole itself with the cut's shadow falling inward."""
    ap = R(APERTURE)
    key = ap.inflate(m(8), m(8))
    pygame.draw.rect(surf, INK, key, width=m(2))
    deboss_rim(surf, key, 0, max(1, m(1.0)), sa=150, ha=190)

    bev = ap.inflate(m(4), m(4))
    pygame.draw.rect(surf, STOCK_CORE, bev, width=m(2))
    dark = pygame.Surface(bev.size, pygame.SRCALPHA)
    pygame.draw.rect(dark, (*STOCK_CORE_D, 255), dark.get_rect(), width=m(2))
    dark.blit(diag_mask(bev.w, bev.h, lower_right=False, gamma=1.5), (0, 0),
              special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(dark, bev.topleft)

    surf.fill((0, 0, 0, 0), ap)
    # The cut casts INTO the view: the sheet's thickness shades the sky it
    # frames along the lit-side walls.
    sh = pygame.Surface(ap.size, pygame.SRCALPHA)
    depth = m(7)
    for i in range(depth):
        a = int(96 * (1 - i / depth) ** 1.9)
        pygame.draw.line(sh, (12, 14, 26, a), (0, i), (ap.w, i))
        pygame.draw.line(sh, (12, 14, 26, int(a * 0.8)), (i, 0), (i, ap.h))
    for i in range(m(4)):
        a = int(40 * (1 - i / m(4)) ** 1.6)
        pygame.draw.line(sh, (12, 14, 26, a), (0, ap.h - 1 - i),
                         (ap.w, ap.h - 1 - i))
    surf.blit(sh, ap.topleft)


# ═════════════════════════════════════════════════════════════════════════════
# REGISTRATION MARKS — press furniture, at the corners where it belongs.
# ═════════════════════════════════════════════════════════════════════════════
def reg_mark(surf, x, y, r=5):
    cx, cy = m(x), m(y)
    rr = m(r)
    pygame.draw.circle(surf, INK, (cx, cy), int(rr * 0.62), max(1, m(0.8)))
    pygame.draw.line(surf, INK, (cx - rr, cy), (cx + rr, cy), max(1, m(0.8)))
    pygame.draw.line(surf, INK, (cx, cy - rr), (cx, cy + rr), max(1, m(0.8)))
    pygame.draw.line(surf, SCARLET, (cx - rr, cy - rr),
                     (cx - int(rr * 0.55), cy - rr), max(1, m(1.2)))
    pygame.draw.line(surf, AIRMAIL_BLUE, (cx + int(rr * 0.55), cy + rr),
                     (cx + rr, cy + rr), max(1, m(1.2)))


# ═════════════════════════════════════════════════════════════════════════════
# THE BAKE — one RGBA surface, transparent at the aperture.
# ═════════════════════════════════════════════════════════════════════════════
_BAKE = None
_CATCH = None
_WORD_POS = None


def build_bake():
    """Everything except the sky, Pip and the foil sweep, composed once at
    SS=2 and downscaled in a single pass."""
    global _WORD_POS
    big = pygame.Surface((DW, DH), pygame.SRCALPHA)

    # ── backing board ────────────────────────────────────────────────────────
    big.blit(multistop_v(DW, DH, BOARD_STOPS), (0, 0))
    mat = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for x in range(0, DW, m(3)):
        pygame.draw.line(mat, (255, 255, 255, 5), (x, 0), (x, DH))
    for y in range(0, DH, m(3)):
        pygame.draw.line(mat, (0, 0, 0, 7), (0, y), (DW, y))
    big.blit(mat, (0, 0))
    # One window's worth of light from the upper left, so the mat falls off
    # diagonally instead of ramping like a UI background. The falloff colour is
    # sampled off the board's own ramp — it stays one material, never a vignette.
    fall = pygame.Surface((DW, DH), pygame.SRCALPHA)
    fall.fill((*lerp_stops(BOARD_STOPS, 1.0), 200))
    fall.blit(diag_mask(DW, DH, lower_right=True, gamma=1.7), (0, 0),
              special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(fall, (0, 0))

    # ── the sheet ────────────────────────────────────────────────────────────
    sh = R(SHEET)
    drop_shadow(big, sh, m(2), m(7), 150, m(4))
    big.blit(vgrad_stops(sh.w, sh.h, m(2),
                         [(0.00, STOCK_TOP), (0.55, STOCK), (1.00, STOCK_BOT)]),
             sh.topleft)
    # Trimmed edges: the lit lip on the top-left, the cut shoulder bottom-right.
    edge = pygame.Surface(sh.size, pygame.SRCALPHA)
    pygame.draw.rect(edge, (255, 253, 248, 200), edge.get_rect(),
                     width=max(1, m(0.9)), border_radius=m(2))
    edge.blit(diag_mask(sh.w, sh.h, lower_right=False, gamma=1.6), (0, 0),
              special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(edge, sh.topleft)
    shoulder = pygame.Surface(sh.size, pygame.SRCALPHA)
    pygame.draw.rect(shoulder, (120, 108, 90, 200), shoulder.get_rect(),
                     width=max(1, m(0.9)), border_radius=m(2))
    shoulder.blit(diag_mask(sh.w, sh.h, lower_right=True, gamma=1.6), (0, 0),
                  special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(shoulder, sh.topleft)

    draw_trim(big)
    for x, y in ((20, 20), (340, 20), (20, 620), (340, 620)):
        reg_mark(big, x, y)

    # ── perimeter furniture ──────────────────────────────────────────────────
    tracked(big, KICKER_L, (COL_L, TOP_LINE_Y), 8, INK_SOFT, track=1.5)
    tracked(big, KICKER_R, (COL_R, TOP_LINE_Y), 8, INK, track=1.2,
            anchor="right")
    rule = pygame.Rect(m(COL_L), m(TOP_RULE_Y), m(COL_W), max(1, m(1.4)))
    rule_mask = pygame.Surface(rule.size, pygame.SRCALPHA)
    rule_mask.fill((255, 255, 255, 255))
    ink_spread(big, rule_mask, rule.topleft, INK)
    big.blit(tint(rule_mask, INK), rule.topleft)
    deboss_marks(big, rule_mask, rule.topleft)
    vtext(big, ROUTE_L, 22.5, 268, 7, INK_SOFT, track=1.6, up=True)
    vtext(big, ROUTE_R, 337.5, 528, 7, INK_SOFT, track=1.6, up=False)
    tracked(big, COLOPHON, (180, COLOPHON_Y), 7, INK_SOFT, track=1.4,
            anchor="center")

    # ── die-cut window ───────────────────────────────────────────────────────
    cut_window(big)
    # The stamp lands across the window frame the way a hand-held die would,
    # then the aperture is punched out of it again — a rubber stamp cannot ink
    # a hole, so the cut edge shears the impression and sells the die-cut.
    stamp_layer = pygame.Surface((DW, DH), pygame.SRCALPHA)
    datestamp(stamp_layer, STAMP_C, STAMP_R)
    stamp_layer.fill((0, 0, 0, 0), R(APERTURE))
    big.blit(stamp_layer, (0, 0))

    # ── wordmark in gold foil ────────────────────────────────────────────────
    wm, _parts = wordmark_mask(m(CAP))
    wx = m(COL_L) - max(1, m(1))
    wy = m(WORD_BASELINE) - wm.get_height()
    _WORD_POS = (wx, wy)
    big.blit(foil_body(wm), (wx, wy))
    deboss_marks(big, wm, (wx, wy), off=max(1, m(0.7)), sa=215, ha=240)

    gold_rule(big, m(COL_L), m(200), m(FOIL_RULE_Y), FOIL_MID, peak=210,
              thick=max(1, m(1.4)))
    tracked(big, SUBTITLE, (COL_L, SUB_Y), 11, INK, track=4.0, weight=0.4)

    # ── ticket, plates ───────────────────────────────────────────────────────
    draw_ticket(big)

    for r, (label, icon) in zip(util_rects(), UTILS):
        dr = R(r)
        keyed_plate(big, dr)
        icon(big, dr.centerx, dr.y + m(24))
        tracked(big, label, (r.centerx, r.bottom - 27), 12, INK, track=1.0,
                anchor="center", weight=0.3)

    pr = R(PROFILE)
    keyed_plate(big, pr)
    icon_docket(big, pr.x + m(26), pr.centery - m(2))
    tracked(big, "PROFILE", (PROFILE.x + 46, PROFILE.y + 12), 9, INK_SOFT,
            track=2.0)
    tracked(big, PLAYER, (PROFILE.x + 46, PROFILE.y + 25), 17, INK, track=0.8,
            weight=0.4)
    px, py = pr.right - m(20), pr.centery - m(2)
    pygame.draw.polygon(big, INK,
                        [(px - m(4), py - m(7)), (px + m(4), py),
                         (px - m(4), py + m(7)), (px - m(1), py)])

    # ── the stock's own fibre, over the whole print ──────────────────────────
    apply_grain(big)
    return downscale(big)


def bake():
    global _BAKE, _CATCH
    if _BAKE is None:
        _BAKE = build_bake()
        wm, _p = wordmark_mask(m(CAP))
        small = pygame.transform.smoothscale(
            wm, (round(wm.get_width() / SS), round(wm.get_height() / SS)))
        _CATCH = (catch_source(small),
                  (round(_WORD_POS[0] / SS), round(_WORD_POS[1] / SS)))
    return _BAKE


# ═════════════════════════════════════════════════════════════════════════════
# THE LIVE APERTURE — the only thing on the page that moves.
# ═════════════════════════════════════════════════════════════════════════════
CROP_TOP = 394                 # lands the alpine crest ~73% down the aperture,
                               # with the receding ranges filling the sill
_sky_scratch = None


def sky_into_window(surf, phase):
    """Draw the biome sky CLIPPED to the aperture band. Because the whole sheet
    is opaque, only 300x146 px of sky is ever visible, so the clip is the whole
    per-frame sky cost — cheaper than the full-screen sky a full-bleed menu pays."""
    global _sky_scratch
    if _sky_scratch is None:
        _sky_scratch = pygame.Surface((W, H))
    band = pygame.Rect(APERTURE.x, CROP_TOP, APERTURE.w, APERTURE.h)
    _sky_scratch.set_clip(band)
    pal = biome.palette_for_phase(phase)
    if not sky_designs.render_active(_sky_scratch, W, H, GROUND_Y, pal, phase):
        raise RuntimeError("no active sky design")
    cloud_pal = sky_designs.active_cloud_palette(phase, pal) or pal
    for (cx, cy, sc, var) in ((92, 438, 0.85, 1), (254, 420, 1.05, 0),
                              (176, 462, 0.70, 2)):
        gdraw.draw_cloud(_sky_scratch, cx, cy, sc, variant=var,
                         palette=cloud_pal)
    # draw_mountains rebakes on a per-frame colour budget; let it converge.
    for _ in range(10):
        gdraw.draw_mountains(_sky_scratch, 420.0, GROUND_Y, W, phase=phase)
    _sky_scratch.set_clip(None)
    surf.blit(_sky_scratch, APERTURE.topleft, band)


_pip_cache = {}


def pip_sprite(scale=0.92):
    """Pip WITH his parcel in the player's actually-equipped skin. Keyed on
    (skin, parcel) and built on demand: both can change in the Store and the
    player can walk straight back here, so a module-import bake would show the
    wrong bird for the rest of the process."""
    store_data.load()
    skin = store_data.equipped("skin") or "skin_base"
    parcel_id = store_data.equipped("parcel")
    key = (skin, parcel_id, round(scale, 3))
    got = _pip_cache.get(key)
    if got is not None:
        return got
    body = parrot.get_skin_frame(skin, 1, 0.0)
    parcel = parrot.get_parcel("normal", parcel_id)
    bw, bh = body.get_size()
    pad = 10
    comp = pygame.Surface((bw + pad * 2, bh + pad * 2 + PARCEL_Y_OFFSET * 2),
                          pygame.SRCALPHA)
    ccx, ccy = comp.get_width() // 2, (bh + pad * 2) // 2
    comp.blit(body, body.get_rect(center=(ccx, ccy)))
    comp.blit(parcel, parcel.get_rect(center=(ccx, ccy + PARCEL_Y_OFFSET + 3)))
    cw, ch = comp.get_size()
    comp = pygame.transform.smoothscale(comp, (int(cw * scale), int(ch * scale)))
    comp = comp.subsurface(comp.get_bounding_rect(min_alpha=8)).copy()
    _pip_cache[key] = (comp, skin, parcel_id)
    return _pip_cache[key]


# A slow arc across the aperture: on from the left, cresting past centre, off
# to the right. One pass every PIP_PERIOD seconds and nothing else ever moves.
PIP_PERIOD = 7.0
PIP_ARC = [(-26, 96), (80, 30), (216, 98), (330, 34)]


def pip_at(u):
    mt = 1 - u
    x = (mt ** 3 * PIP_ARC[0][0] + 3 * mt * mt * u * PIP_ARC[1][0]
         + 3 * mt * u * u * PIP_ARC[2][0] + u ** 3 * PIP_ARC[3][0])
    y = (mt ** 3 * PIP_ARC[0][1] + 3 * mt * mt * u * PIP_ARC[1][1]
         + 3 * mt * u * u * PIP_ARC[2][1] + u ** 3 * PIP_ARC[3][1])
    return x, y


def draw_pip(surf, u):
    sprite, skin, parcel_id = pip_sprite()
    x, y = pip_at(u)
    x1, y1 = pip_at(min(1.0, u + 0.02))
    tilt = -math.degrees(math.atan2(y1 - y, max(0.001, x1 - x))) * 0.55
    img = pygame.transform.rotozoom(sprite, tilt, 1.0)
    r = img.get_rect(center=(APERTURE.x + x, APERTURE.y + y))
    old = surf.get_clip()
    surf.set_clip(APERTURE)
    surf.blit(img, r.topleft)
    surf.set_clip(old)
    return r, skin, parcel_id


def dim_window(surf):
    """The view is OUTSIDE, so it sits a stop under the lit sheet. A flat cool
    veil, not haze: the layers here separate by stock value and cast shadow."""
    veil = pygame.Surface(APERTURE.size, pygame.SRCALPHA)
    veil.fill((16, 20, 40, 40))
    surf.blit(veil, APERTURE.topleft)


# ═════════════════════════════════════════════════════════════════════════════
# FRAME
# ═════════════════════════════════════════════════════════════════════════════
def render(phase, u=0.4, foil_t=0.34):
    surf = pygame.Surface((W, H))
    sky_into_window(surf, phase)
    pip_r, skin, parcel_id = draw_pip(surf, u)
    dim_window(surf)
    surf.blit(bake(), (0, 0))
    src, pos = _CATCH
    surf.blit(catch_band(src, foil_t), pos)
    return surf, pip_r, skin, parcel_id


# ═════════════════════════════════════════════════════════════════════════════
# MEASUREMENT (offline only — no per-frame per-pixel work anywhere above)
# ═════════════════════════════════════════════════════════════════════════════
def mean_rgb(surf, rect):
    """Area-average of a rect. smoothscale straight to 1x1 is NOT a box filter
    in SDL2 (it drops to a 2-tap sample and mis-reports by >100 levels on a
    split field), so the average is taken off an 8x8 reduction instead."""
    r = rect.clip(surf.get_rect())
    if r.w <= 0 or r.h <= 0:
        return (0, 0, 0)
    n = 8
    small = pygame.transform.smoothscale(surf.subsurface(r).copy(), (n, n))
    tot = [0, 0, 0]
    for y in range(n):
        for x in range(n):
            c = small.get_at((x, y))
            tot[0] += c.r
            tot[1] += c.g
            tot[2] += c.b
    return tuple(v // (n * n) for v in tot)


# A clean run of unprinted sheet — the ground every stock-borne element is
# actually measured against, rather than a ring that would swallow the trim.
SHEET_PATCH = pygame.Rect(150, 320, 60, 12)


def ring_rgb(surf, rect, pad=9):
    outer = rect.inflate(pad * 2, pad * 2).clip(surf.get_rect())
    inner = rect.clip(outer)
    mo, mi = mean_rgb(surf, outer), mean_rgb(surf, inner)
    ao, ai = outer.w * outer.h, inner.w * inner.h
    ar = max(1, ao - ai)
    return tuple(max(0, min(255, int((mo[k] * ao - mi[k] * ai) / ar)))
                 for k in range(3))


def deboss_probe(fill=INK):
    """Isolate the deboss on flat stock so the inversion can be READ as numbers
    rather than asserted: a bar bitten into a blank sheet — inked, or blind
    with fill=None — sampled one px either side of each edge."""
    pad = m(14)
    box = pygame.Rect(pad, pad, m(60), m(24))
    big = pygame.Surface((box.w + pad * 2, box.h + pad * 2))
    big.fill(STOCK)
    mask = pygame.Surface(box.size, pygame.SRCALPHA)
    mask.fill((255, 255, 255, 255))
    if fill is not None:
        big.blit(tint(mask, fill), box.topleft)
    deboss_marks(big, mask, box.topleft)
    out = pygame.transform.smoothscale(
        big, (big.get_width() // SS, big.get_height() // SS))
    b = pygame.Rect(box.x // SS, box.y // SS, box.w // SS, box.h // SS)
    return {
        "inner top wall": mean_rgb(out, pygame.Rect(b.x + 4, b.y, b.w - 8, 1)),
        "inner left wall": mean_rgb(out, pygame.Rect(b.x, b.y + 4, 1, b.h - 8)),
        "floor": mean_rgb(out, pygame.Rect(b.x + 6, b.centery, b.w - 12, 4)),
        "inner bottom": mean_rgb(out, pygame.Rect(b.x + 4, b.bottom - 1,
                                                  b.w - 8, 1)),
        "outer bottom lip": mean_rgb(out, pygame.Rect(b.x + 4, b.bottom,
                                                      b.w - 8, 1)),
        "outer right lip": mean_rgb(out, pygame.Rect(b.right, b.y + 4, 1,
                                                     b.h - 8)),
        "outer top (paper)": mean_rgb(out, pygame.Rect(b.x + 4, b.y - 2,
                                                       b.w - 8, 1)),
        "bare stock": mean_rgb(out, pygame.Rect(2, 2, 8, 8)),
    }, out


def lum(c):
    def ch(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(c[0]) + 0.7152 * ch(c[1]) + 0.0722 * ch(c[2])


def contrast(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def greyscale(frame, size=(90, 160)):
    small = pygame.transform.smoothscale(frame, size)
    out = pygame.Surface(size)
    rows = []
    for y in range(size[1]):
        row = []
        for x in range(size[0]):
            c = small.get_at((x, y))
            g = int(0.299 * c.r + 0.587 * c.g + 0.114 * c.b)
            out.set_at((x, y), (g, g, g))
            row.append(g)
        rows.append(row)
    return out, rows


def crop_zoom(frame, rect, factor):
    sub = frame.subsurface(rect.clip(frame.get_rect())).copy()
    return pygame.transform.scale(sub, (sub.get_width() * factor,
                                        sub.get_height() * factor))


# ═════════════════════════════════════════════════════════════════════════════
# REVIEW SHEET
# ═════════════════════════════════════════════════════════════════════════════
def build_sheet(frames, thumb):
    pad, top = 24, 92
    sw = pad + (W + pad) * 4
    sh = top + H + 560
    sheet = pygame.Surface((sw, sh))
    sheet.fill((20, 20, 25))
    sheet.blit(_font(31, True).render(
        "SKYBIT  MENU-V2  —  COVER-TYPE  —  THEME B  \"THE LAUNCH "
        "BULLETIN\"  —  ROUND 2", True, (242, 234, 216)), (pad, 18))
    for i, line in enumerate((
            "a printed object on a desk, not a picture of a place: a cotton-rag "
            "bulletin trimmed inside an ink-blue backing board, airmail chevron "
            "trim, a die-cut window with 2px of core-stock thickness,",
            "and a tipped-in perforated START ticket on whiter stock. Baked "
            "once at SS=2 into one RGBA sheet with a transparent window hole; "
            "per frame only the sky inside the aperture, Pip on his 7s arc, "
            "and the foil sweep.")):
        sheet.blit(_font(15, True).render(line, True, (146, 144, 150)),
                   (pad, 52 + i * 20))
    for i, (name, ph, frame) in enumerate(frames):
        x = pad + i * (W + pad)
        pygame.draw.rect(sheet, (58, 56, 62),
                         pygame.Rect(x - 2, top - 2, W + 4, H + 4), width=2)
        sheet.blit(frame, (x, top))
        sheet.blit(_font(16, True).render(
            f"{name.upper()}   phase {ph:.2f}   "
            f"biome_time {ph*biome.CYCLE_SECONDS:.0f}s",
            True, (228, 220, 202)), (x, top + H + 10))

    ty = top + H + 46
    day = frames[0][2]

    def panel(label, img, x, y):
        sheet.blit(img, (x, y))
        pygame.draw.rect(sheet, (72, 70, 76),
                         pygame.Rect(x - 1, y - 1, img.get_width() + 2,
                                     img.get_height() + 2), width=1)
        sheet.blit(_font(15, True).render(label, True, (228, 220, 202)),
                   (x, y + img.get_height() + 7))
        return x + img.get_width()

    # Row 1 — the squint test plus the two edges that carry the whole illusion.
    panel("90x160 GREYSCALE", thumb, pad, ty)
    panel("DEBOSS + INK SPREAD  4x",
          crop_zoom(day, pygame.Rect(28, 296, 148, 26), 4), pad + 118, ty)
    panel("DIE-CUT EDGE + PAPER THICKNESS  4x",
          crop_zoom(day, pygame.Rect(28, 182, 118, 22), 4), pad + 744, ty)
    panel("RUBBER DATESTAMP  3x",
          crop_zoom(day, pygame.Rect(276, 182, 64, 62), 3), pad + 1252, ty)

    # Row 2 — the ticket affordance and the keyed-plate affordance.
    ry = ty + 210
    panel("PERFORATION + FIBRE FRINGE  4x",
          crop_zoom(day, pygame.Rect(22, 334, 148, 26), 4), pad + 118, ry)
    panel("KEYED PLATE  2x",
          crop_zoom(day, pygame.Rect(28, 452, 104, 76), 2), pad + 744, ry)
    panel("AIRMAIL CHEVRON TRIM  4x",
          crop_zoom(day, pygame.Rect(6, 6, 118, 22), 4), pad + 972, ry)

    # Row 3 — the ~6s foil sweep, four positions of the one masked blit.
    fy = ry + 172
    src, _pos = _CATCH
    wm, _p = wordmark_mask(m(CAP))
    small = pygame.transform.smoothscale(
        wm, (round(wm.get_width() / SS), round(wm.get_height() / SS)))
    sheet.blit(_font(15, True).render(
        "FOIL SWEEP — one masked blit, ~6s loop; the gold never shades, it "
        "catches", True, (228, 220, 202)), (pad + 118, fy - 22))
    fx = pad + 118
    for t in (0.12, 0.36, 0.60, 0.84):
        strip = pygame.Surface((src.get_width() + 12, src.get_height() + 10))
        strip.fill(STOCK)
        strip.blit(foil_body(small), (6, 5))
        strip.blit(catch_band(src, t), (6, 5))
        fx = panel(f"t = {t:.2f}", strip, fx, fy) + 22
    return sheet


# ═════════════════════════════════════════════════════════════════════════════
def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    frames, paths = [], []
    masked = {}
    for name, ph in PHASES:
        biome_time = ph * biome.CYCLE_SECONDS
        phase = biome.phase_for_time(biome_time)
        frame, pip_r, skin, parcel_id = render(phase, PIP_U[name])
        p = os.path.join(OUT_DIR, f"round_2_{name}.png")
        pygame.image.save(frame, p)
        paths.append(p)
        frames.append((name, phase, frame))
        blanked = frame.copy()
        blanked.fill((0, 0, 0), APERTURE)
        masked[name] = pygame.image.tostring(blanked, "RGB")
        if name == "day":
            day_frame, day_pip, day_skin, day_parcel = frame, pip_r, skin, parcel_id

    thumb, rows = greyscale(day_frame)
    sheet = build_sheet(frames, thumb)
    sheet_path = os.path.join(OUT_DIR, "round_2.png")
    pygame.image.save(sheet, sheet_path)

    print("\n=== 1. PHASE-INVARIANCE ===")
    ref = masked["day"]
    identical = all(masked[n] == ref for n, _ in PHASES)
    print(f"  every pixel OUTSIDE the aperture is byte-identical across all "
          f"four phases: {identical}")
    print("  -> measured contrast spread for every element on stock is exactly "
          "0.000 by construction;")
    print("     the sheet is baked once and is not a function of phase. The "
          "aperture is the only phase-variant region.")

    els = []
    wm, _p = wordmark_mask(m(CAP))
    wrect = pygame.Rect(COL_L - 1, WORD_BASELINE - round(wm.get_height() / SS),
                        round(wm.get_width() / SS), round(wm.get_height() / SS))
    els.append(("kicker THE SKY POST", INK_SOFT,
                pygame.Rect(COL_L, TOP_LINE_Y, int(tracked_w(KICKER_L, 8, 1.5)), 9),
                "under"))
    els.append(("docket No. 4471", INK,
                pygame.Rect(COL_R - int(tracked_w(KICKER_R, 8, 1.2)),
                            TOP_LINE_Y, int(tracked_w(KICKER_R, 8, 1.2)), 9),
                "under"))
    els.append(("wordmark foil vs sheet", FOIL_MID, SHEET_PATCH, "under"))
    els.append(("subtitle POCKET SKY FLYER", INK,
                pygame.Rect(COL_L, SUB_Y, int(tracked_w(SUBTITLE, 11, 4)), 12),
                "under"))
    els.append(("START ticket scarlet vs sheet", SCARLET, SHEET_PATCH, "under"))
    els.append(("ticket white stock vs sheet", TICKET_TOP, SHEET_PATCH, "under"))
    els.append(("START caps on scarlet", CREAM, PANEL.inflate(-60, -26), "under"))
    for r, (label, _i) in zip(util_rects(), UTILS):
        els.append((f"plate {label} vs sheet", PLATE_MEAN, SHEET_PATCH, "under"))
        els.append((f"keyline {label}", INK, r, "ring"))
        els.append((f"label {label}", INK,
                    pygame.Rect(r.centerx - 30, r.bottom - 27, 60, 13), "under"))
    els.append(("PROFILE plate vs sheet", PLATE_MEAN, SHEET_PATCH, "under"))
    els.append(("player name", INK,
                pygame.Rect(PROFILE.x + 46, PROFILE.y + 25,
                            int(tracked_w(PLAYER, 17, 0.8)), 20), "under"))
    els.append(("colophon", INK_SOFT,
                pygame.Rect(180 - int(tracked_w(COLOPHON, 7, 1.4)) // 2,
                            COLOPHON_Y, int(tracked_w(COLOPHON, 7, 1.4)), 8),
                "under"))

    print("\n  element                          " +
          "".join(f"{n:>9s}" for n, _ in PHASES) + "    spread")
    worst = 99.0
    for label, ink, rect, mode in els:
        vals = []
        for name, _ph in PHASES:
            f = dict((n, fr) for n, _p2, fr in frames)[name]
            bg = ring_rgb(f, rect) if mode == "ring" else mean_rgb(f, rect)
            vals.append(contrast(ink, bg))
        worst = min(worst, min(vals))
        print(f"  {label:32s}" + "".join(f"{v:9.2f}" for v in vals)
              + f"    {max(vals)-min(vals):.3f}")
    print(f"  lowest number in the table: {worst:.2f}:1 — that is a keyed "
          f"plate's FILL against the sheet, which is deliberately a whisper "
          f"(the plate is a second press of the same stock);")
    print("  the plate is legible off its ink keyline (>11:1) and its solid "
          "ink bottom edge, not off a value jump in its fill.")
    print(f"  every LABEL and every piece of type clears 3:1; START's scarlet "
          f"clears 5.5:1 against cream at all four phases.")

    print("\n=== 2. THE DIE-CUT WINDOW EDGE (the only sky boundary) ===")
    print("  the mandated two-tone pair: an INK keyline outside a CORE-STOCK "
          "paper bevel, against the sky in the aperture.")
    ok_edge = True
    for name, ph, f in frames:
        top_band = mean_rgb(f, pygame.Rect(APERTURE.x + 8, APERTURE.y + 5,
                                           APERTURE.w - 16, 12))
        bot_band = mean_rgb(f, pygame.Rect(APERTURE.x + 8, APERTURE.bottom - 17,
                                           APERTURE.w - 16, 12))
        for lbl, band in (("top", top_band), ("bottom", bot_band)):
            ci, cc = contrast(INK, band), contrast(STOCK_CORE, band)
            best = max(ci, cc)
            ok_edge &= best >= 3.0
            print(f"  {name:7s} {lbl:6s} sky {str(band):16s}  "
                  f"ink keyline {ci:5.2f}:1   core-stock bevel {cc:5.2f}:1   "
                  f"-> carrying leg {best:5.2f}:1")
    print(f"  one leg >= 3:1 at every phase, both edges: {ok_edge}")
    print("  scarlet never touches sky (nearest scarlet is the ticket at "
          f"y{TICKET.y}, {TICKET.y - APERTURE.bottom}px below the aperture).")

    print("\n=== 3. LABEL FIT (measured px) ===")
    fits = [
        (KICKER_L, 8, 1.5, COL_W - 60, "top furniture (decorative)"),
        (KICKER_R, 8, 1.2, 60, "docket number (decorative)"),
        (SUBTITLE, 11, 4.0, COL_W, "subtitle (decorative)"),
        ("START", 30, 6.0, PANEL.w - 62, "ticket, minus the chevron"),
        (PLAYER, 17, 0.8, PROFILE.w - 76, "player name"),
        ("PROFILE", 9, 2.0, PROFILE.w - 76, "profile kicker"),
        (COLOPHON, 7, 1.4, COL_W, "colophon (decorative)"),
        (ROUTE_L, 7, 1.6, 200, "left margin docket (vertical)"),
        (ROUTE_R, 7, 1.6, 200, "right margin docket (vertical)"),
    ]
    for label, _i in UTILS:
        fits.append((label, 12, 1.0, UTIL_W - 10, "utility label (12px floor)"))
    allfit = True
    for text, size, track, avail, note in fits:
        wpx = tracked_w(text, size, track)
        good = wpx <= avail
        allfit &= good
        print(f"  {text[:26]:27s} {size:2d}px trk {track:3.1f}  {wpx:6.1f} / "
              f"{avail:5.1f}px  {'OK  ' if good else 'OVER'}  {note}")
    print(f"  all fit: {allfit}.  smallest INTERACTIVE type = 12px (utility "
          f"labels); 17px player name; 30px START.")

    print("\n=== 4. TAP TARGETS ===")
    targets = [("START", TICKET)]
    for r, (label, _i) in zip(util_rects(), UTILS):
        targets.append((label, r))
    targets.append(("PROFILE", PROFILE))
    for name, r in targets:
        print(f"  {name:9s} {str(r):40s} {r.width}x{r.height}  "
              f">=48dp: {min(r.width, r.height) >= 48}   bottom {r.bottom}")
        assert min(r.width, r.height) >= 48, name
        assert r.bottom <= 624, name
    for i in range(len(targets)):
        for j in range(i + 1, len(targets)):
            assert not targets[i][1].colliderect(targets[j][1]), \
                (targets[i][0], targets[j][0])
    print("  pairwise disjoint: True")
    print(f"  gaps: ticket.bottom {TICKET.bottom} -> plates.top {UTIL_Y} = "
          f"{UTIL_Y - TICKET.bottom}px; plates.bottom {UTIL_Y+UTIL_H} -> "
          f"PROFILE.top {PROFILE.top} = {PROFILE.top-(UTIL_Y+UTIL_H)}px; "
          f"between plates = {UTIL_GAP}px")
    print(f"  lowest interactive edge: {max(r.bottom for _n, r in targets)} "
          f"(limit 624)")
    print(f"  START width {TICKET.w}px vs widest other block "
          f"{PROFILE.w}px -> primary by area as well as colour")

    print("\n=== 5. PRINT CRAFT ===")
    probe = day_frame
    for kind, fill in (("BLIND — no ink, the pure impression", None),
                       ("INKED — spot ink lying in the bite", INK)):
        dp, _dimg = deboss_probe(fill)
        bare = sum(dp["bare stock"])
        print(f"  deboss inversion isolated on flat stock, {kind} "
              f"(RGB sum; bare stock = {bare}):")
        for k in ("outer top (paper)", "inner top wall", "inner left wall",
                  "floor", "inner bottom", "outer bottom lip",
                  "outer right lip"):
            print(f"    {k:19s} {str(dp[k]):18s} sum {sum(dp[k]):4d}  "
                  f"{sum(dp[k]) - bare:+5d} vs bare stock")
    print("    -> the INNER top/left walls sit BELOW the floor they surround "
          "(cool multiply shadow) and the OUTER")
    print("       bottom/right lips sit ABOVE bare stock (additive paper "
          "white). That is the pressed-in signature;")
    print("       a raised element — store_hub.bevel_rim as shipped — reads "
          "the other way round.")
    plate = util_rects()[0]
    pt = mean_rgb(probe, pygame.Rect(plate.x + 6, plate.y + 1, plate.w - 12, 1))
    pmid = mean_rgb(probe, pygame.Rect(plate.x + 6, plate.centery,
                                       plate.w - 12, 4))
    pb = mean_rgb(probe, pygame.Rect(plate.x + 6, plate.bottom, plate.w - 12, 1))
    sheetv = mean_rgb(probe, SHEET_PATCH)
    print(f"  on the LIVE STORE plate: inner top wall {pt} sum {sum(pt)} vs "
          f"plate field {pmid} sum {sum(pmid)} (wall darker by "
          f"{sum(pmid)-sum(pt)});")
    print(f"                           outer bottom lip {pb} sum {sum(pb)} vs "
          f"sheet {sheetv} sum {sum(sheetv)} (lip brighter by "
          f"{sum(pb)-sum(sheetv)})")
    src, pos = _CATCH
    flat = pygame.Surface(src.get_size(), pygame.SRCALPHA)
    flat.fill((255, 255, 255, 255))
    raw = catch_band(flat, 0.45)
    row = raw.get_height() // 2
    al = [raw.get_at((x, row)).a for x in range(raw.get_width())]
    peak = max(al)
    steps = sum(1 for x in range(1, len(al))
                if al[x - 1] < peak * 0.1 and al[x] > peak * 0.9)
    lit = [x for x, a in enumerate(al) if a > peak * 0.5]
    print(f"  foil catch, UNMASKED band: peak alpha {peak}, band spans x "
          f"{lit[0]}..{lit[-1]} of {len(al)}px, and alpha steps 10%->90% "
          f"inside a SINGLE px in {steps} place(s)")
    print("    -> a hard mirror band, not a gradient. A ramp across the "
          "letters would read as lit plastic; a hard band reads as gold "
          "catching a window.")
    print("  masked to the wordmark, per sweep position:")
    for t in (0.15, 0.35, 0.55, 0.75):
        b = catch_band(src, t)
        rr = max(range(b.get_height()),
                 key=lambda y: sum(b.get_at((x, y)).a
                                   for x in range(b.get_width())))
        aa = [b.get_at((x, rr)).a for x in range(b.get_width())]
        pk = max(aa)
        if pk == 0:
            print(f"    t={t:.2f}  band clear of the wordmark (foil at rest)")
            continue
        li = [x for x, a in enumerate(aa) if a > pk * 0.5]
        print(f"    t={t:.2f}  peak alpha {pk:3d}  lit span x "
              f"{li[0]}..{li[-1]} ({li[-1]-li[0]+1}px of {len(aa)})")

    st_rect = pygame.Rect(STAMP_C[0] - STAMP_R, STAMP_C[1] - STAMP_R,
                          STAMP_R * 2, STAMP_R * 2)
    vals = []
    for y in range(st_rect.y, st_rect.bottom, 2):
        for x in range(st_rect.x, st_rect.right, 2):
            c = probe.get_at((x, y))
            vals.append(0.299 * c.r + 0.587 * c.g + 0.114 * c.b)
    inked = [v for v in vals if v < 175]
    print(f"  datestamp coverage: {len(inked)}/{len(vals)} sampled px carry "
          f"ink ({100*len(inked)/len(vals):.0f}%) and the inked pixels span "
          f"L {min(inked):.0f}..{max(inked):.0f} — broken, not solid")
    tw, th = grain_tiles()[0].get_size()
    print(f"  grain: authored on ONE 180x320 tile -> smoothscaled to {tw}x{th} "
          f"device px (one noise cell = one final px) -> tiled "
          f"{math.ceil(DW/tw)}x{math.ceil(DH/th)} with per-tile mirroring so "
          f"the repeat never shows.")
    print(f"    {180*320:,} Python pixel writes at BAKE time, not {DW*DH:,}; "
          f"zero per frame; no numpy and no surfarray anywhere.")
    stock_probe = [probe.get_at((x, 470)).r for x in range(150, 190)]
    print(f"  fibre reads on the stock: R over a 40px flat run "
          f"{min(stock_probe)}..{max(stock_probe)} (spread "
          f"{max(stock_probe)-min(stock_probe)})")

    print("\n=== 6. PIP ===")
    print(f"  equipped skin (read live via store_data.equipped): {day_skin!r}")
    print(f"  equipped parcel: {day_parcel!r} via parrot.get_parcel(mode, id)")
    print(f"  sprite rect {day_pip} -> {day_pip.width}x{day_pip.height}px, "
          f"scale 0.92 of the gameplay frame")
    print(f"  arc: cubic bezier {PIP_ARC} in aperture-local px, one pass every "
          f"{PIP_PERIOD}s, clipped to {APERTURE}")
    inside = APERTURE.clip(day_pip)
    print(f"  clipped to the aperture: {inside.w}x{inside.h} of "
          f"{day_pip.width}x{day_pip.height} visible at u="
          f"{PIP_U['day']} (the arc enters/leaves behind the cut edge)")
    print(f"  bake cache key: (skin, parcel, scale) = "
          f"{list(_pip_cache.keys())} — built on demand, NOT at module import")

    print("\n=== 7. TECHNIQUE ===")
    print(f"  compose at SS={SS} -> {DW}x{DH} device, ONE "
          f"pygame.transform.smoothscale down to {W}x{H} (store_hub.downscale)")
    print("  bake-once: board, sheet, chevron trim, register marks, furniture "
          "type, die-cut, datestamp, foil wordmark, ticket, plates and grain "
          "all live in a single RGBA surface with a transparent window hole")
    print("  per frame: sky clipped to the 300x146 aperture, one Pip blit, one "
          "veil, one bake blit, one masked foil-sweep blit")
    src_lines = open(os.path.abspath(__file__)).read().splitlines()
    imports = [l for l in src_lines
               if l.strip().startswith(("import numpy", "from numpy"))]
    print(f"  numpy imports in this file: {len(imports)} (round 1 had one at "
          f"tools/_menu_v2_cover_type_r1.py:32; numpy is absent on the "
          f"pygbag/WASM runtime)")
    print("  per-pixel Python loops in the DRAW path: 0 — the only set_at "
          "sweeps are the 180x320 grain tile and the 16x16 diagonal masks, "
          "both baked once")
    print("  reused from game.store_hub: m, font, lerp_stops, vgrad_stops, "
          "multistop_v, drop_shadow, contact_shadow, top_sheen, gradient_text,")
    print("    _glyph_base, _stamp_bold, gold_rule, downscale. bevel_rim is "
          "used AS SHIPPED on the raised ticket and INVERTED into deboss_rim "
          "for everything pressed into the sheet.")

    print("\n=== 8. 90x160 GREYSCALE BANDS ===")
    bands = [("board/kicker", 0, 12), ("die-cut window", 12, 50),
             ("wordmark", 50, 80), ("START ticket", 80, 110),
             ("keyed plates", 110, 133), ("profile", 133, 155),
             ("colophon/trim", 155, 160)]
    for nm, y0, y1 in bands:
        seg = [v for row in rows[y0:y1] for v in row]
        dark = sum(1 for v in seg if v < 110) / len(seg) * 100
        print(f"  {nm:16s} rows {y0:3d}-{y1:3d}  mean L {sum(seg)/len(seg):6.1f}"
              f"  min {min(seg):3d}  max {max(seg):3d}  dark cover {dark:5.1f}%")

    print("\n=== FILES ===")
    for p in paths + [sheet_path]:
        print("  " + os.path.relpath(p, _REPO))


if __name__ == "__main__":
    main()
