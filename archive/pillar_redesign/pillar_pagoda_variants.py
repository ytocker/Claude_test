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
    draw_side_shrub,
    draw_wuling_pine,
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


# Round 6 — palette anchors for the 5 new candidates. Each derives from
# stone_* so the day → night biome retint sweeps through; raw RGB targets
# are biased archetypes only.

def _ochre_wood(palette):
    # Fogong larch — warm ochre-brown body of the wooden pagoda, sitting
    # between cedar (Hōryū-ji dark) and terracotta. Brighter than _cedar so
    # the dougong bracket array reads as relief, not silhouette.
    return _mix(palette['stone_dark'], (172, 124, 70), 0.70)


def _ochre_wood_lit(palette):
    # Sun-side highlight on Fogong's larch face — needed for the lit/shadow
    # gradient so a column reads as a 3-D cylinder, not a flat panel.
    return _mix(palette['stone_light'], (218, 168, 102), 0.62)


def _ochre_wood_shadow(palette):
    return _mix(palette['stone_dark'], (98, 62, 32), 0.78)


def _white_plaster_warm(palette):
    # Warm white-clay plaster panels between Fogong's dougong rows — sits
    # one beat warmer than Hōryū-ji's plaster so the two ochre/wood pagodas
    # read distinct side by side.
    return _mix(palette['stone_light'], (244, 232, 206), 0.62)


def _iron_brown(palette):
    # Kaifeng's glazed brown iron tile — derived from stone_dark with the
    # canonical iron-brown bias. Dark enough to read against any sky.
    return _mix(palette['stone_dark'], (118, 68, 44), 0.80)


def _iron_brown_lit(palette):
    return _mix(palette['stone_mid'], (172, 110, 70), 0.70)


def _iron_brown_shadow(palette):
    return _mix(palette['stone_dark'], (62, 32, 18), 0.86)


def _tile_gloss(palette):
    # Per-tile gloss highlight on the iron pagoda's glazed ceramic. A warm
    # cream so each tile catches a 1-px specular even at night.
    return _mix(palette['stone_light'], (236, 198, 130), 0.55)


def _vn_tile_red(palette):
    # Vietnamese curved roof-tile orange-red on the One Pillar pagoda's
    # pavilion. Warm enough to pop against the lotus-pond aqua.
    return _mix(palette['stone_dark'], (188, 96, 58), 0.72)


def _vn_tile_red_lit(palette):
    return _mix(palette['stone_accent'], (228, 140, 84), 0.70)


def _lotus_pink(palette):
    # Pink lotus-petal column-base for One Pillar — anchored in stone_light
    # with a touch of horizon so dusk/sunset retints carry through warmly.
    return _mix(palette['stone_light'],
                _mix(palette['horizon'], (244, 188, 196), 0.62), 0.65)


def _lotus_pink_deep(palette):
    return _mix(palette['stone_mid'],
                _mix(palette['horizon'], (200, 120, 138), 0.70), 0.60)


def _column_grey(palette):
    # Stone column under the One Pillar pavilion — a cool slate derived
    # from stone_mid so it reads as bare granite, not the warm wood body.
    return _mix(palette['stone_mid'], (148, 142, 130), 0.55)


def _pond_aqua(palette):
    # Lotus-pond water at the base of Chùa Một Cột — derived from horizon
    # so dawn/dusk paint it pink, day paints it teal, night paints it ink.
    return _mix(palette['horizon'], (118, 168, 162), 0.55)


def _basalt(palette):
    # Borobudur volcanic andesite — cool desaturated grey anchored to
    # stone_mid so the temple reads as bare stone, not gold or wood.
    return _mix(palette['stone_mid'], (118, 116, 110), 0.66)


def _basalt_lit(palette):
    return _mix(palette['stone_light'], (170, 166, 158), 0.55)


def _basalt_shadow(palette):
    return _mix(palette['stone_dark'], (72, 70, 66), 0.78)


def _basalt_accent(palette):
    # Inset relief shadow on Borobudur's terrace panels — a half-stop darker
    # than _basalt for the sculpted-panel cue.
    return _mix(palette['stone_dark'], (60, 58, 54), 0.78)


def _gold_laos(palette):
    # Pha That Luang gold — slightly warmer + more orange than Shwedagon's
    # gilt so the two gold stupas read distinct at a glance.
    return _mix(palette['stone_accent'], (244, 188, 60), 0.78)


def _gold_laos_deep(palette):
    return _mix(palette['stone_accent'], (180, 128, 28), 0.80)


def _gold_laos_bright(palette):
    return _mix(palette['stone_accent'], (255, 230, 130), 0.82)


def _lacquer_red(palette):
    # Lao lacquer-red trim band on Pha That Luang's tiers — derived from
    # stone_dark with a saturated cinnabar bias.
    return _mix(palette['stone_dark'], (172, 50, 42), 0.78)


def _cream_base(palette):
    # Cream-white base of the Pha That Luang stupa — warmer than the
    # Boudhanath stupa_white so the two cream surfaces don't blur.
    return _mix(palette['stone_light'], (240, 224, 196), 0.62)


def _is_dark_sky(palette):
    """Drives lit-rim alpha — night/dusk skies get a brighter window glow."""
    top = palette['sky_top']
    return (top[0] + top[1] + top[2]) / 3.0 < 110


def _is_warming_sky(palette):
    """Sunset band — sky between dusk-dark and noon-bright. The window glow
    starts WARMING here so the niches don't pop on a single frame from dead
    to glowing once the sun fully sets."""
    top = palette['sky_top']
    avg = (top[0] + top[1] + top[2]) / 3.0
    return 60 <= avg < 110


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
    the cue calibrated to the biome.

    Three-stop glow ramp so the lanterns don't pop on a single frame:
      * DAY/SUNRISE — quiet shadow with a 90-alpha rim, no halo.
      * SUNSET     — 4-px additive amber halo, rim alpha 170 (windows
                     start warming BEFORE night fully lands).
      * DUSK/NIGHT — 14-px additive amber halo, rim alpha 255 (the
                     column becomes a lantern-strung landmark).
    """
    if w < 3 or h < 4:
        return
    dark_sky = _is_dark_sky(palette)
    warming = _is_warming_sky(palette)
    frame = _shade(palette['stone_dark'], -25)
    inside = _shade(palette['stone_dark'], -50)
    if dark_sky and not warming:
        rim_alpha = 255
    elif warming:
        rim_alpha = 170
    else:
        rim_alpha = 90
    rim = _mix(palette['stone_accent'], (255, 215, 120), 0.78)
    # Lay an additive amber halo BEHIND the frame so warm glow seeps around
    # the niche rim before the dark inside is painted on top. Radius 14 px
    # at night (the niche becomes a clear point-source), 4 px at sunset
    # (windows pre-warm), nothing during the day.
    if dark_sky or warming:
        r_outer = 14 if (dark_sky and not warming) else 4
        sz = r_outer * 2 + 2
        glow = pygame.Surface((sz, sz), pygame.SRCALPHA)
        cgx = sz // 2
        cgy = sz // 2
        if dark_sky and not warming:
            pygame.draw.circle(glow, (*rim, 60), (cgx, cgy), r_outer)
            pygame.draw.circle(glow, (*rim, 100), (cgx, cgy), r_outer - 4)
            pygame.draw.circle(glow, (*rim, 160), (cgx, cgy), r_outer - 8)
        else:
            pygame.draw.circle(glow, (*rim, 70), (cgx, cgy), r_outer)
            pygame.draw.circle(glow, (*rim, 110), (cgx, cgy), max(1, r_outer - 2))
        surf.blit(glow, (cx - cgx, cy + h // 2 - cgy),
                  special_flags=pygame.BLEND_RGBA_ADD)
    pygame.draw.rect(surf, frame, (cx - w // 2, cy, w, h))
    pygame.draw.rect(surf, inside, (cx - w // 2 + 1, cy + 1, w - 2, h - 2))
    rim_layer = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(rim_layer, (*rim, rim_alpha), (0, 0, w, h), 1)
    surf.blit(rim_layer, (cx - w // 2, cy))


def _tile_hatch(surf, x1, y1, x2, y2, color, step=3, *, alternating=False):
    """Short perpendicular hatch marks along an eave line — reads as the row
    of tile-ends on a tiled roof. Spans the eave from x1,y1 to x2,y2.

    `alternating=True` doubles density to step/2 but emits a 1-px hatch then
    a 0-px gap then a 1-px hatch — so individual ridge-tiles read on
    Hōryū-ji's flat eaves at PIPE_W = 58 instead of dissolving into a uniform
    row of marks."""
    dx, dy = x2 - x1, y2 - y1
    length = max(1, int(math.hypot(dx, dy)))
    ux, uy = dx / length, dy / length
    nx, ny = -uy, ux
    if alternating:
        # Tighter cadence with skipped rungs so the eye reads paired tile-ends
        # rather than a uniform comb.
        idx = 0
        for s in range(0, length, max(1, step // 2)):
            if idx % 2 == 1:
                idx += 1
                continue
            idx += 1
            sx = x1 + ux * s
            sy = y1 + uy * s
            pygame.draw.line(surf, color,
                             (int(sx), int(sy)),
                             (int(sx + nx * 1.5), int(sy + ny * 1.5)), 1)
    else:
        for s in range(0, length, step):
            sx = x1 + ux * s
            sy = y1 + uy * s
            pygame.draw.line(surf, color,
                             (int(sx), int(sy)),
                             (int(sx + nx * 1.5), int(sy + ny * 1.5)), 1)


# ── Atmospheric + ornament primitives (round 7 epic-adventure pass) ────────

def _draw_plinth_mist(surf, cx, base_y, halo_w, palette):
    """Additive cool-white wedge behind the plinth — lifts the pagoda
    silhouette off the shan-shui mountain band. Drawn BEFORE the pagoda
    body in ADDITIVE so only the soft outer falloff peeks out at the
    silhouette edge once the plinth + foliage land on top. The colour
    biases toward a 90/10 horizon/cool-white mix so dusk and night get a
    legible cyan-white haze instead of disappearing into the warm
    horizon stripe."""
    if halo_w < 24:
        return
    # Cool cyan-white mix so the wedge reads as atmospheric backlight
    # across all biome phases — pure-horizon mist vanished into warm
    # sunsets and dark night skies. Higher cool-white share + alphas
    # so the halo actually registers at PIPE_W=58 instead of getting
    # eaten by the additive blend against bright skies.
    base = _mix(palette['horizon'], (235, 240, 255), 0.55)
    halo_h = 40
    g = pygame.Surface((halo_w, halo_h), pygame.SRCALPHA)
    for ring, alpha in ((1.00, 55), (0.78, 95), (0.55, 140), (0.32, 180)):
        rw = max(2, int(halo_w * 0.5 * ring))
        rh = max(2, int(halo_h * 0.55 * ring))
        pygame.draw.ellipse(g, (*base, alpha),
                            (halo_w // 2 - rw, halo_h - rh - 2,
                             rw * 2, rh * 2))
    surf.blit(g, (cx - halo_w // 2, base_y - halo_h + 4),
              special_flags=pygame.BLEND_RGBA_ADD)


def _draw_entry_door(surf, cx, base_y, palette, *, w=2, h=4, open_glow=False):
    """Recessed entry door at the lowest visible storey — a 2 px × 4 px
    dark inset rect with a 1-px brass sill highlight across the top so
    the door registers as a clean lintel-and-recess against the wood-grain
    body. Sized intentionally tiny so it reads as a single small opening
    at PIPE_W=58 instead of a panel-sized hole.

    When `open_glow` is True a single additive amber pixel sits inside
    the recess, driving the seed-strip open/closed variation."""
    if w < 2 or h < 3:
        return
    inside = _shade(palette['stone_dark'], -55)
    brass = _bronze(palette)
    dx0 = cx - w // 2
    dy0 = base_y - h
    pygame.draw.rect(surf, inside, (dx0, dy0, w, h))
    if open_glow:
        # Single amber pixel additive through the open door — keeps the
        # seed variation legible without bleeding warm light over the
        # entire panel face.
        warm_col = _mix(brass, (255, 220, 130), 0.85)
        warm = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(warm, (*warm_col, 220), (0, h - 2, w, 1))
        warm.set_at((max(0, w // 2 - 1), max(0, h // 2)), (*warm_col, 255))
        surf.blit(warm, (dx0, dy0), special_flags=pygame.BLEND_RGBA_ADD)
    # 1-px brass sill highlight ACROSS the top of the doorway — the
    # canonical lintel cue that makes the recess register as a door
    # against a wood-grain wall, not as a stray shadow.
    pygame.draw.line(surf, _shade(brass, 25),
                     (dx0, dy0), (dx0 + w - 1, dy0), 1)


def _draw_shibi_finial(surf, cx, eave_tip_y, palette, *, side=-1):
    """Hōryū-ji topmost-eave fish-tail ornament — a 5x6 bronze polygon that
    curls UP-and-IN from the eave tip with an asymmetric hook flick so the
    silhouette disagrees with the Fogong chiwen at game scale. `side=-1`
    for the left tip (curls rightward), `side=+1` for the right tip. Drawn
    ONLY on the top tier so the eave row doesn't go noisy."""
    bronze = _bronze(palette)
    dark = _shade(bronze, -55)
    bright = _shade(bronze, 45)
    # Tall fish-tail with a sharp UP flick at the inboard corner — the
    # extra 2 px of vertical reach is what makes shibi vs chiwen read
    # different in the seed strips.
    pts = [
        (cx, eave_tip_y),
        (cx + side * 1, eave_tip_y - 6),
        (cx + side * 2, eave_tip_y - 7),
        (cx + side * 4, eave_tip_y - 5),
        (cx + side * 4, eave_tip_y - 2),
        (cx + side * 3, eave_tip_y),
    ]
    pygame.draw.polygon(surf, dark, pts)
    inner = [(cx + side * 1, eave_tip_y - 1),
             (cx + side * 1, eave_tip_y - 5),
             (cx + side * 3, eave_tip_y - 4),
             (cx + side * 3, eave_tip_y - 1)]
    pygame.draw.polygon(surf, bronze, inner)
    # Glint on the tip + along the upper flick edge.
    pygame.draw.line(surf, bright,
                     (cx + side * 2, eave_tip_y - 6),
                     (cx + side * 3, eave_tip_y - 5), 1)
    pygame.draw.line(surf, bright,
                     (cx + side * 3, eave_tip_y - 3),
                     (cx + side * 3, eave_tip_y - 2), 1)


def _draw_chiwen_finial(surf, cx, eave_tip_y, palette, *, side=-1):
    """Fogong topmost-eave dragon-head ornament — a 5x5 dark silhouette
    that arches FORWARD (down-and-out) from the eave tip with a stubby
    snout + brass eye. The forward-arching profile reads visibly
    different from the shibi's UP-flick at PIPE_W=58."""
    grey_tile = _mix(palette['stone_mid'], (118, 110, 100), 0.62)
    body = _shade(grey_tile, -40)
    brass = _bronze(palette)
    # 5 px wide × 5 px tall silhouette — taller hump curving DOWN to a
    # forward-pointed jaw, asymmetric vs the shibi's vertical flick.
    pts = [
        (cx, eave_tip_y),
        (cx, eave_tip_y - 4),
        (cx + side * 1, eave_tip_y - 5),
        (cx + side * 3, eave_tip_y - 4),
        (cx + side * 4, eave_tip_y - 2),
        (cx + side * 5, eave_tip_y),
        (cx + side * 3, eave_tip_y + 1),
        (cx + side * 1, eave_tip_y + 1),
    ]
    pygame.draw.polygon(surf, body, pts)
    # 1-px brass eye dot on the head + a brass tooth on the jaw.
    pygame.draw.line(surf, brass,
                     (cx + side * 2, eave_tip_y - 3),
                     (cx + side * 2, eave_tip_y - 3), 1)
    pygame.draw.line(surf, brass,
                     (cx + side * 4, eave_tip_y),
                     (cx + side * 4, eave_tip_y), 1)


def _draw_vine_chunks(surf, x, y_top, y_bot, palette, *, seed=0):
    """3 chunky leaf-dot clusters along the corner column — the round-7
    1-px wobble line was a smear at PIPE_W=58, so we replace it with three
    small filled circles in the live foliage palette at jittered y. Each
    cluster is a darker base disk + a lighter top disk so it reads as a
    leaf, not a paint blot."""
    if y_bot - y_top < 16:
        return
    dark = palette['foliage_dark']
    mid = palette['foliage_mid']
    top = palette['foliage_top']
    rng = random.Random(seed)
    span = y_bot - y_top
    # Three clusters at jittered fractions so each seed sets a unique
    # vertical rhythm — the AD's seed-strip variation handle.
    fracs = [0.20 + rng.random() * 0.10,
             0.50 + rng.random() * 0.10,
             0.78 + rng.random() * 0.10]
    side_seq = rng.choice(((-1, 1, -1), (1, -1, 1), (-1, -1, 1), (1, 1, -1)))
    for frac, side in zip(fracs, side_seq):
        py = y_top + int(frac * span)
        px = x + side * 2
        pygame.draw.circle(surf, dark, (px, py), 3)
        pygame.draw.circle(surf, mid, (px - side, py - 1), 2)
        pygame.draw.circle(surf, top, (px - side, py - 2), 1)


