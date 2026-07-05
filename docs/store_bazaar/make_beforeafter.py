"""Assemble the upgrade before/after figure for concepts #1 and #5.

Docs-only tooling: a 2x2 grid — rows are the two concepts, columns are BEFORE
(the prior final, before.png) and AFTER (the upgraded round_3.png). Pure pygame,
headless-safe.
"""
import os
import pygame

HERE = os.path.dirname(os.path.abspath(__file__))

# (dir, display title)
ROWS = [
    ("sky_bazaar",   "FLOATING SKY-BAZAAR"),
    ("lagoon_stilt", "LAGOON STILT-MARKET"),
]
COLS = [("before.png", "BEFORE"), ("round_3.png", "AFTER")]

PANEL_W, PANEL_H = 360, 640
PAD = 26
COLHDR = 46       # column-header band height (top)
ROWLBL = 30       # row-label strip under each panel
GUTTER = 26
BG = (16, 14, 34)
BAND = (26, 22, 52)
GOLD = (244, 198, 96)
CREAM = (245, 232, 206)
SUB = (170, 162, 196)
GREEN = (150, 214, 150)


def main():
    pygame.init()
    ncol, nrow = len(COLS), len(ROWS)
    grid_w = ncol * PANEL_W + (ncol - 1) * GUTTER
    grid_h = nrow * (PANEL_H + ROWLBL) + (nrow - 1) * GUTTER
    W = PAD + grid_w + PAD
    H = PAD + COLHDR + 8 + grid_h + PAD + 36   # +36 footer
    canvas = pygame.Surface((W, H), pygame.SRCALPHA)
    canvas.fill(BG)

    pygame.draw.line(canvas, GOLD, (PAD, 10), (W - PAD, 10), 3)
    pygame.draw.line(canvas, GOLD, (PAD, H - 10), (W - PAD, H - 10), 3)

    title_font = pygame.font.SysFont("Arial", 22, bold=True)
    col_font = pygame.font.SysFont("Arial", 26, bold=True)
    foot_font = pygame.font.SysFont("Arial", 17, bold=True)

    x0 = PAD
    y0 = PAD + COLHDR + 8

    # column headers
    for ci, (_, clabel) in enumerate(COLS):
        cx = x0 + ci * (PANEL_W + GUTTER) + PANEL_W // 2
        color = GREEN if clabel == "AFTER" else SUB
        cs = col_font.render(clabel, True, color)
        canvas.blit(cs, cs.get_rect(center=(cx, PAD + COLHDR // 2)))

    for ri, (d, title) in enumerate(ROWS):
        py = y0 + ri * (PANEL_H + ROWLBL + GUTTER)
        for ci, (fname, clabel) in enumerate(COLS):
            px = x0 + ci * (PANEL_W + GUTTER)
            img = pygame.image.load(os.path.join(HERE, d, fname))
            if img.get_size() != (PANEL_W, PANEL_H):
                img = pygame.transform.smoothscale(img, (PANEL_W, PANEL_H))
            frame_col = GREEN if clabel == "AFTER" else (120, 112, 150)
            pygame.draw.rect(canvas, frame_col,
                             pygame.Rect(px - 2, py - 2, PANEL_W + 4, PANEL_H + 4),
                             width=2, border_radius=6)
            canvas.blit(img, (px, py))
        # row label strip spanning both panels
        lbl = pygame.Rect(x0, py + PANEL_H + 6, grid_w, ROWLBL - 6)
        pygame.draw.rect(canvas, BAND, lbl, border_radius=8)
        ts = title_font.render(f"{ri + 1}.  {title}", True, CREAM)
        canvas.blit(ts, (lbl.x + 14, lbl.y + (lbl.h - ts.get_height()) // 2))

    foot = foot_font.render(
        "Skybit STORE bazaar-landing — upgrade pass (design exploration only; "
        "not yet wired into the game)", True, SUB)
    canvas.blit(foot, (PAD, H - 30))

    out = os.path.join(HERE, "compare_upgrade.png")
    pygame.image.save(canvas, out)
    pygame.image.save(pygame.transform.smoothscale(canvas, (W // 2, H // 2)),
                      os.path.join(HERE, "compare_upgrade@half.png"))
    print("saved", out, canvas.get_size())


if __name__ == "__main__":
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    main()
