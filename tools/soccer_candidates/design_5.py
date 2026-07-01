"""Soccer v9 Design 5 — GERMANY "DIE MANNSCHAFT" (body-recolor approach).

The jersey IS the body: the macaw's torso oval is re-plumaged clean white
through the palette system (like the ninja skin recolors the whole bird),
while the head stays macaw-red and the wings stay macaw-blue. Over that white
torso the _paint pass lays the German tricolour diagonal sash (black/red/gold)
that make the kit instantly read as Germany — plus a black V-collar, the black
eagle crest shield, black shorts, black-hooped white socks, and near-black
cleats.

At 40px the read is a white bird with a black-red-gold flash slashed across
the chest — Die Mannschaft — while the head/wings/beak keep the macaw identity.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (
    BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
)

# ── kit trim colours (drawn in _paint, over the white body) ──────────────────
_BLACK    = ( 10,  10,  12)   # tricolour black band + collar + eagle crest + shorts
_RED      = (200,  16,  46)   # #C8102E tricolour red band
_GOLD     = (255, 204,   0)   # #FFCC00 tricolour gold band
_SHORT_R  = ( 28,  28,  36)   # #1C1C24 shorts rim, reused for near-black cleats
_JRS_W    = (242, 242, 242)   # jersey white, reused for the sock shank + eagle fill
_CLEAT    = ( 28,  28,  36)   # #1C1C24 near-black cleat

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

    # German tricolour diagonal sash — the signature Die Mannschaft flash. Three
    # black/red/gold bands slashed from upper-right to lower-left across the mid
    # torso, clipped to the body oval so the flag stops at the torso edge instead
    # of bleeding onto the wings/tail.
    clip_prev = surf.get_clip()
    surf.set_clip(pygame.Rect(BCX - 19, BCY - 14, 38, 28))
    pygame.draw.line(surf, _BLACK, (BCX + 2, BCY - 14), (BCX - 10, BCY + 14), 4)
    pygame.draw.line(surf, _RED,   (BCX + 7, BCY - 14), (BCX - 5, BCY + 14), 4)
    pygame.draw.line(surf, _GOLD,  (BCX + 12, BCY - 14), (BCX + 0, BCY + 14), 4)
    surf.set_clip(clip_prev)

    # Black V-neck collar — two lines meeting just below the head, so the sashed
    # jersey reads as a collared shirt right under the red head.
    pygame.draw.line(surf, _BLACK, (BCX - 6, BCY - 12), (BCX + 2, BCY - 8), 2)
    pygame.draw.line(surf, _BLACK, (BCX + 8, BCY - 12), (BCX + 2, BCY - 8), 2)

    # Eagle crest — a black shield pentagon on the chest with a 1px-inset white
    # fill so the dark mark reads as the DFB eagle badge, not a black blot. This
    # pins the kit to Germany specifically.
    shield = [(BCX - 12, BCY - 9), (BCX - 4, BCY - 9), (BCX - 4, BCY - 3),
              (BCX - 8, BCY - 1), (BCX - 12, BCY - 3)]
    inner = [(BCX - 11, BCY - 8), (BCX - 5, BCY - 8), (BCX - 5, BCY - 3),
             (BCX - 8, BCY - 2), (BCX - 11, BCY - 3)]
    pygame.draw.polygon(surf, _BLACK, shield)
    pygame.draw.polygon(surf, _JRS_W, inner)

    # Body oval dark outline — a 1px cool ring so the white torso stays legible
    # against a bright sky instead of dissolving into the background.
    pygame.draw.ellipse(surf, (185, 185, 195), (BCX - 19, BCY - 14, 38, 28), 1)

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
        pygame.draw.rect(surf, _CLEAT, (cx, BCY + 14, 9, 5), border_radius=1)


build = _make_skin(_paint, base_fn=_base)
