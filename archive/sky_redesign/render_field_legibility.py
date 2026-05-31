"""
SHIP-READY gate for the sky color-field finalists: a sky is only good if the
gameplay layer pops against it. Composites a green pillar pair, the RED hero
parrot silhouette, and white "9999" HUD score over each finalist at three
representative phases (DAY / SUNSET / NIGHT) — the three hardest contrast cases.

Run:
    python archive/sky_redesign/render_field_legibility.py [round_N]
Writes docs/sky_redesign/<round>.png  (default: field_legibility.png)
"""
import os, sys, pathlib, math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game import biome as _biome
from archive.sky_redesign.field_variants import VARIANTS, VARIANT_NAMES, VARIANT_NOTES

W, H, GROUND_Y = 360, 640, 595
PIPE_W = 58

PHASES = [("DAY", 0.00), ("SUNSET", 0.32), ("NIGHT", 0.62)]

TILE_W, TILE_H = 240, 426
PAD = 8
LABEL_L = 150
LABEL_T = 28

PIPE_MID = (45, 185, 45)
PIPE_DARK = (20, 100, 20)
PIPE_HILIGHT = (110, 240, 110)
BIRD_RED = (240, 55, 55)
BIRD_RED_D = (170, 25, 25)
BIRD_BELLY = (255, 170, 50)


def _pillar(surf, x, gap_y, gap):
    """A simple green pillar pair (top + bottom) with a lighter inner edge —
    enough to judge whether the green silhouette separates from the sky."""
    top_h = gap_y - gap // 2
    bot_y = gap_y + gap // 2
    for (y0, h) in ((0, top_h), (bot_y, GROUND_Y - bot_y)):
        if h <= 0:
            continue
        for i in range(PIPE_W):
            t = i / (PIPE_W - 1)
            if t < 0.18:
                c = PIPE_HILIGHT
            elif t < 0.55:
                c = PIPE_MID
            else:
                c = PIPE_DARK
            pygame.draw.line(surf, c, (x + i, y0), (x + i, y0 + h))
        cap = pygame.Rect(x - 5, (y0 if y0 == 0 else y0) + (h - 18 if y0 == 0 else 0), PIPE_W + 10, 18)
        if y0 == 0:
            cap = pygame.Rect(x - 5, top_h - 18, PIPE_W + 10, 18)
        else:
            cap = pygame.Rect(x - 5, bot_y, PIPE_W + 10, 18)
        pygame.draw.rect(surf, PIPE_MID, cap, border_radius=5)
        pygame.draw.rect(surf, PIPE_DARK, cap, width=2, border_radius=5)


def _parrot(surf, cx, cy):
    """A compact red-parrot silhouette (body + belly + wing + beak) at hero
    scale — the single most important thing that must pop against any sky."""
    pygame.draw.ellipse(surf, BIRD_RED, (cx - 18, cy - 14, 36, 28))
    pygame.draw.ellipse(surf, BIRD_BELLY, (cx - 10, cy - 2, 20, 16))
    pygame.draw.ellipse(surf, BIRD_RED_D, (cx - 6, cy - 10, 22, 16))
    pygame.draw.polygon(surf, (255, 185, 0),
                        [(cx + 16, cy - 2), (cx + 28, cy + 1), (cx + 16, cy + 5)])
    pygame.draw.circle(surf, (255, 255, 255), (cx + 9, cy - 6), 3)
    pygame.draw.circle(surf, (10, 10, 10), (cx + 10, cy - 6), 1)


def _score(surf):
    font = pygame.font.SysFont("dejavusans", 52, bold=True)
    txt = font.render("9999", True, (255, 255, 255))
    sh = font.render("9999", True, (0, 0, 0))
    x = W // 2 - txt.get_width() // 2
    surf.blit(sh, (x + 2, 30))
    surf.blit(txt, (x, 28))


def render_tile(name, phase):
    palette = _biome.palette_for_phase(phase)
    tile = pygame.Surface((W, H))
    tile.blit(VARIANTS[name](W, GROUND_Y, palette), (0, 0))
    # faint ground so pillars have a base
    pygame.draw.rect(tile, (28, 30, 36), (0, GROUND_Y, W, H - GROUND_Y))
    _pillar(tile, int(W * 0.58), 300, 150)
    _parrot(tile, int(W * 0.34), 300)
    _score(tile)
    return pygame.transform.smoothscale(tile, (TILE_W, TILE_H))


def main():
    round_name = sys.argv[1] if len(sys.argv) > 1 else "field_legibility"
    cols, rows = len(PHASES), len(VARIANT_NAMES)
    sheet_w = LABEL_L + cols * (TILE_W + PAD) + PAD
    sheet_h = LABEL_T + rows * (TILE_H + PAD) + PAD
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 18, 22))
    font = pygame.font.SysFont("dejavusans", 15, bold=True)

    for ci, (pname, _) in enumerate(PHASES):
        x = LABEL_L + ci * (TILE_W + PAD) + TILE_W // 2
        lab = font.render(pname, True, (230, 230, 235))
        sheet.blit(lab, (x - lab.get_width() // 2, 6))
    for ri, name in enumerate(VARIANT_NAMES):
        y = LABEL_T + ri * (TILE_H + PAD)
        lab = font.render(name, True, (235, 235, 240))
        sheet.blit(lab, (8, y + 8))
        for ci, (_, phase) in enumerate(PHASES):
            x = LABEL_L + ci * (TILE_W + PAD) + PAD
            sheet.blit(render_tile(name, phase), (x, y))

    out_dir = pathlib.Path(__file__).resolve().parent.parent.parent / "docs" / "sky_redesign"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{round_name}.png"
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
