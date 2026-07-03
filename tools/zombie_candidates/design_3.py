"""VOODOO HEX BIRD — zombie parrot candidate (Design 3, scratch).

A cursed, stitched-together conjure-bird: coarse cross-stitches lash the
head/neck seam, a torn burlap-sack rag hangs off one shoulder, one eye is
sewn shut while the other blazes an unnatural purple, and a sickly-green
hex halo rims the whole body so it reads as legendary-cursed at a glance.

The horror is asymmetry — a live blazing eye beside a dead sewn one — plus
the "repaired with rope" read of oversized X-stitches, far heavier than the
timid seam ticks on the friendly zombie. Scratch explorer only — NOT
registered in ``store_skins.BUILDERS``; exposes
``build(frame_idx, tilt_deg) -> Surface``.
"""
from __future__ import annotations

import pygame

from game.parrot import SPRITE_W, SPRITE_H, _aaellipse
from game.store_skins import _make_prebuilt_skin

# Mossy-corpse body: desaturated enough to feel dead, so the cursed-purple eye
# and green hex glow are the only saturated notes and own the read.
BODY     = (92, 110, 87)
BODY_D   = (58, 72, 55)
BODY_H   = (124, 142, 116)
BELLY    = (150, 164, 134)
OUTLINE  = (32, 38, 30)
BURLAP   = (183, 154, 107)
BURLAP_D = (138, 112, 74)
BURLAP_H = (206, 182, 140)
STITCH   = (17, 17, 17)
HEX      = (124, 255, 138)      # sickly-green hex aura
CURSED   = (178, 75, 255)       # blazing sewn-open eye
CURSED_H = (224, 178, 255)
BONE     = (224, 214, 188)      # voodoo-pin shaft + needle heads
WING     = (78, 96, 74)
WING_D   = (50, 64, 48)
BEAK     = (168, 142, 92)       # dull, no longer glossy-live


def _big_x(surf, cx, cy, r):
    """One coarse repair X: two thick dark strokes with a knot bead at each of
    the four tips, so the 'lashed shut with rope' read survives the shrink that
    erases 1px seam ticks."""
    pygame.draw.line(surf, STITCH, (cx - r, cy - r), (cx + r, cy + r), 2)
    pygame.draw.line(surf, STITCH, (cx - r, cy + r), (cx + r, cy - r), 2)
    for ex, ey in ((cx - r, cy - r), (cx + r, cy + r),
                   (cx - r, cy + r), (cx + r, cy - r)):
        pygame.draw.circle(surf, STITCH, (ex, ey), 1)


def _hex_aura(surf, cx, cy, radius):
    """Soft additive green halo. BLEND_RGB_ADD stacks scaled-RGB fills so the
    glow blooms brightest at the core and fades cleanly to sky with no hard
    alpha edge — the legendary-rarity tell, rendered behind the whole bird."""
    d = radius * 2
    g = pygame.Surface((d, d), pygame.SRCALPHA)
    for f, s in ((1.0, 0.16), (0.80, 0.22), (0.60, 0.30),
                 (0.42, 0.40), (0.26, 0.52)):
        c = (int(HEX[0] * s), int(HEX[1] * s), int(HEX[2] * s))
        pygame.draw.circle(g, c, (radius, radius), int(radius * f))
    surf.blit(g, (cx - radius, cy - radius), special_flags=pygame.BLEND_RGB_ADD)


def _voodoo_wing(angle_deg):
    """Corpse-green wing, kept as its own surface so it rotates with the flap.
    Held dark and matte so it doesn't fight the burlap and cursed eye."""
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    pts = [(24, 24), (44, 13), (48, 28), (32, 42), (18, 36)]
    pygame.draw.polygon(w, WING, pts)
    pygame.draw.polygon(w, WING_D, [(24, 24), (32, 42), (18, 36)])
    pygame.draw.line(w, WING_D, (26, 25), (42, 18), 2)
    pygame.draw.line(w, BODY_H, (25, 25), (40, 16), 1)
    return pygame.transform.rotate(w, angle_deg)


