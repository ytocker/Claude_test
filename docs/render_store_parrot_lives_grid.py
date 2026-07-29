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
    _H_GAUZE, _H_HEM, _H_SCRATCH_PALE, _h_stamp_clipped,
)
from game.dollar_parrot_ghost import _build_parrot_with_palette, _draw_lenses
from game.store_skins import (
    PARROT_DY,
    P_DISCO, P_BLUEGOLD, P_AMAZON, P_SUNCONURE, P_HYACINTH,
    P_COCKATOO, P_LORIKEET, P_PRISM, P_THORNCREST, P_EMBERMOTH,
    _AURORA_PAL, P_MOONBLOOM, P_TEMPEST, P_BINKY, P_CHROME,
    _build_voodoo_zombie,
    _paint_disco, _paint_cockatoo_crest, _paint_prism,
    _paint_thorncrest, _paint_embermoth, _paint_binky,
    _aurora_front,   _aurora_back,
    _moonbloom_front, _moonbloom_back, _MB_OUTLINE,
    _tempest_front,  _tempest_back,   _TP_OUTLINE,
    _chrome_front,   _chrome_back,
    _zb_hex_aura, _zb_rim_halo,
)
from game.skeleton_skin import _flesh_base, _paint as _skeleton_paint

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
SKY_TOP   = (80, 130, 210)
SKY_BOT   = (100, 150, 200)

COLS = ["CLEAN", "FIRST-HIT", "LAST-LIFE"]
COL_STATES = ["clean", "first_hit", "last_life"]

