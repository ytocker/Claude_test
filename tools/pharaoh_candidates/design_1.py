"""DESIGN 1 — GOLDEN PHARAOH (Tutankhamun) — scratch costume exploration.

Egyptian king on a 3-tier value hierarchy — BRONZE body / GOLD regalia / LAPIS
+ TURQUOISE accents — so the king-stuff pops off the flesh at 40px instead of
washing into gold-on-gold. A keylined flaring lapis+gold NEMES headdress (the
#1 read) with a rearing gold URAEUS cobra, a bold 3-band USEKH collar promoted
to the 2nd hero element (turquoise mid-band is the single non-gold focal that
survives the downscale), a fattened keylined false beard, and gold anklets.
The crook & flail were dropped — they were mud at 40px.

Exploration only — NOT registered in store_skins.BUILDERS.
Render: tools/pharaoh_candidates/render_design_1.py.
"""
from __future__ import annotations

import math

import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette

# ── bronze body palette (darker eternal-flesh so regalia can out-pop it) ──────
# The body is pulled one full step down toward bronze on purpose: a 3-tier value
# hierarchy needs the flesh to sit BELOW the regalia, or the gold nemes/collar
# wash into a gold-on-gold blob at 40px. Bright gold + glint are reserved for
# the headdress brow-band, collar top row and uraeus only.
_GP_BODY = _pal(
    tail=[(104, 66, 18), (134, 92, 26), (172, 128, 42), (206, 158, 56)],
    tail_line=(80, 50, 14),
    body_shadow=(128, 88, 28),
    body_main=(206, 158, 56),
    body_chest=(222, 178, 72),
    body_belly=(212, 166, 62),
    sheen=(248, 226, 170, 110),
    wing_main=(186, 138, 46),
    wing_dark=(128, 88, 28),
    wing_tip=(222, 180, 78),
    wing_secondary=(210, 162, 60),
    wing_highlight=(238, 206, 132),
    head_shadow=(144, 100, 32),
    head_main=(212, 166, 62),
    head_cheek=(224, 182, 78),
    head_crown=(220, 174, 70),
    lens_frame=(128, 88, 28),
    lens_body=(54, 36, 12),
    lens_tint=None,
    lens_glint=None,
    beak_main=(210, 164, 60),
    beak_dark=(128, 88, 28),
    beak_gloss=(238, 206, 132),
    foot=(128, 88, 28),
)


def _gp_base(angle_deg):
    return _build_parrot_with_palette(angle_deg, _GP_BODY, draw_lenses=False)


# ── costume colours ──────────────────────────────────────────────────────────
_GP_GOLD   = (244, 196, 48)     # #F4C430 bright regalia gold (reserved)
_GP_GOLD_D = (122, 74, 18)      # #7A4A12 deep bronze shadow / keyline
_GP_KEY    = (122, 74, 18)      # #7A4A12 1px keyline against the bronze body
_GP_GLINT  = (255, 242, 176)    # #FFF2B0 (reserved)
_GP_LAPIS  = (18, 38, 95)       # #12265F stronger lapis so bands read fat
_GP_LAPIS_D = (12, 26, 70)
_GP_TURQ   = (47, 184, 166)     # #2FB8A6 single non-gold focal that survives 40px
_GP_KOHL   = (24, 22, 30)


