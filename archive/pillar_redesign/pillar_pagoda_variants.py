"""Pagoda-pillar candidates for the obstacle-pillar redesign round.

Five distinct architectural takes on the same `draw_pillar_pair` API the live
game uses (game/pillar_variants.py:817), so each candidate can be diffed
straight into that dispatcher once the user picks a winner. Every renderer is
`candidate_<name>(surf, top_rect, bot_rect, palette, seed)` — same signature,
same per-pipe stable seed contract.

The five takes intentionally cover different reading strategies for the
top+bottom pair so the picker can see how each one handles the variable gap:

  candidate_tang_gateway       — Tang tower below, carved awning + banner web
                                 above; reads as a temple gateway.
  candidate_mirrored_split     — One pagoda silhouette is broken by the gap;
                                 top = upper tiers + finial pointing into the
                                 gap, bottom = lower tiers + base.
  candidate_facing_pair        — Twin mini pagodas, both finials pointing at
                                 the gap; the pair bookends the corridor.
  candidate_japanese_pavilion  — Japanese 5-storey tō below, inverted hanging
                                 sky-pavilion on chains above.
  candidate_stupa_canopy       — Whitewashed Tibetan chorten below, sagging
                                 prayer-flag canopy hung from anchor stones
                                 above.

Every candidate also varies these per-seed traits so 5 spawns of the SAME
candidate look like 5 different temples and not five clones:
  * tier count (3 / 5 / 7),
  * body taper / wall width within the rect,
  * which ornament shows up (lantern / cairn / banner / finial pine),
  * which vegetation gets dropped in (moss cascade, climbing vine,
    side shrubs, grass + flowers at the base, ground ferns).

Heavy reuse of the existing foliage/ornament helpers from
game.pillar_variants and game.draw keeps the temples wearing the same
moss and prayer-flags as the rest of the world.
"""
from __future__ import annotations

import math
import random

import pygame

from game.draw import (
    draw_wuling_pine,
    draw_moss_strand,
    draw_side_shrub,
)
from game.pillar_variants import (
    draw_moss_patch,
    draw_climbing_vine,
    draw_grass_bed,
    draw_flower_bed,
    draw_ground_ferns,
    draw_prayer_flags,
    draw_cairn,
    draw_paper_lantern,
    draw_bird_sil,
    draw_incense_smoke,
    draw_cascading_vine,
)


# ── Colour helpers ──────────────────────────────────────────────────────────
#
# Roofs read as "pagoda" only if they pop against the wall — cinnabar (Chinese
# tower), terracotta (Tang), cedar-brown (Japanese tō), and gold-tipped white
# (Tibetan chorten). The codebase keeps everything biome-driven, so each
# roof colour is mixed from the active stone palette to keep day/night
# transitions smooth without breaking the silhouette read.

