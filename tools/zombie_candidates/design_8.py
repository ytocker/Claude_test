"""BARNACLE DROWNED WRETCH — zombie-parrot candidate 8 (archetype: deep-sea).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_zombie`` is untouched. Exposes ``build(frame_idx, tilt_deg) -> Surface``
via store_skins._make_prebuilt_skin, matching the current-skin redraw idiom
(``_build_zombie_redraw``) — a full flat build per wing angle, outlined once.

Read strategy at 40px: this is the only concept whose horror is COLD, not
rotten. The body is a bloated blue-grey drowned corpse, and the single
unmistakable tell is an anglerfish LURE — a glowing bioluminescent bulb dangling
on a stalk that arcs over the skull and hangs the bulb clear IN FRONT of the
dead face, with a band of dark flesh between skull and bulb so the light reads
as a dangling lure rather than a glowing head. That floating glow dot is a shape
and a light source nothing else in the sky owns, so it survives the shrink where
fine linework would vanish. Backing it: a milky pupil-less dead-fish eye, two
barnacle clumps (one riding the shoulder contour as a lumpy bump), and a heavy
teal-olive kelp drape trailing off the back so the silhouette reads waterlogged.
"""
import math
import pygame

from game.store_skins import SPRITE_W, SPRITE_H, _aaellipse, _poly, _make_prebuilt_skin

# Cold waterlogged flesh — a drowned blue-grey, deliberately NOT the green of a
# land corpse, so this zombie reads as "pulled from the deep" at a glance.
_BODY     = (92, 122, 130)         # #5C7A82 waterlogged flesh
_BODY_D   = (37, 51, 58)           # #25333A deep sunless shadow (deepened so the
                                   # blue-grey shape punches against mid-blue sky)
_BODY_H   = (128, 154, 158)        # cold sheen (kept off the head crown)
_BELLY    = (159, 182, 186)        # #9FB6BA pale drowned bloat
_FOOT     = (150, 172, 176)        # pale drowned-flesh feet, so they read against
                                   # the dark kelp instead of merging into it
_OUTLINE  = (30, 44, 50)           # internal linework, darker than the shadow
# Kelp shifted to a cooler desaturated teal-olive so it separates cleanly from
# the warm vine green on the stone pillars behind it.
_SEAWEED  = (46, 85, 84)           # #2E5554 teal-olive kelp
_SEAWEED_D= (32, 62, 62)           # kelp underside
_BARNACLE = (58, 70, 76)           # #3A464C dark shell rim
_BARN_IN  = (100, 118, 122)        # mid recessed shell body (kept dark so the rim
                                   # frames a hole, not a specular highlight)
_BARN_EYE = (232, 238, 236)        # off-white shell opening
_LURE     = (185, 240, 255)        # #B9F0FF bioluminescent bulb core
_LURE_MID = (120, 200, 230)        # bulb body between core and stalk
_STALK    = (34, 46, 52)           # dark illicium stalk
_BEAK     = (150, 158, 150)        # bleached, bloodless horn


def _dw_wing(angle_deg):
    """A heavy, cold-toned wing with a single barnacle riding it so the shell
    tell survives even when the shoulder clump is partly hidden by the pose."""
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    pts = [(24, 24), (44, 14), (48, 29), (33, 42), (18, 35)]
    _poly(w, _BODY, pts)
    _poly(w, _BODY_D, [(24, 24), (33, 42), (18, 35)])
    pygame.draw.line(w, _BODY_D, (26, 25), (42, 18), 2)
    pygame.draw.line(w, _BODY_H, (25, 25), (41, 16), 1)
    # Lone barnacle on the wing shoulder — dark rim, tiny pale opening.
    pygame.draw.circle(w, _BARNACLE, (30, 29), 4)
    pygame.draw.circle(w, _BARN_IN, (30, 29), 2)
    pygame.draw.circle(w, _BARN_EYE, (30, 29), 1)
    return pygame.transform.rotate(w, angle_deg)


