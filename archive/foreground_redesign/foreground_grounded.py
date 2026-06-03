"""Round-3 GROUNDED foreground concepts for the Skybit redesign.

Round 1/2 leaned on summed-sine bank crests that read as ocean waves and as a
near echo of the ink-wash mountain ridges. This round throws that out: a
foreground here is a STABLE, FLAT land/earth plane, opaque to the bottom edge,
whose identity comes from its SURFACE TEXTURE — paving joints, clay cracks,
rake furrows, grass blades, plank grain — not from a rolling silhouette.

Every plane is THIN (~45-60px), sits flat (or with a gentle front-to-back
perspective slope), fills opaque from its top edge down to y=h, and carries a
near->far value fall for depth. They retint across the full day/night cycle off
the same stage palette the sky/mountains/pillars consume, so each plane belongs
to the misty-gorge shan-shui world while keeping its own material character.

Exploration-only — nothing here is imported by the live game. Pure-Pygame /
pygbag-safe (fill, blit, draw.*, SRCALPHA, BLEND_*, Bayer dither blits) — no
surfarray / gfxdraw / numpy / per-pixel set_at on the hot path.

Each painter takes (surf, w, ground_y, h, scroll, pal) where `pal` is a stage
palette dict carrying both the redesign struct_*/ground_*/mtn_* keys AND the
stone_* aliases.
"""
from __future__ import annotations

import math
import random

import pygame


# ── shared colour helpers (mirror foreground_variants so tones harmonise) ─────

def _clamp(c):
    return max(0, min(255, int(c)))


def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return (_clamp(a[0] + (b[0] - a[0]) * t),
            _clamp(a[1] + (b[1] - a[1]) * t),
            _clamp(a[2] + (b[2] - a[2]) * t))


def _shade(c, d):
    return (_clamp(c[0] + d), _clamp(c[1] + d), _clamp(c[2] + d))


def _luma(c):
    return (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) / 255.0


def _sat(c, f):
    g = _luma(c) * 255.0
    return (_clamp(g + (c[0] - g) * f),
            _clamp(g + (c[1] - g) * f),
            _clamp(g + (c[2] - g) * f))


def _nightf(pal):
    """Continuous 0..1 night-ness from sky_top luminance, so a plane can cool its
    surface and add lantern/edge warmth as the stage darkens without a hard step."""
    r, g, b = pal.get('sky_top', (60, 120, 200))
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return max(0.0, min(1.0, (95.0 - lum) / 75.0))


def _horizon(pal):
    return pal.get('horizon', (250, 226, 184))


# ── seamless scatter over world-x (mirrors ground_variants._scatter) ──────────

def _scatter(scroll, w, speed, step, seed_off, margin=24):
    """Yield (screen_x, cell_index, rng) for jittered points marching in world
    space, so any near-plane detail scrolls seamlessly with the world and tiles
    deterministically per cell. The plane itself is static; this only places
    surface marks (pebbles, stones, reeds) that ride the scroll."""
    phase = scroll * speed
    first = int((phase - margin) // step) - 1
    last = int((phase + w + margin) // step) + 2
    for k in range(first, last + 1):
        rng = random.Random((k * 2654435761 ^ seed_off) & 0xFFFFFFFF)
        wx = k * step + rng.uniform(-step * 0.25, step * 0.25)
        sx = int(wx - phase)
        if -margin < sx < w + margin:
            yield sx, k, rng


# ── a flat grounded slab: vertical gradient, opaque crest_y -> bottom h ───────

def _flat_slab(surf, w, h, top_y, top_col, bot_col, ease=1.0):
    """Paint an opaque vertical-gradient land plane from a FLAT top edge at
    `top_y` down to the true frame bottom h. No silhouette, no wave — just a
    solid grounded surface. `ease`>1 keeps it lighter near the front lip and
    darkens toward the foot for a near->far value fall under the eye."""
    depth = h - top_y
    if depth <= 0:
        return
    span = max(1, depth - 1)
    for i in range(depth):
        t = (i / span) ** ease
        pygame.draw.line(surf, _mix(top_col, bot_col, t),
                         (0, top_y + i), (w, top_y + i))


def _perspective_y(top_y, h, frac, curve=1.6):
    """Map a near->far fraction (0=front lip at bottom, 1=back edge at top_y) to a
    screen-y, packed tighter toward the back so receding courses foreshorten."""
    t = frac ** curve
    return int(h - (h - top_y) * t)


# ── faint Bayer-ish grain without surfarray (cached add/sub tiles) ────────────

_GRAIN_CACHE: dict = {}


def _grain_tiles(amp):
    """Two 4x4 ordered-dither tiles (brighten / darken) for cheap surface grain.
    A compact ordered matrix avoids per-pixel work at blit time — tile, then
    blit ADD/SUB over the plane. Cached per amp."""
    cached = _GRAIN_CACHE.get(amp)
    if cached is not None:
        return cached
    m = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))
    pos = pygame.Surface((4, 4))
    neg = pygame.Surface((4, 4))
    for ty in range(4):
        for tx in range(4):
            off = ((m[ty][tx] + 0.5) / 16.0 - 0.5) * 2.0 * amp
            p = max(0, int(round(off)))
            n = max(0, int(round(-off)))
            pos.set_at((tx, ty), (p, p, p))
            neg.set_at((tx, ty), (n, n, n))
    _GRAIN_CACHE[amp] = (pos, neg)
    return pos, neg


def _apply_grain(surf, x0, y0, w, hh, amp):
    """Tile the grain pair over a w x hh region anchored at (x0, y0)."""
    if amp <= 0 or hh <= 0:
        return
    pos, neg = _grain_tiles(amp)
    strip_p = pygame.Surface((w, 4))
    strip_n = pygame.Surface((w, 4))
    for x in range(0, w, 4):
        strip_p.blit(pos, (x, 0))
        strip_n.blit(neg, (x, 0))
    for y in range(0, hh, 4):
        surf.blit(strip_p, (x0, y0 + y), special_flags=pygame.BLEND_RGB_ADD)
        surf.blit(strip_n, (x0, y0 + y), special_flags=pygame.BLEND_RGB_SUB)


def _apply_grain_scroll(surf, x0, y0, w, hh, amp, scroll, speed=0.22):
    """Scroll-LOCKED grain: the dither tile is phase-shifted by the world scroll
    so the speckle rides the surface as it moves instead of crawling in screen
    space (the screen-space _apply_grain shimmers under motion). The 4px tile
    wraps on its own period, so a sub-tile phase offset is all that's needed to
    anchor the grain to world-x; sand uses this so the tooth tracks the dunes."""
    if amp <= 0 or hh <= 0:
        return
    pos, neg = _grain_tiles(amp)
    # Build a w+4 strip so a 0..3px horizontal phase can slide without a gap.
    strip_p = pygame.Surface((w + 4, 4))
    strip_n = pygame.Surface((w + 4, 4))
    for x in range(0, w + 4, 4):
        strip_p.blit(pos, (x, 0))
        strip_n.blit(neg, (x, 0))
    ox = -int(scroll * speed) % 4
    for y in range(0, hh, 4):
        surf.blit(strip_p, (x0 - ox, y0 + y), special_flags=pygame.BLEND_RGB_ADD)
        surf.blit(strip_n, (x0 - ox, y0 + y), special_flags=pygame.BLEND_RGB_SUB)


# ══════════════════════════════════════════════════════════════════════════
# Concept 1 — Flagstone Courtyard / Paved Pilgrim Path  (~56px, temple-stone)
# A flat foreshortened stone-slab pavement in receding courses. Mortar joints
# run as fine inset lines; each course is a row of irregular slabs in a worn
# warm-sandstone tone matched to the Songyue pagoda brick. A man-made temple
# ground — solid, paved, opaque to the bottom. No silhouette anywhere.
# ══════════════════════════════════════════════════════════════════════════

def _sandstone(pal):
    """Worn warm-sandstone paving tone tied to the Songyue brick family (the same
    stone_dark->tan mix the pillar candidate uses), so the courtyard reads as the
    same masonry as the pagoda standing on it."""
    return _mix(pal.get('stone_dark', (95, 70, 55)), (206, 170, 124), 0.62)


