"""BUZZ THE HOUSEFLY (Design 2) — scratch candidate for the ANIMALS fly skin.

The "fly everyone draws": two ENORMOUS glossy red compound eyes crowning the
silhouette, a plump light-grey barrel body tucked below, and a pair of SHORT
WIDE translucent wing-fans held up-and-back over the thorax so the silhouette
breaks above and behind the back on both sides. The wings are the "buzz": they
sweep visibly across the 4 flap poses so motion reads even at 40px. All the
value contrast lives in the eyes (warm-red domes + white catch-lights); the
wings stay a cool translucent grey-blue so they're unmistakably present yet
clearly secondary to the eyes. The mouth is a soft flat labellum pad, never a
needle or bill. Scratch only — not registered in BUILDERS; wrapped by the
shared prebuilt getter so tools/ninja_render can drive it like a production
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
_BRISTLE   = (86, 84, 82)           # short dark setae off the thorax hump
_EYE       = (178, 74, 58)          # #B24A3A warm red-brown compound dome
_EYE_D     = (134, 52, 40)          # eye rim / lower shading
_EYE_FACET = (206, 104, 86)         # lighter facet stipple
_EYE_PUPIL = (92, 34, 28)           # soft pupil hint
_CATCH     = (255, 255, 255)        # glossy catch-light — top contrast note
_SPONGE    = (212, 180, 138)        # #D4B48A light-tan labellum pad
_SPONGE_D  = (176, 146, 104)        # groove / underside of the pad
_LEG       = (78, 76, 74)
# Cool translucent grey-blue membrane. Alpha ~74% (was 48%) so the fans read
# clearly at 40px instead of dissolving into the sky and leaving owl-ear stubs.
_WING_FILL = (237, 239, 242)        # #EDEFF2 membrane
_WING_VEIN = (108, 120, 144)        # thick dark cool grey-blue vein
_WING_A    = 190                    # ~74% alpha — present, still see-through


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


def _fly_wing(f, base_deg):
    """A SHORT, WIDE rounded membrane fan with two thick dark veins. Kept
    translucent grey-blue so it sits behind the eyes as clear buzzing glass,
    never a solid hood. `f` (0 wings down/forward, 1 wings high/back) drives a
    wide 42° sweep so the flap reads as the fly's buzz; `base_deg` splays the
    far vs. near fan into a V opening up-and-back."""
    w = pygame.Surface((34, 24), pygame.SRCALPHA)
    # Fan lies along +x (root at left, wide tip at right); wider than tall.
    pygame.draw.ellipse(w, (*_WING_FILL, _WING_A), (4, 4, 28, 16))
    pygame.draw.ellipse(w, (206, 218, 238, 90), (10, 6, 15, 8))       # sheen
    pygame.draw.ellipse(w, (*_WING_VEIN, 150), (4, 4, 28, 16), 1)     # edge
    # Two THICK dark veins fanning root→tip — the housefly wing tell.
    pygame.draw.line(w, (*_WING_VEIN, 215), (6, 12), (30, 8), 2)
    pygame.draw.line(w, (*_WING_VEIN, 215), (6, 13), (29, 18), 2)
    # +90° points the fan straight up; larger sweeps it up-and-back (left).
    return pygame.transform.rotozoom(w, base_deg + f * 42, 1.0)


def build_buzz_housefly(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)                # 1 wings high/back, 0 down/forward

    # ── SHORT WIDE wing-fans FIRST so the eyes/body crown them: a translucent
    #    grey-blue V fanning up-and-back over the thorax, breaking the
    #    silhouette above and behind the back on both sides ──
    _rot_blit(surf, _fly_wing(f, 112), (29, 29))    # far fan (up-back-left)
    _rot_blit(surf, _fly_wing(f, 88), (36, 29))     # near fan (up, slight back)

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

    # ── clean rounded thorax hump + 3 sparse dark setae (hairy-fly tell) ──
    # A tight hump sitting low on the back, no grey blur bleeding up off the
    # head, so the crown reads as thorax bristles — never owl ear-tufts.
    _aaellipse(surf, _BODY, (30, 34), 8, 6)
    for bx, by in ((25, 30), (28, 29), (31, 29)):
        pygame.draw.line(surf, _BRISTLE, (bx, by), (bx - 2, by - 5), 1)

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

    # ── spongy labellum: a wide FLAT soft round pad below the eye pair, light
    #    tan with a faint central groove so it reads as a mouth sponge, never a
    #    pointed bill/diamond ──
    _aaellipse(surf, _SPONGE_D, (46, 48), 6, 4)
    _aaellipse(surf, _SPONGE, (46, 47), 5, 3)
    pygame.draw.line(surf, _SPONGE_D, (42, 47), (50, 47), 1)       # centre groove

    return surf


build = _make_prebuilt_skin(build_buzz_housefly)
