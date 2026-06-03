"""Shan-shui foreground / ground concepts for the Skybit redesign.

The bright kelly-green cartoon meadow is the last element clashing with the
locked ink-wash art direction. These five concepts replace it with a near-plane
that obeys atmospheric perspective: the foreground sits ONE STEP CLOSER than the
mountain winner's front ridge, so it must read as the DARKEST, most saturated,
most crisply-defined, warm-rim-lit ANCHOR of the frame — the exact inverse of
today's bright green. Every concept retints across the full biome day/night
cycle by drawing from the same stage palette the sky/mountains/pillars consume.

Exploration-only — nothing here is imported by the live game. Pure-Pygame /
pygbag-safe (fill, blit, draw.*, SRCALPHA, BLEND_*) — no surfarray/gfxdraw/numpy
or per-pixel set_at loops on the hot path.

Each painter takes (surf, w, ground_y, h, scroll, pal) where `pal` is a stage
palette dict carrying both the redesign struct_*/ground_*/mtn_* keys AND the
stone_* aliases (so the production pine/Songyue helpers consume it unchanged).
"""
from __future__ import annotations

import math
import random

import pygame

from game.draw import lerp_color, draw_wuling_pine


# ── shared colour helpers (mirror the redesign engines so tones harmonise) ────

def _clamp(c):
    return max(0, min(255, int(c)))


def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return (_clamp(a[0] + (b[0] - a[0]) * t),
            _clamp(a[1] + (b[1] - a[1]) * t),
            _clamp(a[2] + (b[2] - a[2]) * t))


def _shade(c, d):
    return (_clamp(c[0] + d), _clamp(c[1] + d), _clamp(c[2] + d))


def _luma(c):
    return (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) / 255.0


def _sat(c, f):
    g = _luma(c) * 255.0
    return (_clamp(g + (c[0] - g) * f),
            _clamp(g + (c[1] - g) * f),
            _clamp(g + (c[2] - g) * f))


def _nightf(pal):
    """Continuous 0..1 night-ness from sky_top luminance, so a concept can push
    rim-light/lantern warmth as the stage darkens without a hard phase step."""
    r, g, b = pal.get('sky_top', (60, 120, 200))
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return max(0.0, min(1.0, (95.0 - lum) / 75.0))


def _near_ink(pal):
    """The base near-plane ink tone: the stage's nearest mountain tone pushed one
    step DARKER and more SATURATED than V14's front ridge, since the foreground
    is one plane closer. This is the anchor value the whole frame leans on."""
    near = pal.get('mtn_near', (55, 95, 145))
    return _shade(_sat(near, 1.34), -26)


def _rim_color(pal):
    """Warm golden rim-light catch that continues V14's crest highlight one plane
    closer. Pulled from the stage horizon toward warm gold so dawn/dusk flush it
    and night cools it without ever going pure white."""
    horizon = pal.get('horizon', (250, 226, 184))
    return _mix(horizon, (255, 226, 168), 0.55)


def _water_tint(pal):
    return pal.get('water_tint', _mix(pal.get('mtn_near', (60, 100, 120)),
                                      (120, 150, 150), 0.5))


def _mist_tint(pal):
    return pal.get('mist_tint', (210, 224, 224))


# ── low mist tucked at the foreground base (reused by several concepts) ───────

def _base_mist(surf, w, gy, pal, y_frac=0.92, n=3, alpha=64):
    """Soft horizontal haze strips skimming the foreground base — the shan-shui
    breath that separates the dark near-bank from the ridge behind it. Thickens
    toward night as the air cools. Drawn UNDER the near silhouette by callers
    that want the mist to read behind the bank, OVER for a veil in front."""
    night = _nightf(pal)
    col = _mist_tint(pal)
    a0 = int(alpha * (0.7 + 0.5 * night))
    layer = pygame.Surface((w, gy), pygame.SRCALPHA)
    for k in range(n):
        cy = int(gy * y_frac) - k * 7
        half = max(3, 7 - k)
        for dy in range(-half, half + 1):
            yy = cy + dy
            if 0 <= yy < gy:
                a = int(a0 * (1 - k / (n + 0.5)) * (1 - abs(dy) / (half + 1)))
                if a > 0:
                    pygame.draw.line(layer, (*col, a), (0, yy), (w, yy))
    surf.blit(layer, (0, 0))


