"""Render a 3-row × 11-column grid: lives states × power-up appearances.

Each row is one of the three lives phases (Clean / First-hit / Last-life).
Each column is one power-up visual effect applied on top of that lives state.

Run headlessly:
    SDL_AUDIODRIVER=dummy SDL_VIDEODRIVER=offscreen python docs/render_lives_powerup_grid.py
"""
import math
import os
import sys

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_VIDEODRIVER", "offscreen")

import pygame

pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import parrot

# ── Grid geometry ─────────────────────────────────────────────────────────────

LABEL_W = 140
CELL_W   = 100
CELL_H   = 130
HDR_H    = 48
MARGIN   = 12

BG       = (22, 26, 36)
LABEL_BG = (32, 36, 50)
TEXT_COL = (220, 220, 230)
DIM_COL  = (130, 130, 150)

SKY_TOP  = (80, 130, 210)
SKY_BOT  = (100, 150, 200)

# ── Content definition ────────────────────────────────────────────────────────

ROWS = [
    ("CLEAN\n(2 lives)", "clean"),
    ("FIRST HIT\n(1 life)",  "first_hit"),
    ("LAST LIFE\n(0 lives)", "last_life"),
]

COLS = [
    ("Normal",    "normal"),
    ("KFC",       "kfc"),
    ("Ghost",     "ghost"),
    ("Triple",    "triple"),
    ("KFC+Ghost", "kfc_ghost"),
    ("KFC+Triple","kfc_triple"),
    ("Gst+Trpl",  "ghost_triple"),
    ("Skateboard","skateboard"),
    ("Grow",      "grow"),
    ("Shrink",    "shrink"),
    ("Poison",    "poison"),
]

# ── The draw cascade (from Bird.draw) reproduced here without full Bird import ─
# Priority: kfc_ghost_triple > kfc_ghost > kfc_triple > ghost_triple >
#           kfc > ghost > triple > grow > on_last_life > on_first_hit > clean
# Post-cascade: poison tint, shrink scale, ghost alpha

def _get_sprite(lives_state: str, effect: str, frame_idx: int = 1, tilt: float = 0.0) -> pygame.Surface:
    """Return the final parrot sprite for (lives_state, effect) as Bird.draw would."""
    GROW_SCALE = 1.5   # from game.config; used for grow upscale
    SHRINK_VAL = 0.6   # fixed for the shrink demo

    ghost_pulse = math.pi / 2   # peak ghost brightness
    ghost_alpha = int(90 + 0.5 * (1 + math.sin(ghost_pulse)) * 80)  # ~170

    kfc    = "kfc"    in effect
    ghost  = "ghost"  in effect
    triple = "triple" in effect
    skate  = effect == "skateboard"
    grow   = effect == "grow"
    shrink = effect == "shrink"
    poison = effect == "poison"

    # Cascade — matches Bird.draw order (knight combos omitted; not a
    # column in the grid).
    if kfc and ghost and triple:
        img = parrot.get_kfc_ghost_hat_parrot(frame_idx, tilt)
    elif kfc and ghost:
        img = parrot.get_kfc_ghost_parrot(frame_idx, tilt)
    elif kfc and triple:
        img = parrot.get_kfc_hat_parrot(frame_idx, tilt)
    elif ghost and triple:
        img = parrot.get_ghost_hat_parrot(frame_idx, tilt)
    elif kfc:
        img = parrot.get_fried_parrot(frame_idx, tilt)
    elif ghost:
        img = parrot.get_ghost_parrot(frame_idx, tilt)
    elif triple:
        img = parrot.get_hat_parrot(frame_idx, tilt)
    elif grow:
        img = parrot.get_grow_parrot(frame_idx, tilt)
    elif lives_state == "last_life":
        img = parrot.get_hurt_parrot(frame_idx, tilt)
    elif lives_state == "first_hit":
        img = parrot.get_first_hit_parrot(frame_idx, tilt)
    else:
        img = parrot.get_parrot(frame_idx, tilt)

    # Skateboard: the cascade picks the parrot skin normally, but in-game
    # the helmet+board are drawn on top and the parcel is suppressed. For
    # the grid we show the underlying sprite (lives-state visible) so the
    # viewer understands which parrot skin is beneath the helmet.
    # Mark the cell with a label strip instead of trying to render the helmet
    # outside the Bird context. In practice on the grid the underbird skin is
    # visible — that's the accurate information.
    if skate:
        # Skateboard in-game: underlying parrot is the lives skin (cascade above).
        # Re-run without skateboard flag (already done — skate is only post-effect).
        pass  # img already set by lives cascade above

    # Poison tint (BLEND_RGB_MULT over the silhouette)
    if poison:
        img = parrot.tint_copy(img, (180, 225, 75), 0.75)

    # Grow upscale (combo grows use smoothscale)
    if grow and (kfc or ghost or triple):
        w, h = img.get_size()
        img = pygame.transform.smoothscale(img, (int(w * GROW_SCALE), int(h * GROW_SCALE)))

    # Shrink
    if shrink:
        sw, sh = img.get_size()
        img = pygame.transform.smoothscale(
            img, (max(1, int(sw * SHRINK_VAL)), max(1, int(sh * SHRINK_VAL))))

    # Ghost alpha fade
    if ghost:
        img = img.copy()
        img.set_alpha(ghost_alpha)

    return img


