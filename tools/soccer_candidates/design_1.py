"""Soccer v9 Design 1 — ARGENTINA "LA ALBICELESTE" (body-recolor approach).

The jersey IS the body: the macaw's torso oval is re-plumaged white through
the palette system (like the ninja skin recolors the whole bird), while the
head stays macaw-red and the wings stay macaw-blue. Over that white torso the
_paint pass lays the four sky-blue vertical stripes that make the kit instantly
read as Argentina — plus a sky-blue V-collar, the golden Sol de Mayo crest, deep
navy shorts, sky-hooped socks, and near-black cleats.

At 40px the read is a white-and-sky-striped bird with navy shorts — the
Albiceleste — while the head/wings/beak keep the macaw identity.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (
    BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
)

# ── kit trim colours (drawn in _paint, over the white body) ──────────────────
_SKY      = (117, 170, 219)   # #75AADB Argentina sky-blue stripes + collar + hoop
_SKY_D    = ( 92, 142, 190)   # slightly deeper sky for the collar underline
_NAVY     = ( 11,  27,  77)   # #0B1B4D deep-navy shorts
_NAVY_D   = (  6,  15,  45)   # darker navy rim for the shorts leg-line
_GOLD     = (255, 185,   0)   # Sol de Mayo gold disc + rays
_GOLD_D   = (176, 120,   0)   # dark ring so the sun reads as a disc, not a dot
_JRS_W    = (240, 240, 245)   # jersey white, reused to notch the shorts crotch
_SCK      = (245, 245, 250)   # white sock shank
_CLEAT    = ( 28,  28,  36)   # #1C1C24 near-black cleat

# The body oval is re-plumaged WHITE so the jersey IS the body colour. Head
# stays macaw-red, wings stay macaw-blue — so only the torso reads as the kit
# and the bird keeps its identity.
_PAL = _pal(
    tail=[(200, 30, 40), (240, 95, 40), (255, 160, 55), (255, 220, 80)],
    tail_line=(170, 25, 25),
    body_shadow=(185, 188, 205),      # jersey back-half shade (rounds torso)
    body_main=(240, 240, 245),        # jersey white field
    body_chest=(250, 250, 252),       # lit chest
    body_belly=(215, 218, 230),       # slightly cooler belly
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

    # Sky-blue vertical stripes — the signature Albiceleste graphic. Clipped to
    # the body oval bounding rect so the stripes stop at the torso edge instead
    # of bleeding onto the wings/tail; four evenly-spaced 5px bars across 38px.
    body_rect = pygame.Rect(BCX - 19, BCY - 14, 38, 28)
    old_clip = surf.get_clip()
    surf.set_clip(body_rect)
    for x in (BCX - 17, BCX - 9, BCX - 1, BCX + 7):
        pygame.draw.rect(surf, _SKY, (x, BCY - 14, 5, 28))
    surf.set_clip(old_clip)

    # V-neck collar in sky-blue — two lines meeting just below the head, so the
    # striped jersey reads as a collared shirt right under the red head.
    pygame.draw.line(surf, _SKY, (BCX - 6, BCY - 12), (BCX + 2, BCY - 8), 2)
    pygame.draw.line(surf, _SKY, (BCX + 8, BCY - 12), (BCX + 2, BCY - 8), 2)
    pygame.draw.line(surf, _SKY_D, (BCX - 6, BCY - 11), (BCX + 2, BCY - 7), 1)

    # Sol de Mayo crest — a gold disc with a dark ring so it reads as a sun, and
    # a handful of 1px rays radiating outward. The national sun on the chest is
    # what pins the kit to Argentina specifically.
    cxs, cys = BCX + 5, BCY - 5
    for dx, dy in ((0, -6), (0, 6), (-6, 0), (6, 0),
                   (-4, -4), (4, -4), (-4, 4), (4, 4)):
        ex = cxs + (dx * 3) // 6
        ey = cys + (dy * 3) // 6
        pygame.draw.line(surf, _GOLD, (cxs, cys),
                         (cxs + dx // 3, cys + dy // 3), 1)
    pygame.draw.circle(surf, _GOLD_D, (cxs, cys), 4)
    pygame.draw.circle(surf, _GOLD, (cxs, cys), 3)

    # Jersey hem — a 1px light ellipse so the striped shirt bottom separates from
    # the navy shorts below instead of fusing into one dark kit blob.
    pygame.draw.ellipse(surf, (220, 222, 232), (BCX - 9, BCY + 5, 20, 2), 1)

    # Deep-navy shorts, with a darker rim so the leg-line stays crisp against
    # the white-and-sky torso.
    pygame.draw.ellipse(surf, _NAVY, (BCX - 9, BCY + 7, 20, 9))
    pygame.draw.ellipse(surf, _NAVY_D, (BCX - 9, BCY + 7, 20, 9), 1)
    # Crotch notch so the two leg tubes read as separate legs, not a skirt.
    _poly(surf, _JRS_W,
          [(BCX - 1, BCY + 12), (BCX + 3, BCY + 12), (BCX + 1, BCY + 15)])

    # Socks — white shanks with a sky-blue turn-over hoop, one per leg. Shortened
    # to leave a clean gap above the cleats so the kit stack stays legible.
    for sx in (27, 35):
        pygame.draw.line(surf, _SCK, (sx, BCY + 11), (sx, BCY + 16), 4)
        pygame.draw.line(surf, _SKY, (sx, BCY + 12), (sx, BCY + 14), 3)

    # Cleats — near-black boots below the socks with a visible gap.
    for cx in (23, 31):
        pygame.draw.rect(surf, _CLEAT, (cx, BCY + 14, 9, 5), border_radius=1)


build = _make_skin(_paint, base_fn=_base)
