"""ANCIENT CRYPT ROT — zombie-parrot redesign candidate (design 2).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_zombie`` redraw is untouched. Exposes ``build`` — a
``(frame_idx, tilt_deg) -> Surface`` getter — via ``_make_prebuilt_skin``, the
same whole-body prebuilt path the shipped zombie uses.

Concept: a gaunt, mummified husk instead of the friendly cartoon zombie. The
read is dry death, not sickly-cute — desaturated bone-gray plumage with the
skin worn through so the skeleton shows. The loudest 40px tell is a bone-white
RIB LADDER over a sunken cavity on the flank; a knobby vertebral ridge crowns
the back and both eyes are hollow sockets with a faint green ember still burning
inside ("something's still in there"). No white eye-rings, no shine anywhere —
everything is flat and dry so it reads as desiccated, not wet-undead.
"""
import pygame

from game.store_skins import _make_prebuilt_skin
from game.parrot import SPRITE_W, SPRITE_H, _aaellipse

# Rotting palette — desaturated so nothing looks alive or juicy; the only
# saturated pixel in the whole bird is the green socket ember, which makes it
# the eye's magnet at any size.
_ROT_BODY   = (154, 148, 131)      # dry bone-gray plumage
_ROT_BODY_D = (108, 103, 90)       # dried-out shadow tone (tail / underlay)
_ROT_SHADOW = (42, 40, 34)         # deep shadow / socket void
_ROT_CAVITY = (40, 36, 30)         # near-black sunken cavity — the value gap to
                                   # bone-white rungs is what makes ribs read at 40px
_ROT_BONE   = (216, 210, 190)      # bone highlight (ribs / spine tops / beak)
_ROT_MOTTLE = (96, 90, 76)         # patchy decay blotch tone
_ROT_GLOW   = (95, 191, 106)       # socket ember (the one saturated accent)
_ROT_BEAK   = (170, 158, 130)      # dry keratin beak
_ROT_FOOT   = (60, 56, 48)         # gaunt claw


def _soft_glow(surf, cx, cy, r, color, alpha):
    """Translucent additive-feeling glow blob — pygame's draw ops overwrite
    alpha rather than blend, so the ember halo is painted on its own surface
    and blitted so it composites over the dark socket instead of punching a
    flat disc."""
    g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(g, (*color, alpha), (r + 1, r + 1), r)
    surf.blit(g, (cx - r - 1, cy - r - 1))


def _rot_wing(angle_deg):
    """Gaunt, dried wing — same silhouette anchors as the shipped zombie so the
    beat reads, but bone-gray with a torn trailing notch and a couple of dry
    bone-quill lines instead of feather sheen."""
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    pts = [(24, 24), (44, 13), (48, 28), (32, 42), (18, 36)]
    pygame.draw.polygon(w, _ROT_BODY, pts)
    # Underside kept in shadow so the wing separates from the flank ribs behind.
    pygame.draw.polygon(w, _ROT_BODY_D, [(24, 24), (32, 42), (18, 36)])
    # Torn trailing edge — a wedge bitten out so the wing looks decayed.
    pygame.draw.polygon(w, (0, 0, 0, 0), [(48, 28), (40, 30), (44, 36)])
    pygame.draw.polygon(w, _ROT_BODY_D, [(38, 31), (44, 30), (41, 35)])
    # Dry exposed quills — thin bone lines, no highlight sheen.
    pygame.draw.line(w, _ROT_BODY_D, (26, 25), (42, 18), 1)
    pygame.draw.line(w, _ROT_BONE, (27, 27), (40, 21), 1)
    return pygame.transform.rotate(w, angle_deg)


