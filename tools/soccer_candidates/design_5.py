"""THE ULTRA FAN — Pip kitted as a supporter (DESIGN 5 of the SOCCER set).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so production
is untouched.

Concept: the terrace-supporter look. Where the other soccer designs read as a
player on the pitch, this one reads as the fan in the stands — a horizontal
red/white hooped jersey, a red bobble hat with a gold pompom breaking the crown,
and the HERO PROP: a gold/red club scarf looped once at the throat with two
staggered tails waving in the wind. At 40px, in order of value: (1) the scarf
tails streaming down the body as two bright gold diagonals, (2) the red/white
hooped jersey mass, (3) the bobble hat + gold pompom owning the crown, (4) the
socks/cleats at the feet line. The scarf is drawn LAST so it overlays every
kit layer and carries the read alone.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Club red/white/gold — the terrace palette. Red is the jersey base, white the
# hoops + sock body, gold the scarf + pompom hero accent.
_RED       = (192, 57, 43)         # #C0392B club red
_WHITE     = (245, 245, 245)       # #F5F5F5 hoop / sock white
_RED_DK    = (120, 30, 20)         # jersey outline / dark red V collar
_SHT       = (55, 10, 8)           # near-black maroon shorts — one value below the red jersey
_SHORT_DK  = (30, 5, 4)            # shorts outline
_SOCK_COL  = (245, 245, 245)       # white sock body
_HOOP_COL  = (192, 57, 43)         # red sock hoop
_CLEAT_COL = (28, 28, 36)          # #1C1C24 near-black cleats
_GOLD      = (244, 208, 63)        # #F4D03F scarf / pompom gold
_GOLD_DK   = (120, 80, 0)          # dark gold throat-loop edge


def _paint(surf, _a):
    # ── JERSEY — horizontal red/white HOOPS. Fill the polygon red, then clip to
    #    the jersey rect and lay white bands across so the hoops read as a
    #    supporter shirt, not a plain field. Kept INSIDE the base footprint
    #    (bottom ~HY+23) so nothing balloons the silhouette.
    jersey = [(HX - 13, HY + 8), (HX - 14, HY + 18), (HX - 10, HY + 23),
              (HX + 8, HY + 23), (HX + 11, HY + 18), (HX + 9, HY + 8)]
    _poly(surf, _RED, jersey)  # red base
    # THREE fat 4px white bands over the red base — thin lines vanish against a
    # red bird at 40px, so the hoops must be wide enough to survive downscale
    # and read as a white-dominant hooped supporter kit.
    clip_prev = surf.get_clip()
    surf.set_clip(pygame.Rect(HX - 14, HY + 8, 26, 17))
    for sy in (HY + 9, HY + 14, HY + 19):
        pygame.draw.line(surf, _WHITE, (HX - 14, sy), (HX + 13, sy), 4)
    surf.set_clip(clip_prev)
    pygame.draw.polygon(surf, _RED_DK, jersey, 1)  # dark outline
    # Dark-red V collar at the jersey top so the neck reads as a shirt opening.
    _poly(surf, _RED_DK, [(HX - 4, HY + 8), (HX + 4, HY + 8), (HX, HY + 12)])

    # ── SHORTS — near-black maroon so they sit a full value below the red
    #    jersey; that value break (jersey → shorts → white socks → black cleats)
    #    keeps the four kit layers legible instead of one red smear. Crotch
    #    notch keeps the legs reading as two limbs.
    shorts = [(HX - 10, HY + 23), (HX - 11, HY + 29), (HX - 3, HY + 29),
              (HX - 2, HY + 26), (HX, HY + 26), (HX + 1, HY + 29),
              (HX + 7, HY + 29), (HX + 8, HY + 23)]
    _poly(surf, _SHT, shorts)
    pygame.draw.polygon(surf, _SHORT_DK, shorts, 1)

    # ── SOCKS — white body, red hoop at the top (the club sock band).
    for sx in (HX - 7, HX + 3):
        pygame.draw.line(surf, _SOCK_COL, (sx, HY + 29), (sx, HY + 37), 4)
        pygame.draw.line(surf, _HOOP_COL, (sx, HY + 29), (sx, HY + 32), 4)

    # ── CLEATS at the feet (HX-11, HX-1) — near-black boots, no stripe.
    for fx in (HX - 11, HX - 1):
        pygame.draw.rect(surf, _CLEAT_COL, (fx, HY + 33, 10, 5), border_radius=2)

    # ── BOBBLE HAT on the crown — a small red dome capped by a gold pompom that
    #    breaks the crown outline (the fan tell up top).
    pygame.draw.ellipse(surf, _RED, (HX - 8, CROWN_Y - 8, 16, 12))
    pygame.draw.ellipse(surf, _RED_DK, (HX - 8, CROWN_Y - 8, 16, 12), 1)
    pygame.draw.circle(surf, _GOLD, (HX, CROWN_Y - 10), 3)

    # ── SCARF (HERO PROP, drawn LAST so it overlays every kit layer) — a gold/red
    #    club scarf looped once at the throat with two staggered tails waving in
    #    the wind. The two bright gold tails streaming down the body are the
    #    single highest-value diagonals at 40px, so the supporter reads instantly.
    # Loop at the throat — a dark gold edge laid first so the loop separates
    #    cleanly from the beak, then the bright gold band and a thin red accent.
    pygame.draw.line(surf, _GOLD_DK, (HX - 9, HY + 6), (HX + 7, HY + 6), 5)  # dark edge
    pygame.draw.line(surf, _GOLD, (HX - 8, HY + 6), (HX + 6, HY + 6), 3)     # gold top
    pygame.draw.line(surf, _RED, (HX - 8, HY + 7), (HX + 6, HY + 7), 1)      # red accent
    # Left tail — kinked S-curve so it reads as cloth waving in the wind, not a
    #    straight stick. Gold body with a 1px red shadow offset down-right.
    pts_L = [(HX - 6, HY + 7), (HX - 9, HY + 18), (HX - 6, HY + 27), (HX - 9, HY + 34)]
    for i in range(len(pts_L) - 1):
        pygame.draw.line(surf, _GOLD, pts_L[i], pts_L[i + 1], 3)
        pygame.draw.line(surf, _RED,
                         (pts_L[i][0] + 1, pts_L[i][1] + 1),
                         (pts_L[i + 1][0] + 1, pts_L[i + 1][1] + 1), 1)
    # Right tail — longer, opposite phase, for the asymmetric waving read.
    pts_R = [(HX + 4, HY + 7), (HX + 7, HY + 20), (HX + 3, HY + 31), (HX + 7, HY + 40)]
    for i in range(len(pts_R) - 1):
        pygame.draw.line(surf, _GOLD, pts_R[i], pts_R[i + 1], 3)
        pygame.draw.line(surf, _RED,
                         (pts_R[i][0] + 1, pts_R[i][1] + 1),
                         (pts_R[i + 1][0] + 1, pts_R[i + 1][1] + 1), 1)
    # Horizontal tassel caps at each tail end so the scarf reads as tasseled cloth.
    pygame.draw.line(surf, _GOLD, (pts_L[-2][0] - 2, pts_L[-1][1]), (pts_L[-2][0] + 4, pts_L[-1][1]), 4)
    pygame.draw.line(surf, _GOLD, (pts_R[-2][0] - 2, pts_R[-1][1]), (pts_R[-2][0] + 4, pts_R[-1][1]), 4)


build = store_skins._make_skin(_paint)
