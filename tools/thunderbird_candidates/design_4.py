"""NIGHT THUNDER — thunderbird skin candidate (Design 4).

A nocturnal, brooding raptor: deep-indigo body cracked by pale static
lightning-scar veins, lit by two glowing violet eyes (the 40px tell), with
storm-grey ragged wingtips. Scars are STATIC (identical every frame) so the
bird reads as scarred, not animated — except a rare quiet flash on the
power-flap frame (frame 0, wing_angle=50) where the scars brighten.

Scratch exploration builder — wrapped by the ninja_render harness, never
registered in store_skins.BUILDERS.
"""
import pygame
import math

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W, COMPOSITE_H = 64, 84
BCX, BCY = 32, 44
HCX, HCY = 44, 34
CROWN_Y = 24

# Night-storm palette.
NIGHT_INDIGO  = (23, 16, 41)     # #171029 — darkest body base
VIOLET_SHADOW = (59, 42, 99)     # #3B2A63 — mid violet
ELECTRIC      = (124, 91, 214)   # #7C5BD6 — glow + scar accent
STORM_GREY    = (90, 100, 114)   # #5A6472 — ragged wingtips
SCAR_PALE     = (231, 220, 255)  # #E7DCFF — lightning scars


def _flap(a):
    return (a + 40) / 90.0


def _strike(a):
    return 1.0 - _flap(a)


def _glow_dot(surf, center, radius, color, layers=4):
    """Soft additive violet aura — stacked translucent discs so the storm
    haze reads without a hard edge."""
    cx, cy = center
    for i in range(layers, 0, -1):
        r = radius * i / layers
        a = int(46 * (1 - (i - 1) / layers))
        g = pygame.Surface((int(r * 2 + 2), int(r * 2 + 2)), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (int(r + 1), int(r + 1)), int(r))
        surf.blit(g, (cx - r - 1, cy - r - 1), special_flags=pygame.BLEND_RGBA_ADD)


def _wing(angle_deg, strike):
    """Ragged storm wing: violet inner feathers fading to jagged storm-grey
    outer tips, with a faint electric rim along the leading edge."""
    w = pygame.Surface((52, 52), pygame.SRCALPHA)

    # Inner violet plane (anchored at the shoulder, spread out and back).
    inner = [(26, 27), (44, 15), (49, 27), (40, 36), (24, 40)]
    pygame.draw.polygon(w, VIOLET_SHADOW, inner)

    # Ragged storm-grey outer tips — a jagged saw edge instead of a clean arc.
    tips = [(44, 15), (49, 27), (40, 36),
            (46, 33), (43, 27), (48, 22), (44, 19)]
    pygame.draw.polygon(w, STORM_GREY, [(44, 15), (49, 27), (46, 33),
                                        (50, 30), (47, 24), (51, 20)])
    pygame.draw.polygon(w, STORM_GREY, [(40, 36), (49, 27), (44, 34)])

    # Dark underside shadow to seat the wing against the body.
    pygame.draw.polygon(w, NIGHT_INDIGO, [(26, 27), (40, 36), (24, 40)])

    # Feather dividers in mid violet.
    pygame.draw.line(w, VIOLET_SHADOW, (28, 29), (44, 18), 2)
    pygame.draw.line(w, VIOLET_SHADOW, (29, 33), (45, 25), 2)

    # Faint electric rim-light along the leading edge — brighter on the strike.
    rim_a = int(110 + 90 * strike)
    rim = pygame.Surface((52, 52), pygame.SRCALPHA)
    pygame.draw.line(rim, (*ELECTRIC, rim_a), (27, 27), (44, 15), 2)
    w.blit(rim, (0, 0))

    return pygame.transform.rotate(w, angle_deg)


def _scar(surf, pts, bright):
    """A single hairline lightning-scar polyline. `bright` toggles the quiet
    power-flap flash (higher alpha + paler colour)."""
    col = SCAR_PALE if bright else ELECTRIC
    a = 235 if bright else 150
    scar = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.lines(scar, (*col, a), False, pts, 1)
    if bright:
        # A faint halo so the flash feels like light, not a repaint.
        glow = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        pygame.draw.lines(glow, (*ELECTRIC, 70), False, pts, 3)
        surf.blit(glow, (0, 0))
    surf.blit(scar, (0, 0))


