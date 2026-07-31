"""Build docs/flight_log_screen/showcase.png — round-2 finals for the 5
flight-log screen concepts.

Panel order (left → right = A → E):
  A  star_chart     STAR CHART
  B  flight_logbook FLIGHT LOG
  C  pillar_cairn   PILLAR CAIRN
  D  black_box      BLACK BOX
  E  roost_return   ROOST RETURN
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
FEATURE_DIR = os.path.join(ROOT, "docs", "flight_log_screen")

SLUGS = ["star_chart", "flight_logbook", "pillar_cairn", "black_box", "roost_return"]
LABELS = {
    "star_chart":     "STAR CHART",
    "flight_logbook": "FLIGHT LOG",
    "pillar_cairn":   "PILLAR CAIRN",
    "black_box":      "BLACK BOX",
    "roost_return":   "ROOST RETURN",
}
IDS = ["A", "B", "C", "D", "E"]

BG = (8, 8, 20)
GOLD = (240, 192, 64)
GOLD_DIM = (200, 160, 50)
PANEL_W = 200
PANEL_H = 355
GAP = 8
MARGIN = 20
HEADER_H = 40
FOOTER_H = 32

N = len(SLUGS)
CANVAS_W = MARGIN + N * PANEL_W + (N - 1) * GAP + MARGIN
CANVAS_H = MARGIN + HEADER_H + PANEL_H + FOOTER_H + MARGIN

surf = pygame.Surface((CANVAS_W, CANVAS_H))
surf.fill(BG)

font_hdr = pygame.font.Font(FONT_PATH, 16)
font_lbl = pygame.font.Font(FONT_PATH, 11)
font_id = pygame.font.Font(FONT_PATH, 28)

hdr_text = font_hdr.render(
    "FLIGHT LOG SCREEN  ·  ROUND 2 FINALS", True, GOLD)
hdr_x = (CANVAS_W - hdr_text.get_width()) // 2
hdr_y = MARGIN + (HEADER_H - hdr_text.get_height()) // 2
surf.blit(hdr_text, (hdr_x, hdr_y))

for i, slug in enumerate(SLUGS):
    panel_x = MARGIN + i * (PANEL_W + GAP)
    panel_y = MARGIN + HEADER_H
    footer_y = panel_y + PANEL_H
    letter = IDS[i]

    src_path = os.path.join(FEATURE_DIR, slug, "round_2.png")
    src = pygame.image.load(src_path)
    sw, sh = src.get_size()
    # The sheet may be wider than one 360×640 panel; crop to the first panel.
    crop_w = min(sw, 360)
    crop_h = min(sh, 640)
    crop = pygame.Surface((crop_w, crop_h))
    crop.blit(src, (0, 0), (0, 0, crop_w, crop_h))

    panel = pygame.transform.smoothscale(crop, (PANEL_W, PANEL_H))
    surf.blit(panel, (panel_x, panel_y))
    pygame.draw.rect(surf, GOLD_DIM,
                     (panel_x - 1, panel_y - 1, PANEL_W + 2, PANEL_H + 2), 1)

    # ID chip
    CHIP = 30
    chip_x, chip_y = panel_x + 4, panel_y + 4
    chip_bg = pygame.Surface((CHIP, CHIP), pygame.SRCALPHA)
    chip_bg.fill((8, 8, 20, 200))
    surf.blit(chip_bg, (chip_x, chip_y))
    pygame.draw.rect(surf, GOLD, (chip_x, chip_y, CHIP, CHIP), 1)

    id_surf = font_id.render(letter, True, GOLD)
    surf.blit(id_surf, (chip_x + (CHIP - id_surf.get_width()) // 2,
                        chip_y + (CHIP - id_surf.get_height()) // 2))

    # Footer
    label = f"{letter}  ·  {LABELS[slug]}"
    lbl_surf = font_lbl.render(label, True, (220, 210, 190))
    surf.blit(lbl_surf, (panel_x + (PANEL_W - lbl_surf.get_width()) // 2,
                         footer_y + (FOOTER_H - lbl_surf.get_height()) // 2))

out = os.path.join(FEATURE_DIR, "showcase.png")
pygame.image.save(surf, out)
loaded = pygame.image.load(out)
print(f"saved {out}  {loaded.get_size()}")
for x in [100, 300, 500, 700, 900]:
    y = MARGIN + HEADER_H + PANEL_H // 2
    print(f"  x={x:4d} y={y}: {loaded.get_at((x, y))[:3]}")
