"""DISCO Design 1 — BOOGIE NIGHTS: a Saturday Night Fever floor-filler for Pip.

Scratch exploration only; NOT registered in store_skins.BUILDERS, so no live
skin is touched. Rendered in-gameplay through tools/ninja_render.py.

The concept keeps Pip a scarlet macaw — red head, blue wing tips and gold beak
stay fully visible — and layers the '77 disco kit ON TOP so the read is "the
bird got dressed", not "the bird got recoloured". Built from the natural
_build_frame base for exactly that reason.

At 40px the stack reads, in order of value: (1) a big round DARK-BROWN AFRO
that fattens the head silhouette into a huge circle no other skin has, (2) the
CREAM leisure-suit lapels splitting open over a rust shirt strip with a gold
medallion glinting dead-centre chest, (3) a flared bell-bottom cuff on the
wing that widens on the downstroke so the disco kit moves with the flap, and
(4) chunky cream platform boots on wood soles poking below the body. Every
object is a bold mass + one bright accent so it survives the downscale.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly
from game.parrot import _build_frame

# Afro: dark chocolate mass with a warmer rim so the round dome reads as hair,
# not a hat, and a near-black keyline where it meets the scarlet head so the two
# masses don't fuse at 40px.
_AFRO      = (90, 58, 33)
_AFRO_RIM  = (120, 80, 45)          # lighter top-left rim highlight
_AFRO_DK   = (58, 36, 20)           # keyline / lower-fold shadow
_AFRO_TEX  = (74, 46, 26)           # curl-texture shadow dots

# Gold for the pick + medallion — one continuous bright note per object so metal
# reads as metal on both the day and the night sky.
_GOLD      = (232, 192, 72)
_GOLD_H    = (255, 236, 150)
_GOLD_D    = (168, 128, 40)

# Leisure suit: warm cream, not paper-white, so it separates from both the sky
# and the astronaut/tennis whites; the rust shirt strip is the hot centre.
_CREAM     = (245, 240, 228)
_CREAM_D   = (206, 200, 184)        # cloth fold / lapel keyline
_CREAM_H   = (255, 254, 246)
_RUST      = (196, 84, 40)          # exposed shirt strip
_RUST_D    = (150, 58, 26)

# Platform boots: cream upper on a stacked wood sole (two values so the wedge
# reads as a chunky heel, not a flat bar).
_WOOD      = (160, 110, 55)
_WOOD_D    = (116, 78, 38)


def _paint_boogie(surf, wing_angle_deg):
    BCX, BCY = 32, 52               # body ellipse centre in composite space

    # ── Platform boots first, at the base of the body so the body/tail overlap
    #    their roots and only the chunky soles poke below the silhouette. Two
    #    boots (near + far foot); each is a cream upper stacked on a wood wedge
    #    heel so the disco "lift" reads even after the downscale.
    for bx in (25, 33):
        pygame.draw.rect(surf, _CREAM_D, (bx - 4, 69, 9, 6), border_radius=2)
        pygame.draw.rect(surf, _CREAM, (bx - 4, 68, 9, 5), border_radius=2)
        pygame.draw.line(surf, _CREAM_H, (bx - 3, 69), (bx + 3, 69), 1)
        # Stacked wood platform sole — a shallow wedge, lit top edge so it reads
        # as a raised heel and not a shadow.
        _poly(surf, _WOOD_D, [(bx - 5, 74), (bx + 6, 74), (bx + 5, 78), (bx - 4, 78)])
        _poly(surf, _WOOD, [(bx - 5, 74), (bx + 6, 74), (bx + 5, 76), (bx - 5, 76)])

    # ── Bell-bottom cuff flaring off the wing tip. The base wing angles run
    #    negative-on-downstroke, so a share of -wing_angle_deg widens the flare:
    #    the trumpet mouth opens as Pip drives down, closes on the up-beat — the
    #    disco kit animates with the flap. Anchored at the lower-left wing tip.
    cx, cy = 23, 52
    flare = 4 + max(0.0, -wing_angle_deg) * 0.11
    ftop = 3
    cuff = [(cx - ftop, cy - 5), (cx + ftop, cy - 5),
            (cx + flare, cy + 7), (cx - flare, cy + 7)]
    _poly(surf, _CREAM_D, [(x, y + 1) for x, y in cuff])
    _poly(surf, _CREAM, cuff)
    pygame.draw.line(surf, _CREAM_H, (cx - ftop + 1, cy - 4), (cx + ftop - 1, cy - 4), 1)
    # Cuff seam so the flared mouth reads as a hem, not a blob.
    pygame.draw.line(surf, _CREAM_D, (cx - flare + 1, cy + 6),
                     (cx + flare - 1, cy + 6), 1)

    # ── White leisure-suit jacket: two big pointed lapels flanking the chest,
    #    splitting open over a rust shirt strip down the centre-line. Kept inside
    #    x≈22..44 so the blue wing tip and scarlet flank still show past the coat.
    _poly(surf, _RUST, [(BCX - 3, BCY - 10), (BCX + 3, BCY - 10),
                        (BCX + 2, BCY + 8), (BCX - 2, BCY + 8)])   # shirt strip
    pygame.draw.line(surf, _RUST_D, (BCX, BCY - 9), (BCX, BCY + 7), 1)

    # Left lapel — a cream triangle from the collar point down to the open V.
    left = [(BCX + 1, BCY - 11), (BCX - 12, BCY - 6), (BCX - 2, BCY + 7)]
    _poly(surf, _CREAM_D, [(x, y + 1) for x, y in left])
    _poly(surf, _CREAM, left)
    pygame.draw.line(surf, _CREAM_H, (BCX, BCY - 10), (BCX - 10, BCY - 6), 1)
    # Right lapel — mirrored, its point breaking toward the near shoulder.
    right = [(BCX - 1, BCY - 11), (BCX + 11, BCY - 5), (BCX + 3, BCY + 7)]
    _poly(surf, _CREAM_D, [(x, y + 1) for x, y in right])
    _poly(surf, _CREAM, right)
    pygame.draw.line(surf, _CREAM_H, (BCX, BCY - 10), (BCX + 9, BCY - 5), 1)
    # Lapel keylines so the two cream planes stay distinct where they meet.
    pygame.draw.line(surf, _CREAM_D, (BCX + 1, BCY - 10), (BCX - 2, BCY + 6), 1)

    # Gold medallion on a chain, glinting dead-centre chest — the disco heart.
    mx, my = BCX, BCY + 2
    pygame.draw.line(surf, _GOLD_D, (BCX - 4, BCY - 9), (mx, my - 4), 1)
    pygame.draw.line(surf, _GOLD_D, (BCX + 4, BCY - 8), (mx, my - 4), 1)
    pygame.draw.circle(surf, _GOLD_D, (mx, my), 4)
    pygame.draw.circle(surf, _GOLD, (mx, my), 3)
    pygame.draw.circle(surf, _GOLD_H, (mx - 1, my - 1), 1)

    # ── Oversized round AFRO built as a bumpy dome of overlapping puffs so the
    #    head silhouette reads huge and ROUND. Puff centres kept high enough that
    #    the near eye + gold beak still peek out below the hairline. Drawn LAST so
    #    it owns the crown.
    puffs = ((HX - 4, CROWN_Y - 3, 14), (HX - 11, CROWN_Y, 9),
             (HX + 3, CROWN_Y - 1, 10), (HX - 3, CROWN_Y - 7, 10))
    # Near-black keyline first (a fraction larger) so the brown mass separates
    # from the scarlet head where they overlap.
    for px, py, r in puffs:
        pygame.draw.circle(surf, _AFRO_DK, (px, py), r + 1)
    for px, py, r in puffs:
        pygame.draw.circle(surf, _AFRO, (px, py), r)
    # Curl texture — a few shadow dots on the lower-right face so the dome reads
    # as packed hair, not a smooth helmet.
    for tx, ty in ((HX + 4, CROWN_Y + 4), (HX - 2, CROWN_Y + 6),
                   (HX - 9, CROWN_Y + 3)):
        pygame.draw.circle(surf, _AFRO_TEX, (tx, ty), 2)
    # Warm rim highlight catching light on the top-left curls.
    for hx, hy, r in ((HX - 9, CROWN_Y - 4, 4), (HX - 3, CROWN_Y - 9, 4),
                      (HX + 2, CROWN_Y - 6, 3)):
        pygame.draw.circle(surf, _AFRO_RIM, (hx, hy), r)

    # Tiny gold hair-pick tucked into the side of the afro, sticking out — the
    # period detail that says "disco", 3px comb on a short handle.
    pkx, pky = HX - 15, CROWN_Y - 2
    pygame.draw.line(surf, _GOLD_D, (pkx, pky + 3), (pkx + 3, pky - 1), 2)
    pygame.draw.line(surf, _GOLD, (pkx, pky + 3), (pkx + 3, pky - 1), 1)
    for i in range(3):
        tx = pkx - 2 + i
        pygame.draw.line(surf, _GOLD, (tx, pky - 1), (tx - 1, pky - 3), 1)
    pygame.draw.circle(surf, _GOLD_H, (pkx + 3, pky - 1), 1)


build = store_skins._make_skin(_paint_boogie, base_fn=_build_frame)
