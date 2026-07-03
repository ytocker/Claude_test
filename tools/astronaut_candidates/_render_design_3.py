"""Compose the design_3 (STARFARER) review sheet. Scratch only."""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools import ninja_render as nr
from tools.astronaut_candidates.design_3 import build

from game import biome
from game.draw import (get_sky_surface_biome, draw_mountains, draw_ground,
                       draw_cloud)
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y

CONCEPT = "design_3 - STARFARER (Cosmic/Galaxy Deep-Space Explorer, LEGENDARY)"
BG = (12, 11, 26)
CARD = (22, 20, 44)
INK = (232, 230, 250)
SUB = (150, 142, 185)
ACCENT = (63, 224, 255)

pygame.font.init()
F_TITLE = pygame.font.SysFont("DejaVu Sans", 22, bold=True)
F_LABEL = pygame.font.SysFont("DejaVu Sans", 15, bold=True)
F_SMALL = pygame.font.SysFont("DejaVu Sans", 12)


def text(surf, s, pos, font=F_LABEL, color=INK):
    surf.blit(font.render(s, True, color), pos)


def truth_read_40(source, frame_idx=nr.FRAME_IDX):
    """40px NEAREST downscale of a pose, magnified 3x — the survive-shrink read."""
    frame = nr._frame(source, frame_idx, nr.TILT)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = 40 / max(sw, sh)
    small = pygame.transform.smoothscale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    big = pygame.transform.scale(
        small, (small.get_width() * 3, small.get_height() * 3))
    return small, big


def night_gameplay_panel(source, w, h):
    """Same crop as nr.gameplay_panel but over a NIGHT biome — proves the
    cosmic body self-contrasts on a dark sky too."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(0.6)            # deep-night phase
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, 0), (0, 0))
    draw_mountains(scene, 40.0, GROUND_Y, GW,
                   palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (40, 30, 50))
    pip_cx, pip_cy = 96, 270
    frame = nr._frame(source, nr.FRAME_IDX, nr.TILT)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def filmstrip_cell(source, frame_idx, cell):
    """One flap frame on a flat panel — shows the animated glow / star-trail."""
    panel = pygame.Surface((cell, cell), pygame.SRCALPHA)
    pygame.draw.rect(panel, (16, 15, 34), panel.get_rect(), border_radius=8)
    frame = nr._frame(source, frame_idx, 0.0)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = (cell * 0.82) / max(sw, sh)
    frame = pygame.transform.smoothscale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    panel.blit(frame, frame.get_rect(center=(cell // 2, cell // 2)))
    return panel


def _rounded(panel, radius=14):
    w, h = panel.get_size()
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=radius)
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    out.blit(panel, (0, 0))
    out.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return out


def main():
    W, H = 1300, 760
    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    text(sheet, CONCEPT, (28, 16), F_TITLE, INK)
    text(sheet, "Exploration only - not in store_skins.BUILDERS, production art untouched",
         (28, 46), F_SMALL, SUB)
    pygame.draw.line(sheet, ACCENT, (28, 68), (W - 28, 68), 2)

    top_y = 86
    # ── HERO ──
    hero_box = 290
    sheet.blit(nr.hero_panel(build, hero_box, frame_idx=nr.FRAME_IDX,
                             tilt=0.0, bg=CARD), (28, top_y))
    text(sheet, "HERO", (28, top_y + hero_box + 6))

    # ── DAY GAMEPLAY ──
    gp_w, gp_h = 200, 300
    gx = 28 + hero_box + 26
    sheet.blit(_rounded(nr.gameplay_panel(build, gp_w, gp_h)), (gx, top_y))
    text(sheet, "IN GAMEPLAY (day)", (gx, top_y + gp_h + 6))

    # ── NIGHT GAMEPLAY (self-contrast proof) ──
    nx = gx + gp_w + 24
    sheet.blit(_rounded(night_gameplay_panel(build, gp_w, gp_h)), (nx, top_y))
    text(sheet, "IN GAMEPLAY (night)", (nx, top_y + gp_h + 6))

    # ── 40px TRUTH READ ──
    tx = nx + gp_w + 28
    tw = W - tx - 28
    pygame.draw.rect(sheet, CARD, (tx, top_y, tw, gp_h), border_radius=14)
    small, big = truth_read_40(build)
    sheet.blit(big, big.get_rect(center=(tx + tw // 2, top_y + 110)))
    sheet.blit(small, (tx + tw // 2 - small.get_width() // 2, top_y + 240))
    text(sheet, "40px TRUTH READ", (tx + 12, top_y + gp_h + 6))
    text(sheet, "(actual size + 3x nearest)", (tx + 12, top_y + gp_h + 26),
         F_SMALL, SUB)

    # ── FILMSTRIP ──
    strip_y = 470
    pygame.draw.line(sheet, (54, 50, 84), (28, strip_y - 12),
                     (W - 28, strip_y - 12), 1)
    text(sheet, "4-FRAME FILMSTRIP - one tell: dart grows + single visor brightness step",
         (28, strip_y - 8))
    cell = 184
    gap = (W - 56 - cell * 4) // 3
    labels = ["wing up (50)", "mid-up (20)", "level (-10)", "down (-40)"]
    for i in range(4):
        cxp = 28 + i * (cell + gap)
        sheet.blit(filmstrip_cell(build, i, cell), (cxp, strip_y + 18))
        text(sheet, f"frame {i} - {labels[i]}",
             (cxp + 6, strip_y + 18 + cell + 2), F_SMALL, SUB)

    out = "/home/user/skybit/docs/store_redesign/costume/astronaut/design_3/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("SAVED", out)


if __name__ == "__main__":
    main()
