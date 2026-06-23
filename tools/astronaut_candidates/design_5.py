"""DESIGN 5 — STARLINER: the sleek modern SpaceX-IVA pilot. The premium
near-future astronaut — a crisp two-tone WHITE bird in a glossy suit with a
small ANGULAR black-visor helmet (visor DOWN, hard hexagonal faceplate) and a
low-profile GRAY flight-pack tucked onto the shoulder rather than a fat PLSS.
The whole read is black-on-white: sharp, minimal, glossy.

Scratch exploration only — wrapped by ``store_skins._make_skin`` and rendered
via ``tools/ninja_render.py``; NOT registered in ``store_skins.BUILDERS`` so
the live ``skin_astronaut`` is untouched.

Reads at 40px in both day and night because the suit is recoloured to near-
white through the palette system (so the whole bird is a bright blob the dark
sky never swallows) and the HELMET wins the focal fight unambiguously: the
black faceplate is the single largest+darkest mass. The flight-pack is GRAY
with only a thin black accent and sits LOW behind the shoulder, overlapped by
the body and tied in by a white strap, so it reads "pack on back" not "second
head." The dominant white diagonal glint plus the round dark head carry the
"visor" read at size; one bold black shoulder yoke is the only body panel that
survives. The single CYAN status line on the chest module is the lone colour
accent — kept away from the face so the helmet read stays pure.
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

    # ── BACK: low-profile GRAY flight-pack hugging the shoulder. Drawn first so
    #    the body silhouette overlaps its inner ~40% → it reads as worn ON the
    #    back, attached, not a second mass beside the head. It is GRAY (not black)
    #    and sits LOW (top well below the crown) so the dark faceplate stays the
    #    single largest+darkest shape and unambiguously wins the focal fight. The
    #    top is angled/canted (an asymmetric shoulder shape), never a vertical bar
    #    mirroring the round helmet, and a thin white strap ties it to the suit.
    pkx, pky = BCX - 13, BCY + 1        # back-shoulder anchor, low + tucked in
    # Canted slab: top-back corner higher than top-front so the silhouette slopes
    # down toward the body — an angled pack shoulder, not a mirrored stick.
    pack = [(pkx - 5, pky - 6), (pkx + 4, pky - 9), (pkx + 7, pky + 1),
            (pkx + 6, pky + 12), (pkx - 4, pky + 13), (pkx - 6, pky + 3)]
    _poly(surf, _GRAY, pack)
    pygame.draw.line(surf, _SUIT_SH, (pkx - 4, pky - 5), (pkx + 5, pky + 11), 1)
    # BLACK only as a thin lower accent band — keeps the pack's dark area small.
    _poly(surf, _BLACK, [(pkx - 4, pky + 8), (pkx + 6, pky + 8),
                         (pkx + 5, pky + 12), (pkx - 4, pky + 12)])
    # White shoulder strap arcing from the pack top over the shoulder into the
    # body — the explicit "attached" cue at any size.
    pygame.draw.line(surf, _WHITE_HI, (pkx + 3, pky - 8), (BCX + 1, BCY - 9), 2)
    pygame.draw.line(surf, _SUIT_SH, (pkx + 3, pky - 7), (BCX + 1, BCY - 8), 1)

    # ── BODY two-tone: ONE bold black shoulder YOKE band across the upper chest
    #    — the single body panel that survives at 40px. The white body stays clean
    #    below it (no side stripe, no belly seam) so the suit reads glossy and the
    #    eye isn't split across competing dark marks.
    yoke = [(BCX - 14, BCY - 7), (BCX - 4, BCY - 12), (BCX + 9, BCY - 11),
            (BCX + 15, BCY - 5), (BCX + 9, BCY - 5), (BCX - 2, BCY - 7),
            (BCX - 11, BCY - 3)]
    _poly(surf, _BLACK, yoke)
    pygame.draw.line(surf, _GRAY, (BCX - 11, BCY - 6), (BCX + 11, BCY - 8), 1)

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
    # One bold diagonal white glint sweeping across the dark glass — longer and
    #    brighter than the round_1 mark so it is the DOMINANT feature of the
    #    faceplate. With the round dark head it does the whole "visor" read at
    #    40px (the hexagon edges won't survive); no cyan anywhere near the face.
    pygame.draw.line(surf, _WHITE_HI, (fx - 8, fy + 5), (fx + 6, fy - 6), 3)
    # Small black chin/comms wedge under the faceplate (no cyan tell).
    _poly(surf, _BLACK, [(fx - 4, fy + 7), (fx + 6, fy + 7),
                         (fx + 3, fy + 12), (fx - 2, fy + 12)])


build = store_skins._make_skin(_paint, base_fn=_white_base)
