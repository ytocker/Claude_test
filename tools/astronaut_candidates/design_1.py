"""ASTRONAUT redesign — design_1 MOONWALKER (exploration only).

The iconic NASA white EVA spacewalker: a fat marshmallow-white blob bird whose
silhouette is broken from three directions — a boxy PLSS backpack jutting up
past the crown AND out past the back, a round bubble helmet with the postcard
GOLD visor down, and chunky white gloves/boots. The whole bird is re-plumaged
to suit-white through the palette system (like P_NINJA / _VK_PAL) so the body
reads as a pressurised suit, not bare scarlet, with the gold face + brick
backpack carrying the 40px read on day and night.

Scratch builder — NOT registered in store_skins.BUILDERS. Production art is
untouched until a winner is picked.
"""
import math
import pygame

from game import store_skins, parrot
from game.store_skins import HX, HY, CROWN_Y, COMPOSITE_W, COMPOSITE_H, PARROT_DY, _poly
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── palette ──────────────────────────────────────────────────────────────────
_SUIT       = (242, 244, 248)      # #F2F4F8 suit white
_SUIT_SH    = (199, 205, 216)      # #C7CDD8 suit shadow / seam
_SUIT_SH_D  = (168, 175, 190)      # deeper crease so the white holds shape
_GOLD       = (232, 161, 44)       # #E8A12C gold visor
_GOLD_D     = (176, 116, 24)
_GOLD_H     = (255, 224, 150)
_BLUE       = (44, 107, 214)       # #2C6BD6 blue stripes / button
_DARK       = (58, 63, 74)         # #3A3F4A backpack / helmet-rim dark accent
_DARK_H     = (96, 102, 116)
_RED        = (214, 64, 58)
_GREEN      = (78, 196, 110)
_WHITE      = (255, 255, 255)

# Full white-EVA re-plumage. Every slot is a suit-white value so the bird is a
# bright puffy blob; the deepest seam-shadow owns line work, and lenses are
# dropped — the helmet dome owns the face. The beak is suit-toned so no warm
# macaw orange survives to fight the gold visor.
_AST_PAL = _pal(
    tail=[(199, 205, 216), (212, 217, 226), (224, 228, 236), (236, 239, 244)],
    tail_line=_SUIT_SH_D,
    body_shadow=(190, 196, 208),
    body_main=_SUIT,
    body_chest=(252, 253, 255),
    body_belly=(232, 236, 242),
    sheen=(255, 255, 255, 90),
    wing_main=(226, 230, 238),
    wing_dark=_SUIT_SH,
    wing_tip=(248, 250, 253),
    wing_secondary=None,
    wing_highlight=_WHITE,
    head_shadow=(190, 196, 208),
    head_main=_SUIT,
    head_cheek=(250, 251, 254),
    head_crown=(236, 239, 244),
    lens_frame=(210, 215, 224),
    lens_body=(190, 196, 208),
    lens_tint=None,
    lens_glint=None,
    beak_main=(220, 225, 233),
    beak_dark=_SUIT_SH,
    beak_gloss=(250, 251, 254),
    foot=(208, 213, 222),
)


def _white_base(angle_deg):
    # White suited bird, no aviators — the bubble helmet owns the head.
    return _build_parrot_with_palette(angle_deg, _AST_PAL, draw_lenses=False)


