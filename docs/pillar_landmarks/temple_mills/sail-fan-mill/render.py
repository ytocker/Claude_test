"""Standalone candidate: `sail-fan-mill` — a battered Song-brick grist-shrine
cone crowned by a wide scalloped 180° CANVAS FAN sweep: one continuous half-
sunburst of ribbed sail-blades spilling into both gutters.

Colocated EXPLORATION module for the pillar-landmark design loop. It follows the
shipped pagoda idiom (`candidate_*(surf, top_rect, bot_rect, palette, seed)`, an
upright `_draw_one` reused for both rects, the ceiling twin a vertical flip of a
temp surface) but does NOT import into or modify any game/ module — it only
borrows read-only colour + AA + ornament helpers so the exploration reads like
the real game at the pagoda fidelity bar.

Seeded on the winning `waterwheel-mill`: the battered `_brick_cone` body is KEPT
verbatim; the water-wheel, launder + splash pool are REMOVED entirely. The crown
is the new mechanism.

Silhouette identity (set-level pin): the ONLY concept whose crown is a FILLED
convex FAN ARC — a 180° sweep of overlapping canvas leaves with a FLAT base rail
and a SCALLOPED leech edge (vs vane-star's pointed gold rosette, parasol's domed
skirt). The fan is a wide, flat half-ellipse (big horizontal footprint, shallow
vertical rise) so the whole crown reads as one rotating vane-sheet catching a low
sun. Blackout reads as a fat pyramid-cone erupting into a peacock fan.

Column-fill contract: the ~58 px collision column is carried top-to-bottom by the
BRICK CONE; the fan is pure crown/gutter overhang laid over a solid masonry core.
A slim bronze finial mast pokes up through the fan centre to the gap rim so the
centreline is continuously occupied above the shoulder.

Mirror: the ceiling twin is a true vertical FLIP. The fan is bilaterally
symmetric about `cx`, so the flip leaves a clean fan on the hung twin (leaves
sweep down toward the gap). The fan is a shallow half-ellipse whose apex clears
the rim, so on the hung copy the fan-tips hang short of the gap rim while the
thin finial mast alone reaches it.

Run:  python docs/pillar_landmarks/temple_mills/sail-fan-mill/render.py
Out:  docs/pillar_landmarks/temple_mills/sail-fan-mill/round_1.png
"""
from __future__ import annotations

import math
import os
import pathlib
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_REPO = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO))

import pygame

from game.config import GROUND_Y, PIPE_W
from game import biome
from game.pillar_pagodas import (
    _mix,
    _shade,
    _gradient_rect,               # noqa: F401 — kit member (panel volume trick)
    _aa_polyline,
    _lit_niche,
    _tile_hatch,
    _draw_plinth_mist,
    _is_dark_sky,
    _is_warming_sky,              # noqa: F401 — imported per brief material kit
    _cap_lit_for_dark_sky,
    _cap_dark_for_dark_sky,
    _terracotta,
    _song_brick,                 # noqa: F401 — imported per brief material kit
    _brick_mortar,               # body dependency of the reused _brick_cone
    _songyue_dwarf_eave,         # body dependency of the reused corbel courses
    _bronze,
    _gold_bright,
    _plaster,
    _vermilion,
)
from game.pillar_variants import draw_grass_bed
from game.draw import draw_side_shrub


# ── Material roles (all biome-derived via _mix/_shade so day→night retints) ───
#
# BRICK CONE  → stone_dark / stone_mid  (_terracotta + _brick_mortar): the warm
#   clay grist tower kept verbatim from the seed.
# FAN CANVAS  → stone_light (_plaster): sail-leaves, lit→shadow across the sweep
#   so the fan reads as one turning vane-sheet, never a flat painted arc.
# SPARS + RIBS + HUB → stone_accent (_bronze/_gold_bright): the fan armature.
# TIP-BAND    → horizon-warm (_vermilion): the leech scallop band that ties the
#   canvas fan back to the shrine's festival red.

def _brick_lit(p):
    # Sun-side clay — capped at dusk/night so the shaded flank + niche glow
    # carry the silhouette instead of a value-spiking wall.
    return _cap_lit_for_dark_sky(_shade(_terracotta(p), 28), p)


def _brick_mid(p):
    return _terracotta(p)


