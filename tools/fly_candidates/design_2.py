"""BUZZ THE HOUSEFLY (Design 2) — scratch candidate for the ANIMALS fly skin.

The "fly everyone draws": two ENORMOUS glossy red compound eyes crowning the
silhouette as one big goggle mass, a plump light-grey barrel body tucked below,
and stubby CLEAR wings that sit as a soft translucent halo *behind* the eyes —
never a solid grey hood in front. All the contrast lives in the eyes (warm-red
domes + white catch-lights); the body/wings stay light so the eyes read as the
unmistakable hero at 40px. The mouth is a soft round sponge (labellum), never a
needle. Scratch only — not registered in BUILDERS; wrapped by the shared
prebuilt getter so tools/ninja_render can drive it exactly like a production
skin.
"""
import math

import pygame

try:
    from game.animal_skins import (
        _make_prebuilt_skin, _new, _flap, _rot_blit, BCX, BCY, HCX, HCY,
    )
except ImportError:  # pragma: no cover - inline fallback if API shifts
    from game.parrot import SPRITE_W, _WING_ANGLES, _add_outline
    COMPOSITE_W, COMPOSITE_H = SPRITE_W, 84
    BCX, BCY, HCX, HCY = 32, 44, 44, 34

    def _new():
        return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)

    def _flap(angle_deg):
        return (angle_deg + 40) / 90.0

    def _rot_blit(surf, wing, anchor):
        surf.blit(wing, wing.get_rect(center=anchor).topleft)

    def _make_prebuilt_skin(build_fn):
        state = {"frames": None, "rot": {}}

        def getter(frame_idx, tilt_deg):
            if state["frames"] is None:
                state["frames"] = [_add_outline(build_fn(a))
                                   for a in _WING_ANGLES]
            frames = state["frames"]
            frame_idx %= len(frames)
            key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
            s = state["rot"].get(key)
            if s is None:
                s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
                state["rot"][key] = s
            return s
        return getter

from game.parrot import _aaellipse


# ── palette ──────────────────────────────────────────────────────────────────
# Dominant is the light warm-neutral grey; the dark #6E6C6A is spent ONLY on a
# single thin lower-abdomen band so the eyes stay the strongest value contrast.
_BODY      = (154, 152, 150)        # #9A9896 dominant barrel grey
_BODY_H    = (182, 180, 178)        # top specular of the barrel
_BODY_MID  = (138, 136, 134)        # gentle lower shading (still light)
_BAND      = (110, 108, 106)        # #6E6C6A — reserved for one thin band
_RIM       = (128, 126, 124)        # soft belly rim (kept light)
_BRISTLE   = (92, 90, 88)           # short dark setae off the thorax hump
_EYE       = (178, 74, 58)          # #B24A3A warm red-brown compound dome
_EYE_D     = (134, 52, 40)          # eye rim / lower shading
_EYE_FACET = (206, 104, 86)         # lighter facet stipple
_EYE_PUPIL = (92, 34, 28)           # soft pupil hint
_CATCH     = (255, 255, 255)        # glossy catch-light — top contrast note
_SPONGE    = (199, 154, 110)        # #C79A6E labellum pad
_SPONGE_D  = (168, 124, 84)
_LEG       = (78, 76, 74)
_WING_FILL = (237, 239, 242)        # #EDEFF2 clear-wing membrane
_WING_VEIN = (176, 182, 194)
_WING_A    = 122                    # ~50% alpha so the sky reads through


