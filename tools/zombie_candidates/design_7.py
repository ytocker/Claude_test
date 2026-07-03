"""CHARRED EMBER REVENANT — zombie-parrot candidate 7 (archetype: burnt/ash).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_zombie`` is untouched. Exposes ``build(frame_idx, tilt_deg) -> Surface``
via store_skins._make_prebuilt_skin, matching the current-skin redraw idiom
(``_build_zombie_redraw``) — a full flat build per wing angle, outlined once.

Read strategy at 40px: the horror is pure VALUE. A near-black carbonised bird
cracked open by a few molten-orange lava seams — extreme dark/bright contrast
that survives on ANY sky, day or night, because near-black always fights the
sky and hot orange always fights the black. The tells are BIG and few (4–5 fat
ember cracks, one glowing chest core, a split hanging beak), never fine
hatching, so nothing muddies when the sprite shrinks. The single additive glow
core is the concept's beacon — the one point the eye lands on first.
"""
import math
import pygame

from game.store_skins import SPRITE_W, SPRITE_H, _aaellipse, _poly, _make_prebuilt_skin

# Carbonised palette: the whole bird is charcoal so the ember accents are the
# only chroma on it — maximum contrast, maximum "burnt thing still moving".
_CHAR    = (28, 26, 24)            # #1C1A18 near-black char body
_CRUST_H = (74, 67, 64)            # #4A4340 dark charcoal crust highlight
_CHAR_D  = (16, 15, 14)            # deepest carbon shadow / undershadow
_EMBER   = (255, 106, 30)          # #FF6A1E molten ember crack
_CORE    = (255, 194, 74)          # #FFC24A hot glowing core
_ASHCRUST = (112, 116, 122)        # #70747A cool-grey ash crust edge (rear only)
_EYE     = (180, 60, 20)           # #B43C14 dim ember-red dead pupil


def _crack(surf, p0, p1, jag):
    """One thick molten seam with a slight bend — a cooling-lava crack, not a
    straight line. ``jag`` offsets the midpoint sideways so each seam kinks.
    Drawn 3px so it survives the 40px shrink as a clear bright stroke."""
    mx = (p0[0] + p1[0]) // 2 + jag
    my = (p0[1] + p1[1]) // 2 - jag
    pygame.draw.lines(surf, _EMBER, False, [p0, (mx, my), p1], 3)


def _rev_wing(angle_deg):
    """A charred wing: near-black plate with a couple of molten ember seams
    torn across it so a crack tell survives even when the chest is occluded."""
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    pts = [(24, 24), (44, 13), (48, 28), (32, 42), (18, 36)]
    _poly(w, _CHAR, pts)
    _poly(w, _CHAR_D, [(24, 24), (32, 42), (18, 36)])
    # Charcoal crust catch-light along the leading edge.
    pygame.draw.line(w, _CRUST_H, (25, 24), (43, 15), 2)
    # Two ember seams cracking the wing plate.
    _crack(w, (30, 20), (41, 30), 2)
    _crack(w, (24, 30), (33, 39), -1)
    return pygame.transform.rotate(w, angle_deg)


def _glow_core(surf, cx, cy):
    """The concept's beacon: one hot core dot plus a soft additive halo at the
    chest crack junction — the single brightest point on the sprite. Additive
    blend so it blooms over the char instead of sitting as a flat disc."""
    halo = pygame.Surface((26, 26), pygame.SRCALPHA)
    pygame.draw.circle(halo, (255, 120, 30, 90), (13, 13), 12)
    pygame.draw.circle(halo, (255, 160, 50, 110), (13, 13), 7)
    surf.blit(halo, halo.get_rect(center=(cx, cy)).topleft,
              special_flags=pygame.BLEND_RGB_ADD)
    pygame.draw.circle(surf, _EMBER, (cx, cy), 6)
    pygame.draw.circle(surf, _CORE, (cx, cy), 4)
    pygame.draw.circle(surf, (255, 240, 200), (cx - 1, cy - 1), 1)


