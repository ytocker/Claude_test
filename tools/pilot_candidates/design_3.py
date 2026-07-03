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
GLASS_TINT  = (200, 230, 210) # cool monocle glass
IRON_BLACK  = (20, 18, 18)    # iron-cross body
CROSS_WHITE = (230, 225, 215) # iron-cross outline

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

    # ── Brass buttons down the chest — a bright vertical run so the jacket reads
    # as a buttoned tunic, laid first so the iron cross can overlap the top one.
    for by in (BCY - 8, BCY - 3, BCY + 2, BCY + 7):
        pygame.draw.circle(surf, BRASS_D, (BCX + 2, by + 1), 2)
        pygame.draw.circle(surf, BRASS_GOLD, (BCX + 2, by), 2)
        pygame.draw.circle(surf, (255, 230, 150), (BCX + 1, by - 1), 1)

    # ── Iron cross-pattée on the shoulder/upper wing — white-outlined first so a
    # 1px pale rim survives the downscale, then the black body on top. Rides the
    # wing flap because it sits on the composited wing shoulder.
    cxs, cys = BCX + 6, BCY - 10
    pygame.draw.line(surf, CROSS_WHITE, (cxs - 5, cys), (cxs + 5, cys), 5)
    pygame.draw.line(surf, CROSS_WHITE, (cxs, cys - 5), (cxs, cys + 5), 5)
    pygame.draw.line(surf, IRON_BLACK, (cxs - 5, cys), (cxs + 5, cys), 4)
    pygame.draw.line(surf, IRON_BLACK, (cxs, cys - 5), (cxs, cys + 5), 4)

    # ── Tall dark leather flying helmet over the crown — taller than a snug cap so
    # the headgear breaks the outline above the head; leather-dark lifts off the
    # crimson head, one darker seam arcs across the dome.
    helmet = [(HX - 10, CROWN_Y + 1), (HX - 6, CROWN_Y - 6), (HX + 4, CROWN_Y - 7),
              (HX + 10, CROWN_Y), (HX + 11, HY - 2), (HX - 2, HY + 3), (HX - 10, HY - 1)]
    _poly(surf, LEATHER_D, helmet)
    pygame.draw.line(surf, LEATHER_DD, (HX - 4, CROWN_Y - 2), (HX + 6, CROWN_Y - 4), 1)

    # ── Thick fur trim band around the helmet bottom edge — overlapping cream
    # circles make a lumpy, distinctive fur silhouette so the head read isn't just
    # a smooth cap. A shade underside gives each tuft form at the downscale.
    for fx in range(HX - 9, HX + 9, 3):
        pygame.draw.circle(surf, FUR_SHADE, (fx, HY - 1), 4)
        pygame.draw.circle(surf, FUR_CREAM, (fx, HY - 2), 4)
    pygame.draw.circle(surf, (240, 228, 200), (HX - 6, HY - 4), 1)

    # ── Brass monocle on the forward eye — a gleaming ring with cool glass, a hard
    # glint, and a thin chain dropping to the collar so it reads as an aristocrat's
    # eyepiece, not a goggle lens.
    mx, my = HX + 4, HY - 2
    pygame.draw.circle(surf, GLASS_TINT, (mx, my), 4)
    pygame.draw.circle(surf, BRASS_GOLD, (mx, my), 5, 2)
    pygame.draw.circle(surf, (255, 255, 255), (mx + 1, my - 2), 1)
    pygame.draw.line(surf, BRASS_D, (HX + 8, HY + 2), (HX + 4, HY + 8), 1)


build = _make_skin(_paint, base_fn=_baron_base)
