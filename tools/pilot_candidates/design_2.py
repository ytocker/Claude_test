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


# Leather-and-silk palette. Helmet + jacket share the base body brown so the
# costume reads as one worn kit; the scarf cream is the single high-value note.
_LEATHER    = (107, 74, 43)
_LEATHER_D  = (62, 42, 23)
_LEATHER_H  = (150, 110, 72)
_FUR        = (201, 168, 118)
_FUR_D      = (162, 132, 88)
_FUR_H      = (226, 200, 156)
_SCARF      = (232, 226, 212)
_SCARF_D    = (198, 190, 172)
_SCARF_H    = (248, 244, 234)
_BRASS      = (185, 138, 60)
_BRASS_H    = (232, 198, 120)
_GOGGLE     = (46, 42, 38)


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
    BCX, BCY = 32, 52          # body centre in composite space

    # ── 1 · Trailing silk scarf (hero motion tell) ──────────────────────────
    # Streams off the nape and down-back; the tapered tail is what breaks the
    # egg silhouette and sells the dive. Drawn first so the collar/jacket layer
    # roots it at the neck.
    scarf = [(HX - 10, HY - 4), (HX - 12, HY + 2), (HX - 18, HY + 14),
             (HX - 22, HY + 18), (HX - 26, HY + 14), (HX - 20, HY + 8),
             (HX - 14, HY - 2)]
    _poly(surf, _SCARF_D, [(x - 1, y + 1) for x, y in scarf])   # under-shadow
    _poly(surf, _SCARF, scarf)
    # Bright top edge so the ribbon reads as lit silk, tapering to a point.
    pygame.draw.lines(surf, _SCARF_H, False,
                      [(HX - 10, HY - 4), (HX - 14, HY - 2),
                       (HX - 20, HY + 8), (HX - 26, HY + 14)], 1)
    _poly(surf, _SCARF_H, [(HX - 26, HY + 14), (HX - 22, HY + 18),
                           (HX - 24, HY + 15)])                 # pinched tip glint

    # ── 4 · Fur-collar bomber jacket ────────────────────────────────────────
    # Bumpy fur arc across the upper chest; the dark jacket body is just the base
    # brown showing below it. Fur bumps + one highlight tick keep it reading as
    # shearling, not a flat crescent.
    collar = [(BCX - 10, BCY - 12), (BCX - 14, BCY - 6), (BCX - 12, BCY - 2),
              (BCX - 6, BCY - 4), (BCX, BCY - 10), (BCX + 4, BCY - 12)]
    _poly(surf, _FUR_D, [(x, y + 1) for x, y in collar])
    _poly(surf, _FUR, collar)
    for bx, by in ((BCX - 12, BCY - 8), (BCX - 9, BCY - 4), (BCX - 4, BCY - 6),
                   (BCX, BCY - 9)):
        pygame.draw.circle(surf, _FUR_H, (bx, by), 1)
    pygame.draw.circle(surf, _FUR_D, (BCX - 7, BCY - 3), 1)
    # Jacket seam down the chest.
    pygame.draw.line(surf, _LEATHER_D, (BCX, BCY - 10), (BCX, BCY + 8), 1)

    # ── 2 · Leather flight helmet ───────────────────────────────────────────
    # Hugs the whole skull. Same brown as the head, so form comes from the crown
    # seam + a front highlight edge + the chin-strap nub rather than a colour
    # break — reads as a fitted leather cap, not a hat sitting on top.
    helmet = [(HX - 10, CROWN_Y + 2), (HX - 6, CROWN_Y - 3), (HX + 8, CROWN_Y - 2),
              (HX + 11, CROWN_Y + 6), (HX + 10, HY + 2), (HX - 2, HY + 4),
              (HX - 10, HY)]
    _poly(surf, _LEATHER, helmet)
    # Front-crown highlight so the leather reads round under the light.
    pygame.draw.line(surf, _LEATHER_H, (HX - 5, CROWN_Y - 2), (HX + 7, CROWN_Y - 1), 1)
    # Crown seam arcing back-to-front.
    pygame.draw.line(surf, _LEATHER_D, (HX - 4, CROWN_Y), (HX + 6, CROWN_Y + 3), 1)
    # Ear-flap shadow so the side of the cap separates from the cheek.
    pygame.draw.line(surf, _LEATHER_D, (HX - 9, HY - 2), (HX - 7, HY + 3), 2)
    # Chin-strap nub.
    pygame.draw.circle(surf, _LEATHER_D, (HX + 9, HY + 3), 2)
    pygame.draw.circle(surf, _BRASS, (HX + 9, HY + 3), 1)

    # ── 3 · Goggles pushed up on the brow ───────────────────────────────────
    # Two brass-ringed lenses parked on the forehead — the "just landed / ready
    # to dive" tell. Kept OFF the eyes so it never mimics a visor-down look.
    for gx in (HX - 4, HX + 4):
        pygame.draw.circle(surf, _GOGGLE, (gx, CROWN_Y + 5), 4)
        pygame.draw.circle(surf, _BRASS, (gx, CROWN_Y + 5), 4, 1)
        pygame.draw.circle(surf, (255, 255, 255), (gx - 2, CROWN_Y + 3), 1)  # glint
    pygame.draw.line(surf, _BRASS, (HX - 1, CROWN_Y + 5), (HX + 1, CROWN_Y + 5), 2)
    pygame.draw.circle(surf, _BRASS_H, (HX + 5, CROWN_Y + 3), 1)

    # ── Pilot eye on the exposed face ───────────────────────────────────────
    # The base sprite's eye lived in the aviators we dropped, so give the face a
    # single alert eye peeking out below the goggles, ahead of the beak base.
    pygame.draw.circle(surf, (26, 22, 18), (HX + 6, HY + 1), 3)
    pygame.draw.circle(surf, (20, 16, 14), (HX + 6, HY + 1), 2)
    pygame.draw.circle(surf, (255, 255, 255), (HX + 5, HY), 1)


build = _make_skin(_paint, base_fn=_ace_base)
