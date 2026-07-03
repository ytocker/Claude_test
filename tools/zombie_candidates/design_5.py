"""BLOATED GAS-BAG — zombie-parrot candidate 5 (archetype: bloated).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_zombie`` is untouched. Exposes ``build(frame_idx, tilt_deg) -> Surface``
via store_skins._make_prebuilt_skin, matching the current-skin redraw idiom
(``_build_zombie_redraw``) — a full flat build per wing angle, outlined once.

Read strategy at 40px: this is the ONLY concept that changes the body SHAPE.
The silhouette itself carries the horror — a grotesquely over-round parrot
whose belly has ballooned ~1.3x, drum-tight and shiny, straining open along
two pressure seams. The big high-contrast tells (round bloat + maroon gut
splits + sickly-yellow blister cluster + one eye swallowed by swollen flesh)
survive the shrink because none of them are fine detail; each is a filled
block of value that fights the sky. The flap keys a subtle vertical squash so
the gas-bag jiggles and the ooze drips sag lower on the down-beat.
"""
import math
import pygame

from game.store_skins import SPRITE_W, SPRITE_H, _aaellipse, _poly, _make_prebuilt_skin

# Jaundiced-green corpse body with a taut, lighter sheen for the drum-tight
# skin; the hot accents are the sickly-yellow blisters and the maroon gut.
_BODY     = (143, 160, 106)        # #8FA06A jaundiced green
_BODY_D   = (108, 124, 74)         # bloat underside shadow
_BODY_H   = (183, 196, 140)        # taut-skin sheen highlight
_BELLY    = (198, 206, 150)        # over-stretched belly, palest
_OUTLINE  = (36, 43, 27)           # #242B1B internal linework
_BLISTER  = (216, 214, 106)        # #D8D66A festering methane boil
_BLIST_D  = (150, 140, 60)         # blister rim, pressurised edge
_GUT      = (90, 30, 34)           # #5A1E22 split/gut, deep maroon
_GUT_D    = (58, 18, 22)           # gut depth
_OOZE     = (110, 122, 53)         # #6E7A35 sluggish greenish-brown drip
_OOZE_D   = (84, 94, 40)
_WING     = (120, 138, 84)         # wing sits a touch darker than the belly
_WING_D   = (86, 102, 58)
_BEAK     = (196, 176, 120)        # sickly desaturated horn (not fresh yellow)


def _gas_wing(angle_deg):
    """A heavy, slightly swollen wing in the corpse-green range; kept simple so
    the flap reads as a laboured, gas-heavy beat rather than a clean stroke."""
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    pts = [(24, 24), (44, 14), (48, 29), (33, 42), (18, 35)]
    _poly(w, _WING, pts)
    _poly(w, _WING_D, [(24, 24), (33, 42), (18, 35)])
    pygame.draw.line(w, _WING_D, (26, 25), (42, 18), 2)
    pygame.draw.line(w, _BODY_H, (25, 25), (41, 16), 1)
    # A lone blister riding the wing so the tell survives even when the belly is
    # partly hidden behind the wing at some poses.
    pygame.draw.circle(w, _BLIST_D, (30, 30), 3)
    pygame.draw.circle(w, _BLISTER, (30, 30), 2)
    pygame.draw.circle(w, (245, 245, 220), (29, 29), 1)
    return pygame.transform.rotate(w, angle_deg)


def _blister(surf, cx, cy, r):
    """A raised festering boil: dark pressurised rim, sickly-yellow dome, tiny
    specular pin — a pressurised methane bubble read as a lit sphere."""
    pygame.draw.circle(surf, _BLIST_D, (cx, cy), r)
    pygame.draw.circle(surf, _BLISTER, (cx, cy), max(1, r - 1))
    pygame.draw.circle(surf, (247, 246, 218), (cx - 1, cy - 1), 1)


def _split(surf, cx, top, bot, drip):
    """A vertical pressure seam torn open: a maroon gut lens beneath, framed by
    two dark straining skin lips, with a heavy ooze drip sagging from the base.
    ``drip`` (0..1, keyed to the flap) elongates the drip on the down-beat."""
    mid = (top + bot) // 2
    half = 3
    # Deep gut behind — a maroon almond with a darker core so it reads wet.
    _poly(surf, _GUT, [(cx, top), (cx + half, mid), (cx, bot), (cx - half, mid)])
    _poly(surf, _GUT_D, [(cx, top + 2), (cx + half - 1, mid),
                         (cx, bot - 2), (cx - half + 1, mid)])
    # Two dark skin lips straining apart around the gut.
    pygame.draw.line(surf, _OUTLINE, (cx - half, mid), (cx, top), 2)
    pygame.draw.line(surf, _OUTLINE, (cx - half, mid), (cx, bot), 2)
    pygame.draw.line(surf, _OUTLINE, (cx + half, mid), (cx, top), 2)
    pygame.draw.line(surf, _OUTLINE, (cx + half, mid), (cx, bot), 2)
    # Heavy ooze bead sagging out of the base, longer on the down-flap.
    dy = bot + 2 + int(round(4 * drip))
    _aaellipse(surf, _OOZE_D, (cx, dy), 2, 3 + int(round(2 * drip)))
    _aaellipse(surf, _OOZE, (cx, dy - 1), 2, 2 + int(round(2 * drip)))
    pygame.draw.circle(surf, (150, 162, 92), (cx - 1, dy - 2), 1)


