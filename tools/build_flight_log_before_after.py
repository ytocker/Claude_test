"""Build docs/flight_log_progress/before_after_v1.png —
before/after comparison for flight-log concepts B, D, E.

BEFORE: extracted from the original review sheets (round_2.png)
AFTER:  clean Skybit-bg enhanced screens (round_3.png)
"""
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

pygame.display.init()
pygame.display.set_mode((1, 1))
pygame.font.init()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(ROOT, "game", "assets", "LiberationSans-Bold.ttf")
FEATURE_DIR = os.path.join(ROOT, "docs", "flight_log_progress")

# Crop offsets into each round_2 review sheet: (x, y, x+360, y+640)
BEFORE_CROPS = {
    "expedition_route": (24,  68, 384, 708),
    "flight_strip":     (16,  38, 376, 678),
    "sun_arc":          (40, 112, 400, 752),
}

ROWS = [
    ("B", "expedition_route", "B · EXPEDITION ROUTE"),
    ("D", "flight_strip",     "D · FLIGHT STRIP"),
    ("E", "sun_arc",          "E · SUN ARC"),
]

BG = (8, 8, 20)
GOLD = (240, 192, 64)
GOLD_DIM = (200, 160, 50)
TEXT_LIGHT = (220, 210, 190)

PANEL_W = 200
PANEL_H = 355
GAP = 8
MARGIN = 20
ROW_LABEL_H = 28
FOOTER_H = 24
ROW_GAP = 16
COL_HDR_H = 40

N_ROWS = len(ROWS)
ROW_BLOCK_H = ROW_LABEL_H + PANEL_H + FOOTER_H + ROW_GAP
CANVAS_W = MARGIN + PANEL_W + GAP + PANEL_W + MARGIN
CANVAS_H = MARGIN + COL_HDR_H + N_ROWS * ROW_BLOCK_H + MARGIN

surf = pygame.Surface((CANVAS_W, CANVAS_H))
surf.fill(BG)

font_hdr  = pygame.font.Font(FONT_PATH, 14)
font_lbl  = pygame.font.Font(FONT_PATH, 11)
font_col  = pygame.font.Font(FONT_PATH, 13)
font_foot = pygame.font.Font(FONT_PATH, 9)

# Column headers
col_before_cx = MARGIN + PANEL_W // 2
col_after_cx  = MARGIN + PANEL_W + GAP + PANEL_W // 2
hdr_y = MARGIN + (COL_HDR_H - font_col.get_height()) // 2

for label, cx in [("BEFORE", col_before_cx), ("AFTER", col_after_cx)]:
    t = font_col.render(label, True, GOLD)
    surf.blit(t, (cx - t.get_width() // 2, hdr_y))

# Divider under column headers
pygame.draw.line(surf, GOLD_DIM,
                 (MARGIN, MARGIN + COL_HDR_H - 1),
                 (CANVAS_W - MARGIN, MARGIN + COL_HDR_H - 1), 1)

for row_i, (letter, slug, row_label) in enumerate(ROWS):
    row_top = MARGIN + COL_HDR_H + row_i * ROW_BLOCK_H

    # Row label chip
    chip_surf = font_lbl.render(row_label, True, GOLD)
    chip_x = MARGIN
    chip_y = row_top + (ROW_LABEL_H - chip_surf.get_height()) // 2
    surf.blit(chip_surf, (chip_x, chip_y))

    panel_y = row_top + ROW_LABEL_H
    footer_y = panel_y + PANEL_H

    for col_i, kind in enumerate(["before", "after"]):
        panel_x = MARGIN + col_i * (PANEL_W + GAP)

        if kind == "before":
            src_path = os.path.join(FEATURE_DIR, slug, "round_2.png")
            src = pygame.image.load(src_path)
            cx0, cy0, cx1, cy1 = BEFORE_CROPS[slug]
            cw, ch = cx1 - cx0, cy1 - cy0
            crop = pygame.Surface((cw, ch))
            crop.blit(src, (0, 0), (cx0, cy0, cw, ch))
            panel = pygame.transform.smoothscale(crop, (PANEL_W, PANEL_H))
        else:
            src_path = os.path.join(FEATURE_DIR, slug, "round_3.png")
            src = pygame.image.load(src_path)
            sw, sh = src.get_size()
            # round_3 is clean 360×640; scale to panel
            panel = pygame.transform.smoothscale(src, (PANEL_W, PANEL_H))

        surf.blit(panel, (panel_x, panel_y))
        pygame.draw.rect(surf, GOLD_DIM,
                         (panel_x - 1, panel_y - 1, PANEL_W + 2, PANEL_H + 2), 1)

        # Footer label
        foot_text = kind.upper()
        ft = font_foot.render(foot_text, True, TEXT_LIGHT)
        surf.blit(ft, (panel_x + (PANEL_W - ft.get_width()) // 2,
                       footer_y + (FOOTER_H - ft.get_height()) // 2))

    # Row separator
    sep_y = footer_y + FOOTER_H + ROW_GAP // 2
    if row_i < N_ROWS - 1:
        pygame.draw.line(surf, (30, 30, 50),
                         (MARGIN, sep_y), (CANVAS_W - MARGIN, sep_y), 1)

out = os.path.join(FEATURE_DIR, "before_after_v1.png")
pygame.image.save(surf, out)
loaded = pygame.image.load(out)
print(f"saved {out}  {loaded.get_size()}")
