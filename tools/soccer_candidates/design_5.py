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
    # Loop at the throat — a thick gold band with a thin red stripe under it.
    pygame.draw.line(surf, _GOLD, (HX - 8, HY + 6), (HX + 6, HY + 6), 3)
    pygame.draw.line(surf, _RED, (HX - 8, HY + 7), (HX + 6, HY + 7), 1)
    # Left tail hanging down the near side.
    pygame.draw.line(surf, _GOLD, (HX - 6, HY + 7), (HX - 8, HY + 32), 3)
    pygame.draw.line(surf, _RED, (HX - 5, HY + 7), (HX - 7, HY + 32), 1)
    # Right tail — longer, for asymmetry so it reads as waving, not symmetrical.
    pygame.draw.line(surf, _GOLD, (HX + 4, HY + 7), (HX + 6, HY + 38), 3)
    pygame.draw.line(surf, _RED, (HX + 3, HY + 7), (HX + 5, HY + 38), 1)
    # Fringe ticks at the tail ends so the scarf reads as tasseled cloth.
    for ty in (HY + 32, HY + 33, HY + 34):
        pygame.draw.line(surf, _GOLD, (HX - 10, ty), (HX - 6, ty), 1)
    for ty in (HY + 38, HY + 39, HY + 40):
        pygame.draw.line(surf, _GOLD, (HX + 4, ty), (HX + 8, ty), 1)


build = store_skins._make_skin(_paint)
