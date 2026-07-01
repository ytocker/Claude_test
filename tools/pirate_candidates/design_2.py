"""PARROT'S PARROT — the iconic pirate-with-a-companion buccaneer candidate.

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_pirate`` is untouched. Builds on the ORIGINAL pirate (slate tricorn +
continuous gold brim + white skull cockade + eyepatch + gold earring) and
enriches it across more body zones for a richer read:

  * a bold green companion macaw perched HIGH on the back-left so it clears
    Pip's wing and breaks the rear outline against open sky — the signature: a
    second, living creature recognisable at 40px, built from two clean masses
    (body oval + separated head) with a black hooked beak as the parrot cue;
  * a dark-red headscarf/bandana wrapping the crown UNDER the tricorn, reading
    by VALUE against the scarlet head, with one bold sky-side knot tail.

The chest is left deliberately CLEAN — the crowded zone carries nothing, so the
companion stays the unmistakable signature. The scarlet macaw body is untouched;
everything here is an OVERLAY. The 40px truth read, in order of value: the slate
tricorn + gold brim + white skull (the kept pirate anchor), then the green
second bird breaking the back silhouette, then the dark bandana band. Gold lives
in exactly two places — the hat brim and the companion's cheek — and nowhere
else, so the anchor stays the brightest read.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Companion macaw — green/yellow so the second bird POPS as a distinct
# creature against both the scarlet body and the sky at 40px.
_COMP_GREEN   = (47, 168, 90)      # #2FA85A body
_COMP_GREEN_D = (28, 112, 58)      # shadow / wing
_COMP_GREEN_H = (96, 206, 132)     # lit crown edge
_COMP_GOLD    = (242, 197, 61)     # #F2C53D chest/face splash
_COMP_GOLD_H  = (255, 226, 130)
_COMP_BEAK    = (38, 32, 30)       # near-black horn beak
_COMP_EYE     = (24, 20, 22)

# Dark-red bandana wrapping the crown under the tricorn. The SHADOW tone is the
# dominant fill: against Pip's scarlet head the wrap must read by value (a darker
# band over a brighter crown), not by hue.
_BAND_RED   = (192, 57, 43)        # #C0392B (kept for reference)
_BAND_RED_D = (126, 32, 24)        # #7E2018 — dominant dark band
_BAND_RED_H = (224, 104, 88)

# Kept pirate palette (mirrors store_skins._paint_pirate so the anchor reads
# identically — felt, gold trim, skull, earring).
_FELT   = (74, 78, 96)
_FELT_D = (48, 52, 70)
_FELT_H = (120, 126, 150)
_TRIM   = (255, 205, 70)
_TRIM_H = (255, 240, 160)
_GOLD   = (255, 205, 70)
_SKULL  = (244, 246, 240)


def _paint_companion(surf, wing_angle_deg):
    """The signature second creature: a ~12px green macaw perched HIGH on the
    back-left, in the open sky behind Pip. Deliberately built from only TWO bold
    masses — one clean green body oval + a clearly separated round head with a
    black HOOKED BEAK jutting forward into the gap toward Pip. That beak is the
    "this is a parrot" cue; everything else is subtracted so it never mushes into
    a blob at 40px. One gold accent (the cheek patch) and one eye-white catch
    carry the face; a 1px dark forward edge keeps it off Pip's scarlet head."""
    bob = int(round(wing_angle_deg * 0.06))
    # Pushed further back-left and up into empty sky so its forward edge clears
    # Pip's crown on every wing-beat frame.
    cx, cy = HX - 25, CROWN_Y + 2 + bob

    # Body — one plump DARK-green oval. Leaning the lower body on the dark tone
    # sets up the value break: a dark body under a light head reads "bird" at
    # 40px with no internal detail. The mid-green only catches the upper turn.
    pygame.draw.ellipse(surf, _COMP_GREEN_D, (cx - 8, cy - 5, 17, 16))
    pygame.draw.ellipse(surf, _COMP_GREEN_D, (cx - 7, cy - 5, 15, 14))
    pygame.draw.ellipse(surf, _COMP_GREEN, (cx - 6, cy - 4, 11, 7))

    # Head — a distinctly separated round mass filled with the LIGHT green so it
    # wins as the bright end of the silhouette (light head over dark body =
    # "bird looking up-and-forward"). A 1px dark gap below keeps head/body split.
    hx, hy = cx + 6, cy - 6
    pygame.draw.circle(surf, _COMP_GREEN_D, (hx, hy), 6)
    pygame.draw.circle(surf, _COMP_GREEN_H, (hx, hy), 5)
    pygame.draw.circle(surf, (180, 232, 196), (hx - 1, hy - 2), 2)

    # The hooked beak — the key parrot cue. A solid black 3px wedge angled clearly
    # down-and-forward; at 40px this dark notch on the bright head IS the parrot
    # read, so it's the thickest mark on the companion.
    _poly(surf, _COMP_BEAK, [(hx + 3, hy - 1), (hx + 11, hy + 2),
                             (hx + 8, hy + 5), (hx + 4, hy + 4)])
    # Hook curl at the tip so it reads as a parrot's, not a sparrow's, beak.
    pygame.draw.line(surf, _COMP_BEAK, (hx + 10, hy + 2), (hx + 8, hy + 5), 3)

    # ONE gold accent only — the macaw cheek, a 2-3px crescent on the head's
    # forward-LOWER edge so it sits half-on-green / half-against-sky where the
    # value break makes it a visible spark (and doubles as the macaw cue).
    pygame.draw.circle(surf, _COMP_GOLD, (hx + 3, hy + 3), 3)
    pygame.draw.circle(surf, _COMP_GREEN_H, (hx + 1, hy + 2), 2)
    pygame.draw.circle(surf, _COMP_GOLD_H, (hx + 4, hy + 4), 1)

    # Eye + white catch so the tiny head reads as a face.
    pygame.draw.circle(surf, _COMP_EYE, (hx + 2, hy - 1), 1)
    pygame.draw.circle(surf, (235, 238, 240), (hx + 3, hy - 1), 1)

    # 1px dark separation along the companion's FORWARD edge so its green never
    # fuses with Pip's scarlet head/crown beside it.
    pygame.draw.line(surf, _COMP_GREEN_D, (cx + 7, cy - 3), (cx + 4, cy + 6), 1)

    # Tiny perched feet gripping Pip's back so it reads as standing on him.
    pygame.draw.line(surf, _COMP_BEAK, (cx - 1, cy + 9), (cx, cy + 11), 1)
    pygame.draw.line(surf, _COMP_BEAK, (cx + 3, cy + 9), (cx + 4, cy + 11), 1)


