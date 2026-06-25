"""DESIGN 4 — THE UNDERTAKER (gothic nightmare gentleman) for skin_tophat.

Scratch exploration only — NOT registered in store_skins.BUILDERS. The whole
outfit is near-black, so on a night sky the bird risks collapsing into a single
silhouette-less blob. The defence is baked into _paint: a thin PALE COOL
rim-light runs the back edge of coat + hat, the wing-collar is the one bright
value carrying the throat read, and charcoal lapels give value separation from
the jet-black band so the chest doesn't read as one flat shape at 40px. The
silver skull-cane knob is the hero glint — a pale dot that survives downscale.
"""
from __future__ import annotations

import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Concept palette. Three black values (coat / shadow-lift / charcoal lapel) so a
# mourning suit still separates from itself on a dark sky; pale ash carries the
# collar + every silver glint; the wilted rose is the lone warm accent.
_UND_COAT    = (12, 12, 16)        # #0C0C10 matte black coat/hat
_UND_LAPEL   = (42, 42, 51)        # #2A2A33 charcoal lapels (value lift off black)
_UND_PALE    = (201, 199, 206)     # #C9C7CE collar/skull/silver soft glow
_UND_SHADOW  = (106, 110, 120)     # #6A6E78 cool shadow / rim-light source
_UND_ROSE    = (74, 14, 24)        # #4A0E18 wilted rose
_UND_ROSE_H  = (120, 30, 44)       # rose highlight petal
_UND_PALE_D  = (150, 150, 162)     # collar shade so it reads as cloth, not paper
_UND_PALE_H  = (236, 236, 244)     # brightest silver glint
_UND_SKIN    = (176, 174, 182)     # gaunt pale-grey face accent


