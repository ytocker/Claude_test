"""cover-type — main-menu concept round 1 (menu-v2).

Standalone review renderer. Touches nothing under game/; it only READS the
live modules (sky_designs / biome / draw / parrot / store_data) so the mockup
uses the same art the shipped build would.

The thesis: the menu is a printed travel poster, not a screen. The whole canvas
is opaque printed stock and the sky is visible ONLY through a cut window in the
upper third, so every element sits on ground it owns and is phase-proof by
construction. SKYBIT is drawn as custom geometric caps rather than set in the
UI face — the wordmark is the artwork here, and a stock-font title is the one
thing that would give the poster away.

Run headless:
    SDL_VIDEODRIVER=dummy python3 tools/_menu_v2_cover_type_r1.py
"""
import os
import sys
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import pygame  # noqa: E402

pygame.init()
pygame.font.init()
pygame.display.set_mode((360, 640))

import numpy as np  # noqa: E402

from game.config import W, H, GROUND_Y, PARCEL_Y_OFFSET  # noqa: E402
from game import biome, sky_designs, draw as gdraw, parrot, store_data  # noqa: E402
from game.hud import _font  # noqa: E402


OUT_DIR = os.path.join(_REPO, "docs", "menu-v2", "cover-type")

# ── printed-stock palette ────────────────────────────────────────────────────
# Cream stock rather than ink stock: the light ground is the only value key in
# the whole menu round that isn't a sky value, so the concept separates at a
# squint; it also lets the single scarlet element read as the loudest thing on
# the page without any glow.
STOCK      = (240, 231, 211)
STOCK_DEEP = (215, 200, 172)   # utility plates — a second press of the same ink
INK        = (26, 28, 38)
INK_SOFT   = (72, 70, 76)
SCARLET    = (166, 30, 26)
CREAM      = (247, 240, 224)

MARGIN_L = 28
COL_R = 332
COL_W = COL_R - MARGIN_L

WINDOW = pygame.Rect(MARGIN_L, 40, COL_W, 132)
CAP = 72                       # wordmark cap height in px
WORD_BASELINE = 264
RULE_Y = 282
RULE_R = 196
SUB_TOP = 294
START_RECT = pygame.Rect(MARGIN_L, 400, COL_W, 68)
UTIL_Y, UTIL_H, UTIL_W, UTIL_GAP = 490, 68, 96, 8
PROFILE_RECT = pygame.Rect(MARGIN_L, 574, COL_W, 48)

PHASES = [("day", 0.12), ("golden", 0.27), ("plum", 0.47), ("night", 0.70)]


# ── custom geometric caps ────────────────────────────────────────────────────
# Drawn as filled shapes at 4x and downsampled, so the wordmark gets real
# anti-aliasing and can carry proportions the UI face can't: wide bowls, a
# 0.20 cap stem against 0.155 horizontals, and flat-cut diagonal terminals.
SS = 4
STEM = 0.200      # vertical stroke, in cap units
THIN = 0.155      # horizontal stroke — thinner so bowls keep open counters
PAD = 0.06        # room for round-letter overshoot

GLYPH_W = {"S": 0.68, "K": 0.70, "Y": 0.70, "B": 0.66, "I": 0.20, "T": 0.66}
OVERSHOOT = 0.012