def _paint_bandana(surf):
    """A headscarf wrapping the crown UNDER the tricorn. Against Pip's scarlet
    head, hue alone vanishes — so the wrap reads by VALUE: a DARK band (the
    bandana shadow tone is the dominant fill) over the brighter scarlet crown,
    with one crisp highlight crease. One knot tail is pushed BACK-LEFT into open
    sky with a dark outline so it breaks the silhouette instead of the body."""
    # Wrap band hugging the upper head — dark tone dominant so it reads as a
    # darker band laid over the brighter head, not as same-value red-on-red.
    band = [(HX - 12, HY - 4), (HX - 5, HY - 8), (HX + 9, HY - 8),
            (HX + 13, HY - 3), (HX + 12, HY + 1), (HX - 11, HY + 1)]
    _poly(surf, (90, 22, 16), band)               # near-maroon outline
    inner = [(HX - 11, HY - 4), (HX - 5, HY - 7), (HX + 9, HY - 7),
             (HX + 12, HY - 3), (HX + 11, HY), (HX - 10, HY)]
    _poly(surf, _BAND_RED_D, inner)               # dark red dominant fill
    # One crisp highlight crease so the dark band reads as cloth, not a void.
    pygame.draw.line(surf, _BAND_RED_H, (HX - 8, HY - 4), (HX + 8, HY - 5), 1)

    # ONE bold knot tail pushed DOWN-AND-BACK so its dark-maroon shape clears the
    # back-of-head/neck outline against the sky — a tail breaking the silhouette
    # is visible at 40px where a band buried in the head is not.
    kx, ky = HX - 11, HY + 2
    pygame.draw.circle(surf, (90, 22, 16), (kx, ky), 4)
    pygame.draw.circle(surf, _BAND_RED_D, (kx, ky), 3)
    tail = [(kx, ky + 1), (kx - 5, ky + 5), (kx - 9, ky + 11)]
    pygame.draw.lines(surf, (90, 22, 16), False, tail, 4)
    pygame.draw.lines(surf, _BAND_RED_D, False, tail, 3)
    pygame.draw.line(surf, _BAND_RED_H, (kx - 1, ky + 1), (kx - 5, ky + 4), 1)


