"""Build docs/flight_log_arc_v2/arc_count/showcase.png — 5 concept round-2 panels side by side."""
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

pygame.display.init()
pygame.display.set_mode((1, 1))
pygame.font.init()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(ROOT, "game", "assets", "LiberationSans-Bold.ttf")
FEATURE_DIR = os.path.join(ROOT, "docs", "flight_log_arc_v2", "arc_count")

BG       = (8, 8, 20)
GOLD     = (240, 192, 64)
GOLD_DIM = (160, 128, 42)
TEXT     = (220, 210, 190)
DIM_TEXT = (130, 125, 120)

PANEL_W  = 200
PANEL_H  = 355
GAP      = 8
MARGIN   = 20
HEADER_H = 44
FOOTER_H = 32

SLUGS   = ["monolith", "codex", "broadcast", "medallion", "epitaph"]
LABELS  = ["A", "B", "C", "D", "E"]
VERDICTS = ["ITERATE→FINAL"] * 5

N = len(SLUGS)
CANVAS_W = MARGIN + N * PANEL_W + (N - 1) * GAP + MARGIN
CANVAS_H = MARGIN + HEADER_H + PANEL_H + FOOTER_H + MARGIN

surf = pygame.Surface((CANVAS_W, CANVAS_H))
surf.fill(BG)

font_hdr = pygame.font.Font(FONT_PATH, 13)
font_lbl = pygame.font.Font(FONT_PATH, 9)
font_sub = pygame.font.Font(FONT_PATH, 7)
font_id  = pygame.font.Font(FONT_PATH, 18)

# Header
hdr = font_hdr.render("FLIGHT LOG  ·  ARC COUNT  ·  5 CONCEPTS  ·  ROUND 2", True, GOLD)
surf.blit(hdr, ((CANVAS_W - hdr.get_width()) // 2,
                MARGIN + (HEADER_H - hdr.get_height()) // 2))

for i, (slug, label, verdict) in enumerate(zip(SLUGS, LABELS, VERDICTS)):
    px = MARGIN + i * (PANEL_W + GAP)
    py = MARGIN + HEADER_H
    fy = py + PANEL_H

    src_path = os.path.join(FEATURE_DIR, slug, "round_2.png")
    src = pygame.image.load(src_path)
    panel = pygame.transform.smoothscale(src, (PANEL_W, PANEL_H))
    surf.blit(panel, (px, py))
    pygame.draw.rect(surf, GOLD_DIM, (px - 1, py - 1, PANEL_W + 2, PANEL_H + 2), 1)

    # Letter chip
    CHIP = 22
    cx, cy = px + 4, py + 4
    chip_bg = pygame.Surface((CHIP, CHIP), pygame.SRCALPHA)
    chip_bg.fill((8, 8, 20, 200))
    surf.blit(chip_bg, (cx, cy))
    pygame.draw.rect(surf, GOLD, (cx, cy, CHIP, CHIP), 1)
    id_s = font_id.render(label, True, GOLD)
    surf.blit(id_s, (cx + (CHIP - id_s.get_width()) // 2,
                     cy + (CHIP - id_s.get_height()) // 2))

    # Footer
    lbl_top = font_lbl.render(slug.upper(), True, TEXT)
    lbl_bot = font_sub.render(verdict, True, DIM_TEXT)
    surf.blit(lbl_top, (px + (PANEL_W - lbl_top.get_width()) // 2, fy + 6))
    surf.blit(lbl_bot, (px + (PANEL_W - lbl_bot.get_width()) // 2,
                        fy + 6 + lbl_top.get_height() + 2))

out = os.path.join(FEATURE_DIR, "showcase.png")
pygame.image.save(surf, out)
loaded = pygame.image.load(out)
print(f"saved {out}  {loaded.get_size()}")
