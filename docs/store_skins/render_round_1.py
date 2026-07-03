"""Headless renderer for the round-1 store-skin exploration sheet.

Draws each NEW candidate skin as a store-hero (130px) + an in-game small
read (40px) on a dark night-sky card, plus a comparison strip of the
current 6 shipped skins. Saves to docs/store_skins/round_1.png.

Run:  SDL_VIDEODRIVER=dummy python docs/store_skins/render_round_1.py
"""
import os
import sys
import pathlib

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import importlib.util                        # noqa: E402

from game import parrot                       # noqa: E402

# Load the sibling candidate module by path so docs/ never needs to be a
# Python package (keeps the staged CI source tree clean of an __init__).
_spec = importlib.util.spec_from_file_location(
    "candidate_skins", pathlib.Path(__file__).resolve().parent / "candidate_skins.py")
cs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cs)

# ── card palette (matches the store's dark night-sky cards) ──────────────────
BG          = (16, 18, 32)
CARD_TOP    = (38, 40, 70)
CARD_BOT    = (22, 24, 46)
CARD_EDGE   = (88, 96, 150)
INK         = (232, 236, 248)
SUB         = (150, 158, 190)
ACCENT      = (255, 210, 90)
NEW_TAG     = (90, 220, 140)

FONT_DIR = pathlib.Path(__file__).resolve().parents[2] / "game" / "assets"
F_TITLE = pygame.font.Font(str(FONT_DIR / "LiberationSans-Bold.ttf"), 30)
F_NAME  = pygame.font.Font(str(FONT_DIR / "LiberationSans-Bold.ttf"), 20)
F_SUB   = pygame.font.Font(str(FONT_DIR / "LiberationSans-Bold.ttf"), 13)
F_TAG   = pygame.font.Font(str(FONT_DIR / "LiberationSans-Bold.ttf"), 12)


def vgrad(w, h, top, bot, radius=14):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        t = y / max(1, h - 1)
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(s, col, (0, y), (w, y))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=radius)
    s.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return s


def starfield(surf, rect, seed):
    import random
    rng = random.Random(seed)
    for _ in range(int(rect.w * rect.h / 320)):
        x = rect.x + rng.randint(2, rect.w - 2)
        y = rect.y + rng.randint(2, rect.h - 2)
        b = rng.randint(70, 170)
        surf.set_at((x, y), (b, b, min(255, b + 40)))


def fit(sprite, target_h):
    """Scale a sprite so its height is target_h, preserving aspect."""
    w, h = sprite.get_size()
    s = target_h / h
    return pygame.transform.smoothscale(sprite, (max(1, int(w * s)), target_h))


