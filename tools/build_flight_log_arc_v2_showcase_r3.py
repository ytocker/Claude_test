"""Build docs/flight_log_arc_v2/showcase_r3.png — 5 round_3 extreme directions."""
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

pygame.display.init()
pygame.display.set_mode((1, 1))
pygame.font.init()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(ROOT, "game", "assets", "LiberationSans-Bold.ttf")
FEATURE_DIR = os.path.join(ROOT, "docs", "flight_log_arc_v2")

SLUGS = [
    "arc_clean",
    "arc_void",
    "arc_count",
    "arc_minimal",
    "arc_aspirational",
]
LABELS = {
    "arc_clean":        "A · THICK AMBER TRAIL",
    "arc_void":         "B · PITCH BLACK VOID",
    "arc_count":        "C · TARGET RINGS",
    "arc_minimal":      "D · SKELETON TRACE",
    "arc_aspirational": "E · SUNRISE RAYS",
}
IDS = ["A", "B", "C", "D", "E"]

BG       = (8, 8, 20)
GOLD     = (240, 192, 64)
GOLD_DIM = (180, 144, 48)
TEXT     = (220, 210, 190)

PANEL_W  = 200
PANEL_H  = 355
GAP      = 8
MARGIN   = 20
HEADER_H = 44
FOOTER_H = 32

N = len(SLUGS)
CANVAS_W = MARGIN + N * PANEL_W + (N - 1) * GAP + MARGIN
CANVAS_H = MARGIN + HEADER_H + PANEL_H + FOOTER_H + MARGIN

surf = pygame.Surface((CANVAS_W, CANVAS_H))
surf.fill(BG)

font_hdr = pygame.font.Font(FONT_PATH, 15)
font_lbl = pygame.font.Font(FONT_PATH, 10)
font_id  = pygame.font.Font(FONT_PATH, 26)

hdr = font_hdr.render("FLIGHT LOG ARC V2  ·  ROUND 3 — 5 EXTREME DIRECTIONS", True, GOLD)
surf.blit(hdr, ((CANVAS_W - hdr.get_width()) // 2,
                MARGIN + (HEADER_H - hdr.get_height()) // 2))

for i, slug in enumerate(SLUGS):
    px = MARGIN + i * (PANEL_W + GAP)
    py = MARGIN + HEADER_H
    fy = py + PANEL_H
    letter = IDS[i]

    src = pygame.image.load(os.path.join(FEATURE_DIR, slug, "round_3.png"))
    panel = pygame.transform.smoothscale(src, (PANEL_W, PANEL_H))
    surf.blit(panel, (px, py))
    pygame.draw.rect(surf, GOLD_DIM, (px - 1, py - 1, PANEL_W + 2, PANEL_H + 2), 1)

    # ID chip
    CHIP = 28
    cx, cy = px + 4, py + 4
    chip = pygame.Surface((CHIP, CHIP), pygame.SRCALPHA)
    chip.fill((8, 8, 20, 200))
    surf.blit(chip, (cx, cy))
    pygame.draw.rect(surf, GOLD, (cx, cy, CHIP, CHIP), 1)
    id_s = font_id.render(letter, True, GOLD)
    surf.blit(id_s, (cx + (CHIP - id_s.get_width()) // 2,
                     cy + (CHIP - id_s.get_height()) // 2))

    # Footer
    lbl = font_lbl.render(LABELS[slug], True, TEXT)
    surf.blit(lbl, (px + (PANEL_W - lbl.get_width()) // 2,
                    fy + (FOOTER_H - lbl.get_height()) // 2))

out = os.path.join(FEATURE_DIR, "showcase_r3.png")
pygame.image.save(surf, out)
loaded = pygame.image.load(out)
print(f"saved {out}  {loaded.get_size()}")
