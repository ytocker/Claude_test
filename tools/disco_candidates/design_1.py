"""DISCO Design 1 — BOOGIE NIGHTS: a Saturday Night Fever floor-filler for Pip.

Scratch exploration only; NOT registered in store_skins.BUILDERS, so no live
skin is touched. Rendered in-gameplay through tools/ninja_render.py.

The concept keeps Pip a scarlet macaw — red head, blue wing tips and gold beak
stay fully visible — and layers the '77 disco kit ON TOP so the read is "the
bird got dressed", not "the bird got recoloured". Built from the natural
_build_frame base for exactly that reason.

At 40px the stack reads, in order of value: (1) an ESPRESSO near-black AFRO
whose lumpy silhouette separates it from both sandstone pillars (day) and the
night sky, (2) a single bright CREAM jacket panel wrapping the forward chest
with the collar opening as a triangular notch at the throat — a strict side
profile, not a front-on V — carrying ONE gold medallion on a plunging chain,
(3) a cream bell-bottom cuff whose trumpet mouth flares PAST the wing tip into
open sky so it reads against the background, and (4) chunky cream platform boots
on tall two-value wood wedges poking below the body. Every object is a bold mass
+ one bright accent so it survives the downscale.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly
from game.parrot import _build_frame

# Afro: cool espresso near-black so the round dome separates from the sandstone
# pillars on the day sky AND holds contrast against the night sky — a warm brown
# fused into both. A slightly lighter face-value + a near-black keyline give the
# lumps a readable inner form without going milky.
_AFRO      = (45, 34, 38)           # cool espresso near-black mass
_AFRO_RIM  = (78, 60, 62)           # cool top-left rim so curls catch light
_AFRO_DK   = (26, 19, 22)           # keyline / lump-fold shadow
_AFRO_TEX  = (34, 25, 28)           # curl-texture shadow dots

# Gold for the medallion — one continuous bright note so metal reads as metal on
# both the day and the night sky.
_GOLD      = (240, 198, 74)
_GOLD_H    = (255, 240, 158)
_GOLD_D    = (150, 110, 34)

# Leisure suit: warm cream, not paper-white, so it separates from both the sky
# and the astronaut/tennis whites. The lapel V is the bright hero shape now — no
# muddy rust strip competing at the centre.
_CREAM     = (245, 240, 228)
_CREAM_D   = (206, 200, 184)        # cloth fold / lapel keyline
_CREAM_H   = (255, 254, 246)

# Platform boots: cream upper on a stacked wood sole (two values so the tall
# wedge reads as a chunky lift, not a flat bar).
_WOOD      = (166, 114, 58)
_WOOD_D    = (108, 72, 34)


def _paint_boogie(surf, wing_angle_deg):
    BCX, BCY = 32, 52               # body ellipse centre in composite space

    # ── Platform boots first, at the base of the body so the body/tail overlap
    #    their roots and only the chunky soles poke below the silhouette. Taller,
    #    wider wood wedges with a clear two-value step so the disco "lift" reads
    #    below the body even after the downscale; bright cream uppers cap them.
    for bx in (24, 34):
        pygame.draw.rect(surf, _CREAM_D, (bx - 5, 69, 11, 7), border_radius=2)
        pygame.draw.rect(surf, _CREAM, (bx - 5, 68, 11, 6), border_radius=2)
        pygame.draw.line(surf, _CREAM_H, (bx - 4, 69), (bx + 4, 69), 1)
        # Stacked wood platform sole — a tall wedge, lit top half so the lift
        # reads as a raised heel and not a shadow.
        _poly(surf, _WOOD_D, [(bx - 6, 75), (bx + 7, 75), (bx + 6, 81), (bx - 5, 81)])
        _poly(surf, _WOOD, [(bx - 6, 75), (bx + 7, 75), (bx + 6, 78), (bx - 6, 78)])

    # ── Bell-bottom cuff flaring off the wing tip. The base wing angles run
    #    negative-on-downstroke, so a share of -wing_angle_deg widens the flare:
    #    the trumpet mouth opens as Pip drives down, closes on the up-beat — the
    #    disco kit animates with the flap. Anchored low and pushed DOWN so the
    #    cream trumpet mouth clears the red wing tip and reads against open sky.
    cx, cy = 22, 60
    flare = 5 + max(0.0, -wing_angle_deg) * 0.12
    ftop = 3
    cuff = [(cx - ftop, cy - 6), (cx + ftop, cy - 6),
            (cx + flare, cy + 8), (cx - flare, cy + 8)]
    _poly(surf, _CREAM_D, [(x, y + 1) for x, y in cuff])
    _poly(surf, _CREAM, cuff)
    pygame.draw.line(surf, _CREAM_H, (cx - ftop + 1, cy - 5), (cx + ftop - 1, cy - 5), 1)
    # Cuff seam so the flared mouth reads as a hem, not a blob.
    pygame.draw.line(surf, _CREAM_D, (cx - flare + 1, cy + 7),
                     (cx + flare - 1, cy + 7), 1)

    # ── White leisure-suit jacket, rebuilt in strict SIDE PROFILE. A right-facing
    #    bird shows only ONE chest panel — the forward-facing breast — not a
    #    symmetric front-on V. So the coat is a single elongated cream mass hugging
    #    the body's forward (right) face from the shoulder down to a hem at the
    #    lower-front. The top edge dips into a triangular COLLAR NOTCH at the
    #    throat so the scarlet neck shows through the open collar; the wide disco
    #    LAPEL flares up-and-forward off that notch toward the beak. Everything sits
    #    at x>=35 so the scarlet body + blue wing still read past the coat on the
    #    dorsal (left) side.
    jacket_body = [(35, 44),   # rear shoulder, tucked against the wing root
                   (42, 41),   # rise to the back lip of the collar
                   (45, 47),   # notch floor — the throat opening dips in here
                   (49, 43),   # forward lip of the collar
                   (51, 50),   # forward chest, at the body's right edge
                   (49, 59),   # hem, forward
                   (37, 61)]   # hem, rear
    _poly(surf, _CREAM_D, [(x, y + 1) for x, y in jacket_body])
    _poly(surf, _CREAM, jacket_body)
    # Rear keyline separating the coat from the blue wing behind it.
    pygame.draw.line(surf, _CREAM_D, (35, 45), (37, 60), 1)
    # Wide disco lapel — a cream wedge flaring up-and-forward off the collar notch.
    lapel = [(42, 41), (50, 38), (49, 44), (45, 46)]
    _poly(surf, _CREAM_D, [(x, y + 1) for x, y in lapel])
    _poly(surf, _CREAM, lapel)
    pygame.draw.line(surf, _CREAM_H, (43, 42), (49, 39), 1)   # lapel top-light
    # Front placket highlight so the single panel reads as buttoned cloth.
    pygame.draw.line(surf, _CREAM_H, (48, 48), (47, 58), 1)

    # ── Gold medallion on the forward chest, just below the open collar — the ONE
    #    bright accent at 40px. Two straight chain lines drop from the collar notch
    #    and converge on the disc so it reads as a necklace inside the open coat.
    mx, my = HX - 4, HY + 9        # forward chest, below the throat (43, 50)
    pygame.draw.line(surf, _GOLD_D, (HX - 6, HY + 3), (mx, my - 3), 1)   # (41,44)
    pygame.draw.line(surf, _GOLD_D, (HX + 0, HY + 3), (mx, my - 3), 1)   # (47,44)
    pygame.draw.circle(surf, _GOLD_D, (mx, my), 5)      # dark ring
    pygame.draw.circle(surf, _GOLD, (mx, my), 4)        # solid gold disc
    pygame.draw.circle(surf, _GOLD_H, (mx - 1, my - 1), 1)   # glint

    # ── Oversized round AFRO built as a bumpy dome of overlapping puffs so the
    #    head silhouette reads huge and ROUND but HAIRY — offset puff centres make
    #    the outline lumpy, not a smooth coconut ball. Radii trimmed ~18% off R1
    #    so the head is less top-heavy. Puff centres kept high enough that the near
    #    eye + gold beak still peek out below the hairline. Drawn LAST so it owns
    #    the crown.
    puffs = ((HX + 4, CROWN_Y - 2, 11), (HX - 2, CROWN_Y + 1, 7),
             (HX + 8, CROWN_Y, 8),  (HX + 4, CROWN_Y - 7, 8),
             (HX - 1, CROWN_Y - 4, 6), (HX + 6, CROWN_Y - 6, 6))
    # Near-black keyline first (a fraction larger, individually offset) so each
    # lump bumps the silhouette and the brown mass separates from the scarlet
    # head where they overlap.
    for px, py, r in puffs:
        pygame.draw.circle(surf, _AFRO_DK, (px, py), r + 1)
    for px, py, r in puffs:
        pygame.draw.circle(surf, _AFRO, (px, py), r)
    # Curl texture — a few shadow dots on the lower-right face so the dome reads
    # as packed hair, not a smooth helmet.
    for tx, ty in ((HX + 10, CROWN_Y + 3), (HX + 6, CROWN_Y + 5),
                   (HX + 0, CROWN_Y + 2)):
        pygame.draw.circle(surf, _AFRO_TEX, (tx, ty), 2)
    # Cool rim highlight catching light on the top-left curls, following the
    # lump centres so the bumps stay legible.
    for hx, hy, r in ((HX - 1, CROWN_Y - 4, 3), (HX + 6, CROWN_Y - 8, 3),
                      (HX + 11, CROWN_Y - 5, 2)):
        pygame.draw.circle(surf, _AFRO_RIM, (hx, hy), r)


build = store_skins._make_skin(_paint_boogie, base_fn=_build_frame)
