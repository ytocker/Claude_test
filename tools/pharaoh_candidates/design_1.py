"""DESIGN 1 — GOLDEN PHARAOH (Tutankhamun) — scratch costume exploration.

Full Egyptian king: gold body recolor (eternal flesh of the gods), a flaring
lapis+gold NEMES headdress with a rearing gold URAEUS cobra, a short braided
false beard, a broad concentric USEKH collar across the breast, a crook & flail
slung diagonally inside the wing, and gold anklets. The hero read is the wide
nemes silhouette + all-gold body + broad collar; lapis stripes and bronze
shadow carry the value structure on a night sky where gold alone would wash out.

Exploration only — NOT registered in store_skins.BUILDERS.
Render: tools/pharaoh_candidates/render_design_1.py.
"""
from __future__ import annotations

import math

import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette

# ── gold body palette (eternal-flesh gold so the whole bird glows) ───────────
# Gold needs a real value range or it flattens to a coin: bronze in the shadows,
# warm gold mid, pale glint highlight. Lapis is reserved for the nemes so the
# body stays unambiguously golden.
_GP_BODY = _pal(
    tail=[(122, 78, 22), (158, 108, 30), (200, 150, 48), (236, 192, 86)],
    tail_line=(92, 58, 16),
    body_shadow=(150, 104, 32),
    body_main=(232, 184, 70),
    body_chest=(248, 210, 104),
    body_belly=(238, 196, 92),
    sheen=(255, 246, 196, 120),
    wing_main=(214, 162, 54),
    wing_dark=(150, 104, 32),
    wing_tip=(252, 222, 120),
    wing_secondary=(244, 200, 92),
    wing_highlight=(255, 246, 196),
    head_shadow=(168, 118, 38),
    head_main=(240, 196, 84),
    head_cheek=(250, 214, 112),
    head_crown=(248, 208, 102),
    lens_frame=(150, 104, 32),
    lens_body=(60, 40, 14),
    lens_tint=None,
    lens_glint=None,
    beak_main=(238, 196, 88),
    beak_dark=(150, 104, 32),
    beak_gloss=(255, 246, 196),
    foot=(150, 104, 32),
)


def _gp_base(angle_deg):
    return _build_parrot_with_palette(angle_deg, _GP_BODY, draw_lenses=False)


# ── costume colours ──────────────────────────────────────────────────────────
_GP_GOLD   = (244, 196, 48)     # #F4C430
_GP_GOLD_D = (122, 74, 18)      # #7A4A12 deep bronze shadow
_GP_GLINT  = (255, 242, 176)    # #FFF2B0
_GP_LAPIS  = (27, 58, 140)      # #1B3A8C
_GP_LAPIS_D = (18, 38, 96)
_GP_TURQ   = (47, 184, 166)     # #2FB8A6
_GP_KOHL   = (24, 22, 30)


