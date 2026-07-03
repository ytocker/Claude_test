"""CHARRED EMBER REVENANT — zombie-parrot candidate 7 (archetype: burnt/ash).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_zombie`` is untouched. Exposes ``build(frame_idx, tilt_deg) -> Surface``
via store_skins._make_prebuilt_skin, matching the current-skin redraw idiom
(``_build_zombie_redraw``) — a full flat build per wing angle, outlined once.

Read strategy at 40px: the horror is pure VALUE. A near-black carbonised bird
whose whole shell is cracked open by thin molten seams that RADIATE from one
chest junction and wrap the entire body — shoulders, back, neck and skull —
so the tell is "burnt corpse" everywhere, never a single warm belly patch that
could read as an orange-bellied songbird. One isolated additive ember core at
the throat is the beacon the eye lands on first; everything around it stays
untouched near-black so the pinpoint pops. The burn also crosses the skull as
a fat ember fissure, so the head reads as charred too.
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
    """One thin molten seam with a slight bend — a cooling-lava crack, not a
    straight line. ``jag`` offsets the midpoint sideways so each seam kinks.
    Drawn 2px so many of them can wrap the body without pooling into a mass;
    the head fissure is drawn fatter on its own for the skull tell."""
    mx = (p0[0] + p1[0]) // 2 + jag
    my = (p0[1] + p1[1]) // 2 - jag
    pygame.draw.lines(surf, _EMBER, False, [p0, (mx, my), p1], 2)


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
    """The concept's beacon: one hot core dot plus a TIGHT additive halo at the
    throat crack junction — the single brightest point on the sprite, kept
    small so the untouched near-black around it makes it read as one isolated
    pinpoint rather than a warm wash. Additive so it blooms over the char."""
    halo = pygame.Surface((14, 14), pygame.SRCALPHA)
    pygame.draw.circle(halo, (255, 120, 30, 95), (7, 7), 7)
    pygame.draw.circle(halo, (255, 160, 50, 120), (7, 7), 4)
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
    # A thin cool-grey ash crust edge on the LOWER BACK only — kept far from the
    # throat core so it never desaturates the char-vs-ember contrast zone.
    pygame.draw.line(surf, _ASHCRUST, (17, 38), (22, 41), 1)

    # PRIMARY TELL — thin molten seams RADIATING from one chest junction across
    # the whole carbon shell. Two climb onto the shoulder/back, one runs up the
    # neck toward the skull, and the rest fan down and out — so the burn wraps
    # the entire body instead of pooling into one warm belly crescent.
    JX, JY = 33, 30
    _crack(surf, (JX, JY), (22, 18), 2)              # up-left onto the back
    _crack(surf, (JX, JY), (29, 16), -2)             # up onto the shoulder/nape
    _crack(surf, (JX, JY), (41, 22), -2)             # up the neck toward the head
    _crack(surf, (JX, JY), (24, 41), 3)              # down the flank
    _crack(surf, (JX, JY), (44, 34), -2)             # out toward the far shoulder
    _crack(surf, (JX, JY), (30, 44), -2)             # short lower-belly fork

    # Wing — drawn before the core so the beacon is never occluded.
    wing = _rev_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # The single glowing ember core at the throat crack junction — the beacon,
    # laid over the wing so it always reads as the brightest isolated pinpoint.
    _glow_core(surf, JX, JY)
    # Breath flicker: a second, smaller additive kiss that pulses with the flap
    # so the core visibly breathes without moving.
    if breath > 0.5:
        kiss = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(kiss, (255, 150, 40, 70), (6, 6), 5)
        surf.blit(kiss, kiss.get_rect(center=(JX, JY)).topleft,
                  special_flags=pygame.BLEND_RGB_ADD)

    # Head — charred skull, same carbon build as the body.
    _aaellipse(surf, _CHAR_D, (48, 23), 12, 11)
    _aaellipse(surf, _CHAR, (47, 21), 12, 11)
    _aaellipse(surf, _CRUST_H, (46, 16), 6, 3)
    # SKULL FISSURE — a fat 3px ember crack splitting the crown from nape to
    # brow, so the head reads as burnt too and the neck seam below flows into
    # it: the char wraps continuously from body to skull.
    pygame.draw.lines(surf, _EMBER, False,
                      [(42, 25), (47, 17), (52, 14)], 3)

    # Dead eye — one dim ember-red pinprick in a black socket, barely alive.
    pygame.draw.circle(surf, _CHAR_D, (50, 19), 4)   # deep black socket
    pygame.draw.circle(surf, _EYE, (50, 19), 2)      # dim ember pupil, no glint

    # Beak — a solid charred wedge with a single ember line for the crisped
    # mouth. Kept simple so it stays legible instead of dissolving at 40px.
    beak = [(55, 20), (62, 24), (58, 28), (53, 25)]
    _poly(surf, _CHAR, beak)
    pygame.draw.polygon(surf, _CHAR_D, beak, 1)
    pygame.draw.line(surf, _EMBER, (54, 24), (60, 25), 2)

    # Feet — brittle charred stubs.
    pygame.draw.line(surf, _CHAR_D, (28, 45), (26, 49), 2)
    pygame.draw.line(surf, _CHAR_D, (34, 45), (36, 49), 2)
    return surf


build = _make_prebuilt_skin(_build)
