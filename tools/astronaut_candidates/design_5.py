"""DESIGN 5 — STARLINER: the sleek modern SpaceX-IVA pilot. The premium
near-future astronaut — a crisp two-tone WHITE bird in a glossy suit with a
small ANGULAR black-visor helmet (visor DOWN, hard hexagonal faceplate) and a
SLIM low-profile black flight-pack rather than a fat PLSS. The whole read is
black-on-white: sharp, minimal, glossy.

Scratch exploration only — wrapped by ``store_skins._make_skin`` and rendered
via ``tools/ninja_render.py``; NOT registered in ``store_skins.BUILDERS`` so
the live ``skin_astronaut`` is untouched.

Reads at 40px in both day and night because the suit is recoloured to near-
white through the palette system (so the whole bird is a bright blob the dark
sky never swallows) and every hero object is HARD BLACK on that white: the
angular faceplate owns the head as one dark hexagon, the slim flight-pack +
gray umbilical break the back outline, and black shoulder/side panels + boots
+ wingtip gloves carry the two-tone all the way down the body. One thin CYAN
status line on the chest module is the single colour accent — the modern HUD
tell that keeps it from reading as a penguin.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly
from game.parrot import _aaellipse
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── STARLINER palette ────────────────────────────────────────────────────────
_SUIT_W    = (244, 246, 250)       # #F4F6FA glossy suit white
_SUIT_SH   = (200, 205, 214)       # #C8CDD6 suit shadow
_BLACK     = (21, 23, 28)          # #15171C visor / accent panels
_GRAY      = (90, 97, 112)         # #5A6170 umbilical / mid shadow
_CYAN      = (43, 198, 224)        # #2BC6E0 cyan status accent
_WHITE_HI  = (255, 255, 255)


# Full near-WHITE suit recolour. Every plumage slot becomes glossy white with a
# cool shadow; tail/wing line work uses the suit shadow so the dark sky never
# eats the silhouette, and lenses are dropped by the base call so the angular
# faceplate owns the face. Beak goes dark so no warm gold survives the two-tone.
P_STARLINER = _pal(
    tail=[(214, 219, 228), (224, 228, 236), (234, 237, 243), (244, 246, 250)],
    tail_line=_SUIT_SH,
    body_shadow=(196, 201, 211),
    body_main=_SUIT_W,
    body_chest=(255, 255, 255),
    body_belly=(232, 236, 242),
    sheen=(255, 255, 255, 150),
    wing_main=(228, 232, 239),
    wing_dark=_SUIT_SH,
    wing_tip=(248, 250, 253),
    wing_secondary=None,
    wing_highlight=_WHITE_HI,
    head_shadow=(200, 205, 214),
    head_main=_SUIT_W,
    head_cheek=(248, 250, 253),
    head_crown=(255, 255, 255),
    lens_frame=(200, 205, 214),
    lens_body=_BLACK,
    lens_tint=None,
    lens_glint=None,
    beak_main=(70, 76, 90),
    beak_dark=_BLACK,
    beak_gloss=(150, 156, 170),
    foot=_BLACK,
)


def _white_base(angle_deg):
    # Glossy-white suited bird, no aviators — the angular faceplate owns the head.
    return _build_parrot_with_palette(angle_deg, P_STARLINER, draw_lenses=False)


def _paint(surf, wing_angle_deg):
    # Body centre in composite space (parrot body centre (32,32) + PARROT_DY).
    BCX, BCY = 32, 52

    # ── BACK: slim black flight-pack + gray umbilical (drawn first so the body
    #    overlaps its inner edge → it reads as worn on the back, low-profile, not
    #    a fat backpack). A narrow vertical slab rising just past the crown and
    #    poking past the back-shoulder, with a single thin gloss seam.
    pkx, pky = BCX - 16, BCY - 6        # back-shoulder anchor, left/up of body
    pygame.draw.rect(surf, _GRAY, (pkx - 5, pky - 17, 11, 30), border_radius=4)
    pygame.draw.rect(surf, _BLACK, (pkx - 4, pky - 16, 9, 28), border_radius=3)
    pygame.draw.line(surf, _GRAY, (pkx - 1, pky - 13), (pkx - 1, pky + 8), 1)
    # Two slim cyan status pips on the pack top so the dark slab self-separates
    # from the night sky and ties to the chest accent.
    pygame.draw.circle(surf, _CYAN, (pkx + 2, pky - 13), 1)
    pygame.draw.circle(surf, _WHITE_HI, (pkx - 2, pky - 13), 1)
    # Gray umbilical hose curving from the pack base around to the hip.
    pygame.draw.lines(surf, _GRAY, False,
                      [(pkx + 3, pky + 11), (pkx + 9, pky + 16),
                       (BCX - 2, BCY + 9), (BCX + 8, BCY + 7)], 3)
    pygame.draw.lines(surf, _BLACK, False,
                      [(pkx + 3, pky + 11), (pkx + 9, pky + 16),
                       (BCX - 2, BCY + 9), (BCX + 8, BCY + 7)], 1)

    # ── BODY two-tone: black across the collarbone/shoulders, then a black
    #    stripe down each visible side. Clamp to the body silhouette by sizing
    #    each panel to the white blob so the suit reads glossy, not painted-over.
    # Collarbone/shoulder yoke — a black band arcing over the upper chest.
    yoke = [(BCX - 14, BCY - 7), (BCX - 4, BCY - 12), (BCX + 9, BCY - 11),
            (BCX + 15, BCY - 5), (BCX + 9, BCY - 6), (BCX - 2, BCY - 8),
            (BCX - 11, BCY - 4)]
    _poly(surf, _BLACK, yoke)
    pygame.draw.line(surf, _GRAY, (BCX - 11, BCY - 6), (BCX + 11, BCY - 8), 1)
    # Side accent stripe down the near (right) flank.
    side = [(BCX + 13, BCY - 4), (BCX + 16, BCY - 1),
            (BCX + 13, BCY + 9), (BCX + 9, BCY + 7)]
    _poly(surf, _BLACK, side)
    pygame.draw.line(surf, _SUIT_SH, (BCX + 12, BCY - 2), (BCX + 11, BCY + 6), 1)
    # Far-side stripe hint along the belly/tail seam so the two-tone wraps.
    pygame.draw.line(surf, _BLACK, (BCX - 12, BCY + 6), (BCX - 4, BCY + 10), 3)

    # ── CHEST: minimalist rectangular black module with one thin CYAN status
    #    line + dot — the single modern-HUD colour accent on the whole skin.
    mx, my = BCX + 1, BCY + 1
    pygame.draw.rect(surf, _BLACK, (mx - 6, my - 3, 13, 9), border_radius=2)
    pygame.draw.rect(surf, _GRAY, (mx - 6, my - 3, 13, 9), 1, border_radius=2)
    pygame.draw.line(surf, _CYAN, (mx - 4, my + 1), (mx + 3, my + 1), 1)
    pygame.draw.circle(surf, _CYAN, (mx + 5, my - 1), 1)
    pygame.draw.circle(surf, _WHITE_HI, (mx - 4, my + 3), 1)

    # ── LIMBS: black glove at the near wingtip, black boots, and a thin black
    #    seam up the wing root → the two-tone reaches every extremity.
    pygame.draw.line(surf, _BLACK, (BCX + 4, BCY - 6), (BCX + 14, BCY - 9), 2)
    pygame.draw.circle(surf, _BLACK, (BCX + 16, BCY - 4), 3)        # wingtip glove
    pygame.draw.circle(surf, _SUIT_SH, (BCX + 15, BCY - 5), 1)
    for fx in (BCX - 6, BCX):                                       # boots
        pygame.draw.line(surf, _BLACK, (fx, BCY + 13), (fx - 1, BCY + 17), 3)
        pygame.draw.circle(surf, _BLACK, (fx - 1, BCY + 17), 2)

    # ── HEAD: oval white helmet shell, then a hard hexagonal BLACK faceplate
    #    (visor DOWN) with one sharp diagonal white glint, and a small black
    #    chin/comms wedge. The flatter oval (not a bubble) is the modern read.
    hcx, hcy = HX + 1, HY - 1
    # Thin white helmet shell — a slightly squashed oval hugging the head, with a
    # crisp gray rim so the shell separates from the white body (the outline pass
    # only edges the outer silhouette, so this internal rim carries the read).
    pygame.draw.ellipse(surf, _GRAY,   (hcx - 14, hcy - 14, 29, 27))
    pygame.draw.ellipse(surf, _SUIT_W, (hcx - 13, hcy - 13, 27, 25))
    pygame.draw.ellipse(surf, _GRAY,   (hcx - 13, hcy - 13, 27, 25), 1)
    pygame.draw.ellipse(surf, _WHITE_HI, (hcx - 9, hcy - 12, 11, 4))
    # Hard angular faceplate — a hexagon filling the lower-front of the shell.
    fx, fy = hcx + 1, hcy + 1
    face = [(fx - 11, fy - 4), (fx - 6, fy - 8), (fx + 9, fy - 7),
            (fx + 12, fy - 1), (fx + 8, fy + 7), (fx - 7, fy + 7),
            (fx - 11, fy + 2)]
    _poly(surf, (8, 9, 12), [(x, y + 1) for x, y in face])   # hard dark edge
    _poly(surf, _BLACK, face)
    # Slim gray bezel along the faceplate top so the hexagon edge stays crisp.
    pygame.draw.line(surf, _GRAY, (fx - 6, fy - 7), (fx + 8, fy - 6), 1)
    # One sharp diagonal white glint sweeping across the dark glass.
    pygame.draw.line(surf, _WHITE_HI, (fx - 6, fy + 4), (fx + 4, fy - 5), 2)
    pygame.draw.line(surf, _CYAN, (fx + 1, fy + 2), (fx + 5, fy - 2), 1)
    # Small black chin/comms wedge under the faceplate.
    _poly(surf, _BLACK, [(fx - 4, fy + 7), (fx + 6, fy + 7),
                         (fx + 3, fy + 12), (fx - 2, fy + 12)])
    pygame.draw.line(surf, _CYAN, (fx, fy + 9), (fx + 2, fy + 9), 1)


build = store_skins._make_skin(_paint, base_fn=_white_base)
