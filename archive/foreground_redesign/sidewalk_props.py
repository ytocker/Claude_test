"""Round-14 SIDEWALK DRESSING — exploration-only props layers for the foreground.

Round 13 dialled in the sidewalk MATERIAL (warm clay / cool grey-taupe running
bond). Round 14 dresses that pavement with promenade furniture: street lamps,
benches, festive lantern/light strings, planters and greenery — a mixed RANGE of
dressing styles, each a `props_<style>(surf, w, gy, h, scroll, pal)` painter
drawn AFTER the floor and BEFORE the gameplay actors.

Everything is assembled from EXISTING game/ primitives (imported read-only) —
the park bench sprite, the paper-lantern head with its built-in warm halo, the
prayer-flag catenary, cascading vines, cairns, side-shrubs — re-tinted per base
and phase. Nothing here is written into game/.

Design contract the props honour:
  * BIRD-LANE CLEARANCE — props read as DECORATION, never an obstacle. Lamp
    HEADS sit no higher than ~y495, props feet at GROUND_Y, and the band behind
    the bird lane (x≈BIRD_X=90) and in front of the pillar (x≈W-116) is kept
    quiet. Props are scroll-locked to world-x so they never jitter or seam.
  * NIGHT GLOW is warm but CAPPED — every lit halo is clamped to luma ≤153
    (NIGHT_LUMA_CAP) and gated to a dark sky via `_is_dark_sky`, so a coin /
    power-up always stays the brightest object in the frame. In daylight the
    lanterns are unlit shells, no additive bloom at all.

Pure-Pygame / pygbag-safe: fill, blit, draw.*, SRCALPHA, BLEND_RGB_ADD only.
No numpy / gfxdraw / per-frame surfarray.
"""
from __future__ import annotations

import math

import pygame

# Read-only imports of the live game's procedural primitives.
from game.ambient import _build_bench_sprite
from game.pillar_variants import (
    draw_prayer_flags, draw_cascading_vine, draw_cairn,
)
from game.draw import draw_side_shrub

# The night-luma contract + dark-sky gate live in the pillar-redesign archive.
import sys as _sys
import pathlib as _pathlib
_sys.path.insert(0, str(_pathlib.Path(__file__).parent.parent / "pillar_redesign"))
from pillar_pagoda_variants import _is_dark_sky  # noqa: E402
from pagoda_ornaments import _clamp_night  # noqa: E402


# ── shared colour helpers (mirror foreground_grounded so tones harmonise) ─────

def _clamp(c):
    return max(0, min(255, int(c)))


def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return (_clamp(a[0] + (b[0] - a[0]) * t),
            _clamp(a[1] + (b[1] - a[1]) * t),
            _clamp(a[2] + (b[2] - a[2]) * t))


def _shade(c, d):
    return (_clamp(c[0] + d), _clamp(c[1] + d), _clamp(c[2] + d))


def _nightf(pal):
    """Continuous 0..1 night-ness off sky_top luma (matches foreground_grounded
    so props cool in lockstep with the floor they sit on)."""
    r, g, b = pal.get('sky_top', (60, 120, 200))
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return max(0.0, min(1.0, (95.0 - lum) / 75.0))


# ── world-anchored placement ──────────────────────────────────────────────────
#
# Props ride the SAME world scroll as the floor painters: a prop pinned to a
# world-x appears at screen-x = (world_x - scroll*mult) % period, so it tracks
# the pavement with no jitter and wraps seamlessly. `mult` matches the near-floor
# parallax the running-bond courses use (~0.20).

GROUND_Y = 595  # sidewalk top edge; props' feet rest here.
PROP_MULT = 0.20


