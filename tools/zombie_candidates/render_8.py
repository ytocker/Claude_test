"""Render the Design 8 (Barnacle Drowned Wretch) R1 review sheet: gameplay
panel, hero product-shot, and a 40px NEAREST truth-read, labelled and committed
to docs/store_redesign/costume/zombie/design_8/round_1.png."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools.ninja_render import gameplay_panel, hero_panel, FRAME_IDX, TILT, _frame
from tools.zombie_candidates.design_8 import build

OUT = "docs/store_redesign/costume/zombie/design_8/round_1.png"

GAME_W, GAME_H = 200, 350
HERO_BOX = 280
TRUTH = 200          # 40px hero read scaled 5x
PAD = 24
LABEL_H = 44

font_big = pygame.font.SysFont("Arial", 22, bold=True)
font_sm = pygame.font.SysFont("Arial", 14)


def truth_read(source):
    """Scale the hero frame down to 40x40 (NEAREST), then back up 5x — the
    honest 'what survives when shrunk' read the design must pass."""
    frame = _frame(source, FRAME_IDX, TILT)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = 36.0 / max(sw, sh)
    small = pygame.transform.scale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    tiny = pygame.Surface((40, 40), pygame.SRCALPHA)
    tiny.blit(small, small.get_rect(center=(20, 20)))
    return pygame.transform.scale(tiny, (TRUTH, TRUTH))


gp = gameplay_panel(build, GAME_W, GAME_H)
hero = hero_panel(build, HERO_BOX)
tr = truth_read(build)

col_w = [GAME_W, HERO_BOX, TRUTH]
inner_h = max(GAME_H, HERO_BOX, TRUTH)
sheet_w = PAD * 2 + sum(col_w) + PAD * 2 * (len(col_w) - 1)
sheet_h = LABEL_H + PAD + inner_h + PAD + 30

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((26, 32, 36))

title = font_big.render("DESIGN 8 — BARNACLE DROWNED WRETCH", True, (200, 232, 236))
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 12)))

x = PAD
top = LABEL_H + PAD
captions = ["gameplay", "hero (280px)", "40px truth-read"]
for panel, w, cap in zip((gp, hero, tr), col_w, captions):
    y = top + (inner_h - panel.get_height()) // 2
    if cap.startswith("40px"):
        plate = pygame.Rect(x - 6, y - 6, panel.get_width() + 12, panel.get_height() + 12)
        pygame.draw.rect(sheet, (16, 20, 24), plate, border_radius=8)
    sheet.blit(panel, (x, y))
    ct = font_sm.render(cap, True, (150, 174, 172))
    sheet.blit(ct, ct.get_rect(midtop=(x + w // 2, top + inner_h + 6)))
    x += w + PAD * 2

os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
print("wrote", OUT, sheet.get_size())
