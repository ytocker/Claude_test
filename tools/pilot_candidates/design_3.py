"""RED BARON — biplane-ace aristocrat pilot candidate (scratch exploration).

The "flying ace" counterweight to the modern-pilot builds: the whole macaw is
re-plumaged head-to-tail into CRIMSON LEATHER through the palette system, so the
costume paints as a flight kit ON a red-jacketed body instead of accents fighting
scarlet macaw plumage. Over that sit a tall dark fur-trimmed flying helmet, a
gleaming brass monocle on the forward eye, a black iron cross on the shoulder, and
a row of brass buttons down the chest. At 40px the read is, by value: a red-leather
bird, the pale fur band + brass monocle owning the head, and the white-edged iron
cross breaking the wing. Exploration only; nothing here is registered in
store_skins.BUILDERS and no live skin is touched.
"""
import pygame

from game.store_skins import _pal, _build_parrot_with_palette, _make_skin, _poly
from game import store_skins

HX = store_skins.HX          # 47 — head centre x
HY = store_skins.HY          # 41 — head centre y
CROWN_Y = store_skins.CROWN_Y  # 31 — top of head crown

# Aristocrat flying-ace palette. Crimson leather jacket everywhere the base bird
# shows so the flight kit reads as gear over a red uniform, gold beak fits the
# aristocrat, fur/brass/iron-cross carry the only non-red notes. Pushed off native
# scarlet toward a deeper oxblood-crimson so the leather reads as jacket, not bird.
BARON_RED   = (142, 27, 27)   # #8E1B1B jacket / body
RED_DARK    = (94, 15, 15)    # #5E0F0F shadow
RED_LIGHT   = (180, 60, 50)   # #B43C32 chest highlight
LEATHER_D   = (74, 46, 26)    # #4A2E1A helmet leather
LEATHER_DD  = (48, 30, 16)    # #301E10 helmet seam / deepest fold
FUR_CREAM   = (216, 199, 168) # #D8C7A8 fur trim
FUR_SHADE   = (176, 158, 128) # fur underside so the band reads as tufts
BRASS_GOLD  = (232, 199, 102) # #E8C766 monocle ring / buttons
BRASS_D     = (160, 130, 50)  # brass shadow
CHAIN_GOLD  = (184, 147, 63)  # #B8933F dimmed chain so it stays secondary to buttons
LENS_MID    = (127, 168, 181) # #7FA8B5 muted glass so a white glint can pop off it
IRON_BLACK  = (17, 17, 17)    # #111111 iron-cross body
CROSS_WHITE = (255, 255, 255) # #FFFFFF iron-cross rim / monocle specular
RIM_RED     = (168, 48, 48)   # #A83030 night-safe silhouette rim

# Full crimson-leather re-plumage. Gold beak, leather feet; lenses dropped so the
# brass monocle owns the face without an aviator underneath it.
P_BARON = _pal(
    tail=[(74, 15, 15), (94, 15, 15), (120, 22, 22), (142, 27, 27)],
    tail_line=(60, 12, 12),
    body_shadow=RED_DARK,
    body_main=BARON_RED,
    body_chest=(166, 46, 42),
    body_belly=RED_LIGHT,
    sheen=(200, 90, 80, 55),
    wing_main=(130, 24, 24),
    wing_dark=RED_DARK,
    wing_tip=(150, 40, 36),
    wing_secondary=None,
    wing_highlight=RED_LIGHT,
    head_shadow=RED_DARK,
    head_main=BARON_RED,
    head_cheek=(166, 46, 42),
    head_crown=(120, 22, 22),
    lens_frame=LEATHER_D,
    lens_body=(40, 26, 14),
    lens_tint=None,
    lens_glint=None,
    beak_main=BRASS_GOLD,
    beak_dark=BRASS_D,
    beak_gloss=(255, 230, 150),
    foot=LEATHER_D,
)


def _baron_base(angle_deg):
    return _build_parrot_with_palette(angle_deg, P_BARON, draw_lenses=False)


