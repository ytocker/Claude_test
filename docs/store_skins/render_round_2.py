"""Headless renderer for the round-2 store-skin exploration sheet.

Round-2 emphasis (art-director): the 40px in-game crop is the truth test, so
each NEW skin shows a 130px hero AND a prominent 40px chip on the navy store
card. The 3 redrawn current skins show before/after at 40px + hero. The Crown
standby is one of the NEW cards.

Run:  SDL_VIDEODRIVER=dummy python docs/store_skins/render_round_2.py
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
COST        = (255, 214, 96)

FONT_DIR = pathlib.Path(__file__).resolve().parents[2] / "game" / "assets"
F_TITLE = pygame.font.Font(str(FONT_DIR / "LiberationSans-Bold.ttf"), 30)
F_NAME  = pygame.font.Font(str(FONT_DIR / "LiberationSans-Bold.ttf"), 20)
F_SUB   = pygame.font.Font(str(FONT_DIR / "LiberationSans-Bold.ttf"), 13)
F_TAG   = pygame.font.Font(str(FONT_DIR / "LiberationSans-Bold.ttf"), 12)

# Proposed final costs (coins) for the NEW skins.
COSTS = {
    "PIRATE": 150, "NINJA": 170, "WIZARD": 220, "ASTRONAUT": 280,
    "PHARAOH": 300, "VIKING": 200, "COWBOY": 160, "DISCO": 320, "CROWN": 260,
}


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
    w, h = sprite.get_size()
    s = target_h / h
    return pygame.transform.smoothscale(sprite, (max(1, int(w * s)), target_h))


def draw_chip(surf, cx, cy, getter, frame=1, tilt=6, size=40, box=52, label=None):
    """The truth-test chip: skin at `size` px on a tiny navy card."""
    chip = pygame.Rect(cx - box // 2, cy - box // 2, box, box)
    pygame.draw.rect(surf, (12, 13, 26), chip, border_radius=8)
    pygame.draw.rect(surf, (60, 66, 100), chip, 1, border_radius=8)
    small = fit(getter(frame, tilt), size)
    surf.blit(small, small.get_rect(center=chip.center).topleft)
    if label:
        lbl = F_TAG.render(label, True, SUB)
        surf.blit(lbl, (chip.centerx - lbl.get_width() // 2, chip.bottom + 2))
    return chip


def draw_skin_card(surf, x, y, w, h, label, getter):
    card = vgrad(w, h, CARD_TOP, CARD_BOT)
    surf.blit(card, (x, y))
    rect = pygame.Rect(x, y, w, h)
    starfield(surf, rect.inflate(-8, -8), hash(label) & 0xFFFF)
    pygame.draw.rect(surf, CARD_EDGE, rect, 2, border_radius=14)

    # Hero render (mid-flap, slight upward tilt like the store).
    hero = fit(getter(1, -8), 128)
    surf.blit(hero, hero.get_rect(center=(x + w // 2 + 22, y + 74)).topleft)

    # TWO prominent 40px reads (level + diving tilt) — the truth test, enlarged.
    draw_chip(surf, x + 36, y + 76, getter, frame=1, tilt=6, size=42, box=56,
              label="40px lvl")
    draw_chip(surf, x + 36, y + 146, getter, frame=3, tilt=28, size=42, box=56,
              label="40px dive")

    # Name + cost.
    name = F_NAME.render(label, True, INK)
    surf.blit(name, (x + w // 2 - name.get_width() // 2, y + h - 34))
    cost = COSTS.get(label)
    if cost is not None:
        ctxt = F_SUB.render(f"{cost} coins", True, COST)
        surf.blit(ctxt, (x + w // 2 - ctxt.get_width() // 2, y + h - 16))

    # NEW tag (CROWN flagged as standby).
    is_standby = label == "CROWN"
    tag_txt = "STANDBY" if is_standby else "NEW"
    tag_col = (255, 200, 90) if is_standby else NEW_TAG
    tag = F_TAG.render(tag_txt, True, (12, 20, 14))
    tw = tag.get_width() + 12
    tagrect = pygame.Rect(x + w - tw - 8, y + 8, tw, 18)
    pygame.draw.rect(surf, tag_col, tagrect, border_radius=9)
    surf.blit(tag, (tagrect.x + 6, tagrect.y + 2))


# ── layout ───────────────────────────────────────────────────────────────────
COLS = 3
CW, CH = 262, 250
GAP = 18
MARGIN = 28
TITLE_H = 78

rows_new = (len(cs.CANDIDATES) + COLS - 1) // COLS
W = MARGIN * 2 + COLS * CW + (COLS - 1) * GAP
NEW_BLOCK_H = rows_new * CH + (rows_new - 1) * GAP

# Redraw strip: per skin → before-40 / after-40 / after-hero.
REDRAW_LABEL_H = 34
RCW = (W - MARGIN * 2 - 2 * GAP) // 3
RCH = 196
REDRAW_H = REDRAW_LABEL_H + len(cs.REDRAWS) * (RCH + 12)

H = TITLE_H + NEW_BLOCK_H + 34 + REDRAW_H + MARGIN

sheet = pygame.Surface((W, H))
sheet.fill(BG)
for y in range(TITLE_H):
    t = y / TITLE_H
    pygame.draw.line(sheet, (int(16 + 10 * (1 - t)), int(18 + 12 * (1 - t)),
                             int(32 + 18 * (1 - t))), (0, y), (W, y))

title = F_TITLE.render("STORE SKINS — Round 2", True, INK)
sheet.blit(title, (MARGIN, 18))
sub = F_SUB.render(
    "Signatures pushed above the crown, value floor on navy, 2px-min detail · "
    "40px (level + dive) is the truth test", True, SUB)
sheet.blit(sub, (MARGIN, 54))

# New candidate grid.
y0 = TITLE_H
for i, (sid, label, getter) in enumerate(cs.CANDIDATES):
    r, c = divmod(i, COLS)
    x = MARGIN + c * (CW + GAP)
    y = y0 + r * (CH + GAP)
    draw_skin_card(sheet, x, y, CW, CH, label, getter)

# ── Redraw section (before / after) ──────────────────────────────────────────
strip_y = y0 + NEW_BLOCK_H + 20
pygame.draw.line(sheet, (60, 66, 100), (MARGIN, strip_y - 6),
                 (W - MARGIN, strip_y - 6), 1)
hdr = F_NAME.render("Current-skin redraws  (shipped  →  proposed)", True, SUB)
sheet.blit(hdr, (MARGIN, strip_y))

ry = strip_y + REDRAW_LABEL_H
for label, before, after in cs.REDRAWS:
    cells = [
        ("SHIPPED (40px)", before, (110, 60, 70)),
        ("REDRAW (40px)",  after,  (60, 110, 80)),
        ("REDRAW (hero)",  after,  CARD_EDGE),
    ]
    for ci, (cap, getter, edge) in enumerate(cells):
        cx = MARGIN + ci * (RCW + GAP)
        card = vgrad(RCW, RCH, CARD_TOP, CARD_BOT)
        sheet.blit(card, (cx, ry))
        crect = pygame.Rect(cx, ry, RCW, RCH)
        starfield(sheet, crect.inflate(-6, -6), hash(label + cap) & 0x7FFF)
        pygame.draw.rect(sheet, edge, crect, 2, border_radius=12)
        cap_t = F_SUB.render(f"{label}  ·  {cap}", True, INK)
        sheet.blit(cap_t, (cx + 10, ry + 8))
        if "hero" in cap:
            spr = fit(getter(1, -8), 120)
            sheet.blit(spr, spr.get_rect(center=(cx + RCW // 2, ry + RCH // 2 + 12)).topleft)
        else:
            draw_chip(sheet, cx + RCW // 2 - 42, ry + RCH // 2 + 8, getter,
                      frame=1, tilt=6, size=44, box=58, label="level")
            draw_chip(sheet, cx + RCW // 2 + 42, ry + RCH // 2 + 8, getter,
                      frame=3, tilt=26, size=44, box=58, label="dive")
    ry += RCH + 12

out = pathlib.Path(__file__).resolve().parent / "round_2.png"
pygame.image.save(sheet, str(out))
print(f"wrote {out}  ({W}x{H})")
