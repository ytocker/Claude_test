"""Terracotta Warrior + Buddha pillars — HD re-roll.

Replacement for `pillar_terracotta_buddha_variants.py` after the previous
attempt read too thin: aliased silhouettes, flat single-tone fills, no
specular, sparse iconography. This module ships the same 10 candidates
(5 warriors + 5 Buddhas) but every figure is rendered at 4x supersample
through a layered material-pass pipeline so the downscaled image at the
58-px PIPE_W slot carries sub-pixel volume, AO, rim light, specular and
photo-referenced iconography.

Pillar-pair contract is unchanged so the harness can drop it in:
    candidate_<name>(surf, top_rect, bot_rect, palette, seed)

The R11 mirror + R12 adaptive count + R13 stretch-to-fill conventions
from the pagoda module survive; `_mirror_top` is the same hook. Each
candidate's `_draw_*` figure function paints into the HD buffer, and a
single `_render_hd` helper drives the supersample / smoothscale chain.

Research is cited inline at the top of every candidate so a culturally
informed reviewer can verify the silhouette against a real museum piece.
"""
from __future__ import annotations

import math
import random

import pygame

from game.pillar_variants import (
    draw_grass_bed,
    draw_flower_bed,
)


# Supersample factor — 4x is the sweet spot between detail headroom and
# memory cost. Each pillar's HD buffer is ~232x500 px which keeps the
# per-frame smoothscale under 1 ms on the target hardware.
SS = 4


# ── Colour math ────────────────────────────────────────────────────────────