def _brick_shadow(p):
    # Floored at night so the shaded cone edge keeps value over a deep sky and
    # the whole mass doesn't collapse into one black blob.
    return _cap_dark_for_dark_sky(_shade(_terracotta(p), -42), p, floor=60)


def _mortar(p):
    return _shade(_brick_mortar(p), 16)


def _edge_rim(p):
    # Faint cool-lit rim run down the shadow-side outline at night so the cone
    # holds its edge against a dark sky (day palettes never trigger it).
    return _mix(p['stone_mid'], p['stone_light'], 0.55)


# ── Fan-canvas material triad (derived from _plaster so the biome retints) ────

def _canvas_mid(p):
    return _plaster(p)


def _canvas_lit(p):
    # Sun-struck sail face — capped at night so the fan doesn't value-spike into
    # a white blob and drown the finial + hub halo.
    return _cap_lit_for_dark_sky(_shade(_plaster(p), 24), p)


def _canvas_shadow(p):
    # Floored at night so the shaded leaves of the sweep keep value against the
    # dark sky instead of fusing into one silhouette.
    return _cap_dark_for_dark_sky(_shade(_plaster(p), -50), p, floor=58)


def _spar(p):
    # Dark bamboo/bronze spar between leaves — the rigid ribs that make the fan
    # read as an ARRAY of sails, not a single canvas smear.
    return _shade(_bronze(p), -46)


def _rib(p):
    # Bamboo batten cross-ribs hatched along each leaf — mid bronze over canvas.
    return _mix(_canvas_shadow(p), _bronze(p), 0.55)


# ── Brick cone body (kept verbatim from the seed waterwheel-mill) ─────────────

