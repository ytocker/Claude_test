"""PARROT'S PARROT — the iconic pirate-with-a-companion buccaneer candidate.

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_pirate`` is untouched. Builds on the ORIGINAL pirate (slate tricorn +
continuous gold brim + white skull cockade + eyepatch + gold earring) and
enriches it across more body zones for a richer read:

  * a tiny green/yellow companion macaw perched HIGH on the back-left so it
    clears Pip's wing and breaks the rear outline — the signature: a second,
    living creature recognisable at 40px;
  * a red headscarf/bandana wrapping the crown UNDER the tricorn, with two
    short knot tails trailing behind the head;
  * a brown leather bandolier crossing the chest with a brass buckle and a
    couple of stitched musket-cartridge loops.

The scarlet macaw body is untouched — everything here is an OVERLAY. The 40px
truth read, in order of value: the slate tricorn + gold brim + white skull
(the kept pirate anchor), then the green/yellow second bird breaking the back
silhouette, then the bandana red + the bandolier line across the chest.
"""
import math
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

# Red bandana wrapping the crown under the tricorn.
_BAND_RED   = (192, 57, 43)        # #C0392B
_BAND_RED_D = (126, 32, 24)        # #7E2018 shadow
_BAND_RED_H = (224, 104, 88)

# Leather bandolier + brass fittings across the chest.
_LEATHER    = (90, 58, 34)         # #5A3A22
_LEATHER_D  = (60, 38, 22)
_LEATHER_H  = (128, 86, 52)
_BRASS      = (217, 164, 65)       # #D9A441
_BRASS_H    = (255, 222, 150)

# Kept pirate palette (mirrors store_skins._paint_pirate so the anchor reads
# identically — felt, gold trim, skull, earring).
_FELT   = (74, 78, 96)
_FELT_D = (48, 52, 70)
_FELT_H = (120, 126, 150)
_TRIM   = (255, 205, 70)
_TRIM_H = (255, 240, 160)
_GOLD   = (255, 205, 70)
_SKULL  = (244, 246, 240)


def _paint_bandolier(surf):
    """Brown leather strap from the near shoulder down across the chest to the
    far hip, with a brass buckle and two stitched cartridge loops. Body centre
    is ~(32, 52); the strap reads as a single diagonal line across the belly."""
    top = (HX - 3, HY + 12)            # near shoulder, just under the head
    bot = (15, 64)                     # far hip, low on the body
    pygame.draw.line(surf, _LEATHER_D, top, bot, 6)
    pygame.draw.line(surf, _LEATHER, top, bot, 4)
    pygame.draw.line(surf, _LEATHER_H,
                     (top[0] - 1, top[1] + 1), (bot[0] - 1, bot[1] + 1), 1)

    # Direction of the strap, to seat the cartridge loops square across it.
    dx, dy = bot[0] - top[0], bot[1] - top[1]
    blen = math.hypot(dx, dy)
    ux, uy = dx / blen, dy / blen
    px, py = -uy, ux                   # perpendicular

    # Two musket-cartridge loops — brass caps poking off the leather so they
    # read as objects, not stitches, at 40px.
    for t in (16, 26):
        cx = top[0] + ux * t
        cy = top[1] + uy * t
        a = (cx + px * 4, cy + py * 4)
        b = (cx - px * 1, cy - py * 1)
        pygame.draw.line(surf, _LEATHER_D, a, b, 4)
        pygame.draw.circle(surf, _BRASS, (int(a[0]), int(a[1])), 2)
        pygame.draw.circle(surf, _BRASS_H, (int(a[0]), int(a[1] - 1)), 1)

    # Brass buckle mid-chest — the one bright fitting on the strap.
    mx = top[0] + ux * 21
    my = top[1] + uy * 21
    pygame.draw.rect(surf, _BRASS, (int(mx) - 3, int(my) - 3, 7, 7),
                     border_radius=1)
    pygame.draw.rect(surf, _LEATHER_D, (int(mx) - 1, int(my) - 1, 3, 3))
    pygame.draw.circle(surf, _BRASS_H, (int(mx) - 2, int(my) - 2), 1)


