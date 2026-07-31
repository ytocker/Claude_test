"""Build docs/flight_log_progress/showcase.png — Phase 5 design loop showcase."""
import os, math
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import pygame

pygame.display.init()
pygame.display.set_mode((1, 1))
pygame.font.init()

FONT_PATH = 'game/assets/LiberationSans-Bold.ttf'

SLUGS = [
    'sky_ruler',
    'expedition_route',
    'runway_view',
    'flight_strip',
    'sun_arc',
]

LABELS = {
    'sky_ruler':        'SKY RULER',
    'expedition_route': 'EXPEDITION',
    'runway_view':      'RUNWAY',
    'flight_strip':     'FLIGHT STRIP',
    'sun_arc':          'SUN ARC',
}

IDS = ['A', 'B', 'C', 'D', 'E']

# Layout constants
BG        = (8, 8, 20)
PANEL_W   = 200
PANEL_H   = 355
GAP       = 8
MARGIN    = 20
HEADER_H  = 40
FOOTER_H  = 32

N = len(SLUGS)
CANVAS_W = MARGIN + N * PANEL_W + (N - 1) * GAP + MARGIN
CANVAS_H = MARGIN + HEADER_H + PANEL_H + FOOTER_H + MARGIN

surf = pygame.Surface((CANVAS_W, CANVAS_H))
surf.fill(BG)

# ── header ──────────────────────────────────────────────────────────────────
font_hdr = pygame.font.Font(FONT_PATH, 18)
font_lbl = pygame.font.Font(FONT_PATH, 12)
font_id  = pygame.font.Font(FONT_PATH, 30)

hdr_text = font_hdr.render('FLIGHT LOG PROGRESS · ROUND 2 FINALS', True, (240, 192, 64))
hdr_x = (CANVAS_W - hdr_text.get_width()) // 2
hdr_y = MARGIN + (HEADER_H - hdr_text.get_height()) // 2
surf.blit(hdr_text, (hdr_x, hdr_y))

# ── panels ───────────────────────────────────────────────────────────────────
GOLD = (200, 160, 50)

for i, slug in enumerate(SLUGS):
    panel_x = MARGIN + i * (PANEL_W + GAP)
    panel_y = MARGIN + HEADER_H
    footer_y = panel_y + PANEL_H
    letter = IDS[i]

    # Load the source image and crop the primary 360×640 game frame
    src = pygame.image.load(f'docs/flight_log_progress/{slug}/round_2.png')
    w, h = src.get_size()
    crop_w, crop_h = min(w, 360), min(h, 640)
    crop = pygame.Surface((crop_w, crop_h))
    crop.blit(src, (0, 0), (0, 0, crop_w, crop_h))

    # Scale to 200×355
    panel = pygame.transform.smoothscale(crop, (PANEL_W, PANEL_H))
    surf.blit(panel, (panel_x, panel_y))

    # 1px gold border around panel
    pygame.draw.rect(surf, GOLD, (panel_x - 1, panel_y - 1, PANEL_W + 2, PANEL_H + 2), 1)

    # ID letter chip — dark background square in top-left corner of panel
    CHIP = 32
    chip_x, chip_y = panel_x + 4, panel_y + 4
    chip_surf = pygame.Surface((CHIP, CHIP))
    chip_surf.fill((8, 8, 20))
    chip_surf.set_alpha(200)
    surf.blit(chip_surf, (chip_x, chip_y))
    pygame.draw.rect(surf, GOLD, (chip_x, chip_y, CHIP, CHIP), 1)

    id_surf = font_id.render(letter, True, (240, 192, 64))
    id_x = chip_x + (CHIP - id_surf.get_width()) // 2
    id_y = chip_y + (CHIP - id_surf.get_height()) // 2
    surf.blit(id_surf, (id_x, id_y))

    # Footer: "A · SKY RULER" on one line
    label = f'{letter} · {LABELS[slug]}'
    lbl_surf = font_lbl.render(label, True, (220, 210, 190))
    lbl_x = panel_x + (PANEL_W - lbl_surf.get_width()) // 2
    lbl_y = footer_y + (FOOTER_H - lbl_surf.get_height()) // 2
    surf.blit(lbl_surf, (lbl_x, lbl_y))

# ── save ──────────────────────────────────────────────────────────────────────
out = 'docs/flight_log_progress/showcase.png'
pygame.image.save(surf, out)
s = pygame.image.load(out)
print(f'Saved {out} {s.get_size()}')
# sample pixels to verify
for x in [100, 300, 500, 700, 900]:
    print(f'  x={x}: {s.get_at((x, MARGIN + HEADER_H + PANEL_H // 2))[:3]}')
