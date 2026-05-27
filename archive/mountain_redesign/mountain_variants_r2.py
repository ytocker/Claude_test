"""Round-2 background exploration — refined V2/V4 plus five "go wild" concepts.

Round 1 stayed strictly on the mountain theme; the brief for round 2 is "a
really cool background that fits the game atmosphere — go wild". So beyond the
two refined dune/ink ranges, the new concepts are free-form mid-background
forms (floating islands, crystal spires, glowing canyons, aurora ridges, a
distant skyline) — but each keeps the live ``draw_mountains`` contract so the
winner drops straight into the world::

    def variant(surf, scroll, ground_y, w, far_color, near_color)

Every colour is still derived from the biome palette (the two passed mountain
tones, plus a few extra keys pulled from ``game.biome`` for richer mid-tones)
so the whole set re-themes across the day cycle instead of hard-coding a look.
We keep the three-layer parallax read (≈0.06 / 0.15 / 0.28) wherever the form
allows, and lean on translucent haze for atmospheric depth.

Fidelity bump over round 1: ridge sampling steps 1px (was 2), gradients are
built per-band, and crest strokes are drawn so they stay crisp at full size —
the round-1 sheet read low-res because it down-sampled to half tiles.
"""
from __future__ import annotations

import math
import random

import pygame

from game import biome as _biome


# ── shared colour + geometry helpers ─────────────────────────────────────────

def _clamp(c):
    return max(0, min(255, int(c)))


def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return (_clamp(a[0] + (b[0] - a[0]) * t),
            _clamp(a[1] + (b[1] - a[1]) * t),
            _clamp(a[2] + (b[2] - a[2]) * t))


def _shade(c, d):
    return (_clamp(c[0] + d), _clamp(c[1] + d), _clamp(c[2] + d))


def _luma(c) -> float:
    return (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) / 255.0


def _sat(c, f):
    """Scale saturation around the colour's own luma — f>1 vivid, f<1 muted."""
    g = _luma(c) * 255.0
    return (_clamp(g + (c[0] - g) * f),
            _clamp(g + (c[1] - g) * f),
            _clamp(g + (c[2] - g) * f))


