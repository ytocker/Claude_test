"""DISCO — Design 4: THE SELECTOR (funky-soul DJ).

A scratch costume builder for the disco-skin exploration: Pip kept in his
natural scarlet-macaw plumage (red head / blue wings / gold beak) with the
DJ kit layered ON TOP, so the read is "parrot who spins records", not a
recolour. Exploration only — NOT registered in ``store_skins.BUILDERS``.

Ranked by what has to survive at 40px in motion: a black VINYL RECORD held
at the near wing is the hero prop (one colour label + a white gloss sweep so
it reads as spinning wax, not a hole); foam DJ HEADPHONES arc the crown with
one big dark ear-cup breaking the silhouette; amber AVIATOR SHADES tint the
face; a burnt-orange satin wide collar + chestnut blazer lapels dress the
body; platform suede clogs cap the feet. Chrome/steel carries a highlight
edge because metal only reads as metal if it glints at the downscale.
"""
import sys, os; sys.path.insert(0, '/home/user/skybit')

import pygame

from game.store_skins import _make_skin, _poly, HX, HY, CROWN_Y
from game.parrot import _build_frame


# Foam-headphone chrome gets three values so the band reads as a rounded bar,
# not a flat line, after the 40px downscale; the satin/blazer browns are held
# apart by a full value step so the collar doesn't muddy into the lapels.
_SEL_CHROME   = (200, 205, 210)    # foam-band chrome / ear-cup ring
_SEL_CHROME_D = (128, 133, 140)    # band under-shadow
_SEL_CHROME_H = (238, 242, 246)    # band top glint
_SEL_EARCUP   = (40, 40, 44)       # dark foam ear-cup
_SEL_GOLD     = (212, 175, 80)     # aviator frame gold
_SEL_COLLAR   = (181, 86, 30)      # burnt-orange satin collar
_SEL_COLLAR_H = (214, 118, 52)     # satin sheen
_SEL_BLAZER   = (107, 74, 43)      # chestnut blazer lapel
_SEL_VINYL    = (22, 22, 26)       # black wax disc
_SEL_VINYL_H  = (245, 246, 250)    # gloss-sweep highlight
_SEL_LABEL    = (232, 160, 62)     # orange record label
_SEL_WOOD     = (196, 154, 98)     # natural-wood platform sole


def _tinted_lens(surf, cx, cy, w, h, rgba, frame):
    """Amber aviator lens with a thin gold frame. Blitted from its own SRCALPHA
    patch so the tint alpha-BLENDS over Pip's eye (pygame.draw would overwrite
    the pixel with the tint's alpha instead of compositing)."""
    lens = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(lens, rgba, lens.get_rect(), border_radius=2)
    surf.blit(lens, (cx - w // 2, cy - h // 2))
    pygame.draw.rect(surf, frame, (cx - w // 2, cy - h // 2, w, h), 1, border_radius=2)


def _paint_selector(surf, _a):
    # ── BODY: burnt-orange satin wide collar flanking the neck, chestnut blazer
    # lapels falling to the body sides. Drawn first so the head/headphones sit
    # over the collar points the way a real collar tucks under the jaw.
    _poly(surf, _SEL_BLAZER, [(HX - 4, HY + 6), (HX - 9, HY + 20), (24, 58)])
    _poly(surf, _SEL_BLAZER, [(HX + 5, HY + 6), (HX + 10, HY + 20), (48, 60)])
    # Pointed satin collar wings (two triangles) with a single sheen edge each.
    left = [(HX - 9, HY - 3), (HX - 1, HY - 1), (HX - 5, HY + 8)]
    right = [(HX + 8, HY - 3), (HX, HY - 1), (HX + 4, HY + 8)]
    _poly(surf, _SEL_COLLAR, left)
    _poly(surf, _SEL_COLLAR, right)
    pygame.draw.line(surf, _SEL_COLLAR_H, (HX - 8, HY - 2), (HX - 5, HY + 7), 1)
    pygame.draw.line(surf, _SEL_COLLAR_H, (HX + 7, HY - 2), (HX + 4, HY + 7), 1)

    # ── WING: the hero VINYL RECORD held at the near wing tip. Black wax disc,
    # a bright orange label, and a single white gloss sweep across the face so
    # it reads as spinning wax catching the light — not a punched black hole.
    vx, vy = 22, 52
    pygame.draw.circle(surf, _SEL_VINYL, (vx, vy), 8)
    pygame.draw.circle(surf, (48, 48, 54), (vx, vy), 8, 1)      # rim lift off body
    disc = pygame.Rect(vx - 7, vy - 7, 14, 14)
    pygame.draw.arc(surf, _SEL_VINYL_H, disc, 0.5, 1.9, 1)      # gloss sweep
    pygame.draw.circle(surf, _SEL_LABEL, (vx, vy), 3)
    pygame.draw.circle(surf, _SEL_VINYL, (vx, vy), 1)           # spindle hole

    # ── FEET: platform suede clogs — a chestnut suede upper on a thick natural-
    # wood sole, one over each foot so the platform reads as a matched pair.
    for fx in (24, 32):
        pygame.draw.rect(surf, _SEL_BLAZER, (fx, 70, 8, 4), border_radius=1)
        pygame.draw.rect(surf, _SEL_WOOD, (fx - 1, 74, 10, 3), border_radius=1)

    # ── HEAD: amber aviator shades over Pip's eyes (tint blends so the eye still
    # shows), then the foam DJ headphones arcing the crown with one big ear-cup.
    _tinted_lens(surf, HX - 4, HY - 1, 7, 4, (200, 140, 40, 150), _SEL_GOLD)
    _tinted_lens(surf, HX + 6, HY - 1, 7, 4, (200, 140, 40, 150), _SEL_GOLD)

    # Foam band bows up over the skull (three values so the bar reads rounded).
    band = [(HX - 10, CROWN_Y), (HX - 2, CROWN_Y - 6), (HX + 6, CROWN_Y)]
    pygame.draw.lines(surf, _SEL_CHROME_D, False, band, 4)
    pygame.draw.lines(surf, _SEL_CHROME, False, band, 3)
    pygame.draw.lines(surf, _SEL_CHROME_H, False,
                      [(HX - 9, CROWN_Y - 1), (HX - 2, CROWN_Y - 6)], 1)
    # Big near-side foam ear-cup, ringed in chrome so the dark disc reads as a
    # cup breaking the head silhouette, not a shadow.
    pygame.draw.circle(surf, _SEL_EARCUP, (HX + 8, HY - 2), 6)
    pygame.draw.circle(surf, _SEL_CHROME, (HX + 8, HY - 2), 6, 1)
    pygame.draw.circle(surf, _SEL_CHROME_H, (HX + 6, HY - 4), 1)


build = _make_skin(_paint_selector, base_fn=_build_frame)
