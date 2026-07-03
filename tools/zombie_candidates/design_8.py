"""BARNACLE DROWNED WRETCH — zombie-parrot candidate 8 (archetype: deep-sea).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_zombie`` is untouched. Exposes ``build(frame_idx, tilt_deg) -> Surface``
via store_skins._make_prebuilt_skin, matching the current-skin redraw idiom
(``_build_zombie_redraw``) — a full flat build per wing angle, outlined once.

Read strategy at 40px: this is the only concept whose horror is COLD, not
rotten. The body is a bloated blue-grey drowned corpse, and the single
unmistakable tell is an anglerfish LURE — a glowing bioluminescent bulb dangling
on a stalk from the forehead, hanging right in front of the dead face. That
additive-glow ball is a shape and a light source nothing else in the sky owns,
so it survives the shrink where fine linework would vanish. Backing it: milky
dead-fish eye (no pupil), a shoulder+cheek of barnacle clumps that break the
contour with pale opening dots, and seaweed ribbons trailing off the back so the
silhouette itself reads waterlogged.
"""
import math
import pygame

from game.store_skins import SPRITE_W, SPRITE_H, _aaellipse, _poly, _make_prebuilt_skin

# Cold waterlogged flesh — a drowned blue-grey, deliberately NOT the green of a
# land corpse, so this zombie reads as "pulled from the deep" at a glance.
_BODY     = (92, 122, 130)         # #5C7A82 waterlogged flesh
_BODY_D   = (46, 64, 72)           # #2E4048 deep sunless shadow
_BODY_H   = (128, 154, 158)        # cold sheen between main and bloat
_BELLY    = (159, 182, 186)        # #9FB6BA pale drowned bloat
_OUTLINE  = (30, 44, 50)           # internal linework, darker than the shadow
_SEAWEED  = (60, 107, 58)          # #3C6B3A dark sea-green kelp
_SEAWEED_D= (40, 78, 40)           # kelp underside
_BARNACLE = (60, 72, 78)           # #3C484E barnacle shell base
_BARN_IN  = (148, 166, 168)        # lighter calcified inner ring
_BARN_EYE = (232, 238, 236)        # off-white shell opening
_LURE     = (185, 240, 255)        # #B9F0FF bioluminescent bulb core
_LURE_MID = (120, 200, 230)        # bulb body between core and stalk
_STALK    = (34, 46, 52)           # dark illicium stalk
_BEAK     = (150, 158, 150)        # bleached, bloodless horn


def _dw_wing(angle_deg):
    """A heavy, cold-toned wing with a single barnacle riding it so the shell
    tell survives even when the shoulder cluster is partly hidden by the pose."""
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    pts = [(24, 24), (44, 14), (48, 29), (33, 42), (18, 35)]
    _poly(w, _BODY, pts)
    _poly(w, _BODY_D, [(24, 24), (33, 42), (18, 35)])
    pygame.draw.line(w, _BODY_D, (26, 25), (42, 18), 2)
    pygame.draw.line(w, _BODY_H, (25, 25), (41, 16), 1)
    # Lone barnacle on the wing shoulder.
    pygame.draw.circle(w, _BARNACLE, (30, 29), 4)
    pygame.draw.circle(w, _BARN_IN, (30, 29), 2)
    pygame.draw.circle(w, _BARN_EYE, (30, 29), 1)
    return pygame.transform.rotate(w, angle_deg)


def _barnacle(surf, cx, cy, r):
    """A calcified shell clump: dark shell base, lighter calcified inner ring,
    a tiny off-white opening — sized so the pale opening dot still punches
    through at 40px, breaking the smooth contour so the crust reads."""
    pygame.draw.circle(surf, _BARNACLE, (cx, cy), r)
    pygame.draw.circle(surf, _BARN_IN, (cx, cy), max(1, r - 2))
    pygame.draw.circle(surf, _BARN_EYE, (cx, cy), 1)


def _seaweed(surf, pts, width):
    """A wavy kelp ribbon drawn as a dark under-stroke plus a lighter overlay so
    it reads as a rounded frond rather than a flat line; ``pts`` are the bends."""
    pygame.draw.lines(surf, _SEAWEED_D, False, pts, width)
    lit = [(x + 1, y - 1) for (x, y) in pts]
    pygame.draw.lines(surf, _SEAWEED, False, lit, max(1, width - 1))


