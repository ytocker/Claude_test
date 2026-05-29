"""Pagoda-pillar candidates — round 5.

Round 4 read as a row of near-identical Chinese towers, so this round
rebuilds the five from scratch, each modeled on a SPECIFIC iconic
real-world pagoda so their silhouettes, palettes and ornaments diverge
hard at the 360x640 game scale.

  candidate_horyuji          — Hōryū-ji Tō (Japan, 7th c.):
                               cedar columns + white-plaster panels,
                               wide flat shingled eaves, bronze sōrin
                               with 9-disk stack. Top half = same tō
                               MIRRORED, sōrin pointing into the gap.
                               https://en.wikipedia.org/wiki/H%C5%8Dry%C5%AB-ji
  candidate_shwedagon        — Shwedagon (Burma):
                               gilded bell on octagonal terraces, hti
                               umbrella + diamond bud. Top = hanging
                               votive bell with hti chandelier.
                               https://en.wikipedia.org/wiki/Shwedagon_Pagoda
  candidate_boudhanath       — Boudhanath Eye Stupa (Nepal/Tibet):
                               whitewashed dome, harmika cube with the
                               painted Buddha eyes + ūrṇā + nose-glyph,
                               13-step gold pyramid + sun-moon-flame.
                               Top = prayer-flag canopy on anchor
                               blocks.
                               https://en.wikipedia.org/wiki/Boudhanath
  candidate_wat_arun         — Wat Arun Khmer Prang (Thailand):
                               lobed corncob spire in pastel-pink +
                               aqua + cream porcelain mosaic, kala
                               brackets, deva niches. Top = mirrored
                               hanging prang sharing the same palette.
                               https://en.wikipedia.org/wiki/Wat_Arun
  candidate_songyue          — Songyue Twelve-Sided Brick Pagoda
                               (China, Northern Wei 523 CE):
                               terracotta brick, 15 dense dwarf-eaves,
                               12-sided plan, lotus-bud finial. Top =
                               smaller twin pagoda from ceiling.
                               https://en.wikipedia.org/wiki/Songyue_Pagoda

Every renderer shares the live game's pillar-pair contract:
`candidate_<name>(surf, top_rect, bot_rect, palette, seed)`. All hues
derive from the biome palette so day → night retints cleanly. Heavy
reuse of `game.pillar_variants` and `game.draw` keeps the foliage
language consistent.

Each candidate caches its drawn pillar pair to a SRCALPHA bitmap per
seed × palette so the curved eaves and dome arcs don't re-alias every
frame at game runtime — mirrors the KFC sprite-cache pattern in
`game/entities.py:800`.
"""
from __future__ import annotations

import math
import random

import pygame

from game.draw import (
    draw_moss_strand,
)
from game.pillar_variants import (
    draw_grass_bed,
    draw_flower_bed,
    draw_prayer_flags,
)


# ── Colour helpers ──────────────────────────────────────────────────────────
#
# Every architectural colour is mixed against the live palette so the
# biome's day/night retint carries through. No raw RGB constants leak into
# the pillar bodies — archetype hues are derived from stone_dark / stone_mid
# / stone_light / stone_accent and biased toward a target tone.

