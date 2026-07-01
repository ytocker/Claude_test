"""Soccer v11 Design 5 — THE FAN KIT (hooped jersey, body-recolor approach).

The classic horizontally-hooped kit — River Plate, Southampton, Galatasaray —
is one of the most instantly-legible looks in football, so the jersey IS the
body: the macaw's torso oval is re-plumaged clean white through the palette
system (like the ninja skin recolors the whole bird), while the head stays
macaw-red and the wings stay macaw-blue.

On that white torso the _paint pass lays three bold red hoops. They are drawn
as full-width bars but CLIPPED to the body oval, so each hoop wraps the rounded
silhouette instead of spilling into the sky — the read that makes hoops look
like fabric and not a flag. A red "11" sits on the middle white band, deep-red
shorts and red-hooped white socks carry the colour down the legs, and a
white+black soccer ball at the feet names the sport outright at 40px.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (
    BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
)

# The body oval is re-plumaged WHITE so the jersey IS the body colour. Head
# stays macaw-red, wings stay macaw-blue — the red hoops are painted on top in
# _paint so only the torso reads as the kit and the bird keeps its identity.
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

_RED   = (200, 25, 35)     # hoop red
_RED_D = (140, 10, 20)     # hoop top-shadow + shorts rim
_WHITE = (240, 240, 245)   # jersey white, reused on collar/socks/notch
_DKRED = (160, 15, 25)     # deep-red shorts, matched to the hoops


def _base(angle_deg):
    return _build_parrot_with_palette(angle_deg, _PAL)


def _paint(surf, _a):
    # All geometry here is in COMPOSITE space (the 64×100 canvas). The body is
    # already white from _base; the trim below turns the recolor into a hooped
    # fan kit.

    # Body oval outline FIRST — a 1px cool ring so the white torso holds its
    # shape against a bright sky instead of dissolving into it.
    pygame.draw.ellipse(surf, (185, 188, 205), (BCX - 19, BCY - 14, 38, 28), 1)

    # Three bold red hoops CLIPPED to the body oval — drawn full-width but
    # masked to the torso rect so each band wraps the silhouette and reads as
    # fabric rather than a stripe painted over the sky.
    old_clip = surf.get_clip()
    surf.set_clip(pygame.Rect(BCX - 19, BCY - 14, 38, 28))
    for hy in (BCY - 10, BCY - 3, BCY + 4):
        pygame.draw.rect(surf, _RED, (BCX - 19, hy, 38, 4))
        pygame.draw.rect(surf, _RED_D, (BCX - 19, hy, 38, 1))   # top shadow of each hoop
    surf.set_clip(old_clip)

    # White V-collar — separates the white jersey from the red head. A dark
    # outline underneath keeps the notch crisp where white meets red.
    pygame.draw.line(surf, (60, 60, 80), (BCX - 6, BCY - 12), (BCX + 2, BCY - 8), 2)
    pygame.draw.line(surf, _WHITE, (BCX - 5, BCY - 12), (BCX + 2, BCY - 8), 2)
    pygame.draw.line(surf, _WHITE, (BCX + 7, BCY - 12), (BCX + 2, BCY - 8), 2)

    # Squad number "11" in red on the middle white band — two vertical bars.
    pygame.draw.line(surf, _RED, (BCX + 1, BCY - 1), (BCX + 1, BCY + 3), 2)
    pygame.draw.line(surf, _RED, (BCX + 4, BCY - 1), (BCX + 4, BCY + 3), 2)

    # Jersey hem — a 1px light ellipse so the shirt bottom separates from the
    # deep-red shorts below instead of fusing into one colour blob.
    pygame.draw.ellipse(surf, (200, 202, 218), (BCX - 9, BCY + 5, 20, 2), 1)

    # Deep-red shorts (matched to the hoops), with a darker rim so the leg-line
    # stays crisp against the white torso.
    pygame.draw.ellipse(surf, _DKRED, (BCX - 9, BCY + 6, 20, 9))
    pygame.draw.ellipse(surf, _RED_D, (BCX - 9, BCY + 6, 20, 9), 1)
    # Crotch notch so the two leg tubes read as separate legs, not a skirt.
    _poly(surf, _WHITE,
          [(BCX - 1, BCY + 12), (BCX + 3, BCY + 12), (BCX + 1, BCY + 15)])

    # Socks — white shanks with a red turn-over hoop at the top, one per leg,
    # echoing the jersey hoops down the legs.
    for sx in (27, 35):
        pygame.draw.line(surf, _WHITE, (sx, BCY + 10), (sx, BCY + 17), 4)
        pygame.draw.line(surf, _RED, (sx, BCY + 11), (sx, BCY + 13), 3)

    # Cleats — near-black boots below the socks with a white sole stripe so the
    # studs read against dark ground at 40px.
    for cx in (23, 31):
        pygame.draw.rect(surf, (28, 28, 36), (cx, BCY + 14, 9, 5), border_radius=2)
        pygame.draw.line(surf, _WHITE, (cx, BCY + 18), (cx + 8, BCY + 18), 1)

    # Soccer ball — drawn LAST at the feet so nothing overdraws it: a white
    # sphere with a black rim and three black pentagon patches, the prop that
    # names the sport outright.
    bx, by = BCX - 8, BCY + 24
    pygame.draw.circle(surf, (235, 235, 235), (bx, by), 6)
    pygame.draw.circle(surf, (20, 20, 20), (bx, by), 6, 1)
    for px, py in [(bx - 2, by - 3), (bx + 3, by - 1), (bx - 1, by + 3)]:
        pygame.draw.circle(surf, (20, 20, 20), (px, py), 2)


build = _make_skin(_paint, base_fn=_base)
