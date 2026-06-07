"""Live mountain backdrop — V14 "Pagoda-Crowned Ridges (alive)".

Five parallax ridge bands washed with ink-gradient depth, then scattered with
pagodas, pavilions, pines, bamboo, willows, stone lanterns and banners whose mix
follows a per-world-x region archetype — so each stretch of the ridgeline reads
as a different village. Everything re-tints across the biome day/night cycle via
the imported palette; placement is seeded off scroll position so a given world-x
always paints the same scene (no per-frame flicker).

Consolidated single module for the live game (one import surface). Source of
truth for the design exploration + the user-picked winner lives in
`archive/mountain_redesign/` and `docs/mountain_redesign/_comparison_alive_dayNight.png`.
"""
from __future__ import annotations

import math
import random

import pygame


# ── colour math + ridge/ink primitives ───────────────────────────────────────

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

def _ink_wash_strong(surf, heights, ground_y, ink_top, ink_bot, alpha_top,
                     fade=1.4, rim_col=None, rim_w=1):
    """Bolder cousin of ``_ink_wash``: opaque-feeling base alpha plus a
    distinct rim colour argument so the silhouette reads with weight while
    crest brushwork stays calligraphic. Used by every R3 shan-shui variant."""
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
    if rim_col is not None:
        _aa_crest(surf, heights, rim_col, width=rim_w)

def _aa_crest(surf, heights, color, width=1):
    """Anti-aliased ridge stroke where it's cheap (native+WASM both support
    aaline). Falls back gracefully if the segment list is short."""
    if len(heights) < 2:
        return
    pygame.draw.aalines(surf, color, False, heights)
    if width > 1:
        pygame.draw.lines(surf, color, False, heights, width)

# ── ornament drawers ─────────────────────────────────────────────────────────