def _paint(surf, wing_angle_deg):
    # Body centre in composite space (parrot body centre (32,32) + PARROT_DY).
    BCX, BCY = 32, 52

    # ── Night-safe rim — one lighter-crimson pixel line tracing the lower/back
    # contour so the oxblood body keeps a readable silhouette against the night
    # biome, where the deep leather would otherwise sink into a dark sky. Laid
    # first so body detail sits over it.
    pygame.draw.lines(surf, RIM_RED, False,
                      [(8, 50), (11, 57), (19, 62), (28, 65), (38, 64), (46, 58)], 1)

    # ── Tall dark leather flying helmet over the crown — taller than a snug cap so
    # the headgear breaks the outline above the head; leather-dark lifts off the
    # crimson head, one darker seam arcs across the dome. Drawn before the head
    # trim so the fur roots on its lower edge.
    helmet = [(HX - 10, CROWN_Y + 1), (HX - 6, CROWN_Y - 6), (HX + 4, CROWN_Y - 7),
              (HX + 10, CROWN_Y), (HX + 11, HY - 2), (HX - 2, HY + 3), (HX - 10, HY - 1)]
    _poly(surf, LEATHER_D, helmet)
    pygame.draw.line(surf, LEATHER_DD, (HX - 4, CROWN_Y - 2), (HX + 6, CROWN_Y - 4), 1)

    # ── Fur trim band across the brow — overlapping cream circles keep a lumpy
    # tuft silhouette, but held to the spec cream with NO bright-white pixel so the
    # band stops competing with the monocle glint. Small 1px cream bumps carry the
    # lumpy top edge instead of a hotspot.
    for fx in range(HX - 9, HX + 9, 3):
        pygame.draw.circle(surf, FUR_SHADE, (fx, HY - 2), 4)
        pygame.draw.circle(surf, FUR_CREAM, (fx, HY - 3), 4)
    for bx in (HX - 7, HX - 1, HX + 5):
        pygame.draw.circle(surf, FUR_CREAM, (bx, HY - 6), 1)

    # ── Leather line where the fur meets the monocle — a single dark stroke over
    # the top of the eyepiece so helmet trim and lens read as two separate parts,
    # not one merged pale mass.
    pygame.draw.line(surf, LEATHER_D, (46, 34), (55, 33), 1)

    # ── Three brass tunic buttons down the jacket front on a dark seat, so a 1px
    # #5E0F0F gap keeps them from fusing into one gold blob at 40px — and distinct
    # from the monocle chain beside them.
    pygame.draw.line(surf, RED_DARK, (41, 38), (41, 50), 5)
    for by in (40, 44, 48):
        pygame.draw.circle(surf, BRASS_GOLD, (41, by), 2)
        pygame.draw.circle(surf, (255, 230, 150), (40, by - 1), 1)
    for gy in (42, 46):
        pygame.draw.line(surf, RED_DARK, (39, gy), (43, gy), 1)

    # ── Iron cross on the near shoulder — the concept's unique identity marker. A
    # plain plus in near-black under a 1px white rim survives the 40px downscale
    # where a flared cross-pattée would blur; sits clear-left of the button run.
    cxs, cys = 37, 34
    pygame.draw.line(surf, CROSS_WHITE, (cxs - 3, cys), (cxs + 3, cys), 5)
    pygame.draw.line(surf, CROSS_WHITE, (cxs, cys - 3), (cxs, cys + 3), 5)
    pygame.draw.line(surf, IRON_BLACK, (cxs - 3, cys), (cxs + 3, cys), 3)
    pygame.draw.line(surf, IRON_BLACK, (cxs, cys - 3), (cxs, cys + 3), 3)

    # ── Brass monocle on the forward eye — a gleaming ring over muted glass, with
    # a hard pure-white specular clustered upper-right (one bright pixel-cluster
    # reads better than a pale fill) and a thin dimmed chain dropping to the collar
    # so it reads as an aristocrat's eyepiece, not a goggle lens.
    mx, my = HX + 4, HY - 2
    pygame.draw.circle(surf, LENS_MID, (mx, my), 4)
    pygame.draw.circle(surf, BRASS_GOLD, (mx, my), 5, 2)
    pygame.draw.rect(surf, CROSS_WHITE, (51, 37, 2, 2))
    pygame.draw.line(surf, CHAIN_GOLD, (49, 44), (44, 49), 1)


build = _make_skin(_paint, base_fn=_baron_base)
