"""Soccer v6 Design 1 — THE STRIKER.

A crisp modern striker's kit: a white jersey with a navy V-collar, a bold
squad number "9", and a diagonal royal-blue shoulder sash; royal-blue shorts
with a proper crotch notch so the two leg tubes read separately; white socks
with a red turn-over hoop; and near-black cleats with a bright orange sole
stripe. Four stacked visible layers — jersey → shorts → socks → cleats — read
as a footballer even at 40px, and the sash + number + red sock hoop are the
accents that keep the white kit from going flat.
"""
import pygame
from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin

# White jersey + royal-blue trim (classic home-kit striker read).
_JRS_W    = (240, 240, 245)   # #F0F0F5 jersey white field
_JRS_WD   = (192, 196, 216)   # #C0C4D8 cool-grey back-half shade (rounds torso)
_JRS_OUT  = ( 26,  62, 160)   # #1A3EA0 royal-blue garment outline
_NAVY     = ( 20,  40, 110)   # deep navy for V-collar + squad number
_SASH     = ( 26,  62, 160)   # #1A3EA0 royal-blue shoulder sash
_SASH_H   = ( 85, 136, 255)   # #5588FF bright-blue sash highlight

# Royal-blue shorts.
_SHT      = ( 26,  62, 160)   # #1A3EA0 royal-blue shorts
_SHT_D    = ( 16,  40, 112)   # darker-blue shorts outline

# White socks with a red hoop + thin navy secondary hoop.
_SCK      = (240, 240, 245)   # #F0F0F5 white sock body
_SCK_RED  = (192,  57,  43)   # #C0392B red hoop at sock top
_SCK_NAVY = ( 20,  40, 110)   # navy secondary hoop

# Near-black cleats + bright orange sole line.
_CLT      = ( 28,  28,  36)   # #1C1C24 near-black cleat
_CLT_STR  = (232, 120,  32)   # #E87820 bright orange side/sole stripe


def _paint(surf, _a):
    # 1 — JERSEY: proven baseball polygon (top HY+8, hem HY+23) so the kit hugs
    #     the body footprint. White field + a cool-grey back-half so the torso
    #     reads round; a 1px royal-blue outline makes it a garment, not paint.
    jersey = [(HX - 13, HY + 8), (HX - 14, HY + 18), (HX - 10, HY + 23),
              (HX + 8,  HY + 23), (HX + 11, HY + 18), (HX + 9,  HY + 8)]
    _poly(surf, _JRS_W, jersey)
    _poly(surf, _JRS_WD, [(HX + 4, HY + 9), (HX + 11, HY + 18),
                          (HX + 8, HY + 23), (HX + 4, HY + 22)])
    pygame.draw.polygon(surf, _JRS_OUT, jersey, 1)

    # V-collar — a small navy V notch at the jersey top centre so the neckline
    # reads as an open collar, not a blank field.
    _poly(surf, _NAVY, [(HX - 3, HY + 8), (HX + 3, HY + 8), (HX, HY + 11)])

    # Diagonal shoulder sash — a 3px royal-blue band across the chest with a 1px
    # bright-blue highlight on top so it reads as a raised strap at 40px.
    pygame.draw.line(surf, _SASH,   (HX - 12, HY + 10), (HX + 8, HY + 18), 3)
    pygame.draw.line(surf, _SASH_H, (HX - 12, HY + 9),  (HX + 8, HY + 17), 1)

    # Bold squad number "9" — two thick navy strokes (a circle top + a diagonal
    # tail) in the chest centre, drawn OVER the sash so the number owns the read.
    pygame.draw.circle(surf, _NAVY, (HX + 1, HY + 14), 3, 2)         # loop top
    pygame.draw.line(surf, _NAVY, (HX + 3, HY + 14), (HX, HY + 21), 2)  # tail

    # 2 — SHORTS: royal-blue with a visible crotch notch so it reads as TWO leg
    #     tubes (soccer's high-thigh short), not a flat band. 1px darker outline.
    shorts = [(HX - 10, HY + 23), (HX - 11, HY + 29), (HX - 3, HY + 29),
              (HX - 2, HY + 26), (HX, HY + 26), (HX + 1, HY + 29),
              (HX + 7, HY + 29), (HX + 8, HY + 23)]
    _poly(surf, _SHT, shorts)
    pygame.draw.polygon(surf, _SHT_D, shorts, 1)

    # 3 — SOCKS: white knee-highs centred over the two foot positions, with a
    #     red turn-over hoop at the top then a thin navy secondary hoop — the
    #     #1 soccer identifier is the sock line between shorts and cleats.
    for sx in (HX - 7, HX + 3):
        pygame.draw.line(surf, _SCK, (sx, HY + 29), (sx, HY + 37), 4)
        pygame.draw.line(surf, _SCK_RED, (sx, HY + 29), (sx, HY + 32), 4)
        pygame.draw.line(surf, _SCK_NAVY, (sx, HY + 32), (sx, HY + 33), 4)

    # 4 — CLEATS: drawn last so they sit in front of the sock bottoms. Near-black
    #     boots with a bright orange sole line — the striker's flash of colour.
    for fx in (HX - 11, HX - 1):
        pygame.draw.rect(surf, _CLT, (fx, HY + 33, 10, 5), border_radius=2)
        pygame.draw.line(surf, _CLT_STR, (fx + 1, HY + 37), (fx + 9, HY + 37), 1)


build = _make_skin(_paint)