def _pagoda(surf, x, base_y, tiers, base_w, color, accent, scale=1.0):
    """Multi-tier pagoda. Tiers narrow upward, each capped by an upturned eave
    and finishing in a finial spire. Reads as architectural silhouette at any
    scale; tier count and base width drive the read so a 3-tier 8 px-wide
    "village" pagoda sits naturally beside a 7-tier 18 px-wide "temple" one."""
    tier_h = max(4, int(7 * scale))
    eave_lip = max(1, int(3 * scale))
    bw = base_w
    cy = base_y
    for t in range(tiers):
        tw = max(5, bw - t * 2)
        body = pygame.Rect(x - tw // 2, cy - tier_h, tw, tier_h)
        pygame.draw.rect(surf, color, body)
        eave_w = tw + max(6, int(8 * scale))
        roof_top = cy - tier_h - max(2, int(3 * scale))
        roof_pts = [
            (x - eave_w // 2, cy - tier_h),
            (x - eave_w // 2 + 2, roof_top),
            (x + eave_w // 2 - 2, roof_top),
            (x + eave_w // 2, cy - tier_h),
        ]
        pygame.draw.polygon(surf, color, roof_pts)
        pygame.draw.line(surf, color,
                         (x - eave_w // 2 - 1, cy - tier_h - 1),
                         (x - eave_w // 2 + 1, cy - tier_h - max(3, int(4 * scale))), 1)
        pygame.draw.line(surf, color,
                         (x + eave_w // 2, cy - tier_h - 1),
                         (x + eave_w // 2 - 2, cy - tier_h - max(3, int(4 * scale))), 1)
        pygame.draw.aaline(surf, accent,
                           (x - eave_w // 2 + 1, roof_top + 1),
                           (x + eave_w // 2 - 1, roof_top + 1))
        cy -= tier_h + eave_lip
    spire_h = max(4, int(6 * scale))
    pygame.draw.polygon(surf, color,
                        [(x - 1, cy), (x + 1, cy), (x, cy - spire_h)])
    surf.set_at((x, cy - spire_h - 1), accent)

def _bent_pine(surf, x, y_base, h, ink, accent, lean=1):
    """Huangshan-style twisted pine: bent trunk + two flat canopy puffs.
    Compact, silhouette-only, reads as iconic East-Asian punctuation."""
    if y_base <= h + 4:
        return
    seg = max(3, h // 3)
    p0 = (x, y_base)
    p1 = (x + lean * 2, y_base - seg)
    p2 = (x + lean * 4, y_base - seg * 2)
    p3 = (x + lean * 2, y_base - h)
    pygame.draw.lines(surf, ink, False, [p0, p1, p2, p3], 2)
    cw1 = max(7, int(h * 0.75))
    ch1 = max(3, h // 6)
    cw2 = max(5, int(h * 0.5))
    ch2 = max(2, h // 8)
    pygame.draw.ellipse(surf, ink,
                        pygame.Rect(p3[0] - cw1 // 2, p3[1] - ch1 - 1, cw1, ch1 * 2))
    pygame.draw.ellipse(surf, ink,
                        pygame.Rect(p3[0] - cw2 // 2, p3[1] - ch2 - h // 4, cw2, ch2 * 2))
    surf.set_at((p3[0], p3[1] - ch1 - 2), accent)

def _fan_pine(surf, x, y_base, h, ink, accent):
    """Tall fan-canopy pine: straight slim trunk + 3 stacked horizontal layers
    fanning outward. Reads as the dominant pine on a high ridge."""
    if y_base <= h + 4:
        return
    pygame.draw.line(surf, ink, (x, y_base), (x, y_base - h), 2)
    top_y = y_base - h
    layers = 3
    for i in range(layers):
        ly = top_y + i * max(3, h // 6)
        lw = max(8, int(h * (0.55 + i * 0.15)))
        lh = max(2, h // 9)
        pygame.draw.ellipse(surf, ink,
                            pygame.Rect(x - lw // 2, ly - lh, lw, lh * 2))
    surf.set_at((x, top_y - 1), accent)

def _bamboo(surf, x, y_base, h, ink, accent):
    """Bamboo clump: 3 thin vertical stalks of varied heights with small
    paired leaves at the top. Slim, distinct from pines."""
    for k in range(3):
        sx = x + (k - 1) * 3
        sh = int(h * (0.7 + 0.3 * (k % 2 == 1)))
        pygame.draw.line(surf, ink, (sx, y_base), (sx, y_base - sh), 1)
        # Two paired leaves near the top — short diagonal flicks.
        ty = y_base - sh
        pygame.draw.aaline(surf, ink, (sx, ty + 2), (sx - 3, ty - 1))
        pygame.draw.aaline(surf, ink, (sx, ty + 2), (sx + 3, ty - 1))
    surf.set_at((x, y_base - h - 1), accent)

def _willow(surf, x, y_base, h, ink):
    """Weeping willow whisk: a tiny trunk topped by a few drooping fronds.
    The fronds are short downward strokes fanning from a centre point — reads
    as a delicate near-ground tree silhouette."""
    if y_base <= h + 4:
        return
    pygame.draw.line(surf, ink, (x, y_base), (x, y_base - h), 1)
    top_y = y_base - h
    for i in range(7):
        ang = -math.pi / 2 + (i - 3) * 0.32
        fx = x + math.cos(ang) * (h // 2 + 1)
        fy = top_y + 1
        pygame.draw.aaline(surf, ink, (x, top_y), (fx, fy + h // 2 - 1))

def _stone_lantern(surf, x, y_base, ink, accent):
    """Tiny ishi-doro stone lantern: square base + pillar + lit head with a
    pointed cap. Three pixels tall for body, the lit window is the accent."""
    pygame.draw.rect(surf, ink, pygame.Rect(x - 2, y_base - 2, 5, 2))
    pygame.draw.rect(surf, ink, pygame.Rect(x - 1, y_base - 6, 3, 4))
    pygame.draw.rect(surf, ink, pygame.Rect(x - 2, y_base - 9, 5, 3))
    surf.set_at((x, y_base - 8), accent)
    pygame.draw.polygon(surf, ink, [(x - 3, y_base - 9),
                                    (x + 3, y_base - 9),
                                    (x, y_base - 12)])

def _pavilion(surf, x, y_base, color, accent, scale=1.0):
    """A small one-tier pavilion / temple: wider eave than a pagoda, no spire.
    Sits on a hilltop or high ridge as architectural punctuation distinct
    from a tall pagoda."""
    bw = max(7, int(9 * scale))
    bh = max(3, int(4 * scale))
    pygame.draw.rect(surf, color,
                     pygame.Rect(x - bw // 2, y_base - bh, bw, bh))
    eave_w = bw + max(6, int(8 * scale))
    eave_y = y_base - bh
    roof_top = eave_y - max(3, int(5 * scale))
    pygame.draw.polygon(surf, color, [
        (x - eave_w // 2, eave_y),
        (x - eave_w // 2 + 2, roof_top),
        (x + eave_w // 2 - 2, roof_top),
        (x + eave_w // 2, eave_y),
    ])
    pygame.draw.line(surf, color, (x - eave_w // 2 - 1, eave_y - 1),
                     (x - eave_w // 2 + 1, eave_y - max(3, int(4 * scale))), 1)
    pygame.draw.line(surf, color, (x + eave_w // 2, eave_y - 1),
                     (x + eave_w // 2 - 2, eave_y - max(3, int(4 * scale))), 1)
    pygame.draw.aaline(surf, accent,
                       (x - eave_w // 2 + 1, roof_top + 1),
                       (x + eave_w // 2 - 1, roof_top + 1))

def _hanging_banner(surf, x, top_y, length, color):
    """A vertical hanging cloth banner — a tall thin coloured rectangle with
    a tassel at the bottom. Marks villages/shrines on a ridge crown."""
    rect = pygame.Rect(x - 1, top_y, 3, length)
    pygame.draw.rect(surf, color, rect)
    # Tassel — a single pixel tail.
    surf.set_at((x, top_y + length), color)
    surf.set_at((x, top_y + length + 1), color)

# ── ridge analysis ───────────────────────────────────────────────────────────

def _local_peaks(heights, look=14):
    """Return indices of local maxima (highest crest points) so element
    placement lands on visible summits, not random pixels."""
    out = []
    for i in range(look, len(heights) - look):
        x, y = heights[i]
        if all(y <= heights[i + d][1] for d in range(-look, look + 1)):
            out.append(i)
    return out

def _seed_for(scroll, layer_const):
    """Deterministic per-scroll-bucket seed. Bucket size 1px so the variation
    re-rolls smoothly as the world moves; layer_const keeps each band's RNG
    independent so the three layers aren't lockstep."""
    return (int(scroll) ^ layer_const) & 0xFFFFFFFF

# ── region archetype system ──────────────────────────────────────────────────

_V14_REGION_WIDTH = 600

_V14_REGION_STYLES = (
    # 0: slim Tang-tower silhouettes + bamboo + willow groves.
    dict(tier_choices=(5, 7, 7), pag_scale_mul=1.00,
         tree_weights=(('bamboo', 0.45), ('willow', 0.35),
                       ('pine_bent', 0.10), ('pine_fan', 0.10)),
         flavour_weights=(('pagoda', 0.40), ('grove', 0.30),
                          ('shrine', 0.15), ('mixed', 0.15))),
    # 1: squat 3-tier hilltop + fan-pine grove.
    dict(tier_choices=(3, 3, 5), pag_scale_mul=0.88,
         tree_weights=(('pine_fan', 0.55), ('pine_bent', 0.30),
                       ('bamboo', 0.10), ('willow', 0.05)),
         flavour_weights=(('pagoda', 0.30), ('grove', 0.40),
                          ('shrine', 0.15), ('mixed', 0.15))),
    # 2: mid-tier pair + weeping-willow river bank.
    dict(tier_choices=(5, 7), pag_scale_mul=1.05,
         tree_weights=(('willow', 0.55), ('bamboo', 0.20),
                       ('pine_bent', 0.15), ('pine_fan', 0.10)),
         flavour_weights=(('pagoda', 0.45), ('grove', 0.30),
                          ('shrine', 0.10), ('mixed', 0.15))),
    # 3: shrine-heavy + stone lantern paths + bent pine.
    dict(tier_choices=(3, 5), pag_scale_mul=0.92,
         tree_weights=(('pine_bent', 0.50), ('pine_fan', 0.25),
                       ('bamboo', 0.15), ('willow', 0.10)),
         flavour_weights=(('pagoda', 0.20), ('grove', 0.15),
                          ('shrine', 0.50), ('mixed', 0.15))),
    # 4: tallest 7-tier marker + dense bamboo summit.
    dict(tier_choices=(5, 7, 7), pag_scale_mul=1.18,
         tree_weights=(('bamboo', 0.55), ('pine_fan', 0.20),
                       ('willow', 0.15), ('pine_bent', 0.10)),
         flavour_weights=(('pagoda', 0.45), ('grove', 0.35),
                          ('shrine', 0.10), ('mixed', 0.10))),
)

def _v14_region(world_x):
    bucket = int(max(0, world_x) // _V14_REGION_WIDTH)
    return _V14_REGION_STYLES[bucket % len(_V14_REGION_STYLES)]

def _v14_weighted(rng, weights):
    total = sum(w for _, w in weights)
    r = rng.random() * total
    acc = 0.0
    for k, w in weights:
        acc += w
        if r <= acc:
            return k
    return weights[-1][0]

# ── entry point ──────────────────────────────────────────────────────────────

def draw_mountains_v14(surf, scroll, ground_y, w, *, phase=0.02):
    # lazy import: biome imports draw.lerp_color, so importing it at module
    # top would form a draw->mountains_v14->biome->draw cycle.
    from game import biome as _biome
    pal = _biome.palette_for_phase(phase)
    far = pal['mtn_far']
    near = pal['mtn_near']
    horizon = pal['horizon']
    night = min(1.0, pal['star_alpha'] / 235.0)
    haze = _mix(_haze(far, near), horizon, 0.32)

    far_tint = _mix(far, horizon, 0.42)
    specs = [
        (0.05, 124, 140, _mix(far_tint, (235, 238, 248), 0.28), far_tint),
        (0.08, 108, 165, _mix(far_tint, far, 0.62), _mix(far_tint, haze, 0.5)),
        (0.13, 96, 190, _sat(far, 1.20), _mix(far, haze, 0.4)),
        (0.20, 80, 218, _sat(_mix(near, far, 0.4), 1.25), _mix(near, far, 0.5)),
        (0.28, 64, 244, _sat(near, 1.30), _mix(near, far, 0.28)),
    ]
    crest_heights = []
    for k, (speed, base_h, atop, itop, ibot) in enumerate(specs):
        pts, h = _ridge(w, ground_y, scroll, speed, base_h,
                        [(0.011 + k * 0.002, 24 - k * 2, 0.6 + k),
                         (0.030 + k * 0.004, 12, 1.5 - k * 0.3)])
        _ink_wash_strong(surf, h, ground_y, itop, ibot, atop, fade=1.6,
                         rim_col=_shade(_sat(itop, 1.2), -28))
        crest_heights.append(h)

    pag_far = _shade(_sat(_mix(far, near, 0.7), 1.15), -42)
    pag_mid = _shade(_sat(near, 1.20), -46)
    pag_near = _shade(_sat(near, 1.30), -58)
    accent = _mix(horizon, (255, 230, 180), 0.55)
    # Banners pull a warm cinnabar by day, dim toward night.
    banner_col = _shade(_mix(_sat(horizon, 1.3), (190, 70, 60), 0.5),
                        int(-70 * night))

    def scatter_pagoda(heights, layer_idx, base_color, layer_seed,
                       pag_scale_range, tier_choices, tree_scale=1.0,
                       allow_banner=True):
        rng = random.Random(_seed_for(scroll, layer_seed))
        # Far band runs sparser than mid/near so the horizon stays calm.
        if layer_idx == 2:
            n_sections = 1
        else:
            n_sections = 2
        cuts = sorted(rng.sample(range(40, w - 40), n_sections - 1))
        bounds = [0] + cuts + [w]
        peaks = _local_peaks(heights, look=18)
        peaks_by_x = sorted([(heights[i][0], i) for i in peaks])

        def _draw_tree(kind, tx, ty):
            # Region-style picks the kind; this routes to the right helper
            # at a kind-appropriate height (scaled by depth band).
            if kind == 'pine_bent':
                _bent_pine(surf, tx, ty - 1,
                           int(rng.randint(14, 26) * tree_scale),
                           base_color, accent, lean=rng.choice((-1, 1)))
            elif kind == 'pine_fan':
                _fan_pine(surf, tx, ty - 1,
                          int(rng.randint(20, 32) * tree_scale),
                          base_color, accent)
            elif kind == 'bamboo':
                _bamboo(surf, tx, ty - 1,
                        int(rng.randint(10, 18) * tree_scale),
                        base_color, accent)
            else:
                _willow(surf, tx, ty,
                        int(rng.randint(9, 14) * tree_scale), base_color)

        for s in range(n_sections):
            lo, hi = bounds[s], bounds[s + 1]
            section_peaks = [i for x, i in peaks_by_x if lo <= x <= hi]
            # Section flavour follows the REGION at the section's world-x —
            # so consecutive regions feel like different villages on the
            # same shan-shui ridgeline.
            sec_wx = scroll + (lo + hi) * 0.5
            sec_region = _v14_region(sec_wx)
            flavour = _v14_weighted(rng, sec_region['flavour_weights'])

            if flavour == 'pagoda' and section_peaks:
                idx = rng.choice(section_peaks)
                cx, cy = heights[idx]
                elem_region = _v14_region(scroll + cx)
                tiers = rng.choice(elem_region['tier_choices'])
                bw = rng.randint(10, 16)
                lo_s, hi_s = pag_scale_range
                sc = rng.uniform(lo_s, hi_s) * elem_region['pag_scale_mul']
                _pagoda(surf, cx, cy - 1, tiers, bw, base_color, accent, sc)
                if rng.random() < 0.25:
                    _stone_lantern(surf, cx - 10, cy - 1, base_color, accent)
                    _stone_lantern(surf, cx + 10, cy - 1, base_color, accent)
            elif flavour == 'grove' and section_peaks:
                idx = rng.choice(section_peaks)
                cx, cy = heights[idx]
                count = rng.randint(1, 2)
                for _ in range(count):
                    tx = cx + rng.randint(-22, 22)
                    if not (lo <= tx <= hi):
                        continue
                    ty = heights[min(tx, len(heights) - 1)][1]
                    elem_region = _v14_region(scroll + tx)
                    kind = _v14_weighted(rng, elem_region['tree_weights'])
                    _draw_tree(kind, tx, ty)
                if allow_banner and rng.random() < 0.30:
                    bx = cx + rng.randint(-18, 18)
                    by = heights[min(bx, len(heights) - 1)][1]
                    _hanging_banner(surf, bx, by - 18,
                                    rng.randint(10, 16), banner_col)
            elif flavour == 'shrine' and section_peaks:
                idx = rng.choice(section_peaks)
                cx, cy = heights[idx]
                elem_region = _v14_region(scroll + cx)
                pscale = rng.uniform(0.85, 1.15) * elem_region['pag_scale_mul']
                _pavilion(surf, cx, cy - 1, base_color, accent, scale=pscale)
                _stone_lantern(surf, cx + rng.choice((-12, 12)), cy - 1,
                               base_color, accent)
                if rng.random() < 0.50:
                    tx = cx + rng.randint(-26, 26)
                    if lo <= tx <= hi:
                        ty = heights[min(tx, len(heights) - 1)][1]
                        kind = _v14_weighted(rng,
                                             elem_region['tree_weights'])
                        _draw_tree(kind, tx, ty)
            else:  # 'mixed' — one pagoda + at most one accent tree
                if section_peaks:
                    idx = rng.choice(section_peaks)
                    cx, cy = heights[idx]
                    elem_region = _v14_region(scroll + cx)
                    tiers = rng.choice(elem_region['tier_choices'])
                    lo_s, hi_s = pag_scale_range
                    sc = rng.uniform(lo_s, hi_s) * elem_region['pag_scale_mul']
                    _pagoda(surf, cx, cy - 1, tiers, rng.randint(9, 13),
                            base_color, accent, scale=sc)
                if rng.random() < 0.50 and hi - lo >= 20:
                    tx = rng.randint(lo + 6, hi - 6)
                    ty = heights[min(tx, len(heights) - 1)][1]
                    elem_region = _v14_region(scroll + tx)
                    kind = _v14_weighted(rng, elem_region['tree_weights'])
                    _draw_tree(kind, tx, ty)

    # Far band — small pagodas, no trees.
    scatter_pagoda(crest_heights[2], layer_idx=2,
                   base_color=pag_far, layer_seed=0xE14A,
                   pag_scale_range=(0.7, 0.95),
                   tier_choices=(3, 5), tree_scale=0.7,
                   allow_banner=False)
    # Mid band — full vocabulary.
    scatter_pagoda(crest_heights[3], layer_idx=3,
                   base_color=pag_mid, layer_seed=0xE14B,
                   pag_scale_range=(0.95, 1.25),
                   tier_choices=(3, 5, 5, 7), tree_scale=1.0)
    # Near band — biggest pagodas + trees.
    scatter_pagoda(crest_heights[4], layer_idx=4,
                   base_color=pag_near, layer_seed=0xE14C,
                   pag_scale_range=(1.15, 1.55),
                   tier_choices=(5, 7, 7), tree_scale=1.3)
