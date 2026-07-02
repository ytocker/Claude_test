"""MORTIMER DEATHFLY (Design 4) — scratch fly candidate.

A gothic Halloween showpiece fly: a plush velvet-black barrel body carrying a
pale death's-head-hawkmoth skull crest, topped by two huge bioluminescent
yellow-green compound eyes that softly pulse across the flap cycle. Spooky-cute,
never gross. Lives or dies at 40px, so it leans on one bold shape (the round
velvet barrel) + two high-contrast signatures that survive the downscale: the
glowing green eyes (brightest) and the bone skull marking (a body tell, dimmer).

Velvet-on-night can collapse to a hole, so the barrel is rescued three ways: a
baked dark-green outer halo rings the whole mass against ANY sky, a light-grey
rim wraps the lit top-left, and an interior rim-light lifts the crown — the
plump thorax+abdomen must still read as a solid round body at 40px.

Contract mirrors game/animal_skins.py so it lifts straight in later:
`build(frame_idx, tilt_deg) -> Surface` from `_make_prebuilt_skin`.
"""
import math

import pygame

from game.parrot import _WING_ANGLES, _aaellipse

# Local copies of the animal-skin canvas + factory so this scratch builder does
# not depend on tools/ import wiring — matches game/animal_skins.py values.
try:  # prefer the real helpers when importable
    from game.animal_skins import (
        _make_prebuilt_skin, _new, BCX, BCY, HCX, HCY, _rot_blit,
    )
except Exception:  # pragma: no cover - defensive fallback for scratch runs
    from game.parrot import SPRITE_W, _add_outline
    COMPOSITE_W, COMPOSITE_H, DY = SPRITE_W, 84, 12
    BCX, BCY = 32, 32 + DY
    HCX, HCY = 44, 22 + DY

    def _new():
        return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)

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


# ── palette ──────────────────────────────────────────────────────────────────
_VELVET   = (10, 10, 14)          # body core
_RIMLIGHT = (40, 40, 50)          # interior crown rim-light (lit side)
_RIMGREY  = (90, 90, 102)         # #5A5A66 lit-edge rim wrapping the top-left
_HALO     = (90, 122, 24, 102)    # #5A7A18 @ ~40% — baked dark-green outer glow
_BONE     = (232, 228, 216)       # eye speculars + wing leading-edge glow
_SKULL    = (190, 186, 176)       # #BEBAB0 — dimmed so the skull reads as a
_SKULL_D  = (150, 146, 138)       #   BODY marking, never a second face
_SOCKET   = (8, 8, 12)            # skull eye sockets / nasal / teeth
_EYE_CORE = (182, 255, 60)        # biolum hotspot
_EYE_MID  = (122, 176, 32)
_EYE_RIM  = (58, 90, 16)
_EYE_HOT  = (224, 255, 168)
_WING     = (62, 62, 74)          # #3E3E4A — lifted so the fans read on night
_WING_VEIN = (28, 28, 36)
_LABELLUM = (58, 58, 46)          # #3A3A2E — lighter-than-body mouth pad
_SETAE    = (74, 74, 86)          # bristles that catch the grey rim

# Eye pulse per flap frame — the getter feeds exact `_WING_ANGLES`, so keying on
# the rounded angle gives the brief's bright/medium/brightest/medium cadence
# (frame 0 bright, 1 medium, 2 brightest, 3 medium) rather than a monotone ramp.
_EYE_PULSE = {50: 0.82, 20: 0.55, -10: 1.00, -40: 0.62}


def _eye_bloom(surf, cx, cy, r, strength):
    """Soft additive green halo so the eyes glow against the night sky."""
    g = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    for rad in range(r, 0, -1):
        a = int(strength * 60 * (1.0 - rad / r))
        if a > 0:
            pygame.draw.circle(g, (120, 200, 40, a), (r, r), rad)
    surf.blit(g, (cx - r, cy - r), special_flags=pygame.BLEND_RGBA_ADD)


def _compound_eye(surf, cx, cy, strength):
    """A bulging biolum compound eye: dark rim → mid → bright pulsing core."""
    core = tuple(int(_EYE_RIM[i] + (_EYE_CORE[i] - _EYE_RIM[i]) * strength)
                 for i in range(3))
    hot = tuple(int(_EYE_MID[i] + (_EYE_HOT[i] - _EYE_MID[i]) * strength)
                for i in range(3))
    _aaellipse(surf, _EYE_RIM, (cx, cy), 8, 8)
    _aaellipse(surf, _EYE_MID, (cx, cy), 6, 6)
    _aaellipse(surf, core, (cx, cy - 1), 4, 4)
    _aaellipse(surf, hot, (cx - 1, cy - 2), 2, 2)
    # A darker facet arc on the lower rim keeps it reading as a domed lens.
    pygame.draw.arc(surf, _EYE_RIM, (cx - 8, cy - 8, 16, 16),
                    math.radians(200), math.radians(340), 2)