def _paint(surf, _a):
    # ── BEHIND: black cane slung diagonally, silver skull knob breaking the
    # back outline. Painted first so the body covers the shaft mid-section and
    # only the knob + tip overshoot the silhouette — same trick as the pirate's
    # cutlass. The knob is the hero glint, kept clear of the body so it reads as
    # a pale dot at 40px even on night.
    knob = (HX - 23, CROWN_Y + 1)
    foot = (HX - 4, HY + 30)
    # Cool rim underlay on the cane's back edge so the shaft survives a dark sky.
    pygame.draw.line(surf, _UND_SHADOW, (knob[0] - 1, knob[1] + 2),
                     (foot[0] - 1, foot[1]), 4)
    pygame.draw.line(surf, _UND_COAT, knob, foot, 3)
    pygame.draw.line(surf, _UND_SHADOW, (knob[0] + 1, knob[1] + 1),
                     (foot[0] + 1, foot[1] - 1), 1)   # faint shaft glint
    # Silver skull knob — round pale dome + two dark sockets + a short jaw. Kept
    # compact so it stays a clean glowing bead rather than a fussy face at 40px.
    kx, ky = knob
    pygame.draw.circle(surf, _UND_SHADOW, (kx, ky + 1), 5)    # cool halo
    pygame.draw.circle(surf, _UND_PALE, (kx, ky), 4)
    pygame.draw.circle(surf, _UND_PALE_H, (kx - 1, ky - 1), 2)  # bright glow core
    _poly(surf, _UND_PALE, [(kx - 2, ky + 3), (kx + 2, ky + 3),
                            (kx + 1, ky + 5), (kx - 1, ky + 5)])  # jaw
    pygame.draw.circle(surf, _UND_COAT, (kx - 1, ky), 1)     # eye sockets
    pygame.draw.circle(surf, _UND_COAT, (kx + 2, ky), 1)

    # ── BODY: long black frock coat painted OVER the scarlet body. A tall slim
    # tower (the Undertaker silhouette) with a pale cool rim down the BACK edge
    # so the coat doesn't melt into a night sky. Charcoal lapels split the front
    # into a clear V so the chest reads as a coat, not a black slab.
    coat = [(HX - 14, HY + 8), (HX - 16, HY + 30), (HX - 10, HY + 36),
            (HX + 8, HY + 36), (HX + 12, HY + 28), (HX + 10, HY + 8)]
    _poly(surf, _UND_COAT, coat)
    # Pale cool rim-light tracing the back (left) edge + shoulder — the single
    # device that keeps the all-dark silhouette legible against dark skies.
    pygame.draw.lines(surf, _UND_SHADOW, False,
                      [(HX - 14, HY + 8), (HX - 16, HY + 30),
                       (HX - 10, HY + 36)], 2)
    pygame.draw.lines(surf, _UND_PALE_D, False,
                      [(HX - 14, HY + 9), (HX - 15, HY + 24)], 1)
    # Charcoal-grey lapels — a tall V opening from the collar down the chest, a
    # value step off the black coat so the front reads at 40px.
    _poly(surf, _UND_LAPEL, [(HX - 4, HY + 9), (HX - 8, HY + 26),
                             (HX - 3, HY + 22), (HX - 1, HY + 9)])
    _poly(surf, _UND_LAPEL, [(HX + 6, HY + 9), (HX + 9, HY + 24),
                             (HX + 3, HY + 22), (HX + 2, HY + 9)])
    # Jet button + thin silver watch-chain swag across the lower chest.
    pygame.draw.circle(surf, (4, 4, 8), (HX, HY + 24), 2)
    pygame.draw.circle(surf, _UND_LAPEL, (HX - 1, HY + 23), 1)
    pygame.draw.lines(surf, _UND_PALE_D, False,
                      [(HX - 5, HY + 20), (HX - 1, HY + 24), (HX + 5, HY + 20)], 1)
    pygame.draw.line(surf, _UND_PALE_H, (HX + 5, HY + 20), (HX + 6, HY + 18), 1)

    # ── FEET: black buttoned ankle boots with dull silver spat buttons. Drawn a
    # value step over the coat hem and poked below the body to break the lower
    # outline; a rim glint keeps them off a dark floor.
    for fx in (HX - 7, HX + 1):
        pygame.draw.rect(surf, _UND_COAT, (fx, HY + 33, 8, 8), border_radius=2)
        pygame.draw.line(surf, _UND_SHADOW, (fx, HY + 34), (fx, HY + 40), 1)
        pygame.draw.line(surf, _UND_COAT, (fx, HY + 41), (fx + 9, HY + 41), 2)  # sole
        pygame.draw.circle(surf, _UND_PALE_D, (fx + 6, HY + 35), 1)  # spat button
        pygame.draw.circle(surf, _UND_PALE_D, (fx + 6, HY + 38), 1)

    # ── NECK: pale ash wing-collar + black silk cravat. The brightest mass on
    # the whole figure — a crisp pale wedge under the beak that anchors the
    # silhouette read on night. The cravat is a dark knot dropping from its V.
    _poly(surf, _UND_PALE, [(HX - 7, HY + 4), (HX + 8, HY + 4),
                            (HX + 6, HY + 12), (HX - 1, HY + 16),
                            (HX - 5, HY + 12)])
    pygame.draw.line(surf, _UND_PALE_H, (HX - 6, HY + 5), (HX + 7, HY + 5), 1)
    _poly(surf, _UND_PALE_D, [(HX - 1, HY + 16), (HX - 5, HY + 12),
                              (HX - 3, HY + 13)])      # collar fold shade
    # Wing-collar tabs — two small pale points pinched at the throat.
    _poly(surf, _UND_PALE, [(HX - 4, HY + 11), (HX, HY + 14), (HX - 3, HY + 16)])
    _poly(surf, _UND_PALE, [(HX + 5, HY + 11), (HX, HY + 14), (HX + 4, HY + 16)])
    # Black silk cravat knot + drop.
    pygame.draw.circle(surf, _UND_COAT, (HX, HY + 14), 3)
    _poly(surf, _UND_COAT, [(HX - 2, HY + 15), (HX + 2, HY + 15),
                            (HX + 1, HY + 22), (HX - 1, HY + 22)])
    pygame.draw.circle(surf, _UND_LAPEL, (HX - 1, HY + 13), 1)  # silk sheen

    # ── HEAD: gaunt pale-grey face accent on the near cheek so the face reads as
    # a sunken pallor under the hat without repainting the whole macaw.
    pygame.draw.circle(surf, _UND_SKIN, (HX + 6, HY + 2), 4)
    pygame.draw.circle(surf, _UND_SKIN, (HX + 8, HY - 2), 3)

    # Thin drooping black moustache under the beak.
    pygame.draw.lines(surf, _UND_COAT, False,
                      [(HX + 2, HY + 4), (HX + 6, HY + 6), (HX + 7, HY + 10)], 2)
    pygame.draw.lines(surf, _UND_COAT, False,
                      [(HX + 11, HY + 4), (HX + 9, HY + 6), (HX + 9, HY + 10)], 2)

    # Smoked monocle on the NEAR eye — dark lens, silver rim, a thin chain to the
    # coat. The pale rim is the face glint that keeps the head from going flat.
    mx, my = HX + 8, HY - 1
    pygame.draw.circle(surf, (6, 6, 10), (mx, my), 4)       # smoked dark lens
    pygame.draw.circle(surf, _UND_PALE, (mx, my), 4, 1)     # silver rim
    pygame.draw.circle(surf, _UND_PALE_H, (mx - 1, my - 1), 1)  # rim glint
    pygame.draw.line(surf, _UND_PALE_D, (mx + 1, my + 4), (HX + 6, HY + 8), 1)

    # ── HAT: extra-tall matte-black topper. Brim, then a tall crown rising well
    # above CROWN_Y, with a PALE COOL rim down its back edge + top so the black
    # hat survives a night sky. A crepe mourning band + wilted rose finish it.
    cy = CROWN_Y
    pygame.draw.ellipse(surf, _UND_COAT, (HX - 17, cy + 1, 34, 8))   # brim
    pygame.draw.ellipse(surf, _UND_LAPEL, (HX - 15, cy + 1, 30, 4))
    pygame.draw.line(surf, _UND_SHADOW, (HX - 13, cy + 1), (HX + 12, cy + 1), 1)

    top_y = cy - 22                       # extra-tall crown
    pygame.draw.rect(surf, _UND_COAT, (HX - 9, top_y, 18, 24))
    # Cool rim-light down the BACK (left) edge of the crown — the hat's anchor on
    # night so it doesn't dissolve into the sky.
    pygame.draw.line(surf, _UND_SHADOW, (HX - 9, top_y + 2), (HX - 9, cy), 2)
    pygame.draw.line(surf, _UND_PALE_D, (HX - 9, top_y + 3), (HX - 9, top_y + 14), 1)
    pygame.draw.line(surf, _UND_LAPEL, (HX + 7, top_y + 2), (HX + 7, cy - 2), 1)  # front sheen
    # Pale cool top rim — keeps the crown top off a dark floor.
    pygame.draw.ellipse(surf, _UND_SHADOW, (HX - 9, top_y - 2, 18, 6))
    pygame.draw.ellipse(surf, _UND_COAT, (HX - 8, top_y - 1, 16, 4))
    pygame.draw.line(surf, _UND_PALE_D, (HX - 6, top_y - 1), (HX + 4, top_y - 1), 1)

    # Black crepe mourning band wrapping the crown base — a matte band a touch
    # off the coat black, edged with a thin cool line so it still reads as a band.
    pygame.draw.rect(surf, (7, 7, 11), (HX - 9, cy - 4, 18, 5))
    pygame.draw.line(surf, _UND_SHADOW, (HX - 9, cy - 4), (HX + 8, cy - 4), 1)

    # Small wilted dark rose tucked in the band on the near side — the lone warm
    # accent. A tight rose cluster + one drooping petal so it reads as a flower.
    rx, ry = HX + 6, cy - 2
    pygame.draw.circle(surf, _UND_ROSE, (rx, ry), 3)
    pygame.draw.circle(surf, _UND_ROSE_H, (rx - 1, ry - 1), 1)
    _poly(surf, _UND_ROSE, [(rx + 1, ry + 1), (rx + 4, ry + 3), (rx + 1, ry + 4)])
    pygame.draw.line(surf, (40, 50, 38), (rx - 2, ry + 2), (rx - 4, ry + 5), 1)  # wilted stem


build = store_skins._make_skin(_paint)