def _back_color(far):
    return (_clamp((far[0] + 200) // 2),
            _clamp((far[1] + 210) // 2),
            _clamp((far[2] + 230) // 2))


def _haze(far, near):
    return _mix(far, (235, 238, 248), 0.55)


def _ridge(w, ground_y, scroll, speed, base_h, terms, step=1):
    """Sampled ridgeline summed from sine terms. step=1 keeps crests smooth at
    full 360px width (round 1 used step=2 and read jaggy when scaled)."""
    pts = [(0, ground_y)]
    heights: list[tuple[int, int]] = []
    for x in range(0, w + 1, step):
        sx = x + scroll * speed
        h = base_h
        for freq, amp, ph in terms:
            h += math.sin(sx * freq + ph) * amp
        y = ground_y - int(h)
        pts.append((x, y))
        heights.append((x, y))
    pts.append((w, ground_y))
    return pts, heights


def _haze_band(surf, heights, ground_y, color, top_alpha, depth):
    if not heights:
        return
    top = min(y for _, y in heights)
    band = pygame.Surface((surf.get_width(), depth), pygame.SRCALPHA)
    for i in range(depth):
        a = int(top_alpha * (1.0 - i / depth))
        if a <= 0:
            continue
        pygame.draw.line(band, (color[0], color[1], color[2], a),
                         (0, i), (surf.get_width(), i))
    surf.blit(band, (0, max(0, top - depth // 3)))


def _aa_crest(surf, heights, color, width=1):
    """Anti-aliased ridge stroke where it's cheap (native+WASM both support
    aaline). Falls back gracefully if the segment list is short."""
    if len(heights) < 2:
        return
    pygame.draw.aalines(surf, color, False, heights)
    if width > 1:
        pygame.draw.lines(surf, color, False, heights, width)


def _gradient_fill(surf, heights, ground_y, top_col, bot_col, ease=1.0):
    """Vertical gradient clipped under a ridge silhouette. One reusable body
    builder so every concept gets a real per-band gradient, not a flat fill."""
    w = surf.get_width()
    top = min(y for _, y in heights)
    depth = ground_y - top
    if depth <= 0:
        return top, depth
    body = pygame.Surface((w, depth), pygame.SRCALPHA)
    for i in range(depth):
        t = (i / max(1, depth)) ** ease
        pygame.draw.line(body, _mix(top_col, bot_col, t), (0, i), (w, i))
    poly = [(0, depth)] + [(x, y - top) for x, y in heights] + [(w, depth)]
    mask = pygame.Surface((w, depth), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(body, (0, top))
    return top, depth


# ══════════════════════════════════════════════════════════════════════════
# V2 — Wind-Sculpted Dunes (REFINED)
# Richer multi-tone sand: each dune face runs a crest→trough gradient through
# rose / gold / amber / mauve stops keyed off the biome tone, with a smooth
# lit-windward / shadowed-slip-face split and finer wind-ripple striations.
# ══════════════════════════════════════════════════════════════════════════

def _sand_ramp(base):
    """Five-stop sand ramp from a single biome tone. Highlights push toward
    warm gold, mids hold the biome hue, shadows fall into a cool mauve so the
    dunes read as lit sand rather than one muddy brown — the colour the user
    asked for. Each stop stays tinted by ``base`` so it re-themes at night."""
    crest = _mix(base, (255, 236, 188), 0.62)        # sun-struck crest, gold
    upper = _mix(base, (244, 196, 150), 0.40)         # warm amber upper face
    mid = _mix(base, (215, 150, 130), 0.18)           # rose body
    lower = _shade(_mix(base, (120, 95, 130), 0.30), -10)  # mauve trough
    shadow = _shade(_mix(base, (70, 55, 95), 0.35), -22)   # cool slip-face shade
    return crest, upper, mid, lower, shadow


def _dune_layer(surf, heights, ground_y, ramp, crest_bias, ripple_density):
    crest, upper, mid, lower, shadow = ramp
    w = surf.get_width()
    top = min(y for _, y in heights)
    depth = ground_y - top
    if depth <= 0:
        return
    # Multi-stop vertical gradient: crest→upper→mid→lower→shadow. A small set
    # of stops interpolated by depth gives the rose/gold/amber/mauve banding.
    stops = [crest, upper, mid, lower, shadow]
    body = pygame.Surface((w, depth), pygame.SRCALPHA)
    for i in range(depth):
        t = i / max(1, depth)
        seg = t * (len(stops) - 1)
        k = min(len(stops) - 2, int(seg))
        col = _mix(stops[k], stops[k + 1], seg - k)
        pygame.draw.line(body, col, (0, i), (w, i))
    poly = [(0, depth)] + [(x, y - top) for x, y in heights] + [(w, depth)]
    mask = pygame.Surface((w, depth), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(body, (0, top))

    # Smooth lit/shadow split along the crest: descending-right slopes catch
    # the sun (bright crest line), ascending slopes fall into slip-face shade.
    for i in range(1, len(heights)):
        x0, y0 = heights[i - 1]
        x1, y1 = heights[i]
        if (y1 - y0) > crest_bias:
            pygame.draw.aaline(surf, crest, (x0, y0), (x1, y1))
        else:
            pygame.draw.aaline(surf, _mix(mid, shadow, 0.45), (x0, y0), (x1, y1))

    # Fine wind-ripple striations — short, near-horizontal strokes hugging the
    # contour. Denser + finer than round 1 for a sculpted-sand read.
    rng = random.Random(top * 131 + depth)
    for _ in range(int(w * ripple_density)):
        idx = rng.randrange(0, len(heights) - 1)
        x, y = heights[idx]
        ry = y + rng.randint(4, max(5, depth - 4))
        if ry < ground_y - 2:
            length = rng.randint(4, 11)
            tone = _mix(mid, upper, rng.uniform(0.2, 0.6))
            pygame.draw.aaline(surf, tone, (x - length, ry + 1), (x, ry))


def draw_mountains_v2(surf, scroll, ground_y, w, far_color=None, near_color=None):
    far = far_color or (120, 100, 130)
    near = near_color or (90, 70, 95)
    back = _back_color(far)
    haze = _haze(far, near)

    pts, hb = _ridge(w, ground_y, scroll, 0.06, 92,
                     [(0.009, 20, 0.3), (0.021, 9, 1.7), (0.05, 3, 0.9)])
    _dune_layer(surf, hb, ground_y, _sand_ramp(_mix(back, far, 0.5)),
                crest_bias=1, ripple_density=0.05)
    _haze_band(surf, hb, ground_y, haze, 150, 26)

    pts, hf = _ridge(w, ground_y, scroll, 0.15, 66,
                     [(0.012, 26, 1.0), (0.027, 11, 0.4), (0.06, 4, 2.1)])
    _dune_layer(surf, hf, ground_y, _sand_ramp(far),
                crest_bias=0, ripple_density=0.07)
    _haze_band(surf, hf, ground_y, haze, 80, 16)

    pts, hn = _ridge(w, ground_y, scroll, 0.28, 46,
                     [(0.016, 20, 0.5), (0.034, 8, 2.2), (0.07, 4, 1.3)])
    _dune_layer(surf, hn, ground_y, _sand_ramp(near),
                crest_bias=-1, ripple_density=0.09)


# ══════════════════════════════════════════════════════════════════════════
# V4 — Shan-Shui Ink Ridges (REFINED)
# Layered washes, but each ridge layer now carries a distinct theme-matched
# colour wash (cool/violet far → warm/saturated near) instead of near-mono
# grey, with crisper, brighter fog veils opening the gaps between layers.
# ══════════════════════════════════════════════════════════════════════════

def _ink_wash(surf, heights, ground_y, ink_top, ink_bot, alpha_top, fade):
    """Translucent wash, densest + most saturated at the crest, dissolving and
    cooling toward the base. Two-colour so each layer reads as tinted ink."""
    w = surf.get_width()
    top = min(y for _, y in heights)
    depth = ground_y - top
    if depth <= 0:
        return
    wash = pygame.Surface((w, depth), pygame.SRCALPHA)
    for i in range(depth):
        t = i / max(1, depth)
        a = int(alpha_top * (1.0 - t) ** fade)
        if a <= 0:
            continue
        col = _mix(ink_top, ink_bot, t)
        pygame.draw.line(wash, (col[0], col[1], col[2], a), (0, i), (w, i))
    poly = [(0, depth)] + [(x, y - top) for x, y in heights] + [(w, depth)]
    mask = pygame.Surface((w, depth), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
    wash.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(wash, (0, top))
    # Calligraphic crest stroke — a darker, saturated brush edge, AA'd.
    _aa_crest(surf, heights, _shade(_sat(ink_top, 1.2), -28))


def draw_mountains_v4(surf, scroll, ground_y, w, far_color=None, near_color=None):
    pal = _biome.palette_for_phase(_PHASE)
    far = far_color or pal['mtn_far']
    near = near_color or pal['mtn_near']
    horizon = pal['horizon']
    haze = _mix(_haze(far, near), horizon, 0.35)

    # Far layers lean cool/atmospheric toward the horizon tint; near layers get
    # the saturated biome ink. Each (speed, base_h, alpha, top_ink, bot_ink).
    far_tint = _mix(far, horizon, 0.45)
    specs = [
        (0.05, 104, 120, _mix(far_tint, (235, 238, 248), 0.30), far_tint),
        (0.08, 92, 145, _mix(far_tint, far, 0.6), _mix(far_tint, haze, 0.5)),
        (0.13, 80, 170, _sat(far, 1.15), _mix(far, haze, 0.45)),
        (0.20, 66, 200, _sat(_mix(near, far, 0.4), 1.2), _mix(near, far, 0.5)),
        (0.28, 50, 230, _sat(near, 1.25), _mix(near, far, 0.3)),
    ]
    for k, (speed, base_h, atop, itop, ibot) in enumerate(specs):
        pts, h = _ridge(w, ground_y, scroll, speed, base_h,
                        [(0.011 + k * 0.002, 22 - k * 2, 0.6 + k),
                         (0.030 + k * 0.004, 10, 1.5 - k * 0.3)])
        _ink_wash(surf, h, ground_y, itop, ibot, atop, fade=1.6)
        if k < len(specs) - 1:
            # Brighter, crisper fog veil keyed off the horizon glow.
            veil = _mix(haze, horizon, 0.4)
            _haze_band(surf, h, ground_y, veil, 95, 24)


# ══════════════════════════════════════════════════════════════════════════
# NEW 1 — Floating Sky Islands
# Drifting chunks of land at three parallax depths, each with a grass-lit cap,
# a rocky underbelly tapering to a point, and a few hanging roots/vines. Caps
# borrow the biome foliage tones; rock borrows the mountain tones.
# ══════════════════════════════════════════════════════════════════════════

def _island(surf, cx, cy, scale, rock_hi, rock_lo, grass_hi, grass_lo, rim, rng):
    """One floating island: elliptical grassy top + downward rocky spike."""
    rw = int(34 * scale)
    grass_h = int(11 * scale)
    spike_h = int(40 * scale)
    # Rocky underbelly — irregular downward wedge, faceted.
    base_y = cy + grass_h // 2
    left = (cx - rw, base_y)
    right = (cx + rw, base_y)
    tip = (cx + rng.randint(-6, 6), base_y + spike_h)
    mid_l = (cx - rw // 2, base_y + spike_h // 2 + rng.randint(-4, 4))
    mid_r = (cx + rw // 2, base_y + spike_h // 2 + rng.randint(-4, 4))
    rock = [left, mid_l, tip, mid_r, right]
    pygame.draw.polygon(surf, rock_lo, rock)
    # Lit left facet of the rock.
    pygame.draw.polygon(surf, rock_hi, [left, mid_l, tip])
    pygame.draw.aalines(surf, _shade(rock_lo, -18), False, rock)
    # Grassy cap — flattened ellipse sitting on the rock shoulders.
    cap = pygame.Rect(cx - rw, cy - grass_h, rw * 2, grass_h * 2)
    pygame.draw.ellipse(surf, grass_lo, cap)
    pygame.draw.ellipse(surf, grass_hi,
                        pygame.Rect(cx - rw, cy - grass_h, rw * 2, grass_h + 2))
    pygame.draw.arc(surf, rim, cap, math.pi, math.tau, 2)
    # Hanging roots/vines from the underbelly.
    for _ in range(int(2 + scale * 2)):
        vx = cx + rng.randint(-rw + 4, rw - 4)
        vy = base_y + rng.randint(2, 6)
        pygame.draw.line(surf, _mix(rock_lo, grass_lo, 0.4),
                         (vx, vy), (vx + rng.randint(-2, 2),
                                    vy + int(rng.randint(8, 18) * scale)), 1)


def _island_band(surf, w, ground_y, scroll, speed, y_base, scale, spacing,
                 rock_hi, rock_lo, grass_hi, grass_lo, rim, seed):
    phase = scroll * speed
    k0 = int(phase // spacing) - 1
    for k in range(k0, k0 + int(w / spacing) + 3):
        rng = random.Random((k * 374761393 ^ seed) & 0xFFFFFFFF)
        x = int(k * spacing - phase) + rng.randint(-12, 12)
        if -60 < x < w + 60:
            y = y_base + rng.randint(-18, 18)
            s = scale * rng.uniform(0.78, 1.18)
            _island(surf, x, y, s, rock_hi, rock_lo, grass_hi, grass_lo, rim, rng)


def draw_mountains_islands(surf, scroll, ground_y, w, far_color=None, near_color=None):
    pal = _biome.palette_for_phase(_PHASE)
    far = far_color or pal['mtn_far']
    near = near_color or pal['mtn_near']
    g_top = pal['foliage_top']
    g_mid = pal['foliage_mid']
    haze = _haze(far, near)

    # BACK band — small, hazy, high.
    _island_band(surf, w, ground_y, scroll, 0.06, ground_y - 150, 0.7, 150,
                 _mix(far, (255, 240, 210), 0.25), _mix(far, near, 0.4),
                 _mix(g_top, far, 0.45), _mix(g_mid, far, 0.5),
                 _mix(g_top, (255, 255, 255), 0.3), 17)
    # FAR band.
    _island_band(surf, w, ground_y, scroll, 0.15, ground_y - 95, 0.95, 132,
                 _mix(far, (255, 235, 200), 0.3), far,
                 _mix(g_top, far, 0.2), g_mid,
                 _mix(g_top, (255, 255, 255), 0.4), 41)
    # NEAR band — largest, most saturated, lowest.
    _island_band(surf, w, ground_y, scroll, 0.28, ground_y - 40, 1.25, 150,
                 _mix(near, (255, 225, 180), 0.35), near,
                 _mix(g_top, pal['foliage_accent'], 0.2), g_mid,
                 _shade(g_top, 30), 73)


# ══════════════════════════════════════════════════════════════════════════
# NEW 2 — Crystal / Geode Spires
# Clusters of tall faceted crystal shards rising from the horizon, each shard a
# two-tone facet split with an emissive inner glow and a bright rim. Glow hue
# borrows the biome accent so it blooms warm by day and electric at night.
# ══════════════════════════════════════════════════════════════════════════

def _crystal_cluster(surf, cx, base_y, h, lit, dark, glow, rim, rng):
    """A fan of 3–5 shards sharing a base, tallest in the middle."""
    n = rng.randint(3, 5)
    for i in range(n):
        off = (i - (n - 1) / 2.0)
        sh = int(h * (1.0 - abs(off) * rng.uniform(0.16, 0.26)))
        bx = cx + int(off * h * 0.16)
        top = (bx + rng.randint(-3, 3), base_y - sh)
        half = max(3, int(sh * rng.uniform(0.12, 0.18)))
        bl = (bx - half, base_y)
        br = (bx + half, base_y)
        # Split facet: left lit, right shadow, meeting at a centre ridge.
        ridge_b = (bx, base_y)
        pygame.draw.polygon(surf, lit, [top, bl, ridge_b])
        pygame.draw.polygon(surf, dark, [top, br, ridge_b])
        # Emissive core: a thin bright sliver up the centre ridge.
        pygame.draw.aaline(surf, glow, (bx, base_y), top)
        pygame.draw.aaline(surf, rim, top, bl)
        # Soft glow halo at the tip.
        halo = pygame.Surface((half * 4, half * 4), pygame.SRCALPHA)
        for r in range(half * 2, 0, -2):
            a = int(70 * (1 - r / (half * 2)))
            pygame.draw.circle(halo, (glow[0], glow[1], glow[2], a),
                               (half * 2, half * 2), r)
        surf.blit(halo, (top[0] - half * 2, top[1] - half * 2),
                  special_flags=pygame.BLEND_RGBA_ADD)


def _crystal_band(surf, w, ground_y, scroll, speed, y_base, h, spacing,
                  lit, dark, glow, rim, seed):
    phase = scroll * speed
    k0 = int(phase // spacing) - 1
    for k in range(k0, k0 + int(w / spacing) + 3):
        rng = random.Random((k * 2246822519 ^ seed) & 0xFFFFFFFF)
        x = int(k * spacing - phase) + rng.randint(-18, 18)
        if -50 < x < w + 50:
            ch = int(h * rng.uniform(0.7, 1.15))
            _crystal_cluster(surf, x, y_base + rng.randint(-6, 6), ch,
                             lit, dark, glow, rim, rng)


def draw_mountains_crystal(surf, scroll, ground_y, w, far_color=None, near_color=None):
    pal = _biome.palette_for_phase(_PHASE)
    far = far_color or pal['mtn_far']
    near = near_color or pal['mtn_near']
    accent = pal['stone_accent']
    haze = _haze(far, near)
    # Emissive glow hue: blend the warm accent toward an electric cyan/magenta
    # so it pops at night; biome accent keeps it warm by day.
    glow = _mix(accent, (140, 230, 255), 0.45)
    glow = _sat(glow, 1.3)

    # A dark, hazy ridge base so the crystals have something to grow out of.
    pts, hb = _ridge(w, ground_y, scroll, 0.06, 60, [(0.01, 14, 0.5)])
    _gradient_fill(surf, hb, ground_y, _mix(far, haze, 0.5), far, ease=1.2)
    _haze_band(surf, hb, ground_y, haze, 130, 22)

    _crystal_band(surf, w, ground_y, scroll, 0.06, ground_y - 60, 70, 150,
                  _mix(far, glow, 0.3), _mix(far, near, 0.55),
                  _mix(glow, (255, 255, 255), 0.2), _mix(glow, (255, 255, 255), 0.5), 17)
    _haze_band(surf, hb, ground_y, haze, 70, 16)
    _crystal_band(surf, w, ground_y, scroll, 0.15, ground_y - 30, 95, 124,
                  _mix(far, glow, 0.35), _shade(_mix(far, near, 0.4), -10),
                  glow, _mix(glow, (255, 255, 255), 0.55), 41)
    _crystal_band(surf, w, ground_y, scroll, 0.28, ground_y - 4, 125, 138,
                  _mix(near, glow, 0.4), _shade(near, -18),
                  _sat(glow, 1.4), _mix(glow, (255, 255, 255), 0.6), 73)


# ══════════════════════════════════════════════════════════════════════════
# NEW 3 — Bioluminescent Canyon
# Dark layered canyon mesas in silhouette, each veined with rivers of glowing
# spores/lichen that pool brightest near the rims and trickle down the faces.
# The glow is additive so it reads emissive against the night sky and warm by
# day. Inspired by deep-cave bioluminescence palettes (cyan/teal/magenta).
# ══════════════════════════════════════════════════════════════════════════

def _biolum_layer(surf, heights, ground_y, body_top, body_bot, glow, density, seed):
    top, depth = _gradient_fill(surf, heights, ground_y, body_top, body_bot, ease=1.3)
    if depth <= 0:
        return
    w = surf.get_width()
    # Glowing rim hugging the crest — additive so it blooms into the sky a bit.
    rim = pygame.Surface((w, 8), pygame.SRCALPHA)
    crest_top = min(y for _, y in heights)
    for i, (x, y) in enumerate(heights):
        for dy in range(-3, 4):
            a = int(120 * (1 - abs(dy) / 4))
            yy = y + dy - crest_top + 3
            if 0 <= yy < 8 and a > 0:
                rim.set_at((x, yy), (glow[0], glow[1], glow[2], a))
    surf.blit(rim, (0, crest_top - 3), special_flags=pygame.BLEND_RGBA_ADD)
    # Trickling veins down the faces + glowing pools.
    rng = random.Random(seed ^ (crest_top * 911))
    for _ in range(int(w * density)):
        idx = rng.randrange(len(heights))
        x, y = heights[idx]
        vx = x
        vy = y
        steps = rng.randint(6, 16)
        pts = [(vx, vy)]
        for _s in range(steps):
            vx += rng.randint(-2, 2)
            vy += rng.randint(2, 5)
            if vy >= ground_y:
                break
            pts.append((vx, vy))
        if len(pts) > 1:
            pygame.draw.aalines(surf, glow, False, pts)
            # A brighter glowing pool/node at the end.
            pool = pygame.Surface((10, 10), pygame.SRCALPHA)
            for r in range(5, 0, -1):
                a = int(110 * (1 - r / 5))
                pygame.draw.circle(pool, (glow[0], glow[1], glow[2], a), (5, 5), r)
            surf.blit(pool, (pts[-1][0] - 5, pts[-1][1] - 5),
                      special_flags=pygame.BLEND_RGBA_ADD)


def draw_mountains_biolum(surf, scroll, ground_y, w, far_color=None, near_color=None):
    pal = _biome.palette_for_phase(_PHASE)
    far = far_color or pal['mtn_far']
    near = near_color or pal['mtn_near']
    accent = pal['foliage_accent']
    haze = _haze(far, near)
    # Spore glow: teal-cyan by default, pulled toward the biome foliage accent
    # so it warms at golden hour and stays vivid mint at night.
    glow_far = _sat(_mix(accent, (90, 230, 210), 0.55), 1.25)
    glow_near = _sat(_mix(accent, (120, 255, 235), 0.6), 1.35)

    pts, hb = _ridge(w, ground_y, scroll, 0.06, 100,
                     [(0.01, 24, 0.6), (0.027, 11, 1.8)])
    _biolum_layer(surf, hb, ground_y, _shade(_mix(far, near, 0.5), -10),
                  _shade(near, -25), glow_far, 0.05, 17)
    _haze_band(surf, hb, ground_y, _mix(haze, glow_far, 0.2), 80, 20)

    pts, hf = _ridge(w, ground_y, scroll, 0.15, 76,
                     [(0.013, 30, 1.4), (0.033, 14, 0.3)])
    _biolum_layer(surf, hf, ground_y, _shade(near, -20), _shade(near, -45),
                  _mix(glow_far, glow_near, 0.5), 0.07, 41)
    _haze_band(surf, hf, ground_y, _mix(haze, glow_near, 0.15), 60, 16)

    pts, hn = _ridge(w, ground_y, scroll, 0.28, 52,
                     [(0.018, 22, 0.5), (0.045, 10, 1.9)])
    _biolum_layer(surf, hn, ground_y, _shade(near, -40), _shade(near, -65),
                  glow_near, 0.10, 73)


# ══════════════════════════════════════════════════════════════════════════
# NEW 4 — Aurora Ridgelines
# Low, soft rolling ridges in dark silhouette, fronted by a tall vertical
# aurora curtain rising from behind the far ridge — ribboned bands of light
# that sway with parallax. Curtain hues borrow the sky/horizon palette so the
# aurora always harmonises with the sky behind it.
# ══════════════════════════════════════════════════════════════════════════

def _aurora_curtain(surf, w, ground_y, scroll, top_y, hues, strength, seed):
    """Discrete vertical light streamers. Each ribbon owns its hue and only
    paints where its own gaussian band is the clear local winner above a
    threshold, so dark sky shows between streamers instead of merging into a
    solid slab. ``strength`` (0..1) scales the whole curtain by how dark the
    sky is — auroras read against night, wash out by day, like the real thing.
    Additive but alpha-capped so the sky still shows through."""
    if strength <= 0.02:
        return
    h = ground_y - top_y
    curtain = pygame.Surface((w, h), pygame.SRCALPHA)
    rng = random.Random(seed)
    # Each ribbon snakes: its centre x is a function of y, so the streamer
    # curves like a real auroral curtain instead of standing as a stiff bar.
    ribbons = []
    for r in range(5):
        ribbons.append(dict(
            base=rng.uniform(0.08, 0.92),       # rough screen fraction
            drift=rng.uniform(0.004, 0.007),    # horizontal scroll drift
            phase=rng.uniform(0, math.tau),
            sway_amp=rng.uniform(18, 40),       # how far it snakes with y
            sway_freq=rng.uniform(0.006, 0.013),
            sigma=rng.uniform(11, 20),          # soft width
            top=rng.randint(0, 40),             # ragged top start
            hue=hues[r % len(hues)],
        ))
    peak = 70 * strength
    drift = scroll * 0.04
    for r in ribbons:
        cx0 = r['base'] * w - (math.sin(drift * r['drift'] + r['phase']) * 0)
        for yy in range(r['top'], h):
            ty = (yy - r['top']) / max(1, h - r['top'])
            # Curtain centre snakes with height; whole ribbon drifts with scroll.
            centre = (cx0
                      + math.sin(yy * r['sway_freq'] + r['phase']) * r['sway_amp']
                      + math.sin(drift * r['drift'] + r['phase']) * 24)
            vfade = (1.0 - ty) ** 1.25 * (0.4 + 0.6 * math.sin(ty * math.pi) ** 0.4)
            half = r['sigma']
            lo = int(centre - half * 2.5)
            hi = int(centre + half * 2.5)
            for x in range(max(0, lo), min(w, hi)):
                band = math.exp(-((x - centre) ** 2) / (2 * half * half))
                a = int(peak * band * vfade)
                if a <= 2:
                    continue
                prev = curtain.get_at((x, yy))
                # Additive accumulation in the buffer, capped, so crossing
                # ribbons brighten without blowing straight to white.
                na = min(150, prev[3] + a)
                curtain.set_at((x, yy), (r['hue'][0], r['hue'][1], r['hue'][2], na))
    surf.blit(curtain, (0, top_y), special_flags=pygame.BLEND_RGBA_ADD)


def draw_mountains_aurora(surf, scroll, ground_y, w, far_color=None, near_color=None):
    pal = _biome.palette_for_phase(_PHASE)
    far = far_color or pal['mtn_far']
    near = near_color or pal['mtn_near']
    haze = _haze(far, near)
    # Aurora ribbon hues from the palette — foliage greens, sky/horizon tints,
    # plus a magenta lift so it reads as classic aurora regardless of time.
    hues = [
        _sat(_mix(pal['foliage_mid'], (120, 255, 180), 0.6), 1.4),
        _sat(_mix(pal['horizon'], (150, 220, 255), 0.4), 1.3),
        _sat(_mix(pal['sky_mid'], (200, 120, 255), 0.5), 1.3),
        _sat(_mix(pal['foliage_accent'], (160, 255, 220), 0.5), 1.35),
    ]

    # Aurora rises from behind the far ridge. Strength tracks how dark the sky
    # is (star_alpha climbs toward night) so it glows after dusk and all but
    # vanishes in daylight — but keep a faint floor so the row never reads
    # empty in the day/sunrise review cells.
    strength = 0.06 + 0.94 * min(1.0, pal['star_alpha'] / 235.0)
    _aurora_curtain(surf, w, ground_y, scroll, ground_y - 235, hues, strength, 17)

    # Three dark rolling ridges in front, so the curtain reads as "behind".
    pts, hb = _ridge(w, ground_y, scroll, 0.06, 86,
                     [(0.008, 22, 0.4), (0.02, 9, 1.6)])
    _gradient_fill(surf, hb, ground_y, _shade(_mix(far, near, 0.5), -25),
                   _shade(near, -40), ease=1.1)
    _aa_crest(surf, hb, _mix(far, hues[1], 0.3))
    _haze_band(surf, hb, ground_y, _mix(haze, hues[1], 0.2), 70, 18)

    pts, hf = _ridge(w, ground_y, scroll, 0.15, 60,
                     [(0.012, 26, 1.0), (0.03, 11, 0.4)])
    _gradient_fill(surf, hf, ground_y, _shade(near, -30), _shade(near, -55), ease=1.1)
    _aa_crest(surf, hf, _mix(near, hues[0], 0.3))

    pts, hn = _ridge(w, ground_y, scroll, 0.28, 38,
                     [(0.017, 20, 0.5), (0.04, 8, 2.2)])
    _gradient_fill(surf, hn, ground_y, _shade(near, -45), _shade(near, -70), ease=1.1)
    _aa_crest(surf, hn, _mix(near, hues[3], 0.3))


# ══════════════════════════════════════════════════════════════════════════
# NEW 5 — Distant Fantasy Skyline
# A receding city of spires, domes, towers and arches on the horizon. Far rows
# are flat hazy silhouettes; the near row gains lit windows and rim light. A
# storybook skyline that re-themes from sunny pastel to glowing night city.
# ══════════════════════════════════════════════════════════════════════════

def _spire(surf, x, base_y, w_, h, color, rng, roof):
    """A single tower: rectangular body + a roof (dome / cone / flat / arch)."""
    body = pygame.Rect(x - w_ // 2, base_y - h, w_, h)
    pygame.draw.rect(surf, color, body)
    cap_h = max(4, w_)
    if roof == 'dome':
        pygame.draw.ellipse(surf, color,
                            pygame.Rect(x - w_ // 2, base_y - h - cap_h, w_, cap_h * 2))
        pygame.draw.rect(surf, color, pygame.Rect(x - w_ // 2, base_y - h, w_, 4))
    elif roof == 'cone':
        pygame.draw.polygon(surf, color, [(x - w_ // 2, base_y - h),
                                          (x + w_ // 2, base_y - h),
                                          (x, base_y - h - cap_h - 4)])
    elif roof == 'arch':
        pygame.draw.ellipse(surf, color,
                            pygame.Rect(x - w_ // 2, base_y - h - w_, w_, w_ * 2))
    # flat → nothing extra
    return body


def _skyline_row(surf, w, ground_y, scroll, speed, y_base, hmin, hmax, spacing,
                 color, seed, lit_windows=False, window_glow=None, rim=None):
    phase = scroll * speed
    k0 = int(phase // spacing) - 1
    roofs = ['dome', 'cone', 'flat', 'arch', 'cone', 'dome']
    for k in range(k0, k0 + int(w / spacing) + 3):
        rng = random.Random((k * 40503 ^ seed) & 0xFFFFFFFF)
        x = int(k * spacing - phase) + rng.randint(-6, 6)
        if not (-40 < x < w + 40):
            continue
        tw = rng.randint(10, 20)
        th = rng.randint(hmin, hmax)
        roof = roofs[rng.randrange(len(roofs))]
        body = _spire(surf, x, y_base, tw, th, color, rng, roof)
        if rim:
            pygame.draw.line(surf, rim, body.topleft, body.bottomleft, 1)
            pygame.draw.line(surf, rim, body.topleft, body.topright, 1)
        if lit_windows and window_glow:
            cols = max(1, tw // 6)
            rows = max(1, th // 12)
            for cxi in range(cols):
                for ryi in range(rows):
                    if rng.random() < 0.55:
                        wx = body.left + 3 + cxi * 6
                        wy = body.top + 6 + ryi * 12
                        if wy < y_base - 3 and wx < body.right - 2:
                            surf.fill(window_glow, pygame.Rect(wx, wy, 2, 3))


def draw_mountains_skyline(surf, scroll, ground_y, w, far_color=None, near_color=None):
    pal = _biome.palette_for_phase(_PHASE)
    far = far_color or pal['mtn_far']
    near = near_color or pal['mtn_near']
    horizon = pal['horizon']
    haze = _haze(far, near)
    # Window glow: warm lamplight, leaning brighter at night via the horizon
    # tone (which goes pale-bright after dark in this palette).
    window_glow = _sat(_mix(pal['stone_accent'], (255, 220, 130), 0.5), 1.2)

    # BACK row — palest, hazy, tallest-but-thin spires far off.
    _skyline_row(surf, w, ground_y, scroll, 0.06, ground_y - 8, 70, 120, 70,
                 _mix(far, horizon, 0.5), 17)
    _haze_band(surf, [(0, ground_y - 120), (w, ground_y - 120)], ground_y,
               _mix(haze, horizon, 0.4), 110, 26)

    # FAR row.
    _skyline_row(surf, w, ground_y, scroll, 0.15, ground_y - 4, 55, 100, 58,
                 _mix(far, near, 0.5), 41)
    _haze_band(surf, [(0, ground_y - 100), (w, ground_y - 100)], ground_y,
               _mix(haze, horizon, 0.25), 70, 18)

    # NEAR row — darkest silhouette, rim-lit, with lit windows.
    rim = _mix(near, horizon, 0.5)
    _skyline_row(surf, w, ground_y, scroll, 0.28, ground_y, 40, 80, 48,
                 _shade(near, -18), 73, lit_windows=True,
                 window_glow=window_glow, rim=rim)


# ── phase plumbing ────────────────────────────────────────────────────────
# Several concepts need palette keys beyond mtn_far/mtn_near (foliage, horizon,
# accents). The drop-in signature can't carry the phase, so the harness sets
# this module-level phase right before each call. In the live game the same
# extra keys would be read from the already-known palette dict.

_PHASE = 0.02


def set_phase(p: float) -> None:
    global _PHASE
    _PHASE = p % 1.0


# ── dispatcher ───────────────────────────────────────────────────────────────

VARIANTS = {
    2: draw_mountains_v2,
    4: draw_mountains_v4,
    6: draw_mountains_islands,
    7: draw_mountains_crystal,
    8: draw_mountains_biolum,
    9: draw_mountains_aurora,
    10: draw_mountains_skyline,
}

VARIANT_NAMES = {
    2: "Wind-Sculpted Dunes (refined)",
    4: "Shan-Shui Ink Ridges (refined)",
    6: "Floating Sky Islands",
    7: "Crystal Geode Spires",
    8: "Bioluminescent Canyon",
    9: "Aurora Ridgelines",
    10: "Distant Fantasy Skyline",
}

ROW_ORDER = [2, 4, 6, 7, 8, 9, 10]
