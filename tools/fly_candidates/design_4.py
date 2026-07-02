"""MORTIMER DEATHFLY (Design 4) — scratch fly candidate.

A gothic Halloween showpiece fly: a plush pitch-black barrel body carrying a
pale death's-head-hawkmoth skull crest, topped by two huge bioluminescent
yellow-green compound eyes that softly pulse across the flap cycle. Spooky-cute,
never gross. Lives or dies at 40px, so it leans on one bold shape (the round
velvet barrel) + two high-contrast signatures that survive the downscale: the
bone-white skull and the glowing green eyes.

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
_RIMLIGHT = (30, 30, 38)          # body top rim-light
_RIMGREY  = (86, 86, 100)         # soft grey top rim-arc so it isn't a blob
_BONE     = (232, 228, 216)       # skull + wing edge glow
_BONE_D   = (188, 184, 170)
_SOCKET   = (8, 8, 12)            # skull eye sockets / setae
_EYE_CORE = (182, 255, 60)        # biolum hotspot
_EYE_MID  = (122, 176, 32)
_EYE_RIM  = (58, 90, 16)
_EYE_HOT  = (224, 255, 168)
_WING     = (42, 42, 50)
_WING_VEIN = (20, 20, 26)
_LABELLUM = (21, 21, 14)

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
    """Wide, smoky charcoal rounded wing — translucent, bone edge glow, 2 veins.
    `sgn` mirrors the blade so the pair spreads symmetrically off the thorax."""
    w = pygame.Surface((48, 30), pygame.SRCALPHA)
    blade = [(6, 15), (18, 5), (34, 5), (44, 13), (40, 21), (22, 25), (10, 22)]
    pygame.draw.polygon(w, (*_WING, 140), blade)          # ~55% alpha
    pygame.draw.polygon(w, (*_BONE, 90), blade, 1)        # faint bone hem
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
    _rot_blit(surf, _death_wing(20 + spread, -1), (28, 26))
    _rot_blit(surf, _death_wing(20 + spread, +1), (40, 26))

    # Dark head mass so the two compound eyes read as one bulging brow.
    _aaellipse(surf, _VELVET, (HCX, HCY - 1), 10, 8)

    # ── Velvet black barrel body — plump, not elongated ──
    _aaellipse(surf, _VELVET, (BCX, BCY + 1), 13, 12)
    _aaellipse(surf, _RIMLIGHT, (BCX - 1, BCY - 3), 10, 6)
    pygame.draw.arc(surf, _RIMGREY, (BCX - 12, BCY - 11, 24, 22),
                    math.radians(25), math.radians(160), 2)

    # ── Death's-head skull crest on the thorax (bold + simple) ──
    _aaellipse(surf, _BONE_D, (32, 41), 7, 6)             # cranium shadow
    _aaellipse(surf, _BONE, (32, 40), 6, 5)               # domed cranium
    pygame.draw.circle(surf, _SOCKET, (29, 40), 3)        # eye sockets
    pygame.draw.circle(surf, _SOCKET, (35, 40), 3)
    pygame.draw.polygon(surf, _SOCKET,                    # nasal cavity
                        [(31, 43), (33, 43), (32, 46)])
    pygame.draw.polygon(surf, _BONE, [(28, 45), (36, 45),  # jaw / chin bar
                                      (35, 48), (29, 48)])
    for tx in (30, 32, 34):                               # teeth notches
        pygame.draw.line(surf, _SOCKET, (tx, 45), (tx, 48), 1)

    # 3 stiff black setae/bristles off the thorax top — spidery, slightly long.
    for x0, y1 in ((23, 18), (26, 16), (29, 19)):
        pygame.draw.line(surf, _SOCKET, (26, 31), (x0, y1), 1)

    # ── Two huge bioluminescent compound eyes ──
    for ex in (38, 50):
        _compound_eye(surf, ex, 31, strength)

    # Dark spongy labellum tucked under the head front (a pad, not a needle).
    _aaellipse(surf, _LABELLUM, (45, 46), 3, 2)
    pygame.draw.line(surf, _SOCKET, (44, 46), (46, 46), 1)

    return surf


build = _make_prebuilt_skin(build_mortimer_deathfly)
