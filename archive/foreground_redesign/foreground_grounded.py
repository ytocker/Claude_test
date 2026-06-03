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
    top_y = gy - 56
    stone = _sandstone(pal)
    # Near->far value fall: warmer/lighter at the front lip, cooler/darker into
    # the back where the mist sits. Cool the whole plane toward night.
    front = _shade(_sat(stone, 1.04), -2)
    back = _mix(_shade(_sat(stone, 0.86), -30), _horizon(pal), 0.10)
    front = _mix(front, (70, 80, 110), 0.30 * night)
    back = _mix(back, (60, 70, 100), 0.34 * night)
    _flat_slab(surf, w, h, top_y, back, front, ease=0.9)

    joint = _shade(_mix(stone, (60, 44, 34), 0.5), -12 - int(8 * night))
    joint_hi = _mix(_sat(stone, 1.1), (255, 232, 196), 0.4)

    # Receding paving courses: 6 rows packed tighter toward the back (perspective),
    # each a run of irregular-width slabs with inset mortar joints. The course
    # lines are FLAT horizontals (no wave); slab breaks ride the world scroll so
    # the joints flow with the ground.
    n_course = 6
    rim = _mix(_horizon(pal), (255, 224, 168), 0.5)
    for c in range(n_course):
        f0 = c / n_course
        f1 = (c + 1) / n_course
        y_back = _perspective_y(top_y, h, 1.0 - f0)
        y_front = _perspective_y(top_y, h, 1.0 - f1)
        if y_front <= y_back:
            continue
        depth_t = f0  # 0 at back, ->1 at front
        # Slab width grows toward the player; joints march in world space.
        step = int(26 + 30 * depth_t)
        jc = _mix(joint, back, max(0.0, 0.45 * (1 - depth_t)))
        # Horizontal course joint (flat).
        pygame.draw.line(surf, jc, (0, y_back), (w, y_back), 1)
        if depth_t > 0.45:
            pygame.draw.line(surf, _shade(jc, 14), (0, y_back + 1), (w, y_back + 1), 1)
        # Vertical slab joints across this course, jittered per world cell.
        speed = 0.18 + 0.10 * depth_t
        for sx, k, srng in _scatter(scroll, w, speed, step, 0x9A1 + c):
            jy0, jy1 = y_back, y_front
            jx = sx + srng.randint(-2, 2)
            pygame.draw.line(surf, jc, (jx, jy0), (jx, jy1), 1)
            # Faint lit edge on the player-facing side of nearer slabs.
            if depth_t > 0.4:
                pygame.draw.line(surf, _shade(jc, 18), (jx + 1, jy0), (jx + 1, jy1), 1)
        # A few worn slabs catch a faint warm sheen on the front courses.
        if depth_t > 0.55:
            for sx, k, srng in _scatter(scroll, w, speed * 1.3, step, 0x9A1 + c + 40):
                if srng.random() < 0.5:
                    wy = (y_back + y_front) // 2
                    sheen = pygame.Surface((step - 4, max(2, (y_front - y_back) // 2)),
                                           pygame.SRCALPHA)
                    sheen.fill((*rim, int(26 + 20 * depth_t)))
                    surf.blit(sheen, (sx - step // 2, y_back + 2),
                              special_flags=pygame.BLEND_RGB_ADD)

    # Fine stone grain over the whole plane.
    _apply_grain(surf, 0, top_y, w, h - top_y, 4)

    # The single front lip of the pavement gets a restrained warm edge — the
    # paving stone the warm horizon light grazes. Not a mountain crest, just the
    # near course edge picking up the same light the pagoda does.
    lip_y = _perspective_y(top_y, h, 0.02)
    edge = _mix(rim, (255, 214, 150), 0.2 + 0.3 * night)
    pygame.draw.line(surf, edge, (0, top_y), (w, top_y), 1)
    pygame.draw.line(surf, _shade(joint, -10), (0, top_y - 1), (w, top_y - 1), 1)


# ══════════════════════════════════════════════════════════════════════════
# Concept 2 — Sun-Cracked Packed Earth  (~50px, natural)
# The most minimal "solid land underfoot": a flat dry clay plane with a
# procedural polygon crack network, a scatter of embedded pebbles, and a faint
# dust grain. No vegetation, no architecture — just baked earth. Opaque to the
# bottom; the crack lines are the entire identity.
# ══════════════════════════════════════════════════════════════════════════

def _clay(pal):
    """Dry packed-clay tone — a desaturated warm ochre off the stage ground band,
    a touch greyer than the courtyard stone so it reads as earth, not masonry."""
    base = pal.get('ground_mid', (176, 142, 92))
    return _mix(_sat(base, 0.82), (168, 138, 104), 0.5)


def fg_cracked_earth(surf, w, gy, h, scroll, pal):
    night = _nightf(pal)
    top_y = gy - 50
    clay = _clay(pal)
    front = _shade(clay, 4)
    back = _mix(_shade(_sat(clay, 0.88), -26), _horizon(pal), 0.08)
    front = _mix(front, (66, 74, 104), 0.30 * night)
    back = _mix(back, (58, 66, 96), 0.34 * night)
    _flat_slab(surf, w, h, top_y, back, front, ease=0.95)

    crack = _shade(_sat(clay, 0.7), -42 - int(10 * night))
    crack_hi = _shade(clay, 22)  # sunlit upper lip of an open crack

    # Procedural polygon crack network: scatter seed nodes across the plane in
    # world space, then join near neighbours with jagged 2-3 segment cracks. A
    # deterministic per-cell rng keeps the network stable + seamless under scroll.
    region_h = h - top_y
    nodes = []
    for sx, k, srng in _scatter(scroll, w, 0.16, 30, 0x2C7):
        ny = top_y + int(srng.uniform(0.08, 0.98) * region_h)
        nodes.append((sx, ny, k, srng))
    # Sort by x so neighbour joins are local; draw cracks between adjacent nodes
    # and an occasional downward branch — the dry-mud polygon look.
    nodes.sort(key=lambda n: n[0])
    for i, (nx, ny, k, srng) in enumerate(nodes):
        # Link to next 1-2 neighbours with a kinked crack.
        for j in range(1, srng.randint(2, 3)):
            if i + j >= len(nodes):
                break
            tx, ty, _, _ = nodes[i + j]
            if abs(tx - nx) > 52:
                continue
            midx = (nx + tx) // 2 + srng.randint(-5, 5)
            midy = (ny + ty) // 2 + srng.randint(-4, 4)
            depth_t = (ny - top_y) / max(1, region_h)
            cw = 2 if depth_t > 0.6 else 1
            pts = [(nx, ny), (midx, midy), (tx, ty)]
            pygame.draw.lines(surf, crack, False, pts, cw)
            # Sunlit upper lip on nearer cracks gives the crack a tiny relief.
            if depth_t > 0.5 and night < 0.6:
                pygame.draw.aalines(surf, _mix(crack_hi, front, 0.3), False,
                                    [(p[0], p[1] - 1) for p in pts])
        # A short downward hairline branch off some nodes.
        if srng.random() < 0.5:
            by = min(h - 1, ny + srng.randint(6, 16))
            bx = nx + srng.randint(-6, 6)
            pygame.draw.line(surf, crack, (nx, ny), (bx, by), 1)

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
    # Restrained warm front edge — only a faint sun-graze, no golden crest.
    edge = _mix(_horizon(pal), front, 0.45)
    pygame.draw.line(surf, edge, (0, top_y), (w, top_y), 1)
    pygame.draw.line(surf, crack, (0, top_y + 1), (w, top_y + 1), 1)


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

    # Parallel raked furrows: flat horizontal grooves stepping down the plane,
    # each deflected upward into a smooth bump where it passes a stone (the
    # karesansui ripple-around-rock). The deflection is a localized gaussian, NOT
    # a periodic sine, so it reads as raking around an object, never as waves.
    n_groove = 11
    for gi in range(n_groove):
        f = gi / (n_groove - 1)
        base_y = _perspective_y(top_y, h, 1.0 - f * 0.96)
        depth_t = f
        gw = 1 if depth_t < 0.55 else 2

        def deflect(x):
            dy = 0.0
            for (scx, scy, sr) in stone_cx:
                # Only furrows passing near/below the stone curve around it.
                if base_y < scy - sr - 2:
                    continue
                d = (x - scx) / (sr + 14.0)
                dy -= math.exp(-d * d) * (sr + 10) * (0.5 + 0.5 * depth_t)
            return dy

        pts = []
        for x in range(0, w + 1, 4):
            yy = base_y + deflect(x)
            if yy < top_y:
                yy = top_y
            pts.append((x, int(yy)))
        # Groove shadow + a thin raised ridge highlight just above it.
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
    # Quiet front edge — gravel catches a soft pale light, no golden crest.
    edge = _mix(_horizon(pal), front, 0.5)
    pygame.draw.line(surf, edge, (0, top_y), (w, top_y), 1)
    pygame.draw.line(surf, groove, (0, top_y + 1), (w, top_y + 1), 1)


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
    game's kelly meadow."""
    base = pal.get('foliage_mid', (60, 110, 80))
    return _mix(_sat(base, 0.58), (74, 96, 76), 0.45)


def fg_inkwash_meadow(surf, w, gy, h, scroll, pal):
    night = _nightf(pal)
    top_y = gy - 48
    grass = _meadow(pal)
    front = _shade(grass, 2)
    back = _mix(_shade(_sat(grass, 0.85), -22), _horizon(pal), 0.10)
    front = _mix(front, (52, 64, 96), 0.32 * night)
    back = _mix(back, (46, 58, 90), 0.36 * night)
    _flat_slab(surf, w, h, top_y, back, front, ease=0.9)

    region_h = h - top_y
    blade_dk = _shade(_sat(grass, 0.9), -24)
    blade_lt = _mix(grass, (150, 168, 130), 0.4)
    blade_lt = _mix(blade_lt, (70, 80, 108), 0.3 * night)

    # Fine blade texture: short upward flicks scattered in world space, denser and
    # taller toward the front plane, leaning slightly with a gentle breeze phase.
    # Pure 1-2px lines — quiet, not the bright tuft clumps of the live meadow.
    lean = math.sin(scroll * 0.01) * 1.5
    for sx, k, srng in _scatter(scroll, w, 0.26, 7, 0x33D):
        by = top_y + int(srng.uniform(0.10, 1.0) * region_h)
        depth_t = (by - top_y) / max(1, region_h)
        bl = int(3 + depth_t * 6 + srng.randint(0, 2))
        tip_x = sx + int(lean * (0.5 + depth_t)) + srng.randint(-1, 1)
        col = blade_dk if srng.random() < 0.6 else blade_lt
        pygame.draw.line(surf, col, (sx, by), (tip_x, by - bl), 1)

    # A few sparse reeds — taller, thinner stalks with a small seed-head tuft,
    # clumped lightly and kept off the dead-centre so they don't crowd the lane.
    reed_dk = _shade(_sat(grass, 0.7), -30)
    reed_seed = _mix(_horizon(pal), grass, 0.5)
    reed_seed = _mix(reed_seed, (90, 100, 120), 0.35 * night)
    for sx, k, srng in _scatter(scroll, w, 0.24, 64, 0x88E):
        if srng.random() < 0.4:
            continue
        ry = top_y + int(srng.uniform(0.5, 0.95) * region_h)
        rh = srng.randint(14, 24)
        sway = int(lean * 1.6) + srng.randint(-1, 1)
        tip = (sx + sway, ry - rh)
        pygame.draw.line(surf, reed_dk, (sx, ry), tip, 1)
        # Slim seed head — a short fatter stroke at the tip, not a flower.
        pygame.draw.line(surf, reed_seed, (tip[0], tip[1]),
                         (tip[0], tip[1] + 4), 2)
        # A couple of leaf flicks off the stalk.
        midy = ry - rh // 2
        pygame.draw.line(surf, reed_dk, (sx, midy), (sx - 4, midy - 2), 1)

    _apply_grain(surf, 0, top_y, w, h - top_y, 4)
    # No golden crest — the meadow's front lip is just a slightly lit blade line.
    edge = _mix(_horizon(pal), front, 0.55)
    pygame.draw.line(surf, _mix(blade_lt, edge, 0.5), (0, top_y), (w, top_y), 1)


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
    # The board edges converge slightly toward centre with depth (gentle one-point
    # perspective) so the deck recedes. Boards ride the world scroll so the deck
    # slides under the bird. The plank grid is the identity — flat plane, no wave.
    n_plank = 9
    vanish = w * 0.5
    converge = 0.16  # how much board edges pull toward the vanishing column
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

    # Cross-board nosing line at the very front edge (the deck's leading board
    # cap) catches the warm horizon light — a restrained material edge, not a
    # mandatory golden ridge crest.
    nose = _mix(_horizon(pal), front, 0.4 + 0.2 * night)
    pygame.draw.line(surf, _shade(gap, -6), (0, top_y - 1), (w, top_y - 1), 1)
    pygame.draw.line(surf, nose, (0, top_y), (w, top_y), 1)
    pygame.draw.line(surf, _shade(nose, -18), (0, top_y + 2), (w, top_y + 2), 1)
    # A faint warm sheen along the lit run of the front boards at low sun.
    if night < 0.7:
        sheen = pygame.Surface((w, 10), pygame.SRCALPHA)
        sheen.fill((*_mix(nose, (255, 224, 168), 0.4), 26))
        surf.blit(sheen, (0, top_y + 3), special_flags=pygame.BLEND_RGB_ADD)


# ── registry (order matches the brief) ──────────────────────────────────────

CONCEPTS = [
    ("Flagstone Courtyard", fg_flagstone_courtyard),
    ("Sun-Cracked Packed Earth", fg_cracked_earth),
    ("Raked Zen-Gravel Garden", fg_zen_gravel),
    ("Ink-Wash Meadow", fg_inkwash_meadow),
    ("Wood-Plank Boardwalk", fg_wood_boardwalk),
]