def _paint(surf, _a):
    cy = CROWN_Y

    # ── crook & flail, slung diagonally INSIDE the wing ──────────────────────
    # Painted first so the body covers the shaft mid-section; only the gold
    # heads peek inside the silhouette. Both staffs are tucked above the feet
    # line so nothing dangles past the bird's true footprint.
    # Crook (shepherd's hook) — leans one way.
    cr_top = (HX - 16, HY + 4)
    cr_bot = (HX - 9, HY + 18)
    pygame.draw.line(surf, _GP_GOLD_D, cr_top, cr_bot, 4)
    pygame.draw.line(surf, _GP_GOLD, cr_top, cr_bot, 2)
    pygame.draw.lines(surf, _GP_GOLD_D, False,
                      [(HX - 16, HY + 4), (HX - 19, HY + 2), (HX - 18, HY + 6)], 3)
    pygame.draw.lines(surf, _GP_GOLD, False,
                      [(HX - 16, HY + 4), (HX - 19, HY + 2), (HX - 18, HY + 6)], 1)
    # Lapis binding rings down the crook shaft so it reads as a royal staff.
    pygame.draw.circle(surf, _GP_LAPIS, (HX - 14, HY + 8), 1)
    pygame.draw.circle(surf, _GP_LAPIS, (HX - 12, HY + 13), 1)

    # Flail — crossed the other way, a short handle with a beaded tip.
    fl_top = (HX - 8, HY + 3)
    fl_bot = (HX - 15, HY + 17)
    pygame.draw.line(surf, _GP_GOLD_D, fl_top, fl_bot, 4)
    pygame.draw.line(surf, _GP_GOLD, fl_top, fl_bot, 2)
    # Three beaded strands fanning off the flail head.
    for dx in (-2, 0, 2):
        pygame.draw.line(surf, _GP_GOLD_D, fl_top, (fl_top[0] + dx, fl_top[1] - 4), 2)
        pygame.draw.circle(surf, _GP_GOLD, (fl_top[0] + dx, fl_top[1] - 4), 1)
    pygame.draw.circle(surf, _GP_GLINT, (fl_top[0], fl_top[1] - 4), 1)

    # ── broad USEKH collar — concentric bead rows arcing across the breast ────
    # Sits INSIDE the body footprint (top ~HY+6, bottom ~HY+18). Alternating
    # gold + turquoise arcs read as a beaded gorget at 40px; the bronze base
    # arc carries the shape on night where gold alone would vanish.
    col_cx, col_cy = HX - 5, HY + 6
    for r, col in ((13, _GP_GOLD_D), (12, _GP_GOLD), (10, _GP_TURQ),
                   (8, _GP_GOLD), (6, _GP_LAPIS)):
        pygame.draw.arc(surf, col, (col_cx - r, col_cy - r + 2, r * 2, r * 2),
                        3.55, 6.0, 2)
    # Bead dots punctuating the outermost gold row for a jewelled read.
    for k in range(5):
        a = 3.7 + k * 0.42
        bx = col_cx + 12 * math.cos(a)
        by = col_cy + 12 * math.sin(a) + 2
        pygame.draw.circle(surf, _GP_GLINT, (int(bx), int(by)), 1)

    # ── striped flaring NEMES headdress ──────────────────────────────────────
    # Wide shoulder lappets sweeping down past the cheeks are the hero
    # silhouette. Lapis+gold horizontal stripes; bronze edge keeps the gold
    # cloth off a bright sky.
    # Near (front) lappet — flares down the cheek, framing the face.
    near_lappet = [(HX - 2, cy + 4), (HX + 8, cy + 5), (HX + 9, HY + 13),
                   (HX + 1, HY + 15)]
    _poly(surf, _GP_GOLD, near_lappet)
    for i in range(5):
        yy = cy + 6 + i * 3
        col = _GP_LAPIS if i % 2 == 0 else _GP_GOLD_D
        pygame.draw.line(surf, col, (HX - 1, yy), (HX + 9, yy + 1), 2)
    pygame.draw.polygon(surf, _GP_GOLD_D, near_lappet, 1)

    # Far (back) lappet — the flare on the far side that widens the silhouette.
    far_lappet = [(HX - 15, cy + 3), (HX - 5, cy + 3), (HX - 4, HY + 14),
                  (HX - 14, HY + 14)]
    _poly(surf, _GP_GOLD, far_lappet)
    for i in range(5):
        yy = cy + 5 + i * 3
        col = _GP_LAPIS if i % 2 == 0 else _GP_GOLD_D
        pygame.draw.line(surf, col, (HX - 14, yy), (HX - 4, yy), 2)
    pygame.draw.polygon(surf, _GP_GOLD_D, far_lappet, 1)

    # Domed headcloth cap over the crown, flaring wider than the bare head.
    pygame.draw.ellipse(surf, _GP_GOLD_D, (HX - 16, cy - 6, 33, 20))
    pygame.draw.ellipse(surf, _GP_GOLD, (HX - 15, cy - 6, 31, 17))
    # Horizontal lapis+gold stripes banding the cap (the textbook nemes read).
    for i in range(5):
        yy = cy - 4 + i * 3
        col = _GP_LAPIS if i % 2 == 0 else _GP_GOLD_D
        pygame.draw.line(surf, col, (HX - 14, yy), (HX + 15, yy), 2)
    # Fat gold brow-band capping the front.
    pygame.draw.line(surf, _GP_GOLD_D, (HX - 15, cy + 8), (HX + 16, cy + 7), 5)
    pygame.draw.line(surf, _GP_GOLD, (HX - 15, cy + 7), (HX + 16, cy + 6), 3)
    pygame.draw.line(surf, _GP_GLINT, (HX - 12, cy + 6), (HX + 4, cy + 5), 1)

    # ── rearing URAEUS cobra at the brow — the hero accent above the band ─────
    bx = HX
    pygame.draw.line(surf, _GP_GOLD_D, (bx, cy + 5), (bx - 1, cy - 8), 4)
    pygame.draw.line(surf, _GP_GOLD, (bx, cy + 5), (bx - 1, cy - 8), 2)
    # Flared hood.
    _poly(surf, _GP_GOLD,
          [(HX - 6, cy - 7), (HX + 4, cy - 7), (HX - 1, cy - 13)])
    _poly(surf, _GP_LAPIS,
          [(HX - 4, cy - 8), (HX + 2, cy - 8), (HX - 1, cy - 11)])
    pygame.draw.circle(surf, _GP_GLINT, (HX - 1, cy - 12), 2)
    pygame.draw.circle(surf, (210, 50, 50), (HX - 1, cy - 12), 1)  # cobra eye

    # ── thin kohl eye line on the near eye ───────────────────────────────────
    pygame.draw.line(surf, _GP_KOHL, (HX + 1, HY - 2), (HX + 9, HY - 3), 1)
    pygame.draw.line(surf, _GP_KOHL, (HX + 9, HY - 3), (HX + 12, HY - 5), 1)  # liner flick

    # ── short braided FALSE BEARD straight down from the chin ─────────────────
    # Within the head/upper-body footprint — a stubby plaited post, never below
    # the collar.
    by0 = HY + 4
    pygame.draw.rect(surf, _GP_GOLD_D, (HX + 5, by0, 5, 11), border_radius=2)
    pygame.draw.rect(surf, _GP_GOLD, (HX + 6, by0, 3, 10), border_radius=2)
    for j in range(3):
        yy = by0 + 2 + j * 3
        pygame.draw.line(surf, _GP_GOLD_D, (HX + 6, yy), (HX + 9, yy), 1)  # braid seams
    pygame.draw.line(surf, _GP_GLINT, (HX + 7, by0 + 1), (HX + 7, by0 + 8), 1)

    # ── gold anklets at the feet line ────────────────────────────────────────
    for fx in (HX - 21, HX - 14):
        pygame.draw.line(surf, _GP_GOLD_D, (fx, HY + 22), (fx + 4, HY + 22), 3)
        pygame.draw.line(surf, _GP_GOLD, (fx, HY + 22), (fx + 4, HY + 22), 1)


build = store_skins._make_skin(_paint, base_fn=_gp_base)
