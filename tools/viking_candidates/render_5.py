"""Compose the ODINWING review sheet (hero + in-gameplay + 40px truth read +
4-frame shimmer filmstrip) and save it to
docs/store_redesign/costume/viking/design_5/round_1.png.

Scratch only — renders the unregistered candidate builder via the shared
ninja_render harness (production art untouched). Run headless:
  SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python tools/viking_candidates/render_5.py
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.font.init()

from tools.ninja_render import gameplay_panel, hero_panel
from tools.viking_candidates.design_5 import build

FONT = "/home/user/skybit/game/assets/LiberationSans-Bold.ttf"
OUT = "/home/user/skybit/docs/store_redesign/costume/viking/design_5/round_1.png"

BG = (20, 17, 28)
INK = (244, 238, 210)
SUB = (168, 158, 138)
GOLD = (233, 194, 74)


def _label(sheet, text, x, y, size=20, color=INK):
    f = pygame.font.Font(FONT, size)
    sheet.blit(f.render(text, True, color), (x, y))


def _truth_read(box):
    """The '40px truth read': render Pip small at three flap frames, downscale
    each to 40px with NEAREST neighbour (the honest in-flight pixel read), then
    magnify 3x (again NEAREST) and tile — so the reviewer sees exactly what
    survives. The gold winged-helm span + spear + raven must hold every frame."""
    panel = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.rect(panel, (12, 10, 18), panel.get_rect(), border_radius=14)
    tiles = []
    for fi in (0, 2, 3):
        frame = build(fi, 10.0)
        bb = frame.get_bounding_rect()
        if bb.width and bb.height:
            frame = frame.subsurface(bb).copy()
        sw, sh = frame.get_size()
        scale = 40 / max(sw, sh)
        small = pygame.transform.scale(
            frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
        tiles.append(pygame.transform.scale(
            small, (small.get_width() * 3, small.get_height() * 3)))
    gap = 6
    total_w = sum(t.get_width() for t in tiles) + gap * (len(tiles) - 1)
    x = (box - total_w) // 2
    for t in tiles:
        panel.blit(t, (x, (box - t.get_height()) // 2))
        x += t.get_width() + gap
    return panel


def _filmstrip(w, h):
    """4-frame shimmer filmstrip — one tile per wing-flap frame so the animated
    gold pulse / drifting runic halo / breathing helm-wings are visible across a
    full beat. Each tile is the bounded hero on a flat panel."""
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(panel, (28, 23, 38), panel.get_rect(), border_radius=12)
    n = 4
    cell = w // n
    for fi in range(n):
        frame = build(fi, 6.0)
        bb = frame.get_bounding_rect()
        if bb.width and bb.height:
            frame = frame.subsurface(bb).copy()
        sw, sh = frame.get_size()
        scale = min((cell - 8) / sw, (h - 28) / sh)
        scaled = pygame.transform.smoothscale(
            frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
        cx = fi * cell + cell // 2
        panel.blit(scaled, scaled.get_rect(center=(cx, h // 2 - 4)))
        _label(panel, f"f{fi}", cx - 8, h - 22, 14, SUB)
        if fi:
            pygame.draw.line(panel, (44, 38, 56),
                             (fi * cell, 8), (fi * cell, h - 8), 1)
    return panel


def main():
    W, H = 1000, 800
    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    _label(sheet, "ODINWING", 28, 22, 36, INK)
    _label(sheet, "Allfather Valkyrie Helm  ·  LEGENDARY  ·  viking redesign / design_5  ·  ROUND 1",
           30, 64, 18, GOLD)
    pygame.draw.line(sheet, (52, 44, 64), (28, 96), (W - 28, 96), 2)

    pad = 28
    top = 116

    # Hero on the standard navy product panel.
    hp = hero_panel(build, 300)
    sheet.blit(hp, (pad, top))
    _label(sheet, "HERO  ·  product panel", pad, top + 304, 16, SUB)

    # In-gameplay over the daytime biome (the harness scene).
    gw, gh = 207, 300
    gp = gameplay_panel(build, gw, gh)
    gx = pad * 2 + 300
    sheet.blit(gp, (gx, top))
    pygame.draw.rect(sheet, (52, 44, 64), (gx, top, gw, gh), 2, border_radius=6)
    _label(sheet, "IN-GAMEPLAY  ·  daytime biome", gx, top + 304, 16, SUB)

    # 40px truth read (NEAREST shrink, magnified 3x).
    tr = _truth_read(300)
    trx = pad * 3 + 300 + gw
    sheet.blit(tr, (trx, top))
    _label(sheet, "40px TRUTH READ  ·  nearest x3  ·  frames 0/2/3",
           trx, top + 304, 16, SUB)

    # 4-frame shimmer filmstrip across the full width — the legendary animation.
    fs_y = top + 360
    fs = _filmstrip(W - pad * 2, 280)
    sheet.blit(fs, (pad, fs_y))
    _label(sheet, "4-FRAME SHIMMER FILMSTRIP  ·  gold pulse + drifting runic halo + breathing helm-wings",
           pad, fs_y + 284, 16, GOLD)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
