"""Terracotta Warrior + Buddha pillar candidates — round 1.

Sibling exploration to the pagoda set in
`pillar_pagoda_variants.py`. Same pillar-pair contract,
`candidate_<name>(surf, top_rect, bot_rect, palette, seed)`. Bottom rect
holds the figure on a plinth/cliff niche; the top rect is a flipped copy
of the same anatomy drawn into a temp SRCALPHA, sized adaptively so the
mirror fills the rect (R11/12/13 pattern lifted from `_draw_horyuji` &
`_draw_muroji` in the pagoda module).

Two families, five each:

  TERRACOTTA WARRIORS (秦兵马俑) — matte clay-brown bodies with faded
  vermilion / celadon / ochre pigment traces. ONE material per figure
  (Qin clay) — variation comes through pose + armour density + headgear
  + base plinth shape.

    candidate_warrior_general          — high-ranking officer
        https://www.smithsonianmag.com/smart-news/archaeologists-discover-rare-clay-commander-among-thousands-of-life-size-terra-cotta-soldiers-in-china-180985747/
    candidate_warrior_standing_archer  — standing infantry archer
        https://www.travelchinaguide.com/attraction/shaanxi/xian/terra_cotta_army/standing-archers.htm
    candidate_warrior_kneeling_archer  — kneeling crossbowman icon
        https://www.travelchinaguide.com/attraction/shaanxi/xian/terra_cotta_army/kneeling-archers.htm
    candidate_warrior_cavalry          — cavalryman + saddled horse pair
        https://www.travelchinaguide.com/attraction/shaanxi/xian/terra_cotta_army/warrior-types.htm
    candidate_warrior_charioteer       — charioteer with reins
        https://www.travelchinaguide.com/attraction/shaanxi/xian/terra_cotta_army/chariots.htm

  BUDDHA STATUES — each its own material per the real-world source.

    candidate_buddha_leshan      — Leshan cliff Buddha (sandstone)
        https://en.wikipedia.org/wiki/Leshan_Giant_Buddha
    candidate_buddha_tian_tan    — Tian Tan bronze (HK, abhaya mudra)
        https://en.wikipedia.org/wiki/Tian_Tan_Buddha
    candidate_buddha_maitreya    — standing/laughing Maitreya (gilt bronze)
        https://en.wikipedia.org/wiki/Budai
    candidate_buddha_reclining   — Parinirvana (gold-leaf)
        https://en.wikipedia.org/wiki/Reclining_Buddha
    candidate_buddha_guanyin     — Guanyin / Avalokiteśvara (porcelain)
        https://en.wikipedia.org/wiki/Guanyin

Each candidate caches its drawn pillar pair into a per-(seed × palette)
SRCALPHA bitmap so the curved silhouettes don't re-alias every frame —
mirrors the cache pattern in the pagoda module.
"""
from __future__ import annotations

import math
import random

import pygame

from game.draw import (
    draw_side_shrub,
)
from game.pillar_variants import (
    draw_grass_bed,
    draw_flower_bed,
)


# ── Colour helpers ──────────────────────────────────────────────────────────
#
# All hues mix against the live biome palette so day/night retints carry
# through. Raw RGB constants are archetype targets, biased toward the
# stone_* keys so dusk/sunset/night sweep cleanly.