class _Pen:
    """Draws one glyph in cap units (y up from the baseline) onto a 4x mask."""

    def __init__(self, width_units):
        self.wu = width_units
        self.w = int(round(width_units * CAP * SS))
        self.h = int(round((1.0 + PAD * 2) * CAP * SS))
        self.base = (1.0 + PAD) * CAP * SS
        self.surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)

    def px(self, x, y):
        return (x * CAP * SS, self.base - y * CAP * SS)

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
                                        round(2 * rx * CAP * SS),
                                        round(2 * ry * CAP * SS)))

    def poly(self, pts, target=None):
        t = self.surf if target is None else target
        pygame.draw.polygon(t, (255, 255, 255, 255),
                            [self.px(x, y) for x, y in pts])

    def cut_ellipse(self, cx, cy, rx, ry, clip_x=None):
        s = self._scratch()
        if clip_x is not None:
            s.set_clip(pygame.Rect(round(clip_x * CAP * SS), 0, self.w, self.h))
        self.ellipse(cx, cy, rx, ry, target=s)
        s.set_clip(None)
        self._cut(s)

    def cut_wedge(self, cx, cy, a0, a1, r):
        """Remove the pie slice from a0 to a1 (degrees, CCW, 0 = right).
        The radius is kept just past the ring being cut so the slice can't
        reach across the glyph and eat a stroke it was never aimed at."""
        s = self._scratch()
        pts = [(cx, cy)]
        n = 72
        for i in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        self.poly(pts, target=s)
        self._cut(s)

    def diagonal(self, p0, p1, hh):
        """A diagonal stroke offset horizontally, so ends clipped by the cap
        line / baseline come out flat-cut the way a geometric face cuts them."""
        (x0, y0), (x1, y1) = p0, p1
        self.poly([(x0 - hh, y0), (x1 - hh, y1), (x1 + hh, y1), (x0 + hh, y0)])

    def trim(self, x0=None, y_top=None, y_bot=None):
        """Flat-cut whatever a diagonal threw past the cap line, the baseline
        or the right sidebearing — the overshoot is only there so the cut lands
        square instead of on the polygon's own mitre."""
        s = self._scratch()
        if y_top is not None:
            self.rect(-0.4, y_top, self.wu + 0.4, y_top + 0.6, target=s)
        if y_bot is not None:
            self.rect(-0.4, y_bot - 0.6, self.wu + 0.4, y_bot, target=s)
        if x0 is not None:
            self.rect(x0, -0.6, x0 + 0.6, 1.6, target=s)
        self._cut(s)

    def branch(self):
        """A same-geometry mask to build one stroke group in isolation, so its
        own cuts can't reach the strokes already laid down."""
        return _Pen(self.wu)

    def merge(self, other):
        self.surf.blit(other.surf, (0, 0))

    def finish(self):
        out_w = max(1, int(round(self.wu * CAP)))
        out_h = max(1, int(round((1.0 + PAD * 2) * CAP)))
        return pygame.transform.smoothscale(self.surf, (out_w, out_h))


def _glyph_S(p):
    # Two rings whose horizontal strokes overlap into a single spine; the
    # openings are radial cuts, which land near-vertical at both terminals.
    # Each ring is built on its own mask, then unioned — otherwise one ring's
    # opening would bite a hole in the other's arc.
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
_GLYPH_CACHE = {}


def glyph(ch):
    g = _GLYPH_CACHE.get(ch)
    if g is None:
        p = _Pen(GLYPH_W[ch])
        _BUILDERS[ch](p)
        g = p.finish()
        _GLYPH_CACHE[ch] = g
    return g


# Optical pairs. Y|B and I|T open a hole under the arm / crossbar, so they
# close up; K|Y interlocks at the cap line and needs air.
KERN = {("S", "K"): -1, ("K", "Y"): 2, ("Y", "B"): -2,
        ("B", "I"): -1, ("I", "T"): -2}
TRACK = 6.4


def ink_bbox(surf):
    a = pygame.surfarray.array_alpha(surf)
    cols = np.nonzero(a.max(axis=1) > 24)[0]
    rows = np.nonzero(a.max(axis=0) > 24)[0]
    if not len(cols) or not len(rows):
        return None
    return (int(cols[0]), int(rows[0]), int(cols[-1]) + 1, int(rows[-1]) + 1)