def _build_voodoo(wing_angle_deg):
    """Flat composite for one wing angle (no aura — that is composited behind
    the outlined sprite by ``build`` so the glow never gets a hard outline)."""
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # Tail — corpse-green wedges.
    for i, c in enumerate([BODY_D, BODY, BODY_H, BELLY]):
        pts = [(2 + i * 3, 26 + i * 2), (14 + i, 24 + i),
               (20 + i, 30 + i * 2), (6 + i * 3, 36 + i * 2)]
        pygame.draw.polygon(surf, c, pts)

    # Body.
    _aaellipse(surf, BODY_D, (34, 35), 19, 14)
    _aaellipse(surf, BODY, (32, 32), 19, 14)
    _aaellipse(surf, BODY_H, (30, 29), 13, 8)
    _aaellipse(surf, BELLY, (28, 38), 12, 6)

    # Voodoo-doll pin driven through the chest — bone shaft angled across the
    # body with a bright bead head, so the "wounded doll" read lands even small.
    pygame.draw.line(surf, STITCH, (21, 41), (33, 31), 2)
    pygame.draw.line(surf, BONE, (21, 41), (33, 31), 1)
    pygame.draw.circle(surf, STITCH, (34, 30), 3)
    pygame.draw.circle(surf, CURSED, (34, 30), 2)
    pygame.draw.circle(surf, CURSED_H, (33, 29), 1)

    # Wing.
    wing = _voodoo_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # Burlap rag hung off the shoulder — a torn tan drape over the lower front,
    # sitting on top of the wing so it reads as loose cloth, not plumage. A
    # saw-tooth lower hem + two vertical fray lines sell the ripped sacking.
    rag = [(17, 30), (31, 27), (33, 40), (16, 43)]
    pygame.draw.polygon(surf, BURLAP, rag)
    pygame.draw.polygon(surf, BURLAP_D, [(17, 30), (16, 43), (23, 42), (22, 31)])
    pygame.draw.line(surf, BURLAP_H, (19, 31), (30, 29), 1)
    # Saw-tooth ripped hem.
    hem = [(16, 43), (19, 40), (21, 44), (24, 40),
           (27, 44), (30, 40), (33, 43), (33, 40), (16, 40)]
    pygame.draw.polygon(surf, BURLAP_D, hem)
    # Two vertical fray lines through the weave.
    for fx in (22, 27):
        pygame.draw.line(surf, BURLAP_D, (fx, 30), (fx, 41), 1)

    # Head.
    _aaellipse(surf, BODY_D, (48, 23), 12, 11)
    _aaellipse(surf, BODY, (47, 21), 12, 11)
    _aaellipse(surf, BODY_H, (46, 16), 7, 3)

    # Coarse cross-stitches lashing the head/neck seam — the hero repair note,
    # three heavy X's stepping down from the crown into the neck.
    _big_x(surf, 42, 14, 3)
    _big_x(surf, 40, 22, 3)
    _big_x(surf, 39, 30, 3)

    # Sewn-shut dead eye (the far eye) — a dark horizontal slit crossed by three
    # short vertical stitches; the missing eye is half the asymmetry horror.
    pygame.draw.line(surf, STITCH, (41, 21), (47, 21), 2)
    for vx in (42, 44, 46):
        pygame.draw.line(surf, STITCH, (vx, 19), (vx, 23), 1)

    # Cursed blazing eye (the near eye) — a hot purple orb with a self-lit
    # bloom, the other half of the asymmetry and the single brightest note.
    _hex_aura(surf, 50, 19, 6)
    pygame.draw.circle(surf, STITCH, (50, 19), 4)
    pygame.draw.circle(surf, CURSED, (50, 19), 3)
    pygame.draw.circle(surf, CURSED_H, (49, 18), 1)

    # Beak — dull horn, faintly agape.
    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    pygame.draw.polygon(surf, BEAK, beak_pts)
    pygame.draw.polygon(surf, STITCH, beak_pts, 1)
    pygame.draw.line(surf, STITCH, (53, 25), (59, 25), 1)

    # Feet — slack, sickly.
    pygame.draw.line(surf, BODY_D, (28, 45), (26, 49), 2)
    pygame.draw.line(surf, BODY_D, (34, 45), (36, 49), 2)
    return surf


_getter = _make_prebuilt_skin(_build_voodoo)

# Cache the aura-behind composite per (frame, tilt) so the halo tracks the
# rotated sprite without re-blitting every draw.
_aura_cache: dict = {}


def build(frame_idx, tilt_deg):
    core = _getter(frame_idx, tilt_deg)
    key = (frame_idx % 4, int(round(tilt_deg / 3.0)) * 3)
    out = _aura_cache.get(key)
    if out is None:
        pad = 16
        cw, ch = core.get_size()
        out = pygame.Surface((cw + pad * 2, ch + pad * 2), pygame.SRCALPHA)
        # Aura first, centred on the body mass, then the outlined bird on top.
        _hex_aura(out, out.get_width() // 2, out.get_height() // 2 + 4,
                  max(cw, ch) // 2 + 6)
        out.blit(core, (pad, pad))
        _aura_cache[key] = out
    return out
