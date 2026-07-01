"""DESIGN 4 — THE REFEREE (Soccer / Football, v6).

Scratch exploration only — NOT registered in store_skins.BUILDERS, so
production stays untouched. Pip the scarlet macaw kitted as a soccer
REFEREE: an all-black authority kit whose single identity tell is a bright
YELLOW CARD held high in the near wing.

The read is deliberately value-inverted from the player kits: the whole
uniform is near-black (#101010) — jersey, shorts, cleats — so the ONE bright
yellow card owns the eye and cannot be missed at the 40px downscale. White
piping (collar, sleeve edges), a breast-pocket card peeking out, a whistle on
a cord, and a white sock hoop are the only other notes, kept thin so nothing
competes with the raised card. Draw order runs kit-first, hero card LAST so
the yellow always sits in front of the black mass and reads as brandished.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# All-black authority kit, but with internal value steps so the four-layer
# stack (jersey → shorts → socks → cleats) never collapses into one black column.
REF_BLACK  = (16, 16, 16)          # #101010 jersey / cleats
SHORT_COL  = (28, 28, 28)          # #1C1C1C shorts — a hair lifted off the jersey
SOCK_COL   = (24, 24, 24)          # #181818 sock body (a hair lifted off the kit)
HOOP_COL   = (224, 224, 224)       # #E0E0E0 white sock hoop
STRIPE_COL = (224, 224, 224)       # #E0E0E0 white cleat sole stripe
CLEAT_COL  = (16, 16, 16)          # #101010 cleats

# Yellow card — the hero prop, the single brightest + largest element.
CARD_YEL   = (244, 215, 20)        # #F4D719 bright card face
CARD_YEL_H = (255, 240, 100)       # left-edge glint so the flat card reads lit
CARD_DARK  = (160, 140, 0)         # dark card border / pocket-card outline


def _paint(surf, _a):
    # ── JERSEY — near-black field over the torso, held inside the base bird
    #    footprint (hem ~HY+23) so nothing balloons the silhouette. White piping
    #    is the only relief on the black so the shirt still reads as a kit, never
    #    a void, without stealing value from the card.
    jersey = [(HX - 13, HY + 8), (HX - 14, HY + 18), (HX - 10, HY + 23),
              (HX + 8, HY + 23), (HX + 11, HY + 18), (HX + 9, HY + 8)]
    _poly(surf, REF_BLACK, jersey)
    # ONE white collar line — a single seam of relief on the black. A second line
    # only reads as sub-pixel noise at the 40px downscale, so it is dropped.
    pygame.draw.line(surf, (240, 240, 240), (HX - 12, HY + 9), (HX + 10, HY + 9), 1)
    # White sleeve-edge piping down each side so the black shirt has a seam.
    pygame.draw.line(surf, (200, 200, 200), (HX - 13, HY + 9), (HX - 10, HY + 22), 1)
    pygame.draw.line(surf, (200, 200, 200), (HX + 11, HY + 9), (HX + 8, HY + 22), 1)

    # Plain black breast pocket — no competing yellow on the torso; the ONE
    # yellow in the piece is the raised card, kept unrivalled for the hero read.
    pygame.draw.rect(surf, (8, 8, 8), (HX - 6, HY + 13, 5, 5))

    # ── SHORTS — all-black with the crotch notch so the legs read as two, not a
    #    skirt; kept inside the footprint on the feet line.
    shorts = [(HX - 10, HY + 23), (HX - 11, HY + 29), (HX - 3, HY + 29),
              (HX - 2, HY + 26), (HX, HY + 26), (HX + 1, HY + 29),
              (HX + 7, HY + 29), (HX + 8, HY + 23)]
    _poly(surf, SHORT_COL, shorts)

    # ── SOCKS — black body with a bold white hoop over the full HY+29→HY+33 band
    #    so the sock layer separates cleanly from shorts and cleats at 40px.
    for sx in (HX - 7, HX + 3):
        pygame.draw.line(surf, SOCK_COL, (sx, HY + 29), (sx, HY + 37), 4)
        pygame.draw.line(surf, HOOP_COL, (sx, HY + 29), (sx, HY + 33), 4)

    # ── CLEATS — black boots with a bold white sole stripe (2px) at the two feet.
    for fx in (HX - 11, HX - 1):
        pygame.draw.rect(surf, CLEAT_COL, (fx, HY + 33, 10, 5), border_radius=2)
        pygame.draw.line(surf, STRIPE_COL, (fx + 1, HY + 37), (fx + 9, HY + 37), 2)

    # ── HERO PROP · YELLOW CARD — drawn LAST so it sits in front of everything.
    #    Pushed OUTBOARD into clear sky to the right of the head (HX+12) so it no
    #    longer fuses with Pip's yellow beak; isolation against sky is what makes
    #    the card the unmistakable hero read at the 40px downscale.
    pygame.draw.rect(surf, CARD_YEL, (HX + 12, HY - 6, 11, 15), border_radius=1)
    pygame.draw.rect(surf, (140, 120, 0), (HX + 12, HY - 6, 11, 15), 1, border_radius=1)
    # Left-edge glint so the flat yellow face reads as a lit, held card.
    pygame.draw.line(surf, CARD_YEL_H, (HX + 13, HY - 5), (HX + 13, HY + 8), 1)
    # Dark grip block at the card's base — reads as the wing/hand holding it aloft.
    pygame.draw.rect(surf, (20, 20, 20), (HX + 11, HY + 7, 5, 3), border_radius=1)


build = store_skins._make_skin(_paint)