def _draw_mini_lantern(surf, cx, eave_y, palette):
    """Tight 3-px red lantern dangling from a 1-px strand — the shared
    `draw_paper_lantern` produced a lantern much larger than PIPE_W=58
    could fairly host, so two compact dots + an additive red glow carry
    the lantern cue cleanly under Fogong's lowest hanger eave."""
    strand = 5
    pygame.draw.line(surf, _shade(palette['stone_dark'], -20),
                     (cx, eave_y), (cx, eave_y + strand), 1)
    lantern_cy = eave_y + strand + 2
    # 3-px diameter red body + 1-px brass cap, sized so it reads as a
    # clear dot rather than a fuzzy smear.
    red_dark = _mix(palette['stone_dark'], (138, 32, 28), 0.78)
    red_lit = _mix(palette['stone_accent'], (228, 102, 80), 0.78)
    pygame.draw.circle(surf, red_dark, (cx, lantern_cy), 2)
    pygame.draw.circle(surf, red_lit, (cx, lantern_cy - 1), 1)
    # Brass cap pixel on top.
    pygame.draw.line(surf, _bronze(palette),
                     (cx, lantern_cy - 2), (cx, lantern_cy - 2), 1)
    # Additive red glow halo so the lanterns glow against any sky.
    sz = 12
    g = pygame.Surface((sz, sz), pygame.SRCALPHA)
    pygame.draw.circle(g, (*red_lit, 60), (sz // 2, sz // 2), 5)
    pygame.draw.circle(g, (*red_lit, 110), (sz // 2, sz // 2), 3)
    pygame.draw.circle(g, (255, 200, 150, 180), (sz // 2, sz // 2), 1)
    surf.blit(g, (cx - sz // 2, lantern_cy - sz // 2),
              special_flags=pygame.BLEND_RGBA_ADD)


def _draw_sorin_flame_halo(surf, cx, tip_y, palette):
    """1-px additive halo around the sōrin flame jewel — gated on dark
    skies so the spire becomes the night-time focal point like real
    shrine photography. Drawn separately so the flame itself stays the
    bright centre and the halo just feathers around it."""
    if not _is_dark_sky(palette):
        return
    bronze = _bronze(palette)
    bright = _shade(bronze, 60)
    g = pygame.Surface((22, 22), pygame.SRCALPHA)
    pygame.draw.circle(g, (*bright, 70), (11, 11), 9)
    pygame.draw.circle(g, (*bright, 110), (11, 11), 6)
    surf.blit(g, (cx - 11, tip_y - 11),
              special_flags=pygame.BLEND_RGBA_ADD)


# ── Cached eave primitives (Japanese / Chinese flat shingled eave) ──────────

def _eave_tang_curl(surf, cx, y_base, half_w_body, overhang, depth,
                    roof_col, accent_col, tile_col, curl=0.7, *,
                    alternating_hatch=False, fringe=False,
                    drop_shadow=False, fringe_col=None,
                    skip_corner_hook=False):
    """Up-curled tiled eave — anchor points on a quadratic, then tile-hatch
    along the upper edge for shingle-row detail. Corner-hook polygons sit on
    each tip so a Chinese/Japanese roof reads even at small scale.

    Round-7 hooks for Hōryū-ji + Fogong polish:
      * `alternating_hatch=True` — denser hatch w/ skipped rungs so the
        individual ridge-tiles read on Hōryū-ji's flat eaves.
      * `drop_shadow=True` — a 1-px shadow line UNDER the keyline so each
        eave visibly lifts off the wall band below it.
      * `fringe=True` (+ `fringe_col`) — 2-px hanging tile-end strip below
        the keyline, the canonical Chinese pendant-tile cue on Fogong.
      * `skip_corner_hook=True` — leave the corner tip clean so the
        topmost eave can take a shibi/chiwen finial instead."""
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
    # Drop-shadow under the keyline so each eave reads as floating ABOVE
    # the wall band — without this the eave fuses into the wood storey
    # below at dusk/night palettes.
    if drop_shadow:
        pygame.draw.line(surf, _shade(roof_col, -85),
                         (cx - half_outer + 2, y_base + depth),
                         (cx + half_outer - 2, y_base + depth), 1)
    # Hanging tile-end fringe — 2-px strip directly under the keyline so
    # the eave reads as Chinese pendant-tile (not Japanese flat shingle).
    if fringe:
        fcol = fringe_col if fringe_col else _shade(roof_col, -15)
        pygame.draw.rect(surf, fcol,
                         (cx - half_outer + 3, y_base + depth - 2,
                          (half_outer - 3) * 2, 2))
        # Tiny per-tile breaks so the fringe reads as separate pendant
        # tiles instead of a single ribbon.
        for sx in range(cx - half_outer + 4,
                        cx + half_outer - 3, 3):
            pygame.draw.line(surf, _shade(fcol, -45),
                             (sx, y_base + depth - 2),
                             (sx, y_base + depth - 1), 1)
    # Tile hatching along the upper curve so the roof reads as a tile-row.
    _tile_hatch(surf, cx - half_outer + 4, y_base - tip_rise + 2,
                cx + half_outer - 4, y_base - tip_rise + 2,
                tile_col, step=2 if alternating_hatch else 3,
                alternating=alternating_hatch)
    # Accent stripe just under the ridge.
    pygame.draw.line(surf, accent_col,
                     (cx - half_w_body + 1, y_base - 1),
                     (cx + half_w_body - 1, y_base - 1), 1)
    # Corner-hook upturn polygons sharpen the tip silhouette.
    if not skip_corner_hook:
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
                    tier_count=5, finial_h=34, sorin_up=True,
                    entry_door_open=False, draw_entry_door=True):
    """Stack of `tier_count` cedar-and-plaster storeys with wide flat eaves.

    `top_y`/`bot_y` define the tier-stack envelope (excluding the finial).
    When `sorin_up` is True the sōrin sits ABOVE top_y (Japanese tō);
    when False, the finial points DOWN past bot_y (mirrored hanging tō).

    Round-7 polish per the AD punchlist:
      * niche centred on EACH plaster panel of every visible storey
      * topmost eave gets a bronze shibi fish-tail finial (not on every tier)
      * wood grain stippled across each plaster panel
      * nageshi rails: double horizontal shadows at 1/3 and 2/3 down per panel
      * sashi: a 1-px vertical centre-line shadow on each panel
      * recessed entry door at the lowest visible storey
      * additive halo around the sōrin flame jewel (dark sky only)"""
    cedar = _cedar(palette)
    plaster = _plaster(palette)
    roof = _shade(cedar, -10)
    accent = _bronze(palette)
    tile_col = _shade(palette['stone_dark'], -15)
    plaster_shadow = _shade(plaster, -25)

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
        # Plaster infill — slimmer 2 px corner columns (was 3) so the white
        # panel reads as the dominant wall mass at game scale.
        if bw > 6 and th > 4:
            pygame.draw.rect(surf, plaster,
                             (x_l + 2, wall_top + 1, bw - 4, th - 1))
        pygame.draw.rect(surf, cedar, (x_l, wall_top, 2, th))
        pygame.draw.rect(surf, cedar, (x_l + bw - 2, wall_top, 2, th))
        # Optional mid post only on the widest base tiers so upper tiers
        # stay readable as single panels instead of a forest of posts.
        has_mid_post = bw > 26
        if has_mid_post:
            mid_x = cx - 1
            pygame.draw.rect(surf, cedar, (mid_x, wall_top, 2, th))
        # Horizontal cedar beam mid-tier — adds the Hōryū-ji wood-grid cue.
        if th > 10:
            beam_y = wall_top + th // 2
            pygame.draw.line(surf, cedar,
                             (x_l + 1, beam_y), (x_l + bw - 2, beam_y), 1)
        # Nageshi rails — twin horizontal shadow lines at 1/3 and 2/3 of
        # each panel height so the cedar wood-grid reads richer than a
        # single mid-beam. Real Hōryū-ji panels have nageshi + sill rails.
        if th > 12:
            for frac in (1 / 3, 2 / 3):
                rail_y = wall_top + int(th * frac)
                pygame.draw.line(surf, plaster_shadow,
                                 (x_l + 2, rail_y),
                                 (x_l + bw - 3, rail_y), 1)
        # Sashi: 1-px vertical centre-line shadow per panel — the canonical
        # sashi-stud cue. Two panels if there's a mid-post, one otherwise.
        if th > 8:
            if has_mid_post:
                left_panel_cx = (x_l + 2 + cx) // 2
                right_panel_cx = (cx + 1 + x_l + bw - 2) // 2
                for sx in (left_panel_cx, right_panel_cx):
                    pygame.draw.line(surf, plaster_shadow,
                                     (sx, wall_top + 2),
                                     (sx, wall_top + th - 2), 1)
            else:
                pygame.draw.line(surf, plaster_shadow,
                                 (cx, wall_top + 2),
                                 (cx, wall_top + th - 2), 1)
        # Wood-grain stipple removed — at PIPE_W=58 the 1-px dashes had
        # zero read and were eating budget. Plaster panels stay clean.
# ONE lit-rim niche per storey, centred — collapsing the prior
        # per-panel pair to a single window so the 14-px additive halo at
        # night reads as a clear point-source instead of two competing
        # dots that fuse to noise at PIPE_W=58.
        if th > 9 and bw > 12:
            nh = min(7, th - 5)
            nw = min(7, bw - 8)
            _lit_niche(surf, cx, wall_top + 2, nw, nh, palette)
        # Recessed entry door at the LOWEST visible storey only — a tight
        # 2x4 dark recess + 1-px brass sill lintel reads as a clean door
        # cue at PIPE_W=58 where a panel-sized hole dissolved into the
        # plaster body. Open variant shows a warm amber pixel inside.
        if i == 0 and draw_entry_door and bw >= 12 and th >= 12:
            door_base_y = wall_top + th - 1
            _draw_entry_door(surf, cx, door_base_y, palette,
                             w=2, h=4, open_glow=entry_door_open)
        # Wide flat eave with corner up-curl. Eave overhang is what tells the
        # player "tō" — wider than the wall and only gently curled.
        overhang = max(10, 13 - i)
        depth = 5
        is_top_tier = (i == tier_count - 1)
        _eave_tang_curl(surf, cx, wall_top, bw // 2, overhang, depth,
                        roof, accent, tile_col, curl=0.40,
                        alternating_hatch=True,
                        drop_shadow=True,
                        skip_corner_hook=is_top_tier)
        # Topmost tier ONLY gets bronze shibi fish-tail finials. Drawn after
        # the eave so the polygon sits over the curl tip cleanly. We skip
        # the corner-hook on the top tier so the shibi takes its place.
        if is_top_tier:
            half_outer = bw // 2 + overhang
            tip_y_top = wall_top - max(2, int(depth * (0.5 + 0.40)))
            _draw_shibi_finial(surf, cx - half_outer + 1, tip_y_top + 1,
                               palette, side=+1)
            _draw_shibi_finial(surf, cx + half_outer - 1, tip_y_top + 1,
                               palette, side=-1)
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
    # Flame jewel orb + tongue. Halo painted BEFORE the orb so the orb
    # remains the bright centre of the bloom on night palettes.
    tip_y = base_y + dir_sign * finial_h
    _draw_sorin_flame_halo(surf, cx, tip_y, palette)
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
    # Seed-driven variation — drives the per-seed strip the AD asked for.
    vine_side = rng.choice(('left', 'right'))
    entry_open = rng.choice((True, False))
    has_pine_sprig = rng.random() < 0.7
    shrub_jitter = rng.randint(-2, 2)

    # Ground tō.
    if bot_rect.height > 50:
        # Atmospheric mist halo BEFORE pillar paint — pushes the silhouette
        # off the shan-shui mountain band at DUSK/NIGHT.
        _draw_plinth_mist(surf, bcx, bot_rect.bottom,
                          int(bot_rect.width * 2.4), palette)

        # Stepped plinth — bottom row dark stone overhang, top row inset
        # column-grey 4 px narrower, with a stair notch dead-centre.
        plinth_h_total = 10
        bot_row_h = 4
        top_row_h = plinth_h_total - bot_row_h
        plinth_w_bot = int(bot_rect.width * 1.22)
        plinth_w_top = plinth_w_bot - 8
        # Bottom row — overhanging dark stone.
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -10),
                         (bcx - plinth_w_bot // 2,
                          bot_rect.bottom - bot_row_h,
                          plinth_w_bot, bot_row_h))
        # Top row — narrower column-grey body.
        pygame.draw.rect(surf, _column_grey(palette),
                         (bcx - plinth_w_top // 2,
                          bot_rect.bottom - plinth_h_total,
                          plinth_w_top, top_row_h))
        pygame.draw.rect(surf, palette['stone_light'],
                         (bcx - plinth_w_top // 2,
                          bot_rect.bottom - plinth_h_total,
                          plinth_w_top, 1))
        # Stair notch — 6 px wide × 3 px tall centred at the bottom of the
        # top row, with a brass rim line. Reads as a worship-step.
        notch_w, notch_h = 6, 3
        notch_x = bcx - notch_w // 2
        notch_y = bot_rect.bottom - bot_row_h
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -25),
                         (notch_x, notch_y, notch_w, notch_h))
        pygame.draw.line(surf, _bronze(palette),
                         (notch_x, notch_y),
                         (notch_x + notch_w - 1, notch_y), 1)

        finial_h = 36
        envelope_top = bot_rect.y
        envelope_bot = bot_rect.bottom - plinth_h_total
        # Body widens (0.84 → 0.94 of pipe width) so the white plaster panels
        # have real weight against the dark cedar columns at PIPE_W = 58.
        _draw_horyuji_to(surf, bcx,
                         envelope_top + finial_h, envelope_bot,
                         int(bot_rect.width * 0.94), palette,
                         tier_count=tier_count, finial_h=finial_h,
                         sorin_up=True,
                         entry_door_open=entry_open)

        # Vegetation pass — chunky leaf-dot cluster on one corner column
        # (side seed-driven), flanking shrubs, dense grass bed + flowers,
        # optional foreground pine sprig. The chunk-dot version replaces
        # the round-7 thin wobble line which smeared at PIPE_W=58.
        body_half = int(bot_rect.width * 0.94) // 2
        vine_x = bcx - body_half + 1 if vine_side == 'left' else bcx + body_half - 1
        vine_top = max(envelope_top + finial_h + 20, envelope_bot - 70)
        _draw_vine_chunks(surf, vine_x, vine_top, envelope_bot - 4,
                          palette, seed=seed)
        # Side shrubs flanking the plinth.
        draw_side_shrub(surf, bcx - plinth_w_bot // 2 - 2 + shrub_jitter,
                        bot_rect.bottom - 2, palette, scale=0.9)
        draw_side_shrub(surf, bcx + plinth_w_bot // 2 + 2 - shrub_jitter,
                        bot_rect.bottom - 2, palette, scale=0.9)
        # Dense grass bed — density 16 (was 14).
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 10, 16, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 7, seed=seed)
        # Foreground pine sprig — seed-driven, off to one side.
        if has_pine_sprig:
            pine_side = -1 if vine_side == 'right' else 1
            pine_x = bcx + pine_side * (plinth_w_bot // 2 + 8)
            draw_wuling_pine(surf, pine_x, bot_rect.bottom,
                             22, palette, lean=pine_side * 3, layers=4)

    # Ceiling-mounted tō (mirrored, sōrin pointing down into the gap).
    if top_rect.height > 50:
        # Atmospheric mist halo behind the ceiling plinth too.
        _draw_plinth_mist(surf, tcx, top_rect.y + 10,
                          int(top_rect.width * 2.0), palette)

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
        # Hanger uses `tier_count - 2` so the silhouette differs from the
        # ground tō at a glance, per AD note 9. Also `finial_h` 4 px
        # shorter so the spire doesn't outweigh the ground spire.
        hanger_tiers = max(3, tier_count - 2)
        _draw_horyuji_to(surf, tcx,
                         envelope_top, envelope_bot,
                         int(top_rect.width * 0.94), palette,
                         tier_count=hanger_tiers,
                         finial_h=finial_h - 4, sorin_up=False,
                         draw_entry_door=False)
        # Hanging moss — TRIMMED from 4 to 2 strands per AD note 8.
        for off in (-8, 8):
            draw_moss_strand(surf, tcx + off, envelope_bot,
                             7 + abs(off) % 3, palette,
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
        # Suspension chain — longer + thicker so the pendant clearly hangs
        # off the ceiling anchor instead of floating beside it. Each link is
        # a stretched gold oval with a dark outline, chained continuously
        # down the rope so the eye traces the suspension at game scale.
        chain_top = top_rect.y + anchor_h
        # Anchor a generous portion of the ceiling rect to the chain so the
        # hti + bell don't collide with the gap — clamp to leave ~52 px
        # below for the chandelier + bell + diamond bud.
        chain_bot = max(chain_top + 14,
                        min(top_rect.bottom - 52,
                            top_rect.y + anchor_h + 38))
        # Twin rope strands — a dark backbone with a gold inner highlight.
        pygame.draw.line(surf, dark, (tcx, chain_top), (tcx, chain_bot), 4)
        pygame.draw.line(surf, _shade(gold, -10),
                         (tcx, chain_top), (tcx, chain_bot), 2)
        # Larger, denser links so the chain reads at every biome phase.
        for i, cy in enumerate(range(chain_top + 1, chain_bot, 4)):
            pygame.draw.ellipse(surf, dark, (tcx - 4, cy - 1, 8, 5))
            pygame.draw.ellipse(surf, gold, (tcx - 3, cy, 6, 3))
            # Bright gloss pixel on every other link.
            if i % 2 == 0:
                pygame.draw.line(surf, _shade(gold, 60),
                                 (tcx - 1, cy + 1), (tcx + 1, cy + 1), 1)
        # Inverted hti chandelier — fan wider and pack MORE rings so the
        # umbrella-stack reads even when sky brightness varies. Each ring
        # gets a tipped bead at both ends (the canonical hti-finial cue).
        ring_top_y = chain_bot + 2
        rings = rng.choice([7, 8, 9])
        for k in range(rings):
            t = k / max(1, rings - 1)
            ry = ring_top_y + int(t * 22)
            rw = 5 + k * 2
            # 2-px gold lip with a dark shadow underneath — heavier than
            # round 1 so the chandelier reads at small scale.
            pygame.draw.line(surf, dark,
                             (tcx - rw, ry + 1), (tcx + rw, ry + 1), 1)
            pygame.draw.line(surf, gold,
                             (tcx - rw, ry), (tcx + rw, ry), 2)
            # Tipped bead at both ends of every ring — the hti spoke cue.
            pygame.draw.circle(surf, dark, (tcx - rw - 1, ry), 2)
            pygame.draw.circle(surf, gold, (tcx - rw - 1, ry), 1)
            pygame.draw.circle(surf, dark, (tcx + rw + 1, ry), 2)
            pygame.draw.circle(surf, gold, (tcx + rw + 1, ry), 1)
        # Inverted bell pendant — only the LOWER half of an ellipse is drawn
        # so the bell reads as a hanging dome opening downward. Anchor under
        # the bottom of the chandelier (vs ring_top_y) so widening the chain
        # doesn't push the bell off the pendant axis.
        bell_top = ring_top_y + int(22) + 4
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
    """Pastel porcelain mosaic skin of Wat Arun's prang — high-contrast
    diamond tiles on a 5-px lattice with dark mortar in between. The lattice
    is hand-set so the pattern reads as porcelain inlay at PIPE_W = 58, not
    as soft noise. Each diamond gets a brighter inner highlight + a dark
    keyline so the mosaic survives day-bright and night-dark palettes."""
    if w < 6 or h < 6:
        return
    pink = _porcelain_pink(palette)
    aqua = _porcelain_aqua(palette)
    cream = _porcelain_cream(palette)
    dark = _shade(palette['stone_dark'], -10)
    cols = (pink, aqua, cream)
    step = 5
    rows = max(1, h // step)
    cells = max(1, w // step)
    for r in range(rows):
        for c in range(cells):
            tx = x + c * step
            ty = y + r * step
            # Stagger every other row by half a cell so the diamonds
            # interlock the way a real porcelain mosaic on a prang does.
            if r % 2 == 1:
                tx += step // 2
            ci = (r + c + rng.randrange(2)) % 3
            col = cols[ci]
            # Dark mortar keyline around the diamond.
            diamond = [(tx + 2, ty), (tx + 4, ty + 2),
                       (tx + 2, ty + 4), (tx, ty + 2)]
            pygame.draw.polygon(surf, dark, diamond)
            inner = [(tx + 2, ty + 1), (tx + 3, ty + 2),
                     (tx + 2, ty + 3), (tx + 1, ty + 2)]
            pygame.draw.polygon(surf, col, inner)
            # Centre highlight pixel — porcelain catches a tiny gloss spot.
            pygame.draw.line(surf, _shade(col, 35),
                             (tx + 2, ty + 2), (tx + 2, ty + 2), 1)


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

    # Porcelain mosaic skin across the spire: thicker stripe rings + a row
    # of small staggered lozenge dots per band so the body matches the
    # mosaic-clad reference, not a plain striped cone.
    for k in range(rings):
        t = k / rings
        local_w = int(w * (1 - t * t) * 0.5 + 2)
        ry = base_y - int(spire_h * t)
        stripe_col = pink if k % 2 == 0 else aqua
        # 2-px stripe with a darker mortar line above so the band reads
        # as a porcelain inlay row.
        pygame.draw.line(surf, _shade(dark, 25),
                         (cx - local_w + 1, ry - 1),
                         (cx + local_w - 1, ry - 1), 1)
        pygame.draw.line(surf, stripe_col,
                         (cx - local_w + 1, ry),
                         (cx + local_w - 1, ry), 1)
        # Staggered lozenge dots — pink/aqua/cream rotating so the column
        # reads tiled rather than striped.
        dot_col = cream if k % 3 == 0 else (aqua if k % 3 == 1 else pink)
        for off in (-local_w + 3, 0, local_w - 3):
            if off == 0 and local_w < 4:
                continue
            pygame.draw.polygon(surf, dot_col,
                                [(cx + off, ry - 1),
                                 (cx + off + 1, ry),
                                 (cx + off, ry + 1),
                                 (cx + off - 1, ry)])

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
    """Brick-row striations on the body — tighter 3-px mortar rows with a
    lighter, brighter mortar tone so the brick pattern reads at game
    scale instead of dissolving into a flat terracotta column."""
    if w < 4 or h < 4:
        return
    brick = _terracotta(palette)
    mortar = _shade(_brick_mortar(palette), 18)
    pygame.draw.rect(surf, brick, (cx - w // 2, y, w, h))
    # Right-edge cool shadow gives the cylinder its volume.
    pygame.draw.rect(surf, _shade(brick, -30),
                     (cx + w // 2 - 3, y, 3, h))
    # Left-edge highlight.
    pygame.draw.rect(surf, _shade(brick, 18),
                     (cx - w // 2, y, 2, h))
    # Horizontal mortar rows every 3 px — the brick-row cue. Each row gets
    # a half-cell offset on alternate lines so the eye reads brick-bond
    # masonry, not just stripes.
    for idx, k in enumerate(range(y + 2, y + h, 3)):
        if idx % 2 == 0:
            pygame.draw.line(surf, mortar,
                             (cx - w // 2 + 2, k),
                             (cx + w // 2 - 2, k), 1)
        else:
            # Broken row — leaves a brick-end gap mid-line.
            mid = cx
            pygame.draw.line(surf, mortar,
                             (cx - w // 2 + 2, k), (mid - 1, k), 1)
            pygame.draw.line(surf, mortar,
                             (mid + 1, k), (cx + w // 2 - 2, k), 1)


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


# ── Round 6 shared primitives ──────────────────────────────────────────────
#
# The 5 new candidates all push detail past round 5 with at least three of:
#   - vertical body gradient (lit edge → mid → shadow edge),
#   - dougong / bracket / corner-cluster polygons,
#   - glazed-tile checker with per-tile gloss highlights,
#   - lotus petal radial fans,
#   - hexagonal-lattice perforations on perforated bell stupas,
#   - lacquer-red trim band + corner spire chapels,
#   - AA polylines on every curved silhouette via _aa_polyline.
# The helpers below are reused across more than one candidate to keep the
# new code compact.


def _gradient_rect(surf, rect, lit, mid, shadow, *, vertical=False):
    """Per-column or per-row 3-stop body gradient so a flat rectangle reads
    as a 3-D volume at PIPE_W = 58. Without this the new candidates would
    look like the old silhouettes painted with one extra colour. Cheap
    enough to call inside the once-per-(seed, palette) cache."""
    if rect.width < 2 or rect.height < 2:
        return
    if vertical:
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
    else:
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


def _dougong_cluster(surf, cx, y_top, palette, *, w=8, depth=4):
    """A stepped corbel bracket — 3 stacked polygons, each step a touch
    NARROWER than the one above. Sits along the top edge of a wall, JUST
    UNDER the eave. `y_top` is the top edge of the topmost (widest) tier
    — they stack DOWN from there into the wall body. Read as the canonical
    dougong staccato rhythm at Fogong scale where each cluster is ~8 px
    wide. Drawn AFTER the wall body so the bracket pattern overlays the
    wall and BEFORE the eave so the eave can crown them.

    Depth=4 px guarantees each corbel step shows a visible lit top-edge
    line so the bracket array reads as relief, not stripes, at PIPE_W=58.
    Shadow tone pushed to -75 (was -55) so the silhouette punches through
    the wood-tone wall at every biome phase — without this Fogong's
    identity is broken at game scale."""
    if w < 3 or depth < 2:
        return
    dark = _shade(_ochre_wood(palette), -75)
    mid = _ochre_wood(palette)
    lit = _ochre_wood_lit(palette)
    # 3 corbel steps stacked vertically going DOWN (into the wall) —
    # narrowest step at the top (closest to eave), widest at the bottom.
    # Each step is `depth` px tall (was depth-1) so the lit edge gets its
    # own row of pixels separate from the body fill below it.
    for k in range(3):
        step_w = max(2, w - (2 - k) * 2)
        step_y = y_top + k * (depth - 1)
        # Deep shadow polygon — extends 1 px past each side so each step
        # casts a visible drop-shadow under the step above.
        pygame.draw.rect(surf, dark,
                         (cx - step_w // 2 - 1, step_y,
                          step_w + 2, depth))
        # Mid-tone fill, slightly inset.
        pygame.draw.rect(surf, mid,
                         (cx - step_w // 2, step_y, step_w, depth - 1))
        # Lit top-edge highlight on every step — readable at game scale.
        pygame.draw.line(surf, lit,
                         (cx - step_w // 2, step_y),
                         (cx + step_w // 2 - 1, step_y), 1)
        # Tiny lit pixel at the right-side outer edge so the depth reads
        # 3-D rather than flat banding.
        pygame.draw.line(surf, lit,
                         (cx + step_w // 2 - 1, step_y),
                         (cx + step_w // 2 - 1, step_y + 1), 1)


def _glazed_tile_checker(surf, x, y, w, h, palette, *, tile=4):
    """Glazed iron-brown tile field on Kaifeng's body — a regular grid of
    iron-brown squares with a 1-px cream gloss in each top-left and a 1-px
    mortar shadow underneath. The gloss makes the body read as ceramic
    rather than a flat brown rectangle."""
    if w < tile * 2 or h < tile * 2:
        return
    base = _iron_brown(palette)
    base_lit = _iron_brown_lit(palette)
    base_dark = _iron_brown_shadow(palette)
    gloss = _tile_gloss(palette)
    pygame.draw.rect(surf, base, (x, y, w, h))
    cols = w // tile
    rows = h // tile
    for r in range(rows):
        for c in range(cols):
            tx = x + c * tile
            ty = y + r * tile
            # Brick-stagger every other row so the tile field doesn't look
            # like a printed grid — like a real glazed-brick wall.
            if r % 2 == 1:
                tx_off = tile // 2
            else:
                tx_off = 0
            tx2 = tx + tx_off
            if tx2 + tile > x + w:
                continue
            # Alternate the per-tile fill so we get a checker rhythm across
            # the field — half tiles lit, half shadow.
            if (r + c) % 2 == 0:
                pygame.draw.rect(surf, base_lit,
                                 (tx2, ty, tile - 1, tile - 1))
            else:
                pygame.draw.rect(surf, base_dark,
                                 (tx2, ty, tile - 1, tile - 1))
            # Top-left gloss specular — 1 px is all that fits at this scale
            # but the dotted grid reads as glaze sheen across the field.
            pygame.draw.line(surf, gloss,
                             (tx2, ty), (tx2 + 1, ty), 1)
            # Underline shadow — the tile sits in front of mortar.
            pygame.draw.line(surf, _shade(base_dark, -20),
                             (tx2, ty + tile - 1),
                             (tx2 + tile - 2, ty + tile - 1), 1)


def _lotus_petal_fan(surf, cx, cy, radius, palette, *, n_petals=11,
                    arc=math.pi):
    """Radial fan of pink lotus petals spreading from (cx, cy). The default
    `arc=pi` draws a half-fan opening upward — used as the column-base
    cushion on One Pillar Pagoda. Each petal is a teardrop polygon with
    a darker outline and a 1-px lit specular tip."""
    if radius < 4:
        return
    pink = _lotus_pink(palette)
    deep = _lotus_pink_deep(palette)
    edge = _shade(deep, -30)
    bright = _shade(pink, 45)
    # Petals span `arc` centred on the +y axis (sweeping up).
    start = math.pi + (math.pi - arc) / 2
    for i in range(n_petals):
        t = i / max(1, n_petals - 1)
        ang = start + t * arc
        tip_x = cx + math.cos(ang) * radius
        tip_y = cy + math.sin(ang) * radius
        # Petal body — tear-drop with two side-anchors near the base.
        side_l_ang = ang - 0.18
        side_r_ang = ang + 0.18
        sl_x = cx + math.cos(side_l_ang) * radius * 0.45
        sl_y = cy + math.sin(side_l_ang) * radius * 0.45
        sr_x = cx + math.cos(side_r_ang) * radius * 0.45
        sr_y = cy + math.sin(side_r_ang) * radius * 0.45
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
        # Lit specular near the tip.
        pygame.draw.line(surf, bright,
                         (int(tip_x), int(tip_y)),
                         (int(tip_x - math.cos(ang) * 2),
                          int(tip_y - math.sin(ang) * 2)), 1)
        # AA the outer edge.
        _aa_polyline(surf, edge, petal, closed=True)


def _hex_lattice(surf, cx, cy, rx, ry, palette, *, holes=7):
    """Scatter of small dark hex-shaped perforations across an elliptical
    bell stupa — the Borobudur signature. Holes arranged on a vertical
    grid clipped to the ellipse so they read as openwork tile rather than
    random spots. `rx`/`ry` are the parent ellipse half-axes."""
    if rx < 5 or ry < 5:
        return
    dark = _basalt_shadow(palette)
    deeper = _shade(dark, -40)
    step_x = max(4, int(rx * 0.7))
    step_y = max(4, int(ry * 0.55))
    rows = max(2, holes // 3)
    cols = max(2, holes // rows)
    for r in range(rows):
        for c in range(cols):
            offx = (c - (cols - 1) / 2) * step_x
            offy = (r - (rows - 1) / 2) * step_y
            # Clip to the bell ellipse.
            if (offx / max(1, rx)) ** 2 + (offy / max(1, ry)) ** 2 > 0.7:
                continue
            hx = int(cx + offx)
            hy = int(cy + offy)
            # Hex polygon — 6-vertex with the two flat sides top/bottom.
            hex_pts = [
                (hx - 1, hy - 1),
                (hx + 1, hy - 1),
                (hx + 2, hy),
                (hx + 1, hy + 1),
                (hx - 1, hy + 1),
                (hx - 2, hy),
            ]
            pygame.draw.polygon(surf, deeper, hex_pts)
            # Centre-pixel "inside" sample — even darker so the perforation
            # reads as a real opening, not a painted dot.
            pygame.draw.line(surf, _shade(deeper, -25),
                             (hx, hy), (hx, hy), 1)


# ── 6. Fogong (Yingxian) Wooden Pagoda ─────────────────────────────────────
#
# Octagonal 5-storey larch tower (Liao, 1056). What separates it from a
# Japanese tō at game scale: VISIBLE DOUGONG BRACKET ARRAYS under each
# eave, ochre wood walls with bright white-plastered panels between them,
# and gentle gray-tile Chinese eave curls (slightly more curl than
# Hōryū-ji's flat shingled eaves but flatter than a Khmer prang).
#
# Reference: https://en.wikipedia.org/wiki/Pagoda_of_Fogong_Temple

def _draw_fogong_storey(surf, cx, wall_top, bw, th, palette, *,
                        top_tier=False, tier_index=0):
    """A single Fogong octagonal storey: ochre wood frame, lit/mid/shadow
    body gradient, alternating plaster-vs-wood panels separated by visible
    posts, and a dougong bracket array along the top edge.

    Round-7 polish per AD punchlist:
      * 3 dougong clusters per tier @ 8-px each, depth 4 — bracket array
        reads as relief, not stripes.
      * ONE centred niche per storey — three small dots collapsed to noise
        at PIPE_W=58 so the lit halo carries the lantern read cleanly.
      * Per-tier mid-tone lifted by 5% × tier_index toward the lit ochre,
        so higher storeys read atmospheric-recession lighter (not stacked
        identical boxes).
      * Wood-grain stipple removed — sub-pixel at PIPE_W=58 with no read.
    """
    if bw < 12 or th < 7:
        return
    wood = _ochre_wood(palette)
    wood_lit = _ochre_wood_lit(palette)
    wood_dark = _ochre_wood_shadow(palette)
    plaster = _white_plaster_warm(palette)
    plaster_shadow = _shade(plaster, -22)
    # Per-tier atmospheric recession — higher tiers shift toward the lit
    # ochre by 5%/tier so the stack reads as receding planes, not a stack
    # of identical boxes.
    if tier_index > 0:
        lift = min(0.35, tier_index * 0.05)
        wood = _mix(wood, wood_lit, lift)
    x_l = cx - bw // 2
    body_rect = pygame.Rect(x_l, wall_top, bw, th)

    # 3-stop horizontal gradient so the wall reads as a curved octagonal
    # cylinder, not a flat board. Left edge lit, right edge in shadow.
    _gradient_rect(surf, body_rect, wood_lit, wood, wood_dark)

    # Plaster panels — 3 across, sitting BETWEEN cedar-thick wood posts.
    # The plaster has its own light/shadow gradient so it reads as a
    # recessed plane behind the wood frame.
    if bw >= 22 and th >= 9:
        panels = 3
        panel_gap = 2
        panel_zone_w = bw - 6
        panel_w = max(3, (panel_zone_w - (panels - 1) * panel_gap) // panels)
        for i in range(panels):
            px0 = x_l + 3 + i * (panel_w + panel_gap)
            panel_rect = pygame.Rect(px0, wall_top + 2,
                                     panel_w, th - 4)
            _gradient_rect(surf, panel_rect,
                           _shade(plaster, 18), plaster, plaster_shadow)
            # Cross-beam at half-height — adds the Liao wood-frame cue.
            beam_y = wall_top + th // 2
            pygame.draw.line(surf, wood_dark,
                             (px0, beam_y), (px0 + panel_w - 1, beam_y), 1)

    # Wood posts — left, right, and one or two interior so plaster panels
    # read separated. Each post is 2 px wide with a 1-px lit edge.
    posts = [x_l, x_l + bw - 2]
    if bw >= 22:
        # 2 interior posts.
        third = bw // 3
        posts += [x_l + third - 1, x_l + 2 * third - 1]
    for px in posts:
        pygame.draw.rect(surf, wood_dark, (px, wall_top, 2, th))
        pygame.draw.line(surf, wood_lit,
                         (px, wall_top), (px, wall_top + th - 1), 1)

    # Top horizontal beam — the architrave the dougong sits on.
    pygame.draw.rect(surf, wood_dark, (x_l, wall_top, bw, 2))
    pygame.draw.line(surf, wood_lit,
                     (x_l, wall_top + 1), (x_l + bw - 1, wall_top + 1), 1)

    # ONE centred lit-rim niche per storey — three small dots collapse
    # to noise at PIPE_W=58, so a single point-source carries the lit
    # lantern signal cleanly under the 14-px additive halo at night.
    if th > 11 and bw > 12:
        nw = max(3, min(bw - 8, 6))
        nh = max(4, min(th - 7, 6))
        _lit_niche(surf, cx, wall_top + 3, nw, nh, palette)

    # Dougong bracket array along the top edge — Fogong's identity. AD
    # note 1: drop to 3 clusters per tier at 8 px each, depth 4 px. The
    # bracket field reads as carved relief at PIPE_W=58 rather than the
    # stripe-blur it dissolved into before.
    if not top_tier and bw >= 14:
        n_clusters = 3
        for i in range(n_clusters):
            t = (i + 0.5) / n_clusters
            bx = x_l + int(t * bw)
            _dougong_cluster(surf, bx, wall_top + 2, palette,
                             w=8, depth=4)


def _draw_fogong_to(surf, cx, top_y, bot_y, base_w, palette, *,
                    tier_count=5, finial_h=30, sorin_up=True,
                    draw_entry_door=True, entry_door_open=False):
    """Stacked Fogong storeys ending in a small bronze sōrin (down-pointing
    in the mirrored hanging variant). Each storey gets gentle Chinese-tile
    eave curls — between Hōryū-ji-flat and Khmer-corner-sweep so the
    silhouette doesn't blur with the Japanese tō.

    Round-7 polish per AD punchlist:
      * tier_index passed through so the storey gets the +5%/tier
        atmospheric-recession value lift.
      * eave curl ramps to 0.75 on bottom 3 storeys, 0.6 on upper 2 —
        Chinese eaves curl harder at the base.
      * 2-px hanging tile-end fringe under each eave keyline (pendant-tile
        cue, distinct from Hōryū-ji's flat shingles).
      * topmost eave gets paired chiwen dragon-head finials.
      * recessed entry door at the lowest visible storey.
      * additive halo around the sōrin finial jewel under dark skies."""
    wood = _ochre_wood(palette)
    wood_lit = _ochre_wood_lit(palette)
    accent = _bronze(palette)
    tile_col = _shade(palette['stone_dark'], -10)
    grey_tile = _mix(palette['stone_mid'], (118, 110, 100), 0.62)
    fringe_col = _shade(grey_tile, -15)

    total_h = bot_y - top_y
    if total_h < 12:
        return
    weights = [1.0 - 0.06 * i for i in range(tier_count)]
    wsum = sum(weights)
    tier_heights = [max(9, int(total_h * w / wsum)) for w in weights]
    body_widths = [max(12, int(base_w * (0.93 ** i)))
                   for i in range(tier_count)]

    y_cursor = bot_y
    tier_tops = []
    for i in range(tier_count):
        th = tier_heights[i]
        bw = body_widths[i]
        wall_top = y_cursor - th
        if wall_top < top_y - 1:
            break
        is_top_tier = (i == tier_count - 1)
        tier_tops.append((wall_top, bw, th))
        _draw_fogong_storey(surf, cx, wall_top, bw, th, palette,
                            top_tier=is_top_tier, tier_index=i)
        # Recessed entry door on the LOWEST visible storey only — 2x4
        # spec-sized so the dark recess + brass sill registers as a clean
        # opening at PIPE_W=58 instead of a panel-sized blob.
        if i == 0 and draw_entry_door and bw >= 12 and th >= 12:
            _draw_entry_door(surf, cx, wall_top + th - 1, palette,
                             w=2, h=4, open_glow=entry_door_open)
        # Chinese-style grey-tile eave — Chinese eaves curl HARDER at the
        # base than at the top, so the lower three storeys take 0.75 and
        # the upper two take 0.6. AD note 12.
        overhang = max(11, 14 - i)
        depth = 6
        eave_curl = 0.75 if i < 3 else 0.60
        _eave_tang_curl(surf, cx, wall_top - 1, bw // 2,
                        overhang, depth, grey_tile, accent, tile_col,
                        curl=eave_curl, fringe=True, fringe_col=fringe_col,
                        drop_shadow=True,
                        skip_corner_hook=is_top_tier)
        # Topmost eave ONLY: paired chiwen dragon-heads at each upper tip,
        # the canonical Fogong roof crest. Drawn after the eave so the
        # silhouette sits cleanly over the curl.
        if is_top_tier:
            half_outer = bw // 2 + overhang
            tip_y_top = wall_top - 1 - max(2, int(depth * (0.5 + eave_curl)))
            _draw_chiwen_finial(surf, cx - half_outer + 1, tip_y_top + 1,
                                palette, side=+1)
            _draw_chiwen_finial(surf, cx + half_outer - 1, tip_y_top + 1,
                                palette, side=-1)
        y_cursor = wall_top - depth + 1

    if not tier_tops:
        return

    # Bronze sōrin — shorter than Hōryū-ji's, with only 5 disks because
    # Fogong's finial is more compact relative to the body.
    top_wall_y = tier_tops[-1][0]
    base_y = top_wall_y - 2 if sorin_up else bot_y + 2
    dir_sign = -1 if sorin_up else 1
    dark_pal = palette['stone_dark']
    bright = _shade(accent, 45)
    pygame.draw.ellipse(surf, dark_pal, (cx - 6, base_y + dir_sign * 1, 12, 5))
    pygame.draw.ellipse(surf, accent, (cx - 5, base_y + dir_sign * 1 + 1, 10, 3))
    needle_tip = base_y + dir_sign * (finial_h - 4)
    pygame.draw.line(surf, dark_pal,
                     (cx - 1, base_y + dir_sign * 4),
                     (cx - 1, needle_tip), 2)
    pygame.draw.line(surf, accent,
                     (cx, base_y + dir_sign * 4),
                     (cx, needle_tip), 1)
    disks = 5
    for k in range(disks):
        t = k / max(1, disks - 1)
        ry = base_y + dir_sign * (5 + int(t * (finial_h - 11)))
        rw = max(2, 6 - k // 2)
        pygame.draw.ellipse(surf, dark_pal,
                            (cx - rw - 1, ry - 1, rw * 2 + 2, 3))
        pygame.draw.ellipse(surf, accent,
                            (cx - rw, ry, rw * 2, 2))
    tip_y = base_y + dir_sign * finial_h
    # Sōrin flame halo painted before the orb so the orb remains the
    # bright centre under dark skies.
    _draw_sorin_flame_halo(surf, cx, tip_y, palette)
    pygame.draw.circle(surf, dark_pal, (cx, tip_y), 3)
    pygame.draw.circle(surf, bright, (cx, tip_y), 2)


def _draw_fogong(surf, top_rect, bot_rect, palette, seed):
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2
    # Seed-driven variation per the AD seed-strip spec.
    vine_side = rng.choice(('left', 'right'))
    lantern_side = rng.choice(('left', 'right'))
    entry_open = rng.choice((True, False))
    has_pine_sprig = rng.random() < 0.7
    shrub_jitter = rng.randint(-2, 2)
    ground_tier_count = rng.choice([5, 5, 6])

    if bot_rect.height > 50:
        # Atmospheric mist halo behind the plinth — lifts the column off
        # the shan-shui mountain band at DUSK/NIGHT. AD note 10.
        _draw_plinth_mist(surf, bcx, bot_rect.bottom,
                          int(bot_rect.width * 2.5), palette)

        plinth_h = 9
        plinth_w = int(bot_rect.width * 1.22)
        # Cool stone plinth — _column_grey so it reads as a marble base
        # under the warm-wood pagoda, not part of the body.
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -10),
                         (bcx - plinth_w // 2, bot_rect.bottom - plinth_h,
                          plinth_w, plinth_h))
        pygame.draw.rect(surf, _column_grey(palette),
                         (bcx - plinth_w // 2 + 1,
                          bot_rect.bottom - plinth_h + 1,
                          plinth_w - 2, plinth_h - 2))
        pygame.draw.rect(surf, palette['stone_light'],
                         (bcx - plinth_w // 2,
                          bot_rect.bottom - plinth_h, plinth_w, 2))
        # Sumeru-pedestal lotus-petal nicks under the plinth top edge —
        # 7 inverted V-cuts evenly spaced. AD note 5. The dark cuts read
        # as carved lotus petals at PIPE_W=58.
        n_nicks = 7
        nick_zone_w = plinth_w - 6
        nick_dark = _shade(palette['stone_dark'], -25)
        nick_lit = _bronze(palette)
        for k in range(n_nicks):
            t = (k + 0.5) / n_nicks
            nx = bcx - nick_zone_w // 2 + int(t * nick_zone_w)
            ny = bot_rect.bottom - plinth_h + 2
            # Inverted V — 3 px wide × 2 px deep.
            pygame.draw.polygon(surf, nick_dark,
                                [(nx - 1, ny),
                                 (nx, ny + 2),
                                 (nx + 1, ny)])
            pygame.draw.line(surf, nick_lit, (nx, ny), (nx, ny), 1)

        finial_h = 32
        envelope_top = bot_rect.y
        envelope_bot = bot_rect.bottom - plinth_h
        _draw_fogong_to(surf, bcx,
                        envelope_top + finial_h, envelope_bot,
                        int(bot_rect.width * 0.94), palette,
                        tier_count=ground_tier_count, finial_h=finial_h,
                        sorin_up=True,
                        entry_door_open=entry_open)

        # Vegetation pass — chunky leaf-dot cluster on one corner column
        # (side seed-driven), flanking shrubs, dense grass bed, foreground
        # pine sprig. The chunk-dot replacement reads at PIPE_W=58 where
        # the round-7 thin vine line smeared into background noise.
        body_half = int(bot_rect.width * 0.94) // 2
        vine_x = bcx - body_half + 1 if vine_side == 'left' else bcx + body_half - 1
        vine_top = max(envelope_top + finial_h + 20, envelope_bot - 70)
        _draw_vine_chunks(surf, vine_x, vine_top, envelope_bot - 4,
                          palette, seed=seed)
        draw_side_shrub(surf, bcx - plinth_w // 2 - 2 + shrub_jitter,
                        bot_rect.bottom - 2, palette, scale=0.9)
        draw_side_shrub(surf, bcx + plinth_w // 2 + 2 - shrub_jitter,
                        bot_rect.bottom - 2, palette, scale=0.9)
        # Dense grass bed — density 16 (was 14).
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 10, 16, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 6, seed=seed)
        # Foreground pine sprig — seed-driven side. AD note 6.
        if has_pine_sprig:
            pine_side = -1 if vine_side == 'right' else 1
            pine_x = bcx + pine_side * (plinth_w // 2 + 8)
            draw_wuling_pine(surf, pine_x, bot_rect.bottom,
                             22, palette, lean=pine_side * 3, layers=4)

    if top_rect.height > 50:
        # Atmospheric mist halo behind the ceiling plinth too.
        _draw_plinth_mist(surf, tcx, top_rect.y + 12,
                          int(top_rect.width * 2.1), palette)

        plinth_h = 7
        plinth_w = int(top_rect.width * 1.18)
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -10),
                         (tcx - plinth_w // 2, top_rect.y, plinth_w, plinth_h))
        pygame.draw.rect(surf, _column_grey(palette),
                         (tcx - plinth_w // 2 + 1, top_rect.y + 1,
                          plinth_w - 2, plinth_h - 2))
        pygame.draw.rect(surf, palette['stone_light'],
                         (tcx - plinth_w // 2,
                          top_rect.y + plinth_h - 1, plinth_w, 1))
        finial_h = 26
        envelope_top = top_rect.y + plinth_h
        envelope_bot = top_rect.bottom - finial_h
        # Hanger gets `tier_count - 2` storeys and a 4-px-shorter sōrin per
        # AD note 9, so the silhouette differs from the ground tō.
        hanger_tiers = max(3, ground_tier_count - 2)
        _draw_fogong_to(surf, tcx,
                        envelope_top, envelope_bot,
                        int(top_rect.width * 0.94), palette,
                        tier_count=hanger_tiers, finial_h=finial_h - 4,
                        sorin_up=False, draw_entry_door=False)
        # 2 small red lanterns under the lowest hanger eave — dropped
        # from 3 to 2 + bumped to the chunky inline `_draw_mini_lantern`
        # so the lit dots register at PIPE_W=58 where the shared lantern
        # sprite was invisible at SUNSET/DUSK. Side bias is seed-driven
        # so the cluster shifts left/right between sibling seeds.
        if top_rect.height >= 90:
            lantern_side_sign = -1 if lantern_side == 'left' else 1
            for off in (-6, 6):
                lx = tcx + off + lantern_side_sign * 2
                ly = envelope_bot - 1
                _draw_mini_lantern(surf, lx, ly, palette)
        # Hanging moss — kept at 2 strands so the hanger isn't noisy now
        # the lanterns add visual mass.
        for off in (-9, 9):
            draw_moss_strand(surf, tcx + off, envelope_bot,
                             6 + abs(off) % 3, palette,
                             jitter_seed=seed + off)


def candidate_fogong(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('fogong', _draw_fogong, surf, top_rect, bot_rect,
                 palette, seed)


# ── 7. Iron Pagoda of Kaifeng ──────────────────────────────────────────────
#
# Tall slim octagonal 13-storey glazed-brick tower (Northern Song, 1049).
# Sits as a totally different mass from Fogong's wide-and-stocky larch
# tower — narrow body, dense per-storey bracket band, and a continuous
# iron-brown glazed-tile checker that catches per-tile gloss. Crowned
# with a small bronze finial.
#
# Reference: https://en.wikipedia.org/wiki/Iron_Pagoda

def _draw_iron_kaifeng_storey(surf, cx, wall_top, bw, th, palette):
    """One narrow Kaifeng storey: glazed-tile body, narrow shallow eave."""
    if bw < 8 or th < 5:
        return
    body_rect = pygame.Rect(cx - bw // 2, wall_top, bw, th)
    _glazed_tile_checker(surf, body_rect.x, body_rect.y,
                         body_rect.w, body_rect.h, palette, tile=4)
    # Narrow lit-rim window centred on each storey — small inset opening.
    if th >= 8 and bw >= 10:
        _lit_niche(surf, cx, wall_top + 2,
                   min(4, bw // 3), min(5, th - 3), palette)
    # Architrave band on the bottom edge — slightly darker brown line
    # so the storey-edge reads as a structural break.
    pygame.draw.rect(surf, _iron_brown_shadow(palette),
                     (cx - bw // 2, wall_top + th - 2, bw, 2))


def _draw_iron_kaifeng_eave(surf, cx, y_base, half_w, palette, *, depth=3):
    """Shallow gray-tile eave — Kaifeng's eaves are slimmer than Fogong's
    larch eaves, more like dark capping bands. Each eave has a 1-px lit
    rim and a single hooked tile-end at both corners."""
    iron_lit = _iron_brown_lit(palette)
    iron_dark = _iron_brown_shadow(palette)
    overhang = 3
    half_outer = half_w + overhang
    pygame.draw.rect(surf, iron_dark,
                     (cx - half_outer, y_base, half_outer * 2, depth))
    pygame.draw.line(surf, iron_lit,
                     (cx - half_outer + 1, y_base),
                     (cx + half_outer - 1, y_base), 1)
    # Slight up-tick at each corner so it reads as a Chinese eave.
    pygame.draw.line(surf, iron_lit,
                     (cx - half_outer, y_base),
                     (cx - half_outer - 1, y_base - 1), 1)
    pygame.draw.line(surf, iron_lit,
                     (cx + half_outer, y_base),
                     (cx + half_outer + 1, y_base - 1), 1)


def _draw_iron_kaifeng(surf, top_rect, bot_rect, palette, seed):
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2

    def stack(cx, y_top, y_bot, base_w, *, n_storeys, finial_up):
        total_h = y_bot - y_top
        if total_h < 30:
            return
        # Plinth at the base (if upright) or ceiling cap (if mirrored).
        if finial_up:
            plinth_h = 8
            plinth_w = int(base_w * 1.18)
            pygame.draw.rect(surf, _shade(palette['stone_dark'], -10),
                             (cx - plinth_w // 2, y_bot - plinth_h,
                              plinth_w, plinth_h))
            pygame.draw.rect(surf, _column_grey(palette),
                             (cx - plinth_w // 2 + 1,
                              y_bot - plinth_h + 1,
                              plinth_w - 2, plinth_h - 2))
            pygame.draw.rect(surf, palette['stone_light'],
                             (cx - plinth_w // 2,
                              y_bot - plinth_h, plinth_w, 2))
            y_bot -= plinth_h
        else:
            # Ceiling cap — anchor block the mirrored pagoda hangs from.
            cap_h = 7
            cap_w = int(base_w * 1.22)
            pygame.draw.rect(surf, _shade(palette['stone_dark'], -10),
                             (cx - cap_w // 2, y_top, cap_w, cap_h))
            pygame.draw.rect(surf, _column_grey(palette),
                             (cx - cap_w // 2 + 1, y_top + 1,
                              cap_w - 2, cap_h - 2))
            pygame.draw.rect(surf, palette['stone_light'],
                             (cx - cap_w // 2,
                              y_top + cap_h - 1, cap_w, 1))
            y_top += cap_h
        # Finial budget at the tip.
        finial_h = 18
        body_h = (y_bot - y_top) - finial_h
        if body_h < 30:
            return
        storey_h = body_h // n_storeys
        if storey_h < 4:
            n_storeys = max(4, body_h // 5)
            storey_h = body_h // n_storeys
        # The Iron Pagoda tapers gently — top 88% of base width.
        widths = [max(10, int(base_w * (1 - 0.12 * (k / max(1, n_storeys - 1)))))
                  for k in range(n_storeys)]
        if finial_up:
            # Upright stack — widest at y_bot, narrowing upward.
            y_cursor = y_bot
            for k in range(n_storeys):
                bw = widths[k]
                wall_top = y_cursor - storey_h + 1
                _draw_iron_kaifeng_storey(surf, cx, wall_top, bw,
                                          storey_h - 2, palette)
                _draw_iron_kaifeng_eave(surf, cx, wall_top - 1, bw // 2,
                                        palette, depth=2)
                y_cursor = wall_top - 2
            top_w = widths[-1]
            cap_y = y_cursor - 3
        else:
            # Mirrored — widest storey AT the ceiling (y_top), tapering DOWN
            # into the gap. The narrowest storey ends near y_bot with the
            # finial dropping past y_bot.
            y_cursor = y_top
            for k in range(n_storeys):
                bw = widths[k]
                wall_top = y_cursor + 1
                _draw_iron_kaifeng_storey(surf, cx, wall_top, bw,
                                          storey_h - 2, palette)
                # Eave sits BELOW the storey on the mirrored copy.
                _draw_iron_kaifeng_eave(surf, cx, wall_top + storey_h - 2,
                                        bw // 2, palette, depth=2)
                y_cursor = wall_top + storey_h
            top_w = widths[-1]
            cap_y = y_cursor + 3
        # Curved cap dome.
        cap_rect = pygame.Rect(cx - top_w // 3, cap_y - 5,
                               (top_w // 3) * 2, 9)
        pygame.draw.ellipse(surf, _iron_brown_shadow(palette), cap_rect)
        pygame.draw.ellipse(surf, _iron_brown_lit(palette),
                            cap_rect.inflate(-2, -2))
        bronze = _bronze(palette)
        bright = _shade(bronze, 45)
        dark = palette['stone_dark']
        base_y = cap_y - 4 if finial_up else cap_y + 4
        dir_sign = -1 if finial_up else 1
        needle_tip = base_y + dir_sign * finial_h
        pygame.draw.line(surf, dark,
                         (cx - 1, base_y),
                         (cx - 1, needle_tip), 2)
        pygame.draw.line(surf, bronze,
                         (cx, base_y), (cx, needle_tip), 1)
        for k in range(2):
            ry = base_y + dir_sign * (4 + k * 6)
            rw = max(2, 5 - k * 2)
            pygame.draw.ellipse(surf, dark, (cx - rw - 1, ry - 1,
                                            rw * 2 + 2, 3))
            pygame.draw.ellipse(surf, bronze, (cx - rw, ry, rw * 2, 2))
        pygame.draw.circle(surf, dark, (cx, needle_tip), 3)
        pygame.draw.circle(surf, bright, (cx, needle_tip), 2)

    if bot_rect.height > 80:
        stack(bcx, bot_rect.y, bot_rect.bottom,
              int(bot_rect.width * 0.88),
              n_storeys=rng.choice([12, 13]),
              finial_up=True)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 6, 14, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 6, seed=seed)

    if top_rect.height > 60:
        # Top 5 storeys mirrored from the ceiling. We draw a fresh stack
        # of 5 storeys with the bottom of the stack against `top_rect.y`
        # and the finial pointing down past `top_rect.bottom`.
        stack(tcx, top_rect.y, top_rect.bottom,
              int(top_rect.width * 0.86),
              n_storeys=5,
              finial_up=False)
        # Hanging moss off the ceiling root.
        for off in (-10, -2, 6, 14):
            draw_moss_strand(surf, tcx + off, top_rect.y + 4,
                             5 + abs(off) % 3, palette,
                             jitter_seed=seed + off)


def candidate_iron_kaifeng(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('iron_kaifeng', _draw_iron_kaifeng, surf, top_rect, bot_rect,
                 palette, seed)


# ── 8. Chùa Một Cột — One Pillar Pagoda ────────────────────────────────────
#
# A small Vietnamese wooden pavilion (Liên Hoa Đài) perched on a single
# tall stone column rising from a square lotus pond. The pavilion is
# tiny relative to the column — that proportional inversion is the
# whole point. Lotus petals fan out from the column root above the pond.
# Top = a smaller upside-down lotus pavilion hangs from the ceiling on
# a thinner column.
#
# Reference: https://en.wikipedia.org/wiki/One_Pillar_Pagoda

def _draw_vn_pavilion(surf, cx, base_y, palette, *, body_w=30, body_h=22,
                     roof_up=True):
    """The Liên Hoa Đài — a square wooden pavilion with a curved
    Vietnamese ceramic-tile roof. Two dragon-finials curl off the corners
    where the roof peaks."""
    wood = _ochre_wood(palette)
    wood_lit = _ochre_wood_lit(palette)
    wood_dark = _ochre_wood_shadow(palette)
    tile = _vn_tile_red(palette)
    tile_lit = _vn_tile_red_lit(palette)
    tile_dark = _shade(tile, -45)
    accent = _bronze(palette)
    plaster = _white_plaster_warm(palette)

    if body_w < 10 or body_h < 6:
        return
    # Wooden body box.
    wall_rect = pygame.Rect(cx - body_w // 2, base_y - body_h,
                            body_w, body_h)
    _gradient_rect(surf, wall_rect, wood_lit, wood, wood_dark)
    # Plaster panel centred — a small altar opening.
    if body_w >= 14 and body_h >= 10:
        pp = pygame.Rect(cx - body_w // 2 + 3, base_y - body_h + 3,
                         body_w - 6, body_h - 5)
        _gradient_rect(surf, pp, _shade(plaster, 20), plaster,
                       _shade(plaster, -25))
        # Lit-rim door arch — Vietnamese style with a pointed top.
        door_w = min(pp.w - 4, 7)
        door_h = min(pp.h - 2, 10)
        dx0 = cx - door_w // 2
        dy0 = base_y - door_h - 1
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -40),
                         (dx0, dy0, door_w, door_h))
        rim_alpha = 220 if _is_dark_sky(palette) else 110
        rim = _mix(palette['stone_accent'], (255, 215, 120), 0.78)
        rim_layer = pygame.Surface((door_w + 2, door_h + 2), pygame.SRCALPHA)
        pygame.draw.rect(rim_layer, (*rim, rim_alpha),
                         (1, 1, door_w, door_h), 1)
        surf.blit(rim_layer, (dx0 - 1, dy0 - 1))
    # Wood corner posts + lit edges.
    for px in (cx - body_w // 2, cx + body_w // 2 - 2):
        pygame.draw.rect(surf, wood_dark, (px, base_y - body_h, 2, body_h))
        pygame.draw.line(surf, wood_lit,
                         (px, base_y - body_h),
                         (px, base_y - 1), 1)
    # Architrave beam on top.
    pygame.draw.rect(surf, wood_dark,
                     (cx - body_w // 2, base_y - body_h, body_w, 2))

    # Curved Vietnamese tile roof — the signature dragon-eave that flips
    # up on all 4 corners. We draw a wide trapezoidal mass with sharply
    # upturned tips.
    roof_h = max(8, body_h // 2 + 4)
    roof_overhang = max(8, body_w // 3)
    if roof_up:
        ridge_y = base_y - body_h - roof_h
        eave_y = base_y - body_h - 1
        tip_y = ridge_y + 1
    else:
        # Upside-down roof — the curved tips drop into the gap below.
        ridge_y = base_y - body_h + roof_h
        eave_y = base_y - body_h + 1
        tip_y = ridge_y - 1
    half_outer = body_w // 2 + roof_overhang
    # Roof shadow polygon (slightly larger).
    roof_pts = [
        (cx - half_outer, eave_y),
        (cx - half_outer + 2, tip_y),
        (cx - body_w // 2 - 2,
         eave_y + (-2 if roof_up else 2)),
        (cx, ridge_y),
        (cx + body_w // 2 + 2,
         eave_y + (-2 if roof_up else 2)),
        (cx + half_outer - 2, tip_y),
        (cx + half_outer, eave_y),
    ]
    pygame.draw.polygon(surf, tile_dark, roof_pts)
    inner_pts = [
        (cx - half_outer + 1, eave_y + (1 if roof_up else -1)),
        (cx, ridge_y + (1 if roof_up else -1)),
        (cx + half_outer - 1, eave_y + (1 if roof_up else -1)),
    ]
    pygame.draw.polygon(surf, tile, [(cx - half_outer + 1, eave_y),
                                     *inner_pts, (cx + half_outer - 1, eave_y)])
    # Per-row tile hatching down both slopes.
    _tile_hatch(surf, cx - half_outer + 3, eave_y - (3 if roof_up else -3),
                cx - 2, ridge_y + (3 if roof_up else -3),
                _shade(tile, -30), step=3)
    _tile_hatch(surf, cx + 2, ridge_y + (3 if roof_up else -3),
                cx + half_outer - 3, eave_y - (3 if roof_up else -3),
                _shade(tile, -30), step=3)
    # Ridge highlight.
    pygame.draw.line(surf, tile_lit,
                     (cx - body_w // 4, ridge_y + (1 if roof_up else -1)),
                     (cx + body_w // 4, ridge_y + (1 if roof_up else -1)), 1)
    # AA the silhouette.
    _aa_polyline(surf, tile_dark, roof_pts, closed=True)
    # Dragon-finials curling up off each corner tip.
    curl_dir = -1 if roof_up else 1
    for tx in (cx - half_outer, cx + half_outer):
        pygame.draw.polygon(surf, accent,
                            [(tx, tip_y),
                             (tx + (-2 if tx < cx else 2),
                              tip_y + curl_dir * 4),
                             (tx + (-3 if tx < cx else 3),
                              tip_y + curl_dir * 2)])
        pygame.draw.circle(surf, _shade(accent, 40),
                           (tx + (-3 if tx < cx else 3),
                            tip_y + curl_dir * 2), 1)
    # Central ridge ornament — small bronze flame jewel.
    pygame.draw.circle(surf, accent,
                       (cx, ridge_y + (-3 if roof_up else 3)), 2)
    pygame.draw.line(surf, _shade(accent, 40),
                     (cx, ridge_y + (-7 if roof_up else 7)),
                     (cx, ridge_y + (-4 if roof_up else 4)), 1)


def _draw_one_pillar(surf, top_rect, bot_rect, palette, seed):
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2

    pond_aqua = _pond_aqua(palette)
    pond_deep = _shade(pond_aqua, -30)
    pond_lit = _shade(pond_aqua, 25)
    grey = _column_grey(palette)
    grey_dark = _shade(grey, -35)
    grey_lit = _shade(grey, 25)

    if bot_rect.height > 80:
        # Square lotus pond at the base — a flat rectangle stretching the
        # full width of bot_rect with a 3-step gradient so it reads as
        # water. Inset a darker ring so the pond has visible edges.
        pond_h = 22
        pond_top = bot_rect.bottom - pond_h
        pond_w = int(bot_rect.width * 1.40)
        pond_rect = pygame.Rect(bcx - pond_w // 2, pond_top, pond_w, pond_h)
        # Stone rim.
        pygame.draw.rect(surf, grey_dark,
                         (pond_rect.x - 2, pond_rect.y - 2,
                          pond_rect.w + 4, pond_rect.h + 4))
        pygame.draw.rect(surf, grey,
                         (pond_rect.x - 1, pond_rect.y - 1,
                          pond_rect.w + 2, pond_rect.h + 2))
        # Water gradient — lit near the top.
        _gradient_rect(surf, pond_rect, pond_lit, pond_aqua, pond_deep,
                       vertical=True)
        # Water ripples — 3 short horizontal accents.
        for k, off_y in enumerate((-7, -2, 4)):
            ry = pond_top + pond_h // 2 + off_y
            rx0 = bcx - pond_w // 2 + 8 + (k * 7) % 14
            pygame.draw.line(surf, pond_lit,
                             (rx0, ry), (rx0 + 14, ry), 1)
        # Tall slim stone column rising out of the pond — the whole
        # silhouette's identity.
        col_h = bot_rect.height - pond_h - 36
        if col_h > 30:
            col_w = 14
            col_top = pond_top - col_h
            col_rect = pygame.Rect(bcx - col_w // 2, col_top, col_w, col_h)
            # 3-stop column gradient — lit left, shadow right.
            _gradient_rect(surf, col_rect, grey_lit, grey, grey_dark)
            # Vertical grooves — Vietnamese stone columns are fluted.
            for gx in (bcx - col_w // 2 + 3, bcx, bcx + col_w // 2 - 3):
                pygame.draw.line(surf, grey_dark,
                                 (gx, col_top + 2),
                                 (gx, pond_top - 2), 1)
            # Lotus petals fan UP at the column root — the iconic Liên
            # Hoa Đài cushion.
            _lotus_petal_fan(surf, bcx, col_top + 2,
                             radius=20, palette=palette,
                             n_petals=11, arc=math.pi)
            # Tiny outer fan — a second smaller petal ring underneath
            # for added depth.
            _lotus_petal_fan(surf, bcx, col_top + 4,
                             radius=12, palette=palette,
                             n_petals=7, arc=math.pi * 0.85)
            # Pavilion sits on the column top.
            pav_w = max(28, int(bot_rect.width * 0.86))
            pav_h = 24
            _draw_vn_pavilion(surf, bcx, col_top - 2, palette,
                              body_w=pav_w, body_h=pav_h, roof_up=True)
        draw_grass_bed(surf, bcx, pond_rect.y - 1,
                       bot_rect.width + 4, 8, palette, seed=seed)

    if top_rect.height > 50:
        # Hanging upside-down pavilion: thinner column drops from the
        # ceiling, dragon-eave pavilion hangs at its tip with a small
        # downward lotus.
        anchor_w = int(top_rect.width * 0.7)
        anchor_h = 6
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -10),
                         (tcx - anchor_w // 2, top_rect.y,
                          anchor_w, anchor_h))
        pygame.draw.rect(surf, grey,
                         (tcx - anchor_w // 2 + 1, top_rect.y + 1,
                          anchor_w - 2, anchor_h - 2))
        col_w = 10
        col_h = min(top_rect.height - 36, 36)
        col_top = top_rect.y + anchor_h
        col_bot = col_top + col_h
        col_rect = pygame.Rect(tcx - col_w // 2, col_top, col_w, col_h)
        _gradient_rect(surf, col_rect, grey_lit, grey, grey_dark)
        for gx in (tcx - col_w // 2 + 2, tcx + col_w // 2 - 3):
            pygame.draw.line(surf, grey_dark,
                             (gx, col_top + 1),
                             (gx, col_bot - 1), 1)
        # Upside-down lotus petals fan DOWN from the column tip.
        _lotus_petal_fan(surf, tcx, col_bot,
                         radius=14, palette=palette,
                         n_petals=9, arc=math.pi)
        # Pavilion roof points DOWN — `roof_up=False` flips the dragon
        # eaves so they curl into the gap.
        pav_w = max(22, int(top_rect.width * 0.74))
        pav_h = 18
        _draw_vn_pavilion(surf, tcx, col_bot + pav_h + 1, palette,
                          body_w=pav_w, body_h=pav_h, roof_up=False)


def candidate_one_pillar(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('one_pillar', _draw_one_pillar, surf, top_rect, bot_rect,
                 palette, seed)


# ── 9. Borobudur — Stepped Mandala Pyramid ─────────────────────────────────
#
# Five square stepped terraces topped by three concentric circular
# terraces of perforated bell-shaped stupas, crowned by a single
# chattra-topped stupa. Volcanic-basalt grey throughout. Triangular
# silhouette mass; reads as the heaviest, most monumental candidate.
# Top = a single bell-stupa with chattra hanging from ceiling chains.
#
# Reference: https://en.wikipedia.org/wiki/Borobudur

def _draw_borobudur_bell_stupa(surf, cx, cy, palette, *, rx=8, ry=10,
                               with_chattra=True):
    """A single perforated bell stupa — vertical egg-shape with a hex
    lattice perforation pattern and an optional 3-tier chattra spire."""
    base = _basalt(palette)
    lit = _basalt_lit(palette)
    shadow = _basalt_shadow(palette)
    dark = palette['stone_dark']
    # Bell silhouette — slightly wider at base, narrow at top.
    bell_rect = pygame.Rect(cx - rx, cy - ry, rx * 2, ry * 2)
    pygame.draw.ellipse(surf, shadow, bell_rect)
    pygame.draw.ellipse(surf, base, bell_rect.inflate(-2, -2))
    # Lit sliver on the upper-left.
    pygame.draw.arc(surf, lit, bell_rect.inflate(-1, -1),
                    math.pi * 0.65, math.pi * 1.10, 1)
    # Hex perforations.
    _hex_lattice(surf, cx, cy, rx, ry, palette, holes=7)
    # AA silhouette.
    arc_pts = []
    for k in range(13):
        t = k / 12
        ang = math.pi + t * math.pi
        px = cx + math.cos(ang) * rx
        py = cy - math.sin(ang) * ry
        arc_pts.append((int(px), int(py)))
    _aa_polyline(surf, dark, arc_pts)
    if with_chattra:
        # 3-tier chattra umbrella on top.
        tip_y = cy - ry - 6
        pygame.draw.line(surf, dark, (cx - 1, cy - ry),
                         (cx - 1, tip_y), 2)
        pygame.draw.line(surf, lit, (cx, cy - ry),
                         (cx, tip_y), 1)
        for k, ry_off in enumerate((-1, -3, -5)):
            rwc = max(2, 5 - k)
            ry2 = cy - ry + ry_off
            pygame.draw.line(surf, dark, (cx - rwc, ry2 + 1),
                             (cx + rwc, ry2 + 1), 1)
            pygame.draw.line(surf, lit, (cx - rwc, ry2),
                             (cx + rwc, ry2), 1)
        pygame.draw.circle(surf, dark, (cx, tip_y - 1), 2)
        pygame.draw.circle(surf, lit, (cx, tip_y - 1), 1)


def _draw_borobudur(surf, top_rect, bot_rect, palette, seed):
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2

    base = _basalt(palette)
    lit = _basalt_lit(palette)
    shadow = _basalt_shadow(palette)
    accent = _basalt_accent(palette)
    dark = palette['stone_dark']

    if bot_rect.height > 80:
        # 5 square stepped terraces stacked widest-to-narrowest, then
        # 3 circular terraces of perforated bell stupas, then a crowning
        # central bell-stupa with chattra.
        total_h = min(bot_rect.height, 250)
        sq_h = int(total_h * 0.48)
        circ_h = int(total_h * 0.34)
        crown_h = total_h - sq_h - circ_h
        base_y = bot_rect.bottom

        # Square stepped terraces — 5 tiers.
        widest = int(bot_rect.width * 1.55)
        narrowest = int(bot_rect.width * 0.78)
        n_sq = 5
        step_h = sq_h // n_sq
        for i in range(n_sq):
            t = i / max(1, n_sq - 1)
            sw = int(widest + (narrowest - widest) * t)
            sy = base_y - sq_h + i * step_h
            # Step body with horizontal gradient (lit left → shadow right).
            srect = pygame.Rect(bcx - sw // 2, sy, sw, step_h)
            _gradient_rect(surf, srect, lit, base, shadow)
            # Top dark cap-line so each terrace reads as a horizontal slab.
            pygame.draw.rect(surf, dark, (srect.x, srect.y, srect.w, 1))
            pygame.draw.rect(surf, _shade(base, -20),
                             (srect.x, srect.bottom - 2, srect.w, 2))
            # Recessed relief-panel band along the front face — sculpted
            # Mahayana panels at Borobudur's bas-relief band. We draw a
            # row of small dark rectangles separated by thin pilasters.
            if sw >= 30 and step_h >= 8:
                panel_zone = sw - 12
                n_panels = max(3, panel_zone // 14)
                pw = panel_zone // n_panels
                for pi in range(n_panels):
                    px0 = srect.x + 6 + pi * pw
                    panel = pygame.Rect(px0, sy + 2,
                                        max(4, pw - 2), step_h - 5)
                    pygame.draw.rect(surf, accent, panel)
                    pygame.draw.rect(surf, _shade(accent, -25),
                                     (panel.x, panel.y, panel.w, 1))
                    pygame.draw.rect(surf, _shade(base, 25),
                                     (panel.x, panel.y, 1, panel.h))
                    # Tiny seated-buddha silhouette polygon in the panel
                    # centre — a 4-px rounded blob with a halo dot.
                    if pw >= 8 and step_h >= 12:
                        bx = panel.x + panel.w // 2
                        by = panel.y + panel.h // 2 + 1
                        pygame.draw.circle(surf, _shade(base, 35),
                                           (bx, by - 3), 2)
                        pygame.draw.polygon(surf, _shade(base, 35),
                                            [(bx - 2, by + 2),
                                             (bx + 2, by + 2),
                                             (bx + 1, by - 1),
                                             (bx - 1, by - 1)])
            # Lit-rim niche in the central staircase position on bottom 2.
            if i < 2 and sw >= 30:
                _lit_niche(surf, bcx, sy + 2,
                           min(8, sw - 12), min(6, step_h - 4), palette)

        # 3 circular terraces of perforated bell stupas. Each terrace =
        # a horizontal row of bells with depth-shifted shading. Stupas
        # get smaller and fewer toward the crown.
        circ_top = base_y - sq_h - circ_h
        for ci, n_stupas in enumerate((5, 4, 3)):
            tier_y = base_y - sq_h - int(circ_h * (ci + 0.5) / 3)
            tier_w = int(narrowest + (narrowest * 0.18) * (2 - ci))
            spacing = tier_w // max(1, n_stupas)
            rx = max(4, min(7, spacing // 2 - 1))
            ry = max(5, min(8, int(rx * 1.3)))
            for s in range(n_stupas):
                t = (s + 0.5) / n_stupas
                sx = bcx - tier_w // 2 + int(t * tier_w)
                _draw_borobudur_bell_stupa(surf, sx, tier_y, palette,
                                           rx=rx, ry=ry,
                                           with_chattra=False)
            # Floor of the circular terrace — short dark band the bells
            # sit on, so the terrace reads as a deck not a void.
            deck_y = tier_y + ry + 1
            pygame.draw.rect(surf, base,
                             (bcx - tier_w // 2 - 4, deck_y,
                              tier_w + 8, 3))
            pygame.draw.line(surf, dark,
                             (bcx - tier_w // 2 - 4, deck_y),
                             (bcx + tier_w // 2 + 4, deck_y), 1)

        # Crowning central stupa with chattra.
        crown_cx = bcx
        crown_cy = circ_top + crown_h // 2 - 2
        _draw_borobudur_bell_stupa(surf, crown_cx, crown_cy, palette,
                                   rx=8, ry=11, with_chattra=True)

        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 12, 10, palette, seed=seed)

    if top_rect.height > 50:
        # Single hanging bell stupa with chattra dropping into the gap on
        # a pair of dark chains from a basalt anchor block.
        anchor_w = int(top_rect.width * 0.9)
        anchor_h = 8
        anchor_rect = pygame.Rect(tcx - anchor_w // 2, top_rect.y,
                                  anchor_w, anchor_h)
        pygame.draw.rect(surf, dark, anchor_rect)
        _gradient_rect(surf, anchor_rect.inflate(-2, -2),
                       lit, base, shadow)
        pygame.draw.rect(surf, _basalt_lit(palette),
                         (anchor_rect.x + 2, anchor_rect.y + 1,
                          anchor_rect.w - 4, 1))
        # Two chains.
        chain_top = top_rect.y + anchor_h
        chain_bot = min(top_rect.bottom - 24,
                        top_rect.y + anchor_h + 26)
        for cx_off in (-6, 6):
            cx_chain = tcx + cx_off
            pygame.draw.line(surf, dark,
                             (cx_chain, chain_top),
                             (cx_chain, chain_bot), 2)
            for cy in range(chain_top + 2, chain_bot, 4):
                pygame.draw.ellipse(surf, dark,
                                    (cx_chain - 2, cy - 1, 5, 4))
                pygame.draw.ellipse(surf, base,
                                    (cx_chain - 1, cy, 3, 2))
        # Bell stupa with chattra at the tip — drawn upside-up so the
        # chattra reads even when hanging.
        bell_cy = chain_bot + 11
        _draw_borobudur_bell_stupa(surf, tcx, bell_cy, palette,
                                   rx=10, ry=12, with_chattra=False)
        # Decorative downward chattra cone hanging UNDER the bell — three
        # tiered umbrella rings tapering down into the gap.
        for k in range(3):
            ry_off = bell_cy + 12 + k * 4
            rwc = max(2, 6 - k * 2)
            pygame.draw.line(surf, dark, (tcx - rwc, ry_off + 1),
                             (tcx + rwc, ry_off + 1), 1)
            pygame.draw.line(surf, lit, (tcx - rwc, ry_off),
                             (tcx + rwc, ry_off), 1)
        # Final ball drop.
        pygame.draw.circle(surf, dark, (tcx, bell_cy + 26), 2)
        pygame.draw.circle(surf, lit, (tcx, bell_cy + 26), 1)


def candidate_borobudur(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('borobudur', _draw_borobudur, surf, top_rect, bot_rect,
                 palette, seed)


# ── 10. Pha That Luang — Lao Golden Stupa ──────────────────────────────────
#
# Stepped pyramidal base + square second tier with corner spire chapels +
# bulbous lotus-bud crowning spire. Gold throughout with a cream-white
# base and lacquer-red trim bands. Reads gold like Shwedagon but the
# silhouette is the Laotian lotus-bud cone vs the Burmese rounded bell.
# Top = a hanging gold spire chapel pendant from a gold chain.
#
# Reference: https://en.wikipedia.org/wiki/Pha_That_Luang

def _draw_lotus_bud_spire(surf, cx, base_y, tip_y, palette, *, w=10):
    """The signature Lao lotus-bud stupa spire — a tall pointed bud with
    a bulbous base, ridged vertical seams, and a tiny finial flower."""
    gold = _gold_laos(palette)
    gold_d = _gold_laos_deep(palette)
    bright = _gold_laos_bright(palette)
    dark = palette['stone_dark']
    h = base_y - tip_y
    if h < 12:
        return
    # 3-section silhouette: bulbous belly (60% h), tapered neck (30%),
    # tiny finial (10%).
    belly_h = int(h * 0.60)
    neck_h = int(h * 0.30)
    finial_h = h - belly_h - neck_h

    # Belly — elongated teardrop.
    belly_pts = []
    for k in range(13):
        t = k / 12
        ang = math.pi * t
        bx = cx + math.cos(ang + math.pi) * (w / 2 + 1)
        by = base_y - int(math.sin(ang) * belly_h)
        belly_pts.append((int(bx), by))
    # Mirror down to base.
    belly_full = belly_pts + [(cx + w // 2, base_y), (cx - w // 2, base_y)]
    pygame.draw.polygon(surf, dark, belly_full)
    inner_belly = []
    for k in range(13):
        t = k / 12
        ang = math.pi * t
        bx = cx + math.cos(ang + math.pi) * (w / 2 - 0.5)
        by = base_y - int(math.sin(ang) * (belly_h - 2))
        inner_belly.append((int(bx), by))
    inner_full = inner_belly + [(cx + w // 2 - 1, base_y),
                                (cx - w // 2 + 1, base_y)]
    pygame.draw.polygon(surf, gold_d, inner_full)
    # Lit gradient stripe down the left side of belly.
    for k in range(7):
        t = k / 6
        ang = math.pi * (0.55 + t * 0.20)
        bx = cx + math.cos(ang + math.pi) * (w / 2 - 1)
        by = base_y - int(math.sin(ang) * (belly_h - 2))
        pygame.draw.line(surf, gold,
                         (int(bx), by), (int(bx), by), 1)
        pygame.draw.line(surf, bright,
                         (int(bx) - 1, by), (int(bx), by), 1)
    # AA the belly silhouette.
    _aa_polyline(surf, dark, belly_pts)

    # Neck — narrowing column.
    neck_top_y = base_y - belly_h - neck_h
    nw = max(3, w - 4)
    for k in range(neck_h):
        t = k / max(1, neck_h - 1)
        lw = int(nw - t * 2)
        ny = base_y - belly_h - k
        col = gold if k % 2 == 0 else gold_d
        pygame.draw.line(surf, col,
                         (cx - lw // 2, ny), (cx + lw // 2, ny), 1)
    # Neck rim rings — 3 horizontal gold disks for ornament.
    for k in range(3):
        ry = base_y - belly_h - int(neck_h * (k + 1) / 4)
        rw = max(2, nw - 1)
        pygame.draw.line(surf, dark, (cx - rw, ry + 1),
                         (cx + rw, ry + 1), 1)
        pygame.draw.line(surf, bright, (cx - rw, ry),
                         (cx + rw, ry), 1)

    # Finial — pointed tip flower.
    pygame.draw.polygon(surf, dark,
                        [(cx - 2, neck_top_y),
                         (cx + 2, neck_top_y),
                         (cx, tip_y)])
    pygame.draw.polygon(surf, bright,
                        [(cx - 1, neck_top_y),
                         (cx + 1, neck_top_y),
                         (cx, tip_y + 1)])
    # Tiny petal sun-rays around the finial base.
    for ang in (0, math.pi):
        gx = cx + int(math.cos(ang) * 3)
        gy = neck_top_y + 2
        pygame.draw.line(surf, bright, (cx, neck_top_y + 1),
                         (gx, gy), 1)


def _draw_pha_that_luang(surf, top_rect, bot_rect, palette, seed):
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2

    gold = _gold_laos(palette)
    gold_d = _gold_laos_deep(palette)
    bright = _gold_laos_bright(palette)
    cream = _cream_base(palette)
    cream_lit = _shade(cream, 25)
    cream_dark = _shade(cream, -28)
    red = _lacquer_red(palette)
    dark = palette['stone_dark']

    if bot_rect.height > 80:
        total_h = min(bot_rect.height, 250)
        # Budget: 26% cream pyramidal base, 30% square second tier with
        # corner chapels, 44% main lotus-bud spire.
        base_h = int(total_h * 0.26)
        sq_h = int(total_h * 0.30)
        spire_h = total_h - base_h - sq_h

        base_y_bot = bot_rect.bottom
        # ── Cream stepped pyramidal base ──────────────────────────────
        n_base = 3
        step_h = base_h // n_base
        widest = int(bot_rect.width * 1.35)
        narrowest = int(bot_rect.width * 1.00)
        for i in range(n_base):
            t = i / max(1, n_base - 1)
            sw = int(widest + (narrowest - widest) * t)
            sy = base_y_bot - base_h + i * step_h
            srect = pygame.Rect(bcx - sw // 2, sy, sw, step_h)
            _gradient_rect(surf, srect, cream_lit, cream, cream_dark)
            # Lacquer-red trim band along the top of every base step —
            # the canonical Lao band cue.
            pygame.draw.rect(surf, red,
                             (srect.x + 2, srect.y + 1, srect.w - 4, 2))
            pygame.draw.rect(surf, _shade(red, 25),
                             (srect.x + 2, srect.y + 1, srect.w - 4, 1))
            # Gold lotus-petal frieze — small repeating triangles along
            # the top edge of the second step (Pha That Luang's central
            # frieze is 30 lotus petals).
            if i == 1 and sw >= 28:
                n_petals = max(7, sw // 6)
                pw = sw // n_petals
                for pi in range(n_petals):
                    px0 = srect.x + 2 + pi * pw
                    pygame.draw.polygon(surf, gold_d,
                                        [(px0, srect.y + 4),
                                         (px0 + pw // 2, srect.y + 1),
                                         (px0 + pw, srect.y + 4)])
                    pygame.draw.polygon(surf, gold,
                                        [(px0 + 1, srect.y + 4),
                                         (px0 + pw // 2, srect.y + 2),
                                         (px0 + pw - 1, srect.y + 4)])
            # Lit-rim niche on the widest step's centre.
            if i == 0 and sw >= 30 and step_h >= 7:
                _lit_niche(surf, bcx, sy + 2,
                           min(8, sw - 12), min(5, step_h - 4), palette)
            # AA the keyline.
            pygame.draw.line(surf, _shade(cream_dark, -20),
                             (srect.x, srect.bottom - 1),
                             (srect.right - 1, srect.bottom - 1), 1)

        # ── Square second tier with corner spire chapels ─────────────
        sq_top = base_y_bot - base_h - sq_h
        sq_w = int(bot_rect.width * 0.92)
        sq_rect = pygame.Rect(bcx - sq_w // 2, sq_top, sq_w, sq_h)
        # Gold square body with a vertical gradient (lit at the top).
        _gradient_rect(surf, sq_rect, bright, gold, gold_d, vertical=True)
        # Lacquer-red border frame.
        pygame.draw.rect(surf, red, sq_rect, 2)
        # Inner gold tile rows — 3 horizontal stripes for ornament.
        for k in range(3):
            ry = sq_top + 4 + k * max(3, (sq_h - 8) // 3)
            pygame.draw.line(surf, gold_d,
                             (sq_rect.x + 4, ry),
                             (sq_rect.right - 5, ry), 1)
            pygame.draw.line(surf, bright,
                             (sq_rect.x + 4, ry - 1),
                             (sq_rect.right - 5, ry - 1), 1)
        # Central niche.
        if sq_w >= 20 and sq_h >= 12:
            _lit_niche(surf, bcx, sq_top + 3,
                       min(8, sq_w - 14), min(sq_h - 6, 9), palette)

        # 4 visible corner spire chapels (small lotus-bud stupas at each
        # corner of the second tier — Pha That Luang has 30 smaller
        # stupas around the central spire; we condense to a visible pair
        # at PIPE_W = 58).
        chapel_offsets = (-sq_w // 2 + 4, sq_w // 2 - 4)
        for off in chapel_offsets:
            chx = bcx + off
            chapel_top = sq_top - 18
            # Mini lotus-bud spire.
            _draw_lotus_bud_spire(surf, chx, sq_top - 1, chapel_top,
                                  palette, w=6)

        # ── Main lotus-bud spire ─────────────────────────────────────
        spire_base_y = sq_top - 1
        spire_tip_y = spire_base_y - spire_h
        # Octagonal lantern pedestal under the spire — a short ring of
        # gold blocks the spire rises out of.
        lantern_h = 6
        lantern_w = int(sq_w * 0.42)
        lr = pygame.Rect(bcx - lantern_w // 2, spire_base_y - lantern_h + 1,
                         lantern_w, lantern_h)
        _gradient_rect(surf, lr, bright, gold, gold_d, vertical=True)
        pygame.draw.rect(surf, red,
                         (lr.x + 2, lr.bottom - 2, lr.w - 4, 1))
        pygame.draw.rect(surf, dark, lr, 1)
        _draw_lotus_bud_spire(surf, bcx, spire_base_y - lantern_h + 1,
                              spire_tip_y, palette, w=14)

        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 10, 12, palette, seed=seed)

    if top_rect.height > 50:
        # Hanging gold spire pendant — a smaller upside-down lotus-bud
        # spire chapel suspended from a gold chain.
        anchor_w = int(top_rect.width * 0.9)
        anchor_h = 8
        anchor_rect = pygame.Rect(tcx - anchor_w // 2, top_rect.y,
                                  anchor_w, anchor_h)
        pygame.draw.rect(surf, dark, anchor_rect)
        _gradient_rect(surf, anchor_rect.inflate(-2, -2),
                       bright, gold, gold_d, vertical=True)
        pygame.draw.rect(surf, red,
                         (anchor_rect.x + 2, anchor_rect.bottom - 2,
                          anchor_rect.w - 4, 1))
        # Chain.
        chain_top = top_rect.y + anchor_h
        chain_bot = min(top_rect.bottom - 32,
                        top_rect.y + anchor_h + 22)
        pygame.draw.line(surf, dark, (tcx, chain_top), (tcx, chain_bot), 3)
        pygame.draw.line(surf, gold, (tcx, chain_top), (tcx, chain_bot), 1)
        for cy in range(chain_top + 2, chain_bot, 4):
            pygame.draw.ellipse(surf, dark, (tcx - 3, cy - 1, 7, 4))
            pygame.draw.ellipse(surf, gold, (tcx - 2, cy, 5, 2))
        # Upside-down spire — draw INTO a temp surface, flip vertically.
        spire_h = min(top_rect.bottom - chain_bot - 4, 50)
        if spire_h >= 16:
            tmp = pygame.Surface((28, spire_h + 6), pygame.SRCALPHA)
            _draw_lotus_bud_spire(tmp, tmp.get_width() // 2,
                                  spire_h + 2, 2,
                                  palette, w=10)
            flipped = pygame.transform.flip(tmp, False, True)
            surf.blit(flipped, (tcx - flipped.get_width() // 2,
                                chain_bot))


def candidate_pha_that_luang(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('pha_that_luang', _draw_pha_that_luang, surf, top_rect, bot_rect,
                 palette, seed)


# ── Round 8 — East-Asian pagoda atlas palette helpers ──────────────────────
#
# 10 new candidates inspired by the round-7 Hōryū-ji + Fogong baselines.
# Each below derives entirely from the live biome palette so day → night
# retint sweeps cleanly through. Raw RGB targets are archetype biases only.


def _toji_cypress(palette):
    # Tō-ji dark cypress (hinoki) — even darker than Hōryū-ji's cedar so the
    # monumental Edo-period mass reads as a sun-blackened cypress body
    # against any sky. Anchored in stone_dark with a deeper brown bias.
    return _mix(palette['stone_dark'], (58, 38, 26), 0.86)


def _toji_cypress_lit(palette):
    return _mix(palette['stone_mid'], (118, 80, 48), 0.70)


def _toji_cypress_shadow(palette):
    return _mix(palette['stone_dark'], (38, 24, 14), 0.90)


def _vermilion(palette):
    # Daigo-ji/Sensō-ji shu-iro vermilion lacquer — anchored in stone_dark
    # with a high-saturation red bias so the column lacquer reads as the
    # festival-temple red, not the cooler cedar brown of Hōryū-ji.
    return _mix(palette['stone_dark'], (188, 58, 48), 0.78)


def _vermilion_lit(palette):
    return _mix(palette['stone_accent'], (236, 108, 84), 0.78)


def _vermilion_shadow(palette):
    return _mix(palette['stone_dark'], (118, 28, 22), 0.86)


def _bluetile(palette):
    # Yakushi-ji bronze-tile glaze — warm dark slate with copper-bronze
    # bias so the famous bronze-and-cypress mass reads warm at night rather
    # than cool cement. Anchored in stone_dark, biased to oxidised bronze.
    return _mix(palette['stone_dark'], (108, 78, 56), 0.74)


def _bluetile_lit(palette):
    return _mix(palette['stone_mid'], (178, 138, 96), 0.62)


def _porcelain_white(palette):
    # Bao'en porcelain-glaze white — colder than Hōryū-ji's plaster, with
    # a faint cool blue cast so the porcelain tower separates from
    # Liaodi's bone-white and Kumbum's warm-sand under all phases.
    return _mix(palette['stone_light'], (232, 240, 248), 0.78)


def _porcelain_panel_pink(palette):
    return _mix(palette['stone_light'], (244, 200, 200), 0.66)


def _porcelain_panel_teal(palette):
    return _mix(palette['stone_light'], (160, 218, 216), 0.66)


def _porcelain_panel_gold(palette):
    return _mix(palette['stone_accent'], (246, 210, 110), 0.78)


def _porcelain_panel_cream(palette):
    return _mix(palette['stone_light'], (248, 234, 200), 0.66)


def _whitebrick(palette):
    # Liaodi whitewashed brick — COOL bone-white biased to stone_light
    # with a subtle blue-grey cast so the severe minimalism doesn't read
    # as butter-yellow cardboard. Greyer + cooler than porcelain_white,
    # warmer than column_grey.
    return _mix(palette['stone_light'], (220, 224, 226), 0.74)


def _whitebrick_shadow(palette):
    return _mix(palette['stone_mid'], (158, 162, 168), 0.66)


def _liuhe_ochre(palette):
    # Liuhe brick body — warm ochre clay, between terracotta and Fogong's
    # larch. The wood-tile eaves of Liuhe sit darker so this is the
    # body-only colour.
    return _mix(palette['stone_dark'], (188, 138, 88), 0.72)


def _liuhe_ochre_lit(palette):
    return _mix(palette['stone_mid'], (228, 178, 122), 0.70)


def _liuhe_ochre_shadow(palette):
    return _mix(palette['stone_dark'], (118, 78, 48), 0.82)


def _korean_granite(palette):
    # Dabotap Silla granite — a warm pale grey biased to stone_mid with a
    # touch of horizon so the Korean stone reads warmer than Liaodi's
    # whitewashed brick.
    return _mix(palette['stone_mid'], (188, 178, 162), 0.62)


def _korean_granite_lit(palette):
    return _mix(palette['stone_light'], (222, 214, 198), 0.62)


def _korean_granite_shadow(palette):
    return _mix(palette['stone_dark'], (118, 108, 96), 0.78)


def _tibet_white(palette):
    # Kumbum/Tibetan whitewashed lime — WARM SAND undertone so Kumbum
    # separates from Liaodi's cool bone-white under all phases. Cooler
    # than the round-8 over-saturated beige, warmer than porcelain.
    return _mix(palette['stone_light'], (240, 222, 192), 0.74)


def _tibet_red(palette):
    # Kumbum painted band — Tibetan iron-oxide rust, deeper than vermilion.
    return _mix(palette['stone_dark'], (148, 70, 48), 0.80)


def _tibet_ochre(palette):
    # Kumbum gold-ochre band — duller than gilt, sits between saffron and
    # gold_deep.
    return _mix(palette['stone_accent'], (208, 158, 70), 0.74)


# ── Round 8 shared eave + ornament primitives ──────────────────────────────

def _draw_mokoshi_pent(surf, cx, y_base, half_w_body, palette, *, depth=3):
    """Short narrow eave roof for the Yakushi-ji 'skirt storey' — a flat,
    much SHALLOWER pent than the main blue-tile eave so the alternating
    tall/short silhouette reads as 6 visible roofs. Tile colour pulls from
    `_bluetile` so the pent matches its parent roof's glaze."""
    overhang = max(4, half_w_body // 3)
    tile = _bluetile(palette)
    tile_lit = _bluetile_lit(palette)
    half_outer = half_w_body + overhang
    pts = [
        (cx - half_outer, y_base + depth - 1),
        (cx - half_outer + 1, y_base - 1),
        (cx, y_base - 2),
        (cx + half_outer - 1, y_base - 1),
        (cx + half_outer, y_base + depth - 1),
    ]
    pygame.draw.polygon(surf, _shade(tile, -55), pts)
    body_pts = [(p[0], p[1] - 1) if p[1] >= y_base else p for p in pts]
    pygame.draw.polygon(surf, tile, body_pts)
    pygame.draw.line(surf, tile_lit,
                     (cx - half_outer + 2, y_base - 1),
                     (cx + half_outer - 2, y_base - 1), 1)


def _draw_painted_panel(surf, x, y, w, h, palette, *, motif='floral'):
    """Tiny porcelain-glazed painted panel — for Bao'en porcelain tower
    storey-faces. Each panel is a 2-px-bordered rectangle filled with one
    of three motifs:
      * floral — 3-petal lotus rosette in pink + teal + gold
      * lattice — 1-px diagonal weave in teal + cream
      * bodhi — 2-px cream-on-pink stylised leaf
    Sized intentionally tiny (≤8 px each) so a row of 3 panels reads on a
    PIPE_W=58 face as a coloured frieze rather than smear."""
    if w < 4 or h < 4:
        return
    pink = _porcelain_panel_pink(palette)
    teal = _porcelain_panel_teal(palette)
    gold = _porcelain_panel_gold(palette)
    cream = _porcelain_panel_cream(palette)
    dark = _shade(palette['stone_dark'], -20)
    if motif == 'floral':
        pygame.draw.rect(surf, pink, (x, y, w, h))
        pygame.draw.rect(surf, dark, (x, y, w, h), 1)
        # 3-petal rosette centred — top petal cream, sides teal, centre gold.
        cxp = x + w // 2
        cyp = y + h // 2
        pygame.draw.line(surf, cream, (cxp, y + 1), (cxp, cyp), 1)
        pygame.draw.line(surf, teal, (x + 1, cyp), (cxp, cyp), 1)
        pygame.draw.line(surf, teal, (cxp, cyp), (x + w - 2, cyp), 1)
        surf.set_at((cxp, cyp), gold)
    elif motif == 'lattice':
        pygame.draw.rect(surf, teal, (x, y, w, h))
        pygame.draw.rect(surf, dark, (x, y, w, h), 1)
        # Diagonal weave — 1-px cream cross-hatch.
        for i in range(1, min(w, h) - 1, 2):
            surf.set_at((x + i, y + i), cream)
            surf.set_at((x + i, y + h - 1 - i), cream)
    else:  # bodhi
        pygame.draw.rect(surf, pink, (x, y, w, h))
        pygame.draw.rect(surf, dark, (x, y, w, h), 1)
        # Stylised leaf — cream upright tear-drop.
        cxp = x + w // 2
        leaf_pts = [(cxp, y + 1),
                    (x + w - 2, y + h // 2),
                    (cxp, y + h - 2),
                    (x + 1, y + h // 2)]
        pygame.draw.polygon(surf, cream, leaf_pts)
        pygame.draw.line(surf, gold, (cxp, y + 1), (cxp, y + h - 2), 1)


def _draw_baoen_scroll(surf, cx, y, w, h, palette):
    """One tall vertical aqua-on-white painted scroll per storey body —
    replaces the round-8 3-pill frieze that failed (read as UI pills).
    A single narrow porcelain panel with a faint aqua sumi-e brushstroke
    motif so the storey body has a centred painted accent without the
    pill-row dazzle."""
    if w < 3 or h < 5:
        return
    aqua = _porcelain_panel_teal(palette)
    cream = _porcelain_panel_cream(palette)
    dark = _shade(palette['stone_dark'], -20)
    x = cx - w // 2
    # White panel + dark hairline frame.
    pygame.draw.rect(surf, cream, (x, y, w, h))
    pygame.draw.rect(surf, dark, (x, y, w, h), 1)
    # Centred vertical aqua brushstroke — taper at the ends.
    mid = x + w // 2
    pygame.draw.line(surf, aqua, (mid, y + 1), (mid, y + h - 2), 1)
    if h >= 8:
        pygame.draw.line(surf, aqua,
                         (mid - 1, y + h // 3),
                         (mid + 1, y + h // 3), 1)
        pygame.draw.line(surf, aqua,
                         (mid - 1, y + h - h // 3),
                         (mid + 1, y + h - h // 3), 1)
    # Tiny gold seal dot at the bottom — the painted-scroll cue.
    gold = _porcelain_panel_gold(palette)
    surf.set_at((mid, y + h - 2), gold)


def _draw_korean_balustrade(surf, x_l, x_r, y, palette):
    """Dabotap stone balustrade — short row of granite mini-columns capped
    by a flat top rail. Lotus-bud column-caps at the end posts. Reads as
    the Silla railing signature even at PIPE_W=58."""
    granite = _korean_granite(palette)
    lit = _korean_granite_lit(palette)
    shadow = _korean_granite_shadow(palette)
    # Top rail.
    pygame.draw.rect(surf, shadow, (x_l - 1, y, x_r - x_l + 2, 2))
    pygame.draw.rect(surf, lit, (x_l, y, x_r - x_l, 1))
    # Mini-columns every 4 px.
    n_cols = max(3, (x_r - x_l) // 4)
    step = (x_r - x_l) // max(1, n_cols - 1)
    for i in range(n_cols):
        px = x_l + i * step
        pygame.draw.line(surf, shadow, (px, y + 2), (px, y + 6), 1)
        pygame.draw.line(surf, lit, (px - 1, y + 2), (px - 1, y + 6), 1)
        # End posts get a lotus-bud cap.
        if i == 0 or i == n_cols - 1:
            pygame.draw.circle(surf, granite, (px, y + 1), 2)
            pygame.draw.circle(surf, lit, (px - 1, y), 1)


def _draw_tibetan_eyes(surf, cx, cy, palette, *, scale=1.0):
    """Kumbum harmika painted Buddha eyes — SIMPLE 2-dot read at the
    PIPE_W=58 scale. The round-8 _buddha_eye almond shape collapsed to a
    horizontal hatched smudge bar; this draws two clean black dots ~2 px
    apart with a tiny urna between them so the eyes are immediately
    legible. White is sourced from palette stone_light."""
    dark = palette['stone_dark']
    white = _shade(palette['stone_light'], 12)
    sep = max(3, int(4 * scale))
    dot_r = max(1, int(1.6 * scale))
    # Faint white eye-pad behind each dot so the iris reads on the harmika.
    pygame.draw.circle(surf, white, (cx - sep, cy), dot_r + 1)
    pygame.draw.circle(surf, white, (cx + sep, cy), dot_r + 1)
    # Two black iris dots — the unambiguous "Buddha eyes" glyph.
    pygame.draw.circle(surf, dark, (cx - sep, cy), dot_r)
    pygame.draw.circle(surf, dark, (cx + sep, cy), dot_r)
    # Tiny urna dot between/above eyes.
    pygame.draw.circle(surf, dark, (cx, cy - max(1, int(2 * scale))), 1)


def _draw_korean_stair(surf, cx, base_y, palette, *, w=10, h=6):
    """Dabotap corner stair — a 4-step granite stairway sitting on the
    plinth corner. Drawn as receding rectangles each 1 px shorter than
    the one below. Reads as a 4-step stone stair at PIPE_W=58."""
    granite = _korean_granite(palette)
    lit = _korean_granite_lit(palette)
    shadow = _korean_granite_shadow(palette)
    steps = 4
    step_h = max(1, h // steps)
    for k in range(steps):
        sw = max(2, w - k * 2)
        sx = cx - sw // 2
        sy = base_y - (k + 1) * step_h
        pygame.draw.rect(surf, shadow, (sx, sy, sw, step_h))
        pygame.draw.rect(surf, granite, (sx + 1, sy, sw - 1, step_h - 1))
        pygame.draw.line(surf, lit, (sx + 1, sy), (sx + sw - 2, sy), 1)


def _draw_tahoto_dome(surf, cx, base_y, dome_h, body_w, palette):
    """Tahōtō kamebara — hemispherical white-plaster cylinder body. Drawn
    as a stacked: 1) lower square base 2) round dome (cylinder) 3) upper
    square section. Returns the y-coordinate of the dome top so the
    caller can place the upper square + sōrin above it. Adds a dark eave
    horizontal at the dome shoulder + a vertical seam down the centre
    so the round body isn't a perfectly elliptical marshmallow."""
    plaster = _white_plaster_warm(palette)
    plaster_lit = _shade(plaster, 22)
    plaster_shadow = _shade(plaster, -28)
    # Dark eave horizontal AT the dome shoulder — sits at the base seam
    # between square base + round body. Reads as the wood frieze that
    # actually wraps the kamebara on real Tahōtō.
    eave = _shade(palette['stone_dark'], -10)
    pygame.draw.rect(surf, eave,
                     (cx - body_w // 2 - 2, base_y - 2, body_w + 4, 3))
    pygame.draw.line(surf, _shade(eave, -25),
                     (cx - body_w // 2 - 2, base_y + 1),
                     (cx + body_w // 2 + 1, base_y + 1), 1)
    # Hemispherical dome.
    dome_rect = pygame.Rect(cx - body_w // 2, base_y - dome_h,
                            body_w, dome_h * 2)
    pygame.draw.ellipse(surf, plaster_shadow, dome_rect)
    pygame.draw.ellipse(surf, plaster, dome_rect.inflate(-2, -2))
    # Lit highlight ellipse offset up-left.
    pygame.draw.ellipse(surf, plaster_lit,
                        (dome_rect.x + 2, dome_rect.y + 2,
                         body_w - 6, dome_h - 4))
    # Flatten bottom.
    pygame.draw.rect(surf, plaster,
                     (cx - body_w // 2, base_y - 1, body_w, 2))
    # Vertical seam down the centre + faint door slit — breaks the dome
    # from a featureless egg and reads as the kamebara's lapped boarding.
    pygame.draw.line(surf, plaster_shadow,
                     (cx, base_y - dome_h + 2),
                     (cx, base_y - 2), 1)
    # Door slit at the lower-centre.
    slit_h = max(4, dome_h // 3)
    pygame.draw.rect(surf, _shade(palette['stone_dark'], -25),
                     (cx - 1, base_y - slit_h - 1, 2, slit_h))
    # AA outer arc.
    arc_pts = []
    for k in range(13):
        t = k / 12
        ang = math.pi + t * math.pi
        px = cx + math.cos(ang) * body_w * 0.5
        py = base_y - math.sin(ang) * dome_h
        if py <= base_y:
            arc_pts.append((int(px), int(py)))
    if len(arc_pts) >= 2:
        _aa_polyline(surf, plaster_shadow, arc_pts)
    return base_y - dome_h


# ── Round 8 #1. Tō-ji Five-Storey Pagoda (Kyoto, 826/1644) ─────────────────
#
# Monumental dark cypress with HEAVIER, squatter proportions than Hōryū-ji.
# Identity beat: dark cypress + thick deep eaves + bronze sōrin.
# Reference: https://en.wikipedia.org/wiki/T%C5%8D-ji

def _draw_toji_to(surf, cx, top_y, bot_y, base_w, palette, *,
                  tier_count=5, finial_h=36, sorin_up=True,
                  entry_door_open=False, draw_entry_door=True):
    cypress = _toji_cypress(palette)
    cypress_lit = _toji_cypress_lit(palette)
    cypress_shadow = _toji_cypress_shadow(palette)
    plaster = _plaster(palette)
    plaster_shadow = _shade(plaster, -25)
    # Paper-white shoji aperture — much brighter than _plaster so the window
    # stays visible on Tō-ji's dark cypress at day. Warming sky pre-lights
    # the panel from sunset onward so the window doesn't pop on a frame.
    shoji = _mix(palette['stone_light'], (250, 248, 236), 0.86)
    accent = _bronze(palette)
    tile_col = _shade(palette['stone_dark'], -25)

    total_h = bot_y - top_y
    if total_h < 10:
        return
    # Tō-ji's storeys shrink LESS aggressively than Hōryū-ji's — body
    # widths only taper 0.96^i so the silhouette reads squatter.
    weights = [1.0 - 0.04 * i for i in range(tier_count)]
    wsum = sum(weights)
    tier_heights = [max(8, int(total_h * w / wsum)) for w in weights]
    body_widths = [max(14, int(base_w * (0.96 ** i)))
                   for i in range(tier_count)]

    y_cursor = bot_y
    tier_tops = []
    for i in range(tier_count):
        th = tier_heights[i]
        bw = body_widths[i]
        wall_top = y_cursor - th
        if wall_top < top_y - 1:
            break
        tier_tops.append((wall_top, bw, th))
        x_l = cx - bw // 2
        body_rect = pygame.Rect(x_l, wall_top, bw, th)
        # 3-stop body gradient so the dark cypress reads as a 3-D column,
        # not a black silhouette.
        _gradient_rect(surf, body_rect, cypress_lit, cypress, cypress_shadow)
        # Narrow plaster panel band only — Tō-ji is mostly cypress with
        # narrow plaster slits between thick posts.
        if bw > 16 and th > 6:
            for off in (-bw // 4, bw // 4):
                pp_w = max(2, bw // 6)
                pp_x = cx + off - pp_w // 2
                pp_rect = pygame.Rect(pp_x, wall_top + 2, pp_w, th - 4)
                _gradient_rect(surf, pp_rect,
                               _shade(plaster, 18), plaster, plaster_shadow)
        # Heavy left + right posts (3 px each — heavier than Hōryū-ji's 2).
        pygame.draw.rect(surf, cypress_shadow, (x_l, wall_top, 3, th))
        pygame.draw.rect(surf, cypress_shadow, (x_l + bw - 3, wall_top, 3, th))
        pygame.draw.line(surf, cypress_lit,
                         (x_l, wall_top), (x_l, wall_top + th - 1), 1)
        # Centre post on wider tiers.
        if bw > 24:
            pygame.draw.rect(surf, cypress_shadow, (cx - 1, wall_top, 2, th))
        # Mid horizontal beam.
        if th > 10:
            pygame.draw.line(surf, cypress_lit,
                             (x_l + 3, wall_top + th // 2),
                             (x_l + bw - 4, wall_top + th // 2), 1)
        # ONE centred paper-shoji panel per storey — Tō-ji's dark cypress
        # face is too brown-on-brown without the white aperture. Day reads
        # as a bright paper rectangle; sunset onward swaps to the warm lit
        # niche so it becomes a window-glow lantern.
        if th > 9 and bw > 14:
            nh = min(7, th - 5)
            nw = min(6, bw - 10)
            if _is_dark_sky(palette) or _is_warming_sky(palette):
                _lit_niche(surf, cx, wall_top + 2, nw, nh, palette)
            else:
                # Paper shoji on day — 1-px shadow frame + bright fill so
                # the window aperture stays legible against cypress brown.
                pygame.draw.rect(surf, cypress_shadow,
                                 (cx - nw // 2 - 1, wall_top + 1,
                                  nw + 2, nh + 2))
                pygame.draw.rect(surf, shoji,
                                 (cx - nw // 2, wall_top + 2, nw, nh))
                # Faint cross-mullion so it reads as a paper screen, not a
                # flat sticker.
                pygame.draw.line(surf, _shade(shoji, -45),
                                 (cx - nw // 2, wall_top + 2 + nh // 2),
                                 (cx + nw // 2 - 1, wall_top + 2 + nh // 2), 1)
                pygame.draw.line(surf, _shade(shoji, -45),
                                 (cx, wall_top + 2),
                                 (cx, wall_top + 2 + nh - 1), 1)
        # Recessed entry door at the lowest storey.
        if i == 0 and draw_entry_door and bw >= 14 and th >= 12:
            _draw_entry_door(surf, cx, wall_top + th - 1, palette,
                             w=2, h=4, open_glow=entry_door_open)
        # Thick deep eave — depth 7 (was 5 on Hōryū-ji) so the silhouette
        # reads heavier. Curl is gentle (0.35) — Tō-ji eaves are wide but
        # not strongly upturned.
        overhang = max(12, 15 - i)
        depth = 7
        is_top_tier = (i == tier_count - 1)
        _eave_tang_curl(surf, cx, wall_top, bw // 2, overhang, depth,
                        cypress, accent, tile_col, curl=0.35,
                        alternating_hatch=True,
                        drop_shadow=True,
                        skip_corner_hook=is_top_tier)
        if is_top_tier:
            half_outer = bw // 2 + overhang
            tip_y_top = wall_top - max(2, int(depth * (0.5 + 0.35)))
            _draw_shibi_finial(surf, cx - half_outer + 1, tip_y_top + 1,
                               palette, side=+1)
            _draw_shibi_finial(surf, cx + half_outer - 1, tip_y_top + 1,
                               palette, side=-1)
        y_cursor = wall_top - depth + 1

    if not tier_tops:
        return

    # Bronze sōrin — 9-disk stack, taller than Fogong's compact 5.
    top_wall_y = tier_tops[-1][0]
    base_y = top_wall_y - 2 if sorin_up else bot_y + 2
    dir_sign = -1 if sorin_up else 1
    dark_pal = palette['stone_dark']
    bright = _shade(accent, 45)
    pygame.draw.ellipse(surf, dark_pal, (cx - 7, base_y + dir_sign * 1, 14, 5))
    pygame.draw.ellipse(surf, accent, (cx - 6, base_y + dir_sign * 1 + 1, 12, 3))
    needle_tip = base_y + dir_sign * (finial_h - 4)
    pygame.draw.line(surf, dark_pal,
                     (cx - 1, base_y + dir_sign * 4),
                     (cx - 1, needle_tip), 2)
    pygame.draw.line(surf, accent,
                     (cx, base_y + dir_sign * 4),
                     (cx, needle_tip), 1)
    for k in range(9):
        t = k / 8
        ry = base_y + dir_sign * (5 + int(t * (finial_h - 10)))
        rw = max(2, 8 - k // 2)
        pygame.draw.ellipse(surf, dark_pal,
                            (cx - rw - 1, ry - 1, rw * 2 + 2, 3))
        pygame.draw.ellipse(surf, accent,
                            (cx - rw, ry, rw * 2, 2))
    tip_y = base_y + dir_sign * finial_h
    _draw_sorin_flame_halo(surf, cx, tip_y, palette)
    pygame.draw.circle(surf, dark_pal, (cx, tip_y), 3)
    pygame.draw.circle(surf, accent, (cx, tip_y), 2)
    flame = [(cx, tip_y + dir_sign * 5),
             (cx - 2, tip_y + dir_sign * 1),
             (cx + 2, tip_y + dir_sign * 1)]
    pygame.draw.polygon(surf, bright, flame)


def _draw_toji(surf, top_rect, bot_rect, palette, seed):
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2
    tier_count = rng.choice([5, 5, 6])
    vine_side = rng.choice(('left', 'right'))
    entry_open = rng.choice((True, False))
    has_pine_sprig = rng.random() < 0.7
    shrub_jitter = rng.randint(-2, 2)

    if bot_rect.height > 50:
        _draw_plinth_mist(surf, bcx, bot_rect.bottom,
                          int(bot_rect.width * 2.4), palette)
        plinth_h = 11
        plinth_w = int(bot_rect.width * 1.28)
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -10),
                         (bcx - plinth_w // 2, bot_rect.bottom - plinth_h,
                          plinth_w, plinth_h))
        pygame.draw.rect(surf, _column_grey(palette),
                         (bcx - plinth_w // 2 + 1,
                          bot_rect.bottom - plinth_h + 1,
                          plinth_w - 2, plinth_h - 2))
        pygame.draw.rect(surf, palette['stone_light'],
                         (bcx - plinth_w // 2,
                          bot_rect.bottom - plinth_h, plinth_w, 1))
        # Stair notch.
        notch_w, notch_h = 8, 4
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -25),
                         (bcx - notch_w // 2, bot_rect.bottom - notch_h,
                          notch_w, notch_h))
        pygame.draw.line(surf, _bronze(palette),
                         (bcx - notch_w // 2, bot_rect.bottom - notch_h),
                         (bcx + notch_w // 2 - 1, bot_rect.bottom - notch_h), 1)

        finial_h = 38
        envelope_top = bot_rect.y
        envelope_bot = bot_rect.bottom - plinth_h
        _draw_toji_to(surf, bcx,
                      envelope_top + finial_h, envelope_bot,
                      int(bot_rect.width * 0.96), palette,
                      tier_count=tier_count, finial_h=finial_h,
                      sorin_up=True, entry_door_open=entry_open)

        body_half = int(bot_rect.width * 0.96) // 2
        vine_x = bcx - body_half + 1 if vine_side == 'left' else bcx + body_half - 1
        vine_top = max(envelope_top + finial_h + 20, envelope_bot - 70)
        _draw_vine_chunks(surf, vine_x, vine_top, envelope_bot - 4,
                          palette, seed=seed)
        draw_side_shrub(surf, bcx - plinth_w // 2 - 2 + shrub_jitter,
                        bot_rect.bottom - 2, palette, scale=0.9)
        draw_side_shrub(surf, bcx + plinth_w // 2 + 2 - shrub_jitter,
                        bot_rect.bottom - 2, palette, scale=0.9)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 10, 16, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 7, seed=seed)
        if has_pine_sprig:
            pine_side = -1 if vine_side == 'right' else 1
            pine_x = bcx + pine_side * (plinth_w // 2 + 8)
            draw_wuling_pine(surf, pine_x, bot_rect.bottom,
                             22, palette, lean=pine_side * 3, layers=4)

    if top_rect.height > 50:
        _draw_plinth_mist(surf, tcx, top_rect.y + 10,
                          int(top_rect.width * 2.0), palette)
        plinth_h = 7
        plinth_w = int(top_rect.width * 1.18)
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -10),
                         (tcx - plinth_w // 2, top_rect.y, plinth_w, plinth_h))
        pygame.draw.rect(surf, _column_grey(palette),
                         (tcx - plinth_w // 2 + 1, top_rect.y + 1,
                          plinth_w - 2, plinth_h - 2))
        pygame.draw.rect(surf, palette['stone_light'],
                         (tcx - plinth_w // 2,
                          top_rect.y + plinth_h - 1, plinth_w, 1))
        finial_h = 28
        envelope_top = top_rect.y + plinth_h
        envelope_bot = top_rect.bottom - finial_h
        hanger_tiers = max(3, tier_count - 2)
        _draw_toji_to(surf, tcx,
                      envelope_top, envelope_bot,
                      int(top_rect.width * 0.96), palette,
                      tier_count=hanger_tiers, finial_h=finial_h - 4,
                      sorin_up=False, draw_entry_door=False)
        for off in (-8, 8):
            draw_moss_strand(surf, tcx + off, envelope_bot,
                             7 + abs(off) % 3, palette,
                             jitter_seed=seed + off)


def candidate_toji(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('toji', _draw_toji, surf, top_rect, bot_rect, palette, seed)


# ── Round 8 #2. Daigo-ji Five-Story Pagoda (Kyoto, 951) ────────────────────
#
# Vermilion lacquer columns + white plaster walls + extra-long gold sōrin
# (1/3 of total height). "Festival temple" palette beat.
# Reference: https://en.wikipedia.org/wiki/Daigo-ji

def _draw_daigoji_to(surf, cx, top_y, bot_y, base_w, palette, *,
                    tier_count=5, finial_h=42, sorin_up=True,
                    entry_door_open=False, draw_entry_door=True):
    vermilion = _vermilion(palette)
    vermilion_lit = _vermilion_lit(palette)
    vermilion_shadow = _vermilion_shadow(palette)
    plaster = _plaster(palette)
    plaster_shadow = _shade(plaster, -25)
    gold = _gold_bright(palette)
    gold_d = _gold_deep(palette)
    tile_col = _shade(palette['stone_dark'], -10)

    total_h = bot_y - top_y
    if total_h < 10:
        return
    weights = [1.0 - 0.06 * i for i in range(tier_count)]
    wsum = sum(weights)
    tier_heights = [max(8, int(total_h * w / wsum)) for w in weights]
    body_widths = [max(12, int(base_w * (0.92 ** i)))
                   for i in range(tier_count)]

    y_cursor = bot_y
    tier_tops = []
    for i in range(tier_count):
        th = tier_heights[i]
        bw = body_widths[i]
        wall_top = y_cursor - th
        if wall_top < top_y - 1:
            break
        tier_tops.append((wall_top, bw, th))
        x_l = cx - bw // 2
        # White plaster main panel — Daigo-ji reads as more plaster than
        # column, with vermilion only on the framing posts + horizontal beam.
        pygame.draw.rect(surf, _shade(plaster, -28),
                         (x_l, wall_top, bw, th))
        if bw > 8 and th > 4:
            inner = pygame.Rect(x_l + 2, wall_top + 1, bw - 4, th - 1)
            _gradient_rect(surf, inner,
                           _shade(plaster, 18), plaster, plaster_shadow)
        # Vermilion side posts — 3 px wide, lacquer-bright.
        for px in (x_l, x_l + bw - 3):
            pygame.draw.rect(surf, vermilion_shadow, (px, wall_top, 3, th))
            pygame.draw.line(surf, vermilion_lit,
                             (px + 1, wall_top), (px + 1, wall_top + th - 1), 1)
            pygame.draw.rect(surf, vermilion,
                             (px, wall_top + 1, 2, th - 1))
        # Vermilion top + bottom beam.
        pygame.draw.rect(surf, vermilion, (x_l, wall_top, bw, 2))
        pygame.draw.rect(surf, vermilion, (x_l, wall_top + th - 2, bw, 2))
        pygame.draw.line(surf, vermilion_lit,
                         (x_l, wall_top), (x_l + bw - 1, wall_top), 1)
        # Centre post on wider tiers.
        if bw > 22:
            pygame.draw.rect(surf, vermilion, (cx - 1, wall_top, 2, th))
            pygame.draw.line(surf, vermilion_lit,
                             (cx, wall_top), (cx, wall_top + th - 1), 1)
        # Vermilion lintel band — horizontal painted beam under the eave
        # so the plaster panel isn't an empty rectangle. Twin plaster rails
        # below provide the nageshi cue.
        if th > 8:
            lintel_y = wall_top + max(2, th // 4)
            pygame.draw.rect(surf, vermilion_shadow,
                             (x_l + 3, lintel_y, bw - 6, 2))
            pygame.draw.line(surf, vermilion_lit,
                             (x_l + 3, lintel_y), (x_l + bw - 4, lintel_y), 1)
        if th > 14:
            rail_y = wall_top + int(th * 2 / 3)
            pygame.draw.line(surf, plaster_shadow,
                             (x_l + 3, rail_y),
                             (x_l + bw - 4, rail_y), 1)
        # ONE centred lit window per storey (cross-row unification rule) —
        # bright at night/dusk, dark door slit at day so the plaster panel
        # isn't pure white at night.
        if th > 9 and bw > 12:
            nw = min(6, bw - 10)
            nh = min(6, th - 6)
            if _is_dark_sky(palette) or _is_warming_sky(palette):
                _lit_niche(surf, cx, wall_top + 3, nw, nh, palette)
            else:
                # Dark vermilion door slit at day — narrow vertical band so
                # the centre panel isn't featureless white.
                slit_w = max(2, nw // 2)
                slit_h = nh
                pygame.draw.rect(surf, vermilion_shadow,
                                 (cx - slit_w // 2, wall_top + 3,
                                  slit_w, slit_h))
                pygame.draw.line(surf, _shade(plaster, -55),
                                 (cx - slit_w // 2, wall_top + 3),
                                 (cx + slit_w // 2 - 1, wall_top + 3), 1)
        if i == 0 and draw_entry_door and bw >= 12 and th >= 12:
            _draw_entry_door(surf, cx, wall_top + th - 1, palette,
                             w=2, h=4, open_glow=entry_door_open)
        # Vermilion-stained tile eave — uses vermilion as the roof colour
        # rather than cypress brown. Gold accent stripe.
        overhang = max(10, 13 - i)
        depth = 5
        is_top_tier = (i == tier_count - 1)
        _eave_tang_curl(surf, cx, wall_top, bw // 2, overhang, depth,
                        vermilion, gold, tile_col, curl=0.45,
                        alternating_hatch=True, drop_shadow=True,
                        skip_corner_hook=is_top_tier)
        if is_top_tier:
            half_outer = bw // 2 + overhang
            tip_y_top = wall_top - max(2, int(depth * (0.5 + 0.45)))
            _draw_shibi_finial(surf, cx - half_outer + 1, tip_y_top + 1,
                               palette, side=+1)
            _draw_shibi_finial(surf, cx + half_outer - 1, tip_y_top + 1,
                               palette, side=-1)
        y_cursor = wall_top - depth + 1

    if not tier_tops:
        return

    # Extra-long gold sōrin — at Daigo-ji the finial is 1/3 of total tower
    # height, so we boost finial_h passed in and use 11 disks rather than 9.
    top_wall_y = tier_tops[-1][0]
    base_y = top_wall_y - 2 if sorin_up else bot_y + 2
    dir_sign = -1 if sorin_up else 1
    dark_pal = palette['stone_dark']
    bright = _shade(gold, 45)
    pygame.draw.ellipse(surf, dark_pal, (cx - 7, base_y + dir_sign * 1, 14, 5))
    pygame.draw.ellipse(surf, gold, (cx - 6, base_y + dir_sign * 1 + 1, 12, 3))
    needle_tip = base_y + dir_sign * (finial_h - 4)
    pygame.draw.line(surf, dark_pal,
                     (cx - 1, base_y + dir_sign * 4),
                     (cx - 1, needle_tip), 2)
    pygame.draw.line(surf, gold,
                     (cx, base_y + dir_sign * 4),
                     (cx, needle_tip), 1)
    disks = 11
    for k in range(disks):
        t = k / max(1, disks - 1)
        ry = base_y + dir_sign * (5 + int(t * (finial_h - 11)))
        rw = max(2, 8 - k // 2)
        pygame.draw.ellipse(surf, dark_pal,
                            (cx - rw - 1, ry - 1, rw * 2 + 2, 3))
        pygame.draw.ellipse(surf, gold_d,
                            (cx - rw, ry, rw * 2, 2))
        pygame.draw.line(surf, bright,
                         (cx - rw + 1, ry), (cx - rw + 2, ry), 1)
    tip_y = base_y + dir_sign * finial_h
    _draw_sorin_flame_halo(surf, cx, tip_y, palette)
    pygame.draw.circle(surf, dark_pal, (cx, tip_y), 3)
    pygame.draw.circle(surf, gold, (cx, tip_y), 2)
    flame = [(cx, tip_y + dir_sign * 5),
             (cx - 2, tip_y + dir_sign * 1),
             (cx + 2, tip_y + dir_sign * 1)]
    pygame.draw.polygon(surf, bright, flame)


def _draw_daigoji(surf, top_rect, bot_rect, palette, seed):
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2
    tier_count = rng.choice([5, 5])
    vine_side = rng.choice(('left', 'right'))
    entry_open = rng.choice((True, False))
    has_pine_sprig = rng.random() < 0.7
    shrub_jitter = rng.randint(-2, 2)

    if bot_rect.height > 50:
        _draw_plinth_mist(surf, bcx, bot_rect.bottom,
                          int(bot_rect.width * 2.4), palette)
        plinth_h = 10
        plinth_w = int(bot_rect.width * 1.22)
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -10),
                         (bcx - plinth_w // 2, bot_rect.bottom - plinth_h,
                          plinth_w, plinth_h))
        pygame.draw.rect(surf, _column_grey(palette),
                         (bcx - plinth_w // 2 + 1,
                          bot_rect.bottom - plinth_h + 1,
                          plinth_w - 2, plinth_h - 2))
        pygame.draw.rect(surf, palette['stone_light'],
                         (bcx - plinth_w // 2,
                          bot_rect.bottom - plinth_h, plinth_w, 1))

        finial_h = 44  # Daigo-ji finial is ~1/3 of tower height.
        envelope_top = bot_rect.y
        envelope_bot = bot_rect.bottom - plinth_h
        _draw_daigoji_to(surf, bcx,
                         envelope_top + finial_h, envelope_bot,
                         int(bot_rect.width * 0.94), palette,
                         tier_count=tier_count, finial_h=finial_h,
                         sorin_up=True, entry_door_open=entry_open)

        body_half = int(bot_rect.width * 0.94) // 2
        vine_x = bcx - body_half + 1 if vine_side == 'left' else bcx + body_half - 1
        vine_top = max(envelope_top + finial_h + 20, envelope_bot - 70)
        _draw_vine_chunks(surf, vine_x, vine_top, envelope_bot - 4,
                          palette, seed=seed)
        draw_side_shrub(surf, bcx - plinth_w // 2 - 2 + shrub_jitter,
                        bot_rect.bottom - 2, palette, scale=0.9)
        draw_side_shrub(surf, bcx + plinth_w // 2 + 2 - shrub_jitter,
                        bot_rect.bottom - 2, palette, scale=0.9)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 10, 16, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 7, seed=seed)
        if has_pine_sprig:
            pine_side = -1 if vine_side == 'right' else 1
            pine_x = bcx + pine_side * (plinth_w // 2 + 8)
            draw_wuling_pine(surf, pine_x, bot_rect.bottom,
                             22, palette, lean=pine_side * 3, layers=4)

    if top_rect.height > 50:
        _draw_plinth_mist(surf, tcx, top_rect.y + 10,
                          int(top_rect.width * 2.0), palette)
        plinth_h = 7
        plinth_w = int(top_rect.width * 1.18)
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -10),
                         (tcx - plinth_w // 2, top_rect.y, plinth_w, plinth_h))
        pygame.draw.rect(surf, _column_grey(palette),
                         (tcx - plinth_w // 2 + 1, top_rect.y + 1,
                          plinth_w - 2, plinth_h - 2))
        finial_h = 32
        envelope_top = top_rect.y + plinth_h
        envelope_bot = top_rect.bottom - finial_h
        hanger_tiers = max(3, tier_count - 2)
        _draw_daigoji_to(surf, tcx,
                         envelope_top, envelope_bot,
                         int(top_rect.width * 0.94), palette,
                         tier_count=hanger_tiers, finial_h=finial_h - 4,
                         sorin_up=False, draw_entry_door=False)
        for off in (-8, 8):
            draw_moss_strand(surf, tcx + off, envelope_bot,
                             7 + abs(off) % 3, palette,
                             jitter_seed=seed + off)


def candidate_daigoji(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('daigoji', _draw_daigoji, surf, top_rect, bot_rect, palette, seed)


# ── Round 8 #3. Yakushi-ji West Pagoda (Nara, 730/1981 reb.) ───────────────
#
# 3-storey with mokoshi (skirt-roof) pent eaves between each tier → 6 visible
# roofs. White plaster + cedar + blue-glaze ceramic tile.
# Reference: https://en.wikipedia.org/wiki/Yakushi-ji

def _draw_yakushiji_to(surf, cx, top_y, bot_y, base_w, palette, *,
                       tier_count=4, finial_h=40, sorin_up=True,
                       entry_door_open=False, draw_entry_door=True):
    cedar = _cedar(palette)
    plaster = _plaster(palette)
    plaster_shadow = _shade(plaster, -25)
    bluetile = _bluetile(palette)
    bluetile_lit = _bluetile_lit(palette)
    accent = _bronze(palette)
    tile_col = _shade(bluetile, -25)

    total_h = bot_y - top_y
    if total_h < 12:
        return
    # 4 strong shelf-and-body alternations — the round-8 mokoshi conceit
    # collapsed to 6 grey shelves at PIPE_W=58. Dropping mokoshi and
    # committing to 4 alternations gives a legible bronze-eave cadence.
    weights = [1.0, 0.88, 0.78, 0.68]
    wsum = sum(weights)
    tier_heights = [max(10, int(total_h * w / wsum)) for w in weights]
    body_widths = [max(14, int(base_w * (0.93 ** i)))
                   for i in range(tier_count)]
    mokoshi_h = 0  # Mokoshi disabled — keeps the 4 shelves crisp at scale.

    y_cursor = bot_y
    tier_tops = []
    for i in range(tier_count):
        th = tier_heights[i] if i < len(tier_heights) else 12
        bw = body_widths[i]
        wall_top = y_cursor - th
        if wall_top < top_y - 1:
            break
        tier_tops.append((wall_top, bw, th))
        x_l = cx - bw // 2
        # White plaster wall with cedar posts.
        pygame.draw.rect(surf, _shade(plaster, -28),
                         (x_l, wall_top, bw, th))
        if bw > 8 and th > 4:
            inner = pygame.Rect(x_l + 2, wall_top + 1, bw - 4, th - 1)
            _gradient_rect(surf, inner,
                           _shade(plaster, 22), plaster, plaster_shadow)
        for px in (x_l, x_l + bw - 2):
            pygame.draw.rect(surf, _shade(cedar, -25), (px, wall_top, 2, th))
        if bw > 22:
            pygame.draw.rect(surf, cedar, (cx - 1, wall_top, 2, th))
        # Nageshi rails.
        if th > 14:
            for frac in (1 / 3, 2 / 3):
                rail_y = wall_top + int(th * frac)
                pygame.draw.line(surf, plaster_shadow,
                                 (x_l + 2, rail_y),
                                 (x_l + bw - 3, rail_y), 1)
        # ONE centred lit window per storey (cross-row unification rule).
        if th > 13 and bw > 18:
            nw = min(5, bw // 5)
            nh = min(7, th - 7)
            _lit_niche(surf, cx, wall_top + 3, nw, nh, palette)
        if i == 0 and draw_entry_door and bw >= 14 and th >= 12:
            _draw_entry_door(surf, cx, wall_top + th - 1, palette,
                             w=2, h=4, open_glow=entry_door_open)
        # Tall blue-tile eave (deeper than mokoshi).
        overhang = max(11, 14 - i)
        depth = 6
        is_top_tier = (i == tier_count - 1)
        _eave_tang_curl(surf, cx, wall_top, bw // 2, overhang, depth,
                        bluetile, accent, tile_col, curl=0.50,
                        alternating_hatch=True, drop_shadow=True,
                        skip_corner_hook=is_top_tier)
        if is_top_tier:
            half_outer = bw // 2 + overhang
            tip_y_top = wall_top - max(2, int(depth * (0.5 + 0.50)))
            _draw_shibi_finial(surf, cx - half_outer + 1, tip_y_top + 1,
                               palette, side=+1)
            _draw_shibi_finial(surf, cx + half_outer - 1, tip_y_top + 1,
                               palette, side=-1)
        y_cursor = wall_top - depth + 1

    if not tier_tops:
        return

    # Bronze sōrin — standard 9-disk.
    top_wall_y = tier_tops[-1][0]
    base_y = top_wall_y - 2 if sorin_up else bot_y + 2
    dir_sign = -1 if sorin_up else 1
    dark_pal = palette['stone_dark']
    bright = _shade(accent, 45)
    pygame.draw.ellipse(surf, dark_pal, (cx - 6, base_y + dir_sign * 1, 12, 5))
    pygame.draw.ellipse(surf, accent, (cx - 5, base_y + dir_sign * 1 + 1, 10, 3))
    needle_tip = base_y + dir_sign * (finial_h - 4)
    pygame.draw.line(surf, dark_pal,
                     (cx - 1, base_y + dir_sign * 4),
                     (cx - 1, needle_tip), 2)
    pygame.draw.line(surf, accent,
                     (cx, base_y + dir_sign * 4),
                     (cx, needle_tip), 1)
    for k in range(9):
        t = k / 8
        ry = base_y + dir_sign * (5 + int(t * (finial_h - 10)))
        rw = max(2, 7 - k // 2)
        pygame.draw.ellipse(surf, dark_pal,
                            (cx - rw - 1, ry - 1, rw * 2 + 2, 3))
        pygame.draw.ellipse(surf, accent,
                            (cx - rw, ry, rw * 2, 2))
    tip_y = base_y + dir_sign * finial_h
    _draw_sorin_flame_halo(surf, cx, tip_y, palette)
    pygame.draw.circle(surf, dark_pal, (cx, tip_y), 3)
    pygame.draw.circle(surf, accent, (cx, tip_y), 2)
    # Suien (water-vase) — Yakushi-ji's iconic finial has an openwork
    # bronze water-flame instead of the usual orb. Wider flat polygon.
    suien = [(cx, tip_y + dir_sign * 7),
             (cx - 4, tip_y + dir_sign * 4),
             (cx - 2, tip_y + dir_sign * 1),
             (cx + 2, tip_y + dir_sign * 1),
             (cx + 4, tip_y + dir_sign * 4)]
    pygame.draw.polygon(surf, bright, suien)
    pygame.draw.lines(surf, accent, True, suien, 1)


def _draw_yakushiji(surf, top_rect, bot_rect, palette, seed):
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2
    vine_side = rng.choice(('left', 'right'))
    entry_open = rng.choice((True, False))
    has_pine_sprig = rng.random() < 0.7
    shrub_jitter = rng.randint(-2, 2)

    if bot_rect.height > 50:
        _draw_plinth_mist(surf, bcx, bot_rect.bottom,
                          int(bot_rect.width * 2.4), palette)
        plinth_h = 10
        plinth_w = int(bot_rect.width * 1.25)
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -10),
                         (bcx - plinth_w // 2, bot_rect.bottom - plinth_h,
                          plinth_w, plinth_h))
        pygame.draw.rect(surf, _column_grey(palette),
                         (bcx - plinth_w // 2 + 1,
                          bot_rect.bottom - plinth_h + 1,
                          plinth_w - 2, plinth_h - 2))
        pygame.draw.rect(surf, palette['stone_light'],
                         (bcx - plinth_w // 2,
                          bot_rect.bottom - plinth_h, plinth_w, 1))

        finial_h = 42
        envelope_top = bot_rect.y
        envelope_bot = bot_rect.bottom - plinth_h
        _draw_yakushiji_to(surf, bcx,
                           envelope_top + finial_h, envelope_bot,
                           int(bot_rect.width * 0.94), palette,
                           tier_count=4, finial_h=finial_h,
                           sorin_up=True, entry_door_open=entry_open)

        body_half = int(bot_rect.width * 0.94) // 2
        vine_x = bcx - body_half + 1 if vine_side == 'left' else bcx + body_half - 1
        vine_top = max(envelope_top + finial_h + 20, envelope_bot - 70)
        _draw_vine_chunks(surf, vine_x, vine_top, envelope_bot - 4,
                          palette, seed=seed)
        draw_side_shrub(surf, bcx - plinth_w // 2 - 2 + shrub_jitter,
                        bot_rect.bottom - 2, palette, scale=0.9)
        draw_side_shrub(surf, bcx + plinth_w // 2 + 2 - shrub_jitter,
                        bot_rect.bottom - 2, palette, scale=0.9)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 10, 16, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 7, seed=seed)
        if has_pine_sprig:
            pine_side = -1 if vine_side == 'right' else 1
            pine_x = bcx + pine_side * (plinth_w // 2 + 8)
            draw_wuling_pine(surf, pine_x, bot_rect.bottom,
                             22, palette, lean=pine_side * 3, layers=4)

    if top_rect.height > 50:
        _draw_plinth_mist(surf, tcx, top_rect.y + 10,
                          int(top_rect.width * 2.0), palette)
        plinth_h = 7
        plinth_w = int(top_rect.width * 1.18)
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -10),
                         (tcx - plinth_w // 2, top_rect.y, plinth_w, plinth_h))
        pygame.draw.rect(surf, _column_grey(palette),
                         (tcx - plinth_w // 2 + 1, top_rect.y + 1,
                          plinth_w - 2, plinth_h - 2))
        # Reserve the upper ~30 px for Yakushi-ji's signature suien (water-
        # vase) crown so the player diving up reads "Yakushi-ji" not "grey
        # box". The crown hangs immediately under the ceiling anchor.
        accent = _bronze(palette)
        dark_pal = palette['stone_dark']
        bright = _shade(accent, 45)
        crown_top = top_rect.y + plinth_h + 2
        crown_tip = crown_top + 20  # Suien hangs DOWN from anchor.
        # Bronze needle + flame disks pointing down.
        pygame.draw.line(surf, dark_pal,
                         (tcx, crown_top + 2), (tcx, crown_tip - 6), 2)
        pygame.draw.line(surf, accent,
                         (tcx + 1, crown_top + 2), (tcx + 1, crown_tip - 6), 1)
        for k in range(5):
            t = k / 4
            ry = crown_top + 4 + int(t * 12)
            rw = max(2, 5 - k)
            pygame.draw.ellipse(surf, dark_pal,
                                (tcx - rw - 1, ry - 1, rw * 2 + 2, 3))
            pygame.draw.ellipse(surf, accent,
                                (tcx - rw, ry, rw * 2, 2))
        # Inverted suien (water-flame) — the canonical Yakushi-ji silhouette.
        suien = [(tcx, crown_tip),
                 (tcx - 4, crown_tip - 4),
                 (tcx - 2, crown_tip - 7),
                 (tcx + 2, crown_tip - 7),
                 (tcx + 4, crown_tip - 4)]
        pygame.draw.polygon(surf, bright, suien)
        pygame.draw.lines(surf, accent, True, suien, 1)
        # Then the short hanging body BELOW the crown.
        envelope_top = crown_tip + 4
        envelope_bot = top_rect.bottom - 4
        if envelope_bot - envelope_top > 30:
            _draw_yakushiji_to(surf, tcx,
                               envelope_top, envelope_bot,
                               int(top_rect.width * 0.84), palette,
                               tier_count=2, finial_h=10,
                               sorin_up=False, draw_entry_door=False)
        for off in (-8, 8):
            draw_moss_strand(surf, tcx + off, envelope_bot,
                             6 + abs(off) % 3, palette,
                             jitter_seed=seed + off)


def candidate_yakushiji(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('yakushiji', _draw_yakushiji, surf, top_rect, bot_rect,
                 palette, seed)


# ── Round 8 #4. Sensō-ji vermilion pagoda + giant red lantern ──────────────
#
# Sensō-ji 5-storey is heavy vermilion + white. Identity beat for THIS
# candidate: borrow the iconic Kaminarimon red paper lantern and hang it
# from the lowest top eave so the ceiling pagoda becomes a lantern landmark.
# Reference: https://en.wikipedia.org/wiki/Sens%C5%8D-ji

def _draw_sensoji_to(surf, cx, top_y, bot_y, base_w, palette, *,
                    tier_count=4, finial_h=34, sorin_up=True,
                    entry_door_open=False, draw_entry_door=True):
    vermilion = _vermilion(palette)
    vermilion_lit = _vermilion_lit(palette)
    vermilion_shadow = _vermilion_shadow(palette)
    gold = _gold_bright(palette)
    accent = _bronze(palette)
    tile_col = _shade(palette['stone_dark'], -15)

    total_h = bot_y - top_y
    if total_h < 10:
        return
    # Plain vermilion 4-storey body — no white plaster panel, no white-
    # ellipse niches. The lantern is the identity beat; the body is the
    # backdrop. Eaves still flag silhouette.
    weights = [1.0 - 0.06 * i for i in range(tier_count)]
    wsum = sum(weights)
    tier_heights = [max(8, int(total_h * w / wsum)) for w in weights]
    body_widths = [max(12, int(base_w * (0.93 ** i)))
                   for i in range(tier_count)]

    y_cursor = bot_y
    tier_tops = []
    for i in range(tier_count):
        th = tier_heights[i]
        bw = body_widths[i]
        wall_top = y_cursor - th
        if wall_top < top_y - 1:
            break
        tier_tops.append((wall_top, bw, th))
        x_l = cx - bw // 2
        # Plain vermilion wall — gradient body so the lacquer reads as 3-D
        # not a flat red sticker.
        body_rect = pygame.Rect(x_l, wall_top, bw, th)
        _gradient_rect(surf, body_rect, vermilion_lit, vermilion,
                       vermilion_shadow)
        # Heavy vermilion side posts — 4 px (heavier than Daigo-ji's 3).
        for px in (x_l, x_l + bw - 4):
            pygame.draw.rect(surf, vermilion_shadow, (px, wall_top, 4, th))
            pygame.draw.line(surf, vermilion_lit,
                             (px, wall_top), (px, wall_top + th - 1), 1)
        # Gold horizontal trim — visible gilded mid-beam.
        if th > 9:
            beam_y = wall_top + th // 2
            pygame.draw.line(surf, gold,
                             (x_l + 4, beam_y), (x_l + bw - 5, beam_y), 1)
        # Faint dark vertical centre seam — splits the face into two panels
        # so the vermilion body has scaffolding without an ellipse.
        if bw > 18 and th > 7:
            pygame.draw.line(surf, vermilion_shadow,
                             (cx, wall_top + 1), (cx, wall_top + th - 2), 1)
        if i == 0 and draw_entry_door and bw >= 12 and th >= 12:
            _draw_entry_door(surf, cx, wall_top + th - 1, palette,
                             w=2, h=4, open_glow=entry_door_open)
        # Tile eaves — green-glaze tile, vermilion-stained underside.
        overhang = max(10, 13 - i)
        depth = 5
        is_top_tier = (i == tier_count - 1)
        # Use a darker green-ish tile mix.
        roof_tile = _mix(palette['stone_mid'], (78, 98, 88), 0.66)
        _eave_tang_curl(surf, cx, wall_top, bw // 2, overhang, depth,
                        roof_tile, gold, tile_col, curl=0.45,
                        alternating_hatch=True, drop_shadow=True,
                        skip_corner_hook=is_top_tier)
        if is_top_tier:
            half_outer = bw // 2 + overhang
            tip_y_top = wall_top - max(2, int(depth * (0.5 + 0.45)))
            _draw_shibi_finial(surf, cx - half_outer + 1, tip_y_top + 1,
                               palette, side=+1)
            _draw_shibi_finial(surf, cx + half_outer - 1, tip_y_top + 1,
                               palette, side=-1)
        y_cursor = wall_top - depth + 1

    if not tier_tops:
        return

    # Standard gold sōrin.
    top_wall_y = tier_tops[-1][0]
    base_y = top_wall_y - 2 if sorin_up else bot_y + 2
    dir_sign = -1 if sorin_up else 1
    dark_pal = palette['stone_dark']
    bright = _shade(gold, 45)
    pygame.draw.ellipse(surf, dark_pal, (cx - 6, base_y + dir_sign * 1, 12, 5))
    pygame.draw.ellipse(surf, gold, (cx - 5, base_y + dir_sign * 1 + 1, 10, 3))
    needle_tip = base_y + dir_sign * (finial_h - 4)
    pygame.draw.line(surf, dark_pal,
                     (cx - 1, base_y + dir_sign * 4),
                     (cx - 1, needle_tip), 2)
    pygame.draw.line(surf, gold,
                     (cx, base_y + dir_sign * 4),
                     (cx, needle_tip), 1)
    for k in range(9):
        t = k / 8
        ry = base_y + dir_sign * (5 + int(t * (finial_h - 10)))
        rw = max(2, 7 - k // 2)
        pygame.draw.ellipse(surf, dark_pal,
                            (cx - rw - 1, ry - 1, rw * 2 + 2, 3))
        pygame.draw.ellipse(surf, gold,
                            (cx - rw, ry, rw * 2, 2))
    tip_y = base_y + dir_sign * finial_h
    _draw_sorin_flame_halo(surf, cx, tip_y, palette)
    pygame.draw.circle(surf, dark_pal, (cx, tip_y), 3)
    pygame.draw.circle(surf, bright, (cx, tip_y), 2)


def _draw_giant_lantern(surf, cx, top_y, palette, *,
                        lw=36, lh=92):
    """GIANT Kaminarimon chuchin red cylinder + black kanji tablet —
    sized so the lantern IS the silhouette at PIPE_W=58 (32-40 px wide
    × 80-100 px tall by default). Horizontal bamboo ribs across the
    cylinder, gold top + bottom rims, additive amber halo at night.
    `top_y` is the suspension anchor; the body hangs immediately under."""
    red_d = _vermilion_shadow(palette)
    red = _vermilion(palette)
    red_lit = _vermilion_lit(palette)
    gold = _gold_bright(palette)
    dark = palette['stone_dark']
    # 1-px suspension strand from the anchor down to the lantern crown.
    pygame.draw.line(surf, dark, (cx, top_y), (cx, top_y + 3), 1)
    # Lantern body — barrel ellipse anchored under the strand.
    cy = top_y + 3 + lh // 2
    body = pygame.Rect(cx - lw // 2, top_y + 3, lw, lh)
    pygame.draw.ellipse(surf, dark, body)
    pygame.draw.ellipse(surf, red_d, body.inflate(-2, -2))
    # Vertical lit gradient — left side lit, right side darker.
    for col_x in range(body.x + 2, body.right - 1):
        t = (col_x - body.x - 2) / max(1, body.width - 4)
        if t < 0.4:
            col = _mix(red_lit, red, t / 0.4)
        else:
            col = _mix(red, red_d, (t - 0.4) / 0.6)
        # Clip to elliptical body.
        for row_y in range(body.y + 2, body.bottom - 1):
            tt = (row_y - cy) / (lh / 2)
            txc = (col_x - cx) / (lw / 2)
            if txc * txc + tt * tt < 0.95:
                surf.set_at((col_x, row_y), col)
    # Black bamboo rib hoops — horizontal pinstripes spanning the cylinder.
    # Spaced so the chuchin reads as ribbed paper, not a smooth bulb.
    rib_step = max(3, lh // 12)
    for ry in range(body.y + 5, body.bottom - 4, rib_step):
        # Clip ribs to the elliptical envelope.
        tt = (ry - cy) / (lh / 2)
        half = (lw / 2) * math.sqrt(max(0.0, 1.0 - tt * tt))
        if half < 2:
            continue
        pygame.draw.line(surf, dark,
                         (int(cx - half + 1), ry),
                         (int(cx + half - 1), ry), 1)
    # Gold top + bottom rim bands — the chuchin's brass collars.
    rim_top_h = max(3, lh // 16)
    rim_bot_h = max(4, lh // 12)
    pygame.draw.rect(surf, gold,
                     (cx - lw // 2 + 2, body.y, lw - 4, rim_top_h))
    pygame.draw.line(surf, dark,
                     (cx - lw // 2 + 2, body.y + rim_top_h),
                     (cx + lw // 2 - 3, body.y + rim_top_h), 1)
    pygame.draw.rect(surf, gold,
                     (cx - lw // 2 + 2, body.bottom - rim_bot_h,
                      lw - 4, rim_bot_h))
    pygame.draw.line(surf, dark,
                     (cx - lw // 2 + 2, body.bottom - rim_bot_h - 1),
                     (cx + lw // 2 - 3, body.bottom - rim_bot_h - 1), 1)
    # KANJI tablet — black-painted name-plate centred across the cylinder
    # waist. Bigger than before so the calligraphy is legible.
    band_w = max(14, lw - 10)
    band_h = max(18, lh // 4)
    band_x = cx - band_w // 2
    band_y = cy - band_h // 2
    pygame.draw.rect(surf, dark, (band_x, band_y, band_w, band_h))
    pygame.draw.rect(surf, gold, (band_x, band_y, band_w, band_h), 1)
    # Stylised gold kanji — 3 horizontal strokes + a vertical descender so
    # the tablet reads as a name plate even at scale.
    inner_x = band_x + 2
    inner_r = band_x + band_w - 3
    s1 = band_y + max(2, band_h // 5)
    s2 = band_y + band_h // 2
    s3 = band_y + band_h - max(3, band_h // 4)
    for sy in (s1, s2, s3):
        pygame.draw.line(surf, gold, (inner_x, sy), (inner_r, sy), 1)
    pygame.draw.line(surf, gold, (cx, s1), (cx, s3), 1)
    pygame.draw.line(surf, gold,
                     (inner_x + 2, s2 + (s3 - s2) // 2),
                     (inner_r - 2, s2 + (s3 - s2) // 2), 1)
    # Additive halo around the lantern on dark skies — sized to the body.
    if _is_dark_sky(palette) or _is_warming_sky(palette):
        sz = lw + 20
        g = pygame.Surface((sz, sz), pygame.SRCALPHA)
        warm = (255, 180, 100)
        if _is_dark_sky(palette):
            pygame.draw.circle(g, (*warm, 50), (sz // 2, sz // 2), sz // 2 - 1)
            pygame.draw.circle(g, (*warm, 100), (sz // 2, sz // 2), sz // 3)
            pygame.draw.circle(g, (*warm, 160), (sz // 2, sz // 2), sz // 5)
        else:
            pygame.draw.circle(g, (*warm, 70), (sz // 2, sz // 2), sz // 3)
            pygame.draw.circle(g, (*warm, 120), (sz // 2, sz // 2), sz // 6)
        surf.blit(g, (cx - sz // 2, cy - sz // 2),
                  special_flags=pygame.BLEND_RGBA_ADD)
    # Tassel + brass cap dangling under the lantern.
    pygame.draw.line(surf, gold, (cx, body.bottom - 1),
                     (cx, body.bottom + 5), 2)
    pygame.draw.circle(surf, gold, (cx, body.bottom + 6), 2)


def _draw_sensoji(surf, top_rect, bot_rect, palette, seed):
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2
    tier_count = rng.choice([4, 4])
    vine_side = rng.choice(('left', 'right'))
    entry_open = rng.choice((True, False))
    has_pine_sprig = rng.random() < 0.7
    shrub_jitter = rng.randint(-2, 2)

    if bot_rect.height > 50:
        _draw_plinth_mist(surf, bcx, bot_rect.bottom,
                          int(bot_rect.width * 2.4), palette)
        plinth_h = 10
        plinth_w = int(bot_rect.width * 1.22)
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -10),
                         (bcx - plinth_w // 2, bot_rect.bottom - plinth_h,
                          plinth_w, plinth_h))
        pygame.draw.rect(surf, _column_grey(palette),
                         (bcx - plinth_w // 2 + 1,
                          bot_rect.bottom - plinth_h + 1,
                          plinth_w - 2, plinth_h - 2))
        pygame.draw.rect(surf, palette['stone_light'],
                         (bcx - plinth_w // 2,
                          bot_rect.bottom - plinth_h, plinth_w, 1))

        finial_h = 24
        envelope_top = bot_rect.y
        envelope_bot = bot_rect.bottom - plinth_h
        # Body sits BEHIND the lantern; the lantern fills the front half of
        # the visible body and is the identity beat.
        _draw_sensoji_to(surf, bcx,
                         envelope_top + finial_h, envelope_bot,
                         int(bot_rect.width * 0.94), palette,
                         tier_count=tier_count, finial_h=finial_h,
                         sorin_up=True, entry_door_open=entry_open)
        # GIANT Kaminarimon lantern hanging in front of the body — sized
        # ~36 px wide × ~92 px tall so it dominates the silhouette.
        lantern_anchor_y = envelope_top + finial_h + 4
        lantern_h = max(60, min(100, envelope_bot - lantern_anchor_y - 24))
        _draw_giant_lantern(surf, bcx, lantern_anchor_y, palette,
                            lw=36, lh=lantern_h)

        body_half = int(bot_rect.width * 0.94) // 2
        vine_x = bcx - body_half + 1 if vine_side == 'left' else bcx + body_half - 1
        vine_top = max(envelope_top + finial_h + 20, envelope_bot - 70)
        _draw_vine_chunks(surf, vine_x, vine_top, envelope_bot - 4,
                          palette, seed=seed)
        draw_side_shrub(surf, bcx - plinth_w // 2 - 2 + shrub_jitter,
                        bot_rect.bottom - 2, palette, scale=0.9)
        draw_side_shrub(surf, bcx + plinth_w // 2 + 2 - shrub_jitter,
                        bot_rect.bottom - 2, palette, scale=0.9)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 10, 16, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 7, seed=seed)
        if has_pine_sprig:
            pine_side = -1 if vine_side == 'right' else 1
            pine_x = bcx + pine_side * (plinth_w // 2 + 8)
            draw_wuling_pine(surf, pine_x, bot_rect.bottom,
                             22, palette, lean=pine_side * 3, layers=4)

    if top_rect.height > 50:
        _draw_plinth_mist(surf, tcx, top_rect.y + 10,
                          int(top_rect.width * 2.0), palette)
        # Heavy gate-style anchor beam — Sensō-ji's lantern hangs from a
        # massive vermilion lintel.
        anchor_h = 10
        anchor_w = int(top_rect.width * 1.4)
        ar = pygame.Rect(tcx - anchor_w // 2, top_rect.y, anchor_w, anchor_h)
        pygame.draw.rect(surf, _vermilion_shadow(palette), ar)
        pygame.draw.rect(surf, _vermilion(palette),
                         (ar.x + 1, ar.y + 1, ar.w - 2, ar.h - 2))
        pygame.draw.rect(surf, _gold_bright(palette),
                         (ar.x + 2, ar.y + 2, ar.w - 4, 2))
        pygame.draw.rect(surf, _gold_bright(palette),
                         (ar.x + 2, ar.bottom - 4, ar.w - 4, 2))
        # GIANT lantern — the identity beat.
        _draw_giant_lantern(surf, tcx, top_rect.y + anchor_h, palette)


def candidate_sensoji(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('sensoji', _draw_sensoji, surf, top_rect, bot_rect,
                 palette, seed)


# ── Round 8 #5. Tahōtō — Ishiyama-dera Round-Body 2-Storey (1194) ──────────
#
# Hemispherical white-plaster body cradled between TWO eaves with a sōrin
# on top. Totally distinct silhouette.
# Reference: https://en.wikipedia.org/wiki/Tah%C5%8Dt%C5%8D

def _draw_tahoto(surf, top_rect, bot_rect, palette, seed):
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2
    vine_side = rng.choice(('left', 'right'))
    entry_open = rng.choice((True, False))
    has_pine_sprig = rng.random() < 0.7
    shrub_jitter = rng.randint(-2, 2)

    cedar = _cedar(palette)
    plaster = _white_plaster_warm(palette)
    plaster_lit = _shade(plaster, 22)
    plaster_shadow = _shade(plaster, -28)
    accent = _bronze(palette)
    tile_col = _shade(palette['stone_dark'], -15)

    if bot_rect.height > 80:
        _draw_plinth_mist(surf, bcx, bot_rect.bottom,
                          int(bot_rect.width * 2.4), palette)
        plinth_h = 10
        plinth_w = int(bot_rect.width * 1.25)
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -10),
                         (bcx - plinth_w // 2, bot_rect.bottom - plinth_h,
                          plinth_w, plinth_h))
        pygame.draw.rect(surf, _column_grey(palette),
                         (bcx - plinth_w // 2 + 1,
                          bot_rect.bottom - plinth_h + 1,
                          plinth_w - 2, plinth_h - 2))
        pygame.draw.rect(surf, palette['stone_light'],
                         (bcx - plinth_w // 2,
                          bot_rect.bottom - plinth_h, plinth_w, 1))

        envelope_bot = bot_rect.bottom - plinth_h
        total_h = min(bot_rect.height - plinth_h, 240)
        # Budget: 30% lower square storey, 8% mokoshi pent, 30% kamebara
        # cylinder/dome, 12% upper square + roof, 20% sōrin finial.
        lower_h = int(total_h * 0.30)
        moko_h = max(4, int(total_h * 0.08))
        dome_h = int(total_h * 0.30)
        upper_h = int(total_h * 0.12)
        finial_h = total_h - lower_h - moko_h - dome_h - upper_h

        # Lower square storey — cedar + plaster wide base.
        lower_top = envelope_bot - lower_h
        lower_w = int(bot_rect.width * 1.05)
        x_l = bcx - lower_w // 2
        pygame.draw.rect(surf, _shade(plaster, -28),
                         (x_l, lower_top, lower_w, lower_h))
        inner = pygame.Rect(x_l + 2, lower_top + 1,
                            lower_w - 4, lower_h - 1)
        _gradient_rect(surf, inner, plaster_lit, plaster, plaster_shadow)
        # Cedar posts — 4 across, since the tahōtō base is square + showy.
        for k in range(4):
            t = k / 3
            px = x_l + int(t * (lower_w - 2))
            pygame.draw.rect(surf, _shade(cedar, -25), (px, lower_top, 2, lower_h))
            pygame.draw.line(surf, _shade(cedar, 20),
                             (px, lower_top), (px, lower_top + lower_h - 1), 1)
        # Nageshi rail.
        if lower_h > 14:
            for frac in (1 / 3, 2 / 3):
                rail_y = lower_top + int(lower_h * frac)
                pygame.draw.line(surf, plaster_shadow,
                                 (x_l + 2, rail_y),
                                 (x_l + lower_w - 3, rail_y), 1)
        # Big central doorway niche.
        _lit_niche(surf, bcx, lower_top + 4,
                   min(8, lower_w - 16), min(10, lower_h - 8), palette)
        _draw_entry_door(surf, bcx, lower_top + lower_h - 1, palette,
                         w=2, h=5, open_glow=entry_open)

        # Mokoshi pent roof — Tahōtō's lower eave. Wider than Yakushi-ji's.
        moko_y = lower_top - 1
        _draw_mokoshi_pent(surf, bcx, moko_y, lower_w // 2 - 2, palette,
                           depth=moko_h)

        # Hemispherical KAMEBARA — the signature round white body.
        dome_base_y = moko_y - moko_h
        dome_w = int(bot_rect.width * 0.86)
        dome_top_y = _draw_tahoto_dome(surf, bcx, dome_base_y, dome_h,
                                       dome_w, palette)
        # Sumeru frieze around the kamebara waist — a band of vertical
        # cedar dashes simulating the wood frame around the cylinder.
        waist_y = dome_base_y - dome_h // 2
        for dx in range(-dome_w // 2 + 4, dome_w // 2 - 3, 3):
            pygame.draw.line(surf, _shade(cedar, -10),
                             (bcx + dx, waist_y - 1),
                             (bcx + dx, waist_y + 1), 1)

        # Upper square section above the kamebara — short cube with niche.
        upper_y_top = dome_top_y - upper_h
        upper_w = int(dome_w * 0.55)
        pygame.draw.rect(surf, _shade(plaster, -28),
                         (bcx - upper_w // 2, upper_y_top, upper_w, upper_h))
        _gradient_rect(surf,
                       pygame.Rect(bcx - upper_w // 2 + 1, upper_y_top + 1,
                                   upper_w - 2, upper_h - 2),
                       plaster_lit, plaster, plaster_shadow)
        # Upper pyramidal roof — drawn directly via _eave_tang_curl but
        # with extreme curl (pyramidal upturn).
        _eave_tang_curl(surf, bcx, upper_y_top, upper_w // 2,
                        max(7, upper_w // 3), 5,
                        cedar, accent, tile_col, curl=0.6,
                        alternating_hatch=True, drop_shadow=True,
                        skip_corner_hook=True)
        # Topmost shibi finials.
        half_outer = upper_w // 2 + max(7, upper_w // 3)
        _draw_shibi_finial(surf, bcx - half_outer + 1,
                           upper_y_top - 4, palette, side=+1)
        _draw_shibi_finial(surf, bcx + half_outer - 1,
                           upper_y_top - 4, palette, side=-1)

        # Bronze sōrin — short, 7-disk.
        sorin_base = upper_y_top - 5
        sorin_tip = sorin_base - finial_h
        dark_pal = palette['stone_dark']
        pygame.draw.ellipse(surf, dark_pal,
                            (bcx - 5, sorin_base - 2, 10, 4))
        pygame.draw.ellipse(surf, accent,
                            (bcx - 4, sorin_base - 1, 8, 2))
        pygame.draw.line(surf, accent, (bcx, sorin_base),
                         (bcx, sorin_tip), 1)
        for k in range(7):
            t = k / 6
            ry = sorin_base - int(t * (finial_h - 4))
            rw = max(2, 6 - k // 2)
            pygame.draw.ellipse(surf, dark_pal,
                                (bcx - rw - 1, ry - 1, rw * 2 + 2, 3))
            pygame.draw.ellipse(surf, accent,
                                (bcx - rw, ry, rw * 2, 2))
        _draw_sorin_flame_halo(surf, bcx, sorin_tip, palette)
        pygame.draw.circle(surf, dark_pal, (bcx, sorin_tip), 3)
        pygame.draw.circle(surf, _shade(accent, 45), (bcx, sorin_tip), 2)
        pygame.draw.polygon(surf, _shade(accent, 60),
                            [(bcx, sorin_tip - 5),
                             (bcx - 2, sorin_tip - 1),
                             (bcx + 2, sorin_tip - 1)])

        # Foliage.
        body_half = lower_w // 2
        vine_x = bcx - body_half + 1 if vine_side == 'left' else bcx + body_half - 1
        _draw_vine_chunks(surf, vine_x, lower_top + 12, envelope_bot - 4,
                          palette, seed=seed)
        draw_side_shrub(surf, bcx - plinth_w // 2 - 2 + shrub_jitter,
                        bot_rect.bottom - 2, palette, scale=0.9)
        draw_side_shrub(surf, bcx + plinth_w // 2 + 2 - shrub_jitter,
                        bot_rect.bottom - 2, palette, scale=0.9)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 10, 16, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 7, seed=seed)
        if has_pine_sprig:
            pine_side = -1 if vine_side == 'right' else 1
            pine_x = bcx + pine_side * (plinth_w // 2 + 8)
            draw_wuling_pine(surf, pine_x, bot_rect.bottom,
                             22, palette, lean=pine_side * 3, layers=4)

    if top_rect.height > 50:
        _draw_plinth_mist(surf, tcx, top_rect.y + 10,
                          int(top_rect.width * 2.0), palette)
        # Hanging mini-tahōtō from the ceiling — small dome + pyramidal cap.
        anchor_h = 8
        anchor_w = int(top_rect.width * 1.15)
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -10),
                         (tcx - anchor_w // 2, top_rect.y, anchor_w, anchor_h))
        pygame.draw.rect(surf, _column_grey(palette),
                         (tcx - anchor_w // 2 + 1, top_rect.y + 1,
                          anchor_w - 2, anchor_h - 2))
        # Cap = pyramidal roof first (it sits at the TOP of the hanging).
        cap_y = top_rect.y + anchor_h + 6
        cap_w = int(top_rect.width * 0.62)
        _eave_tang_inverted(surf, tcx, cap_y, cap_w // 2,
                            max(6, cap_w // 4), 4, cedar, accent, tile_col,
                            curl=0.6)
        # Then upper square + dome below.
        upper_h = 10
        upper_w = int(cap_w * 0.7)
        pygame.draw.rect(surf, _shade(plaster, -28),
                         (tcx - upper_w // 2, cap_y + 1, upper_w, upper_h))
        _gradient_rect(surf,
                       pygame.Rect(tcx - upper_w // 2 + 1, cap_y + 2,
                                   upper_w - 2, upper_h - 2),
                       plaster_lit, plaster, plaster_shadow)
        # Hanging mini-dome — draw ONLY the lower half of an ellipse so
        # the silhouette reads as a downward-opening dome. We paint into
        # a temp SRCALPHA, mask off the top half by alpha-clearing it,
        # and blit so the live sky shows above the rim.
        dome_w = int(top_rect.width * 0.7)
        dome_h = 14
        dome_top = cap_y + upper_h + 2
        tmp = pygame.Surface((dome_w + 4, dome_h * 2 + 2), pygame.SRCALPHA)
        full = pygame.Rect(2, 1, dome_w, dome_h * 2)
        pygame.draw.ellipse(tmp, _shade(plaster, -55), full)
        pygame.draw.ellipse(tmp, plaster, full.inflate(-2, -2))
        pygame.draw.ellipse(tmp, plaster_lit,
                            (4, 3, dome_w - 4, dome_h - 2))
        # Punch out the top half by clearing alpha to 0 with a fill rect.
        tmp.fill((0, 0, 0, 0),
                 rect=pygame.Rect(0, 0, dome_w + 4, dome_h),
                 special_flags=pygame.BLEND_RGBA_SUB)
        surf.blit(tmp, (tcx - (dome_w + 4) // 2, dome_top - 1))


def candidate_tahoto(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('tahoto', _draw_tahoto, surf, top_rect, bot_rect,
                 palette, seed)


# ── Round 8 #6. Liuhe (Six Harmonies) Pagoda (Hangzhou, 1165) ──────────────
#
# 13 visible storeys, brick body + dense wooden eaves, ascending ochre.
# Tall + ascending feel — many many eaves stacked.
# Reference: https://en.wikipedia.org/wiki/Liuhe_Pagoda

def _draw_liuhe(surf, top_rect, bot_rect, palette, seed):
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2
    vine_side = rng.choice(('left', 'right'))
    entry_open = rng.choice((True, False))
    has_pine_sprig = rng.random() < 0.7
    shrub_jitter = rng.randint(-2, 2)

    ochre = _liuhe_ochre(palette)
    ochre_lit = _liuhe_ochre_lit(palette)
    ochre_shadow = _liuhe_ochre_shadow(palette)
    grey_tile = _mix(palette['stone_mid'], (118, 110, 100), 0.62)
    accent = _bronze(palette)
    tile_col = _shade(grey_tile, -20)
    fringe_col = _shade(grey_tile, -15)

    if bot_rect.height > 80:
        _draw_plinth_mist(surf, bcx, bot_rect.bottom,
                          int(bot_rect.width * 2.4), palette)
        plinth_h = 9
        plinth_w = int(bot_rect.width * 1.22)
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -10),
                         (bcx - plinth_w // 2, bot_rect.bottom - plinth_h,
                          plinth_w, plinth_h))
        pygame.draw.rect(surf, _column_grey(palette),
                         (bcx - plinth_w // 2 + 1,
                          bot_rect.bottom - plinth_h + 1,
                          plinth_w - 2, plinth_h - 2))
        pygame.draw.rect(surf, palette['stone_light'],
                         (bcx - plinth_w // 2,
                          bot_rect.bottom - plinth_h, plinth_w, 1))

        envelope_bot = bot_rect.bottom - plinth_h
        # 13 storeys is the Liuhe identity — pack many thin eaves.
        tier_count = 13
        finial_h = 24
        total_h = min(bot_rect.height - plinth_h - finial_h, 240)
        # Storey heights linearly shrinking toward the top.
        weights = [1.0 - 0.04 * i for i in range(tier_count)]
        wsum = sum(weights)
        tier_heights = [max(4, int(total_h * w / wsum)) for w in weights]
        # Body widths ascend in a smooth taper.
        body_widths = [max(10, int(bot_rect.width * (1.0 - 0.03 * i)))
                       for i in range(tier_count)]

        y_cursor = envelope_bot
        tier_tops = []
        for i in range(tier_count):
            th = tier_heights[i]
            bw = body_widths[i]
            wall_top = y_cursor - th
            if wall_top < bot_rect.y + finial_h:
                break
            tier_tops.append((wall_top, bw, th))
            x_l = bcx - bw // 2
            # Brick body with horizontal taper.
            body_rect = pygame.Rect(x_l, wall_top, bw, th)
            _gradient_rect(surf, body_rect, ochre_lit, ochre, ochre_shadow)
            # 2-px brick mortar lines — 3 horizontal lines for the brick
            # courses cue.
            if th >= 5:
                for k in range(1, max(2, th // 2)):
                    if k * 2 >= th:
                        break
                    pygame.draw.line(surf, ochre_shadow,
                                     (x_l + 1, wall_top + k * 2),
                                     (x_l + bw - 2, wall_top + k * 2), 1)
            # ONE centred lit window per storey — bright at night/dusk,
            # dark door slit at day. Niches replace the dot-row that
            # collapsed at PIPE_W=58.
            if th > 4 and bw > 14:
                nw = min(3, bw // 8)
                nh = max(2, min(3, th - 2))
                if _is_dark_sky(palette) or _is_warming_sky(palette):
                    _lit_niche(surf, bcx, wall_top + 1, nw, nh, palette)
                else:
                    pygame.draw.rect(surf, ochre_shadow,
                                     (bcx - nw // 2, wall_top + 1,
                                      nw, nh))
            if i == 0 and bw >= 14 and th >= 8:
                _draw_entry_door(surf, bcx, wall_top + th - 1, palette,
                                 w=2, h=4, open_glow=entry_open)
            # Thin grey-tile eave with strong corner curl + pendant fringe.
            overhang = max(8, 11 - i // 3)
            depth = 3
            is_top_tier = (i == tier_count - 1)
            _eave_tang_curl(surf, bcx, wall_top, bw // 2, overhang, depth,
                            grey_tile, accent, tile_col, curl=0.70,
                            fringe=True, fringe_col=fringe_col,
                            drop_shadow=True,
                            skip_corner_hook=is_top_tier)
            # Tiny iron-bell hanging from eave tips — Liuhe has 104. Bells
            # ALTERNATE left/right per storey, with the starting side
            # toggled by seed parity so adjacent Liuhe pillars aren't
            # pixel-identical bunting. Drawn 2 px taller for legibility.
            if i % 2 == 0:
                half_outer = bw // 2 + overhang
                bell_y = wall_top + 1
                start_side = -1 if (seed % 2 == 0) else 1
                bell_sign = start_side if (i // 2) % 2 == 0 else -start_side
                bx = bcx + bell_sign * (half_outer - 2)
                pygame.draw.line(surf, _shade(accent, -25),
                                 (bx, bell_y), (bx, bell_y + 3), 1)
                pygame.draw.circle(surf, accent, (bx, bell_y + 4), 2)
                pygame.draw.circle(surf, _shade(accent, 35),
                                   (bx - 1, bell_y + 3), 1)
            y_cursor = wall_top - depth + 1

        # Bronze finial — short.
        if tier_tops:
            top_wall_y = tier_tops[-1][0]
            dark_pal = palette['stone_dark']
            bright = _shade(accent, 45)
            tip_y = top_wall_y - finial_h
            pygame.draw.line(surf, dark_pal, (bcx, top_wall_y - 4),
                             (bcx, tip_y), 2)
            pygame.draw.line(surf, accent, (bcx + 1, top_wall_y - 4),
                             (bcx + 1, tip_y), 1)
            for k in range(5):
                t = k / 4
                ry = top_wall_y - 4 - int(t * (finial_h - 6))
                rw = max(2, 5 - k)
                pygame.draw.ellipse(surf, dark_pal,
                                    (bcx - rw - 1, ry - 1, rw * 2 + 2, 3))
                pygame.draw.ellipse(surf, accent,
                                    (bcx - rw, ry, rw * 2, 2))
            _draw_sorin_flame_halo(surf, bcx, tip_y, palette)
            pygame.draw.circle(surf, dark_pal, (bcx, tip_y), 3)
            pygame.draw.circle(surf, bright, (bcx, tip_y), 2)

        body_half = bot_rect.width // 2
        vine_x = bcx - body_half + 1 if vine_side == 'left' else bcx + body_half - 1
        _draw_vine_chunks(surf, vine_x, envelope_bot - 60,
                          envelope_bot - 4, palette, seed=seed)
        draw_side_shrub(surf, bcx - plinth_w // 2 - 2 + shrub_jitter,
                        bot_rect.bottom - 2, palette, scale=0.9)
        draw_side_shrub(surf, bcx + plinth_w // 2 + 2 - shrub_jitter,
                        bot_rect.bottom - 2, palette, scale=0.9)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 10, 16, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 7, seed=seed)
        if has_pine_sprig:
            pine_side = -1 if vine_side == 'right' else 1
            pine_x = bcx + pine_side * (plinth_w // 2 + 8)
            draw_wuling_pine(surf, pine_x, bot_rect.bottom,
                             22, palette, lean=pine_side * 3, layers=4)

    if top_rect.height > 50:
        _draw_plinth_mist(surf, tcx, top_rect.y + 10,
                          int(top_rect.width * 2.0), palette)
        # Hanging short version of Liuhe — 6 visible storeys hung from the
        # ceiling, each with one tile eave + iron bell.
        anchor_h = 6
        anchor_w = int(top_rect.width * 1.18)
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -10),
                         (tcx - anchor_w // 2, top_rect.y, anchor_w, anchor_h))
        pygame.draw.rect(surf, _column_grey(palette),
                         (tcx - anchor_w // 2 + 1, top_rect.y + 1,
                          anchor_w - 2, anchor_h - 2))
        envelope_top = top_rect.y + anchor_h
        envelope_bot = top_rect.bottom - 4
        hanger_tiers = 6
        total_hang = envelope_bot - envelope_top
        th_each = max(5, total_hang // hanger_tiers)
        for k in range(hanger_tiers):
            wall_top = envelope_top + k * th_each
            bw = max(10, int(top_rect.width * (1.0 - 0.03 * k)))
            x_l = tcx - bw // 2
            body_rect = pygame.Rect(x_l, wall_top, bw, th_each - 3)
            _gradient_rect(surf, body_rect, ochre_lit, ochre, ochre_shadow)
            # Inverted eave below.
            _eave_tang_inverted(surf, tcx, wall_top + th_each - 3,
                                bw // 2, max(7, 10 - k // 2), 3,
                                grey_tile, accent, tile_col, curl=0.70)


def candidate_liuhe(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('liuhe', _draw_liuhe, surf, top_rect, bot_rect,
                 palette, seed)


# ── Round 8 #7. Bao'en — Nanjing Porcelain Tower (Ming) ────────────────────
#
# Once-iconic 9-storey white-glazed porcelain tower with painted floral
# panels at each storey + gilt eaves + interior glow at night.
# Reference: https://en.wikipedia.org/wiki/Porcelain_Tower_of_Nanjing

def _draw_baoen(surf, top_rect, bot_rect, palette, seed):
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2
    vine_side = rng.choice(('left', 'right'))
    entry_open = rng.choice((True, False))
    has_pine_sprig = rng.random() < 0.7
    shrub_jitter = rng.randint(-2, 2)

    white = _porcelain_white(palette)
    white_lit = _shade(white, 18)
    white_shadow = _shade(white, -28)
    gold = _gold_bright(palette)
    gold_d = _gold_deep(palette)
    accent = _bronze(palette)
    tile_col = _shade(gold_d, -20)

    if bot_rect.height > 80:
        _draw_plinth_mist(surf, bcx, bot_rect.bottom,
                          int(bot_rect.width * 2.4), palette)
        plinth_h = 10
        plinth_w = int(bot_rect.width * 1.25)
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -10),
                         (bcx - plinth_w // 2, bot_rect.bottom - plinth_h,
                          plinth_w, plinth_h))
        pygame.draw.rect(surf, _column_grey(palette),
                         (bcx - plinth_w // 2 + 1,
                          bot_rect.bottom - plinth_h + 1,
                          plinth_w - 2, plinth_h - 2))
        pygame.draw.rect(surf, palette['stone_light'],
                         (bcx - plinth_w // 2,
                          bot_rect.bottom - plinth_h, plinth_w, 1))

        envelope_bot = bot_rect.bottom - plinth_h
        tier_count = 9
        finial_h = 30
        total_h = min(bot_rect.height - plinth_h - finial_h, 230)
        weights = [1.0 - 0.06 * i for i in range(tier_count)]
        wsum = sum(weights)
        tier_heights = [max(7, int(total_h * w / wsum)) for w in weights]
        body_widths = [max(12, int(bot_rect.width * (0.94 ** i)))
                       for i in range(tier_count)]

        y_cursor = envelope_bot
        tier_tops = []
        for i in range(tier_count):
            th = tier_heights[i]
            bw = body_widths[i]
            wall_top = y_cursor - th
            if wall_top < bot_rect.y + finial_h:
                break
            tier_tops.append((wall_top, bw, th))
            x_l = bcx - bw // 2
            body_rect = pygame.Rect(x_l, wall_top, bw, th)
            # White porcelain body — vertically lit (top whiter, bottom
            # slightly cooler) so the glaze reads as glossy ceramic.
            _gradient_rect(surf, body_rect, white_lit, white, white_shadow,
                           vertical=True)
            # ONE tall vertical aqua-on-white scroll per storey body — the
            # round-8 3-pill panel row read as UI pills. A single narrow
            # painted scroll keeps the porcelain identity without dazzle.
            if bw >= 18 and th >= 8:
                scroll_w = max(4, bw // 5)
                scroll_h = min(th - 2, max(6, th - 3))
                scroll_y = wall_top + (th - scroll_h) // 2
                _draw_baoen_scroll(surf, bcx, scroll_y,
                                   scroll_w, scroll_h, palette)
            # ONE centred lit window per storey (cross-row unification) —
            # bright at night, dark slit at day. Sits beside the scroll.
            if th > 8 and bw > 18:
                nw = max(2, bw // 8)
                nh = min(4, th - 4)
                # Window offset to the right of the scroll so they coexist.
                win_x = bcx + bw // 4
                if _is_dark_sky(palette) or _is_warming_sky(palette):
                    _lit_niche(surf, win_x, wall_top + 2, nw, nh, palette)
                else:
                    pygame.draw.rect(surf, _shade(white, -45),
                                     (win_x - nw // 2, wall_top + 2,
                                      nw, nh))
            if i == 0 and bw >= 14 and th >= 10:
                _draw_entry_door(surf, bcx, wall_top + th - 1, palette,
                                 w=2, h=4, open_glow=entry_open)
            # GILT eave — Bao'en's eaves are gilded. Use gold as roof.
            overhang = max(10, 13 - i)
            depth = 4
            is_top_tier = (i == tier_count - 1)
            _eave_tang_curl(surf, bcx, wall_top, bw // 2, overhang, depth,
                            gold_d, gold, tile_col, curl=0.55,
                            alternating_hatch=True, drop_shadow=True,
                            skip_corner_hook=is_top_tier)
            # Lantern dangling at the corner — Bao'en was said to have 140
            # lamps. Render compact dots only every 2 storeys.
            if i % 2 == 1:
                half_outer = bw // 2 + overhang
                for sign in (-1, 1):
                    _draw_mini_lantern(surf, bcx + sign * (half_outer - 2),
                                       wall_top, palette)
            if is_top_tier:
                half_outer = bw // 2 + overhang
                tip_y_top = wall_top - max(2, int(depth * (0.5 + 0.55)))
                _draw_chiwen_finial(surf, bcx - half_outer + 1,
                                    tip_y_top + 1, palette, side=+1)
                _draw_chiwen_finial(surf, bcx + half_outer - 1,
                                    tip_y_top + 1, palette, side=-1)
            y_cursor = wall_top - depth + 1

        # Tall gilt-bronze finial — a pearl-and-flame on a needle.
        if tier_tops:
            top_wall_y = tier_tops[-1][0]
            dark_pal = palette['stone_dark']
            bright = _shade(gold, 60)
            tip_y = top_wall_y - finial_h
            pygame.draw.line(surf, dark_pal, (bcx, top_wall_y - 2),
                             (bcx, tip_y), 2)
            pygame.draw.line(surf, gold, (bcx + 1, top_wall_y - 2),
                             (bcx + 1, tip_y), 1)
            for k in range(7):
                t = k / 6
                ry = top_wall_y - 2 - int(t * (finial_h - 6))
                rw = max(2, 6 - k // 2)
                pygame.draw.ellipse(surf, dark_pal,
                                    (bcx - rw - 1, ry - 1, rw * 2 + 2, 3))
                pygame.draw.ellipse(surf, gold,
                                    (bcx - rw, ry, rw * 2, 2))
            _draw_sorin_flame_halo(surf, bcx, tip_y, palette)
            pygame.draw.circle(surf, dark_pal, (bcx, tip_y), 4)
            pygame.draw.circle(surf, gold, (bcx, tip_y), 3)
            pygame.draw.circle(surf, bright, (bcx - 1, tip_y - 1), 1)

        body_half = bot_rect.width // 2
        vine_x = bcx - body_half + 1 if vine_side == 'left' else bcx + body_half - 1
        _draw_vine_chunks(surf, vine_x, envelope_bot - 70,
                          envelope_bot - 4, palette, seed=seed)
        draw_side_shrub(surf, bcx - plinth_w // 2 - 2 + shrub_jitter,
                        bot_rect.bottom - 2, palette, scale=0.9)
        draw_side_shrub(surf, bcx + plinth_w // 2 + 2 - shrub_jitter,
                        bot_rect.bottom - 2, palette, scale=0.9)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 10, 16, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 7, seed=seed)
        if has_pine_sprig:
            pine_side = -1 if vine_side == 'right' else 1
            pine_x = bcx + pine_side * (plinth_w // 2 + 8)
            draw_wuling_pine(surf, pine_x, bot_rect.bottom,
                             22, palette, lean=pine_side * 3, layers=4)

    if top_rect.height > 50:
        _draw_plinth_mist(surf, tcx, top_rect.y + 10,
                          int(top_rect.width * 2.0), palette)
        # Hanging porcelain pendant — short 3-storey mini Bao'en with
        # painted panels mirrored.
        anchor_h = 8
        anchor_w = int(top_rect.width * 1.18)
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -10),
                         (tcx - anchor_w // 2, top_rect.y, anchor_w, anchor_h))
        pygame.draw.rect(surf, _column_grey(palette),
                         (tcx - anchor_w // 2 + 1, top_rect.y + 1,
                          anchor_w - 2, anchor_h - 2))
        envelope_top = top_rect.y + anchor_h
        envelope_bot = top_rect.bottom - 6
        hanger_tiers = 3
        total_hang = envelope_bot - envelope_top
        th_each = max(10, total_hang // hanger_tiers)
        for k in range(hanger_tiers):
            wall_top = envelope_top + k * th_each
            bw = max(12, int(top_rect.width * (0.94 ** k)))
            x_l = tcx - bw // 2
            body_rect = pygame.Rect(x_l, wall_top, bw, th_each - 4)
            _gradient_rect(surf, body_rect, white_lit, white, white_shadow,
                           vertical=True)
            # Single mini scroll on each hanger storey body so the
            # hanger reads as Bao'en, not as a generic porcelain block.
            if bw >= 14:
                sc_w = max(3, bw // 5)
                sc_h = min(th_each - 6, max(5, th_each // 2))
                sc_y = wall_top + (th_each - 4 - sc_h) // 2
                _draw_baoen_scroll(surf, tcx, sc_y, sc_w, sc_h, palette)
            _eave_tang_inverted(surf, tcx, wall_top + th_each - 4,
                                bw // 2, max(8, 12 - k), 3,
                                gold_d, gold, tile_col, curl=0.55)


def candidate_baoen(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('baoen', _draw_baoen, surf, top_rect, bot_rect, palette, seed)


# ── Round 8 #8. Liaodi Pagoda (Dingzhou, Northern Song 1055) ───────────────
#
# Tallest pre-modern brick pagoda in China. 11 storeys, octagonal,
# whitewashed brick, slim, shallow eaves. Severe minimalism.
# Reference: https://en.wikipedia.org/wiki/Liaodi_Pagoda

def _draw_liaodi(surf, top_rect, bot_rect, palette, seed):
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2
    vine_side = rng.choice(('left', 'right'))
    entry_open = rng.choice((True, False))
    has_pine_sprig = rng.random() < 0.7
    shrub_jitter = rng.randint(-2, 2)

    white = _whitebrick(palette)
    white_shadow = _whitebrick_shadow(palette)
    white_lit = _shade(white, 22)
    grey_tile = _mix(palette['stone_mid'], (138, 130, 118), 0.62)
    accent = _bronze(palette)
    tile_col = _shade(grey_tile, -20)

    if bot_rect.height > 80:
        _draw_plinth_mist(surf, bcx, bot_rect.bottom,
                          int(bot_rect.width * 2.4), palette)
        plinth_h = 8
        plinth_w = int(bot_rect.width * 1.18)
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -10),
                         (bcx - plinth_w // 2, bot_rect.bottom - plinth_h,
                          plinth_w, plinth_h))
        pygame.draw.rect(surf, _column_grey(palette),
                         (bcx - plinth_w // 2 + 1,
                          bot_rect.bottom - plinth_h + 1,
                          plinth_w - 2, plinth_h - 2))
        pygame.draw.rect(surf, palette['stone_light'],
                         (bcx - plinth_w // 2,
                          bot_rect.bottom - plinth_h, plinth_w, 1))

        envelope_bot = bot_rect.bottom - plinth_h
        tier_count = 11
        finial_h = 22
        total_h = min(bot_rect.height - plinth_h - finial_h, 235)
        # Liaodi is famously slim + tall — taper very gently.
        weights = [1.0 - 0.025 * i for i in range(tier_count)]
        wsum = sum(weights)
        tier_heights = [max(6, int(total_h * w / wsum)) for w in weights]
        body_widths = [max(10, int(bot_rect.width * (0.97 ** i)))
                       for i in range(tier_count)]

        y_cursor = envelope_bot
        tier_tops = []
        for i in range(tier_count):
            th = tier_heights[i]
            bw = body_widths[i]
            wall_top = y_cursor - th
            if wall_top < bot_rect.y + finial_h:
                break
            tier_tops.append((wall_top, bw, th))
            x_l = bcx - bw // 2
            body_rect = pygame.Rect(x_l, wall_top, bw, th)
            _gradient_rect(surf, body_rect, white_lit, white, white_shadow)
            # 3 fine horizontal brick courses — the bleached-brick cue.
            for k in range(1, max(2, th // 2)):
                cy = wall_top + k * 2
                if cy >= wall_top + th - 1:
                    break
                pygame.draw.line(surf, white_shadow,
                                 (x_l + 1, cy), (x_l + bw - 2, cy), 1)
            # Rim shading along the gap-facing edge — keeps the slim
            # tower from flattening against a bright day sky. The left
            # edge gets a 1-px cool shadow.
            pygame.draw.line(surf, white_shadow,
                             (x_l, wall_top + 1),
                             (x_l, wall_top + th - 2), 1)
            pygame.draw.line(surf, _shade(white_shadow, -10),
                             (x_l - 1, wall_top + 1),
                             (x_l - 1, wall_top + th - 2), 1)
            # ONE narrow tall niche per storey (true to the real Liaodi).
            if th > 6 and bw > 12:
                nh = min(th - 3, 5)
                _lit_niche(surf, bcx, wall_top + 1,
                           min(4, bw // 6), nh, palette)
            if i == 0 and bw >= 12 and th >= 8:
                _draw_entry_door(surf, bcx, wall_top + th - 1, palette,
                                 w=2, h=4, open_glow=entry_open)
            # Very shallow grey-tile eave — Liaodi has tiered stone-eaves
            # that read almost as capping bands.
            overhang = max(7, 10 - i // 2)
            depth = 2
            is_top_tier = (i == tier_count - 1)
            _eave_tang_curl(surf, bcx, wall_top, bw // 2, overhang, depth,
                            grey_tile, accent, tile_col, curl=0.30,
                            drop_shadow=True,
                            skip_corner_hook=is_top_tier)
            y_cursor = wall_top - depth + 1

        # Slender bronze finial.
        if tier_tops:
            top_wall_y = tier_tops[-1][0]
            dark_pal = palette['stone_dark']
            tip_y = top_wall_y - finial_h
            pygame.draw.line(surf, dark_pal,
                             (bcx, top_wall_y - 2), (bcx, tip_y), 2)
            pygame.draw.line(surf, accent,
                             (bcx + 1, top_wall_y - 2), (bcx + 1, tip_y), 1)
            for k in range(5):
                t = k / 4
                ry = top_wall_y - 2 - int(t * (finial_h - 4))
                rw = max(2, 4 - k // 2)
                pygame.draw.ellipse(surf, dark_pal,
                                    (bcx - rw - 1, ry - 1, rw * 2 + 2, 3))
                pygame.draw.ellipse(surf, accent,
                                    (bcx - rw, ry, rw * 2, 2))
            _draw_sorin_flame_halo(surf, bcx, tip_y, palette)
            pygame.draw.circle(surf, dark_pal, (bcx, tip_y), 3)
            pygame.draw.circle(surf, _shade(accent, 45), (bcx, tip_y), 2)

        body_half = bot_rect.width // 2
        vine_x = bcx - body_half + 1 if vine_side == 'left' else bcx + body_half - 1
        _draw_vine_chunks(surf, vine_x, envelope_bot - 70,
                          envelope_bot - 4, palette, seed=seed)
        draw_side_shrub(surf, bcx - plinth_w // 2 - 2 + shrub_jitter,
                        bot_rect.bottom - 2, palette, scale=0.9)
        draw_side_shrub(surf, bcx + plinth_w // 2 + 2 - shrub_jitter,
                        bot_rect.bottom - 2, palette, scale=0.9)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 10, 16, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 7, seed=seed)
        if has_pine_sprig:
            pine_side = -1 if vine_side == 'right' else 1
            pine_x = bcx + pine_side * (plinth_w // 2 + 8)
            draw_wuling_pine(surf, pine_x, bot_rect.bottom,
                             22, palette, lean=pine_side * 3, layers=4)

    if top_rect.height > 50:
        _draw_plinth_mist(surf, tcx, top_rect.y + 10,
                          int(top_rect.width * 2.0), palette)
        # Reserve the upper ~24 px for an INVERTED slender bronze finial —
        # the down-pillar's hat. Without it the hanger reads as a flat
        # plate; this gives Liaodi a recognisable crown when diving up.
        dark_pal = palette['stone_dark']
        crown_top = top_rect.y + 2
        crown_tip = crown_top + 16
        pygame.draw.line(surf, dark_pal, (tcx, crown_top + 2),
                         (tcx, crown_tip), 2)
        pygame.draw.line(surf, accent, (tcx + 1, crown_top + 2),
                         (tcx + 1, crown_tip), 1)
        for k in range(4):
            t = k / 3
            ry = crown_top + 3 + int(t * 11)
            rw = max(1, 3 - k // 2)
            pygame.draw.ellipse(surf, dark_pal,
                                (tcx - rw - 1, ry - 1, rw * 2 + 2, 3))
            pygame.draw.ellipse(surf, accent,
                                (tcx - rw, ry, rw * 2, 2))
        # Tiny pearl bud at the tip — the inverted Liaodi crown.
        pygame.draw.circle(surf, dark_pal, (tcx, crown_tip + 2), 2)
        pygame.draw.circle(surf, _shade(accent, 45),
                           (tcx, crown_tip + 2), 1)
        # Then the slim hanging body below the crown.
        anchor_h = 4
        anchor_y = crown_tip + 4
        anchor_w = int(top_rect.width * 1.12)
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -10),
                         (tcx - anchor_w // 2, anchor_y, anchor_w, anchor_h))
        pygame.draw.rect(surf, _column_grey(palette),
                         (tcx - anchor_w // 2 + 1, anchor_y + 1,
                          anchor_w - 2, anchor_h - 2))
        envelope_top = anchor_y + anchor_h
        envelope_bot = top_rect.bottom - 4
        hanger_tiers = 4
        total_hang = envelope_bot - envelope_top
        th_each = max(7, total_hang // hanger_tiers)
        for k in range(hanger_tiers):
            wall_top = envelope_top + k * th_each
            bw = max(10, int(top_rect.width * (0.97 ** k)))
            x_l = tcx - bw // 2
            body_rect = pygame.Rect(x_l, wall_top, bw, th_each - 2)
            _gradient_rect(surf, body_rect, white_lit, white, white_shadow)
            _eave_tang_inverted(surf, tcx, wall_top + th_each - 2,
                                bw // 2, max(6, 8 - k // 2), 2,
                                grey_tile, accent, tile_col, curl=0.30)


def candidate_liaodi(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('liaodi', _draw_liaodi, surf, top_rect, bot_rect,
                 palette, seed)


# ── Round 8 #9. Bulguksa Dabotap — Korean Stone Pagoda (Silla 751) ─────────
#
# Granite "Pagoda of Many Treasures": square base, 4 corner stair stones,
# octagonal upper section, stone railings, lotus-shaped balustrade capitals.
# Heavy stone ornament identity.
# Reference: https://en.wikipedia.org/wiki/Dabotap

def _draw_warm_cream_lotus(surf, cx, cy, w, h, palette):
    """8 short rounded triangular petals in warm-cream-on-stone around the
    spire base. Replaces the magenta lotus-pink palm-frond read the AD
    flagged. Drawn as a row of 8 small rounded triangles fanning ±π/2,
    flanking a central spire, sized to (w, h) but kept squat (h ≈ w/2)
    so the petals don't read as palm fronds."""
    cream = _mix(palette['stone_light'], (248, 232, 198), 0.78)
    cream_lit = _mix(palette['stone_light'], (252, 244, 220), 0.82)
    cream_shadow = _mix(palette['stone_mid'], (188, 168, 130), 0.66)
    n = 8
    r = max(2, min(w // 6, h - 1))
    for k in range(n):
        # Spread petals across the front half ±80° from straight up.
        t = (k + 0.5) / n
        ang = math.pi * (0.1 + 0.8 * t)
        ox = int(math.cos(ang) * (w // 2 - r))
        oy = -int(math.sin(ang) * (h // 2))
        px = cx + ox
        py = cy + oy
        # Petal tip slightly above the base point so the silhouette is
        # rounded-triangular, not circular.
        tip = (px, py - r)
        bl = (px - r, py + r // 2)
        br = (px + r, py + r // 2)
        pygame.draw.polygon(surf, cream_shadow, [tip, bl, br])
        pygame.draw.polygon(surf, cream,
                            [(tip[0], tip[1] + 1),
                             (bl[0] + 1, bl[1]),
                             (br[0] - 1, br[1])])
        # 1-px cream highlight on the lit side.
        pygame.draw.line(surf, cream_lit,
                         (tip[0] - 1, tip[1] + 1),
                         (bl[0] + 1, bl[1] - 1), 1)


def _draw_dabotap(surf, top_rect, bot_rect, palette, seed):
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2
    vine_side = rng.choice(('left', 'right'))
    entry_open = rng.choice((True, False))
    has_pine_sprig = rng.random() < 0.7
    shrub_jitter = rng.randint(-2, 2)

    granite = _korean_granite(palette)
    granite_lit = _korean_granite_lit(palette)
    granite_shadow = _korean_granite_shadow(palette)
    accent = _bronze(palette)

    if bot_rect.height > 80:
        _draw_plinth_mist(surf, bcx, bot_rect.bottom,
                          int(bot_rect.width * 2.4), palette)

        total_h = min(bot_rect.height, 230)
        # AD stripped to 3 sections — the round-8 7-section stack was too
        # busy for PIPE_W=58 and read as one-eyed-pyramid at night. Now:
        # 1) wide square BASE 2) octagonal DRUM 3) lotus capital + spire.
        # No cornice ledges, no corner stairs, no balustrades — they were
        # invisible at scale and added noise.
        base_h = int(total_h * 0.34)
        drum_h = int(total_h * 0.34)
        cap_h = int(total_h * 0.18)
        finial_h = total_h - base_h - drum_h - cap_h

        envelope_bot = bot_rect.bottom

        # 1) Wide square BASE — granite block with a small entry door at
        # the SIDE (not centred) so it doesn't read as eyes on the dive-
        # down pillar. Single niche placed off-axis low.
        base_w = int(bot_rect.width * 1.20)
        base_top = envelope_bot - base_h
        base_rect = pygame.Rect(bcx - base_w // 2, base_top, base_w, base_h)
        _gradient_rect(surf, base_rect, granite_lit, granite, granite_shadow)
        pygame.draw.rect(surf, granite_shadow, base_rect, 1)
        # Heavy seam at the base top — reads as the cap stone.
        pygame.draw.rect(surf, granite_shadow,
                         (base_rect.x, base_top, base_w, 2))
        pygame.draw.line(surf, granite_lit,
                         (base_rect.x + 1, base_top + 2),
                         (base_rect.right - 2, base_top + 2), 1)
        # Off-axis door slit — placed left-of-centre so the dive-down
        # pillar can't read as a single eye. Window glow handles night.
        door_off = -base_w // 5
        if _is_dark_sky(palette) or _is_warming_sky(palette):
            _lit_niche(surf, bcx + door_off, base_top + base_h // 3,
                       min(4, base_w // 8), min(6, base_h - 8), palette)
        else:
            pygame.draw.rect(surf, granite_shadow,
                             (bcx + door_off - 2, base_top + base_h // 3,
                              4, min(6, base_h - 8)))
        _draw_entry_door(surf, bcx, envelope_bot - 1, palette,
                         w=2, h=5, open_glow=entry_open)

        # 2) Octagonal DRUM — the middle section. Tall slim granite drum
        # with vertical octagonal seam lines so it reads as a faceted
        # stone, not a single column.
        drum_top = base_top - drum_h
        drum_w = int(base_w * 0.58)
        drum_rect = pygame.Rect(bcx - drum_w // 2, drum_top, drum_w, drum_h)
        _gradient_rect(surf, drum_rect, granite_lit, granite, granite_shadow)
        # Octagonal seams — 3 vertical lines per face split.
        for sign in (-1, 1):
            for frac in (0.18, 0.42):
                px = bcx + sign * int(drum_w * frac)
                pygame.draw.line(surf, granite_shadow,
                                 (px, drum_top + 1),
                                 (px, drum_top + drum_h - 2), 1)
        pygame.draw.line(surf, granite_lit,
                         (bcx - drum_w // 2 + 1, drum_top),
                         (bcx + drum_w // 2 - 1, drum_top), 1)
        # Cap-stone band at the top of the drum so the lotus has somewhere
        # to sit visually.
        cap_band_y = drum_top + 2
        pygame.draw.rect(surf, granite_shadow,
                         (bcx - drum_w // 2 - 2, cap_band_y, drum_w + 4, 2))

        # 3) LOTUS capital + spire — warm-cream-on-stone petals (NOT
        # magenta), 8 short rounded triangles. Then a slim bronze finial.
        cap_y = drum_top - cap_h
        _draw_warm_cream_lotus(surf, bcx, drum_top + 1, drum_w + 8,
                               cap_h * 2, palette)
        # Slim granite finial pole with bronze cap.
        f_top = cap_y + 1
        f_bot = f_top + finial_h - 2
        if finial_h > 4:
            pygame.draw.rect(surf, granite_shadow,
                             (bcx - 2, f_top, 4, finial_h - 2))
            pygame.draw.line(surf, granite_lit,
                             (bcx - 1, f_top), (bcx - 1, f_bot - 1), 1)
            pygame.draw.circle(surf, palette['stone_dark'], (bcx, f_top), 3)
            pygame.draw.circle(surf, accent, (bcx, f_top), 2)
            pygame.draw.circle(surf, _shade(accent, 45),
                               (bcx - 1, f_top - 1), 1)
            _draw_sorin_flame_halo(surf, bcx, f_top, palette)

        body_half = base_w // 2
        vine_x = bcx - body_half + 1 if vine_side == 'left' else bcx + body_half - 1
        _draw_vine_chunks(surf, vine_x, base_top - 50, base_top - 2,
                          palette, seed=seed)
        draw_side_shrub(surf, bcx - base_w // 2 - 2 + shrub_jitter,
                        bot_rect.bottom - 2, palette, scale=0.9)
        draw_side_shrub(surf, bcx + base_w // 2 + 2 - shrub_jitter,
                        bot_rect.bottom - 2, palette, scale=0.9)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 10, 16, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 7, seed=seed)
        if has_pine_sprig:
            pine_side = -1 if vine_side == 'right' else 1
            pine_x = bcx + pine_side * (base_w // 2 + 8)
            draw_wuling_pine(surf, pine_x, bot_rect.bottom,
                             22, palette, lean=pine_side * 3, layers=4)

    if top_rect.height > 50:
        _draw_plinth_mist(surf, tcx, top_rect.y + 10,
                          int(top_rect.width * 2.0), palette)
        # Reserve the upper ~28 px for the SIGNATURE silhouette — an
        # inverted lotus capital + slim drum so the dive-up read says
        # Dabotap (Korean stone, lotus crown), not "grey block + door".
        # The lotus + drum hang DIRECTLY below the ceiling anchor.
        anchor_h = 4
        anchor_w = int(top_rect.width * 1.10)
        pygame.draw.rect(surf, granite_shadow,
                         (tcx - anchor_w // 2, top_rect.y, anchor_w, anchor_h))
        pygame.draw.rect(surf, granite,
                         (tcx - anchor_w // 2 + 1, top_rect.y + 1,
                          anchor_w - 2, anchor_h - 2))
        # Inverted lotus crown — warm cream petals pointing DOWN.
        lotus_cy = top_rect.y + anchor_h + 4
        cream = _mix(palette['stone_light'], (248, 232, 198), 0.78)
        cream_lit = _mix(palette['stone_light'], (252, 244, 220), 0.82)
        cream_shadow = _mix(palette['stone_mid'], (188, 168, 130), 0.66)
        for k in range(7):
            t = (k + 0.5) / 7
            ang = math.pi * (0.15 + 0.7 * t)
            r = 3
            ox = int(math.cos(ang) * 10)
            oy = int(math.sin(ang) * 7)
            tip = (tcx + ox, lotus_cy + oy)
            tl = (tcx + ox - r, lotus_cy + oy - r // 2)
            tr = (tcx + ox + r, lotus_cy + oy - r // 2)
            pygame.draw.polygon(surf, cream_shadow, [tip, tl, tr])
            pygame.draw.polygon(surf, cream,
                                [(tip[0], tip[1] - 1),
                                 (tl[0] + 1, tl[1]),
                                 (tr[0] - 1, tr[1])])
            pygame.draw.line(surf, cream_lit,
                             (tl[0] + 1, tl[1] - 1),
                             (tr[0] - 1, tr[1] - 1), 1)
        # Then the drum below the inverted lotus.
        drum_top = lotus_cy + 10
        drum_w = int(top_rect.width * 0.42)
        drum_h = min(top_rect.bottom - drum_top - 4, 26)
        if drum_h > 8:
            drum_rect = pygame.Rect(tcx - drum_w // 2, drum_top,
                                    drum_w, drum_h)
            _gradient_rect(surf, drum_rect, granite_lit, granite,
                           granite_shadow)
            # Octagonal seams on the hanging drum.
            for sign in (-1, 1):
                px = tcx + sign * int(drum_w * 0.3)
                pygame.draw.line(surf, granite_shadow,
                                 (px, drum_top + 1),
                                 (px, drum_top + drum_h - 2), 1)


def candidate_dabotap(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('dabotap', _draw_dabotap, surf, top_rect, bot_rect,
                 palette, seed)


# ── Round 8 #10. Kumbum — Gyantse Stupa-Mandala (Tibet 1427) ───────────────
#
# Multi-tiered stepped stupa-temple, whitewashed body with red + ochre
# painted ranges, square stepped base, harmika cube with painted Buddha
# eyes at the crown, gold spire. Fortress-stupa.
# Reference: https://en.wikipedia.org/wiki/Kumbum

def _draw_kumbum(surf, top_rect, bot_rect, palette, seed):
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2
    vine_side = rng.choice(('left', 'right'))
    entry_open = rng.choice((True, False))
    has_pine_sprig = rng.random() < 0.6
    shrub_jitter = rng.randint(-2, 2)

    white = _tibet_white(palette)
    white_lit = _shade(white, 22)
    white_shadow = _shade(white, -28)
    red = _tibet_red(palette)
    red_lit = _shade(red, 22)
    ochre = _tibet_ochre(palette)
    gold = _gold_bright(palette)
    gold_d = _gold_deep(palette)
    dark = palette['stone_dark']

    if bot_rect.height > 80:
        _draw_plinth_mist(surf, bcx, bot_rect.bottom,
                          int(bot_rect.width * 2.4), palette)

        total_h = min(bot_rect.height, 245)
        # Budget: 38% 4-tier square stepped base, 18% cylindrical bumpa
        # vase, 10% harmika cube with eyes, 18% 13-ring spire, 16% canopy.
        base_h = int(total_h * 0.38)
        bumpa_h = int(total_h * 0.18)
        harm_h = int(total_h * 0.10)
        spire_h = int(total_h * 0.18)
        canopy_h = total_h - base_h - bumpa_h - harm_h - spire_h

        envelope_bot = bot_rect.bottom

        # 4-tier stepped base — Tibetan fortress-mandala. Each tier wider
        # at the bottom, painted with alternating red/ochre bands at top.
        n_tiers = 4
        step_h = base_h // n_tiers
        widest = int(bot_rect.width * 1.30)
        narrowest = int(bot_rect.width * 0.92)
        for i in range(n_tiers):
            t = i / max(1, n_tiers - 1)
            sw = int(widest + (narrowest - widest) * t)
            sy = envelope_bot - base_h + i * step_h
            srect = pygame.Rect(bcx - sw // 2, sy, sw, step_h)
            _gradient_rect(surf, srect, white_lit, white, white_shadow,
                           vertical=True)
            pygame.draw.rect(surf, white_shadow, srect, 1)
            # Painted red trim band along the top of every tier.
            pygame.draw.rect(surf, red,
                             (srect.x + 1, srect.y + 1, srect.w - 2, 2))
            pygame.draw.rect(surf, red_lit,
                             (srect.x + 1, srect.y + 1, srect.w - 2, 1))
            # Painted ochre fine line UNDER the red band.
            pygame.draw.rect(surf, ochre,
                             (srect.x + 1, srect.y + 3, srect.w - 2, 1))
            # Per-tier niche row — chapels are the Kumbum signature.
            n_chapels = max(2, sw // 16)
            for k in range(n_chapels):
                t_pos = (k + 0.5) / n_chapels
                nx = bcx - sw // 2 + int(t_pos * sw)
                _lit_niche(surf, nx, sy + 5,
                           min(4, sw // (n_chapels * 2)),
                           min(step_h - 8, 4), palette)
            # Entry door at the centre of the widest tier.
            if i == 0 and sw >= 30 and step_h >= 8:
                _draw_entry_door(surf, bcx, sy + step_h - 1, palette,
                                 w=2, h=5, open_glow=entry_open)
            # AA bottom edge.
            pygame.draw.line(surf, white_shadow,
                             (srect.x, srect.bottom - 1),
                             (srect.right - 1, srect.bottom - 1), 1)

        # Cylindrical bumpa (vase) section — round white drum with red trim.
        bumpa_base_y = envelope_bot - base_h
        bumpa_top_y = bumpa_base_y - bumpa_h
        bumpa_w = int(narrowest * 0.78)
        bumpa_rect = pygame.Rect(bcx - bumpa_w // 2, bumpa_top_y,
                                 bumpa_w, bumpa_h)
        pygame.draw.ellipse(surf, white_shadow, bumpa_rect)
        pygame.draw.ellipse(surf, white,
                            bumpa_rect.inflate(-2, -2))
        # Flatten top + bottom edges.
        pygame.draw.rect(surf, white,
                         (bcx - bumpa_w // 2 + 1, bumpa_top_y + 2,
                          bumpa_w - 2, bumpa_h - 4))
        pygame.draw.rect(surf, white_lit,
                         (bcx - bumpa_w // 2 + 2, bumpa_top_y + 3,
                          bumpa_w - 4, 1))
        # Red painted band around the widest waist.
        waist_y = bumpa_top_y + bumpa_h // 2
        pygame.draw.rect(surf, red,
                         (bcx - bumpa_w // 2 + 2, waist_y, bumpa_w - 4, 3))
        pygame.draw.line(surf, ochre,
                         (bcx - bumpa_w // 2 + 2, waist_y + 1),
                         (bcx + bumpa_w // 2 - 3, waist_y + 1), 1)
        # 4 chapel niches across the bumpa face (Kumbum's 4 large chapels).
        for off in (-bumpa_w // 4, bumpa_w // 4):
            _lit_niche(surf, bcx + off, bumpa_top_y + 3,
                       3, min(bumpa_h - 8, 5), palette)
        # AA upper arc.
        arc_pts = []
        for k in range(13):
            t = k / 12
            ang = math.pi + t * math.pi
            px = bcx + math.cos(ang) * bumpa_w * 0.5
            py = bumpa_top_y + bumpa_h // 2 - math.sin(ang) * bumpa_h * 0.4
            if py <= bumpa_top_y + bumpa_h // 2:
                arc_pts.append((int(px), int(py)))
        if len(arc_pts) >= 2:
            _aa_polyline(surf, white_shadow, arc_pts)

        # Harmika cube — square cube above bumpa with Buddha eyes.
        harm_w = int(bumpa_w * 0.72)
        harm_top_y = bumpa_top_y - harm_h
        harm_rect = pygame.Rect(bcx - harm_w // 2, harm_top_y, harm_w, harm_h)
        _gradient_rect(surf, harm_rect, white_lit, white, white_shadow)
        pygame.draw.rect(surf, white_shadow, harm_rect, 1)
        # Painted eyes — Kumbum's signature beat.
        eye_y = harm_top_y + harm_h // 2
        if harm_w >= 18:
            _draw_tibetan_eyes(surf, bcx, eye_y, palette, scale=0.9)
        # Ochre band at the top + red band at the bottom of the cube.
        pygame.draw.rect(surf, ochre,
                         (harm_rect.x + 1, harm_top_y + 1,
                          harm_rect.w - 2, 1))
        pygame.draw.rect(surf, red,
                         (harm_rect.x + 1, harm_rect.bottom - 2,
                          harm_rect.w - 2, 1))

        # 13-ring gold spire — Buddhist 13 levels of enlightenment.
        spire_base_y = harm_top_y
        spire_top_y = spire_base_y - spire_h
        rings = 13
        for k in range(rings):
            t = k / max(1, rings - 1)
            ry = spire_base_y - int(t * spire_h)
            rw = max(2, 7 - k // 2)
            pygame.draw.line(surf, dark,
                             (bcx - rw, ry + 1), (bcx + rw, ry + 1), 1)
            pygame.draw.line(surf, gold,
                             (bcx - rw, ry), (bcx + rw, ry), 1)
            # Specular gloss on every 3rd ring.
            if k % 3 == 0:
                pygame.draw.line(surf, _shade(gold, 60),
                                 (bcx - rw + 1, ry), (bcx - rw + 2, ry), 1)

        # Filigreed parasol canopy + finial.
        canopy_y = spire_top_y - canopy_h
        # Parasol disc.
        pygame.draw.ellipse(surf, dark,
                            (bcx - 10, canopy_y - 2, 20, 7))
        pygame.draw.ellipse(surf, gold,
                            (bcx - 9, canopy_y - 1, 18, 5))
        pygame.draw.ellipse(surf, gold_d,
                            (bcx - 8, canopy_y, 16, 3))
        # Hanging tassels around the parasol.
        for k in (-7, -4, 0, 4, 7):
            pygame.draw.line(surf, gold,
                             (bcx + k, canopy_y + 3), (bcx + k, canopy_y + 6), 1)
            pygame.draw.circle(surf, gold, (bcx + k, canopy_y + 7), 1)
        # Sun-moon-flame on top of the parasol.
        moon_y = canopy_y - 4
        pygame.draw.circle(surf, dark, (bcx, moon_y), 3)
        pygame.draw.circle(surf, gold, (bcx, moon_y), 2)
        # Sun above moon.
        sun_y = moon_y - 4
        pygame.draw.circle(surf, dark, (bcx, sun_y), 2)
        pygame.draw.circle(surf, _shade(gold, 60), (bcx, sun_y), 1)
        # Tiny flame on top.
        pygame.draw.polygon(surf, _shade(gold, 60),
                            [(bcx, sun_y - 5),
                             (bcx - 1, sun_y - 2),
                             (bcx + 1, sun_y - 2)])
        _draw_sorin_flame_halo(surf, bcx, sun_y, palette)

        body_half = widest // 2
        vine_x = bcx - body_half + 1 if vine_side == 'left' else bcx + body_half - 1
        _draw_vine_chunks(surf, vine_x, envelope_bot - base_h + 10,
                          envelope_bot - 4, palette, seed=seed)
        draw_side_shrub(surf, bcx - widest // 2 - 2 + shrub_jitter,
                        bot_rect.bottom - 2, palette, scale=0.9)
        draw_side_shrub(surf, bcx + widest // 2 + 2 - shrub_jitter,
                        bot_rect.bottom - 2, palette, scale=0.9)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 10, 16, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 7, seed=seed)
        if has_pine_sprig:
            pine_side = -1 if vine_side == 'right' else 1
            pine_x = bcx + pine_side * (widest // 2 + 8)
            draw_wuling_pine(surf, pine_x, bot_rect.bottom,
                             22, palette, lean=pine_side * 3, layers=4)

    if top_rect.height > 50:
        _draw_plinth_mist(surf, tcx, top_rect.y + 10,
                          int(top_rect.width * 2.0), palette)
        # Prayer-flag canopy — Tibetan signature. Strung between two stone
        # anchor blocks down from the ceiling.
        anchor_h = 6
        anchor_w = int(top_rect.width * 1.18)
        pygame.draw.rect(surf, dark,
                         (tcx - anchor_w // 2, top_rect.y, anchor_w, anchor_h))
        pygame.draw.rect(surf, _column_grey(palette),
                         (tcx - anchor_w // 2 + 1, top_rect.y + 1,
                          anchor_w - 2, anchor_h - 2))
        # Prayer flags strung between two anchor blocks. We render them
        # manually so the flag-colour rotation can offset by seed —
        # without this, adjacent Kumbums show pixel-identical bunting.
        flag_colors = [(60, 70, 200), (240, 240, 240), (220, 40, 35),
                       (60, 160, 80), (240, 200, 70)]
        col_off = seed % 5
        x_l = tcx - anchor_w // 2 + 4
        x_r = tcx + anchor_w // 2 - 4
        y_anchor = top_rect.y + anchor_h
        mx, my = (x_l + x_r) // 2, y_anchor + 14
        n_flags = 7
        steps = 30
        pts = []
        for i in range(steps + 1):
            t = i / steps
            bx = (1 - t) ** 2 * x_l + 2 * (1 - t) * t * mx + t * t * x_r
            by = (1 - t) ** 2 * y_anchor + 2 * (1 - t) * t * my + t * t * y_anchor
            pts.append((int(bx), int(by)))
        for i in range(len(pts) - 1):
            pygame.draw.line(surf, _shade(dark, 25), pts[i], pts[i + 1], 1)
        for i in range(n_flags):
            px, py = pts[int((i + 0.5) / n_flags * steps)]
            col = flag_colors[(i + col_off) % 5]
            pygame.draw.rect(surf, col, (px - 3, py, 6, 8))
            pygame.draw.rect(surf, _shade(dark, -10), (px - 3, py, 6, 8), 1)
        # Hanging mini-Kumbum spire below the flags — small white drum +
        # red painted band + small harmika eyes.
        drum_top = top_rect.y + anchor_h + 24
        drum_w = int(top_rect.width * 0.6)
        drum_h = min(top_rect.bottom - drum_top - 16, 22)
        if drum_h > 6:
            drum_rect = pygame.Rect(tcx - drum_w // 2, drum_top,
                                    drum_w, drum_h)
            _gradient_rect(surf, drum_rect, white_lit, white, white_shadow,
                           vertical=True)
            pygame.draw.rect(surf, red,
                             (drum_rect.x + 1, drum_top + drum_h // 2,
                              drum_rect.w - 2, 2))
            pygame.draw.rect(surf, ochre,
                             (drum_rect.x + 1, drum_top + drum_h // 2 + 2,
                              drum_rect.w - 2, 1))
            # Tiny harmika eyes if wide enough.
            if drum_w >= 22:
                _draw_tibetan_eyes(surf, tcx, drum_top + 4, palette, scale=0.7)
            # 13-ring gold spire dangles below — extended 6 px taller so
            # the hanger crown reads as Kumbum, not stub. 7 rings spread
            # the full extra length without collapsing into a clump.
            sp_top = drum_top + drum_h
            sp_bot = min(top_rect.bottom - 2, sp_top + 18)
            pygame.draw.line(surf, dark, (tcx, sp_top), (tcx, sp_bot), 2)
            pygame.draw.line(surf, gold, (tcx + 1, sp_top),
                             (tcx + 1, sp_bot), 1)
            for k in range(7):
                t = k / 6
                ry = sp_top + int(t * (sp_bot - sp_top - 2))
                rw = max(1, 4 - k // 2)
                pygame.draw.line(surf, gold,
                                 (tcx - rw, ry), (tcx + rw, ry), 1)
            # Tiny finial bud at the tip.
            pygame.draw.circle(surf, dark, (tcx, sp_bot + 1), 2)
            pygame.draw.circle(surf, _shade(gold, 45), (tcx, sp_bot + 1), 1)


def candidate_kumbum(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('kumbum', _draw_kumbum, surf, top_rect, bot_rect,
                 palette, seed)


# ── Registry ────────────────────────────────────────────────────────────────
#
# Round 8 — user pointed at Hōryū-ji + Fogong as the round-7 leads and asked
# for 10 NEW East-Asian-iconic candidates inspired by them. Baselines bookend
# the new set so the side-by-side comparison stays honest.

CANDIDATES = {
    "horyuji":   candidate_horyuji,
    "toji":      candidate_toji,
    "daigoji":   candidate_daigoji,
    "yakushiji": candidate_yakushiji,
    "sensoji":   candidate_sensoji,
    "tahoto":    candidate_tahoto,
    "liuhe":     candidate_liuhe,
    "baoen":     candidate_baoen,
    "liaodi":    candidate_liaodi,
    "dabotap":   candidate_dabotap,
    "kumbum":    candidate_kumbum,
    "fogong":    candidate_fogong,
}

CANDIDATE_BLURBS = {
    "horyuji":   "Hōryū-ji Tō — cedar columns + plaster panels, bronze sōrin (KEEPER)",
    "toji":      "Tō-ji — monumental dark cypress + thick deep eaves (Kyoto 1644)",
    "daigoji":   "Daigo-ji — vermilion lacquer + plaster + 1/3-tower gold sōrin (951)",
    "yakushiji": "Yakushi-ji — 3-storey + mokoshi skirt roofs → 6-roof silhouette (730)",
    "sensoji":   "Sensō-ji — vermilion 5-storey + giant red Kaminarimon lantern (Tokyo)",
    "tahoto":    "Tahōtō — round white-plaster kamebara body, square base + cap (1194)",
    "liuhe":     "Liuhe — 13-storey brick + dense wooden eaves + iron bells (Hangzhou 1165)",
    "baoen":     "Bao'en — 9-storey porcelain tower + painted floral panels (Nanjing Ming)",
    "liaodi":    "Liaodi — slim 11-storey whitewashed brick, severe minimalism (Dingzhou 1055)",
    "dabotap":   "Dabotap — Silla granite many-treasures pagoda + lotus capitals (Bulguksa 751)",
    "kumbum":    "Kumbum — Tibetan stupa-mandala + Buddha eyes + 13-ring gold spire (Gyantse 1427)",
    "fogong":    "Fogong — octagonal larch + dougong brackets + grey-tile curls (KEEPER)",
}
