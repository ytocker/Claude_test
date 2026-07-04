"""DISCO — Design 4: THE SELECTOR (funky-soul DJ).

A scratch costume builder for the disco-skin exploration: Pip kept in his
natural scarlet-macaw plumage (red head / blue wings / gold beak) with the
DJ kit layered ON TOP, so the read is "parrot who spins records", not a
recolour. Exploration only — NOT registered in ``store_skins.BUILDERS``.

Ranked by what has to survive at 40px in motion: a black VINYL RECORD held
at the near wing is the sole hero prop — it owns the one bold dark circle on
the bird, so nothing else is allowed to rival it in darkness. The DJ
headphones read off the EAR-CUP, not the band: a desaturated charcoal cup
ringed in silver sits at true ear height on the side of the skull, while the
band stays a muted steel arc so it never flares white like a shock of hair.
Amber AVIATOR SHADES tint the face lightly enough that the eye-glint still
shows through; a saturated burnt-orange satin collar is the one warm garment
accent, set a full value step above a cool chestnut blazer so the two cloth
layers never fuse; platform suede clogs cap the feet.
"""
import sys, os; sys.path.insert(0, '/home/user/skybit')

import pygame

from game.store_skins import _make_skin, _poly, HX, HY, CROWN_Y
from game.parrot import _build_frame


# The band is deliberately a muted steel with no bright top glint — a bright
# chrome highlight over the crown read as white hair at 40px. The headphone
# read is carried by the ear-cup instead: a desaturated charcoal (kept well
# lighter than the vinyl so the record stays the single bold dark circle)
# under a silver rim ring. Collar/blazer are split by a full value step AND a
# hue split (warm satin vs. cool chestnut) so they read as two garments.
_SEL_CHROME   = (150, 154, 160)    # muted band steel / connector arm
_SEL_CHROME_D = (100, 103, 110)    # band under-shadow
_SEL_RIM      = (190, 194, 200)    # ear-cup silver rim ring
_SEL_EARCUP   = (58, 60, 66)       # desaturated charcoal cup (vinyl stays darker)
_SEL_EARCUP_C = (40, 42, 48)       # cup speaker centre
_SEL_GOLD     = (212, 175, 80)     # aviator frame gold
_SEL_COLLAR   = (216, 102, 30)     # saturated burnt-orange satin — the one warm accent
_SEL_COLLAR_H = (244, 146, 62)     # satin sheen
_SEL_BLAZER   = (70, 48, 40)       # cool chestnut blazer, a value step under the collar
_SEL_BLAZER_E = (38, 26, 22)       # dark lapel edge line (defines the coat at 40px)
_SEL_VINYL    = (20, 20, 24)       # black wax disc — THE bold dark circle
_SEL_VINYL_H  = (245, 246, 250)    # gloss-sweep highlight
_SEL_LABEL    = (236, 150, 50)     # orange record label
_SEL_WOOD     = (196, 154, 98)     # natural-wood platform sole