def _paint_pirate_core(surf):
    """The KEPT pirate anchor — gold hoop earring, eyepatch over the near eye,
    slate tricorn lifted off the crown with a continuous bright gold brim band,
    and the big white skull cockade dead-centre-front. Mirrors the original
    ``store_skins._paint_pirate`` so the identity read is unchanged."""
    # Gold hoop earring under the head.
    pygame.draw.circle(surf, _GOLD, (HX - 8, HY + 10), 3, 2)
    pygame.draw.circle(surf, _TRIM_H, (HX - 9, HY + 9), 1)

    # Eyepatch over the NEAR (right) eye + a strap up over the crown.
    pygame.draw.line(surf, _FELT_D, (HX + 11, HY - 2), (HX - 6, CROWN_Y), 2)
    pygame.draw.ellipse(surf, _FELT_D, (HX + 6, HY - 5, 9, 9))
    pygame.draw.ellipse(surf, _FELT, (HX + 7, HY - 4, 7, 7))

    # Tricorn lifted a row higher so the brim breaks the crown outline. Sits
    # ON TOP of the bandana wrap painted earlier.
    cy = CROWN_Y - 3
    brim = [(HX - 17, cy + 5), (HX - 5, cy - 7), (HX + 4, cy - 8),
            (HX + 16, cy + 4), (HX + 6, cy + 9), (HX - 6, cy + 9)]
    pygame.draw.polygon(surf, _FELT_D, brim)
    inner = [(HX - 14, cy + 4), (HX - 4, cy - 5), (HX + 3, cy - 6),
             (HX + 13, cy + 3), (HX + 5, cy + 7), (HX - 5, cy + 7)]
    pygame.draw.polygon(surf, _FELT, inner)
    pygame.draw.polygon(surf, _FELT_H, [(HX - 4, cy - 5), (HX + 3, cy - 6),
                                        (HX + 2, cy - 2), (HX - 3, cy - 2)])
    # One continuous bright gold band tracing the whole brim edge — the read.
    band = [(HX - 15, cy + 4), (HX - 4, cy - 5), (HX + 3, cy - 6),
            (HX + 14, cy + 3)]
    pygame.draw.lines(surf, _TRIM, False, band, 2)
    pygame.draw.lines(surf, _TRIM_H, False,
                      [(HX - 13, cy + 3), (HX - 4, cy - 6), (HX + 3, cy - 7)], 1)
    # Big white skull cockade dead-centre-front.
    sx, sy = HX, cy + 1
    pygame.draw.circle(surf, _SKULL, (sx, sy), 4)
    pygame.draw.polygon(surf, _SKULL, [(sx - 3, sy + 2), (sx + 3, sy + 2),
                                       (sx + 1, sy + 5), (sx - 1, sy + 5)])
    pygame.draw.circle(surf, (40, 30, 40), (sx - 2, sy - 1), 1)
    pygame.draw.circle(surf, (40, 30, 40), (sx + 2, sy - 1), 1)


def _paint(surf, wing_angle_deg):
    # Back-to-front draw order: companion (behind/on the back) first, then the
    # bandana wrap, then the kept tricorn/skull anchor on top so the hat sits
    # over the wrap and the read priority is preserved. The chest is left CLEAN
    # — the companion is the signature, so the crowded zone carries nothing.
    _paint_companion(surf, wing_angle_deg)
    _paint_bandana(surf)
    _paint_pirate_core(surf)


build = store_skins._make_skin(_paint)
