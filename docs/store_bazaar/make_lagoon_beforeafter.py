"""Assemble the lagoon polish-pass before/after figure.

Docs-only tooling: a single-row BEFORE (round_3) | AFTER (round_4) comparison of
the Lagoon Stilt-Market polish pass. Pure pygame, headless-safe.
"""
import os
import pygame

HERE = os.path.dirname(os.path.abspath(__file__))
CONCEPT = "lagoon_stilt"
COLS = [("round_3.png", "BEFORE"), ("round_4.png", "AFTER")]

PANEL_W, PANEL_H = 360, 640
PAD = 26
COLHDR = 46
GUTTER = 26
BG = (16, 14, 34)
GOLD = (244, 198, 96)
SUB = (170, 162, 196)
GREEN = (150, 214, 150)


def main():
    pygame.init()
    ncol = len(COLS)
    grid_w = ncol * PANEL_W + (ncol - 1) * GUTTER
    W = PAD + grid_w + PAD
    H = PAD + COLHDR + 8 + PANEL_H + PAD + 36
    canvas = pygame.Surface((W, H), pygame.SRCALPHA)
    canvas.fill(BG)

    pygame.draw.line(canvas, GOLD, (PAD, 10), (W - PAD, 10), 3)
    pygame.draw.line(canvas, GOLD, (PAD, H - 10), (W - PAD, H - 10), 3)

    col_font = pygame.font.SysFont("Arial", 26, bold=True)
    foot_font = pygame.font.SysFont("Arial", 17, bold=True)

    x0 = PAD
    py = PAD + COLHDR + 8
    for ci, (fname, clabel) in enumerate(COLS):
        px = x0 + ci * (PANEL_W + GUTTER)
        cx = px + PANEL_W // 2
        color = GREEN if clabel == "AFTER" else SUB
        cs = col_font.render(clabel, True, color)
        canvas.blit(cs, cs.get_rect(center=(cx, PAD + COLHDR // 2)))

        img = pygame.image.load(os.path.join(HERE, CONCEPT, fname))
        if img.get_size() != (PANEL_W, PANEL_H):
            img = pygame.transform.smoothscale(img, (PANEL_W, PANEL_H))
        frame_col = GREEN if clabel == "AFTER" else (120, 112, 150)
        pygame.draw.rect(canvas, frame_col,
                         pygame.Rect(px - 2, py - 2, PANEL_W + 4, PANEL_H + 4),
                         width=2, border_radius=6)
        canvas.blit(img, (px, py))

    foot = foot_font.render(
        "Skybit STORE — LAGOON STILT-MARKET polish pass: Pip airborne, premium "
        "water ripples, no white aura, PARCELS as a normal stall (design exploration only)",
        True, SUB)
    canvas.blit(foot, (PAD, H - 30))

    out = os.path.join(HERE, "compare_lagoon_polish.png")
    pygame.image.save(canvas, out)
    print("saved", out, canvas.get_size())


if __name__ == "__main__":
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    main()