def draw_skin_card(surf, x, y, w, h, label, getter, is_new=True):
    card = vgrad(w, h, CARD_TOP, CARD_BOT)
    surf.blit(card, (x, y))
    rect = pygame.Rect(x, y, w, h)
    starfield(surf, rect.inflate(-8, -8), hash(label) & 0xFFFF)
    pygame.draw.rect(surf, CARD_EDGE, rect, 2, border_radius=14)

    # Hero render (mid-flap frame index 1, slight upward tilt like the store).
    hero = getter(1, -8)
    hero = fit(hero, 132)
    hrect = hero.get_rect(center=(x + w // 2, y + h // 2 - 14))
    surf.blit(hero, hrect.topleft)

    # Small in-game read in a chip at the bottom-left.
    chip = pygame.Rect(x + 10, y + h - 56, 50, 50)
    pygame.draw.rect(surf, (12, 13, 26), chip, border_radius=8)
    pygame.draw.rect(surf, (60, 66, 100), chip, 1, border_radius=8)
    small = fit(getter(1, 6), 40)
    srect = small.get_rect(center=chip.center)
    surf.blit(small, srect.topleft)
    lbl = F_TAG.render("40px", True, SUB)
    surf.blit(lbl, (chip.x + 2, chip.bottom + 1))

    # Name.
    name = F_NAME.render(label, True, INK)
    surf.blit(name, (x + w // 2 - name.get_width() // 2, y + h - 30))

    if is_new:
        tag = F_TAG.render("NEW", True, (12, 20, 14))
        tw = tag.get_width() + 12
        tagrect = pygame.Rect(x + w - tw - 8, y + 8, tw, 18)
        pygame.draw.rect(surf, NEW_TAG, tagrect, border_radius=9)
        surf.blit(tag, (tagrect.x + 6, tagrect.y + 2))


# ── layout ───────────────────────────────────────────────────────────────────
COLS = 4
CW, CH = 196, 232
GAP = 18
MARGIN = 28
TITLE_H = 74

rows_new = (len(cs.CANDIDATES) + COLS - 1) // COLS
W = MARGIN * 2 + COLS * CW + (COLS - 1) * GAP
NEW_BLOCK_H = rows_new * CH + (rows_new - 1) * GAP

# Current-skins comparison strip (smaller cards, one row).
CUR = [
    ("TOP HAT",  parrot.get_hat_parrot),
    ("SKELETON", parrot.get_skeleton_parrot),
    ("FRIED",    parrot.get_fried_parrot),
    ("GHOST",    parrot.get_ghost_parrot),
    ("ZOMBIE",   lambda f, t: parrot.get_dead_parrot(f, t, "B")),
    ("KNIGHT",   parrot.get_knight_parrot),
]
SCW, SCH = 122, 150
STRIP_LABEL_H = 34
strip_w = len(CUR) * SCW + (len(CUR) - 1) * 12
STRIP_H = STRIP_LABEL_H + SCH

H = TITLE_H + NEW_BLOCK_H + 40 + STRIP_H + MARGIN

sheet = pygame.Surface((W, H))
sheet.fill(BG)
# Faint top vignette band.
for y in range(TITLE_H):
    t = y / TITLE_H
    pygame.draw.line(sheet, (int(16 + 10 * (1 - t)), int(18 + 12 * (1 - t)),
                             int(32 + 18 * (1 - t))), (0, y), (W, y))

title = F_TITLE.render("STORE SKINS — Round 1 candidates", True, INK)
sheet.blit(title, (MARGIN, 18))
sub = F_SUB.render("8 new procedural macaw skins · hero (130px) + in-game (40px) reads",
                   True, SUB)
sheet.blit(sub, (MARGIN, 52))

# New candidate grid.
y0 = TITLE_H
for i, (sid, label, getter) in enumerate(cs.CANDIDATES):
    r, c = divmod(i, COLS)
    x = MARGIN + c * (CW + GAP)
    y = y0 + r * (CH + GAP)
    draw_skin_card(sheet, x, y, CW, CH, label, getter, is_new=True)

# Divider + current strip.
strip_y = y0 + NEW_BLOCK_H + 22
pygame.draw.line(sheet, (60, 66, 100), (MARGIN, strip_y - 8),
                 (W - MARGIN, strip_y - 8), 1)
hdr = F_NAME.render("Currently shipping (for comparison)", True, SUB)
sheet.blit(hdr, (MARGIN, strip_y))

sx = MARGIN
sy = strip_y + STRIP_LABEL_H
for label, getter in CUR:
    card = vgrad(SCW, SCH, CARD_TOP, CARD_BOT)
    sheet.blit(card, (sx, sy))
    crect = pygame.Rect(sx, sy, SCW, SCH)
    starfield(sheet, crect.inflate(-6, -6), hash(label) & 0x7FFF)
    pygame.draw.rect(sheet, (60, 66, 100), crect, 2, border_radius=12)
    spr = fit(getter(1, -6), 96)
    sheet.blit(spr, spr.get_rect(center=(sx + SCW // 2, sy + SCH // 2 - 12)).topleft)
    nm = F_SUB.render(label, True, INK)
    sheet.blit(nm, (sx + SCW // 2 - nm.get_width() // 2, sy + SCH - 22))
    sx += SCW + 12

out = pathlib.Path(__file__).resolve().parent / "round_1.png"
pygame.image.save(sheet, str(out))
print(f"wrote {out}  ({W}x{H})")