def _death_wing(angle_deg, sgn):
    """Wide smoky charcoal fan — a clear bone leading edge + a full faint hem
    keep the up-and-back span legible at 40px, where a flat translucent shape
    used to vanish. `sgn` mirrors the blade so the pair spreads symmetrically."""
    w = pygame.Surface((48, 30), pygame.SRCALPHA)
    blade = [(6, 15), (18, 5), (34, 5), (44, 13), (40, 21), (22, 25), (10, 22)]
    pygame.draw.polygon(w, (*_WING, 178), blade)          # ~70% alpha fill
    pygame.draw.polygon(w, (*_BONE, 70), blade, 1)        # faint full hem
    # Bright 1px bone stroke on the leading/top edge — the wing's read at 40px.
    pygame.draw.lines(w, (*_BONE, 220), False,
                      [(6, 15), (18, 5), (34, 5), (44, 13)], 1)
    pygame.draw.line(w, _WING_VEIN, (10, 15), (38, 9), 1)
    pygame.draw.line(w, _WING_VEIN, (10, 17), (34, 20), 1)
    out = pygame.transform.rotate(w, angle_deg)
    if sgn < 0:
        out = pygame.transform.flip(out, True, False)
    return out


def build_mortimer_deathfly(wing_angle_deg):
    surf = _new()
    f = (wing_angle_deg + 40) / 90.0
    strength = _EYE_PULSE.get(int(round(wing_angle_deg)),
                              0.55 + 0.45 * math.sin(f * math.pi))
    spread = (f - 0.5) * 22                # wings swing symmetrically w/ flap

    # Eyes: hero glow first so lids/facets sit crisply on top of the bloom.
    for ex in (38, 50):
        _eye_bloom(surf, ex, 31, 15, strength)

    # Wings spread behind the barrel for a menacing, moth-like span.
    _rot_blit(surf, _death_wing(20 + spread, -1), (28, 27))
    _rot_blit(surf, _death_wing(20 + spread, +1), (40, 27))

    # ── Baked dark-green outer halo: draw green mass 2px proud of every body
    #    ellipse, then paint velvet inside — the leftover ring anchors the
    #    round shape against ANY sky before the house outline even wraps it. ──
    _aaellipse(surf, _HALO, (44, 33), 12, 10)             # head halo
    _aaellipse(surf, _HALO, (33, 50), 14, 12)             # abdomen halo
    _aaellipse(surf, _HALO, (BCX, BCY), 14, 13)           # thorax halo

    # Dark head mass so the two compound eyes read as one bulging brow.
    _aaellipse(surf, _VELVET, (44, 33), 10, 8)

    # ── Velvet barrel body — plump thorax + a fatter abdomen bulging down and
    #    behind so the classic fat-fly proportion reads (~26×24px visible). ──
    _aaellipse(surf, _VELVET, (33, 50), 12, 11)           # fat abdomen
    _aaellipse(surf, _VELVET, (BCX, BCY), 12, 11)         # thorax
    # Interior rim-light lifts the lit crown out of the black core.
    _aaellipse(surf, _RIMLIGHT, (27, 40), 8, 5)
    # Light-grey lit-edge rim wrapping the top-left of the mass (the read that
    # keeps the barrel from collapsing to a black hole on a dark sky).
    pygame.draw.arc(surf, _RIMGREY, (BCX - 14, BCY - 13, 28, 26),
                    math.radians(95), math.radians(185), 2)

    # ── Death's-head skull crest — dimmed + slightly smaller than R1 so it
    #    reads as a thorax marking, not a rival face to the glowing eyes. ──
    _aaellipse(surf, _SKULL_D, (32, 42), 5, 6)            # cranium shadow
    _aaellipse(surf, _SKULL, (32, 41), 5, 5)              # domed cranium
    pygame.draw.circle(surf, _SOCKET, (30, 41), 2)        # eye sockets
    pygame.draw.circle(surf, _SOCKET, (34, 41), 2)
    pygame.draw.polygon(surf, _SOCKET,                    # nasal cavity
                        [(31, 43), (33, 43), (32, 45)])
    pygame.draw.polygon(surf, _SKULL, [(29, 45), (35, 45),  # jaw / chin bar
                                       (34, 47), (30, 47)])
    for tx in (31, 32, 33):                               # teeth notches
        pygame.draw.line(surf, _SOCKET, (tx, 45), (tx, 47), 1)

    # 3 stiff setae off the thorax hump — grey so they flick clear of the sky.
    for x0, y1 in ((22, 20), (25, 18), (29, 21)):
        pygame.draw.line(surf, _SETAE, (27, 34), (x0, y1), 1)

    # ── Two huge bioluminescent compound eyes — the brightest thing here ──
    for ex in (38, 50):
        _compound_eye(surf, ex, 31, strength)

    # Spongy labellum pad tucked under the face — a readable lighter nub.
    _aaellipse(surf, _LABELLUM, (46, 45), 3, 2)
    pygame.draw.line(surf, _SOCKET, (45, 45), (47, 45), 1)

    return surf


build = _make_prebuilt_skin(build_mortimer_deathfly)
