"""MORTIMER DEATHFLY (Design 4) — scratch fly candidate.

A gothic Halloween showpiece fly: a plump charcoal-plum barrel body carrying a
tiny bone-white death's-head skull on its thorax hump, crowned by two huge
bioluminescent yellow-green compound eyes that softly pulse across the flap
cycle. Spooky-cute, never gross. Lives or dies at 40px, so it leans on one
bold shape (the fat velvet barrel) + two high-contrast tells that survive the
downscale: the glowing green eyes (brightest) and the bone skull (a body mark).

The read this build defends: "fat black fly + spooky eyes" — NOT "grey wings +
floating eyes." So the barrel is the hero mass, painted in a fill that clears
the night sky on its own (charcoal-plum, not near-black) and ringed by a grey
rim-light that wraps the WHOLE lower barrel — the body must read as a solid
round mass even with the eye-glow switched off. The wings are pulled in behind
it as supporting span, never the anchor. Eyes sit centred as a matched pair on
the head; the skull rides UP on the thorax hump below them.

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
# Body base is charcoal-plum, NOT near-black: at 40px on a night sky #0A0A0E
# collapsed to a hole, so the barrel must carry its own value above background.
_VELVET   = (42, 38, 50)          # #2A2632 barrel base fill
_VELVET_D = (30, 27, 38)          # abdomen/thorax core shadow
_RIMLIGHT = (70, 66, 82)          # interior crown lift on the lit side
_RIMGREY  = (90, 90, 102)         # #5A5A66 rim-light wrapping the lower barrel
_BONE     = (230, 226, 214)       # #E6E2D6 eye speculars + wing leading edge
_SKULL    = (230, 226, 214)       # #E6E2D6 — bone-white hero skull (the tell)
_SKULL_D  = (150, 146, 138)       #   cranium shadow keeps it domed, not flat
_SOCKET   = (12, 10, 16)          # skull eye sockets / nasal / teeth
_EYE_CORE = (182, 255, 60)        # biolum hotspot
_EYE_MID  = (122, 176, 32)
_EYE_RIM  = (58, 90, 16)
_EYE_HOT  = (224, 255, 168)
_WING     = (60, 60, 72)          # smoky charcoal fan, dimmed so it recedes
_WING_VEIN = (28, 28, 36)
_LABELLUM = (58, 58, 46)          # #3A3A2E — dark sponge mouth pad
_SETAE    = (16, 14, 20)          # 3 black thorax bristles

# Head/eye anchor: a matched pair symmetric about the body centre BCX, sitting
# high so the fat barrel keeps all the room below it.
_EYE_L, _EYE_R = BCX - 7, BCX + 7  # (25, 39)
_EYE_Y = 30

# Eye pulse per flap frame — the getter feeds exact `_WING_ANGLES`, so keying on
# the rounded angle gives the brief's bright/medium/brightest/medium cadence
# (frame 0 bright, 1 medium, 2 brightest, 3 medium) rather than a monotone ramp.
_EYE_PULSE = {50: 0.82, 20: 0.55, -10: 1.00, -40: 0.62}


def _eye_bloom(surf, cx, cy, r, strength):
    """Soft additive green halo so the eyes glow against the night sky. The
    falloff is kept tight and steep so the house silhouette outline (alpha>8)
    hugs the lens instead of tracing a stray fringe-ring out past the body."""
    g = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    for rad in range(r, 0, -1):
        a = int(strength * 44 * (1.0 - rad / r) ** 1.6)
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


def _death_wing(angle_deg, sgn, scale=1.0):
    """Wide smoky charcoal fan — a clear bone leading edge + a full faint hem
    keep the up-and-back span legible at 40px, where a flat translucent shape
    used to vanish. `scale` pulls the pair IN so it never out-anchors the barrel,
    and `sgn` mirrors the blade so the pair spreads symmetrically."""
    w = pygame.Surface((48, 30), pygame.SRCALPHA)
    blade = [(6, 15), (18, 5), (34, 5), (44, 13), (40, 21), (22, 25), (10, 22)]
    pygame.draw.polygon(w, (*_WING, 170), blade)          # ~67% alpha fill
    pygame.draw.polygon(w, (*_BONE, 60), blade, 1)        # faint full hem
    # Bright 1px bone stroke on the leading/top edge — the wing's read at 40px.
    pygame.draw.lines(w, (*_BONE, 210), False,
                      [(6, 15), (18, 5), (34, 5), (44, 13)], 1)
    pygame.draw.line(w, _WING_VEIN, (10, 15), (38, 9), 1)
    pygame.draw.line(w, _WING_VEIN, (10, 17), (34, 20), 1)
    if scale != 1.0:
        sz = (max(1, int(48 * scale)), max(1, int(30 * scale)))
        w = pygame.transform.smoothscale(w, sz)
    out = pygame.transform.rotate(w, angle_deg)
    if sgn < 0:
        out = pygame.transform.flip(out, True, False)
    return out


def build_mortimer_deathfly(wing_angle_deg):
    surf = _new()
    f = (wing_angle_deg + 40) / 90.0
    strength = _EYE_PULSE.get(int(round(wing_angle_deg)),
                              0.55 + 0.45 * math.sin(f * math.pi))
    spread = (f - 0.5) * 18                # pulled-in symmetric flap swing

    # Eyes: hero glow underlay first so lids/facets sit crisply over the bloom.
    for ex in (_EYE_L, _EYE_R):
        _eye_bloom(surf, ex, _EYE_Y, 11, strength)

    # ── Wings: drawn FIRST so they sit behind the barrel, and pulled ~18% in
    #    so the fat body — not the fans — anchors the silhouette. ──
    _rot_blit(surf, _death_wing(18 + spread, -1, 0.82), (BCX - 6, 40))
    _rot_blit(surf, _death_wing(18 + spread, +1, 0.82), (BCX + 6, 40))

    # ── The velvet barrel — one continuous fat mass. The abdomen is the LARGEST
    #    single shape so it out-anchors the wings; the thorax hump merges up
    #    into the head. Painted charcoal-plum so it reads with the glow off. ──
    _aaellipse(surf, _VELVET_D, (BCX, 54), 16, 14)         # fat abdomen shadow
    _aaellipse(surf, _VELVET, (BCX, 53), 15, 13)           # fat abdomen (hero)
    _aaellipse(surf, _VELVET_D, (BCX, 42), 13, 11)         # thorax shadow
    _aaellipse(surf, _VELVET, (BCX, 41), 12, 10)           # thorax hump
    _aaellipse(surf, _VELVET, (BCX, 31), 15, 9)            # head brow mass

    # Rim-light carried ALL the way around the LOWER barrel (left→bottom→right),
    # so the round mass is defined by its own lit contour, never only by a halo.
    pygame.draw.arc(surf, _RIMGREY, (BCX - 15, 40, 30, 26),
                    math.radians(182), math.radians(358), 2)
    # Brighter lit crown wrapping the top-left of the thorax + interior lift.
    pygame.draw.arc(surf, _RIMGREY, (BCX - 12, 30, 24, 22),
                    math.radians(70), math.radians(200), 2)
    _aaellipse(surf, _RIMLIGHT, (BCX - 5, 38), 6, 4)

    # 3 stiff black setae flicking off the thorax shoulder — bristly tell.
    for x1, y1 in ((21, 31), (24, 29), (28, 32)):
        pygame.draw.line(surf, _SETAE, (BCX - 6, 38), (x1, y1), 1)

    # Dark sponge labellum tucked at the base of the face (the mouth), a shade
    # lighter than the barrel so the bilobed pad reads just under the eyes.
    _aaellipse(surf, _LABELLUM, (BCX, 37), 4, 2)
    pygame.draw.line(surf, _SOCKET, (BCX, 36), (BCX, 38), 1)

    # ── Death's-head skull — bone-white hero, riding UP on the thorax hump,
    #    clear of the eyes, so it reads as the legendary tiny-skull tell. ──
    _aaellipse(surf, _SKULL_D, (BCX, 44), 5, 6)            # cranium shadow
    _aaellipse(surf, _SKULL, (BCX, 43), 5, 5)              # domed cranium
    pygame.draw.circle(surf, _SOCKET, (BCX - 2, 42), 2)    # eye sockets
    pygame.draw.circle(surf, _SOCKET, (BCX + 2, 42), 2)
    pygame.draw.polygon(surf, _SOCKET,                     # nasal cavity
                        [(BCX - 1, 44), (BCX + 1, 44), (BCX, 46)])
    pygame.draw.polygon(surf, _SKULL, [(BCX - 3, 46), (BCX + 3, 46),  # jaw bar
                                       (BCX + 2, 48), (BCX - 2, 48)])
    for tx in (BCX - 1, BCX, BCX + 1):                    # teeth notches
        pygame.draw.line(surf, _SOCKET, (tx, 46), (tx, 48), 1)

    # ── Two huge bioluminescent compound eyes — the brightest thing here,
    #    centred as a matched pair on the head brow. ──
    for ex in (_EYE_L, _EYE_R):
        _compound_eye(surf, ex, _EYE_Y, strength)

    return surf


build = _make_prebuilt_skin(build_mortimer_deathfly)
