"""Soccer v7 Design 1 — THE STRIKER (body-recolor approach).

The previous take anchored a flat jersey polygon to the head, so it only
covered the head-side of the body and missed the belly entirely. This
version makes the JERSEY the body itself: the macaw's body oval is
re-plumaged white through the palette system (exactly like the ninja skin
recolors the whole bird), while the head stays macaw-red and the wings stay
macaw-blue. On top of that white torso the _paint pass adds the kit trim
that reads as football — a navy V-collar, a diagonal royal-blue sash, the
squad number "9", royal-blue shorts, hooped socks, and cleats.

At 40px the read is a white-bodied bird with blue shorts and a red-hooped
sock line — a striker, not a recolor. Head/wings keep the macaw identity.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (
    BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
)

# ── kit trim colours (drawn in _paint, over the white body) ──────────────────
_ROYAL    = ( 26,  62, 160)   # #1A3EA0 royal-blue shorts + sash + collar
_ROYAL_D  = ( 16,  40, 112)   # darker royal for the shorts outline / seams
_SASH_H   = ( 85, 136, 255)   # #5588FF bright-blue sash highlight
_NAVY     = ( 20,  40, 110)   # navy V-collar + squad-number "9"
_JRS_W    = (240, 240, 245)   # jersey white, reused to notch the shorts crotch
_SCK      = (240, 240, 245)   # #F0F0F5 white sock
_SCK_RED  = (192,  57,  43)   # #C0392B red sock hoop
_CLEAT    = ( 28,  28,  36)   # #1C1C24 near-black cleat
_CLEAT_SL = (232, 120,  32)   # #E87820 bright-orange sole stripe

# The body oval is re-plumaged WHITE so the jersey IS the body colour. Head
# stays macaw-red, wings stay macaw-blue, aviator shades stay gold-framed —
# so only the torso reads as the kit and the bird keeps its identity.
_PAL = _pal(
    tail=[(200, 30, 40), (240, 95, 40), (255, 160, 55), (255, 220, 80)],
    tail_line=(170, 25, 25),
    body_shadow=(180, 185, 205),      # jersey back-half shade (rounds torso)
    body_main=(240, 240, 245),        # jersey white field
    body_chest=(248, 248, 252),       # lit chest
    body_belly=(215, 218, 230),       # slightly cooler belly
    sheen=(255, 255, 255, 120),
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
    # already white from _base, so the trim below is what turns the recolor
    # into a striker's kit.

    # V-collar — a small navy triangle notched at the head/body junction, so
    # the white jersey reads as a collared shirt right under the red head.
    _poly(surf, _NAVY, [(HX - 3, HY + 6), (HX + 2, HY + 6), (HX, HY + 10)])

    # Diagonal royal-blue sash across the BODY (not the head) — the single
    # bold graphic stripe that carries the "team kit" read at 40px.
    pygame.draw.line(surf, _ROYAL, (BCX - 8, BCY - 8), (BCX + 6, BCY + 2), 2)
    pygame.draw.line(surf, _SASH_H, (BCX - 8, BCY - 9), (BCX + 6, BCY + 1), 1)

    # Squad number "9" on the open white chest — a small navy ring with a
    # short diagonal tail so it reads as a numeral, not a dot.
    pygame.draw.circle(surf, _NAVY, (BCX + 1, BCY - 1), 3, 2)
    pygame.draw.line(surf, _NAVY, (BCX + 3, BCY - 1), (BCX + 1, BCY + 4), 2)

    # Royal-blue shorts over the lower body — one ellipse with a darker rim so
    # the leg-line separates from the white torso above.
    pygame.draw.ellipse(surf, _ROYAL, (BCX - 10, BCY + 7, 22, 11))
    pygame.draw.ellipse(surf, _ROYAL_D, (BCX - 10, BCY + 7, 22, 11), 1)
    # Crotch notch so the two leg tubes read as separate legs, not a skirt.
    _poly(surf, _JRS_W,
          [(BCX - 1, BCY + 14), (BCX + 3, BCY + 14), (BCX + 1, BCY + 18)])

    # Socks — white shanks with a red turn-over hoop, one per leg.
    for sx in (27, 35):
        pygame.draw.line(surf, _SCK, (sx, BCY + 11), (sx, BCY + 17), 4)
        pygame.draw.line(surf, _SCK_RED, (sx, BCY + 12), (sx, BCY + 14), 4)

    # Cleats — near-black boots with a bright-orange sole stripe at the base
    # so the studs read against dark ground at 40px.
    for cx in (23, 31):
        pygame.draw.rect(surf, _CLEAT, (cx, BCY + 13, 9, 5), border_radius=1)
        pygame.draw.line(surf, _CLEAT_SL,
                         (cx, BCY + 17), (cx + 8, BCY + 17), 2)


build = _make_skin(_paint, base_fn=_base)