# ── per-concept ridge / bank silhouette sampler ───────────────────────────────

def _bank_top(x, base_h, amp, freq, seed):
    """One organic near-bank crest height (px above ground line) — a couple of
    summed sines so the lip rolls like a calligraphic ink stroke, never a flat
    rule. base_h/amp are pixel values, not fractions, so each concept dials its
    own height range directly."""
    h = base_h
    h += math.sin(x * freq + seed) * amp
    h += math.sin(x * freq * 2.7 + seed * 1.7) * (amp * 0.35)
    h += math.sin(x * freq * 0.4 + seed * 0.6) * (amp * 0.5)
    return h


def _filled_bank(surf, w, gy, h, top_col, bot_col, crest_fn, ease=1.3):
    """Fill a vertical gradient clipped under a bank silhouette (crest_fn(x)->y).
    Darkest, most saturated mass in the frame; the gradient gives the near earth
    internal body rather than a flat slab."""
    pts = [crest_fn(x) for x in range(0, w + 1, 2)]
    top = min(y for _, y in pts)
    depth = gy - top
    if depth <= 0:
        return pts
    body = pygame.Surface((w, depth), pygame.SRCALPHA)
    for i in range(depth):
        t = (i / max(1, depth)) ** ease
        pygame.draw.line(body, _mix(top_col, bot_col, t), (0, i), (w, i))
    poly = [(0, depth)] + [(x, y - top) for x, y in pts] + [(w, depth)]
    mask = pygame.Surface((w, depth), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(body, (0, top))
    return pts


def _rim_stroke(surf, pts, color, width=2):
    """A warm rim-light catch riding the bank crest — V14's golden crest one
    plane closer. AA where cheap; a thicker under-stroke gives it body."""
    if len(pts) < 2:
        return
    pygame.draw.lines(surf, color, False, pts, width)
    pygame.draw.aalines(surf, _mix(color, (255, 255, 255), 0.4), False, pts)


# ══════════════════════════════════════════════════════════════════════════
# Concept 1 — Near-Ridge Ink Bank  (thin–medium, ~50px)
# The floor IS the closest, darkest ink-wash ridge: a saturation-boosted near
# tone band with a crisp GOLDEN rim-lit crest (continuing V14's near ridge one
# layer closer), low mist tucked at its base, and tiny pagoda-nub echoes of the
# summit pagodas. Tightest tie to the mountain winner.
# ══════════════════════════════════════════════════════════════════════════

def fg_near_ridge_ink_bank(surf, w, gy, h, scroll, pal):
    night = _nightf(pal)
    ink = _near_ink(pal)
    ink_top = ink
    ink_bot = _shade(ink, -22)
    rim = _rim_color(pal)

    # Mist tucked at the base BEHIND the bank so the ridge behind it dissolves
    # into the bank foot — drawn first.
    _base_mist(surf, w, gy, pal, y_frac=0.985, n=3,
               alpha=int(48 + 26 * night))

    def crest(x):
        sx = x + scroll * 0.30
        return (x, int(gy - _bank_top(sx, base_h=30, amp=12,
                                      freq=0.022, seed=9)))

    pts = _filled_bank(surf, w, gy, h, ink_top, ink_bot, crest, ease=1.2)
    _rim_stroke(surf, pts, rim, width=2)

    # Tiny pagoda-nub echoes on the two locally-tallest crest points — the
    # foreground answer to V14's summit pagodas, near-black so they read as
    # architectural punctuation against the warm rim.
    pag = _shade(_sat(ink, 1.2), -34)
    tall = sorted(pts, key=lambda p: p[1])[:6]
    for (px, py) in tall[::3]:
        _nub_pagoda(surf, px, py + 1, pag, rim)

    # A faint front veil of mist so the foot reads humid even by day.
    _base_mist(surf, w, gy, pal, y_frac=0.99, n=2, alpha=int(20 + 18 * night))


def _nub_pagoda(surf, x, base_y, color, accent):
    """A 2-tier pagoda nub — the smallest readable pagoda silhouette, echoing the
    summit pagodas one plane closer."""
    cy = base_y
    for t in range(2):
        tw = 9 - t * 3
        pygame.draw.rect(surf, color, (x - tw // 2, cy - 4, tw, 4))
        ew = tw + 5
        pygame.draw.polygon(surf, color, [(x - ew // 2, cy - 4),
                                          (x + ew // 2, cy - 4),
                                          (x, cy - 7)])
        pygame.draw.aaline(surf, accent, (x - ew // 2 + 1, cy - 5),
                           (x + ew // 2 - 1, cy - 5))
        cy -= 7
    pygame.draw.line(surf, color, (x, cy), (x, cy - 4), 1)
    surf.set_at((x, cy - 4), accent)


# ══════════════════════════════════════════════════════════════════════════
# Concept 2 — Still-Water Inlet  (medium–tall, ~80px)
# Calm jade water shelf mirroring the sky gradient + soft reflections of the
# pillars/peaks, a thin dark shoreline rim, low mist skimming the surface, and
# warm lantern-glint reflections at night. The reflection logic is the same
# squashed-and-tinted trick the karst stilt-houses use.
# ══════════════════════════════════════════════════════════════════════════

def fg_still_water_inlet(surf, w, gy, h, scroll, pal):
    night = _nightf(pal)
    water = _water_tint(pal)
    horizon = pal.get('horizon', (250, 226, 184))
    rim = _rim_color(pal)

    # 1. Dark shoreline bank — a near-bank lip the water laps against, raised
    # higher than a hairline so it reads as the darkest, crispest anchor edge of
    # the frame with the still water as a receding shelf below it.
    shore_top = gy - 20
    shore = _near_ink(pal)
    def crest(x):
        sx = x + scroll * 0.30
        return (x, int(shore_top - _bank_top(sx, base_h=4, amp=5,
                                             freq=0.03, seed=4)))
    pts = _filled_bank(surf, w, gy, h, shore, _shade(shore, -20), crest, ease=1.0)

    # 2. Jade water shelf below the shore — a tall vertical gradient that MIRRORS
    # the sky: bright horizon tone at the waterline darkening into a deep
    # saturated jade toward the player, the broad calm sheet reflections sit on.
    wtop = gy + 2
    wh = h - wtop
    surf_top = _mix(horizon, water, 0.40)
    surf_bot = _shade(_sat(water, 1.25), -46)
    shelf = pygame.Surface((w, max(1, wh)))
    for i in range(wh):
        t = (i / max(1, wh)) ** 0.85
        pygame.draw.line(shelf, _mix(surf_top, surf_bot, t), (0, i), (w, i))
    surf.blit(shelf, (0, wtop))

    # 3. Mirrored reflections of the pillar pair: vertically squashed, tinted to
    # the water, broken by horizontal ripple gaps so they shimmer rather than
    # sit as solid bars (the still-water read of draw_stilt_houses pushed
    # stronger). The near pillar is at ~x 0.68; a peak echo at ~0.30.
    refl = pygame.Surface((w, wh), pygame.SRCALPHA)
    pillar_ink = _shade(_sat(pal.get('mtn_near', (55, 95, 145)), 1.25), -4)
    refls = [(int(w * 0.685), 28, 110), (int(w * 0.30), 22, 70)]
    for cx, rw, base_a in refls:
        for yy in range(0, min(wh, 96)):
            t = yy / 96.0
            # Ripple breakup: skip thin horizontal slices so the column shimmers.
            if (yy + int(math.sin(yy * 0.4 + cx) * 2)) % 7 < 2:
                continue
            a = int(base_a * (1 - t) ** 1.3)
            jit = int(math.sin(yy * 0.45 + cx) * 2.0)
            pygame.draw.line(refl, (*pillar_ink, a),
                             (cx - rw // 2 + jit, yy), (cx + rw // 2 + jit, yy))
    surf.blit(refl, (0, wtop))

    # 4. Warm lantern-glint reflections at night — vertical warm smears wobbling
    # down the water under the pillars, the only saturated note after dark.
    if night > 0.2:
        glow = pal.get('glow_color', (255, 200, 120))
        gl = pygame.Surface((w, wh), pygame.SRCALPHA)
        for cx, _rw, _a in refls:
            for yy in range(0, min(wh, 110), 2):
                t = yy / 110.0
                a = int(170 * night * (1 - t))
                jx = cx + int(math.sin(yy * 0.6) * 3)
                pygame.draw.line(gl, (*glow, a), (jx - 1, yy), (jx + 1, yy))
        surf.blit(gl, (0, wtop), special_flags=pygame.BLEND_RGB_ADD)

    # 5. Bright waterline glints + low mist skimming the surface. The top glint
    # sits right on the shoreline so land/water separation stays crisp.
    glint = pygame.Surface((w, wh), pygame.SRCALPHA)
    pygame.draw.line(glint, (*rim, 130), (0, 1), (w, 1), 1)
    pygame.draw.line(glint, (*rim, 70), (int(w * 0.18), 9), (int(w * 0.82), 9), 1)
    pygame.draw.line(glint, (*rim, 45), (int(w * 0.30), 20), (int(w * 0.70), 20), 1)
    surf.blit(glint, (0, wtop), special_flags=pygame.BLEND_RGB_ADD)
    _base_mist(surf, w, gy, pal, y_frac=1.04, n=2, alpha=int(30 + 24 * night))
    _rim_stroke(surf, pts, rim, width=2)


# ══════════════════════════════════════════════════════════════════════════
# Concept 3 — Terraced Paddy Steps  (tall, layered, ~95px)
# Stepped Longji rice-terrace walls receding with haze; thin water glints catch
# the horizon rim-light on each lip; sandstone-tan earth matched to the Songyue
# pagoda brick so the foreground reads as the same masonry family.
# ══════════════════════════════════════════════════════════════════════════

def _terracotta(pal):
    """Yungang-grotto sandstone face matched to the Songyue pillar brick (the
    same _mix the pillar candidate uses) so the terraces read as one stone
    family as the biome retints."""
    return _mix(pal.get('stone_dark', (95, 70, 55)), (208, 158, 116), 0.66)


def fg_terraced_paddy(surf, w, gy, h, scroll, pal):
    night = _nightf(pal)
    rim = _rim_color(pal)
    horizon = pal.get('horizon', (250, 226, 184))
    earth = _terracotta(pal)
    water = _water_tint(pal)
    mtint = _mist_tint(pal)

    # Stepped Longji terraces drawn FRONT (lowest, darkest, most saturated) →
    # BACK (highest, hazed toward the mist) as overlapping opaque earth slabs,
    # each capped by a crisp dark riser shadow + a thin flooded-water glint line
    # catching the horizon rim. The flooded shelf is alpha-composited (NOT
    # additive — an additive band on a bright sunset sky blows out to white),
    # so each lip reads as a sliver of still water, never a bright stripe.
    n_steps = 5
    top_of_steps = gy - 96
    # Each front step sits LOWER and is drawn LAST, so nearer earth overlaps the
    # paddy shelf of the step behind it — the classic stacked-terrace read.
    step_y = [int(top_of_steps + (h - top_of_steps) * (s / n_steps) ** 0.92)
              for s in range(n_steps + 1)]

    for s in range(n_steps):                       # 0 = back/top, last = front
        depth_t = s / (n_steps - 1)                # 0=back, 1=front
        y_lip = step_y[s]
        y_bot = h
        # Front earth darkest + most saturated; back earth hazed toward mist.
        face = _sat(_shade(earth, -6 - int(34 * depth_t)), 0.95 + 0.4 * depth_t)
        face = _mix(face, mtint, 0.40 * (1 - depth_t))

        def lip(x, y0=y_lip, s=s):
            sx = x + scroll * (0.14 + 0.035 * s)
            return (x, int(y0 - math.sin(sx * 0.026 + s * 1.3) * 4
                           - math.sin(sx * 0.068 + s * 2.1) * 2))
        pts = [lip(x) for x in range(0, w + 1, 3)]

        # Opaque earth slab from the lip down to the frame bottom (the next,
        # nearer step paints over its lower part).
        pygame.draw.polygon(surf, face, [(0, y_bot)] + pts + [(w, y_bot)])

        # Flooded-paddy shelf: a short alpha-composited water band hugging the
        # lip, brighter and bluer on nearer steps where it catches the most rim.
        wcol = _mix(horizon, _sat(water, 1.1), 0.5)
        shelf_h = max(5, int(7 + 5 * depth_t))
        band = pygame.Surface((w, shelf_h), pygame.SRCALPHA)
        a0 = int(120 + 90 * depth_t)
        for i in range(shelf_h):
            t = i / max(1, shelf_h)
            a = int(a0 * (1 - t) ** 1.6)
            if a > 0:
                pygame.draw.line(band, (*wcol, a), (0, i), (w, i))
        # Clip the band under the lip silhouette so it only floods the shelf top.
        mask = pygame.Surface((w, shelf_h), pygame.SRCALPHA)
        avg_y = int(sum(y for _, y in pts) / len(pts))
        poly = [(0, shelf_h)] + [(x, max(0, y - avg_y)) for x, y in pts] + [(w, shelf_h)]
        pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
        band.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(band, (0, avg_y))

        # Crisp dark riser shadow right under the water line so steps separate.
        pygame.draw.lines(surf, _shade(face, -22), False,
                          [(x, y + shelf_h) for x, y in pts], 2)
        # Warm rim glint catching the lip — strongest on the nearest lips, the
        # foreground answer to V14's golden crest.
        rim_a = _mix(rim, wcol, 0.25)
        _rim_stroke(surf, pts, rim_a, width=1 if depth_t < 0.6 else 2)

    # Low mist pooling between the back terraces to deepen the recession.
    _base_mist(surf, w, gy, pal, y_frac=0.80, n=2, alpha=int(26 + 24 * night))


# ══════════════════════════════════════════════════════════════════════════
# Concept 4 — Pine & Bamboo Fringe Bluff  (medium, ~65px)
# A dark earthen near-bank crowned with a calligraphic fringe of wuling pines +
# bamboo silhouettes, mist curling at the base, sparse moss accents. The living
# fringe is the calligraphy; the bank is the dark mass it grows from.
# ══════════════════════════════════════════════════════════════════════════

def fg_pine_bamboo_bluff(surf, w, gy, h, scroll, pal):
    night = _nightf(pal)
    ink = _near_ink(pal)
    rim = _rim_color(pal)

    _base_mist(surf, w, gy, pal, y_frac=0.985, n=3, alpha=int(46 + 28 * night))

    # The dark earthen bluff — a taller, rounder mass than concept 1 so the
    # fringe has a bank to grow from.
    def crest(x):
        sx = x + scroll * 0.30
        return (x, int(gy - _bank_top(sx, base_h=34, amp=10,
                                      freq=0.018, seed=12)))
    pts = _filled_bank(surf, w, gy, h, ink, _shade(ink, -20), crest, ease=1.2)
    _rim_stroke(surf, pts, rim, width=2)

    # A height lookup so the fringe roots sit ON the rolling bank lip.
    xy = {x: y for x, y in pts}
    def bank_y(x):
        return xy.get((x // 2) * 2, gy - 30)

    foliage = {
        'foliage_dark': pal.get('foliage_dark', (34, 72, 58)),
        'foliage_mid': pal.get('foliage_mid', (58, 110, 84)),
        'foliage_top': pal.get('foliage_top', (96, 150, 116)),
        'foliage_accent': pal.get('foliage_accent', (146, 188, 140)),
    }

    # Calligraphic bamboo culms — thin jade verticals with node ticks + leaf
    # flicks, clumped at the frame edges so the centre stays open to the gap.
    bdark = foliage['foliage_dark']
    bmid = foliage['foliage_mid']
    btop = foliage['foliage_top']
    for cx0, n_c, scale in ((int(w * 0.08), 6, 1.0), (int(w * 0.93), 5, 0.85)):
        for i in range(n_c):
            x = cx0 + (i - n_c // 2) * 5
            root = bank_y(max(0, min(w, x)))
            ch = int((34 + (i % 3) * 8) * scale)
            top_y = root - ch
            pygame.draw.line(surf, bdark, (x, root), (x + (i % 2), top_y), 2)
            for t in (0.5, 0.74):
                ny = int(root - ch * t)
                pygame.draw.line(surf, bmid, (x - 1, ny), (x + 1, ny), 1)
            pygame.draw.line(surf, bmid, (x, top_y + 5),
                             (x + 6 + (i % 2) * 3, top_y - 2), 1)
            pygame.draw.line(surf, btop, (x, top_y + 9), (x - 5, top_y + 1), 1)

    # Wuling pines as the hero calligraphy — the horizontal peacock-tail reads
    # instantly as shan-shui. A taller leaning pine + a smaller companion, set
    # off-centre so the gap stays clear.
    fpal = dict(pal)
    fpal.update(foliage)
    px = int(w * 0.24)
    draw_wuling_pine(surf, px, bank_y(px), 46, fpal, lean=12,
                     direction='up', layers=6)
    px2 = int(w * 0.17)
    draw_wuling_pine(surf, px2, bank_y(px2), 28, fpal, lean=-6,
                     direction='up', layers=4)
    px3 = int(w * 0.78)
    draw_wuling_pine(surf, px3, bank_y(px3), 38, fpal, lean=-10,
                     direction='up', layers=5)

    # Sparse moss accents dotting the dark bank — tiny brighter foliage flicks.
    rng = random.Random(int(scroll) ^ 0x5135)
    for _ in range(14):
        mx = rng.randint(0, w - 1)
        my = bank_y(mx) + rng.randint(4, 26)
        pygame.draw.circle(surf, foliage['foliage_mid'], (mx, my), 1)


# ══════════════════════════════════════════════════════════════════════════
# Concept 5 — Mist-Veiled Stone Shore  (thin mass, tall mist veil, ~45px)
# The most restrained: a few weathered sumi-e ink-stone boulders emerging from a
# thick low mist blanket that largely dissolves the ground into negative space
# (the shan-shui "void"). Big rocks surrounding smaller ones, dry-broken edges.
# ══════════════════════════════════════════════════════════════════════════

def fg_mist_veiled_shore(surf, w, gy, h, scroll, pal):
    night = _nightf(pal)
    ink = _near_ink(pal)
    rim = _rim_color(pal)

    # A thin dark shore strip so the bottom isn't pure void — the boulders sit
    # on it, the rest dissolves into mist.
    strip = pygame.Surface((w, h - gy), pygame.SRCALPHA)
    sc_top = _shade(ink, -8)
    for i in range(h - gy):
        t = i / max(1, h - gy)
        a = int(255 * min(1.0, 0.5 + t))
        pygame.draw.line(strip, (*_mix(sc_top, _shade(sc_top, -16), t), a),
                         (0, i), (w, i))
    surf.blit(strip, (0, gy))

    # Weathered ink-stone boulders: a few BIG ones with smaller ones nestled
    # around them (classic shan-shui grouping). Each is a flat-bottomed lump
    # with a dry-broken upper contour + a warm rim catch on the lit shoulder.
    rng = random.Random(0x57043 ^ int(scroll * 0.3))
    groups = [(int(w * 0.20), 1.25), (int(w * 0.55), 1.55), (int(w * 0.83), 1.0)]
    for gx, gs in groups:
        # Big anchor boulder + 1-2 smaller companions clustered to one side.
        _ink_boulder(surf, gx, gy, gs, ink, rim, rng)
        for j in range(rng.randint(1, 2)):
            ox = gx + rng.choice((-1, 1)) * rng.randint(16, 30)
            _ink_boulder(surf, ox, gy, gs * rng.uniform(0.4, 0.62),
                         ink, rim, rng)

    # The hero: a THICK low mist blanket that swallows the rock feet and most of
    # the ground into the void. Many soft bands rising as the day cools, so
    # predawn/dusk read as near-total dissolution — the most negative-space look.
    nbands = 5 + int(round(night * 3))
    _base_mist(surf, w, gy, pal, y_frac=0.97, n=nbands,
               alpha=int(58 + 34 * night))
    # One higher faint sheet catching the boulder shoulders so even the tallest
    # rock reads half-dissolved rather than a hard silhouette.
    _base_mist(surf, w, gy, pal, y_frac=0.90, n=2, alpha=int(24 + 18 * night))
    _ = rim  # rim already consumed per-boulder


def _ink_boulder(surf, cx, base_y, scale, ink, rim, rng):
    """A weathered sumi-e ink-stone: a flat-bottomed lump with a dry-broken
    upper contour (a few jittered crest points), darkest in the frame, with a
    warm rim catch on the lit (left) shoulder."""
    bw = int(20 * scale)
    bh = int(16 * scale)
    cx_l = cx - bw // 2
    cx_r = cx + bw // 2
    top = base_y - bh
    # Dry-broken upper contour: walk left→right with small jitters.
    crest = [(cx_l, base_y)]
    steps = max(4, bw // 4)
    for i in range(steps + 1):
        x = cx_l + (cx_r - cx_l) * i / steps
        # A rounded lump profile + jitter so the edge reads as a loaded brush.
        d = (x - cx) / max(1, bw / 2)
        y = top + (bh * d * d) - rng.randint(0, max(1, int(2 * scale)))
        crest.append((int(x), int(y)))
    crest.append((cx_r, base_y))
    body = _shade(_sat(ink, 1.1), -10)
    pygame.draw.polygon(surf, body, crest)
    # Darker base shadow band so the rock sits IN the shore, not on it.
    pygame.draw.polygon(surf, _shade(body, -18),
                        [(cx_l, base_y), (cx_l, base_y - 3),
                         (cx_r, base_y - 3), (cx_r, base_y)])
    # Warm rim catch on the lit left shoulder — the single bright note per rock.
    lit = [(x, y) for (x, y) in crest[1:len(crest) // 2 + 1]]
    if len(lit) >= 2:
        pygame.draw.aalines(surf, rim, False, lit)


# ── registry ──────────────────────────────────────────────────────────────

CONCEPTS = [
    ("Near-Ridge Ink Bank", fg_near_ridge_ink_bank),
    ("Still-Water Inlet", fg_still_water_inlet),
    ("Terraced Paddy Steps", fg_terraced_paddy),
    ("Pine & Bamboo Fringe Bluff", fg_pine_bamboo_bluff),
    ("Mist-Veiled Stone Shore", fg_mist_veiled_shore),
]
