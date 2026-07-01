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

# All-black authority kit — one near-black body value so the yellow card is the
# single bright element that carries the read at 40px.
REF_BLACK  = (16, 16, 16)          # #101010 jersey / shorts / cleats
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
    # White collar piping — two thin lines at the jersey top (bright over dim).
    pygame.draw.line(surf, (240, 240, 240), (HX - 12, HY + 9), (HX + 10, HY + 9), 1)
    pygame.draw.line(surf, (180, 180, 180), (HX - 12, HY + 11), (HX + 10, HY + 11), 1)
    # White sleeve-edge piping down each side so the black shirt has a seam.
    pygame.draw.line(surf, (200, 200, 200), (HX - 13, HY + 9), (HX - 10, HY + 22), 1)
    pygame.draw.line(surf, (200, 200, 200), (HX + 11, HY + 9), (HX + 8, HY + 22), 1)

    # Breast pocket with a yellow card peeking out — a tiny yellow tab above the
    # pocket edge so it reads as a spare card tucked in the shirt (the second,
    # quieter yellow that ties the identity to the torso, not just the raised hand).
    pygame.draw.rect(surf, CARD_YEL, (HX - 6, HY + 13, 5, 5))
    pygame.draw.rect(surf, CARD_DARK, (HX - 6, HY + 13, 5, 5), 1)

    # Whistle on a cord — a short dark cord arc from the collar to a small silver
    # whistle body, the classic ref cue kept low-value so it doesn't fight the card.
    pygame.draw.lines(surf, (48, 48, 48), False,
                      [(HX - 2, HY + 9), (HX + 1, HY + 12), (HX + 4, HY + 12)], 1)
    pygame.draw.rect(surf, (196, 200, 208), (HX + 4, HY + 11, 3, 2))
    pygame.draw.line(surf, (240, 244, 250), (HX + 4, HY + 11), (HX + 6, HY + 11), 1)

    # ── SHORTS — all-black with the crotch notch so the legs read as two, not a
    #    skirt; kept inside the footprint on the feet line.
    shorts = [(HX - 10, HY + 23), (HX - 11, HY + 29), (HX - 3, HY + 29),
              (HX - 2, HY + 26), (HX, HY + 26), (HX + 1, HY + 29),
              (HX + 7, HY + 29), (HX + 8, HY + 23)]
    _poly(surf, REF_BLACK, shorts)

    # ── SOCKS — black body with a white hoop at the top over each shin.
    for sx in (HX - 7, HX + 3):
        pygame.draw.line(surf, SOCK_COL, (sx, HY + 29), (sx, HY + 37), 4)
        pygame.draw.line(surf, HOOP_COL, (sx, HY + 29), (sx, HY + 32), 4)

    # ── CLEATS — black boots with a white sole stripe at the two feet (x≈36, 46).
    for fx in (HX - 11, HX - 1):
        pygame.draw.rect(surf, CLEAT_COL, (fx, HY + 33, 10, 5), border_radius=2)
        pygame.draw.line(surf, STRIPE_COL, (fx + 1, HY + 37), (fx + 9, HY + 37), 1)

    # ── HERO PROP · YELLOW CARD — drawn LAST so it sits in front of the entire
    #    black kit: a bright yellow card brandished HIGH in the near (right) wing.
    #    It is the single brightest AND largest element, the referee's whole tell,
    #    lifted toward the crown so it breaks the silhouette against open sky.
    pygame.draw.rect(surf, CARD_YEL, (HX + 6, HY - 2, 10, 14), border_radius=1)
    pygame.draw.rect(surf, CARD_DARK, (HX + 6, HY - 2, 10, 14), 1)
    # Left-edge highlight so the flat yellow face reads as a lit, held card.
    pygame.draw.line(surf, CARD_YEL_H, (HX + 7, HY - 1), (HX + 7, HY + 11), 1)


build = store_skins._make_skin(_paint)
