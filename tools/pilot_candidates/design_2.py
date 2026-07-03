"""Pilot costume — Design 2: ACE, the WW1/WW2 open-cockpit dogfighter.

The hero read is a brown leather flight helmet hugging the whole skull with a
silk scarf streaming off the nape as a trailing pennant — the motion tell that
separates this from a static-headgear costume. Goggles ride pushed UP on the
brow (deliberately not over the eyes, so it never reads as the aviator-shades
base or a diving visor), and a fur-collar bomber jacket grounds the chest.

Scratch exploration only — wired through _make_skin exactly like the production
store skins so the preview matches the shipped compositing, but never registered
in BUILDERS.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
import pygame
from game.store_skins import _pal, _build_parrot_with_palette, _make_skin, _poly, HX, HY, CROWN_Y
from game.parrot import SPRITE_W, SPRITE_H, _aaellipse


# Locked to a three-value read so the bird never collapses to a brown blob at
# 40px: DARK helmet crown is the head mass, MID body brown is the base plumage,
# LIGHT cream (scarf + shearling) is the single high-value note the eye lands on.
_LEATHER    = (107, 74, 43)        # mid — base body brown (unchanged base plumage)
_LEATHER_D  = (62, 42, 23)         # dark — leather helmet crown (#3E2A17)
_LEATHER_H  = (150, 110, 72)
_SEAM_H     = (138, 98, 56)        # #8A6238 — lone helmet seam highlight arc
_FUR        = (201, 168, 118)      # #C9A876 — shearling collar bumps
_FUR_D      = (162, 132, 88)
_FUR_H      = (216, 196, 154)      # #D8C49A — fleece highlight fleck
_SCARF      = (232, 226, 212)      # #E8E2D4 — silk pennant (the lightest value)
_SCARF_D    = (190, 182, 164)
_SCARF_H    = (248, 244, 234)
_BRASS      = (185, 138, 60)
_BRASS_H    = (232, 198, 120)
_GOGGLE     = (46, 42, 38)
_GLASS      = (120, 150, 168)      # cool lens reflection so goggles read as glass
_EYE        = (26, 14, 6)          # #1A0E06 — dark eye dot below the goggles


# Full leather re-plumage so the helmet and jacket sit on a body that already
# reads as tan flight gear; lenses are dropped so the goggles own the brow and a
# single painted eye owns the face.
P_ACE = _pal(
    tail=[(78, 54, 31), (90, 62, 34), (100, 70, 40), (112, 80, 48)],
    tail_line=_LEATHER_D,
    body_shadow=_LEATHER_D,
    body_main=_LEATHER,
    body_chest=(165, 124, 82),
    body_belly=(150, 110, 72),
    sheen=(255, 238, 208, 55),
    wing_main=(90, 62, 34),
    wing_dark=_LEATHER_D,
    wing_tip=(120, 86, 48),
    wing_secondary=None,
    wing_highlight=_LEATHER_H,
    head_shadow=_LEATHER_D,
    head_main=_LEATHER,
    head_cheek=(130, 95, 58),
    head_crown=(120, 86, 48),
    lens_frame=_LEATHER_D,
    lens_body=_GOGGLE,
    lens_tint=None,
    lens_glint=None,
    beak_main=(180, 150, 80),
    beak_dark=(120, 90, 40),
    beak_gloss=(212, 186, 120),
    foot=_LEATHER_D,
)


def _ace_base(angle_deg):
    # No aviators — the pushed-up goggles + one painted eye carry the face.
    return _build_parrot_with_palette(angle_deg, P_ACE, draw_lenses=False)


def _paint(surf, wing_angle_deg):
    # ── 1 · Trailing silk pennant off the nape (hero motion tell) ───────────
    # Roots at the nape and streams BACK-and-DOWN, its forked tip overshooting
    # the tail into open sky so the cream crosses the left silhouette — that
    # break is the whole "diving ace" read. Drawn first so the collar/helmet
    # root it at the neck. The lightest value on the bird.
    scarf = [(41, 33), (31, 38), (20, 43), (9, 47), (4, 49),
             (9, 51), (7, 55), (18, 50), (30, 45), (40, 39)]
    _poly(surf, _SCARF_D, [(x - 1, y + 1) for x, y in scarf])   # under-shadow
    _poly(surf, _SCARF, scarf)
    # Lit upper edge so the ribbon reads as wind-caught silk, tapering to a fork.
    pygame.draw.lines(surf, _SCARF_H, False,
                      [(41, 33), (31, 38), (20, 43), (9, 47), (4, 49)], 1)
    pygame.draw.line(surf, _SCARF_H, (7, 55), (9, 51), 1)       # fork glint

    # ── 4 · Shearling collar (the body/head value break) ────────────────────
    # A row of fleece bumps arcing the neckline between the dark helmet and the
    # mid body — cream over a dark rim so each lump reads round, with a fleck of
    # the brightest fleece on top. This is what stops the bird reading monochrome.
    for bx, by in ((28, 48), (32, 46), (37, 45), (42, 45), (46, 47)):
        pygame.draw.circle(surf, _FUR_D, (bx, by + 1), 5)
        pygame.draw.circle(surf, _FUR, (bx, by), 4)
        pygame.draw.circle(surf, _FUR_H, (bx - 1, by - 1), 1)

    # ── 2 · Leather flight helmet (the darkest mass) ────────────────────────
    # A solid dark-brown dome over crown + back + upper head so the head is the
    # deepest value on the bird and the lighter goggles pop off it. The lower
    # front edge stays above the eye so the mid-brown face + beak read below it.
    helmet = [(37, 47), (34, 40), (34, 32), (39, 27), (47, 26), (54, 28),
              (58, 34), (57, 39), (49, 38), (43, 41), (38, 43)]
    _poly(surf, _LEATHER_D, helmet)
    # One seam highlight arc crown→nape so the leather reads as a rounded shell.
    pygame.draw.lines(surf, _SEAM_H, False,
                      [(50, 30), (45, 28), (40, 30), (37, 35), (36, 41)], 1)
    # Short chin strap dropping off the ear-flap to a brass stud on the jaw.
    pygame.draw.line(surf, _LEATHER_D, (39, 43), (44, 48), 2)
    pygame.draw.circle(surf, _BRASS, (44, 48), 1)

    # ── 3 · Goggles pushed up on the FOREHEAD ───────────────────────────────
    # Two brass-ringed glass lenses parked high on the crown (y≈HY−9), well above
    # the eye — the "just pulled up, ready to dive" tell, never a visor-down or
    # sunglasses read. A side strap wraps back to the helmet shell.
    gy = HY - 9
    for gx in (42, 52):
        pygame.draw.circle(surf, _GOGGLE, (gx, gy), 4)
        pygame.draw.circle(surf, _BRASS, (gx, gy), 4, 1)
        pygame.draw.circle(surf, _GLASS, (gx - 1, gy - 1), 2)          # glass sheen
        pygame.draw.circle(surf, (255, 255, 255), (gx - 1, gy - 2), 1)  # glint
    pygame.draw.line(surf, _BRASS, (46, gy), (48, gy), 2)              # nose bridge
    pygame.draw.line(surf, _BRASS, (56, gy), (59, 34), 1)             # strap to shell
    pygame.draw.circle(surf, _BRASS_H, (41, gy - 1), 1)

    # ── Pilot eye on the exposed face, BELOW the goggles ────────────────────
    # A single dark eye dot on the mid-brown face, stacked under the goggle pair
    # so the 40px read is: dark eye + two round lenses above = goggles-on-brow.
    pygame.draw.circle(surf, _EYE, (50, 42), 2)
    pygame.draw.circle(surf, (255, 255, 255), (49, 41), 1)


build = _make_skin(_paint, base_fn=_ace_base)