# Rows: (skin_id, display_name, palette, paint_fn, back_fn,
#        outline_color, draw_std_lenses, special)
# draw_std_lenses=False → body built with draw_lenses=False always;
#                          no _draw_lenses call in last_life (paint_fn owns lenses)
# special: None | "skeleton" | "zombie"
SKINS = [
    ("skin_skeleton",   "SKELETON",   None,        None,                  None,            None,        True,  "skeleton"),
    ("skin_zombie",     "ZOMBIE",     None,        None,                  None,            None,        True,  "zombie"),
    ("skin_disco",      "DISCO",      P_DISCO,     _paint_disco,          None,            None,        True,  None),
    ("skin_bluegold",   "BLUE MACAW", P_BLUEGOLD,  None,                  None,            None,        True,  None),
    ("skin_amazon",     "AMAZON",     P_AMAZON,    None,                  None,            None,        True,  None),
    ("skin_sunconure",  "SUN CONURE", P_SUNCONURE, None,                  None,            None,        True,  None),
    ("skin_hyacinth",   "HYACINTH",   P_HYACINTH,  None,                  None,            None,        True,  None),
    ("skin_cockatoo",   "COCKATOO",   P_COCKATOO,  _paint_cockatoo_crest, None,            None,        True,  None),
    ("skin_lorikeet",   "LORIKEET",   P_LORIKEET,  None,                  None,            None,        True,  None),
    ("skin_prism",      "PRISM",      P_PRISM,     _paint_prism,          None,            None,        True,  None),
    ("skin_thorncrest", "THORNCREST", P_THORNCREST,_paint_thorncrest,     None,            None,        True,  None),
    ("skin_embermoth",  "EMBERMOTH",  P_EMBERMOTH, _paint_embermoth,      None,            None,        True,  None),
    ("skin_aurora",     "AURORA",     _AURORA_PAL, _aurora_front,         _aurora_back,    None,        True,  None),
    ("skin_moonbloom",  "MOONBLOOM",  P_MOONBLOOM, _moonbloom_front,      _moonbloom_back, _MB_OUTLINE, True,  None),
    ("skin_tempest",    "TEMPEST",    P_TEMPEST,   _tempest_front,        _tempest_back,   _TP_OUTLINE, True,  None),
    ("skin_binky",      "BINKY",      P_BINKY,     _paint_binky,          None,            None,        True,  None),
    ("skin_chrome",     "CHROME",     P_CHROME,    _chrome_front,         _chrome_back,    None,        False, None),
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


def _draw_open_beak(surf, P):
    """Split two-polygon beak matching the hurt-frame anatomy (open mouth look)."""
    beak_lo = tuple(int(c * 0.87) for c in P['beak_main'])
    upper = [(55, 21), (61, 24), (58, 26), (52, 25)]
    lower = [(52, 26), (58, 27), (59, 30), (54, 31)]
    pygame.draw.polygon(surf, P['beak_main'], upper)
    pygame.draw.polygon(surf, P['beak_dark'], upper, 1)
    pygame.draw.polygon(surf, beak_lo, lower)
    pygame.draw.polygon(surf, P['beak_dark'], lower, 1)
    pygame.draw.line(surf, P['beak_gloss'], (55, 22), (59, 24), 1)


def _composite_with_back(comp, back_fn, outline_color):
    """Outline comp, composite back_fn result behind it, return final surface."""
    kw = {"outline_color": outline_color} if outline_color else {}
    bird = _add_outline(comp, **kw)
    if back_fn is None:
        return bird
    pad = (bird.get_width() - 64) // 2
    result = pygame.Surface(bird.get_size(), pygame.SRCALPHA)
    back = pygame.Surface((64, 100), pygame.SRCALPHA)
    back_fn(back, 10.0)
    result.blit(back, (pad, pad))
    result.blit(bird, (0, 0))
    return result


# ── palette / composite hurt builders ────────────────────────────────────────

def _build_hurt_composite(palette, paint_fn, back_fn, outline_color,
                          lives_state, draw_std_lenses):
    """Unified builder for all composite (palette-based) hurt states."""
    is_last = (lives_state == "last_life")

    # body: draw standard lenses in base only for first_hit with std lenses
    draw_body_lenses = (not is_last) and draw_std_lenses
    body = _build_parrot_with_palette(10.0, palette, draw_lenses=draw_body_lenses)
    comp = pygame.Surface((64, 100), pygame.SRCALPHA)
    comp.blit(body, (0, PARROT_DY))

    if not is_last:
        # first_hit: paint_fn AFTER body (lenses already in body for std-lens skins)
        if paint_fn:
            paint_fn(comp, 10.0)
        sprite = comp.subsurface((0, PARROT_DY, 64, 60))
        _draw_open_beak(sprite, palette)
        _h_draw_bandaids(sprite)
        _fh_draw_single_crack(sprite)
    else:
        # last_life: dressings first, then lenses, then paint_fn so lens overlays
        # are drawn ON TOP of the palette lenses (fixes prism crystal rim lines etc.)
        sprite = comp.subsurface((0, PARROT_DY, 64, 60))
        _h_draw_bandaids(sprite)
        _h_draw_headwrap(sprite)
        if draw_std_lenses:
            _draw_lenses(sprite, 50, 20, palette)
        _draw_open_beak(sprite, palette)
        if paint_fn:
            paint_fn(comp, 10.0)
        _h_draw_chest_dressing(sprite)
        _h_draw_ragged_cuts(sprite)
        _h_draw_cracked_lens(sprite)

    return _composite_with_back(comp, back_fn, outline_color)


def _build_hurt_simple(palette, lives_state):
    """Hurt builder for pure-palette skins (no accessories, no back layer)."""
    if lives_state == "first_hit":
        base = _build_parrot_with_palette(10.0, palette)
        _draw_open_beak(base, palette)
        _h_draw_bandaids(base)
        _fh_draw_single_crack(base)
    else:
        base = _build_parrot_with_palette(10.0, palette, draw_lenses=False)
        _h_draw_bandaids(base)
        _h_draw_headwrap(base)
        _draw_lenses(base, 50, 20, palette)
        _draw_open_beak(base, palette)
        _h_draw_chest_dressing(base)
        _h_draw_ragged_cuts(base)
        _h_draw_cracked_lens(base)
    return _add_outline(base)


def _draw_headwrap_shifted(surf, dy):
    """Headwrap cap shifted down by dy pixels — so it sits on visible skull bone."""
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    d = pygame.draw
    cap_pts = [(36, 21 + dy), (37, 16 + dy), (40, 12 + dy), (45, 10 + dy),
               (51, 11 + dy), (56, 14 + dy), (59, 18 + dy), (59, 21 + dy)]
    d.polygon(layer, _H_GAUZE, cap_pts)
    d.lines(layer, _H_HEM, False, cap_pts[:-1], 1)
    d.line(layer, _H_HEM, (38, 19 + dy), (57, 19 + dy), 1)
    d.line(layer, _H_HEM, (40, 17 + dy), (56, 17 + dy), 1)
    d.line(layer, _H_HEM, (40, 13 + dy), (54, 13 + dy), 1)
    d.line(layer, _H_HEM, (39, 15 + dy), (56, 15 + dy), 1)
    knot_pts = [(36, 16 + dy), (38, 14 + dy), (41, 15 + dy), (40, 18 + dy), (37, 19 + dy)]
    d.polygon(layer, _H_GAUZE, knot_pts)
    d.polygon(layer, _H_HEM,   knot_pts, 1)
    _h_stamp_clipped(surf, layer)
    d.line(surf, _H_GAUZE, (36, 17 + dy), (33, 20 + dy), 2)
    d.line(surf, _H_HEM,   (36, 17 + dy), (33, 20 + dy), 1)
    d.line(surf, _H_GAUZE, (37, 19 + dy), (35, 23 + dy), 2)
    d.line(surf, _H_HEM,   (37, 19 + dy), (35, 23 + dy), 1)
    surf.set_at((41, 19 + dy), _H_SCRATCH_PALE)
    surf.set_at((42, 19 + dy), _H_SCRATCH_PALE)
    surf.set_at((41, 20 + dy), (*_H_SCRATCH_PALE[:2], _H_SCRATCH_PALE[2] - 20))


def _build_hurt_skeleton(lives_state):
    """Skeleton hurt: build in composite space so bones (skull/ribs/spine) are present."""
    comp = pygame.Surface((64, 100), pygame.SRCALPHA)
    comp.blit(_flesh_base(10.0), (0, PARROT_DY))
    _skeleton_paint(comp, 10.0)
    sprite = comp.subsurface((0, PARROT_DY, 64, 60))
    if lives_state == "first_hit":
        _h_draw_bandaids(sprite)
        _fh_draw_single_crack(sprite)
    else:
        _h_draw_bandaids(sprite)
        _draw_headwrap_shifted(sprite, 5)
        _h_draw_chest_dressing(sprite)
        _h_draw_ragged_cuts(sprite)
    return _add_outline(comp)


def _build_hurt_zombie(lives_state):
    """Zombie hurt: dressings + cursed-green aura compositing."""
    base = _build_voodoo_zombie(10.0)
    if lives_state == "first_hit":
        _h_draw_bandaids(base)
        _fh_draw_single_crack(base)
    else:
        _h_draw_bandaids(base)
        _draw_headwrap_shifted(base, 7)
        _h_draw_chest_dressing(base)
        _h_draw_ragged_cuts(base)
    core = _add_outline(base)
    pad = 16
    cw, ch = core.get_size()
    out = pygame.Surface((cw + pad * 2, ch + pad * 2), pygame.SRCALPHA)
    _zb_hex_aura(out, out.get_width() // 2, out.get_height() // 2 + 4,
                 max(cw, ch) // 2 + 6)
    ring = _zb_rim_halo(core)
    out.blit(ring, (pad - 2, pad - 2))
    out.blit(core, (pad, pad))
    return out


def render_cell(skin_id, palette, paint_fn, back_fn, outline_color,
                draw_std_lenses, lives_state, special):
    cell = pygame.Surface((CELL_W, CELL_H))
    fill_sky(cell)

    par = get_parcel("normal")

    if lives_state == "clean":
        img = _parrot.get_skin_frame(skin_id, 1, 0.0)
        cell.blit(img, img.get_rect(center=(CELL_W // 2, BIRD_Y)))
    else:
        if special == "skeleton":
            img = _build_hurt_skeleton(lives_state)
        elif special == "zombie":
            img = _build_hurt_zombie(lives_state)
        elif paint_fn is not None or back_fn is not None:
            img = _build_hurt_composite(palette, paint_fn, back_fn, outline_color,
                                        lives_state, draw_std_lenses)
        else:
            img = _build_hurt_simple(palette, lives_state)
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

    for ci, col_label in enumerate(COLS):
        cx = MARGIN + LABEL_W + ci * CELL_W + CELL_W // 2
        surf = fnt_hdr.render(col_label, True, TEXT_COL)
        canvas.blit(surf, surf.get_rect(center=(cx, MARGIN + HDR_H // 2)))

    for ri, (skin_id, display_name, palette, paint_fn, back_fn,
             outline_color, draw_std_lenses, special) in enumerate(SKINS):
        row_top = MARGIN + HDR_H + ri * CELL_H

        label_rect = pygame.Rect(MARGIN, row_top, LABEL_W, CELL_H)
        pygame.draw.rect(canvas, LABEL_BG, label_rect)
        lbl = fnt_label.render(display_name, True, TEXT_COL)
        canvas.blit(lbl, lbl.get_rect(center=(MARGIN + LABEL_W // 2, row_top + CELL_H // 2)))

        for ci, (col_label, col_state) in enumerate(zip(COLS, COL_STATES)):
            cell_x = MARGIN + LABEL_W + ci * CELL_W
            cell = render_cell(skin_id, palette, paint_fn, back_fn, outline_color,
                               draw_std_lenses, col_state, special)
            canvas.blit(cell, (cell_x, row_top))
            pygame.draw.rect(canvas, BG, (cell_x, row_top, CELL_W, 1))
            pygame.draw.rect(canvas, BG, (cell_x, row_top, 1, CELL_H))

    pygame.draw.rect(canvas, (60, 65, 85), canvas.get_rect(), 2)

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "store_parrot_lives_grid.png")
    pygame.image.save(canvas, out_path)
    print(f"Saved {total_w}×{total_h} → {out_path}")
    pygame.quit()


if __name__ == "__main__":
    main()