def _world_xs(scroll, w, period, x0, mult=PROP_MULT, margin=70):
    """Yield screen-x for a prop repeated every `period` world-px, anchored at
    world-offset `x0`, scroll-locked. `margin` lets a wide prop spill off-edge
    without popping."""
    phase = scroll * mult
    first = int((phase - margin - x0) // period) - 1
    last = int((phase + w + margin - x0) // period) + 1
    for k in range(first, last + 1):
        sx = int(x0 + k * period - phase)
        if -margin < sx < w + margin:
            yield sx, k


# ── bird-lane quiet zone ──────────────────────────────────────────────────────
#
# Keep the area directly behind the bird (x≈BIRD_X=90) and in front of the
# pillar base (x≈W-116=244) free of tall furniture so nothing reads as an
# obstacle. A prop centred inside these bands is skipped.

_BIRD_LANE = (58, 122)        # around BIRD_X = 90
_PILLAR_LANE = (228, 300)     # around the pillar base x ≈ 244


def _in_quiet_zone(sx, half_w=10):
    for lo, hi in (_BIRD_LANE, _PILLAR_LANE):
        if sx + half_w > lo and sx - half_w < hi:
            return True
    return False


# ── warm lit halo, night-only, capped ────────────────────────────────────────
#
# The single source of festive light. Daylight => no glow. Dark sky => a soft
# additive halo whose colour is clamped to NIGHT_LUMA_CAP so the lamps can never
# out-shine a coin. Strength scales with night-ness for a smooth dusk->night
# fade-in rather than a hard pop.

_GLOW_CACHE: dict = {}

# The additive-glow PEAK is held well under NIGHT_LUMA_CAP so even where a halo
# lands on the brightest lit lantern face, base+halo stays below the coin. The
# RGB itself falls off radially (BLEND_RGB_ADD adds raw RGB, ignoring alpha), so
# a single blit can add at most `peak` and the edges fade cleanly to zero.
_GLOW_PEAK = 92  # < NIGHT_LUMA_CAP (153); keeps lit-face + halo under the coin.


def _warm_glow(radius, color, peak):
    """A cached radial halo for BLEND_RGB_ADD whose RGB falls off to zero at the
    rim. `peak` is the centre add (capped); ratios preserve the warm hue."""
    key = (radius, color, peak)
    g = _GLOW_CACHE.get(key)
    if g is not None:
        return g
    size = radius * 2 + 2
    surf = pygame.Surface((size, size))
    surf.fill((0, 0, 0))
    cx = cy = radius + 1
    mx = max(1, max(color))
    base = tuple(int(peak * c / mx) for c in color)  # warm ratio at centre add
    for r in range(radius, 0, -1):
        f = 1.0 - (r / radius)        # 0 at rim -> 1 at centre
        f = f * f
        col = (int(base[0] * f), int(base[1] * f), int(base[2] * f))
        pygame.draw.circle(surf, col, (cx, cy), r)
    _GLOW_CACHE[key] = surf
    return surf


def _add_lamp_glow(surf, cx, cy, pal, *, radius=16, alpha=120, color=(255, 196, 110)):
    """Blit a capped warm halo at (cx, cy) ONLY when the sky is dark. `alpha`
    scales the peak add (0..~_GLOW_PEAK) so callers keep their relative weights.
    Returns the night strength used (0 in daylight)."""
    if not _is_dark_sky(pal):
        return 0.0
    night = _nightf(pal)
    strength = max(0.0, min(1.0, (night - 0.45) / 0.55))
    if strength <= 0.02:
        return 0.0
    peak = int(min(_GLOW_PEAK, _GLOW_PEAK * (alpha / 120.0)) * strength)
    if peak <= 1:
        return strength
    g = _warm_glow(radius, color, peak)
    surf.blit(g, (cx - radius - 1, cy - radius - 1), special_flags=pygame.BLEND_RGB_ADD)
    return strength


# ── prop primitives built on the game helpers ─────────────────────────────────

def _draw_bench(surf, sx, pal, tint=None):
    """Place the cached 42×28 park-bench sprite with its feet at GROUND_Y,
    optionally re-tinted toward `tint` and cooled toward night."""
    sprite = _build_bench_sprite()
    night = _nightf(pal)
    if tint is not None or night > 0.05:
        sprite = sprite.copy()
        # Value/hue nudge via a full-surface multiply so the wood reads warm clay
        # or cool stone per base, then a cool night wash.
        if tint is not None:
            sprite.fill((*tint, 255), special_flags=pygame.BLEND_RGBA_MULT)
        if night > 0.05:
            k = int(255 * (1 - 0.34 * night))
            kb = int(255 * (1 - 0.28 * night))
            sprite.fill((k, k, kb, 255), special_flags=pygame.BLEND_RGBA_MULT)
    sw, sh = sprite.get_size()
    surf.blit(sprite, (sx - sw // 2, GROUND_Y - sh + 1))


def _draw_planter(surf, sx, pal, *, w=18, kind='shrub', color=None):
    """A small stone/terracotta planter box with greenery, feet at GROUND_Y."""
    night = _nightf(pal)
    box_h = 9
    by = GROUND_Y - 1
    box = color or _mix(pal.get('stone_mid', (150, 132, 110)), (150, 120, 92), 0.5)
    box = _mix(box, (60, 70, 100), 0.30 * night)
    pygame.draw.rect(surf, _shade(box, -18), (sx - w // 2, by - box_h, w, box_h))
    pygame.draw.rect(surf, box, (sx - w // 2 + 1, by - box_h, w - 2, box_h - 2))
    pygame.draw.rect(surf, _shade(box, 16), (sx - w // 2 + 1, by - box_h, w - 2, 2))
    # Greenery rising out of the box — a shrub dome or a small conifer.
    fol = {
        'foliage_dark': _mix(pal.get('foliage_dark', (40, 80, 55)), (40, 56, 86), 0.3 * night),
        'foliage_mid': _mix(pal.get('foliage_mid', (60, 110, 75)), (46, 64, 94), 0.3 * night),
        'foliage_top': _mix(pal.get('foliage_top', (96, 150, 100)), (60, 80, 110), 0.3 * night),
    }
    if kind == 'conifer':
        cy = by - box_h
        gd, gm, gt = fol['foliage_dark'], fol['foliage_mid'], fol['foliage_top']
        for i, (tw, th, dy) in enumerate(((10, 8, 0), (8, 7, 6), (5, 6, 11))):
            ty = cy - 14 + dy
            pygame.draw.polygon(surf, gd, [(sx - tw // 2, ty + th), (sx + tw // 2, ty + th), (sx, ty)])
            pygame.draw.polygon(surf, gm, [(sx - tw // 2 + 1, ty + th), (sx + tw // 2 - 1, ty + th), (sx, ty + 1)])
        pygame.draw.polygon(surf, gt, [(sx - 2, cy - 14 + 3), (sx + 2, cy - 14 + 3), (sx, cy - 16)])
    else:
        draw_side_shrub(surf, sx, by - box_h - 2, fol, scale=1.15)


def _draw_lamp_post(surf, sx, pal, *, style='ornate', height=98, lantern='red'):
    """A slim street-lamp: a dark post topped with a lantern head that carries a
    capped warm glow at night. Head sits at GROUND_Y-height (kept ≥ ~y495 by the
    caller's height budget). `style` switches wrought-iron / stone / minimal."""
    night = _nightf(pal)
    base_y = GROUND_Y - 1
    top_y = base_y - height
    if style == 'stone':
        post = _mix(pal.get('stone_mid', (150, 132, 110)), (120, 110, 96), 0.5)
        pw = 4
    elif style == 'minimal':
        post = _mix((60, 56, 60), (90, 84, 80), 0.4)
        pw = 3
    else:  # ornate wrought-iron
        post = (54, 48, 46)
        pw = 3
    post = _mix(post, (54, 60, 86), 0.32 * night)
    # Footing base.
    pygame.draw.rect(surf, _shade(post, -14), (sx - pw, base_y - 5, pw * 2, 5))
    pygame.draw.rect(surf, _shade(post, 10), (sx - pw, base_y - 5, pw * 2, 1))
    # The shaft.
    pygame.draw.rect(surf, post, (sx - pw // 2, top_y + 6, max(2, pw - 1), height - 6))
    pygame.draw.line(surf, _shade(post, 20), (sx - pw // 2, top_y + 6),
                     (sx - pw // 2, base_y - 5), 1)
    # Ornate scrollwork bracket near the head.
    if style == 'ornate':
        pygame.draw.arc(surf, post, (sx - 9, top_y + 4, 18, 14), math.radians(20), math.radians(160), 2)
        pygame.draw.circle(surf, _shade(post, 14), (sx, top_y + 4), 2)
    # Lantern head — reuse the game's paper-lantern (built-in halo) for festive
    # styles; a cleaner glass box for the minimal/stone lamps.
    if lantern in ('red', 'gold'):
        # The lantern helper already paints its own warm halo; in daylight we
        # knock that halo back by drawing the head first onto a scratch layer and
        # only keeping the bright halo at night. Simpler + still capped: draw the
        # shell, then add our own gated halo.
        _draw_lantern_head(surf, sx, top_y + 8, pal, color=lantern, scale=0.85,
                           glow_radius=12, glow_alpha=64)
    else:
        _draw_glass_head(surf, sx, top_y + 8, pal, style=style)


def _draw_lantern_head(surf, cx, cy, pal, *, color='red', scale=0.85,
                       glow_radius=None, glow_alpha=None):
    """A hanging paper-lantern head with a night-gated, capped warm halo. The
    game's draw_paper_lantern bakes in a bright halo, so in daylight we draw only
    its shell and add our own controlled glow at night. The halo scales DOWN with
    the lantern so a dense garland of small lanterns can't sum its halos into a
    bright band that competes with the coin."""
    night = _nightf(pal)
    dark = (170, 30, 35) if color == 'red' else (190, 140, 40)
    light = (230, 80, 65) if color == 'red' else (245, 210, 100)
    # At night the lit halo is what sells the lantern, so the painted body is
    # dimmed HARD — otherwise a bright gold/red face plus the additive halo on top
    # clips to white and out-shines the coin. Keep the night body under the cap.
    if night > 0.3:
        k = min(1.0, night)
        dark = _mix(dark, _shade(dark, -40), 0.6 * k)
        light = _clamp_night(_mix(light, _shade(light, -55), 0.55 * k))[:3]
    lw, lh = max(8, int(15 * scale)), max(10, int(19 * scale))
    cap = max(2, int(3 * scale))
    body = pygame.Rect(cx - lw // 2, cy + cap - 1, lw, lh - 2 * cap + 2)
    pygame.draw.rect(surf, (55, 35, 25), (cx - lw // 2 + 1, cy, lw - 2, cap))
    pygame.draw.rect(surf, (55, 35, 25), (cx - lw // 2 + 1, cy + lh - cap, lw - 2, cap))
    pygame.draw.ellipse(surf, dark, body)
    pygame.draw.ellipse(surf, light, body.inflate(-max(2, int(3 * scale)), -max(1, int(2 * scale))))
    # Capped warm halo only when dark — tight so the lantern reads lit-from-within
    # rather than washing the sky behind it.
    gr = glow_radius if glow_radius is not None else max(7, int(11 * scale))
    ga = glow_alpha if glow_alpha is not None else 70
    _add_lamp_glow(surf, cx, cy + lh // 2, pal, radius=gr, alpha=ga,
                   color=(255, 150, 110) if color == 'red' else (255, 205, 120))


def _draw_glass_head(surf, cx, cy, pal, *, style='minimal'):
    """A clean four-pane glass lantern head for the refined/stone lamps."""
    night = _nightf(pal)
    frame = _mix((50, 46, 48), (80, 76, 72), 0.4)
    frame = _mix(frame, (54, 60, 86), 0.3 * night)
    glass_day = _mix(pal.get('horizon', (250, 226, 184)), (210, 220, 230), 0.5)
    lit = _clamp_night((255, 210, 150))[:3] if _is_dark_sky(pal) else glass_day
    gw, gh = 11, 14
    box = pygame.Rect(cx - gw // 2, cy, gw, gh)
    # Cap.
    pygame.draw.polygon(surf, frame, [(cx - gw // 2 - 2, cy), (cx + gw // 2 + 2, cy), (cx, cy - 6)])
    pygame.draw.rect(surf, _mix(lit, glass_day, 0.25), box)
    pygame.draw.rect(surf, frame, box, 1)
    pygame.draw.line(surf, frame, (cx, cy), (cx, cy + gh), 1)
    pygame.draw.line(surf, frame, (cx - gw // 2, cy + gh // 2), (cx + gw // 2, cy + gh // 2), 1)
    pygame.draw.rect(surf, frame, (cx - 2, cy + gh, 4, 3))
    _add_lamp_glow(surf, cx, cy + gh // 2, pal, radius=12, alpha=68,
                   color=(255, 208, 150))


def _catenary_pts(x1, x2, top_y, sag, steps):
    """A quadratic sag arc from (x1,top_y) to (x2,top_y) dipping `sag` at centre."""
    mx = (x1 + x2) * 0.5
    my = top_y + sag
    out = []
    for i in range(steps + 1):
        t = i / steps
        bx = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * mx + t * t * x2
        by = (1 - t) ** 2 * top_y + 2 * (1 - t) * t * my + t * t * top_y
        out.append((bx, by))
    return out


def _garland_spans(scroll, w, period, x0, mult=PROP_MULT):
    """Yield (x_left, x_right) screen spans for a festive strand repeated every
    `period` world-px, scroll-locked, so the bunting wraps seamlessly across the
    whole promenade regardless of which posts happen to be on screen."""
    phase = scroll * mult
    first = int((phase - x0) // period) - 1
    last = int((phase + w - x0) // period) + 1
    for k in range(first, last + 1):
        xl = x0 + k * period - phase
        xr = xl + period
        if xr > -10 and xl < w + 10:
            yield xl, xr


def _draw_lantern_garland(surf, w, scroll, pal, *, top_y, period=120, sag=24,
                          per_span=3, colors=('red', 'gold')):
    """A self-contained, world-anchored strand of paper lanterns slung in
    repeating catenary spans across the whole pavement. Each lantern carries a
    capped night halo; the rope sags on a quadratic arc between hook points a
    `period` apart, so it reads as continuous festive bunting independent of the
    lamp posts."""
    night = _nightf(pal)
    rope = _mix((62, 52, 44), (40, 44, 60), 0.3 * night)
    for xl, xr in _garland_spans(scroll, w, period, x0=12):
        pts = _catenary_pts(xl, xr, top_y, sag, 16)
        pygame.draw.lines(surf, rope, False, [(int(x), int(y)) for x, y in pts], 1)
        for j in range(per_span):
            t = (j + 0.5) / per_span
            bx = (1 - t) ** 2 * xl + 2 * (1 - t) * t * ((xl + xr) * 0.5) + t * t * xr
            by = (1 - t) ** 2 * top_y + 2 * (1 - t) * t * (top_y + sag) + t * t * top_y
            _draw_lantern_head(surf, int(bx), int(by), pal,
                               color=colors[j % len(colors)], scale=0.6,
                               glow_radius=7, glow_alpha=52)


def _draw_fairy_lights(surf, w, scroll, pal, *, top_y, period=130, sag=22, per_span=8):
    """Warm fairy-light bunting: a fine wire catenary studded with tiny bulbs,
    repeating in world-anchored spans across the pavement. Bulbs are unlit beads
    by day; at night each gets a capped warm point plus a soft shared halo."""
    night = _nightf(pal)
    wire = _mix((72, 66, 60), (44, 48, 64), 0.3 * night)
    dark = _is_dark_sky(pal)
    warm = (240, 196, 120)
    bead = _mix(warm, (120, 110, 96), 0.55)
    for xl, xr in _garland_spans(scroll, w, period, x0=8):
        pts = _catenary_pts(xl, xr, top_y, sag, 22)
        pygame.draw.lines(surf, wire, False, [(int(x), int(y)) for x, y in pts], 1)
        for j in range(per_span):
            t = (j + 0.5) / per_span
            bx = int((1 - t) ** 2 * xl + 2 * (1 - t) * t * ((xl + xr) * 0.5) + t * t * xr)
            by = int((1 - t) ** 2 * top_y + 2 * (1 - t) * t * (top_y + sag) + t * t * top_y) + 2
            if dark:
                lit = _clamp_night(warm)[:3]
                pygame.draw.circle(surf, lit, (bx, by), 2)
                _add_lamp_glow(surf, bx, by, pal, radius=5, alpha=48, color=warm)
            else:
                pygame.draw.circle(surf, bead, (bx, by), 1)


def _draw_prayer_strand(surf, w, scroll, pal, *, period, x0, y):
    """World-anchored prayer-flag bunting spans, night-dimmed so the fixed bright
    flag colours (the game helper includes a near-white) never out-shine a coin."""
    night = _nightf(pal)
    layer = pygame.Surface((w, GROUND_Y), pygame.SRCALPHA)
    for xl, xr in _garland_spans(scroll, w, period, x0=x0):
        draw_prayer_flags(layer, int(xl), y, int(xr), y, n=6)
    if night > 0.05:
        k = int(255 * (1 - 0.42 * night))
        kb = int(255 * (1 - 0.34 * night))
        layer.fill((k, k, kb, 255), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(layer, (0, 0))


def _draw_wreath(surf, cx, cy, pal):
    """A small evergreen wreath with a red bow, for a lamp post."""
    night = _nightf(pal)
    gd = _mix((36, 78, 50), (40, 56, 86), 0.3 * night)
    gm = _mix((60, 116, 70), (46, 64, 94), 0.3 * night)
    pygame.draw.circle(surf, gd, (cx, cy), 8, 4)
    pygame.draw.circle(surf, gm, (cx, cy), 8, 2)
    for a in range(0, 360, 45):
        bx = cx + int(math.cos(math.radians(a)) * 8)
        by = cy + int(math.sin(math.radians(a)) * 8)
        pygame.draw.circle(surf, gm, (bx, by), 2)
    # Little red berries + bow.
    red = _mix((190, 50, 45), (90, 60, 80), 0.25 * night)
    for a in (40, 150, 250):
        bx = cx + int(math.cos(math.radians(a)) * 8)
        by = cy + int(math.sin(math.radians(a)) * 8)
        pygame.draw.circle(surf, red, (bx, by), 1)
    pygame.draw.polygon(surf, red, [(cx - 3, cy + 8), (cx, cy + 6), (cx + 3, cy + 8), (cx, cy + 11)])


def _draw_cairn(surf, sx, pal):
    night = _nightf(pal)
    # draw_cairn uses fixed warm stone tones; layer a soft night cool wash shaped
    # as overlapping stacked ellipses (not a visible rectangle) so the stones cool
    # with the stage without a hard box edge.
    draw_cairn(surf, sx, GROUND_Y - 1, n=3)
    if night > 0.1:
        a = int(58 * night)
        wash = pygame.Surface((20, 20), pygame.SRCALPHA)
        for (ew, eh, dy) in ((16, 7, 13), (12, 5, 8), (8, 4, 4)):
            pygame.draw.ellipse(wash, (44, 54, 84, a), (10 - ew // 2, dy, ew, eh))
        surf.blit(wash, (sx - 10, GROUND_Y - 21))


def _draw_vine_trail(surf, sx, pal):
    """A short cascading vine spilling onto the sidewalk (e.g. off a planter)."""
    night = _nightf(pal)
    fol = {
        'foliage_dark': _mix(pal.get('foliage_dark', (40, 80, 55)), (40, 56, 86), 0.3 * night),
        'foliage_mid': _mix(pal.get('foliage_mid', (60, 110, 75)), (46, 64, 94), 0.3 * night),
        'foliage_top': _mix(pal.get('foliage_top', (96, 150, 100)), (60, 80, 110), 0.3 * night),
    }
    draw_cascading_vine(surf, sx, GROUND_Y - 16, 14, fol)


# ══════════════════════════════════════════════════════════════════════════
# Style rows. Each lays a coherent set of furniture across the pavement,
# world-anchored, clearing the bird + pillar lanes.
# ══════════════════════════════════════════════════════════════════════════

# A clay-vs-stone bench tint, so the wood warms on terracotta and cools on the
# grey-taupe paver. None => the sprite's own warm wood.
def _bench_tint(pal):
    return None


def props_temple_festival(surf, w, gy, h, scroll, pal):
    """Ornate wrought-iron lamp posts + a red/gold paper-lantern garland strung
    between them + a prayer-flag bunting + a stone bench + a planter."""
    period = 250
    # The festive strands are world-anchored across the whole pavement so they
    # read continuously; the lamp posts are placed where the bird/pillar lanes
    # are clear and act as visual hook points beneath the bunting.
    _draw_lantern_garland(surf, w, scroll, pal, top_y=GROUND_Y - 100, period=118,
                          sag=24, per_span=3)
    for sx, k in _world_xs(scroll, w, period, x0=20):
        if not _in_quiet_zone(sx, 6):
            _draw_lamp_post(surf, sx, pal, style='ornate', height=100, lantern='red')
    for sx, k in _world_xs(scroll, w, period, x0=170):
        if not _in_quiet_zone(sx, 6):
            _draw_lamp_post(surf, sx, pal, style='ornate', height=92, lantern='gold')
    # Prayer-flag bunting on a second, lower world-anchored strand. The game
    # helper paints fixed bright flag colours (incl. a near-white), so at night
    # the whole strand is rendered to a scratch layer and value-dimmed — a bright
    # white flag would otherwise out-shine the coin.
    _draw_prayer_strand(surf, w, scroll, pal, period=150, x0=70, y=GROUND_Y - 70)
    # Bench + planter on offset anchors.
    for sx, k in _world_xs(scroll, w, period, x0=95):
        if not _in_quiet_zone(sx, 22):
            _draw_bench(surf, sx, pal, tint=_bench_tint(pal))
    for sx, k in _world_xs(scroll, w, period, x0=215):
        if not _in_quiet_zone(sx, 12):
            _draw_planter(surf, sx, pal, kind='shrub')


def props_holiday_lights(surf, w, gy, h, scroll, pal):
    """A warm fairy-light bunting + a wreathed minimal post + a classic park
    bench + potted mini-evergreens."""
    period = 240
    _draw_fairy_lights(surf, w, scroll, pal, top_y=GROUND_Y - 96, period=128, sag=20)
    for sx, k in _world_xs(scroll, w, period, x0=30):
        if not _in_quiet_zone(sx, 6):
            _draw_lamp_post(surf, sx, pal, style='minimal', height=98, lantern='glass')
            _draw_wreath(surf, sx, GROUND_Y - 70, pal)
    for sx, k in _world_xs(scroll, w, period, x0=180):
        if not _in_quiet_zone(sx, 6):
            _draw_lamp_post(surf, sx, pal, style='minimal', height=88, lantern='glass')
    for sx, k in _world_xs(scroll, w, period, x0=110):
        if not _in_quiet_zone(sx, 22):
            _draw_bench(surf, sx, pal, tint=_bench_tint(pal))
    for sx, k in _world_xs(scroll, w, period, x0=205):
        if not _in_quiet_zone(sx, 12):
            _draw_planter(surf, sx, pal, kind='conifer')


def props_serene_garden(surf, w, gy, h, scroll, pal):
    """Minimal festivity: a dim stone lamp post + planters + a cascading vine +
    a cairn + a bench. Natural, contemplative."""
    period = 260
    for sx, k in _world_xs(scroll, w, period, x0=24):
        if _in_quiet_zone(sx, 6):
            continue
        _draw_lamp_post(surf, sx, pal, style='stone', height=86, lantern='glass')
    for sx, k in _world_xs(scroll, w, period, x0=150):
        if not _in_quiet_zone(sx, 12):
            _draw_planter(surf, sx, pal, kind='shrub')
            _draw_vine_trail(surf, sx + 11, pal)
    for sx, k in _world_xs(scroll, w, period, x0=195):
        if not _in_quiet_zone(sx, 10):
            _draw_cairn(surf, sx, pal)
    for sx, k in _world_xs(scroll, w, period, x0=100):
        if not _in_quiet_zone(sx, 22):
            _draw_bench(surf, sx, pal, tint=_bench_tint(pal))


def props_elegant_minimal(surf, w, gy, h, scroll, pal):
    """Sparse + refined: ONE ornate lamp post per period + a bench + a touch of
    greenery."""
    period = 300
    for sx, k in _world_xs(scroll, w, period, x0=40):
        if not _in_quiet_zone(sx, 6):
            _draw_lamp_post(surf, sx, pal, style='ornate', height=96, lantern='glass')
    for sx, k in _world_xs(scroll, w, period, x0=160):
        if not _in_quiet_zone(sx, 22):
            _draw_bench(surf, sx, pal, tint=_bench_tint(pal))
    for sx, k in _world_xs(scroll, w, period, x0=210):
        if not _in_quiet_zone(sx, 12):
            _draw_planter(surf, sx, pal, kind='shrub')


def props_the_works(surf, w, gy, h, scroll, pal):
    """The fully-dressed promenade: lamp posts + a lantern garland + a bench +
    planters + a flag — dense but balanced, the likely shippable target."""
    period = 230
    _draw_lantern_garland(surf, w, scroll, pal, top_y=GROUND_Y - 98, period=112,
                          sag=22, per_span=3)
    for sx, k in _world_xs(scroll, w, period, x0=18):
        if not _in_quiet_zone(sx, 6):
            _draw_lamp_post(surf, sx, pal, style='ornate', height=98, lantern='red')
    for sx, k in _world_xs(scroll, w, period, x0=152):
        if not _in_quiet_zone(sx, 6):
            _draw_lamp_post(surf, sx, pal, style='ornate', height=90, lantern='gold')
    for sx, k in _world_xs(scroll, w, period, x0=92):
        if not _in_quiet_zone(sx, 22):
            _draw_bench(surf, sx, pal, tint=_bench_tint(pal))
    for sx, k in _world_xs(scroll, w, period, x0=200):
        if not _in_quiet_zone(sx, 12):
            _draw_planter(surf, sx, pal, kind='conifer')
    for sx, k in _world_xs(scroll, w, period, x0=128):
        if not _in_quiet_zone(sx, 8):
            _draw_cairn(surf, sx, pal)


# Style rows in render order. (label, painter)
STYLES_R14 = [
    ("Temple Festival", props_temple_festival),
    ("Holiday Lights", props_holiday_lights),
    ("Serene Garden", props_serene_garden),
    ("Elegant Minimal", props_elegant_minimal),
    ("The Works", props_the_works),
]
