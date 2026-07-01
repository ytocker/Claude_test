"""SOCCER — BRAZIL "CANARINHO" (DESIGN 2 of the SOCCER set).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so production
is untouched.

Concept: the jersey IS the body. The whole body oval is recoloured through the
palette system (the ninja/cockatoo route) to Brazil's canary yellow #FFCB05, so
Pip reads as the Seleção kit from chest to belly. The head stays macaw-red and
the wings stay macaw-blue so he's still recognisably himself, just kitted out.

The Canarinho read is carried entirely by TRIM, not stripes — a plain canary
field is what makes this jersey iconic, so the green oval border, green V-collar
+ shoulder line, and the little green crest diamond do all the talking. The
shorts are Brazil royal blue and the socks are white with a single green hoop.
At 40px the value order is (1) yellow torso mass, (2) the green outline + collar
framing it, (3) the blue shorts and green sock hoop below.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP


# Canarinho kit — the body oval is recoloured to canary yellow; the head is kept
# macaw-red so Pip stays recognisable under the jersey.
_PAL = _pal(
    tail=[(200, 30, 40), (240, 95, 40), (255, 160, 55), (255, 220, 80)],
    tail_line=(170, 25, 25),
    body_shadow=(205, 162, 0),      # jersey drop-shade for roundness
    body_main=(255, 203, 5),        # #FFCB05 canary yellow field
    body_chest=(255, 215, 20),      # lit upper chest
    body_belly=(230, 180, 0),       # shaded lower belly
    sheen=(255, 240, 80, 70),       # soft jersey sheen band
    wing_main=BIRD_WING,            # keep macaw-blue wings
    wing_dark=BIRD_WING_D,
    wing_tip=BIRD_TIP,
    wing_secondary=(255, 200, 60),
    wing_highlight=(170, 210, 255),
    head_shadow=(150, 15, 20),      # keep macaw-red head
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

# Body centre in COMPOSITE space (base body centre (32,32) + PARROT_DY 20 on y).
BCX, BCY = 32, 52

_GREEN    = (0, 156, 59)        # #009C3B Brazil green — border, collar, crest, hoop
_GREEN_D  = (0, 96, 36)         # crest/diamond dark outline
_SHT      = (30, 58, 138)       # #1E3A8A royal-blue shorts
_SHT_D    = (18, 38, 100)       # shorts darker rim
_SCK      = (245, 245, 250)     # white sock
_CLT      = (28, 28, 36)        # #1C1C24 near-black cleats


def _base(angle_deg):
    return _build_parrot_with_palette(angle_deg, _PAL)


def _paint(surf, _a):
    # ── GREEN OVAL BORDER — traces the recoloured torso so the plain canary
    #    field reads as a framed jersey rather than yellow feathers. This is the
    #    single strongest Canarinho tell at 40px.
    pygame.draw.ellipse(surf, _GREEN, (BCX - 19, BCY - 14, 38, 28), 2)

    # ── V-COLLAR + SHOULDER TRIM — two green strokes meeting at a point under the
    #    neck, capped by a horizontal shoulder line, so the yellow torso reads as
    #    a collared Seleção shirt right below the red head.
    pygame.draw.line(surf, _GREEN, (BCX - 6, BCY - 12), (BCX + 2, BCY - 8), 2)
    pygame.draw.line(surf, _GREEN, (BCX + 8, BCY - 12), (BCX + 2, BCY - 8), 2)
    pygame.draw.line(surf, _GREEN, (BCX - 6, BCY - 12), (BCX + 8, BCY - 12), 3)

    # ── CREST BADGE — a small green lozenge/diamond on the chest with a dark
    #    outline; reads as the CBF-style team crest, not a stray dot.
    dcx, dcy = BCX + 5, BCY - 4
    diamond = [(dcx, dcy - 3), (dcx + 4, dcy), (dcx, dcy + 3), (dcx - 4, dcy)]
    _poly(surf, _GREEN, diamond)
    pygame.draw.polygon(surf, _GREEN_D, diamond, 1)

    # ── SLEEVE SEAM ARCS — a green stroke at each wing root anchors the jersey
    #    read so the wings look like they emerge from fabric sleeves.
    pygame.draw.line(surf, _GREEN, (BCX + 8, BCY - 10), (BCX + 16, BCY - 4), 1)
    pygame.draw.line(surf, _GREEN, (BCX - 6, BCY - 10), (BCX - 14, BCY - 4), 1)

    # ── SHORTS — royal-blue ellipse with a darker rim, the cool block that
    #    grounds the warm yellow torso.
    pygame.draw.ellipse(surf, _SHT, (BCX - 9, BCY + 7, 20, 9))
    pygame.draw.ellipse(surf, _SHT_D, (BCX - 9, BCY + 7, 20, 9), 1)

    # ── SOCKS — white shanks with a single green turn-over hoop, one per leg.
    for sx in (27, 35):
        pygame.draw.line(surf, _SCK, (sx, BCY + 11), (sx, BCY + 16), 4)
        pygame.draw.line(surf, _GREEN, (sx, BCY + 12), (sx, BCY + 14), 4)

    # ── CLEATS — near-black boots below the socks with a visible gap so the kit
    #    stack (yellow / blue / white / black) stays legible at 40px.
    for cx in (23, 31):
        pygame.draw.rect(surf, _CLT, (cx, BCY + 14, 9, 5), border_radius=1)


build = _make_skin(_paint, base_fn=_base)