def _tinted_lens(surf, cx, cy, w, h, rgba, frame):
    """Amber aviator lens with a thin gold frame. Blitted from its own SRCALPHA
    patch so the tint alpha-BLENDS over Pip's eye (pygame.draw would overwrite
    the pixel with the tint's alpha instead of compositing). The tint is kept
    light so an eye-glint still shows through and the face doesn't go blank."""
    lens = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(lens, rgba, lens.get_rect(), border_radius=2)
    surf.blit(lens, (cx - w // 2, cy - h // 2))
    pygame.draw.rect(surf, frame, (cx - w // 2, cy - h // 2, w, h), 1, border_radius=2)


def _paint_selector(surf, _a):
    # ── BODY: a chestnut blazer coat blanketing the lower body — the broad
    # right panel also buries the natural green wing-tip that otherwise flickers
    # as a stray green pixel at the lower-right at 40px. Cool + dark so it sits a
    # clear value step under the warm collar laid over it next.
    _poly(surf, _SEL_BLAZER, [(HX - 4, HY + 6), (HX - 9, HY + 20), (24, 58)])
    _poly(surf, _SEL_BLAZER, [(HX + 5, HY + 6), (HX + 10, HY + 20), (48, 60)])
    _poly(surf, _SEL_BLAZER, [(HX + 4, HY + 8), (63, HY + 7), (61, HY + 24), (46, HY + 22)])
    # Thin dark lapel edges give the coat a defined silhouette at the downscale.
    pygame.draw.line(surf, _SEL_BLAZER_E, (HX - 4, HY + 6), (25, 57), 1)
    pygame.draw.line(surf, _SEL_BLAZER_E, (HX + 5, HY + 6), (63, HY + 7), 1)
    pygame.draw.line(surf, _SEL_BLAZER_E, (63, HY + 7), (61, HY + 24), 1)
    # Pointed satin collar wings — the one saturated warm garment accent, riding
    # over the blazer so the hue/value split reads as collar-on-coat.
    left = [(HX - 9, HY - 3), (HX - 1, HY - 1), (HX - 5, HY + 8)]
    right = [(HX + 8, HY - 3), (HX, HY - 1), (HX + 4, HY + 8)]
    _poly(surf, _SEL_COLLAR, left)
    _poly(surf, _SEL_COLLAR, right)
    pygame.draw.line(surf, _SEL_COLLAR_H, (HX - 8, HY - 2), (HX - 5, HY + 7), 1)
    pygame.draw.line(surf, _SEL_COLLAR_H, (HX + 7, HY - 2), (HX + 4, HY + 7), 1)

    # ── WING: the hero VINYL RECORD held at the near wing tip, and the ONLY bold
    # dark circle allowed on the bird. Black wax disc, a bright orange label
    # pushed large (r=4) so the colour survives, and a single white gloss sweep
    # so it reads as spinning wax catching the light — not a punched black hole.
    vx, vy = 22, 52
    pygame.draw.circle(surf, _SEL_VINYL, (vx, vy), 8)
    pygame.draw.circle(surf, (48, 48, 54), (vx, vy), 8, 1)      # rim lift off body
    disc = pygame.Rect(vx - 7, vy - 7, 14, 14)
    pygame.draw.arc(surf, _SEL_VINYL_H, disc, 0.5, 1.9, 1)      # gloss sweep
    pygame.draw.circle(surf, _SEL_LABEL, (vx, vy), 4)
    pygame.draw.circle(surf, _SEL_VINYL, (vx, vy), 1)           # spindle hole

    # ── FEET: platform suede clogs — a chestnut suede upper on a thick natural-
    # wood sole, one over each foot so the platform reads as a matched pair.
    for fx in (24, 32):
        pygame.draw.rect(surf, _SEL_BLAZER, (fx, 70, 8, 4), border_radius=1)
        pygame.draw.rect(surf, _SEL_WOOD, (fx - 1, 74, 10, 3), border_radius=1)

    # ── HEAD: amber aviator shades (light tint, so the eye-glint reads through),
    # then the muted-steel band and the ear-cup that actually sells the phones.
    _tinted_lens(surf, HX - 4, HY - 1, 7, 4, (200, 140, 40, 110), _SEL_GOLD)
    _tinted_lens(surf, HX + 6, HY - 1, 7, 4, (200, 140, 40, 110), _SEL_GOLD)

    # Foam band bows up over the skull in two muted-steel values (no bright glint
    # — that read as white hair). The near arm drops from the band to the cup.
    band = [(HX - 10, CROWN_Y), (HX - 2, CROWN_Y - 6), (HX + 6, CROWN_Y)]
    pygame.draw.lines(surf, _SEL_CHROME_D, False, band, 4)
    pygame.draw.lines(surf, _SEL_CHROME, False, band, 3)
    pygame.draw.line(surf, _SEL_CHROME_D, (HX + 6, CROWN_Y), (HX + 8, HY - 3), 3)
    pygame.draw.line(surf, _SEL_CHROME, (HX + 6, CROWN_Y), (HX + 8, HY - 3), 2)
    # Round charcoal ear-cup at TRUE EAR HEIGHT on the side of the skull, ringed
    # in silver. Desaturated so it clearly reads as a cup yet never rivals the
    # vinyl as the bold dark circle; sat low (HY+2) so it can't be taken for an
    # eye and stays value-separated from the amber lens above it.
    pygame.draw.circle(surf, _SEL_EARCUP, (HX + 8, HY + 2), 6)
    pygame.draw.circle(surf, _SEL_RIM, (HX + 8, HY + 2), 6, 2)
    pygame.draw.circle(surf, _SEL_EARCUP_C, (HX + 8, HY + 2), 2)


build = _make_skin(_paint_selector, base_fn=_build_frame)
