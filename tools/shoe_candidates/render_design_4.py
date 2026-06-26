"""Render the WING BOOTS (design_4) round-1 review sheet.

Headless. Composites the legendary product-shot + Pip wearing it (day/night,
hero, 4-frame filmstrip) + the 40px nearest-neighbour truth read so the wing
silhouette can be judged at gameplay scale.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.insert(0, os.path.dirname(__file__))

import pygame
pygame.init()

import design_4
from game import parrot, shoe_skins, biome
from game.store_skins import _make_skin
from game.shoe_skins import _foot_paint
from tools import ninja_render

draw_shoe = design_4.draw_shoe

FONT = pygame.font.SysFont("Arial", 15, bold=True)
SMALL = pygame.font.SysFont("Arial", 12)


def label(surf, text, x, y, color=(245, 240, 225)):
    surf.blit(SMALL.render(text, True, color), (x, y))


def title(surf, text, x, y):
    surf.blit(FONT.render(text, True, (255, 224, 150)), (x, y))


def big_icon():
    """Product shot on an oversized SRCALPHA canvas so the up/back wings that
    break the unit box are never clipped by the standard icon padding."""
    W, H = 240, 200
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    # Generous side/top room: wings reach t<0 above and behind the heel.
    bx, by, bw, bh = 90, 96, 104, 58
    draw_shoe(s, bx, by, bw, bh, 1)
    return parrot._add_outline(s)


def worn_frame_nearest(target_h, *, night=False):
    build = _make_skin(_foot_paint(draw_shoe))
    frame = build(2, 8.0)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy() if bb.width else frame
    sw, sh = frame.get_size()
    scale = target_h / sh
    small = pygame.transform.scale(frame, (max(1, int(sw * scale)), target_h))
    bg = (16, 20, 40) if night else (150, 196, 222)
    panel = pygame.Surface(small.get_size())
    panel.fill(bg)
    panel.blit(small, (0, 0))
    return panel


def main():
    build = _make_skin(_foot_paint(draw_shoe))

    SHEET_W, SHEET_H = 1180, 760
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill((30, 28, 40))

    title(sheet, "WING BOOTS — legendary ~3200 — design_4 — round 1", 20, 14)

    # ── product-shot icon (big) ────────────────────────────────────────────────
    icon = big_icon()
    icon = pygame.transform.smoothscale(
        icon, (int(icon.get_width() * 1.4), int(icon.get_height() * 1.4)))
    sheet.blit(icon, (20, 50))
    title(sheet, "PRODUCT SHOT", 40, 50)

    # also the canonical store-built icon, to confirm the registry path works
    store_icon = shoe_skins._build_icon(draw_shoe)
    sheet.blit(store_icon, (40, 350))
    label(sheet, "store _build_icon()", 40, 350 + store_icon.get_height() + 4)

    # ── Pip wearing it: day + night gameplay panels ────────────────────────────
    day = ninja_render.gameplay_panel(build, 210, 300)
    sheet.blit(day, (380, 60))
    title(sheet, "PIP — DAY", 380, 42)

    # night gameplay panel: reuse gameplay_panel then darken-tint
    night = ninja_render.gameplay_panel(build, 210, 300)
    tint = pygame.Surface(night.get_size(), pygame.SRCALPHA)
    tint.fill((20, 24, 70, 150))
    night.blit(tint, (0, 0))
    sheet.blit(night, (700, 60))
    title(sheet, "PIP — NIGHT", 700, 42)

    # ── hero panel ─────────────────────────────────────────────────────────────
    hero = ninja_render.hero_panel(build, 280)
    sheet.blit(hero, (380, 390))
    title(sheet, "HERO", 380, 372)

    # ── 4-frame filmstrip (flap cycle wing read) ───────────────────────────────
    title(sheet, "FILMSTRIP 0..3", 700, 372)
    fx = 700
    for fi in range(4):
        f = build(fi, 6.0)
        bb = f.get_bounding_rect()
        f = f.subsurface(bb).copy() if bb.width else f
        f = pygame.transform.smoothscale(
            f, (int(f.get_width() * 1.6), int(f.get_height() * 1.6)))
        cell = pygame.Surface((f.get_width() + 8, f.get_height() + 8), pygame.SRCALPHA)
        pygame.draw.rect(cell, (44, 42, 58), cell.get_rect(), border_radius=8)
        cell.blit(f, (4, 4))
        sheet.blit(cell, (fx, 392))
        label(sheet, str(fi), fx + 4, 392 + cell.get_height())
        fx += cell.get_width() + 6

    # ── 40px NEAREST truth read: day/night, 1x + 4x ────────────────────────────
    title(sheet, "40px TRUTH (nearest) — day | night, 1x & 4x", 20, 560)
    tx = 20
    for night_mode, tag in ((False, "day"), (True, "night")):
        w1 = worn_frame_nearest(40, night=night_mode)
        sheet.blit(w1, (tx, 590))
        label(sheet, tag + " 1x", tx, 590 + w1.get_height() + 2)
        w4 = pygame.transform.scale(
            w1, (w1.get_width() * 4, w1.get_height() * 4))
        sheet.blit(w4, (tx + w1.get_width() + 12, 590))
        label(sheet, tag + " 4x", tx + w1.get_width() + 12,
              590 + w4.get_height() + 2)
        tx += w1.get_width() + w4.get_width() + 60

    out_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..",
        "docs", "store_redesign", "shoes", "design_4"))
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_1.png")
    pygame.image.save(sheet, out)
    print("WROTE", out)
    print("exists:", os.path.exists(out))


if __name__ == "__main__":
    main()
