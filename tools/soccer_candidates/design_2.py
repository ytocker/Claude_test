"""SOCCER — THE GOALKEEPER (DESIGN 2 of the SOCCER set).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so production
is untouched.

Concept: where the other soccer looks are outfield strikers, this one reads as
the KEEPER — the position with its own visual language. Two oversized padded
ORANGE GLOVE mitts (one on each wing, drawn LAST in front of everything) are the
hero prop: the biggest, brightest shapes on the sprite, the unmistakable
goalkeeper tell. Beneath them a HV neon-green keeper jersey (the classic
"look at me / distinct from both teams" keeper colour) with a dark back-half for
roundness and a small orange chest diamond, dark charcoal crotch-notch shorts,
neon-green hooped socks, and bright-yellow cleats whose colour IS the accent
(no side stripe competing with the gloves).

At 40px, in order of value: (1) the two big bright-orange mitts breaking both
wing outlines — the keeper read; (2) the neon-green jersey/socks mass; (3) the
yellow cleats; (4) the orange chest diamond. The mitts sit forward of the whole
kit so nothing dulls them; the yellow boots and orange gloves are warm notes
that pop off the cool green on both day and night sky.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, _poly

# Keeper kit palette.
_GK_GREEN    = (57, 211, 83)       # #39D353 neon keeper green (jersey/socks)
_GK_GREEN_D  = (30, 122, 46)       # #1E7A2E back-half shade for roundness
_GK_GREEN_DD = (15, 74, 26)        # #0F4A1A garment outline / sock hoop / collar
_GK_CHARCOAL = (42, 42, 42)        # #2A2A2A shorts
_GK_BLACK    = (10, 10, 10)        # shorts / cleat outline
_GK_YELLOW   = (232, 192, 32)      # #E8C020 hero-yellow cleats
_GK_ORANGE   = (245, 124, 0)       # #F57C00 gloves + chest diamond
_GK_STRAP    = (62, 31, 0)         # #3E1F00 dark-brown knuckle strap
_GK_HI       = (255, 183, 77)      # #FFB74D bright glove highlight

# Named per the brief so the socks/cleats read like the shared soccer kit code.
SOCK_COL   = _GK_GREEN
HOOP_COL   = _GK_GREEN_DD
CLEAT_COL  = _GK_YELLOW
STRIPE_COL = _GK_BLACK


def _paint(surf, _a):
    # ── JERSEY — neon-green keeper shirt hugging the torso, held inside the base
    #    bird footprint (hem ~HY+23) so nothing balloons the silhouette.
    jersey = [(HX - 13, HY + 8), (HX - 14, HY + 18), (HX - 10, HY + 23),
              (HX + 8, HY + 23), (HX + 11, HY + 18), (HX + 9, HY + 8)]
    _poly(surf, _GK_GREEN, jersey)
    # Dark back-half down the off-side so the shirt reads as a rounded torso.
    _poly(surf, _GK_GREEN_D, [(HX + 3, HY + 9), (HX + 9, HY + 8), (HX + 11, HY + 18),
                              (HX + 8, HY + 23), (HX + 4, HY + 22)])
    # Narrow dark-green collar V at the jersey top so the neck reads as a shirt.
    _poly(surf, _GK_GREEN_DD, [(HX - 5, HY + 8), (HX + 4, HY + 8),
                               (HX, HY + 12), (HX - 2, HY + 12)])
    # 1px dark-green garment outline so the shirt holds its edge at 40px.
    pygame.draw.polygon(surf, _GK_GREEN_DD, jersey, 1)
    # Keeper crest — a small dark-green diamond so it reads as a club badge, not a
    # second orange blob competing with the hero gloves.
    pygame.draw.rect(surf, (10, 74, 26), (HX - 7, HY + 10, 5, 5))
    pygame.draw.rect(surf, (0, 30, 0), (HX - 7, HY + 10, 5, 5), 1)

    # ── SHORTS — dark charcoal with a crotch notch (two leg tubes), tucked under
    #    the jersey hem, 1px black outline.
    shorts = [(HX - 10, HY + 23), (HX - 11, HY + 29), (HX - 3, HY + 29),
              (HX - 2, HY + 26), (HX, HY + 26), (HX + 1, HY + 29),
              (HX + 7, HY + 29), (HX + 8, HY + 23)]
    _poly(surf, _GK_CHARCOAL, shorts)
    pygame.draw.polygon(surf, _GK_BLACK, shorts, 1)

    # ── SOCKS — neon-green body with a dark-green hoop at the top, 4px wide,
    #    centred over the feet.
    for sx in (HX - 7, HX + 3):
        pygame.draw.line(surf, SOCK_COL, (sx, HY + 29), (sx, HY + 37), 4)
        pygame.draw.line(surf, HOOP_COL, (sx, HY + 29), (sx, HY + 32), 4)

    # ── CLEATS — bright yellow at the feet; the yellow colour IS the accent, so no
    #    side stripe competing with the gloves. 1px black outline.
    for fx in (HX - 11, HX - 1):
        pygame.draw.rect(surf, CLEAT_COL, (fx, HY + 33, 10, 5), border_radius=2)
        pygame.draw.rect(surf, STRIPE_COL, (fx, HY + 33, 10, 5), 1, border_radius=2)

    # ── GOALKEEPER GLOVES (HERO PROP, drawn LAST so they sit in FRONT of the whole
    #    kit) — two big oversized padded orange mitts dropped to WING height and
    #    outboard, so they break both wing silhouettes instead of drowning in head
    #    plumage. Each has a dark-brown knuckle strap, a 1px dark outline separating
    #    orange from the scarlet wing, a top highlight, and an upward thumb notch.
    #    These are the largest, brightest shapes on the sprite: the keeper tell.
    # LEFT mitt (far wing) at wing height.
    pygame.draw.rect(surf, _GK_ORANGE, (HX - 14, HY + 15, 6, 6), border_radius=3)  # thumb
    pygame.draw.rect(surf, _GK_ORANGE, (HX - 24, HY + 16, 14, 13), border_radius=4)
    pygame.draw.rect(surf, _GK_STRAP, (HX - 24, HY + 16, 14, 3))
    pygame.draw.rect(surf, _GK_STRAP, (HX - 24, HY + 16, 14, 13), 1, border_radius=4)
    pygame.draw.line(surf, _GK_HI, (HX - 23, HY + 17), (HX - 12, HY + 17), 1)
    # RIGHT mitt (near wing) at wing height.
    pygame.draw.rect(surf, _GK_ORANGE, (HX + 8, HY + 15, 6, 6), border_radius=3)  # thumb
    pygame.draw.rect(surf, _GK_ORANGE, (HX + 10, HY + 16, 14, 13), border_radius=4)
    pygame.draw.rect(surf, _GK_STRAP, (HX + 10, HY + 16, 14, 3))
    pygame.draw.rect(surf, _GK_STRAP, (HX + 10, HY + 16, 14, 13), 1, border_radius=4)
    pygame.draw.line(surf, _GK_HI, (HX + 11, HY + 17), (HX + 22, HY + 17), 1)


build = store_skins._make_skin(_paint)