def _lerp(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def _vgrad_ellipse(surf, cx, cy, rx, ry, top, bot):
    """Vertical top→bottom colour ramp clipped to an ellipse — sells the round
    barrel body reading as a lit dumpling rather than a flat disc."""
    for yy in range(-ry, ry + 1):
        frac = 1.0 - (yy / ry) ** 2
        if frac <= 0:
            continue
        half = rx * math.sqrt(frac)
        col = _lerp(top, bot, (yy + ry) / (2 * ry))
        pygame.draw.line(surf, col, (cx - half, cy + yy), (cx + half, cy + yy))


def _fly_wing(f, sgn):
    """A compact CLEAR wing, kept translucent + small so the pair reads as a
    soft halo *behind* the eyes rather than a grey hood in front. `f` (0=down,
    1=up) sweeps it up on the up-stroke; `sgn` splays far vs. near."""
    w = pygame.Surface((34, 22), pygame.SRCALPHA)
    # Tucked-in teardrop membrane (far edge pulled in ~20% vs. the R1 hood).
    pygame.draw.ellipse(w, (*_WING_FILL, _WING_A), (8, 4, 22, 15))
    pygame.draw.ellipse(w, (255, 255, 255, 60), (13, 6, 12, 8))       # sheen
    pygame.draw.ellipse(w, (*_WING_VEIN, 120), (8, 4, 22, 15), 1)     # edge
    pygame.draw.line(w, (*_WING_VEIN, 110), (13, 9), (29, 8), 1)      # vein
    ang = sgn * (24 + f * 34)                # up-swept on the up-stroke
    return pygame.transform.rotozoom(w, ang, 1.0)


def build_buzz_housefly(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)                # 0 wings down, 1 wings up

    # ── clear wings drawn FIRST so the eyes crown them: a translucent halo
    #    fanning up-back behind the head, never a mass in front of the face ──
    _rot_blit(surf, _fly_wing(f, +1), (36, 25))     # far wing (up-back-left)
    _rot_blit(surf, _fly_wing(f, -1), (50, 25))     # near wing (up-back-right)

    # ── plump light-grey barrel body tucked below/behind the eyes ──
    _aaellipse(surf, _RIM, (BCX + 1, BCY + 3), 14, 13)              # soft rim
    _vgrad_ellipse(surf, BCX, BCY + 1, 13, 12, _BODY_H, _BODY_MID)  # lit barrel
    # ONE thin dark abdominal band low on the belly — the only dark grey used.
    pygame.draw.arc(surf, _BAND, (BCX - 12, BCY + 5, 24, 12),
                    math.radians(205), math.radians(335), 2)
    # Top-left specular so the barrel reads glossy-round.
    _aaellipse(surf, _BODY_H, (BCX - 4, BCY - 5), 5, 3)

    # Thin dangling legs — kept as separate strokes so the barrel stays plump
    # (it must NOT taper straight into the legs).
    for lx, bend in ((BCX - 3, -3), (BCX + 2, 0), (BCX + 7, 3)):
        pygame.draw.lines(surf, _LEG, False,
                          [(lx, BCY + 11), (lx + bend, BCY + 16),
                           (lx + bend + 3, BCY + 19)], 1)

    # ── thorax top hump + a small bristle flick (hairy-fly tell) ──
    _aaellipse(surf, _BODY, (30, 32), 9, 7)
    for bx, by in ((24, 30), (27, 28), (30, 27)):
        pygame.draw.line(surf, _BRISTLE, (bx, by), (bx - 1, by - 4), 1)

    # ── light-grey head behind the eyes (keeps the face one bright mass) ──
    _aaellipse(surf, _BODY_MID, (HCX, HCY + 3), 12, 9)
    _vgrad_ellipse(surf, HCX, HCY + 2, 11, 8, _BODY_H, _BODY)

    # ═══ HERO: two ENORMOUS glossy compound eyes crowning the silhouette ═══
    # Full ~16px domes, nudged up/forward and nearly touching so the pair is
    # the widest bright element in the top half and eats 60%+ of the head.
    for ex in (37, 49):
        _aaellipse(surf, _EYE_D, (ex + 1, 32), 9, 9)                # rim shade
        _aaellipse(surf, _EYE, (ex, 31), 8, 8)                      # red dome
        for fx, fy in ((ex - 3, 33), (ex + 2, 34), (ex + 3, 29),
                       (ex - 1, 30)):
            pygame.draw.circle(surf, _EYE_FACET, (fx, fy), 1)       # facets
        pygame.draw.circle(surf, _EYE_PUPIL, (ex, 31), 2)          # pupil hint
        # BIG catch-light + a soft secondary = the strongest contrast on screen.
        _aaellipse(surf, _CATCH, (ex - 3, 28), 3, 2)
        pygame.draw.circle(surf, _CATCH, (ex + 3, 34), 1)
        pygame.draw.circle(surf, _EYE_D, (ex, 31), 8, 1)           # crisp rim

    # ── spongy labellum: a clear soft round pad directly below the eye pair ──
    _aaellipse(surf, _SPONGE_D, (46, 45), 4, 3)
    _aaellipse(surf, _SPONGE, (46, 44), 3, 3)
    pygame.draw.line(surf, _SPONGE_D, (44, 44), (48, 44), 1)       # centre seam

    return surf


build = _make_prebuilt_skin(build_buzz_housefly)