def _mix(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def _shade(c, d):
    return (max(0, min(255, c[0] + d)),
            max(0, min(255, c[1] + d)),
            max(0, min(255, c[2] + d)))


def _cedar(palette):
    # Dark cedar columns of a Japanese tō — deep brown grounded in stone_dark
    # so dusk and night still read warm-brown instead of cool-grey.
    return _mix(palette['stone_dark'], (78, 48, 32), 0.78)


def _plaster(palette):
    # White-clay plaster panel between cedar columns; biased to stone_light
    # so the biome carries cool nights and warm dawns through it.
    return _mix(palette['stone_light'], (242, 232, 212), 0.55)


def _bronze(palette):
    # Patinated bronze sōrin — green-warm so it reads metallic, not gold.
    return _mix(palette['stone_accent'], (158, 132, 70), 0.62)


def _gold_bright(palette):
    # Shwedagon gilt — brighter, more saturated than the patinated bronze.
    return _mix(palette['stone_accent'], (240, 196, 78), 0.78)


def _gold_deep(palette):
    return _mix(palette['stone_accent'], (175, 130, 40), 0.78)


def _stupa_white(palette):
    # Whitewashed Boudhanath dome — warmer than plaster, faint cream tint.
    return _mix(palette['stone_light'], (248, 242, 228), 0.62)


def _saffron(palette):
    # Boudhanath/Tibetan saffron accent — derived from stone_accent.
    return _mix(palette['stone_accent'], (220, 138, 52), 0.70)


def _lapis(palette):
    # Boudhanath blue eye-paint accent.
    return _mix(palette['stone_dark'], (48, 78, 130), 0.66)


def _porcelain_pink(palette):
    # Wat Arun pastel — desaturated rose around stone_light.
    return _mix(palette['stone_light'], (236, 188, 188), 0.62)


def _porcelain_aqua(palette):
    return _mix(palette['stone_light'], (170, 218, 214), 0.62)


def _porcelain_cream(palette):
    return _mix(palette['stone_light'], (244, 234, 208), 0.58)


def _terracotta(palette):
    # Songyue brick base — warm clay-red anchored in stone_dark.
    return _mix(palette['stone_dark'], (162, 84, 52), 0.72)


def _brick_mortar(palette):
    return _mix(palette['stone_mid'], (130, 80, 56), 0.50)


def _is_dark_sky(palette):
    """Drives lit-rim alpha — night/dusk skies get a brighter window glow."""
    top = palette['sky_top']
    return (top[0] + top[1] + top[2]) / 3.0 < 110


# ── Generic ornament primitives ─────────────────────────────────────────────

def _aa_polyline(surf, color, points, closed=False):
    """Anti-aliased polyline for curved silhouettes (eave + dome arcs)."""
    if len(points) >= 2:
        try:
            pygame.draw.aalines(surf, color, closed, points)
        except (ValueError, TypeError):
            pygame.draw.lines(surf, color, closed, points, 1)


def _lit_niche(surf, cx, cy, w, h, palette):
    """A small dark window/doorway niche with a thin lit rim. The rim brightens
    against dark sky palettes so the niche reads as warm interior light at
    night and as a quiet shadow at noon — sampling sky_top brightness keeps
    the cue calibrated to the biome."""
    if w < 3 or h < 4:
        return
    frame = _shade(palette['stone_dark'], -25)
    inside = _shade(palette['stone_dark'], -50)
    rim_alpha = 220 if _is_dark_sky(palette) else 90
    rim = _mix(palette['stone_accent'], (255, 215, 120), 0.78)
    pygame.draw.rect(surf, frame, (cx - w // 2, cy, w, h))
    pygame.draw.rect(surf, inside, (cx - w // 2 + 1, cy + 1, w - 2, h - 2))
    rim_layer = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(rim_layer, (*rim, rim_alpha), (0, 0, w, h), 1)
    surf.blit(rim_layer, (cx - w // 2, cy))


def _tile_hatch(surf, x1, y1, x2, y2, color, step=3):
    """Short perpendicular hatch marks along an eave line — reads as the row
    of tile-ends on a tiled roof. Spans the eave from x1,y1 to x2,y2."""
    dx, dy = x2 - x1, y2 - y1
    length = max(1, int(math.hypot(dx, dy)))
    ux, uy = dx / length, dy / length
    nx, ny = -uy, ux
    for s in range(0, length, step):
        sx = x1 + ux * s
        sy = y1 + uy * s
        pygame.draw.line(surf, color,
                         (int(sx), int(sy)),
                         (int(sx + nx * 1.5), int(sy + ny * 1.5)), 1)


# ── Cached eave primitives (Japanese / Chinese flat shingled eave) ──────────

def _eave_tang_curl(surf, cx, y_base, half_w_body, overhang, depth,
                    roof_col, accent_col, tile_col, curl=0.7):
    """Up-curled tiled eave — anchor points on a quadratic, then tile-hatch
    along the upper edge for shingle-row detail. Corner-hook polygons sit on
    each tip so a Chinese/Japanese roof reads even at small scale."""
    overhang = max(overhang, 7)
    tip_rise = max(2, int(depth * (0.5 + curl)))
    centre_sag = max(1, depth // 3)
    half_outer = half_w_body + overhang
    pts = [
        (cx - half_outer,     y_base + depth - 1),
        (cx - half_outer,     y_base - tip_rise),
        (cx - half_outer + 3, y_base - tip_rise + 1),
        (cx - half_w_body,    y_base - centre_sag // 2),
        (cx,                  y_base + 1 - centre_sag),
        (cx + half_w_body,    y_base - centre_sag // 2),
        (cx + half_outer - 3, y_base - tip_rise + 1),
        (cx + half_outer,     y_base - tip_rise),
        (cx + half_outer,     y_base + depth - 1),
    ]
    pygame.draw.polygon(surf, _shade(roof_col, -55), pts)
    body_pts = [(p[0], p[1] - 1) if p[1] >= y_base else p for p in pts]
    pygame.draw.polygon(surf, roof_col, body_pts)
    # Keyline under the eave so the silhouette stays crisp on bright skies.
    keyline = _shade(roof_col, -75)
    pygame.draw.line(surf, keyline,
                     (cx - half_outer + 1, y_base + depth - 1),
                     (cx + half_outer - 1, y_base + depth - 1), 1)
    # Tile hatching along the upper curve so the roof reads as a tile-row.
    _tile_hatch(surf, cx - half_outer + 4, y_base - tip_rise + 2,
                cx + half_outer - 4, y_base - tip_rise + 2,
                tile_col, step=3)
    # Accent stripe just under the ridge.
    pygame.draw.line(surf, accent_col,
                     (cx - half_w_body + 1, y_base - 1),
                     (cx + half_w_body - 1, y_base - 1), 1)
    # Corner-hook upturn polygons sharpen the tip silhouette.
    hook = _shade(roof_col, 30)
    pygame.draw.polygon(surf, hook,
                        [(cx - half_outer, y_base - tip_rise),
                         (cx - half_outer + 4, y_base - tip_rise - 2),
                         (cx - half_outer + 4, y_base - tip_rise + 1)])
    pygame.draw.polygon(surf, hook,
                        [(cx + half_outer, y_base - tip_rise),
                         (cx + half_outer - 4, y_base - tip_rise - 2),
                         (cx + half_outer - 4, y_base - tip_rise + 1)])
    # AA the upper edge so the curve stays smooth at small scale.
    _aa_polyline(surf, keyline, pts[1:-1])


def _eave_tang_inverted(surf, cx, y_base, half_w_body, overhang, depth,
                        roof_col, accent_col, tile_col, curl=0.7):
    """Same eave geometry mirrored vertically — for a hanging tō where the
    eave is seen from below."""
    overhang = max(overhang, 7)
    tip_rise = max(2, int(depth * (0.5 + curl)))
    centre_sag = max(1, depth // 3)
    half_outer = half_w_body + overhang
    pts = [
        (cx - half_outer,     y_base - depth + 1),
        (cx - half_outer,     y_base + tip_rise),
        (cx - half_outer + 3, y_base + tip_rise - 1),
        (cx - half_w_body,    y_base + centre_sag // 2),
        (cx,                  y_base - 1 + centre_sag),
        (cx + half_w_body,    y_base + centre_sag // 2),
        (cx + half_outer - 3, y_base + tip_rise - 1),
        (cx + half_outer,     y_base + tip_rise),
        (cx + half_outer,     y_base - depth + 1),
    ]
    pygame.draw.polygon(surf, _shade(roof_col, -55), pts)
    body_pts = [(p[0], p[1] + 1) if p[1] <= y_base else p for p in pts]
    pygame.draw.polygon(surf, roof_col, body_pts)
    keyline = _shade(roof_col, -75)
    pygame.draw.line(surf, keyline,
                     (cx - half_outer + 1, y_base - depth + 1),
                     (cx + half_outer - 1, y_base - depth + 1), 1)
    _tile_hatch(surf, cx - half_outer + 4, y_base + tip_rise - 2,
                cx + half_outer - 4, y_base + tip_rise - 2,
                tile_col, step=3)
    pygame.draw.line(surf, accent_col,
                     (cx - half_w_body + 1, y_base + 1),
                     (cx + half_w_body - 1, y_base + 1), 1)
    hook = _shade(roof_col, 30)
    pygame.draw.polygon(surf, hook,
                        [(cx - half_outer, y_base + tip_rise),
                         (cx - half_outer + 4, y_base + tip_rise + 2),
                         (cx - half_outer + 4, y_base + tip_rise - 1)])
    pygame.draw.polygon(surf, hook,
                        [(cx + half_outer, y_base + tip_rise),
                         (cx + half_outer - 4, y_base + tip_rise + 2),
                         (cx + half_outer - 4, y_base + tip_rise - 1)])
    _aa_polyline(surf, keyline, pts[1:-1])


# ── Per-candidate cache ────────────────────────────────────────────────────
#
# Each candidate composites its pillar pair into a per-(seed, palette-id)
# SRCALPHA bitmap once, then blits — clean curves at game scale and no
# expensive eave re-tracing every frame.

_PILLAR_CACHE: dict = {}


def _palette_key(palette):
    # Compact palette identity so cache hits across frames with same biome
    # bucket; pulling only a handful of keys keeps the dict cheap.
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
        # Compose into a transparent canvas the size of the whole tile so
        # we can blit at (0,0). Allocating a screen-sized SRCALPHA per cache
        # miss is fine because the harness renders a fixed handful of tiles.
        bitmap = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        draw_fn(bitmap, top_rect, bot_rect, palette, seed)
        _PILLAR_CACHE[key] = bitmap
    surf.blit(bitmap, (0, 0))


# ── 1. Hōryū-ji Tō ─────────────────────────────────────────────────────────
#
# Bottom = full 5-storey tō rooted on the ground, sōrin pointing UP.
# Top = same tō MIRRORED from the ceiling, sōrin tip pointing DOWN into
# the gap. Identifying cues at scale: cedar-dark vertical column posts
# framing white plaster panels + bronze sōrin with stacked disks.
#
# Reference: https://en.wikipedia.org/wiki/H%C5%8Dry%C5%AB-ji

def _draw_horyuji_to(surf, cx, top_y, bot_y, base_w, palette, *,
                    tier_count=5, finial_h=34, sorin_up=True):
    """Stack of `tier_count` cedar-and-plaster storeys with wide flat eaves.

    `top_y`/`bot_y` define the tier-stack envelope (excluding the finial).
    When `sorin_up` is True the sōrin sits ABOVE top_y (Japanese tō);
    when False, the finial points DOWN past bot_y (mirrored hanging tō)."""
    cedar = _cedar(palette)
    plaster = _plaster(palette)
    roof = _shade(cedar, -10)
    accent = _bronze(palette)
    tile_col = _shade(palette['stone_dark'], -15)

    total_h = bot_y - top_y
    if total_h < 10:
        return
    # Tier height weighted slightly toward base — true to a real tō where
    # the first storey is the tallest.
    weights = [1.0 - 0.06 * i for i in range(tier_count)]
    wsum = sum(weights)
    tier_heights = [max(8, int(total_h * w / wsum)) for w in weights]
    body_widths = [max(12, int(base_w * (0.92 ** i)))
                   for i in range(tier_count)]

    # Build tiers ground-up; first tier sits at bot_y, last tier ends near top_y.
    y_cursor = bot_y
    tier_tops = []
    for i in range(tier_count):
        th = tier_heights[i]
        bw = body_widths[i]
        wall_top = y_cursor - th
        if wall_top < top_y - 1:
            break
        tier_tops.append((wall_top, bw, th))
        # Cedar column frame + plaster infill panel — what makes Hōryū-ji
        # read as cedar-wood, not generic Chinese cinnabar.
        x_l = cx - bw // 2
        # Outer cedar shadow.
        pygame.draw.rect(surf, _shade(cedar, -25),
                         (x_l, wall_top, bw, th))
        # Plaster infill leaves the leftmost + rightmost 3 px as cedar columns.
        if bw > 8 and th > 4:
            pygame.draw.rect(surf, plaster,
                             (x_l + 3, wall_top + 1, bw - 6, th - 1))
        # Vertical cedar columns at corners (already covered) + one mid post.
        pygame.draw.rect(surf, cedar, (x_l, wall_top, 3, th))
        pygame.draw.rect(surf, cedar, (x_l + bw - 3, wall_top, 3, th))
        if bw > 18:
            mid_x = cx - 1
            pygame.draw.rect(surf, cedar, (mid_x, wall_top, 2, th))
        # Horizontal cedar beam mid-tier — adds the Hōryū-ji wood-grid cue.
        if th > 10:
            beam_y = wall_top + th // 2
            pygame.draw.line(surf, cedar,
                             (x_l + 1, beam_y), (x_l + bw - 2, beam_y), 1)
        # Lit-rim niche painted on each storey.
        if th > 9 and bw > 12:
            nw = min(8, bw - 8)
            nh = min(8, th - 5)
            _lit_niche(surf, cx, wall_top + 2, nw, nh, palette)
        # Wide flat eave with corner up-curl. Eave overhang is what tells the
        # player "tō" — wider than the wall and only gently curled.
        overhang = max(10, 13 - i)
        depth = 5
        _eave_tang_curl(surf, cx, wall_top, bw // 2, overhang, depth,
                        roof, accent, tile_col, curl=0.40)
        y_cursor = wall_top - depth + 1

    if not tier_tops:
        return

    # Bronze sōrin — 9-disk stack on a needle + flame jewel. Mirrored when the
    # tō hangs from the ceiling.
    top_wall_y = tier_tops[-1][0]
    base_y = top_wall_y - 2 if sorin_up else bot_y + 2
    dir_sign = -1 if sorin_up else 1
    dark_pal = palette['stone_dark']
    bright = _shade(accent, 40)
    # Lotus pad base.
    pygame.draw.ellipse(surf, dark_pal, (cx - 6, base_y + dir_sign * 1, 12, 5))
    pygame.draw.ellipse(surf, accent, (cx - 5, base_y + dir_sign * 1 + 1, 10, 3))
    # Central needle.
    needle_tip = base_y + dir_sign * (finial_h - 4)
    pygame.draw.line(surf, dark_pal,
                     (cx - 1, base_y + dir_sign * 4),
                     (cx - 1, needle_tip), 2)
    pygame.draw.line(surf, accent,
                     (cx, base_y + dir_sign * 4),
                     (cx, needle_tip), 1)
    # 9 disks tapering toward the flame.
    disks = 9
    for k in range(disks):
        t = k / max(1, disks - 1)
        ry = base_y + dir_sign * (5 + int(t * (finial_h - 10)))
        rw = max(2, 7 - k // 2)
        pygame.draw.ellipse(surf, dark_pal,
                            (cx - rw - 1, ry - 1, rw * 2 + 2, 3))
        pygame.draw.ellipse(surf, accent,
                            (cx - rw, ry, rw * 2, 2))
    # Flame jewel orb + tongue.
    tip_y = base_y + dir_sign * finial_h
    pygame.draw.circle(surf, dark_pal, (cx, tip_y), 3)
    pygame.draw.circle(surf, accent, (cx, tip_y), 2)
    flame = [(cx, tip_y + dir_sign * 5),
             (cx - 2, tip_y + dir_sign * 1),
             (cx + 2, tip_y + dir_sign * 1)]
    pygame.draw.polygon(surf, bright, flame)


def _draw_horyuji(surf, top_rect, bot_rect, palette, seed):
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2
    tier_count = rng.choice([4, 5, 5])

    # Ground tō.
    if bot_rect.height > 50:
        plinth_h = 8
        plinth_w = int(bot_rect.width * 1.16)
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -10),
                         (bcx - plinth_w // 2, bot_rect.bottom - plinth_h,
                          plinth_w, plinth_h))
        pygame.draw.rect(surf, palette['stone_light'],
                         (bcx - plinth_w // 2, bot_rect.bottom - plinth_h,
                          plinth_w, 2))
        finial_h = 36
        envelope_top = bot_rect.y
        envelope_bot = bot_rect.bottom - plinth_h
        _draw_horyuji_to(surf, bcx,
                         envelope_top + finial_h, envelope_bot,
                         int(bot_rect.width * 0.84), palette,
                         tier_count=tier_count, finial_h=finial_h,
                         sorin_up=True)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 6, 14, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 7, seed=seed)

    # Ceiling-mounted tō (mirrored, sōrin pointing down into the gap).
    if top_rect.height > 50:
        plinth_h = 6
        plinth_w = int(top_rect.width * 1.14)
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -10),
                         (tcx - plinth_w // 2, top_rect.y, plinth_w, plinth_h))
        pygame.draw.rect(surf, palette['stone_light'],
                         (tcx - plinth_w // 2, top_rect.y + plinth_h - 1,
                          plinth_w, 1))
        # Hanging tō envelope spans from just below the plinth down to
        # `bot_y` (inside top_rect); finial then drops PAST bot_y into the
        # gap so the spire pokes out toward the player.
        finial_h = 28
        envelope_top = top_rect.y + plinth_h
        envelope_bot = top_rect.bottom - finial_h
        # Build the tō with smaller tier count for the hanging half so the
        # silhouette doesn't visually outweigh the ground tō.
        _draw_horyuji_to(surf, tcx,
                         envelope_top, envelope_bot,
                         int(top_rect.width * 0.84), palette,
                         tier_count=max(3, tier_count - 1),
                         finial_h=finial_h, sorin_up=False)
        # Hanging moss off the lowest eave-tip area for warmth.
        for off in (-14, -4, 4, 14):
            draw_moss_strand(surf, tcx + off, envelope_bot,
                             6 + abs(off) % 4, palette,
                             jitter_seed=seed + off)


def candidate_horyuji(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('horyuji', _draw_horyuji, surf, top_rect, bot_rect,
                 palette, seed)


# ── 2. Shwedagon Gold Stupa ────────────────────────────────────────────────
#
# Iconic Burmese stupa: receding square + octagonal terraces, bell dome,
# polygonal floral-edged tiers, hti umbrella stack, diamond bud. We draw
# a stack of widening trapezoidal terraces, then a tall bell with a hti
# spire tapering through 7 gold rings.
#
# Reference: https://en.wikipedia.org/wiki/Shwedagon_Pagoda

def _draw_shwedagon_bell(surf, cx, base_y, palette, *,
                         body_w=56, total_h=180):
    """Multi-tier terraced base + bell + hti spire + diamond bud.

    `base_y` is the ground line; `total_h` is the silhouette from ground
    to the diamond bud."""
    gold = _gold_bright(palette)
    gold_d = _gold_deep(palette)
    dark = _shade(palette['stone_dark'], -10)
    accent_red = _mix(palette['stone_dark'], (148, 50, 32), 0.62)
    tile = _shade(gold_d, -25)

    # Vertical budget split: ~36% terraces, ~22% bell, ~42% hti + bud.
    terrace_h = max(28, int(total_h * 0.36))
    bell_h = max(20, int(total_h * 0.22))
    hti_h = total_h - terrace_h - bell_h

    # ── Terraces (square + octagonal) ──────────────────────────────────
    n_terraces = 4
    t_step = terrace_h // n_terraces
    widest = int(body_w * 1.10)
    narrowest = int(body_w * 0.70)
    for i in range(n_terraces):
        t = i / max(1, n_terraces - 1)
        sw = int(widest + (narrowest - widest) * t)
        sy = base_y - terrace_h + i * t_step
        # Edge shadow.
        pygame.draw.rect(surf, _shade(gold_d, -50),
                         (cx - sw // 2, sy, sw, t_step))
        # Face fill.
        pygame.draw.rect(surf, gold_d,
                         (cx - sw // 2 + 1, sy + 1, sw - 2, t_step - 2))
        # Top highlight strip.
        pygame.draw.rect(surf, gold,
                         (cx - sw // 2 + 2, sy + 1, sw - 4, 1))
        # Red lacquer accent band on the top edge of every odd terrace.
        if i % 2 == 1:
            pygame.draw.rect(surf, accent_red,
                             (cx - sw // 2 + 2, sy + t_step - 2,
                              sw - 4, 1))
        # Tile-hatch row along the top edge — terrace-mould detail.
        _tile_hatch(surf, cx - sw // 2 + 3, sy + 1,
                    cx + sw // 2 - 3, sy + 1, tile, step=3)
        # Lit-rim niche on the largest two terraces for shrine-windows.
        if i < 2 and sw > 22 and t_step > 8:
            _lit_niche(surf, cx, sy + 2,
                       min(8, sw - 12), min(6, t_step - 4), palette)

    # ── Bell dome (anda) ───────────────────────────────────────────────
    bell_top_y = base_y - terrace_h - bell_h
    bell_bottom_y = base_y - terrace_h
    bell_w = int(body_w * 0.78)
    bell_rect = pygame.Rect(cx - bell_w // 2, bell_top_y,
                            bell_w, bell_h * 2)
    # Outer dark ring + gilded body.
    pygame.draw.ellipse(surf, dark, bell_rect)
    pygame.draw.ellipse(surf, gold_d, bell_rect.inflate(-2, -2))
    # Brighter gold front face.
    pygame.draw.ellipse(surf, gold,
                        (bell_rect.x + 2, bell_rect.y + 2,
                         bell_rect.w - 4, bell_rect.h - 6))
    # Mask off the bottom half so it sits flat on the terrace.
    pygame.draw.rect(surf, gold_d,
                     (cx - bell_w // 2 - 1, bell_bottom_y - 1,
                      bell_w + 2, bell_h))
    # Lower belly band — red lacquer cinch.
    pygame.draw.rect(surf, accent_red,
                     (cx - bell_w // 2 + 3, bell_bottom_y - 3,
                      bell_w - 6, 2))
    # AA the dome's upper arc for smooth silhouette.
    arc_pts = []
    for k in range(13):
        t = k / 12
        ang = math.pi + t * math.pi
        px = cx + math.cos(ang) * bell_w * 0.5
        py = bell_top_y + bell_h - math.sin(ang) * bell_h
        if py <= bell_bottom_y:
            arc_pts.append((int(px), int(py)))
    if len(arc_pts) >= 2:
        _aa_polyline(surf, dark, arc_pts)

    # ── Hti spire — ringed cone tapering up to diamond bud ─────────────
    spire_base_y = bell_top_y + 4
    spire_top_y = spire_base_y - hti_h + 10
    spire_pole = max(spire_top_y, bell_top_y - hti_h + 12)
    # Cone backbone.
    pygame.draw.polygon(surf, dark,
                        [(cx - 6, spire_base_y),
                         (cx + 6, spire_base_y),
                         (cx + 1, spire_pole),
                         (cx - 1, spire_pole)])
    pygame.draw.polygon(surf, gold_d,
                        [(cx - 5, spire_base_y - 1),
                         (cx + 5, spire_base_y - 1),
                         (cx, spire_pole + 1)])
    # 7 hti rings — wider near base, tighter near tip.
    rings = 7
    ring_top = spire_pole + 2
    ring_bot = spire_base_y - 2
    for k in range(rings):
        t = k / max(1, rings - 1)
        ry = int(ring_bot + (ring_top - ring_bot) * t)
        rw = max(2, 7 - k)
        pygame.draw.line(surf, dark,
                         (cx - rw, ry + 1), (cx + rw, ry + 1), 1)
        pygame.draw.line(surf, gold,
                         (cx - rw, ry), (cx + rw, ry), 1)
    # Diamond bud (sein bu) — crystalline orb on the tip with a tiny flame.
    bud_y = spire_pole - 4
    pygame.draw.circle(surf, dark, (cx, bud_y), 4)
    pygame.draw.circle(surf, gold, (cx, bud_y), 3)
    pygame.draw.circle(surf, _shade(gold, 60), (cx - 1, bud_y - 1), 1)
    # 4-point diamond glints.
    for ang in (0, math.pi / 2, math.pi, math.pi * 1.5):
        gx = cx + int(math.cos(ang) * 5)
        gy = bud_y + int(math.sin(ang) * 5)
        pygame.draw.line(surf, _shade(gold, 80),
                         (cx, bud_y), (gx, gy), 1)
    # Flag-vane right above the bud.
    pygame.draw.rect(surf, accent_red, (cx - 1, bud_y - 8, 5, 3))


def _draw_shwedagon(surf, top_rect, bot_rect, palette, seed):
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2
    gold = _gold_bright(palette)
    gold_d = _gold_deep(palette)
    dark = _shade(palette['stone_dark'], -10)
    accent_red = _mix(palette['stone_dark'], (148, 50, 32), 0.62)

    # Ground stupa — full Shwedagon silhouette inside bot_rect.
    if bot_rect.height > 80:
        body_w = int(bot_rect.width * 1.05)
        _draw_shwedagon_bell(surf, bcx, bot_rect.bottom,
                             palette,
                             body_w=body_w,
                             total_h=min(bot_rect.height, 230))
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 6, 14, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 7, seed=seed)

    # Ceiling — hanging gold votive bell pendant with hti chandelier rings.
    if top_rect.height > 40:
        # Anchor block under the ceiling.
        anchor_w = int(top_rect.width * 1.18)
        anchor_h = 8
        pygame.draw.rect(surf, dark,
                         (tcx - anchor_w // 2, top_rect.y, anchor_w, anchor_h))
        pygame.draw.rect(surf, gold_d,
                         (tcx - anchor_w // 2 + 1, top_rect.y + 1,
                          anchor_w - 2, anchor_h - 1))
        pygame.draw.rect(surf, gold,
                         (tcx - anchor_w // 2 + 2, top_rect.y + 1,
                          anchor_w - 4, 1))
        # Suspension chain — thicker rope + larger interlocking gold links so
        # the pendant reads as hanging, not floating-bell-with-stick. Chain
        # links alternate vertical/horizontal so the eye reads a real chain.
        chain_top = top_rect.y + anchor_h
        chain_bot = min(top_rect.bottom - 36, top_rect.y + anchor_h + 22)
        pygame.draw.line(surf, dark, (tcx, chain_top), (tcx, chain_bot), 3)
        pygame.draw.line(surf, _shade(gold, -25), (tcx - 1, chain_top),
                         (tcx - 1, chain_bot), 1)
        for i, cy in enumerate(range(chain_top + 2, chain_bot, 5)):
            if i % 2 == 0:
                pygame.draw.ellipse(surf, dark, (tcx - 3, cy - 1, 6, 4))
                pygame.draw.ellipse(surf, gold, (tcx - 2, cy, 4, 2))
            else:
                pygame.draw.ellipse(surf, dark, (tcx - 2, cy - 2, 4, 5))
                pygame.draw.ellipse(surf, gold, (tcx - 1, cy - 1, 2, 3))
        # Inverted hti rings — fan WIDER and ADD MORE rings so the chandelier
        # reads as the umbrella-stack ornament instead of a single bar. Step
        # widens faster than round 1 (rw = 4 + k * 2 vs 3 + k).
        ring_top_y = chain_bot + 2
        rings = rng.choice([6, 7, 8])
        for k in range(rings):
            t = k / max(1, rings - 1)
            ry = ring_top_y + int(t * 20)
            rw = 4 + k * 2
            # Dark shadow rim then gold lip — every other ring gets a small
            # bead at each tip for the umbrella-spoke cue.
            pygame.draw.line(surf, dark,
                             (tcx - rw, ry + 1), (tcx + rw, ry + 1), 1)
            pygame.draw.line(surf, gold,
                             (tcx - rw, ry), (tcx + rw, ry), 1)
            if k % 2 == 1 and rw > 5:
                pygame.draw.circle(surf, _shade(gold, 50), (tcx - rw, ry), 1)
                pygame.draw.circle(surf, _shade(gold, 50), (tcx + rw, ry), 1)
        # Inverted bell pendant — only the LOWER half of an ellipse is drawn
        # so the bell reads as a hanging dome opening downward. Built as a
        # closed fan polygon (arc + flat mouth) because pygame can't natively
        # clip an ellipse mid-shape, and a full-ellipse + rect-mask approach
        # would paint a flat band over the sky gradient behind the cache.
        bell_top = ring_top_y + 16
        bell_w = int(top_rect.width * 0.78)
        bell_h = 22
        steps = 17
        fan_arc = []
        for k in range(steps + 1):
            t = k / steps
            ang = t * math.pi  # 0 → pi sweeps the lower half clockwise.
            fx = tcx + math.cos(ang) * bell_w * 0.5
            fy = bell_top + math.sin(ang) * bell_h
            fan_arc.append((int(fx), int(fy)))
        fan_dark = [(tcx + bell_w // 2, bell_top),
                    *fan_arc,
                    (tcx - bell_w // 2, bell_top)]
        pygame.draw.polygon(surf, dark, fan_dark)
        fan_gold = []
        for k in range(steps + 1):
            t = k / steps
            ang = t * math.pi
            fx = tcx + math.cos(ang) * (bell_w * 0.5 - 1.5)
            fy = bell_top + math.sin(ang) * (bell_h - 1.5)
            fan_gold.append((int(fx), int(fy)))
        fan_gold = [(tcx + bell_w // 2 - 1, bell_top + 1),
                    *fan_gold,
                    (tcx - bell_w // 2 + 1, bell_top + 1)]
        pygame.draw.polygon(surf, gold_d, fan_gold)
        _aa_polyline(surf, dark, fan_arc)
        # Lower rim with red lacquer band.
        pygame.draw.rect(surf, accent_red,
                         (tcx - bell_w // 2 + 3, bell_top + 1,
                          bell_w - 6, 2))
        # Diamond bud dangles below.
        bud_y = bell_top + 8
        pygame.draw.circle(surf, dark, (tcx, bud_y), 4)
        pygame.draw.circle(surf, gold, (tcx, bud_y), 3)
        for ang in (0, math.pi / 2, math.pi, math.pi * 1.5):
            gx = tcx + int(math.cos(ang) * 5)
            gy = bud_y + int(math.sin(ang) * 5)
            pygame.draw.line(surf, _shade(gold, 80),
                             (tcx, bud_y), (gx, gy), 1)


def _palette_sky_band(palette, top_rect):
    """Approximate sky colour behind the top-rect so we can mask shapes that
    should appear cut by the gap edge — keeps the chandelier cropped without
    relying on the live sky surface."""
    return _mix(palette['sky_top'], palette['sky_horizon'],
                top_rect.bottom / 400.0)


def candidate_shwedagon(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('shwedagon', _draw_shwedagon, surf, top_rect, bot_rect,
                 palette, seed)


# ── 3. Boudhanath Eye Stupa ────────────────────────────────────────────────
#
# Bottom = whitewashed hemispherical dome on a square stepped base, with
# the iconic painted Buddha eyes on the harmika cube + ūrṇā curl + nose-
# glyph + 13-step gold pyramid + sun-moon-flame finial.
# Top = prayer-flag canopy strung from two carved anchor stones across
# the gap ceiling.
#
# Reference: https://en.wikipedia.org/wiki/Boudhanath

def _buddha_eye(surf, cx, cy, palette, scale=1.0):
    """The iconic Boudhanath Buddha eye glyph — heavy painted brow, almond
    eyeball with a tall vertical pupil, dot ūrṇā above + the question-mark
    nose-glyph centre. All proportions match the actual harmika painting."""
    w = int(8 * scale)
    h = int(4 * scale)
    white = _stupa_white(palette)
    blue = _lapis(palette)
    dark = palette['stone_dark']
    # Almond eyeball outline (open at the top).
    eye_rect = pygame.Rect(cx - w, cy - h // 2, w * 2, h)
    pygame.draw.ellipse(surf, white, eye_rect)
    pygame.draw.ellipse(surf, dark, eye_rect, 1)
    # Heavy painted brow — dark crescent above the eye.
    brow_pts = [(cx - w, cy - h // 2),
                (cx - w + 2, cy - h),
                (cx, cy - h - 1),
                (cx + w - 2, cy - h),
                (cx + w, cy - h // 2)]
    pygame.draw.polygon(surf, dark, brow_pts)
    pygame.draw.lines(surf, blue, False, brow_pts, 1)
    # Vertical pupil (the Boudhanath eye is famously narrow + tall).
    pygame.draw.rect(surf, blue,
                     (cx - max(1, w // 4), cy - h // 2 + 1,
                      max(1, w // 2), h - 2))
    pygame.draw.rect(surf, dark, (cx - 1, cy - h // 2 + 1, 2, h - 2))


def _draw_boudhanath_stupa(surf, cx, base_y, palette, *,
                           body_w=58, total_h=190):
    """Square stepped base + dome + harmika with Buddha-eyes + 13-step gold
    pyramid + sun-moon-flame jewel."""
    white = _stupa_white(palette)
    edge = _shade(white, -55)
    shadow = _shade(white, -28)
    saffron = _saffron(palette)
    gold = _gold_deep(palette)
    bright_gold = _gold_bright(palette)
    dark = palette['stone_dark']

    # Budget the silhouette: 30% base, 30% dome, 12% harmika, 28% spire.
    base_h = max(22, int(total_h * 0.30))
    dome_h = max(20, int(total_h * 0.30))
    harm_h = max(8, int(total_h * 0.12))
    spire_h = total_h - base_h - dome_h - harm_h

    # Square stepped base — 3 receding tiers wider at the bottom.
    n_steps = 3
    step_h = base_h // n_steps
    widest = int(body_w * 1.18)
    narrowest = int(body_w * 0.88)
    for i in range(n_steps):
        t = i / max(1, n_steps - 1)
        sw = int(widest + (narrowest - widest) * t)
        sy = base_y - base_h + i * step_h
        pygame.draw.rect(surf, edge, (cx - sw // 2, sy, sw, step_h))
        pygame.draw.rect(surf, white,
                         (cx - sw // 2 + 1, sy + 1, sw - 2, step_h - 2))
        # Saffron edge band.
        pygame.draw.rect(surf, saffron,
                         (cx - sw // 2 + 2, sy + step_h - 2,
                          sw - 4, 1))
        # Right edge cool shadow.
        pygame.draw.rect(surf, shadow,
                         (cx + sw // 2 - 2, sy + 1, 2, step_h - 2))
        # Lit-rim niche row on the widest two steps.
        if i < 2 and sw > 24:
            for off in (-int(sw * 0.32), 0, int(sw * 0.32)):
                _lit_niche(surf, cx + off, sy + 2,
                           min(6, sw // 6), min(5, step_h - 4), palette)

    # Hemispherical dome (anda).
    dome_top_step_y = base_y - base_h
    dome_w = int(body_w * 1.00)
    dome_rect = pygame.Rect(cx - dome_w // 2, dome_top_step_y - dome_h,
                            dome_w, dome_h * 2)
    pygame.draw.ellipse(surf, edge, dome_rect)
    pygame.draw.ellipse(surf, white, dome_rect.inflate(-2, -2))
    # Cool right-side shadow.
    pygame.draw.arc(surf, shadow, dome_rect.inflate(-2, -2),
                    math.pi * 1.55, math.pi * 1.95, 1)
    # Flatten the bottom on the top step.
    pygame.draw.rect(surf, edge,
                     (cx - dome_w // 2, dome_top_step_y - 1, dome_w, 2))
    # Saffron belly stripe.
    belly_y = dome_top_step_y - 8
    pygame.draw.rect(surf, saffron,
                     (cx - dome_w // 2 + 4, belly_y, dome_w - 8, 2))
    # AA the upper arc for smooth silhouette.
    arc_pts = []
    for k in range(13):
        t = k / 12
        ang = math.pi + t * math.pi
        px = cx + math.cos(ang) * dome_w * 0.5
        py = dome_top_step_y - math.sin(ang) * dome_h
        if py <= dome_top_step_y:
            arc_pts.append((int(px), int(py)))
    if len(arc_pts) >= 2:
        _aa_polyline(surf, edge, arc_pts)

    # Harmika cube — square tower above the dome with painted Buddha eyes.
    harm_w = int(body_w * 0.72)
    harm_top_y = dome_top_step_y - dome_h - harm_h + 4
    pygame.draw.rect(surf, edge, (cx - harm_w // 2, harm_top_y, harm_w, harm_h))
    pygame.draw.rect(surf, white,
                     (cx - harm_w // 2 + 1, harm_top_y + 1,
                      harm_w - 2, harm_h - 2))
    pygame.draw.rect(surf, shadow,
                     (cx + harm_w // 2 - 2, harm_top_y + 1,
                      2, harm_h - 2))
    # Buddha eyes — pair painted across the harmika face.
    eye_y = harm_top_y + harm_h // 2
    if harm_w >= 22:
        _buddha_eye(surf, cx - harm_w // 4, eye_y, palette, scale=0.85)
        _buddha_eye(surf, cx + harm_w // 4, eye_y, palette, scale=0.85)
        # Nose-glyph (the curl between/under the eyes) — Nepali numeral 1.
        pygame.draw.line(surf, dark, (cx, eye_y + 1), (cx, eye_y + 4), 1)
        pygame.draw.line(surf, dark, (cx - 1, eye_y + 4), (cx + 1, eye_y + 4), 1)
        pygame.draw.line(surf, dark, (cx, eye_y + 5),
                         (cx + 2, eye_y + 7), 1)
        # Ūrṇā curl — dot above the nose.
        pygame.draw.circle(surf, _lapis(palette), (cx, eye_y - 5), 1)

    # 13-step gold pyramid + sun-moon-flame.
    steps = 13
    step_yi = max(2, spire_h // (steps + 4))
    start_y = harm_top_y - 1
    for k in range(steps):
        sy = start_y - k * step_yi
        rw = max(2, 8 - (k * 6) // steps)
        pygame.draw.line(surf, _shade(gold, -25), (cx - rw, sy + 1),
                         (cx + rw, sy + 1), 1)
        pygame.draw.line(surf, gold, (cx - rw, sy), (cx + rw, sy), 1)
        if k == 0 or k == steps // 2 or k == steps - 1:
            pygame.draw.line(surf, bright_gold, (cx - rw, sy),
                             (cx + rw, sy), 1)
    spire_top = start_y - steps * step_yi
    # Lotus pad.
    pygame.draw.ellipse(surf, dark, (cx - 4, spire_top - 2, 8, 4))
    pygame.draw.ellipse(surf, gold, (cx - 3, spire_top - 1, 6, 3))
    # Moon crescent.
    pygame.draw.circle(surf, bright_gold, (cx, spire_top - 5), 3)
    pygame.draw.circle(surf, _mix(palette['stone_dark'],
                                  palette['stone_mid'], 0.4),
                       (cx + 1, spire_top - 5), 2)
    # Sun disc.
    pygame.draw.circle(surf, dark, (cx, spire_top - 9), 2)
    pygame.draw.circle(surf, bright_gold, (cx, spire_top - 9), 1)
    # Flame jewel tip.
    pygame.draw.polygon(surf, bright_gold,
                        [(cx, spire_top - 14),
                         (cx - 2, spire_top - 10),
                         (cx + 2, spire_top - 10)])


def _draw_boudhanath(surf, top_rect, bot_rect, palette, seed):
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    white = _stupa_white(palette)
    edge = _shade(white, -55)
    shadow = _shade(white, -28)
    saffron = _saffron(palette)
    gold = _gold_deep(palette)

    if bot_rect.height > 70:
        body_w = int(bot_rect.width * 1.00)
        _draw_boudhanath_stupa(surf, bcx, bot_rect.bottom, palette,
                               body_w=body_w,
                               total_h=min(bot_rect.height, 240))
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 8, 14, palette, seed=seed)

    if top_rect.height > 16:
        # Two carved anchor stones at the upper corners — short whitewashed
        # posts the prayer-flag lines hang from.
        for ax in (top_rect.x + 7, top_rect.x + top_rect.width - 7):
            stone_h = min(top_rect.height, 22)
            stone_top = top_rect.bottom - stone_h
            pygame.draw.rect(surf, edge, (ax - 8, stone_top, 16, stone_h))
            pygame.draw.rect(surf, white,
                             (ax - 7, stone_top + 1, 14, stone_h - 2))
            pygame.draw.rect(surf, shadow,
                             (ax + 6, stone_top + 1, 2, stone_h - 2))
            pygame.draw.rect(surf, saffron,
                             (ax - 6, top_rect.bottom - 5, 12, 2))
            pygame.draw.rect(surf, gold,
                             (ax - 5, top_rect.bottom - 4, 10, 1))
        # Sagging prayer-flag strings — the canonical Boudhanath canopy.
        n_strings = rng.choice([3, 4])
        for k in range(n_strings):
            jitter = k * 4 - 4
            draw_prayer_flags(surf,
                              top_rect.x + 6 + jitter,
                              top_rect.bottom - 3,
                              top_rect.x + top_rect.width - 6 - jitter,
                              top_rect.bottom - 3,
                              n=7 + k)
        # Moss tipping the anchor stones.
        for off in (-3, 3):
            for ax in (top_rect.x + 7, top_rect.x + top_rect.width - 7):
                draw_moss_strand(surf, ax + off, top_rect.bottom - 2,
                                 9, palette, jitter_seed=seed + ax + off)


def candidate_boudhanath(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('boudhanath', _draw_boudhanath, surf, top_rect, bot_rect,
                 palette, seed)


# ── 4. Wat Arun Khmer Prang ────────────────────────────────────────────────
#
# Tall lobed corncob spire wrapped in pastel porcelain mosaic (pink, aqua,
# cream). Multi-tier square base. Kala-face brackets bend out of each
# tier; deva niches on the body. Top = mirrored prang sharing the palette.
#
# Reference: https://en.wikipedia.org/wiki/Wat_Arun

def _mosaic_lozenges(surf, x, y, w, h, palette, *, rng):
    """Scattered lozenge tiles in pastel-pink, aqua, cream — the porcelain
    mosaic skin of Wat Arun's prang. Lozenges sit on a 4-px row grid so the
    pattern reads as a hand-set mosaic at game scale, not coloured noise."""
    if w < 6 or h < 6:
        return
    cols = (_porcelain_pink(palette),
            _porcelain_aqua(palette),
            _porcelain_cream(palette))
    rows = max(1, h // 4)
    cells = max(1, w // 4)
    for r in range(rows):
        for c in range(cells):
            tx = x + c * 4
            ty = y + r * 4
            ci = rng.randrange(3)
            col = cols[ci]
            # Lozenge: small diamond every other cell so the row stays open.
            if (r + c) % 2 == 0:
                pygame.draw.polygon(surf, col,
                                    [(tx + 2, ty), (tx + 3, ty + 2),
                                     (tx + 2, ty + 3), (tx + 1, ty + 2)])
            else:
                pygame.draw.rect(surf, col, (tx + 1, ty + 1, 2, 2))


def _prang_corncob(surf, cx, base_y, tip_y, palette, *, w=46, rng):
    """The Khmer prang's signature corncob spire — a tall lobed silhouette
    drawn as a stack of horizontal "rings" of decreasing width with paired
    lobes on the left/right at each ring. Wrapped in mosaic and capped with
    a 7-tier diamond bud."""
    pink = _porcelain_pink(palette)
    aqua = _porcelain_aqua(palette)
    cream = _porcelain_cream(palette)
    dark = palette['stone_dark']
    gold = _gold_deep(palette)
    bright = _gold_bright(palette)
    spire_h = base_y - tip_y
    if spire_h < 20:
        return
    rings = max(8, spire_h // 8)

    # Centre silhouette: parabolic taper from w at base to ~4 at tip.
    centre_pts_l = []
    centre_pts_r = []
    for k in range(rings + 1):
        t = k / rings
        # Parabolic taper — fatter near base for the corncob bulge.
        local_w = int(w * (1 - t * t) * 0.5 + 2)
        ry = base_y - int(spire_h * t)
        centre_pts_l.append((cx - local_w, ry))
        centre_pts_r.append((cx + local_w, ry))

    body = list(reversed(centre_pts_l)) + centre_pts_r
    # Cream backing.
    pygame.draw.polygon(surf, cream, body)
    # Dark edge silhouette.
    _aa_polyline(surf, _shade(dark, 10), body, closed=True)

    # Horizontal mosaic stripe rings — alternating pink/aqua.
    for k in range(rings):
        t = k / rings
        local_w = int(w * (1 - t * t) * 0.5 + 2)
        ry = base_y - int(spire_h * t)
        stripe_col = pink if k % 2 == 0 else aqua
        pygame.draw.line(surf, stripe_col,
                         (cx - local_w + 1, ry),
                         (cx + local_w - 1, ry), 1)
        # Tiny lozenge dot in cream at the centre of every 4th ring for tile
        # detail.
        if k % 4 == 1:
            pygame.draw.polygon(surf, cream,
                                [(cx, ry - 1), (cx + 1, ry),
                                 (cx, ry + 1), (cx - 1, ry)])

    # Lobed paired bumps — small pink/aqua bulges on alternate sides every
    # 3 rings.
    for k in range(0, rings, 3):
        t = k / rings
        local_w = int(w * (1 - t * t) * 0.5 + 2)
        ry = base_y - int(spire_h * t)
        bulge_col = aqua if k % 2 == 0 else pink
        pygame.draw.circle(surf, bulge_col, (cx - local_w - 1, ry), 1)
        pygame.draw.circle(surf, bulge_col, (cx + local_w + 1, ry), 1)

    # 7-tier diamond bud cap (Wat Arun's signature finial: lotus + crystal).
    bud_y = tip_y
    pygame.draw.polygon(surf, dark,
                        [(cx - 3, bud_y + 8),
                         (cx + 3, bud_y + 8),
                         (cx, bud_y - 6)])
    pygame.draw.polygon(surf, gold,
                        [(cx - 2, bud_y + 7),
                         (cx + 2, bud_y + 7),
                         (cx, bud_y - 5)])
    pygame.draw.circle(surf, bright, (cx, bud_y - 1), 2)


def _draw_wat_arun_prang(surf, cx, base_y, palette, *,
                        body_w=52, total_h=200, rng):
    """Multi-tier square base + corncob spire + porcelain mosaic skin."""
    pink = _porcelain_pink(palette)
    aqua = _porcelain_aqua(palette)
    cream = _porcelain_cream(palette)
    dark = palette['stone_dark']
    gold = _gold_deep(palette)
    # ~40% base tiers, ~60% corncob spire.
    base_h = max(28, int(total_h * 0.40))
    spire_h = total_h - base_h

    # Stepped square base — 3 receding tiers.
    n_tiers = 3
    tier_h = base_h // n_tiers
    widest = int(body_w * 1.20)
    narrowest = int(body_w * 0.86)
    for i in range(n_tiers):
        t = i / max(1, n_tiers - 1)
        tw = int(widest + (narrowest - widest) * t)
        ty = base_y - base_h + i * tier_h
        # Dark silhouette edge.
        pygame.draw.rect(surf, _shade(dark, 10),
                         (cx - tw // 2, ty, tw, tier_h))
        # Cream fill.
        pygame.draw.rect(surf, cream,
                         (cx - tw // 2 + 1, ty + 1, tw - 2, tier_h - 2))
        # Pink top frieze.
        pygame.draw.rect(surf, pink,
                         (cx - tw // 2 + 2, ty + 1, tw - 4, 2))
        # Aqua bottom band.
        pygame.draw.rect(surf, aqua,
                         (cx - tw // 2 + 2, ty + tier_h - 3, tw - 4, 2))
        # Mosaic patterning across the cream interior.
        _mosaic_lozenges(surf, cx - tw // 2 + 4, ty + 4,
                         tw - 8, tier_h - 7, palette, rng=rng)
        # Kala-face bracket on the front edge of each tier — a small dark
        # mascaron with eyes that pokes out the bottom front face.
        kala_y = ty + tier_h - 4
        pygame.draw.polygon(surf, dark,
                            [(cx - 5, kala_y),
                             (cx + 5, kala_y),
                             (cx + 3, kala_y + 3),
                             (cx - 3, kala_y + 3)])
        pygame.draw.rect(surf, _shade(gold, 20),
                         (cx - 2, kala_y + 1, 1, 1))
        pygame.draw.rect(surf, _shade(gold, 20),
                         (cx + 1, kala_y + 1, 1, 1))
        # Deva-niche on the widest base tier — a tall pink arch with the
        # rim-lit cue.
        if i == 0 and tw > 24:
            _lit_niche(surf, cx, ty + 4,
                       min(10, tw - 14), min(tier_h - 6, 9), palette)

    # Corncob spire.
    spire_base_y = base_y - base_h
    spire_tip_y = spire_base_y - spire_h
    _prang_corncob(surf, cx, spire_base_y, spire_tip_y, palette,
                   w=int(body_w * 0.92), rng=rng)


def _draw_wat_arun(surf, top_rect, bot_rect, palette, seed):
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2

    if bot_rect.height > 80:
        body_w = int(bot_rect.width * 1.05)
        _draw_wat_arun_prang(surf, bcx, bot_rect.bottom, palette,
                            body_w=body_w,
                            total_h=min(bot_rect.height, 250),
                            rng=rng)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 6, 14, palette, seed=seed)

    if top_rect.height > 60:
        # Hanging mirrored prang from the ceiling — same palette so the pair
        # reads as one continuous spire bracketing the gap.
        body_w = int(top_rect.width * 0.96)
        total_h = min(top_rect.height - 4, 160)
        # Build the same prang upside-down: pass an upside-down y math by
        # drawing into a temporary surface, then flipping.
        tmp = pygame.Surface((body_w * 2 + 12, total_h + 12), pygame.SRCALPHA)
        _draw_wat_arun_prang(tmp, tmp.get_width() // 2,
                             total_h + 4, palette,
                             body_w=body_w,
                             total_h=total_h,
                             rng=random.Random(seed + 17))
        flipped = pygame.transform.flip(tmp, False, True)
        surf.blit(flipped, (tcx - flipped.get_width() // 2,
                            top_rect.y))


def candidate_wat_arun(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('wat_arun', _draw_wat_arun, surf, top_rect, bot_rect,
                 palette, seed)


# ── 5. Songyue Twelve-Sided Brick Pagoda ───────────────────────────────────
#
# Northern Wei (523 CE), 12-sided plan, 15 densely stacked dwarf eaves,
# parabolic profile, lotus-bud finial. Reads totally distinct from a
# tiered Japanese tō because of the dense-eave stack and squat dome
# shoulders.
#
# Reference: https://en.wikipedia.org/wiki/Songyue_Pagoda

def _songyue_brick_band(surf, cx, y, w, h, palette):
    """Brick-row striations on the body — horizontal hatch every 4 px in
    alternating mortar/brick tones. What makes Songyue read as brick."""
    if w < 4 or h < 4:
        return
    brick = _terracotta(palette)
    mortar = _brick_mortar(palette)
    pygame.draw.rect(surf, brick, (cx - w // 2, y, w, h))
    # Right-edge cool shadow gives the cylinder its volume.
    pygame.draw.rect(surf, _shade(brick, -30),
                     (cx + w // 2 - 3, y, 3, h))
    # Left-edge highlight.
    pygame.draw.rect(surf, _shade(brick, 18),
                     (cx - w // 2, y, 2, h))
    # Horizontal mortar rows every 4 px — the brick-row cue.
    for k in range(y + 2, y + h, 4):
        pygame.draw.line(surf, mortar,
                         (cx - w // 2 + 2, k), (cx + w // 2 - 2, k), 1)


def _songyue_dwarf_eave(surf, cx, y, half_w, palette, depth=2):
    """A short cornice ledge — a thin dark lip with a brick-row highlight on
    top. We stack 15 of these to get Songyue's signature dense-eave column.
    Each eave overhangs the body slightly so the silhouette reads as a
    cascade of lips rather than a smooth cylinder."""
    overhang = 3
    brick = _terracotta(palette)
    dark = _shade(brick, -55)
    top_col = _shade(brick, 18)
    half_outer = half_w + overhang
    pygame.draw.rect(surf, dark,
                     (cx - half_outer, y, half_outer * 2, depth))
    pygame.draw.line(surf, top_col,
                     (cx - half_outer + 1, y),
                     (cx + half_outer - 1, y), 1)
    # Tiny corner-up nicks at each end so the lip reads cornice-like.
    pygame.draw.line(surf, top_col,
                     (cx - half_outer, y),
                     (cx - half_outer, y - 1), 1)
    pygame.draw.line(surf, top_col,
                     (cx + half_outer, y),
                     (cx + half_outer, y - 1), 1)


def _draw_songyue(surf, top_rect, bot_rect, palette, seed):
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2

    def draw_one(cx, base_y, top_y, body_w_base, dwarf_eaves=15):
        """A single Songyue silhouette: tall main storey + dense eave column
        + parabolic dome shoulder + lotus-bud finial."""
        total_h = base_y - top_y
        if total_h < 60:
            return
        # Budget: 32% main storey, 50% dense-eave column, 18% lotus bud.
        main_h = int(total_h * 0.32)
        eave_h = int(total_h * 0.50)
        bud_h = total_h - main_h - eave_h

        # Plinth.
        plinth_h = 6
        plinth_w = int(body_w_base * 1.10)
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -10),
                         (cx - plinth_w // 2, base_y - plinth_h,
                          plinth_w, plinth_h))
        pygame.draw.rect(surf, palette['stone_light'],
                         (cx - plinth_w // 2, base_y - plinth_h, plinth_w, 1))
        # Main storey — tall brick band with pointed-arch doorway niche.
        main_top = base_y - plinth_h - main_h
        _songyue_brick_band(surf, cx, main_top,
                            body_w_base, main_h, palette)
        # Pointed arch doorway niche — Songyue's signature opening shape.
        door_w = min(body_w_base - 16, 16)
        door_h = min(main_h - 6, 22)
        if door_w >= 8 and door_h >= 10:
            dx0 = cx - door_w // 2
            dy0 = main_top + main_h - door_h
            # Rectangular shaft.
            pygame.draw.rect(surf, _shade(palette['stone_dark'], -50),
                             (dx0, dy0 + door_h // 3, door_w, door_h - door_h // 3))
            # Triangular arch top.
            pygame.draw.polygon(surf, _shade(palette['stone_dark'], -50),
                                [(dx0, dy0 + door_h // 3),
                                 (dx0 + door_w // 2, dy0),
                                 (dx0 + door_w, dy0 + door_h // 3)])
            # Lit rim around the arch — sampled brightness as in _lit_niche.
            rim_alpha = 200 if _is_dark_sky(palette) else 80
            rim_col = _mix(palette['stone_accent'], (255, 215, 120), 0.78)
            rim_layer = pygame.Surface((door_w + 2, door_h + 2), pygame.SRCALPHA)
            pygame.draw.polygon(rim_layer, (*rim_col, rim_alpha),
                                [(1, door_h // 3 + 1),
                                 (door_w // 2 + 1, 1),
                                 (door_w + 1, door_h // 3 + 1),
                                 (door_w + 1, door_h + 1),
                                 (1, door_h + 1)], 1)
            surf.blit(rim_layer, (dx0 - 1, dy0 - 1))
            # Lotus motif at the apex.
            pygame.draw.circle(surf, _gold_deep(palette),
                               (dx0 + door_w // 2, dy0 + 2), 1)

        # Dense-eave column — `dwarf_eaves` cornices stacked tightly.
        # The body underneath gradually narrows so the eaves trace a
        # parabolic profile.
        eave_top_y = main_top - 1
        step = max(2, eave_h // dwarf_eaves)
        for k in range(dwarf_eaves):
            t = k / max(1, dwarf_eaves - 1)
            # Parabolic taper.
            local_w = int(body_w_base * (1 - 0.55 * (t ** 1.2)))
            ey = eave_top_y - k * step
            # Brick body band between eaves.
            _songyue_brick_band(surf, cx, ey - step + 1,
                                local_w, step - 1, palette)
            _songyue_dwarf_eave(surf, cx, ey - step + 1,
                                local_w // 2, palette, depth=2)
            # Small lit windows on every 3rd band so the body reads inhabited.
            if k % 3 == 1 and local_w > 14:
                _lit_niche(surf, cx, ey - step + 2,
                           min(4, local_w // 3), min(3, step - 2), palette)

        # Smooth dome shoulder topping the eave stack — short dark cap.
        cap_y = eave_top_y - dwarf_eaves * step
        cap_w = max(6, int(body_w_base * 0.30))
        cap_rect = pygame.Rect(cx - cap_w // 2, cap_y - 5, cap_w, 10)
        pygame.draw.ellipse(surf, _shade(_terracotta(palette), -30), cap_rect)
        pygame.draw.ellipse(surf, _terracotta(palette),
                            cap_rect.inflate(-2, -2))
        # Lotus-bud finial — Songyue's iconic crowning ornament.
        bud_base_y = cap_y - 4
        bud_tip_y = bud_base_y - max(8, bud_h - 4)
        gold = _gold_deep(palette)
        bright = _gold_bright(palette)
        dark = palette['stone_dark']
        # Lotus pad at the base of the bud.
        pygame.draw.ellipse(surf, dark,
                            (cx - 5, bud_base_y - 1, 10, 4))
        pygame.draw.ellipse(surf, gold,
                            (cx - 4, bud_base_y, 8, 2))
        # Pointed bud shape — tear-drop polygon.
        bud_pts = [(cx - 4, bud_base_y),
                   (cx - 2, bud_base_y - 6),
                   (cx, bud_tip_y),
                   (cx + 2, bud_base_y - 6),
                   (cx + 4, bud_base_y)]
        pygame.draw.polygon(surf, dark, bud_pts)
        bud_inner = [(cx - 3, bud_base_y),
                     (cx - 1, bud_base_y - 5),
                     (cx, bud_tip_y + 1),
                     (cx + 1, bud_base_y - 5),
                     (cx + 3, bud_base_y)]
        pygame.draw.polygon(surf, gold, bud_inner)
        # Tiny highlight on the bud's left flank.
        pygame.draw.line(surf, bright,
                         (cx - 1, bud_tip_y + 2),
                         (cx - 2, bud_base_y - 2), 1)
        # AA the bud outline for a smooth silhouette.
        _aa_polyline(surf, dark, bud_pts, closed=True)

    if bot_rect.height > 80:
        draw_one(bcx, bot_rect.bottom, bot_rect.y,
                 int(bot_rect.width * 1.00),
                 dwarf_eaves=15)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 6, 14, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 6, seed=seed)

    if top_rect.height > 60:
        # Twin Songyue from the ceiling — narrower silhouette so it reads as
        # a child of the main one, not a duplicate. Drawn upside down by
        # composing into a temp surface, then flipping vertically. The twin
        # uses 11 dwarf-eaves vs the main's 15 so the polygonal dense-eave
        # cue still reads while keeping the ceiling silhouette lighter.
        small_body_w = int(top_rect.width * 0.88)
        small_h = min(top_rect.height - 2, 150)
        tmp = pygame.Surface((small_body_w * 2 + 14, small_h + 8),
                             pygame.SRCALPHA)
        _draw_mini_songyue(tmp, tmp.get_width() // 2, small_h + 2, 2,
                           small_body_w, palette, dwarf_eaves=11)
        flipped = pygame.transform.flip(tmp, False, True)
        surf.blit(flipped, (tcx - flipped.get_width() // 2, top_rect.y))


def _draw_mini_songyue(surf, cx, base_y, top_y, body_w_base, palette,
                       dwarf_eaves=11):
    """Compact Songyue silhouette used for the ceiling twin — same DNA as
    the main draw_one but slimmer budget, callable from any surface so the
    flip-into-temp trick can mirror it."""
    total_h = base_y - top_y
    if total_h < 40:
        return
    main_h = int(total_h * 0.30)
    eave_h = int(total_h * 0.55)
    bud_h = total_h - main_h - eave_h

    plinth_h = 5
    plinth_w = int(body_w_base * 1.10)
    pygame.draw.rect(surf, _shade(palette['stone_dark'], -10),
                     (cx - plinth_w // 2, base_y - plinth_h,
                      plinth_w, plinth_h))
    pygame.draw.rect(surf, palette['stone_light'],
                     (cx - plinth_w // 2, base_y - plinth_h, plinth_w, 1))

    main_top = base_y - plinth_h - main_h
    _songyue_brick_band(surf, cx, main_top, body_w_base, main_h, palette)
    if body_w_base > 18 and main_h > 10:
        _lit_niche(surf, cx, main_top + 2,
                   min(6, body_w_base - 8), min(main_h - 4, 7), palette)

    eave_top_y = main_top - 1
    step = max(2, eave_h // dwarf_eaves)
    for k in range(dwarf_eaves):
        t = k / max(1, dwarf_eaves - 1)
        local_w = int(body_w_base * (1 - 0.55 * (t ** 1.2)))
        ey = eave_top_y - k * step
        _songyue_brick_band(surf, cx, ey - step + 1,
                            local_w, step - 1, palette)
        _songyue_dwarf_eave(surf, cx, ey - step + 1,
                            local_w // 2, palette, depth=2)

    cap_y = eave_top_y - dwarf_eaves * step
    cap_w = max(6, int(body_w_base * 0.30))
    cap_rect = pygame.Rect(cx - cap_w // 2, cap_y - 5, cap_w, 10)
    pygame.draw.ellipse(surf, _shade(_terracotta(palette), -30), cap_rect)
    pygame.draw.ellipse(surf, _terracotta(palette),
                        cap_rect.inflate(-2, -2))
    bud_base_y = cap_y - 4
    bud_tip_y = bud_base_y - max(6, bud_h - 4)
    gold = _gold_deep(palette)
    dark = palette['stone_dark']
    pygame.draw.ellipse(surf, dark, (cx - 4, bud_base_y - 1, 8, 3))
    pygame.draw.ellipse(surf, gold, (cx - 3, bud_base_y, 6, 2))
    bud_pts = [(cx - 3, bud_base_y),
               (cx - 1, bud_base_y - 5),
               (cx, bud_tip_y),
               (cx + 1, bud_base_y - 5),
               (cx + 3, bud_base_y)]
    pygame.draw.polygon(surf, dark, bud_pts)
    pygame.draw.polygon(surf, gold,
                        [(cx - 2, bud_base_y),
                         (cx, bud_tip_y + 1),
                         (cx + 2, bud_base_y)])


def candidate_songyue(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('songyue', _draw_songyue, surf, top_rect, bot_rect,
                 palette, seed)


# ── Registry ────────────────────────────────────────────────────────────────

CANDIDATES = {
    "horyuji":      candidate_horyuji,
    "shwedagon":    candidate_shwedagon,
    "boudhanath":   candidate_boudhanath,
    "wat_arun":     candidate_wat_arun,
    "songyue":      candidate_songyue,
}

CANDIDATE_BLURBS = {
    "horyuji":    "Hōryū-ji Tō — cedar columns + plaster panels, bronze sōrin",
    "shwedagon":  "Shwedagon — gold bell on octagonal terraces + hti rings",
    "boudhanath": "Boudhanath Eye Stupa — Buddha eyes + 13-step gold spire",
    "wat_arun":   "Wat Arun — pastel porcelain corncob prang + kala brackets",
    "songyue":    "Songyue — 12-sided terracotta brick + 15 dwarf-eaves",
}