def _paint_companion(surf, wing_angle_deg):
    """A tiny ~9px green/yellow macaw perched HIGH on the back-left so it clears
    Pip's wing and breaks the rear outline against open sky. Beak faces forward
    (right, toward Pip's head), folded wing + stubby tail trail back-left. The
    companion bobs a hair with the wing beat so it reads as alive."""
    bob = int(round(wing_angle_deg * 0.06))
    cx, cy = HX - 22, CROWN_Y + 4 + bob   # back-left, up near the shoulder/back

    # Stubby tail trailing off the back-left — breaks the silhouette into sky.
    _poly(surf, _COMP_GREEN_D, [(cx - 5, cy + 1), (cx - 12, cy + 1),
                                (cx - 11, cy + 5), (cx - 4, cy + 4)])
    pygame.draw.line(surf, _COMP_GREEN, (cx - 5, cy + 2), (cx - 11, cy + 2), 2)

    # Body — a plump green oval; gold belly splash so the second bird isn't a
    # flat green blob at distance.
    pygame.draw.ellipse(surf, _COMP_GREEN_D, (cx - 6, cy - 4, 13, 12))
    pygame.draw.ellipse(surf, _COMP_GREEN, (cx - 5, cy - 4, 11, 11))
    pygame.draw.ellipse(surf, _COMP_GOLD, (cx - 2, cy + 1, 6, 6))
    pygame.draw.ellipse(surf, _COMP_GOLD_H, (cx - 1, cy + 2, 3, 3))

    # Folded wing — a darker green plane laid over the back so the form turns.
    _poly(surf, _COMP_GREEN_D, [(cx - 5, cy - 3), (cx + 2, cy - 4),
                                (cx + 1, cy + 3), (cx - 6, cy + 2)])
    pygame.draw.line(surf, _COMP_GREEN_H, (cx - 4, cy - 2), (cx + 1, cy - 3), 1)

    # Head sits up-and-forward, crown lit so it reads round; eye + beak face
    # Pip (right). Small, but the contrast carries the "second bird" read.
    hx, hy = cx + 4, cy - 5
    pygame.draw.circle(surf, _COMP_GREEN_D, (hx, hy), 5)
    pygame.draw.circle(surf, _COMP_GREEN, (hx, hy), 4)
    pygame.draw.circle(surf, _COMP_GREEN_H, (hx - 1, hy - 2), 2)
    # Yellow cheek patch — macaw signature.
    pygame.draw.circle(surf, _COMP_GOLD, (hx + 1, hy + 1), 2)
    # Hooked beak poking forward off the head, into the gap toward Pip.
    _poly(surf, _COMP_BEAK, [(hx + 3, hy - 1), (hx + 8, hy + 1),
                             (hx + 3, hy + 3)])
    pygame.draw.line(surf, _COMP_BEAK, (hx + 3, hy + 1), (hx + 7, hy + 1), 1)
    # Eye dot — a bright catch so the tiny head reads as a face.
    pygame.draw.circle(surf, _COMP_EYE, (hx + 1, hy - 1), 1)
    pygame.draw.circle(surf, (235, 238, 240), (hx + 2, hy - 1), 1)

    # Tiny perched feet gripping Pip's back so it reads as standing on him.
    pygame.draw.line(surf, _COMP_BEAK, (cx - 1, cy + 7), (cx, cy + 9), 1)
    pygame.draw.line(surf, _COMP_BEAK, (cx + 2, cy + 7), (cx + 3, cy + 9), 1)


def _paint_bandana(surf):
    """A red headscarf wrapping the crown UNDER the tricorn, with two short knot
    tails trailing behind the head. Drawn before the tricorn so the hat brim
    sits on top of the wrap; the tails poke off the back-right of the skull."""
    # Wrap band hugging the upper head, just below where the brim will sit.
    band = [(HX - 12, HY - 4), (HX - 5, HY - 8), (HX + 9, HY - 8),
            (HX + 13, HY - 3), (HX + 12, HY + 1), (HX - 11, HY + 1)]
    _poly(surf, _BAND_RED_D, band)
    inner = [(HX - 11, HY - 4), (HX - 5, HY - 7), (HX + 9, HY - 7),
             (HX + 12, HY - 3), (HX + 11, HY), (HX - 10, HY)]
    _poly(surf, _BAND_RED, inner)
    # A lit crease so the wrap reads as cloth, not a flat cap.
    pygame.draw.line(surf, _BAND_RED_H, (HX - 9, HY - 4), (HX + 9, HY - 5), 1)

    # Two short knot tails trailing off the back of the head (left, into sky).
    kx, ky = HX - 11, HY - 2            # knot at the back-left of the wrap
    pygame.draw.circle(surf, _BAND_RED_D, (kx, ky), 3)
    pygame.draw.circle(surf, _BAND_RED, (kx, ky), 2)
    for spread in (0, 4):
        t0 = (kx, ky + spread)
        t1 = (kx - 6, ky + 1 + spread)
        t2 = (kx - 11, ky + 4 + spread)
        pygame.draw.lines(surf, _BAND_RED_D, False, [t0, t1, t2], 3)
        pygame.draw.lines(surf, _BAND_RED, False, [t0, t1, t2], 2)


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
    # Back-to-front draw order: companion (behind/on the back) and bandolier on
    # the body first, then the bandana wrap, then the kept tricorn/skull anchor
    # on top so the hat sits over the wrap and the read priority is preserved.
    _paint_companion(surf, wing_angle_deg)
    _paint_bandolier(surf)
    _paint_bandana(surf)
    _paint_pirate_core(surf)


build = store_skins._make_skin(_paint)
