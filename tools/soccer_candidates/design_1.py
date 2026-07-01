"""Soccer v5 Design 1 — THE KIT.

Classic European club soccer kit: white jersey with a royal-blue chest band
and crest, dark navy shorts, white knee-high socks with a navy hoop, and
near-black cleats with a white sole stripe. Four stacked visible layers —
jersey → shorts → socks → cleats — is what makes a soccer player
instantly recognizable even at 40px.
"""
import pygame
from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin

# Classic white + royal-blue European kit (think Real Madrid / Arsenal white).
_JRS_W   = (240, 240, 248)   # jersey white field
_JRS_WD  = (195, 196, 215)   # jersey shade (back half)
_JRS_BL  = ( 30,  65, 185)   # royal blue accent band
_JRS_BLD = ( 15,  35, 110)   # blue garment outline + collar
_CREST   = (255, 220,  60)   # small gold crest pip on chest
_SHT     = ( 10,  24,  64)   # dark navy shorts
_SHT_D   = (  5,  12,  35)   # shorts shadow edge
_SCK     = (228, 230, 242)   # white sock
_SCK_BD  = ( 20,  50, 130)   # navy sock hoop at top
_CLT     = ( 28,  28,  36)   # near-black cleat
_CLT_H   = (210, 210, 210)   # white sole stripe


def _paint(surf, _a):
    # 1 — JERSEY: proven polygon from baseball design_4.py; top at HY+8,
    #     hem at HY+23. Fills y49–64 with a white body + right-side shade zone
    #     so the torso reads as round. Blue outline makes it clothing, not paint.
    jersey = [(HX - 13, HY + 8), (HX - 14, HY + 18), (HX - 10, HY + 23),
              (HX + 8,  HY + 23), (HX + 11, HY + 18), (HX + 9,  HY + 8)]
    _poly(surf, _JRS_W, jersey)
    # Shade the back (right) half — rounded torso, not flat.
    _poly(surf, _JRS_WD, [(HX + 4, HY + 9), (HX + 11, HY + 18),
                           (HX + 8, HY + 23), (HX + 4, HY + 22)])
    # Garment outline — 1px blue edge makes it read as a garment boundary.
    pygame.draw.polygon(surf, _JRS_BLD, jersey, 1)
    # Horizontal chest band — thin royal-blue stripe at mid-chest.
    pygame.draw.line(surf, _JRS_BL,  (HX - 12, HY + 13), (HX + 10, HY + 13), 2)
    pygame.draw.line(surf, _JRS_BLD, (HX - 12, HY + 15), (HX + 10, HY + 15), 1)
    # Crew-neck collar arc at the jersey top centre.
    pygame.draw.arc(surf, _JRS_BLD, pygame.Rect(HX - 4, HY + 7, 8, 6), 0.4, 2.7, 1)
    # Small gold crest pip on the left chest.
    pygame.draw.circle(surf, _CREST,   (HX - 5, HY + 11), 2)
    pygame.draw.circle(surf, _JRS_BLD, (HX - 5, HY + 11), 1)

    # 2 — SHORTS: dark-navy 6px band immediately below the jersey hem.
    #     The "very short shorts" (mid-thigh) read is unique to soccer —
    #     no other sport wears shorts this high on the leg.
    shorts = [(HX - 10, HY + 23), (HX - 12, HY + 29),
              (HX + 8,  HY + 29), (HX + 8,  HY + 23)]
    _poly(surf, _SHT, shorts)
    _poly(surf, _SHT_D, [(HX + 5, HY + 23), (HX + 8, HY + 23),
                          (HX + 8, HY + 29), (HX + 5, HY + 29)])

    # 3 — KNEE-HIGH SOCKS: two white 3px-wide pillar lines from shorts-hem
    #     down 8px. The navy hoop at the sock top is the classic turn-over
    #     cuff visible on every professional soccer kit. This is the #1 soccer
    #     identifier at 40px — the sock line between shorts and cleats.
    for sx in (HX - 11, HX + 2):
        pygame.draw.line(surf, _SCK,    (sx, HY + 29), (sx, HY + 37), 3)
        pygame.draw.line(surf, _SCK_BD, (sx, HY + 29), (sx, HY + 32), 3)

    # 4 — CLEATS: drawn last so they sit in front of sock bottoms.
    #     Near-black boots with a white sole stripe — the stud-bottomed cleat
    #     read. Drawn as ellipses matching the baseball cleat approach.
    for fx in (HX - 12, HX + 1):
        pygame.draw.ellipse(surf, _CLT, (fx - 2, HY + 33, 10, 5))
        pygame.draw.line(surf, _CLT_H,  (fx - 1, HY + 37), (fx + 7, HY + 37), 1)


build = _make_skin(_paint)