def _build(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # Flap-keyed gas jiggle: the whole bloated body squashes a hair taller on
    # the up-beat and rounder on the down-beat, so the gas-bag visibly wobbles
    # instead of holding a rigid egg. Kept tiny to read as a heavy jiggle.
    t = (wing_angle_deg + 40) / 90.0                 # 0 (down) .. 1 (up)
    jig = int(round(2 * math.sin(t * math.pi)))      # 0..2 px vertical swell
    drip = 1.0 - t                                   # ooze sags on the down-beat

    # Tail — short green wedges, mostly swallowed by the bloat.
    for i, c in enumerate([_BODY_D, _BODY, _BODY_H]):
        pts = [(2 + i * 3, 28 + i * 2), (13 + i, 26 + i),
               (18 + i, 32 + i * 2), (5 + i * 3, 38 + i * 2)]
        _poly(surf, c, pts)

    # Bloated body — ~1.3x the normal 19x14 build, drawn as stacked ellipses so
    # it reads as a taut over-inflated sphere: undershadow, main mass, belly.
    _aaellipse(surf, _BODY_D, (33, 34 + jig), 25, 19 + jig)
    _aaellipse(surf, _BODY, (31, 32), 24, 18 + jig)
    _aaellipse(surf, _BELLY, (28, 39), 16, 10)
    # Drum-tight sheen arc riding the upper-front of the swell.
    _aaellipse(surf, _BODY_H, (26, 26), 13, 6)
    pygame.draw.arc(surf, (222, 228, 190),
                    (14, 18, 34, 26), math.radians(35), math.radians(140), 2)

    # Pressure splits + oozing gut, straining open across the taut belly.
    _split(surf, 21, 31, 43, drip)
    _split(surf, 39, 34, 45, drip)

    # Blister cluster on the belly — pressurised methane boils, wobbling a touch
    # with the jiggle so they feel gas-filled.
    for bx, by, r in ((24, 39, 4), (32, 44, 3), (36, 38, 5),
                      (27, 33, 3), (33, 41, 4)):
        _blister(surf, bx, by - (jig if by > 36 else 0), r)

    # Wing.
    wing = _gas_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 27)).topleft)

    # Head — smaller than the ballooned body so the bloat dominates.
    _aaellipse(surf, _BODY_D, (48, 23), 12, 11)
    _aaellipse(surf, _BODY, (47, 21), 12, 11)
    _aaellipse(surf, _BODY_H, (45, 16), 6, 3)

    # Asymmetric eyes: one normal-but-dim eye, the other a tiny slit nearly
    # swallowed by a swollen flesh bulge — puffed shut by the bloat.
    pygame.draw.circle(surf, (206, 206, 186), (51, 19), 3)   # dim, not glossy
    pygame.draw.circle(surf, (30, 30, 24), (51, 20), 2)
    pygame.draw.circle(surf, (120, 120, 108), (50, 18), 1)   # weak, sickly glint
    # Swollen shut eye: a puffed body-tone bulge with a barely-visible dark slit.
    _aaellipse(surf, _BODY_H, (44, 22), 5, 4)
    pygame.draw.arc(surf, _OUTLINE, (39, 18, 10, 8),
                    math.radians(200), math.radians(340), 2)   # heavy lid fold
    pygame.draw.circle(surf, (34, 34, 26), (44, 23), 1)        # lost tiny eye

    # Beak — sickly desaturated horn.
    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    _poly(surf, _BEAK, beak_pts)
    pygame.draw.polygon(surf, _OUTLINE, beak_pts, 1)
    pygame.draw.line(surf, _OUTLINE, (52, 26), (58, 27), 1)    # slack mouth line

    # Feet — stubby, pressed under the heavy belly.
    pygame.draw.line(surf, _BODY_D, (28, 47), (26, 51), 2)
    pygame.draw.line(surf, _BODY_D, (35, 47), (37, 51), 2)
    return surf


build = _make_prebuilt_skin(_build)
