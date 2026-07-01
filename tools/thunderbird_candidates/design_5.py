"""ANCESTRAL SPIRIT — a translucent, glowing spirit-raptor thunderbird.

Defined by rim-glow and absence, not solid colour. A low-alpha teal body
fades under a bright ghost-white rim-line that traces the whole silhouette,
so the read survives at 40px on both bright-day and night skies. The rim
hue shimmers teal<->lilac across the flap cycle; wispy crest trails and
ghost feather-arcs dissolve behind the wing, and hollow white-glow eyes
carry the face. The bright continuous rim + hollow eyes do the work — the
fill is barely there on purpose.
"""
import pygame
import math

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W, COMPOSITE_H = 64, 84
BCX, BCY = 32, 44
HCX, HCY = 44, 34
CROWN_Y = 24

# Spirit palette. Fills ride low alpha; only the rim-line + eyes are opaque.
VOID = (12, 26, 30)            # #0C1A1E — reference bg only, never fill
TEAL = (47, 167, 155)          # #2FA79B — semi-transparent body fill
LILAC = (183, 166, 232)        # #B7A6E8 — rim highlight + shimmer
GHOST = (217, 255, 246)        # #D9FFF6 — rim-line + eyes + glow


def _flap(a):
    return (a + 40) / 90.0


def _strike(a):
    return 1.0 - _flap(a)


def _rim_hue(frame_idx):
    """Shimmer the rim/highlight teal<->lilac across the cycle. Frames run
    0->1->2->3 wings up->down; nudging the mix on 0/2/3 gives the sprite a
    living, breathing spectral flicker without changing its silhouette."""
    mix = {0: 0.15, 1: 0.0, 2: 0.6, 3: 0.9}.get(frame_idx, 0.3)
    return tuple(int(TEAL[i] * (1 - mix) + LILAC[i] * mix) for i in range(3))


def _spectral_fill(surf, pts, base, alpha, shimmer):
    """A low-alpha feather/body block painted on its own SRCALPHA layer so the
    translucency composites cleanly, with a lighter shimmer wash up top to
    fake the teal->lilac gradient the concept calls for."""
    layer = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.polygon(layer, (*base, alpha), pts)
    surf.blit(layer, (0, 0))
    # A brighter shimmer streak biased to the upper third of the block.
    top = min(p[1] for p in pts)
    bot = max(p[1] for p in pts)
    hi = [(x, y) for (x, y) in pts if y < top + (bot - top) * 0.55]
    if len(hi) >= 3:
        wash = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        pygame.draw.polygon(wash, (*shimmer, max(30, alpha - 40)), hi)
        surf.blit(wash, (0, 0))


def _rim(surf, pts, closed=True, width=2):
    """The load-bearing bright ghost-white rim-line. Full alpha, continuous —
    this is what makes the spirit read against any sky."""
    pygame.draw.lines(surf, GHOST, closed, [(round(x), round(y)) for x, y in pts], width)


def _glow_dot(surf, cx, cy, r, color, alpha):
    """A soft radial-ish glow puff via stacked fading rings — used for eye
    haloes, faint talon wisps and peeling ghost particles."""
    g = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
    for k in range(r, 0, -1):
        a = int(alpha * (k / r) ** 2 * 0.5)
        pygame.draw.circle(g, (*color, a), (r * 2, r * 2), r * 2 - (r - k) * 2 + r)
    surf.blit(g, (cx - r * 2, cy - r * 2))


def _wing_pts(base_x, side, lift, spread):
    """Swept spirit-wing silhouette anchored at the shoulder. ``lift`` raises
    the tip on the up-stroke; ``spread`` fans the trailing edge."""
    return [
        (base_x, CROWN_Y + 8),
        (base_x + side * (10 + spread), CROWN_Y + 4 - lift),
        (base_x + side * (24 + spread), CROWN_Y + 10 - lift),
        (base_x + side * (26 + spread), CROWN_Y + 20 - lift * 0.4),
        (base_x + side * (14 + spread * 0.5), BCY + 4),
        (base_x + side * 4, BCY - 2),
    ]