def wordmark(text="SKYBIT", color=INK):
    """Return (surface, baseline_offset, advances) for the set wordmark."""
    parts, x = [], 0.0
    prev = None
    for ch in text:
        g = glyph(ch)
        bb = ink_bbox(g)
        if prev is not None:
            x += TRACK + KERN.get((prev, ch), 0)
        parts.append((ch, g, bb, x))
        x += bb[2] - bb[0]
        prev = ch
    total = int(math.ceil(x))
    surf = pygame.Surface((total + 4, glyph("S").get_height()), pygame.SRCALPHA)
    for _ch, g, bb, gx in parts:
        surf.blit(g, (round(gx - bb[0]), 0))
    tinted = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    tinted.fill((*color, 255))
    tinted.blit(surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    baseline = (1.0 + PAD) * CAP
    return tinted, baseline, parts


# ── printed stock ────────────────────────────────────────────────────────────
_paper = None


def paper():
    """Bake the stock once: fibre speckle + a faint press vignette. Baked, not
    per-frame, so the noise never costs anything at draw time."""
    global _paper
    if _paper is not None:
        return _paper
    rng = np.random.default_rng(7)
    base = np.zeros((W, H, 3), dtype=np.float32)
    base[:, :] = STOCK
    grain = rng.normal(0.0, 3.1, (W, H, 1)).astype(np.float32)
    fibre = (rng.random((W, H, 1)) > 0.9965).astype(np.float32) * -26.0
    yy = np.linspace(-1.0, 1.0, H, dtype=np.float32)[None, :, None]
    xx = np.linspace(-1.0, 1.0, W, dtype=np.float32)[:, None, None]
    vignette = -9.0 * np.clip((xx * xx * 0.55 + yy * yy * 0.75), 0.0, 1.0)
    arr = np.clip(base + grain + fibre + vignette, 0, 255).astype(np.uint8)
    surf = pygame.Surface((W, H))
    pygame.surfarray.blit_array(surf, arr)
    _paper = surf
    return surf


# ── the view through the cut window ──────────────────────────────────────────
def world_plate(phase):
    """Sky + mountains + clouds for one phase, straight from the live modules."""
    plate = pygame.Surface((W, H))
    pal = biome.palette_for_phase(phase)
    if not sky_designs.render_active(plate, W, H, GROUND_Y, pal, phase):
        raise RuntimeError("no active sky design")
    cloud_pal = sky_designs.active_cloud_palette(phase, pal) or pal
    for (cx, cy, sc, var) in ((92, 396, 0.85, 1), (250, 378, 1.05, 0),
                              (170, 414, 0.7, 2)):
        gdraw.draw_cloud(plate, cx, cy, sc, variant=var, palette=cloud_pal)
    # Mountains rebake on a per-frame colour budget, so let it converge.
    for _ in range(10):
        gdraw.draw_mountains(plate, 420.0, GROUND_Y, W, phase=phase)
    return plate


# The crop lands the ridge crest ~70% down the aperture, so the window reads as
# a landscape view rather than a swatch of flat sky.
CROP_TOP = 362


def draw_window(surf, phase):
    plate = world_plate(phase)
    view = plate.subsurface(pygame.Rect(0, CROP_TOP, W, WINDOW.height)).copy()
    surf.blit(view, WINDOW.topleft,
              pygame.Rect(WINDOW.x, 0, WINDOW.width, WINDOW.height))
    # Paper thickness: the cut edge shades the view along the top and left.
    sh = pygame.Surface(WINDOW.size, pygame.SRCALPHA)
    for i in range(9):
        a = int(52 * (1 - i / 9.0) ** 2)
        pygame.draw.line(sh, (*INK, a), (0, i), (WINDOW.width, i))
        pygame.draw.line(sh, (*INK, a), (i, 0), (i, WINDOW.height))
    surf.blit(sh, WINDOW.topleft)
    pygame.draw.rect(surf, INK, WINDOW.inflate(6, 6), width=3)


# ── small type ───────────────────────────────────────────────────────────────
def tracked(surf, text, pos, size, color, track=0, anchor="left", alpha=255):
    f = _font(size, True)
    imgs = [f.render(c, True, color) for c in text]
    widths = [im.get_width() for im in imgs]
    total = sum(widths) + track * (len(text) - 1)
    x, y = pos
    if anchor == "center":
        x -= total // 2
    elif anchor == "right":
        x -= total
    if alpha < 255:
        strip = pygame.Surface((max(1, total), f.get_height()), pygame.SRCALPHA)
        cx = 0
        for im, wdt in zip(imgs, widths):
            strip.blit(im, (cx, 0))
            cx += wdt + track
        strip.set_alpha(alpha)
        surf.blit(strip, (x, y))
    else:
        for im, wdt in zip(imgs, widths):
            surf.blit(im, (x, y))
            x += wdt + track
    return pygame.Rect(pos[0] if anchor == "left" else x, y, total, f.get_height())


def tracked_w(text, size, track=0):
    f = _font(size, True)
    return sum(f.size(c)[0] for c in text) + track * (len(text) - 1)


# ── utility icons (ink line art, poster-flat) ────────────────────────────────
def icon_bag(surf, cx, cy, s=1.0):
    w, h = int(20 * s), int(17 * s)
    body = pygame.Rect(cx - w // 2, cy - h // 2 + 3, w, h)
    pygame.draw.rect(surf, INK, body, width=3, border_radius=2)
    pygame.draw.arc(surf, INK, pygame.Rect(cx - 7, body.top - 8, 14, 16),
                    0.15, math.pi - 0.15, 3)


def icon_trophy(surf, cx, cy):
    cup = [(cx - 9, cy - 9), (cx + 9, cy - 9), (cx + 7, cy + 1),
           (cx + 3, cy + 5), (cx - 3, cy + 5), (cx - 7, cy + 1)]
    pygame.draw.polygon(surf, INK, cup)
    pygame.draw.arc(surf, INK, pygame.Rect(cx + 6, cy - 9, 11, 12),
                    -1.35, 1.25, 3)
    pygame.draw.arc(surf, INK, pygame.Rect(cx - 17, cy - 9, 11, 12),
                    math.pi - 1.25, math.pi + 1.35, 3)
    pygame.draw.rect(surf, INK, pygame.Rect(cx - 2, cy + 4, 4, 4))
    pygame.draw.rect(surf, INK, pygame.Rect(cx - 8, cy + 8, 16, 4),
                     border_radius=1)


def icon_gear(surf, cx, cy):
    r_out, r_in = 10, 6.6
    for i in range(8):
        a = math.radians(i * 45)
        pts = []
        for k in (-0.30, 0.30):
            for rr in (r_in - 1, r_out + 1.5):
                pts.append((cx + rr * math.cos(a + k), cy + rr * math.sin(a + k)))
        pygame.draw.polygon(surf, INK, [pts[0], pts[1], pts[3], pts[2]])
    pygame.draw.circle(surf, INK, (cx, cy), int(r_in + 1.6))
    pygame.draw.circle(surf, STOCK_DEEP, (cx, cy), 4)


# ── Pip ──────────────────────────────────────────────────────────────────────
PIP_CENTER = (262, 348)
PIP_TILT = -30.0
PIP_SCALE = 1.32
# A hero pose, not a gameplay frame: the parcel drops a few px further than the
# in-game offset so the thing he is delivering is legible at rest.
PARCEL_HERO_DROP = 6


def pip_sprite():
    """Pip mid-dive WITH his parcel, in the player's actually-equipped skin."""
    store_data.load()
    skin = store_data.equipped("skin") or "skin_base"
    parcel_id = store_data.equipped("parcel")
    body = parrot.get_skin_frame(skin, 1, 0.0)
    parcel = parrot.get_parcel("normal", parcel_id)
    bw, bh = body.get_size()
    pad = 14
    comp = pygame.Surface((bw + pad * 2, bh + pad * 2 + PARCEL_Y_OFFSET * 2),
                          pygame.SRCALPHA)
    ccx, ccy = comp.get_width() // 2, (bh + pad * 2) // 2
    comp.blit(body, body.get_rect(center=(ccx, ccy)))
    comp.blit(parcel, parcel.get_rect(
        center=(ccx, ccy + PARCEL_Y_OFFSET + PARCEL_HERO_DROP)))
    rot = pygame.transform.rotate(comp, PIP_TILT)
    rw, rh = rot.get_size()
    big = pygame.transform.smoothscale(
        rot, (int(rw * PIP_SCALE), int(rh * PIP_SCALE)))
    # Trim the rotation padding so the published rect is Pip's real ink, not a
    # transparent box that would misreport his size and his clearance.
    bb = ink_bbox(big)
    return big.subsurface(pygame.Rect(bb[0], bb[1], bb[2] - bb[0],
                                      bb[3] - bb[1])).copy(), skin, parcel_id


def draw_pip(surf):
    sprite, skin, parcel_id = pip_sprite()
    r = sprite.get_rect(center=PIP_CENTER)
    # A flat offset shadow, not a glow: the poster is a print, so Pip drops the
    # kind of shadow a second ink pass would give him.
    sh = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
    sh.fill((*INK, 255))
    sh.blit(sprite, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    sh.set_alpha(46)
    surf.blit(sh, (r.x + 5, r.y + 6))
    surf.blit(sprite, r.topleft)
    return r, skin, parcel_id


TRAIL = [(232, 328), (186, 378), (108, 368), (64, 320)]


def draw_trail(surf):
    """The only curve on the page: one hairline arc from Pip's tail back
    toward the type."""
    s = 3
    layer = pygame.Surface((W * s, H * s), pygame.SRCALPHA)
    pts = []
    for i in range(65):
        t = i / 64.0
        mt = 1 - t
        x = (mt ** 3 * TRAIL[0][0] + 3 * mt * mt * t * TRAIL[1][0]
             + 3 * mt * t * t * TRAIL[2][0] + t ** 3 * TRAIL[3][0])
        y = (mt ** 3 * TRAIL[0][1] + 3 * mt * mt * t * TRAIL[1][1]
             + 3 * mt * t * t * TRAIL[2][1] + t ** 3 * TRAIL[3][1])
        pts.append((x * s, y * s))
    pygame.draw.lines(layer, SCARLET, False, pts, 7)
    pygame.draw.circle(layer, SCARLET, (int(pts[-1][0]), int(pts[-1][1])), 8)
    surf.blit(pygame.transform.smoothscale(layer, (W, H)), (0, 0))


# ── the menu ─────────────────────────────────────────────────────────────────
KICKER = "AIR PARCEL SERVICE"
SUBTITLE = "POCKET SKY FLYER"
PLAYER = "YTOCKER"
UTILS = (("STORE", icon_bag), ("TOP 10", icon_trophy), ("SETTINGS", icon_gear))


def util_rects():
    return [pygame.Rect(MARGIN_L + i * (UTIL_W + UTIL_GAP), UTIL_Y,
                        UTIL_W, UTIL_H) for i in range(3)]


def render(phase, bg_only=False):
    surf = paper().copy()
    tracked(surf, KICKER, (MARGIN_L, 18), 10, INK_SOFT, track=3)
    draw_window(surf, phase)
    if bg_only:
        # Same ground, no ink: lets the contrast pass sample what each element
        # actually sits on instead of assuming a flat colour.
        pygame.draw.rect(surf, SCARLET, START_RECT)
        for r in util_rects():
            pygame.draw.rect(surf, STOCK_DEEP, r, border_radius=2)
        return surf

    wm, base_off, _parts = wordmark("SKYBIT", INK)
    bb = ink_bbox(wm)
    # Optical alignment: S is a round left extremum, so it hangs a hair past
    # the margin the flat stems sit on.
    wx = MARGIN_L - 1 - bb[0]
    surf.blit(wm, (wx, WORD_BASELINE - int(base_off)))

    pygame.draw.rect(surf, INK, pygame.Rect(MARGIN_L, RULE_Y,
                                            RULE_R - MARGIN_L, 2))
    tracked(surf, SUBTITLE, (MARGIN_L, SUB_TOP), 11, INK, track=4)

    draw_trail(surf)
    pip_r, skin, parcel_id = draw_pip(surf)

    pygame.draw.rect(surf, SCARLET, START_RECT)
    tracked(surf, "START", (START_RECT.centerx, START_RECT.centery - 15),
            27, CREAM, track=5, anchor="center")
    cx, cy = START_RECT.right - 26, START_RECT.centery
    pygame.draw.lines(surf, CREAM, False,
                      [(cx - 5, cy - 8), (cx + 4, cy), (cx - 5, cy + 8)], 3)

    for r, (label, icon) in zip(util_rects(), UTILS):
        pygame.draw.rect(surf, STOCK_DEEP, r, border_radius=2)
        pygame.draw.rect(surf, INK, r, width=2, border_radius=2)
        # A heavier bottom edge: three keyed plates read as three pressable
        # things in a way a middot row of labels never can.
        pygame.draw.rect(surf, INK, pygame.Rect(r.x, r.bottom - 5, r.w, 5),
                         border_radius=2)
        icon(surf, r.centerx, r.top + 24)
        tracked(surf, label, (r.centerx, r.bottom - 25), 12, INK, track=1,
                anchor="center")

    pygame.draw.rect(surf, INK, pygame.Rect(MARGIN_L, PROFILE_RECT.top - 8,
                                            COL_W, 1))
    tracked(surf, "PROFILE", (MARGIN_L, PROFILE_RECT.top + 6), 10, INK_SOFT,
            track=3)
    tracked(surf, PLAYER, (MARGIN_L, PROFILE_RECT.top + 21), 19, INK, track=1)
    px, py = PROFILE_RECT.right - 12, PROFILE_RECT.centery + 2
    pygame.draw.lines(surf, INK, False,
                      [(px - 6, py - 7), (px, py), (px - 6, py + 7)], 3)
    return surf, pip_r, skin, parcel_id


# ── review sheet ─────────────────────────────────────────────────────────────
def greyscale_thumb(frame, size=(90, 160)):
    small = pygame.transform.smoothscale(frame, size)
    arr = pygame.surfarray.array3d(small).astype(np.float32)
    lum = (arr[:, :, 0] * 0.299 + arr[:, :, 1] * 0.587
           + arr[:, :, 2] * 0.114)
    g = np.dstack([lum, lum, lum]).astype(np.uint8)
    out = pygame.Surface(size)
    pygame.surfarray.blit_array(out, g)
    return out, lum


def build_sheet(frames, thumb):
    pad, top, foot = 22, 76, 232
    sw = pad + (W + pad) * 4
    sh = top + H + foot
    sheet = pygame.Surface((sw, sh))
    sheet.fill((22, 22, 26))
    f_title = _font(30, True)
    sheet.blit(f_title.render("SKYBIT  MENU-V2  —  COVER-TYPE  —  ROUND 1",
                              True, (240, 232, 214)), (pad, 18))
    sheet.blit(_font(15, True).render(
        "printed travel poster: opaque cream stock, sky only through the cut "
        "window; custom-drawn geometric caps; single left margin x=28",
        True, (150, 148, 152)), (pad, 50))
    for i, (name, ph, frame) in enumerate(frames):
        x = pad + i * (W + pad)
        pygame.draw.rect(sheet, (60, 58, 62),
                         pygame.Rect(x - 2, top - 2, W + 4, H + 4), width=2)
        sheet.blit(frame, (x, top))
        sheet.blit(_font(16, True).render(f"{name.upper()}   phase {ph:.2f}",
                                          True, (226, 218, 200)),
                   (x, top + H + 10))
    ty = top + H + 48
    sheet.blit(thumb, (pad, ty))
    sheet.blit(_font(16, True).render(
        "90x160 GREYSCALE  (day frame)", True, (226, 218, 200)),
        (pad + 104, ty))
    for i, line in enumerate((
            "squint test: one bright page, one dark aperture band at the top,",
            "one heavy black word under it, one solid dark bar low, then three",
            "small plates and a name row. Hierarchy survives with no colour.")):
        sheet.blit(_font(14, True).render(line, True, (150, 148, 152)),
                   (pad + 104, ty + 26 + i * 20))
    return sheet


# ── verification ─────────────────────────────────────────────────────────────
def lum(c):
    def ch(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(c[0]) + 0.7152 * ch(c[1]) + 0.0722 * ch(c[2])


def contrast(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def mean_bg(bg, rect):
    r = rect.clip(pygame.Rect(0, 0, W, H))
    arr = pygame.surfarray.array3d(bg.subsurface(r)).astype(np.float32)
    return tuple(int(v) for v in arr.reshape(-1, 3).mean(axis=0))


def ring_bg(bg, rect, pad=10):
    """Mean colour of the band immediately OUTSIDE a rect — what a filled
    element (the START bar, a utility plate) is actually seen against."""
    outer = rect.inflate(pad * 2, pad * 2).clip(pygame.Rect(0, 0, W, H))
    arr = pygame.surfarray.array3d(bg.subsurface(outer)).astype(np.float32)
    mask = np.ones(arr.shape[:2], dtype=bool)
    inner = rect.clip(outer)
    mask[inner.x - outer.x:inner.right - outer.x,
         inner.y - outer.y:inner.bottom - outer.y] = False
    return tuple(int(v) for v in arr[mask].mean(axis=0))


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    frames, paths = [], []
    day_frame = None
    for name, ph in PHASES:
        frame, pip_r, skin, parcel_id = render(ph)
        p = os.path.join(OUT_DIR, f"round_1_{name}.png")
        pygame.image.save(frame, p)
        paths.append(p)
        frames.append((name, ph, frame))
        if name == "day":
            day_frame = frame
            day_pip, day_skin, day_parcel = pip_r, skin, parcel_id

    thumb, lum_arr = greyscale_thumb(day_frame)
    sheet = build_sheet(frames, thumb)
    sheet_path = os.path.join(OUT_DIR, "round_1.png")
    pygame.image.save(sheet, sheet_path)

    # ── 1. contrast, every phase, against the ground actually under it ──
    wm, base_off, parts = wordmark("SKYBIT", INK)
    bb = ink_bbox(wm)
    wm_rect = pygame.Rect(MARGIN_L - 1, WORD_BASELINE - int(base_off) + bb[1],
                          bb[2] - bb[0], bb[3] - bb[1])
    elements = [
        ("kicker AIR PARCEL SERVICE", INK_SOFT,
         pygame.Rect(MARGIN_L, 18, tracked_w(KICKER, 10, 3), 12)),
        ("wordmark SKYBIT", INK, wm_rect),
        ("rule under wordmark", INK,
         pygame.Rect(MARGIN_L, RULE_Y, RULE_R - MARGIN_L, 2)),
        ("subtitle POCKET SKY FLYER", INK,
         pygame.Rect(MARGIN_L, SUB_TOP, tracked_w(SUBTITLE, 11, 4), 13)),
        ("trail hairline", SCARLET, pygame.Rect(64, 318, 170, 62)),
        ("START bar vs stock", SCARLET, START_RECT, "ring"),
        ("START caps on bar", CREAM, START_RECT.inflate(-40, -22)),
    ]
    for r, (label, _icon) in zip(util_rects(), UTILS):
        elements.append((f"util plate {label} vs stock", STOCK_DEEP, r, "ring"))
        elements.append((f"util keyline {label}", INK, r, "ring"))
        elements.append((f"util label {label}", INK,
                         pygame.Rect(r.centerx - 30, r.bottom - 25, 60, 14)))
    elements.append(("PROFILE kicker", INK_SOFT,
                     pygame.Rect(MARGIN_L, PROFILE_RECT.top + 6,
                                 tracked_w("PROFILE", 10, 3), 12)))
    elements.append(("player name", INK,
                     pygame.Rect(MARGIN_L, PROFILE_RECT.top + 21,
                                 tracked_w(PLAYER, 19, 1), 22)))

    print("\n=== 1. CONTRAST (ink vs the ground it sits on) ===")
    bgs = {name: render(ph, bg_only=True) for name, ph in PHASES}
    header = f"{'element':34s}" + "".join(f"{n:>10s}" for n, _ in PHASES)
    print(header)
    invariant = []
    worst = 99.0
    for entry in elements:
        label, ink, rect = entry[0], entry[1], entry[2]
        mode = entry[3] if len(entry) > 3 else "under"
        vals = []
        for name, _ph in PHASES:
            bg = (ring_bg(bgs[name], rect) if mode == "ring"
                  else mean_bg(bgs[name], rect))
            vals.append(contrast(ink, bg))
        spread = max(vals) - min(vals)
        invariant.append((label, spread))
        worst = min(worst, min(vals))
        print(f"{label:34s}" + "".join(f"{v:10.2f}" for v in vals)
              + f"   spread {spread:.3f}")
    print(f"worst contrast anywhere: {worst:.2f}")
    print("phase-variant elements (spread > 0.05): "
          + str([l for l, s in invariant if s > 0.05] or "none"))

    # sky-adjacent: the aperture edge + Pip, who breaks the window
    print("\n-- sky-adjacent: the cut window is the ONLY place phase shows --")
    edge_min = 99.0
    for name, ph in PHASES:
        bg = bgs[name]
        inner = mean_bg(bg, pygame.Rect(WINDOW.x + 6, WINDOW.y + 6,
                                        WINDOW.w - 12, 20))
        low = mean_bg(bg, pygame.Rect(WINDOW.x + 6, WINDOW.bottom - 26,
                                      WINDOW.w - 12, 20))
        # The aperture edge is a keyline AND a stock/sky value step; whichever
        # of the two is carrying at this phase is what defines the cut.
        edge = max(contrast(INK, inner), contrast(STOCK, inner))
        edge_min = min(edge_min, edge,
                       max(contrast(INK, low), contrast(STOCK, low)))
        low_edge = max(contrast(INK, low), contrast(STOCK, low))
        print(f"  {name:7s} top band {str(inner):16s} keyline "
              f"{contrast(INK, inner):5.2f} / stock step "
              f"{contrast(STOCK, inner):5.2f} -> {edge:5.2f}   |   "
              f"ridge band {str(low):16s} keyline {contrast(INK, low):5.2f} / "
              f"stock step {contrast(STOCK, low):5.2f} -> {low_edge:5.2f}")
    print(f"  aperture edge never falls below {edge_min:.2f} — the keyline "
          f"carries the bright phases, the cream stock carries the dark ones")

    # ── 2. type ──
    print("\n=== 2. WORDMARK TYPE ===")
    print(f"  cap height {CAP}px  stem {STEM:.3f}cap ({STEM*CAP:.1f}px)  "
          f"horizontals {THIN:.3f}cap ({THIN*CAP:.1f}px)")
    print(f"  rendered ink bbox on canvas: x {wm_rect.left}..{wm_rect.right} "
          f"(w {wm_rect.width}), y {wm_rect.top}..{wm_rect.bottom} "
          f"(h {wm_rect.height})")
    print(f"  left margin axis x={MARGIN_L}; S (round) ink starts at "
          f"x={wm_rect.left} -> {MARGIN_L - wm_rect.left}px optical overhang")
    print(f"  tracking {TRACK}px = {TRACK/CAP:.3f} em; kerns {KERN}")
    print(f"  clearance to right margin (x={COL_R}): "
          f"{COL_R - wm_rect.right}px")
    print(f"  rule stops at x={RULE_R}: "
          f"{100*(RULE_R-MARGIN_L)/COL_W:.0f}% of the column, "
          f"{COL_R-RULE_R}px short of the right margin")
    xs = []
    for ch, g, gbb, gx in parts:
        xs.append(f"{ch}:{gbb[2]-gbb[0]}px")
    print("  glyph ink widths " + " ".join(xs))

    # ── 3. label fit ──
    print("\n=== 3. LABEL FIT (measured px vs available) ===")
    fits = [
        (KICKER, 10, 3, COL_W, "kicker (decorative, non-interactive)"),
        (SUBTITLE, 11, 4, COL_W, "subtitle (decorative)"),
        ("START", 27, 5, START_RECT.width - 70, "START bar (minus chevron)"),
        ("PROFILE", 10, 3, COL_W - 30, "profile kicker (decorative)"),
        (PLAYER, 19, 1, COL_W - 30, "player name"),
    ]
    for label, _icon in UTILS:
        fits.append((label, 12, 1, UTIL_W - 12, "utility label (12px min)"))
    ok = True
    for text, size, track, avail, note in fits:
        wpx = tracked_w(text, size, track)
        good = wpx <= avail
        ok &= good
        print(f"  {text:9s} {size:2d}px track {track}  {wpx:4d}px / {avail:4d}px "
              f"{'OK ' if good else 'OVER'}  {note}")
    print(f"  all labels fit: {ok}; smallest INTERACTIVE type = 12px "
          f"(utility labels), 19px player name, 27px START")

    # ── 4. tap targets ──
    print("\n=== 4. TAP TARGETS ===")
    targets = [("START", START_RECT), ("PROFILE", PROFILE_RECT)]
    for r, (label, _icon) in zip(util_rects(), UTILS):
        targets.append((label, r))
    for name, r in targets:
        print(f"  {name:9s} {str(r):38s} {r.width}x{r.height}"
              f"  >=48dp: {min(r.width, r.height) >= 48}")
        assert min(r.width, r.height) >= 48, name
        assert r.bottom <= 624, name
    for i in range(len(targets)):
        for j in range(i + 1, len(targets)):
            a, b = targets[i][1], targets[j][1]
            assert not a.colliderect(b), (targets[i][0], targets[j][0])
    print("  pairwise disjoint: True")
    print(f"  gaps: START.bottom {START_RECT.bottom} -> utilities.top {UTIL_Y}"
          f" = {UTIL_Y - START_RECT.bottom}px; utilities.bottom "
          f"{UTIL_Y+UTIL_H} -> PROFILE.top {PROFILE_RECT.top} = "
          f"{PROFILE_RECT.top - (UTIL_Y+UTIL_H)}px; between utility plates = "
          f"{UTIL_GAP}px")
    print(f"  lowest interactive edge: {max(r.bottom for _n, r in targets)} "
          f"(limit 624)")

    # ── 5. thumbnail ──
    print("\n=== 5. THUMBNAIL (90x160 greyscale of the day frame) ===")
    bands = [("kicker/window", 0, 44), ("wordmark", 44, 78),
             ("pip band", 78, 100), ("START", 100, 118),
             ("utilities", 118, 141), ("profile", 141, 160)]
    for nm, y0, y1 in bands:
        seg = lum_arr[:, y0:y1]
        print(f"  {nm:14s} rows {y0:3d}-{y1:3d}  mean L {seg.mean():6.1f}"
              f"  min {seg.min():5.1f}  max {seg.max():5.1f}"
              f"  ink coverage {(seg < 110).mean()*100:5.1f}%")

    # ── 6. Pip ──
    print("\n=== 6. PIP ===")
    print(f"  equipped skin from store_data.equipped('skin'): {day_skin!r}")
    print(f"  equipped parcel: {day_parcel!r}  (drawn via "
          f"parrot.get_parcel(mode, parcel_id))")
    print(f"  sprite rect {day_pip} -> {day_pip.width}x{day_pip.height}px, "
          f"tilt {PIP_TILT}deg, scale {PIP_SCALE}")
    body = parrot.get_skin_frame(day_skin, 1, 0.0)
    print(f"  base frame {body.get_size()} at {PIP_SCALE}x -> "
          f"{int(body.get_width()*PIP_SCALE)}px nominal, "
          f"{day_pip.width}px of actual ink across")
    parcel = parrot.get_parcel("normal", day_parcel)
    pa = pygame.surfarray.array_alpha(parcel)
    print(f"  parcel {parcel.get_size()}, opaque px "
          f"{int((pa > 40).sum())} -> carried at "
          f"+{PARCEL_Y_OFFSET + PARCEL_HERO_DROP}px, rotated with him")
    print(f"  clears START (top {START_RECT.top}): "
          f"{day_pip.bottom <= START_RECT.top}")

    print("\n=== FILES ===")
    for p in paths + [sheet_path]:
        print("  " + os.path.relpath(p, _REPO))


if __name__ == "__main__":
    main()