# ── Helpers ───────────────────────────────────────────────────────────────────

def fill_sky(surf: pygame.Surface):
    w, h = surf.get_size()
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (w - 1, y))


def make_font(size: int, bold: bool = False) -> pygame.font.Font:
    return pygame.font.SysFont("dejavusans,arial,sans", size, bold=bold)


def render_cell(lives_state: str, effect: str) -> pygame.Surface:
    cell = pygame.Surface((CELL_W, CELL_H))
    fill_sky(cell)

    img = _get_sprite(lives_state, effect)
    r = img.get_rect(center=(CELL_W // 2, 52))
    cell.blit(img, r.topleft)

    # Skateboard label strip
    if effect == "skateboard":
        font_tiny = make_font(8)
        note = font_tiny.render("+ board", True, (240, 240, 120))
        cell.blit(note, note.get_rect(centerx=CELL_W // 2, bottom=CELL_H - 4))

    return cell


# ── Canvas assembly ───────────────────────────────────────────────────────────

def main():
    n_rows = len(ROWS)
    n_cols = len(COLS)

    total_w = MARGIN + LABEL_W + n_cols * CELL_W + MARGIN
    total_h = MARGIN + HDR_H + n_rows * CELL_H + MARGIN

    canvas = pygame.Surface((total_w, total_h))
    canvas.fill(BG)

    font_title = make_font(13, bold=True)
    font_hdr   = make_font(10, bold=True)
    font_row   = make_font(10, bold=True)

    # Title
    title = font_title.render(
        "LIVES STATES  ×  POWER-UP APPEARANCES", True, TEXT_COL)
    canvas.blit(title, title.get_rect(
        centerx=total_w // 2, centery=MARGIN + HDR_H // 2))

    # Column headers
    hdr_y = MARGIN + HDR_H // 2
    for ci, (label, _) in enumerate(COLS):
        cx = MARGIN + LABEL_W + ci * CELL_W + CELL_W // 2
        lines = label.split("+")
        line_h = 13
        start_y = hdr_y - (len(lines) * line_h) // 2
        for i, ln in enumerate(lines):
            txt = font_hdr.render(ln, True, TEXT_COL)
            canvas.blit(txt, txt.get_rect(centerx=cx, top=start_y + i * line_h))

    # Rows
    for ri, (row_label, lives_state) in enumerate(ROWS):
        row_top = MARGIN + HDR_H + ri * CELL_H

        # Row label panel
        label_rect = pygame.Rect(MARGIN, row_top, LABEL_W, CELL_H)
        pygame.draw.rect(canvas, LABEL_BG, label_rect)
        lines = row_label.split("\n")
        line_h = 14
        cy = row_top + CELL_H // 2 - (len(lines) * line_h) // 2
        for ln in lines:
            col = DIM_COL if ln.startswith("(") else TEXT_COL
            txt = font_row.render(ln, True, col)
            canvas.blit(txt, txt.get_rect(centerx=MARGIN + LABEL_W // 2, top=cy))
            cy += line_h

        for ci, (_, effect) in enumerate(COLS):
            cell_x = MARGIN + LABEL_W + ci * CELL_W
            cell = render_cell(lives_state, effect)
            canvas.blit(cell, (cell_x, row_top))
            pygame.draw.rect(canvas, BG,
                             pygame.Rect(cell_x, row_top, CELL_W, CELL_H), 1)

    # Outer border
    pygame.draw.rect(canvas, (60, 65, 85), canvas.get_rect(), 2)

    # Save
    out_dir  = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "lives_powerup_grid.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {canvas.get_width()}×{canvas.get_height()} -> {out_path}")
    pygame.quit()


if __name__ == "__main__":
    main()
