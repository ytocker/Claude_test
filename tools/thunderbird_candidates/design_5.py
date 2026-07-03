"""ANCESTRAL SPIRIT — a translucent, glowing spirit-raptor thunderbird.

Defined by rim-glow and absence, not solid colour, yet built to read on ANY
sky. The trick is a DUAL rim: a deep void-teal dark under-stroke drawn
outside/under a bright ghost-white inner line, so a continuous dark contour
anchors the silhouette against bright day while the ghost line still glows on
night. The teal body carries one committed dark value floor low in the shell
so the spirit is never just barely-denser-than-sky. The fill hue shimmers
teal<->lilac across the flap cycle, but the rim-line and its dark under-stroke
are pinned to constant values so the outline never drifts with the shimmer.
Wings are one bold swept chevron per side (bird-of-prey read at 40px); the
hollow white-glow eye and glowing claw-tips carry the identity beats.
"""
import pygame
import math

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W, COMPOSITE_H = 64, 84
BCX, BCY = 32, 44
HCX, HCY = 44, 34
CROWN_Y = 24

# Spirit palette. Fills ride low alpha; the rim's bright line + dark
# under-stroke + eyes are the committed high-contrast values.
VOID = (12, 26, 30)            # #0C1A1E — dark rim under-stroke + eye socket
VOID_DEEP = (18, 48, 48)       # #123030 — softer dark under-stroke alt
FLOOR = (29, 95, 88)           # #1D5F58 — darker teal value floor, lower body
TEAL = (47, 167, 155)          # #2FA79B — semi-transparent body fill
LILAC = (183, 166, 232)        # #B7A6E8 — fill shimmer ONLY (never the rim)
GHOST = (217, 255, 246)        # #D9FFF6 — rim inner line + eyes + glow


def _flap(a):
    return (a + 40) / 90.0


def _strike(a):
    return 1.0 - _flap(a)


def _fill_hue(frame_idx):
    """Shimmer the FILL teal<->lilac across the cycle. Frames run 0->1->2->3
    wings up->down; nudging the mix gives a living spectral flicker. This is
    intentionally used only for the fill wash — the rim never sees lilac, so
    the silhouette outline value is stable across the whole cycle."""
    mix = {0: 0.15, 1: 0.0, 2: 0.45, 3: 0.7}.get(frame_idx, 0.3)
    return tuple(int(TEAL[i] * (1 - mix) + LILAC[i] * mix) for i in range(3))


def _spectral_fill(surf, pts, base, alpha, shimmer, floor=False):
    """A translucent feather/body block on its own SRCALPHA layer so the
    translucency composites cleanly. A denser core anchors a value on day; a
    darker teal floor washes the lower third so one committed dark value lives
    in the shape even while the top stays airy and ghostly."""
    layer = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.polygon(layer, (*base, alpha), pts)
    surf.blit(layer, (0, 0))
    top = min(p[1] for p in pts)
    bot = max(p[1] for p in pts)
    if floor:
        # Bake a darker teal value floor into the lower body so the shape has
        # a committed dark value even on a bright sky (a ghost can be
        # translucent yet still anchor one dense value).
        lo = [(x, y) for (x, y) in pts if y > top + (bot - top) * 0.42]
        if len(lo) >= 3:
            fl = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
            pygame.draw.polygon(fl, (*FLOOR, min(200, alpha + 40)), lo)
            surf.blit(fl, (0, 0))
    # A brighter shimmer streak biased to the upper third of the block.
    hi = [(x, y) for (x, y) in pts if y < top + (bot - top) * 0.5]
    if len(hi) >= 3:
        wash = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        pygame.draw.polygon(wash, (*shimmer, max(24, alpha - 60)), hi)
        surf.blit(wash, (0, 0))


def _rim(surf, pts, closed=True):
    """The load-bearing DUAL rim: a deep void-teal dark under-stroke drawn
    first (grown to sit just outside/under the bright line) then the bright
    ghost-white inner line on top. The dark halo guarantees a continuous dark
    contour on bright day; the ghost line guarantees the glow on night. Both
    are pinned to constant colours so the outline never drifts with shimmer."""
    ipts = [(round(x), round(y)) for x, y in pts]
    # Dark under-stroke: thicker so it peeks out beyond the bright line as a
    # 1px dark halo on every side.
    pygame.draw.lines(surf, (*VOID, 210), closed, ipts, 4)
    # Bright inner line on top.
    pygame.draw.lines(surf, GHOST, closed, ipts, 2)


def _glow_dot(surf, cx, cy, r, color, alpha):
    """A soft radial-ish glow puff via stacked fading rings — used for eye
    haloes and the glowing claw tips."""
    g = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
    for k in range(r, 0, -1):
        a = int(alpha * (k / r) ** 2 * 0.5)
        pygame.draw.circle(g, (*color, a), (r * 2, r * 2), r * 2 - (r - k) * 2 + r)
    surf.blit(g, (cx - r * 2, cy - r * 2))


