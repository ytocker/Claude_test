"""THE ULTRA FAN — Pip kitted as a supporter (DESIGN 5 of the SOCCER set).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so production
is untouched.

Architecture: the whole jersey is the BODY itself — the macaw body oval is
re-plumaged bold club-red through the palette system (like the ninja/mummy
skins), and the paint pass clips two bold white HOOPS directly OVER that body
oval. That fixes the earlier flat-polygon jersey, which anchored to the head
centre and missed the belly entirely. Head stays macaw-red and wings stay
macaw-blue, so the recoloured red body reads as the shirt over the bird's frame.

The read at 40px, in order of value: (1) the gold club SCARF looping the throat
with ONE bold tail streaming UP-BACK into open sky above the shoulder — a scarf
only reads as a scarf when its tail lives in clear sky, so the negative space is
doing the work; (2) the red body with two wide white hoops; (3) the red bobble
hat + gold pompom owning the crown; (4) near-black shorts / socks / cleats
anchoring the feet line. Zones are kept apart on purpose: body hoops own the
upper belly, dark shorts own a clean band at the bottom, scarf owns the throat +
sky — so nothing collides in the mid-belly.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (
    BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
)

# Body centre in COMPOSITE space (parrot body centre (32,32) + PARROT_DY=20).
BCX, BCY = 32, 52

# Club terrace palette — bold red jersey body, gold scarf/pompom accent, white
# hoops/socks. The body slots go red so the recolour reads as the shirt; head
# stays scarlet macaw, wings stay the macaw blue, so the bird underneath the kit
# is still Pip.
_RED       = (192, 57, 43)         # #C0392B club red (jersey body)
_WHITE     = (245, 245, 250)       # hoop / sock white
_BODY_EDGE = (140, 35, 22)         # 1px red outline holding the body oval edge
_SHORTS    = (58, 10, 4)           # near-black maroon shorts (anchors the bottom)
_SHORTS_DK = (80, 15, 6)           # shorts edge (a value above the near-black shorts)
_SOCK_COL  = (245, 245, 245)       # #F5F5F5 white sock body
_HOOP_COL  = (192, 57, 43)         # red sock hoop
_CLEAT_COL = (28, 28, 36)          # #1C1C24 near-black cleats
_GOLD      = (244, 200, 32)        # scarf gold
_GOLD_DK   = (100, 70, 0)          # dark gold scarf backing
_SCARF_R   = (192, 57, 43)         # red centre stripe on the scarf tail
_POM_GOLD  = (244, 208, 63)        # #F4D03F pompom gold
_POM_HI    = (255, 230, 100)       # pompom highlight

# Red jersey re-plumage: body slots go club-red, everything else stays macaw so
# the head reads scarlet, the wings macaw-blue, the beak gold. Lenses kept (the
# fan still wears the aviators) via the default draw_lenses=True.
_PAL = _pal(
    tail=[(200, 30, 40), (240, 95, 40), (255, 160, 55), (255, 220, 80)],
    tail_line=(170, 25, 25),
    body_shadow=(120, 28, 18),
    body_main=(192, 57, 43),
    body_chest=(210, 72, 55),
    body_belly=(165, 45, 35),
    sheen=None,
    wing_main=BIRD_WING,
    wing_dark=BIRD_WING_D,
    wing_tip=BIRD_TIP,
    wing_secondary=(255, 200, 60),
    wing_highlight=(170, 210, 255),
    head_shadow=(150, 15, 20),
    head_main=BIRD_RED,
    head_cheek=(255, 130, 130),
    head_crown=(255, 170, 170),
    lens_frame=(255, 200, 50),
    lens_body=(20, 20, 30),
    lens_tint=(35, 55, 90, 130),
    lens_glint=(255, 255, 255),
    beak_main=BIRD_BEAK,
    beak_dark=BIRD_BEAK_D,
    beak_gloss=(255, 230, 150),
    foot=BIRD_BEAK_D,
)


def _base(angle_deg):
    return _build_parrot_with_palette(angle_deg, _PAL)


def _paint(surf, _a):
    # ── JERSEY HOOPS — TWO wide white bands (5px) clipped to the body-oval
    #    bounding rect so they read as a hooped supporter shirt over the red body.
    #    Three thin hoops merged into a blur at the 40px downscale; two wider,
    #    evenly-spaced hoops hold their gaps and own the upper belly cleanly.
    clip_prev = surf.get_clip()
    surf.set_clip(pygame.Rect(BCX - 19, BCY - 14, 38, 28))
    for sy in (BCY - 7, BCY + 3):
        pygame.draw.rect(surf, _WHITE, (BCX - 19, sy, 38, 5))
    surf.set_clip(clip_prev)
    # 1px red outline holds the body-oval edge so the clipped hoops don't fray
    # the silhouette.
    pygame.draw.ellipse(surf, _BODY_EDGE, (BCX - 19, BCY - 14, 38, 28), 1)

    # ── SHORTS — near-black maroon owning a clean band at the very bottom of the
    #    body, well below the hoops, so the kit layers (jersey → shorts → white
    #    socks → black cleats) stay legible and the shorts anchor the feet line
    #    instead of melting into the red body.
    pygame.draw.ellipse(surf, _SHORTS, (BCX - 9, BCY + 7, 20, 9))
    pygame.draw.ellipse(surf, _SHORTS_DK, (BCX - 9, BCY + 7, 20, 9), 1)

    # ── SOCKS — white body with a red club hoop at the top, at the two feet x's.
    for sx in (27, 35):
        pygame.draw.line(surf, _SOCK_COL, (sx, BCY + 11), (sx, BCY + 17), 4)
        pygame.draw.line(surf, _HOOP_COL, (sx, BCY + 12), (sx, BCY + 14), 4)

    # ── CLEATS — near-black boots at the feet line.
    for fx in (23, 31):
        pygame.draw.rect(surf, _CLEAT_COL, (fx, BCY + 14, 9, 5), border_radius=1)

    # ── BOBBLE HAT — a small red dome on the crown capped by a gold pompom that
    #    breaks the crown outline (the fan tell up top). Crown centre in composite
    #    is (HX, CROWN_Y); the dome sits just above it.
    hat_cx, hat_cy = HX - 2, CROWN_Y - 3
    pygame.draw.ellipse(surf, _RED, (hat_cx - 8, hat_cy - 5, 16, 10))
    pygame.draw.ellipse(surf, _BODY_EDGE, (hat_cx - 8, hat_cy - 5, 16, 10), 1)
    pygame.draw.circle(surf, _POM_GOLD, (hat_cx, hat_cy - 5), 4)
    pygame.draw.circle(surf, _POM_HI, (hat_cx - 1, hat_cy - 6), 2)

    # ── SCARF (HERO PROP, drawn LAST so it overlays every kit layer) — a gold
    #    club scarf looped at the throat with ONE bold tail streaming UP and BACK
    #    into the open sky above/behind the shoulder. A scarf only reads as a
    #    scarf when its tail lives in clear sky, so the tail exits the body upward
    #    into negative space rather than lying over the striped belly (where the
    #    old twin tails collided with the hoops and vanished).
    # Throat loop — wraps the neck/head-body junction, dark gold backing under a
    #    bright gold band.
    tx, ty = HX - 6, HY + 3
    pygame.draw.line(surf, _GOLD_DK, (tx - 4, ty), (tx + 6, ty - 2), 5)
    pygame.draw.line(surf, _GOLD, (tx - 4, ty - 1), (tx + 6, ty - 3), 3)

    # ONE bold tail — arcs up-left off the throat, past the top of the body, and
    #    well into clear sky above the bird; red centre stripe over gold face over
    #    a dark-gold backing so the cloth reads as a hooped club scarf.
    tail_pts = [
        (tx - 3, ty),
        (BCX - 14, BCY - 18),
        (BCX - 22, BCY - 28),
        (BCX - 20, BCY - 38),
    ]
    for i in range(len(tail_pts) - 1):
        pygame.draw.line(surf, _GOLD_DK, tail_pts[i], tail_pts[i + 1], 5)
        pygame.draw.line(surf, _GOLD, tail_pts[i], tail_pts[i + 1], 3)
        pygame.draw.line(surf, _SCARF_R, tail_pts[i], tail_pts[i + 1], 1)

    # Bold tassel cap at the tail end — the visual period out in open sky.
    pygame.draw.circle(surf, _GOLD_DK, tail_pts[-1], 5)
    pygame.draw.circle(surf, _GOLD, tail_pts[-1], 4)
    pygame.draw.circle(surf, _POM_HI, (tail_pts[-1][0] - 1, tail_pts[-1][1] - 1), 2)


build = _make_skin(_paint, base_fn=_base)
