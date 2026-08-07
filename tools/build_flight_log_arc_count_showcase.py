"""Build docs/flight_log_arc_v2/arc_count/showcase.png — BEFORE + 5 concept round-2 panels."""
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

BG        = (8, 8, 20)
GOLD      = (240, 192, 64)
GOLD_DIM  = (160, 128, 42)
SLATE_DIM = (80, 84, 100)
TEXT      = (220, 210, 190)
DIM_TEXT  = (130, 125, 120)

PANEL_W  = 200
PANEL_H  = 355
GAP      = 8
BEFORE_GAP = 20   # wider gap separating BEFORE from concepts
MARGIN   = 20
HEADER_H = 44
FOOTER_H = 32

CONCEPTS = ["monolith", "codex", "broadcast", "medallion", "epitaph"]
LABELS   = ["A", "B", "C", "D", "E"]
VERDICTS = ["ITERATE→FINAL"] * 5

N_TOTAL  = 1 + len(CONCEPTS)
CANVAS_W = (MARGIN + PANEL_W + BEFORE_GAP
            + len(CONCEPTS) * PANEL_W + (len(CONCEPTS) - 1) * GAP + MARGIN)
CANVAS_H = MARGIN + HEADER_H + PANEL_H + FOOTER_H + MARGIN

surf = pygame.Surface((CANVAS_W, CANVAS_H))
surf.fill(BG)

font_hdr  = pygame.font.Font(FONT_PATH, 13)
font_lbl  = pygame.font.Font(FONT_PATH, 9)
font_sub  = pygame.font.Font(FONT_PATH, 7)
font_id   = pygame.font.Font(FONT_PATH, 18)
font_bef  = pygame.font.Font(FONT_PATH, 8)

# Header
hdr = font_hdr.render(
    "FLIGHT LOG  ·  ARC COUNT  ·  ORIGINAL vs 5 CONCEPTS  ·  ROUND 2", True, GOLD)
surf.blit(hdr, ((CANVAS_W - hdr.get_width()) // 2,
                MARGIN + (HEADER_H - hdr.get_height()) // 2))

py = MARGIN + HEADER_H

# --- BEFORE panel ---
bx = MARGIN
by = py
bfy = by + PANEL_H

before_src = pygame.image.load(os.path.join(FEATURE_DIR, "round_7.png"))
before_panel = pygame.transform.smoothscale(before_src, (PANEL_W, PANEL_H))
surf.blit(before_panel, (bx, by))
# Muted slate border to distinguish it from concept panels
pygame.draw.rect(surf, SLATE_DIM, (bx - 1, by - 1, PANEL_W + 2, PANEL_H + 2), 1)

# "BEFORE" chip
CHIP_W, CHIP_H = 44, 16
cxb, cyb = bx + 4, by + 4
chip_bg = pygame.Surface((CHIP_W, CHIP_H), pygame.SRCALPHA)
chip_bg.fill((8, 8, 20, 200))
surf.blit(chip_bg, (cxb, cyb))
pygame.draw.rect(surf, SLATE_DIM, (cxb, cyb, CHIP_W, CHIP_H), 1)
bef_s = font_bef.render("BEFORE", True, SLATE_DIM)
surf.blit(bef_s, (cxb + (CHIP_W - bef_s.get_width()) // 2,
                  cyb + (CHIP_H - bef_s.get_height()) // 2))

# Footer
lbl_top = font_lbl.render("ORIGINAL", True, DIM_TEXT)
lbl_bot = font_sub.render("R7 · UNMODIFIED", True, (90, 88, 100))
surf.blit(lbl_top, (bx + (PANEL_W - lbl_top.get_width()) // 2, bfy + 6))
surf.blit(lbl_bot, (bx + (PANEL_W - lbl_bot.get_width()) // 2,
                    bfy + 6 + lbl_top.get_height() + 2))

# Thin divider line between BEFORE and concepts
div_x = bx + PANEL_W + BEFORE_GAP // 2
pygame.draw.line(surf, (40, 42, 58), (div_x, py), (div_x, py + PANEL_H), 1)

# --- Concept panels ---
concepts_x0 = MARGIN + PANEL_W + BEFORE_GAP

for i, (slug, label, verdict) in enumerate(zip(CONCEPTS, LABELS, VERDICTS)):
    px = concepts_x0 + i * (PANEL_W + GAP)
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