def _mix(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def _shade(c, d):
    return (max(0, min(255, c[0] + d)),
            max(0, min(255, c[1] + d)),
            max(0, min(255, c[2] + d)))


def _with_alpha(c, a):
    return (c[0], c[1], c[2], a)


def _is_dark_sky(palette):
    top = palette['sky_top']
    return (top[0] + top[1] + top[2]) / 3.0 < 110


def _is_warming_sky(palette):
    top = palette['sky_top']
    avg = (top[0] + top[1] + top[2]) / 3.0
    return 60 <= avg < 110


# ── Material ramps ────────────────────────────────────────────────────────
#
# Each ramp is a key-addressable dict of 5-8 archetype RGB targets. The
# `_palette_blend` step mixes those archetypes against the live biome
# palette so dawn/dusk/night retints sweep through every material at the
# same strength — bronze stays bronze at noon, bronze stays bronze at
# night, but biome shadow tints carry. The mix anchors are picked so the
# canonical hue dominates at noon and the biome shadow dominates at night.

_CLAY_RAMP = {
    # Excavated Qin terracotta — base fired-clay brown body, warm undertone
    # at the lit upper-left, cool shadow in the recesses. Polychrome
    # fragments are kept low-saturation: most pigment has flaked off but
    # protected recesses keep faint vermilion / malachite / ochre / white.
    'body':       (158, 102, 72),
    'lit':        (208, 152, 110),
    'mid':        (180, 124, 88),
    'shadow':     (84, 50, 32),
    'deep':       (52, 30, 18),
    'vermilion':  (172, 60, 46),
    'malachite':  (118, 148, 102),
    'ochre':      (212, 162, 70),
    'white':      (228, 218, 196),
    'specular':   (245, 220, 188),
}

_BRONZE_RAMP = {
    # Patinated outdoor bronze (Tian Tan archetype) — warm bronze body,
    # verdigris in deepest recess only (so the figure doesn't flip green),
    # dark patina under chin/armpit, gold-leaf wear on raised edges,
    # oxidation runoff drips on robe folds, true-white specular at the
    # brow and the lotus rim.
    'body':       (180, 130, 70),
    'lit':        (228, 188, 118),
    'mid':        (200, 150, 86),
    'shadow':     (118, 86, 48),
    'patina':     (62, 46, 32),
    'verdigris':  (78, 132, 108),
    'runoff':     (54, 70, 58),
    'gold':       (236, 196, 110),
    'specular':   (252, 240, 210),
}

_GILT_RAMP = {
    # Gilt-bronze (Maitreya / Budai archetype) — bright saturated gold
    # body with visible red-lacquer wear cracks. Warmer than patinated
    # bronze; sits between bronze and gold-leaf in saturation.
    'body':       (228, 176, 56),
    'lit':        (252, 232, 138),
    'mid':        (238, 196, 94),
    'shadow':     (168, 116, 38),
    'deep':       (98, 64, 22),
    'lacquer':    (148, 48, 32),
    'patina':     (84, 68, 28),
    'specular':   (255, 250, 224),
}

_SANDSTONE_RAMP = {
    # Cliff-carved red sandstone (Leshan + Yungang archetype) — warm tan
    # body with cool shadow, algae green only on permanently wet weather-
    # faces, white salt efflorescence in micro-pits, dark vertical crack
    # lines + visible bedding-plane strata.
    'body':       (188, 142, 96),
    'lit':        (228, 188, 142),
    'mid':        (208, 162, 114),
    'shadow':     (108, 74, 50),
    'deep':       (72, 48, 32),
    'algae':      (102, 124, 86),
    'salt':       (232, 222, 204),
    'crack':      (52, 32, 22),
}

_PORCELAIN_RAMP = {
    # Dehua blanc-de-chine porcelain (Guanyin archetype) — cool-cast
    # off-white body with a warm rim that cues the subsurface scatter on
    # a real porcelain edge. True-white specular at cheekbone / shoulder,
    # visible hairline crackle, cobalt-fire dots at eye / hair / diadem,
    # faint gilt brushwork on robe borders.
    'body':       (244, 246, 248),
    'lit':        (255, 255, 255),
    'mid':        (212, 218, 226),
    'shadow':     (158, 168, 184),
    'warm_rim':   (236, 220, 196),
    'cobalt':     (60, 86, 142),
    'gilt':       (218, 176, 92),
    'specular':   (255, 255, 255),
}

_GOLD_LEAF_RAMP = {
    # Gold-leaf gilded lacquer (cliff-niche reclining figure) — true
    # bright gold body with warm mid + warm shadow, visible wear cracks
    # revealing the red lacquer underbase, bright specular at brow /
    # shoulder / knee / sole.
    'body':       (248, 204, 84),
    'lit':        (255, 240, 168),
    'mid':        (240, 188, 72),
    'shadow':     (180, 132, 36),
    'deep':       (108, 76, 18),
    'lacquer':    (156, 52, 30),
    'specular':   (255, 252, 232),
}


def _palette_blend(ramp, palette):
    """Anchor a material ramp's archetype hues onto the live biome.

    Each key is mixed against the canonical biome key it belongs to
    (lit → stone_light, shadow → stone_dark, etc.) so day/night still
    re-tints the material, but the canonical hue still dominates so a
    bronze never reads as a grey stone at night.
    """
    sl = palette['stone_light']
    sm = palette['stone_mid']
    sd = palette['stone_dark']
    sa = palette['stone_accent']
    out = {}
    for k, target in ramp.items():
        if k in ('lit', 'specular', 'white', 'salt', 'gold', 'gilt'):
            anchor, t = sl, 0.72
        elif k in ('body', 'mid', 'warm_rim'):
            anchor, t = sm, 0.74
        elif k in ('shadow', 'patina', 'verdigris', 'runoff',
                   'algae', 'crack', 'deep', 'lacquer'):
            anchor, t = sd, 0.80
        elif k in ('vermilion', 'malachite', 'ochre', 'cobalt'):
            anchor, t = sa, 0.62
        else:
            anchor, t = sm, 0.70
        out[k] = _mix(anchor, target, t)
    return out


# ── Supersample render driver ─────────────────────────────────────────────

def _render_hd(figure_fn, surf, rect, palette, seed):
    """Allocate an SS-times-larger SRCALPHA buffer, run `figure_fn` into
    it at high resolution, then `smoothscale` it down onto `surf`.

    `figure_fn(buf, cx, base_y, top_y, palette, seed)` paints the figure
    bottom-anchored at `base_y` with the head ceiling at `top_y`, in the
    HD buffer's local coordinates. Returns nothing; mutates `surf`.
    """
    if rect.w < 4 or rect.h < 4:
        return
    bw, bh = rect.w * SS, rect.h * SS
    buf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    figure_fn(buf, bw // 2, bh - 1, 0, palette, seed)
    scaled = pygame.transform.smoothscale(buf, (rect.w, rect.h))
    surf.blit(scaled, (rect.x, rect.y))


# ── Anti-aliased primitive helpers (HD-space) ─────────────────────────────

def _aa_polyline(surf, color, points, closed=False, width=1):
    if len(points) < 2:
        return
    if width <= 1:
        try:
            pygame.draw.aalines(surf, color, closed, points)
        except (ValueError, TypeError):
            pygame.draw.lines(surf, color, closed, points, 1)
    else:
        pygame.draw.lines(surf, color, closed, points, width)


def _gradient_fill_rect(buf, rect, top_col, bot_col):
    """Subtle vertical 2-stop gradient inside a rect — used to cue body
    volume against directional light. Runs at HD resolution so the
    downscaled result has clean sub-pixel banding."""
    if rect.w < 2 or rect.h < 2:
        return
    for i in range(rect.h):
        t = i / max(1, rect.h - 1)
        col = _mix(top_col, bot_col, t)
        pygame.draw.line(buf, col,
                         (rect.x, rect.y + i),
                         (rect.right - 1, rect.y + i))


def _radial_gradient_circle(buf, cx, cy, r, center_col, edge_col):
    """Concentric-ring radial fill — for halos, lit hot-spots, lotus seed
    cups. Drawn at HD scale so the gradient banding smooths away."""
    if r < 2:
        return
    for k in range(r, 0, -1):
        t = 1.0 - k / r
        col = _mix(edge_col, center_col, t)
        pygame.draw.circle(buf, col, (cx, cy), k)


def _soft_glow(buf, cx, cy, r, rgb, peak_alpha):
    """Additive amber glow under haloed deities. Three concentric rings
    with falling alpha so the edge stays soft when downscaled."""
    if r < 4:
        return
    sz = r * 2 + 8
    g = pygame.Surface((sz, sz), pygame.SRCALPHA)
    rings = (peak_alpha, peak_alpha // 2, peak_alpha // 4)
    for k, a in enumerate(rings):
        kr = r - k * (r // 4)
        if kr > 0:
            pygame.draw.circle(g, (*rgb, a), (sz // 2, sz // 2), kr)
    buf.blit(g, (cx - sz // 2, cy - sz // 2),
             special_flags=pygame.BLEND_RGBA_ADD)


# ── Per-candidate cache ───────────────────────────────────────────────────
#
# Same cache pattern as the failed attempt — the HD pass is expensive
# enough that re-rendering every frame at runtime would tank the FPS.

_PILLAR_CACHE: dict = {}


def _palette_key(palette):
    return (palette['sky_top'], palette['stone_dark'],
            palette['stone_mid'], palette['stone_light'],
            palette['stone_accent'])


def _cached_draw(name, draw_fn, surf, top_rect, bot_rect, palette, seed):
    key = (name, seed, _palette_key(palette),
           top_rect.x, top_rect.y, top_rect.w, top_rect.h,
           bot_rect.x, bot_rect.y, bot_rect.w, bot_rect.h)
    bitmap = _PILLAR_CACHE.get(key)
    if bitmap is None:
        bitmap = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        draw_fn(bitmap, top_rect, bot_rect, palette, seed)
        _PILLAR_CACHE[key] = bitmap
    surf.blit(bitmap, (0, 0))


def _mirror_top(surf, top_rect, body_h_natural, hd_draw_fn, *,
                mirror_strategy="flip"):
    """R11 mirror + R12 adaptive + R13 stretch — same contract as the
    previous attempt but the HD buffer lives at `top_rect.w * SS` width.

    `hd_draw_fn(buf, cx, base_y, top_y, palette, seed)` paints the figure
    inside the HD-space buffer; this helper then smoothscales + flips
    according to `mirror_strategy`."""
    if top_rect.height < 50:
        return
    avail = top_rect.height
    ratio = avail / max(1, body_h_natural)
    # Same clamp band as the previous attempt — tall slots fall back to
    # the natural height rather than stretch the iconography past its
    # recognisable proportions.
    if 0.7 <= ratio <= 1.25:
        tmp_h = avail
    else:
        tmp_h = body_h_natural
    bw = top_rect.width * SS
    bh = tmp_h * SS
    buf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    hd_draw_fn(buf, bw // 2, bh - 1, 0)
    scaled = pygame.transform.smoothscale(buf, (top_rect.width, tmp_h))
    tcx = top_rect.x + top_rect.width // 2
    if mirror_strategy == "redraw":
        surf.blit(scaled, (tcx - top_rect.width // 2,
                           top_rect.bottom - tmp_h))
    elif mirror_strategy == "flip_horizontal":
        flipped = pygame.transform.flip(scaled, True, True)
        surf.blit(flipped, (tcx - top_rect.width // 2, top_rect.y))
    else:
        flipped = pygame.transform.flip(scaled, False, True)
        surf.blit(flipped, (tcx - top_rect.width // 2, top_rect.y))


# ── Layered pass primitives (run inside the HD buffer) ────────────────────
#
# Every figure is built as: silhouette → body base → AO → mid-tones →
# rim light → specular → iconographic details → material accents. The
# helpers below are the small reusable atoms each pass calls.


def _ao_under(buf, cx, cy, w, h, shadow):
    """Cast a soft AO oval under chin / hem / armpit recess. Drawn as
    three nested ellipses with falling alpha so it reads as a soft
    ambient occlusion at downscale rather than a hard band."""
    if w < 4 or h < 2:
        return
    g = pygame.Surface((w + 4, h + 4), pygame.SRCALPHA)
    for k, a in enumerate((110, 80, 50)):
        pygame.draw.ellipse(g, (*shadow, a),
                            (k * 2, k, w - k * 4, h - k * 2))
    buf.blit(g, (cx - (w + 4) // 2, cy - (h + 4) // 2))


def _rim_light(buf, points, lit, width=None):
    """Bright upper-left edge highlight along a polyline. The implied
    key light sits top-left, ~30 deg above the figure — every figure
    consumes the SAME key direction so the family reads coherent."""
    if width is None:
        width = max(2, SS // 2)
    if len(points) >= 2:
        pygame.draw.lines(buf, lit, False, points, width)


def _specular_dot(buf, x, y, r, spec):
    """True-bright specular highlight on a curved metal/porcelain face.
    Three concentric circles so the dot has a hot core and a soft fall
    off when downscaled. Used sparingly — only on the brightest few
    points per figure so the lighting reads believable."""
    if r < 1:
        return
    pygame.draw.circle(buf, _shade(spec, -30), (x, y), r + 1)
    pygame.draw.circle(buf, spec, (x, y), r)
    pygame.draw.circle(buf, (255, 255, 255), (x, y), max(1, r // 2))


def _crackle_lines(buf, rect, color, *, density=6, seed=0):
    """Porcelain hairline crackle / sandstone erosion crack network. A
    short branching tree of dim sub-pixel lines layered on top of the
    body fill — invisible at noon, visible at thumbnail because the
    smoothscale preserves the dim banding."""
    if rect.w < 4 or rect.h < 4:
        return
    rng = random.Random(seed)
    for _ in range(density):
        x = rng.randint(rect.x, rect.right - 1)
        y = rng.randint(rect.y, rect.bottom - 1)
        ang = rng.uniform(0, math.tau)
        ln = rng.randint(SS, SS * 4)
        x2 = int(x + math.cos(ang) * ln)
        y2 = int(y + math.sin(ang) * ln)
        pygame.draw.line(buf, color, (x, y), (x2, y2), 1)
        # one short branch off the main crack
        ba = ang + rng.uniform(-1.1, 1.1)
        bl = ln // 2
        bx = int(x + math.cos(ang) * (ln // 2))
        by = int(y + math.sin(ang) * (ln // 2))
        pygame.draw.line(buf, color,
                         (bx, by),
                         (int(bx + math.cos(ba) * bl),
                          int(by + math.sin(ba) * bl)), 1)


def _clay_pigment_patch(buf, cx, cy, w, h, pigment, alpha=110):
    """Fragmentary surviving polychrome patch on excavated clay — a soft
    blob of one canonical Qin pigment (vermilion/malachite/ochre/white).
    Always semi-transparent so the underlying clay shows through, never
    a full coat. Matches the protected-recess survival pattern from
    excavation photos."""
    if w < 2 or h < 2:
        return
    g = pygame.Surface((w, h), pygame.SRCALPHA)
    for k in range(3):
        a = alpha - k * 30
        if a > 0:
            pygame.draw.ellipse(g, (*pigment, a),
                                (k, k, w - k * 2, h - k * 2))
    buf.blit(g, (cx - w // 2, cy - h // 2))


def _verdigris_run(buf, x_top, y_top, length, color, *, drips=4):
    """Vertical oxidation runoff down a bronze fold or robe drape — a
    short tapered ribbon that fades toward the bottom. Only drawn on
    the patinated-bronze ramp."""
    if length < 2:
        return
    g = pygame.Surface((SS * 2, length), pygame.SRCALPHA)
    for i in range(length):
        t = i / length
        a = int(120 * (1 - t * t))
        pygame.draw.line(g, (*color, a),
                         (SS, i), (SS, i), 1)
    buf.blit(g, (x_top - SS, y_top))
    # A few wandering droplet trails so the run reads as fluid, not a
    # printed line.
    for k in range(drips):
        off = (k - drips // 2) * SS
        droplet_y = y_top + length - k * (length // max(1, drips))
        pygame.draw.line(buf, color,
                         (x_top + off, droplet_y),
                         (x_top + off, droplet_y + SS), 1)


def _strata_band(buf, rect, body, top_edge, base_crack):
    """One sedimentary strata band on a sandstone cliff face — flat
    body, lit top edge, dark bedding-plane crack at the base. Stacked
    bottom-up to build a cliff."""
    pygame.draw.rect(buf, body, rect)
    pygame.draw.line(buf, top_edge,
                     (rect.x, rect.y), (rect.right - 1, rect.y),
                     max(1, SS // 3))
    pygame.draw.line(buf, base_crack,
                     (rect.x, rect.bottom - 1),
                     (rect.right - 1, rect.bottom - 1),
                     max(1, SS // 4))


def _gilt_wear_crack(buf, x1, y1, x2, y2, lacquer):
    """A short crack in a gilt-bronze surface where the gold leaf has
    worn away revealing the red lacquer underbase. Used on Maitreya +
    niche-reclining Buddha so the gilding reads aged rather than
    factory-fresh."""
    pygame.draw.line(buf, lacquer, (x1, y1), (x2, y2), max(1, SS // 3))


# ── Plinth helpers (HD-space) ─────────────────────────────────────────────

def _draw_clay_plinth_hd(buf, cx, base_y, w, palette, *, h=None):
    """Packed Qin-tomb earth plinth under a warrior — three-stop
    vertical block: dark overhang base, mid body, lit top edge."""
    ramp = _palette_blend(_CLAY_RAMP, palette)
    if h is None:
        h = 9 * SS
    rect = pygame.Rect(cx - w // 2, base_y - h, w, h)
    _gradient_fill_rect(buf, rect, ramp['mid'], ramp['shadow'])
    # AO band along the front face base — the plinth meets ground here.
    pygame.draw.rect(buf, ramp['deep'],
                     (rect.x - SS, rect.bottom - SS,
                      rect.w + SS * 2, SS))
    # Lit top edge — strong key light hits the top facet flat-on.
    pygame.draw.rect(buf, ramp['lit'],
                     (rect.x, rect.y, rect.w, max(1, SS // 2)))
    # Stamped soil-pattern flecks across the top — visual texture so the
    # plinth doesn't read as a flat slab at thumbnail.
    rng = random.Random(cx + base_y)
    for _ in range(8):
        fx = rng.randint(rect.x + SS, rect.right - SS)
        fy = rect.y + rng.randint(SS, max(SS + 1, h // 3))
        pygame.draw.line(buf, _shade(ramp['shadow'], -10),
                         (fx, fy), (fx + SS // 2, fy), 1)


def _draw_lotus_throne_hd(buf, cx, base_y, w, palette, *, h=None, n=9,
                          petal_color=None, edge_color=None,
                          rim_color=None, gilt_color=None):
    """Lotus throne — half-fan of overlapping petals with gilt-edged
    tips. Used by Tian Tan, Maitreya, Guanyin. Petals share the figure's
    own material palette so the figure + throne read as one piece."""
    if h is None:
        h = 14 * SS
    if petal_color is None:
        petal_color = _mix(palette['stone_light'], (242, 188, 196), 0.62)
    if edge_color is None:
        edge_color = _shade(petal_color, -55)
    if rim_color is None:
        rim_color = _shade(petal_color, 50)
    if gilt_color is None:
        gilt_color = _mix(palette['stone_accent'], (236, 196, 110), 0.78)
    base_rect = pygame.Rect(cx - w // 2, base_y - h // 2, w, h // 2 + SS)
    pygame.draw.ellipse(buf, _shade(edge_color, -20), base_rect)
    pygame.draw.ellipse(buf, edge_color, base_rect.inflate(-SS, -SS))
    radius = w // 2 - SS
    cy = base_y - h // 2
    for i in range(n):
        t = i / max(1, n - 1)
        ang = math.pi + t * math.pi
        tip_x = cx + math.cos(ang) * radius
        tip_y = cy + math.sin(ang) * (h // 2 + SS // 2)
        sl_ang = ang - 0.22
        sr_ang = ang + 0.22
        sl_x = cx + math.cos(sl_ang) * radius * 0.55
        sl_y = cy + math.sin(sl_ang) * (h // 2 + SS // 2) * 0.55
        sr_x = cx + math.cos(sr_ang) * radius * 0.55
        sr_y = cy + math.sin(sr_ang) * (h // 2 + SS // 2) * 0.55
        petal = [(int(cx), int(cy)),
                 (int(sl_x), int(sl_y)),
                 (int(tip_x), int(tip_y)),
                 (int(sr_x), int(sr_y))]
        pygame.draw.polygon(buf, edge_color, petal)
        inner = [(int(cx), int(cy)),
                 (int(sl_x + (tip_x - sl_x) * 0.22),
                  int(sl_y + (tip_y - sl_y) * 0.22)),
                 (int(tip_x), int(tip_y)),
                 (int(sr_x + (tip_x - sr_x) * 0.22),
                  int(sr_y + (tip_y - sr_y) * 0.22))]
        pygame.draw.polygon(buf, petal_color, inner)
        # Gilt rim along the tip — the canonical lotus-throne cue.
        pygame.draw.line(buf, gilt_color,
                         (int(tip_x), int(tip_y)),
                         (int((sl_x + tip_x) / 2),
                          int((sl_y + tip_y) / 2)),
                         max(1, SS // 3))
        pygame.draw.line(buf, gilt_color,
                         (int(tip_x), int(tip_y)),
                         (int((sr_x + tip_x) / 2),
                          int((sr_y + tip_y) / 2)),
                         max(1, SS // 3))
        # Hot specular at the tip — a one-pixel highlight that survives
        # the downscale.
        _specular_dot(buf, int(tip_x), int(tip_y), max(1, SS // 4),
                      rim_color)


def _draw_cliff_niche_hd(buf, cx, base_y, w, h, palette,
                         *, inflate_x=None, inflate_y=None):
    """Sandstone cliff face with a niche carved INTO it. The cliff is
    drawn first as 6 strata bands of varying height + tone, then the
    arched niche is excavated through them so the Buddha sits IN the
    rock and the strata edges bookmark the left + right niche walls."""
    if w < 14 or h < 24:
        return
    ramp = _palette_blend(_SANDSTONE_RAMP, palette)
    if inflate_x is None:
        inflate_x = 12 * SS
    if inflate_y is None:
        inflate_y = 10 * SS
    rect = pygame.Rect(cx - w // 2, base_y - h, w, h)
    outer = rect.inflate(inflate_x, inflate_y)

    band_seeds = (0.22, 0.13, 0.30, 0.10, 0.18, 0.25, 0.14)
    norm = sum(band_seeds)
    y = outer.bottom
    bands = []
    for sb in band_seeds:
        bh = max(SS * 2, int(outer.height * (sb / norm)))
        bands.append((y - bh, bh))
        y -= bh
    if y > outer.y:
        last_y, last_h = bands[-1]
        bands[-1] = (outer.y, last_h + (last_y - outer.y))

    for i, (by, bh) in enumerate(bands):
        t = i / max(1, len(bands) - 1)
        body = _mix(ramp['mid'], ramp['shadow'], t * 0.55)
        top_edge = _mix(ramp['lit'], ramp['mid'], t * 0.45)
        crack = _shade(body, -28)
        _strata_band(buf, pygame.Rect(outer.x, by, outer.width, bh),
                     body, top_edge, crack)
        # Erosion pits along each band — small darker chips of stone.
        for k in range(4):
            px = outer.x + SS + ((i * 13 + k * 21) % (outer.width - SS * 2))
            py = by + max(SS, bh // 2) + ((k + i) % max(1, bh // 3))
            pygame.draw.circle(buf, _shade(body, -22), (px, py), 1)

    # Algae streaks on the lower bands — weather-face wetting cue.
    rng = random.Random(cx + base_y + w)
    for _ in range(5):
        sx = rng.randint(outer.x + SS, outer.right - SS)
        sy = rng.randint(outer.bottom - outer.height // 3, outer.bottom - SS)
        slen = rng.randint(SS * 2, SS * 6)
        for dy in range(slen):
            a = int(120 * (1 - dy / slen))
            buf.set_at((sx, sy + dy),
                       (*ramp['algae'], a))
    # Salt efflorescence streaks on the upper third — white wash from
    # rainwater percolation.
    for _ in range(4):
        sx = rng.randint(outer.x + SS, outer.right - SS)
        sy = rng.randint(outer.y + SS, outer.y + outer.height // 3)
        slen = rng.randint(SS, SS * 4)
        for dy in range(slen):
            a = int(95 * (1 - dy / slen))
            buf.set_at((sx, sy + dy), (*ramp['salt'], a))

    # Niche cut through the strata — dark inner recess with a rounded
    # arch top. Drawn LAST so it overrides the strata fills inside the
    # niche bounds, leaving the strata edges visible on the outer walls.
    arch_h = max(SS * 6, h // 4)
    inner = _shade(ramp['deep'], -10)
    pygame.draw.rect(buf, inner,
                     (rect.x, rect.y + arch_h, rect.w, rect.h - arch_h))
    pygame.draw.ellipse(buf, inner,
                        (rect.x, rect.y, rect.w, arch_h * 2))
    # Dark rim along the niche wall — carved-edge depth cue.
    pygame.draw.line(buf, _shade(inner, -18),
                     (rect.x, rect.y + arch_h),
                     (rect.x, rect.bottom - 1), max(1, SS // 3))
    pygame.draw.line(buf, _shade(inner, -18),
                     (rect.right - 1, rect.y + arch_h),
                     (rect.right - 1, rect.bottom - 1), max(1, SS // 3))
    # Lit hit along the upper-inside arch (light enters from above).
    pygame.draw.arc(buf, _mix(ramp['mid'], ramp['lit'], 0.35),
                    (rect.x + SS, rect.y + SS,
                     rect.w - SS * 2, arch_h * 2 - SS * 2),
                    math.pi * 0.15, math.pi * 0.85, max(1, SS // 3))


def _draw_buddha_head_hd(buf, cx, top_y, w, h, palette, ramp,
                         *, ushnisha=True, snail_curls=True,
                         urna=True, half_eyes=True,
                         long_ears=True, halo_radius=0,
                         smiling=False):
    """Standard Buddha head — egg-shape body, snail-shell hair curls,
    optional ushnisha cranial bump, half-closed contemplative eyes,
    urna dot, long lobed ears. The head is the same archetype across
    Tian Tan / Maitreya / Leshan / Reclining / Niche — variation comes
    through the surface material ramp."""
    head_rect = pygame.Rect(cx - w // 2, top_y, w, h)

    # Halo behind head — drawn FIRST so the head sits on top.
    if halo_radius > 0:
        halo_rim = _mix(palette['stone_accent'], (255, 220, 130), 0.78)
        glow_alpha = 130 if _is_dark_sky(palette) else 70
        _soft_glow(buf, cx, top_y + h // 2, halo_radius,
                   halo_rim, glow_alpha)
        # Radial petal rays inside the halo — only on lit-halo deities.
        n_rays = 12
        for k in range(n_rays):
            ang = k * math.tau / n_rays
            x1 = cx + math.cos(ang) * (halo_radius - SS * 2)
            y1 = top_y + h // 2 + math.sin(ang) * (halo_radius - SS * 2)
            x2 = cx + math.cos(ang) * halo_radius
            y2 = top_y + h // 2 + math.sin(ang) * halo_radius
            pygame.draw.line(buf, _shade(halo_rim, 30),
                             (int(x1), int(y1)),
                             (int(x2), int(y2)), max(1, SS // 3))

    # Head body — gradient fill, lit upper-left, shadow lower-right.
    pygame.draw.ellipse(buf, ramp['shadow'], head_rect)
    inner_rect = head_rect.inflate(-SS, -SS)
    pygame.draw.ellipse(buf, ramp['body'], inner_rect)
    # Cheek lit — soft gradient ellipse on the upper-left.
    cheek_rect = pygame.Rect(head_rect.x + SS,
                             head_rect.y + h // 4,
                             w // 2, h // 2)
    g = pygame.Surface((cheek_rect.w, cheek_rect.h), pygame.SRCALPHA)
    for k in range(cheek_rect.w // 2, 0, -1):
        a = int(95 * (k / (cheek_rect.w / 2)))
        pygame.draw.ellipse(g, (*ramp['lit'], a),
                            ((cheek_rect.w - k * 2) // 2,
                             (cheek_rect.h - k) // 2,
                             k * 2, k))
    buf.blit(g, cheek_rect.topleft)
    # AO under chin — small dark band where the chin meets the neck.
    _ao_under(buf, cx, head_rect.bottom - SS,
              int(w * 0.7), SS * 3, ramp['shadow'])

    # Snail-shell hair curls — small filled circles tiled across the
    # crown.  The canonical Buddha-image hair pattern; visible at scale.
    if snail_curls:
        curl_r = max(1, int(w * 0.07))
        rows = 3
        cols = int(w / (curl_r * 2 + 1))
        hair_top = head_rect.y + SS
        for r in range(rows):
            for c in range(cols):
                cxk = head_rect.x + curl_r + c * (curl_r * 2 + 1)
                cyk = hair_top + r * (curl_r * 2 - 1)
                # Skip the curls outside the egg's elliptic clip.
                dx = (cxk - cx) / (w / 2)
                dy = (cyk - (top_y + h / 2)) / (h / 2)
                if dx * dx + dy * dy > 0.95:
                    continue
                pygame.draw.circle(buf, ramp['shadow'],
                                   (cxk, cyk), curl_r)
                pygame.draw.circle(buf, _shade(ramp['shadow'], 25),
                                   (cxk - max(1, curl_r // 3),
                                    cyk - max(1, curl_r // 3)),
                                   max(1, curl_r // 2))

    # Ushnisha cranial bump — the canonical wisdom-mound on top of head.
    if ushnisha:
        bump_w = int(w * 0.32)
        bump_h = int(h * 0.16)
        bump_rect = pygame.Rect(cx - bump_w // 2,
                                top_y - bump_h + SS,
                                bump_w, bump_h * 2)
        pygame.draw.ellipse(buf, ramp['shadow'], bump_rect)
        pygame.draw.ellipse(buf, ramp['body'],
                            bump_rect.inflate(-SS, -SS))
        # Wisdom-flame tip — a small candle-flame on top of the bump.
        flame_color = _mix(palette['stone_accent'], (255, 196, 88), 0.78)
        pygame.draw.polygon(buf, flame_color, [
            (cx, top_y - bump_h - SS * 2),
            (cx - SS, top_y - bump_h + SS // 2),
            (cx + SS, top_y - bump_h + SS // 2),
        ])
        _specular_dot(buf, cx, top_y - bump_h + SS // 2,
                      max(1, SS // 3), ramp.get('specular', ramp['lit']))

    # Long ear lobes — large U-shapes on each side of the head.
    if long_ears:
        ear_w = max(SS, int(w * 0.10))
        ear_h = max(SS * 2, int(h * 0.35))
        for side in (-1, 1):
            ex = cx + side * (w // 2 - SS // 2)
            ey = top_y + h // 3
            pygame.draw.ellipse(buf, ramp['shadow'],
                                (ex - ear_w // 2, ey,
                                 ear_w, ear_h))
            pygame.draw.ellipse(buf, ramp['body'],
                                (ex - ear_w // 2 + SS // 2,
                                 ey + SS // 2,
                                 ear_w - SS, ear_h - SS))
            # Lobe dimple — the lobe interior recess.
            pygame.draw.ellipse(buf, ramp['shadow'],
                                (ex - ear_w // 3,
                                 ey + ear_h * 2 // 3,
                                 ear_w // 2, ear_h // 3))

    # Eye line — two slim closed-eye slashes if the face is meditating,
    # otherwise tiny crescents.
    eye_y = top_y + int(h * 0.50)
    eye_dx = int(w * 0.18)
    if half_eyes:
        for side in (-1, 1):
            ex = cx + side * eye_dx
            pygame.draw.line(buf, ramp['shadow'],
                             (ex - SS, eye_y),
                             (ex + SS, eye_y), max(1, SS // 2))
            if 'cobalt' in ramp:
                # Cobalt-fired eye dots — Dehua porcelain hot accent.
                buf.set_at((ex, eye_y), ramp['cobalt'])
    if smiling:
        # Round, laughing crescent eyes for Budai.
        for side in (-1, 1):
            ex = cx + side * eye_dx
            pygame.draw.arc(buf, ramp['shadow'],
                            (ex - SS, eye_y - SS, SS * 2, SS * 2),
                            math.pi * 0.15, math.pi * 0.85, max(1, SS // 2))

    # Urna dot between brows — small white pearl, the canonical wisdom
    # mark.
    if urna:
        ux = cx
        uy = top_y + int(h * 0.36)
        pygame.draw.circle(buf, ramp.get('specular', ramp['lit']),
                           (ux, uy), max(1, SS // 3))

    # Mouth — soft smile line.
    if smiling:
        mouth_y = top_y + int(h * 0.74)
        pygame.draw.arc(buf, ramp['shadow'],
                        (cx - int(w * 0.20), mouth_y - SS,
                         int(w * 0.40), SS * 4),
                        math.pi * 1.05, math.pi * 1.95, max(1, SS // 2))
    else:
        mouth_y = top_y + int(h * 0.74)
        pygame.draw.line(buf, ramp['shadow'],
                         (cx - SS * 2, mouth_y),
                         (cx + SS * 2, mouth_y), max(1, SS // 2))


# ── Warrior shared primitives ─────────────────────────────────────────────


def _draw_warrior_head_hd(buf, cx, top_y, w, h, palette, ramp,
                          *, beard=True, headgear='bun'):
    """Standard Qin-warrior head — egg shape, mustache + beard, eyes,
    + a parametric headgear: 'bun' (rear topknot), 'side_bun' (right-
    of-centre bun for archers), 'cavalry_cap' (small leather round
    cap), 'trapezoid_cap' (long charioteer cap), 'fishtail_crown'
    (officer guan)."""
    head_rect = pygame.Rect(cx - w // 2, top_y, w, h)
    pygame.draw.ellipse(buf, ramp['shadow'], head_rect)
    pygame.draw.ellipse(buf, ramp['body'], head_rect.inflate(-SS, -SS))
    # Lit cheek — warm highlight gradient on the upper-left.
    g = pygame.Surface((w // 2, h // 2), pygame.SRCALPHA)
    for k in range(w // 4, 0, -1):
        a = int(110 * (k / (w / 4)))
        pygame.draw.ellipse(g, (*ramp['lit'], a),
                            ((w // 2 - k * 2) // 2,
                             (h // 2 - k) // 2,
                             k * 2, k))
    buf.blit(g, (head_rect.x + SS, head_rect.y + h // 4))
    # AO under chin.
    _ao_under(buf, cx, head_rect.bottom - SS // 2,
              int(w * 0.7), SS * 3, ramp['shadow'])

    # Eye line — Qin-warrior eyes drawn forward-staring + intent.
    eye_y = top_y + int(h * 0.45)
    eye_dx = int(w * 0.20)
    for side in (-1, 1):
        ex = cx + side * eye_dx
        pygame.draw.line(buf, ramp['shadow'],
                         (ex - SS, eye_y),
                         (ex + SS, eye_y), max(1, SS // 2))
        # Tiny pupil dot — clay-fired warrior gaze.
        buf.set_at((ex, eye_y), ramp['deep'])

    # Brow line.
    pygame.draw.line(buf, _shade(ramp['shadow'], -20),
                     (cx - int(w * 0.28), eye_y - SS),
                     (cx - int(w * 0.05), eye_y - SS - SS // 2),
                     max(1, SS // 3))
    pygame.draw.line(buf, _shade(ramp['shadow'], -20),
                     (cx + int(w * 0.28), eye_y - SS),
                     (cx + int(w * 0.05), eye_y - SS - SS // 2),
                     max(1, SS // 3))

    # Nose line.
    nose_y = top_y + int(h * 0.62)
    pygame.draw.line(buf, _shade(ramp['shadow'], -10),
                     (cx, eye_y + SS), (cx - SS // 2, nose_y),
                     max(1, SS // 3))

    # Mustache + beard.
    if beard:
        mustache_y = top_y + int(h * 0.72)
        for side in (-1, 1):
            pygame.draw.line(buf, ramp['deep'],
                             (cx + side * SS, mustache_y),
                             (cx + side * int(w * 0.30),
                              mustache_y + SS // 2), max(1, SS // 2))
        beard_y = top_y + int(h * 0.85)
        pygame.draw.polygon(buf, ramp['deep'], [
            (cx - int(w * 0.22), beard_y),
            (cx + int(w * 0.22), beard_y),
            (cx + int(w * 0.12), head_rect.bottom + SS),
            (cx - int(w * 0.12), head_rect.bottom + SS),
        ])
        pygame.draw.polygon(buf, _shade(ramp['shadow'], -10), [
            (cx - int(w * 0.18), beard_y + SS // 2),
            (cx + int(w * 0.18), beard_y + SS // 2),
            (cx + int(w * 0.10), head_rect.bottom + SS // 2),
            (cx - int(w * 0.10), head_rect.bottom + SS // 2),
        ])

    # Headgear ── varies per warrior class.
    if headgear == 'bun':
        # Rear topknot bun — centred behind the head, leaning slightly
        # forward (the canonical generic warrior bun).
        bun_w = int(w * 0.42)
        bun_h = int(h * 0.32)
        bun_rect = pygame.Rect(cx - bun_w // 2,
                               top_y - bun_h // 2, bun_w, bun_h)
        pygame.draw.ellipse(buf, ramp['shadow'], bun_rect)
        pygame.draw.ellipse(buf, ramp['body'],
                            bun_rect.inflate(-SS, -SS))
        # Tie ribbon at base — ochre band.
        ochre = ramp.get('ochre',
                         _mix(palette['stone_accent'], (212, 162, 70), 0.68))
        pygame.draw.rect(buf, ochre,
                         (cx - bun_w // 3, top_y - SS, bun_w * 2 // 3, SS))
    elif headgear == 'side_bun':
        # Right-of-centre forward-leaning bun — Pit-1 standing-archer
        # canonical hair. Distinctly OFF-CENTRE.
        bun_w = int(w * 0.40)
        bun_h = int(h * 0.36)
        bun_cx = cx + int(w * 0.18)
        bun_rect = pygame.Rect(bun_cx - bun_w // 2,
                               top_y - bun_h // 2 - SS, bun_w, bun_h)
        pygame.draw.ellipse(buf, ramp['shadow'], bun_rect)
        pygame.draw.ellipse(buf, ramp['body'],
                            bun_rect.inflate(-SS, -SS))
        # Hair lines radiating from temple to bun.
        for k in range(3):
            pygame.draw.line(buf, ramp['deep'],
                             (cx - SS, top_y + int(h * 0.20) + k * SS),
                             (bun_cx - bun_w // 4,
                              top_y + SS + k * SS),
                             max(1, SS // 3))
        ochre = ramp.get('ochre',
                         _mix(palette['stone_accent'], (212, 162, 70), 0.68))
        pygame.draw.line(buf, ochre,
                         (bun_cx - bun_w // 3, top_y),
                         (bun_cx + bun_w // 3, top_y),
                         max(1, SS // 2))
    elif headgear == 'cavalry_cap':
        # Small rounded leather cap — chin strap visible.
        cap_w = int(w * 1.10)
        cap_h = int(h * 0.40)
        cap_rect = pygame.Rect(cx - cap_w // 2,
                               top_y - cap_h // 2, cap_w, cap_h)
        pygame.draw.ellipse(buf, ramp['deep'], cap_rect)
        pygame.draw.ellipse(buf, ramp['shadow'],
                            cap_rect.inflate(-SS, -SS))
        # Cap rim ridge — separates leather from forehead.
        pygame.draw.arc(buf, ramp['lit'],
                        (cap_rect.x + SS, cap_rect.y + SS,
                         cap_rect.w - SS * 2, cap_rect.h - SS),
                        math.pi * 1.10, math.pi * 1.90,
                        max(1, SS // 3))
        # Chin strap — under-chin line.
        for side in (-1, 1):
            pygame.draw.line(buf, ramp['deep'],
                             (cx + side * (w // 2 - SS),
                              top_y + h // 3),
                             (cx + side * SS, head_rect.bottom + SS),
                             max(1, SS // 3))
    elif headgear == 'trapezoid_cap':
        # Long trapezoidal charioteer cap — tall rectangle that hooks
        # backward at the apex. Ochre + vermilion bands.
        cap_w = int(w * 0.85)
        cap_h = int(h * 0.85)
        # Hook-back tail.
        pygame.draw.polygon(buf, ramp['deep'], [
            (cx - cap_w // 2, top_y),
            (cx + cap_w // 2, top_y),
            (cx + cap_w // 2 + SS, top_y - cap_h // 2),
            (cx + cap_w // 3, top_y - cap_h),
            (cx - cap_w // 3, top_y - cap_h),
            (cx - cap_w // 2 - SS, top_y - cap_h // 2),
        ])
        # Front face — slightly lighter.
        pygame.draw.polygon(buf, ramp['shadow'], [
            (cx - cap_w // 2 + SS, top_y),
            (cx + cap_w // 2 - SS, top_y),
            (cx + cap_w // 2, top_y - cap_h // 2),
            (cx + cap_w // 3 - SS, top_y - cap_h + SS),
            (cx - cap_w // 3 + SS, top_y - cap_h + SS),
            (cx - cap_w // 2, top_y - cap_h // 2),
        ])
        # Two ochre rank bands across the cap.
        ochre = _mix(palette['stone_accent'], (212, 162, 70), 0.68)
        verm = _mix(palette['stone_accent'], (172, 60, 46), 0.62)
        pygame.draw.line(buf, ochre,
                         (cx - cap_w // 2 + SS, top_y - cap_h // 4),
                         (cx + cap_w // 2 - SS, top_y - cap_h // 4),
                         max(1, SS // 2))
        pygame.draw.line(buf, verm,
                         (cx - cap_w // 2 + SS, top_y - cap_h * 2 // 3),
                         (cx + cap_w // 2 - SS, top_y - cap_h * 2 // 3),
                         max(1, SS // 2))
        # Cap top-edge specular.
        pygame.draw.line(buf, ramp['lit'],
                         (cx - cap_w // 3, top_y - cap_h + SS),
                         (cx + cap_w // 3, top_y - cap_h + SS), 1)
    elif headgear == 'fishtail_crown':
        # The officer's twin-fish-tail guan — symmetric outward-curving
        # tapered wedges meeting at centre. The iconic 'general' silhouette.
        crown_h = int(h * 1.10)
        flare = int(w * 0.85)
        base_w = int(w * 0.55)
        pygame.draw.rect(buf, ramp['deep'],
                         (cx - base_w // 2, top_y - SS // 2,
                          base_w, SS * 2))
        for side in (-1, 1):
            pts = [
                (cx + side * SS, top_y - SS // 2),
                (cx + side * (base_w // 2),
                 top_y - SS // 2),
                (cx + side * flare,
                 top_y - crown_h // 2),
                (cx + side * (flare - SS),
                 top_y - crown_h),
                (cx + side * SS, top_y - crown_h + SS * 2),
            ]
            pygame.draw.polygon(buf, ramp['deep'], pts)
            inner = [(cx + side * SS, top_y - SS),
                     (cx + side * (base_w // 2 - SS // 2),
                      top_y - SS),
                     (cx + side * (flare - SS),
                      top_y - crown_h // 2),
                     (cx + side * (flare - SS * 2),
                      top_y - crown_h + SS),
                     (cx + side * SS, top_y - crown_h + SS * 3)]
            pygame.draw.polygon(buf, ramp['shadow'], inner)
            # Ochre spine band along the fish tail.
            ochre = _mix(palette['stone_accent'], (212, 162, 70), 0.68)
            pygame.draw.line(buf, ochre,
                             (cx + side * SS * 2, top_y - SS),
                             (cx + side * (flare - SS * 2),
                              top_y - crown_h // 2),
                             max(1, SS // 2))
            pygame.draw.line(buf, ochre,
                             (cx + side * (flare - SS * 2),
                              top_y - crown_h // 2),
                             (cx + side * (flare - SS * 3),
                              top_y - crown_h + SS * 2),
                             max(1, SS // 2))
            # Vermilion knot at tip.
            verm = _mix(palette['stone_accent'], (172, 60, 46), 0.62)
            pygame.draw.circle(buf, verm,
                               (cx + side * (flare - SS),
                                top_y - crown_h + SS),
                               max(1, SS // 2))


def _draw_armour_panel_hd(buf, panel_rect, ramp, palette,
                          *, rows=5, cols=3, knot=True):
    """Square scale-armour panel — rows × cols of small rounded plates
    with bronze rivets + white inter-plate stitching. The defining
    visual texture across Qin warrior torsos."""
    if panel_rect.w < SS * 6 or panel_rect.h < SS * 6:
        return
    plate_w = panel_rect.w // cols
    plate_h = panel_rect.h // rows
    for r in range(rows):
        for c in range(cols):
            px = panel_rect.x + c * plate_w
            py = panel_rect.y + r * plate_h
            plate = pygame.Rect(px + SS // 2, py + SS // 2,
                                plate_w - SS, plate_h - SS)
            pygame.draw.rect(buf, _shade(ramp['shadow'], -10), plate)
            pygame.draw.rect(buf, _shade(ramp['body'], -8),
                             plate.inflate(-SS // 2, -SS // 2))
            # Lit top edge.
            pygame.draw.line(buf, ramp['lit'],
                             (plate.x, plate.y),
                             (plate.right - 1, plate.y),
                             max(1, SS // 3))
            # Bronze rivets — 2 small dots, top-left + top-right of plate.
            rivet = _mix(palette['stone_accent'], (152, 124, 70), 0.72)
            pygame.draw.circle(buf, rivet,
                               (plate.x + SS, plate.y + SS),
                               max(1, SS // 3))
            pygame.draw.circle(buf, rivet,
                               (plate.right - SS, plate.y + SS),
                               max(1, SS // 3))
        # White stitching between rows — thread holding the plates.
        if r > 0:
            white = ramp.get('white',
                             _mix(palette['stone_light'],
                                  (228, 218, 196), 0.60))
            pygame.draw.line(buf, white,
                             (panel_rect.x + SS,
                              panel_rect.y + r * plate_h),
                             (panel_rect.right - SS,
                              panel_rect.y + r * plate_h),
                             max(1, SS // 3))
    # Vermilion ribbon-knot at top centre — the rank-signature.
    if knot:
        verm = _mix(palette['stone_accent'], (172, 60, 46), 0.62)
        knot_y = panel_rect.y + plate_h // 2
        pygame.draw.rect(buf, verm,
                         (panel_rect.x + panel_rect.w // 2 - SS,
                          knot_y, SS * 2, SS * 2))
        # Two trailing tails — bow ribbon.
        pygame.draw.line(buf, verm,
                         (panel_rect.x + panel_rect.w // 2 - SS,
                          knot_y + SS * 2),
                         (panel_rect.x + panel_rect.w // 2 - SS * 2,
                          knot_y + SS * 5), max(1, SS // 2))
        pygame.draw.line(buf, verm,
                         (panel_rect.x + panel_rect.w // 2 + SS,
                          knot_y + SS * 2),
                         (panel_rect.x + panel_rect.w // 2 + SS * 2,
                          knot_y + SS * 5), max(1, SS // 2))


# ── 1. Terracotta General (高级军吏俑) ─────────────────────────────────────
#
# High-ranking officer (~10 ever excavated). Iconography: double
# fish-tail crown (guan), hands clasped over abdomen, dense plated
# armour with vermilion ribbon-knots, ceremonial long robe past knee,
# wide shoulder pauldrons. Ceremonial polearm held against right flank.
#
# Research:
#   https://www.smithsonianmag.com/smart-news/archaeologists-discover-rare-clay-commander-among-thousands-of-life-size-terra-cotta-soldiers-in-china-180985747/
#   https://www.scmp.com/news/china/science/article/3291332/mysterious-terracotta-commander-offers-new-clues-chinas-ancient-qin-dynasty-army
#   https://en.wikipedia.org/wiki/Terracotta_Army

def _hd_general(buf, cx, base_y, top_y, palette, seed):
    ramp = _palette_blend(_CLAY_RAMP, palette)
    total = base_y - top_y
    if total < 60 * SS:
        return

    crown_h = max(SS * 12, int(total * 0.17))
    head_h = max(SS * 10, int(total * 0.13))
    neck_h = max(SS * 2, int(total * 0.03))
    torso_h = max(SS * 20, int(total * 0.35))
    skirt_h = max(SS * 14, int(total * 0.24))
    feet_h = total - crown_h - head_h - neck_h - torso_h - skirt_h

    y = base_y

    # ── Polearm ── drawn FIRST so the body overlaps the shaft at hip.
    shaft_x = cx + int(total * 0.14)
    spear_h = max(SS * 8, total // 8)
    shaft_top_y = top_y + spear_h
    pygame.draw.line(buf, ramp['deep'],
                     (shaft_x, shaft_top_y), (shaft_x, base_y - SS * 2),
                     max(2, SS // 2))
    pygame.draw.line(buf, _shade(ramp['shadow'], 15),
                     (shaft_x + SS // 2, shaft_top_y),
                     (shaft_x + SS // 2, base_y - SS * 2),
                     max(1, SS // 3))
    # Ochre grip wrap at hip height.
    grip_y = base_y - total // 3
    ochre = ramp['ochre']
    pygame.draw.rect(buf, ochre,
                     (shaft_x - SS, grip_y, SS * 3, SS * 2))
    # Spear head — flame-leaf bronze blade.
    bronze = _palette_blend(_BRONZE_RAMP, palette)
    blade_w = max(SS * 2, spear_h // 4)
    pygame.draw.polygon(buf, bronze['shadow'], [
        (shaft_x, shaft_top_y),
        (shaft_x - blade_w, shaft_top_y - spear_h // 2),
        (shaft_x, top_y + SS),
        (shaft_x + blade_w, shaft_top_y - spear_h // 2),
    ])
    pygame.draw.polygon(buf, bronze['lit'], [
        (shaft_x, shaft_top_y - SS),
        (shaft_x - blade_w + SS, shaft_top_y - spear_h // 2),
        (shaft_x, top_y + SS * 2),
    ])
    _specular_dot(buf, shaft_x, top_y + spear_h // 4,
                  max(1, SS // 3), bronze['specular'])

    # ── Square-toed Qin shoes peeking from under robe. ───────────────
    shoe_w = max(SS * 10, int(total * 0.18))
    shoe_rect = pygame.Rect(cx - shoe_w // 2, y - feet_h, shoe_w, feet_h)
    pygame.draw.rect(buf, ramp['deep'], shoe_rect)
    pygame.draw.rect(buf, ramp['shadow'], shoe_rect.inflate(-SS, -SS))
    pygame.draw.line(buf, ramp['deep'],
                     (cx, y - feet_h + SS), (cx, y - SS), max(1, SS // 2))
    y -= feet_h

    # ── Skirt / lower ceremonial robe — flared trapezoid ─────────────
    skirt_top_w = max(SS * 14, int(total * 0.22))
    skirt_bot_w = max(skirt_top_w + SS * 4, int(total * 0.30))
    skirt_pts = [
        (cx - skirt_bot_w // 2, y),
        (cx + skirt_bot_w // 2, y),
        (cx + skirt_top_w // 2, y - skirt_h),
        (cx - skirt_top_w // 2, y - skirt_h),
    ]
    pygame.draw.polygon(buf, ramp['shadow'], skirt_pts)
    inner_pts = [
        (cx - skirt_bot_w // 2 + SS, y - SS),
        (cx + skirt_bot_w // 2 - SS, y - SS),
        (cx + skirt_top_w // 2 - SS, y - skirt_h + SS),
        (cx - skirt_top_w // 2 + SS, y - skirt_h + SS),
    ]
    pygame.draw.polygon(buf, ramp['body'], inner_pts)
    # Robe drape folds — 5 tapered vertical ribbons spanning the skirt.
    for k in range(-2, 3):
        fx = cx + k * (skirt_top_w // 5)
        fxb = cx + k * (skirt_bot_w // 5)
        pygame.draw.line(buf, _shade(ramp['shadow'], -8),
                         (fxb, y - SS), (fx, y - skirt_h + SS * 2),
                         max(1, SS // 3))
        # Lit ridge along the fold's left edge.
        pygame.draw.line(buf, ramp['mid'],
                         (fxb - SS // 2, y - SS),
                         (fx - SS // 2, y - skirt_h + SS * 2),
                         max(1, SS // 3))
    # Lit body edge on the left flank — directional volume cue.
    _rim_light(buf, [
        (cx - skirt_top_w // 2 + SS, y - skirt_h + SS * 2),
        (cx - skirt_bot_w // 2 + SS, y - SS),
    ], ramp['lit'])
    # Saffron/ochre sash at waist.
    pygame.draw.rect(buf, ramp['vermilion'],
                     (cx - skirt_top_w // 2, y - skirt_h - SS,
                      skirt_top_w, SS * 2))
    # Surviving polychrome patches in protected creases.
    _clay_pigment_patch(buf, cx - skirt_top_w // 4,
                        y - skirt_h * 2 // 3, SS * 4, SS * 2,
                        ramp['malachite'], alpha=80)
    _clay_pigment_patch(buf, cx + skirt_top_w // 4,
                        y - skirt_h // 3, SS * 3, SS * 2,
                        ramp['ochre'], alpha=90)
    y -= skirt_h

    # ── Torso + plated armour ────────────────────────────────────────
    torso_w = max(SS * 14, int(total * 0.23))
    armour_top = y - torso_h
    pygame.draw.rect(buf, ramp['shadow'],
                     (cx - torso_w // 2, armour_top, torso_w, torso_h))
    _gradient_fill_rect(buf,
                        pygame.Rect(cx - torso_w // 2 + SS,
                                    armour_top + SS,
                                    torso_w - SS * 2, torso_h - SS * 2),
                        ramp['lit'], ramp['mid'])
    # Armour panel.
    panel = pygame.Rect(cx - torso_w // 2 + SS * 2,
                        armour_top + SS * 3,
                        torso_w - SS * 4, torso_h - SS * 6)
    _draw_armour_panel_hd(buf, panel, ramp, palette,
                          rows=5, cols=3, knot=True)
    # Wide shoulder pauldrons — wider than the torso, ochre rim.
    pad_w = torso_w + SS * 8
    pygame.draw.rect(buf, ramp['shadow'],
                     (cx - pad_w // 2, armour_top - SS,
                      pad_w, SS * 4))
    pygame.draw.rect(buf, ramp['body'],
                     (cx - pad_w // 2 + SS, armour_top - SS,
                      pad_w - SS * 2, SS * 3))
    pygame.draw.line(buf, ramp['ochre'],
                     (cx - pad_w // 2 + SS, armour_top - SS),
                     (cx + pad_w // 2 - SS, armour_top - SS),
                     max(1, SS // 3))
    # Pauldron rivets — small bronze dots along the rim.
    rivet = _mix(palette['stone_accent'], (152, 124, 70), 0.72)
    for kx in range(-3, 4):
        rx = cx + kx * (pad_w // 8)
        pygame.draw.circle(buf, rivet, (rx, armour_top), max(1, SS // 3))
    # Hands clasped at abdomen — dark oval.
    hand_y = armour_top + (torso_h * 2) // 3
    pygame.draw.ellipse(buf, ramp['deep'],
                        (cx - SS * 5, hand_y - SS, SS * 10, SS * 4))
    pygame.draw.ellipse(buf, ramp['shadow'],
                        (cx - SS * 4, hand_y - SS, SS * 8, SS * 3))
    # Hand specular — soft lit-side highlight.
    _specular_dot(buf, cx - SS * 2, hand_y, max(1, SS // 3),
                  ramp['specular'])
    y = armour_top

    # ── Neck ─────────────────────────────────────────────────────────
    neck_w = max(SS * 4, int(total * 0.07))
    pygame.draw.rect(buf, ramp['shadow'],
                     (cx - neck_w // 2, y - neck_h, neck_w, neck_h))
    pygame.draw.rect(buf, ramp['body'],
                     (cx - neck_w // 2 + SS // 2,
                      y - neck_h, neck_w - SS, neck_h - SS))
    y -= neck_h

    # ── Head + crown ─────────────────────────────────────────────────
    head_w = max(SS * 10, int(total * 0.16))
    _draw_warrior_head_hd(buf, cx, y - head_h, head_w, head_h,
                          palette, ramp, beard=True,
                          headgear='fishtail_crown')


def _draw_general(surf, top_rect, bot_rect, palette, seed):
    bcx = bot_rect.x + bot_rect.width // 2
    plinth_w_screen = int(bot_rect.width * 1.20)
    plinth_h_screen = 9

    # ── Bottom pillar
    if bot_rect.height > 80:
        # HD figure in own buffer.
        bw = bot_rect.width * SS
        bh = (bot_rect.height - plinth_h_screen) * SS
        fig_buf = pygame.Surface((bw, bh), pygame.SRCALPHA)
        _hd_general(fig_buf, bw // 2, bh - 1, 0, palette, seed)
        scaled = pygame.transform.smoothscale(
            fig_buf, (bot_rect.width, bot_rect.height - plinth_h_screen))
        surf.blit(scaled, (bot_rect.x,
                           bot_rect.bottom - plinth_h_screen
                           - scaled.get_height()))
        # Plinth + foliage in screen-space (these are small and the
        # pillar_variants helpers already match the game style).
        ramp = _palette_blend(_CLAY_RAMP, palette)
        pygame.draw.rect(surf, ramp['shadow'],
                         (bcx - plinth_w_screen // 2,
                          bot_rect.bottom - plinth_h_screen,
                          plinth_w_screen, plinth_h_screen))
        pygame.draw.line(surf, ramp['lit'],
                         (bcx - plinth_w_screen // 2,
                          bot_rect.bottom - plinth_h_screen),
                         (bcx + plinth_w_screen // 2 - 1,
                          bot_rect.bottom - plinth_h_screen), 1)
        # Twin pennant battle-standards flanking the plinth — visual
        # silhouette flair.
        verm = _mix(palette['stone_accent'], (172, 60, 46), 0.62)
        ochre = _mix(palette['stone_accent'], (212, 162, 70), 0.68)
        for side in (-1, 1):
            sx = bcx + side * (plinth_w_screen // 2 + 5)
            pygame.draw.line(surf, _shade(ramp['shadow'], -20),
                             (sx, bot_rect.bottom - 1),
                             (sx, bot_rect.bottom - 18), 1)
            pygame.draw.polygon(surf, verm,
                                [(sx, bot_rect.bottom - 18),
                                 (sx + side * 7, bot_rect.bottom - 15),
                                 (sx + side * 5, bot_rect.bottom - 11),
                                 (sx + side * 8, bot_rect.bottom - 7),
                                 (sx, bot_rect.bottom - 9)])
            pygame.draw.line(surf, ochre,
                             (sx, bot_rect.bottom - 18),
                             (sx + side * 7, bot_rect.bottom - 15), 1)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 6, 14, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 6, seed=seed)

    natural_h = max(120, bot_rect.height - plinth_h_screen - 4)

    def draw_into(buf, cx, base_y, top_y):
        _hd_general(buf, cx, base_y, top_y, palette, seed)

    _mirror_top(surf, top_rect, natural_h, draw_into,
                mirror_strategy="flip")


def candidate_warrior_general(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('warrior_general', _draw_general, surf, top_rect,
                 bot_rect, palette, seed)


# ── 2. Standing Archer / Light Infantry (立射俑) ──────────────────────────
#
# Pit 2 standing archer in shooting stance: left foot forward (the 丁
# character stance), torso slight left turn, left arm extended forward
# and slightly down ready to draw, right arm bent across chest. Side-
# bun (right-of-centre). Light leather scale vest over knee-length
# robe — NO heavy armour (combat infantry, must keep mobility).
# Vertical bow stave held in the lead hand.
#
# Research:
#   https://www.travelchinaguide.com/attraction/shaanxi/xian/terra_cotta_army/standing-archers.htm
#   https://en.wikipedia.org/wiki/Terracotta_Army
#   https://visitterracottawarriors.com/index.php/2024/08/05/most-comprehensive-introduction-of-terracotta-warriors-pit-2/

def _hd_archer(buf, cx, base_y, top_y, palette, seed):
    ramp = _palette_blend(_CLAY_RAMP, palette)
    total = base_y - top_y
    if total < 60 * SS:
        return

    head_h = max(SS * 10, int(total * 0.13))
    neck_h = max(SS * 2, int(total * 0.03))
    torso_h = max(SS * 22, int(total * 0.34))
    leg_h = total - head_h - neck_h - torso_h

    y = base_y

    # ── Bow stave — drawn FIRST so the lead arm covers the grip. The
    # bow stave is the canonical archer silhouette cue: a tall vertical
    # arc rising past the head with subtle taper at both ends.
    bow_x = cx - int(total * 0.20)
    bow_top = top_y + int(total * 0.05)
    bow_bot = base_y - int(total * 0.15)
    bow_lit = _mix(palette['stone_accent'], (152, 124, 70), 0.66)
    bow_shadow = _shade(bow_lit, -55)
    # Bow stave drawn as a slightly curved tapered ribbon.
    n_seg = 14
    for k in range(n_seg):
        t = k / (n_seg - 1)
        y_a = int(bow_top + (bow_bot - bow_top) * t)
        # Outward bulge mid-bow.
        x_off = int(math.sin(t * math.pi) * SS * 1.5)
        # Taper width.
        w_seg = max(1, int(SS * (1.4 - abs(t - 0.5) * 1.2)))
        pygame.draw.line(buf, bow_shadow,
                         (bow_x - x_off, y_a),
                         (bow_x - x_off + w_seg, y_a), 1)
        pygame.draw.line(buf, bow_lit,
                         (bow_x - x_off + 1, y_a),
                         (bow_x - x_off + w_seg - 1, y_a), 1)
    # Bowstring — taut faint thread.
    pygame.draw.line(buf, _shade(bow_lit, 60),
                     (bow_x + SS, bow_top + SS),
                     (bow_x + SS, bow_bot - SS), max(1, SS // 4))

    # ── Legs in 丁-stance: left foot forward + slightly out, right foot
    # planted straight back. Wraps with calf-binding leggings (visible
    # diagonal stripes on the calves).
    leg_w = max(SS * 4, int(total * 0.07))
    # Right (rear) leg — straight + slightly to the right of centre.
    rl_x = cx + int(total * 0.06)
    pygame.draw.rect(buf, ramp['shadow'],
                     (rl_x - leg_w // 2, y - leg_h, leg_w, leg_h))
    pygame.draw.rect(buf, ramp['body'],
                     (rl_x - leg_w // 2 + SS // 2, y - leg_h,
                      leg_w - SS, leg_h - SS))
    # Left (front) leg — angled with foot forward.
    ll_x = cx - int(total * 0.10)
    ll_pts = [
        (ll_x - leg_w // 2 + SS, y - leg_h),
        (ll_x + leg_w // 2, y - leg_h),
        (ll_x + leg_w // 2 - SS * 2, y),
        (ll_x - leg_w // 2 - SS * 2, y),
    ]
    pygame.draw.polygon(buf, ramp['shadow'], ll_pts)
    inner_ll = [
        (ll_x - leg_w // 2 + SS * 2, y - leg_h + SS),
        (ll_x + leg_w // 2 - SS, y - leg_h + SS),
        (ll_x + leg_w // 2 - SS * 3, y - SS),
        (ll_x - leg_w // 2 - SS, y - SS),
    ]
    pygame.draw.polygon(buf, ramp['body'], inner_ll)
    # Calf-binding wraps — diagonal stripes on both calves.
    for leg_x in (rl_x, ll_x):
        for k in range(4):
            stripe_y = y - leg_h // 2 + k * (leg_h // 8)
            pygame.draw.line(buf, ramp['deep'],
                             (leg_x - leg_w // 2 + SS // 2, stripe_y),
                             (leg_x + leg_w // 2 - SS // 2, stripe_y - SS),
                             max(1, SS // 3))
    # Square-toed shoes.
    for foot_cx, foot_w in ((rl_x, leg_w + SS * 2),
                            (ll_x - SS * 2, leg_w + SS * 3)):
        pygame.draw.rect(buf, ramp['deep'],
                         (foot_cx - foot_w // 2, y - SS * 2,
                          foot_w, SS * 2))
    y -= leg_h

    # ── Robe + light scale vest. Robe is knee-length matte clay; vest
    # has a small diamond-pattern scale band across the chest only.
    torso_w = max(SS * 14, int(total * 0.22))
    armour_top = y - torso_h
    pygame.draw.rect(buf, ramp['shadow'],
                     (cx - torso_w // 2, armour_top, torso_w, torso_h))
    _gradient_fill_rect(buf,
                        pygame.Rect(cx - torso_w // 2 + SS,
                                    armour_top + SS,
                                    torso_w - SS * 2, torso_h - SS * 2),
                        ramp['lit'], ramp['mid'])
    # Slight torso lean — twist the robe-fold lines a bit to the left.
    for k in range(-2, 3):
        fx_top = cx + k * (torso_w // 6) - SS
        fx_bot = cx + k * (torso_w // 6)
        pygame.draw.line(buf, _shade(ramp['shadow'], -8),
                         (fx_bot, y - SS),
                         (fx_top, armour_top + SS), max(1, SS // 3))
    # Light scale-vest panel — only across the chest top half.
    vest = pygame.Rect(cx - torso_w // 2 + SS * 2,
                       armour_top + SS * 2,
                       torso_w - SS * 4, torso_h * 2 // 5)
    _draw_armour_panel_hd(buf, vest, ramp, palette,
                          rows=3, cols=3, knot=False)
    # Belt at waist — celadon-pigment trace.
    pygame.draw.rect(buf, ramp['malachite'],
                     (cx - torso_w // 2, y - SS * 2, torso_w, SS * 2))
    # Faded pigment patches in protected armpit recess + belly.
    _clay_pigment_patch(buf, cx - torso_w // 3,
                        armour_top + torso_h * 2 // 3,
                        SS * 3, SS * 2, ramp['vermilion'], alpha=85)
    _clay_pigment_patch(buf, cx + torso_w // 3,
                        armour_top + torso_h // 3,
                        SS * 2, SS * 2, ramp['ochre'], alpha=80)

    # Left arm extended forward + slightly down — gripping the bow.
    arm_w = max(SS * 3, int(total * 0.05))
    arm_pts = [
        (cx - torso_w // 2 + SS, armour_top + SS * 3),
        (cx - torso_w // 2 - SS, armour_top + SS * 3 + arm_w),
        (bow_x + SS * 2, bow_top + (bow_bot - bow_top) // 2 + SS * 2),
        (bow_x + SS * 2, bow_top + (bow_bot - bow_top) // 2 - SS * 2),
    ]
    pygame.draw.polygon(buf, ramp['shadow'], arm_pts)
    pygame.draw.polygon(buf, ramp['body'], [
        (cx - torso_w // 2 + SS * 2,
         armour_top + SS * 3 + SS // 2),
        (cx - torso_w // 2,
         armour_top + SS * 3 + arm_w - SS // 2),
        (bow_x + SS * 3,
         bow_top + (bow_bot - bow_top) // 2 + SS),
        (bow_x + SS * 3,
         bow_top + (bow_bot - bow_top) // 2 - SS),
    ])
    # Right arm bent across chest.
    pygame.draw.polygon(buf, ramp['shadow'], [
        (cx + torso_w // 2 - SS, armour_top + SS * 3),
        (cx + torso_w // 2 + arm_w, armour_top + SS * 4),
        (cx + SS * 2, armour_top + torso_h // 2),
        (cx + SS * 2, armour_top + torso_h // 2 - arm_w),
    ])
    pygame.draw.polygon(buf, ramp['body'], [
        (cx + torso_w // 2 - SS * 2, armour_top + SS * 3 + SS // 2),
        (cx + torso_w // 2 + arm_w - SS, armour_top + SS * 4),
        (cx + SS * 3, armour_top + torso_h // 2 - SS // 2),
        (cx + SS * 3, armour_top + torso_h // 2 - arm_w + SS),
    ])
    y = armour_top

    # ── Neck.
    neck_w = max(SS * 4, int(total * 0.07))
    pygame.draw.rect(buf, ramp['shadow'],
                     (cx - neck_w // 2, y - neck_h, neck_w, neck_h))
    pygame.draw.rect(buf, ramp['body'],
                     (cx - neck_w // 2 + SS // 2,
                      y - neck_h, neck_w - SS, neck_h - SS))
    y -= neck_h

    # ── Head + side bun.
    head_w = max(SS * 10, int(total * 0.16))
    _draw_warrior_head_hd(buf, cx, y - head_h, head_w, head_h,
                          palette, ramp, beard=False,
                          headgear='side_bun')


def _draw_archer(surf, top_rect, bot_rect, palette, seed):
    bcx = bot_rect.x + bot_rect.width // 2
    plinth_h = 8

    if bot_rect.height > 80:
        bw = bot_rect.width * SS
        bh = (bot_rect.height - plinth_h) * SS
        fig_buf = pygame.Surface((bw, bh), pygame.SRCALPHA)
        _hd_archer(fig_buf, bw // 2, bh - 1, 0, palette, seed)
        scaled = pygame.transform.smoothscale(
            fig_buf, (bot_rect.width, bot_rect.height - plinth_h))
        surf.blit(scaled, (bot_rect.x,
                           bot_rect.bottom - plinth_h
                           - scaled.get_height()))
        ramp = _palette_blend(_CLAY_RAMP, palette)
        pygame.draw.rect(surf, ramp['shadow'],
                         (bcx - int(bot_rect.width * 1.15) // 2,
                          bot_rect.bottom - plinth_h,
                          int(bot_rect.width * 1.15), plinth_h))
        pygame.draw.line(surf, ramp['lit'],
                         (bcx - int(bot_rect.width * 1.15) // 2,
                          bot_rect.bottom - plinth_h),
                         (bcx + int(bot_rect.width * 1.15) // 2 - 1,
                          bot_rect.bottom - plinth_h), 1)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 4, 12, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 5, seed=seed)

    natural_h = max(120, bot_rect.height - plinth_h - 4)

    def draw_into(buf, cx, base_y, top_y):
        _hd_archer(buf, cx, base_y, top_y, palette, seed)

    _mirror_top(surf, top_rect, natural_h, draw_into,
                mirror_strategy="flip")


def candidate_warrior_standing_archer(surf, top_rect, bot_rect,
                                       palette, seed):
    _cached_draw('warrior_standing_archer', _draw_archer, surf,
                 top_rect, bot_rect, palette, seed)


# ── 3. Kneeling Crossbowman (跪射俑) ──────────────────────────────────────
#
# Museum-icon crouch: right knee + foot planted, left knee down on the
# ground, torso upright, hands clasped at chest miming the crossbow
# grip. Rear bun + chin strap. Dense scale armour vest over a tunic.
# The most photographed terracotta figure — silhouette MUST read at
# thumbnail as the kneeling pose.
#
# Research:
#   https://www.travelchinaguide.com/attraction/shaanxi/xian/terra_cotta_army/kneeling-archers.htm
#   https://en.wikipedia.org/wiki/Terracotta_Army
#   https://www.britannica.com/topic/terra-cotta-army

def _hd_kneeling(buf, cx, base_y, top_y, palette, seed):
    ramp = _palette_blend(_CLAY_RAMP, palette)
    total = base_y - top_y
    if total < 60 * SS:
        return

    # Vertical budget — kneeling pose compresses leg height so torso +
    # head dominate the silhouette.
    head_h = max(SS * 11, int(total * 0.14))
    neck_h = max(SS * 2, int(total * 0.025))
    torso_h = max(SS * 24, int(total * 0.38))
    thigh_h = max(SS * 8, int(total * 0.13))
    shin_h = max(SS * 16, int(total * 0.27))
    foot_h = total - head_h - neck_h - torso_h - thigh_h - shin_h

    y = base_y

    # ── Left foot + shin lying flat on the ground (knee down).
    flat_shin_w = max(SS * 5, int(total * 0.09))
    flat_shin_len = max(SS * 18, int(total * 0.32))
    pygame.draw.polygon(buf, ramp['shadow'], [
        (cx - flat_shin_len // 2, y),
        (cx + flat_shin_len // 2, y),
        (cx + flat_shin_len // 2 - SS, y - foot_h),
        (cx - flat_shin_len // 2 + SS, y - foot_h),
    ])
    pygame.draw.polygon(buf, ramp['body'], [
        (cx - flat_shin_len // 2 + SS, y - SS // 2),
        (cx + flat_shin_len // 2 - SS, y - SS // 2),
        (cx + flat_shin_len // 2 - SS * 2, y - foot_h + SS),
        (cx - flat_shin_len // 2 + SS * 2, y - foot_h + SS),
    ])
    # Toe of left foot poking out.
    pygame.draw.rect(buf, ramp['deep'],
                     (cx - flat_shin_len // 2 - SS * 2,
                      y - foot_h + SS, SS * 3, SS * 2))
    y -= foot_h

    # ── Right foot — planted with sole flat under bent knee. Drawn as a
    # forward-projecting wedge ahead of the figure.
    right_foot_w = max(SS * 7, int(total * 0.12))
    right_foot_x = cx + flat_shin_len // 4
    pygame.draw.polygon(buf, ramp['deep'], [
        (right_foot_x - right_foot_w // 2, y),
        (right_foot_x + right_foot_w, y),
        (right_foot_x + right_foot_w, y - SS * 2),
        (right_foot_x - right_foot_w // 2, y - SS * 2),
    ])
    pygame.draw.line(buf, ramp['lit'],
                     (right_foot_x - right_foot_w // 2, y - SS * 2),
                     (right_foot_x + right_foot_w, y - SS * 2),
                     max(1, SS // 3))

    # ── Right shin — angled forward-up from foot to bent-knee. Drawn
    # with calf-binding stripes.
    right_knee_x = cx + int(total * 0.06)
    shin_pts = [
        (right_foot_x - right_foot_w // 2 + SS, y - SS),
        (right_foot_x + right_foot_w // 2, y - SS),
        (right_knee_x + flat_shin_w // 2, y - shin_h - foot_h),
        (right_knee_x - flat_shin_w // 2 - SS, y - shin_h - foot_h),
    ]
    pygame.draw.polygon(buf, ramp['shadow'], shin_pts)
    inner_shin = [
        (right_foot_x - right_foot_w // 2 + SS * 2, y - SS * 2),
        (right_foot_x + right_foot_w // 2 - SS, y - SS * 2),
        (right_knee_x + flat_shin_w // 2 - SS, y - shin_h - foot_h + SS),
        (right_knee_x - flat_shin_w // 2, y - shin_h - foot_h + SS),
    ]
    pygame.draw.polygon(buf, ramp['body'], inner_shin)
    # Calf-binding stripes — 4 short diagonals.
    for k in range(4):
        t = (k + 1) / 5
        sx_a = int(right_foot_x - right_foot_w // 4 + flat_shin_w * t)
        sy_a = int(y - SS - (shin_h - foot_h) * t)
        sx_b = sx_a + SS * 2
        sy_b = sy_a + SS
        pygame.draw.line(buf, ramp['deep'],
                         (sx_a, sy_a), (sx_b, sy_b), max(1, SS // 3))

    # ── Left thigh down to plinth (the planted-knee thigh).
    thigh_pts = [
        (cx - flat_shin_w, y - SS),
        (cx + flat_shin_w, y - SS),
        (cx + flat_shin_w + SS, y - foot_h - thigh_h),
        (cx - flat_shin_w + SS, y - foot_h - thigh_h),
    ]
    pygame.draw.polygon(buf, ramp['shadow'], thigh_pts)
    pygame.draw.polygon(buf, ramp['body'], [
        (cx - flat_shin_w + SS, y - SS),
        (cx + flat_shin_w - SS, y - SS),
        (cx + flat_shin_w, y - foot_h - thigh_h + SS),
        (cx - flat_shin_w + SS * 2, y - foot_h - thigh_h + SS),
    ])
    y -= thigh_h + foot_h - SS * 2

    # ── Torso + dense armour. Note the kneeling figure's armour is the
    # densest of all warrior classes — overlapping diamond-pattern
    # plates on chest, shoulder + waist.
    armour_top = y - torso_h
    torso_w = max(SS * 15, int(total * 0.26))
    pygame.draw.rect(buf, ramp['shadow'],
                     (cx - torso_w // 2, armour_top, torso_w, torso_h))
    _gradient_fill_rect(buf,
                        pygame.Rect(cx - torso_w // 2 + SS,
                                    armour_top + SS,
                                    torso_w - SS * 2, torso_h - SS * 2),
                        ramp['lit'], ramp['mid'])
    panel = pygame.Rect(cx - torso_w // 2 + SS * 2,
                        armour_top + SS * 3,
                        torso_w - SS * 4, torso_h - SS * 5)
    _draw_armour_panel_hd(buf, panel, ramp, palette,
                          rows=7, cols=4, knot=True)
    # Hands clasped at chest — miming the crossbow grip. Two hands
    # overlapping in front of the upper torso.
    grip_y = armour_top + torso_h // 3
    pygame.draw.ellipse(buf, ramp['deep'],
                        (cx - SS * 5, grip_y - SS,
                         SS * 10, SS * 4))
    pygame.draw.ellipse(buf, ramp['shadow'],
                        (cx - SS * 4, grip_y - SS,
                         SS * 8, SS * 3))
    _specular_dot(buf, cx - SS * 2, grip_y, max(1, SS // 3),
                  ramp['specular'])
    # Crossbow horizontal bar — short stub poking out from clasped
    # hands on the right side. Reads as the bow stock.
    bow_x_end = cx + SS * 5
    pygame.draw.line(buf, ramp['deep'],
                     (cx + SS * 3, grip_y),
                     (bow_x_end + SS * 2, grip_y),
                     max(1, SS // 2))
    pygame.draw.line(buf, ramp['mid'],
                     (cx + SS * 3, grip_y - SS // 2),
                     (bow_x_end + SS * 2, grip_y - SS // 2), 1)
    y = armour_top

    # ── Neck.
    neck_w = max(SS * 4, int(total * 0.07))
    pygame.draw.rect(buf, ramp['shadow'],
                     (cx - neck_w // 2, y - neck_h, neck_w, neck_h))
    pygame.draw.rect(buf, ramp['body'],
                     (cx - neck_w // 2 + SS // 2,
                      y - neck_h, neck_w - SS, neck_h - SS))
    y -= neck_h

    # ── Head + rear bun.
    head_w = max(SS * 10, int(total * 0.17))
    _draw_warrior_head_hd(buf, cx, y - head_h, head_w, head_h,
                          palette, ramp, beard=False,
                          headgear='bun')


def _draw_kneeling(surf, top_rect, bot_rect, palette, seed):
    bcx = bot_rect.x + bot_rect.width // 2
    plinth_h = 7

    if bot_rect.height > 80:
        bw = bot_rect.width * SS
        bh = (bot_rect.height - plinth_h) * SS
        fig_buf = pygame.Surface((bw, bh), pygame.SRCALPHA)
        _hd_kneeling(fig_buf, bw // 2, bh - 1, 0, palette, seed)
        scaled = pygame.transform.smoothscale(
            fig_buf, (bot_rect.width, bot_rect.height - plinth_h))
        surf.blit(scaled, (bot_rect.x,
                           bot_rect.bottom - plinth_h
                           - scaled.get_height()))
        ramp = _palette_blend(_CLAY_RAMP, palette)
        pygame.draw.rect(surf, ramp['shadow'],
                         (bcx - int(bot_rect.width * 1.10) // 2,
                          bot_rect.bottom - plinth_h,
                          int(bot_rect.width * 1.10), plinth_h))
        pygame.draw.line(surf, ramp['lit'],
                         (bcx - int(bot_rect.width * 1.10) // 2,
                          bot_rect.bottom - plinth_h),
                         (bcx + int(bot_rect.width * 1.10) // 2 - 1,
                          bot_rect.bottom - plinth_h), 1)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 4, 12, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2,
                        bot_rect.width - 4, 5, seed=seed)

    natural_h = max(120, bot_rect.height - plinth_h - 4)

    def draw_into(buf, cx, base_y, top_y):
        _hd_kneeling(buf, cx, base_y, top_y, palette, seed)

    _mirror_top(surf, top_rect, natural_h, draw_into,
                mirror_strategy="flip")


def candidate_warrior_kneeling_archer(surf, top_rect, bot_rect,
                                       palette, seed):
    _cached_draw('warrior_kneeling_archer', _draw_kneeling, surf,
                 top_rect, bot_rect, palette, seed)


# ── 4. Cavalryman + Saddled Horse (骑兵俑 + 鞍马) ──────────────────────────
#
# Pair: cavalryman standing beside his northwestern saddle horse. The
# canonical Pit-2 silhouette — rider in short tunic + light vest, small
# round leather cap with chin strap, no shoulder pauldrons (mobility
# for bow draw), holding the horse's reins in left hand. Horse: short
# legs, large nostril, soft saddle with raised pommel + cantle, two
# belly bands, cropped mane, braided plait tail. No stirrups.
#
# Research:
#   https://www.travelchinaguide.com/attraction/shaanxi/xian/terra_cotta_army/cavalrymen.htm
#   https://www.travelchinaguide.com/attraction/shaanxi/xian/terra_cotta_army/hairstyle.htm
#   https://en.wikipedia.org/wiki/Terracotta_Army

def _hd_cavalry(buf, cx, base_y, top_y, palette, seed):
    ramp = _palette_blend(_CLAY_RAMP, palette)
    total = base_y - top_y
    if total < 60 * SS:
        return

    # Horse takes the right ~55% of the silhouette, rider takes the
    # left ~45% standing at the horse's near (left-viewer) side.
    horse_cx = cx + int(total * 0.13)
    rider_cx = cx - int(total * 0.18)

    # ── Horse body. Drawn FIRST so the rider overlaps the saddle area.
    horse_w = max(SS * 22, int(total * 0.42))
    horse_h = max(SS * 16, int(total * 0.32))
    horse_top = base_y - int(total * 0.50)
    horse_bot = base_y - int(total * 0.20)
    # Barrel of the body.
    barrel_rect = pygame.Rect(horse_cx - horse_w // 2, horse_top,
                              horse_w, horse_h)
    pygame.draw.ellipse(buf, ramp['shadow'], barrel_rect)
    pygame.draw.ellipse(buf, ramp['body'],
                        barrel_rect.inflate(-SS, -SS))
    _gradient_fill_rect(buf,
                        pygame.Rect(barrel_rect.x + SS * 2,
                                    barrel_rect.y + SS,
                                    barrel_rect.w - SS * 4,
                                    barrel_rect.h // 2),
                        ramp['lit'], ramp['mid'])
    # Forelegs — short with hoof.
    for leg_off in (int(horse_w * 0.34), int(horse_w * 0.18)):
        lx = horse_cx + leg_off
        pygame.draw.rect(buf, ramp['shadow'],
                         (lx - SS, horse_bot,
                          SS * 2, base_y - horse_bot - SS))
        pygame.draw.rect(buf, ramp['body'],
                         (lx - SS + SS // 2, horse_bot,
                          SS, base_y - horse_bot - SS * 2))
        pygame.draw.rect(buf, ramp['deep'],
                         (lx - SS * 2, base_y - SS,
                          SS * 4, SS))
    # Rear legs.
    for leg_off in (-int(horse_w * 0.34), -int(horse_w * 0.18)):
        lx = horse_cx + leg_off
        pygame.draw.rect(buf, ramp['shadow'],
                         (lx - SS, horse_bot,
                          SS * 2, base_y - horse_bot - SS))
        pygame.draw.rect(buf, ramp['body'],
                         (lx - SS + SS // 2, horse_bot,
                          SS, base_y - horse_bot - SS * 2))
        pygame.draw.rect(buf, ramp['deep'],
                         (lx - SS * 2, base_y - SS,
                          SS * 4, SS))
    # Horse neck + head — rises forward + up from the front of the body.
    neck_top_y = horse_top - int(total * 0.10)
    head_x = horse_cx + horse_w // 2 + SS * 3
    neck_pts = [
        (horse_cx + horse_w // 2 - SS * 2, horse_top + SS * 2),
        (horse_cx + horse_w // 2 + SS * 2, horse_top + SS * 3),
        (head_x - SS, neck_top_y + SS * 2),
        (head_x - SS * 3, neck_top_y),
    ]
    pygame.draw.polygon(buf, ramp['shadow'], neck_pts)
    pygame.draw.polygon(buf, ramp['body'], [
        (horse_cx + horse_w // 2 - SS, horse_top + SS * 3),
        (horse_cx + horse_w // 2 + SS, horse_top + SS * 4),
        (head_x - SS * 2, neck_top_y + SS * 2),
        (head_x - SS * 4, neck_top_y + SS),
    ])
    # Cropped mane — short vertical bristles along the top of the neck.
    for k in range(7):
        t = k / 6
        mx = int(horse_cx + horse_w // 2 - SS * 2
                 + ((head_x - SS * 3) - (horse_cx + horse_w // 2 - SS * 2))
                 * t)
        my = int(horse_top + SS * 2 + (neck_top_y - horse_top - SS * 2) * t)
        pygame.draw.line(buf, ramp['deep'],
                         (mx, my - SS * 2),
                         (mx, my + SS // 2), max(1, SS // 3))
    # Horse head — small wedge with large nostril.
    head_rect = pygame.Rect(head_x - SS * 4, neck_top_y,
                            SS * 8, SS * 5)
    pygame.draw.ellipse(buf, ramp['shadow'], head_rect)
    pygame.draw.ellipse(buf, ramp['body'], head_rect.inflate(-SS, -SS))
    # Nostril — defining feature of the northwestern breed.
    pygame.draw.circle(buf, ramp['deep'],
                       (head_x + SS * 2, neck_top_y + SS * 3),
                       max(1, SS // 2))
    # Eye.
    pygame.draw.circle(buf, ramp['deep'],
                       (head_x, neck_top_y + SS), max(1, SS // 3))
    # Bridle reins — go from horse mouth up to rider's left hand.
    rein_color = ramp['deep']
    pygame.draw.line(buf, rein_color,
                     (head_x + SS * 2, neck_top_y + SS * 2),
                     (rider_cx + SS * 2,
                      base_y - int(total * 0.46)),
                     max(1, SS // 3))
    pygame.draw.line(buf, rein_color,
                     (head_x + SS, neck_top_y + SS),
                     (rider_cx + SS,
                      base_y - int(total * 0.46) + SS),
                     max(1, SS // 3))
    # Braided tail — drops behind the rear quarter, longer than mane.
    tail_x = horse_cx - horse_w // 2 - SS
    tail_top = horse_top + SS * 4
    for k in range(7):
        ox = int(math.sin(k * 0.9) * SS)
        pygame.draw.line(buf, ramp['shadow'],
                         (tail_x + ox - SS, tail_top + k * SS * 2),
                         (tail_x + ox + SS, tail_top + k * SS * 2),
                         max(1, SS // 2))
    pygame.draw.line(buf, ramp['deep'],
                     (tail_x, tail_top),
                     (tail_x - SS, tail_top + SS * 14), max(1, SS // 2))
    # Saddle — vermilion saddle cloth + raised pommel + cantle.
    saddle_w = int(horse_w * 0.55)
    saddle_y = horse_top - SS
    pygame.draw.rect(buf, ramp['vermilion'],
                     (horse_cx - saddle_w // 2, saddle_y,
                      saddle_w, SS * 3))
    # Pommel + cantle — small raised arches at each end.
    pygame.draw.polygon(buf, ramp['shadow'], [
        (horse_cx - saddle_w // 2 - SS, saddle_y),
        (horse_cx - saddle_w // 2, saddle_y - SS * 2),
        (horse_cx - saddle_w // 2 + SS * 2, saddle_y - SS),
        (horse_cx - saddle_w // 2 + SS * 2, saddle_y),
    ])
    pygame.draw.polygon(buf, ramp['shadow'], [
        (horse_cx + saddle_w // 2 + SS, saddle_y),
        (horse_cx + saddle_w // 2, saddle_y - SS * 2),
        (horse_cx + saddle_w // 2 - SS * 2, saddle_y - SS),
        (horse_cx + saddle_w // 2 - SS * 2, saddle_y),
    ])
    # Belly bands — two short curves under the barrel.
    for band_off in (-int(horse_w * 0.18), int(horse_w * 0.18)):
        bx = horse_cx + band_off
        pygame.draw.arc(buf, ramp['deep'],
                        (bx - SS * 2, horse_bot - SS,
                         SS * 4, SS * 4),
                        math.pi * 0.05, math.pi * 0.95,
                        max(1, SS // 3))

    # ── Rider standing at horse's near side, slightly forward.
    rider_top = base_y - int(total * 0.85)
    rider_head_h = int(total * 0.13)
    rider_head_w = int(total * 0.14)
    rider_neck_y = rider_top + rider_head_h + SS * 2
    rider_torso_h = int(total * 0.35)
    rider_torso_w = int(total * 0.16)

    # Legs — straight standing.
    leg_bot = base_y
    leg_top = leg_bot - int(total * 0.30)
    for off in (-SS * 2, SS * 2):
        pygame.draw.rect(buf, ramp['shadow'],
                         (rider_cx + off - SS, leg_top,
                          SS * 2, leg_bot - leg_top))
        pygame.draw.rect(buf, ramp['body'],
                         (rider_cx + off - SS + SS // 2, leg_top,
                          SS, leg_bot - leg_top - SS))
        # Calf-binding stripes.
        for k in range(4):
            stripe_y = leg_top + k * (leg_bot - leg_top) // 4 + SS * 2
            pygame.draw.line(buf, ramp['deep'],
                             (rider_cx + off - SS, stripe_y),
                             (rider_cx + off + SS, stripe_y - SS),
                             max(1, SS // 3))
        # Foot.
        pygame.draw.rect(buf, ramp['deep'],
                         (rider_cx + off - SS * 2, leg_bot - SS,
                          SS * 4, SS))
    # Torso — short tunic + light vest. No shoulder pauldrons.
    torso_top = rider_neck_y
    pygame.draw.rect(buf, ramp['shadow'],
                     (rider_cx - rider_torso_w // 2, torso_top,
                      rider_torso_w, rider_torso_h))
    _gradient_fill_rect(buf,
                        pygame.Rect(rider_cx - rider_torso_w // 2 + SS,
                                    torso_top + SS,
                                    rider_torso_w - SS * 2,
                                    rider_torso_h - SS * 2),
                        ramp['lit'], ramp['mid'])
    # Compact armour vest — small panel mid-torso only.
    vest = pygame.Rect(rider_cx - rider_torso_w // 2 + SS,
                       torso_top + SS * 2,
                       rider_torso_w - SS * 2,
                       rider_torso_h // 2)
    _draw_armour_panel_hd(buf, vest, ramp, palette,
                          rows=4, cols=3, knot=False)
    # Cross-collar — diagonal line from left shoulder down to right hip.
    pygame.draw.line(buf, ramp['vermilion'],
                     (rider_cx - rider_torso_w // 2, torso_top + SS),
                     (rider_cx + rider_torso_w // 4, torso_top + SS * 4),
                     max(1, SS // 2))
    # Left arm reaching forward holding reins — bent at elbow.
    pygame.draw.polygon(buf, ramp['shadow'], [
        (rider_cx + rider_torso_w // 2 - SS, torso_top + SS * 3),
        (rider_cx + rider_torso_w // 2 + SS * 2, torso_top + SS * 4),
        (rider_cx + SS * 5, torso_top + SS * 7),
        (rider_cx + SS * 5, torso_top + SS * 5),
    ])
    pygame.draw.polygon(buf, ramp['body'], [
        (rider_cx + rider_torso_w // 2 - SS * 2, torso_top + SS * 3 + SS // 2),
        (rider_cx + rider_torso_w // 2 + SS, torso_top + SS * 4),
        (rider_cx + SS * 5, torso_top + SS * 6),
        (rider_cx + SS * 5, torso_top + SS * 5 + SS // 2),
    ])
    # Hand gripping reins.
    pygame.draw.circle(buf, ramp['deep'],
                       (rider_cx + SS * 6, torso_top + SS * 6),
                       max(1, SS))
    # ── Rider head + cavalry cap.
    _draw_warrior_head_hd(buf, rider_cx, rider_top,
                          rider_head_w, rider_head_h,
                          palette, ramp, beard=False,
                          headgear='cavalry_cap')


def _draw_cavalry(surf, top_rect, bot_rect, palette, seed):
    bcx = bot_rect.x + bot_rect.width // 2
    plinth_h = 7

    if bot_rect.height > 80:
        bw = bot_rect.width * SS
        bh = (bot_rect.height - plinth_h) * SS
        fig_buf = pygame.Surface((bw, bh), pygame.SRCALPHA)
        _hd_cavalry(fig_buf, bw // 2, bh - 1, 0, palette, seed)
        scaled = pygame.transform.smoothscale(
            fig_buf, (bot_rect.width, bot_rect.height - plinth_h))
        surf.blit(scaled, (bot_rect.x,
                           bot_rect.bottom - plinth_h
                           - scaled.get_height()))
        ramp = _palette_blend(_CLAY_RAMP, palette)
        pygame.draw.rect(surf, ramp['shadow'],
                         (bcx - int(bot_rect.width * 1.15) // 2,
                          bot_rect.bottom - plinth_h,
                          int(bot_rect.width * 1.15), plinth_h))
        pygame.draw.line(surf, ramp['lit'],
                         (bcx - int(bot_rect.width * 1.15) // 2,
                          bot_rect.bottom - plinth_h),
                         (bcx + int(bot_rect.width * 1.15) // 2 - 1,
                          bot_rect.bottom - plinth_h), 1)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 4, 12, palette, seed=seed)

    natural_h = max(120, bot_rect.height - plinth_h - 4)

    def draw_into(buf, cx, base_y, top_y):
        _hd_cavalry(buf, cx, base_y, top_y, palette, seed)

    # Horse + rider is asymmetric → flipping vertically AND horizontally
    # mirrors as a paired guardian facing inward, which reads natural.
    _mirror_top(surf, top_rect, natural_h, draw_into,
                mirror_strategy="flip_horizontal")


def candidate_warrior_cavalry(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('warrior_cavalry', _draw_cavalry, surf, top_rect,
                 bot_rect, palette, seed)


# ── 5. Charioteer (御手俑) ────────────────────────────────────────────────
#
# Charioteer standing at attention with both arms forward holding the
# reins. Tall trapezoidal cap (the lower-officer rank signature),
# ceremonial knee-length robe, heavy armour with shoulder pauldrons
# protecting the bow arm, ceremonial sword at left hip. A horizontal
# chariot pole projects forward from the plinth (silhouette cue that
# no other warrior shares).
#
# Research:
#   https://www.travelchinaguide.com/attraction/shaanxi/xian/terra_cotta_army/chariots.htm
#   https://www.travelchinaguide.com/attraction/shaanxi/xian/terra_cotta_army/hairstyle.htm
#   https://en.wikipedia.org/wiki/Terracotta_Army

def _hd_charioteer(buf, cx, base_y, top_y, palette, seed):
    ramp = _palette_blend(_CLAY_RAMP, palette)
    bronze = _palette_blend(_BRONZE_RAMP, palette)
    total = base_y - top_y
    if total < 60 * SS:
        return

    cap_h = max(SS * 13, int(total * 0.18))
    head_h = max(SS * 9, int(total * 0.12))
    neck_h = max(SS * 2, int(total * 0.025))
    torso_h = max(SS * 22, int(total * 0.36))
    skirt_h = max(SS * 14, int(total * 0.22))
    feet_h = total - cap_h - head_h - neck_h - torso_h - skirt_h

    y = base_y

    # ── Forward-projecting chariot pole — drawn FIRST so the figure
    # legs overlap the pole base. Reads as the yoke pole extending
    # from the chariot ahead of the figure.
    pole_y = base_y - int(total * 0.16)
    pole_end_x = cx - int(total * 0.45)
    pygame.draw.line(buf, ramp['deep'],
                     (cx + SS * 3, pole_y),
                     (pole_end_x, pole_y - SS * 3), max(2, SS // 2))
    pygame.draw.line(buf, _shade(ramp['shadow'], 10),
                     (cx + SS * 3, pole_y - SS // 2),
                     (pole_end_x, pole_y - SS * 3 - SS // 2),
                     max(1, SS // 3))
    # Bronze ferrule at the pole tip.
    pygame.draw.circle(buf, bronze['shadow'],
                       (pole_end_x, pole_y - SS * 3), max(2, SS))
    pygame.draw.circle(buf, bronze['lit'],
                       (pole_end_x - SS // 2, pole_y - SS * 3 - SS // 2),
                       max(1, SS // 2))

    # ── Feet.
    shoe_w = max(SS * 10, int(total * 0.16))
    pygame.draw.rect(buf, ramp['deep'],
                     (cx - shoe_w // 2, y - feet_h, shoe_w, feet_h))
    pygame.draw.rect(buf, ramp['shadow'],
                     (cx - shoe_w // 2 + SS // 2, y - feet_h,
                      shoe_w - SS, feet_h - SS // 2))
    pygame.draw.line(buf, ramp['deep'],
                     (cx, y - feet_h + SS), (cx, y - SS), max(1, SS // 2))
    y -= feet_h

    # ── Skirt — knee-length pleated robe.
    skirt_top_w = max(SS * 14, int(total * 0.22))
    skirt_bot_w = max(skirt_top_w + SS * 4, int(total * 0.28))
    pygame.draw.polygon(buf, ramp['shadow'], [
        (cx - skirt_bot_w // 2, y),
        (cx + skirt_bot_w // 2, y),
        (cx + skirt_top_w // 2, y - skirt_h),
        (cx - skirt_top_w // 2, y - skirt_h),
    ])
    pygame.draw.polygon(buf, ramp['body'], [
        (cx - skirt_bot_w // 2 + SS, y - SS),
        (cx + skirt_bot_w // 2 - SS, y - SS),
        (cx + skirt_top_w // 2 - SS, y - skirt_h + SS),
        (cx - skirt_top_w // 2 + SS, y - skirt_h + SS),
    ])
    for k in range(-2, 3):
        fx = cx + k * (skirt_top_w // 5)
        fxb = cx + k * (skirt_bot_w // 5)
        pygame.draw.line(buf, _shade(ramp['shadow'], -10),
                         (fxb, y - SS), (fx, y - skirt_h + SS * 2),
                         max(1, SS // 3))
        pygame.draw.line(buf, ramp['mid'],
                         (fxb - SS // 2, y - SS),
                         (fx - SS // 2, y - skirt_h + SS * 2),
                         max(1, SS // 3))
    # Sash at waist.
    pygame.draw.rect(buf, ramp['ochre'],
                     (cx - skirt_top_w // 2, y - skirt_h - SS,
                      skirt_top_w, SS * 2))
    y -= skirt_h

    # ── Torso + armour.
    torso_w = max(SS * 14, int(total * 0.22))
    armour_top = y - torso_h
    pygame.draw.rect(buf, ramp['shadow'],
                     (cx - torso_w // 2, armour_top, torso_w, torso_h))
    _gradient_fill_rect(buf,
                        pygame.Rect(cx - torso_w // 2 + SS,
                                    armour_top + SS,
                                    torso_w - SS * 2, torso_h - SS * 2),
                        ramp['lit'], ramp['mid'])
    panel = pygame.Rect(cx - torso_w // 2 + SS * 2,
                        armour_top + SS * 3,
                        torso_w - SS * 4, torso_h - SS * 5)
    _draw_armour_panel_hd(buf, panel, ramp, palette,
                          rows=5, cols=3, knot=True)
    # Shoulder pauldrons.
    pad_w = torso_w + SS * 6
    pygame.draw.rect(buf, ramp['shadow'],
                     (cx - pad_w // 2, armour_top - SS, pad_w, SS * 3))
    pygame.draw.rect(buf, ramp['body'],
                     (cx - pad_w // 2 + SS, armour_top - SS,
                      pad_w - SS * 2, SS * 2))
    # ── Both arms extended forward gripping reins — symmetric pair of
    # arms reaching toward the chariot pole.
    for side in (-1, 1):
        sh_x = cx + side * (torso_w // 2 - SS)
        sh_y = armour_top + SS * 3
        hand_x = cx + side * SS - int(total * 0.04)
        hand_y = armour_top + torso_h * 2 // 3 - SS
        pygame.draw.polygon(buf, ramp['shadow'], [
            (sh_x - SS, sh_y),
            (sh_x + SS, sh_y + SS),
            (hand_x + SS, hand_y + SS),
            (hand_x - SS, hand_y),
        ])
        pygame.draw.polygon(buf, ramp['body'], [
            (sh_x, sh_y + SS // 2),
            (sh_x + SS, sh_y + SS),
            (hand_x, hand_y + SS),
            (hand_x - SS // 2, hand_y + SS // 2),
        ])
        # Hand fist.
        pygame.draw.circle(buf, ramp['deep'], (hand_x, hand_y),
                           max(2, SS))
        # Rein lines going forward from each fist.
        pygame.draw.line(buf, ramp['deep'],
                         (hand_x, hand_y),
                         (hand_x - int(total * 0.10),
                          hand_y + SS),
                         max(1, SS // 3))
    # Ceremonial sword at left hip — vertical bronze hilt.
    sword_x = cx - torso_w // 2 - SS
    sword_y = armour_top + torso_h - SS * 3
    pygame.draw.rect(buf, bronze['shadow'],
                     (sword_x - SS, sword_y - SS * 4,
                      SS * 2, SS * 5))
    pygame.draw.rect(buf, bronze['lit'],
                     (sword_x - SS + SS // 2, sword_y - SS * 4,
                      SS, SS * 4))
    # Hilt pommel — round bronze bead.
    pygame.draw.circle(buf, bronze['gold'],
                       (sword_x, sword_y - SS * 4), max(1, SS))
    y = armour_top

    # ── Neck.
    neck_w = max(SS * 4, int(total * 0.07))
    pygame.draw.rect(buf, ramp['shadow'],
                     (cx - neck_w // 2, y - neck_h, neck_w, neck_h))
    pygame.draw.rect(buf, ramp['body'],
                     (cx - neck_w // 2 + SS // 2,
                      y - neck_h, neck_w - SS, neck_h - SS))
    y -= neck_h

    # ── Head + trapezoidal cap.
    head_w = max(SS * 9, int(total * 0.14))
    _draw_warrior_head_hd(buf, cx, y - head_h, head_w, head_h,
                          palette, ramp, beard=True,
                          headgear='trapezoid_cap')


def _draw_charioteer(surf, top_rect, bot_rect, palette, seed):
    bcx = bot_rect.x + bot_rect.width // 2
    plinth_h = 7

    if bot_rect.height > 80:
        bw = bot_rect.width * SS
        bh = (bot_rect.height - plinth_h) * SS
        fig_buf = pygame.Surface((bw, bh), pygame.SRCALPHA)
        _hd_charioteer(fig_buf, bw // 2, bh - 1, 0, palette, seed)
        scaled = pygame.transform.smoothscale(
            fig_buf, (bot_rect.width, bot_rect.height - plinth_h))
        surf.blit(scaled, (bot_rect.x,
                           bot_rect.bottom - plinth_h
                           - scaled.get_height()))
        ramp = _palette_blend(_CLAY_RAMP, palette)
        pygame.draw.rect(surf, ramp['shadow'],
                         (bcx - int(bot_rect.width * 1.18) // 2,
                          bot_rect.bottom - plinth_h,
                          int(bot_rect.width * 1.18), plinth_h))
        pygame.draw.line(surf, ramp['lit'],
                         (bcx - int(bot_rect.width * 1.18) // 2,
                          bot_rect.bottom - plinth_h),
                         (bcx + int(bot_rect.width * 1.18) // 2 - 1,
                          bot_rect.bottom - plinth_h), 1)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 4, 12, palette, seed=seed)

    natural_h = max(120, bot_rect.height - plinth_h - 4)

    def draw_into(buf, cx, base_y, top_y):
        _hd_charioteer(buf, cx, base_y, top_y, palette, seed)

    # Charioteer has the asymmetric forward chariot pole + sword on left
    # hip — a vertical flip would mirror these into nonsense, so re-draw
    # the figure right-side-up in the top slot.
    _mirror_top(surf, top_rect, natural_h, draw_into,
                mirror_strategy="redraw")


def candidate_warrior_charioteer(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('warrior_charioteer', _draw_charioteer, surf,
                 top_rect, bot_rect, palette, seed)


# ── 6. Leshan Giant Buddha (乐山大佛) ─────────────────────────────────────
#
# Tang-dynasty 71m seated Maitreya carved directly INTO red sandstone
# cliff at the river confluence. Iconography: cliff niche framing,
# oversized head + body proportions (the head IS the silhouette top),
# 1021 snail-shell hair curls, ushnisha, long ears, dhyana mudra
# (hands resting palms-up on knees), seated cross-legged with feet on
# a rock ledge (not lotus).
#
# Research:
#   https://en.wikipedia.org/wiki/Leshan_Giant_Buddha
#   https://www.chinaculturetour.com/leshan/top-attractions/leshan-giant-buddha.htm
#   https://www.ancienttravel.org/destinations/leshan-giant-buddha/

def _hd_leshan(buf, cx, base_y, top_y, palette, seed):
    ramp_stone = _palette_blend(_SANDSTONE_RAMP, palette)
    total = base_y - top_y
    if total < 60 * SS:
        return

    # Cliff niche FRAMES the figure — drawn as sedimentary strata
    # excavated by the niche. Niche slightly bigger than the figure so
    # the strata edges show along the outer left + right.
    niche_w = int(total * 0.55)
    niche_h = int(total * 0.95)
    niche_top = top_y + int(total * 0.02)
    _draw_cliff_niche_hd(buf, cx, niche_top + niche_h,
                         niche_w, niche_h, palette,
                         inflate_x=int(total * 0.30),
                         inflate_y=int(total * 0.05))

    # ── Buddha body — sits oversized inside the niche. Head dominates.
    head_w = max(SS * 22, int(total * 0.38))
    head_h = max(SS * 22, int(total * 0.34))
    head_top = niche_top + int(total * 0.04)
    body_top = head_top + head_h
    body_bot = niche_top + niche_h - int(total * 0.04)
    body_h = body_bot - body_top
    body_w = max(SS * 24, int(total * 0.44))

    # Body — wide flat-front torso with robe folds. Two arms drape down
    # to rest on knees.
    body_rect = pygame.Rect(cx - body_w // 2, body_top, body_w, body_h)
    pygame.draw.rect(buf, ramp_stone['shadow'], body_rect)
    _gradient_fill_rect(buf,
                        pygame.Rect(body_rect.x + SS, body_rect.y + SS,
                                    body_rect.w - SS * 2,
                                    body_rect.h - SS * 2),
                        ramp_stone['lit'], ramp_stone['mid'])
    # Robe drape folds — vertical tapered ribbons.
    for k in range(-3, 4):
        fx = cx + k * (body_w // 8)
        pygame.draw.line(buf, _shade(ramp_stone['shadow'], -15),
                         (fx, body_top + SS),
                         (fx + k * SS // 2, body_bot - SS),
                         max(1, SS // 3))
        pygame.draw.line(buf, ramp_stone['mid'],
                         (fx + SS // 2, body_top + SS),
                         (fx + k * SS // 2 + SS // 2, body_bot - SS),
                         max(1, SS // 3))
    # Arms — drawn as inset trapezoids on body sides, hands resting
    # palms up on knees (the dhyana mudra at scale).
    for side in (-1, 1):
        arm_pts = [
            (cx + side * (body_w // 2 - SS), body_top + SS * 4),
            (cx + side * (body_w // 2 + SS * 2), body_top + SS * 6),
            (cx + side * (body_w // 2 + SS * 2), body_bot - SS * 2),
            (cx + side * (body_w // 2 - SS * 3), body_bot - SS * 2),
        ]
        pygame.draw.polygon(buf, ramp_stone['shadow'], arm_pts)
        pygame.draw.polygon(buf, ramp_stone['mid'], [
            (cx + side * (body_w // 2 - SS * 2), body_top + SS * 5),
            (cx + side * (body_w // 2 + SS), body_top + SS * 7),
            (cx + side * (body_w // 2 + SS), body_bot - SS * 3),
            (cx + side * (body_w // 2 - SS * 4), body_bot - SS * 3),
        ])
        # Hand resting on knee — palm-up oval at the bottom of each arm.
        hand_x = cx + side * (body_w // 2 - SS)
        hand_y = body_bot - SS * 2
        pygame.draw.ellipse(buf, ramp_stone['deep'],
                            (hand_x - SS * 3, hand_y - SS,
                             SS * 6, SS * 3))
        pygame.draw.ellipse(buf, ramp_stone['mid'],
                            (hand_x - SS * 3 + SS // 2,
                             hand_y - SS + SS // 2,
                             SS * 5, SS * 2))
    # Salt + algae streaks on body — same weathering language as cliff.
    rng = random.Random(seed + 13)
    for _ in range(5):
        sx = rng.randint(body_rect.x + SS, body_rect.right - SS)
        sy = rng.randint(body_rect.y + SS, body_rect.y + body_rect.h // 2)
        slen = rng.randint(SS * 2, SS * 5)
        for dy in range(slen):
            a = int(85 * (1 - dy / slen))
            buf.set_at((sx, sy + dy), (*ramp_stone['salt'], a))

    # ── Head — oversized, on top of the body. Snail curls, ushnisha,
    # long ears — same Buddha-head archetype, in sandstone material.
    _draw_buddha_head_hd(buf, cx, head_top, head_w, head_h,
                         palette, ramp_stone,
                         ushnisha=True, snail_curls=True,
                         urna=True, half_eyes=True,
                         long_ears=True, halo_radius=0,
                         smiling=False)


def _draw_leshan(surf, top_rect, bot_rect, palette, seed):
    if bot_rect.height > 80:
        bw = bot_rect.width * SS
        bh = bot_rect.height * SS
        fig_buf = pygame.Surface((bw, bh), pygame.SRCALPHA)
        _hd_leshan(fig_buf, bw // 2, bh - 1, 0, palette, seed)
        scaled = pygame.transform.smoothscale(
            fig_buf, (bot_rect.width, bot_rect.height))
        surf.blit(scaled, (bot_rect.x, bot_rect.y))

    natural_h = max(120, bot_rect.height)

    def draw_into(buf, cx, base_y, top_y):
        _hd_leshan(buf, cx, base_y, top_y, palette, seed)

    _mirror_top(surf, top_rect, natural_h, draw_into,
                mirror_strategy="flip")


def candidate_buddha_leshan(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('buddha_leshan', _draw_leshan, surf, top_rect,
                 bot_rect, palette, seed)


# ── 7. Tian Tan Buddha (天坛大佛) ────────────────────────────────────────
#
# Hong Kong's 34m bronze seated Sakyamuni atop a 3-tier circular altar
# modeled on Beijing's Temple of Heaven. Iconography: right hand
# abhaya mudra (palm forward, fingers up) - fearlessness;  left hand
# varada (palm up, fingers down) - granting wishes; robe draped over
# LEFT shoulder leaving right exposed; lotus throne above 3-tier
# circular altar; circle aureole with radial petal rays + central
# wisdom-flame ushnisha. Bronze with selective verdigris in recesses.
#
# Research:
#   https://en.wikipedia.org/wiki/Tian_Tan_Buddha
#   https://www.baldhiker.com/tian-tan-buddha-hong-kong/
#   https://www.visitourchina.com/hong-kong/attraction/tiantan-buddha-statue.html

def _hd_tian_tan(buf, cx, base_y, top_y, palette, seed):
    ramp = _palette_blend(_BRONZE_RAMP, palette)
    total = base_y - top_y
    if total < 60 * SS:
        return

    # Vertical budget: altar 28%, lotus 8%, lap 12%, torso 25%, arms,
    # head 14%, halo behind head.
    altar_h = max(SS * 16, int(total * 0.28))
    lotus_h = max(SS * 6, int(total * 0.08))
    body_h = max(SS * 28, int(total * 0.45))
    head_h = max(SS * 14, int(total * 0.18))

    y = base_y

    # ── 3-tier circular Temple-of-Heaven altar.
    tier_widths = (int(total * 0.85), int(total * 0.70), int(total * 0.55))
    tier_h = altar_h // 3
    for i, tw in enumerate(tier_widths):
        tier_y = y - tier_h
        tier_rect = pygame.Rect(cx - tw // 2, tier_y, tw, tier_h)
        # Round front + back so the tier reads circular at thumbnail.
        pygame.draw.rect(buf, ramp['shadow'], tier_rect)
        _gradient_fill_rect(buf,
                            pygame.Rect(tier_rect.x + SS,
                                        tier_rect.y + SS // 2,
                                        tier_rect.w - SS * 2,
                                        tier_rect.h - SS),
                            ramp['mid'], ramp['shadow'])
        # Circular cap on top so the tier reads round.
        pygame.draw.ellipse(buf, ramp['mid'],
                            (tier_rect.x, tier_rect.y - SS,
                             tier_rect.w, SS * 3))
        pygame.draw.ellipse(buf, ramp['lit'],
                            (tier_rect.x + SS, tier_rect.y - SS // 2,
                             tier_rect.w - SS * 2, SS * 2))
        # Vertical bronze panels — short hatched lines around the tier
        # rim cueing the canonical Temple-of-Heaven balustrade.
        for k in range(8):
            px = tier_rect.x + tier_rect.w * (k + 1) // 9
            pygame.draw.line(buf, ramp['patina'],
                             (px, tier_rect.y + SS),
                             (px, tier_rect.bottom - SS),
                             max(1, SS // 3))
        # Verdigris drips down recess between tiers.
        if i < len(tier_widths) - 1:
            for k in range(4):
                drip_x = tier_rect.x + tier_rect.w * (k * 2 + 1) // 8
                _verdigris_run(buf, drip_x, tier_rect.y + SS // 2,
                               SS * 3, ramp['verdigris'], drips=2)
        y -= tier_h

    # ── Lotus throne above altar.
    lotus_w = int(tier_widths[-1] * 0.85)
    _draw_lotus_throne_hd(buf, cx, y, lotus_w, palette,
                          h=lotus_h * 2, n=9,
                          petal_color=ramp['mid'],
                          edge_color=ramp['shadow'],
                          rim_color=ramp['lit'],
                          gilt_color=ramp['gold'])
    y -= lotus_h

    # ── Seated body. Robe drapes LEFT shoulder leaving right exposed.
    body_w = int(total * 0.46)
    body_rect = pygame.Rect(cx - body_w // 2, y - body_h, body_w, body_h)
    pygame.draw.rect(buf, ramp['shadow'], body_rect)
    _gradient_fill_rect(buf,
                        pygame.Rect(body_rect.x + SS,
                                    body_rect.y + SS,
                                    body_rect.w - SS * 2,
                                    body_rect.h - SS * 2),
                        ramp['lit'], ramp['mid'])
    # Lap fold — horizontal AO band where thighs meet body.
    lap_y = body_rect.y + body_rect.h * 2 // 3
    _ao_under(buf, cx, lap_y, body_w - SS * 2, SS * 3, ramp['patina'])
    # Robe drape over LEFT shoulder — diagonal sash across body.
    drape_pts = [
        (body_rect.x + SS, body_rect.y + SS),
        (body_rect.x + body_rect.w // 2, body_rect.y + SS * 3),
        (body_rect.x + body_rect.w * 3 // 4,
         body_rect.y + body_rect.h * 2 // 3),
        (body_rect.x + body_rect.w * 3 // 4 + SS * 2,
         body_rect.y + body_rect.h - SS * 2),
        (body_rect.x + body_rect.w // 3,
         body_rect.y + body_rect.h - SS * 2),
        (body_rect.x + SS,
         body_rect.y + body_rect.h * 2 // 3),
    ]
    pygame.draw.polygon(buf, ramp['mid'], drape_pts)
    pygame.draw.lines(buf, ramp['lit'], False, drape_pts[:4],
                      max(1, SS // 3))
    # Right shoulder bare — slight shadow indent on the right.
    pygame.draw.ellipse(buf, ramp['shadow'],
                        (body_rect.right - SS * 4, body_rect.y + SS,
                         SS * 6, SS * 6))
    pygame.draw.ellipse(buf, ramp['mid'],
                        (body_rect.right - SS * 4 + SS,
                         body_rect.y + SS * 2,
                         SS * 4, SS * 4))
    # ── Right arm — abhaya mudra. Bent at elbow, hand raised in front
    # of chest, palm forward, fingers UP. The defining gesture.
    abhaya_x = cx - body_w // 4
    abhaya_y = body_rect.y - SS * 3
    pygame.draw.polygon(buf, ramp['shadow'], [
        (body_rect.x + body_rect.w * 3 // 5, body_rect.y + SS * 3),
        (body_rect.x + body_rect.w * 3 // 5 + SS * 3, body_rect.y + SS * 5),
        (abhaya_x + SS * 4, abhaya_y + SS * 8),
        (abhaya_x + SS, abhaya_y + SS * 4),
    ])
    pygame.draw.polygon(buf, ramp['mid'], [
        (body_rect.x + body_rect.w * 3 // 5, body_rect.y + SS * 4),
        (body_rect.x + body_rect.w * 3 // 5 + SS * 2, body_rect.y + SS * 5),
        (abhaya_x + SS * 3, abhaya_y + SS * 8),
        (abhaya_x + SS, abhaya_y + SS * 5),
    ])
    # Hand — palm up, fingers extended vertical.
    palm_rect = pygame.Rect(abhaya_x - SS, abhaya_y, SS * 6, SS * 8)
    pygame.draw.ellipse(buf, ramp['shadow'], palm_rect)
    pygame.draw.ellipse(buf, ramp['mid'], palm_rect.inflate(-SS, -SS))
    # Four fingers — short vertical bars on top of palm.
    for k in range(4):
        fx = palm_rect.x + SS + k * (palm_rect.w - SS * 2) // 4
        pygame.draw.line(buf, ramp['lit'],
                         (fx + SS // 2, palm_rect.y + SS),
                         (fx + SS // 2, palm_rect.y - SS * 2),
                         max(1, SS // 2))
        pygame.draw.line(buf, ramp['shadow'],
                         (fx, palm_rect.y + SS),
                         (fx, palm_rect.y - SS * 2),
                         max(1, SS // 3))
    # Specular at palm-centre.
    _specular_dot(buf, palm_rect.x + palm_rect.w // 2,
                  palm_rect.y + palm_rect.h // 2,
                  max(1, SS // 3), ramp['specular'])

    # ── Left arm — varada mudra. Drapes down to LEFT KNEE, palm up,
    # fingers extended DOWN. Bestowal of blessings gesture.
    varada_x = cx + body_w // 4 + SS
    varada_y = body_rect.y + body_rect.h * 5 // 6
    pygame.draw.polygon(buf, ramp['shadow'], [
        (body_rect.x + body_rect.w * 2 // 5, body_rect.y + SS * 3),
        (body_rect.x + body_rect.w // 4, body_rect.y + SS * 6),
        (varada_x - SS * 2, varada_y - SS),
        (varada_x + SS, varada_y - SS * 4),
    ])
    pygame.draw.polygon(buf, ramp['mid'], [
        (body_rect.x + body_rect.w * 2 // 5, body_rect.y + SS * 4),
        (body_rect.x + body_rect.w // 4, body_rect.y + SS * 7),
        (varada_x - SS * 2, varada_y - SS * 2),
        (varada_x + SS, varada_y - SS * 4),
    ])
    # Hand on knee — palm-up oval with downward-extending fingers.
    pygame.draw.ellipse(buf, ramp['shadow'],
                        (varada_x - SS * 3, varada_y,
                         SS * 6, SS * 3))
    pygame.draw.ellipse(buf, ramp['mid'],
                        (varada_x - SS * 2, varada_y + SS // 2,
                         SS * 4, SS * 2))
    # Fingers DOWN.
    for k in range(4):
        fx = varada_x - SS * 2 + k * SS + SS // 2
        pygame.draw.line(buf, ramp['shadow'],
                         (fx, varada_y + SS * 3),
                         (fx, varada_y + SS * 5),
                         max(1, SS // 3))

    # Verdigris on body recesses — selective patina in deep folds only,
    # not on raised surfaces.
    for k in range(3):
        _verdigris_run(buf, body_rect.x + SS * 4 + k * SS * 6,
                       body_rect.y + body_rect.h // 2,
                       SS * 4, ramp['verdigris'], drips=2)

    # ── Head + halo + ushnisha.
    head_w = max(SS * 14, int(total * 0.22))
    halo_r = int(head_w * 0.85)
    _draw_buddha_head_hd(buf, cx, y - body_h - head_h + SS * 2,
                         head_w, head_h, palette, ramp,
                         ushnisha=True, snail_curls=True,
                         urna=True, half_eyes=True,
                         long_ears=True, halo_radius=halo_r,
                         smiling=False)


def _draw_tian_tan(surf, top_rect, bot_rect, palette, seed):
    if bot_rect.height > 80:
        bw = bot_rect.width * SS
        bh = bot_rect.height * SS
        fig_buf = pygame.Surface((bw, bh), pygame.SRCALPHA)
        _hd_tian_tan(fig_buf, bw // 2, bh - 1, 0, palette, seed)
        scaled = pygame.transform.smoothscale(
            fig_buf, (bot_rect.width, bot_rect.height))
        surf.blit(scaled, (bot_rect.x, bot_rect.y))

    natural_h = max(120, bot_rect.height)

    def draw_into(buf, cx, base_y, top_y):
        _hd_tian_tan(buf, cx, base_y, top_y, palette, seed)

    _mirror_top(surf, top_rect, natural_h, draw_into,
                mirror_strategy="flip")


def candidate_buddha_tian_tan(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('buddha_tian_tan', _draw_tian_tan, surf, top_rect,
                 bot_rect, palette, seed)


# ── 8. Standing Maitreya / Budai (彌勒佛 / 布袋) ────────────────────────────
#
# The Laughing Buddha — round exposed belly, broad grin + closed-curve
# laughing eyes, long ear lobes, saffron-orange monastic robe LEFT
# shoulder bare, cloth sack carried in one hand (or set beside), arms
# raised up in welcome. Gilt-bronze finish with visible red-lacquer
# wear cracks. Stands on a small lotus throne (smaller than Tian Tan's).
#
# Research:
#   https://en.wikipedia.org/wiki/Budai
#   https://butuzou.com/blogs/blog/chinese-maitreya-laughing-buddha
#   https://religion.utk.edu/megan-bryson-in-the-conversation-who-is-the-laughing-buddha-a-scholar-of-east-asian-buddhism-explains/

def _hd_maitreya(buf, cx, base_y, top_y, palette, seed):
    ramp = _palette_blend(_GILT_RAMP, palette)
    total = base_y - top_y
    if total < 60 * SS:
        return

    lotus_h = max(SS * 6, int(total * 0.08))
    feet_h = max(SS * 3, int(total * 0.05))
    robe_h = max(SS * 14, int(total * 0.24))
    belly_h = max(SS * 12, int(total * 0.20))
    chest_h = max(SS * 10, int(total * 0.16))
    head_h = max(SS * 12, int(total * 0.17))

    y = base_y

    # ── Lotus throne — smaller than Tian Tan's, gilt-rim petals.
    lotus_w = int(total * 0.55)
    _draw_lotus_throne_hd(buf, cx, y, lotus_w, palette,
                          h=lotus_h * 2, n=9,
                          petal_color=ramp['mid'],
                          edge_color=ramp['shadow'],
                          rim_color=ramp['lit'],
                          gilt_color=ramp['lit'])
    y -= lotus_h

    # ── Bare feet poking out of robe.
    foot_w = int(total * 0.11)
    for off in (-foot_w + SS, foot_w - SS):
        pygame.draw.ellipse(buf, ramp['shadow'],
                            (cx + off - foot_w // 2, y - feet_h,
                             foot_w, feet_h * 2))
        pygame.draw.ellipse(buf, ramp['mid'],
                            (cx + off - foot_w // 2 + SS // 2,
                             y - feet_h + SS // 2,
                             foot_w - SS, feet_h * 2 - SS))
    y -= feet_h

    # ── Lower robe — flared trapezoid bell.
    robe_top_w = int(total * 0.30)
    robe_bot_w = int(total * 0.45)
    pygame.draw.polygon(buf, ramp['shadow'], [
        (cx - robe_bot_w // 2, y),
        (cx + robe_bot_w // 2, y),
        (cx + robe_top_w // 2, y - robe_h),
        (cx - robe_top_w // 2, y - robe_h),
    ])
    pygame.draw.polygon(buf, ramp['mid'], [
        (cx - robe_bot_w // 2 + SS, y - SS),
        (cx + robe_bot_w // 2 - SS, y - SS),
        (cx + robe_top_w // 2 - SS, y - robe_h + SS),
        (cx - robe_top_w // 2 + SS, y - robe_h + SS),
    ])
    # Gold wear cracks revealing red lacquer underbase.
    for k in range(4):
        cx_a = cx + (k - 2) * (robe_top_w // 5)
        cy_a = y - robe_h // 3 - k * SS
        _gilt_wear_crack(buf, cx_a, cy_a,
                         cx_a + SS * 2, cy_a + SS * 3, ramp['lacquer'])
    # Robe drape folds.
    for k in range(-2, 3):
        fx = cx + k * (robe_top_w // 5)
        fxb = cx + k * (robe_bot_w // 5)
        pygame.draw.line(buf, _shade(ramp['shadow'], -15),
                         (fxb, y - SS), (fx, y - robe_h + SS),
                         max(1, SS // 3))
        pygame.draw.line(buf, ramp['lit'],
                         (fxb + SS // 2, y - SS),
                         (fx + SS // 2, y - robe_h + SS),
                         max(1, SS // 3))
    y -= robe_h

    # ── Big round laughing belly. Bare flesh + saffron robe tied at
    # the WAIST (below belly). The defining Budai silhouette feature.
    belly_w = int(total * 0.50)
    belly_rect = pygame.Rect(cx - belly_w // 2, y - belly_h,
                             belly_w, belly_h + SS * 2)
    pygame.draw.ellipse(buf, ramp['shadow'], belly_rect)
    # Highlight gradient on upper-left of belly.
    pygame.draw.ellipse(buf, ramp['mid'],
                        belly_rect.inflate(-SS, -SS))
    g = pygame.Surface((belly_w, belly_h), pygame.SRCALPHA)
    for k in range(belly_w // 3, 0, -1):
        a = int(110 * (k / (belly_w / 3)))
        pygame.draw.ellipse(g, (*ramp['lit'], a),
                            ((belly_w - k * 2) // 2,
                             (belly_h - k) // 3, k * 2, k))
    buf.blit(g, (belly_rect.x + SS, belly_rect.y + SS))
    # Belly button.
    pygame.draw.circle(buf, ramp['shadow'],
                       (cx, y - belly_h // 2),
                       max(1, SS))
    # Saffron robe sash tied at waist, draped low.
    saffron = _mix(palette['stone_accent'], (220, 138, 52), 0.72)
    sash_y = y - SS * 2
    pygame.draw.polygon(buf, saffron, [
        (cx - belly_w // 2, sash_y),
        (cx + belly_w // 2, sash_y),
        (cx + belly_w // 2 - SS, sash_y + SS * 4),
        (cx - belly_w // 2 + SS, sash_y + SS * 4),
    ])
    pygame.draw.polygon(buf, _shade(saffron, -25), [
        (cx - belly_w // 2, sash_y + SS * 4),
        (cx + belly_w // 2, sash_y + SS * 4),
        (cx + belly_w // 2 - SS, sash_y + SS * 5),
        (cx - belly_w // 2 + SS, sash_y + SS * 5),
    ])
    # Specular hot-spot on belly.
    _specular_dot(buf, cx - belly_w // 4, y - belly_h * 2 // 3,
                  max(1, SS // 3), ramp['specular'])
    y -= belly_h

    # ── Upper chest + arms raised up in welcome (both arms up + out).
    chest_w = int(total * 0.42)
    chest_top = y - chest_h
    pygame.draw.rect(buf, ramp['shadow'],
                     (cx - chest_w // 2, chest_top, chest_w, chest_h))
    _gradient_fill_rect(buf,
                        pygame.Rect(cx - chest_w // 2 + SS,
                                    chest_top + SS,
                                    chest_w - SS * 2, chest_h - SS),
                        ramp['lit'], ramp['mid'])
    # Saffron sash diagonal across LEFT shoulder.
    pygame.draw.polygon(buf, saffron, [
        (cx - chest_w // 2, chest_top + SS),
        (cx - chest_w // 4, chest_top - SS),
        (cx + chest_w // 4, chest_top + chest_h),
        (cx + SS, chest_top + chest_h + SS),
    ])
    # ── Both arms raised — symmetric welcome pose.
    for side in (-1, 1):
        sh_x = cx + side * (chest_w // 2 - SS)
        sh_y = chest_top + SS * 2
        hand_x = cx + side * (chest_w // 2 + SS * 6)
        hand_y = chest_top - SS * 4
        pygame.draw.polygon(buf, ramp['shadow'], [
            (sh_x - SS, sh_y),
            (sh_x + SS, sh_y + SS),
            (hand_x + side * SS, hand_y + SS * 2),
            (hand_x - side * SS, hand_y - SS),
        ])
        pygame.draw.polygon(buf, ramp['mid'], [
            (sh_x - SS // 2, sh_y + SS // 2),
            (sh_x + SS // 2, sh_y + SS),
            (hand_x + side * SS // 2, hand_y + SS),
            (hand_x - side * SS // 2, hand_y),
        ])
        # Hand — palm raised.
        hand_rect = pygame.Rect(hand_x - SS * 2, hand_y - SS * 2,
                                SS * 4, SS * 5)
        pygame.draw.ellipse(buf, ramp['shadow'], hand_rect)
        pygame.draw.ellipse(buf, ramp['mid'], hand_rect.inflate(-SS, -SS))
        # 4 raised fingers.
        for k in range(4):
            fx = hand_rect.x + SS + k * (hand_rect.w - SS * 2) // 4
            pygame.draw.line(buf, ramp['lit'],
                             (fx + SS // 2, hand_rect.y + SS),
                             (fx + SS // 2, hand_rect.y - SS),
                             max(1, SS // 2))

    # ── Head + halo. Smiling crescent eyes.
    head_w = max(SS * 14, int(total * 0.22))
    halo_r = int(head_w * 0.75)
    _draw_buddha_head_hd(buf, cx, chest_top - head_h + SS * 2,
                         head_w, head_h, palette, ramp,
                         ushnisha=True, snail_curls=False,  # Budai is bald
                         urna=False, half_eyes=False,
                         long_ears=True, halo_radius=halo_r,
                         smiling=True)


def _draw_maitreya(surf, top_rect, bot_rect, palette, seed):
    if bot_rect.height > 80:
        bw = bot_rect.width * SS
        bh = bot_rect.height * SS
        fig_buf = pygame.Surface((bw, bh), pygame.SRCALPHA)
        _hd_maitreya(fig_buf, bw // 2, bh - 1, 0, palette, seed)
        scaled = pygame.transform.smoothscale(
            fig_buf, (bot_rect.width, bot_rect.height))
        surf.blit(scaled, (bot_rect.x, bot_rect.y))

    natural_h = max(120, bot_rect.height)

    def draw_into(buf, cx, base_y, top_y):
        _hd_maitreya(buf, cx, base_y, top_y, palette, seed)

    _mirror_top(surf, top_rect, natural_h, draw_into,
                mirror_strategy="flip")


def candidate_buddha_maitreya(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('buddha_maitreya', _draw_maitreya, surf, top_rect,
                 bot_rect, palette, seed)


# ── 9. Cliff-Niche Reclining Buddha (涅槃·龕) ──────────────────────────────
#
# Yungang Cave 5 archetype — horizontal Parinirvana figure carved into
# a horizontal niche in a sandstone cliff. Saffron-sash diagonal across
# the body, head propped on a pillow on the right, bare feet soles
# forward on the left, halo behind the head, gilt-leaf wear on robe
# borders revealing red lacquer underbase.
#
# Research:
#   https://en.wikipedia.org/wiki/Yungang_Grottoes
#   https://en.wikipedia.org/wiki/Reclining_Buddha
#   https://www.britannica.com/place/Yungang-caves

def _hd_niche_reclining(buf, cx, base_y, top_y, palette, seed):
    ramp_stone = _palette_blend(_SANDSTONE_RAMP, palette)
    ramp_gold = _palette_blend(_GOLD_LEAF_RAMP, palette)
    total = base_y - top_y
    if total < 60 * SS:
        return

    # The cliff dominates: vertical strata column fills the whole
    # pillar, with a horizontal niche carved into the LOWER half.
    cliff_rect = pygame.Rect(cx - int(total * 0.45),
                             top_y,
                             int(total * 0.90), total)
    # Strata bands fill the cliff.
    band_seeds = (0.18, 0.10, 0.22, 0.08, 0.14, 0.18, 0.10)
    norm = sum(band_seeds)
    y_a = cliff_rect.bottom
    bands = []
    for sb in band_seeds:
        bh = max(SS * 2, int(cliff_rect.height * (sb / norm)))
        bands.append((y_a - bh, bh))
        y_a -= bh
    if y_a > cliff_rect.y:
        last_y, last_h = bands[-1]
        bands[-1] = (cliff_rect.y, last_h + (last_y - cliff_rect.y))
    for i, (by, bh) in enumerate(bands):
        t = i / max(1, len(bands) - 1)
        body = _mix(ramp_stone['mid'], ramp_stone['shadow'], t * 0.50)
        top_edge = _mix(ramp_stone['lit'], ramp_stone['mid'], t * 0.45)
        crack = _shade(body, -28)
        _strata_band(buf, pygame.Rect(cliff_rect.x, by,
                                       cliff_rect.width, bh),
                     body, top_edge, crack)
    # Erosion + algae.
    rng = random.Random(seed + 17)
    for _ in range(8):
        sx = rng.randint(cliff_rect.x + SS, cliff_rect.right - SS)
        sy = rng.randint(cliff_rect.y + cliff_rect.h // 2,
                         cliff_rect.bottom - SS)
        slen = rng.randint(SS * 2, SS * 6)
        for dy in range(slen):
            a = int(120 * (1 - dy / slen))
            buf.set_at((sx, sy + dy), (*ramp_stone['algae'], a))

    # ── Horizontal niche carved into the lower half of the cliff.
    niche_h = int(total * 0.36)
    niche_w = int(cliff_rect.width * 0.95)
    niche_top = cliff_rect.y + int(total * 0.40)
    niche_rect = pygame.Rect(cx - niche_w // 2, niche_top,
                             niche_w, niche_h)
    inner = _shade(ramp_stone['deep'], -10)
    # Niche is a horizontal arched recess — flat bottom + half-circle arc
    # both ends.
    arc_r = niche_h // 2
    pygame.draw.rect(buf, inner,
                     (niche_rect.x + arc_r, niche_rect.y,
                      niche_rect.w - arc_r * 2, niche_rect.h))
    pygame.draw.ellipse(buf, inner,
                        (niche_rect.x, niche_rect.y,
                         arc_r * 2, niche_rect.h))
    pygame.draw.ellipse(buf, inner,
                        (niche_rect.right - arc_r * 2, niche_rect.y,
                         arc_r * 2, niche_rect.h))
    # Niche rim darks.
    pygame.draw.line(buf, _shade(inner, -25),
                     (niche_rect.x + arc_r, niche_rect.y),
                     (niche_rect.right - arc_r, niche_rect.y),
                     max(1, SS // 3))

    # ── Halo BEHIND head — light hot circle on the right side of niche.
    head_cx = niche_rect.right - arc_r - SS * 2
    head_cy = niche_rect.y + niche_rect.h // 2
    halo_r = niche_h // 2 - SS
    halo_rim = _mix(palette['stone_accent'], (255, 220, 130), 0.80)
    glow_a = 150 if _is_dark_sky(palette) else 90
    _soft_glow(buf, head_cx, head_cy, halo_r, halo_rim, glow_a)

    # ── Reclining figure — horizontal body filling the niche, head
    # propped on a pillow on the RIGHT, feet on the LEFT.
    body_left = niche_rect.x + arc_r // 2
    body_right = niche_rect.right - arc_r - SS * 4
    body_w = body_right - body_left
    body_y = niche_rect.y + niche_rect.h // 2
    body_h = niche_rect.h // 3
    # Body — long oval pill.
    body_pill = pygame.Rect(body_left, body_y - body_h // 2,
                            body_w, body_h)
    pygame.draw.rect(buf, ramp_gold['shadow'],
                     (body_pill.x + body_h // 2, body_pill.y,
                      body_pill.w - body_h, body_pill.h))
    pygame.draw.ellipse(buf, ramp_gold['shadow'],
                        (body_pill.x, body_pill.y,
                         body_h, body_pill.h))
    pygame.draw.ellipse(buf, ramp_gold['shadow'],
                        (body_pill.right - body_h, body_pill.y,
                         body_h, body_pill.h))
    # Gradient inside.
    _gradient_fill_rect(buf,
                        pygame.Rect(body_pill.x + SS,
                                    body_pill.y + SS,
                                    body_pill.w - SS * 2,
                                    body_pill.h - SS * 2),
                        ramp_gold['lit'], ramp_gold['mid'])
    # Diagonal saffron sash across body — red-orange wide stripe.
    saffron = _mix(palette['stone_accent'], (220, 138, 52), 0.78)
    sash_pts = [
        (body_pill.x + SS * 3, body_pill.y + SS),
        (body_pill.x + body_pill.w * 2 // 3, body_pill.y + body_pill.h - SS),
        (body_pill.x + body_pill.w * 2 // 3 + SS * 2,
         body_pill.y + body_pill.h - SS),
        (body_pill.x + SS * 5, body_pill.y + SS),
    ]
    pygame.draw.polygon(buf, saffron, sash_pts)
    pygame.draw.polygon(buf, _shade(saffron, -25), [
        (body_pill.x + SS * 5, body_pill.y + SS),
        (body_pill.x + body_pill.w * 2 // 3 + SS * 2,
         body_pill.y + body_pill.h - SS),
        (body_pill.x + body_pill.w * 2 // 3 + SS,
         body_pill.y + body_pill.h - SS),
        (body_pill.x + SS * 4, body_pill.y + SS),
    ])
    # Gilt border along robe edge — bright gold stripe top + bottom.
    pygame.draw.line(buf, ramp_gold['lit'],
                     (body_pill.x + SS * 2, body_pill.y),
                     (body_pill.right - SS * 2, body_pill.y),
                     max(1, SS // 2))
    pygame.draw.line(buf, ramp_gold['lit'],
                     (body_pill.x + SS * 2, body_pill.bottom - 1),
                     (body_pill.right - SS * 2, body_pill.bottom - 1),
                     max(1, SS // 2))
    # Gilt wear-cracks revealing red lacquer.
    for k in range(5):
        cx_a = body_pill.x + SS * 3 + k * (body_pill.w // 5)
        cy_a = body_pill.y + body_pill.h // 2 - SS
        _gilt_wear_crack(buf, cx_a, cy_a, cx_a + SS, cy_a + SS * 2,
                         ramp_gold['lacquer'])
    # Specular highlight on shoulder + knee.
    _specular_dot(buf, body_pill.x + body_pill.w // 3, body_pill.y + SS,
                  max(1, SS // 3), ramp_gold['specular'])
    _specular_dot(buf, body_pill.x + body_pill.w * 2 // 3,
                  body_pill.y + body_pill.h // 2,
                  max(1, SS // 3), ramp_gold['specular'])
    # ── Feet at LEFT end — two soles facing forward (the canonical
    # Parinirvana cue).
    feet_x = body_pill.x - SS
    pygame.draw.ellipse(buf, ramp_gold['shadow'],
                        (feet_x - SS * 3, body_y - body_h // 3,
                         SS * 6, body_h * 2 // 3))
    pygame.draw.ellipse(buf, ramp_gold['mid'],
                        (feet_x - SS * 2, body_y - body_h // 3 + SS // 2,
                         SS * 4, body_h * 2 // 3 - SS))
    # Toe lines.
    for k in range(4):
        ty = body_y - body_h // 4 + k * (body_h // 8)
        pygame.draw.line(buf, ramp_gold['shadow'],
                         (feet_x - SS * 3, ty),
                         (feet_x - SS * 2, ty), max(1, SS // 3))
    # ── Head propped on pillow at RIGHT end. Head is a Buddha head in
    # gold material, slightly tilted.
    head_w = int(body_h * 1.6)
    head_h = int(body_h * 1.4)
    head_top = head_cy - head_h // 2 - SS
    head_left = head_cx - head_w // 2
    # Pillow under head — small rounded cushion.
    pillow_rect = pygame.Rect(head_left - SS,
                              head_cy + head_h // 3,
                              head_w + SS * 2, SS * 4)
    pygame.draw.ellipse(buf, ramp_stone['mid'], pillow_rect)
    pygame.draw.ellipse(buf, ramp_stone['lit'],
                        pillow_rect.inflate(-SS, -SS))
    pygame.draw.line(buf, ramp_stone['shadow'],
                     (pillow_rect.x + SS, pillow_rect.bottom - SS),
                     (pillow_rect.right - SS, pillow_rect.bottom - SS),
                     max(1, SS // 3))
    # Head itself.
    _draw_buddha_head_hd(buf, head_cx, head_top, head_w, head_h,
                         palette, ramp_gold,
                         ushnisha=True, snail_curls=True,
                         urna=True, half_eyes=True,
                         long_ears=True, halo_radius=0,
                         smiling=False)


def _draw_niche_reclining(surf, top_rect, bot_rect, palette, seed):
    if bot_rect.height > 80:
        bw = bot_rect.width * SS
        bh = bot_rect.height * SS
        fig_buf = pygame.Surface((bw, bh), pygame.SRCALPHA)
        _hd_niche_reclining(fig_buf, bw // 2, bh - 1, 0, palette, seed)
        scaled = pygame.transform.smoothscale(
            fig_buf, (bot_rect.width, bot_rect.height))
        surf.blit(scaled, (bot_rect.x, bot_rect.y))

    natural_h = max(120, bot_rect.height)

    def draw_into(buf, cx, base_y, top_y):
        _hd_niche_reclining(buf, cx, base_y, top_y, palette, seed)

    # The horizontal niche + figure orientation is asymmetric → vertical
    # flip would invert the head + feet positions into nonsense. Re-draw
    # right-side-up in the top slot so the upper figure is a second
    # paired niche carved into the same cliff.
    _mirror_top(surf, top_rect, natural_h, draw_into,
                mirror_strategy="redraw")


def candidate_buddha_niche_reclining(surf, top_rect, bot_rect,
                                      palette, seed):
    _cached_draw('buddha_niche_reclining', _draw_niche_reclining,
                 surf, top_rect, bot_rect, palette, seed)


# ── 10. Guanyin / Avalokiteśvara (觀音) ──────────────────────────────────
#
# Dehua white-porcelain (blanc de chine) Guanyin — slender hourglass
# body, flame-spire diadem with tiny Amitabha Buddha effigy at centre,
# water-vase held in LEFT hand at hip, willow branch in RIGHT hand
# raised, cool silk sash from left shoulder, flame-tipped aureole
# behind head, cobalt-fired eye dots + tiny gilt brushwork on robe
# borders. Stands on a small lotus throne.
#
# Research:
#   https://en.wikipedia.org/wiki/Dehua_porcelain
#   https://en.wikipedia.org/wiki/Guanyin
#   https://www.metmuseum.org/art/collection/search/61509
#   https://www.chinafurnitureonline.com/guanyin-chinese-bodhisattva

def _hd_guanyin(buf, cx, base_y, top_y, palette, seed):
    ramp = _palette_blend(_PORCELAIN_RAMP, palette)
    total = base_y - top_y
    if total < 60 * SS:
        return

    lotus_h = max(SS * 5, int(total * 0.07))
    feet_h = max(SS * 2, int(total * 0.03))
    robe_h = max(SS * 16, int(total * 0.30))
    waist_h = max(SS * 4, int(total * 0.06))
    chest_h = max(SS * 10, int(total * 0.16))
    neck_h = max(SS * 2, int(total * 0.025))
    head_h = max(SS * 11, int(total * 0.15))
    diadem_h = max(SS * 8, int(total * 0.11))

    y = base_y

    # ── Lotus throne — small.
    lotus_w = int(total * 0.45)
    petal = ramp['warm_rim']
    _draw_lotus_throne_hd(buf, cx, y, lotus_w, palette,
                          h=lotus_h * 2, n=9,
                          petal_color=petal,
                          edge_color=ramp['shadow'],
                          rim_color=ramp['lit'],
                          gilt_color=ramp['gilt'])
    y -= lotus_h

    # ── Feet under robe hem.
    y -= feet_h

    # ── Lower robe — slim trapezoid (slender hourglass), with vertical
    # silk-fold creases. Porcelain glow at the bottom hem.
    robe_top_w = int(total * 0.18)
    robe_bot_w = int(total * 0.40)
    pygame.draw.polygon(buf, ramp['shadow'], [
        (cx - robe_bot_w // 2, y),
        (cx + robe_bot_w // 2, y),
        (cx + robe_top_w // 2, y - robe_h),
        (cx - robe_top_w // 2, y - robe_h),
    ])
    pygame.draw.polygon(buf, ramp['body'], [
        (cx - robe_bot_w // 2 + SS, y - SS),
        (cx + robe_bot_w // 2 - SS, y - SS),
        (cx + robe_top_w // 2 - SS, y - robe_h + SS),
        (cx - robe_top_w // 2 + SS, y - robe_h + SS),
    ])
    # Warm rim along the hem — subsurface scattering cue on porcelain.
    pygame.draw.line(buf, ramp['warm_rim'],
                     (cx - robe_bot_w // 2 + SS, y - SS),
                     (cx + robe_bot_w // 2 - SS, y - SS),
                     max(1, SS // 2))
    # Silk-fold lines, more numerous than other Buddhas.
    for k in range(-3, 4):
        fx = cx + k * (robe_top_w // 7)
        fxb = cx + k * (robe_bot_w // 7)
        pygame.draw.line(buf, ramp['mid'],
                         (fxb, y - SS),
                         (fx, y - robe_h + SS * 2),
                         max(1, SS // 3))
        pygame.draw.line(buf, ramp['lit'],
                         (fxb - SS // 2, y - SS),
                         (fx - SS // 2, y - robe_h + SS * 2),
                         max(1, SS // 3))
    # Gilt brushwork along the hem — fine gold band.
    pygame.draw.line(buf, ramp['gilt'],
                     (cx - robe_bot_w // 2 + SS * 2, y - SS * 2),
                     (cx + robe_bot_w // 2 - SS * 2, y - SS * 2),
                     max(1, SS // 3))
    # Hairline crackle over the body.
    _crackle_lines(buf, pygame.Rect(cx - robe_top_w // 2, y - robe_h,
                                     robe_top_w, robe_h),
                   _shade(ramp['shadow'], -10),
                   density=5, seed=seed)
    y -= robe_h

    # ── Waist — narrow.
    waist_w = int(total * 0.14)
    pygame.draw.rect(buf, ramp['shadow'],
                     (cx - waist_w // 2, y - waist_h, waist_w, waist_h))
    pygame.draw.rect(buf, ramp['body'],
                     (cx - waist_w // 2 + SS // 2, y - waist_h,
                      waist_w - SS, waist_h - SS))
    # Vase held in LEFT hand at hip — bulbous white porcelain pot with
    # cobalt rim.
    vase_x = cx - int(total * 0.22)
    vase_y = y - waist_h
    vase_w = int(total * 0.10)
    vase_h = int(total * 0.14)
    pygame.draw.ellipse(buf, ramp['shadow'],
                        (vase_x - vase_w // 2,
                         vase_y - vase_h // 2,
                         vase_w, vase_h))
    pygame.draw.ellipse(buf, ramp['body'],
                        (vase_x - vase_w // 2 + SS // 2,
                         vase_y - vase_h // 2 + SS // 2,
                         vase_w - SS, vase_h - SS))
    # Vase neck — short cylinder at top with cobalt rim.
    pygame.draw.rect(buf, ramp['shadow'],
                     (vase_x - vase_w // 4,
                      vase_y - vase_h // 2 - SS * 2,
                      vase_w // 2, SS * 3))
    pygame.draw.line(buf, ramp['cobalt'],
                     (vase_x - vase_w // 4,
                      vase_y - vase_h // 2 - SS * 2),
                     (vase_x + vase_w // 4,
                      vase_y - vase_h // 2 - SS * 2),
                     max(1, SS // 2))
    # Vase specular hot-spot.
    _specular_dot(buf, vase_x - SS, vase_y - SS,
                  max(1, SS // 3), ramp['specular'])
    # Water trickle — tiny blue droplet stream falling from vase mouth
    # toward the lotus base.
    for k in range(6):
        dy = vase_y - vase_h // 2 - SS + k * SS * 2
        if dy < y:
            buf.set_at((vase_x, dy), ramp['cobalt'])
    # Left hand cradling vase.
    pygame.draw.ellipse(buf, ramp['mid'],
                        (vase_x - SS * 2, vase_y + vase_h // 3,
                         SS * 4, SS * 3))
    y -= waist_h

    # ── Chest — slender torso. Cool silk sash from LEFT shoulder.
    chest_w = int(total * 0.22)
    chest_top = y - chest_h
    pygame.draw.rect(buf, ramp['shadow'],
                     (cx - chest_w // 2, chest_top, chest_w, chest_h))
    _gradient_fill_rect(buf,
                        pygame.Rect(cx - chest_w // 2 + SS,
                                    chest_top + SS,
                                    chest_w - SS * 2, chest_h - SS),
                        ramp['lit'], ramp['body'])
    # Silk sash across left shoulder.
    sash_color = _mix(ramp['mid'], ramp['cobalt'], 0.20)
    pygame.draw.polygon(buf, sash_color, [
        (cx - chest_w // 2 - SS, chest_top),
        (cx - chest_w // 4, chest_top - SS * 2),
        (cx + chest_w // 4, chest_top + chest_h),
        (cx - chest_w // 4, chest_top + chest_h + SS * 2),
    ])
    # Sash rim — bright porcelain edge.
    pygame.draw.line(buf, ramp['lit'],
                     (cx - chest_w // 2 - SS, chest_top),
                     (cx + chest_w // 4, chest_top + chest_h),
                     max(1, SS // 3))
    # Gilt brushwork along sash.
    pygame.draw.line(buf, ramp['gilt'],
                     (cx - chest_w // 4, chest_top - SS),
                     (cx + chest_w // 4 - SS, chest_top + chest_h - SS),
                     max(1, SS // 3))
    # Right arm raised holding willow branch.
    willow_color = _mix(ramp['mid'], (120, 168, 130), 0.50)
    willow_dark = _shade(willow_color, -40)
    # Arm — bent up, hand near shoulder.
    branch_hand_x = cx + int(total * 0.16)
    branch_hand_y = chest_top - SS * 2
    pygame.draw.polygon(buf, ramp['shadow'], [
        (cx + chest_w // 2 - SS, chest_top + SS * 2),
        (cx + chest_w // 2 + SS * 2, chest_top + SS * 3),
        (branch_hand_x + SS * 2, branch_hand_y + SS * 2),
        (branch_hand_x - SS, branch_hand_y - SS),
    ])
    pygame.draw.polygon(buf, ramp['mid'], [
        (cx + chest_w // 2, chest_top + SS * 2 + SS // 2),
        (cx + chest_w // 2 + SS, chest_top + SS * 3),
        (branch_hand_x + SS, branch_hand_y + SS),
        (branch_hand_x - SS // 2, branch_hand_y),
    ])
    # Willow branch — a curved stem rising up + leaves.
    pygame.draw.line(buf, willow_dark,
                     (branch_hand_x, branch_hand_y),
                     (branch_hand_x + SS * 2,
                      branch_hand_y - int(total * 0.14)),
                     max(1, SS // 2))
    # Willow leaves — slim tapered ovals along the branch.
    for k in range(6):
        t = (k + 1) / 7
        lx = int(branch_hand_x + SS * 2 * t)
        ly = int(branch_hand_y - int(total * 0.14) * t)
        leaf_dx = (1 if k % 2 == 0 else -1) * SS * 2
        pygame.draw.polygon(buf, willow_color, [
            (lx, ly),
            (lx + leaf_dx, ly + SS),
            (lx + leaf_dx + SS, ly + SS * 3),
            (lx, ly + SS * 2),
        ])
        pygame.draw.line(buf, willow_dark,
                         (lx, ly), (lx + leaf_dx + SS // 2, ly + SS * 2),
                         max(1, SS // 3))
    y = chest_top

    # ── Neck.
    neck_w = max(SS * 3, int(total * 0.05))
    pygame.draw.rect(buf, ramp['shadow'],
                     (cx - neck_w // 2, y - neck_h, neck_w, neck_h))
    pygame.draw.rect(buf, ramp['body'],
                     (cx - neck_w // 2 + SS // 2,
                      y - neck_h, neck_w - SS, neck_h - SS))
    # Faint warm rim on neck — subsurface glow.
    pygame.draw.line(buf, ramp['warm_rim'],
                     (cx - neck_w // 2, y - neck_h + SS // 2),
                     (cx - neck_w // 2, y - SS // 2),
                     max(1, SS // 3))
    y -= neck_h

    # ── Head + flame-tipped aureole + diadem.
    head_w = max(SS * 11, int(total * 0.16))
    halo_r = int(head_w * 0.85)
    # Flame aureole — slightly oval halo, gilt rim.
    halo_rim = ramp['gilt']
    glow_a = 130 if _is_dark_sky(palette) else 70
    _soft_glow(buf, cx, y - head_h // 2, halo_r, halo_rim, glow_a)
    # Flame tips around aureole rim.
    for k in range(12):
        ang = k * math.tau / 12
        rim_x = cx + math.cos(ang) * halo_r
        rim_y = y - head_h // 2 + math.sin(ang) * halo_r
        tip_x = cx + math.cos(ang) * (halo_r + SS * 2)
        tip_y = y - head_h // 2 + math.sin(ang) * (halo_r + SS * 2)
        # Flame tongue.
        pygame.draw.polygon(buf, halo_rim, [
            (int(rim_x - math.cos(ang + math.pi / 2) * SS),
             int(rim_y - math.sin(ang + math.pi / 2) * SS)),
            (int(tip_x), int(tip_y)),
            (int(rim_x + math.cos(ang + math.pi / 2) * SS),
             int(rim_y + math.sin(ang + math.pi / 2) * SS)),
        ])
    # Head — porcelain head with cobalt eye dots.
    _draw_buddha_head_hd(buf, cx, y - head_h, head_w, head_h,
                         palette, ramp,
                         ushnisha=False, snail_curls=False,
                         urna=True, half_eyes=True,
                         long_ears=True, halo_radius=0,
                         smiling=False)

    # ── Flame-spire diadem ABOVE head with central Amitabha effigy.
    diadem_y = y - head_h
    diadem_w = int(head_w * 1.05)
    # Diadem base — small crown band.
    pygame.draw.rect(buf, ramp['mid'],
                     (cx - diadem_w // 2, diadem_y - SS * 2,
                      diadem_w, SS * 3))
    pygame.draw.line(buf, ramp['gilt'],
                     (cx - diadem_w // 2, diadem_y - SS * 2),
                     (cx + diadem_w // 2 - 1, diadem_y - SS * 2),
                     max(1, SS // 2))
    # Flame spires — 5 sharp peaks rising up.
    spike_h = diadem_h - SS * 2
    for k in range(5):
        sx = cx + (k - 2) * (diadem_w // 5)
        sh = spike_h if k == 2 else int(spike_h * 0.75)
        if k != 2:
            pygame.draw.polygon(buf, ramp['mid'], [
                (sx - SS, diadem_y - SS * 2),
                (sx + SS, diadem_y - SS * 2),
                (sx, diadem_y - SS * 2 - sh),
            ])
            pygame.draw.line(buf, ramp['lit'],
                             (sx, diadem_y - SS * 2),
                             (sx, diadem_y - SS * 2 - sh),
                             max(1, SS // 3))
    # ── Central niche with tiny seated Amitabha effigy — the canonical
    # Guanyin-diadem signature. Cobalt-fired silhouette.
    amitabha_w = SS * 6
    amitabha_h = spike_h - SS
    amitabha_rect = pygame.Rect(cx - amitabha_w // 2,
                                diadem_y - SS * 2 - amitabha_h,
                                amitabha_w, amitabha_h)
    # Niche behind effigy — small arched frame.
    pygame.draw.rect(buf, ramp['shadow'],
                     amitabha_rect.inflate(SS, SS))
    pygame.draw.ellipse(buf, ramp['shadow'],
                        (amitabha_rect.x - SS // 2,
                         amitabha_rect.y - SS,
                         amitabha_rect.w + SS, SS * 3))
    # Body of the tiny seated Buddha — cobalt-fire silhouette.
    pygame.draw.polygon(buf, ramp['cobalt'], [
        (amitabha_rect.x + SS // 2,
         amitabha_rect.bottom),
        (amitabha_rect.right - SS // 2,
         amitabha_rect.bottom),
        (amitabha_rect.right - SS,
         amitabha_rect.y + SS * 2),
        (amitabha_rect.x + SS,
         amitabha_rect.y + SS * 2),
    ])
    # Tiny head.
    pygame.draw.circle(buf, ramp['cobalt'],
                       (amitabha_rect.x + amitabha_rect.w // 2,
                        amitabha_rect.y + SS),
                       max(1, SS))
    # Gilt highlights along the diadem.
    pygame.draw.line(buf, ramp['gilt'],
                     (cx - diadem_w // 2 + SS,
                      diadem_y - SS * 2 - SS // 2),
                     (cx + diadem_w // 2 - SS,
                      diadem_y - SS * 2 - SS // 2),
                     max(1, SS // 3))


def _draw_guanyin(surf, top_rect, bot_rect, palette, seed):
    if bot_rect.height > 80:
        bw = bot_rect.width * SS
        bh = bot_rect.height * SS
        fig_buf = pygame.Surface((bw, bh), pygame.SRCALPHA)
        _hd_guanyin(fig_buf, bw // 2, bh - 1, 0, palette, seed)
        scaled = pygame.transform.smoothscale(
            fig_buf, (bot_rect.width, bot_rect.height))
        surf.blit(scaled, (bot_rect.x, bot_rect.y))

    natural_h = max(120, bot_rect.height)

    def draw_into(buf, cx, base_y, top_y):
        _hd_guanyin(buf, cx, base_y, top_y, palette, seed)

    # Vase + willow are asymmetric props that a vertical flip would
    # invert into nonsense → re-draw right-side-up in the top slot.
    _mirror_top(surf, top_rect, natural_h, draw_into,
                mirror_strategy="redraw")


def candidate_buddha_guanyin(surf, top_rect, bot_rect, palette, seed):
    _cached_draw('buddha_guanyin', _draw_guanyin, surf, top_rect,
                 bot_rect, palette, seed)


# ── Registries ───────────────────────────────────────────────────────────

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
    "https://www.travelchinaguide.com/attraction/shaanxi/xian/terra_cotta_army/cavalrymen.htm",
    "https://www.travelchinaguide.com/attraction/shaanxi/xian/terra_cotta_army/chariots.htm",
    "https://en.wikipedia.org/wiki/Leshan_Giant_Buddha",
    "https://en.wikipedia.org/wiki/Tian_Tan_Buddha",
    "https://en.wikipedia.org/wiki/Budai",
    "https://en.wikipedia.org/wiki/Yungang_Grottoes",
    "https://en.wikipedia.org/wiki/Guanyin",
]

VARIANT_REFERENCES = [
    [
        "https://www.scmp.com/news/china/science/article/3291332/mysterious-terracotta-commander-offers-new-clues-chinas-ancient-qin-dynasty-army",
        "https://en.wikipedia.org/wiki/Terracotta_Army",
        "https://smarthistory.org/the-terracotta-warriors/",
    ],
    [
        "https://visitterracottawarriors.com/index.php/2024/08/05/most-comprehensive-introduction-of-terracotta-warriors-pit-2/",
        "https://en.wikipedia.org/wiki/Terracotta_Army",
    ],
    [
        "https://www.britannica.com/topic/terra-cotta-army",
        "https://en.wikipedia.org/wiki/Terracotta_Army",
    ],
    [
        "https://www.travelchinaguide.com/attraction/shaanxi/xian/terra_cotta_army/hairstyle.htm",
        "https://en.wikipedia.org/wiki/Terracotta_Army",
    ],
    [
        "https://www.travelchinaguide.com/attraction/shaanxi/xian/terra_cotta_army/hairstyle.htm",
    ],
    [
        "https://www.chinaculturetour.com/leshan/top-attractions/leshan-giant-buddha.htm",
        "https://www.ancienttravel.org/destinations/leshan-giant-buddha/",
    ],
    [
        "https://www.baldhiker.com/tian-tan-buddha-hong-kong/",
        "https://www.visitourchina.com/hong-kong/attraction/tiantan-buddha-statue.html",
    ],
    [
        "https://butuzou.com/blogs/blog/chinese-maitreya-laughing-buddha",
        "https://religion.utk.edu/megan-bryson-in-the-conversation-who-is-the-laughing-buddha-a-scholar-of-east-asian-buddhism-explains/",
    ],
    [
        "https://en.wikipedia.org/wiki/Reclining_Buddha",
        "https://www.britannica.com/place/Yungang-caves",
    ],
    [
        "https://en.wikipedia.org/wiki/Dehua_porcelain",
        "https://www.metmuseum.org/art/collection/search/61509",
        "https://www.chinafurnitureonline.com/guanyin-chinese-bodhisattva",
    ],
]


# Forward-declared so candidate helpers below can refer to the cache key.
__all__ = [
    'candidate_warrior_general',
    'candidate_warrior_standing_archer',
    'candidate_warrior_kneeling_archer',
    'candidate_warrior_cavalry',
    'candidate_warrior_charioteer',
    'candidate_buddha_leshan',
    'candidate_buddha_tian_tan',
    'candidate_buddha_maitreya',
    'candidate_buddha_niche_reclining',
    'candidate_buddha_guanyin',
    'VARIANTS', 'VARIANT_NAMES', 'VARIANT_SOURCES', 'VARIANT_REFERENCES',
]