def _build_frame(wing_angle_deg, frame_idx=1):
    surf = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    strike = _strike(wing_angle_deg)   # 0 wings-up … 1 wings-down power stroke
    shimmer = _rim_hue(frame_idx)
    flapping = strike > 0.35           # peel ghost particles on the stroke

    # --- Wings/back: translucent feather fans with dissolving ghost-trails.
    for side in (-1, 1):
        base_x = BCX + side * 6
        lift = int((1 - strike) * 10)
        spread = int(strike * 4)
        wpts = _wing_pts(base_x, side, lift, spread)

        # Ghost feather-arcs streaming BEHIND the wing (drawn first, faint).
        for t in range(3):
            trail = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
            ax = base_x + side * (26 + spread + t * 5)
            ay = CROWN_Y + 12 - lift + t * 4
            rect = pygame.Rect(0, 0, 20 + t * 6, 26)
            rect.center = (ax, ay)
            a0, a1 = (2.2, 4.6) if side == 1 else (4.8, 0.9)
            pygame.draw.arc(trail, (*shimmer, 70 - t * 18), rect, a0, a1, 2)
            surf.blit(trail, (0, 0))

        # Feather fill fading lighter toward the tip.
        _spectral_fill(surf, wpts, TEAL, 82, shimmer)
        tip_pts = wpts[1:4]
        _spectral_fill(surf, tip_pts + [wpts[4]], LILAC, 55, GHOST)
        # Bright rim traces the wing edge.
        _rim(surf, wpts, closed=True, width=2)

        # A couple of inner feather-quill rim strokes for structure.
        for q in (0.35, 0.62):
            qx = base_x + side * (6 + q * 20 + spread)
            pygame.draw.line(surf, (*GHOST, 150),
                             (base_x + side * 3, CROWN_Y + 12),
                             (qx, CROWN_Y + 18 - lift), 1)

        # Peeling ghost particles off the trailing edge on the flap frames.
        if flapping:
            for p in range(3):
                px = base_x + side * (24 + spread + p * 6)
                py = BCY - 4 + p * 5
                _glow_dot(surf, px, py, 3 - (p // 2), GHOST, 90 - p * 22)

    # --- Body: low-alpha teal shell with a lilac shimmer core.
    body = [
        (BCX, BCY - 18),
        (BCX + 15, BCY - 8),
        (BCX + 14, BCY + 12),
        (BCX + 5, BCY + 22),
        (BCX - 7, BCY + 20),
        (BCX - 15, BCY + 6),
        (BCX - 13, BCY - 10),
    ]
    _spectral_fill(surf, body, TEAL, 118, shimmer)
    # Inner shimmer core — brighter lilac, small, to fake the vertical gradient.
    core = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.ellipse(core, (*LILAC, 70),
                        pygame.Rect(BCX - 8, BCY - 12, 16, 20))
    surf.blit(core, (0, 0))
    _rim(surf, body, closed=True, width=2)

    # --- Talons: barely-there glowing claw wisps.
    for side in (-1, 1):
        tx = BCX + side * 7
        ty = BCY + 20
        _glow_dot(surf, tx, ty + 3, 3, GHOST, 60)
        for k in (-1, 0, 1):
            wisp = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
            cx = tx + k * 3
            pygame.draw.arc(wisp, (*GHOST, 120),
                            pygame.Rect(cx - 3, ty, 6, 9), 3.5, 5.9, 1)
            surf.blit(wisp, (0, 0))

    # --- Head: translucent teal mass under a bright rim.
    head = [
        (HCX - 9, HCY - 9),
        (HCX + 3, HCY - 12),
        (HCX + 11, HCY - 5),
        (HCX + 11, HCY + 4),
        (HCX + 3, HCY + 10),
        (HCX - 8, HCY + 8),
    ]
    _spectral_fill(surf, head, TEAL, 118, shimmer)
    _rim(surf, head, closed=True, width=2)

    # --- Head/crest: wispy tapering crest trails fading out.
    for t, (spanx, spany, curl) in enumerate((
            (14, -14, 0.6), (17, -10, 0.4), (16, -5, 0.25))):
        crest = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        x0, y0 = HCX - 2, HCY - 8
        pts = []
        for s in range(9):
            f = s / 8.0
            x = x0 - spanx * f
            y = y0 + spany * f - math.sin(f * math.pi) * (6 - t * 1.5) * curl
            pts.append((x, y))
        for i in range(len(pts) - 1):
            a = int(150 * (1 - i / len(pts)))
            pygame.draw.line(crest, (*GHOST, a), pts[i], pts[i + 1],
                             2 if i < 3 else 1)
        surf.blit(crest, (0, 0))

    # --- Hollow white-glow eye: bright ring, dark hollow centre.
    ex, ey = HCX + 3, HCY - 1
    _glow_dot(surf, ex, ey, 5, GHOST, 130)
    pygame.draw.circle(surf, GHOST, (ex, ey), 4, 0)
    # Hollow it out — dark void centre reads as a spectral socket.
    hollow = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.circle(hollow, (*VOID, 210), (ex, ey), 2)
    surf.blit(hollow, (0, 0))

    # --- Beak: a thin ghost-rim hook, hollow inside.
    beak = [
        (HCX + 10, HCY),
        (HCX + 17, HCY + 2),
        (HCX + 11, HCY + 6),
    ]
    _spectral_fill(surf, beak, LILAC, 70, GHOST)
    _rim(surf, beak, closed=True, width=1)

    return surf


_cache = {}


def build(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    idx = frame_idx % len(_WING_ANGLES)
    angle = _WING_ANGLES[idx]
    key = (idx, round(tilt_deg / 3) * 3)
    if key not in _cache:
        _cache[key] = pygame.transform.rotozoom(
            _add_outline(_build_frame(angle, idx)), key[1], 1.0)
    return _cache[key]
