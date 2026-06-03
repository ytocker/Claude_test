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


def _filled_bank(surf, w, gy, h, top_col, bot_col, crest_fn, ease=1.3,
                 bottom=None):
    """Fill a vertical gradient clipped under a bank silhouette (crest_fn(x)->y).
    Darkest, most saturated mass in the frame; the gradient gives the near earth
    internal body rather than a flat slab.

    The mass fills OPAQUE down to `bottom` (defaults to the true frame bottom h,
    NOT the ground line gy) so no dead flat panel can ever open below the
    foreground between gy and the screen edge — the round-1 base-strip bug."""
    bottom = h if bottom is None else bottom
    pts = [crest_fn(x) for x in range(0, w + 1, 2)]
    top = min(y for _, y in pts)
    depth = bottom - top
    if depth <= 0:
        return pts
    body = pygame.Surface((w, depth), pygame.SRCALPHA)
    # Ease across the FULL crest-to-bottom span (not just crest-to-ground): the
    # body keeps darkening continuously through the gy→bottom strip instead of
    # clamping to a flat slab there, which is what opened the round-1 dead panel.
    # bot_col is reached only at the true frame edge, so the near earth is one
    # solid darkening mass with no horizontal seam below the ground line.
    span = max(1, depth - 1)
    for i in range(depth):
        t = (i / span) ** ease
        pygame.draw.line(body, _mix(top_col, bot_col, min(1.0, t)), (0, i), (w, i))
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
    # Drive the body well past the old -22 so the near earth keeps darkening all
    # the way to the frame edge — the foot is the darkest value in the frame, so
    # the bank reads as one solid plane closer than V14's ridge, no dead strip.
    ink_bot = _shade(_sat(ink, 1.1), -46)
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
    # Reconceived: nearest = darkest. The frame is a DARK rim-lit earthen bank
    # that fills almost the whole foreground; the water is only a THIN reflective
    # SLIVER at the very foot of the bank — a hint of the inlet, not a tall
    # bright shelf (which would have violated nearest=darkest). No fussy ripple
    # columns; just the dark mass, a warm rim crest, a single soft waterline
    # glint, and night lantern glints.
    night = _nightf(pal)
    water = _water_tint(pal)
    horizon = pal.get('horizon', (250, 226, 184))
    rim = _rim_color(pal)

    # The thin water sliver lives in the bottom strip; the bank fills down to it.
    water_top = h - 14

    # 1. Dark earthen bank — the dominant dark mass, crest rolling like an ink
    # stroke, body darkening to the waterline so it's the closest plane.
    ink = _near_ink(pal)
    def crest(x):
        sx = x + scroll * 0.30
        return (x, int(gy - _bank_top(sx, base_h=28, amp=10,
                                      freq=0.026, seed=4)))
    pts = _filled_bank(surf, w, gy, h, ink, _shade(_sat(ink, 1.1), -48),
                       crest, ease=1.2, bottom=water_top)

    # 2. Thin water sliver at the foot — a short vertical gradient catching the
    # horizon tone at its lip and deepening to dark jade, so it reads as still
    # water lapping the bank rather than a bright shelf.
    wh = h - water_top
    surf_top = _mix(horizon, water, 0.45)
    surf_bot = _shade(_sat(water, 1.2), -40)
    sliver = pygame.Surface((w, max(1, wh)))
    for i in range(wh):
        t = (i / max(1, wh)) ** 0.7
        pygame.draw.line(sliver, _mix(surf_top, surf_bot, t), (0, i), (w, i))
    surf.blit(sliver, (0, water_top))

    # 3. A single soft warm glint on the waterline — the inlet's only bright note
    # by day, sitting right at the bank foot so land/water stays crisp.
    glint = pygame.Surface((w, wh), pygame.SRCALPHA)
    pygame.draw.line(glint, (*rim, 120), (0, 1), (w, 1), 1)
    pygame.draw.line(glint, (*rim, 55), (int(w * 0.25), 6), (int(w * 0.75), 6), 1)
    surf.blit(glint, (0, water_top), special_flags=pygame.BLEND_RGB_ADD)

    # 4. Night lantern glints — a couple of warm vertical smears wobbling in the
    # sliver under the pillar pair, the one saturated note after dark. Kept thin
    # so they read as caught lamplight, not the old reflection bars.
    if night > 0.2:
        glow = pal.get('glow_color', (255, 200, 120))
        gl = pygame.Surface((w, wh), pygame.SRCALPHA)
        for cx in (int(w * 0.68), int(w * 0.30)):
            for yy in range(0, wh, 2):
                t = yy / max(1, wh)
                a = int(180 * night * (1 - t))
                jx = cx + int(math.sin(yy * 0.7) * 2)
                pygame.draw.line(gl, (*glow, a), (jx - 1, yy), (jx + 1, yy))
        surf.blit(gl, (0, water_top), special_flags=pygame.BLEND_RGB_ADD)

    # 5. Warm rim crest on the bank lip — V14's gold one plane closer, kept warm
    # at night so the bank edge never dissolves.
    warm = _mix(rim, (255, 212, 148), 0.3 + 0.4 * night)
    _rim_stroke(surf, pts, warm, width=2)
    _base_mist(surf, w, gy, pal, y_frac=0.97, n=2, alpha=int(24 + 22 * night))


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

    # Longji "Dragon's-Backbone" terraces drawn BACK (highest, hazed toward the
    # mist) → FRONT (lowest, darkest, most saturated, crispest) as overlapping
    # opaque earth slabs that every fill to the true frame bottom h, so no dead
    # panel can open below them. Front-to-back is a VALUE gradient, not uniform
    # banding: the nearest 2 slabs are thick, dark and saturated and carry the
    # single darkest/crispest riser in the frame; the back slabs are thinner,
    # paler and dissolve into haze. Each lip carries a sliver of still flooded
    # water that catches a warm rim glint — preserved even at night so the
    # terraces never flatten to one muddy value.
    n_steps = 6
    # ~75px total mass so the terraces never crowd the pillar base or bird lane.
    # The rhythm is deliberately non-uniform (anti-wallpaper): the back half is
    # three FINE hazed lips packed tight, the front is two-to-three THICK land
    # slabs — so the eye reads receding land, not a striped pattern.
    top_of_steps = gy - 74
    # Cumulative fractions from the back lip down to the ground line. Tight at the
    # back (small gaps → fine steps), widening hard toward the player (broad
    # nearest slabs). The last gap (0.62→1.0) is the dominant nearest land mass.
    lip_fracs = [0.0, 0.16, 0.30, 0.44, 0.62, 1.0]
    step_y = [int(top_of_steps + (gy - top_of_steps) * f) for f in lip_fracs]

    for s in range(n_steps):                       # 0 = back/top, last = front
        depth_t = s / (n_steps - 1)                # 0=back, 1=front
        front = depth_t > 0.7                       # the nearest land slabs
        y_lip = step_y[s]
        # Front-to-back VALUE gradient, not banding: nearest earth is pushed a
        # full ~15-20% darker + more saturated than the mid slabs; back earth
        # hazes lighter and washes toward the mist tone so it recedes. The
        # nearest slab also keeps darkening to the true frame bottom h.
        face = _sat(_shade(earth, 10 - int(64 * depth_t)), 0.84 + 0.62 * depth_t)
        face = _mix(face, mtint, 0.50 * (1 - depth_t))
        # The very nearest slab gets an extra darken/saturate step so it is
        # unmistakably the closest plane (Longji: front terraces darkest).
        if s == n_steps - 1:
            face = _sat(_shade(face, -10), 1.12)

        def lip(x, y0=y_lip, s=s):
            sx = x + scroll * (0.12 + 0.035 * s)
            return (x, int(y0 - math.sin(sx * 0.026 + s * 1.3) * 4
                           - math.sin(sx * 0.068 + s * 2.1) * 2))
        pts = [lip(x) for x in range(0, w + 1, 3)]

        # Opaque earth slab from the lip down to the frame bottom (the next,
        # nearer step paints over its lower part — and the nearest fills h).
        pygame.draw.polygon(surf, face, [(0, h)] + pts + [(w, h)])
        # Gently darken the bottom of the nearest slab toward the edge so the
        # foot is the single darkest value, giving the near earth solid body.
        if s == n_steps - 1:
            foot = pygame.Surface((w, h - y_lip), pygame.SRCALPHA)
            fh = h - y_lip
            for i in range(fh):
                t = (i / max(1, fh))
                a = int(150 * t * t)
                if a:
                    pygame.draw.line(foot, (*_shade(face, -30), a), (0, i), (w, i))
            surf.blit(foot, (0, y_lip))

        # Flooded-paddy shelf: a short alpha-composited water band hugging the
        # lip, brighter and bluer on nearer steps where it catches the most rim.
        wcol = _mix(horizon, _sat(water, 1.1), 0.5)
        shelf_h = max(4, int(4 + 7 * depth_t))
        band = pygame.Surface((w, shelf_h), pygame.SRCALPHA)
        a0 = int(95 + 105 * depth_t)
        for i in range(shelf_h):
            t = i / max(1, shelf_h)
            a = int(a0 * (1 - t) ** 1.6)
            if a > 0:
                pygame.draw.line(band, (*wcol, a), (0, i), (w, i))
        mask = pygame.Surface((w, shelf_h), pygame.SRCALPHA)
        avg_y = int(sum(y for _, y in pts) / len(pts))
        poly = [(0, shelf_h)] + [(x, max(0, y - avg_y)) for x, y in pts] + [(w, shelf_h)]
        pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
        band.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(band, (0, avg_y))

        # Riser line under the water lip. The nearest riser is the single
        # darkest, crispest line in the whole frame (width 3, deepest shade);
        # back risers are thin + soft so the eye is pulled to the front edge.
        riser_shade = -22 - int(20 * (1 - depth_t))
        riser_w = 3 if s == n_steps - 1 else (2 if front else 1)
        pygame.draw.lines(surf, _shade(face, riser_shade), False,
                          [(x, y + shelf_h) for x, y in pts], riser_w)

        # Warm rim glint riding the water lip — the foreground echo of V14's gold
        # crest. Crucially, a NIGHT floor keeps a warm-gold catch on every lip
        # after dark (rim_a stays warm, never washing to the water tone), so the
        # terraces hold their stepped read at night instead of muddying to one
        # value. Nearest lips glow strongest.
        warm = _mix(rim, (255, 210, 142), 0.35 + 0.45 * night)
        rim_a = _mix(warm, wcol, max(0.0, 0.20 - 0.20 * night))
        lip_w = 2 if front else 1
        _rim_stroke(surf, pts, rim_a, width=lip_w)
        if night > 0.1 and depth_t > 0.4:
            # An additive gold kiss on every front-half lip so the stepped read
            # survives the dark — strongest on the nearest, present on all.
            glint = pygame.Surface((w, 3), pygame.SRCALPHA)
            ga = int(135 * night * (0.35 + 0.65 * depth_t))
            pygame.draw.lines(glint, (*_mix(warm, (255, 232, 172), 0.5), ga),
                              False, [(x, 1) for x, _ in pts], 1)
            surf.blit(glint, (0, avg_y - 1), special_flags=pygame.BLEND_RGB_ADD)

    # Low mist pooling between the back terraces to deepen the recession (kept
    # high so it never veils the dark crisp nearest slabs).
    _base_mist(surf, w, gy, pal, y_frac=0.55, n=2, alpha=int(26 + 24 * night))


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

    # The dark earthen bluff — a taller, rounder mass than concept 1, kept under
    # ~62px so it doesn't crowd the bird lane. Body darkens to the frame edge so
    # no dead strip opens below it.
    def crest(x):
        sx = x + scroll * 0.30
        return (x, int(gy - _bank_top(sx, base_h=32, amp=9,
                                      freq=0.018, seed=12)))
    pts = _filled_bank(surf, w, gy, h, ink, _shade(_sat(ink, 1.1), -46),
                       crest, ease=1.2)
    _rim_stroke(surf, pts, rim, width=2)

    # A height lookup so the fringe roots sit ON the rolling bank lip.
    xy = {x: y for x, y in pts}
    def bank_y(x):
        return xy.get((x // 2) * 2, gy - 30)

    # Retint the foliage away from the live game's kelly meadow greens toward a
    # desaturated ink-teal that belongs to the shan-shui frame — pull each tone
    # toward the near-ink so the fringe reads as calligraphy on the bank, not a
    # reintroduced meadow. Night cools/darkens it further.
    def _teal(c, f):
        return _sat(_mix(c, ink, 0.30 + 0.18 * night), f)
    foliage = {
        'foliage_dark': _teal(pal.get('foliage_dark', (34, 72, 58)), 0.66),
        'foliage_mid': _teal(pal.get('foliage_mid', (58, 110, 84)), 0.62),
        'foliage_top': _teal(pal.get('foliage_top', (96, 150, 116)), 0.60),
        'foliage_accent': _teal(pal.get('foliage_accent', (146, 188, 140)), 0.55),
    }

    # Calligraphic bamboo culms — thin verticals with node ticks + leaf flicks,
    # clumped HARD at the left edge only so the right side (where the pillar pair
    # and the bird's flight lane sit) stays open and uncluttered.
    bdark = foliage['foliage_dark']
    bmid = foliage['foliage_mid']
    btop = foliage['foliage_top']
    for cx0, n_c, scale in ((int(w * 0.06), 5, 1.0),):
        for i in range(n_c):
            x = cx0 + (i - n_c // 2) * 5
            root = bank_y(max(0, min(w, x)))
            ch = int((30 + (i % 3) * 7) * scale)
            top_y = root - ch
            pygame.draw.line(surf, bdark, (x, root), (x + (i % 2), top_y), 2)
            for t in (0.5, 0.74):
                ny = int(root - ch * t)
                pygame.draw.line(surf, bmid, (x - 1, ny), (x + 1, ny), 1)
            pygame.draw.line(surf, bmid, (x, top_y + 5),
                             (x + 6 + (i % 2) * 3, top_y - 2), 1)
            pygame.draw.line(surf, btop, (x, top_y + 9), (x - 5, top_y + 1), 1)

    # Wuling pines as the hero calligraphy — the horizontal peacock-tail reads
    # instantly as shan-shui. Both pines sit on the LEFT third, clear of the
    # pillar pair (x 244-302) and the centre gap so the fringe never crowds the
    # zone the bird flies through.
    fpal = dict(pal)
    fpal.update(foliage)
    px = int(w * 0.20)
    draw_wuling_pine(surf, px, bank_y(px), 42, fpal, lean=11,
                     direction='up', layers=6)
    px2 = int(w * 0.30)
    draw_wuling_pine(surf, px2, bank_y(px2), 26, fpal, lean=-6,
                     direction='up', layers=4)

    # Sparse moss accents dotting the dark bank — tiny brighter foliage flicks,
    # kept off the right pillar zone so that side stays clean.
    rng = random.Random(int(scroll) ^ 0x5135)
    for _ in range(12):
        mx = rng.randint(0, int(w * 0.55))
        my = bank_y(mx) + rng.randint(4, 22)
        pygame.draw.circle(surf, foliage['foliage_mid'], (mx, my), 1)


# ══════════════════════════════════════════════════════════════════════════
# Concept 5 — Mist-Veiled Stone Shore  (thin mass, tall mist veil, ~45px)
# The most restrained: a few weathered sumi-e ink-stone boulders emerging from a
# thick low mist blanket that largely dissolves the ground into negative space
# (the shan-shui "void"). Big rocks surrounding smaller ones, dry-broken edges.
# ══════════════════════════════════════════════════════════════════════════

def fg_mist_veiled_shore(surf, w, gy, h, scroll, pal):
    # Ma Yuan / Xia Gui "one-corner" convention: a dark crisp foreground rock
    # mass dissolving into void. The boulders are pushed one full value/sat step
    # DARKER than the near-ink base so they read unmistakably as the CLOSEST
    # plane (round-1 they sat too light and read as a mid-mountain layer).
    night = _nightf(pal)
    ink = _near_ink(pal)
    # The boulder ink: a full step darker + more saturated than the base near
    # tone, so the rocks are the darkest mass in the frame at every phase.
    rock_ink = _shade(_sat(ink, 1.22), -22)
    rim = _rim_color(pal)
    # Warm golden rim matched to V14's ridge-crest treatment, held warm at night.
    grim = _mix(rim, (255, 214, 150), 0.35 + 0.45 * night)

    # A dark shore strip the boulders sit in — darkened to the frame edge so the
    # foot is solid and the rocks sit IN it, not floating on a flat panel.
    sh = h - gy
    strip = pygame.Surface((w, sh), pygame.SRCALPHA)
    sc_top = _shade(ink, -6)
    sc_bot = _shade(_sat(ink, 1.1), -40)
    for i in range(sh):
        t = i / max(1, sh)
        a = int(255 * min(1.0, 0.55 + t))
        pygame.draw.line(strip, (*_mix(sc_top, sc_bot, t), a), (0, i), (w, i))
    surf.blit(strip, (0, gy))

    # Weathered ink-stone boulders: a few BIG ones with smaller companions
    # nestled around them (classic shan-shui grouping). Slightly larger than
    # round-1 so the mass dominates the closest plane.
    rng = random.Random(0x57043 ^ int(scroll * 0.3))
    groups = [(int(w * 0.20), 1.40), (int(w * 0.55), 1.70), (int(w * 0.83), 1.15)]
    for gx, gs in groups:
        _ink_boulder(surf, gx, gy, gs, rock_ink, grim, rng, night)
        for j in range(rng.randint(1, 2)):
            ox = gx + rng.choice((-1, 1)) * rng.randint(16, 30)
            _ink_boulder(surf, ox, gy, gs * rng.uniform(0.42, 0.64),
                         rock_ink, grim, rng, night)

    # The hero: a THICK low mist blanket swallowing the rock feet and most of the
    # ground into the void. Kept LOWER (y_frac up from 0.97) and lighter at night
    # than round-1 so the dark boulder crowns stay legible after dark instead of
    # dissolving into the void.
    nbands = 5 + int(round(night * 2))
    _base_mist(surf, w, gy, pal, y_frac=0.985, n=nbands,
               alpha=int(54 + 22 * night))
    # One higher faint sheet catching only the boulder feet so the crowns read.
    _base_mist(surf, w, gy, pal, y_frac=0.93, n=2, alpha=int(20 + 12 * night))


def _ink_boulder(surf, cx, base_y, scale, ink, grim, rng, night):
    """A weathered sumi-e ink-stone: a flat-bottomed lump with a dry-broken
    upper contour, the darkest mass in the frame, with a warm GOLDEN rim catch
    riding its whole top edge (V14's ridge-crest treatment one plane closer)."""
    bw = int(20 * scale)
    bh = int(17 * scale)
    cx_l = cx - bw // 2
    cx_r = cx + bw // 2
    top = base_y - bh
    crest = [(cx_l, base_y)]
    steps = max(4, bw // 4)
    for i in range(steps + 1):
        x = cx_l + (cx_r - cx_l) * i / steps
        d = (x - cx) / max(1, bw / 2)
        y = top + (bh * d * d) - rng.randint(0, max(1, int(2 * scale)))
        crest.append((int(x), int(y)))
    crest.append((cx_r, base_y))
    pygame.draw.polygon(surf, ink, crest)
    # Darker base shadow band so the rock sits IN the shore, not on it.
    pygame.draw.polygon(surf, _shade(ink, -16),
                        [(cx_l, base_y), (cx_l, base_y - 3),
                         (cx_r, base_y - 3), (cx_r, base_y)])
    # Warm golden rim catch riding the WHOLE upper contour (not just one
    # shoulder), matching V14's crest highlight — a thin warm under-stroke with
    # a brighter AA line on top so the rock crown stays lit even at night.
    top_edge = crest[1:-1]
    if len(top_edge) >= 2:
        pygame.draw.lines(surf, _shade(grim, -22), False, top_edge, 2)
        pygame.draw.aalines(surf, _mix(grim, (255, 255, 255), 0.35),
                            False, top_edge)
        # A brighter accent on the lit (left) shoulder only.
        lit = top_edge[:max(2, len(top_edge) // 2)]
        if len(lit) >= 2:
            pygame.draw.aalines(surf, _mix(grim, (255, 248, 220), 0.5),
                                False, lit)


# ── registry ──────────────────────────────────────────────────────────────

CONCEPTS = [
    ("Near-Ridge Ink Bank", fg_near_ridge_ink_bank),
    ("Still-Water Inlet", fg_still_water_inlet),
    ("Terraced Paddy Steps", fg_terraced_paddy),
    ("Pine & Bamboo Fringe Bluff", fg_pine_bamboo_bluff),
    ("Mist-Veiled Stone Shore", fg_mist_veiled_shore),
]
