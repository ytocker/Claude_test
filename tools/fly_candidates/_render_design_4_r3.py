import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
from tools.fly_candidates.design_4 import build

NIGHT = (12, 14, 24)
DUSK  = (74, 62, 84)          # a lighter sky to prove the barrel reads on ANY bg
INK   = (8, 8, 12)
font  = pygame.font.Font(None, 22)
small = pygame.font.Font(None, 18)


def hero_panel(fi, bg):
    hp = pygame.Surface((188, 200), pygame.SRCALPHA)
    pygame.draw.rect(hp, bg, hp.get_rect(), border_radius=14)
    fr = build(fi, 0.0)
    bb = fr.get_bounding_rect()
    fr2 = fr.subsurface(bb).copy() if (bb.width and bb.height) else fr
    sw, sh = fr2.get_size()
    scale = (200 * 0.80) / max(sw, sh)
    fr2 = pygame.transform.smoothscale(
        fr2, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    hp.blit(fr2, fr2.get_rect(center=(94, 100)))
    hp.blit(small.render(f"F{fi}", True, (200, 200, 210)), (8, 8))
    return hp


def truth_row(bg, label):
    """40px in-game size, then NEAREST-upscaled x3 so the true pixels show."""
    row = pygame.Surface((4 * 130 + 16, 176), pygame.SRCALPHA)
    row.fill(bg)
    row.blit(small.render(label, True, (220, 220, 225)), (6, 4))
    for fi in range(4):
        fr = build(fi, 0.0)
        h = int(40 * fr.get_height() / fr.get_width())
        fr40 = pygame.transform.smoothscale(fr, (40, h))   # real in-game size
        big = pygame.transform.scale(fr40, (120, 3 * h))    # NEAREST inspect
        row.blit(big, (8 + fi * 130, (176 - 3 * h) // 2 + 10))
    return row


rows = []
# Row 1 — hero frames on night sky.
r1 = pygame.Surface((4 * 196 + 8, 208), pygame.SRCALPHA)
r1.fill(INK)
for i in range(4):
    r1.blit(hero_panel(i, NIGHT), (8 + i * 196, 4))
rows.append(r1)
# Row 2 + 3 — 40px truth strips on night AND on a lighter sky.
rows.append(truth_row(NIGHT, "40px truth — NIGHT sky"))
rows.append(truth_row(DUSK,  "40px truth — DUSK sky (glow-independent read)"))

W = max(r.get_width() for r in rows)
H = sum(r.get_height() for r in rows) + 8 * (len(rows) + 1)
sheet = pygame.Surface((W + 16, H), pygame.SRCALPHA)
sheet.fill(INK)
y = 8
for r in rows:
    sheet.blit(r, (8, y))
    y += r.get_height() + 8

out = "/home/user/skybit/docs/store_redesign/animal/fly/design_4/round_3.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("Saved", out, sheet.get_size())
