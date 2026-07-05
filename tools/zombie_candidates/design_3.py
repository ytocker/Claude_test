"""VOODOO HEX BIRD — zombie parrot candidate (Design 3, scratch).

A cursed, stitched-together conjure-bird: two bold cross-stitches lash the
head/neck seam, a ragged burlap drape hangs off the BACK shoulder and breaks
the silhouette, one eye is sewn shut while the other blazes an unnatural
purple, a voodoo pin is driven through the exposed chest, and a persistent
sickly-green rim halo traces the whole body so it reads as legendary-cursed
on any sky.

The horror is asymmetry — a live blazing eye beside a dead sewn one — plus the
"reassembled corpse" read of oversized X-stitches and a stitched torso seam,
far heavier than the timid seam ticks on the friendly zombie. Scratch explorer
only — NOT registered in ``store_skins.BUILDERS``; exposes
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
# Dulled, desaturated cursed sacking — dark enough that it stops competing with
# the blazing eye and reads as a rotted rag rather than a clean beige box.
BURLAP   = (150, 120, 80)
BURLAP_D = (110, 88, 58)
BURLAP_H = (176, 146, 104)
STITCH   = (17, 17, 17)
SEAM     = (45, 58, 42)          # exposed stitched-torso seam (undead tell)
HEX      = (124, 255, 138)       # sickly-green hex aura + rim halo
CURSED   = (178, 75, 255)        # blazing sewn-open eye / pin bead
CURSED_H = (224, 178, 255)
BONE     = (224, 214, 188)       # voodoo-pin shaft
WING     = (78, 96, 74)
WING_D   = (50, 64, 48)
BEAK     = (168, 142, 92)        # dull, no longer glossy-live


def _big_x(surf, cx, cy, r):
    """One coarse repair X: two thick dark strokes, no knot beads — a pair of
    these read cleanly as 'lashed shut with rope' where cramped triples with
    r=1 beads collapse into a muddy stain at gameplay size."""
    pygame.draw.line(surf, STITCH, (cx - r, cy - r), (cx + r, cy + r), 2)
    pygame.draw.line(surf, STITCH, (cx - r, cy + r), (cx + r, cy - r), 2)


def _hex_aura(surf, cx, cy, radius):
    """Soft additive green bloom. BLEND_RGB_ADD stacks scaled-RGB fills so the
    glow blooms brightest at the core and fades cleanly to sky with no hard
    alpha edge. It is a bonus layer only — invisible over bright blue sky — so
    the persistent rim halo in ``build`` is what actually carries the tell."""
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
    """Flat composite for one wing angle (no aura/halo — those are composited
    behind the outlined sprite by ``build`` so the glow never gets a hard
    outline)."""
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

    # Ragged burlap drape hung off the BACK/tail shoulder — a narrow torn
    # triangle whose frayed hem pokes past the body ellipse so it breaks the
    # round silhouette into something cursed and asymmetric, not a beige box.
    rag = [(12, 28), (24, 26), (20, 44), (9, 40)]
    pygame.draw.polygon(surf, BURLAP, rag)
    # Inner fold sits in shadow so the drape reads as hanging cloth with depth.
    pygame.draw.polygon(surf, BURLAP_D, [(12, 28), (16, 27), (18, 43), (9, 40)])
    pygame.draw.line(surf, BURLAP_H, (13, 29), (23, 27), 1)
    # Irregular torn hem — teeth 2-3px deep, uneven, poking below the body edge.
    hem = [(9, 40), (11, 46), (13, 41), (15, 47),
           (17, 42), (18, 45), (20, 44)]
    pygame.draw.polygon(surf, BURLAP_D, hem)
    # Two fray threads through the weave.
    for fx in (14, 18):
        pygame.draw.line(surf, BURLAP_D, (fx, 29), (fx, 42), 1)

    # Wing.
    wing = _voodoo_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # Exposed stitched-torso seam — short darker-green ties across the belly
    # sell a body cut open and sewn back together (the bodily undead tell).
    for sy in (36, 40, 44):
        pygame.draw.line(surf, SEAM, (24, sy), (34, sy), 1)
    for sx in range(25, 34, 3):
        pygame.draw.line(surf, SEAM, (sx, 34), (sx, 46), 1)

    # Voodoo-doll pin driven through the now-exposed chest — bone shaft angled
    # across the body with an oversized cursed bead head (r3) so the "wounded
    # doll" wound reads at gameplay size now the rag no longer hides it.
    pygame.draw.line(surf, STITCH, (23, 42), (35, 32), 2)
    pygame.draw.line(surf, BONE, (23, 42), (35, 32), 1)
    pygame.draw.circle(surf, STITCH, (36, 31), 4)
    pygame.draw.circle(surf, CURSED, (36, 31), 3)
    pygame.draw.circle(surf, CURSED_H, (35, 30), 1)

    # Head.
    _aaellipse(surf, BODY_D, (48, 23), 12, 11)
    _aaellipse(surf, BODY, (47, 21), 12, 11)
    _aaellipse(surf, BODY_H, (46, 16), 7, 3)

    # Two bold, well-spaced repair X's — crown and neck — lashing the head back
    # on. Separation is what makes them read as stitches instead of a stain.
    _big_x(surf, 44, 12, 3)
    _big_x(surf, 37, 28, 3)

    # Sewn-shut dead eye (the far eye) — a dark horizontal slit crossed by three
    # short vertical stitches; the missing eye is half the asymmetry horror.
    pygame.draw.line(surf, STITCH, (41, 21), (47, 21), 2)
    for vx in (42, 44, 46):
        pygame.draw.line(surf, STITCH, (vx, 19), (vx, 23), 1)

    # Cursed blazing eye (the near eye) — the best tell, so it truly blazes:
    # a fat purple orb (r4) with a self-lit bloom and a 1px hotspot.
    _hex_aura(surf, 50, 19, 7)
    pygame.draw.circle(surf, STITCH, (50, 19), 5)
    pygame.draw.circle(surf, CURSED, (50, 19), 4)
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

# Cache the halo+aura-behind composite per (frame, tilt) so the cursed edge
# tracks the rotated sprite without re-deriving the silhouette every draw.
_aura_cache: dict = {}


def _rim_halo(core, alpha=160):
    """A persistent 2px green stroke traced around the sprite's silhouette,
    drawn on a normal-blend layer (NOT additive) so the cursed edge survives
    over bright blue sky where the additive bloom washes out to nothing. Built
    by unioning the alpha mask blitted at 2px offsets in all eight directions."""
    mask = pygame.mask.from_surface(core)
    sil = mask.to_surface(setcolor=(HEX[0], HEX[1], HEX[2], alpha),
                          unsetcolor=(0, 0, 0, 0))
    cw, ch = core.get_size()
    ring = pygame.Surface((cw + 4, ch + 4), pygame.SRCALPHA)
    for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2),
                   (2, 2), (-2, 2), (2, -2), (-2, -2)):
        ring.blit(sil, (2 + dx, 2 + dy))
    return ring


def build(frame_idx, tilt_deg):
    core = _getter(frame_idx, tilt_deg)
    key = (frame_idx % 4, int(round(tilt_deg / 3.0)) * 3)
    out = _aura_cache.get(key)
    if out is None:
        pad = 16
        cw, ch = core.get_size()
        out = pygame.Surface((cw + pad * 2, ch + pad * 2), pygame.SRCALPHA)
        # Soft additive bloom first (bonus layer), then the persistent rim halo
        # that carries the tell on any background, then the outlined bird.
        _hex_aura(out, out.get_width() // 2, out.get_height() // 2 + 4,
                  max(cw, ch) // 2 + 6)
        ring = _rim_halo(core)
        out.blit(ring, (pad - 2, pad - 2))
        out.blit(core, (pad, pad))
        _aura_cache[key] = out
    return out
