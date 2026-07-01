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
        # 2px white sole so the boot reads against the navy sock at 40px.
        pygame.draw.line(surf, _BOOT_S, (fx - 3, HY + 26), (fx + 3, HY + 26), 2)

    pygame.draw.line(surf, _SHORTS_G, (BCX - 8, HY + 24), (HX + 8, HY + 24), 4)

    # Two-zone jersey body — darker back, lit chest panel.
    _poly(surf, _CAP_BACK, jersey)
    chest = [(BCX, HY + 7), (BCX, HY + 23), (HX + 8, HY + 23),
             (HX + 11, HY + 18), (HX + 9, HY + 8)]
    _poly(surf, _CAP_CHEST, chest)

    # ELEMENT 3 — dark navy garment outline.
    pygame.draw.polygon(surf, _CAP_OUT, jersey, 2)

    # ELEMENT 4 — chest seam line.
    pygame.draw.line(surf, _CAP_HI, (HX - 1, HY + 11), (HX, HY + 21), 1)

    # Squad number "10" — tall enough (7px) to survive the 40px truth read
    # instead of collapsing into a two-pixel smudge. Sole chest element so it
    # never competes with the crest for the same few pixels.
    pygame.draw.rect(surf, _NUM_W, (HX - 5, HY + 14, 2, 7))       # the "1"
    pygame.draw.rect(surf, _NUM_W, (HX - 2, HY + 14, 5, 7), 1)    # the "0"

    # Crest — a tiny gold pip shifted fully off the "10" (down-right) so the
    # number stays legible and the badge no longer smears into the digits.
    pygame.draw.circle(surf, _CAP_OUT, (HX + 6, HY + 17), 3)
    pygame.draw.circle(surf, _CREST_G, (HX + 6, HY + 17), 2)

    # Vertically SPREAD trim so collar / cuff / armband never merge into one
    # gold-white smear at the 40px truth scale.

    # ELEMENT 2 — white sleeve cuff edges at HY+12, between collar and armband.
    pygame.draw.line(surf, (220, 225, 235), (BCX - 10, HY + 12), (BCX - 3, HY + 12), 2)
    pygame.draw.line(surf, (220, 225, 235), (HX + 4, HY + 12), (HX + 10, HY + 12), 2)

    # Gold captain armband — pushed DOWN to the lower near arm (HY+19..21) so
    # it clears the cuff and reads as its own worn band, not collar spill.
    pygame.draw.line(surf, _ARM_SH, (HX + 4, HY + 20), (HX + 11, HY + 22), 4)
    pygame.draw.line(surf, _ARM_GOLD, (HX + 4, HY + 19), (HX + 11, HY + 21), 4)
    pygame.draw.line(surf, (255, 220, 80), (HX + 5, HY + 19), (HX + 9, HY + 20), 1)

    # ELEMENT 1 — crew-neck collar. Raised to STRADDLE the jersey top (centre at
    # y≈HY+5, above the HY+8 shirt edge) so its interior shows the parrot's
    # scarlet neck, not navy chest. Fill scarlet first, then ring it in white.
    collar_rect = pygame.Rect(HX - 9, HY + 1, 15, 8)
    pygame.draw.ellipse(surf, (200, 40, 40), collar_rect.inflate(-4, -3))
    pygame.draw.ellipse(surf, (230, 235, 245), collar_rect, 2)


build = _make_skin(_paint)