def _mix(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def _shade(c, d):
    return (max(0, min(255, c[0] + d)),
            max(0, min(255, c[1] + d)),
            max(0, min(255, c[2] + d)))


def _cinnabar(palette):
    # Pull a saturated red roof out of the stone_dark so it retints at night.
    return _mix(palette['stone_dark'], (210, 60, 45), 0.62)


def _terracotta(palette):
    return _mix(palette['stone_mid'], (190, 90, 55), 0.55)


def _cedar(palette):
    return _mix(palette['stone_dark'], (110, 70, 45), 0.70)


def _chorten_white(palette):
    # Whitewashed chorten body — biased toward stone_light so dusk/night
    # still leans warm/cool with the rest of the scene.
    return _mix(palette['stone_light'], (245, 240, 232), 0.55)


def _gilt(palette):
    return _mix(palette['stone_accent'], (235, 195, 90), 0.65)


# ── Common drawing primitives ───────────────────────────────────────────────

def _wall_strip(surf, x, y, w, h, palette):
    """A plastered pagoda wall — light face + warm shadow on the right edge."""
    if h <= 0 or w <= 0:
        return
    light = _mix(palette['stone_light'], (250, 245, 230), 0.30)
    mid = palette['stone_mid']
    pygame.draw.rect(surf, mid, (x, y, w, h))
    pygame.draw.rect(surf, light, (x, y, max(1, w - 2), max(1, h - 1)))
    pygame.draw.rect(surf, _shade(mid, -25), (x + w - 2, y, 2, h))


def _eave(surf, cx, y, half_w, depth, roof_col, accent_col, curl=0.50):
    """A single curving eave row — wider than the wall below.
    `curl` 0..1 controls how steeply the tips rise (Tang tower curls hard,
    Japanese tō stays flatter)."""
    rise = max(2, int(depth * curl))
    pts = [
        (cx - half_w,         y + 1),
        (cx - half_w + 2,     y - rise),
        (cx,                  y - max(2, rise // 2)),
        (cx + half_w - 2,     y - rise),
        (cx + half_w,         y + 1),
        (cx + half_w - 1,     y + depth),
        (cx - half_w + 1,     y + depth),
    ]
    pygame.draw.polygon(surf, _shade(roof_col, -40), pts)
    inner = [(p[0], p[1] + 1) for p in pts]
    pygame.draw.polygon(surf, roof_col, inner)
    pygame.draw.line(surf, accent_col,
                     (cx - half_w + 2, y),
                     (cx + half_w - 2, y), 1)


def _finial_sorin(surf, cx, top_y, height, palette):
    """Sōrin-style finial — stack of discs above a central spire.
    Reads like a pagoda mast at game scale."""
    gold = _gilt(palette)
    dark = palette['stone_dark']
    base_y = top_y
    pygame.draw.line(surf, dark, (cx, base_y), (cx, base_y - height), 2)
    rings = max(3, height // 6)
    for i in range(rings):
        ry = base_y - 3 - i * (height // rings)
        rw = max(2, 6 - i // 2)
        pygame.draw.line(surf, gold, (cx - rw, ry), (cx + rw, ry), 1)
    pygame.draw.circle(surf, gold, (cx, base_y - height + 2), 3)
    pygame.draw.circle(surf, _shade(gold, 40),
                       (cx, base_y - height + 2), 1)


def _chinese_finial(surf, cx, top_y, height, palette):
    """Chinese tower finial — bulb + spire, more bulbous than sōrin."""
    gold = _gilt(palette)
    dark = palette['stone_dark']
    pygame.draw.line(surf, dark, (cx, top_y), (cx, top_y - height + 6), 2)
    pygame.draw.ellipse(surf, gold,
                        (cx - 4, top_y - 12, 8, 10))
    pygame.draw.circle(surf, _shade(gold, 30),
                       (cx, top_y - height + 4), 2)
    pygame.draw.circle(surf, _gilt(palette),
                       (cx, top_y - height + 8), 3)


def _window_lattice(surf, cx, y, w, h, palette):
    """Small red-trimmed lattice window for pagoda walls."""
    if w < 6 or h < 6:
        return
    frame = _mix(palette['stone_dark'], (170, 60, 40), 0.55)
    inner = _mix(palette['stone_mid'], (255, 230, 160), 0.35)
    pygame.draw.rect(surf, frame, (cx - w // 2, y, w, h))
    pygame.draw.rect(surf, inner, (cx - w // 2 + 1, y + 1, w - 2, h - 2))
    pygame.draw.line(surf, frame,
                     (cx, y + 1), (cx, y + h - 1), 1)
    pygame.draw.line(surf, frame,
                     (cx - w // 2 + 1, y + h // 2),
                     (cx + w // 2 - 1, y + h // 2), 1)


def _doorway(surf, cx, base_y, w, h, palette):
    if h < 5:
        return
    frame = _mix(palette['stone_dark'], (170, 60, 40), 0.55)
    inside = _shade(palette['stone_dark'], -10)
    pygame.draw.rect(surf, frame, (cx - w // 2, base_y - h, w, h))
    pygame.draw.rect(surf, inside,
                     (cx - w // 2 + 1, base_y - h + 1, w - 2, h - 1))
    pygame.draw.arc(surf, _gilt(palette),
                    (cx - w // 2, base_y - h - 1, w, 4), 0, math.pi, 1)


# ── 1. Tang Tower + Awning + Banner Web ─────────────────────────────────────

def candidate_tang_gateway(surf, top_rect, bot_rect, palette, seed):
    """Bottom is a multi-tier Chinese tower pagoda; top is a paired ceiling
    element — carved awning eave + banner web — so the pair reads as a
    temple gateway you fly through."""
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2
    roof = _cinnabar(palette)
    accent = _gilt(palette)
    wall = palette['stone_mid']

    # Per-seed signature variation.
    tier_count = rng.choice([3, 5, 7])
    base_w_factor = rng.uniform(0.82, 0.96)
    has_lantern = rng.random() < 0.55
    has_cairn = rng.random() < 0.45
    has_pine = rng.random() < 0.40

    # ── Bottom pagoda ───────────────────────────────────────────────────
    if bot_rect.height > 30:
        # Plinth at base.
        plinth_h = 10
        plinth_w = int(bot_rect.width * 1.05)
        pygame.draw.rect(surf, _shade(wall, -25),
                         (bcx - plinth_w // 2, bot_rect.bottom - plinth_h,
                          plinth_w, plinth_h))
        pygame.draw.rect(surf, palette['stone_light'],
                         (bcx - plinth_w // 2, bot_rect.bottom - plinth_h,
                          plinth_w, 2))

        # Tiers stack from the plinth up to the spire.
        usable_h = bot_rect.height - plinth_h - 18  # 18 = finial budget
        tier_h = max(10, usable_h // tier_count)
        for i in range(tier_count):
            t = i / max(1, tier_count - 1)
            tier_w = int(bot_rect.width * (base_w_factor - t * 0.32))
            ty = bot_rect.bottom - plinth_h - (i + 1) * tier_h
            # Wall.
            _wall_strip(surf, bcx - tier_w // 2, ty,
                        tier_w, tier_h - 4, palette)
            # Window/door per tier.
            if i == 0 and tier_h > 12:
                _doorway(surf, bcx, ty + tier_h - 4,
                         min(14, tier_w - 6), min(12, tier_h - 6), palette)
            elif tier_h > 10 and tier_w > 14:
                _window_lattice(surf, bcx,
                                ty + 2, min(10, tier_w - 8),
                                min(7, tier_h - 6), palette)
            # Curved eave overhanging the wall.
            eave_half = tier_w // 2 + 6
            _eave(surf, bcx, ty + tier_h - 5, eave_half, 4,
                  roof, accent, curl=0.85)

        # Finial.
        top_tier_y = bot_rect.bottom - plinth_h - tier_count * tier_h
        _chinese_finial(surf, bcx, top_tier_y, 18, palette)

        # Optional decorative pine on the top tier ledge.
        if has_pine and bot_rect.height > 110:
            draw_wuling_pine(surf, bcx + 14, top_tier_y + 4, 18,
                             palette, lean=6, layers=3)

        # Optional small red lantern hanging from lowest eave.
        if has_lantern:
            lt_y = bot_rect.bottom - plinth_h - tier_h + 4
            draw_paper_lantern(surf, bcx - 18, lt_y, strand=6,
                               scale=0.7, color='red')
            draw_paper_lantern(surf, bcx + 18, lt_y, strand=6,
                               scale=0.7, color='red')

        # Climbing vine up one side, varied by seed.
        if bot_rect.height > 90:
            side_x = bot_rect.x + (4 if seed % 2 else bot_rect.width - 6)
            draw_climbing_vine(surf, side_x, bot_rect.y + 24,
                               bot_rect.bottom - 14, palette, seed=seed)

        # Optional offering cairn at the base.
        if has_cairn and bot_rect.height > 70:
            draw_cairn(surf, bcx - 18, bot_rect.bottom - plinth_h + 1,
                       n=3, pennant=False)

        # Grass + flower bed at the very base.
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 4, 14, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 8, seed=seed)

    # ── Top awning + banner web ─────────────────────────────────────────
    if top_rect.height > 18:
        # Two stacked eaves that flare DOWN — they're the underside of the
        # gateway awning the player flies under.
        awning_h = min(top_rect.height, 70)
        for i, off in enumerate((0, 18, 36)):
            if off + 16 > awning_h:
                break
            ey = top_rect.bottom - off - 6
            half = top_rect.width // 2 + 8 - i * 2
            _eave(surf, tcx, ey, half, 5, roof, accent, curl=0.95)
        # Plastered wall block above the bottom-most eave.
        wall_top = max(top_rect.y, top_rect.bottom - awning_h)
        wall_h = top_rect.bottom - 50 - wall_top
        if wall_h > 6:
            _wall_strip(surf, tcx - top_rect.width // 2 + 4, wall_top,
                        top_rect.width - 8, wall_h, palette)
            # Window on the upper wall.
            if wall_h > 16:
                _window_lattice(surf, tcx, wall_top + 4,
                                min(14, top_rect.width - 14),
                                min(10, wall_h - 6), palette)
        # Banner web — strings of prayer flags fanning down from the awning
        # corners to anchor stones inside the bottom pagoda's top tier.
        if bot_rect.height > 50:
            for sx, ex in ((tcx - 24, bcx - 20), (tcx + 24, bcx + 20)):
                draw_prayer_flags(surf, sx, top_rect.bottom - 2,
                                  ex, bot_rect.y - 4, n=6)
        # Moss tipping the awning corners.
        for off in (-22, -10, 10, 22):
            draw_moss_strand(surf, tcx + off, top_rect.bottom - 4,
                             8 + abs(off) % 6, palette,
                             jitter_seed=seed + off)
        # A drifting silhouette bird high in the gap-top region.
        if top_rect.height > 60:
            draw_bird_sil(surf, tcx - 28,
                          max(20, top_rect.y + 28), size=4)


# ── 2. Mirrored Tiered Pagoda (broken silhouette) ───────────────────────────

def candidate_mirrored_split(surf, top_rect, bot_rect, palette, seed):
    """The gap breaks ONE pagoda silhouette. Top rect carries the upper
    tiers + finial pointing down; bottom rect carries the lower tiers + base.
    Reads as a single temple cleaved horizontally by the corridor."""
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2
    roof = _cinnabar(palette)
    accent = _gilt(palette)

    tier_count_bot = rng.choice([2, 3, 4])
    tier_count_top = rng.choice([2, 3, 4])
    base_w_factor = rng.uniform(0.88, 1.00)
    has_lantern = rng.random() < 0.50
    has_pine = rng.random() < 0.55

    # ── Bottom half: lower tiers + base ────────────────────────────────
    if bot_rect.height > 26:
        plinth_h = 12
        plinth_w = int(bot_rect.width * 1.10)
        pygame.draw.rect(surf, _shade(palette['stone_mid'], -25),
                         (bcx - plinth_w // 2, bot_rect.bottom - plinth_h,
                          plinth_w, plinth_h))
        pygame.draw.rect(surf, palette['stone_light'],
                         (bcx - plinth_w // 2, bot_rect.bottom - plinth_h,
                          plinth_w, 2))
        # Wider lower tiers, growing narrower as they approach the gap.
        usable_h = bot_rect.height - plinth_h - 4
        tier_h = max(14, usable_h // tier_count_bot)
        for i in range(tier_count_bot):
            t = i / max(1, tier_count_bot - 1)
            tier_w = int(bot_rect.width * (base_w_factor - t * 0.15))
            ty = bot_rect.bottom - plinth_h - (i + 1) * tier_h
            _wall_strip(surf, bcx - tier_w // 2, ty,
                        tier_w, tier_h - 5, palette)
            if i == 0 and tier_h > 14:
                _doorway(surf, bcx, ty + tier_h - 5,
                         min(16, tier_w - 6), min(14, tier_h - 7), palette)
            else:
                _window_lattice(surf, bcx, ty + 3,
                                min(12, tier_w - 8),
                                min(8, tier_h - 8), palette)
            eave_half = tier_w // 2 + 7
            _eave(surf, bcx, ty + tier_h - 6, eave_half, 5,
                  roof, accent, curl=0.85)
        # Top tier transitions into the gap — a small "stub" finial-cap
        # so the broken silhouette reads as architecture, not a cut.
        cap_y = bot_rect.y
        pygame.draw.rect(surf, _shade(roof, -30),
                         (bcx - 14, cap_y, 28, 3))
        pygame.draw.rect(surf, roof, (bcx - 13, cap_y + 1, 26, 2))

        # Ground vegetation.
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 4, 14, palette, seed=seed)
        if has_lantern:
            draw_paper_lantern(surf, bcx - plinth_w // 2 - 4,
                               bot_rect.bottom - plinth_h + 1, strand=18,
                               scale=0.8, color='red')
            draw_paper_lantern(surf, bcx + plinth_w // 2 + 4,
                               bot_rect.bottom - plinth_h + 1, strand=18,
                               scale=0.8, color='red')

    # ── Top half: upper tiers + finial pointing DOWN ───────────────────
    if top_rect.height > 22:
        usable_h = top_rect.height - 16  # finial budget
        tier_h = max(10, usable_h // tier_count_top)
        for i in range(tier_count_top):
            t = i / max(1, tier_count_top - 1)
            tier_w = int(top_rect.width * (0.70 - t * 0.25))
            # i = 0 is the BOTTOM-most tier above the gap — closest to player.
            ty = top_rect.bottom - 16 - (i + 1) * tier_h
            if ty < top_rect.y:
                break
            _wall_strip(surf, tcx - tier_w // 2, ty,
                        tier_w, tier_h - 4, palette)
            _window_lattice(surf, tcx, ty + 2,
                            min(8, tier_w - 6),
                            min(6, tier_h - 6), palette)
            eave_half = tier_w // 2 + 5
            _eave(surf, tcx, ty + tier_h - 4, eave_half, 4,
                  roof, accent, curl=0.95)
        # The downward finial — drawn at the BOTTOM of the top rect.
        spike_y = top_rect.bottom
        pygame.draw.line(surf, _gilt(palette),
                         (tcx, spike_y - 16), (tcx, spike_y - 1), 2)
        pygame.draw.ellipse(surf, _gilt(palette),
                            (tcx - 3, spike_y - 14, 6, 6))

        # Hanging moss + a sideways pine off one upper tier.
        for off in (-12, -4, 4, 12):
            draw_moss_strand(surf, tcx + off, top_rect.bottom - 16,
                             8 + abs(off) % 5, palette,
                             jitter_seed=seed + off)
        if has_pine and top_rect.height > 80:
            draw_wuling_pine(surf, tcx + 12, top_rect.bottom - 36, 16,
                             palette, lean=8, direction='down', layers=3)


# ── 3. Facing Pair (twin pagodas) ───────────────────────────────────────────

def candidate_facing_pair(surf, top_rect, bot_rect, palette, seed):
    """Top AND bottom rects each carry a full mini pagoda whose finials point
    at the gap. Reads as a bookended temple corridor."""
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2
    roof = _terracotta(palette)
    accent = _gilt(palette)
    wall = palette['stone_mid']

    tier_count = rng.choice([3, 4, 5])
    has_lantern = rng.random() < 0.65
    has_shrubs = rng.random() < 0.60
    has_vines = rng.random() < 0.55

    # ── Bottom mini-pagoda (rooted on ground, finial UP toward gap) ────
    if bot_rect.height > 28:
        plinth_h = 8
        plinth_w = int(bot_rect.width * 1.05)
        pygame.draw.rect(surf, _shade(wall, -25),
                         (bcx - plinth_w // 2, bot_rect.bottom - plinth_h,
                          plinth_w, plinth_h))
        pygame.draw.rect(surf, palette['stone_light'],
                         (bcx - plinth_w // 2, bot_rect.bottom - plinth_h,
                          plinth_w, 2))
        usable_h = bot_rect.height - plinth_h - 14
        tier_h = max(10, usable_h // tier_count)
        for i in range(tier_count):
            t = i / max(1, tier_count - 1)
            tier_w = int(bot_rect.width * (0.95 - t * 0.42))
            ty = bot_rect.bottom - plinth_h - (i + 1) * tier_h
            _wall_strip(surf, bcx - tier_w // 2, ty,
                        tier_w, tier_h - 4, palette)
            if i == 0 and tier_h > 12:
                _doorway(surf, bcx, ty + tier_h - 4,
                         min(12, tier_w - 6), min(10, tier_h - 6), palette)
            elif tier_w > 12:
                _window_lattice(surf, bcx, ty + 2,
                                min(8, tier_w - 6),
                                min(6, tier_h - 6), palette)
            eave_half = tier_w // 2 + 5
            _eave(surf, bcx, ty + tier_h - 5, eave_half, 4,
                  roof, accent, curl=0.75)
        top_tier_y = bot_rect.bottom - plinth_h - tier_count * tier_h
        _finial_sorin(surf, bcx, top_tier_y, 14, palette)
        if has_shrubs:
            draw_side_shrub(surf, bot_rect.x + 4,
                            bot_rect.bottom - plinth_h - 4, palette,
                            scale=0.85)
            draw_side_shrub(surf, bot_rect.x + bot_rect.width - 4,
                            bot_rect.bottom - plinth_h - 4, palette,
                            scale=0.85)
        if has_vines and bot_rect.height > 90:
            draw_climbing_vine(surf, bot_rect.x + bot_rect.width - 6,
                               bot_rect.y + 24, bot_rect.bottom - 14,
                               palette, seed=seed)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 4, 14, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 7, seed=seed)

    # ── Top mini-pagoda (rooted on ceiling, finial DOWN toward gap) ────
    if top_rect.height > 28:
        plinth_h = 6
        plinth_w = int(top_rect.width * 1.05)
        # The "plinth" of the top pagoda sits at the CEILING (y=0).
        pygame.draw.rect(surf, _shade(wall, -25),
                         (tcx - plinth_w // 2, 0, plinth_w, plinth_h))
        usable_h = top_rect.height - plinth_h - 14
        tier_h = max(10, usable_h // tier_count)
        for i in range(tier_count):
            t = i / max(1, tier_count - 1)
            tier_w = int(top_rect.width * (0.95 - t * 0.42))
            # i = 0 is the BOTTOM-most tier (closest to gap).
            ty = plinth_h + (tier_count - 1 - i) * tier_h
            _wall_strip(surf, tcx - tier_w // 2, ty,
                        tier_w, tier_h - 4, palette)
            if tier_w > 12:
                _window_lattice(surf, tcx, ty + 2,
                                min(8, tier_w - 6),
                                min(6, tier_h - 6), palette)
            # Eave still curls UPWARD even though the building hangs down —
            # this is the underside of the eave the player flies past.
            eave_half = tier_w // 2 + 5
            _eave(surf, tcx, ty + tier_h - 5, eave_half, 4,
                  roof, accent, curl=0.75)
        # Finial points DOWN into the gap from the bottom of the lowest tier.
        finial_y = plinth_h + tier_count * tier_h
        if finial_y < top_rect.bottom:
            pygame.draw.line(surf, _gilt(palette),
                             (tcx, finial_y),
                             (tcx, min(finial_y + 14, top_rect.bottom - 1)),
                             2)
            pygame.draw.circle(surf, _gilt(palette),
                               (tcx, min(finial_y + 12, top_rect.bottom - 2)),
                               2)
        # Hanging lanterns from the bottom-most eave corners.
        if has_lantern:
            draw_paper_lantern(surf, tcx - 16, finial_y - 4,
                               strand=10, scale=0.7, color='red')
            draw_paper_lantern(surf, tcx + 16, finial_y - 4,
                               strand=10, scale=0.7, color='red')
        # Moss on the awning corners.
        for off in (-14, -4, 4, 14):
            draw_moss_strand(surf, tcx + off, finial_y - 6,
                             7 + abs(off) % 4, palette,
                             jitter_seed=seed + off)


# ── 4. Japanese 5-storey Tō + Sky Pavilion ──────────────────────────────────

def candidate_japanese_pavilion(surf, top_rect, bot_rect, palette, seed):
    """Bottom is a wooden Japanese 5-storey tō with deep up-curled eaves and a
    sōrin finial. Top is an inverted floating sky-pavilion suspended on chains
    from the ceiling — a tiny hanging shrine."""
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2
    roof = _cedar(palette)
    accent = _gilt(palette)

    tier_count = rng.choice([3, 5, 7])
    has_pine = rng.random() < 0.50
    has_lantern = rng.random() < 0.45
    has_ferns = rng.random() < 0.60

    # ── Tō tower ───────────────────────────────────────────────────────
    if bot_rect.height > 30:
        plinth_h = 8
        plinth_w = int(bot_rect.width * 1.08)
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -10),
                         (bcx - plinth_w // 2, bot_rect.bottom - plinth_h,
                          plinth_w, plinth_h))
        pygame.draw.rect(surf, palette['stone_light'],
                         (bcx - plinth_w // 2, bot_rect.bottom - plinth_h,
                          plinth_w, 2))
        # Japanese tō teigen — uniform-width tiers, deep eaves that flare
        # wider than the wall they sit on. Tier-narrowing is subtle.
        usable_h = bot_rect.height - plinth_h - 26  # spire budget
        tier_h = max(10, usable_h // tier_count)
        for i in range(tier_count):
            t = i / max(1, tier_count - 1)
            tier_w = int(bot_rect.width * (0.78 - t * 0.20))
            ty = bot_rect.bottom - plinth_h - (i + 1) * tier_h
            # Wall with vertical timber striping.
            _wall_strip(surf, bcx - tier_w // 2, ty,
                        tier_w, tier_h - 5, palette)
            for sx in range(bcx - tier_w // 2 + 3, bcx + tier_w // 2 - 2, 4):
                pygame.draw.line(surf, _shade(palette['stone_mid'], -25),
                                 (sx, ty + 1), (sx, ty + tier_h - 6), 1)
            if i == 0 and tier_h > 12:
                _doorway(surf, bcx, ty + tier_h - 5,
                         min(12, tier_w - 6), min(10, tier_h - 6), palette)
            # Deep, gently up-curled eave — flatter than Chinese tower.
            eave_half = tier_w // 2 + 8
            _eave(surf, bcx, ty + tier_h - 5, eave_half, 5,
                  roof, accent, curl=0.50)
        # Sōrin spire.
        top_tier_y = bot_rect.bottom - plinth_h - tier_count * tier_h
        _finial_sorin(surf, bcx, top_tier_y, 22, palette)
        # Small pine clinging to the plinth.
        if has_pine:
            draw_wuling_pine(surf, bot_rect.x + 6,
                             bot_rect.bottom - plinth_h - 2, 18,
                             palette, lean=-6, layers=3)
            draw_wuling_pine(surf, bot_rect.x + bot_rect.width - 6,
                             bot_rect.bottom - plinth_h - 2, 18,
                             palette, lean=6, layers=3)
        if has_ferns:
            draw_ground_ferns(surf, bcx, bot_rect.bottom - plinth_h + 1,
                              bot_rect.width + 6, 4, palette, seed=seed)
        # Grass at the very base for groundedness.
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 4, 14, palette, seed=seed)

    # ── Sky pavilion (suspended shrine) ────────────────────────────────
    if top_rect.height > 30:
        # Chains hang from the ceiling at the top of top_rect.
        pavilion_h = min(top_rect.height - 8, 56)
        pav_top_y = max(top_rect.y, top_rect.bottom - pavilion_h)
        # Chains.
        for cx_off in (-12, 12):
            cy = top_rect.y
            cyb = pav_top_y
            pygame.draw.line(surf, palette['stone_dark'],
                             (tcx + cx_off, cy), (tcx + cx_off, cyb), 1)
            for r in range(cy + 6, cyb, 6):
                pygame.draw.circle(surf, _shade(palette['stone_light'], 20),
                                   (tcx + cx_off, r), 2, 1)
        # Pavilion roof — single tier with deep flared eave.
        eave_half = top_rect.width // 2 + 8
        _eave(surf, tcx, pav_top_y, eave_half, 6,
              roof, accent, curl=0.55)
        # Pavilion body (open walls — just corner posts + a hint of an
        # interior lantern glow).
        body_top = pav_top_y + 6
        body_bot = top_rect.bottom - 4
        if body_bot > body_top:
            _wall_strip(surf, tcx - top_rect.width // 2 + 6, body_top,
                        top_rect.width - 12, body_bot - body_top, palette)
            # Posts.
            for px in (tcx - top_rect.width // 2 + 8,
                       tcx + top_rect.width // 2 - 9):
                pygame.draw.line(surf, palette['stone_dark'],
                                 (px, body_top), (px, body_bot), 1)
            # Inside lantern.
            draw_paper_lantern(surf, tcx, body_top - 2,
                               strand=4, scale=0.7, color='gold')
        # Cloud puff under the pavilion to make it feel floating.
        for cx_off, sz in ((-12, 4), (0, 6), (12, 4), (6, 3), (-6, 3)):
            pygame.draw.circle(surf,
                               _mix(palette['stone_light'],
                                    (250, 250, 250), 0.55),
                               (tcx + cx_off, top_rect.bottom + 1), sz)
        if has_lantern:
            # Additional lantern hanging from one eave corner into the gap.
            draw_paper_lantern(surf, tcx + (eave_half - 4),
                               pav_top_y + 4, strand=12, scale=0.7,
                               color='red')


# ── 5. Tibetan Stupa + Prayer-Flag Canopy ───────────────────────────────────

def candidate_stupa_canopy(surf, top_rect, bot_rect, palette, seed):
    """Bottom is a whitewashed chorten (stepped plinth, bell dome, harmika,
    13-ring spire). Top is a sagging prayer-flag canopy strung from two
    carved anchor stones at the upper corners."""
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2
    white = _chorten_white(palette)
    edge = _shade(white, -50)
    gold = _gilt(palette)
    dark = palette['stone_dark']

    step_count = rng.choice([3, 4, 5])
    n_flag_strings = rng.choice([2, 3])
    has_pines = rng.random() < 0.60
    has_cairn = rng.random() < 0.55

    # ── Chorten ────────────────────────────────────────────────────────
    if bot_rect.height > 50:
        usable_h = bot_rect.height - 6
        # Vertical budget: spire 22, harmika 8, dome 22, plinth = remainder.
        spire_h = 22
        harmika_h = 8
        dome_h = 22
        steps_h = max(20, usable_h - spire_h - harmika_h - dome_h)
        # Stepped plinth at the base — `step_count` lifts forming a wedding cake.
        step_band_w = bot_rect.width
        for i in range(step_count):
            tt = i / max(1, step_count)
            sh = max(4, steps_h // step_count)
            sw = int(step_band_w * (1.05 - tt * 0.18))
            sy = bot_rect.bottom - sh * (i + 1)
            if sy < bot_rect.y:
                break
            pygame.draw.rect(surf, edge, (bcx - sw // 2, sy, sw, sh))
            pygame.draw.rect(surf, white,
                             (bcx - sw // 2 + 1, sy + 1, sw - 2, sh - 2))
            # Warm shadow along the right edge.
            pygame.draw.rect(surf, _shade(white, -35),
                             (bcx + sw // 2 - 2, sy + 1, 2, sh - 2))
        # Bell dome (anda).
        dome_top_y = bot_rect.bottom - steps_h - dome_h
        dome_w = int(bot_rect.width * 0.78)
        pygame.draw.ellipse(surf, edge,
                            (bcx - dome_w // 2, dome_top_y,
                             dome_w, dome_h))
        pygame.draw.ellipse(surf, white,
                            (bcx - dome_w // 2 + 1, dome_top_y + 1,
                             dome_w - 2, dome_h - 2))
        # Gold band around the dome's waist.
        pygame.draw.rect(surf, gold,
                         (bcx - dome_w // 2 + 2, dome_top_y + dome_h - 6,
                          dome_w - 4, 2))
        # Sun + moon symbol on the dome face.
        pygame.draw.circle(surf, gold, (bcx, dome_top_y + dome_h // 2), 2)
        # Harmika (square box).
        harmika_w = int(bot_rect.width * 0.42)
        harmika_y = dome_top_y - harmika_h
        pygame.draw.rect(surf, edge,
                         (bcx - harmika_w // 2, harmika_y,
                          harmika_w, harmika_h))
        pygame.draw.rect(surf, white,
                         (bcx - harmika_w // 2 + 1, harmika_y + 1,
                          harmika_w - 2, harmika_h - 2))
        # Buddha eyes.
        eye_y = harmika_y + 3
        pygame.draw.line(surf, dark, (bcx - 5, eye_y), (bcx - 3, eye_y), 1)
        pygame.draw.line(surf, dark, (bcx + 3, eye_y), (bcx + 5, eye_y), 1)
        # Spire — 13 rings tapering to a point.
        spire_y = harmika_y - spire_h
        pygame.draw.line(surf, dark, (bcx, harmika_y), (bcx, spire_y), 2)
        rings = 13
        for i in range(rings):
            ry = harmika_y - 1 - int(i * (spire_h - 6) / rings)
            rw = max(1, 5 - i // 3)
            pygame.draw.line(surf, gold, (bcx - rw, ry), (bcx + rw, ry), 1)
        # Lotus + jewel finial.
        pygame.draw.circle(surf, gold, (bcx, spire_y + 2), 3)
        pygame.draw.circle(surf, _shade(gold, 50), (bcx, spire_y - 1), 1)
        # Side pines climbing up the steps.
        if has_pines:
            draw_wuling_pine(surf, bot_rect.x + 4,
                             bot_rect.bottom - steps_h + 4, 22,
                             palette, lean=-5, layers=3)
            draw_wuling_pine(surf, bot_rect.x + bot_rect.width - 4,
                             bot_rect.bottom - steps_h + 4, 22,
                             palette, lean=5, layers=3)
        # Offering cairn at the base.
        if has_cairn:
            draw_cairn(surf, bcx + bot_rect.width // 2 + 6,
                       bot_rect.bottom - 2, n=3, pennant=True)
        # Ground cover.
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 8, 14, palette, seed=seed)
    elif bot_rect.height > 0:
        # Degenerate small chorten if the gap is huge — just plinth + dome.
        pygame.draw.rect(surf, white,
                         (bot_rect.x + 4, bot_rect.y + 2,
                          bot_rect.width - 8, max(1, bot_rect.height - 4)))

    # ── Anchor stones + flag canopy on the ceiling ─────────────────────
    if top_rect.height > 12:
        # Anchor stones at the upper-left and upper-right corners — these
        # are short carved blocks the flag lines hang from.
        for ax in (top_rect.x + 4, top_rect.x + top_rect.width - 4):
            stone_h = min(top_rect.height, 16)
            pygame.draw.rect(surf, edge,
                             (ax - 6, top_rect.bottom - stone_h, 12, stone_h))
            pygame.draw.rect(surf, white,
                             (ax - 5, top_rect.bottom - stone_h + 1,
                              10, stone_h - 2))
            pygame.draw.rect(surf, gold,
                             (ax - 4, top_rect.bottom - 4, 8, 2))
        # Multiple prayer flag strings sagging across the gap.
        for k in range(n_flag_strings):
            jitter = k * 6 - 4
            draw_prayer_flags(surf,
                              top_rect.x + 4 + jitter,
                              top_rect.bottom - 4,
                              top_rect.x + top_rect.width - 4 - jitter,
                              top_rect.bottom - 4,
                              n=7 + k)
        # Moss tipping the corners.
        for off in (-2, 2):
            for ax in (top_rect.x + 4, top_rect.x + top_rect.width - 4):
                draw_moss_strand(surf, ax + off, top_rect.bottom - 2,
                                 10, palette, jitter_seed=seed + ax + off)
        # A drifting bird above the flags.
        if top_rect.height > 50:
            draw_bird_sil(surf, tcx, max(20, top_rect.y + 30), size=5)


# ── Registry ────────────────────────────────────────────────────────────────

CANDIDATES = {
    "tang_gateway":        candidate_tang_gateway,
    "mirrored_split":      candidate_mirrored_split,
    "facing_pair":         candidate_facing_pair,
    "japanese_pavilion":   candidate_japanese_pavilion,
    "stupa_canopy":        candidate_stupa_canopy,
}

CANDIDATE_BLURBS = {
    "tang_gateway":      "Tang tower + carved awning eave with banner web",
    "mirrored_split":    "Single pagoda silhouette broken at the gap",
    "facing_pair":       "Twin mini pagodas — finials face the gap",
    "japanese_pavilion": "Japanese 5-storey tō + hanging sky-pavilion",
    "stupa_canopy":      "Tibetan chorten + prayer-flag canopy on anchor stones",
}