def _build_crypt_rot(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # ── Tail — dry, desaturated wedges (darker → lighter bone toward the fan).
    for i, c in enumerate([_ROT_BODY_D, (128, 122, 106), _ROT_BODY, (172, 166, 146)]):
        pts = [(2 + i * 3, 26 + i * 2), (14 + i, 24 + i),
               (20 + i, 30 + i * 2), (6 + i * 3, 36 + i * 2)]
        pygame.draw.polygon(surf, c, pts)

    # ── Body mass — flat dry tones, no belly-sheen highlight (kept desiccated).
    _aaellipse(surf, _ROT_BODY_D, (34, 35), 19, 14)
    _aaellipse(surf, _ROT_BODY, (32, 32), 19, 14)
    _aaellipse(surf, (168, 162, 144), (30, 29), 12, 7)     # faint dry topside

    # ── Dust / mottle — scattered patchy decay so the hide looks rotted, not
    #    clean-painted. Fixed positions keep every frame identical.
    for mx, my, mrx, mry in ((22, 38, 4, 2), (36, 40, 3, 2), (40, 30, 3, 2),
                             (26, 26, 2, 2), (18, 33, 2, 1), (30, 42, 3, 1),
                             (44, 36, 2, 2)):
        _aaellipse(surf, _ROT_MOTTLE, (mx, my), mrx, mry)

    # ── Spine bumps — a knobby vertebral ridge that BREAKS the back silhouette.
    #    The beads sit high enough that the top of each knob protrudes above the
    #    body outline, so the bumpy contour survives downscale (internal beads do
    #    not read at 40px — a broken outline does). Drawn before the wing so the
    #    wing root tucks under the ridge.
    for sx, sy, sr in ((21, 20, 4), (27, 18, 5), (33, 17, 5), (39, 18, 4)):
        pygame.draw.circle(surf, _ROT_SHADOW, (sx, sy + 1), sr)       # under-shadow
        pygame.draw.circle(surf, _ROT_BODY, (sx, sy), sr)
        pygame.draw.circle(surf, _ROT_BONE, (sx - 1, sy - 1), max(1, sr - 2))

    # ── Rib ladder — THE hero tell. A near-black cavity, then a stack of
    #    HORIZONTAL bone-white rungs marching down the mid-flank. Horizontal
    #    rungs read as a ribcage; the earlier vertical/bowed strokes reached the
    #    lower silhouette edge and mis-read as a grinning row of teeth. Each rung
    #    gets a hard 1px dark line directly beneath it so the value alternation
    #    survives downscale to 40px.
    cavity = [(16, 34), (23, 30), (32, 31), (34, 40), (26, 44), (17, 41)]
    pygame.draw.polygon(surf, _ROT_CAVITY, cavity)
    pygame.draw.polygon(surf, _ROT_SHADOW, cavity, 1)
    for ry in (31, 34, 37, 40):
        pygame.draw.rect(surf, _ROT_BONE, (18, ry, 9, 2))            # bone rung
        pygame.draw.rect(surf, _ROT_SHADOW, (18, ry + 2, 9, 1))      # drop-shadow

    # ── Wing (blitted centred like the shipped zombie).
    wing = _rot_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # ── Head — gaunt skull, flat dry tones, no cheek sheen.
    _aaellipse(surf, _ROT_BODY_D, (48, 23), 12, 11)
    _aaellipse(surf, _ROT_BODY, (47, 21), 12, 11)
    _aaellipse(surf, (168, 162, 144), (46, 16), 6, 3)
    # A hairline skull crack so the head reads as bone, not a smooth cartoon.
    pygame.draw.line(surf, _ROT_SHADOW, (47, 12), (49, 18), 1)
    pygame.draw.line(surf, _ROT_SHADOW, (49, 18), (46, 22), 1)

    # ── Hollow sockets — both eyes gone. Near-black pits, each with a dim green
    #    ember + soft halo floating inside. No white eye-ring anywhere.
    for ex, ey, er in ((50, 19, 4), (44, 21, 3)):
        pygame.draw.circle(surf, _ROT_SHADOW, (ex, ey), er)
        pygame.draw.circle(surf, (18, 20, 16), (ex, ey), max(1, er - 1))
        _soft_glow(surf, ex, ey, er, _ROT_GLOW, 90)
        # 2px pinlight — the dim green dot in a black socket is the strongest
        # undead tell; kept as a crisp core, never allowed to bloom to a glow-ball.
        pygame.draw.circle(surf, _ROT_GLOW, (ex, ey), 2)

    # ── Cracked dry beak — desaturated keratin, split along the lower mandible
    #    with one chip notched out of the tip.
    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    pygame.draw.polygon(surf, _ROT_BEAK, beak_pts)
    pygame.draw.polygon(surf, _ROT_SHADOW, beak_pts, 1)
    # Chip removed from the tip — a small notch punched back out of the beak.
    pygame.draw.polygon(surf, (0, 0, 0, 0), [(61, 24), (58, 25), (59, 27)])
    # Crack splitting the lower beak.
    pygame.draw.line(surf, _ROT_SHADOW, (53, 25), (58, 25), 1)
    pygame.draw.line(surf, _ROT_SHADOW, (55, 22), (55, 26), 1)

    # ── Feet — gaunt, dark claws (thin, dried).
    pygame.draw.line(surf, _ROT_FOOT, (28, 45), (26, 49), 2)
    pygame.draw.line(surf, _ROT_FOOT, (34, 45), (36, 49), 2)

    # ── Dark rim — trace the outer silhouette in deep shadow so the bone-gray
    #    husk separates from white clouds and the night biome, not just the sky.
    #    Done last against the assembled mask so the rim follows the true contour.
    mask = pygame.mask.from_surface(surf)
    for px, py in mask.outline():
        surf.set_at((px, py), _ROT_SHADOW)

    return surf


build = _make_prebuilt_skin(_build_crypt_rot)
