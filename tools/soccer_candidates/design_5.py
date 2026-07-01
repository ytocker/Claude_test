"""Soccer v9 Design 5 — GERMANY "DIE MANNSCHAFT" white-dominance (body-recolor).

Germany's home kit is famously almost pure white with minimal black trim, so
the jersey IS the body: the macaw's torso oval is re-plumaged clean white
through the palette system (like the ninja skin recolors the whole bird), while
the head stays macaw-red and the wings stay macaw-blue.

No tricolour sash — an earlier diagonal black/red/gold band fused with the red
head and echoed the gold beak, reading as a rainbow blob at 40px. Instead the
white torso carries the modern DFB accents: a single bold black horizontal
chest stripe placed low in the mid-chest (clear of the red head/beak), a black
V-collar that hard-separates the white jersey from the red head, and a small
black eagle-crest disc marked with a white cross. Black shorts, black-hooped
white socks, and near-black cleats finish the kit.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (
    BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
)

# ── kit trim colours (drawn in _paint, over the white body) ──────────────────
_BLACK    = ( 10,  10,  12)   # collar + chest stripe + eagle badge + shorts
_SHORT_R  = ( 28,  28,  36)   # #1C1C24 shorts rim, reused for near-black cleats
_JRS_W    = (242, 242, 242)   # jersey white, reused for crotch notch + sock shank

# The body oval is re-plumaged WHITE so the jersey IS the body colour. Head
# stays macaw-red, wings stay macaw-blue — so only the torso reads as the kit
# and the bird keeps its identity.
_PAL = _pal(
    tail=[(200, 30, 40), (240, 95, 40), (255, 160, 55), (255, 220, 80)],
    tail_line=(170, 25, 25),
    body_shadow=(185, 185, 195),      # jersey back-half shade (rounds torso)
    body_main=(242, 242, 242),        # jersey white field
    body_chest=(250, 250, 250),       # lit chest
    body_belly=(215, 215, 220),       # slightly cooler belly
    sheen=(255, 255, 255, 100),
    wing_main=BIRD_WING,              # keep macaw-blue wings
    wing_dark=BIRD_WING_D,
    wing_tip=BIRD_TIP,
    wing_secondary=(255, 200, 60),
    wing_highlight=(170, 210, 255),
    head_shadow=(150, 15, 20),        # keep macaw-red head
    head_main=BIRD_RED,
    head_cheek=(255, 130, 130),
    head_crown=(255, 170, 170),
    lens_frame=(255, 200, 50),        # keep aviator shades
    lens_body=(20, 20, 30),
    lens_tint=(35, 55, 90, 130),
    lens_glint=(255, 255, 255),
    beak_main=BIRD_BEAK,
    beak_dark=BIRD_BEAK_D,
    beak_gloss=(255, 230, 150),
    foot=BIRD_BEAK_D,
)

# Body centre in COMPOSITE space (sprite body centre (32,32) + PARROT_DY=20).
BCX, BCY = 32, 52


def _base(angle_deg):
    return _build_parrot_with_palette(angle_deg, _PAL)


def _paint(surf, _a):
    # All geometry here is in COMPOSITE space (the 64×100 canvas). The body is
    # already white from _base; the trim below turns the recolor into the kit.

    # Body oval outline — a 1px cool ring so the white torso stays legible
    # against a bright sky instead of dissolving into the background.
    pygame.draw.ellipse(surf, (185, 185, 195), (BCX - 19, BCY - 14, 38, 28), 1)

    # Black V-collar — the critical separator so the white jersey doesn't fuse
    # into the red head. Two lines meeting just below the head.
    pygame.draw.line(surf, _BLACK, (BCX - 6, BCY - 12), (BCX + 2, BCY - 8), 2)
    pygame.draw.line(surf, _BLACK, (BCX + 8, BCY - 12), (BCX + 2, BCY - 8), 2)

    # Bold black horizontal chest stripe — the classic modern DFB accent, placed
    # low in the mid-chest (well clear of the red head and gold beak so it can't
    # fuse with either).
    pygame.draw.line(surf, _BLACK, (BCX - 17, BCY - 5), (BCX + 17, BCY - 5), 3)

    # Eagle-crest badge — a small black disc marked with a white cross so the
    # dark spot reads as the DFB badge, pinning the kit to Germany specifically.
    pygame.draw.circle(surf, _BLACK, (BCX - 8, BCY - 7), 4)
    pygame.draw.line(surf, _JRS_W, (BCX - 11, BCY - 7), (BCX - 5, BCY - 7), 1)
    pygame.draw.line(surf, _JRS_W, (BCX - 8, BCY - 10), (BCX - 8, BCY - 4), 1)

    # Jersey hem — a 1px light ellipse so the shirt bottom separates from the
    # black shorts below instead of fusing into one dark kit blob.
    pygame.draw.ellipse(surf, (220, 220, 226), (BCX - 9, BCY + 5, 20, 2), 1)

    # Black shorts, with a lighter rim so the leg-line stays crisp against the
    # white torso.
    pygame.draw.ellipse(surf, _BLACK, (BCX - 9, BCY + 7, 20, 9))
    pygame.draw.ellipse(surf, _SHORT_R, (BCX - 9, BCY + 7, 20, 9), 1)
    # Crotch notch so the two leg tubes read as separate legs, not a skirt.
    _poly(surf, _JRS_W,
          [(BCX - 1, BCY + 12), (BCX + 3, BCY + 12), (BCX + 1, BCY + 15)])

    # Socks — white shanks with a black turn-over hoop, one per leg. Shortened to
    # leave a clean gap above the cleats so the kit stack stays legible.
    for sx in (27, 35):
        pygame.draw.line(surf, _JRS_W, (sx, BCY + 11), (sx, BCY + 16), 4)
        pygame.draw.line(surf, _BLACK, (sx, BCY + 12), (sx, BCY + 14), 3)

    # Cleats — near-black boots below the socks with a visible gap.
    for cx in (23, 31):
        pygame.draw.rect(surf, _SHORT_R, (cx, BCY + 14, 9, 5), border_radius=1)


build = _make_skin(_paint, base_fn=_base)
