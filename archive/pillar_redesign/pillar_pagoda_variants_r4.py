"""Pagoda-pillar candidates for the obstacle-pillar redesign round.

Five distinct architectural takes on the same `draw_pillar_pair` API the live
game uses (game/pillar_variants.py:817), so each candidate can be diffed
straight into that dispatcher once the user picks a winner. Every renderer is
`candidate_<name>(surf, top_rect, bot_rect, palette, seed)` — same signature,
same per-pipe stable seed contract.

Reading strategy per candidate:

  candidate_tang_gateway       — Chinese tower below, carved awning + banner
                                 web above; reads as a temple gateway.
  candidate_mirrored_split     — ONE pagoda silhouette cleaved by the gap:
                                 lower tiers + base below, upper tiers +
                                 downward finial above.
  candidate_facing_pair        — Twin Japanese tō; both finials point at the
                                 gap, bookending the corridor.
  candidate_japanese_pavilion  — 5-storey tō below, hanging cloud shrine on
                                 chains above with an up-curled eave + lit
                                 lantern glow.
  candidate_stupa_canopy       — Tibetan chorten below (stepped base, bell
                                 dome, harmika, 13-step spire, sun-moon-flame),
                                 sagging prayer-flag canopy above.

Each seed selects a deliberate "spawn flavor" so 5 spawns of the SAME candidate
read as 5 distinct temples and not five clones:
  flavor 0 — plain
  flavor 1 — lantern-strung
  flavor 2 — banner-draped
  flavor 3 — pine-crowned
  flavor 4 — cairn-flanked

Heavy reuse of the existing foliage/ornament helpers from game.pillar_variants
and game.draw keeps the temples wearing the same moss, prayer-flags and pines
as the rest of the world.
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
    draw_climbing_vine,
    draw_grass_bed,
    draw_flower_bed,
    draw_ground_ferns,
    draw_prayer_flags,
    draw_cairn,
    draw_paper_lantern,
    draw_bird_sil,
)


# ── Colour helpers ──────────────────────────────────────────────────────────
#
# Roofs only read as "pagoda" if they pop against the wall, but every shade
# is mixed against the live palette so dusk/night retints carry through. No
# raw RGBs hit the pillar — anchors come from stone_dark / stone_mid /
# stone_light / stone_accent and we blend toward an archetype hue.

def _mix(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def _shade(c, d):
    return (max(0, min(255, c[0] + d)),
            max(0, min(255, c[1] + d)),
            max(0, min(255, c[2] + d)))


def _cinnabar(palette):
    # Deeper cinnabar — pulled toward stone_dark so the roof keeps a high-
    # contrast silhouette against the warm sunset gradient and stays readable
    # at night without going washed-out at day.
    return _mix(palette['stone_dark'], (175, 45, 35), 0.58)


def _terracotta(palette):
    # Deepened toward stone_dark — earlier mid-based mix lost separation
    # against warm sky gradients.
    return _mix(palette['stone_dark'], (155, 75, 45), 0.60)


def _cedar(palette):
    # Warm wooden roof for Japanese tō — deeper / browner than cinnabar.
    return _mix(palette['stone_dark'], (115, 75, 50), 0.72)


def _chorten_white(palette):
    # Whitewashed chorten body — biased toward stone_light so dusk/night
    # still leans warm/cool with the rest of the scene.
    return _mix(palette['stone_light'], (245, 240, 232), 0.55)


def _gilt(palette):
    return _mix(palette['stone_accent'], (235, 195, 90), 0.65)


# ── Eave primitive ──────────────────────────────────────────────────────────
#
# The single iconic silhouette cue for a pagoda is the up-curled eave that
# overhangs the wall below. We draw it as a polygon with anchor points along
# a quadratic curve so the corners RISE above the body and the centre dips
# slightly. The overhang is `overhang` px past `half_w_body` on each side —
# without that overhang the tier reads as a brick block, not a roof.

def _eave_curve(cx, y_base, half_w_body, overhang, depth, curl):
    """Anchor points for the top edge of an up-curled eave roof.

    `half_w_body` is the wall half-width (the tier the eave sits on).
    Tips of the eave land at half_w_body + overhang on each side.
    `depth` is roof thickness; `curl` (0..1.4) scales how high the tips rise.
    """
    tip_rise = max(2, int(depth * (0.5 + curl)))
    centre_sag = max(1, depth // 3)
    half_outer = half_w_body + overhang
    # Top edge from left tip → eaves dip → centre ridge → eaves rise → right tip.
    # Multi-anchor so the silhouette reads curved at game scale (no native AA).
    return [
        (cx - half_outer,     y_base + depth - 1),         # left tip outer-bottom
        (cx - half_outer,     y_base - tip_rise),          # left tip upper
        (cx - half_outer + 3, y_base - tip_rise + 1),      # upper rim left
        (cx - half_w_body,    y_base - centre_sag // 2),   # ridge dip left
        (cx,                  y_base + 1 - centre_sag),    # ridge centre (slight sag)
        (cx + half_w_body,    y_base - centre_sag // 2),   # ridge dip right
        (cx + half_outer - 3, y_base - tip_rise + 1),      # upper rim right
        (cx + half_outer,     y_base - tip_rise),          # right tip upper
        (cx + half_outer,     y_base + depth - 1),         # right tip outer-bottom
    ]


def _eave(surf, cx, y_base, half_w_body, overhang, depth, roof_col,
          accent_col, curl=0.7):
    """A single up-curled eave row centred on cx, sitting on top of a wall
    that is `half_w_body * 2` wide. The eave sticks OUT past the wall by
    `overhang` px on each side — that overhang is what makes the player read
    pagoda."""
    # Wider overhang so the silhouette cue survives the 58 px PIPE_W.
    overhang = max(overhang, 7)
    pts = _eave_curve(cx, y_base, half_w_body, overhang, depth, curl)
    # Dark backing — full silhouette in shadow tone.
    pygame.draw.polygon(surf, _shade(roof_col, -55), pts)
    # Main roof body inset by one px on the bottom for a subtle eave shadow.
    body_pts = [(p[0], p[1] - 1) if p[1] >= y_base else p for p in pts]
    pygame.draw.polygon(surf, roof_col, body_pts)
    # Hard keyline under the eave so tier separation reads against any sky —
    # this is the cue that survives bright sunset gradients where the roof
    # colour itself would otherwise blend with the warm background.
    keyline = _shade(roof_col, -75)
    half_outer = half_w_body + overhang
    pygame.draw.line(surf, keyline,
                     (cx - half_outer + 1, y_base + depth - 1),
                     (cx + half_outer - 1, y_base + depth - 1), 1)
    # Gold accent strip just under the ridge.
    pygame.draw.line(surf, accent_col,
                     (cx - half_w_body + 1, y_base - 1),
                     (cx + half_w_body - 1, y_base - 1), 1)
    # Two-pixel highlight at the eave tips so the up-curl pops in silhouette
    # even when aalines would alias at this scale.
    tip_rise = max(2, int(depth * (0.5 + curl)))
    highlight = _shade(roof_col, 25)
    pygame.draw.line(surf, highlight,
                     (cx - half_outer, y_base - tip_rise),
                     (cx - half_outer + 2, y_base - tip_rise + 1), 1)
    pygame.draw.line(surf, highlight,
                     (cx + half_outer, y_base - tip_rise),
                     (cx + half_outer - 2, y_base - tip_rise + 1), 1)


def _eave_inverted(surf, cx, y_base, half_w_body, overhang, depth, roof_col,
                   accent_col, curl=0.7):
    """An eave whose tips curl DOWN — used as the underside seen on a hanging
    awning/shrine. Same silhouette logic as `_eave`, mirrored vertically."""
    overhang = max(overhang, 7)
    # Mirror the curve points around y_base.
    pts = _eave_curve(cx, y_base, half_w_body, overhang, depth, curl)
    mirrored = [(p[0], 2 * y_base - p[1]) for p in pts]
    pygame.draw.polygon(surf, _shade(roof_col, -55), mirrored)
    body = [(p[0], p[1] + 1) for p in mirrored]
    pygame.draw.polygon(surf, roof_col, body)
    # Hard keyline along the UPPER edge so the awning underside reads cleanly
    # against the gap sky behind it.
    keyline = _shade(roof_col, -75)
    half_outer = half_w_body + overhang
    pygame.draw.line(surf, keyline,
                     (cx - half_outer + 1, y_base - depth + 1),
                     (cx + half_outer - 1, y_base - depth + 1), 1)
    pygame.draw.line(surf, accent_col,
                     (cx - half_w_body + 1, y_base + 1),
                     (cx + half_w_body - 1, y_base + 1), 1)
    # Tip highlights for the downward curl.
    tip_drop = max(2, int(depth * (0.5 + curl)))
    highlight = _shade(roof_col, 25)
    pygame.draw.line(surf, highlight,
                     (cx - half_outer, y_base + tip_drop),
                     (cx - half_outer + 2, y_base + tip_drop - 1), 1)
    pygame.draw.line(surf, highlight,
                     (cx + half_outer, y_base + tip_drop),
                     (cx + half_outer - 2, y_base + tip_drop - 1), 1)


# ── Wall + window primitives ────────────────────────────────────────────────

def _wall_strip(surf, x, y, w, h, palette):
    """Plastered pagoda wall — light face + warm shadow stripe on right edge."""
    if h <= 0 or w <= 0:
        return
    light = _mix(palette['stone_light'], (250, 245, 230), 0.30)
    mid = palette['stone_mid']
    pygame.draw.rect(surf, mid, (x, y, w, h))
    pygame.draw.rect(surf, light, (x, y, max(1, w - 2), max(1, h - 1)))
    pygame.draw.rect(surf, _shade(mid, -25), (x + w - 2, y, 2, h))


def _timber_wall(surf, x, y, w, h, palette):
    """Wooden tō tier wall — only the two corner posts so the silhouette stays
    legible at the 58 px PIPE_W. A 4 px-spaced timber grid aliased into pixel
    noise at this scale; corner posts alone read as a wooden bay."""
    if h <= 0 or w <= 0:
        return
    _wall_strip(surf, x, y, w, h, palette)
    timber = _shade(palette['stone_dark'], -10)
    pygame.draw.line(surf, timber, (x + 2, y + 1), (x + 2, y + h - 2), 1)
    pygame.draw.line(surf, timber,
                     (x + w - 3, y + 1), (x + w - 3, y + h - 2), 1)
    # A single light beam mid-height adds horizontal rhythm without aliasing.
    if h > 12:
        beam_y = y + h // 2
        pygame.draw.line(surf, timber,
                         (x + 2, beam_y), (x + w - 3, beam_y), 1)


def _window_lattice(surf, cx, y, w, h, palette):
    """Red-trimmed lattice window."""
    if w < 6 or h < 5:
        return
    frame = _mix(palette['stone_dark'], (170, 60, 40), 0.55)
    inner = _mix(palette['stone_mid'], (255, 230, 160), 0.35)
    pygame.draw.rect(surf, frame, (cx - w // 2, y, w, h))
    pygame.draw.rect(surf, inner, (cx - w // 2 + 1, y + 1, w - 2, h - 2))
    pygame.draw.line(surf, frame, (cx, y + 1), (cx, y + h - 1), 1)
    pygame.draw.line(surf, frame,
                     (cx - w // 2 + 1, y + h // 2),
                     (cx + w // 2 - 1, y + h // 2), 1)


def _lit_window(surf, cx, y, w, h, palette):
    """A glowing window for a hanging shrine — warm yellow inside, dark frame."""
    if w < 6 or h < 5:
        return
    frame = _mix(palette['stone_dark'], (110, 50, 30), 0.55)
    glow = _mix(palette['stone_accent'], (255, 215, 130), 0.75)
    pygame.draw.rect(surf, frame, (cx - w // 2, y, w, h))
    pygame.draw.rect(surf, glow, (cx - w // 2 + 1, y + 1, w - 2, h - 2))
    # Cross mullion.
    pygame.draw.line(surf, frame, (cx, y + 1), (cx, y + h - 1), 1)
    pygame.draw.line(surf, frame,
                     (cx - w // 2 + 1, y + h // 2),
                     (cx + w // 2 - 1, y + h // 2), 1)
    # Bloom around the window.
    bloom_r = max(4, w)
    g = pygame.Surface((bloom_r * 2, bloom_r * 2), pygame.SRCALPHA)
    pygame.draw.circle(g, (255, 215, 140, 70), (bloom_r, bloom_r), bloom_r)
    pygame.draw.circle(g, (255, 235, 180, 110),
                       (bloom_r, bloom_r), max(2, bloom_r // 2))
    surf.blit(g, (cx - bloom_r, y + h // 2 - bloom_r))


def _doorway(surf, cx, base_y, w, h, palette):
    if h < 5 or w < 5:
        return
    frame = _mix(palette['stone_dark'], (170, 60, 40), 0.55)
    inside = _shade(palette['stone_dark'], -10)
    pygame.draw.rect(surf, frame, (cx - w // 2, base_y - h, w, h))
    pygame.draw.rect(surf, inside,
                     (cx - w // 2 + 1, base_y - h + 1, w - 2, h - 1))
    pygame.draw.arc(surf, _gilt(palette),
                    (cx - w // 2, base_y - h - 2, w, 5), 0, math.pi, 1)


# ── Finial primitives ───────────────────────────────────────────────────────
#
# Three distinct finial silhouettes, each large enough to read at game scale.
# Sōrin = stacked disks, Chinese = bulb + flame jewel, chorten = 13-step
# spire + sun-moon-flame stack.

def _finial_sorin(surf, cx, base_y, height, palette):
    """Japanese sōrin — needle with 7 disks stacked at decreasing diameter
    and a flame jewel on top. The disks are what makes the eye read 'pagoda'."""
    gold = _gilt(palette)
    dark = palette['stone_dark']
    bright = _shade(gold, 40)
    # Base lotus pad.
    pygame.draw.ellipse(surf, dark, (cx - 5, base_y - 4, 10, 6))
    pygame.draw.ellipse(surf, gold, (cx - 4, base_y - 3, 8, 4))
    # Central spire.
    pygame.draw.line(surf, dark, (cx, base_y - 2),
                     (cx, base_y - height + 4), 2)
    # 7 disks (kurin) tapering up the needle.
    disks = 7
    disk_top = base_y - height + 4
    span = base_y - 6 - disk_top
    for i in range(disks):
        ry = base_y - 6 - int(i * span / max(1, disks - 1))
        rw = max(2, 6 - i // 2)
        # Edge-aware disk so it doesn't read as a flat horizontal line.
        pygame.draw.ellipse(surf, dark, (cx - rw - 1, ry - 1, rw * 2 + 2, 3))
        pygame.draw.ellipse(surf, gold, (cx - rw, ry, rw * 2, 2))
    # Flame jewel.
    top_y = base_y - height
    pygame.draw.circle(surf, dark, (cx, top_y + 2), 3)
    pygame.draw.circle(surf, gold, (cx, top_y + 2), 2)
    pygame.draw.polygon(surf, bright,
                        [(cx, top_y - 4), (cx - 2, top_y + 1),
                         (cx + 2, top_y + 1)])


def _finial_chinese(surf, cx, base_y, height, palette):
    """Chinese tower finial — bulb + needle + flame jewel. More bulbous than
    sōrin so the two read distinct in the same scene."""
    gold = _gilt(palette)
    dark = palette['stone_dark']
    bright = _shade(gold, 40)
    # Bulb at the base.
    pygame.draw.ellipse(surf, dark, (cx - 5, base_y - 8, 10, 10))
    pygame.draw.ellipse(surf, gold, (cx - 4, base_y - 7, 8, 8))
    # Needle.
    pygame.draw.line(surf, dark, (cx, base_y - 7),
                     (cx, base_y - height + 4), 2)
    # Two small rings on the needle for vertical rhythm.
    for ry in (base_y - height + 10, base_y - height + 16):
        if ry < base_y - 8:
            pygame.draw.line(surf, gold, (cx - 3, ry), (cx + 3, ry), 1)
    # Flame jewel on top.
    top_y = base_y - height
    pygame.draw.circle(surf, dark, (cx, top_y + 3), 3)
    pygame.draw.circle(surf, gold, (cx, top_y + 3), 2)
    pygame.draw.polygon(surf, bright,
                        [(cx, top_y - 5), (cx - 2, top_y + 2),
                         (cx + 2, top_y + 2)])


def _finial_chorten(surf, cx, harmika_top_y, palette):
    """13-step chorten spire + sun-moon-flame jewel above the harmika.

    Returns the y of the topmost flame tip so the caller knows the silhouette
    extent. Spire steps taper linearly so the eye reads a triangle, not a stack
    of equal lines."""
    gold = _gilt(palette)
    dark = palette['stone_dark']
    bright = _shade(gold, 40)
    # Spire — 13 narrowing steps anchored to the harmika roof.
    steps = 13
    step_h = 2
    start_y = harmika_top_y - 1
    for i in range(steps):
        sy = start_y - i * step_h
        rw = max(1, 6 - (i * 5) // steps)
        pygame.draw.line(surf, dark, (cx - rw, sy + 1), (cx + rw, sy + 1), 1)
        pygame.draw.line(surf, gold, (cx - rw, sy), (cx + rw, sy), 1)
    spire_top = start_y - steps * step_h
    # Lotus pad.
    pygame.draw.ellipse(surf, dark, (cx - 4, spire_top - 2, 8, 4))
    pygame.draw.ellipse(surf, gold, (cx - 3, spire_top - 1, 6, 3))
    # Moon crescent.
    pygame.draw.circle(surf, gold, (cx, spire_top - 5), 3)
    pygame.draw.circle(surf, _mix(palette['stone_dark'],
                                  palette['stone_mid'], 0.5),
                       (cx + 1, spire_top - 5), 2)
    # Sun disc.
    pygame.draw.circle(surf, dark, (cx, spire_top - 9), 2)
    pygame.draw.circle(surf, gold, (cx, spire_top - 9), 1)
    # Flame jewel tip.
    tip_y = spire_top - 14
    pygame.draw.polygon(surf, bright,
                        [(cx, tip_y), (cx - 2, spire_top - 10),
                         (cx + 2, spire_top - 10)])
    return tip_y


# ── Per-seed spawn flavor ───────────────────────────────────────────────────
#
# Each seed deterministically selects one of five flavors so a row of five
# pillars reads as five distinct temples. The flavor controls which ornament
# the candidate decorates with — the candidate still owns where on the body
# the ornament lands.

FLAVORS = ('plain', 'lantern', 'banner', 'pine', 'cairn')


def _flavor_for(seed: int) -> str:
    return FLAVORS[seed % len(FLAVORS)]


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
    flavor = _flavor_for(seed)

    # Tier count chosen so smaller towers read as 3-tier and tall ones as 7.
    tier_count = rng.choice([3, 5, 7])

    # ── Bottom pagoda — tapering tier stack ────────────────────────────
    if bot_rect.height > 36:
        plinth_h = 10
        plinth_w = int(bot_rect.width * 1.10)
        # Plinth shadow + face highlight.
        pygame.draw.rect(surf, _shade(wall, -30),
                         (bcx - plinth_w // 2, bot_rect.bottom - plinth_h,
                          plinth_w, plinth_h))
        pygame.draw.rect(surf, palette['stone_light'],
                         (bcx - plinth_w // 2, bot_rect.bottom - plinth_h,
                          plinth_w, 2))

        # Carve the tier stack so lower tiers are TALL and upper tiers are
        # SHORT — the silhouette tightens toward the spire.
        finial_h = 26
        usable_h = bot_rect.height - plinth_h - finial_h
        # Each tier's share of the stack — weighted toward the base.
        weights = [1.0 - 0.10 * i for i in range(tier_count)]
        wsum = sum(weights)
        tier_heights = [max(10, int(usable_h * w / wsum)) for w in weights]

        # Body taper: each successive tier ~88% of the one below.
        base_body_w = int(bot_rect.width * 0.86)
        body_widths = []
        for i in range(tier_count):
            scale = 1.0 * (0.88 ** i)
            body_widths.append(max(10, int(base_body_w * scale)))

        # Stack from plinth-top upward.
        y_cursor = bot_rect.bottom - plinth_h
        tier_tops = []
        for i in range(tier_count):
            th = tier_heights[i]
            bw = body_widths[i]
            wall_top = y_cursor - th
            tier_tops.append((wall_top, bw, th))
            # Wall body (eave will sit on top of this rect).
            _wall_strip(surf, bcx - bw // 2, wall_top, bw, th, palette)
            # Decorate with a doorway on tier 0, lattice windows higher up.
            if i == 0 and th > 14 and bw > 16:
                _doorway(surf, bcx, y_cursor,
                         min(14, bw - 8), min(th - 4, 14), palette)
            elif th > 9 and bw > 14:
                _window_lattice(surf, bcx, wall_top + 3,
                                min(10, bw - 8), min(7, th - 6), palette)
            # Up-curled eave over this tier — overhang shrinks as we climb.
            overhang = max(6, 10 - i)
            depth = 4 if i < tier_count - 2 else 3
            _eave(surf, bcx, wall_top, bw // 2, overhang, depth,
                  roof, accent, curl=0.95)
            y_cursor = wall_top - depth + 1

        # Chinese flame-jewel finial on top of the highest tier.
        top_wall_y = tier_tops[-1][0]
        _finial_chinese(surf, bcx, top_wall_y - 2, finial_h, palette)

        # Per-seed ornament layered on top.
        if flavor == 'pine' and bot_rect.height > 110:
            draw_wuling_pine(surf, bcx + 12, top_wall_y + 2, 16,
                             palette, lean=6, layers=3)
        elif flavor == 'lantern':
            # Two lanterns dangling from the LOWEST eave corners.
            lo_top, lo_bw, lo_th = tier_tops[0]
            ly = lo_top
            draw_paper_lantern(surf, bcx - lo_bw // 2 - 4, ly, strand=8,
                               scale=0.7, color='red')
            draw_paper_lantern(surf, bcx + lo_bw // 2 + 4, ly, strand=8,
                               scale=0.7, color='red')
        elif flavor == 'cairn' and bot_rect.height > 70:
            draw_cairn(surf, bcx - plinth_w // 2 - 8,
                       bot_rect.bottom - 2, n=3, pennant=False)
        elif flavor == 'banner' and len(tier_tops) >= 2:
            # Vertical banner strip dangling from a mid-tier eave.
            mt_top, mt_bw, _ = tier_tops[len(tier_tops) // 2]
            bx = bcx - 2
            by = mt_top + 1
            pygame.draw.rect(surf, _shade(roof, -10), (bx, by, 4, 14))
            pygame.draw.rect(surf, accent, (bx, by, 4, 2))
            pygame.draw.rect(surf, _gilt(palette), (bx + 1, by + 5, 2, 2))

        # Persistent climbing vine on one side, plus base groundcover.
        if bot_rect.height > 90:
            side_x = bot_rect.x + (4 if seed % 2 else bot_rect.width - 6)
            draw_climbing_vine(surf, side_x, bot_rect.y + 24,
                               bot_rect.bottom - 14, palette, seed=seed)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 6, 14, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 8, seed=seed)

    # ── Top awning + banner web ─────────────────────────────────────────
    if top_rect.height > 22:
        # Visible corner pillars FROM the screen ceiling down to the awning —
        # the awning now reads as a roof supported by columns, not a floating
        # box. Pillars also brace the prayer-flag banner web.
        col_h = min(top_rect.height - 6, 56)
        col_w = 6
        col_top_y = top_rect.y
        col_bot_y = col_top_y + col_h
        col_xs = (top_rect.x + 3, top_rect.x + top_rect.width - 3 - col_w)
        for cx_l in col_xs:
            # Column shadow.
            pygame.draw.rect(surf, _shade(palette['stone_dark'], -10),
                             (cx_l, col_top_y, col_w, col_h))
            # Column light face.
            pygame.draw.rect(surf, palette['stone_light'],
                             (cx_l + 1, col_top_y, col_w - 2, col_h - 1))
            # Cinnabar capital + base bands so the columns feel architectural.
            pygame.draw.rect(surf, _shade(roof, -25),
                             (cx_l - 1, col_top_y, col_w + 2, 3))
            pygame.draw.rect(surf, roof,
                             (cx_l - 1, col_bot_y - 4, col_w + 2, 3))

        # Awning eave underside curls DOWN from the ceiling between the
        # columns, sized to the full top_rect.width so it looks like a roof
        # spanning the gateway rather than a small floating panel.
        eave_y0 = top_rect.bottom - 3
        _eave_inverted(surf, tcx, eave_y0,
                       top_rect.width // 2 + 6, 12, 7, roof, accent, curl=1.0)
        # Second eave higher up — also spanning the full width.
        awning_budget = min(top_rect.height - 4, 64)
        if awning_budget > 26:
            _eave_inverted(surf, tcx, eave_y0 - 18,
                           top_rect.width // 2 + 3, 9, 6, roof, accent,
                           curl=0.90)
        # Wall block bridging the awning up to the column capitals — sits
        # behind the columns so the columns still read as structural fronts.
        wall_top = max(col_top_y + 4, top_rect.bottom - awning_budget)
        wall_h = max(0, eave_y0 - 24 - wall_top)
        if wall_h > 6:
            _wall_strip(surf, tcx - top_rect.width // 2 + 10, wall_top,
                        top_rect.width - 20, wall_h, palette)
            if wall_h > 14:
                _window_lattice(surf, tcx, wall_top + 4,
                                min(14, top_rect.width - 22),
                                min(10, wall_h - 6), palette)

        # Banner web — prayer flags hanging from the awning corners DOWN to
        # the column bases, fully INSIDE the top rect (was crossing the gap
        # corridor and muddying the playable edge).
        for sx, ex in ((tcx - top_rect.width // 2 + 8, col_xs[0] + col_w // 2),
                       (tcx + top_rect.width // 2 - 8,
                        col_xs[1] + col_w // 2)):
            draw_prayer_flags(surf, sx, top_rect.bottom - 4,
                              ex, col_bot_y - 6, n=5)
        # Moss tipping the awning corners — pulled INSIDE top_rect.
        for off in (-22, -10, 10, 22):
            draw_moss_strand(surf, tcx + off, top_rect.bottom - 3,
                             6 + abs(off) % 5, palette,
                             jitter_seed=seed + off)
        # Per-seed ornament — flavor decides what hangs from the awning.
        if flavor == 'lantern':
            draw_paper_lantern(surf, tcx, top_rect.bottom - 4,
                               strand=14, scale=0.75, color='gold')
        elif flavor == 'banner':
            # Central vertical hanging banner from the awning underside.
            pygame.draw.rect(surf, _shade(roof, -30),
                             (tcx - 3, top_rect.bottom - 2, 6, 16))
            pygame.draw.rect(surf, accent,
                             (tcx - 3, top_rect.bottom - 2, 6, 3))
            pygame.draw.rect(surf, _gilt(palette),
                             (tcx - 1, top_rect.bottom + 5, 2, 2))
        elif flavor == 'pine':
            # Small pine clinging to a column base.
            draw_wuling_pine(surf, col_xs[0] - 4, col_bot_y - 2, 10,
                             palette, lean=-3, layers=2)
        elif flavor == 'cairn':
            # Small cairn on top of the column capital area.
            draw_cairn(surf, col_xs[1] + col_w + 3, col_bot_y - 2,
                       n=2, pennant=False)
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
    flavor = _flavor_for(seed)

    tier_count_bot = rng.choice([2, 3, 4])
    tier_count_top = rng.choice([2, 3, 4])

    # ── Bottom half — lower tiers + base ───────────────────────────────
    if bot_rect.height > 28:
        plinth_h = 12
        plinth_w = int(bot_rect.width * 1.12)
        pygame.draw.rect(surf, _shade(palette['stone_mid'], -30),
                         (bcx - plinth_w // 2, bot_rect.bottom - plinth_h,
                          plinth_w, plinth_h))
        pygame.draw.rect(surf, palette['stone_light'],
                         (bcx - plinth_w // 2, bot_rect.bottom - plinth_h,
                          plinth_w, 2))

        # Reverse-weighted heights so the lowest tier is the tallest.
        usable_h = bot_rect.height - plinth_h - 4
        weights = [1.0 - 0.12 * i for i in range(tier_count_bot)]
        wsum = sum(weights)
        tier_heights = [max(12, int(usable_h * w / wsum)) for w in weights]
        # Body taper.
        base_body_w = int(bot_rect.width * 0.95)
        body_widths = [max(14, int(base_body_w * (0.90 ** i)))
                       for i in range(tier_count_bot)]

        y_cursor = bot_rect.bottom - plinth_h
        tier_tops = []
        for i in range(tier_count_bot):
            th = tier_heights[i]
            bw = body_widths[i]
            wall_top = y_cursor - th
            tier_tops.append((wall_top, bw, th))
            _wall_strip(surf, bcx - bw // 2, wall_top, bw, th, palette)
            if i == 0 and th > 14:
                _doorway(surf, bcx, y_cursor,
                         min(16, bw - 6), min(14, th - 6), palette)
            elif th > 9 and bw > 14:
                _window_lattice(surf, bcx, wall_top + 3,
                                min(12, bw - 8), min(8, th - 8), palette)
            overhang = max(6, 9 - i)
            depth = 5
            _eave(surf, bcx, wall_top, bw // 2, overhang, depth,
                  roof, accent, curl=0.95)
            y_cursor = wall_top - depth + 1

        # Cap a short "ridge" at the cut so the silhouette reads architectural —
        # thicker than before so the gap-facing edge stays crisp against sky.
        cap_y = max(bot_rect.y, y_cursor - 4)
        pygame.draw.rect(surf, _shade(roof, -55),
                         (bcx - 16, cap_y, 32, 5))
        pygame.draw.rect(surf, roof, (bcx - 15, cap_y + 1, 30, 3))
        pygame.draw.rect(surf, accent, (bcx - 12, cap_y + 1, 24, 1))

        # Vegetation + per-seed flavour at base.
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 6, 14, palette, seed=seed)
        if flavor == 'lantern':
            draw_paper_lantern(surf, bcx - plinth_w // 2 - 4,
                               bot_rect.bottom - plinth_h + 1, strand=18,
                               scale=0.8, color='red')
            draw_paper_lantern(surf, bcx + plinth_w // 2 + 4,
                               bot_rect.bottom - plinth_h + 1, strand=18,
                               scale=0.8, color='red')
        elif flavor == 'cairn' and bot_rect.height > 80:
            draw_cairn(surf, bcx + plinth_w // 2 + 10,
                       bot_rect.bottom - 2, n=3, pennant=True)
        elif flavor == 'pine' and bot_rect.height > 110:
            draw_wuling_pine(surf, bot_rect.x + 4,
                             bot_rect.bottom - plinth_h, 20,
                             palette, lean=-6, layers=3)
        elif flavor == 'banner' and tier_tops:
            mt_top, mt_bw, _ = tier_tops[len(tier_tops) // 2]
            bx = bcx + mt_bw // 2 - 6
            pygame.draw.rect(surf, _shade(roof, -10), (bx, mt_top + 1, 4, 12))
            pygame.draw.rect(surf, accent, (bx, mt_top + 1, 4, 2))

    # ── Top half — upper tiers + downward finial ───────────────────────
    if top_rect.height > 26:
        finial_h = 16
        usable_h = top_rect.height - finial_h
        weights = [1.0 - 0.10 * i for i in range(tier_count_top)]
        wsum = sum(weights)
        tier_heights = [max(10, int(usable_h * w / wsum)) for w in weights]
        # Upper tiers are narrower than lower ones.
        base_body_w = int(top_rect.width * 0.70)
        body_widths = [max(10, int(base_body_w * (0.90 ** i)))
                       for i in range(tier_count_top)]
        # i = 0 is the BOTTOM-most tier above the gap (closest to player).
        # Build from the gap up so the first eave is the widest.
        y_cursor = top_rect.bottom - finial_h
        for i in range(tier_count_top):
            th = tier_heights[i]
            bw = body_widths[i]
            wall_top = y_cursor - th
            if wall_top < top_rect.y:
                break
            _wall_strip(surf, tcx - bw // 2, wall_top, bw, th, palette)
            if th > 7 and bw > 10:
                _window_lattice(surf, tcx, wall_top + 2,
                                min(8, bw - 6), min(6, th - 6), palette)
            overhang = max(5, 8 - i)
            depth = 4
            _eave(surf, tcx, wall_top, bw // 2, overhang, depth,
                  roof, accent, curl=1.0)
            y_cursor = wall_top - depth + 1

        # Downward finial — a hefty inverted sōrin pointing into the gap. Real
        # disks (not 1 px lines) plus a downward flame jewel so the player
        # actually reads it as the "ceiling temple's spire" at game scale.
        gold = _gilt(palette)
        dark_pal = palette['stone_dark']
        bright = _shade(gold, 40)
        spike_top_y = top_rect.bottom - finial_h
        spike_bot_y = min(top_rect.bottom + 4,
                          top_rect.bottom + finial_h - 2)
        # Inverted lotus pad at the spire's base (= just under the lowest tier).
        pygame.draw.ellipse(surf, dark_pal, (tcx - 6, spike_top_y - 1, 12, 6))
        pygame.draw.ellipse(surf, gold, (tcx - 5, spike_top_y, 10, 4))
        # Central spire pole.
        pygame.draw.line(surf, dark_pal,
                         (tcx, spike_top_y + 3), (tcx, spike_bot_y - 4), 2)
        # 4 disks tapering DOWN the spire — widest at top, narrowest at the tip.
        disks = 4
        for k in range(disks):
            ry = spike_top_y + 6 + int(k * (finial_h - 12) / max(1, disks - 1))
            rw = max(2, 5 - k)
            pygame.draw.ellipse(surf, dark_pal,
                                (tcx - rw - 1, ry - 1, rw * 2 + 2, 3))
            pygame.draw.ellipse(surf, gold,
                                (tcx - rw, ry, rw * 2, 2))
        # Downward flame jewel at the tip, pointing into the gap.
        tip_y = spike_bot_y
        pygame.draw.circle(surf, dark_pal, (tcx, tip_y - 4), 3)
        pygame.draw.circle(surf, gold, (tcx, tip_y - 4), 2)
        pygame.draw.polygon(surf, bright,
                            [(tcx, tip_y + 2), (tcx - 2, tip_y - 3),
                             (tcx + 2, tip_y - 3)])

        # Hanging moss + per-seed flavour.
        for off in (-12, -4, 4, 12):
            draw_moss_strand(surf, tcx + off, top_rect.bottom - finial_h - 2,
                             7 + abs(off) % 5, palette,
                             jitter_seed=seed + off)
        if flavor == 'pine' and top_rect.height > 80:
            draw_wuling_pine(surf, tcx + 12, top_rect.bottom - 38, 16,
                             palette, lean=8, direction='down', layers=3)
        elif flavor == 'lantern':
            draw_paper_lantern(surf, tcx, top_rect.bottom - finial_h - 4,
                               strand=8, scale=0.7, color='gold')


# ── 3. Facing Pair (twin tō) ────────────────────────────────────────────────

def candidate_facing_pair(surf, top_rect, bot_rect, palette, seed):
    """Top AND bottom rects each carry a full mini Japanese tō whose finials
    point at the gap. Reads as a bookended temple corridor."""
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2
    roof = _terracotta(palette)
    accent = _gilt(palette)
    wall = palette['stone_mid']
    flavor = _flavor_for(seed)

    tier_count = rng.choice([3, 4, 5])

    # ── Bottom mini tō (rooted on ground, sōrin UP) ────────────────────
    if bot_rect.height > 32:
        plinth_h = 8
        plinth_w = int(bot_rect.width * 1.08)
        pygame.draw.rect(surf, _shade(wall, -30),
                         (bcx - plinth_w // 2, bot_rect.bottom - plinth_h,
                          plinth_w, plinth_h))
        pygame.draw.rect(surf, palette['stone_light'],
                         (bcx - plinth_w // 2, bot_rect.bottom - plinth_h,
                          plinth_w, 2))

        finial_h = 22
        usable_h = bot_rect.height - plinth_h - finial_h
        weights = [1.0 - 0.10 * i for i in range(tier_count)]
        wsum = sum(weights)
        tier_heights = [max(10, int(usable_h * w / wsum)) for w in weights]
        base_body_w = int(bot_rect.width * 0.86)
        body_widths = [max(10, int(base_body_w * (0.88 ** i)))
                       for i in range(tier_count)]

        y_cursor = bot_rect.bottom - plinth_h
        tier_tops = []
        for i in range(tier_count):
            th = tier_heights[i]
            bw = body_widths[i]
            wall_top = y_cursor - th
            tier_tops.append((wall_top, bw, th))
            _timber_wall(surf, bcx - bw // 2, wall_top, bw, th, palette)
            if i == 0 and th > 12:
                _doorway(surf, bcx, y_cursor,
                         min(12, bw - 6), min(10, th - 4), palette)
            elif th > 9 and bw > 12:
                _window_lattice(surf, bcx, wall_top + 2,
                                min(8, bw - 6), min(6, th - 6), palette)
            overhang = max(7, 10 - i)
            depth = 5 if i < tier_count - 1 else 4
            # Japanese eave — flatter curl than Tang.
            _eave(surf, bcx, wall_top, bw // 2, overhang, depth,
                  roof, accent, curl=0.55)
            y_cursor = wall_top - depth + 1

        top_wall_y = tier_tops[-1][0]
        _finial_sorin(surf, bcx, top_wall_y - 2, finial_h, palette)

        # Per-seed ornaments.
        if flavor == 'pine' and bot_rect.height > 90:
            draw_side_shrub(surf, bot_rect.x + 4,
                            bot_rect.bottom - plinth_h - 2, palette,
                            scale=0.85)
            draw_side_shrub(surf, bot_rect.x + bot_rect.width - 4,
                            bot_rect.bottom - plinth_h - 2, palette,
                            scale=0.85)
        elif flavor == 'lantern':
            lo_top, lo_bw, _ = tier_tops[0]
            draw_paper_lantern(surf, bcx - lo_bw // 2 - 4, lo_top + 2,
                               strand=8, scale=0.75, color='red')
            draw_paper_lantern(surf, bcx + lo_bw // 2 + 4, lo_top + 2,
                               strand=8, scale=0.75, color='red')
        elif flavor == 'cairn' and bot_rect.height > 80:
            draw_cairn(surf, bcx - plinth_w // 2 - 8,
                       bot_rect.bottom - 2, n=3, pennant=False)
        elif flavor == 'banner' and len(tier_tops) >= 2:
            mt_top, mt_bw, _ = tier_tops[1]
            bx = bcx + mt_bw // 2 - 4
            pygame.draw.rect(surf, _shade(roof, -10), (bx, mt_top + 1, 4, 12))
            pygame.draw.rect(surf, accent, (bx, mt_top + 1, 4, 2))

        # Climbing vine on one side (always — it's the candidate's house style).
        if bot_rect.height > 90:
            draw_climbing_vine(surf, bot_rect.x + bot_rect.width - 6,
                               bot_rect.y + 24, bot_rect.bottom - 14,
                               palette, seed=seed)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 4, 14, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 7, seed=seed)

    # ── Top mini tō (rooted on ceiling, sōrin DOWN) ────────────────────
    if top_rect.height > 32:
        plinth_h = 6
        plinth_w = int(top_rect.width * 1.08)
        # Ceiling plinth.
        pygame.draw.rect(surf, _shade(wall, -30),
                         (tcx - plinth_w // 2, 0, plinth_w, plinth_h))
        pygame.draw.rect(surf, _shade(palette['stone_light'], -10),
                         (tcx - plinth_w // 2, plinth_h - 1, plinth_w, 1))

        finial_h = 16
        usable_h = top_rect.height - plinth_h - finial_h
        weights = [1.0 - 0.10 * i for i in range(tier_count)]
        wsum = sum(weights)
        tier_heights = [max(10, int(usable_h * w / wsum)) for w in weights]
        # Top-most (ceiling-adjacent) tier widest; tier shrinks toward gap.
        base_body_w = int(top_rect.width * 0.86)
        body_widths = [max(10, int(base_body_w * (0.88 ** i)))
                       for i in range(tier_count)]

        # i=0 is the WIDEST tier — sits just under the ceiling plinth.
        y_cursor = plinth_h
        for i in range(tier_count):
            th = tier_heights[i]
            bw = body_widths[i]
            wall_top = y_cursor
            wall_bot = wall_top + th
            _timber_wall(surf, tcx - bw // 2, wall_top, bw, th, palette)
            if th > 7 and bw > 10:
                _window_lattice(surf, tcx, wall_top + 2,
                                min(8, bw - 6), min(6, th - 6), palette)
            # Eave curls UP (same direction as ground tō) — the player sees
            # the eave silhouette at every tier.
            overhang = max(6, 9 - i)
            depth = 4
            _eave(surf, tcx, wall_bot, bw // 2, overhang, depth,
                  roof, accent, curl=0.55)
            y_cursor = wall_bot + depth - 1

        # Downward sōrin from the bottom of the lowest tier — same beefy-disk
        # treatment as the mirrored candidate so the player sees a clear
        # spire pointing into the gap, not a wisp of pixels.
        gold = _gilt(palette)
        dark_pal = palette['stone_dark']
        bright = _shade(gold, 40)
        spike_top_y = y_cursor
        spike_bot_y = min(top_rect.bottom + 4, spike_top_y + finial_h)
        # Inverted lotus pad anchoring the spire to the lowest tier underside.
        pygame.draw.ellipse(surf, dark_pal, (tcx - 6, spike_top_y - 1, 12, 6))
        pygame.draw.ellipse(surf, gold, (tcx - 5, spike_top_y, 10, 4))
        # Spire pole.
        pygame.draw.line(surf, dark_pal,
                         (tcx, spike_top_y + 3), (tcx, spike_bot_y - 4), 2)
        # 4 tapering disks.
        disks = 4
        for k in range(disks):
            ry = spike_top_y + 6 + int(k * (finial_h - 12) / max(1, disks - 1))
            rw = max(2, 5 - k)
            pygame.draw.ellipse(surf, dark_pal,
                                (tcx - rw - 1, ry - 1, rw * 2 + 2, 3))
            pygame.draw.ellipse(surf, gold,
                                (tcx - rw, ry, rw * 2, 2))
        # Flame jewel tip.
        tip_y = spike_bot_y
        pygame.draw.circle(surf, dark_pal, (tcx, tip_y - 4), 3)
        pygame.draw.circle(surf, gold, (tcx, tip_y - 4), 2)
        pygame.draw.polygon(surf, bright,
                            [(tcx, tip_y + 2), (tcx - 2, tip_y - 3),
                             (tcx + 2, tip_y - 3)])

        # Hanging moss off the lowest eave's tips.
        for off in (-14, -4, 4, 14):
            draw_moss_strand(surf, tcx + off, spike_top_y - 4,
                             7 + abs(off) % 4, palette,
                             jitter_seed=seed + off)

        # Per-seed flavour for the top half.
        if flavor == 'lantern':
            draw_paper_lantern(surf, tcx - 16, spike_top_y,
                               strand=10, scale=0.7, color='red')
            draw_paper_lantern(surf, tcx + 16, spike_top_y,
                               strand=10, scale=0.7, color='red')
        elif flavor == 'banner':
            # Vertical banner on the ceiling-adjacent tier.
            bx = tcx + body_widths[0] // 2 - 4
            pygame.draw.rect(surf, _shade(roof, -10), (bx, plinth_h + 3, 4, 12))
            pygame.draw.rect(surf, accent, (bx, plinth_h + 3, 4, 2))


# ── 4. Japanese 5-storey Tō + Hanging Cloud Shrine ──────────────────────────

def candidate_japanese_pavilion(surf, top_rect, bot_rect, palette, seed):
    """Bottom is a wooden 5-storey tō with deep up-curled eaves and a sōrin
    spire. Top is a small cloud-mounted shrine — readable single tier with an
    up-curled eave, lit window glow, suspended on a cloud puff and two visible
    chains from the ceiling."""
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2
    roof = _cedar(palette)
    accent = _gilt(palette)
    flavor = _flavor_for(seed)

    tier_count = rng.choice([3, 5, 7])

    # ── Tō tower ───────────────────────────────────────────────────────
    if bot_rect.height > 36:
        plinth_h = 8
        plinth_w = int(bot_rect.width * 1.10)
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -10),
                         (bcx - plinth_w // 2, bot_rect.bottom - plinth_h,
                          plinth_w, plinth_h))
        pygame.draw.rect(surf, palette['stone_light'],
                         (bcx - plinth_w // 2, bot_rect.bottom - plinth_h,
                          plinth_w, 2))

        finial_h = 30
        usable_h = bot_rect.height - plinth_h - finial_h
        weights = [1.0 - 0.09 * i for i in range(tier_count)]
        wsum = sum(weights)
        tier_heights = [max(10, int(usable_h * w / wsum)) for w in weights]
        base_body_w = int(bot_rect.width * 0.78)
        # Japanese tō: tier widths only narrow slightly each storey — the
        # silhouette is mostly defined by the wide eave overhang.
        body_widths = [max(10, int(base_body_w * (0.92 ** i)))
                       for i in range(tier_count)]

        y_cursor = bot_rect.bottom - plinth_h
        tier_tops = []
        for i in range(tier_count):
            th = tier_heights[i]
            bw = body_widths[i]
            wall_top = y_cursor - th
            tier_tops.append((wall_top, bw, th))
            _timber_wall(surf, bcx - bw // 2, wall_top, bw, th, palette)
            if i == 0 and th > 12:
                _doorway(surf, bcx, y_cursor,
                         min(12, bw - 6), min(10, th - 4), palette)
            elif th > 9 and bw > 12:
                _window_lattice(surf, bcx, wall_top + 2,
                                min(10, bw - 6), min(7, th - 6), palette)
            # Deep, gently up-curled eave — much wider than the wall below.
            overhang = max(9, 12 - i)
            depth = 5
            _eave(surf, bcx, wall_top, bw // 2, overhang, depth,
                  roof, accent, curl=0.50)
            y_cursor = wall_top - depth + 1

        # Sōrin finial.
        top_wall_y = tier_tops[-1][0]
        _finial_sorin(surf, bcx, top_wall_y - 2, finial_h, palette)

        # Per-seed flavours.
        if flavor == 'pine':
            draw_wuling_pine(surf, bot_rect.x + 6,
                             bot_rect.bottom - plinth_h, 20,
                             palette, lean=-6, layers=3)
            draw_wuling_pine(surf, bot_rect.x + bot_rect.width - 6,
                             bot_rect.bottom - plinth_h, 18,
                             palette, lean=6, layers=3)
        elif flavor == 'lantern' and tier_tops:
            lo_top, lo_bw, _ = tier_tops[0]
            draw_paper_lantern(surf, bcx - lo_bw // 2 - 6, lo_top + 2,
                               strand=10, scale=0.8, color='red')
            draw_paper_lantern(surf, bcx + lo_bw // 2 + 6, lo_top + 2,
                               strand=10, scale=0.8, color='red')
        elif flavor == 'cairn' and bot_rect.height > 80:
            draw_cairn(surf, bcx - plinth_w // 2 - 10,
                       bot_rect.bottom - 2, n=3, pennant=False)
        elif flavor == 'banner' and len(tier_tops) >= 3:
            mt_top, mt_bw, _ = tier_tops[len(tier_tops) // 2]
            bx = bcx + mt_bw // 2 - 4
            pygame.draw.rect(surf, _shade(roof, -10), (bx, mt_top + 1, 4, 14))
            pygame.draw.rect(surf, accent, (bx, mt_top + 1, 4, 2))

        # Always — ground ferns + grass to make it feel grown-into.
        draw_ground_ferns(surf, bcx, bot_rect.bottom - plinth_h + 1,
                          bot_rect.width + 6, 3, palette, seed=seed)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 4, 14, palette, seed=seed)

    # ── Hanging cloud shrine (top) ─────────────────────────────────────
    if top_rect.height > 32:
        # The shrine hangs from the ceiling at the top of top_rect. It's a
        # single readable tier with: up-curled eave, lit window glow, walls,
        # and a soft cloud puff at its base. Two chains anchor it to the
        # screen ceiling.
        shrine_h = min(top_rect.height - 6, 46)
        # Anchor shrine BOTTOM ~10 px above the gap so a cloud puff fits below.
        shrine_bot_y = top_rect.bottom - 8
        shrine_top_y = shrine_bot_y - shrine_h
        body_w = top_rect.width - 6
        body_x = tcx - body_w // 2

        # Chains from the ceiling down to the shrine roof corners.
        for cx_off in (-body_w // 2 + 4, body_w // 2 - 4):
            chain_x = tcx + cx_off
            pygame.draw.line(surf, palette['stone_dark'],
                             (chain_x, top_rect.y),
                             (chain_x, shrine_top_y), 1)
            # Chain link dots so the eye reads links, not a stick.
            for cy in range(top_rect.y + 4, shrine_top_y, 5):
                pygame.draw.circle(surf, _shade(palette['stone_light'], 10),
                                   (chain_x, cy), 2, 1)

        # Eave on top of the shrine — single deep curl.
        _eave(surf, tcx, shrine_top_y, body_w // 2, 8, 6,
              roof, accent, curl=0.85)

        # Shrine wall body.
        wall_top = shrine_top_y + 1
        wall_h = shrine_bot_y - wall_top
        if wall_h > 6:
            _wall_strip(surf, body_x + 2, wall_top, body_w - 4, wall_h,
                        palette)
            # Corner posts + lit window in the centre.
            for px in (body_x + 3, body_x + body_w - 4):
                pygame.draw.line(surf, palette['stone_dark'],
                                 (px, wall_top), (px, shrine_bot_y - 1), 1)
            if wall_h > 10:
                _lit_window(surf, tcx, wall_top + 2,
                            min(16, body_w - 12), min(wall_h - 4, 14),
                            palette)

        # Floor lip.
        pygame.draw.rect(surf, _shade(roof, -20),
                         (body_x + 2, shrine_bot_y - 2, body_w - 4, 2))

        # Cloud puff beneath the shrine — pillowy, two-tone, larger than
        # before so the eye reads "shrine resting on a cloud" rather than
        # "shrine sitting on a wall lip". Soft underside shadow + brighter
        # top crest with extra puff lobes for silhouette weight.
        cloud_top = shrine_bot_y - 2
        cloud_col = _mix(palette['stone_light'], (252, 252, 252), 0.65)
        cloud_shade = _shade(cloud_col, -32)
        cloud_lobes = (
            (-24, 5), (-16, 8), (-8, 10), (0, 11), (8, 10), (16, 8), (24, 5),
            (-20, 4), (-4, 6), (4, 6), (20, 4),
        )
        # Underside shadow pass — slightly offset down.
        for cx_off, sz in cloud_lobes:
            pygame.draw.circle(surf, cloud_shade,
                               (tcx + cx_off, cloud_top + 3), sz + 2)
        # Cloud body pass.
        for cx_off, sz in cloud_lobes:
            pygame.draw.circle(surf, cloud_col,
                               (tcx + cx_off, cloud_top + 1), sz)
        # Bright crest highlight along the top — gives a wisp of volume.
        bright_cloud = _mix(cloud_col, (255, 255, 255), 0.5)
        for cx_off, sz in cloud_lobes:
            if abs(cx_off) <= 16:
                pygame.draw.circle(surf, bright_cloud,
                                   (tcx + cx_off, cloud_top - 1),
                                   max(1, sz - 3))

        # Per-seed flavour for the shrine — sized up so the silhouette
        # actually changes across the row of five spawns. Each flavor
        # commits to one bold visible detail instead of a tiny inset one.
        if flavor == 'lantern':
            # TWO lanterns dangling from BOTH eave corners — symmetrical
            # silhouette tells you instantly which spawn this is.
            draw_paper_lantern(surf, tcx - body_w // 2 - 3,
                               shrine_top_y + 4, strand=12, scale=0.8,
                               color='red')
            draw_paper_lantern(surf, tcx + body_w // 2 + 3,
                               shrine_top_y + 4, strand=12, scale=0.8,
                               color='red')
        elif flavor == 'banner':
            # Long pennant banner dropping from the eave centre down past
            # the cloud — the dominant flag-spawn cue.
            bx = tcx - 3
            pygame.draw.rect(surf, _shade(roof, -30),
                             (bx, shrine_top_y + 6, 6, 22))
            pygame.draw.rect(surf, accent,
                             (bx, shrine_top_y + 6, 6, 3))
            pygame.draw.rect(surf, _gilt(palette),
                             (bx + 1, shrine_top_y + 14, 4, 2))
            # Tassel V at the bottom.
            pygame.draw.polygon(surf, _shade(roof, -30),
                                [(bx, shrine_top_y + 28),
                                 (bx + 3, shrine_top_y + 32),
                                 (bx + 6, shrine_top_y + 28)])
        elif flavor == 'pine':
            # Two pines clinging to the cloud sides.
            draw_wuling_pine(surf, tcx - 20, cloud_top + 4, 12,
                             palette, lean=-4, layers=2)
            draw_wuling_pine(surf, tcx + 20, cloud_top + 4, 12,
                             palette, lean=4, layers=2)
        elif flavor == 'cairn':
            # Tiny floating cairn riding the cloud.
            draw_cairn(surf, tcx + 18, cloud_top + 3, n=3, pennant=False)

        # Bird drifting near the shrine.
        if top_rect.height > 60:
            draw_bird_sil(surf, tcx + 22,
                          max(20, top_rect.y + 28), size=4)


# ── 5. Tibetan Chorten + Prayer-Flag Canopy ─────────────────────────────────

def candidate_stupa_canopy(surf, top_rect, bot_rect, palette, seed):
    """Bottom is a whitewashed chorten (square stepped base, bell-dome,
    harmika cube, 13-step spire + sun-moon-flame jewel). Top is a sagging
    prayer-flag canopy strung from two carved anchor stones."""
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2
    white = _chorten_white(palette)
    edge = _shade(white, -55)
    shadow = _shade(white, -28)
    gold = _gilt(palette)
    dark = palette['stone_dark']
    flavor = _flavor_for(seed)

    step_count = rng.choice([3, 4, 5])
    n_flag_strings = rng.choice([2, 3])

    # ── Chorten ────────────────────────────────────────────────────────
    if bot_rect.height > 60:
        # Vertical budget — leave room for spire (~30) + harmika (8) + dome (24).
        spire_extent = 30
        harmika_h = 10
        dome_h = 24
        steps_avail = bot_rect.height - spire_extent - harmika_h - dome_h - 4
        steps_avail = max(20, steps_avail)
        # Square stepped base — each step widens slightly toward the bottom.
        step_h = max(6, steps_avail // step_count)
        widest = int(bot_rect.width * 1.10)
        narrowest = int(bot_rect.width * 0.72)
        # Bottom-up — top step (smallest) closest to the dome.
        for i in range(step_count):
            t = i / max(1, step_count - 1)
            sw = int(widest + (narrowest - widest) * (1 - t))
            sy = bot_rect.bottom - step_h * (step_count - i)
            if sy < bot_rect.y:
                break
            # Edge shadow band.
            pygame.draw.rect(surf, edge, (bcx - sw // 2, sy, sw, step_h))
            pygame.draw.rect(surf, white,
                             (bcx - sw // 2 + 1, sy + 1, sw - 2, step_h - 2))
            # Right-edge cool shadow.
            pygame.draw.rect(surf, shadow,
                             (bcx + sw // 2 - 2, sy + 1, 2, step_h - 2))
            # Gold trim along the top of the topmost step.
            if i == step_count - 1:
                pygame.draw.rect(surf, gold,
                                 (bcx - sw // 2 + 3, sy, sw - 6, 1))

        # Bell dome (anda) sits centered on the top of the topmost step. We
        # draw it as a half-ellipse with a flat bottom so it doesn't read
        # as a beach ball — extend slightly past the top step.
        top_step_y = bot_rect.bottom - step_h * step_count
        dome_w = int(bot_rect.width * 0.80)
        dome_y = top_step_y - dome_h + 6
        # Full ellipse but bottom clipped flat at top_step_y.
        dome_rect = pygame.Rect(bcx - dome_w // 2, dome_y, dome_w, dome_h)
        dome_inner = dome_rect.inflate(-2, -2)
        # Mask: draw ellipse then a wall-color rect to "flatten" the bottom.
        pygame.draw.ellipse(surf, edge, dome_rect)
        pygame.draw.ellipse(surf, white, dome_inner)
        # Cool shadow along the dome's lower-right.
        for k in range(3):
            pygame.draw.arc(surf, shadow, dome_inner,
                            math.pi * 1.55, math.pi * 1.95, 1)
        # Hard horizontal cut at the dome's base so the bell sits flat on the
        # top step instead of bulging below it.
        pygame.draw.rect(surf, edge,
                         (bcx - dome_w // 2, top_step_y - 1, dome_w, 2))
        # Gold belly band — the dome's iconic decorative belt.
        belt_y = dome_y + dome_h - 9
        pygame.draw.rect(surf, gold,
                         (bcx - dome_w // 2 + 4, belt_y, dome_w - 8, 2))
        pygame.draw.rect(surf, _shade(gold, -30),
                         (bcx - dome_w // 2 + 4, belt_y + 2, dome_w - 8, 1))

        # Harmika cube sits centered on top of the dome.
        harmika_w = int(bot_rect.width * 0.46)
        harmika_y = dome_y - harmika_h + 2
        pygame.draw.rect(surf, edge,
                         (bcx - harmika_w // 2, harmika_y, harmika_w,
                          harmika_h))
        pygame.draw.rect(surf, white,
                         (bcx - harmika_w // 2 + 1, harmika_y + 1,
                          harmika_w - 2, harmika_h - 2))
        # Right-edge cool shadow.
        pygame.draw.rect(surf, shadow,
                         (bcx + harmika_w // 2 - 2, harmika_y + 1,
                          2, harmika_h - 2))
        # Buddha eyes — two small dark slashes.
        eye_y = harmika_y + harmika_h // 2 - 1
        pygame.draw.line(surf, dark, (bcx - 6, eye_y), (bcx - 3, eye_y), 1)
        pygame.draw.line(surf, dark, (bcx + 3, eye_y), (bcx + 6, eye_y), 1)
        # Tiny gold tilaka dot between the eyes.
        pygame.draw.circle(surf, gold, (bcx, eye_y - 3), 1)

        # 13-step spire + sun-moon-flame stack above the harmika.
        _finial_chorten(surf, bcx, harmika_y, palette)

        # Per-seed flavours.
        if flavor == 'pine':
            draw_wuling_pine(surf, bot_rect.x + 4,
                             bot_rect.bottom - step_h, 22,
                             palette, lean=-5, layers=3)
            draw_wuling_pine(surf, bot_rect.x + bot_rect.width - 4,
                             bot_rect.bottom - step_h, 22,
                             palette, lean=5, layers=3)
        elif flavor == 'cairn':
            draw_cairn(surf, bcx + bot_rect.width // 2 + 8,
                       bot_rect.bottom - 2, n=3, pennant=True)
        elif flavor == 'lantern':
            # Butter lamps either side, sitting on the dome's belly band.
            lamp_y = belt_y - 14
            draw_paper_lantern(surf, bcx - widest // 2 - 4, lamp_y,
                               strand=4, scale=0.65, color='gold')
            draw_paper_lantern(surf, bcx + widest // 2 + 4, lamp_y,
                               strand=4, scale=0.65, color='gold')
        elif flavor == 'banner':
            # A short carved offering stone at the base.
            ox = bcx - widest // 2 - 6
            pygame.draw.rect(surf, edge, (ox - 3, bot_rect.bottom - 7, 7, 6))
            pygame.draw.rect(surf, white,
                             (ox - 2, bot_rect.bottom - 6, 5, 4))
            pygame.draw.rect(surf, gold,
                             (ox - 2, bot_rect.bottom - 6, 5, 1))

        # Ground cover always.
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 8, 14, palette, seed=seed)
    elif bot_rect.height > 0:
        # Degenerate small chorten if the gap is huge — single capsule.
        pygame.draw.ellipse(surf, white,
                            (bot_rect.x + 4, bot_rect.y + 2,
                             bot_rect.width - 8, max(1, bot_rect.height - 4)))

    # ── Ceiling-mounted chorten — STRUCTURAL MIRROR ────────────────────
    # Round-11 user direction overrides the prior prayer-flag canopy:
    # the top must be a true 180° structural mirror of the bottom
    # chorten (stepped square base at the ceiling, bell dome + harmika
    # below, 13-step spire + sun-moon-flame jewel pointing DOWN into
    # the gap). We render the chorten anatomy into a temp surface in
    # standing orientation, then `pygame.transform.flip` so the base
    # anchors at the ceiling and the flame tip pokes into the gap.
    # Prayer flags + anchor stones dropped — they were ornaments, not
    # structure; the user explicitly defers ornaments to a later pass.
    if top_rect.height > 60:
        # `_finial_chorten` extends ~14 px above the harmika cube — keep
        # the reserved spire extent close to that so the chorten fills
        # the full top_rect envelope instead of leaving dead space at
        # the gap edge. The 16-px reserve gives the flame jewel a tiny
        # padding past the gap so it pokes INTO the gap per user spec.
        spire_extent = 16
        harmika_h = 10
        dome_h = 24
        steps_avail = top_rect.height - spire_extent - harmika_h - dome_h - 4
        steps_avail = max(20, steps_avail)
        step_h = max(6, steps_avail // step_count)
        widest = int(top_rect.width * 1.10)
        narrowest = int(top_rect.width * 0.72)
        # Tight temp sizing — flipping places the sun-moon-flame jewel
        # tip ~3 px above the temp's bottom, so blitting at top_rect.y
        # lands the flame just inside top_rect.bottom (the gap edge).
        tmp_h = top_rect.height + 4
        tmp_w = max(widest + 16, top_rect.width * 4)
        tmp = pygame.Surface((tmp_w, tmp_h), pygame.SRCALPHA)
        tmp_cx = tmp_w // 2
        tmp_bot = tmp_h - 1
        # Stepped square base — same widths as the bottom chorten so
        # the silhouettes overlay clean as one mirrored pair.
        for i in range(step_count):
            t = i / max(1, step_count - 1)
            sw = int(widest + (narrowest - widest) * (1 - t))
            sy = tmp_bot - step_h * (step_count - i)
            if sy < 0:
                break
            pygame.draw.rect(tmp, edge, (tmp_cx - sw // 2, sy, sw, step_h))
            pygame.draw.rect(tmp, white,
                             (tmp_cx - sw // 2 + 1, sy + 1, sw - 2, step_h - 2))
            pygame.draw.rect(tmp, shadow,
                             (tmp_cx + sw // 2 - 2, sy + 1, 2, step_h - 2))
            if i == step_count - 1:
                pygame.draw.rect(tmp, gold,
                                 (tmp_cx - sw // 2 + 3, sy, sw - 6, 1))
        # Bell dome anchored on the top of the topmost step.
        top_step_y = tmp_bot - step_h * step_count
        dome_w = int(top_rect.width * 0.80)
        dome_y = top_step_y - dome_h + 6
        dome_rect = pygame.Rect(tmp_cx - dome_w // 2, dome_y, dome_w, dome_h)
        dome_inner = dome_rect.inflate(-2, -2)
        pygame.draw.ellipse(tmp, edge, dome_rect)
        pygame.draw.ellipse(tmp, white, dome_inner)
        for _ in range(3):
            pygame.draw.arc(tmp, shadow, dome_inner,
                            math.pi * 1.55, math.pi * 1.95, 1)
        pygame.draw.rect(tmp, edge,
                         (tmp_cx - dome_w // 2, top_step_y - 1, dome_w, 2))
        belt_y = dome_y + dome_h - 9
        pygame.draw.rect(tmp, gold,
                         (tmp_cx - dome_w // 2 + 4, belt_y, dome_w - 8, 2))
        pygame.draw.rect(tmp, _shade(gold, -30),
                         (tmp_cx - dome_w // 2 + 4, belt_y + 2, dome_w - 8, 1))
        # Harmika cube on the dome.
        harmika_w = int(top_rect.width * 0.46)
        harmika_y = dome_y - harmika_h + 2
        pygame.draw.rect(tmp, edge,
                         (tmp_cx - harmika_w // 2, harmika_y,
                          harmika_w, harmika_h))
        pygame.draw.rect(tmp, white,
                         (tmp_cx - harmika_w // 2 + 1, harmika_y + 1,
                          harmika_w - 2, harmika_h - 2))
        pygame.draw.rect(tmp, shadow,
                         (tmp_cx + harmika_w // 2 - 2, harmika_y + 1,
                          2, harmika_h - 2))
        # Buddha eyes + tilaka — same proportions as the bottom so the
        # flipped face reads as a true mirror.
        eye_y = harmika_y + harmika_h // 2 - 1
        pygame.draw.line(tmp, dark, (tmp_cx - 6, eye_y),
                         (tmp_cx - 3, eye_y), 1)
        pygame.draw.line(tmp, dark, (tmp_cx + 3, eye_y),
                         (tmp_cx + 6, eye_y), 1)
        pygame.draw.circle(tmp, gold, (tmp_cx, eye_y - 3), 1)
        # 13-step spire + sun-moon-flame jewel.
        _finial_chorten(tmp, tmp_cx, harmika_y, palette)
        flipped = pygame.transform.flip(tmp, False, True)
        surf.blit(flipped, (tcx - tmp_w // 2, top_rect.y))


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
    "facing_pair":       "Twin mini tō — sōrin finials face the gap",
    "japanese_pavilion": "Japanese tō + hanging cloud shrine on chains",
    "stupa_canopy":      "Tibetan chorten + prayer-flag canopy on anchor stones",
}