def _build(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # Flap-keyed ember breath: the cracks glow a touch hotter on the down-beat,
    # like a bellows fanning the coals — a subtle life sign on a dead thing.
    t = (wing_angle_deg + 40) / 90.0                 # 0 (down) .. 1 (up)
    breath = 1.0 - abs(t - 0.0)                       # hottest at the down-beat

    # Tail — charred wedges, each a shade of carbon so the fan reads by value.
    for i, c in enumerate([_CHAR_D, _CHAR, _CRUST_H]):
        pts = [(2 + i * 3, 27 + i * 2), (14 + i, 25 + i),
               (19 + i, 31 + i * 2), (6 + i * 3, 37 + i * 2)]
        _poly(surf, c, pts)
    # One ember line licking up a tail wedge so the burn wraps the whole bird.
    pygame.draw.line(surf, _EMBER, (5, 34), (12, 30), 2)

    # Body — carbonised mass: undershadow, main char, upper crust catch-light.
    _aaellipse(surf, _CHAR_D, (34, 35), 19, 14)
    _aaellipse(surf, _CHAR, (32, 32), 19, 14)
    _aaellipse(surf, _CRUST_H, (29, 27), 11, 5)
    # Cooled-ash dusting on the lower belly where the fire has died back.
    _aaellipse(surf, _ASH, (27, 40), 7, 3)

    # PRIMARY TELL — a few big molten seams cracking the chest open. Kept few
    # and fat so they read as lava fissures at 40px, not as noisy hatching.
    _crack(surf, (23, 26), (35, 38), 3)              # long diagonal chest split
    _crack(surf, (26, 34), (40, 30), -3)             # cross seam over the belly
    _crack(surf, (20, 33), (30, 43), 2)              # lower-belly fissure
    _crack(surf, (33, 24), (41, 34), -2)             # shoulder seam toward wing

    # The single glowing ember core at the chest crack junction — the beacon.
    _glow_core(surf, 30, 34)
    # Breath flicker: a second, smaller additive kiss that pulses with the flap
    # so the core visibly breathes without moving.
    if breath > 0.5:
        kiss = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(kiss, (255, 150, 40, 70), (6, 6), 5)
        surf.blit(kiss, kiss.get_rect(center=(30, 34)).topleft,
                  special_flags=pygame.BLEND_RGB_ADD)

    # Wing.
    wing = _rev_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # Head — charred skull, same carbon build as the body.
    _aaellipse(surf, _CHAR_D, (48, 23), 12, 11)
    _aaellipse(surf, _CHAR, (47, 21), 12, 11)
    _aaellipse(surf, _CRUST_H, (46, 16), 6, 3)
    # An ember seam crawling up the back of the skull.
    _crack(surf, (42, 24), (50, 15), 2)

    # Dead eye — one dim ember-red pinprick in a black socket, barely alive.
    pygame.draw.circle(surf, _CHAR_D, (50, 19), 4)   # deep black socket
    pygame.draw.circle(surf, _EYE, (50, 19), 2)      # dim ember pupil, no glint

    # Split / peeled beak — two charred halves hanging apart with a molten line
    # bleeding between them, a crisped open mouth.
    upper = [(55, 20), (61, 23), (58, 25), (53, 24)]
    lower = [(53, 26), (58, 27), (60, 29), (54, 29)]
    _poly(surf, _CHAR, upper)
    _poly(surf, _CHAR, lower)
    pygame.draw.polygon(surf, _CHAR_D, upper, 1)
    pygame.draw.polygon(surf, _CHAR_D, lower, 1)
    # The ember gap between the peeled halves — the hot mouth.
    pygame.draw.line(surf, _EMBER, (54, 25), (59, 26), 2)

    # Feet — brittle charred stubs.
    pygame.draw.line(surf, _CHAR_D, (28, 45), (26, 49), 2)
    pygame.draw.line(surf, _CHAR_D, (34, 45), (36, 49), 2)
    return surf


build = _make_prebuilt_skin(_build)