def _paint(surf, _a):
    cy = CROWN_Y

    # ── broad USEKH collar — promoted to the 2nd hero element ─────────────────
    # A bold 3-band arc below the chin: bronze base / turquoise mid / gold top,
    # ~3px each. The turquoise is the deliberate single non-gold focal that
    # survives the downscale, giving the bronze body a distinct collar shape
    # instead of more gold-on-gold mush.
    col_cx, col_cy = HX - 4, HY + 4
    for r, col, w in ((14, _GP_KEY, 4), (13, _GP_GOLD_D, 3),
                      (11, _GP_TURQ, 3), (8, _GP_GOLD, 3)):
        pygame.draw.arc(surf, col, (col_cx - r, col_cy - r + 2, r * 2, r * 2),
                        3.55, 6.0, w)
    # A few gold beads punctuating the top row for a jewelled read.
    for k in range(4):
        a = 3.75 + k * 0.52
        bx = col_cx + 8 * math.cos(a)
        by = col_cy + 8 * math.sin(a) + 2
        pygame.draw.circle(surf, _GP_GOLD, (int(bx), int(by)), 1)

    # ── striped flaring NEMES headdress — the #1 hero read ────────────────────
    # The whole cloth (cap + both lappets) is wrapped in a 1px deep-bronze
    # keyline so its edge survives the downscale against the gold body, instead
    # of melting into a back-lump. Lappets splay into the classic flaring
    # trapezoid flanking the cheeks. Four FAT 2px bands of strong lapis between
    # the gold read as ~3-4 thick stripes, not thin downscale noise.

    # Far (back) lappet — flared low and wide to flank the far cheek.
    far_lappet = [(HX - 15, cy + 3), (HX - 4, cy + 4), (HX - 3, HY + 12),
                  (HX - 15, HY + 16)]
    _poly(surf, _GP_GOLD, far_lappet)
    for i in range(4):
        yy = cy + 5 + i * 3
        col = _GP_LAPIS if i % 2 == 0 else _GP_GOLD
        pygame.draw.line(surf, col, (HX - 14, yy), (HX - 4, yy), 2)
    pygame.draw.polygon(surf, _GP_KEY, far_lappet, 1)

    # Near (front) lappet — flares down and out to the lower-left, framing the
    # face in the trapezoid that says "pharaoh" at a glance.
    near_lappet = [(HX - 2, cy + 4), (HX + 9, cy + 5), (HX + 10, HY + 10),
                   (HX + 1, HY + 18)]
    _poly(surf, _GP_GOLD, near_lappet)
    for i in range(4):
        yy = cy + 6 + i * 3
        col = _GP_LAPIS if i % 2 == 0 else _GP_GOLD
        pygame.draw.line(surf, col, (HX - 1, yy), (HX + 9, yy + 1), 2)
    pygame.draw.polygon(surf, _GP_KEY, near_lappet, 1)

    # Domed headcloth cap over the crown, flaring wider than the bare head.
    pygame.draw.ellipse(surf, _GP_KEY, (HX - 17, cy - 7, 35, 22))
    pygame.draw.ellipse(surf, _GP_GOLD, (HX - 15, cy - 6, 31, 17))
    # Four FAT lapis+gold bands across the cap (the textbook nemes read).
    for i in range(4):
        yy = cy - 4 + i * 4
        col = _GP_LAPIS if i % 2 == 0 else _GP_GOLD
        pygame.draw.line(surf, col, (HX - 14, yy), (HX + 15, yy), 2)
    pygame.draw.ellipse(surf, _GP_KEY, (HX - 17, cy - 7, 35, 22), 1)
    # Bright gold brow-band capping the front — reserved-gold focal.
    pygame.draw.line(surf, _GP_KEY, (HX - 15, cy + 8), (HX + 16, cy + 7), 5)
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
    # Fattened to ~4px with a hard bronze keyline so the plaited post survives
    # the downscale; within the head footprint, never below the collar.
    by0 = HY + 4
    pygame.draw.rect(surf, _GP_KEY, (HX + 5, by0, 6, 11), border_radius=2)
    pygame.draw.rect(surf, _GP_GOLD, (HX + 6, by0, 4, 10), border_radius=2)
    for j in range(3):
        yy = by0 + 2 + j * 3
        pygame.draw.line(surf, _GP_GOLD_D, (HX + 6, yy), (HX + 9, yy), 1)  # braid seams

    # ── gold anklets at the feet line ────────────────────────────────────────
    for fx in (HX - 21, HX - 14):
        pygame.draw.line(surf, _GP_GOLD_D, (fx, HY + 22), (fx + 4, HY + 22), 3)
        pygame.draw.line(surf, _GP_GOLD, (fx, HY + 22), (fx + 4, HY + 22), 1)


build = store_skins._make_skin(_paint, base_fn=_gp_base)