def _barnacle(surf, cx, cy, r):
    """A calcified shell lump: a dark shell rim ringing a small pale opening, so
    it reads as a raised barnacle biting the contour — a lump/hole, not a
    specular dot. The mid-tone body stays dark enough that the rim keeps framing
    the pale core at 40px instead of flooding the clump pale."""
    pygame.draw.circle(surf, _BARNACLE, (cx, cy), r)             # dark shell rim
    pygame.draw.circle(surf, _BARN_IN, (cx, cy), max(1, r - 2))  # recessed body
    pygame.draw.circle(surf, _BARN_EYE, (cx, cy), max(1, r // 3))  # pale opening


def _seaweed(surf, pts, width):
    """A wavy kelp ribbon drawn as a dark under-stroke plus a lighter overlay so
    it reads as a rounded frond rather than a flat line; ``pts`` are the bends."""
    pygame.draw.lines(surf, _SEAWEED_D, False, pts, width)
    lit = [(x + 1, y - 1) for (x, y) in pts]
    pygame.draw.lines(surf, _SEAWEED, False, lit, max(1, width - 1))


def _lure(surf, tip, sway):
    """The hero tell: an anglerfish illicium arcing UP and forward over the skull
    to a glowing bulb that hangs clear in front of the dead face. The stalk rises
    off the brow and dips down so a band of dark flesh sits between skull and
    bulb — the light must read as a dangling lure, not a glowing head.

    The halo is drawn with NORMAL alpha (not additive): an additive glow only
    brightens pixels that are already opaque, so over the transparent water in
    front of the beak it would vanish and only the face would light up — exactly
    the "glowing face" failure. Plain alpha lets the halo float as its own dot.
    ``sway`` nudges the tip a hair with the flap so the lure bobs in the current.
    """
    root = (46, 15)
    tx, ty = tip[0] + sway, tip[1]
    # Dark stalk: brow → up-and-over the skull (bend) → down to the hanging bulb.
    bend = (58, 9)
    stalk = [root, bend, (int(tx), int(ty))]
    pygame.draw.lines(surf, _STALK, False, stalk, 2)
    pygame.draw.circle(surf, _STALK, root, 2)   # fleshy base knuckle on the brow

    # Soft halo as its own translucent dot so it glows in open water.
    glow = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    for rad, a in ((8, 70), (5, 130), (3, 190)):
        pygame.draw.circle(glow, (120, 205, 240, a), (int(tx), int(ty)), rad)
    surf.blit(glow, (0, 0))

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

    # Seaweed drape FIRST so it trails behind the body — a heavy back frond that
    # runs well below the tail as a tail-drape, extending the silhouette down,
    # plus two shorter ribbons, all bending like kelp in a slow current.
    _seaweed(surf, [(10, 24), (5, 33 + kelp), (11, 43), (6, 55 + kelp), (10, 62)], 4)
    _seaweed(surf, [(16, 30), (10, 39 - kelp), (16, 47), (11, 57)], 3)
    _seaweed(surf, [(22, 34), (18, 44 + kelp), (24, 51), (19, 58 + kelp)], 3)

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

    # Shoulder barnacle riding the top-of-shoulder contour so it pokes above the
    # outline as a visible lumpy bump.
    _barnacle(surf, 23, 20, 6)

    # Wing.
    wing = _dw_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # Head — crown kept dark (no sheen) so the detached lure glow pops against
    # dark flesh instead of fusing with a pale highlight.
    _aaellipse(surf, _BODY_D, (48, 23), 12, 11)
    _aaellipse(surf, _BODY, (47, 21), 12, 11)

    # Cheek barnacle clump — a second shell growing on the face itself.
    _barnacle(surf, 43, 26, 5)

    # Milky drowned eye: a flat pale orb with NO pupil and no glint — the classic
    # dead-fish stare, sized big with a dark rim so the blank eye registers as
    # the coarse undead cue even at 40px.
    pygame.draw.circle(surf, _OUTLINE, (50, 19), 5)
    pygame.draw.circle(surf, (200, 216, 222), (50, 19), 4)

    # Beak — bleached, bloodless horn, slack.
    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    _poly(surf, _BEAK, beak_pts)
    pygame.draw.polygon(surf, _OUTLINE, beak_pts, 1)
    pygame.draw.line(surf, _OUTLINE, (52, 26), (58, 27), 1)   # slack drowned mouth

    # Feet — limp, hanging, in pale drowned flesh so they separate from the kelp.
    pygame.draw.line(surf, _FOOT, (28, 46), (26, 51), 2)
    pygame.draw.line(surf, _FOOT, (35, 46), (37, 51), 2)

    # Anglerfish lure LAST so the bulb and its halo sit clear in front of the
    # face — the money tell nothing else in the sky carries.
    _lure(surf, (60, 27), sway)
    return surf


build = _make_prebuilt_skin(_build)
