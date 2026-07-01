"""SOCCER — THE GOALKEEPER (DESIGN 2 of the SOCCER set).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so production
is untouched.

Concept: the jersey IS the body. Instead of stapling a flat polygon shirt over
the scarlet macaw (which only ever covered the head-side of the torso and left
the belly bare), this recolours the whole body oval through the palette system
the ninja/cockatoo skins use — HV neon keeper green from chest to belly, with a
darker green shade for roundness and a bright sheen. The head stays macaw-red and
the wings stay macaw-blue so Pip is still recognisably himself, just kitted out.

Over that recoloured torso the _paint pass lays the keeper kit — crew collar,
white badge pip, charcoal shorts, hooped neon socks, yellow cleats — and, drawn
LAST so nothing dulls them, the hero prop: two OVERSIZED padded ORANGE keeper
gloves, one on each wing. At 40px the order of value is (1) the two big bright
mitts breaking both wing outlines (the unmistakable keeper tell), (2) the neon
green torso/socks mass, (3) the yellow boots. The orange gloves and yellow boots
are warm notes that pop off the cool green on both day and night skies.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP


# Keeper kit — the body oval is recoloured to the neon-green jersey; the head is
# kept macaw-red so Pip stays recognisable under the kit.
_PAL = _pal(
    tail=[(200, 30, 40), (240, 95, 40), (255, 160, 55), (255, 220, 80)],
    tail_line=(170, 25, 25),
    body_shadow=(20, 130, 42),      # jersey drop-shade for roundness
    body_main=(57, 211, 83),        # #39D353 neon keeper green
    body_chest=(80, 230, 105),      # lit upper chest
    body_belly=(38, 178, 66),       # shaded lower belly
    sheen=(120, 255, 160, 110),     # bright jersey sheen band
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

_COLLAR   = (26, 112, 49)      # #1A7031 dark-green collar / sock hoop
_BADGE    = (240, 240, 240)    # white keeper badge pip
_SHORTS   = (42, 42, 42)       # #2A2A2A charcoal shorts
_SHORTS_D = (20, 20, 20)       # shorts outline
_SOCK     = (57, 211, 83)      # #39D353 neon socks (match jersey)
_CLEAT    = (232, 192, 32)     # #E8C020 yellow cleats
_CLEAT_D  = (150, 120, 12)     # cleat outline


def _base(angle_deg):
    return _build_parrot_with_palette(angle_deg, _PAL)


def _paint(surf, _a):
    # ── CREW COLLAR — a 1px dark-green arc just below the head/body junction so
    #    the recoloured torso reads as a shirt neckline, not bare feathers.
    pygame.draw.lines(surf, _COLLAR, False,
                      [(BCX - 5, BCY - 11), (BCX + 2, BCY - 9),
                       (BCX + 10, BCY - 11)], 1)
    # White keeper badge pip on the chest.
    pygame.draw.circle(surf, _BADGE, (BCX + 2, BCY - 3), 3)
    pygame.draw.circle(surf, _COLLAR, (BCX + 2, BCY - 3), 3, 1)

    # ── SHORTS — dark charcoal ellipse tucked under the jersey hem, 1px darker
    #    outline so it holds its edge against the green torso.
    shorts = pygame.Rect(BCX - 10, BCY + 7, 22, 11)
    pygame.draw.ellipse(surf, _SHORTS, shorts)
    pygame.draw.ellipse(surf, _SHORTS_D, shorts, 1)

    # ── SOCKS — neon-green matching the jersey, with a dark hoop at the top.
    for sx in (27, 35):
        pygame.draw.line(surf, _SOCK, (sx, BCY + 11), (sx, BCY + 17), 4)
        pygame.draw.line(surf, _COLLAR, (sx, BCY + 12), (sx, BCY + 14), 4)

    # ── CLEATS — bright yellow at the feet, 1px dark-yellow outline. The colour
    #    IS the accent, so no side stripe competes with the gloves.
    for fx in (23, 31):
        pygame.draw.rect(surf, _CLEAT, (fx, BCY + 13, 9, 5), border_radius=2)
        pygame.draw.rect(surf, _CLEAT_D, (fx, BCY + 13, 9, 5), 1, border_radius=2)

    # ── GOALKEEPER GLOVES (HERO PROP, drawn LAST so they sit in FRONT of the
    #    whole kit) — two oversized padded orange mitts, one on each wing tip.
    #    Bright orange with a dark knuckle strap + thumb tab: the biggest,
    #    brightest shapes on the sprite, the unmistakable keeper tell at 40px.
    for gx in (BCX - 23, BCX + 10):
        pygame.draw.rect(surf, (245, 110, 10), (gx, BCY - 10, 14, 12),
                         border_radius=3)
        pygame.draw.rect(surf, (120, 50, 0), (gx, BCY - 10, 14, 12),
                         border_radius=3, width=1)
        pygame.draw.line(surf, (120, 50, 0), (gx, BCY - 7), (gx + 14, BCY - 7), 3)
        pygame.draw.rect(surf, (255, 140, 40), (gx + 2, BCY - 11, 8, 5),
                         border_radius=2)


build = _make_skin(_paint, base_fn=_base)