def _backpack(surf):
    # Chunky PLSS life-support backpack — the single hardest-edged tell. A
    # rounded white brick rising well ABOVE the crown and bulging OUT past the
    # back into open sky, drawn first so the body/helmet sit in front of it.
    bx, by, bw, bh = HX - 30, CROWN_Y - 6, 22, 46
    pygame.draw.rect(surf, _DARK, (bx - 2, by - 2, bw + 4, bh + 4), border_radius=7)
    pygame.draw.rect(surf, _SUIT_SH, (bx, by, bw, bh), border_radius=6)
    pygame.draw.rect(surf, _SUIT, (bx + 2, by + 1, bw - 4, bh - 4), border_radius=5)
    # Vertical seam splitting the pack into two life-support cans + a top vent.
    pygame.draw.line(surf, _SUIT_SH, (bx + bw // 2, by + 4), (bx + bw // 2, by + bh - 5), 2)
    pygame.draw.line(surf, _SUIT_SH, (bx + 3, by + 12), (bx + bw - 3, by + 12), 2)
    pygame.draw.rect(surf, _DARK, (bx + 4, by + 3, bw - 8, 4), border_radius=2)
    pygame.draw.line(surf, _DARK_H, (bx + 5, by + 4), (bx + bw - 6, by + 4), 1)
    # Antenna nub on top, breaking the crown line on the back corner.
    pygame.draw.line(surf, _DARK, (bx + bw - 6, by), (bx + bw - 3, by - 8), 2)
    pygame.draw.circle(surf, _RED, (bx + bw - 3, by - 8), 2)
    pygame.draw.circle(surf, (255, 190, 185), (bx + bw - 4, by - 9), 1)


def _paint(surf, wing_angle_deg):
    # ── back element drawn first so the body overlaps its front edge ──────────
    _backpack(surf)

    # Oxygen hose looping from the backpack's lower flank around to the chest
    # panel — a curved dark line with a lighter core so it reads as tubing.
    hose = [(HX - 12, HY + 18), (HX - 16, HY + 12), (HX - 11, HY + 6),
            (HX - 2, HY + 9), (HX + 2, HY + 13)]
    pygame.draw.lines(surf, _DARK, False, hose, 4)
    pygame.draw.lines(surf, _DARK_H, False, hose, 2)

    # ── chest: DCM control panel, centred on the torso ───────────────────────
    px, py, pw, ph = HX - 10, HY + 9, 17, 11
    pygame.draw.rect(surf, _DARK, (px - 1, py - 1, pw + 2, ph + 2), border_radius=4)
    pygame.draw.rect(surf, (224, 228, 236), (px, py, pw, ph), border_radius=3)
    # Three status button dots + a thin gauge line.
    pygame.draw.circle(surf, _RED, (px + 4, py + 4), 2)
    pygame.draw.circle(surf, _GREEN, (px + 9, py + 4), 2)
    pygame.draw.circle(surf, _BLUE, (px + 14, py + 4), 2)
    pygame.draw.line(surf, _DARK_H, (px + 3, py + 8), (px + pw - 3, py + 8), 1)
    pygame.draw.line(surf, _GREEN, (px + 3, py + 8), (px + 9, py + 8), 1)

    # ── body: horizontal joint/segment seams so the torso reads as fabric ─────
    bcx, bcy = 32, 32 + PARROT_DY
    pygame.draw.line(surf, _SUIT_SH, (bcx - 13, bcy + 8), (bcx + 13, bcy + 8), 2)
    pygame.draw.line(surf, _SUIT_SH, (bcx - 12, bcy + 12), (bcx + 12, bcy + 12), 2)

    # ── limbs: blue arm stripe at the wing root + thick white glove at tip ────
    pygame.draw.line(surf, _BLUE, (40, 47), (47, 44), 3)
    pygame.draw.line(surf, (130, 170, 240), (40, 46), (47, 43), 1)
    # Thick rounded glove cuff + mitt at the wingtip.
    pygame.draw.circle(surf, _SUIT_SH, (49, 43), 5)
    pygame.draw.circle(surf, _SUIT, (49, 42), 4)
    pygame.draw.circle(surf, _DARK, (45, 44), 1)   # cuff seam dot

    # Chunky white moon boots over the feet.
    for fx in (26, 35):
        pygame.draw.ellipse(surf, _SUIT_SH, (fx - 5, 63, 11, 7))
        pygame.draw.ellipse(surf, _SUIT, (fx - 4, 62, 9, 5))
        pygame.draw.line(surf, _DARK, (fx - 4, 67), (fx + 4, 67), 2)   # sole

    # ── head: round bubble helmet with the GOLD visor down ───────────────────
    cx, cy = HX + 1, HY - 1
    r = 15
    # White EVA neck-rim ring behind the dome ties helmet to the suit collar.
    pygame.draw.ellipse(surf, _DARK, (cx - 13, cy + 8, 28, 11))
    pygame.draw.ellipse(surf, _SUIT, (cx - 12, cy + 8, 26, 8))
    pygame.draw.line(surf, _SUIT_SH, (cx - 10, cy + 13), (cx + 11, cy + 13), 1)

    # Clear dome — a hard bright sphere (opaque so it never reads out of focus).
    pygame.draw.circle(surf, _DARK, (cx, cy), r + 1)
    pygame.draw.circle(surf, (214, 224, 234), (cx, cy), r)
    pygame.draw.circle(surf, (236, 242, 248), (cx, cy - 1), r - 2)

    # GOLD reflective visor filling the lower-front of the dome — one clean
    # curved shape clipped to the sphere so it stays a crescent, not a blob.
    visor = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.ellipse(visor, _GOLD_D, (3, r - 3, r * 2 - 2, r + 2))
    pygame.draw.ellipse(visor, _GOLD, (4, r - 2, r * 2 - 4, r))
    clip = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(clip, (255, 255, 255, 255), (r + 2, r + 2), r - 2)
    visor.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(visor, (cx - r - 2, cy - r - 2))
    # Single diagonal white sweep highlight across the gold.
    pygame.draw.line(surf, _GOLD_H, (cx - 9, cy + 7), (cx + 2, cy - 1), 2)
    pygame.draw.line(surf, _WHITE, (cx - 7, cy + 6), (cx - 2, cy + 2), 1)
    # Hard dark visor brow so the gold doesn't bleed into the clear dome.
    pygame.draw.line(surf, _GOLD_D, (cx - 12, cy + 1), (cx + 11, cy - 1), 2)

    # Thin white helmet rim ring + a bright specular hot-spot on the dome.
    pygame.draw.circle(surf, _WHITE, (cx, cy), r, 2)
    pygame.draw.circle(surf, _WHITE, (cx - 7, cy - 8), 3)
    pygame.draw.circle(surf, _WHITE, (cx - 5, cy - 10), 1)


build = store_skins._make_skin(_paint, base_fn=_white_base)
