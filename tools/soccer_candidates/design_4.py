"""DESIGN 4 — THE REFEREE (Soccer / Football, v4).

Scratch exploration only — NOT registered in store_skins.BUILDERS, so
production stays untouched. Pip the scarlet macaw kitted as the match
official. Earlier passes read as "a parrot painted in team colours"; v4
forces the jersey to read as actual CLOTHING through four shirt-construction
elements: a referee V-neck collar, white sleeve cuffs, a garment outline with
dual rim-lights, and a centre placket seam.

The kit is true near-black so the read is BLACK at the 40px downscale, not a
charcoal-blue plane: the lit plane is a single 2px sliver on the near edge.
White is rationed to the collar V, sleeve edges, sock hoop and sole stripe so
the steel whistle and yellow card own the eye. The dual rim-lights (cool grey
on the far back contour, neutral on the near front) are the only thing that
keeps a true-black garment from dissolving into the night sky.

Headless render: tools/soccer_candidates/render_design_4.py.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin

# Body centre in composite space (parrot body centre (32,32) + PARROT_DY).
BCX, BCY = 32, 52

# Near-black referee kit. The lit plane is kept dark on purpose so the read is
# BLACK, not a charcoal-blue plane; white + steel + yellow are the only
# high-value notes, reserved for the shirt-construction edges and hero props.
_REF_BLACK = (26, 28, 34)     # true near-black jersey body
_REF_LIT   = (36, 38, 46)     # lit plane (barely visible, 2px sliver only)
_REF_RIM   = (40, 42, 50)     # garment outline
_REF_BACK  = (120, 124, 130)  # far-side rim-light (carries the night separation)
_REF_WHITE = (230, 235, 245)  # collar V, sleeve edges
_REF_YCRD  = (255, 221, 70)   # yellow card
_REF_RCRD  = (220, 50, 40)    # red card sliver
_REF_WSTL  = (180, 185, 195)  # whistle steel
_BOOT_D    = (26, 24, 32)
_BOOT_S    = (200, 205, 215)
_SHORTS_D  = (20, 24, 30)
_SOCK_D    = (26, 28, 34)


def _paint(surf, _a):
    # Full-body referee jersey polygon — left edge anchored on BCX so the kit
    # wraps the WHOLE visible body (x=20..58), reading as a worn garment rather
    # than a chest patch.
    jersey = [
        (BCX - 10, HY + 7),   # left shoulder
        (BCX - 12, HY + 17),  # left hip
        (BCX - 8,  HY + 23),  # left hem
        (HX + 8,   HY + 23),  # right hem
        (HX + 11,  HY + 18),  # right hip
        (HX + 9,   HY + 8),   # right shoulder
    ]

    # 1 — PEAKED OFFICIALS CAP. Drawn first so the body/jersey overlaps its
    #     base; a forward-brimmed dome on the crown, never a brow headband, so
    #     the open macaw face is preserved. The bright leading edge + a mid-grey
    #     gap line carve the dome and brim apart at 40px.
    pygame.draw.ellipse(surf, _REF_BLACK, (HX - 8, CROWN_Y + 2, 17, 9))
    pygame.draw.ellipse(surf, (36, 38, 46), (HX - 7, CROWN_Y + 2, 15, 7))   # subtle highlight
    pygame.draw.line(surf, _REF_BLACK, (HX - 4, CROWN_Y + 10), (HX + 12, CROWN_Y + 9), 3)  # brim
    pygame.draw.line(surf, (220, 225, 235), (HX + 2, CROWN_Y + 8), (HX + 12, CROWN_Y + 8), 2)  # bright leading edge
    pygame.draw.line(surf, (70, 72, 76), (HX + 2, CROWN_Y + 10), (HX + 10, CROWN_Y + 10), 1)  # gap line

    # 2 — BLACK SOCKS (knee-high) with a white hoop. The shadow stripe gives the
    #     black sock an edge against the night sky.
    for fx in (HX - 9, HX + 1):
        pygame.draw.line(surf, (18, 20, 26), (fx + 1, HY + 13), (fx + 1, HY + 25), 6)  # shadow
        pygame.draw.line(surf, _SOCK_D, (fx, HY + 13), (fx, HY + 25), 5)
        pygame.draw.line(surf, (200, 205, 215), (fx - 1, HY + 15), (fx + 2, HY + 15), 2)  # white hoop

    # 3 — BOOTS with a white sole stripe.
    for fx in (HX - 9, HX + 1):
        pygame.draw.ellipse(surf, _BOOT_D, (fx - 4, HY + 23, 9, 5))
        pygame.draw.line(surf, _BOOT_S, (fx - 3, HY + 25), (fx + 3, HY + 25), 1)

    # 4 — BLACK SHORTS just under the jersey hem.
    pygame.draw.line(surf, _SHORTS_D, (BCX - 8, HY + 24), (HX + 8, HY + 24), 4)

    # 5 — JERSEY BODY (true black). The lit plane is a single 2px sliver on the
    #     near edge so the read stays BLACK rather than a grey chest plane.
    _poly(surf, _REF_BLACK, jersey)
    pygame.draw.line(surf, _REF_LIT, (HX + 9, HY + 9), (HX + 10, HY + 17), 2)  # lit sliver

    # 6 — SHIRT ELEMENT 3: GARMENT OUTLINE with DUAL RIM-LIGHTS. The cool-grey
    #     back rim + neutral front outline + full polygon edge are the only
    #     thing that separates a true-black garment from the night sky and from
    #     Pip's own scarlet body.
    pygame.draw.lines(surf, (120, 124, 130), False,
                      [(BCX - 10, HY + 7), (BCX - 12, HY + 17), (BCX - 8, HY + 23)], 2)  # back rim (left)
    pygame.draw.lines(surf, (100, 102, 108), False,
                      [(HX + 9, HY + 8), (HX + 11, HY + 18), (HX + 8, HY + 23)], 1)      # front outline (right)
    pygame.draw.polygon(surf, _REF_RIM, jersey, 1)

    # 7 — SHIRT ELEMENT 4: CENTRE PLACKET seam down the shirt front.
    pygame.draw.line(surf, (38, 40, 46), (HX, HY + 9), (HX, HY + 21), 1)

    # 8 — SHIRT ELEMENT 2: WHITE SLEEVE EDGES (cuffs on each shoulder).
    pygame.draw.line(surf, _REF_WHITE, (BCX - 10, HY + 12), (BCX - 3, HY + 12), 2)
    pygame.draw.line(surf, _REF_WHITE, (HX + 4, HY + 12), (HX + 10, HY + 12), 2)

    # 9 — SHIRT ELEMENT 1: V-NECK COLLAR (referee style). Two white lines meet
    #     at the centre-front, each backed by a cool keyline shadow so the V
    #     reads as a stitched neckline rather than a paint stroke.
    pygame.draw.line(surf, _REF_WHITE, (HX, HY + 9), (HX - 5, HY + 6), 3)
    pygame.draw.line(surf, _REF_WHITE, (HX, HY + 9), (HX + 6, HY + 6), 3)
    pygame.draw.line(surf, (100, 105, 115), (HX - 1, HY + 9), (HX - 5, HY + 7), 1)
    pygame.draw.line(surf, (100, 105, 115), (HX + 1, HY + 9), (HX + 6, HY + 7), 1)

    # 10 — LANYARD + WHISTLE, drawn last as the hero prop: a steel disc at the
    #      bottom of a lanyard V, the single brightest note that says "referee".
    pygame.draw.line(surf, (80, 84, 92), (HX - 2, HY + 8), (HX - 2, HY + 17), 1)  # lanyard V
    pygame.draw.line(surf, (80, 84, 92), (HX + 2, HY + 8), (HX + 2, HY + 17), 1)
    wx, wy = HX, HY + 17
    pygame.draw.circle(surf, (100, 104, 112), (wx, wy), 4)   # disc shadow
    pygame.draw.circle(surf, _REF_WSTL, (wx, wy), 3)         # steel body
    pygame.draw.circle(surf, (220, 225, 235), (wx - 1, wy - 1), 1)  # glint

    # 11 — YELLOW + RED CARDS, drawn last on the opposite breast from the
    #      whistle: a bright booking card with a red sliver behind it.
    yl, yt = HX - 9, HY + 9
    pygame.draw.rect(surf, (180, 140, 0), (yl - 1, yt - 1, 8, 8))   # halo
    pygame.draw.rect(surf, _REF_YCRD, (yl, yt, 7, 7))
    pygame.draw.line(surf, (255, 240, 120), (yl + 1, yt + 1), (yl + 5, yt + 1), 1)  # glint
    pygame.draw.rect(surf, _REF_RCRD, (yl + 2, yt + 4, 6, 5))       # red card sliver behind


build = _make_skin(_paint)