def _brick_cone(surf, cx, top_y, base_y, hw_top, hw_base, palette):
    """Steeply-battered brick trapezoid painted as horizontal scan-lines, each a
    short left-lit → mid → right-shadow ramp, so the flat cone reads as rounded
    masonry volume at PIPE_W=58 (the `_gradient_rect` volume trick adapted to a
    per-row sloping width). Mortar coursing is overlaid every 3 px with a broken
    half-cell offset so the eye reads brick-bond, not stripes. WASM-safe: only
    pygame.draw 1-px lines."""
    lit, mid, shadow = _brick_lit(palette), _brick_mid(palette), _brick_shadow(palette)
    mortar = _mortar(palette)
    rim = _edge_rim(palette)
    dark_sky = _is_dark_sky(palette)
    h = base_y - top_y
    if h < 2:
        return
    for i in range(h):
        y = top_y + i
        t = i / (h - 1)                       # 0 at shoulder, 1 at base
        hw = int(round(hw_top + (hw_base - hw_top) * t))
        if hw < 1:
            continue
        for j in range(hw):
            u = j / max(1, hw)
            pygame.draw.line(surf, _mix(lit, mid, u),
                             (cx - hw + j, y), (cx - hw + j, y), 1)
            pygame.draw.line(surf, _mix(mid, shadow, u),
                             (cx + j, y), (cx + j, y), 1)
        # Brick coursing: a mortar row every 3 px, alternate rows broken at the
        # centreline for a bonded-masonry read rather than ledger stripes.
        if i % 3 == 2:
            if (i // 3) % 2 == 0:
                pygame.draw.line(surf, mortar,
                                 (cx - hw + 1, y), (cx + hw - 1, y), 1)
            else:
                pygame.draw.line(surf, mortar,
                                 (cx - hw + 1, y), (cx - 1, y), 1)
                pygame.draw.line(surf, mortar,
                                 (cx + 1, y), (cx + hw - 1, y), 1)
        if dark_sky:
            pygame.draw.line(surf, rim, (cx + hw - 1, y), (cx + hw - 1, y), 1)
    # AA the two sloping silhouette edges so the cone flanks read smooth.
    edge = _shade(_brick_shadow(palette), -18)
    _aa_polyline(surf, edge, [(cx - hw_top, top_y), (cx - hw_base, base_y)])
    _aa_polyline(surf, edge, [(cx + hw_top, top_y), (cx + hw_base, base_y)])


# ── The scalloped canvas fan ──────────────────────────────────────────────────

def _ell(cx, hub_y, rx, ry, a, s=1.0):
    # Point on the (scaled) fan ellipse at angle `a` measured up from the flat
    # base rail — cos maps left/right, -sin maps the shallow vertical rise.
    return (cx + rx * s * math.cos(a), hub_y - ry * s * math.sin(a))


def _sail_fan(surf, cx, hub_y, top_y, rx, ry, n_blades, palette):
    """A 180° canvas FAN: a wide flat half-ellipse of overlapping ribbed sail-
    leaves, lit→shadow across the sweep so it reads as one rotating vane-sheet.
    Each leaf is a filled canvas wedge with a dark leading SPAR, bamboo cross-
    RIBS hatched along its centre, and a convex SCALLOP bump on the leech (outer)
    edge banded in vermilion — the flat-based scalloped canvas signature. A thin
    bronze finial mast pokes up through the centre to `top_y` (the gap rim) so
    the centreline stays occupied above the shoulder.

    WASM-safe: only pygame.draw polygon/line/circle + aalines and an additive
    SRCALPHA halo blit gated on a dark sky."""
    if rx < 8 or ry < 5:
        # Too short to fan — drop a stub finial so the centreline still reaches.
        pygame.draw.line(surf, _spar(palette), (cx, hub_y), (cx, top_y + 1), 2)
        pygame.draw.circle(surf, _gold_bright(palette), (cx, top_y + 1), 2)
        return

    c_lit, c_mid, c_shadow = _canvas_lit(palette), _canvas_mid(palette), _canvas_shadow(palette)
    spar = _spar(palette)
    rib = _rib(palette)
    verm = _vermilion(palette)
    dark_sky = _is_dark_sky(palette)
    r_in = max(3, int(min(rx, ry) * 0.22))

    # Shaded backing half-disc so the thin gaps between leaves never flash sky
    # over the gutter — the fan reads as a solid sweep with slotted ribs.
    backing = _shade(c_shadow, -14)
    back_pts = [(cx + rx * math.cos(a), hub_y - ry * math.sin(a))
                for a in [math.pi * k / 22 for k in range(23)]]
    back_pts.append((cx + rx, hub_y))
    back_pts.append((cx - rx, hub_y))
    pygame.draw.polygon(surf, backing, [(int(x), int(y)) for x, y in back_pts])

    amin, amax = 0.0, math.pi
    edges = [amin + (amax - amin) * k / n_blades for k in range(n_blades + 1)]

    for k in range(n_blades):
        a0, a1 = edges[k], edges[k + 1]
        am = 0.5 * (a0 + a1)
        # Across-sweep facing: low sun on the LEFT rim → left leaves lit, right
        # leaves shadowed, so the fan reads as caught mid-rotation.
        face = 0.5 - 0.5 * math.cos(am)
        base_col = _mix(_mix(c_shadow, c_mid, 0.58), c_lit, 0.12 + face * 0.72)

        o0 = _ell(cx, hub_y, rx, ry, a0)
        om = _ell(cx, hub_y, rx, ry, am, 1.06)       # convex scallop bump
        o1 = _ell(cx, hub_y, rx, ry, a1)
        i0 = (cx + r_in * math.cos(a0), hub_y - r_in * math.sin(a0))
        i1 = (cx + r_in * math.cos(a1), hub_y - r_in * math.sin(a1))
        leaf = [i0, o0, om, o1, i1]
        pygame.draw.polygon(surf, base_col, [(int(x), int(y)) for x, y in leaf])

        # A trailing-half shadow triangle so each leaf has an internal fold —
        # canvas volume, not a flat wedge.
        fold = _mix(base_col, c_shadow, 0.5)
        pygame.draw.polygon(surf, fold, [(int(cx), int(hub_y)),
                                         (int(om[0]), int(om[1])),
                                         (int(o1[0]), int(o1[1]))])

        # Bamboo cross-ribs: perpendicular battens hatched along the leaf spine.
        spine_o = _ell(cx, hub_y, rx, ry, am)
        _tile_hatch(surf, cx, hub_y, spine_o[0], spine_o[1], rib, step=4)

        # Dark leading SPAR on the a0 boundary so leaves stay a counted array.
        pygame.draw.line(surf, spar, (int(cx), int(hub_y)),
                         (int(o0[0]), int(o0[1])), 1)

        # Scalloped leech edge: a dark keyline under a vermilion tip-band so the
        # convex bump reads at 58 px and ties the fan to the shrine's red.
        scallop = [o0, om, o1]
        _aa_polyline(surf, _shade(verm, -40), scallop)
        _aa_polyline(surf, verm, [(o0[0], o0[1] - 1), (om[0], om[1] - 1),
                                  (o1[0], o1[1] - 1)])

    # Final trailing spar + the FLAT base rail (the fan's hard bottom edge).
    pygame.draw.line(surf, spar, (int(cx), int(hub_y)),
                     (int(cx - rx), int(hub_y)), 1)
    pygame.draw.line(surf, spar, (int(cx + rx), int(hub_y)),
                     (int(cx - rx), int(hub_y)), 2)
    pygame.draw.line(surf, _shade(spar, 22),
                     (int(cx + rx), int(hub_y - 1)),
                     (int(cx - rx), int(hub_y - 1)), 1)

    # Night halo behind the bronze hub (gated on dark sky — day never triggers).
    # Kept warm/amber-biased with low additive alphas so the core reads as a
    # gilt glow, never clipping to a hot white blowout over the lit canvas.
    if dark_sky:
        glow_r = 13
        sz = glow_r * 2 + 2
        glow = pygame.Surface((sz, sz), pygame.SRCALPHA)
        gcol = _mix(_bronze(palette), (232, 176, 92), 0.7)
        for ring, alpha in ((1.0, 34), (0.62, 60), (0.34, 92)):
            pygame.draw.circle(glow, (*gcol, alpha), (sz // 2, sz // 2),
                               max(1, int(glow_r * ring)))
        surf.blit(glow, (cx - sz // 2, hub_y - sz // 2),
                  special_flags=pygame.BLEND_RGBA_ADD)

    # Bronze hub boss over the leaf roots.
    pygame.draw.circle(surf, _shade(_bronze(palette), -28), (cx, hub_y), r_in + 2)
    pygame.draw.circle(surf, _bronze(palette), (cx, hub_y), r_in)
    pygame.draw.circle(surf, _gold_bright(palette), (cx - 1, hub_y - 1),
                       max(1, r_in - 2))

    # Slim bronze finial mast up through the fan centre to the gap rim.
    pygame.draw.line(surf, _shade(_bronze(palette), -24),
                     (cx, hub_y - r_in), (cx, top_y + 2), 2)
    pygame.draw.circle(surf, _bronze(palette), (cx, top_y + 2), 2)
    pygame.draw.circle(surf, _gold_bright(palette), (cx, top_y + 2), 1)


# ── One upright silhouette ───────────────────────────────────────────────────

def _draw_one(surf, cx, base_y, top_y, body_w, palette, seed, *, decor=True):
    """One upright sail-fan-mill filling [top_y, base_y]. Height-adaptive: the
    batter is capped so both shoulder and base half-widths stay ≥ PIPE_W/2 (the
    cone always fills the collision column); the crown zone + fan leaf-count
    scale down on short sections."""
    total_h = base_y - top_y
    if total_h < 20:
        return
    side = 1 if (seed % 2 == 0) else -1        # which flank carries the door

    # Batter capped: base spills into the gutter, shoulder stays wide enough that
    # every body row still spans the full 58 px column (hw >= PIPE_W/2 = 29).
    hw_base = max(PIPE_W // 2 + 4, int(body_w * 0.82))
    hw_cap = max(PIPE_W // 2 + 1, int(body_w * 0.60))   # >= 0.72 of hw_base

    # Crown zone above the shoulder: taller than the seed's corbel cap so the
    # shallow fan half-ellipse has vertical room and still clears the gap rim.
    crown_h = max(12, min(int(total_h * 0.22), 42))
    shoulder_y = top_y + crown_h

    # 3-layer plinth under the cone.
    plinth_h = 6 if total_h > 60 else 3
    pw0 = hw_base * 2 + 10
    if decor:
        _draw_plinth_mist(surf, cx, base_y, pw0 + 8, palette)
    pygame.draw.rect(surf, _shade(palette['stone_dark'], -16),
                     (cx - pw0 // 2, base_y - plinth_h, pw0, plinth_h))
    pygame.draw.rect(surf, _shade(palette['stone_mid'], -6),
                     (cx - pw0 // 2 + 2, base_y - plinth_h + 1, pw0 - 4, 2))
    pygame.draw.line(surf, palette['stone_light'],
                     (cx - pw0 // 2, base_y - plinth_h),
                     (cx + pw0 // 2, base_y - plinth_h), 1)

    body_base_y = base_y - plinth_h
    _brick_cone(surf, cx, shoulder_y, body_base_y, hw_cap, hw_base, palette)

    # Sparse corbel string-courses banding the shaft (2-3 total).
    body_h = body_base_y - shoulder_y
    n_band = max(0, min(3, body_h // 46))
    for k in range(n_band):
        ht = (k + 1) / (n_band + 1)
        y = int(shoulder_y + body_h * (1 - ht))
        hw = int(round(hw_cap + (hw_base - hw_cap) * (1 - ht)))
        _songyue_dwarf_eave(surf, cx, y, hw, palette, depth=2)
        _tile_hatch(surf, cx - hw + 3, y - 1, cx + hw - 3, y - 1,
                    _mortar(palette), step=5)

    # Low shrine doorway niche on the shaft — a warm lantern at night.
    if body_h > 26 and hw_base > 16:
        door_w = min(9, hw_base // 3)
        door_h = min(15, body_h // 3)
        dcx = cx + side * (hw_base // 4)
        _lit_niche(surf, dcx, body_base_y - door_h, door_w, door_h, palette)

    # ── The 180° scalloped canvas fan (crown/gutter overhang, centred on cx) ──
    rx = min(int(hw_base + 32), cx - 4, surf.get_width() - cx - 4)
    ry = crown_h - 7
    n_blades = max(5, min(9, int(rx / 10)))
    _sail_fan(surf, cx, shoulder_y, top_y, rx, ry, n_blades, palette)

    if decor:
        draw_grass_bed(surf, cx, base_y - 1, pw0 + 6, 14, palette, seed=seed)
        draw_side_shrub(surf, cx - side * (hw_base - 2), base_y - 1, palette,
                        scale=0.85)


def candidate_sail_fan_mill(surf, top_rect, bot_rect, palette, seed):
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2

    if bot_rect.height > 22:
        _draw_one(surf, bcx, bot_rect.bottom, bot_rect.y,
                  bot_rect.width, palette, seed, decor=True)

    if top_rect.height > 22:
        # Structural mirror: draw upright into a temp sized to top_rect.height,
        # flip vertically, hang from the ceiling. The fan is bilateral about cx,
        # so the flip keeps a clean fan on the hung twin.
        w = surf.get_width()
        tmp = pygame.Surface((w, top_rect.height), pygame.SRCALPHA)
        _draw_one(tmp, tcx, top_rect.height, 0,
                  top_rect.width, palette, seed, decor=False)
        flipped = pygame.transform.flip(tmp, False, True)
        surf.blit(flipped, (0, top_rect.y))


# ── Review harness ───────────────────────────────────────────────────────────

MARGIN = 70
CACHE_W = PIPE_W + MARGIN * 2
PHASE_DAY = 0.30
PHASE_NIGHT = 0.85
SEED = 12

GAP_Y, GAP_H = 205, 150
TOP_H = int(GAP_Y - GAP_H / 2)
BOT_TOP = int(GAP_Y + GAP_H / 2)
CROP_TOP, CROP_BOT = 14, 496


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _sky_ground(w, h, pal, ground_h):
    cell = pygame.Surface((w, h))
    sky_h = h - ground_h
    for y in range(sky_h):
        t = y / max(1, sky_h - 1)
        pygame.draw.line(cell, _lerp(pal['sky_top'], pal['horizon'], t), (0, y), (w, y))
    for y in range(sky_h, h):
        t = (y - sky_h) / max(1, h - sky_h)
        pygame.draw.line(cell, _lerp(pal['ground_top'], pal['ground_mid'], t),
                         (0, y), (w, y))
    return cell


def _pair_surf(pal):
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, TOP_H)
    bot_rect = pygame.Rect(MARGIN, BOT_TOP, PIPE_W, GROUND_Y - BOT_TOP)
    candidate_sail_fan_mill(surf, top_rect, bot_rect, pal, SEED)
    return surf


def _render_pair(pal):
    surf = _pair_surf(pal)
    cell = _sky_ground(CACHE_W, GROUND_Y, pal, 60)
    cell.blit(surf, (0, 0))
    guide = (255, 90, 90)
    for rim in (TOP_H, BOT_TOP):
        for x in range(0, CACHE_W, 8):
            pygame.draw.line(cell, guide, (x, rim), (x + 4, rim), 1)
    return cell.subsurface(pygame.Rect(0, CROP_TOP, CACHE_W,
                                       CROP_BOT - CROP_TOP)).copy()


def _measure_centreline(pal):
    """On the top (hung) section, how close does the body centreline reach the
    gap rim (TOP_H)? Returns px gap between the lowest filled pixel at x=cx in
    the top section and the rim (0 = touches)."""
    surf = _pair_surf(pal)
    cx = MARGIN + PIPE_W // 2
    low = -1
    for y in range(0, TOP_H + 2):
        if surf.get_at((cx, y))[3] > 50:
            low = y
    return TOP_H - low if low >= 0 else TOP_H


def _measure_fan_tip(pal):
    """Mirrored fan-tip clearance: on the hung (top) section, the lowest filled
    pixel that is NOT the central finial mast (|x-cx|>=3). Returns px gap to the
    gap rim (TOP_H) — the fan mass should clear the rim by >=5 px."""
    surf = _pair_surf(pal)
    cx = MARGIN + PIPE_W // 2
    low = -1
    for y in range(0, TOP_H + 2):
        for x in range(0, CACHE_W):
            if abs(x - cx) < 3:
                continue
            if surf.get_at((x, y))[3] > 50:
                low = y
                break
    return TOP_H - low if low >= 0 else TOP_H


def _measure_fill(pal, section_h):
    """Max vertical run (px) of ZERO-fill rows inside the PIPE_W collision
    column for a bottom-only section of the given height."""
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    candidate_sail_fan_mill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
                            bot_rect, pal, SEED)
    cx = MARGIN + PIPE_W // 2
    x0, x1 = cx - PIPE_W // 2, cx + PIPE_W // 2
    run = worst = 0
    for y in range(GROUND_Y - section_h, GROUND_Y):
        filled = any(surf.get_at((x, y))[3] > 50 for x in range(x0, x1 + 1))
        run = 0 if filled else run + 1
        worst = max(worst, run)
    return worst


def _render_feas(pal, section_h):
    head = 16
    cell_h = section_h + head + 10
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    candidate_sail_fan_mill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
                            bot_rect, pal, SEED)
    cell = _sky_ground(CACHE_W, cell_h, pal, 10)
    crop_top = GROUND_Y - section_h - head
    cell.blit(surf, (0, 0), pygame.Rect(0, crop_top, CACHE_W, cell_h))
    cx = MARGIN + PIPE_W // 2
    for ex in (cx - PIPE_W // 2, cx + PIPE_W // 2):
        pygame.draw.line(cell, (255, 60, 60), (ex, 0), (ex, cell_h), 1)
    return cell, cell_h


def _render_blackout(pal, section_h=235):
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    candidate_sail_fan_mill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
                            bot_rect, pal, SEED)
    crop_top = GROUND_Y - section_h - 12
    crop = surf.subsurface(pygame.Rect(0, crop_top, CACHE_W, section_h + 12)).copy()
    mask = pygame.mask.from_surface(crop, 60)
    return mask.to_surface(setcolor=(18, 18, 22, 255),
                           unsetcolor=(232, 232, 236, 255))


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    day = biome.palette_for_phase(PHASE_DAY)
    night = biome.palette_for_phase(PHASE_NIGHT)

    pair_day = _render_pair(day)
    pair_night = _render_pair(night)
    cl_day = _measure_centreline(day)
    cl_night = _measure_centreline(night)
    ft_day = _measure_fan_tip(day)
    ft_night = _measure_fan_tip(night)

    heights = [70, 210, 355]
    feas = [_render_feas(day, h) for h in heights]
    fills = {h: _measure_fill(day, h) for h in heights}
    blackout = _render_blackout(day)

    pad = 14
    label_h = 22
    title_h = 62
    pw, ph = pair_day.get_width(), pair_day.get_height()

    title = pygame.font.SysFont(None, 30)
    sub = pygame.font.SysFont(None, 18)
    label = pygame.font.SysFont(None, 19)

    left_w = pad + pw + pad + pw + pad
    feas_w = max(c.get_width() for c, _ in feas)
    right_w = feas_w + pad * 2
    sheet_w = left_w + right_w

    bo_w, bo_h = blackout.get_width(), blackout.get_height()
    left_h = title_h + ph + label_h + pad + bo_h + label_h + pad
    feas_col_h = title_h + sum(ch + label_h + pad for _, ch in feas) + 24
    sheet_h = max(left_h, feas_col_h) + pad

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 25, 30))

    sheet.blit(title.render("sail-fan-mill — round 1", True, (245, 240, 230)),
               (pad, 12))
    sheet.blit(sub.render("brick cone + 180 scalloped CANVAS FAN sweep: flat "
                          "base rail, ribbed sail-leaves, vermilion leech band",
                          True, (170, 172, 182)), (pad, 40))

    for i, (pair, name, cl, ft) in enumerate((
            (pair_day, f"DAY  PHASE={PHASE_DAY}", cl_day, ft_day),
            (pair_night, f"NIGHT  PHASE={PHASE_NIGHT}", cl_night, ft_night))):
        hx = pad + i * (pw + pad)
        hy = title_h
        sheet.blit(pair, (hx, hy))
        pygame.draw.rect(sheet, (60, 62, 72), (hx, hy, pw, ph), 1)
        lab = label.render(name, True, (255, 224, 150))
        sheet.blit(lab, (hx + (pw - lab.get_width()) // 2, hy + ph + 3))
        cl2 = sub.render(f"centreline gap {cl}px  ·  fan-tip clr {ft}px", True,
                         (200, 202, 212))
        sheet.blit(cl2, (hx + (pw - cl2.get_width()) // 2, hy + ph + 3 + 18))

    bx = pad
    by = title_h + ph + label_h + pad + 14
    sheet.blit(blackout, (bx, by))
    pygame.draw.rect(sheet, (60, 62, 72), (bx, by, bo_w, bo_h), 1)
    lab = label.render("BLACKOUT — 58px silhouette read", True, (255, 224, 150))
    sheet.blit(lab, (bx, by + bo_h + 3))

    fx = left_w + pad
    fy = title_h
    sheet.blit(sub.render("FEASIBILITY — collision-column fill (red = PIPE_W)",
                          True, (255, 224, 150)), (fx, fy - 22))
    for (cell, ch), h in zip(feas, heights):
        sheet.blit(cell, (fx, fy))
        pygame.draw.rect(sheet, (60, 62, 72), (fx, fy, cell.get_width(), ch), 1)
        lab = label.render(f"{h}px  ·  max empty run {fills[h]}px", True,
                           (210, 212, 222))
        sheet.blit(lab, (fx, fy + ch + 3))
        fy += ch + label_h + pad

    out = _REPO / "docs" / "pillar_landmarks" / "temple_mills" / "sail-fan-mill" / "round_1.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")
    print(f"mirror centreline->rim gap: day={cl_day}px night={cl_night}px")
    print(f"mirror fan-tip clearance: day={ft_day}px night={ft_night}px")
    print("max empty run: " + "  ".join(f"{h}px->{fills[h]}px" for h in heights))

    # PIL-sanity (no display): assert day != night on the pair surface, and no
    # pixel spikes to hot white on either palette.
    day_surf, night_surf = _pair_surf(day), _pair_surf(night)
    diff = 0
    for yy in range(0, day_surf.get_height(), 3):
        for xx in range(0, day_surf.get_width(), 3):
            cd, cn = day_surf.get_at((xx, yy)), night_surf.get_at((xx, yy))
            if cd[3] > 50 or cn[3] > 50:
                if abs(cd[0] - cn[0]) + abs(cd[1] - cn[1]) + abs(cd[2] - cn[2]) > 24:
                    diff += 1
    print(f"day!=night sampled differing pixels = {diff}")
    for pname, psurf in (("day", day_surf), ("night", night_surf)):
        hot = 0
        for yy in range(psurf.get_height()):
            for xx in range(psurf.get_width()):
                c = psurf.get_at((xx, yy))
                if c[3] > 50 and c[0] >= 250 and c[1] >= 250 and c[2] >= 250:
                    hot += 1
        print(f"{pname}: pure-white(>=250) alpha>50 pixels = {hot}")


if __name__ == "__main__":
    main()
