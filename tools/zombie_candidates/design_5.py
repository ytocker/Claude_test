"""BLOATED GAS-BAG — zombie-parrot candidate 5 (archetype: bloated).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_zombie`` is untouched. Exposes ``build(frame_idx, tilt_deg) -> Surface``
via store_skins._make_prebuilt_skin, matching the current-skin redraw idiom
(``_build_zombie_redraw``) — a full flat build per wing angle, outlined once.

Read strategy at 40px: this is the ONLY concept that changes the body SHAPE.
The silhouette itself carries the horror — a grotesquely over-round parrot
whose belly has ballooned ~1.3x, drum-tight and shiny, its round bottom edge
sagging into ooze drips that break the contour so even the black cut-out reads
as rot. The tells are concentrated into ONE loud red-maroon gut wound on the
lower-front belly (clear of the wing that occludes the centre), backed by a
sickly-yellow blister trio pushed onto the lightest upper back where yellow
survives, and a flat milky dead eye. Each is a filled block of value that
fights the sky rather than fine detail, so all survive the shrink. The flap
keys a subtle vertical squash so the gas-bag jiggles and the drips sag lower
on the down-beat.
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
# One loud red tell beats two hidden dark ones: a single bright gut wound that
# fights the green instead of two dim splits that read as dirt at 40px.
_GASH     = (158, 46, 44)          # #9E2E2C bright bloody gut
_GASH_D   = (70, 22, 26)           # #46161A wet dark core
_GASH_SPEC= (210, 150, 140)        # wet specular on the top lip
_SKINLIP  = (200, 210, 150)        # #C8D296 bright skin-lip so maroon pops
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
    """A raised festering boil: dark pressurised rim, sickly-yellow dome, fat
    specular dome — sized so the wet sphere still reads at 40px on the light
    upper back, where yellow-on-light survives (yellow-on-mid-green doesn't)."""
    pygame.draw.circle(surf, _BLIST_D, (cx, cy), r)
    pygame.draw.circle(surf, _BLISTER, (cx, cy), max(1, r - 1))
    pygame.draw.circle(surf, (255, 255, 235), (cx - 1, cy - 1), 2)


def _gash(surf, cx, top, bot, half):
    """The single loud undead tell: one vertical gut wound torn down the
    lower-front belly, clear of the wing. Bright bloody lens over a wet dark
    core, a specular on the top lip, framed by a bright skin-lip so the maroon
    pops off the green rather than muddying into it."""
    mid = (top + bot) // 2
    # Bright skin-lip frame first, a hair wider than the wound, so the red sits
    # in a light halo instead of blending straight into the belly green.
    _poly(surf, _SKINLIP, [(cx, top - 1), (cx + half + 1, mid),
                           (cx, bot + 1), (cx - half - 1, mid)])
    # Bright gut lens.
    _poly(surf, _GASH, [(cx, top), (cx + half, mid), (cx, bot), (cx - half, mid)])
    # Wet dark core down the centre.
    _poly(surf, _GASH_D, [(cx, top + 3), (cx + half - 2, mid),
                          (cx, bot - 3), (cx - half + 2, mid)])
    # Wet specular near the top lip.
    pygame.draw.circle(surf, _GASH_SPEC, (cx - 1, top + 3), 1)


def _drip(surf, cx, cy, drip):
    """A heavy ooze bead sagging BELOW the round body contour so the silhouette
    itself drips and sags — rot that reads even as a black cut-out. ``drip``
    (0..1, keyed to the flap) elongates the sag on the down-beat."""
    ln = 3 + int(round(3 * drip))
    pygame.draw.line(surf, _OOZE_D, (cx, cy - 2), (cx, cy + ln), 2)
    _aaellipse(surf, _OOZE_D, (cx, cy + ln), 3, 3)
    _aaellipse(surf, _OOZE, (cx, cy + ln - 1), 2, 2)
    pygame.draw.circle(surf, (150, 162, 92), (cx - 1, cy + ln - 1), 1)


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

    # Ooze drips sagging below the round bottom contour so the silhouette rots.
    _drip(surf, 22, 51, drip)
    _drip(surf, 34, 52, drip)
    _drip(surf, 28, 54, drip * 0.6)

    # ONE loud gut wound on the lower-front belly, clear of the wing (which
    # blits over the belly centre) so it is never occluded.
    _gash(surf, 24, 37, 50, 5)

    # Blister trio moved up onto the lightest upper back / shoulder, where the
    # sickly yellow fights the pale skin instead of drowning in mid-green.
    for bx, by, r in ((18, 30, 5), (22, 25, 4), (15, 36, 4)):
        _blister(surf, bx, by - (jig if by < 32 else 0), r)

    # Wing.
    wing = _gas_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 27)).topleft)

    # Head — smaller than the ballooned body so the bloat dominates.
    _aaellipse(surf, _BODY_D, (48, 23), 12, 11)
    _aaellipse(surf, _BODY, (47, 21), 12, 11)
    _aaellipse(surf, _BODY_H, (45, 16), 6, 3)

    # Dead milky open eye: a pale clouded iris ring with a tiny off-centre dark
    # pupil and NO glint — a flat lifeless stare reads as undead at 40px, where
    # a swollen-lid slit would just vanish. A dark rim seats it in the flesh.
    pygame.draw.circle(surf, _OUTLINE, (51, 19), 4)
    pygame.draw.circle(surf, (198, 200, 180), (51, 19), 3)    # milky clouded iris
    pygame.draw.circle(surf, (30, 30, 24), (52, 20), 1)       # tiny off-centre pupil

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
