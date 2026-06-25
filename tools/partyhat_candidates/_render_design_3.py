"""Render the design_3 (JESTER CAP) review sheet (SCRATCH ONLY)."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from tools.ninja_render import gameplay_panel, hero_panel
from tools.partyhat_candidates import design_3 as d

FONT = pygame.font.SysFont("sans", 16, bold=True)
SMALL = pygame.font.SysFont("sans", 13)


def label(surf, text, x, y):
    surf.blit(SMALL.render(text, True, (235, 232, 245)), (x, y))


def checker_bg(box):
    bg = pygame.Surface((box, box))
    a, b = (210, 210, 216), (188, 188, 196)
    s = 8
    for j in range(0, box, s):
        for i in range(0, box, s):
            bg.fill(a if (i // s + j // s) % 2 == 0 else b, (i, j, s, s))
    return bg


# Panels
GP_W, GP_H = 252, 360
gp = gameplay_panel(d.build, GP_W, GP_H)

HERO = 360
hero = hero_panel(d.build, HERO)

# 40px NEAREST "truth read": shrink an in-game frame hard, then blow it back up.
frame = d.build(2, 10.0)
bb = frame.get_bounding_rect()
fr = frame.subsurface(bb).copy() if bb.width else frame
# scale longest side to 40
sw, sh = fr.get_size()
sc = 40 / max(sw, sh)
small = pygame.transform.smoothscale(fr, (max(1, int(sw * sc)), max(1, int(sh * sc))))
truth_box = 200
truth = pygame.Surface((truth_box, truth_box), pygame.SRCALPHA)
truth.blit(checker_bg(truth_box), (0, 0))
up = pygame.transform.scale(small, (small.get_width() * 4, small.get_height() * 4))
truth.blit(up, up.get_rect(center=(truth_box // 2, truth_box // 2)))
# also show the actual 40px chip 1:1
truth.blit(small, (8, 8))

# Store icon, cropped to content on a panel.
icon = d.icon
ib = icon.get_bounding_rect()
icon_c = icon.subsurface(ib).copy() if ib.width else icon
ibox_w, ibox_h = 250, 200
icon_panel = pygame.Surface((ibox_w, ibox_h), pygame.SRCALPHA)
pygame.draw.rect(icon_panel, (28, 26, 40), icon_panel.get_rect(), border_radius=12)
isc = min((ibox_w * 0.84) / icon_c.get_width(), (ibox_h * 0.84) / icon_c.get_height())
icon_s = pygame.transform.smoothscale(
    icon_c, (int(icon_c.get_width() * isc), int(icon_c.get_height() * isc)))
icon_panel.blit(icon_s, icon_s.get_rect(center=(ibox_w // 2, ibox_h // 2)))

# Compose sheet.
PAD = 18
title_h = 40
col1 = GP_W
col2 = HERO
sheet_w = PAD * 4 + col1 + max(col2, truth_box + PAD + 250)
sheet_h = title_h + PAD * 3 + max(GP_H, HERO + PAD + truth_box)
sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
sheet.fill((24, 22, 34))

sheet.blit(FONT.render("PARTY HAT redesign — DESIGN 3: JESTER CAP", True,
                       (255, 233, 120)), (PAD, 12))

x = PAD
y = title_h + PAD
sheet.blit(gp, (x, y))
label(sheet, "in-gameplay (40px-class read, mid-flight)", x, y + GP_H + 2)

x2 = PAD * 2 + col1
sheet.blit(hero, (x2, y))
label(sheet, "hero product shot", x2, y + HERO + 2)

# Right column second row: truth + icon side by side under hero.
ry = y + HERO + 22
sheet.blit(truth, (x2, ry))
label(sheet, "40px NEAREST truth read", x2, ry + truth_box + 2)
sheet.blit(icon_panel, (x2 + truth_box + PAD, ry))
label(sheet, "store icon", x2 + truth_box + PAD, ry + truth_box + 2)

out = "docs/store_redesign/hats/partyhat/design_3/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("WROTE", out, sheet.get_size())
