"""Soccer D5 — THE GOLDEN WHISTLE.

Pip the referee reimagined as a CHARACTER rather than a shirt. The scarlet
macaw body stays visible in the centre; the costume is a stack of props that
break the outline and read at 40px: an oversized YELLOW CARD brandished high
on the far wing (the hero prop, drawn last so it sits in front), a fat GOLD
ARMBAND wrapping the near wing arm, a silver WHISTLE on a dark cord at the
throat, and 2-3 bold black/white referee accent STRIPES down each FLANK ONLY
so the scarlet chest is never covered. Boots stay minimal so nothing competes
with the card. The yellow card is the brightest, biggest element — it owns the
read even downscaled.
"""
import pygame
from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin

# Body centre in composite space — the flank stripes / props hang off this.
BCX, BCY = 32, 52

# The card is the single brightest note; every other colour is held below it so
# nothing steals the hero read. Stripes are pure ref black/white on the flanks.
_CARD_Y  = (244, 213, 20)            # brandished yellow card (brightest note)
_CARD_BD = (160, 140, 0)             # card border / dark keyline
_SILVER  = (190, 196, 202)           # whistle body
_GOLD    = (240, 190, 30)            # captain armband gold
_GOLD_H  = (255, 220, 80)            # armband highlight
_STR_B   = (20, 20, 20)              # ref black flank stripe
_STR_W   = (240, 240, 240)           # ref white flank stripe
_BOOT_D  = (26, 24, 32)              # minimal dark boots


def _paint(surf, _a):
    # 1 — FLANK STRIPES (drawn first, under the props): 2 bold black/white
    #     vertical stripes down each flank ONLY. The scarlet centre between the
    #     two flank pairs stays untouched so the body reads as Pip, not a shirt.
    # Left flank.
    pygame.draw.line(surf, _STR_B, (BCX - 10, HY + 5), (BCX - 9, HY + 20), 3)
    pygame.draw.line(surf, _STR_W, (BCX - 6, HY + 5), (BCX - 5, HY + 20), 2)
    # Right flank.
    pygame.draw.line(surf, _STR_B, (HX + 5, HY + 5), (HX + 6, HY + 20), 3)
    pygame.draw.line(surf, _STR_W, (HX + 9, HY + 5), (HX + 10, HY + 20), 2)

    # 2 — minimal dark boots at the feet so nothing balloons the silhouette and
    #     the card keeps the read.
    for fx in (HX - 7, HX + 3):
        pygame.draw.ellipse(surf, _BOOT_D, (fx - 4, HY + 24, 9, 5))

    # 3 — WHISTLE NECKLACE: a dark cord arc under the chin, then a small
    #     horizontal silver whistle with its hole — the referee's tell at the
    #     throat, kept off the scarlet chest centre by riding low on the neck.
    pygame.draw.arc(surf, (60, 50, 40), pygame.Rect(HX - 8, HY - 2, 16, 12), 3.7, 5.8, 1)
    pygame.draw.rect(surf, _SILVER, (HX - 3, HY + 6, 7, 4), border_radius=2)
    pygame.draw.circle(surf, (100, 100, 110), (HX, HY + 8), 2)

    # 4 — GOLD ARMBAND on the near (right) wing arm: a thick captain's band with
    #     a bright highlight so it reads as metal, not a flat stripe, at 40px.
    pygame.draw.line(surf, _GOLD, (HX + 4, BCY - 6), (HX + 12, BCY - 4), 5)
    pygame.draw.line(surf, _GOLD_H, (HX + 5, BCY - 7), (HX + 11, BCY - 5), 2)

    # 5 — YELLOW CARD brandished high on the far (left) wing — drawn LAST so it
    #     sits in FRONT of everything. The single biggest/brightest shape: it
    #     must read immediately at 40px as a ref holding a card aloft.
    pygame.draw.rect(surf, _CARD_Y, (BCX - 18, BCY - 14, 10, 14), border_radius=1)
    pygame.draw.rect(surf, _CARD_BD, (BCX - 18, BCY - 14, 10, 14), 1)


build = _make_skin(_paint)
