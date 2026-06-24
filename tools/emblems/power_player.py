"""Bespoke engraved center glyphs for the POWER PLAYER (gold) achievements.

These supersede the shared ``_glyph_powerup``/``_glyph_magnet``/``_glyph_kfc``
fallbacks so each medal's silhouette depicts THAT achievement's nature while
staying a struck-metal sibling of the rest of the family: bold filled polygons,
thick lines and discs authored in the passed ``col`` (the builder strokes a
dark inset down-right + lit body + up-left sheen for the engrave relief), and
saturated accents (KFC red, magnet poles) routed through ``_accent`` so a
dormant medal stays bronze-monochrome. Nothing here drops below ~5px detail.

Seven distinct silhouettes per the v2 LOCKED spec — anchor-sparkle, plate ring,
magnet, binder grid, fanned bucket, biting mouth, sparkle-vortex — so no two
read alike at the ~22px engrave size.
"""
from __future__ import annotations

import math

import pygame

import game.achievement_icons as ai


def _sparkle_pts(cx, cy, r, waist=0.26, reach=0.78):
    # The franchise four-point sparkle, parameterised so the family's anchor,
    # the bitten one and the vortex motes all share one star body.
    return [
        (cx, cy - r * reach), (cx + r * waist, cy - r * waist),
        (cx + r * reach, cy), (cx + r * waist, cy + r * waist),
        (cx, cy + r * reach), (cx - r * waist, cy + r * waist),
        (cx - r * reach, cy), (cx - r * waist, cy - r * waist),
    ]


# ── first_powerup — Power Up! ────────────────────────────────────────────────
def _glyph_first_powerup(surf, cx, cy, r, col):
    # The canonical four-point sparkle (the category anchor) with a small
    # up-chevron notched into its lower point — "your first power-up."
    star = _sparkle_pts(cx, cy - r * 0.06, r * 0.92)
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in star])
    # Up-arrow tucked under the sparkle's lower point so the read is "rising".
    w = max(3, int(r * 0.22))
    tip = (cx, int(cy + r * 0.30))
    pygame.draw.lines(surf, col, False, [
        (cx - int(r * 0.34), cy + int(r * 0.72)), tip,
        (cx + int(r * 0.34), cy + int(r * 0.72)),
    ], w)


# ── powerup_sampler — Buffet ─────────────────────────────────────────────────
def _glyph_sampler(surf, cx, cy, r, col):
    # A thin plate ring carrying FOUR IDENTICAL filled dots evenly spaced on it
    # — quantity-on-a-container, not shape variety (distinct morsels die at row
    # size). The ring keeps it a plate, not a magnet horseshoe.
    # Thin plate ring kept smaller, with four FAT dots ringed fully OUTSIDE it
    # and detached — so at 44px the read is four discrete blobs (count carries
    # it), not a single hollow diamond fused to the outline.
    ring_r = int(r * 0.52)
    pygame.draw.circle(surf, col, (cx, cy), ring_r, max(3, int(r * 0.11)))
    dot_r = max(5, int(r * 0.28))
    dot_orbit = ring_r + dot_r + max(2, int(r * 0.12))   # clear gap to the ring
    for i in range(4):
        a = -math.pi / 2 + i * math.pi / 2     # top, right, bottom, left
        dx = cx + int(math.cos(a) * dot_orbit)
        dy = cy + int(math.sin(a) * dot_orbit)
        pygame.draw.circle(surf, col, (dx, dy), dot_r)


# ── magnet_life — Animal Magnetism ───────────────────────────────────────────
def _glyph_magnet_life(surf, cx, cy, r, col):
    # The horseshoe magnet pulling a $ coin toward its banded poles, with two
    # short attraction-arc ticks — "magnetism, 15x". Reuses the franchise red /
    # steel pole accent (unlock-only) via _accent. Magnet shifted up-left so the
    # coin being yanked in has room at the lower-right.
    mx, my = cx - int(r * 0.18), cy - int(r * 0.16)
    rr = int(r * 0.42)
    leg_w = max(6, int(r * 0.26))
    bar = max(6, int(r * 0.28))
    top = my - int(r * 0.40)
    arc_rect = pygame.Rect(mx - rr, top, rr * 2, rr * 2)
    pygame.draw.arc(surf, col, arc_rect, math.radians(6), math.radians(174), bar)
    leg_top = top + rr
    leg_h = int(r * 0.46)
    for sgn in (-1, 1):
        lx = mx + sgn * rr - leg_w // 2
        pygame.draw.rect(surf, col, (lx, leg_top, leg_w, leg_h))
    tip_h = max(4, int(r * 0.18))
    for sgn, tip in ((-1, ai._accent((212, 64, 56))), (1, ai._accent((224, 228, 240)))):
        lx = mx + sgn * rr - leg_w // 2
        pygame.draw.rect(surf, tip, (lx, leg_top + leg_h, leg_w, tip_h))
    # The $ coin being drawn toward the poles, parked at the lower-right with a
    # clear gap below the steel pole so the two never merge.
    coin_x = cx + int(r * 0.56)
    coin_y = cy + int(r * 0.54)
    coin_r = int(r * 0.28)
    pygame.draw.circle(surf, col, (coin_x, coin_y), coin_r, max(2, int(r * 0.10)))
    f = ai._glyph_font(int(coin_r * 2.0))
    g = f.render("$", True, col)
    surf.blit(g, g.get_rect(center=(coin_x, coin_y)))
    # Two attraction arcs between the poles and the coin (the pull).
    for off in (-0.10, 0.14):
        ax = mx + int(r * 0.30)
        ay = leg_top + leg_h + int(r * (0.30 + off))
        pygame.draw.arc(surf, col, (ax, ay, int(r * 0.46), int(r * 0.46)),
                        math.radians(200), math.radians(320), max(2, int(r * 0.09)))


