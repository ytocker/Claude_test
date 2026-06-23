"""ASTRONAUT redesign — design_1 MOONWALKER (exploration only).

The iconic NASA white EVA spacewalker: a fat marshmallow-white blob bird whose
silhouette is broken from three directions — a boxy PLSS backpack jutting up
past the crown AND out past the back, a round bubble helmet with the postcard
GOLD visor down, and a chunky hard-edged moon-boot mass. The whole bird is
re-plumaged to suit-white through the palette system so the body reads as a
pressurised suit, not bare scarlet, with the gold face + brick backpack
carrying the 40px read on day and night.

R2 fix-list (each tied to the 40px read):
  * The white suit wash-out on pale day sky is solved by underlaying ONE
    continuous dark (#3A3F4A) keyline around the WHOLE painted silhouette —
    same contour weight the helmet/backpack already carry — so the lower-left
    wing/tail/boot edge stops dissolving into the sky.
  * Chest clutter (DCM micro-panel, oxygen hose, belly seams) is dropped so
    the visor owns the central band uncluttered; only ONE chunky tri-dot
    cluster survives, and only because it still reads at thumbnail size.
  * Moon boots are one flatter hard-edged mass with a dark sole keyline as
    the literal bottom of the silhouette.
  * Blue is a single deliberate accent band across the backpack top — the one
    place it reads at 40px — instead of a lost wing-root arm stripe.

Scratch builder — NOT registered in store_skins.BUILDERS. Production art is
untouched until a winner is picked.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, COMPOSITE_W, COMPOSITE_H, PARROT_DY
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── palette ──────────────────────────────────────────────────────────────────
_SUIT       = (242, 244, 248)      # #F2F4F8 suit white
_SUIT_SH    = (199, 205, 216)      # #C7CDD8 suit shadow / seam
_SUIT_SH_D  = (168, 175, 190)      # deeper crease so the white holds shape
_GOLD       = (232, 161, 44)       # #E8A12C gold visor
_GOLD_D     = (176, 116, 24)
_GOLD_H     = (255, 224, 150)
_BLUE       = (44, 107, 214)       # #2C6BD6 the one deliberate blue accent
_BLUE_H     = (130, 170, 240)
_DARK       = (58, 63, 74)         # #3A3F4A the continuous suit keyline value
_RED        = (214, 64, 58)
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
    # The dark border is the same #3A3F4A keyline weight the whole suit gets,
    # so the brick stays a distinct mass once the body keyline lands beside it.
    bx, by, bw, bh = HX - 31, CROWN_Y - 6, 23, 47
    pygame.draw.rect(surf, _DARK, (bx - 2, by - 2, bw + 4, bh + 4), border_radius=7)
    pygame.draw.rect(surf, _SUIT_SH, (bx, by, bw, bh), border_radius=6)
    pygame.draw.rect(surf, _SUIT, (bx + 2, by + 1, bw - 4, bh - 4), border_radius=5)
    # The one deliberate BLUE accent: a chunky band across the pack top, the
    # one spot blue survives at 40px (central, against white, full-width).
    pygame.draw.rect(surf, _BLUE, (bx + 2, by + 3, bw - 4, 6), border_radius=2)
    pygame.draw.line(surf, _BLUE_H, (bx + 3, by + 4), (bx + bw - 4, by + 4), 1)
    # Vertical seam splitting the pack into two life-support cans.
    pygame.draw.line(surf, _SUIT_SH_D, (bx + bw // 2, by + 12), (bx + bw // 2, by + bh - 5), 2)
    # Antenna nub on top, breaking the crown line on the back corner.
    pygame.draw.line(surf, _DARK, (bx + bw - 6, by), (bx + bw - 3, by - 8), 2)
    pygame.draw.circle(surf, _RED, (bx + bw - 3, by - 8), 2)
    pygame.draw.circle(surf, (255, 190, 185), (bx + bw - 4, by - 9), 1)


def _suit_keyline(surf):
    """Underlay ONE continuous #3A3F4A keyline around the whole painted bird.

    White-on-pale-sky was dissolving at the lower-left wing/tail/boot edge —
    the helmet and backpack carried a visible dark contour but the soft suit
    did not. Deriving a 1px-dilated dark silhouette of everything drawn so far
    and stamping it BEHIND that art gives the entire body the same contour
    weight, so the read survives the 40px day wash-out. (The engine's own
    1px outline is near-black and too thin to hold the white at thumbnail.)
    """
    mask = pygame.mask.from_surface(surf, threshold=12)
    line = mask.to_surface(setcolor=_DARK, unsetcolor=(0, 0, 0, 0))
    key = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1),
                   (-2, 0), (2, 0), (0, 2)):
        key.blit(line, (dx, dy))
    key.blit(surf, (0, 0))
    surf.blit(key, (0, 0))


def _paint(surf, wing_angle_deg):
    # ── back element drawn first so the body overlaps its front edge ──────────
    _backpack(surf)

    # ── chunky moon-boot mass: ONE flatter hard-edged block under the feet,
    #     a dark sole keyline forming the literal bottom of the silhouette ─────
    bootx, booty, bootw, booth = 22, 62, 21, 8
    pygame.draw.rect(surf, _SUIT_SH, (bootx, booty, bootw, booth), border_radius=3)
    pygame.draw.rect(surf, _SUIT, (bootx + 1, booty, bootw - 2, booth - 3), border_radius=3)
    pygame.draw.line(surf, _SUIT_SH_D, (bootx + bootw // 2, booty + 1),
                     (bootx + bootw // 2, booty + booth - 3), 2)   # split the two boots
    pygame.draw.rect(surf, _DARK, (bootx, booty + booth - 3, bootw, 3), border_radius=2)  # hard sole

    # Chest DCM panel was CUT: at 40px it vanished behind the visor as a smudge,
    # so the gold visor owns the central band uncluttered. The status colours now
    # live only on the antenna nub (red) + backpack band (blue) where they read.

    # ── wingtip glove: thick rounded white mitt (kept — the silhouette tell) ──
    pygame.draw.circle(surf, _SUIT_SH, (49, 43), 5)
    pygame.draw.circle(surf, _SUIT, (49, 42), 4)
    pygame.draw.circle(surf, _DARK, (45, 44), 1)   # cuff seam dot

    # ── head: round bubble helmet with the GOLD visor down ───────────────────
    cx, cyh = HX + 1, HY - 1
    r = 15
    # White EVA neck-rim ring behind the dome ties helmet to the suit collar.
    pygame.draw.ellipse(surf, _DARK, (cx - 13, cyh + 8, 28, 11))
    pygame.draw.ellipse(surf, _SUIT, (cx - 12, cyh + 8, 26, 8))

    # Clear dome — a hard bright sphere (opaque so it never reads out of focus).
    pygame.draw.circle(surf, _DARK, (cx, cyh), r + 1)
    pygame.draw.circle(surf, (214, 224, 234), (cx, cyh), r)
    pygame.draw.circle(surf, (236, 242, 248), (cx, cyh - 1), r - 2)

    # GOLD reflective visor filling the lower-front of the dome — one clean
    # curved shape clipped to the sphere so it stays a crescent, not a blob.
    visor = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.ellipse(visor, _GOLD_D, (3, r - 3, r * 2 - 2, r + 2))
    pygame.draw.ellipse(visor, _GOLD, (4, r - 2, r * 2 - 4, r))
    clip = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(clip, (255, 255, 255, 255), (r + 2, r + 2), r - 2)
    visor.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(visor, (cx - r - 2, cyh - r - 2))
    # Single diagonal white sweep highlight across the gold (best element).
    pygame.draw.line(surf, _GOLD_H, (cx - 9, cyh + 7), (cx + 2, cyh - 1), 2)
    pygame.draw.line(surf, _WHITE, (cx - 7, cyh + 6), (cx - 2, cyh + 2), 1)
    # Hard dark visor brow so the gold doesn't bleed into the clear dome.
    pygame.draw.line(surf, _GOLD_D, (cx - 12, cyh + 1), (cx + 11, cyh - 1), 2)

    # Thin white helmet rim ring + a bright specular hot-spot on the dome.
    pygame.draw.circle(surf, _WHITE, (cx, cyh), r, 2)
    pygame.draw.circle(surf, _WHITE, (cx - 7, cyh - 8), 3)
    pygame.draw.circle(surf, _WHITE, (cx - 5, cyh - 10), 1)

    # ── final pass: ONE continuous dark keyline behind everything ─────────────
    _suit_keyline(surf)


build = store_skins._make_skin(_paint, base_fn=_white_base)