def _build_frame(wing_angle_deg):
    surf = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    strike = _strike(wing_angle_deg)
    # The power-flap frame (angle 50) is the rare quiet flash.
    flash = wing_angle_deg == 50

    # --- Far wing (behind body) ---
    far = _wing(wing_angle_deg * 0.7 - 8, strike)
    fr = far.get_rect(center=(BCX - 9, BCY - 4))
    surf.blit(far, fr)

    # --- Dim violet body aura ---
    _glow_dot(surf, (BCX, BCY + 2), 20, ELECTRIC, layers=4)

    # --- Talons: charcoal claws over a cold violet glow circle ---
    _glow_dot(surf, (BCX - 2, BCY + 20), 7, ELECTRIC, layers=3)
    for tx in (BCX - 6, BCX - 1, BCX + 4):
        pygame.draw.line(surf, (44, 44, 54), (tx, BCY + 14), (tx, BCY + 22), 2)
        pygame.draw.line(surf, (28, 28, 38), (tx, BCY + 22), (tx - 2, BCY + 25), 2)

    # --- Body: deep indigo base with a lighter violet cap ---
    _aaellipse(surf, NIGHT_INDIGO, (BCX, BCY + 2), 16, 17)
    # Lighter violet cap (upper body catches the storm light).
    cap = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    _aaellipse(cap, VIOLET_SHADOW, (BCX, BCY - 3), 14, 11)
    surf.blit(cap, (0, 0))
    # Chest belly darker to keep the base heavy and brooding.
    _aaellipse(surf, NIGHT_INDIGO, (BCX - 1, BCY + 8), 11, 9)

    # --- Static lightning-scar veins branching across the chest ---
    _scar(surf, [(BCX - 8, BCY - 4), (BCX - 3, BCY + 1),
                 (BCX - 5, BCY + 5), (BCX + 1, BCY + 10)], flash)
    _scar(surf, [(BCX - 3, BCY + 1), (BCX + 4, BCY - 2),
                 (BCX + 3, BCY + 4), (BCX + 8, BCY + 3)], flash)
    _scar(surf, [(BCX + 4, BCY - 2), (BCX + 9, BCY - 6)], flash)

    # --- Head: sharp swept-back blade crest ---
    # Crest shards — thin polygons angled back and up from the crown.
    crest_col = VIOLET_SHADOW
    for (bx, by, tx, ty, w0) in ((HCX - 6, CROWN_Y + 4, HCX - 15, CROWN_Y - 6, 3),
                                 (HCX - 2, CROWN_Y + 2, HCX - 12, CROWN_Y - 10, 3),
                                 (HCX + 2, CROWN_Y + 2, HCX - 7, CROWN_Y - 12, 2)):
        pygame.draw.polygon(surf, crest_col, [
            (bx, by), (bx + w0, by + 1), (tx + 1, ty + 1), (tx, ty)])
    # Crest tip highlights — electric edges.
    pygame.draw.line(surf, ELECTRIC, (HCX - 6, CROWN_Y + 4), (HCX - 15, CROWN_Y - 6), 1)
    pygame.draw.line(surf, ELECTRIC, (HCX - 2, CROWN_Y + 2), (HCX - 12, CROWN_Y - 10), 1)

    # Head mass — dark indigo with a violet cap catch.
    _aaellipse(surf, NIGHT_INDIGO, (HCX, HCY), 11, 10)
    hcap = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    _aaellipse(hcap, VIOLET_SHADOW, (HCX + 1, HCY - 3), 9, 6)
    surf.blit(hcap, (0, 0))

    # --- Beak: sharp charcoal hook, predatory ---
    pygame.draw.polygon(surf, (40, 38, 52), [
        (HCX + 9, HCY - 1), (HCX + 17, HCY + 1), (HCX + 9, HCY + 5)])
    pygame.draw.polygon(surf, (26, 24, 36), [
        (HCX + 14, HCY + 1), (HCX + 17, HCY + 1), (HCX + 12, HCY + 5)])

    # --- Glowing violet eyes — the PRIMARY 40px tell, kept bright ---
    for ex, ey in ((HCX + 3, HCY - 1),):
        _glow_dot(surf, (ex, ey), 6, ELECTRIC, layers=3)
        pygame.draw.circle(surf, ELECTRIC, (ex, ey), 4)
        pygame.draw.circle(surf, SCAR_PALE, (ex, ey), 2)
        pygame.draw.circle(surf, (255, 255, 255), (ex - 1, ey - 1), 1)
    # A second smaller eye-glint hint (far eye) to sell two glowing eyes.
    _glow_dot(surf, (HCX - 4, HCY), 4, ELECTRIC, layers=2)
    pygame.draw.circle(surf, ELECTRIC, (HCX - 4, HCY), 2)
    pygame.draw.circle(surf, SCAR_PALE, (HCX - 4, HCY), 1)

    # --- Near wing (in front of body) ---
    near = _wing(wing_angle_deg, strike)
    nr = near.get_rect(center=(BCX - 3, BCY - 2))
    surf.blit(near, nr)

    return surf


_cache = {}


def build(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    angle = _WING_ANGLES[frame_idx % len(_WING_ANGLES)]
    key = (frame_idx % len(_WING_ANGLES), round(tilt_deg / 3) * 3)
    if key not in _cache:
        _cache[key] = pygame.transform.rotozoom(
            _add_outline(_build_frame(angle)), key[1], 1.0)
    return _cache[key]
