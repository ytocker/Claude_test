"""Soccer v4 DESIGN 3 — THE CAPTAIN.

The jersey reads as actual CLOTHING rather than a recolored bird: a
crew-neck white collar, white sleeve cuffs, a dark garment outline and a
chest seam give the shirt fabric-edge silhouette cues a flat fill can't.
The gold captain's armband sits isolated on the near shoulder so it is
unmistakably an armband, not part of the body shading."""
import pygame
from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin

# Body centre anchors — kit geometry is keyed off these so limbs, crest and
# collar stay aligned with the macaw base regardless of frame.
BCX, BCY = 32, 52

_CAP_BACK = (7, 20, 72)       # darkest navy — back/shadow zone of the shirt
_CAP_CHEST = (13, 40, 120)    # lighter chest zone for a lit front face
_CAP_OUT = (5, 14, 45)        # near-black navy garment outline
_CAP_HI = (20, 50, 130)       # highlight seam down the chest
_ARM_GOLD = (232, 178, 40)    # captain armband gold
_ARM_SH = (160, 120, 20)      # armband shadow
_CREST_R = (180, 30, 30)      # crest red
_CREST_G = (232, 178, 40)     # crest gold
_NUM_W = (240, 244, 255)      # squad-number white
_SOCK_N = (7, 20, 72)         # navy socks matching the jersey
_BOOT_D = (26, 24, 32)
_BOOT_S = (200, 205, 215)
_SHORTS_G = (130, 136, 155)   # grey shorts


def _paint(surf, _a):
    jersey = [
        (BCX - 10, HY + 7),
        (BCX - 12, HY + 17),
        (BCX - 8, HY + 23),
        (HX + 8, HY + 23),
        (HX + 11, HY + 18),
        (HX + 9, HY + 8),
    ]

    # Socks first so the jersey hem and shorts overlap the tops cleanly.
    for fx in (HX - 9, HX + 1):
        pygame.draw.line(surf, (4, 12, 50), (fx + 1, HY + 13), (fx + 1, HY + 25), 6)
        pygame.draw.line(surf, _SOCK_N, (fx, HY + 13), (fx, HY + 25), 5)
        pygame.draw.line(surf, (220, 225, 235), (fx - 1, HY + 15), (fx + 2, HY + 15), 2)

    for fx in (HX - 9, HX + 1):
        pygame.draw.ellipse(surf, _BOOT_D, (fx - 4, HY + 23, 9, 5))
        pygame.draw.line(surf, _BOOT_S, (fx - 3, HY + 25), (fx + 3, HY + 25), 1)

    pygame.draw.line(surf, _SHORTS_G, (BCX - 8, HY + 24), (HX + 8, HY + 24), 4)

    # Two-zone jersey body — darker back, lit chest panel.
    _poly(surf, _CAP_BACK, jersey)
    chest = [(BCX, HY + 7), (BCX, HY + 23), (HX + 8, HY + 23),
             (HX + 11, HY + 18), (HX + 9, HY + 8)]
    _poly(surf, _CAP_CHEST, chest)

    # Crest — small club shield on the upper chest.
    _poly(surf, _CREST_G, [(HX - 4, HY + 10), (HX - 6, HY + 13),
                           (HX - 4, HY + 15), (HX - 2, HY + 13)])
    _poly(surf, _CREST_R, [(HX - 4, HY + 11), (HX - 5, HY + 13),
                           (HX - 4, HY + 14), (HX - 3, HY + 13)])

    # Squad number "10" below the crest.
    pygame.draw.rect(surf, _NUM_W, (HX - 4, HY + 14, 2, 6))
    pygame.draw.rect(surf, _NUM_W, (HX - 1, HY + 14, 4, 6), 1)

    # ELEMENT 3 — dark navy garment outline.
    pygame.draw.polygon(surf, _CAP_OUT, jersey, 2)

    # ELEMENT 4 — chest seam line.
    pygame.draw.line(surf, _CAP_HI, (HX - 1, HY + 11), (HX, HY + 21), 1)

    # ELEMENT 2 — white sleeve cuff edges.
    pygame.draw.line(surf, (220, 225, 235), (BCX - 10, HY + 12), (BCX - 3, HY + 12), 2)
    pygame.draw.line(surf, (220, 225, 235), (HX + 4, HY + 12), (HX + 10, HY + 12), 2)

    # Gold captain armband — isolated on the near shoulder, below the cuff edge.
    pygame.draw.line(surf, _ARM_SH, (HX + 2, HY + 10), (HX + 9, HY + 10), 5)
    pygame.draw.line(surf, _ARM_GOLD, (HX + 2, HY + 9), (HX + 9, HY + 9), 4)
    pygame.draw.line(surf, (255, 220, 80), (HX + 3, HY + 9), (HX + 7, HY + 9), 1)

    # ELEMENT 1 — crew-neck white collar ring (drawn last so it crowns the neck).
    collar_rect = pygame.Rect(HX - 7, HY + 4, 15, 9)
    pygame.draw.ellipse(surf, (230, 235, 245), collar_rect, 3)
    pygame.draw.ellipse(surf, (100, 105, 115), collar_rect, 1)


build = _make_skin(_paint)
