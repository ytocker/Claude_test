"""
Render a grid: rows = store PARROT-tab skins, columns = lives states.

Output: docs/store_parrot_lives_grid.png
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import pygame
pygame.init()
pygame.font.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.parrot as _parrot
from game.parrot import (
    _h_draw_bandaids, _h_draw_headwrap, _h_draw_chest_dressing,
    _h_draw_ragged_cuts, _h_draw_cracked_lens, _fh_draw_single_crack,
    _add_outline, get_parcel,
)
from game.dollar_parrot_ghost import _build_parrot_with_palette, _draw_lenses
from game.store_skins import (
    P_DISCO, P_BLUEGOLD, P_AMAZON, P_SUNCONURE, P_HYACINTH,
    P_COCKATOO, P_LORIKEET, P_PRISM, P_THORNCREST, P_EMBERMOTH,
    _AURORA_PAL, P_MOONBLOOM, P_TEMPEST, P_BINKY, P_CHROME,
    _build_voodoo_zombie,
)
from game.skeleton_skin import _flesh_base

# ── layout ────────────────────────────────────────────────────────────────────
LABEL_W = 150
CELL_W  = 110
CELL_H  = 140
HDR_H   = 48
MARGIN  = 14
BIRD_Y  = 52

BG        = (22, 26, 36)
LABEL_BG  = (32, 36, 50)
TEXT_COL  = (220, 220, 230)
DIM_COL   = (130, 130, 150)
SKY_TOP   = (80, 130, 210)
SKY_BOT   = (100, 150, 200)

COLS = ["CLEAN", "FIRST-HIT", "LAST-LIFE"]
COL_STATES = ["clean", "first_hit", "last_life"]

# Rows: (skin_id, display_name, palette | None, special)
# special: None | "skeleton" | "zombie"
SKINS = [
    ("skin_skeleton",  "SKELETON",    None,        "skeleton"),
    ("skin_zombie",    "ZOMBIE",      None,        "zombie"),
    ("skin_disco",     "DISCO",       P_DISCO,     None),
    ("skin_bluegold",  "BLUE MACAW",  P_BLUEGOLD,  None),
    ("skin_amazon",    "AMAZON",      P_AMAZON,    None),
    ("skin_sunconure", "SUN CONURE",  P_SUNCONURE, None),
    ("skin_hyacinth",  "HYACINTH",    P_HYACINTH,  None),
    ("skin_cockatoo",  "COCKATOO",    P_COCKATOO,  None),
    ("skin_lorikeet",  "LORIKEET",    P_LORIKEET,  None),
    ("skin_prism",     "PRISM",       P_PRISM,     None),
    ("skin_thorncrest","THORNCREST",  P_THORNCREST,None),
    ("skin_embermoth", "EMBERMOTH",   P_EMBERMOTH, None),
    ("skin_aurora",    "AURORA",      _AURORA_PAL, None),
    ("skin_moonbloom", "MOONBLOOM",   P_MOONBLOOM, None),
    ("skin_tempest",   "TEMPEST",     P_TEMPEST,   None),
    ("skin_binky",     "BINKY",       P_BINKY,     None),
    ("skin_chrome",    "CHROME",      P_CHROME,    None),
]


def _font(size):
    return pygame.font.SysFont("monospace", size, bold=True)


def fill_sky(surf):
    w, h = surf.get_size()
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (w - 1, y))


def _build_first_hit(palette):
    base = _build_parrot_with_palette(10.0, palette)
    _h_draw_bandaids(base)
    _fh_draw_single_crack(base)
    return _add_outline(base)


def _build_last_life(palette):
    base = _build_parrot_with_palette(10.0, palette, draw_lenses=False)
    _h_draw_bandaids(base)
    _h_draw_headwrap(base)
    _draw_lenses(base, 50, 20, palette)
    _h_draw_chest_dressing(base)
    _h_draw_ragged_cuts(base)
    _h_draw_cracked_lens(base)
    return _add_outline(base)


def _build_special_first_hit(base_surf):
    _h_draw_bandaids(base_surf)
    _fh_draw_single_crack(base_surf)
    return _add_outline(base_surf)


def _build_special_last_life(base_surf):
    _h_draw_bandaids(base_surf)
    _h_draw_headwrap(base_surf)
    _h_draw_chest_dressing(base_surf)
    _h_draw_ragged_cuts(base_surf)
    return _add_outline(base_surf)


def render_cell(skin_id, palette, lives_state, special):
    cell = pygame.Surface((CELL_W, CELL_H))
    fill_sky(cell)

    par = get_parcel("normal")

    if lives_state == "clean":
        img = _parrot.get_skin_frame(skin_id, 1, 0.0)
        cell.blit(img, img.get_rect(center=(CELL_W // 2, BIRD_Y)))
    elif lives_state == "first_hit":
        if special == "skeleton":
            img = _build_special_first_hit(_flesh_base(10.0))
        elif special == "zombie":
            img = _build_special_first_hit(_build_voodoo_zombie(10.0))
        else:
            img = _build_first_hit(palette)
        cell.blit(img, img.get_rect(center=(CELL_W // 2, BIRD_Y)))
        cell.blit(par, par.get_rect(center=(CELL_W // 2, BIRD_Y + 12)))
    else:  # last_life
        if special == "skeleton":
            img = _build_special_last_life(_flesh_base(10.0))
        elif special == "zombie":
            img = _build_special_last_life(_build_voodoo_zombie(10.0))
        else:
            img = _build_last_life(palette)
        cell.blit(img, img.get_rect(center=(CELL_W // 2, BIRD_Y)))
        cell.blit(par, par.get_rect(center=(CELL_W // 2, BIRD_Y + 12)))

    return cell


def main():
    n_rows = len(SKINS)
    n_cols = len(COLS)
    total_w = MARGIN + LABEL_W + n_cols * CELL_W + MARGIN
    total_h = MARGIN + HDR_H + n_rows * CELL_H + MARGIN

    canvas = pygame.Surface((total_w, total_h))
    canvas.fill(BG)

    fnt_title = _font(14)
    fnt_hdr   = _font(11)
    fnt_label = _font(11)

    title = fnt_title.render("STORE PARROTS × LIVES STATE", True, TEXT_COL)
    canvas.blit(title, title.get_rect(center=(total_w // 2, MARGIN + HDR_H // 2)))

    # column headers
    for ci, col_label in enumerate(COLS):
        cx = MARGIN + LABEL_W + ci * CELL_W + CELL_W // 2
        cy = MARGIN + HDR_H // 2
        surf = fnt_hdr.render(col_label, True, TEXT_COL)
        canvas.blit(surf, surf.get_rect(center=(cx, cy)))

    # rows
    for ri, (skin_id, display_name, palette, special) in enumerate(SKINS):
        row_top = MARGIN + HDR_H + ri * CELL_H

        # label panel
        label_rect = pygame.Rect(MARGIN, row_top, LABEL_W, CELL_H)
        pygame.draw.rect(canvas, LABEL_BG, label_rect)

        # skin name centred in label
        lbl = fnt_label.render(display_name, True, TEXT_COL)
        canvas.blit(lbl, lbl.get_rect(center=(MARGIN + LABEL_W // 2, row_top + CELL_H // 2)))

        # cells
        for ci, (col_label, col_state) in enumerate(zip(COLS, COL_STATES)):
            cell_x = MARGIN + LABEL_W + ci * CELL_W
            cell = render_cell(skin_id, palette, col_state, special)
            canvas.blit(cell, (cell_x, row_top))
            # 1-px divider
            pygame.draw.rect(canvas, BG, (cell_x, row_top, CELL_W, 1))
            pygame.draw.rect(canvas, BG, (cell_x, row_top, 1, CELL_H))

    # outer border
    pygame.draw.rect(canvas, (60, 65, 85), canvas.get_rect(), 2)

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "store_parrot_lives_grid.png")
    pygame.image.save(canvas, out_path)
    print(f"Saved {total_w}×{total_h} → {out_path}")
    pygame.quit()


if __name__ == "__main__":
    main()