def _lure(surf, tip, sway):
    """The hero tell: an anglerfish illicium arcing off the forehead to a glowing
    bioluminescent bulb hovering in front of the dead face. The bulb is backed by
    an additive glow halo (BLEND_RGB_ADD) so it acts as a genuine light source —
    a shape and a glow nothing else in the sky owns, so it survives the shrink.
    ``sway`` nudges the tip a hair with the flap so the lure bobs."""
    root = (45, 16)
    tx, ty = tip[0] + sway, tip[1]
    # Curved dark stalk: forehead → forward-and-down to the bulb, via a control
    # bend so the illicium droops naturally instead of running straight.
    bend = (54, 12)
    stalk = [root, bend, (tx, ty)]
    pygame.draw.lines(surf, _STALK, False, stalk, 2)
    pygame.draw.circle(surf, _STALK, root, 2)   # fleshy base knuckle on the brow

    # Additive glow halo on its own surface so the light bleeds over the face.
    glow = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    for rad, a in ((9, 40), (6, 70), (4, 120)):
        pygame.draw.circle(glow, (110, 190, 230, a), (int(tx), int(ty)), rad)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    # Solid bulb on top of its own glow.
    pygame.draw.circle(surf, _LURE_MID, (int(tx), int(ty)), 4)
    pygame.draw.circle(surf, _LURE, (int(tx), int(ty)), 3)
    pygame.draw.circle(surf, (245, 255, 255), (int(tx) - 1, int(ty) - 1), 1)


def _build(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # Flap phase drives a slow, underwater bob of the lure and a drift of the
    # trailing kelp, so the whole figure sways like it hangs in deep current.
    t = (wing_angle_deg + 40) / 90.0                 # 0 (down) .. 1 (up)
    sway = int(round(2 * math.sin(t * math.pi)))     # -0..2 px lure bob
    kelp = int(round(2 * math.sin(t * math.pi + 1))) # kelp drifts out of phase

    # Seaweed drape FIRST so it trails behind the body — three kelp ribbons off
    # the back and tail, bending downward like fronds caught in a slow current.
    _seaweed(surf, [(10, 24), (6, 32 + kelp), (12, 40), (7, 49 + kelp)], 3)
    _seaweed(surf, [(16, 30), (10, 38 - kelp), (16, 45), (11, 53)], 3)
    _seaweed(surf, [(22, 34), (18, 43 + kelp), (24, 50), (19, 56 + kelp)], 3)

    # Tail — short cold wedges under the kelp.
    for i, c in enumerate([_BODY_D, _BODY, _BODY_H]):
        pts = [(3 + i * 3, 27 + i * 2), (14 + i, 25 + i),
               (19 + i, 31 + i * 2), (6 + i * 3, 37 + i * 2)]
        _poly(surf, c, pts)

    # Bloated waterlogged body — stacked cold ellipses reading as a swollen,
    # sodden mass: sunless undershadow, blue-grey main, pale drowned belly.
    _aaellipse(surf, _BODY_D, (34, 35), 20, 15)
    _aaellipse(surf, _BODY, (32, 32), 20, 15)
    _aaellipse(surf, _BODY_H, (29, 28), 13, 7)
    _aaellipse(surf, _BELLY, (28, 39), 13, 7)

    # Shoulder barnacle cluster — a crust of shells breaking the upper-back
    # contour with pale opening dots.
    _barnacle(surf, 28, 32, 5)
    _barnacle(surf, 23, 29, 4)
    _barnacle(surf, 31, 27, 4)

    # Wing.
    wing = _dw_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # Head.
    _aaellipse(surf, _BODY_D, (48, 23), 12, 11)
    _aaellipse(surf, _BODY, (47, 21), 12, 11)
    _aaellipse(surf, _BODY_H, (46, 16), 7, 3)

    # Cheek barnacle clump — a shell growing on the face itself.
    _barnacle(surf, 44, 24, 4)

    # Milky drowned eye: a flat pale-blue-white orb with NO pupil and no glint —
    # the classic dead-fish stare. A dark rim seats it into the sodden flesh.
    pygame.draw.circle(surf, _OUTLINE, (50, 19), 5)
    pygame.draw.circle(surf, (190, 210, 220), (50, 19), 4)

    # Beak — bleached, bloodless horn, slack.
    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    _poly(surf, _BEAK, beak_pts)
    pygame.draw.polygon(surf, _OUTLINE, beak_pts, 1)
    pygame.draw.line(surf, _OUTLINE, (52, 26), (58, 27), 1)   # slack drowned mouth

    # Feet — limp, hanging.
    pygame.draw.line(surf, _BODY_D, (28, 46), (26, 51), 2)
    pygame.draw.line(surf, _BODY_D, (35, 46), (37, 51), 2)

    # Anglerfish lure LAST so the bulb and its additive glow sit in front of the
    # face — the money tell nothing else in the sky carries.
    _lure(surf, (58, 20), sway)
    return surf


build = _make_prebuilt_skin(_build)
