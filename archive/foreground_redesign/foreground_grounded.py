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
            # Rare worn/mossy slab — a soft darker wash + a few moss flecks along
            # the slab's back joint. ~1 in 6 so most flags stay clean/formal.
            if depth_t > 0.4 and srng.random() < 0.16:
                ww = step - 6
                wp = pygame.Surface((ww, max(3, (y_front - y_back) - 2)),
                                    pygame.SRCALPHA)
                wp.fill((*_shade(back, -12), 46))
                surf.blit(wp, (jx + 3, y_back + 2))
                if night < 0.65:
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
        # the front, neutral toward the back).
        mortar = _mix(joint, moss, 0.30 * (1 - depth_t) + 0.10)
        mb = pygame.Surface((w, course_h), pygame.SRCALPHA)
        mb.fill((*mortar, int(60 + 50 * depth_t)))
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
            # A 1px darker contact at the stone foot.
            pygame.draw.line(surf, _shade(face, -18),
                             (cx - half + 1, inset_b - 1),
                             (cx + half - 1, inset_b - 1), 1)

    _apply_grain(surf, 0, top_y, w, h - top_y, 4)


# ── Stone 3 — Cobblestone Setts (~40px) ─────────────────────────────────────
# Small rounded/squared setts in receding courses — the most "paved road/path"
# read. Each sett is a little rounded hump with a lit cap and a shadow gap, laid
# in offset courses (informed by _draw_cobble_curb).

