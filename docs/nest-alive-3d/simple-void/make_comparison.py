"""Compose the simple-void v3 review sheet (2x2 BEFORE/AFTER grid + 8x zoom strip).

Nearest-neighbour scaling throughout: this is a pixel-art slot, so smoothing
would hide exactly the twig/rim detail the review is about.
"""
import os, sys

os.environ.setdefault('SDL_VIDEODRIVER', 'offscreen')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
sys.path.insert(0, '/home/user/skybit')

import pygame
pygame.init()

sys.path.insert(0, '/home/user/skybit/docs/nest-alive-3d/simple-void')
import render as R

SKY = R.SKY
W, H = 62, 130
CY = 73

BG      = (8, 8, 20)
HAIRUNE = (48, 48, 62)
MUTED   = (196, 200, 214)
TITLE_C = (238, 240, 250)

GRID_ZOOM = 4
ZOOM      = 8
CROP      = pygame.Rect(5, 57, 52, 56)
GAP       = 10
MARGIN    = 20
GUTTER    = 130

FONT_PATH = '/home/user/skybit/game/assets/LiberationSans-Bold.ttf'
f_title = pygame.font.Font(FONT_PATH, 30)
f_head  = pygame.font.Font(FONT_PATH, 22)
f_row   = pygame.font.Font(FONT_PATH, 20)
f_tile  = pygame.font.Font(FONT_PATH, 19)


def render_panel(fn, alive):
    surf = pygame.Surface((W, H))
    surf.fill(SKY)
    fn(surf, CY, alive)
    return surf


before_in  = render_panel(R.draw_slot_before, True)
after_in   = render_panel(R.draw_slot_after,  True)
before_out = render_panel(R.draw_slot_before, False)
after_out  = render_panel(R.draw_slot_after,  False)

CELL_W, CELL_H = W * GRID_ZOOM, H * GRID_ZOOM
TILE_W, TILE_H = CROP.w * ZOOM, CROP.h * ZOOM

grid_w  = CELL_W * 2 + GAP
strip_w = TILE_W * 4 + GAP * 3

title_y  = MARGIN
head_y   = title_y + 46
grid_y   = head_y + 34
grid_h   = CELL_H * 2 + GAP
strip_y  = grid_y + grid_h + 46
label_y  = strip_y + TILE_H + 8

sheet_w = max(GUTTER + grid_w, strip_w) + MARGIN * 2
sheet_h = label_y + 26 + MARGIN

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)


def centred(text, font, col, cx, y):
    img = font.render(text, True, col)
    sheet.blit(img, (cx - img.get_width() // 2, y))


def right_aligned(text, font, col, rx, cy):
    img = font.render(text, True, col)
    sheet.blit(img, (rx - img.get_width(), cy - img.get_height() // 2))


centred('simple-void · v3', f_title, TITLE_C, sheet_w // 2, title_y)

grid_x = (sheet_w - grid_w + GUTTER) // 2
if grid_x < MARGIN + GUTTER:
    grid_x = MARGIN + GUTTER

panels = ((before_in, after_in), (before_out, after_out))
row_names = ('parrot IN', 'parrot OUT')

for ri, row in enumerate(panels):
    for ci, panel in enumerate(row):
        x = grid_x + ci * (CELL_W + GAP)
        y = grid_y + ri * (CELL_H + GAP)
        sheet.blit(pygame.transform.scale(panel, (CELL_W, CELL_H)), (x, y))
        pygame.draw.rect(sheet, HAIRUNE, (x, y, CELL_W, CELL_H), 1)
    right_aligned(row_names[ri], f_row, MUTED,
                  grid_x - 16, grid_y + ri * (CELL_H + GAP) + CELL_H // 2)

for ci, head in enumerate(('BEFORE', 'AFTER')):
    centred(head, f_head, MUTED, grid_x + ci * (CELL_W + GAP) + CELL_W // 2, head_y)

strip_x = (sheet_w - strip_w) // 2
tiles = (
    (before_in,  'BEFORE · parrot IN',  (196, 158, 138)),
    (after_in,   'AFTER · parrot IN',   (150, 226, 182)),
    (before_out, 'BEFORE · parrot OUT', (226, 138, 116)),
    (after_out,  'AFTER · parrot OUT',  (124, 234, 202)),
)
for ti, (panel, label, col) in enumerate(tiles):
    x = strip_x + ti * (TILE_W + GAP)
    crop = panel.subsurface(CROP).copy()
    sheet.blit(pygame.transform.scale(crop, (TILE_W, TILE_H)), (x, strip_y))
    pygame.draw.rect(sheet, HAIRUNE, (x, strip_y, TILE_W, TILE_H), 1)
    centred(label, f_tile, col, x + TILE_W // 2, label_y)

OUT = '/home/user/skybit/docs/nest-alive-3d/simple-void/comparison.png'
pygame.image.save(sheet, OUT)
print('saved', OUT, sheet.get_size())

# ── Numeric verification (never open the image) ──────────────────────────────
print('AFTER-OUT (31,74):', after_out.get_at((31, 74))[:3])
bad = []
for y in range(0, 70):
    for x in range(W):
        r, g, b = after_out.get_at((x, y))[:3]
        if r < 30 and g < 30 and b < 30:
            bad.append((x, y, r, g, b))
print('dark pixels above y=69 in AFTER-OUT:', len(bad), bad[:8])