def fg_flagstone_courtyard(surf, w, gy, h, scroll, pal):
    night = _nightf(pal)
    # Thinned to ~50px (was 52) so the band reads as a flat receding floor strip,
    # not a tall wall of tile.
    top_y = gy - 50
    stone = _sandstone(pal)
    # Strong near->far value fall: warmer/lighter at the front lip, cooler/darker
    # into the back where the mist sits, with a widened spread so the plane reads
    # as a floor tilting to a horizon. Cool the whole plane toward night.
    front = _shade(_sat(stone, 1.05), 2)
    back = _mix(_shade(_sat(stone, 0.84), -34), _horizon(pal), 0.16)
    front = _mix(front, (70, 80, 110), 0.30 * night)
    back = _mix(back, (60, 70, 100), 0.34 * night)
    _flat_slab(surf, w, h, top_y, back, front, ease=0.8)

    # Foreshorten the back edge so the top line recedes into the mist instead of
    # butting flat against the sky — a long value-lift across the rear band plus
    # a tight 4px top-edge feather so the joint with the mist is gradient, never
    # a drawn seam (matched to the meadow's treatment).
    region_h = h - top_y
    mist_back = _mix(back, _horizon(pal), 0.24 + 0.10 * night)
    recede_h = int(region_h * 0.34)
    for i in range(recede_h):
        t = 1.0 - (i / max(1, recede_h - 1))
        t = t * t
        if t <= 0.01:
            continue
        ln = pygame.Surface((w, 1), pygame.SRCALPHA)
        ln.fill((*_mix(back, mist_back, t), int(200 * t)))
        surf.blit(ln, (0, top_y + i))

    joint = _shade(_mix(stone, (60, 44, 34), 0.5), -12 - int(8 * night))

    # Receding paving courses: 6 rows packed tighter toward the back (perspective).
    # The grid is deliberately BROKEN so it reads as a worn temple courtyard, not
    # tile wallpaper: each course carries its own running-bond phase offset, slab
    # widths/breaks vary per slab (not a fixed step), joint value jitters
    # slab-to-slab, and a couple of slabs per front course are cracked/worn.
    n_course = 6
    rim = _mix(_horizon(pal), (255, 224, 168), 0.5)
    # Per-course running-bond phase: a pseudo-random fraction of the step per
    # course (not a rigid alternating half-step) so vertical joints never stack
    # into the wallpaper grid the way an even offset would.
    bond_rng = random.Random((int(scroll * 0.18) // 24) & 0xFFFFFFFF)
    for c in range(n_course):
        f0 = c / n_course
        f1 = (c + 1) / n_course
        y_back = _perspective_y(top_y, h, 1.0 - f0)
        y_front = _perspective_y(top_y, h, 1.0 - f1)
        if y_front <= y_back:
            continue
        depth_t = f0  # 0 at back, ->1 at front
        # Mean slab width grows toward the player; the running-bond offset is an
        # irregular per-course phase shift (0.2-0.8 of a step) so vertical joints
        # never line up between courses (the wallpaper-grid killer). Per-course
        # joint value also drifts so courses don't read identically toned.
        step = int(26 + 30 * depth_t)
        bond = int(bond_rng.uniform(0.2, 0.8) * step)
        jc = _mix(joint, back, max(0.0, 0.45 * (1 - depth_t)))
        jc = _shade(jc, bond_rng.randint(-6, 6))
        # Horizontal course joint (flat).
        pygame.draw.line(surf, jc, (0, y_back), (w, y_back), 1)
        if depth_t > 0.45:
            pygame.draw.line(surf, _shade(jc, 14), (0, y_back + 1), (w, y_back + 1), 1)
        # Vertical slab joints across this course at IRREGULAR widths: each cell
        # nudges its break by a wide per-slab fraction of the step so slab
        # lengths vary strongly, and the joint value jitters so no two joints
        # read identical.
        speed = 0.18 + 0.10 * depth_t
        for sx, k, srng in _scatter(scroll, w, speed, step, 0x9A1 + c):
            jy0, jy1 = y_back, y_front
            jx = sx + bond + int(srng.uniform(-0.40, 0.40) * step)
            jvar = _shade(jc, srng.randint(-9, 9))
            pygame.draw.line(surf, jvar, (jx, jy0), (jx, jy1), 1)
            # Faint lit edge on the player-facing side of nearer slabs.
            if depth_t > 0.4:
                pygame.draw.line(surf, _shade(jvar, 18), (jx + 1, jy0), (jx + 1, jy1), 1)
            # 1-2 cracked / worn slabs per front course: a hairline fracture and
            # a chipped darker corner so the slab reads as aged, not pristine.
            if depth_t > 0.45 and srng.random() < 0.30:
                cw0 = jx + srng.randint(6, max(8, step - 8))
                cw0 = min(w - 2, cw0)
                crk = _shade(jc, -10)
                midc = (jy0 + jy1) // 2 + srng.randint(-3, 3)
                pygame.draw.line(surf, crk, (cw0, jy0 + 2),
                                 (cw0 + srng.randint(-4, 4), midc), 1)
                pygame.draw.line(surf, crk, (cw0 + srng.randint(-4, 4), midc),
                                 (cw0 + srng.randint(-5, 5), jy1 - 1), 1)
                # Worn/scuffed patch — a faint darker wash on the slab face.
                wp = pygame.Surface((srng.randint(6, 12),
                                     max(2, (jy1 - jy0) // 2)), pygame.SRCALPHA)
                wp.fill((*_shade(back, -14), 40))
                surf.blit(wp, (cw0 - 4, jy0 + 2))
        # A few worn slabs catch a faint warm sheen on the front courses —
        # kept LOW and per-slab, never a continuous bright seam across the band.
        if depth_t > 0.55:
            for sx, k, srng in _scatter(scroll, w, speed * 1.3, step, 0x9A1 + c + 40):
                if srng.random() < 0.42:
                    sheen = pygame.Surface((step - 6, max(2, (y_front - y_back) // 2)),
                                           pygame.SRCALPHA)
                    sheen.fill((*rim, int(18 + 14 * depth_t)))
                    surf.blit(sheen, (sx - step // 2, y_back + 2),
                              special_flags=pygame.BLEND_RGB_ADD)

    # Fine stone grain over the whole plane.
    _apply_grain(surf, 0, top_y, w, h - top_y, 4)

    # Tight top-edge feather: a 4px soft transition that dissolves the back of
    # the plane into the mist colour so the top line is a gradient, never a hard
    # seam — matched to the meadow lead.
    feather = _mix(mist_back, _horizon(pal), 0.16)
    for i in range(4):
        a = int(140 * (1.0 - i / 4.0))
        ln = pygame.Surface((w, 1), pygame.SRCALPHA)
        ln.fill((*feather, a))
        surf.blit(ln, (0, top_y - 1 + i))


# ══════════════════════════════════════════════════════════════════════════
# Concept 2 — Sun-Cracked Packed Earth  (~50px, natural)
# The most minimal "solid land underfoot": a flat dry clay plane with a
# procedural polygon crack network, a scatter of embedded pebbles, and a faint
# dust grain. No vegetation, no architecture — just baked earth. Opaque to the
# bottom; the crack lines are the entire identity.
# ══════════════════════════════════════════════════════════════════════════

def _clay(pal):
    """Dry packed-clay tone — pulled toward the warm sandstone family for charm
    (the round-3 clay read muddy-grey). Off the stage ground band, kept a touch
    earthier than the courtyard stone so it still reads as baked earth, not
    masonry, but warmer and more inviting than the prior muted ochre."""
    base = pal.get('ground_mid', (176, 142, 92))
    warm = _mix(base, (198, 158, 110), 0.5)
    return _mix(_sat(warm, 0.90), (192, 152, 108), 0.4)


def fg_cracked_earth(surf, w, gy, h, scroll, pal):
    night = _nightf(pal)
    top_y = gy - 50
    clay = _clay(pal)
    front = _shade(clay, 4)
    back = _mix(_shade(_sat(clay, 0.88), -26), _horizon(pal), 0.08)
    front = _mix(front, (66, 74, 104), 0.30 * night)
    back = _mix(back, (58, 66, 96), 0.34 * night)
    _flat_slab(surf, w, h, top_y, back, front, ease=0.95)

    # Low-contrast cracks (lifted off the round-3 near-black so the net never
    # resolves into a high-contrast ridge skyline).
    crack = _shade(_sat(clay, 0.78), -30 - int(8 * night))
    crack_hi = _shade(clay, 18)  # sunlit upper lip of an open crack

    # SHORT, BRANCHING crack fragments — NOT a connected polygon mesh. Round 3
    # chained every node to its sorted neighbour, which summed into a continuous
    # jagged line that read as a mountain crest. Here each seed fires its OWN
    # little star of 2-3 short stubby cracks radiating to nearby random angles,
    # so the marks stay local, broken, and low-contrast: dry-mud crazing, never a
    # continuous horizontal fracture across the band.
    region_h = h - top_y
    for sx, k, srng in _scatter(scroll, w, 0.16, 26, 0x2C7):
        ny = top_y + int(srng.uniform(0.16, 0.96) * region_h)
        depth_t = (ny - top_y) / max(1, region_h)
        n_arms = srng.randint(2, 3)
        for _a in range(n_arms):
            ang = srng.uniform(0, math.tau)
            seg = srng.randint(6, 13)
            # Two-segment kinked stub so each arm bends a little but stays short.
            mx = sx + int(math.cos(ang) * seg * 0.6)
            my = ny + int(math.sin(ang) * seg * 0.6)
            ang2 = ang + srng.uniform(-0.6, 0.6)
            ex = mx + int(math.cos(ang2) * seg * 0.5)
            ey = my + int(math.sin(ang2) * seg * 0.5)
            ey = max(top_y + 1, min(h - 1, ey))
            my = max(top_y + 1, min(h - 1, my))
            cw = 2 if depth_t > 0.7 else 1
            pts = [(sx, ny), (mx, my), (ex, ey)]
            pygame.draw.lines(surf, crack, False, pts, cw)
            # Sunlit upper lip on nearer cracks gives a tiny relief.
            if depth_t > 0.55 and night < 0.6:
                pygame.draw.aalines(surf, _mix(crack_hi, front, 0.35), False,
                                    [(p[0], p[1] - 1) for p in pts])

    # Embedded pebbles half-sunk in the clay — small flat ellipses with a lit top
    # edge, larger/brighter toward the front plane.
    for sx, k, srng in _scatter(scroll, w, 0.22, 22, 0x71B):
        py = top_y + int(srng.uniform(0.30, 0.96) * region_h)
        depth_t = (py - top_y) / max(1, region_h)
        if srng.random() > 0.4 + 0.4 * depth_t:
            continue
        pr = 1 + int(depth_t * 2.2)
        pc = _mix(clay, (150, 138, 120), 0.5)
        pc = _mix(pc, (60, 70, 100), 0.3 * night)
        pygame.draw.ellipse(surf, _shade(pc, -22),
                            (sx - pr, py - pr // 2, pr * 2, pr + 1))
        pygame.draw.ellipse(surf, pc, (sx - pr, py - pr // 2 - 1, pr * 2, pr + 1))
        if night < 0.6:
            surf.set_at((sx, py - pr // 2 - 1), _shade(pc, 26))

    _apply_grain(surf, 0, top_y, w, h - top_y, 5)
    # Top edge: a soft 4px feather into the mist (NO drawn crack/edge lines — a
    # continuous dark crack line at the top read as a connected fracture ridge).
    mist_back = _mix(back, _horizon(pal), 0.20 + 0.10 * night)
    feather = _mix(mist_back, _horizon(pal), 0.14)
    for i in range(4):
        a = int(140 * (1.0 - i / 4.0))
        ln = pygame.Surface((w, 1), pygame.SRCALPHA)
        ln.fill((*feather, a))
        surf.blit(ln, (0, top_y - 1 + i))


# ══════════════════════════════════════════════════════════════════════════
# Concept 3 — Raked Zen-Gravel Garden  (~52px, cultivated karesansui)
# A pale gravel plane combed with parallel raked furrow grooves that bend in a
# gentle curve around 2-3 set mossy stones. Calm, cultivated, very different in
# read from the natural cracked earth. Opaque to the bottom; the furrow rhythm
# is the identity, NOT a wave silhouette — the grooves are surface texture on a
# flat plane.
# ══════════════════════════════════════════════════════════════════════════

def _gravel(pal):
    """Pale raked-gravel tone — a light cool sand, lifted off the warm ground band
    toward grey so it reads as the bright karesansui gravel, distinct from clay."""
    base = pal.get('ground_top', (214, 184, 124))
    return _mix(_sat(base, 0.62), (208, 200, 184), 0.55)


def fg_zen_gravel(surf, w, gy, h, scroll, pal):
    night = _nightf(pal)
    top_y = gy - 52
    gravel = _gravel(pal)
    front = _shade(gravel, 6)
    back = _shade(_sat(gravel, 0.92), -22)
    front = _mix(front, (62, 72, 104), 0.34 * night)
    back = _mix(back, (54, 64, 96), 0.38 * night)
    _flat_slab(surf, w, h, top_y, back, front, ease=0.85)

    region_h = h - top_y
    # Two set stones (and a small companion) the furrows flow around. Their world
    # positions ride the scroll so the raking re-curves around them seamlessly.
    stone_cx = []
    for sx, k, srng in _scatter(scroll, w, 0.15, 150, 0x4E1):
        sr = srng.randint(7, 11)
        sy = top_y + int(srng.uniform(0.42, 0.78) * region_h)
        stone_cx.append((sx, sy, sr))

    groove = _shade(_sat(gravel, 0.8), -26 - int(8 * night))
    ridge = _shade(gravel, 16)

    # Parallel raked furrows: DEAD-STRAIGHT horizontal grooves stepping down the
    # plane. Round 3's wide gaussian deflection swelled the furrows into nested
    # arcs that read as rolling waves on the floor. Here a furrow is a flat
    # horizontal line; the ONLY deviation is a tiny, tight local nudge in a
    # narrow band right at a stone's edge (radius ~ the stone itself, amplitude a
    # few px) so the rake reads as combing snug around the rock — no swelling
    # arcs, no nested contours, just straight lines with a small notch at a stone.
    n_groove = 11
    for gi in range(n_groove):
        f = gi / (n_groove - 1)
        base_y = _perspective_y(top_y, h, 1.0 - f * 0.96)
        depth_t = f

        def nudge(x):
            dy = 0.0
            for (scx, scy, sr) in stone_cx:
                # Only furrows passing right beside the stone get the small notch.
                if abs(base_y - scy) > sr + 3:
                    continue
                dx = abs(x - scx)
                if dx > sr + 5:
                    continue
                # Tight cosine notch confined to the stone's own width; capped at
                # a few px so it can never grow into a wave.
                e = 0.5 + 0.5 * math.cos(math.pi * min(1.0, dx / (sr + 5.0)))
                dy -= e * min(4.0, sr * 0.4)
            return dy

        # Straight base line drawn in two flat halves with only the local notch
        # where a stone sits; most of the furrow is a perfectly horizontal line.
        pts = []
        for x in range(0, w + 1, 4):
            yy = base_y + nudge(x)
            if yy < top_y:
                yy = top_y
            pts.append((x, int(yy)))
        pygame.draw.aalines(surf, groove, False, pts)
        if depth_t > 0.35:
            pygame.draw.aalines(surf, ridge, False, [(x, y - 1) for x, y in pts])

    # The set stones: rounded mossy boulders sitting ON the gravel with a soft
    # contact shadow, a cool stone body, and a faint moss cap.
    for (scx, scy, sr) in stone_cx:
        # Contact shadow ellipse.
        sh = pygame.Surface((sr * 3, sr), pygame.SRCALPHA)
        sh.fill((0, 0, 0, 0))
        pygame.draw.ellipse(sh, (0, 0, 0, 70), (0, 0, sr * 3, sr))
        surf.blit(sh, (scx - sr * 3 // 2, scy - sr // 2 + sr - 2))
        body = _mix(pal.get('stone_dark', (95, 80, 70)), (96, 92, 86), 0.5)
        body = _mix(body, (50, 60, 92), 0.34 * night)
        pygame.draw.ellipse(surf, _shade(body, -22),
                            (scx - sr, scy - sr + 2, sr * 2, sr + 2))
        pygame.draw.ellipse(surf, body, (scx - sr, scy - sr, sr * 2, sr + 2))
        # Lit top-left shoulder.
        pygame.draw.arc(surf, _shade(body, 26),
                        (scx - sr, scy - sr, sr * 2, sr + 2),
                        math.radians(70), math.radians(160), 2)
        # Faint moss cap (muted, not a flower).
        moss = _mix(pal.get('foliage_mid', (60, 110, 70)), body, 0.45)
        moss = _mix(moss, (40, 56, 86), 0.3 * night)
        for _ in range(4):
            mx = scx + random.Random(scx ^ scy ^ _).randint(-sr + 2, sr - 2)
            surf.set_at((mx, scy - sr + 2), moss)

    _apply_grain(surf, 0, top_y, w, h - top_y, 4)
    # Top edge: soft 4px feather into the mist (no drawn continuous edge lines).
    mist_back = _mix(back, _horizon(pal), 0.18 + 0.10 * night)
    feather = _mix(mist_back, _horizon(pal), 0.14)
    for i in range(4):
        a = int(135 * (1.0 - i / 4.0))
        ln = pygame.Surface((w, 1), pygame.SRCALPHA)
        ln.fill((*feather, a))
        surf.blit(ln, (0, top_y - 1 + i))


# ══════════════════════════════════════════════════════════════════════════
# Concept 4 — Ink-Wash Meadow  (~48px, muted grassland)
# The "fixed" original meadow: a flat desaturated low-grass plane with a fine
# blade texture and a few sparse reeds — NO cartoon flowers / ladybugs / bees /
# dandelions. Reads as quiet shan-shui grassland, not a bright kelly lawn.
# Opaque to the bottom; the blade field is the texture, the plane stays flat.
# ══════════════════════════════════════════════════════════════════════════

def _meadow(pal):
    """Muted ink-wash grass — the stage foliage pulled hard toward a desaturated
    teal-green so it sits in the shan-shui frame instead of reading as the live
    game's kelly meadow. Pulled a further ~12% notch toward the misty biome's
    muted teal-green (lower saturation, more of the cool teal mix) so the DAY
    plane stops reading a hair too saturated/uniform against the misted ranks."""
    base = pal.get('foliage_mid', (60, 110, 80))
    return _mix(_sat(base, 0.42), (78, 100, 86), 0.58)


def fg_inkwash_meadow(surf, w, gy, h, scroll, pal):
    night = _nightf(pal)
    top_y = gy - 48
    grass = _meadow(pal)
    region_h = h - top_y

    # Strong near->far value fall so the plane reads as a FLOOR tilting toward a
    # horizon, not a stacked strip: the front lip sits clearly lighter/warmer and
    # the back lifts toward the mist. Widen the front<->back spread (vs round 3's
    # near-flat ramp) so the eye reads the plane receding, then ease<1 packs the
    # darker mid into the near third under the bird lane.
    front = _shade(grass, 10)
    back = _mix(_shade(_sat(grass, 0.80), -30), _horizon(pal), 0.18)
    front = _mix(front, (52, 64, 96), 0.32 * night)
    back = _mix(back, (46, 58, 90), 0.36 * night)
    _flat_slab(surf, w, h, top_y, back, front, ease=0.78)

    # Foreshorten the back edge: the round-3 hard horizontal seam "stepped"
    # against the mist. Replace it with (a) a soft multi-px transition right at
    # the top line that dissolves the seam, and (b) a long value-fall lift across
    # the rear ~40% of the band so the surface tilts away to a horizon. Two
    # passes: a wide gentle lift, then a tight ~4px feather right at top_y so the
    # joint with the mist is gradient, never a drawn line.
    mist_back = _mix(back, _horizon(pal), 0.26 + 0.10 * night)
    recede_h = int(region_h * 0.40)
    for i in range(recede_h):
        # 1 at the very back edge -> 0 where the recede band ends.
        t = 1.0 - (i / max(1, recede_h - 1))
        t = t * t
        if t <= 0.01:
            continue
        col = _mix(back, mist_back, t)
        a = int(205 * t)
        ln = pygame.Surface((w, 1), pygame.SRCALPHA)
        ln.fill((*col, a))
        surf.blit(ln, (0, top_y + i))
    # Tight top-edge feather: a 4px soft transition that bleeds the very back of
    # the plane into the mist colour so the top line is never a hard seam.
    feather = _mix(mist_back, _horizon(pal), 0.18)
    for i in range(4):
        a = int(150 * (1.0 - i / 4.0))
        ln = pygame.Surface((w, 1), pygame.SRCALPHA)
        ln.fill((*feather, a))
        surf.blit(ln, (0, top_y - 1 + i))

    blade_dk = _shade(_sat(grass, 0.9), -24)
    blade_lt = _mix(grass, (150, 168, 130), 0.4)
    blade_lt = _mix(blade_lt, (70, 80, 108), 0.3 * night)

    # Fine blade texture: short upward flicks scattered in world space, denser and
    # taller toward the front plane, leaning slightly with a gentle breeze phase.
    # Pure 1-2px lines — quiet, not the bright tuft clumps of the live meadow.
    # Blades fade toward the receding back so they don't pepper the misted rim.
    lean = math.sin(scroll * 0.01) * 1.5
    for sx, k, srng in _scatter(scroll, w, 0.26, 7, 0x33D):
        by = top_y + int(srng.uniform(0.10, 1.0) * region_h)
        depth_t = (by - top_y) / max(1, region_h)
        if depth_t < 0.16 and srng.random() < 0.7:
            continue
        bl = int(3 + depth_t * 6 + srng.randint(0, 2))
        tip_x = sx + int(lean * (0.5 + depth_t)) + srng.randint(-1, 1)
        col = blade_dk if srng.random() < 0.6 else blade_lt
        if depth_t < 0.3:
            col = _mix(col, mist_back, 0.4)
        pygame.draw.line(surf, col, (sx, by), (tip_x, by - bl), 1)

    # Sparse reeds — taller, thinner stalks with a small seed-head tuft. CLUMPED
    # (Poisson-ish) rather than evenly stamped: a coarse world step picks sparse
    # clump anchors, and to break the regular picket rhythm each firing anchor
    # also drops a satellite tuft a random gap to one side, so reeds gather in
    # uneven groups of marsh-grass with bare ground between — never a fence line.
    reed_dk = _shade(_sat(grass, 0.7), -30)
    reed_seed = _mix(_horizon(pal), grass, 0.5)
    reed_seed = _mix(reed_seed, (90, 100, 120), 0.35 * night)

    def _draw_clump(cx0, cluster_y, srng, count):
        for ci in range(count):
            cx_off = srng.randint(-8, 8)
            ry = cluster_y + srng.randint(-3, 3)
            rx = cx0 + cx_off
            rh = srng.randint(13 + ci, 24)
            sway = int(lean * 1.6) + srng.randint(-1, 1)
            tip = (rx + sway, ry - rh)
            pygame.draw.line(surf, reed_dk, (rx, ry), tip, 1)
            # Slim seed head — a short fatter stroke at the tip, not a flower.
            pygame.draw.line(surf, reed_seed, (tip[0], tip[1]),
                             (tip[0], tip[1] + 4), 2)
            # A leaf flick off the stalk.
            midy = ry - rh // 2
            pygame.draw.line(surf, reed_dk, (rx, midy), (rx - 4, midy - 2), 1)

    for sx, k, srng in _scatter(scroll, w, 0.24, 132, 0x88E):
        # Sparse firing so clumps are well-separated; the wide step + jitter in
        # _scatter already de-grids the anchors, the satellite adds local cluster.
        if srng.random() < 0.40:
            continue
        cluster_y = top_y + int(srng.uniform(0.58, 0.95) * region_h)
        _draw_clump(sx, cluster_y, srng, srng.randint(2, 4))
        # ~half the anchors spawn a tighter satellite tuft a short irregular gap
        # away, so reeds bunch in uneven natural groups instead of even spacing.
        if srng.random() < 0.5:
            gap = srng.randint(10, 26) * (1 if srng.random() < 0.5 else -1)
            sat_y = cluster_y + srng.randint(-4, 4)
            _draw_clump(sx + gap, sat_y, srng, srng.randint(1, 2))

    _apply_grain(surf, 0, top_y, w, h - top_y, 4)


# ══════════════════════════════════════════════════════════════════════════
# Concept 5 — Wood-Plank Boardwalk  (~58px, architectural)
# A foreshortened timber deck of planks running INTO the screen, with grain
# striations, dark shadow gaps between boards, and a warm larch/ochre tone tying
# to the stilt-house / engawa vocabulary. The most architectural texture of the
# five and visually distinct from the other four. Opaque to the bottom; planks
# converge slightly toward a vanishing band for depth — no wave silhouette.
# ══════════════════════════════════════════════════════════════════════════

def _larch(pal):
    """Warm larch/ochre deck timber off the pagoda's _ochre_wood family (the same
    stone_dark->ochre mix the wooden pagoda uses) so the boardwalk reads as the
    same carpentry as the stilt-house engawa."""
    return _mix(pal.get('stone_dark', (95, 70, 55)), (176, 128, 74), 0.66)


def fg_wood_boardwalk(surf, w, gy, h, scroll, pal):
    night = _nightf(pal)
    top_y = gy - 58
    wood = _larch(pal)
    front = _shade(_sat(wood, 1.02), 6)
    back = _mix(_shade(_sat(wood, 0.88), -28), _horizon(pal), 0.08)
    front = _mix(front, (64, 72, 104), 0.30 * night)
    back = _mix(back, (56, 64, 96), 0.34 * night)
    _flat_slab(surf, w, h, top_y, back, front, ease=0.9)

    region_h = h - top_y
    gap = _shade(_sat(wood, 0.7), -52 - int(10 * night))   # dark shadow gap
    grain_dk = _shade(wood, -22)
    grain_lt = _shade(_sat(wood, 1.05), 20)

    # Planks run INTO the screen as long boards separated by vertical shadow gaps.
    # The board edges converge only VERY slightly toward centre with depth — a
    # near-orthographic deck that reads as ground underfoot, not a pier deck
    # pointing at a hard vanishing point. Boards ride the world scroll so the
    # deck slides under the bird. The plank grid is the identity — flat, no wave.
    n_plank = 9
    vanish = w * 0.5
    # Near-orthographic: a very slight pull so boards barely converge — this
    # reads as a flat deck underfoot rather than a pier deck aimed at a hard
    # one-point vanish (the art-director's pier read).
    converge = 0.025
    phase = scroll * 0.20
    board_w = w / n_plank
    for pi in range(n_plank + 1):
        # World-anchored board edge so the seam pattern scrolls; wrap with phase.
        wx = (pi * board_w - (phase % board_w))
        # Front (near, bottom) x and back (far, top) x — pulled toward vanish.
        fx = wx
        bx = vanish + (wx - vanish) * (1 - converge)
        # Shadow gap between boards (a thin dark wedge, wider at the front).
        pygame.draw.line(surf, gap, (int(fx), h - 1), (int(bx), top_y), 2)
        pygame.draw.aaline(surf, _shade(gap, 16),
                           (int(fx) + 1, h - 1), (int(bx) + 1, top_y))

    # Grain striations + knots inside each board: short along-board strokes and a
    # few elliptical knots, brighter near the front. Walk board centres.
    for pi in range(n_plank):
        wx = ((pi + 0.5) * board_w - (phase % board_w))
        fx = wx
        bx = vanish + (wx - vanish) * (1 - converge)
        krng = random.Random((int((phase // board_w) + pi) * 40503) & 0xFFFFFFFF)
        # 2-3 grain lines following the board's converging direction.
        for _ in range(krng.randint(2, 3)):
            o = krng.uniform(-0.34, 0.34)
            fxo = fx + o * board_w
            bxo = bx + o * board_w * (1 - converge)
            col = grain_dk if krng.random() < 0.6 else grain_lt
            pygame.draw.aaline(surf, col, (fxo, h - 2),
                               (bxo, top_y + 1))
        # An occasional knot, on the nearer half only (reads at scale).
        if krng.random() < 0.5:
            ky = top_y + int(krng.uniform(0.55, 0.95) * region_h)
            kx = fx + krng.uniform(-0.25, 0.25) * board_w
            kr = krng.randint(1, 2)
            pygame.draw.ellipse(surf, grain_dk,
                                (int(kx) - kr, ky - kr, kr * 2 + 1, kr + 1))

    # Foreshorten the back edge into the mist so the top line recedes, not steps.
    region_top = h - top_y
    mist_back = _mix(back, _horizon(pal), 0.18 + 0.10 * night)
    recede_h = int(region_top * 0.28)
    for i in range(recede_h):
        t = 1.0 - (i / max(1, recede_h - 1))
        t = t * t
        if t <= 0.01:
            continue
        ln = pygame.Surface((w, 1), pygame.SRCALPHA)
        ln.fill((*_mix(back, mist_back, t), int(170 * t)))
        surf.blit(ln, (0, top_y + i))

    # Cross-board nosing at the front edge is a SOFT, low-contrast, desaturated
    # board cap — the forbidden mountain-crest echo means it must NEVER brighten
    # or go golden at sunset. The nose is derived from the back timber (not the
    # lit front), desaturated ~40% toward neutral and held BELOW the plane value
    # so it can only ever read as a quiet recede, never a hot crest. No horizon
    # warmth, no additive sheen, at any time of day. A 4px feather replaces the
    # old drawn nose lines so the top edge is a gradient, never a stripe.
    nose = _shade(_sat(_mix(back, front, 0.4), 0.6), -8)
    feather = _mix(mist_back, nose, 0.5)
    for i in range(4):
        a = int(130 * (1.0 - i / 4.0))
        ln = pygame.Surface((w, 1), pygame.SRCALPHA)
        ln.fill((*feather, a))
        surf.blit(ln, (0, top_y - 1 + i))


# ══════════════════════════════════════════════════════════════════════════
# Round-5 GROUNDED leads: SHORTER flagstone family + a SAND family.
#
# The round-4 leads shipped too tall (~50px flagstone read as a wall of tile,
# not a floor strip). This round keeps the Flagstone Courtyard DNA — warm
# Songyue sandstone, near->far value fall, soft 4px top feather, opaque fill,
# grain — but drops the band to ~38-42px so it reads LOW and grounded, and
# explores three shape/joint takes on it. It then opens a parallel SAND family
# (~36-40px) on the same scaffolding: warm pale-gold derived from the sandstone
# family, wind-grain, DEAD-STRAIGHT horizontal striations only (never undulating
# arcs), scattered pebbles/shells/tufts.
#
# Shared helpers below keep all six on the same grounded base so they retint
# together with the stage and never grow a wave silhouette.
# ══════════════════════════════════════════════════════════════════════════


def _grounded_base(surf, w, gy, h, top_y, pal, front, back, *,
                   ease=0.82, recede=0.34, feather_mix=0.16,
                   feather_a=140, recede_a=200):
    """Lay the common grounded plane: opaque value-fall slab front->back, a
    back-edge recede lift into the mist, and a tight 4px top-edge feather so the
    join with the mist is a gradient, never a drawn seam. Returns (region_h,
    mist_back) so a concept can keep reusing the same mist tone for its marks."""
    night = _nightf(pal)
    _flat_slab(surf, w, h, top_y, back, front, ease=ease)
    region_h = h - top_y
    mist_back = _mix(back, _horizon(pal), 0.22 + 0.10 * night)
    recede_h = int(region_h * recede)
    for i in range(recede_h):
        t = 1.0 - (i / max(1, recede_h - 1))
        t = t * t
        if t <= 0.01:
            continue
        ln = pygame.Surface((w, 1), pygame.SRCALPHA)
        ln.fill((*_mix(back, mist_back, t), int(recede_a * t)))
        surf.blit(ln, (0, top_y + i))
    feather = _mix(mist_back, _horizon(pal), feather_mix)
    for i in range(4):
        a = int(feather_a * (1.0 - i / 4.0))
        ln = pygame.Surface((w, 1), pygame.SRCALPHA)
        ln.fill((*feather, a))
        surf.blit(ln, (0, top_y - 1 + i))
    return region_h, mist_back


def _sand(pal):
    """Warm pale-gold sand tone derived from the Songyue sandstone family,
    lightened and de-grained toward a soft dune gold so it reads as sand under
    the same light as the pillar's brick, not a separate material."""
    base = _mix(_sandstone(pal), pal.get('ground_mid', (176, 142, 92)), 0.35)
    return _mix(_sat(base, 0.92), (224, 198, 150), 0.55)


# ── Stone 1 — Cut-Stone Temple Flags (~40px) ────────────────────────────────
# Fewer, LARGER dressed rectangular slabs in clean tight joints; an occasional
# worn/mossy slab. The refined, formal temple-courtyard read.

def fg_cut_stone_flags(surf, w, gy, h, scroll, pal):
    night = _nightf(pal)
    top_y = gy - 40
    stone = _sandstone(pal)
    front = _shade(_sat(stone, 1.05), 2)
    back = _mix(_shade(_sat(stone, 0.84), -32), _horizon(pal), 0.16)
    front = _mix(front, (70, 80, 110), 0.30 * night)
    back = _mix(back, (60, 70, 100), 0.34 * night)
    region_h, mist_back = _grounded_base(surf, w, gy, h, top_y, pal, front, back,
                                         ease=0.82, recede=0.32)

    joint = _shade(_mix(stone, (60, 44, 34), 0.5), -10 - int(8 * night))
    moss = _mix(pal.get('foliage_mid', (60, 110, 70)), stone, 0.5)
    moss = _mix(moss, (40, 56, 86), 0.3 * night)

    # FEWER courses (4) of LARGER dressed slabs. Tight clean joints (1px, no
    # value jitter chaos) so the read is formal/refined, not rustic. Running
    # bond is a gentle even half-step — dressed temple flags ARE laid regular,
    # the charm is in size + the rare worn slab, not in irregularity.
    n_course = 4
    for c in range(n_course):
        f0 = c / n_course
        f1 = (c + 1) / n_course
        y_back = _perspective_y(top_y, h, 1.0 - f0)
        y_front = _perspective_y(top_y, h, 1.0 - f1)
        if y_front <= y_back:
            continue
        depth_t = f0
        step = int(48 + 40 * depth_t)        # large dressed flags
        bond = (c % 2) * (step // 2)         # clean even running bond
        jc = _mix(joint, back, max(0.0, 0.4 * (1 - depth_t)))
        # Crisp horizontal course joint with a 1px lit lower lip near the front.
        pygame.draw.line(surf, jc, (0, y_back), (w, y_back), 1)
        if depth_t > 0.4:
            pygame.draw.line(surf, _shade(jc, 16), (0, y_back + 1), (w, y_back + 1), 1)
        speed = 0.18 + 0.10 * depth_t
        for sx, k, srng in _scatter(scroll, w, speed, step, 0xC51 + c):
            jx = sx + bond
            pygame.draw.line(surf, jc, (jx, y_back), (jx, y_front), 1)
            if depth_t > 0.4:
                pygame.draw.line(surf, _shade(jc, 16), (jx + 1, y_back), (jx + 1, y_front), 1)
            # Per-slab VALUE variation so the paving never reads as a perfect
            # repeat as it scrolls: most slabs sit at the base tone, but ~1 in 3
            # carry a gentle lighter- or darker-faced wash (value only, no hue
            # shift). The lift/drop is held low so it tells the slabs apart
            # without lighting a bright patch under the bird lane.
            roll = srng.random()
            ww = step - 6
            if roll < 0.34 and ww > 4:
                dv = srng.choice((-13, -9, 9, 13))
                wp = pygame.Surface((ww, max(3, (y_front - y_back) - 2)),
                                    pygame.SRCALPHA)
                # Brighten with ADD, darken with a low-alpha dark wash, so both
                # stay value-only against whatever the night cool-mix made the base.
                if dv > 0:
                    wp.fill((dv, dv, dv))
                    surf.blit(wp, (jx + 3, y_back + 2),
                              special_flags=pygame.BLEND_RGB_ADD)
                else:
                    wp.fill((-dv, -dv, -dv))
                    surf.blit(wp, (jx + 3, y_back + 2),
                              special_flags=pygame.BLEND_RGB_SUB)
            # Rare worn/mossy slab on top of the value variation — a few moss
            # flecks along the back joint, daytime only. ~1 in 7 so it stays a
            # quiet accent, not a feature.
            if depth_t > 0.4 and roll > 0.86 and night < 0.65:
                for mfx in range(jx + 4, jx + ww, 5):
                    if srng.random() < 0.5:
                        surf.set_at((min(w - 1, mfx), y_back + 2), moss)

    _apply_grain(surf, 0, top_y, w, h - top_y, 4)


# ── Stone 2 — Crazy-Paving Fieldstone (~40px) ───────────────────────────────
# Irregular polygonal stones with mossy joint lines — a rustic flagged path.
# Varied stone shapes, explicitly NOT a grid: each stone is a jittered convex
# blob with its own facets; the mortar gaps are the negative space between them.

def fg_crazy_paving(surf, w, gy, h, scroll, pal):
    night = _nightf(pal)
    top_y = gy - 40
    stone = _sandstone(pal)
    front = _shade(_sat(stone, 1.04), 3)
    back = _mix(_shade(_sat(stone, 0.84), -32), _horizon(pal), 0.16)
    front = _mix(front, (70, 80, 110), 0.30 * night)
    back = _mix(back, (60, 70, 100), 0.34 * night)
    region_h, mist_back = _grounded_base(surf, w, gy, h, top_y, pal, front, back,
                                         ease=0.82, recede=0.32)

    # The mortar is the slab base value; stones are drawn ON TOP as filled
    # polygons slightly LIGHTER than the mortar, so the gaps read as recessed
    # joints. Mossy tint in the joints near the front.
    moss = _mix(pal.get('foliage_mid', (60, 110, 70)), stone, 0.55)
    moss = _mix(moss, (40, 56, 86), 0.3 * night)
    joint = _shade(_mix(stone, (60, 44, 34), 0.5), -14 - int(8 * night))

    # First lay a mortar wash a notch darker than the plane so the gaps between
    # stones read as set-in joints, then stamp irregular stones over it.
    n_course = 4
    for c in range(n_course):
        f0 = c / n_course
        f1 = (c + 1) / n_course
        y_back = _perspective_y(top_y, h, 1.0 - f0)
        y_front = _perspective_y(top_y, h, 1.0 - f1)
        if y_front <= y_back:
            continue
        depth_t = f0
        course_h = y_front - y_back
        # Faint mossy mortar band under this course (so joints read greenish near
        # the front, neutral toward the back). The alpha gains a night floor so
        # the joint-shadow survives after dark instead of letting the polygons
        # collapse toward the flat Cut-Stone read once the base cools.
        mortar = _mix(joint, moss, 0.30 * (1 - depth_t) + 0.10)
        mb = pygame.Surface((w, course_h), pygame.SRCALPHA)
        mb.fill((*mortar, int(60 + 50 * depth_t + 40 * night)))
        surf.blit(mb, (0, y_back))
        # Irregular stones: walk world cells, each a jittered convex polygon that
        # fills most of its cell leaving a thin mortar gap. Stone widths/shapes
        # vary strongly so it never resolves into a grid.
        step = int(30 + 26 * depth_t)
        speed = 0.18 + 0.10 * depth_t
        for sx, k, srng in _scatter(scroll, w, speed, step, 0x7B2 + c):
            sw = step - srng.randint(4, 8)
            inset_t = y_back + 2
            inset_b = y_front - 1
            if inset_b <= inset_t:
                continue
            cx = sx
            face = _shade(_mix(stone, front, 0.4 * depth_t), srng.randint(-8, 10))
            face = _mix(face, (66, 76, 106), 0.30 * night)
            # 5-7 sided jittered polygon roughly filling the cell.
            n_v = srng.randint(5, 7)
            half = sw // 2
            pts = []
            for vi in range(n_v):
                ang = (vi / n_v) * math.tau + srng.uniform(-0.3, 0.3)
                rx = half * (0.7 + srng.uniform(-0.18, 0.18))
                ry = (course_h * 0.5 - 1) * (0.78 + srng.uniform(-0.16, 0.16))
                px = cx + int(math.cos(ang) * rx)
                py = (inset_t + inset_b) // 2 + int(math.sin(ang) * ry)
                pts.append((px, py))
            pygame.draw.polygon(surf, face, pts)
            # Soft lit upper-left facet edge on nearer stones for a little relief.
            if depth_t > 0.35 and night < 0.7:
                lit = [p for p in pts if p[1] <= (inset_t + inset_b) // 2]
                if len(lit) >= 2:
                    pygame.draw.lines(surf, _shade(face, 18), False, lit, 1)
            # A darker contact at the stone foot AND a short dark riser up each
            # side, so the polygon keeps a visible recessed joint into the night
            # (a single foot line alone vanished once the base cooled).
            contact = _shade(face, -20 - int(10 * night))
            pygame.draw.line(surf, contact,
                             (cx - half + 1, inset_b - 1),
                             (cx + half - 1, inset_b - 1), 1)
            side_h = max(1, (inset_b - inset_t) // 3)
            pygame.draw.line(surf, contact, (cx - half + 1, inset_b - 1),
                             (cx - half + 1, inset_b - 1 - side_h), 1)
            pygame.draw.line(surf, contact, (cx + half - 1, inset_b - 1),
                             (cx + half - 1, inset_b - 1 - side_h), 1)

    _apply_grain(surf, 0, top_y, w, h - top_y, 4)


# ── Stone 3 — River-Cobble Paving (~40px) ───────────────────────────────────
# Distinctly NOT the dressed Cut-Stone slab: LARGER irregular ROUNDED river
# cobbles, each a domed ellipse with its own size + tone, bedded in WIDE dark
# mortar joints. Fewer-but-bigger rounded humps in offset courses reads as a
# rough cobbled lane, the opposite of the flat dressed flag.

def fg_cobblestone_setts(surf, w, gy, h, scroll, pal):
    night = _nightf(pal)
    top_y = gy - 40
    stone = _mix(_sandstone(pal), (150, 132, 110), 0.30)   # a touch greyer/cooler
    front = _shade(_sat(stone, 1.02), 3)
    back = _mix(_shade(_sat(stone, 0.86), -30), _horizon(pal), 0.16)
    front = _mix(front, (70, 80, 110), 0.30 * night)
    back = _mix(back, (60, 70, 100), 0.34 * night)
    region_h, mist_back = _grounded_base(surf, w, gy, h, top_y, pal, front, back,
                                         ease=0.82, recede=0.30)

    # WIDE dark mortar — the cobbles sit in deep grout, the defining contrast
    # that separates this from the tight-jointed dressed flags. Lay the whole
    # plane's bedding a notch darker so every cobble reads as a rounded hump
    # lifted out of recessed grout.
    grout = _shade(_sat(stone, 0.74), -38 - int(8 * night))

    # Fewer, larger rounded cobbles in offset courses. Each cobble is a domed
    # ellipse (NOT a radius-rect) with per-cobble width/height/tone jitter, set
    # with a clear gap to its neighbours so the wide grout always shows.
    n_course = 5
    for c in range(n_course):
        f0 = c / n_course
        f1 = (c + 1) / n_course
        y_back = _perspective_y(top_y, h, 1.0 - f0)
        y_front = _perspective_y(top_y, h, 1.0 - f1)
        if y_front <= y_back:
            continue
        depth_t = f0
        ch = max(4, y_front - y_back)
        # Big cobbles: cell step grows strongly toward the player so near cobbles
        # are chunky rounded stones, not little setts.
        step = int(16 + 18 * depth_t)
        bond = (c % 2) * (step // 2)
        speed = 0.20 + 0.10 * depth_t
        # A bedding grout band so the gaps between rounded cobbles read deep.
        gb = pygame.Surface((w, ch), pygame.SRCALPHA)
        gb.fill((*grout, int(120 + 50 * depth_t + 30 * night)))
        surf.blit(gb, (0, y_back))
        for sx, k, srng in _scatter(scroll, w, speed, step, 0x3D9 + c):
            jx = sx + bond
            # Per-cobble size jitter — clearly irregular rounded stones, with a
            # gap kept to the cell edge so the wide grout shows between them.
            cw = step - srng.randint(5, 9)
            chh = max(3, ch - srng.randint(1, 3))
            cap = _shade(_mix(stone, front, 0.5 * depth_t), srng.randint(-12, 16))
            cap = _mix(cap, (66, 76, 106), 0.30 * night)
            ex = jx + (step - cw) // 2
            ey = y_back + (ch - chh) // 2
            # Dark contact ellipse under the cobble for bedded roundness.
            pygame.draw.ellipse(surf, _shade(cap, -26 - int(8 * night)),
                                (ex, ey + 1, cw, chh))
            pygame.draw.ellipse(surf, cap, (ex, ey, cw, chh))
            # Lit dome cap (upper-left arc) so each cobble reads as a 3D hump.
            if night < 0.74 and cw >= 4:
                pygame.draw.arc(surf, _shade(cap, 24),
                                (ex, ey, cw, chh),
                                math.radians(50), math.radians(165), 2)
            # A darker lower-right shoulder.
            pygame.draw.arc(surf, _shade(cap, -22),
                            (ex, ey, cw, chh),
                            math.radians(250), math.radians(350), 1)

    _apply_grain(surf, 0, top_y, w, h - top_y, 3)


# ── Sand 1 — Desert Dune Sand (~38px) ───────────────────────────────────────
# The most minimal sand: warm pale-gold, fine wind-grain, faint DEAD-STRAIGHT
# horizontal ripple striations (never arcs), a few tiny pebbles.

def fg_desert_dune(surf, w, gy, h, scroll, pal):
    night = _nightf(pal)
    top_y = gy - 38
    sand = _sand(pal)
    # Hold a clear front->back value-fall even at night: the front lip keeps a
    # touch of warm lift while the back deepens, so dusk/night don't flatten to a
    # dead fill. The night cool-mix is applied AFTER the front/back spread so the
    # spread survives instead of collapsing the two tones together.
    front = _shade(_sat(sand, 1.02), 6)
    back = _shade(_sat(sand, 0.88), -26)
    back = _mix(back, _horizon(pal), 0.18)
    front = _mix(front, (74, 84, 116), 0.26 * night)
    back = _mix(back, (52, 62, 96), 0.40 * night)
    region_h, mist_back = _grounded_base(surf, w, gy, h, top_y, pal, front, back,
                                         ease=0.92, recede=0.30)

    # Wind ripples: DEAD-STRAIGHT horizontal striation pairs (a faint shadow line
    # + a faint lit line just above it) marching down the plane, packed tighter
    # toward the back. NO curvature whatsoever — a ripple is a straight line.
    rip_dk = _shade(_sat(sand, 0.86), -16 - int(6 * night))
    rip_lt = _shade(sand, 12)
    rip_lt = _mix(rip_lt, mist_back, 0.2)
    n_rip = 14
    for ri in range(n_rip):
        f = (ri + 0.5) / n_rip
        y = _perspective_y(top_y, h, 1.0 - f)
        depth_t = f
        # Broken dashes so the striation reads as wind-blown grain banding, not a
        # ruled line, and never a continuous bright seam. Phase scrolls with world.
        ph = int(scroll * (0.16 + 0.08 * depth_t))
        dash = 7 + int(depth_t * 5)
        a = int(40 + 60 * depth_t)
        for x0 in range(-(ph % (dash * 2)), w, dash * 2):
            seg = pygame.Surface((dash, 1), pygame.SRCALPHA)
            seg.fill((*rip_dk, a))
            surf.blit(seg, (x0, y))
            if depth_t > 0.3 and night < 0.7:
                seg2 = pygame.Surface((dash, 1), pygame.SRCALPHA)
                seg2.fill((*rip_lt, int(a * 0.7)))
                surf.blit(seg2, (x0 + dash // 2, y - 1))

    # A few tiny pebbles half-sunk, larger/brighter toward the front.
    for sx, k, srng in _scatter(scroll, w, 0.22, 40, 0x5A1):
        py = top_y + int(srng.uniform(0.4, 0.96) * region_h)
        depth_t = (py - top_y) / max(1, region_h)
        if srng.random() > 0.35 + 0.35 * depth_t:
            continue
        pr = 1 + int(depth_t * 1.6)
        pc = _mix(sand, (170, 150, 122), 0.5)
        pc = _mix(pc, (60, 70, 100), 0.3 * night)
        pygame.draw.ellipse(surf, _shade(pc, -20), (sx - pr, py - pr // 2, pr * 2, pr + 1))
        if night < 0.65:
            surf.set_at((sx, py - pr // 2), _shade(pc, 22))

    # Explicit grain speckle that survives dusk/night: a sparse scatter of single
    # pixels a few % BRIGHTER than the local base, biased to the lower third so
    # the near sand keeps a visible tooth after dark (the ordered-dither grain
    # below shrinks to near-nothing once the plane darkens). Scroll-locked via
    # _scatter so the speckle rides the dunes instead of crawling in screen space.
    spk = _mix(front, (255, 244, 214), 0.22)
    spk = _mix(spk, (120, 132, 160), 0.5 * night)
    for sx, k, srng in _scatter(scroll, w, 0.24, 5, 0x5C9):
        py = top_y + int(srng.uniform(0.34, 1.0) * region_h)
        depth_t = (py - top_y) / max(1, region_h)
        if srng.random() > 0.16 + 0.30 * depth_t:
            continue
        surf.set_at((sx, py), _mix(spk, mist_back, max(0.0, 0.5 * (1 - depth_t))))

    # Slightly heavier grain than stone for the fine sand tooth; scroll-locked so
    # the tooth tracks the dunes rather than shimmering under motion.
    _apply_grain_scroll(surf, 0, top_y, w, h - top_y, 6, scroll)


# ── Sand 2 — Wet-Shore Sand (~38px) ─────────────────────────────────────────
# Packed tan sand with a darker DAMP TIDE-LINE band near the front, scattered
# shells/pebbles, a subtle low sheen. Coastal.

def fg_wet_shore(surf, w, gy, h, scroll, pal):
    night = _nightf(pal)
    top_y = gy - 38
    sand = _mix(_sand(pal), (200, 178, 140), 0.3)    # packed tan, a touch cooler
    front = _shade(_sat(sand, 1.0), 2)
    back = _mix(_shade(_sat(sand, 0.9), -20), _horizon(pal), 0.18)
    front = _mix(front, (66, 76, 108), 0.30 * night)
    back = _mix(back, (56, 66, 98), 0.34 * night)
    region_h, mist_back = _grounded_base(surf, w, gy, h, top_y, pal, front, back,
                                         ease=0.85, recede=0.30)

    # Damp patches — NOT a tide-line. A continuous darker/wet horizontal band
    # across the lane read as the forbidden bright dashed seam fighting the bird.
    # Instead the damp reads as SHORT, vertically-jittered, low-contrast smears
    # scattered over the near half: each is a soft darker-cool blot a few px tall,
    # capped so it can never lift more than ~10-12% over the surrounding sand and
    # never aligns into a continuous horizontal run. Anchored to world-x so the
    # damp rides the surface as it scrolls.
    damp = _mix(_sat(sand, 0.88), (118, 116, 116), 0.32)
    damp = _mix(damp, (50, 60, 92), 0.34 * night)
    for sx, k, srng in _scatter(scroll, w, 0.22, 30, 0x6C4):
        # Bias damp lower (nearer) where wet sand would sit, but jitter the y so
        # no two smears share a row -> no horizontal seam can form.
        py = top_y + int(srng.uniform(0.46, 0.98) * region_h)
        if srng.random() < 0.35:
            continue
        depth_t = (py - top_y) / max(1, region_h)
        sw = srng.randint(16, 34)
        sh = srng.randint(2, 4)
        # Cap the alpha low so the value shift stays within ~10-12% of the sand.
        a = int(26 + 16 * depth_t)
        blot = pygame.Surface((sw, sh), pygame.SRCALPHA)
        blot.fill((*damp, a))
        surf.blit(blot, (sx - sw // 2, py - sh // 2))
        # A faint cool-dark lower contact under the nearer smears so the blot
        # reads as damp depth, not just a tint. Still per-smear, never a run.
        if depth_t > 0.5:
            edge = pygame.Surface((sw - 4, 1), pygame.SRCALPHA)
            edge.fill((*_shade(damp, -10), a))
            surf.blit(edge, (sx - sw // 2 + 2, py - sh // 2 + sh))

    # Scattered shells + pebbles, denser on the damp band.
    for sx, k, srng in _scatter(scroll, w, 0.22, 34, 0x9F3):
        py = top_y + int(srng.uniform(0.42, 0.96) * region_h)
        depth_t = (py - top_y) / max(1, region_h)
        if srng.random() > 0.34 + 0.4 * depth_t:
            continue
        pr = 1 + int(depth_t * 2.0)
        if srng.random() < 0.32:
            # A little fan shell — a pale wedge with 2-3 rib lines.
            shc = _mix((230, 214, 196), sand, 0.35)
            shc = _mix(shc, (70, 80, 108), 0.3 * night)
            sw = pr + 2
            pygame.draw.polygon(surf, shc, [
                (sx, py + 1), (sx - sw, py - sw), (sx + sw, py - sw)])
            pygame.draw.line(surf, _shade(shc, -22), (sx, py + 1), (sx, py - sw), 1)
            pygame.draw.line(surf, _shade(shc, -16), (sx, py + 1), (sx - sw + 1, py - sw + 1), 1)
            pygame.draw.line(surf, _shade(shc, -16), (sx, py + 1), (sx + sw - 1, py - sw + 1), 1)
        else:
            pc = _mix(sand, (160, 150, 132), 0.5)
            pc = _mix(pc, (60, 70, 100), 0.3 * night)
            pygame.draw.ellipse(surf, _shade(pc, -20), (sx - pr, py - pr // 2, pr * 2, pr + 1))
            if night < 0.65:
                surf.set_at((sx, py - pr // 2), _shade(pc, 22))

    _apply_grain_scroll(surf, 0, top_y, w, h - top_y, 5, scroll)


# ── Sand 3 — Riverbank Sandbar (~38px) ──────────────────────────────────────
# Coarse-grained sand, scattered small flat stones, sparse DRY grass tufts at
# the back edge. The most "natural land" of the sand family.

def fg_riverbank_sandbar(surf, w, gy, h, scroll, pal):
    night = _nightf(pal)
    top_y = gy - 38
    sand = _mix(_sand(pal), (206, 184, 142), 0.25)
    front = _shade(_sat(sand, 1.02), 3)
    back = _mix(_shade(_sat(sand, 0.9), -22), _horizon(pal), 0.18)
    front = _mix(front, (68, 78, 108), 0.30 * night)
    back = _mix(back, (58, 68, 100), 0.34 * night)
    region_h, mist_back = _grounded_base(surf, w, gy, h, top_y, pal, front, back,
                                         ease=0.86, recede=0.30)

    # Coarse grain mottle: a sparse scatter of 1px lighter/darker specks across
    # the plane gives the coarse riverbar tooth without any line work.
    for sx, k, srng in _scatter(scroll, w, 0.26, 6, 0x2E8):
        py = top_y + int(srng.uniform(0.18, 1.0) * region_h)
        depth_t = (py - top_y) / max(1, region_h)
        if srng.random() < 0.4:
            continue
        spec = _shade(sand, srng.randint(-22, 22))
        spec = _mix(spec, mist_back, max(0.0, 0.4 * (1 - depth_t)))
        surf.set_at((sx, py), spec)

    # Scattered small FLAT river stones — low ellipses, half-sunk, varied tones,
    # larger toward the front.
    for sx, k, srng in _scatter(scroll, w, 0.22, 26, 0x4B7):
        py = top_y + int(srng.uniform(0.4, 0.96) * region_h)
        depth_t = (py - top_y) / max(1, region_h)
        if srng.random() > 0.4 + 0.4 * depth_t:
            continue
        pw = 2 + int(depth_t * 4)
        ph = max(1, pw // 2)
        pc = _mix(sand, (150, 142, 128), 0.55)
        pc = _mix(pc, _shade(pal.get('stone_dark', (95, 80, 70)), 20),
                  srng.uniform(0.0, 0.35))
        pc = _mix(pc, (60, 70, 100), 0.3 * night)
        pygame.draw.ellipse(surf, _shade(pc, -18), (sx - pw, py - ph + 1, pw * 2, ph + 1))
        pygame.draw.ellipse(surf, pc, (sx - pw, py - ph, pw * 2, ph + 1))
        if night < 0.65:
            pygame.draw.line(surf, _shade(pc, 22), (sx - pw + 1, py - ph),
                             (sx + pw - 2, py - ph), 1)

    # A FEW clearly-SILHOUETTED dry-grass tufts at the BACK edge (where the bar
    # meets the bank). The round-5 many-thin-blade clumps read as noisy dark
    # flecks at 1x; here each firing anchor draws ONE bold readable tuft — a
    # filled straw fan (a solid silhouette) plus 2-3 outer blades for shape, taller
    # and far more sparse so 2-3 distinct tufts carry the rear, never a flecky
    # field. Confined to the rear ~28% so they never crowd the bird lane.
    straw = _mix((198, 184, 130), sand, 0.28)
    straw = _mix(straw, (96, 104, 120), 0.34 * night)
    straw_dk = _shade(straw, -30)
    for sx, k, srng in _scatter(scroll, w, 0.2, 116, 0x8D2):
        if srng.random() < 0.45:
            continue
        ty = top_y + int(srng.uniform(0.08, 0.26) * region_h)
        th_ = srng.randint(11, 17)
        spread = srng.randint(5, 8)
        lean = srng.randint(-3, 3)
        # Solid silhouette fan so the tuft reads as a shape, not a flick scatter.
        apex = (sx + lean, ty - th_)
        pygame.draw.polygon(surf, straw_dk, [
            (sx - spread, ty), (sx + spread, ty),
            (apex[0] + 2, apex[1] + 2), (apex[0] - 2, apex[1] + 2)])
        # A couple of bright outer blades to catch the light and define the fan.
        for bo in (-spread, -spread // 2, spread // 2, spread):
            bx = sx + bo
            bh = th_ - abs(bo)
            pygame.draw.line(surf, straw, (bx, ty),
                             (bx + lean // 2, ty - max(4, bh)), 1)

    # Coarse riverbar tooth + scroll-locked dither grain (the screen-space grain
    # crawled under motion).
    _apply_grain_scroll(surf, 0, top_y, w, h - top_y, 6, scroll)


# ── registry (order matches the brief) ──────────────────────────────────────

# Round-4 originals (kept so the baseline row can render the ~50px flagstone).
CONCEPTS = [
    ("Flagstone Courtyard", fg_flagstone_courtyard),
    ("Sun-Cracked Packed Earth", fg_cracked_earth),
    ("Raked Zen-Gravel Garden", fg_zen_gravel),
    ("Ink-Wash Meadow", fg_inkwash_meadow),
    ("Wood-Plank Boardwalk", fg_wood_boardwalk),
]

# Round-5 sheet: baseline (~50px flagstone) + 3 shorter stone + 3 sand.
CONCEPTS_R5 = [
    ("Flagstone Courtyard (BASELINE ~50px)", fg_flagstone_courtyard),
    ("Cut-Stone Temple Flags", fg_cut_stone_flags),
    ("Crazy-Paving Fieldstone", fg_crazy_paving),
    ("Cobblestone Setts", fg_cobblestone_setts),
    ("Desert Dune Sand", fg_desert_dune),
    ("Wet-Shore Sand", fg_wet_shore),
    ("Riverbank Sandbar", fg_riverbank_sandbar),
]

# Round-6 sheet: same 7-row layout, polishing the two LEADS (Cut-Stone +
# Desert Dune) per the art-director punch list while keeping the full
# 3-stone / 3-sand comparison.
CONCEPTS_R6 = [
    ("Flagstone Courtyard (BASELINE ~50px)", fg_flagstone_courtyard),
    ("Cut-Stone Temple Flags", fg_cut_stone_flags),
    ("Crazy-Paving Fieldstone", fg_crazy_paving),
    ("River-Cobble Paving", fg_cobblestone_setts),
    ("Desert Dune Sand", fg_desert_dune),
    ("Wet-Shore Sand", fg_wet_shore),
    ("Riverbank Sandbar", fg_riverbank_sandbar),
]


# ══════════════════════════════════════════════════════════════════════════
# Round 7 — PREMIUM 45px HERO STRIP.
#
# The round-5/6 floors painted from `top_y = gy - 40..50` down to h, so the
# band was 85-95px tall and its top edge floated ~40-50px ABOVE the real
# GROUND_Y, overlapping up into the mountain zone. They also leaned on a
# muted, dithered, foreshortened "mist recede" wash that read as a near echo
# of the ink-wash ridges rather than its own material.
#
# Round 7 fixes both. EVERY round-7 floor's top edge sits at `top_y = gy`
# (y=595) so the painted plane occupies EXACTLY the original 45px strip
# (595->640), flush with the mountain bases. And every concept is conceived
# for that 45px hero strip with a SLICK, HIGH-END light model: a crisp
# contact-shadow line where the floor meets the mountains (its own object,
# not a continuation of the ridges), a controlled value-fall, refined
# micro-relief with paired lit/shadow edges, a tasteful BLEND_RGB_ADD
# specular sheen near the front lip, and a FINE dither tooth — not the muted
# hazy wash of the prior rounds. Each carries its own material identity:
# polished temple paving / inlaid mosaic / domed river cobble / golden dune
# sand / satin wind-rippled sand / riverbar sand.
# ══════════════════════════════════════════════════════════════════════════


def _premium_base(surf, w, gy, h, pal, front, back, *, ease=1.0,
                  contact_a=150, sheen=None, sheen_a=30):
    """The round-7 grounded plane on the 45px hero strip: an OPAQUE value-fall
    slab from a FLAT top edge at GROUND_Y down to h, a CRISP 2px contact
    shadow right at the top line (so the floor reads as its own solid object
    meeting the mountains — never a bright seam, never a hazy recede), and an
    optional soft BLEND_RGB_ADD specular sheen pooled in the near third for a
    premium, lit-material read. Returns (top_y, region_h, night)."""
    night = _nightf(pal)
    top_y = gy                       # FLUSH with the mountain bases at y=595.
    region_h = h - top_y             # exactly 45px on the live canvas.
    _flat_slab(surf, w, h, top_y, back, front, ease=ease)

    # Crisp contact shadow at the floor's back edge: a 2px darkened lip that
    # sets the plane apart from the mountains as a distinct object. Darkened,
    # never lightened, so it can never read as the forbidden bright crest.
    csh = _shade(_sat(back, 0.9), -22 - int(8 * night))
    sh = pygame.Surface((w, 3), pygame.SRCALPHA)
    sh.fill((*csh, contact_a))
    surf.blit(sh, (0, top_y), special_flags=pygame.BLEND_RGB_SUB)
    # A single faint lit hairline just under the contact line gives the lip a
    # tasteful soft bevel (premium edge), held low so it never seams.
    bev = pygame.Surface((w, 1), pygame.SRCALPHA)
    bev.fill((*_mix(front, (255, 250, 235), 0.25), int(46 * (1.0 - night))))
    surf.blit(bev, (0, top_y + 3), special_flags=pygame.BLEND_RGB_ADD)

    # Premium near-lip specular sheen: a soft additive glow pooled across the
    # FRONT third so the material reads as catching the stage light. Pure
    # additive + a vertical falloff so it never makes a hard horizontal band.
    if sheen is not None:
        sh_top = top_y + int(region_h * 0.45)
        for y in range(sh_top, h):
            t = (y - sh_top) / max(1, h - 1 - sh_top)
            a = int(sheen_a * (t ** 1.4) * (1.0 - 0.55 * night))
            if a <= 0:
                continue
            ln = pygame.Surface((w, 1), pygame.SRCALPHA)
            ln.fill((*sheen, a))
            surf.blit(ln, (0, y), special_flags=pygame.BLEND_RGB_ADD)
    return top_y, region_h, night


def _spec_dab(surf, x, y, w, hh, col, a):
    """A small soft additive specular dab — the premium highlight beat. A tiny
    SRCALPHA tile filled with a low-alpha bright tone, blitted ADD so it lifts
    a controlled glint on a stone face / ripple crest without a hard edge."""
    if w <= 0 or hh <= 0:
        return
    dab = pygame.Surface((w, hh), pygame.SRCALPHA)
    dab.fill((*col, a))
    surf.blit(dab, (x, y), special_flags=pygame.BLEND_RGB_ADD)


# ── Stone A — Polished Temple Pavement (45px, top@595) ───────────────────────
# Large dressed flagstones, but PREMIUM: crisp beveled joints (a 1px dark
# riser + a 1px lit upper lip), per-slab specular glints, a controlled satin
# sheen near the lip. Reads as polished, expensive inlaid temple stone — not
# the muted dithered Cut-Stone repeat.

def fg_polished_pavement(surf, w, gy, h, scroll, pal):
    stone = _sandstone(pal)
    # Rich-but-controlled colour: a warm lit front, a cooler set-back, both
    # kept saturated enough to read as crafted stone, not hazy ground.
    front = _shade(_sat(stone, 1.08), 6)
    back = _shade(_sat(stone, 0.92), -20)
    night = _nightf(pal)
    front = _mix(front, (66, 78, 112), 0.28 * night)
    back = _mix(back, (54, 66, 100), 0.32 * night)
    sheen = _mix((255, 246, 222), front, 0.0)
    top_y, region_h, night = _premium_base(
        surf, w, gy, h, pal, front, back, ease=0.95, sheen=sheen, sheen_a=22)

    joint_dk = _shade(_mix(stone, (54, 40, 30), 0.55), -16 - int(8 * night))
    joint_lt = _mix(front, (255, 248, 226), 0.30)

    # THREE crisp courses on the 45px strip — large dressed flags, tight clean
    # joints. The premium read is the bevel: every joint is a 1px dark riser
    # with a 1px lit upper lip, so each flag sits proud with a defined edge.
    n_course = 3
    for c in range(n_course):
        f0 = c / n_course
        f1 = (c + 1) / n_course
        y_back = _perspective_y(top_y, h, 1.0 - f0)
        y_front = _perspective_y(top_y, h, 1.0 - f1)
        if y_front <= y_back:
            continue
        depth_t = f0
        step = int(54 + 46 * depth_t)        # large dressed flags
        bond = (c % 2) * (step // 2)
        # Crisp horizontal course joint: dark riser + lit lip just below it.
        pygame.draw.line(surf, joint_dk, (0, y_back), (w, y_back), 1)
        if y_back + 1 < y_front:
            pygame.draw.line(surf, joint_lt, (0, y_back + 1), (w, y_back + 1), 1)
        speed = 0.18 + 0.10 * depth_t
        for sx, k, srng in _scatter(scroll, w, speed, step, 0xE71 + c):
            jx = sx + bond
            # Vertical joint: a crisp dark riser with a lit right lip (light
            # falls from upper-left), so the flag edge reads beveled + proud.
            pygame.draw.line(surf, joint_dk, (jx, y_back), (jx, y_front), 1)
            pygame.draw.line(surf, joint_lt, (jx + 1, y_back + 1),
                             (jx + 1, y_front), 1)
            # Per-slab face: a faint specular glint on ~1 in 2 near slabs — a
            # soft additive dab pooled toward the slab's lit upper-left, the
            # premium "polished" beat. Kept low + per-slab, never a seam.
            if depth_t > 0.32 and srng.random() < 0.5:
                gw = max(4, step - 12)
                gh = max(2, (y_front - y_back) // 2)
                _spec_dab(surf, jx + 4, y_back + 2, gw, gh,
                          (255, 247, 224),
                          int(18 + 16 * depth_t) - int(10 * night))
            # ~1 in 4 near slabs carry a subtle darker inlay rectangle (a
            # polished panel inset), giving the floor a designed, tiled feel.
            if depth_t > 0.4 and srng.random() < 0.26:
                iw = max(4, step - 16)
                ih = max(2, (y_front - y_back) - 6)
                inlay = pygame.Surface((iw, ih), pygame.SRCALPHA)
                inlay.fill((10, 8, 6, 30))
                surf.blit(inlay, (jx + 6, y_back + 3),
                          special_flags=pygame.BLEND_RGB_SUB)
                pygame.draw.rect(surf, joint_lt, (jx + 6, y_back + 3, iw, ih), 1)

    _apply_grain(surf, 0, top_y, w, region_h, 3)


# ── Stone B — Inlaid Geometric Mosaic (45px, top@595) ────────────────────────
# A polished stone band laid as a repeating geometric mosaic: a fine inlaid
# fret border at the back lip, then diamond/lozenge tessellation across the
# near band, each tile catching a crisp light edge. The most "designed +
# expensive" of the stone takes — its own material identity, distinct from
# the ridges and from the dressed flags.

def fg_inlaid_mosaic(surf, w, gy, h, scroll, pal):
    stone = _sandstone(pal)
    # Two-tone mosaic: a warm light tile + a cool dark tile, so the pattern
    # reads as inlay, not texture. Both stay rich/controlled.
    light = _shade(_sat(stone, 1.05), 12)
    dark = _shade(_sat(_mix(stone, (120, 92, 70), 0.5), 0.95), -10)
    night = _nightf(pal)
    front = _mix(light, (66, 78, 112), 0.26 * night)
    back = _mix(_shade(light, -22), (54, 66, 100), 0.32 * night)
    top_y, region_h, night = _premium_base(
        surf, w, gy, h, pal, front, back, ease=0.95,
        sheen=_mix((255, 244, 220), light, 0.0), sheen_a=20)

    d_light = _mix(light, (66, 78, 112), 0.26 * night)
    d_dark = _mix(dark, (50, 62, 96), 0.30 * night)
    grout = _shade(_mix(stone, (54, 40, 30), 0.5), -16 - int(8 * night))
    edge_lt = _mix(d_light, (255, 250, 232), 0.35)

    # A fine inlaid FRET (key-pattern) border just below the contact line:
    # crisp short dark+lit strokes stepping along the back lip, the premium
    # temple-inlay signature. Scroll-locked so it rides the floor.
    fret_y = top_y + 5
    for sx, k, srng in _scatter(scroll, w, 0.16, 14, 0x1F4):
        pygame.draw.line(surf, grout, (sx, fret_y), (sx, fret_y + 4), 1)
        pygame.draw.line(surf, grout, (sx, fret_y), (sx + 5, fret_y), 1)
        pygame.draw.line(surf, edge_lt, (sx + 1, fret_y + 1),
                         (sx + 1, fret_y + 4), 1)

    # Diamond/lozenge tessellation across the near band: each cell a filled
    # rotated square alternating light/dark, edged with a crisp lit upper-left
    # and dark lower-right so every tile reads as a beveled inlay piece.
    band_top = top_y + 12
    cell = 16
    row = 0
    y = band_top
    while y < h:
        ch = min(cell, h - y)
        speed = 0.18 + 0.06 * ((y - top_y) / max(1, region_h))
        for sx, k, srng in _scatter(scroll, w, speed, cell, 0x2A8 + row):
            cx = sx + (cell // 2 if row % 2 else 0)
            cy = y + ch // 2
            r = cell // 2 - 1
            tile = d_light if (k + row) % 2 == 0 else d_dark
            # Diamond face.
            pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
            pygame.draw.polygon(surf, tile, pts)
            # Crisp lit upper-left edge + dark lower-right edge = beveled inlay.
            pygame.draw.line(surf, edge_lt, (cx - r, cy), (cx, cy - r), 1)
            pygame.draw.line(surf, edge_lt, (cx, cy - r), (cx + r, cy), 1)
            pygame.draw.line(surf, grout, (cx + r, cy), (cx, cy + r), 1)
            pygame.draw.line(surf, grout, (cx, cy + r), (cx - r, cy), 1)
            # A small specular glint on the lit shoulder of near light tiles.
            if tile is d_light and cy > top_y + region_h * 0.5:
                _spec_dab(surf, cx - 2, cy - r + 1, 3, 3, (255, 248, 226),
                          22 - int(12 * night))
        y += ch
        row += 1

    _apply_grain(surf, 0, top_y, w, region_h, 3)


# ── Stone C — Glazed River-Cobble (45px, top@595) ────────────────────────────
# The River-Cobble direction carried forward but PREMIUM: fewer, larger domed
# cobbles bedded in crisp dark grout, each with a defined dark contact, a lit
# upper-left dome arc, AND a tight additive specular dab on the crown so the
# stones read as glazed/wet-polished river rock — not the muted hump field.

def fg_glazed_cobble(surf, w, gy, h, scroll, pal):
    stone = _mix(_sandstone(pal), (150, 134, 114), 0.34)
    front = _shade(_sat(stone, 1.04), 6)
    back = _shade(_sat(stone, 0.9), -18)
    night = _nightf(pal)
    front = _mix(front, (66, 78, 112), 0.28 * night)
    back = _mix(back, (54, 66, 100), 0.32 * night)
    top_y, region_h, night = _premium_base(
        surf, w, gy, h, pal, front, back, ease=0.95,
        sheen=_mix((230, 240, 255), front, 0.0), sheen_a=16)

    grout = _shade(_sat(stone, 0.74), -40 - int(8 * night))

    # THREE courses of large domed cobbles on the strip; wide crisp grout.
    n_course = 3
    for c in range(n_course):
        f0 = c / n_course
        f1 = (c + 1) / n_course
        y_back = _perspective_y(top_y, h, 1.0 - f0)
        y_front = _perspective_y(top_y, h, 1.0 - f1)
        if y_front <= y_back:
            continue
        depth_t = f0
        ch = max(5, y_front - y_back)
        step = int(20 + 22 * depth_t)
        bond = (c % 2) * (step // 2)
        speed = 0.20 + 0.10 * depth_t
        # Crisp grout bedding band (not a hazy wash) so gaps read deep + clean.
        gb = pygame.Surface((w, ch), pygame.SRCALPHA)
        gb.fill((*grout, int(150 + 40 * depth_t)))
        surf.blit(gb, (0, y_back))
        for sx, k, srng in _scatter(scroll, w, speed, step, 0x6E2 + c):
            jx = sx + bond
            cw = step - srng.randint(5, 9)
            chh = max(4, ch - srng.randint(1, 3))
            cap = _shade(_mix(stone, front, 0.55 * depth_t), srng.randint(-10, 16))
            cap = _mix(cap, (62, 74, 106), 0.28 * night)
            ex = jx + (step - cw) // 2
            ey = y_back + (ch - chh) // 2
            # Crisp dark contact ellipse under each cobble for bedded roundness.
            pygame.draw.ellipse(surf, _shade(cap, -30 - int(8 * night)),
                                (ex, ey + 1, cw, chh))
            pygame.draw.ellipse(surf, cap, (ex, ey, cw, chh))
            # Lit upper-left dome arc + dark lower-right shoulder = crisp 3D.
            if cw >= 5:
                pygame.draw.arc(surf, _shade(cap, 28),
                                (ex, ey, cw, chh),
                                math.radians(55), math.radians(165), 2)
                pygame.draw.arc(surf, _shade(cap, -24),
                                (ex, ey, cw, chh),
                                math.radians(250), math.radians(350), 1)
            # Premium glaze glint: a tight additive specular dab on the crown
            # of near cobbles so they read as wet-polished river stone.
            if depth_t > 0.35 and cw >= 6 and night < 0.78:
                _spec_dab(surf, ex + cw // 4, ey + chh // 5,
                          max(2, cw // 4), max(2, chh // 3),
                          (255, 252, 240), 30 - int(16 * night))

    _apply_grain(surf, 0, top_y, w, region_h, 3)


# ── Sand A — Golden Desert Dune (45px, top@595) ──────────────────────────────
# Refined warm golden sand with CRISP wind-ripple micro-relief: each ripple is
# a paired lit ridge-crest + shadow trough (not a hazy dashed line), packed
# tighter to the back, with a satin specular sheen near the lip and a fine
# scroll-locked tooth. Reads as designed, expensive desert sand.

def fg_golden_dune(surf, w, gy, h, scroll, pal):
    sand = _sand(pal)
    front = _shade(_sat(sand, 1.06), 8)
    back = _shade(_sat(sand, 0.92), -18)
    night = _nightf(pal)
    front = _mix(front, (70, 82, 116), 0.24 * night)
    back = _mix(back, (52, 64, 98), 0.36 * night)
    top_y, region_h, night = _premium_base(
        surf, w, gy, h, pal, front, back, ease=1.0,
        sheen=_mix((255, 244, 206), front, 0.0), sheen_a=26)

    # Wind ripples as CRISP micro-relief: for each ripple line a 1px shadow
    # trough with a 1px lit crest immediately above it (the light catches the
    # windward face). Solid short strokes, not hazy dashes — the relief reads
    # as sculpted ripple, refined and defined. Packed tighter toward the back.
    rip_dk = _shade(_sat(sand, 0.86), -22 - int(6 * night))
    rip_lt = _mix(_shade(sand, 18), (255, 248, 214), 0.30)
    rip_lt = _mix(rip_lt, (120, 132, 162), 0.5 * night)
    n_rip = 10
    for ri in range(n_rip):
        f = (ri + 0.5) / n_rip
        y = _perspective_y(top_y, h, 1.0 - f)
        depth_t = f
        # Gentle per-segment crest jitter (a few px) so the ripple reads as
        # wind-sculpted relief, not a ruled line — still essentially straight,
        # never an undulating arc.
        ph = int(scroll * (0.16 + 0.08 * depth_t))
        seg = 10 + int(depth_t * 8)
        a_dk = int(70 + 60 * depth_t)
        a_lt = int(50 + 70 * depth_t)
        x = -(ph % (seg * 2))
        while x < w:
            jit = ((x // seg) % 3) - 1            # -1,0,1 deterministic wobble
            yy = y + jit
            shadow = pygame.Surface((seg, 1), pygame.SRCALPHA)
            shadow.fill((*rip_dk, a_dk))
            surf.blit(shadow, (x, yy))
            if night < 0.72:
                crest = pygame.Surface((seg, 1), pygame.SRCALPHA)
                crest.fill((*rip_lt, a_lt))
                surf.blit(crest, (x, yy - 1), special_flags=pygame.BLEND_RGB_ADD)
            x += seg

    # A few tiny pebbles, larger/brighter toward the front, each with a crisp
    # lit top pixel — a small premium relief beat on the otherwise smooth sand.
    for sx, k, srng in _scatter(scroll, w, 0.22, 44, 0x5B2):
        py = top_y + int(srng.uniform(0.5, 0.96) * region_h)
        depth_t = (py - top_y) / max(1, region_h)
        if srng.random() > 0.3 + 0.35 * depth_t:
            continue
        pr = 1 + int(depth_t * 1.6)
        pc = _mix(sand, (172, 152, 124), 0.5)
        pc = _mix(pc, (60, 70, 100), 0.3 * night)
        pygame.draw.ellipse(surf, _shade(pc, -22),
                            (sx - pr, py - pr // 2, pr * 2, pr + 1))
        if night < 0.7:
            surf.set_at((sx, py - pr // 2), _shade(pc, 26))

    # Fine scroll-locked tooth (kept low so it stays a refined micro-grain, not
    # a hazy dither wash).
    _apply_grain_scroll(surf, 0, top_y, w, region_h, 4, scroll)


# ── Sand B — Satin Rippled Sand (45px, top@595) ──────────────────────────────
# A finer, smoother satin sand: denser low-amplitude ripple relief + a broad
# soft specular sheen sweeping the near band, giving a polished silk-dune look
# distinct from the coarser golden dune. Its own refined material identity.

def fg_satin_sand(surf, w, gy, h, scroll, pal):
    sand = _mix(_sand(pal), (236, 212, 168), 0.4)   # paler, silkier gold
    front = _shade(_sat(sand, 1.05), 8)
    back = _shade(_sat(sand, 0.94), -14)
    night = _nightf(pal)
    front = _mix(front, (72, 84, 116), 0.24 * night)
    back = _mix(back, (54, 66, 100), 0.34 * night)
    top_y, region_h, night = _premium_base(
        surf, w, gy, h, pal, front, back, ease=1.0,
        sheen=_mix((255, 248, 220), front, 0.0), sheen_a=34)

    # Denser, lower-amplitude satin ripples: closely-spaced crisp crest lines,
    # each a 1px lit line over a 1px shadow, so the surface reads as combed silk
    # sand. Phase scrolls; jitter is tiny so the read stays smooth + refined.
    rip_dk = _shade(_sat(sand, 0.9), -16 - int(6 * night))
    rip_lt = _mix(_shade(sand, 20), (255, 250, 224), 0.35)
    n_rip = 16
    for ri in range(n_rip):
        f = (ri + 0.5) / n_rip
        y = _perspective_y(top_y, h, 1.0 - f)
        depth_t = f
        ph = int(scroll * (0.15 + 0.08 * depth_t))
        seg = 14 + int(depth_t * 10)
        a_dk = int(46 + 44 * depth_t)
        a_lt = int(40 + 60 * depth_t)
        x = -(ph % (seg * 2))
        while x < w:
            shadow = pygame.Surface((seg, 1), pygame.SRCALPHA)
            shadow.fill((*rip_dk, a_dk))
            surf.blit(shadow, (x, y))
            if night < 0.74:
                crest = pygame.Surface((seg, 1), pygame.SRCALPHA)
                crest.fill((*rip_lt, a_lt))
                surf.blit(crest, (x + seg // 2, y - 1),
                          special_flags=pygame.BLEND_RGB_ADD)
            x += seg

    # A broad soft satin highlight sweep near the lip — a wide low-alpha
    # additive ellipse so the silk sand catches a controlled sheen pool (the
    # premium beat), held below night so dusk/night stay matte.
    if night < 0.7:
        sweep_h = int(region_h * 0.55)
        glow = pygame.Surface((w, sweep_h), pygame.SRCALPHA)
        gc = _mix((255, 248, 222), front, 0.0)
        pygame.draw.ellipse(glow, (*gc, int(24 * (1.0 - night))),
                            (-w // 6, 0, int(w * 1.33), sweep_h))
        surf.blit(glow, (0, h - sweep_h), special_flags=pygame.BLEND_RGB_ADD)

    _apply_grain_scroll(surf, 0, top_y, w, region_h, 4, scroll)


# ── Sand C — Riverbank Sandbar (45px, top@595) ───────────────────────────────
# The riverbank carried forward, premium: coarse warm sand, crisp half-sunk
# flat river stones with lit caps + dark contacts, and 2-3 bold silhouetted
# dry-grass tufts at the back. Crisp relief, no hazy wash.

def fg_premium_riverbank(surf, w, gy, h, scroll, pal):
    sand = _mix(_sand(pal), (208, 186, 144), 0.28)
    front = _shade(_sat(sand, 1.04), 6)
    back = _shade(_sat(sand, 0.92), -16)
    night = _nightf(pal)
    front = _mix(front, (68, 80, 110), 0.28 * night)
    back = _mix(back, (56, 68, 100), 0.32 * night)
    top_y, region_h, night = _premium_base(
        surf, w, gy, h, pal, front, back, ease=1.0,
        sheen=_mix((255, 246, 212), front, 0.0), sheen_a=20)

    # Coarse warm tooth — a sparse crisp speck scatter (lit + shadow specks),
    # giving the riverbar grain without a hazy dither blanket.
    for sx, k, srng in _scatter(scroll, w, 0.26, 6, 0x2F9):
        py = top_y + int(srng.uniform(0.2, 1.0) * region_h)
        if srng.random() < 0.5:
            continue
        d = srng.randint(-20, 22)
        surf.set_at((sx, py), _shade(sand, d))

    # Crisp half-sunk flat river stones: dark contact ellipse + lit cap + a
    # 1px specular top, larger toward the front.
    for sx, k, srng in _scatter(scroll, w, 0.22, 26, 0x4C7):
        py = top_y + int(srng.uniform(0.42, 0.96) * region_h)
        depth_t = (py - top_y) / max(1, region_h)
        if srng.random() > 0.4 + 0.4 * depth_t:
            continue
        pw = 2 + int(depth_t * 4)
        ph = max(1, pw // 2)
        pc = _mix(sand, (152, 144, 130), 0.55)
        pc = _mix(pc, _shade(pal.get('stone_dark', (95, 80, 70)), 22),
                  srng.uniform(0.0, 0.35))
        pc = _mix(pc, (60, 70, 100), 0.3 * night)
        pygame.draw.ellipse(surf, _shade(pc, -22),
                            (sx - pw, py - ph + 1, pw * 2, ph + 1))
        pygame.draw.ellipse(surf, pc, (sx - pw, py - ph, pw * 2, ph + 1))
        if night < 0.7:
            pygame.draw.line(surf, _shade(pc, 26), (sx - pw + 1, py - ph),
                             (sx + pw - 2, py - ph), 1)
            _spec_dab(surf, sx - 1, py - ph, 2, 1, (255, 250, 232),
                      24 - int(12 * night))

    # 2-3 bold silhouetted dry-grass tufts at the BACK edge — solid straw fans
    # plus a few lit outer blades, sparse + readable.
    straw = _mix((200, 186, 132), sand, 0.3)
    straw = _mix(straw, (96, 104, 120), 0.34 * night)
    straw_dk = _shade(straw, -32)
    for sx, k, srng in _scatter(scroll, w, 0.2, 120, 0x8E2):
        if srng.random() < 0.5:
            continue
        ty = top_y + int(srng.uniform(0.12, 0.30) * region_h)
        th_ = srng.randint(10, 15)
        spread = srng.randint(5, 8)
        lean = srng.randint(-3, 3)
        apex = (sx + lean, ty - th_)
        pygame.draw.polygon(surf, straw_dk, [
            (sx - spread, ty), (sx + spread, ty),
            (apex[0] + 2, apex[1] + 2), (apex[0] - 2, apex[1] + 2)])
        for bo in (-spread, -spread // 2, spread // 2, spread):
            bx = sx + bo
            bh = th_ - abs(bo)
            pygame.draw.line(surf, straw, (bx, ty),
                             (bx + lean // 2, ty - max(4, bh)), 1)

    _apply_grain_scroll(surf, 0, top_y, w, region_h, 4, scroll)


# Round-7 sheet: the ORIGINAL game floor (height + "mountains start from the
# floor top" reference) + a premium 3-stone / 3-sand set, all on the 45px hero
# strip with top edge FLUSH at GROUND_Y. The original row is rendered by the
# render module's `_render_original` (fn=None).
CONCEPTS_R7 = [
    ("ORIGINAL GAME FLOOR", None),
    ("Polished Temple Pavement", fg_polished_pavement),
    ("Inlaid Geometric Mosaic", fg_inlaid_mosaic),
    ("Glazed River-Cobble", fg_glazed_cobble),
    ("Golden Desert Dune", fg_golden_dune),
    ("Satin Rippled Sand", fg_satin_sand),
    ("Riverbank Sandbar", fg_premium_riverbank),
]


# ══════════════════════════════════════════════════════════════════════════
# Round 8 — net every floor top to EXACTLY y=595 + RESCUE THE SAND.
#
# Round 7 was right on HEIGHT and the stone family read premium, but it carried
# three disqualifying faults the round-8 base + sand model fix:
#
#   1. The opaque top row at y=595 was a near-BLACK contact line (the BLEND_SUB
#      lip in _premium_base sampled ~20 luma) — a hard dark seam against the
#      sky, worst at night. _premium_base_v8 replaces it with a soft WARM-LIT
#      1px lip so the topmost opaque row reads as a lit bevel meeting the
#      mountains, never a dark seam — and the lit surface starts AT 595 with no
#      sky sliver above it.
#   2. The sand's additive-to-white sheen + white ripple dashes pooled the
#      lower band to ~253 luma (pure white). The v8 SAND model never touches
#      255: the lower-band lift is a WARM TONAL value raise within the sand hue
#      (capped well under 230 luma), and ripples are two warm tones a few
#      values apart (light-tan crest / mid-tan trough) — no BLEND_ADD, no white.
#   3. Because that sheen was additive, the sand GLOWED at night instead of
#      retinting. The v8 sand has NO additive light, so it drops in value with
#      the biome and sits BELOW the night-sky luma — darker than the sky, never
#      glowing. That night retint is the gate the whole round is built around.
# ══════════════════════════════════════════════════════════════════════════


def _premium_base_v8(surf, w, gy, h, pal, front, back, *, ease=1.0,
                     lip_warm=(255, 244, 222), lip_a=70):
    """The round-8 grounded plane on the 45px hero strip. Identical opaque
    value-fall slab from the FLAT top edge at GROUND_Y (y=595) down to h as
    round 7 — but the back-edge treatment is inverted: instead of a BLEND_SUB
    near-black contact line that read as a dark seam against the sky, the top
    row gets a soft WARM-LIT 1px lip (a low-alpha warm tone, value-only) so the
    floor's topmost opaque pixels read as a lit bevel meeting the mountains.
    A single faint shadow hairline sits one row BELOW the lit lip to still set
    the plane apart as its own object, but it never touches the y=595 edge.
    No additive sheen here — concepts add their own controlled, capped light so
    nothing can pool toward white. Returns (top_y, region_h, night)."""
    night = _nightf(pal)
    top_y = gy                       # FLUSH with the mountain bases at y=595.
    region_h = h - top_y             # exactly 45px on the live canvas.
    _flat_slab(surf, w, h, top_y, back, front, ease=ease)

    # Soft warm-lit top lip RIGHT AT y=595: the opaque top row reads lit, not as
    # a dark seam. Warmth fades toward night so the lip cools with the stage but
    # never goes dark (the seam read). Value-only alpha blend, never additive.
    lip = pygame.Surface((w, 1), pygame.SRCALPHA)
    lit = _mix(front, lip_warm, 0.45)
    # The lip cools AND DARKENS toward night so the topmost opaque row sits
    # below the night-sky luma instead of floating bright (a lit lip that stayed
    # warm at night would glow at the seam). At full night it sits at the night
    # surface value, not above it.
    lit = _mix(lit, _shade(front, -10), night)
    lip.fill((*lit, int(lip_a * (1.0 - 0.55 * night)) + int(18 * (1.0 - night))))
    surf.blit(lip, (0, top_y))
    # A faint object-defining shadow hairline ONE row below the lit lip — keeps
    # the floor reading as its own plane sitting in front of the mountains,
    # without ever darkening the y=595 edge itself.
    sh = pygame.Surface((w, 1), pygame.SRCALPHA)
    sh.fill((*_shade(_sat(back, 0.92), -16 - int(6 * night)), 90))
    surf.blit(sh, (0, top_y + 1))
    return top_y, region_h, night


def _sand_v8(pal):
    """Warm sand for the round-8 leads — the round-7 _sand hue, but the tone is
    chosen so the OPAQUE slab itself carries the material (no additive sheen is
    layered on top), and the value-fall is built to stay tan, never near-white,
    in the lower band."""
    base = _mix(_sandstone(pal), pal.get('ground_mid', (176, 142, 92)), 0.35)
    return _mix(_sat(base, 0.94), (216, 188, 140), 0.55)


def _sand_tones_v8(pal, base, *, night):
    """Build the capped warm tonal palette every round-8 sand concept shares:
    a front (near lip) value-LIFTED within the warm hue but held under ~225
    luma, a cooler set-back, and a gentle lower-band lift tone — all retinted
    toward the night sky so the surface drops below the night-sky luma. Returns
    (front, back, lift) where `lift` is a warm tone a few values above `front`
    for the lower-band tonal raise (NEVER white, NEVER additive)."""
    # Front lip: warm + lifted, but capped so it can never approach white.
    front = _shade(_sat(base, 1.04), 6)
    if _luma(front) * 255.0 > 224:
        front = _mix(front, (224, 196, 150), 0.6)
    back = _shade(_sat(base, 0.9), -18)
    # Night retint: pull HARD toward a dark cool night ground so the whole plane
    # sits clearly BELOW the ~89-luma night sky and reads as ground, never glow
    # (the round's pass/fail gate). The night target is deliberately darker than
    # the night sky tone; the mix is near-total at full night so even the lit
    # front lip lands under the sky.
    night_dk = (30, 38, 60)
    front = _mix(front, night_dk, 0.74 * night)
    back = _mix(back, _shade(night_dk, -8), 0.80 * night)
    # Lower-band lift: a warm tan a touch above the front in DAY, capped under
    # ~225 luma — the tonal replacement for the blown additive sheen. It is
    # pulled to the SAME dark night ground at night so it can never lift the
    # near band above the night sky.
    lift = _mix(front, (228, 200, 156), 0.5)
    if _luma(lift) * 255.0 > 224:
        lift = _mix(lift, (220, 192, 148), 0.7)
    lift = _mix(lift, night_dk, 0.80 * night)
    return front, back, lift


def _sand_lowband_lift(surf, w, top_y, region_h, h, lift, *, night):
    """Raise the value of the near (lower) ~40% of a sand strip toward `lift`
    with a vertical falloff — a WARM TONAL lift, blended value-only (never
    additive), so the front sand catches the light without pooling toward
    white. Held below night so the night plane stays a dark ground."""
    band_top = top_y + int(region_h * 0.58)
    span = max(1, h - 1 - band_top)
    peak = 0.50 * (1.0 - 0.85 * night)       # max blend strength, day vs night
    for y in range(band_top, h):
        t = (y - band_top) / span
        a = int(255 * peak * (t ** 1.3))
        if a <= 0:
            continue
        ln = pygame.Surface((w, 1), pygame.SRCALPHA)
        ln.fill((*lift, a))
        surf.blit(ln, (0, y))


# ── Sand LEAD — Riverbank Sandbar v8 (45px, top@595) ─────────────────────────
# The riverbank's charming identity kept intact — half-sunk lit river stones +
# bold dry-grass tufts — but every highlight is now a capped WARM TONE, the
# ripples/grain are tonal, the top edge is a warm-lit lip (no dark seam), and
# the whole plane retints below the night sky instead of glowing.

def fg_riverbank_v8(surf, w, gy, h, scroll, pal):
    base = _mix(_sand_v8(pal), (206, 184, 142), 0.30)
    night = _nightf(pal)
    front, back, lift = _sand_tones_v8(pal, base, night=night)
    top_y, region_h, night = _premium_base_v8(
        surf, w, gy, h, pal, front, back, ease=1.0,
        lip_warm=(255, 240, 214), lip_a=64)

    # Warm tonal lower-band lift — the front sand catches the light as a capped
    # tan raise, not an additive white pool.
    _sand_lowband_lift(surf, w, top_y, region_h, h, lift, night=night)

    # Tonal ripple relief: each ripple is a mid-tan TROUGH with a light-tan
    # CREST one row above it — two warm tones a few values apart, blended
    # value-only. No white, no additive, no continuous bright stripe (each
    # ripple is broken into short segments with a tiny deterministic wobble).
    rip_trough = _mix(_shade(_sat(base, 0.9), -16), back, 0.25)
    rip_trough = _mix(rip_trough, (40, 50, 78), 0.44 * night)
    rip_crest = _mix(_shade(base, 12), lift, 0.5)
    rip_crest = _mix(rip_crest, (52, 62, 90), 0.42 * night)
    n_rip = 7
    for ri in range(n_rip):
        f = (ri + 0.5) / n_rip
        y = _perspective_y(top_y, h, 1.0 - f)
        depth_t = f
        ph = int(scroll * (0.16 + 0.08 * depth_t))
        seg = 11 + int(depth_t * 8)
        a_t = int(56 + 46 * depth_t)
        a_c = int(46 + 50 * depth_t)
        x = -(ph % (seg * 2))
        while x < w:
            jit = ((x // seg) % 3) - 1
            yy = y + jit
            tr = pygame.Surface((seg - 2, 1), pygame.SRCALPHA)
            tr.fill((*rip_trough, a_t))
            surf.blit(tr, (x, yy))
            cr = pygame.Surface((seg - 2, 1), pygame.SRCALPHA)
            cr.fill((*rip_crest, a_c))
            surf.blit(cr, (x, yy - 1))
            x += seg

    # Coarse warm tooth — sparse tonal specks (lit + shadow), value-only. The
    # speck tone is the NIGHT-retinted front, not the raw day base, so the
    # tooth drops below the night sky with the rest of the plane (a raw-base
    # speck would stay day-bright and spike above the night sky).
    speck = _mix(base, (30, 38, 60), 0.74 * night)
    for sx, k, srng in _scatter(scroll, w, 0.26, 6, 0x2F9):
        py = top_y + int(srng.uniform(0.2, 1.0) * region_h)
        if srng.random() < 0.5:
            continue
        d = srng.randint(-18, 18)
        surf.set_at((sx, py), _shade(speck, d))

    # Half-sunk flat river stones: dark contact ellipse + lit cap. The cap
    # highlight is the stone's OWN warm tone lightened (capped), NOT a white
    # specular dab — so the stones never glint white and they retint at night.
    for sx, k, srng in _scatter(scroll, w, 0.22, 26, 0x4C7):
        py = top_y + int(srng.uniform(0.42, 0.96) * region_h)
        depth_t = (py - top_y) / max(1, region_h)
        if srng.random() > 0.4 + 0.4 * depth_t:
            continue
        pw = 2 + int(depth_t * 4)
        ph = max(1, pw // 2)
        pc = _mix(base, (158, 148, 130), 0.5)
        pc = _mix(pc, _shade(pal.get('stone_dark', (95, 80, 70)), 20),
                  srng.uniform(0.0, 0.35))
        # Retint the stones to the same dark night ground as the slab so their
        # lit caps can never spike above the night sky (the gate). Near-total
        # at full night, matching _sand_tones_v8's night pull.
        pc = _mix(pc, (26, 32, 52), 0.80 * night)
        pygame.draw.ellipse(surf, _shade(pc, -22),
                            (sx - pw, py - ph + 1, pw * 2, ph + 1))
        pygame.draw.ellipse(surf, pc, (sx - pw, py - ph, pw * 2, ph + 1))
        # Lit top edge: a capped warm lighten of the stone tone (value-only),
        # the warm boost AND the value lift faded toward night so the cap stays
        # below the night sky.
        cap_lit = _mix(_shade(pc, int(22 * (1.0 - 0.6 * night))),
                       (236, 214, 176), 0.35 * (1.0 - night))
        pygame.draw.line(surf, cap_lit, (sx - pw + 1, py - ph),
                         (sx + pw - 2, py - ph), 1)

    # 2-3 bold silhouetted dry-grass tufts at the BACK — the charming silhouette
    # echo of the original, kept warm/tonal. Retinted to the dark night ground
    # so the straw reads as a dark silhouette against the night sky (a warm
    # straw would glow above the ~90-luma night sky at the back lip).
    straw = _mix((196, 182, 130), base, 0.32)
    straw = _mix(straw, (34, 42, 64), 0.70 * night)
    straw_dk = _shade(straw, -32)
    for sx, k, srng in _scatter(scroll, w, 0.2, 120, 0x8E2):
        if srng.random() < 0.5:
            continue
        ty = top_y + int(srng.uniform(0.14, 0.32) * region_h)
        th_ = srng.randint(10, 15)
        spread = srng.randint(5, 8)
        lean = srng.randint(-3, 3)
        apex = (sx + lean, ty - th_)
        pygame.draw.polygon(surf, straw_dk, [
            (sx - spread, ty), (sx + spread, ty),
            (apex[0] + 2, apex[1] + 2), (apex[0] - 2, apex[1] + 2)])
        for bo in (-spread, -spread // 2, spread // 2, spread):
            bx = sx + bo
            bh = th_ - abs(bo)
            pygame.draw.line(surf, straw, (bx, ty),
                             (bx + lean // 2, ty - max(4, bh)), 1)

    # Fine scroll-locked tooth, low amp so it stays a refined warm grain.
    _apply_grain_scroll(surf, 0, top_y, w, region_h, 3, scroll)


# ── Sand secondary — Golden Desert Dune v8 (45px, top@595) ───────────────────
# Warm golden sand with gentle TONAL wind-relief: paired light-tan / mid-tan
# ripple tones, a capped warm lower-band lift, fine tooth. No additive sheen,
# no white pool, no golden crest — it retints below the night sky.

def fg_golden_dune_v8(surf, w, gy, h, scroll, pal):
    base = _sand_v8(pal)
    night = _nightf(pal)
    front, back, lift = _sand_tones_v8(pal, base, night=night)
    top_y, region_h, night = _premium_base_v8(
        surf, w, gy, h, pal, front, back, ease=1.0,
        lip_warm=(255, 242, 210), lip_a=66)

    _sand_lowband_lift(surf, w, top_y, region_h, h, lift, night=night)

    # Tonal wind ripples: light-tan crest over mid-tan trough, two warm tones a
    # few values apart, value-only blend. Packed tighter toward the back.
    rip_trough = _mix(_shade(_sat(base, 0.88), -18), back, 0.2)
    rip_trough = _mix(rip_trough, (40, 50, 78), 0.46 * night)
    rip_crest = _mix(_shade(base, 14), lift, 0.45)
    rip_crest = _mix(rip_crest, (52, 62, 90), 0.42 * night)
    n_rip = 9
    for ri in range(n_rip):
        f = (ri + 0.5) / n_rip
        y = _perspective_y(top_y, h, 1.0 - f)
        depth_t = f
        ph = int(scroll * (0.16 + 0.08 * depth_t))
        seg = 12 + int(depth_t * 8)
        a_t = int(50 + 44 * depth_t)
        a_c = int(42 + 48 * depth_t)
        x = -(ph % (seg * 2))
        while x < w:
            jit = ((x // seg) % 3) - 1
            yy = y + jit
            tr = pygame.Surface((seg - 2, 1), pygame.SRCALPHA)
            tr.fill((*rip_trough, a_t))
            surf.blit(tr, (x, yy))
            cr = pygame.Surface((seg - 2, 1), pygame.SRCALPHA)
            cr.fill((*rip_crest, a_c))
            surf.blit(cr, (x, yy - 1))
            x += seg

    # A few tiny pebbles with a capped warm-lit top (no white set_at).
    for sx, k, srng in _scatter(scroll, w, 0.22, 44, 0x5B2):
        py = top_y + int(srng.uniform(0.5, 0.96) * region_h)
        depth_t = (py - top_y) / max(1, region_h)
        if srng.random() > 0.3 + 0.35 * depth_t:
            continue
        pr = 1 + int(depth_t * 1.6)
        pc = _mix(base, (176, 156, 126), 0.5)
        pc = _mix(pc, (30, 38, 60), 0.74 * night)
        pygame.draw.ellipse(surf, _shade(pc, -22),
                            (sx - pr, py - pr // 2, pr * 2, pr + 1))
        surf.set_at((sx, py - pr // 2),
                    _mix(_shade(pc, 18), (230, 208, 168), 0.3 * (1.0 - night)))

    _apply_grain_scroll(surf, 0, top_y, w, region_h, 3, scroll)


# ── Stone LEAD — Inlaid Geometric Mosaic v8 (45px, top@595) ──────────────────
# The round-7 mosaic kept (ship-quality crisp fret border + beveled diamond
# tessellation) with two light touches: the warm-lit top lip (no dark seam at
# y=595) and the two-tone diamond contrast nudged DOWN ~10% in the bird-lane
# mid-band so the tessellation stays quiet behind gameplay.

def fg_inlaid_mosaic_v8(surf, w, gy, h, scroll, pal):
    stone = _sandstone(pal)
    light = _shade(_sat(stone, 1.05), 12)
    dark = _shade(_sat(_mix(stone, (120, 92, 70), 0.5), 0.95), -10)
    night = _nightf(pal)
    front = _mix(light, (66, 78, 112), 0.26 * night)
    back = _mix(_shade(light, -22), (54, 66, 100), 0.32 * night)
    top_y, region_h, night = _premium_base_v8(
        surf, w, gy, h, pal, front, back, ease=0.95,
        lip_warm=(255, 246, 224), lip_a=66)

    d_light = _mix(light, (66, 78, 112), 0.26 * night)
    d_dark = _mix(dark, (50, 62, 96), 0.30 * night)
    grout = _shade(_mix(stone, (54, 40, 30), 0.5), -16 - int(8 * night))
    edge_lt = _mix(d_light, (255, 250, 232), 0.35)
    # The two mosaic tones pulled ~10% toward each other (their mean) ONLY in
    # the mid band, so the tessellation reads quieter behind the bird lane while
    # the front/back keep the crisp two-tone inlay contrast.
    mid_mean = _mix(d_light, d_dark, 0.5)
    q_light = _mix(d_light, mid_mean, 0.10)
    q_dark = _mix(d_dark, mid_mean, 0.10)

    # Fine inlaid FRET border just below the lit lip — the temple-inlay hero.
    fret_y = top_y + 6
    for sx, k, srng in _scatter(scroll, w, 0.16, 14, 0x1F4):
        pygame.draw.line(surf, grout, (sx, fret_y), (sx, fret_y + 4), 1)
        pygame.draw.line(surf, grout, (sx, fret_y), (sx + 5, fret_y), 1)
        pygame.draw.line(surf, edge_lt, (sx + 1, fret_y + 1),
                         (sx + 1, fret_y + 4), 1)

    # Diamond/lozenge tessellation. The mid band (bird lane) uses the quieted
    # tones; the front/back keep the full two-tone contrast.
    band_top = top_y + 13
    cell = 16
    row = 0
    y = band_top
    mid_lo = top_y + region_h * 0.34
    mid_hi = top_y + region_h * 0.74
    while y < h:
        ch = min(cell, h - y)
        speed = 0.18 + 0.06 * ((y - top_y) / max(1, region_h))
        in_mid = mid_lo <= (y + ch // 2) <= mid_hi
        tl = q_light if in_mid else d_light
        td = q_dark if in_mid else d_dark
        for sx, k, srng in _scatter(scroll, w, speed, cell, 0x2A8 + row):
            cx = sx + (cell // 2 if row % 2 else 0)
            cy = y + ch // 2
            r = cell // 2 - 1
            tile = tl if (k + row) % 2 == 0 else td
            pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
            pygame.draw.polygon(surf, tile, pts)
            pygame.draw.line(surf, edge_lt, (cx - r, cy), (cx, cy - r), 1)
            pygame.draw.line(surf, edge_lt, (cx, cy - r), (cx + r, cy), 1)
            pygame.draw.line(surf, grout, (cx + r, cy), (cx, cy + r), 1)
            pygame.draw.line(surf, grout, (cx, cy + r), (cx - r, cy), 1)
            # Capped warm glint on the lit shoulder of the FRONT-most light
            # tiles only (kept out of the mid band so the lane stays quiet, and
            # faded out at night so it never glows after dark).
            if tile is d_light and cy > top_y + region_h * 0.78 and night < 0.5:
                _spec_dab(surf, cx - 2, cy - r + 1, 3, 3, (248, 238, 218),
                          int(15 * (1.0 - 2.0 * night)))
        y += ch
        row += 1

    _apply_grain(surf, 0, top_y, w, region_h, 3)


# ── Stone fallback — Polished Temple Pavement v8 (45px, top@595) ─────────────
# Round-7 polished pavement, ship-clean, with only the netting fix: the
# warm-lit top lip at y=595 in place of the dark contact seam. Everything else
# (beveled joints, per-slab glints, inlay panels) is kept verbatim.

def fg_polished_pavement_v8(surf, w, gy, h, scroll, pal):
    stone = _sandstone(pal)
    front = _shade(_sat(stone, 1.08), 6)
    back = _shade(_sat(stone, 0.92), -20)
    night = _nightf(pal)
    front = _mix(front, (66, 78, 112), 0.28 * night)
    back = _mix(back, (54, 66, 100), 0.32 * night)
    top_y, region_h, night = _premium_base_v8(
        surf, w, gy, h, pal, front, back, ease=0.95,
        lip_warm=(255, 248, 228), lip_a=104)

    joint_dk = _shade(_mix(stone, (54, 40, 30), 0.55), -16 - int(8 * night))
    # Lit lip tone for joints — warm and crisp, but pulled back from pure white
    # so a front-course inlay-panel outline reads as a bright bevel edge, not a
    # blown-out continuous white bar at the front lip.
    joint_lt = _mix(front, (244, 230, 206), 0.26)

    n_course = 3
    for c in range(n_course):
        f0 = c / n_course
        f1 = (c + 1) / n_course
        y_back = _perspective_y(top_y, h, 1.0 - f0)
        y_front = _perspective_y(top_y, h, 1.0 - f1)
        if y_front <= y_back:
            continue
        depth_t = f0
        step = int(54 + 46 * depth_t)
        bond = (c % 2) * (step // 2)
        pygame.draw.line(surf, joint_dk, (0, y_back), (w, y_back), 1)
        if y_back + 1 < y_front:
            pygame.draw.line(surf, joint_lt, (0, y_back + 1), (w, y_back + 1), 1)
        speed = 0.18 + 0.10 * depth_t
        for sx, k, srng in _scatter(scroll, w, speed, step, 0xE71 + c):
            jx = sx + bond
            pygame.draw.line(surf, joint_dk, (jx, y_back), (jx, y_front), 1)
            pygame.draw.line(surf, joint_lt, (jx + 1, y_back + 1),
                             (jx + 1, y_front), 1)
            # Per-slab polished glint — a soft warm additive dab, faded HARD
            # toward night and made smaller/dimmer overall so a near slab never
            # holds a blown-white pooled patch (a daytime polish read, not a
            # night glow, and never a clipped white block even in DAY).
            if depth_t > 0.32 and srng.random() < 0.45 and night < 0.5:
                gw = max(4, step - 16)
                gh = max(2, (y_front - y_back) // 3)
                _spec_dab(surf, jx + 6, y_back + 3, gw, gh,
                          (250, 238, 214),
                          int((12 + 9 * depth_t) * (1.0 - 2.0 * night)))
            if depth_t > 0.4 and srng.random() < 0.26:
                iw = max(4, step - 16)
                ih = max(2, (y_front - y_back) - 6)
                inlay = pygame.Surface((iw, ih), pygame.SRCALPHA)
                inlay.fill((10, 8, 6, 30))
                surf.blit(inlay, (jx + 6, y_back + 3),
                          special_flags=pygame.BLEND_RGB_SUB)
                pygame.draw.rect(surf, joint_lt, (jx + 6, y_back + 3, iw, ih), 1)

    _apply_grain(surf, 0, top_y, w, region_h, 3)


# ══════════════════════════════════════════════════════════════════════════
# Round 9 — make the SAND cheerful: a REAL happy BEACH, not a serious riverbank.
#
# Round 8's Riverbank Sandbar is technically clean (capped tonal lower band, no
# white pool, night-retint below the sky) but the MOOD reads "muted natural
# desert/riverbank" — a touch serious. Round 9 keeps every v8 technical win by
# reusing the v8 sand scaffolding VERBATIM (_premium_base_v8 warm-lit lip,
# _sand_tones_v8's hard night pull, _sand_lowband_lift's capped value-only
# raise) and changes only the MATERIAL/MOOD: a brighter, cheerier sand HUE
# (more saturation + lighter, still under the day luma cap) plus playful beach
# accents — scattered shells, starfish, and (for the wet take) a soft broken
# damp scallop with a faint sky-blue reflection. The "cheerful" lives in the
# day/sunset cells; the shared v8 night pull keeps NIGHT a calm moonlit beach
# that still sits below the night sky.
# ══════════════════════════════════════════════════════════════════════════


def _beach_base(pal, *, warmth, light):
    """A brighter, cheerier beach hue derived from the v8 sand tone. `warmth`
    pushes saturation toward a happy golden/coral cast; `light` lifts the value.
    The cap in _sand_tones_v8 still clamps the lower band well under ~224 luma,
    so this can stay cheerful in DAY without ever pooling toward white."""
    base = _sand_v8(pal)
    base = _sat(base, warmth)
    return _shade(base, light)


def _beach_shell(surf, cx, cy, r, col, *, night, ridged=False):
    """A tiny scallop shell: a warm dome with a couple of radiating rib lines and
    a soft lit crown. Drawn from the shell's OWN tone (lightened for the crown,
    darkened for the ribs) — never an additive white dab — and pulled to the v8
    dark night ground so it retints below the night sky instead of glinting."""
    col = _mix(col, (28, 36, 58), 0.78 * night)
    base_d = _shade(col, -26)
    # Fan body: a small filled half-ellipse (dome up), seated with a shadow foot.
    pygame.draw.ellipse(surf, base_d, (cx - r, cy - r + 1, r * 2, r * 2 - 1))
    pygame.draw.ellipse(surf, col, (cx - r, cy - r, r * 2, r * 2 - 1))
    # Radiating ribs from the hinge (bottom centre) — the unmistakable shell read.
    rib = _shade(col, -18)
    if r >= 2:
        for dx in (-r + 1, 0, r - 1):
            pygame.draw.line(surf, rib, (cx, cy + r - 1),
                             (cx + dx, cy - r + 1), 1)
    # Capped warm-lit crown, faded out toward night so it never glows after dark.
    crown = _mix(_shade(col, 16), (244, 226, 196), 0.4 * (1.0 - night))
    surf.set_at((cx, cy - r + 1), crown)
    if ridged and r >= 3:
        surf.set_at((cx - 1, cy - r + 2), _shade(col, 8))
        surf.set_at((cx + 1, cy - r + 2), _shade(col, 8))


def _beach_starfish(surf, cx, cy, r, col, *, night):
    """A small five-arm starfish: a warm star polygon with a slightly lit centre.
    Same tonal discipline as the shells — own tone lightened for the centre, no
    additive white, retinted to the v8 dark night ground."""
    col = _mix(col, (30, 38, 60), 0.78 * night)
    pts = []
    for i in range(5):
        a = -math.pi / 2 + i * (2 * math.pi / 5)
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
        a2 = a + math.pi / 5
        pts.append((cx + math.cos(a2) * r * 0.42, cy + math.sin(a2) * r * 0.42))
    pygame.draw.polygon(surf, _shade(col, -22), pts)
    pygame.draw.polygon(surf, col,
                        [(x, y - 1) for (x, y) in pts])
    # Lit core dot, capped + day-only so the star reads convex without glowing.
    surf.set_at((cx, cy - 1),
                _mix(_shade(col, 14), (240, 222, 192), 0.35 * (1.0 - night)))


def _beach_accents(surf, w, top_y, region_h, h, scroll, base, *, night,
                   density, palette, seed):
    """Scatter small beach treasures (shells + the odd starfish) across the near
    band of a beach strip. `density` scales how many appear; `palette` is the
    list of cheerful accent hues to draw from. Kept in the FRONT band (out of the
    quiet back lip), scroll-locked via _scatter, and capped at the readability
    ceiling so even the playful take never clutters the bird lane."""
    step = max(14, int(46 / max(0.1, density)))
    for sx, k, srng in _scatter(scroll, w, 0.24, step, seed):
        # Keep accents in the lower (near) band so the back lip stays quiet.
        py = top_y + int(srng.uniform(0.52, 0.95) * region_h)
        depth_t = (py - top_y) / max(1, region_h)
        if srng.random() > 0.32 + 0.5 * depth_t:
            continue
        col = _mix(srng.choice(palette), base, 0.32)
        kind = srng.random()
        r = 2 + int(depth_t * 2)
        # Small soft contact shadow under the treasure so it sits IN the sand.
        sh = pygame.Surface((r * 2 + 2, 2), pygame.SRCALPHA)
        sh.fill((0, 0, 0, 40))
        surf.blit(sh, (sx - r - 1, py + r - 1), special_flags=pygame.BLEND_RGB_SUB)
        if kind < 0.16 and r >= 2:
            _beach_starfish(surf, sx, py, r + 1, col, night=night)
        else:
            _beach_shell(surf, sx, py, r, col, night=night,
                         ridged=srng.random() < 0.5)


# Cheerful accent hues, kept under the day luma cap (no near-white) so they pop
# on the sand without pooling bright. Warm corals/peaches + a couple of cool
# shell tones for variety; the painters mix each toward the sand base.
_SHELL_WARM = [(232, 158, 132), (236, 186, 150), (226, 142, 120),
               (240, 200, 158), (210, 150, 138)]
_SHELL_PASTEL = [(238, 188, 196), (224, 196, 214), (200, 198, 222),
                 (240, 206, 170), (210, 214, 206)]


# ── Beach 1 — Sunny Golden Beach (45px, top@595) ─────────────────────────────
# The minimal happy beach: bright warm cheerfully-saturated golden sand, a soft
# CAPPED tonal sun-sparkle in the near band (value-only, never white), and a
# few small scattered shells. Classic, clean, joyful.

def fg_beach_golden(surf, w, gy, h, scroll, pal):
    base = _beach_base(pal, warmth=1.22, light=14)
    night = _nightf(pal)
    front, back, lift = _sand_tones_v8(pal, base, night=night)
    top_y, region_h, night = _premium_base_v8(
        surf, w, gy, h, pal, front, back, ease=1.0,
        lip_warm=(255, 240, 206), lip_a=66)

    _sand_lowband_lift(surf, w, top_y, region_h, h, lift, night=night)

    # Soft tonal sun-sparkle: a sparse field of capped warm-light specks (a few
    # values above the lift, NEVER white, value-only) so the front sand twinkles
    # like sun on dry beach. Retinted to the v8 night ground so it darkens with
    # the stage rather than glowing.
    spark = _mix(lift, (236, 212, 168), 0.5)
    spark = _mix(spark, (34, 42, 64), 0.80 * night)
    for sx, k, srng in _scatter(scroll, w, 0.27, 7, 0x9A1):
        py = top_y + int(srng.uniform(0.55, 0.98) * region_h)
        if srng.random() < 0.62:
            continue
        surf.set_at((sx, py), spark)

    # A few small scattered shells — minimal, the cheerful punctuation.
    _beach_accents(surf, w, top_y, region_h, h, scroll, base, night=night,
                   density=0.55, palette=_SHELL_WARM, seed=0xB31)

    _apply_grain_scroll(surf, 0, top_y, w, region_h, 3, scroll)


# ── Beach 2 — Tropical Coral Beach (45px, top@595) ───────────────────────────
# The most pastel-cheerful take: lighter cream sand with a pink-coral cast, plus
# playful colourful little shells and a starfish accent. Soft and sweet, the
# "ice-cream beach" mood — still under the day luma cap, still retints at night.

def fg_beach_coral(surf, w, gy, h, scroll, pal):
    # Cream + coral cast: lighten + warm, then pull a touch toward a soft pink so
    # the sand reads pastel-tropical, not plain tan. The _sand_tones_v8 cap keeps
    # the lower band under ~224 luma so the cream never pools toward white.
    base = _beach_base(pal, warmth=1.1, light=22)
    base = _mix(base, (240, 210, 196), 0.30)        # gentle coral-cream blush
    night = _nightf(pal)
    front, back, lift = _sand_tones_v8(pal, base, night=night)
    top_y, region_h, night = _premium_base_v8(
        surf, w, gy, h, pal, front, back, ease=1.0,
        lip_warm=(255, 238, 224), lip_a=64)

    _sand_lowband_lift(surf, w, top_y, region_h, h, lift, night=night)

    # Faint pastel mottle: a sparse two-tone speckle (a soft peach + a soft
    # shell-pink) blended value-only so the cream sand has a playful candy grain
    # rather than flat tan. Both tones pulled to the v8 night ground.
    peach = _mix(base, (244, 206, 184), 0.5)
    peach = _mix(peach, (34, 42, 64), 0.80 * night)
    pink = _mix(base, (238, 196, 206), 0.5)
    pink = _mix(pink, (34, 42, 64), 0.80 * night)
    for sx, k, srng in _scatter(scroll, w, 0.25, 6, 0xC42):
        py = top_y + int(srng.uniform(0.5, 0.98) * region_h)
        if srng.random() < 0.58:
            continue
        tone = peach if srng.random() < 0.5 else pink
        ln = pygame.Surface((2, 1), pygame.SRCALPHA)
        ln.fill((*tone, 70))
        surf.blit(ln, (sx, py))

    # Playful colourful shells + a starfish — the pastel-cheerful punctuation,
    # drawn from the soft pastel accent set.
    _beach_accents(surf, w, top_y, region_h, h, scroll, base, night=night,
                   density=0.9, palette=_SHELL_PASTEL, seed=0xD73)

    _apply_grain_scroll(surf, 0, top_y, w, region_h, 3, scroll)


# ── Beach 3 — Wet-Shore Beach / gentle surf (45px, top@595) ──────────────────
# Golden sand meeting a soft, BROKEN, low-contrast damp scalloped tide line —
# NOT a bright continuous seam (that was the round-5 mistake). The damp patch
# carries a faint sky-blue reflection (the happy "water just kissed the shore"
# read) plus a couple of shells in the wet sand. Each scallop is a short broken
# arc of slightly DARKER damp sand, never a lit run.

def fg_beach_wetshore(surf, w, gy, h, scroll, pal):
    base = _beach_base(pal, warmth=1.18, light=12)
    night = _nightf(pal)
    front, back, lift = _sand_tones_v8(pal, base, night=night)
    top_y, region_h, night = _premium_base_v8(
        surf, w, gy, h, pal, front, back, ease=1.0,
        lip_warm=(255, 240, 208), lip_a=66)

    _sand_lowband_lift(surf, w, top_y, region_h, h, lift, night=night)

    # Damp band across the NEAR strip: the wet sand is a touch DARKER and cooler
    # than the dry sand (water darkens sand — the opposite of a bright seam), with
    # a faint sky-blue reflection mixed in. Value-only alpha, gentle vertical
    # falloff so it has no hard top edge. Pulled to the v8 night ground.
    sky_ref = pal.get('sky_top', (120, 180, 220))
    damp = _shade(_sat(base, 0.92), -20)
    damp = _mix(damp, sky_ref, 0.16)                # faint water reflection
    damp = _mix(damp, (28, 36, 58), 0.80 * night)
    damp_top = top_y + int(region_h * 0.66)
    for y in range(damp_top, h):
        t = (y - damp_top) / max(1, h - 1 - damp_top)
        a = int(120 * (t ** 1.2) * (1.0 - 0.4 * night))
        if a <= 0:
            continue
        ln = pygame.Surface((w, 1), pygame.SRCALPHA)
        ln.fill((*damp, a))
        surf.blit(ln, (0, y))

    # The tide line itself: a BROKEN low-contrast damp scallop near the top of
    # the wet band. Each scallop is a SHORT arc of slightly darker damp sand with
    # a paler frothy bead a row above — but both are broken into tiny segments
    # with deterministic gaps + wobble so the run is NEVER continuous and NEVER
    # bright. The froth bead is a capped warm cream (value-only), not white.
    scallop_dk = _mix(damp, _shade(back, -10), 0.4)
    froth = _mix(lift, (240, 230, 214), 0.4)
    froth = _mix(froth, (40, 48, 72), 0.78 * night)
    tide_y = damp_top - 1
    seg = 9
    ph = int(scroll * 0.2)
    x = -(ph % (seg * 2))
    si = (ph // seg)
    while x < w:
        srng = random.Random(((si) * 2654435761 ^ 0xE19) & 0xFFFFFFFF)
        si += 1
        # Skip ~1 in 3 cells so the tide line is visibly broken, never a run.
        if srng.random() < 0.34:
            x += seg
            continue
        wob = srng.randint(-2, 2)
        slen = seg - 3 - srng.randint(0, 2)
        yy = tide_y + wob
        # Short damp-darker scallop arc segment (value-only, low contrast).
        arc = pygame.Surface((slen, 1), pygame.SRCALPHA)
        arc.fill((*scallop_dk, 96))
        surf.blit(arc, (x, yy))
        # Pale frothy bead one row above — capped cream, broken with the scallop.
        bead = pygame.Surface((slen - 2, 1), pygame.SRCALPHA)
        bead.fill((*froth, 70))
        surf.blit(bead, (x + 1, yy - 1))
        x += seg

    # A couple of shells washed up in the wet sand.
    _beach_accents(surf, w, top_y, region_h, h, scroll, base, night=night,
                   density=0.5, palette=_SHELL_WARM, seed=0xF57)

    _apply_grain_scroll(surf, 0, top_y, w, region_h, 3, scroll)


# ── Beach 4 — Shell-Dotted Playful Beach (45px, top@595) ─────────────────────
# The "fun" extreme: cheerful warm sand with the most playful scatter of
# colourful shells + starfish. Accent density is the highest of the set but still
# held at the readability ceiling (kept in the near band, capped count) so the
# bird lane stays clear. The sand itself is a friendly mid-golden so the colourful
# treasures pop.

def fg_beach_playful(surf, w, gy, h, scroll, pal):
    base = _beach_base(pal, warmth=1.16, light=16)
    night = _nightf(pal)
    front, back, lift = _sand_tones_v8(pal, base, night=night)
    top_y, region_h, night = _premium_base_v8(
        surf, w, gy, h, pal, front, back, ease=1.0,
        lip_warm=(255, 240, 210), lip_a=66)

    _sand_lowband_lift(surf, w, top_y, region_h, h, lift, night=night)

    # Light tonal twinkle so the sand isn't flat under the busy accents.
    spark = _mix(lift, (234, 210, 166), 0.5)
    spark = _mix(spark, (34, 42, 64), 0.80 * night)
    for sx, k, srng in _scatter(scroll, w, 0.27, 9, 0x7C5):
        py = top_y + int(srng.uniform(0.55, 0.98) * region_h)
        if srng.random() < 0.66:
            continue
        surf.set_at((sx, py), spark)

    # The playful punctuation: dense, colourful shells + starfish drawn from BOTH
    # accent sets so the scatter is varied and fun. Density is the set max but
    # _beach_accents still gates each on the near band + depth so the lane is
    # clear. Two passes (warm + pastel) at offset seeds give a richer mix.
    _beach_accents(surf, w, top_y, region_h, h, scroll, base, night=night,
                   density=1.0, palette=_SHELL_WARM, seed=0x311)
    _beach_accents(surf, w, top_y, region_h, h, scroll, base, night=night,
                   density=0.8, palette=_SHELL_PASTEL, seed=0x9F4)

    _apply_grain_scroll(surf, 0, top_y, w, region_h, 3, scroll)


# ══════════════════════════════════════════════════════════════════════════
# Round 10 — TUNE the chosen Shell-Dotted lead (no redesign, no palette change).
#
# The Shell-Dotted Playful Beach (fg_beach_playful) is the sand winner: warm
# gold + a multi-hue shell/starfish scatter that instantly reads "fun sunny
# beach". This round only refines it:
#   1. trim the accent count ~20-25% and bias it to the LOWER 40% of the band so
#      the strip just under the floor-top (the bird lane) stays pristine,
#   2. cap accents per SCREEN-WIDTH (not per tile) so a scroll never doubles
#      density at a tile seam,
#   3. (Version A only) borrow ~15% of the Wet-Shore value step into the BASE so
#      the very bottom edge goes a faint hint cooler/damper — grounding the
#      shells without the full cool tide band that dampened Wet-Shore's cheer,
#   4. keep the night accent floor: muted DARK dots, no rim glow (already clean),
#   5. keep the base gold EXACTLY as round-9 (the same _beach_base call).
# Reuses the v8 scaffolding verbatim so every tech gate holds.
# ══════════════════════════════════════════════════════════════════════════


def _beach_accents_tuned(surf, w, top_y, region_h, h, scroll, base, *, night,
                         density, palette, seed, drawn, cap):
    """The round-9 _beach_accents with the round-10 tuning: ~20-25% fewer marks,
    biased to the LOWER 40% of the band (so the bird lane just under the floor-
    top stays clear), and a SCREEN-WIDTH count cap shared across passes via the
    mutable `drawn` list so a tile seam can never momentarily double density.
    `drawn[0]` is the running count; the function stops once it hits `cap`.
    Tone discipline (own-tone shells, no additive white, v8 dark-night retint)
    is unchanged from round 9. Returns nothing; mutates `drawn[0]`."""
    # A slightly wider world step thins the scatter ~22% vs round 9, and the
    # firing gate is dropped a notch so fewer cells fire — the count trim.
    step = max(16, int(56 / max(0.1, density)))
    for sx, k, srng in _scatter(scroll, w, 0.24, step, seed):
        if drawn[0] >= cap:
            break
        # Bias to the LOWER 40% of the strip: depth 0.60..0.96 (was 0.52..0.95),
        # so nothing lands in the upper bird-lane band under the floor-top.
        py = top_y + int(srng.uniform(0.60, 0.96) * region_h)
        depth_t = (py - top_y) / max(1, region_h)
        # Lower firing probability (was 0.32 + 0.5*depth) trims the count further
        # while still favouring the very front of the band.
        if srng.random() > 0.22 + 0.46 * depth_t:
            continue
        col = _mix(srng.choice(palette), base, 0.32)
        kind = srng.random()
        r = 2 + int(depth_t * 2)
        # Small soft contact shadow under the treasure so it sits IN the sand.
        sh = pygame.Surface((r * 2 + 2, 2), pygame.SRCALPHA)
        sh.fill((0, 0, 0, 40))
        surf.blit(sh, (sx - r - 1, py + r - 1), special_flags=pygame.BLEND_RGB_SUB)
        if kind < 0.16 and r >= 2:
            _beach_starfish(surf, sx, py, r + 1, col, night=night)
        else:
            _beach_shell(surf, sx, py, r, col, night=night,
                         ridged=srng.random() < 0.5)
        drawn[0] += 1


def _damp_bottom_hint(surf, w, top_y, region_h, h, base, *, night):
    """Borrow ~15% of the Wet-Shore damp value step into the BASE bottom edge: a
    FAINT cooler/damper hint at the very screen floor (y near 640) that grounds
    the shells and adds beach credibility — WITHOUT the full cool tide band that
    dampened Wet-Shore's cheer. The hint is a soft low-contrast value step, not a
    bright (or dark) drawn seam: it darkens only ~15% of Wet-Shore's -20 step,
    mixes a whisper of sky reflection, blends value-only with a steep falloff so
    it touches only the bottom ~12% of the band, and fades hard toward night so
    it never competes with the v8 night ground."""
    # 15% of Wet-Shore's step: ~-3 value, plus a faint sky reflection (also ~15%
    # of Wet-Shore's 0.16 mix). Pulled to the v8 night ground like the wet take.
    damp = _shade(_sat(base, 0.985), -3)
    sky_ref = (150, 178, 198)
    damp = _mix(damp, sky_ref, 0.024)
    damp = _mix(damp, (30, 38, 60), 0.80 * night)
    band_top = top_y + int(region_h * 0.88)   # bottom ~12% of the strip only
    span = max(1, h - 1 - band_top)
    # Peak alpha is low so the step stays soft; ^2.4 falloff keeps the top of the
    # hint imperceptible (no edge) and only the floor row carries the full hint.
    peak = 64 * (1.0 - 0.7 * night)
    for y in range(band_top, h):
        t = (y - band_top) / span
        a = int(peak * (t ** 2.4))
        if a <= 0:
            continue
        ln = pygame.Surface((w, 1), pygame.SRCALPHA)
        ln.fill((*damp, a))
        surf.blit(ln, (0, y))


def _beach_playful_tuned(surf, w, gy, h, scroll, pal, *, damp_bottom):
    """The round-9 Shell-Dotted lead with the round-10 tuning applied. Base gold
    is the EXACT round-9 _beach_base call (unchanged); the accent scatter is the
    trimmed, lower-biased, width-capped version; `damp_bottom` toggles the faint
    damp-bottom hint (Version A on, Version B off)."""
    base = _beach_base(pal, warmth=1.16, light=16)   # round-9 gold, UNCHANGED
    night = _nightf(pal)
    front, back, lift = _sand_tones_v8(pal, base, night=night)
    top_y, region_h, night = _premium_base_v8(
        surf, w, gy, h, pal, front, back, ease=1.0,
        lip_warm=(255, 240, 210), lip_a=66)

    _sand_lowband_lift(surf, w, top_y, region_h, h, lift, night=night)

    # Version A only: the faint damp-bottom hint, laid UNDER the accents so the
    # shells/starfish sit on top of the damp floor (grounded, not floating).
    if damp_bottom:
        _damp_bottom_hint(surf, w, top_y, region_h, h, base, night=night)

    # Light tonal twinkle so the sand isn't flat under the accents (unchanged).
    spark = _mix(lift, (234, 210, 166), 0.5)
    spark = _mix(spark, (34, 42, 64), 0.80 * night)
    for sx, k, srng in _scatter(scroll, w, 0.27, 9, 0x7C5):
        py = top_y + int(srng.uniform(0.55, 0.98) * region_h)
        if srng.random() < 0.66:
            continue
        surf.set_at((sx, py), spark)

    # The playful punctuation: two passes (warm + pastel) for hue variety, now
    # trimmed + lower-biased + SHARING a single screen-width count cap so the
    # second pass can't push past the ceiling at a seam. ~9 across the width
    # holds the density a clear notch under round 9's per-tile count.
    drawn = [0]
    cap = 9
    _beach_accents_tuned(surf, w, top_y, region_h, h, scroll, base, night=night,
                         density=1.0, palette=_SHELL_WARM, seed=0x311,
                         drawn=drawn, cap=cap)
    _beach_accents_tuned(surf, w, top_y, region_h, h, scroll, base, night=night,
                         density=0.8, palette=_SHELL_PASTEL, seed=0x9F4,
                         drawn=drawn, cap=cap)

    _apply_grain_scroll(surf, 0, top_y, w, region_h, 3, scroll)


def fg_beach_playful_dampbottom(surf, w, gy, h, scroll, pal):
    """Version A — tuned Shell-Dotted on a base WITH the faint damp-bottom hint."""
    _beach_playful_tuned(surf, w, gy, h, scroll, pal, damp_bottom=True)


def fg_beach_playful_tuned(surf, w, gy, h, scroll, pal):
    """Version B — tuned Shell-Dotted on the plain warm-gold base (no hint)."""
    _beach_playful_tuned(surf, w, gy, h, scroll, pal, damp_bottom=False)


# Round-10 sheet: SAND-ONLY, final tuning of the chosen Shell-Dotted lead. A
# tight A/B (the art-director says this single A/B is the whole round):
#   Row 0 original ref, Row 1 the UNTUNED round-9 Shell-Dotted (before/contrast),
#   Row 2 Version A (tuned scatter + damp-bottom hint), Row 3 Version B (tuned
#   scatter on the plain gold base).
CONCEPTS_R10 = [
    ("ORIGINAL GAME FLOOR", None),
    ("Shell-Dotted r9 (untuned)", fg_beach_playful),
    ("A: tuned + damp-bottom", fg_beach_playful_dampbottom),
    ("B: tuned (plain gold)", fg_beach_playful_tuned),
]


# Round-9 sheet: SAND-ONLY cheerful-beach spread. The stone leads are untouched.
# Row 0 original ref + Row 1 the round-8 Riverbank (the BEFORE/contrast) + the
# four cheerful beach takes (golden / coral-pastel / wet-shore / shell-dotted).
CONCEPTS_R9 = [
    ("ORIGINAL GAME FLOOR", None),
    ("Riverbank Sandbar v8", fg_riverbank_v8),
    ("Sunny Golden Beach", fg_beach_golden),
    ("Tropical Coral Beach", fg_beach_coral),
    ("Wet-Shore Beach", fg_beach_wetshore),
    ("Shell-Dotted Playful Beach", fg_beach_playful),
]


# Round-8 sheet: lean, focused on the two LEADS (Mosaic + Riverbank) with their
# fallback/secondary, all netted to y=595 with the warm-lit lip + rescued sand.
# Satin Sand is dropped; Glazed Cobble is dropped (its glaze never read clearly
# premium against the mountains — not carried into round 8).
CONCEPTS_R8 = [
    ("ORIGINAL GAME FLOOR", None),
    ("Inlaid Geometric Mosaic", fg_inlaid_mosaic_v8),
    ("Polished Temple Pavement", fg_polished_pavement_v8),
    ("Riverbank Sandbar", fg_riverbank_v8),
    ("Golden Desert Dune", fg_golden_dune_v8),
]


# ══════════════════════════════════════════════════════════════════════════
# Round 11 — a COMPLETE NEW FLOOR: a premium PAVED BRICK / PAVER walkway.
#
# The prior leads were sand and dressed stone. This round chases a different
# hero entirely: a manicured brick SIDEWALK the bird flies over — warm clay
# laid in herringbone / running-bond / basketweave, plus a cool stone-paver
# palette counterpoint. The amazing-UX bar is threefold: it looks PREMIUM
# (per-brick bevel + a restrained specular dab), it stays QUIET behind the
# play lane, and it TILES SEAMLESSLY under scroll.
#
# Seamless scroll is the make-or-break: every pattern is keyed off ONE integer
# world phase (`ph = int(scroll * speed)`), and each brick/joint is placed by
# its world-cell index so the wrap at the screen edge is just the next cell in
# the same lattice — no pattern jump, no seam-doubling. The bevel lines (lit
# UL / shadow LR) and the world-anchored grain ride the same phase, so the
# whole surface translates as one rigid sheet as the world scrolls.
# ══════════════════════════════════════════════════════════════════════════


def _clay(pal):
    """Warm red-clay brick body tone tied to the Songyue masonry family: the
    worn sandstone pulled toward a terracotta so the walkway reads as fired
    clay brick, not raw sandstone. Stays warm in DAY; the painters cool it via
    `_nightf` so the night walkway retints without glowing."""
    terracotta = (196, 102, 70)
    return _mix(_mix(pal.get('stone_dark', (95, 70, 55)), terracotta, 0.70),
                _sandstone(pal), 0.22)


def _brick_tones(pal, body, *, night, cool=False):
    """Shared LIT-PLANE brick palette. Returns (front, back, mortar, bevel_lt,
    bevel_dk) all retinted toward a cool dark night ground so the walkway sits
    BELOW the night sky (the round's gate) with DARK mortar and no glow. `cool`
    swaps the day warmth out for a stone-grey cast (the paver counterpoint).
    Mortar is a desaturated, shaded body so a running-bond course can never
    read as a bright/dark seam line across the screen."""
    front = _shade(_sat(body, 1.05 if not cool else 0.92), 4)
    if _luma(front) * 255.0 > 222:                # never approach white in DAY
        front = _mix(front, _shade(body, -8), 0.5)
    back = _shade(_sat(body, 0.88), -22)
    # Night ground: cool + dark, so even the lit front lands under the ~89-luma
    # night sky. Pavers pull to a slightly cooler blue than warm clay.
    night_dk = (34, 42, 62) if not cool else (30, 40, 58)
    front = _mix(front, night_dk, 0.72 * night)
    back = _mix(back, _shade(night_dk, -8), 0.78 * night)
    # Mortar: low-contrast, desaturated, a notch darker than the body — and
    # night-cooled so it stays the darkest read on the plane after dark.
    mortar = _shade(_sat(body, 0.74), -34 - int(8 * night))
    mortar = _mix(mortar, _shade(night_dk, -12), 0.80 * night)
    # Per-brick bevel: a lit upper-left lip + a shadow lower-right. Kept value-
    # only and LOW-CONTRAST (close to the face) so that even where many bricks
    # in a running-bond course share a top-edge y, the aligned lit lips never
    # sum into a bright continuous horizontal seam across the screen. Per-brick
    # face value variation, not the bevel, carries the primary relief read.
    bevel_lt = _mix(front, (255, 246, 224) if not cool else (236, 240, 248),
                    0.16 * (1.0 - 0.5 * night))
    # Shadow bevel kept moderate (not deep) so an aligned course of brick
    # bottoms reads as a soft recessed joint, never a hard dark seam line.
    bevel_dk = _shade(_sat(body, 0.85), -20 - int(8 * night))
    bevel_dk = _mix(bevel_dk, _shade(night_dk, -10), 0.78 * night)
    return front, back, mortar, bevel_lt, bevel_dk


def _brick_face(pal, base, srng, *, night, cool=False):
    """Per-brick worn value variation around `base`: a small deterministic value
    drift so no two bricks read identical (the worn-clay charm), kept tonal so
    the field never sparkles. Capped under the day white-pool ceiling."""
    d = srng.randint(-12, 12)
    c = _shade(base, d)
    # An occasional cooler/warmer clay so a course carries a few stand-out
    # bricks, like a real reclaimed-brick walkway.
    if srng.random() < 0.22:
        tgt = (150, 70, 50) if not cool else (120, 126, 138)
        c = _mix(c, _mix(tgt, (40, 48, 66), 0.7 * night), 0.28)
    if _luma(c) * 255.0 > 222:
        c = _mix(c, _shade(base, -10), 0.5)
    return c


def _brick_dab(surf, x, y, w, hh, night):
    """The restrained premium specular: a single low-alpha warm ADD dab on a
    brick's lit shoulder. Faded HARD toward night so a brick never glints after
    dark, and kept tiny so it reads as a satin sheen, not a blown highlight. The
    alpha is low enough that even stacked with the grain ADD it can't pool a
    bright clay face toward white (the no-white-pool gate)."""
    if night >= 0.5:
        return
    a = int(8 * (1.0 - 2.0 * night))
    if a <= 0:
        return
    _spec_dab(surf, x, y, max(2, w), max(2, hh), (244, 226, 198), a)


# ── Brick 1 — Herringbone Clay Brick (45px, top@595) ─────────────────────────
# The hero "really nice bricks": warm terracotta laid in a classic 45deg
# herringbone. Each brick is an angled parallelogram (NET-NEW vertex geometry)
# with a 1px lit upper-left edge + 1px shadow lower-right, a low-contrast mortar
# gap, and a restrained per-brick specular dab. The lattice is keyed off ONE
# world phase so the diagonal weave wraps seamlessly under scroll.

def fg_brick_herringbone(surf, w, gy, h, scroll, pal):
    body = _clay(pal)
    night = _nightf(pal)
    front, back, mortar, bevel_lt, bevel_dk = _brick_tones(pal, body, night=night)
    top_y, region_h, night = _premium_base_v8(
        surf, w, gy, h, pal, front, back, ease=0.95,
        lip_warm=(255, 238, 212), lip_a=66)

    # Herringbone is a lattice of unit cells of size (2L x 2L) tiling the plane,
    # each holding two perpendicular bricks (one "/" leaning, one "\" leaning).
    # A brick is L long x B wide. World-anchoring: the lattice origin marches
    # with `ph` (integer world phase) so the weave is the SAME pattern wrapped
    # at any scroll — the cell index does the tiling, the screen just samples it.
    L = 22                                    # brick length
    B = 9                                     # brick width
    speed = 0.20
    ph = int(scroll * speed)
    # Cells span the full strip plus a margin so partial bricks at both edges
    # come from real neighbour cells (no clipped-pattern seam at the wrap).
    cols = w // (2 * L) + 3
    rows = region_h // (2 * L) + 3
    # The body fill behind the weave reads as deep mortar bedding. Kept LOW
    # alpha so the bricks dominate the read and the terracotta stays warm/lit;
    # only the thin 45deg gaps between angled bricks show the recessed mortar.
    bed = pygame.Surface((w, region_h), pygame.SRCALPHA)
    bed.fill((*mortar, 110))
    surf.blit(bed, (0, top_y))

    def _para(cx, cy, lean):
        """Corners of an L x B brick centred at (cx, cy), leaning '/' (lean=+1)
        or '\\' (lean=-1) at 45deg. The long axis is the diagonal; the brick is
        a parallelogram swept B wide perpendicular to it."""
        # Long-axis unit (45deg) and the perpendicular width offset.
        ax, ay = (0.7071, -0.7071 * lean)
        px, py = (-ay, ax)                    # perpendicular
        hl, hw = L * 0.5, B * 0.5
        return [
            (cx - ax * hl - px * hw, cy - ay * hl - py * hw),
            (cx + ax * hl - px * hw, cy + ay * hl - py * hw),
            (cx + ax * hl + px * hw, cy + ay * hl + py * hw),
            (cx - ax * hl + px * hw, cy - ay * hl + py * hw),
        ]

    mid_lo = top_y + region_h * 0.30
    mid_hi = top_y + region_h * 0.72
    for ry in range(-1, rows):
        for cxi in range(-1, cols):
            # Two bricks per cell, offset so they interlock into the weave.
            cell_x = cxi * 2 * L - (ph % (2 * L))
            cell_y = top_y + ry * 2 * L
            srng = random.Random(((cxi + (ph // (2 * L))) * 2654435761
                                  ^ (ry * 40503)) & 0xFFFFFFFF)
            in_mid = mid_lo <= cell_y + L <= mid_hi
            for bi, (ox, oy, lean) in enumerate((
                    (L * 0.5, L * 0.5, +1),
                    (L * 1.5, L * 0.5, -1))):
                cx = cell_x + ox
                cy = cell_y + oy
                if cx < -L or cx > w + L or cy < top_y - L or cy > h + L:
                    continue
                pts = _para(cx, cy, lean)
                fr = _brick_face(pal, _mix(back, front,
                                           max(0.0, min(1.0, (cy - top_y) /
                                                        max(1, region_h)))),
                                 srng, night=night)
                # Quiet the bird lane: pull mid-band bricks toward their mean so
                # the weave reads calm behind the player.
                if in_mid:
                    fr = _mix(fr, _mix(back, front, 0.5), 0.18)
                pygame.draw.polygon(surf, fr, [(int(x), int(y)) for x, y in pts])
                # Bevel: lit upper-left edge, shadow lower-right edge. The two
                # "upper-left" polygon edges get the lit lip; the opposite pair
                # gets the shadow — a crisp 1px proud-brick read.
                ip = [(int(x), int(y)) for x, y in pts]
                pygame.draw.line(surf, bevel_lt, ip[0], ip[1], 1)
                pygame.draw.line(surf, bevel_lt, ip[0], ip[3], 1)
                pygame.draw.line(surf, bevel_dk, ip[1], ip[2], 1)
                pygame.draw.line(surf, bevel_dk, ip[2], ip[3], 1)
                # Restrained specular on the front, lit bricks only — kept out of
                # the quiet mid band, faded out at night.
                if not in_mid and cy > top_y + region_h * 0.6 and srng.random() < 0.4:
                    _brick_dab(surf, int(cx) - 3, int(cy) - 3, 5, 4, night)

    _apply_grain_scroll(surf, 0, top_y, w, region_h, 3, scroll, speed)


# ── Brick 2 — Running-Bond Clay Brick Sidewalk (45px, top@595) ───────────────
# The clean classic sidewalk: horizontal courses of warm red-clay bricks in
# running bond (each course offset a half-brick so vertical joints never stack).
# Fine low-contrast mortar, subtle per-brick worn value variation, a 1px lit
# top lip + shadow bottom on each brick. Courses foreshorten gently toward the
# back. World-anchored on one phase so the bond wraps seamlessly.

def fg_brick_running_bond(surf, w, gy, h, scroll, pal):
    body = _clay(pal)
    night = _nightf(pal)
    front, back, mortar, bevel_lt, bevel_dk = _brick_tones(pal, body, night=night)
    top_y, region_h, night = _premium_base_v8(
        surf, w, gy, h, pal, front, back, ease=0.95,
        lip_warm=(255, 238, 212), lip_a=66)

    # Bedding mortar behind the bricks so every gap reads as a recessed joint.
    bed = pygame.Surface((w, region_h), pygame.SRCALPHA)
    bed.fill((*mortar, 130))
    surf.blit(bed, (0, top_y))

    mid_lo = top_y + region_h * 0.30
    mid_hi = top_y + region_h * 0.72
    n_course = 6
    for c in range(n_course):
        f0 = c / n_course
        f1 = (c + 1) / n_course
        y_back = _perspective_y(top_y, h, 1.0 - f0)
        y_front = _perspective_y(top_y, h, 1.0 - f1)
        if y_front <= y_back + 1:
            continue
        depth_t = f0
        brick_w = int(30 + 22 * depth_t)
        # Running bond: alternate courses shift a half-brick. The shift is part
        # of the world lattice (added to the world index) so it wraps with scroll.
        bond = (c % 2) * (brick_w // 2)
        speed = 0.18 + 0.08 * depth_t
        in_mid = mid_lo <= (y_back + y_front) * 0.5 <= mid_hi
        bh = y_front - y_back
        # Mortar gap is the 1px between the bedding band and each brick face;
        # inset the brick by 1px on all sides so the dark bedding shows as joints.
        for sx, k, srng in _scatter(scroll, w, speed, brick_w, 0xB21 + c):
            bx = sx + bond
            base = _mix(back, front, depth_t)
            fr = _brick_face(pal, base, srng, night=night)
            if in_mid:
                fr = _mix(fr, base, 0.16)
            rect = (bx + 1, y_back + 1, brick_w - 2, bh - 2)
            if rect[2] <= 0 or rect[3] <= 0:
                continue
            pygame.draw.rect(surf, fr, rect)
            # Bevel only on the VERTICAL edges (lit left / shadow right) so the
            # relief reads per-brick without ever forming a bright HORIZONTAL
            # line: in running bond every brick in a course shares one top-edge
            # y, so a lit top lip would sum into a continuous bright seam. The
            # horizontal course joint instead reads softly from the recessed
            # dark bedding gap alone — a low-contrast mortar course, not a seam.
            pygame.draw.line(surf, bevel_lt, (rect[0], rect[1]),
                             (rect[0], rect[1] + rect[3] - 1), 1)
            pygame.draw.line(surf, bevel_dk, (rect[0] + rect[2] - 1, rect[1]),
                             (rect[0] + rect[2] - 1, rect[1] + rect[3] - 1), 1)
            # No additive glint on this palette: the warm clay front already
            # sits bright, and an ADD dab there risks a single clipped-white
            # pixel where it stacks with the grain. The crisp vertical bevel +
            # the recessed bedding joint carry the premium read.

    _apply_grain_scroll(surf, 0, top_y, w, region_h, 3, scroll, 0.20)


# ── Brick 3 — Basketweave Brick (45px, top@595) ──────────────────────────────
# A decorative premium promenade: brick PAIRS alternating horizontal / vertical
# in a checkerboard basketweave (NET-NEW pair geometry). Each pair is two
# bricks; the woven read comes from neighbouring pairs running perpendicular.
# World-anchored on one phase so the weave wraps with scroll.

def fg_brick_basketweave(surf, w, gy, h, scroll, pal):
    body = _clay(pal)
    night = _nightf(pal)
    front, back, mortar, bevel_lt, bevel_dk = _brick_tones(pal, body, night=night)
    top_y, region_h, night = _premium_base_v8(
        surf, w, gy, h, pal, front, back, ease=0.95,
        lip_warm=(255, 238, 212), lip_a=66)

    bed = pygame.Surface((w, region_h), pygame.SRCALPHA)
    bed.fill((*mortar, 120))
    surf.blit(bed, (0, top_y))

    # A basketweave unit is a square block of side U holding either two
    # HORIZONTAL stacked bricks or two VERTICAL side-by-side bricks; the choice
    # alternates by (col+row) parity so the weave checkerboards. The block grid
    # marches with the world phase for a seamless wrap.
    U = 18
    speed = 0.20
    ph = int(scroll * speed)
    cols = w // U + 3
    rows = region_h // U + 2
    mid_lo = top_y + region_h * 0.30
    mid_hi = top_y + region_h * 0.72

    def _brick_rect(rect, base, srng, in_mid):
        if rect[2] <= 1 or rect[3] <= 1:
            return
        fr = _brick_face(pal, base, srng, night=night)
        if in_mid:
            fr = _mix(fr, base, 0.18)
        pygame.draw.rect(surf, fr, rect)
        # Vertical-edge bevel only (lit left / shadow right): the weave packs
        # many brick tops at one y, so a lit top lip would sum into a bright
        # horizontal seam. The horizontal joints read from the dark bedding gap.
        pygame.draw.line(surf, bevel_lt, (rect[0], rect[1]),
                         (rect[0], rect[1] + rect[3] - 1), 1)
        pygame.draw.line(surf, bevel_dk, (rect[0] + rect[2] - 1, rect[1]),
                         (rect[0] + rect[2] - 1, rect[1] + rect[3] - 1), 1)

    for ry in range(0, rows):
        by = top_y + ry * U
        for cxi in range(-1, cols):
            bx = cxi * U - (ph % U)
            wci = cxi + (ph // U)             # world column index for parity
            srng = random.Random(((wci * 2654435761) ^ (ry * 40503)) & 0xFFFFFFFF)
            base = _mix(back, front,
                        max(0.0, min(1.0, (by - top_y) / max(1, region_h))))
            in_mid = mid_lo <= by + U * 0.5 <= mid_hi
            horizontal = (wci + ry) % 2 == 0
            if horizontal:
                # Two stacked horizontal bricks (full width, half height each).
                _brick_rect((bx + 1, by + 1, U - 2, U // 2 - 1),
                            base, srng, in_mid)
                _brick_rect((bx + 1, by + U // 2 + 1, U - 2, U - U // 2 - 2),
                            _shade(base, srng.randint(-8, 8)), srng, in_mid)
            else:
                # Two side-by-side vertical bricks (half width, full height each).
                _brick_rect((bx + 1, by + 1, U // 2 - 1, U - 2),
                            base, srng, in_mid)
                _brick_rect((bx + U // 2 + 1, by + 1, U - U // 2 - 2, U - 2),
                            _shade(base, srng.randint(-8, 8)), srng, in_mid)
            # No additive glint: the bevel + bedding joint carry the read and an
            # ADD dab on the bright clay front risks a clipped-white pixel.

    _apply_grain_scroll(surf, 0, top_y, w, region_h, 3, scroll, speed)


# ── Brick 4 — Refined Stone / Concrete Pavers (45px, top@595) ────────────────
# The "something else" PALETTE COUNTERPOINT: cool grey-taupe square pavers laid
# in a clean grid (offset every other course a touch so it isn't a rigid mesh),
# crisp recessed joints + a soft bevel. Modern-premium, the cool answer to the
# warm clay. Same v8 scaffolding + world-anchored grid so it wraps seamlessly.

def fg_paver_stone(surf, w, gy, h, scroll, pal):
    # Cool stone derived from stone_mid/light, nudged grey-taupe.
    body = _mix(pal.get('stone_mid', (150, 132, 110)),
                pal.get('stone_light', (188, 170, 146)), 0.45)
    body = _sat(body, 0.78)
    night = _nightf(pal)
    front, back, mortar, bevel_lt, bevel_dk = _brick_tones(
        pal, body, night=night, cool=True)
    top_y, region_h, night = _premium_base_v8(
        surf, w, gy, h, pal, front, back, ease=0.95,
        lip_warm=(244, 246, 250), lip_a=58)

    bed = pygame.Surface((w, region_h), pygame.SRCALPHA)
    bed.fill((*mortar, 120))
    surf.blit(bed, (0, top_y))

    mid_lo = top_y + region_h * 0.30
    mid_hi = top_y + region_h * 0.72
    n_course = 5
    for c in range(n_course):
        f0 = c / n_course
        f1 = (c + 1) / n_course
        y_back = _perspective_y(top_y, h, 1.0 - f0)
        y_front = _perspective_y(top_y, h, 1.0 - f1)
        if y_front <= y_back + 1:
            continue
        depth_t = f0
        # Squarish pavers: width ~ tracks the course height so tiles read square.
        pav_w = int(26 + 22 * depth_t)
        bond = (c % 2) * (pav_w // 3)         # slight offset, not a rigid mesh
        speed = 0.18 + 0.08 * depth_t
        in_mid = mid_lo <= (y_back + y_front) * 0.5 <= mid_hi
        bh = y_front - y_back
        for sx, k, srng in _scatter(scroll, w, speed, pav_w, 0xC42 + c):
            bx = sx + bond
            base = _mix(back, front, depth_t)
            fr = _brick_face(pal, base, srng, night=night, cool=True)
            if in_mid:
                fr = _mix(fr, base, 0.18)
            rect = (bx + 1, y_back + 1, pav_w - 2, bh - 2)
            if rect[2] <= 0 or rect[3] <= 0:
                continue
            pygame.draw.rect(surf, fr, rect)
            # Vertical-edge bevel only (lit left / shadow right): an aligned
            # course of lit TOP lips would read as a bright horizontal seam, so
            # the horizontal joint is carried by the recessed dark bedding gap
            # alone — a soft low-contrast course, never a bright line.
            pygame.draw.line(surf, bevel_lt, (rect[0], rect[1]),
                             (rect[0], rect[1] + rect[3] - 1), 1)
            pygame.draw.line(surf, bevel_dk, (rect[0] + rect[2] - 1, rect[1]),
                             (rect[0] + rect[2] - 1, rect[1] + rect[3] - 1), 1)
            # No specular dab here: the cool stone front is already bright, so a
            # warm ADD glint would pool toward white. The crisp bevel + recessed
            # joint carry the premium read for this palette instead.

    _apply_grain_scroll(surf, 0, top_y, w, region_h, 3, scroll, 0.20)


# Round-11 sheet: a PAVED-WALKWAY spread — the new-floor hero hunt. Row 0 the
# original ref, Row 1 the round-8 stone Mosaic lead (quality/contrast anchor),
# then four brick/paver attempts covering PATTERN (herringbone / running-bond /
# basketweave / grid) AND PALETTE (warm clay <-> cool stone).
CONCEPTS_R11 = [
    ("ORIGINAL GAME FLOOR", None),
    ("Inlaid Geometric Mosaic", fg_inlaid_mosaic_v8),
    ("Herringbone Clay Brick", fg_brick_herringbone),
    ("Running-Bond Clay Sidewalk", fg_brick_running_bond),
    ("Basketweave Brick", fg_brick_basketweave),
    ("Refined Stone Pavers", fg_paver_stone),
]