def fg_cobblestone_setts(surf, w, gy, h, scroll, pal):
    night = _nightf(pal)
    top_y = gy - 40
    stone = _mix(_sandstone(pal), (150, 132, 110), 0.28)   # a touch greyer/cooler
    front = _shade(_sat(stone, 1.02), 3)
    back = _mix(_shade(_sat(stone, 0.86), -30), _horizon(pal), 0.16)
    front = _mix(front, (70, 80, 110), 0.30 * night)
    back = _mix(back, (60, 70, 100), 0.34 * night)
    region_h, mist_back = _grounded_base(surf, w, gy, h, top_y, pal, front, back,
                                         ease=0.82, recede=0.30)

    gapc = _shade(_sat(stone, 0.8), -34 - int(8 * night))   # dark joint between setts

    # Many short courses of small setts; courses pack tighter toward the back.
    # Each sett is a rounded-rect hump with a lit upper cap and a 1px shadow on
    # its lower-right, offset half a sett per course for the classic bond.
    n_course = 7
    for c in range(n_course):
        f0 = c / n_course
        f1 = (c + 1) / n_course
        y_back = _perspective_y(top_y, h, 1.0 - f0)
        y_front = _perspective_y(top_y, h, 1.0 - f1)
        if y_front <= y_back:
            continue
        depth_t = f0
        ch = max(3, y_front - y_back)
        sw = int(9 + 9 * depth_t)               # sett width grows toward player
        bond = (c % 2) * (sw // 2)
        speed = 0.20 + 0.10 * depth_t
        for sx, k, srng in _scatter(scroll, w, speed, sw, 0x3D9 + c):
            jx = sx + bond + srng.randint(-1, 1)
            cap = _shade(_mix(stone, front, 0.5 * depth_t), srng.randint(-10, 14))
            cap = _mix(cap, (66, 76, 106), 0.30 * night)
            sh = max(2, ch - 2)
            rect = pygame.Rect(jx, y_back + 1, max(3, sw - 2), sh)
            # Dark joint surround first, then the rounded sett over it.
            pygame.draw.rect(surf, gapc, rect.inflate(2, 1))
            br = min(3, sh // 2)
            pygame.draw.rect(surf, cap, rect, border_radius=br)
            # Lit cap on top edge + a shadow on the lower-right for roundness.
            if night < 0.72:
                pygame.draw.line(surf, _shade(cap, 22),
                                 (jx + 1, y_back + 1), (jx + max(3, sw - 4), y_back + 1), 1)
            pygame.draw.line(surf, _shade(cap, -20),
                             (jx + max(3, sw - 3), y_back + 2),
                             (jx + max(3, sw - 3), y_back + sh - 1), 1)

    _apply_grain(surf, 0, top_y, w, h - top_y, 3)


# ── Sand 1 — Desert Dune Sand (~38px) ───────────────────────────────────────
# The most minimal sand: warm pale-gold, fine wind-grain, faint DEAD-STRAIGHT
# horizontal ripple striations (never arcs), a few tiny pebbles.

def fg_desert_dune(surf, w, gy, h, scroll, pal):
    night = _nightf(pal)
    top_y = gy - 38
    sand = _sand(pal)
    front = _shade(_sat(sand, 1.02), 4)
    back = _mix(_shade(_sat(sand, 0.9), -22), _horizon(pal), 0.18)
    front = _mix(front, (68, 78, 108), 0.30 * night)
    back = _mix(back, (58, 68, 100), 0.34 * night)
    region_h, mist_back = _grounded_base(surf, w, gy, h, top_y, pal, front, back,
                                         ease=0.88, recede=0.30)

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

    # Slightly heavier grain than stone for the fine sand tooth.
    _apply_grain(surf, 0, top_y, w, h - top_y, 6)


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

    # Damp tide-line: a darker, slightly cooler band across the near third where
    # the sand is wet. A FLAT horizontal band (no crest), darkest at its front
    # edge, easing back to dry sand. A subtle additive sheen sits on the damp
    # band so it reads glossy without a continuous bright seam.
    damp = _mix(_sat(sand, 0.84), (120, 116, 110), 0.45)
    damp = _mix(damp, (50, 60, 92), 0.34 * night)
    band_top = top_y + int(region_h * 0.52)
    for y in range(band_top, h):
        t = (y - band_top) / max(1, h - band_top)   # 0 at band top -> 1 at foot
        # Wet strongest mid-band, easing at the very foot (where dry footprints
        # would sit) so it isn't a flat slab of dark.
        wet = math.sin(min(1.0, t) * math.pi) * 0.5 + t * 0.4
        ln = pygame.Surface((w, 1), pygame.SRCALPHA)
        ln.fill((*damp, int(110 * min(1.0, wet))))
        surf.blit(ln, (0, y))
    # Low sheen — a few soft additive smears riding the damp band, kept LOW and
    # broken so it never becomes a bright horizontal seam.
    if night < 0.75:
        sheen = _mix(_horizon(pal), (255, 245, 220), 0.4)
        for sx, k, srng in _scatter(scroll, w, 0.2, 56, 0x6C4):
            sy = band_top + srng.randint(2, max(3, region_h // 4))
            sw = srng.randint(18, 40)
            sl = pygame.Surface((sw, 2), pygame.SRCALPHA)
            sl.fill((*sheen, srng.randint(14, 26)))
            surf.blit(sl, (sx - sw // 2, sy), special_flags=pygame.BLEND_RGB_ADD)

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

    _apply_grain(surf, 0, top_y, w, h - top_y, 5)


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

    # Sparse DRY grass tufts at the BACK edge only (where the bar meets the bank).
    # Pale straw blades fanning up; clumped and sparse so the front sand stays
    # open. Confined to the rear ~30% so they never crowd the bird lane.
    straw = _mix((196, 184, 132), sand, 0.3)
    straw = _mix(straw, (96, 104, 120), 0.34 * night)
    straw_dk = _shade(straw, -26)
    for sx, k, srng in _scatter(scroll, w, 0.2, 70, 0x8D2):
        if srng.random() < 0.4:
            continue
        ty = top_y + int(srng.uniform(0.06, 0.30) * region_h)
        n_blade = srng.randint(3, 6)
        for _b in range(n_blade):
            bx = sx + srng.randint(-6, 6)
            bh = srng.randint(5, 11)
            lean = srng.randint(-3, 3)
            col = straw if srng.random() < 0.6 else straw_dk
            pygame.draw.line(surf, col, (bx, ty), (bx + lean, ty - bh), 1)

    _apply_grain(surf, 0, top_y, w, h - top_y, 6)


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
