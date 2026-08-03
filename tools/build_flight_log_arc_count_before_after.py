"""Build docs/flight_log_arc_v2/arc_count/before_after.png — r3 vs r4 side by side."""
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
GOLD_DIM = (180, 144, 48)
TEXT     = (220, 210, 190)
DIM_TEXT = (140, 135, 130)

PANEL_W  = 240
PANEL_H  = 426    # 240 / 360 * 640 = 426.67
GAP      = 16
MARGIN   = 20
HEADER_H = 44
FOOTER_H = 36

CANVAS_W = MARGIN + PANEL_W + GAP + PANEL_W + MARGIN
CANVAS_H = MARGIN + HEADER_H + PANEL_H + FOOTER_H + MARGIN

surf = pygame.Surface((CANVAS_W, CANVAS_H))
surf.fill(BG)

font_hdr = pygame.font.Font(FONT_PATH, 14)
font_lbl = pygame.font.Font(FONT_PATH, 9)
font_sub = pygame.font.Font(FONT_PATH, 8)
font_id  = pygame.font.Font(FONT_PATH, 22)

# Header
hdr = font_hdr.render("ARC COUNT  C  ·  INFORMATION ENRICHMENT PASS", True, GOLD)
surf.blit(hdr, ((CANVAS_W - hdr.get_width()) // 2,
                MARGIN + (HEADER_H - hdr.get_height()) // 2))

panels = [
    ("round_5.png", "C · BEFORE (R5)", "FLAT AHEAD + TEXT ABOVE",     "A"),
    ("round_6.png", "C · AFTER (R6)",  "DASHED FADE + BELOW + CLEAN", "B"),
]

for i, (fname, footer_top, footer_bot, letter) in enumerate(panels):
    px = MARGIN + i * (PANEL_W + GAP)
    py = MARGIN + HEADER_H
    fy = py + PANEL_H

    src = pygame.image.load(os.path.join(FEATURE_DIR, fname))
    panel = pygame.transform.smoothscale(src, (PANEL_W, PANEL_H))
    surf.blit(panel, (px, py))
    pygame.draw.rect(surf, GOLD_DIM, (px - 1, py - 1, PANEL_W + 2, PANEL_H + 2), 1)

    # Letter chip
    CHIP = 26
    cx, cy = px + 4, py + 4
    chip_bg = pygame.Surface((CHIP, CHIP), pygame.SRCALPHA)
    chip_bg.fill((8, 8, 20, 210))
    surf.blit(chip_bg, (cx, cy))
    pygame.draw.rect(surf, GOLD, (cx, cy, CHIP, CHIP), 1)
    id_s = font_id.render(letter, True, GOLD)
    surf.blit(id_s, (cx + (CHIP - id_s.get_width()) // 2,
                     cy + (CHIP - id_s.get_height()) // 2))

    # Footer — two lines
    lbl_top = font_lbl.render(footer_top, True, TEXT)
    lbl_bot = font_sub.render(footer_bot, True, DIM_TEXT)
    surf.blit(lbl_top, (px + (PANEL_W - lbl_top.get_width()) // 2,
                        fy + 6))
    surf.blit(lbl_bot, (px + (PANEL_W - lbl_bot.get_width()) // 2,
                        fy + 6 + lbl_top.get_height() + 2))

out = os.path.join(FEATURE_DIR, "before_after.png")
pygame.image.save(surf, out)
loaded = pygame.image.load(out)
print(f"saved {out}  {loaded.get_size()}")