# ── powerup_collector — Gotta Grab 'Em All ───────────────────────────────────
def _glyph_collector(surf, cx, cy, r, col):
    # A rounded "binder" rectangle holding a 3x3 grid of IDENTICAL filled dots —
    # grid completeness (a full container of same dots), not pip variety. The
    # rectangular frame separates it from Buffet's plate RING.
    bw, bh = int(r * 1.56), int(r * 1.56)
    rect = pygame.Rect(cx - bw // 2, cy - bh // 2, bw, bh)
    pygame.draw.rect(surf, col, rect, max(3, int(r * 0.13)),
                     border_radius=max(2, int(r * 0.16)))
    dot_r = max(4, int(r * 0.16))
    span = r * 0.50          # grid pitch
    for gy in (-1, 0, 1):
        for gx in (-1, 0, 1):
            pygame.draw.circle(surf, col,
                               (cx + int(gx * span), cy + int(gy * span)), dot_r)


# ── greasy_fingers — Finger Lickin' ──────────────────────────────────────────
def _glyph_greasy(surf, cx, cy, r, col):
    # An UPRIGHT striped KFC bucket with fries fanned out the top + a grease
    # shine-tick — distinct from kfc_incident's tipped/spilled bucket. Brand-red
    # tub accent via _accent (unlock-only). Fan splays wide so it reads as a
    # full upright bucket of fries, not the plain trapezoid tub.
    # Fries fanned out FIRST so the bucket rim overlaps their base.
    fry_w = max(3, int(r * 0.16))
    base_x, base_y = cx, int(cy + r * 0.10)
    for ang in (-46, -22, 0, 22, 46):
        a = math.radians(ang - 90)
        tx = base_x + int(math.cos(a) * r * 0.86)
        ty = base_y + int(math.sin(a) * r * 0.86)
        pygame.draw.line(surf, col, (base_x, base_y), (tx, ty), fry_w)
        pygame.draw.circle(surf, col, (tx, ty), max(2, fry_w // 2))
    # Upright tapered tub (narrower at the base than the rim) — the bucket body.
    tub = [
        (cx - r * 0.52, cy - r * 0.04),     # rim left
        (cx + r * 0.52, cy - r * 0.04),     # rim right
        (cx + r * 0.40, cy + r * 0.74),     # base right
        (cx - r * 0.40, cy + r * 0.74),     # base left
    ]
    pygame.draw.polygon(surf, ai._accent((214, 74, 60)),
                        [(int(x), int(y)) for x, y in tub])
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in tub],
                        max(2, int(r * 0.10)))
    # Two vertical bucket stripes so it reads as the striped tub, upright.
    for dx in (-0.18, 0.18):
        x = int(cx + dx * r)
        pygame.draw.line(surf, col, (x, int(cy + r * 0.02)),
                         (x, int(cy + r * 0.68)), max(2, int(r * 0.08)))
    # Grease shine-tick on the rim's lit upper-left.
    pygame.draw.line(surf, col, (int(cx - r * 0.30), int(cy + r * 0.12)),
                     (int(cx - r * 0.12), int(cy + r * 0.12)), max(2, int(r * 0.08)))


# ── power_hungry / power_addict — appetite grows (shared helper) ─────────────
def _appetite(surf, cx, cy, r, col, stage):
    """One motif escalated by appetite: stage 0 (hungry) = an open jaw biting a
    single four-point sparkle with one bite-notch; stage 1 (addict) = a vortex
    of sparkles spiralling into a central one — one bite becomes a whirlpool."""
    if stage == 0:
        # A bold open maw (a filled Pac-Man-style jaw with a wedge bite missing)
        # CHOMPING a four-point sparkle wedged in its gape. The solid round jaw
        # reads as a mouth at row size where thin lip-arcs do not.
        jx, jy = cx - int(r * 0.20), cy + int(r * 0.04)
        jr = int(r * 0.74)
        # Filled disc, then the open wedge cut out (toward the upper-right, where
        # the sparkle sits) in the inset-shadow tone so the gape reads as a mouth.
        pygame.draw.circle(surf, col, (jx, jy), jr)
        gape = []
        a_lo, a_hi = math.radians(-44), math.radians(20)   # mouth opening, up-right
        gape.append((jx, jy))
        for i in range(9):
            a = a_lo + (a_hi - a_lo) * i / 8
            gape.append((jx + math.cos(a) * jr * 1.15, jy + math.sin(a) * jr * 1.15))
        pygame.draw.polygon(surf, ai._GLYPH_SH, [(int(x), int(y)) for x, y in gape])
        # A round eye-dot so the disc reads as a face/head, not a moon.
        pygame.draw.circle(surf, ai._GLYPH_SH,
                           (int(jx - jr * 0.18), int(jy - jr * 0.40)),
                           max(3, int(r * 0.13)))
        # The sparkle pushed INTO the gape (overlapping the mouth opening) and
        # enlarged, with one bold bite-notch missing from its NEAR (lower-left)
        # edge — the half toward the jaw — so it reads as "mouth devouring a
        # sparkle," not a lone Pac-Man beside a speck.
        sx, sy = cx + int(r * 0.30), cy - int(r * 0.20)
        sr = r * 0.66
        star = _sparkle_pts(sx, sy, sr)
        pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in star])
        pygame.draw.circle(surf, ai._GLYPH_SH,
                           (int(sx - sr * 0.52), int(sy + sr * 0.54)),
                           max(4, int(r * 0.28)))
    else:
        # Sparkle-WHIRLPOOL: ONE dominant central sparkle with three satellite
        # sparkles caught on a clear inward SPIRAL — each seated on a thick arc
        # that curls toward the centre, shrinking as it goes (a vortex, not a
        # sprinkle) — plus a bold simplified crown arc on top, so the
        # one-bite→whirlpool climb past power_hungry reads at chip size.
        cy_v = cy + int(r * 0.10)                       # seat below the crown
        # Spiral arms first so the satellites sit on top of their own tails.
        for i in range(3):
            a0 = -math.pi / 2 + i * (2 * math.pi / 3)   # arm start angle
            arc_r = int(r * (0.86 - i * 0.04))
            rect = pygame.Rect(cx - arc_r, cy_v - arc_r, arc_r * 2, arc_r * 2)
            # Each arm sweeps ~150° inward; same handedness for all three reads
            # as one rotating whirlpool.
            pygame.draw.arc(surf, col, rect, a0, a0 + math.radians(150),
                            max(2, int(r * 0.12)))
        # Dominant centre sparkle.
        cstar = _sparkle_pts(cx, cy_v, r * 0.56)
        pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in cstar])
        # Three satellite sparkles riding the spiral, shrinking toward centre.
        for i in range(3):
            a = -math.pi / 2 + i * (2 * math.pi / 3) + math.radians(150)
            rad = r * (0.84 - i * 0.06)
            mx = cx + math.cos(a) * rad
            my = cy_v + math.sin(a) * rad
            ms = r * (0.30 - i * 0.05)
            mote = _sparkle_pts(mx, my, ms)
            pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in mote])
        # Bold three-point crown arc seated on top — the L4 insatiable rung.
        cw = r * 0.62
        cyt = cy - int(r * 0.78)
        crown = [
            (cx - cw, cyt + r * 0.22),
            (cx - cw, cyt),
            (cx - cw * 0.5, cyt + r * 0.16),
            (cx, cyt - r * 0.10),
            (cx + cw * 0.5, cyt + r * 0.16),
            (cx + cw, cyt),
            (cx + cw, cyt + r * 0.22),
        ]
        pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in crown])


def _glyph_power_hungry(surf, cx, cy, r, col):
    _appetite(surf, cx, cy, r, col, stage=0)


def _glyph_power_addict(surf, cx, cy, r, col):
    _appetite(surf, cx, cy, r, col, stage=1)


GLYPHS = {
    "first_powerup": _glyph_first_powerup,
    "powerup_sampler": _glyph_sampler,
    "magnet_life": _glyph_magnet_life,
    "powerup_collector": _glyph_collector,
    "greasy_fingers": _glyph_greasy,
    "power_hungry": _glyph_power_hungry,
    "power_addict": _glyph_power_addict,
}