def _wing_pts(base_x, side, lift, spread):
    """One bold swept-wing chevron per side — a clean bird-of-prey silhouette
    that survives at 40px. ``lift`` raises the tip on the up-stroke;
    ``spread`` fans the trailing edge. No inner quills; the dual rim traces
    this single polygon so the read stays crisp when shrunk."""
    return [
        (base_x, CROWN_Y + 6),
        (base_x + side * (14 + spread), CROWN_Y + 1 - lift),
        (base_x + side * (30 + spread), CROWN_Y + 9 - lift),
        (base_x + side * (27 + spread), CROWN_Y + 21 - lift * 0.4),
        (base_x + side * (13 + spread * 0.5), BCY + 5),
        (base_x + side * 4, BCY - 3),
    ]


def _build_frame(wing_angle_deg, frame_idx=1):
    surf = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    strike = _strike(wing_angle_deg)   # 0 wings-up … 1 wings-down power stroke
    shimmer = _fill_hue(frame_idx)

    # --- Wings/back: one bold swept chevron per side with a dissolving trail.
    for side in (-1, 1):
        base_x = BCX + side * 6
        lift = int((1 - strike) * 10)
        spread = int(strike * 4)
        wpts = _wing_pts(base_x, side, lift, spread)

        # A single faint ghost feather-trail streaming behind the tip (fades
        # out at 40px, charming at hero size). One arc, not a fan — keeps the
        # silhouette from turning into a fuzzy blob.
        trail = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        ax = base_x + side * (32 + spread)
        ay = CROWN_Y + 12 - lift
        rect = pygame.Rect(0, 0, 22, 26)
        rect.center = (ax, ay)
        a0, a1 = (2.2, 4.6) if side == 1 else (4.8, 0.9)
        pygame.draw.arc(trail, (*shimmer, 60), rect, a0, a1, 2)
        surf.blit(trail, (0, 0))

        # Translucent fill with a committed teal value floor along the lower
        # (trailing) edge, then the load-bearing dual rim.
        _spectral_fill(surf, wpts, TEAL, 130, shimmer, floor=True)
        _rim(surf, wpts, closed=True)

    # --- Body: teal shell with a committed dark value floor + shimmer core.
    body = [
        (BCX, BCY - 18),
        (BCX + 15, BCY - 8),
        (BCX + 14, BCY + 12),
        (BCX + 5, BCY + 22),
        (BCX - 7, BCY + 20),
        (BCX - 15, BCY + 6),
        (BCX - 13, BCY - 10),
    ]
    _spectral_fill(surf, body, TEAL, 165, shimmer, floor=True)
    # Inner shimmer core — brighter lilac, small, to fake the vertical gradient
    # (fill only; it never touches the rim value).
    core = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.ellipse(core, (*LILAC, 66),
                        pygame.Rect(BCX - 8, BCY - 12, 16, 18))
    surf.blit(core, (0, 0))
    _rim(surf, body, closed=True)

    # --- Talons: clear glowing spirit-claws with bright r=2 tips so they read
    # on bright day (no more invisible arc-wisps).
    for side in (-1, 1):
        tx = BCX + side * 6
        ty = BCY + 21
        for k in (-1, 1):
            cx = tx + k * 3
            claw = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
            # Dark under-stroke then bright claw so it reads on light sky too.
            pygame.draw.line(claw, (*VOID, 200), (tx, ty), (cx, ty + 6), 3)
            pygame.draw.line(claw, GHOST, (tx, ty), (cx, ty + 6), 1)
            surf.blit(claw, (0, 0))
            _glow_dot(surf, cx, ty + 6, 2, GHOST, 150)
            pygame.draw.circle(surf, GHOST, (cx, ty + 6), 2)

    # --- Head: translucent teal mass under the dual rim.
    head = [
        (HCX - 9, HCY - 9),
        (HCX + 3, HCY - 12),
        (HCX + 11, HCY - 5),
        (HCX + 11, HCY + 4),
        (HCX + 3, HCY + 10),
        (HCX - 8, HCY + 8),
    ]
    _spectral_fill(surf, head, TEAL, 165, shimmer, floor=True)
    _rim(surf, head, closed=True)

    # --- Head/crest: wispy tapering crest trails fading out (vanish at 40px).
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

    # --- Hollow white-glow eye: bright ring, dark hollow centre. The strongest
    # identity beat; enlarged 1px so it survives 40px on both skies.
    ex, ey = HCX + 3, HCY - 1
    _glow_dot(surf, ex, ey, 6, GHOST, 140)
    pygame.draw.circle(surf, GHOST, (ex, ey), 5, 0)
    # Hollow it out — dark void centre reads as a spectral socket.
    hollow = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.circle(hollow, (*VOID, 220), (ex, ey), 3)
    surf.blit(hollow, (0, 0))

    # --- Beak: a thin dual-rim hook.
    beak = [
        (HCX + 10, HCY),
        (HCX + 17, HCY + 2),
        (HCX + 11, HCY + 6),
    ]
    _spectral_fill(surf, beak, TEAL, 150, shimmer, floor=True)
    _rim(surf, beak, closed=True)

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