def _mix(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def _shade(c, d):
    return (max(0, min(255, c[0] + d)),
            max(0, min(255, c[1] + d)),
            max(0, min(255, c[2] + d)))


# Terracotta-family palette anchors — matte fired-clay tones. ONE shared
# body palette across all 5 warriors so the family reads coherent. Pose +
# armour + headgear is what differentiates them.

def _clay_body(palette):
    # Matte fired-clay brown — the warm earth tone of unglazed Qin clay.
    # Anchored in stone_dark so dusk/night still read warm-clay, not grey.
    return _mix(palette['stone_dark'], (158, 102, 72), 0.74)


def _clay_lit(palette):
    # Sun-side highlight on the curved torso — half-stop brighter than
    # body so the figure reads as a 3-D volume at PIPE_W = 58.
    return _mix(palette['stone_light'], (208, 152, 110), 0.62)


def _clay_shadow(palette):
    return _mix(palette['stone_dark'], (84, 50, 32), 0.82)


def _clay_crack(palette):
    # Hairline crack across the fired body — darker than shadow, the
    # canonical "buried 2000 years" cue.
    return _mix(palette['stone_dark'], (52, 30, 18), 0.88)


def _pigment_vermilion(palette):
    # Faded vermilion ribbon-knot pigment trace on officer armour.
    return _mix(palette['stone_dark'], (172, 60, 46), 0.72)


def _pigment_celadon(palette):
    # Pale green pigment on Qin scale-armour straps. Iconic +ironic
    # because most fades to nothing in the soil; here we honour the
    # documented trace.
    return _mix(palette['stone_mid'], (118, 148, 102), 0.55)


def _pigment_ochre(palette):
    # Yellow-ochre band along binding-knots + caps.
    return _mix(palette['stone_accent'], (212, 162, 70), 0.68)


def _pigment_white(palette):
    # White-stitching trace between armour plates.
    return _mix(palette['stone_light'], (228, 218, 196), 0.55)


def _plinth_dark(palette):
    # Dark Qin-tomb earth packed under the figure's plinth.
    return _mix(palette['stone_dark'], (76, 56, 42), 0.82)


# Buddha-family palette anchors. UNLIKE the warriors, each Buddha gets
# its OWN material — bronze, sandstone, gilt, gold-leaf, porcelain.

def _sandstone_warm(palette):
    # Leshan cliff cretaceous-red sandstone body.
    return _mix(palette['stone_mid'], (188, 142, 96), 0.62)


def _sandstone_lit(palette):
    return _mix(palette['stone_light'], (228, 188, 142), 0.58)


def _sandstone_shadow(palette):
    return _mix(palette['stone_dark'], (108, 74, 50), 0.80)


def _bronze_dark(palette):
    # Generic darker bronze — used by chariot bells + cavalry trim
    # where a warm metallic accent is wanted but verdigris would
    # collide with the warrior clay palette.
    return _mix(palette['stone_dark'], (78, 76, 52), 0.78)


def _bronze_body(palette):
    return _mix(palette['stone_accent'], (152, 124, 70), 0.66)


def _bronze_lit(palette):
    return _mix(palette['stone_light'], (212, 178, 104), 0.62)


# ── Tian Tan bronze helpers. Round 3: AD flagged round 2's all-green
# shift as a regression — read as "green stone Buddha" rather than the
# warm patinated bronze of the actual Hong Kong statue. Lit + body go
# BACK to a warm-bronze (180,130,70 family) tone so day/sunset retint
# stays distinctly metallic-warm. Verdigris (60,110,90) survives ONLY
# in the deepest recess shadow — under the lotus throne lip, deep robe
# folds, back of the altar tiers — where the canonical patina would
# actually settle on a real outdoor bronze.

def _tian_tan_dark(palette):
    return _mix(palette['stone_dark'], (60, 110, 90), 0.86)


def _tian_tan_body(palette):
    return _mix(palette['stone_mid'], (180, 130, 70), 0.78)


def _tian_tan_lit(palette):
    return _mix(palette['stone_light'], (228, 188, 118), 0.70)


def _gilt_bronze(palette):
    # Standing Maitreya gilt-bronze finish — round 2 pushed clearly
    # WARMER (gold-yellow saturation up) so it sits cleanly between
    # the verdigris Tian Tan and the cooler porcelain Guanyin.
    return _mix(palette['stone_accent'], (236, 176, 56), 0.86)


def _gilt_bright(palette):
    return _mix(palette['stone_accent'], (255, 232, 138), 0.92)


def _gilt_shadow(palette):
    # Round-2: a darker amber that keeps its warmth at night instead
    # of collapsing toward neutral grey.
    return _mix(palette['stone_dark'], (168, 116, 38), 0.84)


def _gold_leaf(palette):
    # Reclining Buddha gold-leaf face — saturated, with a luminous edge.
    return _mix(palette['stone_accent'], (238, 196, 88), 0.80)


def _gold_leaf_deep(palette):
    return _mix(palette['stone_accent'], (172, 124, 36), 0.82)


def _porcelain_white(palette):
    # Guanyin porcelain — round 3 shifts COOL-WHITE so the body reads
    # clearly cooler than Maitreya's warm gilt at thumbnail. AD round 2
    # flagged that the warm cream let Guanyin collide with Maitreya in
    # day phase.
    return _mix(palette['stone_light'], (235, 240, 248), 0.70)


def _porcelain_shadow(palette):
    # Cool-cast shadow keeps the cool-white reading consistent.
    return _mix(palette['stone_mid'], (162, 172, 188), 0.58)


def _saffron_robe(palette):
    # Saffron-orange monastic robe band — used as a small accent.
    return _mix(palette['stone_accent'], (216, 140, 56), 0.72)


def _lotus_pink(palette):
    # Pink lotus base petals — anchored to stone_light + horizon.
    return _mix(palette['stone_light'],
                _mix(palette['horizon'], (242, 188, 196), 0.62), 0.62)


def _lotus_pink_deep(palette):
    return _mix(palette['stone_mid'],
                _mix(palette['horizon'], (198, 122, 138), 0.66), 0.58)


def _is_dark_sky(palette):
    top = palette['sky_top']
    return (top[0] + top[1] + top[2]) / 3.0 < 110


def _is_warming_sky(palette):
    top = palette['sky_top']
    avg = (top[0] + top[1] + top[2]) / 3.0
    return 60 <= avg < 110


# ── Shared primitives ──────────────────────────────────────────────────────

def _aa_polyline(surf, color, points, closed=False):
    if len(points) >= 2:
        try:
            pygame.draw.aalines(surf, color, closed, points)
        except (ValueError, TypeError):
            pygame.draw.lines(surf, color, closed, points, 1)


def _vert_gradient_rect(surf, rect, lit, mid, shadow):
    """3-stop vertical body gradient inside `rect` — turns a flat tone into
    a perceived cylinder so the warrior torso doesn't look like a stamp."""
    if rect.width < 2 or rect.height < 2:
        return
    n = rect.height
    for i in range(n):
        t = i / max(1, n - 1)
        if t < 0.5:
            col = _mix(lit, mid, t * 2)
        else:
            col = _mix(mid, shadow, (t - 0.5) * 2)
        pygame.draw.line(surf, col,
                         (rect.x, rect.y + i),
                         (rect.right - 1, rect.y + i), 1)


def _horiz_gradient_rect(surf, rect, lit, mid, shadow):
    """Per-column gradient — left-lit / right-shadow so a torso reads as
    a 3-D volume against a single light source."""
    if rect.width < 2 or rect.height < 2:
        return
    n = rect.width
    for i in range(n):
        t = i / max(1, n - 1)
        if t < 0.5:
            col = _mix(lit, mid, t * 2)
        else:
            col = _mix(mid, shadow, (t - 0.5) * 2)
        pygame.draw.line(surf, col,
                         (rect.x + i, rect.y),
                         (rect.x + i, rect.bottom - 1), 1)


def _draw_clay_plinth(surf, cx, base_y, w, palette, *, h=8):
    """Standard packed-earth plinth under a warrior — overhanging dark
    band + lit top edge. Sits under every terracotta figure so the
    family reads coherent and the soldier's feet don't float."""
    dark = _plinth_dark(palette)
    lit = _mix(palette['stone_light'], (208, 178, 138), 0.55)
    pygame.draw.rect(surf, dark, (cx - w // 2, base_y - h, w, h))
    pygame.draw.rect(surf, _shade(dark, -20),
                     (cx - w // 2 - 2, base_y - 2, w + 4, 2))
    pygame.draw.line(surf, lit,
                     (cx - w // 2, base_y - h),
                     (cx + w // 2 - 1, base_y - h), 1)


def _draw_lotus_plinth(surf, cx, base_y, w, palette, *, h=14, n_petals=9):
    """Lotus-throne plinth — half-fan of pink petals along the upper rim
    over a dark inner cushion. Used under seated/standing Buddha figures
    where the canonical iconography demands a lotus."""
    if w < 12 or h < 6:
        return
    pink = _lotus_pink(palette)
    deep = _lotus_pink_deep(palette)
    edge = _shade(deep, -30)
    bright = _shade(pink, 45)
    base_rect = pygame.Rect(cx - w // 2, base_y - h // 2, w, h // 2 + 2)
    pygame.draw.ellipse(surf, _shade(deep, -45), base_rect)
    pygame.draw.ellipse(surf, deep, base_rect.inflate(-2, -2))
    radius = w // 2 - 1
    cy = base_y - h // 2
    for i in range(n_petals):
        t = i / max(1, n_petals - 1)
        ang = math.pi + t * math.pi
        tip_x = cx + math.cos(ang) * radius
        tip_y = cy + math.sin(ang) * (h // 2 + 1)
        sl_ang = ang - 0.20
        sr_ang = ang + 0.20
        sl_x = cx + math.cos(sl_ang) * radius * 0.55
        sl_y = cy + math.sin(sl_ang) * (h // 2 + 1) * 0.55
        sr_x = cx + math.cos(sr_ang) * radius * 0.55
        sr_y = cy + math.sin(sr_ang) * (h // 2 + 1) * 0.55
        petal = [(int(cx), int(cy)),
                 (int(sl_x), int(sl_y)),
                 (int(tip_x), int(tip_y)),
                 (int(sr_x), int(sr_y))]
        pygame.draw.polygon(surf, edge, petal)
        inner = [(int(cx), int(cy)),
                 (int(sl_x + (tip_x - sl_x) * 0.18),
                  int(sl_y + (tip_y - sl_y) * 0.18)),
                 (int(tip_x), int(tip_y)),
                 (int(sr_x + (tip_x - sr_x) * 0.18),
                  int(sr_y + (tip_y - sr_y) * 0.18))]
        pygame.draw.polygon(surf, pink, inner)
        pygame.draw.line(surf, bright,
                         (int(tip_x), int(tip_y)),
                         (int(tip_x), int(tip_y)), 1)


def _draw_cliff_niche(surf, cx, base_y, w, h, palette,
                      *, outer_inflate_x=12, outer_inflate_y=10):
    """Cliff-face niche framing the Leshan Buddha. Round 2: the cliff
    is drawn as STRUCTURAL sedimentary rock — horizontal strata bands
    of varying height + deeper colour transitions stack from base to
    sky, then the niche is excavated THROUGH them so the strata edges
    bookmark the niche on left + right walls. Drawn BEFORE the Buddha
    body so the figure sits IN the niche."""
    if w < 14 or h < 24:
        return
    cliff_dark = _sandstone_shadow(palette)
    cliff_mid = _sandstone_warm(palette)
    cliff_lit = _sandstone_lit(palette)
    inner = _shade(cliff_dark, -30)
    rect = pygame.Rect(cx - w // 2, base_y - h, w, h)
    outer_rect = rect.inflate(outer_inflate_x, outer_inflate_y)

    # ── Structural strata bands. Each band has its own height + tone
    # so the cliff reads as carved sandstone, not a flat slab. Heights
    # vary irregularly between bands (sandstone-rich + erosion-thin
    # interleave); tones progress from warm at base to cool at top so
    # the cliff has vertical depth.
    band_seeds = (0.22, 0.13, 0.30, 0.10, 0.18, 0.25, 0.14)
    norm = sum(band_seeds)
    y = outer_rect.bottom
    accum = 0
    bands = []
    for sb in band_seeds:
        bh = max(3, int(outer_rect.height * (sb / norm)))
        bands.append((y - bh, bh))
        y -= bh
        accum += bh
    # Fill remainder with the top-most band to cover any rounding.
    if y > outer_rect.y:
        bands[-1] = (outer_rect.y, bands[-1][1] + (y - outer_rect.y))

    for i, (by, bh) in enumerate(bands):
        # Gradient from warm body at base to cooler shadow at the top.
        t = i / max(1, len(bands) - 1)
        band_body = _mix(cliff_mid, cliff_dark, t * 0.65)
        band_top = _mix(cliff_lit, cliff_mid, t * 0.55)
        pygame.draw.rect(surf, band_body,
                         (outer_rect.x, by, outer_rect.width, bh))
        # Lit top edge of each band — the canonical strata cue.
        pygame.draw.line(surf, band_top,
                         (outer_rect.x, by),
                         (outer_rect.right - 1, by), 1)
        # Dark crack at the band base — the bedding plane.
        pygame.draw.line(surf, _shade(band_body, -25),
                         (outer_rect.x, by + bh - 1),
                         (outer_rect.right - 1, by + bh - 1), 1)
        # A few erosion pits scattered along the band — small darker
        # pixels to break up the flat fill.
        for k in range(3):
            px = outer_rect.x + 3 + ((i * 13 + k * 21) % (outer_rect.width - 6))
            py = by + max(1, bh // 2) + ((k + i) % max(1, bh // 2))
            pygame.draw.line(surf, _shade(band_body, -20),
                             (px, py), (px, py), 1)

    # ── Niche cut THROUGH the strata: dark inner recess with rounded
    # arched top. Drawn LAST so it overrides the band fills inside the
    # niche bounds, leaving the strata as visible edges along the
    # exterior walls.
    arch_h = max(10, h // 4)
    pygame.draw.rect(surf, inner,
                     (rect.x, rect.y + arch_h, rect.w, rect.h - arch_h))
    pygame.draw.ellipse(surf, inner,
                        (rect.x, rect.y, rect.w, arch_h * 2))
    # Dark rim on the niche wall — gives the recess its carved depth.
    pygame.draw.line(surf, _shade(inner, -15),
                     (rect.x, rect.y + arch_h),
                     (rect.x, rect.bottom - 1), 1)
    pygame.draw.line(surf, _shade(inner, -15),
                     (rect.right - 1, rect.y + arch_h),
                     (rect.right - 1, rect.bottom - 1), 1)
    # Light hit on the upper inside of the arch (lit from above).
    pygame.draw.arc(surf, _shade(cliff_mid, -30),
                    (rect.x + 1, rect.y + 1, rect.w - 2, arch_h * 2 - 2),
                    math.pi * 0.15, math.pi * 0.85, 1)


def _draw_lit_halo(surf, cx, cy, r, palette, *, intensity=1.0):
    """Additive amber halo behind a Buddha head — quiet at noon, hot at
    night. Used by Tian Tan + Maitreya + Guanyin where the iconography
    canonically gets a circle aureole."""
    if r < 6:
        return
    dark = _is_dark_sky(palette)
    warm = _is_warming_sky(palette)
    if dark and not warm:
        alphas = (160, 110, 70)
    elif warm:
        alphas = (110, 75, 45)
    else:
        alphas = (55, 38, 22)
    rim = _mix(palette['stone_accent'], (255, 220, 130), 0.78)
    sz = r * 2 + 4
    g = pygame.Surface((sz, sz), pygame.SRCALPHA)
    for k, a in enumerate(alphas):
        pygame.draw.circle(g, (*rim, int(a * intensity)),
                           (sz // 2, sz // 2), r - k * (r // 4))
    surf.blit(g, (cx - sz // 2, cy - sz // 2),
              special_flags=pygame.BLEND_RGBA_ADD)


# ── Per-candidate cache ────────────────────────────────────────────────────

_PILLAR_CACHE: dict = {}


def _palette_key(palette):
    return (palette['sky_top'], palette['stone_dark'],
            palette['stone_mid'], palette['stone_light'],
            palette['stone_accent'])


def _cached_draw(candidate_name, draw_fn, surf, top_rect, bot_rect,
                 palette, seed):
    key = (candidate_name, seed, _palette_key(palette),
           top_rect.x, top_rect.y, top_rect.w, top_rect.h,
           bot_rect.x, bot_rect.y, bot_rect.w, bot_rect.h)
    bitmap = _PILLAR_CACHE.get(key)
    if bitmap is None:
        bitmap = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        draw_fn(bitmap, top_rect, bot_rect, palette, seed)
        _PILLAR_CACHE[key] = bitmap
    surf.blit(bitmap, (0, 0))


def _mirror_top(surf, top_rect, body_h_natural, draw_fn, *,
                tmp_w_factor=4, min_tmp_w=120, mirror_strategy="flip"):
    """R11 mirror + R12 adaptive count + R13 stretch into top_rect.

    `body_h_natural` is the bottom's natural full-figure height (from
    plinth to head-top). `draw_fn(tmp, tmp_cx, base_y, top_y)` paints
    the same anatomy bottom-anchored at `base_y` with a head ceiling
    at `top_y`. We size `tmp_h` so the figure (slightly compressed or
    stretched, ±30%) exactly fills the top_rect; out-of-bounds ratios
    fall back to the natural height and leave a small sky band rather
    than distort the silhouette.

    `mirror_strategy` decides how the top pillar mirrors the bottom:
      - "flip" — classic vertical flip (default). Right for symmetric
        figures where a vertical flip still reads naturally.
      - "redraw" — draw the SAME figure non-flipped into the top rect,
        head-down anchored at top_rect.top + figure_h, so the top
        reads as a SECOND statue facing the same direction. Use for
        variants with asymmetric props (vase, cloth bag) where a
        vertical flip would invert the prop into nonsense.
      - "flip_horizontal" — vertically flipped AND horizontally
        mirrored, so the top reads as a paired guardian figure
        facing inward."""
    if top_rect.height < 50:
        return
    top_avail = top_rect.height
    ratio = top_avail / max(1, body_h_natural)
    # Round 3: tighten the upper clamp from 1.3 → 1.25. AD flagged head
    # clipping on Maitreya + Guanyin in tall top slots where the figure
    # was being stretched past its natural proportions; the lower
    # ceiling drops back to the natural height and leaves a small sky
    # band rather than slicing the crown/ushnisha.
    if 0.7 <= ratio <= 1.25:
        tmp_h = top_avail
    else:
        tmp_h = body_h_natural
    tmp_w = max(top_rect.width * tmp_w_factor, min_tmp_w)
    tmp = pygame.Surface((tmp_w, tmp_h), pygame.SRCALPHA)
    tmp_cx = tmp_w // 2
    draw_fn(tmp, tmp_cx, tmp_h - 1, 0)
    tcx = top_rect.x + top_rect.width // 2
    if mirror_strategy == "redraw":
        # Bottom-aligned with the slot bottom — the figure stands
        # right-side-up in the top slot, as if a second matching
        # statue had been carved.
        surf.blit(tmp, (tcx - tmp_w // 2,
                        top_rect.bottom - tmp_h))
    elif mirror_strategy == "flip_horizontal":
        flipped = pygame.transform.flip(tmp, True, True)
        surf.blit(flipped, (tcx - tmp_w // 2, top_rect.y))
    else:
        flipped = pygame.transform.flip(tmp, False, True)
        surf.blit(flipped, (tcx - tmp_w // 2, top_rect.y))


# ── 1. Terracotta General (高级军吏俑) ──────────────────────────────────────
#
# Highest-ranking officer figure: only ~10 ever excavated. Identifying
# cues at scale: tall double-fish-tail crown ribbon-knot ("guan"), long
# ceremonial robe past the knee, elaborate plated armour with knot
# ribbons at chest, hands clasped over the abdomen.
#
# References:
#   https://www.smithsonianmag.com/smart-news/archaeologists-discover-rare-clay-commander-among-thousands-of-life-size-terra-cotta-soldiers-in-china-180985747/
#   https://en.wikipedia.org/wiki/Terracotta_Army

def _draw_general_figure(surf, cx, base_y, top_y, palette):
    """Bottom-anchored high officer. `base_y` is feet line, `top_y`
    clamps the crown tip — figure auto-scales to fit."""
    total = base_y - top_y
    if total < 60:
        return
    body = _clay_body(palette)
    lit = _clay_lit(palette)
    shadow = _clay_shadow(palette)
    crack = _clay_crack(palette)
    vermilion = _pigment_vermilion(palette)
    celadon = _pigment_celadon(palette)
    ochre = _pigment_ochre(palette)
    white = _pigment_white(palette)

    # Vertical budget split — taller crown for officer rank, beefed
    # up vs round 1 so the silhouette reads "officer" at thumbnail.
    crown_h = max(12, int(total * 0.17))
    head_h = max(10, int(total * 0.13))
    neck_h = max(2, int(total * 0.03))
    torso_h = max(20, int(total * 0.35))
    skirt_h = max(14, int(total * 0.24))
    feet_h = total - crown_h - head_h - neck_h - torso_h - skirt_h

    y = base_y
    # ── Feet/shoes (square-toed Qin shoes peeking under robe) ──────────
    shoe_w = max(10, int(total * 0.16))
    pygame.draw.rect(surf, shadow, (cx - shoe_w // 2, y - feet_h,
                                     shoe_w, feet_h))
    pygame.draw.rect(surf, body, (cx - shoe_w // 2 + 1, y - feet_h + 1,
                                   shoe_w - 2, feet_h - 2))
    # Split between two feet — center vertical groove.
    pygame.draw.line(surf, crack,
                     (cx, y - feet_h + 1), (cx, y - 1), 1)
    y -= feet_h

    # ── Skirt / lower ceremonial robe — flared trapezoid ───────────────
    skirt_top_w = max(14, int(total * 0.21))
    skirt_bot_w = max(skirt_top_w + 4, int(total * 0.28))
    skirt_pts = [
        (cx - skirt_bot_w // 2, y),
        (cx + skirt_bot_w // 2, y),
        (cx + skirt_top_w // 2, y - skirt_h),
        (cx - skirt_top_w // 2, y - skirt_h),
    ]
    pygame.draw.polygon(surf, shadow, skirt_pts)
    inner = [
        (cx - skirt_bot_w // 2 + 1, y - 1),
        (cx + skirt_bot_w // 2 - 1, y - 1),
        (cx + skirt_top_w // 2 - 1, y - skirt_h + 1),
        (cx - skirt_top_w // 2 + 1, y - skirt_h + 1),
    ]
    pygame.draw.polygon(surf, body, inner)
    # Lit edge on the left flank.
    pygame.draw.line(surf, lit,
                     (cx - skirt_top_w // 2 + 1, y - skirt_h + 2),
                     (cx - skirt_bot_w // 2 + 1, y - 1), 1)
    # Vertical robe-fold creases — 3 lines down the skirt.
    for k in range(-1, 2):
        fx = cx + k * (skirt_top_w // 4)
        pygame.draw.line(surf, _shade(body, -25),
                         (fx, y - skirt_h + 3), (fx, y - 2), 1)
    # Saffron sash band wrapping the waist — bottom of torso.
    pygame.draw.rect(surf, vermilion,
                     (cx - skirt_top_w // 2, y - skirt_h - 1,
                      skirt_top_w, 2))
    y -= skirt_h

    # ── Torso + plated armour ──────────────────────────────────────────
    torso_w = max(14, int(total * 0.22))
    armour_top = y - torso_h
    pygame.draw.rect(surf, shadow,
                     (cx - torso_w // 2, armour_top, torso_w, torso_h))
    # 3-stop horizontal volume.
    _horiz_gradient_rect(surf,
                         pygame.Rect(cx - torso_w // 2 + 1, armour_top + 1,
                                     torso_w - 2, torso_h - 2),
                         lit, body, shadow)
    # Scale-armour plates — 4 rows × 3 cols of small rounded squares,
    # only on the chest panel.
    plate_cols = 3
    plate_rows = max(3, torso_h // 7)
    plate_w = max(2, (torso_w - 6) // plate_cols)
    plate_h = max(2, (torso_h - 8) // plate_rows)
    panel_top = armour_top + 4
    panel_left = cx - (plate_cols * plate_w) // 2
    for r in range(plate_rows):
        for c in range(plate_cols):
            px = panel_left + c * plate_w
            py = panel_top + r * plate_h
            pygame.draw.rect(surf, _shade(body, -15),
                             (px, py, plate_w - 1, plate_h - 1))
            pygame.draw.line(surf, lit, (px, py),
                             (px + plate_w - 2, py), 1)
            # White-stitching trace between plates.
            if r > 0 and r % 2 == 0:
                pygame.draw.line(surf, white,
                                 (px, py - 1),
                                 (px + plate_w - 2, py - 1), 1)
    # Ribbon-knot at chest centre — the canonical officer cue. Vermilion
    # bow with two trailing tails.
    knot_y = armour_top + torso_h // 3
    pygame.draw.rect(surf, vermilion, (cx - 2, knot_y, 4, 3))
    pygame.draw.line(surf, vermilion,
                     (cx - 3, knot_y + 3), (cx - 4, knot_y + 7), 1)
    pygame.draw.line(surf, vermilion,
                     (cx + 3, knot_y + 3), (cx + 4, knot_y + 7), 1)
    pygame.draw.line(surf, _shade(vermilion, 35),
                     (cx - 1, knot_y + 1), (cx, knot_y + 1), 1)
    # Shoulder pad — wider than torso, dark edged.
    pad_y = armour_top - 1
    pad_w = torso_w + 6
    pygame.draw.rect(surf, shadow,
                     (cx - pad_w // 2, pad_y, pad_w, 3))
    pygame.draw.rect(surf, body,
                     (cx - pad_w // 2 + 1, pad_y, pad_w - 2, 2))
    pygame.draw.line(surf, ochre,
                     (cx - pad_w // 2 + 1, pad_y),
                     (cx + pad_w // 2 - 2, pad_y), 1)
    # Hands clasped at abdomen — small dark oval below knot.
    hand_y = armour_top + (torso_h * 2) // 3
    pygame.draw.ellipse(surf, shadow,
                        (cx - 5, hand_y - 1, 10, 4))
    pygame.draw.ellipse(surf, body,
                        (cx - 4, hand_y - 1, 8, 3))
    y = armour_top

    # ── Neck ────────────────────────────────────────────────────────────
    neck_w = max(4, int(total * 0.06))
    pygame.draw.rect(surf, shadow,
                     (cx - neck_w // 2, y - neck_h, neck_w, neck_h))
    pygame.draw.rect(surf, body,
                     (cx - neck_w // 2, y - neck_h, neck_w - 1, neck_h - 1))
    y -= neck_h

    # ── Head ────────────────────────────────────────────────────────────
    head_w = max(10, int(total * 0.14))
    head_rect = pygame.Rect(cx - head_w // 2, y - head_h, head_w, head_h)
    pygame.draw.ellipse(surf, shadow, head_rect)
    pygame.draw.ellipse(surf, body, head_rect.inflate(-2, -2))
    # Tiny lit-side highlight on left cheek.
    pygame.draw.line(surf, lit,
                     (head_rect.x + 2, head_rect.y + head_h // 3),
                     (head_rect.x + 2, head_rect.y + (head_h * 2) // 3), 1)
    # Mustache + beard line — single dark hairline.
    pygame.draw.line(surf, crack,
                     (cx - 3, head_rect.bottom - 3),
                     (cx + 3, head_rect.bottom - 3), 1)
    y -= head_h

    # ── Double fish-tail crown (guan) — the rank signature.
    # Round 2: WIDER + TALLER so the silhouette reads "officer"
    # instantly at thumbnail. Drawn as two outward-curling tapered
    # wedges meeting at centre. Each tail is a convex pentagon that
    # rises from the base + flares outward, then comes to a hooked
    # tip pointing slightly outward-up.
    crown_base_w = max(12, int(total * 0.20))
    pygame.draw.rect(surf, shadow,
                     (cx - crown_base_w // 2, y - 3, crown_base_w, 5))
    pygame.draw.rect(surf, body,
                     (cx - crown_base_w // 2 + 1, y - 2,
                      crown_base_w - 2, 3))
    # Each fish-tail — convex tapered wedge from base to outward-
    # hooking tip. The flare is BIG (the iconic guan signature).
    tail_h = crown_h
    flare = max(7, int(total * 0.10))
    for side in (-1, 1):
        # Pentagon: base inner, base outer, mid outer (flare apex),
        # tip top (curling slightly back inward), tip inner.
        pts = [
            (cx + side * 1, y - 2),                              # base inner
            (cx + side * 4, y - 2),                              # base outer
            (cx + side * flare, y - 2 - tail_h // 2),            # mid flare
            (cx + side * (flare - 2), y - 2 - tail_h),           # tip outer
            (cx + side * 1, y - 2 - tail_h + 2),                 # tip inner
        ]
        pygame.draw.polygon(surf, shadow, pts)
        # Inner highlight wedge — 1 px inset on lit side.
        inner_pts = [
            (cx + side * 1, y - 3),
            (cx + side * 3, y - 3),
            (cx + side * (flare - 1), y - 3 - tail_h // 2),
            (cx + side * (flare - 3), y - 3 - tail_h + 1),
            (cx + side * 1, y - 3 - tail_h + 3),
        ]
        pygame.draw.polygon(surf, body, inner_pts)
        # Ochre band along the fish-tail spine.
        pygame.draw.line(surf, ochre,
                         (cx + side * 2, y - 3),
                         (cx + side * (flare - 1), y - 3 - tail_h // 2), 1)
        pygame.draw.line(surf, ochre,
                         (cx + side * (flare - 1), y - 3 - tail_h // 2),
                         (cx + side * (flare - 2), y - 2 - tail_h + 1), 1)
        # Hot tip — white pigment dot at the outermost point.
        pygame.draw.line(surf, _pigment_white(palette),
                         (cx + side * (flare - 2), y - 2 - tail_h + 1),
                         (cx + side * (flare - 2), y - 2 - tail_h + 1), 1)


def _draw_general_polearm(surf, cx, base_y, top_y, palette):
    """Ceremonial polearm — tall vertical staff with a flame-shaped
    spear blade at the tip, held against the right flank of the
    officer. Round 2 silhouette-diff vs charioteer: this single
    vertical element rises ABOVE the crown so the General's pillar
    has a clean spear-tip apex profile that no other warrior shares.
    Drawn BEFORE the figure so the body can overlap the shaft."""
    if base_y - top_y < 60:
        return
    shaft_x = cx + 9
    crack = _clay_crack(palette)
    body = _clay_body(palette)
    ochre = _pigment_ochre(palette)
    vermilion = _pigment_vermilion(palette)
    # Staff — dark walnut wood column from plinth to spear base.
    spear_h = max(10, (base_y - top_y) // 8)
    shaft_top_y = top_y + spear_h + 1
    pygame.draw.line(surf, crack,
                     (shaft_x, shaft_top_y), (shaft_x, base_y - 2), 2)
    pygame.draw.line(surf, _shade(body, -10),
                     (shaft_x + 1, shaft_top_y),
                     (shaft_x + 1, base_y - 2), 1)
    # Ochre wrap at the grip — a short band at torso height.
    grip_y = base_y - (base_y - top_y) // 3
    pygame.draw.rect(surf, ochre,
                     (shaft_x - 1, grip_y, 4, 2))
    pygame.draw.line(surf, vermilion,
                     (shaft_x - 1, grip_y + 2), (shaft_x + 2, grip_y + 2), 1)
    # Spear head — flame-leaf bronze blade at the apex.
    blade_w = max(3, spear_h // 3)
    pygame.draw.polygon(surf, _bronze_dark(palette), [
        (shaft_x, shaft_top_y),
        (shaft_x - blade_w, shaft_top_y - spear_h // 2),
        (shaft_x, top_y),
        (shaft_x + blade_w, shaft_top_y - spear_h // 2),
    ])
    pygame.draw.polygon(surf, _bronze_lit(palette), [
        (shaft_x, shaft_top_y - 1),
        (shaft_x - blade_w + 1, shaft_top_y - spear_h // 2),
        (shaft_x, top_y + 1),
    ])


def _draw_general(surf, top_rect, bot_rect, palette, seed):
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    plinth_w = int(bot_rect.width * 1.18)
    plinth_h = 8

    if bot_rect.height > 80:
        _draw_clay_plinth(surf, bcx, bot_rect.bottom, plinth_w, palette,
                          h=plinth_h)
        # Polearm BEFORE the figure so the body overlaps the shaft and
        # the staff reads as held against the right flank.
        figure_top = bot_rect.y + 4
        figure_base = bot_rect.bottom - plinth_h
        _draw_general_polearm(surf, bcx, figure_base, figure_top, palette)
        _draw_general_figure(surf, bcx, figure_base, figure_top, palette)
        # Side flair — pair of battle pennants on TALLER posts, pushed
        # further out so the silhouette flares past the pillar core.
        for side in (-1, 1):
            sx = bcx + side * (plinth_w // 2 + 5)
            pygame.draw.line(surf, _shade(_clay_body(palette), -45),
                             (sx, bot_rect.bottom - 1),
                             (sx, bot_rect.bottom - 16), 1)
            # Twin-tail pennant — bigger triangular flag with a forked
            # trailing tail so the silhouette reads as a battle-standard.
            pygame.draw.polygon(surf, _pigment_vermilion(palette),
                                [(sx, bot_rect.bottom - 16),
                                 (sx + side * 6, bot_rect.bottom - 13),
                                 (sx + side * 5, bot_rect.bottom - 10),
                                 (sx + side * 7, bot_rect.bottom - 7),
                                 (sx, bot_rect.bottom - 9)])
            pygame.draw.line(surf, _pigment_ochre(palette),
                             (sx, bot_rect.bottom - 16),
                             (sx + side * 6, bot_rect.bottom - 13), 1)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 6, 14, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 6, seed=seed)

    natural_h = max(120, bot_rect.height - plinth_h - 4)

    def draw_into(tmp, tmp_cx, base_y, top_y):
        _draw_clay_plinth(tmp, tmp_cx, base_y, plinth_w, palette,
                          h=plinth_h)
        _draw_general_polearm(tmp, tmp_cx, base_y - plinth_h, top_y + 4,
                              palette)
        _draw_general_figure(tmp, tmp_cx, base_y - plinth_h, top_y + 4,
                             palette)

    _mirror_top(surf, top_rect, natural_h, draw_into,
                mirror_strategy="flip")


def candidate_warrior_general(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('warrior_general', _draw_general, surf, top_rect,
                 bot_rect, palette, seed)


# ── 2. Standing Archer / Infantry (立射俑) ─────────────────────────────────
#
# Standing archer — left leg slightly forward, torso lean, left arm
# raised forward and slightly down ready to draw, right arm bent to
# chest. Lightly armoured: leather scale-vest, NO long ceremonial
# robe (combat infantry). Topknot hair-bun.
#
# References:
#   https://www.travelchinaguide.com/attraction/shaanxi/xian/terra_cotta_army/standing-archers.htm
#   https://en.wikipedia.org/wiki/Terracotta_Army

def _draw_archer_figure(surf, cx, base_y, top_y, palette):
    total = base_y - top_y
    if total < 60:
        return
    body = _clay_body(palette)
    lit = _clay_lit(palette)
    shadow = _clay_shadow(palette)
    crack = _clay_crack(palette)
    celadon = _pigment_celadon(palette)
    vermilion = _pigment_vermilion(palette)
    ochre = _pigment_ochre(palette)
    white = _pigment_white(palette)

    bun_h = max(4, int(total * 0.07))
    head_h = max(9, int(total * 0.13))
    neck_h = max(2, int(total * 0.03))
    torso_h = max(20, int(total * 0.34))
    leg_h = total - bun_h - head_h - neck_h - torso_h

    y = base_y

    # ── Legs — left foot slightly forward (lean stance) ────────────────
    leg_w = max(4, int(total * 0.06))
    foot_w = leg_w + 3
    # Right leg (rear) — fully vertical.
    rl_x = cx + 4
    pygame.draw.rect(surf, shadow,
                     (rl_x - leg_w // 2, y - leg_h, leg_w, leg_h))
    pygame.draw.rect(surf, body,
                     (rl_x - leg_w // 2 + 1, y - leg_h,
                      leg_w - 2, leg_h - 1))
    # Right foot.
    pygame.draw.rect(surf, shadow,
                     (rl_x - foot_w // 2, y - 3, foot_w, 3))
    # Left leg (front) — angled slightly forward (left at base).
    ll_x = cx - 5
    pts = [
        (ll_x - leg_w // 2 + 1, y - leg_h),
        (ll_x + leg_w // 2, y - leg_h),
        (ll_x + leg_w // 2 - 2, y),
        (ll_x - leg_w // 2 - 1, y),
    ]
    pygame.draw.polygon(surf, shadow, pts)
    pygame.draw.polygon(surf, body,
                        [(p[0] + (1 if i < 2 else -1), p[1])
                         for i, p in enumerate(pts)])
    # Left foot pointing forward.
    pygame.draw.rect(surf, shadow,
                     (ll_x - foot_w // 2 - 2, y - 3, foot_w + 1, 3))
    # Calf-binding wraps — 2 short horizontal ochre bands per leg.
    for ly in (y - leg_h // 3, y - (leg_h * 2) // 3):
        pygame.draw.line(surf, ochre,
                         (rl_x - leg_w // 2, ly),
                         (rl_x + leg_w // 2 - 1, ly), 1)
        pygame.draw.line(surf, ochre,
                         (ll_x - leg_w // 2, ly),
                         (ll_x + leg_w // 2 - 1, ly), 1)
    y -= leg_h

    # ── Torso — leather scale vest, slight forward lean ────────────────
    torso_w = max(12, int(total * 0.20))
    torso_top = y - torso_h
    # Lean — torso shifted slightly LEFT toward draw-arm direction.
    lean = 2
    torso_pts = [
        (cx - torso_w // 2, y),
        (cx + torso_w // 2, y),
        (cx + torso_w // 2 + lean, torso_top + 2),
        (cx - torso_w // 2 + lean, torso_top + 2),
    ]
    pygame.draw.polygon(surf, shadow, torso_pts)
    inner_pts = [
        (cx - torso_w // 2 + 1, y - 1),
        (cx + torso_w // 2 - 1, y - 1),
        (cx + torso_w // 2 + lean - 1, torso_top + 3),
        (cx - torso_w // 2 + lean + 1, torso_top + 3),
    ]
    pygame.draw.polygon(surf, body, inner_pts)
    # Scale-armour — rows of celadon-tinted small plates across chest.
    plate_rows = max(2, torso_h // 7)
    plate_w = 3
    panel_top = torso_top + 4
    panel_h = torso_h - 8
    if panel_h > 4 and torso_w > 8:
        for r in range(plate_rows):
            ny = panel_top + r * (panel_h // plate_rows)
            for c in range(-2, 3):
                px = cx + c * plate_w + lean // 2
                pygame.draw.rect(surf, _shade(body, -25),
                                 (px, ny, plate_w - 1, 2))
                pygame.draw.line(surf, celadon, (px, ny), (px + 1, ny), 1)
    # Right arm — bent at the chest, palm in (resting at clavicle).
    arm_shadow = _shade(body, -25)
    r_arm_top = torso_top + 3
    r_arm_pts = [
        (cx + torso_w // 2 - 1, r_arm_top),
        (cx + torso_w // 2 + 5, r_arm_top + 4),
        (cx + torso_w // 2 + 3, r_arm_top + 11),
        (cx + 2, r_arm_top + 9),
        (cx + 2, r_arm_top + 5),
    ]
    pygame.draw.polygon(surf, arm_shadow, r_arm_pts)
    pygame.draw.polygon(surf, body,
                        [(p[0] - 1, p[1] + 1) for p in r_arm_pts])
    # Left arm — held tight to the side, hand gripping a vertical bow
    # STAVE against the flank. Round 2 fix: no horizontal extension,
    # so the silhouette no longer reads as broken anatomy.
    l_arm_top = torso_top + 3
    l_arm_pts = [
        (cx - torso_w // 2 + 1, l_arm_top),
        (cx - torso_w // 2 - 3, l_arm_top + 3),
        (cx - torso_w // 2 - 4, l_arm_top + 11),
        (cx - torso_w // 2, l_arm_top + 13),
        (cx - 1, l_arm_top + 11),
        (cx - 1, l_arm_top + 5),
    ]
    pygame.draw.polygon(surf, arm_shadow, l_arm_pts)
    inner = [
        (cx - torso_w // 2 + 1, l_arm_top + 1),
        (cx - torso_w // 2 - 2, l_arm_top + 4),
        (cx - torso_w // 2 - 3, l_arm_top + 10),
        (cx - 2, l_arm_top + 11),
        (cx - 2, l_arm_top + 6),
    ]
    pygame.draw.polygon(surf, body, inner)
    # Bow STAVE — vertical wooden stave held against the left flank.
    # Wood shaft from below the hand-grip up past the shoulder, with
    # a slight outward bow-curve away from the body so the silhouette
    # reads as "warrior with bow" rather than "warrior with a stick".
    bow_x = cx - torso_w // 2 - 5
    bow_top_y = torso_top - max(6, total // 10)
    bow_bot_y = y - 4  # slightly above the leg line
    pygame.draw.line(surf, crack,
                     (bow_x, bow_top_y), (bow_x, bow_bot_y), 2)
    # Outward bow-belly midway down the stave — drawn as a 3-segment
    # subtle curve, 1-2 px out at the centre.
    bow_mid_y = (bow_top_y + bow_bot_y) // 2
    pygame.draw.line(surf, crack,
                     (bow_x, bow_top_y), (bow_x - 2, bow_mid_y), 1)
    pygame.draw.line(surf, crack,
                     (bow_x - 2, bow_mid_y), (bow_x, bow_bot_y), 1)
    # Bowstring — a faint celadon line connecting tip to tip just
    # inside the belly.
    pygame.draw.line(surf, _shade(celadon, -20),
                     (bow_x + 1, bow_top_y),
                     (bow_x + 1, bow_bot_y), 1)
    # Bow nocks — small ochre caps at each tip.
    pygame.draw.line(surf, ochre,
                     (bow_x - 1, bow_top_y), (bow_x + 1, bow_top_y), 1)
    pygame.draw.line(surf, ochre,
                     (bow_x - 1, bow_bot_y), (bow_x + 1, bow_bot_y), 1)
    # Bow-hand fingers gripping the stave — a darker line where the
    # hand wraps the wood.
    pygame.draw.line(surf, crack,
                     (cx - torso_w // 2 - 5, l_arm_top + 12),
                     (cx - torso_w // 2 - 3, l_arm_top + 12), 1)
    # Belt across the torso bottom — vermilion sash with knot.
    pygame.draw.rect(surf, vermilion,
                     (cx - torso_w // 2 + 1, y - 3, torso_w - 2, 2))
    pygame.draw.rect(surf, _shade(vermilion, 30), (cx - 1, y - 4, 3, 4))
    y = torso_top

    # ── Neck ────────────────────────────────────────────────────────────
    pygame.draw.rect(surf, shadow,
                     (cx - 2, y - neck_h, 4, neck_h))
    pygame.draw.rect(surf, body,
                     (cx - 1, y - neck_h, 3, neck_h))
    y -= neck_h

    # ── Head ────────────────────────────────────────────────────────────
    head_w = max(9, int(total * 0.13))
    head_rect = pygame.Rect(cx - head_w // 2, y - head_h, head_w, head_h)
    pygame.draw.ellipse(surf, shadow, head_rect)
    pygame.draw.ellipse(surf, body, head_rect.inflate(-2, -2))
    pygame.draw.line(surf, lit,
                     (head_rect.x + 2, head_rect.y + head_h // 3),
                     (head_rect.x + 2, head_rect.y + (head_h * 2) // 3), 1)
    # Focused gaze — single dark eye dot.
    pygame.draw.line(surf, crack,
                     (cx - 2, head_rect.y + head_h // 2 - 1),
                     (cx - 1, head_rect.y + head_h // 2 - 1), 1)
    y -= head_h

    # ── Topknot bun (上挽圆髻) — pulled to the right side, the canonical
    # infantry hairstyle. Offset by +2 px so the knot reads as a side
    # bun, not a centre crown. ──────────────────────────────────────────
    bun_w = max(5, int(total * 0.09))
    bun_x = cx + 2
    pygame.draw.ellipse(surf, shadow,
                        (bun_x - bun_w // 2, y - bun_h, bun_w, bun_h + 1))
    pygame.draw.ellipse(surf, body,
                        (bun_x - bun_w // 2 + 1, y - bun_h + 1,
                         bun_w - 2, bun_h - 1))
    # Hair pin — tiny ochre slash.
    pygame.draw.line(surf, ochre,
                     (bun_x - bun_w // 4, y - bun_h // 2),
                     (bun_x + bun_w // 4, y - bun_h // 2 + 1), 1)


def _draw_archer(surf, top_rect, bot_rect, palette, seed):
    bcx = bot_rect.x + bot_rect.width // 2
    plinth_w = int(bot_rect.width * 1.16)
    plinth_h = 8

    if bot_rect.height > 80:
        _draw_clay_plinth(surf, bcx, bot_rect.bottom, plinth_w, palette,
                          h=plinth_h)
        figure_top = bot_rect.y + 4
        figure_base = bot_rect.bottom - plinth_h
        _draw_archer_figure(surf, bcx, figure_base, figure_top, palette)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 6, 14, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 6, seed=seed)

    natural_h = max(120, bot_rect.height - plinth_h - 4)

    def draw_into(tmp, tmp_cx, base_y, top_y):
        _draw_clay_plinth(tmp, tmp_cx, base_y, plinth_w, palette,
                          h=plinth_h)
        _draw_archer_figure(tmp, tmp_cx, base_y - plinth_h, top_y + 4,
                            palette)

    _mirror_top(surf, top_rect, natural_h, draw_into,
                mirror_strategy="flip")


def candidate_warrior_standing_archer(surf, top_rect, bot_rect, palette,
                                      seed):
    _cached_draw('warrior_archer', _draw_archer, surf, top_rect,
                 bot_rect, palette, seed)


# ── 3. Kneeling Crossbowman (跪射俑) ───────────────────────────────────────
#
# The museum-icon. Kneels on right knee, left knee up. Hands at waist
# right side, frozen as if gripping a crossbow horizontally. Hair-bun
# at the back of the head, full scale-armour vest. Famously the BEST
# preserved Qin figures because the low crouch protected them.
#
# References:
#   https://www.travelchinaguide.com/attraction/shaanxi/xian/terra_cotta_army/kneeling-archers.htm
#   https://ancientwarhistory.com/the-enigmatic-kneeling-archers-of-the-terracotta-army-history-mystery-and-modern-fascination/

def _draw_kneeling_figure(surf, cx, base_y, top_y, palette):
    total = base_y - top_y
    if total < 60:
        return
    body = _clay_body(palette)
    lit = _clay_lit(palette)
    shadow = _clay_shadow(palette)
    crack = _clay_crack(palette)
    celadon = _pigment_celadon(palette)
    vermilion = _pigment_vermilion(palette)
    ochre = _pigment_ochre(palette)
    white = _pigment_white(palette)

    # The kneel compresses the figure: legs ~ 35% of total, torso ~ 30%,
    # head + bun ~ 20%, the rest is the crouch ground anchor.
    crouch_h = max(6, int(total * 0.10))
    legs_h = max(14, int(total * 0.28))
    torso_h = max(22, int(total * 0.36))
    bun_h = max(5, int(total * 0.07))
    head_h = total - crouch_h - legs_h - torso_h - bun_h

    y = base_y

    # ── Crouch ground anchor — boots + right shin laid flat ────────────
    base_w = max(16, int(total * 0.30))
    pygame.draw.rect(surf, shadow,
                     (cx - base_w // 2, y - crouch_h, base_w, crouch_h))
    pygame.draw.rect(surf, body,
                     (cx - base_w // 2 + 1, y - crouch_h + 1,
                      base_w - 2, crouch_h - 2))
    # Right boot stretched flat — long oval to the left.
    boot_pts = [
        (cx - base_w // 2 - 2, y - 2),
        (cx + 2, y - 2),
        (cx + 2, y - crouch_h + 1),
        (cx - base_w // 2 - 1, y - crouch_h + 1),
    ]
    pygame.draw.polygon(surf, _shade(body, -20), boot_pts)
    pygame.draw.line(surf, lit,
                     (cx - base_w // 2 - 1, y - crouch_h + 1),
                     (cx + 1, y - crouch_h + 1), 1)
    y -= crouch_h

    # ── Lower body — right shin extends LEFT (lying flat under the body),
    # left thigh angles UP-FORWARD to support the raised knee ──────────
    # Right shin (flat).
    shin_w = max(7, int(total * 0.11))
    pygame.draw.rect(surf, shadow,
                     (cx - shin_w, y - shin_w // 2 - 1, shin_w + 2,
                      shin_w // 2 + 1))
    pygame.draw.rect(surf, body,
                     (cx - shin_w + 1, y - shin_w // 2,
                      shin_w, shin_w // 2 - 1))
    # Raised left knee — angled trapezoid up to the front.
    knee_top_y = y - legs_h
    knee_pts = [
        (cx - 2, y),
        (cx + 10, y),
        (cx + 9, knee_top_y),
        (cx + 1, knee_top_y),
    ]
    pygame.draw.polygon(surf, shadow, knee_pts)
    inner = [
        (cx - 1, y - 1),
        (cx + 9, y - 1),
        (cx + 8, knee_top_y + 1),
        (cx + 2, knee_top_y + 1),
    ]
    pygame.draw.polygon(surf, body, inner)
    # Lit edge on left side of the knee.
    pygame.draw.line(surf, lit,
                     (cx + 2, knee_top_y + 1),
                     (cx - 1, y - 1), 1)
    # Calf-binding wrap on the raised shin.
    for ly in (knee_top_y + legs_h // 3,
               knee_top_y + (legs_h * 2) // 3):
        pygame.draw.line(surf, ochre,
                         (cx + 1, ly), (cx + 8, ly), 1)
    y = knee_top_y

    # ── Torso — full scale-armour vest, tight upright ───────────────────
    torso_w = max(14, int(total * 0.22))
    torso_top = y - torso_h
    pygame.draw.rect(surf, shadow,
                     (cx - torso_w // 2, torso_top, torso_w, torso_h))
    _vert_gradient_rect(surf,
                        pygame.Rect(cx - torso_w // 2 + 1, torso_top + 1,
                                    torso_w - 2, torso_h - 2),
                        lit, body, shadow)
    # Scale plates over the entire vest — DENSER than the standing
    # archer's because kneeling crossbowmen wore full scale.
    plate_w = 3
    plate_h = 3
    panel_top = torso_top + 3
    panel_h = torso_h - 6
    rows = panel_h // plate_h
    for r in range(rows):
        for c in range(-3, 4):
            px = cx + c * plate_w
            py = panel_top + r * plate_h
            if r % 2 == 1:
                px += 1
            if (r + c) % 2 == 0:
                col = _shade(body, -25)
            else:
                col = _shade(body, -10)
            pygame.draw.rect(surf, col, (px, py, plate_w - 1, plate_h - 1))
            pygame.draw.line(surf, white, (px, py), (px + 1, py), 1)
            pygame.draw.line(surf, celadon, (px, py + plate_h - 2),
                             (px, py + plate_h - 2), 1)
    # Vermilion ribbon-knot at chest (less elaborate than General).
    pygame.draw.rect(surf, vermilion,
                     (cx - 1, torso_top + torso_h // 3, 3, 2))
    # Both arms come together at the right hip — gripping crossbow.
    arm_shadow = _shade(body, -30)
    grip_y = torso_top + (torso_h * 2) // 3
    # Right arm — extends to the right, hand at hip.
    pygame.draw.polygon(surf, arm_shadow, [
        (cx + torso_w // 2 - 1, torso_top + 4),
        (cx + torso_w // 2 + 4, torso_top + 7),
        (cx + torso_w // 2 + 6, grip_y),
        (cx + torso_w // 2 + 3, grip_y + 2),
        (cx + 3, grip_y),
    ])
    pygame.draw.polygon(surf, body, [
        (cx + torso_w // 2 - 1, torso_top + 5),
        (cx + torso_w // 2 + 3, torso_top + 7),
        (cx + torso_w // 2 + 5, grip_y - 1),
        (cx + 4, grip_y - 1),
    ])
    # Left arm — also reaches right, supporting the crossbow.
    pygame.draw.polygon(surf, arm_shadow, [
        (cx - torso_w // 2 + 1, torso_top + 5),
        (cx - torso_w // 2 - 2, torso_top + 9),
        (cx + 1, grip_y - 1),
        (cx + 4, grip_y + 1),
        (cx + 2, grip_y + 2),
        (cx - 2, grip_y),
    ])
    pygame.draw.polygon(surf, body, [
        (cx - torso_w // 2 + 1, torso_top + 6),
        (cx - torso_w // 2 - 1, torso_top + 9),
        (cx + 1, grip_y - 1),
        (cx + 3, grip_y),
    ])
    # Crossbow — thicker stroke (round 2) so the silhouette element
    # survives down to thumbnail. 2-px shaft + a wider stock + a
    # forward limb arm so the bow reads even at small render sizes.
    bow_left_x = cx + 1
    bow_right_x = cx + torso_w // 2 + 7
    bow_y = grip_y - 1
    pygame.draw.line(surf, crack,
                     (bow_left_x, bow_y),
                     (bow_right_x, bow_y), 2)
    pygame.draw.line(surf, _shade(crack, -10),
                     (bow_left_x, bow_y + 2),
                     (bow_right_x, bow_y + 2), 1)
    # Forward limb arms — thicker bow horns at the front end.
    pygame.draw.line(surf, crack,
                     (bow_right_x, bow_y - 2),
                     (bow_right_x, bow_y + 3), 2)
    # Bowstring — a thin celadon-toned line behind the bow.
    pygame.draw.line(surf, _shade(celadon, -25),
                     (bow_left_x, bow_y + 1),
                     (bow_right_x - 1, bow_y + 1), 1)
    # Stock pointing slightly back-right.
    pygame.draw.line(surf, crack,
                     (bow_right_x, bow_y),
                     (bow_right_x + 3, bow_y + 2), 2)
    y = torso_top

    # ── Head ────────────────────────────────────────────────────────────
    head_w = max(9, int(total * 0.13))
    head_rect = pygame.Rect(cx - head_w // 2 + 1, y - head_h, head_w, head_h)
    pygame.draw.ellipse(surf, shadow, head_rect)
    pygame.draw.ellipse(surf, body, head_rect.inflate(-2, -2))
    pygame.draw.line(surf, lit,
                     (head_rect.x + 2, head_rect.y + head_h // 3),
                     (head_rect.x + 2, head_rect.y + (head_h * 2) // 3), 1)
    # Eye + brow dot facing forward-left.
    pygame.draw.line(surf, crack,
                     (cx - 2, head_rect.y + head_h // 2 - 1),
                     (cx - 1, head_rect.y + head_h // 2 - 1), 1)
    y -= head_h

    # ── Topknot bun — pulled to the LEFT (rear) so it disagrees with
    # the standing archer's right-side bun.
    bun_x = cx - 2
    bun_w = max(5, int(total * 0.08))
    pygame.draw.ellipse(surf, shadow,
                        (bun_x - bun_w // 2, y - bun_h, bun_w, bun_h + 1))
    pygame.draw.ellipse(surf, body,
                        (bun_x - bun_w // 2 + 1, y - bun_h + 1,
                         bun_w - 2, bun_h - 1))


def _draw_kneeling(surf, top_rect, bot_rect, palette, seed):
    bcx = bot_rect.x + bot_rect.width // 2
    plinth_w = int(bot_rect.width * 1.22)
    plinth_h = 6

    if bot_rect.height > 80:
        _draw_clay_plinth(surf, bcx, bot_rect.bottom, plinth_w, palette,
                          h=plinth_h)
        figure_top = bot_rect.y + 4
        figure_base = bot_rect.bottom - plinth_h
        _draw_kneeling_figure(surf, bcx, figure_base, figure_top, palette)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 6, 14, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 6, seed=seed)

    # Kneeling pose is COMPACT, so the natural figure height is shorter
    # than the standing figures — the auto-stretch will reach a touch
    # taller in the top rect.
    natural_h = max(110, int(bot_rect.height * 0.85) - plinth_h - 4)

    def draw_into(tmp, tmp_cx, base_y, top_y):
        _draw_clay_plinth(tmp, tmp_cx, base_y, plinth_w, palette,
                          h=plinth_h)
        _draw_kneeling_figure(tmp, tmp_cx, base_y - plinth_h, top_y + 4,
                              palette)

    _mirror_top(surf, top_rect, natural_h, draw_into,
                mirror_strategy="flip")


def candidate_warrior_kneeling_archer(surf, top_rect, bot_rect, palette,
                                      seed):
    _cached_draw('warrior_kneeling', _draw_kneeling, surf, top_rect,
                 bot_rect, palette, seed)


# ── 4. Cavalry + Saddled Horse (骑兵俑 + 鞍马) ─────────────────────────────
#
# Two-figure composition: a saddled horse silhouette in the foreground
# with the rider standing beside the horse's neck (canonical pit-2
# presentation — riders stood by their horses since the horses can't
# share the firing line). Rider wears a short tunic + the unique
# cavalry rounded cap (NO topknot, NO heavy armour).
#
# References:
#   https://www.travelchinaguide.com/attraction/shaanxi/xian/terra_cotta_army/warrior-types.htm
#   https://en.wikipedia.org/wiki/Terracotta_Army

def _draw_horse_silhouette(surf, cx, base_y, top_y, palette):
    """Round 2: PARTIAL horse silhouette flanking the rider — head,
    arched neck, and the front of the saddle/withers. No legs, no
    barrel body, no tail. The crop reads as the head + neck of the
    horse the rider is dismounted next to, which mirrors cleanly as
    a paired top-bottom horse-head motif against the standard pillar
    width (no plinth overhang)."""
    total = base_y - top_y
    if total < 50:
        return
    body = _clay_body(palette)
    lit = _clay_lit(palette)
    shadow = _clay_shadow(palette)
    crack = _clay_crack(palette)
    vermilion = _pigment_vermilion(palette)
    ochre = _pigment_ochre(palette)

    # Vertical layout of the BUST — head sits about 60% up from the
    # base, neck arches down from the head into the saddle stub.
    saddle_y = base_y - max(20, int(total * 0.30))
    neck_h = max(14, int(total * 0.22))
    head_h = max(9, int(total * 0.14))

    # Bust anchored to the LEFT of the rider. Neck arches up-right
    # so the snout points toward the rider.
    hx = cx - 12

    # ── Saddle stub at the bottom of the bust — front pommel + a thin
    # withers band so the cropped horse reads as still "saddled".
    saddle_w = max(10, int(total * 0.18))
    saddle_rect = pygame.Rect(hx - saddle_w // 2, saddle_y - 2,
                              saddle_w, 4)
    pygame.draw.rect(surf, _shade(crack, 10), saddle_rect)
    pygame.draw.rect(surf, vermilion,
                     (saddle_rect.x + 1, saddle_rect.y + 1,
                      saddle_rect.w - 2, 2))
    pygame.draw.rect(surf, crack,
                     (saddle_rect.right - 2, saddle_y - 4, 2, 2))

    # ── Withers stub — short hump above the saddle, suggests the body
    # without drawing it.
    pygame.draw.ellipse(surf, shadow,
                        (hx - saddle_w // 2 - 1, saddle_y - 6,
                         saddle_w + 2, 8))
    pygame.draw.ellipse(surf, body,
                        (hx - saddle_w // 2, saddle_y - 5,
                         saddle_w, 6))

    # ── Arched neck rising from the withers, curving up-right toward
    # the rider. Two-segment trapezoid; lit on left flank.
    neck_top_x = hx + 4
    neck_top_y = saddle_y - neck_h
    neck_pts = [
        (hx - 3, saddle_y - 4),
        (hx + 5, saddle_y - 4),
        (neck_top_x + 3, neck_top_y + 2),
        (neck_top_x - 3, neck_top_y + 2),
    ]
    pygame.draw.polygon(surf, shadow, neck_pts)
    inner = [
        (hx - 2, saddle_y - 5),
        (hx + 4, saddle_y - 5),
        (neck_top_x + 2, neck_top_y + 3),
        (neck_top_x - 2, neck_top_y + 3),
    ]
    pygame.draw.polygon(surf, body, inner)
    pygame.draw.line(surf, lit,
                     (neck_top_x - 2, neck_top_y + 3),
                     (hx - 2, saddle_y - 5), 1)
    # Mane — chunky dashes down the back of the arched neck.
    for k in range(0, neck_h, 2):
        t = k / max(1, neck_h)
        mx = neck_top_x + 3 + int((hx + 5 - (neck_top_x + 3)) * t)
        my = neck_top_y + 2 + int(((saddle_y - 4) - (neck_top_y + 2)) * t)
        pygame.draw.line(surf, _shade(body, -45),
                         (mx, my), (mx + 1, my + 1), 1)

    # ── Head at the top of the arch — angled muzzle pointing up-right.
    head_rect = pygame.Rect(neck_top_x - head_h // 2,
                            neck_top_y - head_h + 2,
                            head_h + 2, head_h)
    pygame.draw.ellipse(surf, shadow, head_rect)
    pygame.draw.ellipse(surf, body, head_rect.inflate(-2, -2))
    # Snout — extends up-right past the head ellipse.
    snout_x = head_rect.right - 1
    snout_y = head_rect.y + head_h // 2 - 1
    pygame.draw.ellipse(surf, shadow,
                        (snout_x - 1, snout_y, 5, 4))
    pygame.draw.ellipse(surf, body,
                        (snout_x, snout_y + 1, 3, 2))
    # Eye dot.
    pygame.draw.line(surf, crack,
                     (head_rect.x + 3, head_rect.y + head_h // 2 - 1),
                     (head_rect.x + 3, head_rect.y + head_h // 2 - 1), 1)
    # Two ear stubs at the back of the head.
    pygame.draw.polygon(surf, shadow, [
        (head_rect.x + 1, head_rect.y + 1),
        (head_rect.x + 3, head_rect.y - 2),
        (head_rect.x + 4, head_rect.y + 2),
    ])
    pygame.draw.polygon(surf, body, [
        (head_rect.x + 2, head_rect.y),
        (head_rect.x + 3, head_rect.y - 1),
        (head_rect.x + 4, head_rect.y + 1),
    ])
    # Forelock — sweeping forward off the brow.
    pygame.draw.line(surf, _shade(body, -45),
                     (head_rect.x + 5, head_rect.y),
                     (head_rect.x + 7, head_rect.y + 2), 1)
    # Bridle strap — ochre, looping under the cheek.
    pygame.draw.line(surf, ochre,
                     (head_rect.x + 1, head_rect.y + head_h // 2),
                     (snout_x + 1, snout_y + 2), 1)
    pygame.draw.line(surf, ochre,
                     (head_rect.x + 4, head_rect.bottom - 1),
                     (head_rect.right - 1, head_rect.bottom - 1), 1)


def _draw_cavalry_rider(surf, cx, base_y, top_y, palette):
    """Standing cavalry rider beside the horse — short tunic, rounded
    cap, hands at sides. SHORTER than the General/Archer figures because
    a real cavalry figure was lighter than the heavy infantry."""
    total = base_y - top_y
    if total < 40:
        return
    body = _clay_body(palette)
    lit = _clay_lit(palette)
    shadow = _clay_shadow(palette)
    crack = _clay_crack(palette)
    ochre = _pigment_ochre(palette)
    vermilion = _pigment_vermilion(palette)
    white = _pigment_white(palette)

    # Round 3: torso bumped +6% (0.34 → 0.40) so legs settle around 35%
    # of total instead of 40%. AD round 2 flagged the rider reading
    # leggy next to the warrior set; this brings the cavalry proportion
    # into the same band as the infantry.
    cap_h = max(4, int(total * 0.10))
    head_h = max(7, int(total * 0.16))
    torso_h = max(14, int(total * 0.40))
    legs_h = total - cap_h - head_h - torso_h

    y = base_y

    # Legs in trousers — tucked into boots. Round 3: trouser width +1 px
    # (0.05 → 0.07 family) so the rider reads more grounded next to the
    # warrior set; AD round 2 noted it sat thin-legged.
    leg_w = max(5, int(total * 0.07))
    foot_w = max(6, int(total * 0.09))
    for side in (-1, 1):
        lx = cx + side * max(2, int(total * 0.035))
        pygame.draw.rect(surf, shadow,
                         (lx - leg_w // 2, y - legs_h, leg_w, legs_h))
        pygame.draw.rect(surf, body,
                         (lx - leg_w // 2 + 1, y - legs_h,
                          leg_w - 1, legs_h - 1))
        # Ochre calf-binding band partway up the trouser.
        pygame.draw.line(surf, ochre,
                         (lx - leg_w // 2, y - legs_h // 3),
                         (lx + leg_w // 2 - 1, y - legs_h // 3), 1)
        pygame.draw.rect(surf, _shade(body, -40),
                         (lx - foot_w // 2, y - 4, foot_w, 4))  # boot
    y -= legs_h

    # Torso — short tunic. NO scale-armour panel (cavalry was light).
    torso_w = max(8, int(total * 0.20))
    torso_top = y - torso_h
    pygame.draw.rect(surf, shadow,
                     (cx - torso_w // 2, torso_top, torso_w, torso_h))
    _horiz_gradient_rect(surf,
                         pygame.Rect(cx - torso_w // 2 + 1, torso_top + 1,
                                     torso_w - 2, torso_h - 2),
                         lit, body, shadow)
    # Belt with vermilion sash band.
    pygame.draw.rect(surf, vermilion,
                     (cx - torso_w // 2, y - 3, torso_w, 2))
    # Arms at sides — one hand lightly clutches reins (forward), the
    # other rests near the hip.
    arm_shadow = _shade(body, -25)
    # Left arm — forward, toward the horse head.
    pygame.draw.polygon(surf, arm_shadow, [
        (cx - torso_w // 2 + 1, torso_top + 2),
        (cx - torso_w // 2 - 4, torso_top + 5),
        (cx - torso_w // 2 - 5, torso_top + 9),
        (cx - 2, torso_top + 8),
    ])
    pygame.draw.polygon(surf, body, [
        (cx - torso_w // 2 + 1, torso_top + 3),
        (cx - torso_w // 2 - 3, torso_top + 5),
        (cx - torso_w // 2 - 4, torso_top + 8),
        (cx - 2, torso_top + 7),
    ])
    # Right arm — down at hip.
    pygame.draw.rect(surf, arm_shadow,
                     (cx + torso_w // 2 - 1, torso_top + 2, 3, torso_h - 4))
    pygame.draw.rect(surf, body,
                     (cx + torso_w // 2 - 1, torso_top + 3, 2, torso_h - 6))
    y = torso_top

    # Head.
    head_rect = pygame.Rect(cx - head_h // 2, y - head_h, head_h, head_h)
    pygame.draw.ellipse(surf, shadow, head_rect)
    pygame.draw.ellipse(surf, body, head_rect.inflate(-2, -2))
    pygame.draw.line(surf, lit,
                     (head_rect.x + 2, head_rect.y + head_h // 3),
                     (head_rect.x + 2, head_rect.y + (head_h * 2) // 3), 1)
    pygame.draw.line(surf, crack,
                     (cx - 2, head_rect.y + head_h // 2),
                     (cx - 1, head_rect.y + head_h // 2), 1)
    y -= head_h

    # Rounded cavalry cap (NO topknot, NO crown) — the distinguishing
    # cue. Chin strap drawn from the cap brim down past the cheek.
    cap_w = max(7, int(total * 0.16))
    cap_pts = [
        (cx - cap_w // 2, y),
        (cx + cap_w // 2, y),
        (cx + cap_w // 2 - 1, y - cap_h),
        (cx - cap_w // 2 + 1, y - cap_h),
    ]
    pygame.draw.polygon(surf, shadow, cap_pts)
    inner = [
        (cx - cap_w // 2 + 1, y - 1),
        (cx + cap_w // 2 - 1, y - 1),
        (cx + cap_w // 2 - 2, y - cap_h + 1),
        (cx - cap_w // 2 + 2, y - cap_h + 1),
    ]
    pygame.draw.polygon(surf, body, inner)
    # Cap rim — ochre.
    pygame.draw.line(surf, ochre,
                     (cx - cap_w // 2 + 1, y),
                     (cx + cap_w // 2 - 2, y), 1)
    # Chin strap — single vermilion line down the right cheek.
    pygame.draw.line(surf, vermilion,
                     (cx + cap_w // 2 - 2, y + 1),
                     (cx + cap_w // 2 - 3, y + head_h - 1), 1)


def _draw_cavalry(surf, top_rect, bot_rect, palette, seed):
    bcx = bot_rect.x + bot_rect.width // 2
    # Round 2: STANDARD pillar width — no plinth overhang. The cropped
    # horse bust + standing rider both fit inside the pillar grid.
    plinth_w = int(bot_rect.width * 1.18)
    plinth_h = 7

    if bot_rect.height > 80:
        _draw_clay_plinth(surf, bcx, bot_rect.bottom, plinth_w, palette,
                          h=plinth_h)
        figure_top = bot_rect.y + 4
        figure_base = bot_rect.bottom - plinth_h
        slot_h = figure_base - figure_top
        # Rider stands on the right of the partial-horse silhouette at
        # a SIZE matched to the other warriors (about 78% of the slot
        # height) so the cavalry figure stays in the same scale band.
        rider_top = figure_base - int(slot_h * 0.78)
        # Horse bust uses the same size — head + neck + saddle stub
        # rise to roughly the rider's shoulders.
        horse_top = figure_base - int(slot_h * 0.78)
        _draw_cavalry_rider(surf, bcx + 4, figure_base, rider_top,
                            palette)
        _draw_horse_silhouette(surf, bcx, figure_base, horse_top,
                               palette)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 6, 14, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 6, seed=seed)

    natural_h = max(120, int((bot_rect.height - plinth_h - 4) * 0.78))

    def draw_into(tmp, tmp_cx, base_y, top_y):
        _draw_clay_plinth(tmp, tmp_cx, base_y, plinth_w, palette,
                          h=plinth_h)
        b = base_y - plinth_h
        slot = b - top_y - 4
        rider_t = b - int(slot * 0.96)
        horse_t = b - int(slot * 0.96)
        _draw_cavalry_rider(tmp, tmp_cx + 4, b, rider_t, palette)
        _draw_horse_silhouette(tmp, tmp_cx, b, horse_t, palette)

    _mirror_top(surf, top_rect, natural_h, draw_into,
                mirror_strategy="flip")


def candidate_warrior_cavalry(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('warrior_cavalry', _draw_cavalry, surf, top_rect,
                 bot_rect, palette, seed)


# ── 5. Charioteer (御手俑) ──────────────────────────────────────────────────
#
# Tall + lean. Arms extended FORWARD-UP as if gripping reins, ceremonial
# long robe pulled tight at the waist, full neck-guard armour (covers
# arms to wrist). Sword at the left hip.
#
# References:
#   https://www.travelchinaguide.com/attraction/shaanxi/xian/terra_cotta_army/chariots.htm
#   https://en.wikipedia.org/wiki/Terracotta_Army

def _draw_charioteer_figure(surf, cx, base_y, top_y, palette):
    total = base_y - top_y
    if total < 60:
        return
    body = _clay_body(palette)
    lit = _clay_lit(palette)
    shadow = _clay_shadow(palette)
    crack = _clay_crack(palette)
    vermilion = _pigment_vermilion(palette)
    ochre = _pigment_ochre(palette)
    celadon = _pigment_celadon(palette)
    white = _pigment_white(palette)

    cap_h = max(6, int(total * 0.09))
    head_h = max(10, int(total * 0.14))
    neck_h = max(3, int(total * 0.04))
    torso_h = max(20, int(total * 0.30))
    skirt_h = max(16, int(total * 0.27))
    feet_h = total - cap_h - head_h - neck_h - torso_h - skirt_h

    y = base_y

    # Feet — narrow square-toe planted in a slight stance, suggesting
    # the charioteer braced inside a moving chariot. Round 2: feet sit
    # SLIGHTLY apart so the silhouette reads "driving stance".
    foot_w = max(10, int(total * 0.15))
    pygame.draw.rect(surf, shadow,
                     (cx - foot_w // 2 - 1, y - feet_h, foot_w + 2, feet_h))
    pygame.draw.rect(surf, body,
                     (cx - foot_w // 2, y - feet_h + 1,
                      foot_w, feet_h - 2))
    pygame.draw.line(surf, crack,
                     (cx, y - feet_h + 1), (cx, y - 1), 1)
    # Bent-knee cue — a small dark notch at mid-shin signalling the
    # driver's knees-bent stance.
    pygame.draw.line(surf, crack,
                     (cx - foot_w // 2, y - feet_h // 2),
                     (cx + foot_w // 2, y - feet_h // 2), 1)
    y -= feet_h

    # Skirt — long ceremonial, WIDER bottom hem because round 2 leans
    # the charioteer slightly forward at the waist (suggested seated-
    # driving stance), so the skirt flares as it pools toward the
    # plinth. Diagonal silhouette ≠ General's vertical silhouette.
    skirt_top_w = max(12, int(total * 0.17))
    skirt_bot_w = max(skirt_top_w + 4, int(total * 0.27))
    # Forward lean — top of skirt shifts FORWARD-LEFT vs bottom so the
    # whole torso pitches into the driving direction.
    lean_x = 2
    skirt_pts = [
        (cx - skirt_bot_w // 2, y),
        (cx + skirt_bot_w // 2, y),
        (cx + skirt_top_w // 2 - lean_x, y - skirt_h),
        (cx - skirt_top_w // 2 - lean_x, y - skirt_h),
    ]
    pygame.draw.polygon(surf, shadow, skirt_pts)
    inner = [
        (cx - skirt_bot_w // 2 + 1, y - 1),
        (cx + skirt_bot_w // 2 - 1, y - 1),
        (cx + skirt_top_w // 2 - lean_x - 1, y - skirt_h + 1),
        (cx - skirt_top_w // 2 - lean_x + 1, y - skirt_h + 1),
    ]
    pygame.draw.polygon(surf, body, inner)
    pygame.draw.line(surf, lit,
                     (cx - skirt_top_w // 2 - lean_x + 1, y - skirt_h + 2),
                     (cx - skirt_bot_w // 2 + 1, y - 1), 1)
    # Robe creases — 4 lines for the tighter cinch.
    for k in range(-2, 3):
        if k == 0:
            continue
        fx = cx + k * (skirt_top_w // 6)
        pygame.draw.line(surf, _shade(body, -25),
                         (fx, y - skirt_h + 2), (fx, y - 2), 1)
    # Sword scabbard at left hip — dark hilt + scabbard tracing down
    # the left flank of the skirt.
    pygame.draw.rect(surf, crack,
                     (cx - skirt_top_w // 2 - 1, y - skirt_h - 2, 3, 4))
    pygame.draw.line(surf, ochre,
                     (cx - skirt_top_w // 2, y - skirt_h - 1),
                     (cx - skirt_top_w // 2 + 1, y - skirt_h - 1), 1)
    pygame.draw.line(surf, _shade(crack, 15),
                     (cx - skirt_top_w // 2 + 1, y - skirt_h - 2),
                     (cx - skirt_top_w // 2 + 2, y - skirt_h + skirt_h // 2), 2)
    y -= skirt_h

    # Torso — narrow + tall, full neck-armour wraps to wrists.
    torso_w = max(11, int(total * 0.18))
    torso_top = y - torso_h
    pygame.draw.rect(surf, shadow,
                     (cx - torso_w // 2, torso_top, torso_w, torso_h))
    _vert_gradient_rect(surf,
                        pygame.Rect(cx - torso_w // 2 + 1, torso_top + 1,
                                    torso_w - 2, torso_h - 2),
                        lit, body, shadow)
    # Wide neck-guard collar — a high-set band of armour around the
    # base of the neck.
    pygame.draw.rect(surf, _shade(body, -20),
                     (cx - torso_w // 2 - 2, torso_top, torso_w + 4, 3))
    pygame.draw.line(surf, ochre,
                     (cx - torso_w // 2 - 2, torso_top),
                     (cx + torso_w // 2 + 1, torso_top), 1)
    # Plates — dense vertical strips, not horizontal scales (charioteer
    # plate-mail orientation).
    plate_top = torso_top + 4
    plate_h = torso_h - 6
    for k in range(-2, 3):
        px = cx + k * 3
        pygame.draw.line(surf, _shade(body, -25),
                         (px, plate_top), (px, plate_top + plate_h), 1)
        pygame.draw.line(surf, white,
                         (px - 1, plate_top), (px - 1, plate_top + 1), 1)
    # Vermilion belt at waist.
    pygame.draw.rect(surf, vermilion,
                     (cx - torso_w // 2, y - 3, torso_w, 2))
    # Arms reaching UP-FORWARD — the canonical reins-gripping pose.
    arm_shadow = _shade(body, -25)
    # Left arm — reaches up-forward (forward-left).
    pygame.draw.polygon(surf, arm_shadow, [
        (cx - torso_w // 2 + 1, torso_top + 3),
        (cx - torso_w // 2 - 7, torso_top - 2),
        (cx - torso_w // 2 - 11, torso_top + 4),
        (cx - torso_w // 2 - 5, torso_top + 8),
        (cx - 2, torso_top + 9),
    ])
    pygame.draw.polygon(surf, body, [
        (cx - torso_w // 2 + 1, torso_top + 4),
        (cx - torso_w // 2 - 6, torso_top - 1),
        (cx - torso_w // 2 - 9, torso_top + 4),
        (cx - 2, torso_top + 8),
    ])
    # Right arm — also forward-up but slightly lower.
    pygame.draw.polygon(surf, arm_shadow, [
        (cx + torso_w // 2 - 1, torso_top + 4),
        (cx + torso_w // 2 + 4, torso_top),
        (cx + torso_w // 2 + 8, torso_top + 5),
        (cx + torso_w // 2 + 3, torso_top + 11),
        (cx + 1, torso_top + 10),
    ])
    pygame.draw.polygon(surf, body, [
        (cx + torso_w // 2 - 1, torso_top + 5),
        (cx + torso_w // 2 + 4, torso_top + 1),
        (cx + torso_w // 2 + 7, torso_top + 5),
        (cx + 1, torso_top + 9),
    ])
    # Reins — round 2 fix: extend FORWARD over the plinth front edge.
    # Pair of 2-px leather reins descending from the front fist down
    # past the plinth top, terminating beyond the body. Survives
    # thumbnail render.
    rein_origin_x = cx - torso_w // 2 - 11
    rein_origin_y = torso_top + 4
    rein_end_x = cx - torso_w // 2 - 22
    rein_end_y = base_y - feet_h - 2
    for k in (0, 3):
        pygame.draw.line(surf, crack,
                         (rein_origin_x, rein_origin_y + k),
                         (rein_end_x, rein_end_y + k), 2)
        pygame.draw.line(surf, _shade(crack, 30),
                         (rein_origin_x + 1, rein_origin_y + k),
                         (rein_end_x + 1, rein_end_y + k), 1)
    y = torso_top

    # Neck.
    pygame.draw.rect(surf, shadow,
                     (cx - 2, y - neck_h, 4, neck_h))
    pygame.draw.rect(surf, body,
                     (cx - 1, y - neck_h, 3, neck_h))
    y -= neck_h

    # Head.
    head_w = max(9, int(total * 0.13))
    head_rect = pygame.Rect(cx - head_w // 2, y - head_h, head_w, head_h)
    pygame.draw.ellipse(surf, shadow, head_rect)
    pygame.draw.ellipse(surf, body, head_rect.inflate(-2, -2))
    pygame.draw.line(surf, lit,
                     (head_rect.x + 2, head_rect.y + head_h // 3),
                     (head_rect.x + 2, head_rect.y + (head_h * 2) // 3), 1)
    pygame.draw.line(surf, crack,
                     (cx - 2, head_rect.y + head_h // 2),
                     (cx - 1, head_rect.y + head_h // 2), 1)
    y -= head_h

    # Long charioteer cap — tall trapezoidal headgear, distinct from
    # both bun + crown. Two ochre bands across the height.
    cap_w = max(8, int(total * 0.13))
    cap_pts = [
        (cx - cap_w // 2, y),
        (cx + cap_w // 2, y),
        (cx + cap_w // 2 - 2, y - cap_h),
        (cx - cap_w // 2 + 2, y - cap_h),
    ]
    pygame.draw.polygon(surf, shadow, cap_pts)
    inner_pts = [
        (cx - cap_w // 2 + 1, y - 1),
        (cx + cap_w // 2 - 1, y - 1),
        (cx + cap_w // 2 - 3, y - cap_h + 1),
        (cx - cap_w // 2 + 3, y - cap_h + 1),
    ]
    pygame.draw.polygon(surf, body, inner_pts)
    for k in range(2):
        py = y - 2 - k * 2
        pygame.draw.line(surf, ochre,
                         (cx - cap_w // 2 + 2, py),
                         (cx + cap_w // 2 - 3, py), 1)


def _draw_chariot_pole(surf, cx, base_y, plinth_w, palette):
    """Round 2: chariot pole + draft yoke stub protruding FORWARD
    (leftward) from the plinth front edge. Lengthens the silhouette
    horizontally and gives the charioteer a unique footprint vs the
    General's vertical-polearm motif."""
    pole_y = base_y - 3
    pole_start_x = cx - plinth_w // 2
    pole_end_x = pole_start_x - max(8, plinth_w // 4)
    # Wood pole — thick walnut shaft.
    pygame.draw.line(surf, _clay_crack(palette),
                     (pole_start_x, pole_y),
                     (pole_end_x, pole_y - 2), 3)
    pygame.draw.line(surf, _shade(_clay_body(palette), -10),
                     (pole_start_x, pole_y + 1),
                     (pole_end_x, pole_y - 1), 1)
    # Bronze yoke ferrule at the far end — short cross-piece.
    pygame.draw.line(surf, _bronze_dark(palette),
                     (pole_end_x - 1, pole_y - 4),
                     (pole_end_x - 1, pole_y + 2), 2)
    pygame.draw.line(surf, _bronze_lit(palette),
                     (pole_end_x, pole_y - 3),
                     (pole_end_x, pole_y + 1), 1)


def _draw_charioteer(surf, top_rect, bot_rect, palette, seed):
    bcx = bot_rect.x + bot_rect.width // 2
    plinth_w = int(bot_rect.width * 1.14)
    plinth_h = 7

    if bot_rect.height > 80:
        _draw_clay_plinth(surf, bcx, bot_rect.bottom, plinth_w, palette,
                          h=plinth_h)
        # Chariot pole stub BEFORE the figure so the reins descend
        # past it.
        _draw_chariot_pole(surf, bcx, bot_rect.bottom - plinth_h,
                           plinth_w, palette)
        figure_top = bot_rect.y + 4
        figure_base = bot_rect.bottom - plinth_h
        _draw_charioteer_figure(surf, bcx, figure_base, figure_top,
                                palette)
        # Pair of bronze chariot bell ornaments at the plinth — implies
        # the chariot the figure stands in.
        for side in (-1, 1):
            bx = bcx + side * (plinth_w // 2 + 2)
            pygame.draw.circle(surf, _bronze_dark(palette),
                               (bx, bot_rect.bottom - 4), 2)
            pygame.draw.circle(surf, _bronze_lit(palette),
                               (bx, bot_rect.bottom - 5), 1)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 6, 14, palette, seed=seed)

    natural_h = max(120, bot_rect.height - plinth_h - 4)

    def draw_into(tmp, tmp_cx, base_y, top_y):
        _draw_clay_plinth(tmp, tmp_cx, base_y, plinth_w, palette,
                          h=plinth_h)
        _draw_chariot_pole(tmp, tmp_cx, base_y - plinth_h, plinth_w,
                           palette)
        _draw_charioteer_figure(tmp, tmp_cx, base_y - plinth_h,
                                top_y + 4, palette)

    _mirror_top(surf, top_rect, natural_h, draw_into,
                mirror_strategy="flip")


def candidate_warrior_charioteer(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('warrior_charioteer', _draw_charioteer, surf, top_rect,
                 bot_rect, palette, seed)


# ── 6. Leshan Giant Buddha (乐山大佛) ─────────────────────────────────────
#
# Seated cliff Buddha carved into Cretaceous red sandstone. Frontal
# symmetry, hands resting on knees (dhyana / earth-touching), head
# proportionally HUGE (the real statue has a 15 m head on a 71 m body).
# Sits inside a cliff niche.
#
# Reference: https://en.wikipedia.org/wiki/Leshan_Giant_Buddha

def _draw_leshan_figure(surf, cx, base_y, top_y, palette):
    total = base_y - top_y
    if total < 60:
        return
    body = _sandstone_warm(palette)
    lit = _sandstone_lit(palette)
    shadow = _sandstone_shadow(palette)
    dark = _shade(shadow, -25)
    saffron = _saffron_robe(palette)
    bronze = _bronze_body(palette)

    # Cliff niche FIRST so the Buddha sits IN the recess. Round 2:
    # niche is SLIMMER (so the figure fills ~85% of it) and the cliff
    # wall around it carries the structural strata.
    niche_w = max(34, int(total * 0.48))
    niche_h = max(80, int(total * 0.92))
    _draw_cliff_niche(surf, cx, base_y, niche_w, niche_h, palette,
                      outer_inflate_x=18, outer_inflate_y=14)

    # Round 2: figure proportions bumped so the seated Buddha fills
    # ~85% of the niche width (head 0.30, torso 0.40, knees 0.26).
    head_h = max(16, int(total * 0.26))
    torso_h = max(22, int(total * 0.36))
    knees_h = max(15, int(total * 0.24))
    lotus_h = total - head_h - torso_h - knees_h

    y = base_y

    # Lotus base — fills the bottom of the niche.
    _draw_lotus_plinth(surf, cx, y, max(30, int(total * 0.44)), palette,
                       h=lotus_h)
    y -= lotus_h

    # Knees — bigger humps fill almost the niche width.
    knee_w = max(10, int(total * 0.18))
    for side in (-1, 1):
        kx = cx + side * (knee_w // 2 + 1)
        knee_rect = pygame.Rect(kx - knee_w // 2, y - knees_h,
                                knee_w, knees_h + 3)
        pygame.draw.ellipse(surf, shadow, knee_rect)
        pygame.draw.ellipse(surf, body, knee_rect.inflate(-2, -2))
        # Lit side highlight.
        pygame.draw.arc(surf, lit, knee_rect.inflate(-3, -3),
                        math.pi * 0.7, math.pi * 1.0, 1)
        # Hand resting flat ON the knee — small dark oval.
        pygame.draw.ellipse(surf, dark,
                            (kx - 6, y - knees_h + 2, 12, 4))
        pygame.draw.ellipse(surf, body,
                            (kx - 5, y - knees_h + 2, 10, 3))
        pygame.draw.line(surf, lit,
                         (kx - 5, y - knees_h + 2),
                         (kx + 4, y - knees_h + 2), 1)
    y -= knees_h

    # Torso — barrel-like, BROADER than round 1 so the figure better
    # fills the niche width.
    torso_top = y - torso_h
    torso_w = max(22, int(total * 0.38))
    upper_w = max(18, int(total * 0.32))
    torso_pts = [
        (cx - torso_w // 2, y),
        (cx + torso_w // 2, y),
        (cx + upper_w // 2, torso_top),
        (cx - upper_w // 2, torso_top),
    ]
    pygame.draw.polygon(surf, shadow, torso_pts)
    inner = [
        (cx - torso_w // 2 + 1, y - 1),
        (cx + torso_w // 2 - 1, y - 1),
        (cx + upper_w // 2 - 1, torso_top + 1),
        (cx - upper_w // 2 + 1, torso_top + 1),
    ]
    pygame.draw.polygon(surf, body, inner)
    # Vertical robe folds — 3 thick lines down the centre.
    for k in (-1, 0, 1):
        fx = cx + k * 4
        pygame.draw.line(surf, _shade(body, -25),
                         (fx, torso_top + 2),
                         (fx, y - 2), 1)
    # Saffron robe band across the chest.
    pygame.draw.line(surf, saffron,
                     (cx - upper_w // 2 + 2, torso_top + 5),
                     (cx + upper_w // 2 - 2, torso_top + 5), 1)
    # Right shoulder bare — diagonal band cuts across.
    pygame.draw.line(surf, _shade(body, -25),
                     (cx - upper_w // 2 + 1, torso_top + 2),
                     (cx + upper_w // 2 - 1, torso_top + 7), 1)
    y = torso_top

    # Massive head — the Leshan signature is the OVERSIZED head sitting
    # almost directly on the shoulders. Round 2: bigger so the figure
    # fills ~85% of the niche.
    head_w = max(18, int(total * 0.30))
    head_rect = pygame.Rect(cx - head_w // 2, y - head_h, head_w,
                             head_h + 2)
    pygame.draw.ellipse(surf, shadow, head_rect)
    pygame.draw.ellipse(surf, body, head_rect.inflate(-2, -2))
    # Ushnisha — the crown topknot. Drawn as a small dome on top of the
    # head, distinguishing this from a topknot.
    ush_w = max(6, int(total * 0.10))
    ush_rect = pygame.Rect(cx - ush_w // 2, y - head_h - ush_w // 2,
                            ush_w, ush_w + 2)
    pygame.draw.ellipse(surf, shadow, ush_rect)
    pygame.draw.ellipse(surf, body, ush_rect.inflate(-2, -2))
    # Snail-shell curls dotting the head — the canonical Buddha hair
    # texture. 1-px dots in a grid.
    for r in range(2):
        for c in range(-3, 4):
            dx = cx + c * 3
            dy = y - head_h + 3 + r * 3
            pygame.draw.line(surf, _shade(body, -30),
                             (dx, dy), (dx, dy), 1)
    # Long pendulous ears — wide-set dark blocks on each side.
    for side in (-1, 1):
        ex = cx + side * (head_w // 2 - 1)
        pygame.draw.rect(surf, _shade(body, -25),
                         (ex - 1 if side < 0 else ex,
                          y - (head_h * 3) // 4, 3, head_h // 2))
        pygame.draw.line(surf, lit,
                         (ex - 1 if side < 0 else ex + 2,
                          y - (head_h * 3) // 4),
                         (ex - 1 if side < 0 else ex + 2,
                          y - head_h // 3), 1)
    # Closed eyes — 2 dark slits.
    for side in (-1, 1):
        eye_x = cx + side * (head_w // 5)
        eye_y = y - (head_h * 2) // 3
        pygame.draw.line(surf, dark,
                         (eye_x - 1, eye_y), (eye_x + 1, eye_y), 1)
    # Urna — third-eye dot on the brow.
    pygame.draw.line(surf, bronze,
                     (cx, y - (head_h * 2) // 3 - 2),
                     (cx, y - (head_h * 2) // 3 - 2), 1)
    # Serene smile — a barely-curve mouth line.
    pygame.draw.line(surf, dark,
                     (cx - 2, y - head_h // 3),
                     (cx + 2, y - head_h // 3), 1)


def _draw_leshan(surf, top_rect, bot_rect, palette, seed):
    bcx = bot_rect.x + bot_rect.width // 2

    if bot_rect.height > 80:
        figure_top = bot_rect.y + 4
        figure_base = bot_rect.bottom - 2
        _draw_leshan_figure(surf, bcx, figure_base, figure_top, palette)
        # Light grass bed — Leshan sits above the river, faint riverbed
        # texture instead of dense grass.
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 4, 8, palette, seed=seed)

    natural_h = max(120, bot_rect.height - 8)

    def draw_into(tmp, tmp_cx, base_y, top_y):
        _draw_leshan_figure(tmp, tmp_cx, base_y - 2, top_y + 4, palette)

    _mirror_top(surf, top_rect, natural_h, draw_into,
                mirror_strategy="flip")


def candidate_buddha_leshan(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('buddha_leshan', _draw_leshan, surf, top_rect, bot_rect,
                 palette, seed)


# ── 7. Tian Tan Buddha (天坛大佛) ───────────────────────────────────────────
#
# Modern monumental bronze (Hong Kong, 1993). Seated Sakyamuni on a
# three-tier lotus throne, right hand raised in abhaya mudra (palm out,
# fingers up — "fearlessness"), left hand in varada (palm up on knee).
# Bronze body with golden-amber rim highlights + a circular halo.
#
# Reference: https://en.wikipedia.org/wiki/Tian_Tan_Buddha

def _draw_tian_tan_figure(surf, cx, base_y, top_y, palette):
    total = base_y - top_y
    if total < 60:
        return
    # Round 2: verdigris bronze (clearly greener than the warrior clay
    # + the gilt Maitreya), so the three bronze-family Buddhas read as
    # distinct materials at noon → night.
    body = _tian_tan_body(palette)
    lit = _tian_tan_lit(palette)
    shadow = _tian_tan_dark(palette)
    dark = _shade(shadow, -20)
    rim = _gilt_bright(palette)

    head_h = max(14, int(total * 0.20))
    torso_h = max(22, int(total * 0.32))
    knees_h = max(14, int(total * 0.22))
    lotus_h = total - head_h - torso_h - knees_h

    y = base_y

    # 3-tier altar platform — circular terraces (Temple of Heaven echo),
    # in matching verdigris bronze.
    tier_total = max(8, lotus_h - 4)
    tier_h = max(2, tier_total // 3)
    for i in range(3):
        ty = base_y - i * tier_h
        tw = max(20, int(total * (0.50 - i * 0.06)))
        pygame.draw.ellipse(surf, dark,
                            (cx - tw // 2, ty - tier_h, tw, tier_h + 2))
        pygame.draw.ellipse(surf, shadow,
                            (cx - tw // 2 + 1, ty - tier_h + 1,
                             tw - 2, tier_h))
        pygame.draw.ellipse(surf, lit,
                            (cx - tw // 2 + 2, ty - tier_h + 1,
                             tw - 4, 1))
    # Top lotus petal ring directly under the seated Buddha.
    _draw_lotus_plinth(surf, cx, base_y - tier_total, max(22, int(total * 0.38)),
                       palette, h=4, n_petals=7)
    y -= lotus_h

    # Crossed legs (lotus position) — single rounded trapezoid wider
    # than the torso, with a centre fold line.
    leg_w = max(20, int(total * 0.36))
    leg_top_w = max(14, int(total * 0.24))
    leg_top = y - knees_h
    leg_pts = [
        (cx - leg_w // 2, y),
        (cx + leg_w // 2, y),
        (cx + leg_top_w // 2, leg_top),
        (cx - leg_top_w // 2, leg_top),
    ]
    pygame.draw.polygon(surf, shadow, leg_pts)
    inner = [
        (cx - leg_w // 2 + 1, y - 1),
        (cx + leg_w // 2 - 1, y - 1),
        (cx + leg_top_w // 2 - 1, leg_top + 1),
        (cx - leg_top_w // 2 + 1, leg_top + 1),
    ]
    pygame.draw.polygon(surf, body, inner)
    pygame.draw.line(surf, lit,
                     (cx - leg_top_w // 2 + 1, leg_top + 1),
                     (cx - leg_w // 2 + 1, y - 1), 1)
    # Centre robe fold V on the lap.
    pygame.draw.polygon(surf, _shade(body, -25),
                        [(cx, leg_top + 1), (cx - 3, y - 1),
                         (cx + 3, y - 1)])
    # Left hand resting palm-up on left knee (varada mudra).
    pygame.draw.ellipse(surf, dark,
                        (cx - leg_w // 2 + 2, leg_top - 1,
                         8, 4))
    pygame.draw.ellipse(surf, lit,
                        (cx - leg_w // 2 + 3, leg_top - 1,
                         6, 2))
    y = leg_top

    # Torso — narrower than the lap, vertical body with a thin
    # bronze sheen.
    torso_top = y - torso_h
    torso_w = max(12, int(total * 0.22))
    upper_w = max(11, int(total * 0.20))
    torso_pts = [
        (cx - torso_w // 2, y),
        (cx + torso_w // 2, y),
        (cx + upper_w // 2, torso_top),
        (cx - upper_w // 2, torso_top),
    ]
    pygame.draw.polygon(surf, shadow, torso_pts)
    inner = [
        (cx - torso_w // 2 + 1, y - 1),
        (cx + torso_w // 2 - 1, y - 1),
        (cx + upper_w // 2 - 1, torso_top + 1),
        (cx - upper_w // 2 + 1, torso_top + 1),
    ]
    pygame.draw.polygon(surf, body, inner)
    pygame.draw.line(surf, lit,
                     (cx - upper_w // 2 + 1, torso_top + 1),
                     (cx - torso_w // 2 + 1, y - 1), 1)
    # Robe folds — diagonal lines across the chest.
    for k in range(3):
        py = torso_top + 3 + k * 4
        pygame.draw.line(surf, _shade(body, -25),
                         (cx - upper_w // 2 + 2, py),
                         (cx + upper_w // 2 - 2, py + 2), 1)
    # Right hand raised in abhaya mudra — at the right side, palm
    # forward, fingers up. Tall narrow rect with a fingertip dot.
    arm_shadow = _shade(body, -25)
    # Arm sweeping up.
    pygame.draw.polygon(surf, arm_shadow, [
        (cx + upper_w // 2, torso_top + 4),
        (cx + upper_w // 2 + 4, torso_top - 2),
        (cx + upper_w // 2 + 7, torso_top + 4),
        (cx + upper_w // 2 + 5, torso_top + 12),
        (cx + 2, torso_top + 12),
    ])
    pygame.draw.polygon(surf, body, [
        (cx + upper_w // 2, torso_top + 5),
        (cx + upper_w // 2 + 3, torso_top - 1),
        (cx + upper_w // 2 + 6, torso_top + 5),
        (cx + 2, torso_top + 11),
    ])
    # Palm — abhaya mudra reads at silhouette level. Round 3: paint the
    # palm in the body mid-tone (NOT the lit highlight) so it no longer
    # punches as a glowing handprint mid-torso; a single 1-px lit rim
    # along the palm's outer edge preserves the gesture cue.
    pygame.draw.rect(surf, shadow,
                     (cx + upper_w // 2 + 3, torso_top - 4, 4, 4))
    pygame.draw.rect(surf, body,
                     (cx + upper_w // 2 + 4, torso_top - 3, 2, 3))
    # Outer-rim 1-px highlight — keeps the gesture readable without the
    # round-2 floating-bright-palm artefact.
    pygame.draw.line(surf, lit,
                     (cx + upper_w // 2 + 6, torso_top - 4),
                     (cx + upper_w // 2 + 6, torso_top - 1), 1)
    # Finger lines.
    for fx in (cx + upper_w // 2 + 3, cx + upper_w // 2 + 5,
               cx + upper_w // 2 + 6):
        pygame.draw.line(surf, dark,
                         (fx, torso_top - 4), (fx, torso_top - 2), 1)
    # Left arm — wraps to the lap.
    pygame.draw.polygon(surf, arm_shadow, [
        (cx - upper_w // 2 + 1, torso_top + 4),
        (cx - upper_w // 2 - 3, torso_top + 8),
        (cx - upper_w // 2 - 1, torso_top + 14),
        (cx - 2, torso_top + 12),
    ])
    pygame.draw.polygon(surf, body, [
        (cx - upper_w // 2 + 1, torso_top + 5),
        (cx - upper_w // 2 - 2, torso_top + 8),
        (cx - upper_w // 2, torso_top + 13),
        (cx - 2, torso_top + 11),
    ])
    y = torso_top

    # Halo BEHIND the head — additive amber, night-hot.
    head_w = max(11, int(total * 0.20))
    head_y_centre = y - head_h // 2
    _draw_lit_halo(surf, cx, head_y_centre, max(10, int(total * 0.20)),
                   palette)

    # Head — round, serene, with ushnisha top + long ears + closed eyes.
    head_rect = pygame.Rect(cx - head_w // 2, y - head_h, head_w, head_h)
    pygame.draw.ellipse(surf, shadow, head_rect)
    pygame.draw.ellipse(surf, body, head_rect.inflate(-2, -2))
    pygame.draw.line(surf, lit,
                     (head_rect.x + 2, head_rect.y + head_h // 3),
                     (head_rect.x + 2, head_rect.y + (head_h * 2) // 3), 1)
    # Ushnisha topknot — small dome.
    ush_w = max(4, head_w // 3)
    ush_rect = pygame.Rect(cx - ush_w // 2, y - head_h - ush_w // 2 + 1,
                            ush_w, ush_w + 1)
    pygame.draw.ellipse(surf, shadow, ush_rect)
    pygame.draw.ellipse(surf, body, ush_rect.inflate(-2, -2))
    # Snail-curl hair dots.
    for c in range(-2, 3):
        dy = y - head_h + 2
        dx = cx + c * 2
        pygame.draw.line(surf, _shade(body, -30), (dx, dy), (dx, dy), 1)
    # Long ears.
    for side in (-1, 1):
        ex = cx + side * (head_w // 2 - 1)
        pygame.draw.rect(surf, _shade(body, -20),
                         (ex - 1 if side < 0 else ex,
                          y - (head_h * 2) // 3, 2, (head_h * 2) // 3))
    # Closed eyes.
    for side in (-1, 1):
        eye_x = cx + side * (head_w // 5)
        eye_y = y - (head_h * 2) // 3 + 2
        pygame.draw.line(surf, dark,
                         (eye_x - 1, eye_y), (eye_x + 1, eye_y), 1)
    # Urna.
    pygame.draw.line(surf, rim,
                     (cx, y - (head_h * 2) // 3),
                     (cx, y - (head_h * 2) // 3), 1)
    # Smile.
    pygame.draw.line(surf, dark,
                     (cx - 1, y - head_h // 4),
                     (cx + 1, y - head_h // 4), 1)


def _draw_tian_tan(surf, top_rect, bot_rect, palette, seed):
    bcx = bot_rect.x + bot_rect.width // 2

    if bot_rect.height > 80:
        figure_top = bot_rect.y + 4
        figure_base = bot_rect.bottom - 2
        _draw_tian_tan_figure(surf, bcx, figure_base, figure_top, palette)

    natural_h = max(120, bot_rect.height - 8)

    def draw_into(tmp, tmp_cx, base_y, top_y):
        _draw_tian_tan_figure(tmp, tmp_cx, base_y - 2, top_y + 4, palette)

    _mirror_top(surf, top_rect, natural_h, draw_into,
                mirror_strategy="flip")


def candidate_buddha_tian_tan(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('buddha_tian_tan', _draw_tian_tan, surf, top_rect,
                 bot_rect, palette, seed)


# ── 8. Standing Maitreya / Budai (彌勒菩薩, gilt-bronze) ──────────────────
#
# Standing Laughing Buddha: round belly exposed, big grin, cloth bag
# slung over one shoulder, arms spread in welcome. Gilt-bronze finish
# so it reads warmer than Tian Tan's patina.
#
# Reference: https://en.wikipedia.org/wiki/Budai

def _draw_maitreya_figure(surf, cx, base_y, top_y, palette):
    total = base_y - top_y
    if total < 60:
        return
    body = _gilt_bronze(palette)
    lit = _gilt_bright(palette)
    # Round 2: use the dedicated gilt shadow rather than generic bronze
    # so the silhouette stays warmer than Tian Tan's verdigris.
    shadow = _gilt_shadow(palette)
    dark = _shade(shadow, -20)
    saffron = _saffron_robe(palette)

    # Round 3: plinth budget shaved from ~0.22 → 0.15 of total (−30%);
    # the freed budget rolls into the skirt so the figure occupies more
    # of the slot. AD round 2 flagged the plinth as overbearing.
    head_h = max(13, int(total * 0.20))
    neck_h = max(2, int(total * 0.03))
    torso_h = max(20, int(total * 0.30))
    skirt_h = max(20, int(total * 0.32))
    base_plinth_h = total - head_h - neck_h - torso_h - skirt_h

    y = base_y

    # Octagonal stone base — Maitreya statues sit on a low platform.
    plinth_w = max(20, int(total * 0.40))
    pygame.draw.rect(surf, _plinth_dark(palette),
                     (cx - plinth_w // 2, y - base_plinth_h,
                      plinth_w, base_plinth_h))
    pygame.draw.rect(surf, _shade(_plinth_dark(palette), 25),
                     (cx - plinth_w // 2 + 1,
                      y - base_plinth_h, plinth_w - 2, 1))
    # Bare feet poking forward at the base.
    for side in (-1, 1):
        fx = cx + side * 4
        pygame.draw.ellipse(surf, _shade(body, -25),
                            (fx - 3, y - base_plinth_h - 2, 6, 4))
        pygame.draw.ellipse(surf, body,
                            (fx - 2, y - base_plinth_h - 1, 4, 2))
    y -= base_plinth_h

    # Skirt — flowing robe pooling around the feet, wide hem.
    skirt_bot_w = max(22, int(total * 0.38))
    skirt_top_w = max(14, int(total * 0.24))
    skirt_pts = [
        (cx - skirt_bot_w // 2, y),
        (cx + skirt_bot_w // 2, y),
        (cx + skirt_top_w // 2, y - skirt_h),
        (cx - skirt_top_w // 2, y - skirt_h),
    ]
    pygame.draw.polygon(surf, shadow, skirt_pts)
    inner = [
        (cx - skirt_bot_w // 2 + 1, y - 1),
        (cx + skirt_bot_w // 2 - 1, y - 1),
        (cx + skirt_top_w // 2 - 1, y - skirt_h + 1),
        (cx - skirt_top_w // 2 + 1, y - skirt_h + 1),
    ]
    pygame.draw.polygon(surf, body, inner)
    # Flowing fold creases — curving outward at the hem.
    for k in range(-2, 3):
        fx_top = cx + k * (skirt_top_w // 6)
        fx_bot = cx + k * (skirt_bot_w // 5)
        pygame.draw.line(surf, _shade(body, -25),
                         (fx_top, y - skirt_h + 2), (fx_bot, y - 2), 1)
    # Saffron sash hanging from the waist.
    pygame.draw.rect(surf, saffron,
                     (cx - skirt_top_w // 2, y - skirt_h - 1,
                      skirt_top_w, 2))
    y -= skirt_h

    # Torso — round belly exposed. Wide oval bulging at the waist.
    belly_w = max(18, int(total * 0.30))
    belly_h = max(13, int(total * 0.20))
    belly_rect = pygame.Rect(cx - belly_w // 2, y - belly_h,
                             belly_w, belly_h + 4)
    pygame.draw.ellipse(surf, shadow, belly_rect)
    pygame.draw.ellipse(surf, body, belly_rect.inflate(-2, -2))
    # Lit highlight on belly upper-left.
    pygame.draw.arc(surf, lit, belly_rect.inflate(-4, -4),
                    math.pi * 0.8, math.pi * 1.25, 2)
    # Navel dot.
    pygame.draw.line(surf, dark,
                     (cx, y - belly_h // 2 + 1),
                     (cx, y - belly_h // 2 + 1), 1)
    # Upper torso narrower than belly — chest.
    chest_w = max(14, int(total * 0.22))
    chest_top = y - belly_h - torso_h + belly_h
    chest_pts = [
        (cx - belly_w // 2 + 2, y - belly_h),
        (cx + belly_w // 2 - 2, y - belly_h),
        (cx + chest_w // 2, chest_top),
        (cx - chest_w // 2, chest_top),
    ]
    pygame.draw.polygon(surf, shadow, chest_pts)
    inner_pts = [
        (cx - belly_w // 2 + 3, y - belly_h + 1),
        (cx + belly_w // 2 - 3, y - belly_h + 1),
        (cx + chest_w // 2 - 1, chest_top + 1),
        (cx - chest_w // 2 + 1, chest_top + 1),
    ]
    pygame.draw.polygon(surf, body, inner_pts)
    # Necklace — saffron bead band.
    pygame.draw.line(surf, saffron,
                     (cx - chest_w // 2 + 1, chest_top + 3),
                     (cx + chest_w // 2 - 1, chest_top + 3), 1)
    # Round 2: BOTH arms raised in the symmetric "welcome" pose. The
    # round belly + arms-up posture + laughing face carry the Budai
    # ID without the cloth bag (which was unreadable at thumbnail AND
    # inverted under the top mirror).
    arm_shadow = _shade(body, -25)
    # Right arm — raised cheerfully, hand at temple height.
    pygame.draw.polygon(surf, arm_shadow, [
        (cx + chest_w // 2 - 1, chest_top + 4),
        (cx + chest_w // 2 + 5, chest_top - 2),
        (cx + chest_w // 2 + 8, chest_top + 4),
        (cx + chest_w // 2 + 4, chest_top + 10),
        (cx + 2, chest_top + 8),
    ])
    pygame.draw.polygon(surf, body, [
        (cx + chest_w // 2 - 1, chest_top + 5),
        (cx + chest_w // 2 + 4, chest_top - 1),
        (cx + chest_w // 2 + 7, chest_top + 4),
        (cx + 2, chest_top + 7),
    ])
    # Right palm — small gilt rounded pad above the arm.
    pygame.draw.ellipse(surf, lit,
                        (cx + chest_w // 2 + 4, chest_top - 5, 5, 4))
    pygame.draw.ellipse(surf, body,
                        (cx + chest_w // 2 + 5, chest_top - 4, 3, 3))
    # Left arm — mirrored welcome lift, hand at the other temple.
    pygame.draw.polygon(surf, arm_shadow, [
        (cx - chest_w // 2 + 1, chest_top + 4),
        (cx - chest_w // 2 - 5, chest_top - 2),
        (cx - chest_w // 2 - 8, chest_top + 4),
        (cx - chest_w // 2 - 4, chest_top + 10),
        (cx - 2, chest_top + 8),
    ])
    pygame.draw.polygon(surf, body, [
        (cx - chest_w // 2 + 1, chest_top + 5),
        (cx - chest_w // 2 - 4, chest_top - 1),
        (cx - chest_w // 2 - 7, chest_top + 4),
        (cx - 2, chest_top + 7),
    ])
    # Left palm — mirrored gilt pad.
    pygame.draw.ellipse(surf, lit,
                        (cx - chest_w // 2 - 8, chest_top - 5, 5, 4))
    pygame.draw.ellipse(surf, body,
                        (cx - chest_w // 2 - 7, chest_top - 4, 3, 3))
    y = chest_top

    # Neck.
    pygame.draw.rect(surf, shadow,
                     (cx - 3, y - neck_h, 6, neck_h))
    pygame.draw.rect(surf, body,
                     (cx - 2, y - neck_h, 5, neck_h - 1))
    y -= neck_h

    # Head halo (subtler than Tian Tan).
    _draw_lit_halo(surf, cx, y - head_h // 2,
                   max(8, int(total * 0.16)), palette, intensity=0.7)

    # Head — round + jolly. Eyes shut, big toothy grin.
    head_w = max(13, int(total * 0.22))
    head_rect = pygame.Rect(cx - head_w // 2, y - head_h, head_w,
                             head_h + 1)
    pygame.draw.ellipse(surf, shadow, head_rect)
    pygame.draw.ellipse(surf, body, head_rect.inflate(-2, -2))
    pygame.draw.line(surf, lit,
                     (head_rect.x + 2, head_rect.y + head_h // 3),
                     (head_rect.x + 2, head_rect.y + (head_h * 2) // 3), 1)
    # Shaved head — no ushnisha. A few dot highlights on the crown.
    pygame.draw.line(surf, _shade(body, -25),
                     (cx - 2, y - head_h + 2),
                     (cx + 2, y - head_h + 2), 1)
    # Eyes — closed in laughter, drawn as upward curves.
    for side in (-1, 1):
        ex = cx + side * (head_w // 5)
        ey = y - (head_h * 2) // 3 + 1
        pygame.draw.line(surf, dark, (ex - 1, ey), (ex + 1, ey - 1), 1)
        pygame.draw.line(surf, dark, (ex + 1, ey - 1), (ex + 2, ey), 1)
    # Big toothy grin — a wider mouth, white teeth pixel.
    mouth_y = y - head_h // 4
    pygame.draw.line(surf, dark,
                     (cx - 3, mouth_y), (cx + 3, mouth_y), 1)
    pygame.draw.line(surf, dark,
                     (cx - 3, mouth_y), (cx - 4, mouth_y - 1), 1)
    pygame.draw.line(surf, dark,
                     (cx + 3, mouth_y), (cx + 4, mouth_y - 1), 1)
    pygame.draw.line(surf, _pigment_white(palette),
                     (cx - 2, mouth_y - 1), (cx + 2, mouth_y - 1), 1)
    # Earlobes.
    for side in (-1, 1):
        ex = cx + side * (head_w // 2 - 1)
        pygame.draw.rect(surf, _shade(body, -20),
                         (ex - 1 if side < 0 else ex,
                          y - (head_h * 2) // 3, 2, head_h // 2))


def _draw_maitreya(surf, top_rect, bot_rect, palette, seed):
    bcx = bot_rect.x + bot_rect.width // 2

    if bot_rect.height > 80:
        figure_top = bot_rect.y + 4
        figure_base = bot_rect.bottom - 2
        _draw_maitreya_figure(surf, bcx, figure_base, figure_top, palette)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 4, 10, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 6, seed=seed)

    natural_h = max(120, bot_rect.height - 8)

    def draw_into(tmp, tmp_cx, base_y, top_y):
        _draw_maitreya_figure(tmp, tmp_cx, base_y - 2, top_y + 4, palette)

    # Round 2: redraw so the top reads as a second standing Maitreya
    # facing forward rather than an upside-down statue. With the cloth
    # bag dropped the figure is now fully symmetric, so the redraw
    # also reads as a paired guardian-of-the-temple-gate set.
    _mirror_top(surf, top_rect, natural_h, draw_into,
                mirror_strategy="redraw")


def candidate_buddha_maitreya(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('buddha_maitreya', _draw_maitreya, surf, top_rect,
                 bot_rect, palette, seed)


# ── 9. Cliff-Niche Reclining Buddha (round 2 replacement) ─────────────────
#
# Round 1's vertical-stack Parinirvana didn't land — a tilted body forced
# into a vertical pillar slot. Round 2 swaps the solve entirely: the
# pillar IS a sandstone cave-temple cliff face (Yungang Grottoes echo),
# and a small horizontal niche is carved into the lower third holding a
# horizontally-laid gold-leaf reclining Buddha. The cliff identity reads
# at thumbnail, and the reclining figure sits inside a niche where the
# horizontal pose is correct.
#
# References:
#   https://en.wikipedia.org/wiki/Reclining_Buddha
#   https://en.wikipedia.org/wiki/Yungang_Grottoes

def _draw_horizontal_reclining(surf, niche_rect, palette):
    """Horizontal reclining Buddha INSIDE the niche. Head on the left
    end resting on a small pillow, body extending right, feet at the
    right end. Gold-leaf finish."""
    if niche_rect.width < 24 or niche_rect.height < 10:
        return
    body = _gold_leaf(palette)
    lit = _shade(body, 35)
    shadow = _gold_leaf_deep(palette)
    dark = _shade(shadow, -35)
    saffron = _saffron_robe(palette)

    cy = niche_rect.y + niche_rect.height // 2 + 1
    left_x = niche_rect.x + 3
    right_x = niche_rect.right - 4
    body_h = max(4, niche_rect.height - 4)

    # ── Pillow under the head, at the left end.
    pillow_w = max(8, int(niche_rect.width * 0.18))
    pillow_h = max(3, body_h // 2)
    pillow_rect = pygame.Rect(left_x, cy - pillow_h // 2 - 1,
                              pillow_w, pillow_h + 2)
    pygame.draw.ellipse(surf, dark, pillow_rect)
    pygame.draw.ellipse(surf, _porcelain_white(palette),
                        pillow_rect.inflate(-2, -2))
    pygame.draw.line(surf, saffron,
                     (pillow_rect.x + 1, pillow_rect.y + pillow_h // 2),
                     (pillow_rect.right - 1, pillow_rect.y + pillow_h // 2), 1)

    # ── Body — long horizontal bar from after the head to the feet.
    head_w = max(7, int(niche_rect.width * 0.15))
    head_left = left_x + pillow_w // 3
    head_top = cy - body_h // 2 - 2
    head_rect = pygame.Rect(head_left, head_top, head_w, body_h + 3)
    pygame.draw.ellipse(surf, shadow, head_rect)
    pygame.draw.ellipse(surf, body, head_rect.inflate(-2, -2))
    # Ushnisha bump on top-left of head.
    pygame.draw.ellipse(surf, shadow,
                        (head_rect.x + 1, head_rect.y - 2, 4, 4))
    pygame.draw.ellipse(surf, body,
                        (head_rect.x + 2, head_rect.y - 1, 3, 3))
    # Snail-curls along the top of the head.
    for c in range(3):
        dx = head_rect.x + 2 + c * 2
        pygame.draw.line(surf, _shade(body, -30),
                         (dx, head_rect.y + 1), (dx, head_rect.y + 1), 1)
    # Closed eye + serene mouth on the right of the head.
    pygame.draw.line(surf, dark,
                     (head_rect.right - 3, head_rect.y + body_h // 2),
                     (head_rect.right - 2, head_rect.y + body_h // 2), 1)
    pygame.draw.line(surf, dark,
                     (head_rect.right - 2, head_rect.y + body_h - 1),
                     (head_rect.right - 1, head_rect.y + body_h - 1), 1)
    # Long ear hanging.
    pygame.draw.line(surf, _shade(body, -25),
                     (head_rect.x + 2, head_rect.bottom - 2),
                     (head_rect.x + 2, head_rect.bottom + 1), 1)

    # ── Torso + legs — single horizontal bar from head_rect right edge
    # to feet, with horizontal robe creases.
    bar_left = head_rect.right - 2
    bar_right = right_x - 4
    bar_top = cy - body_h // 2
    bar_h = body_h
    pygame.draw.rect(surf, shadow,
                     (bar_left, bar_top, bar_right - bar_left, bar_h))
    pygame.draw.rect(surf, body,
                     (bar_left + 1, bar_top + 1,
                      bar_right - bar_left - 2, bar_h - 2))
    pygame.draw.line(surf, lit,
                     (bar_left + 1, bar_top + 1),
                     (bar_right - 1, bar_top + 1), 1)
    # Saffron robe sash band across the body — runs along the upper
    # third so the figure reads as draped.
    sash_y = bar_top + max(1, bar_h // 3)
    pygame.draw.line(surf, saffron,
                     (bar_left + 1, sash_y),
                     (bar_right - 1, sash_y), 1)
    # Folds — short vertical ticks every ~4 px.
    for fx in range(bar_left + 4, bar_right - 2, 4):
        pygame.draw.line(surf, _shade(body, -25),
                         (fx, bar_top + 1),
                         (fx, bar_top + bar_h - 2), 1)
    # Knees bulge — a small hump near the foot end.
    knee_x = bar_right - max(8, niche_rect.width // 6)
    pygame.draw.ellipse(surf, _shade(body, -10),
                        (knee_x - 2, bar_top - 1, 5, bar_h + 2))
    pygame.draw.arc(surf, lit,
                    (knee_x - 2, bar_top - 1, 5, bar_h + 2),
                    math.pi * 1.1, math.pi * 1.9, 1)

    # ── Feet (soles facing right end) — a small dark-edged bump.
    foot_w = max(4, bar_h)
    pygame.draw.ellipse(surf, shadow,
                        (bar_right - 2, bar_top, foot_w, bar_h))
    pygame.draw.ellipse(surf, body,
                        (bar_right - 1, bar_top + 1, foot_w - 2, bar_h - 2))
    # Toe dot stripes.
    for tk in range(3):
        pygame.draw.line(surf, dark,
                         (bar_right + 1, bar_top + 1 + tk * (bar_h // 3)),
                         (bar_right + 1, bar_top + 1 + tk * (bar_h // 3)),
                         1)


def _draw_cliff_column(surf, cx, base_y, top_y, palette,
                       *, full_w):
    """Plain sandstone cliff column with horizontal strata bands.
    Round-2 cliff identity for the reclining-Buddha pillar — fills
    the entire bottom rect so the cliff IS the pillar."""
    if base_y - top_y < 40:
        return
    cliff_dark = _sandstone_shadow(palette)
    cliff_mid = _sandstone_warm(palette)
    cliff_lit = _sandstone_lit(palette)
    rect = pygame.Rect(cx - full_w // 2, top_y, full_w, base_y - top_y)

    # Vertical strata stack — variable heights, tones cool toward top.
    band_seeds = (0.20, 0.12, 0.26, 0.10, 0.18, 0.14)
    norm = sum(band_seeds)
    y = rect.bottom
    bands = []
    for sb in band_seeds:
        bh = max(3, int(rect.height * (sb / norm)))
        bands.append((y - bh, bh))
        y -= bh
    if y > rect.y:
        bands[-1] = (rect.y, bands[-1][1] + (y - rect.y))
    for i, (by, bh) in enumerate(bands):
        t = i / max(1, len(bands) - 1)
        band_body = _mix(cliff_mid, cliff_dark, t * 0.65)
        band_top = _mix(cliff_lit, cliff_mid, t * 0.55)
        pygame.draw.rect(surf, band_body,
                         (rect.x, by, rect.width, bh))
        pygame.draw.line(surf, band_top,
                         (rect.x, by), (rect.right - 1, by), 1)
        pygame.draw.line(surf, _shade(band_body, -25),
                         (rect.x, by + bh - 1),
                         (rect.right - 1, by + bh - 1), 1)
        for k in range(2):
            px = rect.x + 3 + ((i * 11 + k * 17) % (rect.width - 6))
            py = by + max(1, bh // 2) + ((k + i) % max(1, bh // 2))
            pygame.draw.line(surf, _shade(band_body, -20),
                             (px, py), (px, py), 1)


def _draw_niche_reclining_figure(surf, cx, base_y, top_y, palette,
                                 *, pillar_w):
    """Sandstone cliff column with a horizontal carved niche in the
    lower third holding a horizontal reclining Buddha. The cliff IS
    the pillar — the niche is small relative to the column height."""
    total = base_y - top_y
    if total < 60:
        return

    _draw_cliff_column(surf, cx, base_y, top_y, palette, full_w=pillar_w)

    # ── Niche in the lower third — horizontal rectangle with a small
    # arched top, cut into the cliff so the gold figure inside reads
    # as a sanctum.
    niche_w = max(40, int(pillar_w * 1.05))
    niche_h = max(14, int(total * 0.15))
    # Niche bottom sits ~25% up from the base of the cliff column.
    niche_bottom_y = base_y - max(10, int(total * 0.18))
    niche_top_y = niche_bottom_y - niche_h
    niche_rect = pygame.Rect(cx - niche_w // 2, niche_top_y,
                             niche_w, niche_h)
    inner = _shade(_sandstone_shadow(palette), -40)

    # Carve — dark filled rect + small arched cap at the top.
    arch_h = max(4, niche_h // 4)
    pygame.draw.rect(surf, inner,
                     (niche_rect.x, niche_rect.y + arch_h,
                      niche_rect.w, niche_rect.h - arch_h))
    pygame.draw.ellipse(surf, inner,
                        (niche_rect.x, niche_rect.y,
                         niche_rect.w, arch_h * 2))
    # Dark rim along sides + base of the niche.
    pygame.draw.line(surf, _shade(inner, -25),
                     (niche_rect.x, niche_rect.y + arch_h),
                     (niche_rect.x, niche_rect.bottom - 1), 1)
    pygame.draw.line(surf, _shade(inner, -25),
                     (niche_rect.right - 1, niche_rect.y + arch_h),
                     (niche_rect.right - 1, niche_rect.bottom - 1), 1)
    pygame.draw.line(surf, _shade(inner, -25),
                     (niche_rect.x, niche_rect.bottom - 1),
                     (niche_rect.right - 1, niche_rect.bottom - 1), 1)
    # Niche sill — a slim lit stone lip just below the niche.
    pygame.draw.line(surf, _sandstone_lit(palette),
                     (niche_rect.x - 2, niche_rect.bottom),
                     (niche_rect.right + 1, niche_rect.bottom), 1)

    # ── Halo glow behind the figure — quiet at noon, hot at night.
    _draw_lit_halo(surf, cx, niche_rect.y + niche_rect.height // 2 - 2,
                   max(8, niche_rect.height // 2 + 2), palette,
                   intensity=0.7)

    # ── Reclining figure inside the niche.
    _draw_horizontal_reclining(surf, niche_rect, palette)


def _draw_niche_reclining(surf, top_rect, bot_rect, palette, seed):
    bcx = bot_rect.x + bot_rect.width // 2
    pillar_w = bot_rect.width

    if bot_rect.height > 80:
        figure_top = bot_rect.y
        figure_base = bot_rect.bottom
        _draw_niche_reclining_figure(surf, bcx, figure_base, figure_top,
                                     palette, pillar_w=pillar_w)
        # No grass bed — the cliff plunges straight to the ground line.

    natural_h = max(120, bot_rect.height)

    def draw_into(tmp, tmp_cx, base_y, top_y):
        _draw_niche_reclining_figure(tmp, tmp_cx, base_y, top_y,
                                     palette, pillar_w=pillar_w)

    # Flip — the cliff + niche reads cleanly as a paired top-bottom
    # cliff face with a niche carved into the bottom of each, so the
    # mirrored top niche sits near the gap edge (sky-facing) and feels
    # natural rather than upside-down.
    _mirror_top(surf, top_rect, natural_h, draw_into,
                mirror_strategy="flip")


def candidate_buddha_niche_reclining(surf, top_rect, bot_rect, palette,
                                     seed):
    _cached_draw('buddha_niche_reclining', _draw_niche_reclining, surf,
                 top_rect, bot_rect, palette, seed)


# ── 10. Guanyin / Avalokiteśvara (千手觀音 / 觀音) ─────────────────────────
#
# Standing slender bodhisattva — flowing white-porcelain robe, water
# vase in the left hand, willow branch in the right, flame-shaped halo
# behind the head. The most ELEGANT silhouette of the set.
#
# Reference: https://en.wikipedia.org/wiki/Guanyin

def _draw_guanyin_figure(surf, cx, base_y, top_y, palette):
    total = base_y - top_y
    if total < 60:
        return
    body = _porcelain_white(palette)
    lit = _shade(body, 15)
    shadow = _porcelain_shadow(palette)
    dark = _shade(shadow, -30)
    saffron = _saffron_robe(palette)
    rim = _gilt_bright(palette)
    bronze = _bronze_body(palette)

    head_h = max(11, int(total * 0.16))
    crown_h = max(5, int(total * 0.08))
    neck_h = max(2, int(total * 0.03))
    torso_h = max(20, int(total * 0.28))
    skirt_h = max(20, int(total * 0.30))
    lotus_h = total - head_h - crown_h - neck_h - torso_h - skirt_h

    y = base_y

    # Lotus pedestal at the feet.
    _draw_lotus_plinth(surf, cx, y, max(24, int(total * 0.40)), palette,
                       h=lotus_h)
    y -= lotus_h

    # Skirt — long, narrow, flowing. NARROWER than the warriors' robes
    # to give Guanyin the elegant elongated silhouette.
    skirt_top_w = max(8, int(total * 0.14))
    skirt_bot_w = max(14, int(total * 0.22))
    skirt_pts = [
        (cx - skirt_bot_w // 2, y),
        (cx + skirt_bot_w // 2, y),
        (cx + skirt_top_w // 2, y - skirt_h),
        (cx - skirt_top_w // 2, y - skirt_h),
    ]
    pygame.draw.polygon(surf, shadow, skirt_pts)
    inner = [
        (cx - skirt_bot_w // 2 + 1, y - 1),
        (cx + skirt_bot_w // 2 - 1, y - 1),
        (cx + skirt_top_w // 2 - 1, y - skirt_h + 1),
        (cx - skirt_top_w // 2 + 1, y - skirt_h + 1),
    ]
    pygame.draw.polygon(surf, body, inner)
    # Lit on the left flank.
    pygame.draw.line(surf, lit,
                     (cx - skirt_top_w // 2 + 1, y - skirt_h + 2),
                     (cx - skirt_bot_w // 2 + 1, y - 1), 1)
    # Many fine vertical folds — Guanyin's robes are famously detailed.
    for k in range(-3, 4):
        if k == 0:
            continue
        fx_top = cx + k * (skirt_top_w // 8)
        fx_bot = cx + k * (skirt_bot_w // 6)
        pygame.draw.line(surf, _shade(body, -25),
                         (fx_top, y - skirt_h + 3), (fx_bot, y - 2), 1)
    # Flowing scarf-tails on each side of the skirt — wavy outward
    # curves.
    for side in (-1, 1):
        sx_top = cx + side * (skirt_top_w // 2 - 1)
        sx_bot = cx + side * (skirt_bot_w // 2 + 2)
        # Cyan/saffron scarf hint.
        for k in range(3):
            t = k / 2
            wave = math.sin(t * math.pi) * 2 * side
            mx = sx_top + (sx_bot - sx_top) * t + wave
            my = y - skirt_h + (skirt_h // 2) * t + (skirt_h // 2) * k * 0.5
            pygame.draw.circle(surf, saffron,
                               (int(mx), int(my)), 1)
    # Saffron belt band at waist.
    pygame.draw.rect(surf, saffron,
                     (cx - skirt_top_w // 2 - 1, y - skirt_h - 1,
                      skirt_top_w + 2, 2))
    y -= skirt_h

    # Torso — narrow + elegant. Vertical body with a subtle hourglass.
    torso_w = max(10, int(total * 0.16))
    torso_top = y - torso_h
    torso_pts = [
        (cx - torso_w // 2, y),
        (cx + torso_w // 2, y),
        (cx + torso_w // 2 + 1, torso_top + torso_h // 2),
        (cx + torso_w // 2 - 1, torso_top),
        (cx - torso_w // 2 + 1, torso_top),
        (cx - torso_w // 2 - 1, torso_top + torso_h // 2),
    ]
    pygame.draw.polygon(surf, shadow, torso_pts)
    inner_pts = [
        (cx - torso_w // 2 + 1, y - 1),
        (cx + torso_w // 2 - 1, y - 1),
        (cx + torso_w // 2, torso_top + torso_h // 2),
        (cx + torso_w // 2 - 2, torso_top + 1),
        (cx - torso_w // 2 + 2, torso_top + 1),
        (cx - torso_w // 2, torso_top + torso_h // 2),
    ]
    pygame.draw.polygon(surf, body, inner_pts)
    # Subtle gradient.
    _vert_gradient_rect(surf,
                        pygame.Rect(cx - torso_w // 2 + 2, torso_top + 2,
                                    torso_w - 4, torso_h - 4),
                        lit, body, shadow)
    # Necklace — fine saffron band across the chest.
    pygame.draw.line(surf, saffron,
                     (cx - torso_w // 2 + 1, torso_top + 4),
                     (cx + torso_w // 2 - 1, torso_top + 4), 1)
    # Small bronze pendant centred.
    pygame.draw.line(surf, bronze,
                     (cx, torso_top + 5), (cx, torso_top + 7), 1)
    # Round 3: bold vertical silk sash dropping from the left shoulder
    # past the hip. AD round 2 flagged Guanyin/Maitreya colliding at
    # thumbnail; this single 2-px cream stripe is the strongest
    # "this is NOT Maitreya" cue that survives small scales.
    sash_x = cx - torso_w // 2 + 2
    sash_top_y = torso_top + 2
    sash_bot_y = y + max(4, skirt_h // 4)
    sash_col = _mix(_pigment_white(palette), (240, 232, 220), 0.55)
    pygame.draw.line(surf, sash_col,
                     (sash_x, sash_top_y), (sash_x, sash_bot_y), 2)
    pygame.draw.line(surf, _shade(sash_col, -30),
                     (sash_x + 2, sash_top_y), (sash_x + 2, sash_bot_y), 1)
    # Left arm — drops down holding a small WATER VASE (lotus-bud
    # shaped) at hip height.
    arm_shadow = _shade(body, -25)
    pygame.draw.polygon(surf, arm_shadow, [
        (cx - torso_w // 2, torso_top + 3),
        (cx - torso_w // 2 - 4, torso_top + 8),
        (cx - torso_w // 2 - 5, torso_top + torso_h - 3),
        (cx - torso_w // 2 - 2, torso_top + torso_h - 1),
    ])
    pygame.draw.polygon(surf, body, [
        (cx - torso_w // 2, torso_top + 4),
        (cx - torso_w // 2 - 3, torso_top + 8),
        (cx - torso_w // 2 - 4, torso_top + torso_h - 4),
        (cx - torso_w // 2 - 2, torso_top + torso_h - 2),
    ])
    # Water vase — lotus-bud / pear shape at the bottom of the left hand.
    vase_x = cx - torso_w // 2 - 5
    vase_y = torso_top + torso_h - 1
    pygame.draw.ellipse(surf, dark,
                        (vase_x - 4, vase_y - 4, 8, 8))
    pygame.draw.ellipse(surf, _shade(body, -10),
                        (vase_x - 3, vase_y - 3, 6, 6))
    pygame.draw.line(surf, lit,
                     (vase_x - 2, vase_y - 2), (vase_x, vase_y - 3), 1)
    # Vase neck — small bottleneck on top.
    pygame.draw.rect(surf, dark, (vase_x - 1, vase_y - 6, 3, 3))
    # Right arm — raised at elbow, holding the WILLOW BRANCH up to
    # bless. Hand at chest height with the willow extending up.
    pygame.draw.polygon(surf, arm_shadow, [
        (cx + torso_w // 2, torso_top + 3),
        (cx + torso_w // 2 + 4, torso_top - 2),
        (cx + torso_w // 2 + 7, torso_top + 4),
        (cx + torso_w // 2 + 4, torso_top + 10),
        (cx + 1, torso_top + 9),
    ])
    pygame.draw.polygon(surf, body, [
        (cx + torso_w // 2, torso_top + 4),
        (cx + torso_w // 2 + 3, torso_top - 1),
        (cx + torso_w // 2 + 6, torso_top + 4),
        (cx + 1, torso_top + 8),
    ])
    # Hand pinching the willow stem.
    hand_x = cx + torso_w // 2 + 5
    hand_y = torso_top - 3
    pygame.draw.ellipse(surf, dark, (hand_x - 2, hand_y - 1, 4, 3))
    pygame.draw.ellipse(surf, lit, (hand_x - 1, hand_y - 1, 3, 2))
    # Willow branch — single thin saffron-green twig with small leaf
    # drips falling off it.
    willow_top_y = hand_y - 10
    pygame.draw.line(surf, _pigment_celadon(palette),
                     (hand_x, hand_y - 1),
                     (hand_x + 1, willow_top_y), 1)
    for k in range(3):
        py = hand_y - 2 - k * 3
        pygame.draw.line(surf, _pigment_celadon(palette),
                         (hand_x + 1, py), (hand_x - 2, py + 1), 1)
        pygame.draw.line(surf, _shade(_pigment_celadon(palette), -15),
                         (hand_x - 2, py + 1), (hand_x - 2, py + 1), 1)
    y = torso_top

    # Neck.
    pygame.draw.rect(surf, shadow,
                     (cx - 2, y - neck_h, 4, neck_h))
    pygame.draw.rect(surf, body,
                     (cx - 1, y - neck_h, 3, neck_h - 1))
    y -= neck_h

    # Flame halo — bigger and BRIGHTER than the Tian Tan halo.
    halo_r = max(11, int(total * 0.18))
    _draw_lit_halo(surf, cx, y - head_h // 2, halo_r, palette,
                   intensity=1.0)
    # Flame-shaped outer rim — gold pointed petals around the halo.
    for k, ang in enumerate((math.pi * 1.5, math.pi * 1.35,
                              math.pi * 1.65, math.pi * 1.20,
                              math.pi * 1.80)):
        fx = cx + math.cos(ang) * (halo_r - 1)
        fy = y - head_h // 2 + math.sin(ang) * (halo_r - 1)
        tip_x = cx + math.cos(ang) * (halo_r + 2)
        tip_y = y - head_h // 2 + math.sin(ang) * (halo_r + 2)
        pygame.draw.line(surf, rim,
                         (int(fx), int(fy)),
                         (int(tip_x), int(tip_y)), 1)

    # Head — slender oval, serene expression.
    head_w = max(10, int(total * 0.17))
    head_rect = pygame.Rect(cx - head_w // 2, y - head_h, head_w,
                             head_h + 1)
    pygame.draw.ellipse(surf, shadow, head_rect)
    pygame.draw.ellipse(surf, body, head_rect.inflate(-2, -2))
    pygame.draw.line(surf, lit,
                     (head_rect.x + 2, head_rect.y + head_h // 3),
                     (head_rect.x + 2, head_rect.y + (head_h * 2) // 3), 1)
    # Closed eyes — gentle curves.
    for side in (-1, 1):
        ex = cx + side * (head_w // 5)
        ey = y - (head_h * 2) // 3 + 1
        pygame.draw.line(surf, dark,
                         (ex - 1, ey), (ex + 1, ey - 1), 1)
    # Urna.
    pygame.draw.line(surf, rim,
                     (cx, y - (head_h * 2) // 3 - 1),
                     (cx, y - (head_h * 2) // 3 - 1), 1)
    # Smile.
    pygame.draw.line(surf, dark,
                     (cx - 1, y - head_h // 4),
                     (cx + 1, y - head_h // 4), 1)
    # Long earrings — small saffron drops.
    for side in (-1, 1):
        ex = cx + side * (head_w // 2 - 1)
        pygame.draw.line(surf, dark,
                         (ex, y - head_h // 3),
                         (ex + side, y - 1), 1)
        pygame.draw.line(surf, bronze,
                         (ex + side, y - 1), (ex + side, y - 1), 1)
    y -= head_h

    # Crown — small bronze diadem with 3 spire-points, smaller than
    # the General's fish-tail. Has a tiny seated Amitabha-Buddha effigy
    # at the centre (Guanyin canonical motif), drawn as a small
    # triangular bronze dot.
    crown_w = max(8, int(total * 0.14))
    pygame.draw.rect(surf, dark,
                     (cx - crown_w // 2, y - 2, crown_w, 3))
    pygame.draw.rect(surf, bronze,
                     (cx - crown_w // 2 + 1, y - 1, crown_w - 2, 2))
    # 3 spire-points along the diadem.
    for k, mx in ((-1, cx - crown_w // 3), (0, cx),
                   (1, cx + crown_w // 3)):
        pygame.draw.polygon(surf, bronze, [
            (mx - 1, y - 2),
            (mx + 1, y - 2),
            (mx, y - crown_h),
        ])
        pygame.draw.line(surf, rim,
                         (mx, y - 2), (mx, y - crown_h + 1), 1)
    # Small Amitabha effigy centred above the diadem.
    pygame.draw.line(surf, rim,
                     (cx, y - crown_h),
                     (cx, y - crown_h), 1)


def _draw_guanyin_with_night_keyline(surf, draw_fn, bbox, palette):
    """Round 2: at NIGHT phase only, paint a faint cool-blue keyline
    along the porcelain silhouette so Guanyin doesn't melt into the
    dark sky. Renders the figure into a temp SRCALPHA, dilates it 1 px
    in cool blue under the figure, and re-blits the original on top.
    Other phases get the figure directly with no keyline."""
    if not _is_dark_sky(palette):
        draw_fn(surf)
        return
    bx, by, bw, bh = bbox
    pad = 3
    tmp = pygame.Surface((bw + pad * 2, bh + pad * 2), pygame.SRCALPHA)
    # The caller-supplied wrapper paints the figure into `tmp` at the
    # bbox offset; we then build a 1-px cool-blue keyline along the
    # silhouette via pygame.mask, blit it under the figure, and stack
    # the figure on top so the rim peeks out the silhouette edge.
    draw_fn(tmp, pad - bx, pad - by)
    mask = pygame.mask.from_surface(tmp)
    silhouette = mask.to_surface(
        setcolor=(160, 195, 230, 120),
        unsetcolor=(0, 0, 0, 0))
    silhouette.set_alpha(None)
    glow = pygame.Surface(tmp.get_size(), pygame.SRCALPHA)
    # 4-directional 1-px dilation = silhouette outline ring.
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        glow.blit(silhouette, (dx, dy))
    surf.blit(glow, (bx - pad, by - pad))
    surf.blit(tmp, (bx - pad, by - pad))


def _draw_guanyin(surf, top_rect, bot_rect, palette, seed):
    bcx = bot_rect.x + bot_rect.width // 2

    if bot_rect.height > 80:
        figure_top = bot_rect.y + 4
        figure_base = bot_rect.bottom - 2

        # Bounding box for the night-keyline pass — wider than the
        # pillar to catch the willow + halo flares + scarf-tails.
        bbox = (bot_rect.x - 24, bot_rect.y - 4,
                bot_rect.width + 48, bot_rect.height + 8)

        def figure_into(target, off_x=0, off_y=0):
            _draw_guanyin_figure(target, bcx + off_x,
                                 figure_base + off_y,
                                 figure_top + off_y, palette)

        _draw_guanyin_with_night_keyline(surf, figure_into, bbox, palette)
        # Light foliage — Guanyin classically stands above a pond.
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 4, 10, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 6, seed=seed)

    natural_h = max(120, bot_rect.height - 8)

    def draw_into(tmp, tmp_cx, base_y, top_y):
        _draw_guanyin_figure(tmp, tmp_cx, base_y - 2, top_y + 4, palette)

    # Round 2: redraw so the top reads as a SECOND porcelain Guanyin
    # facing forward (twin guardian pairing), keeping the vase + willow
    # right-side up.
    _mirror_top(surf, top_rect, natural_h, draw_into,
                mirror_strategy="redraw")


def candidate_buddha_guanyin(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('buddha_guanyin', _draw_guanyin, surf, top_rect,
                 bot_rect, palette, seed)


# ── Registries ────────────────────────────────────────────────────────────

VARIANTS = [
    candidate_warrior_general,
    candidate_warrior_standing_archer,
    candidate_warrior_kneeling_archer,
    candidate_warrior_cavalry,
    candidate_warrior_charioteer,
    candidate_buddha_leshan,
    candidate_buddha_tian_tan,
    candidate_buddha_maitreya,
    candidate_buddha_niche_reclining,
    candidate_buddha_guanyin,
]

VARIANT_NAMES = [
    "Terracotta General (高级军吏俑)",
    "Standing Archer / Infantry (立射俑)",
    "Kneeling Crossbowman (跪射俑)",
    "Cavalryman + Saddled Horse (骑兵俑)",
    "Charioteer (御手俑)",
    "Leshan Giant Buddha (乐山大佛)",
    "Tian Tan Buddha (天坛大佛)",
    "Standing Maitreya / Budai (彌勒)",
    "Cliff-Niche Reclining Buddha (涅槃·龕)",
    "Guanyin / Avalokiteśvara (觀音)",
]

VARIANT_SOURCES = [
    "https://www.smithsonianmag.com/smart-news/archaeologists-discover-rare-clay-commander-among-thousands-of-life-size-terra-cotta-soldiers-in-china-180985747/",
    "https://www.travelchinaguide.com/attraction/shaanxi/xian/terra_cotta_army/standing-archers.htm",
    "https://www.travelchinaguide.com/attraction/shaanxi/xian/terra_cotta_army/kneeling-archers.htm",
    "https://www.travelchinaguide.com/attraction/shaanxi/xian/terra_cotta_army/warrior-types.htm",
    "https://www.travelchinaguide.com/attraction/shaanxi/xian/terra_cotta_army/chariots.htm",
    "https://en.wikipedia.org/wiki/Leshan_Giant_Buddha",
    "https://en.wikipedia.org/wiki/Tian_Tan_Buddha",
    "https://en.wikipedia.org/wiki/Budai",
    "https://en.wikipedia.org/wiki/Yungang_Grottoes",
    "https://en.wikipedia.org/wiki/Guanyin",
]
