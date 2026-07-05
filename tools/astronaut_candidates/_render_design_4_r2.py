"""Compose the design_4 (ROCKETEER) ROUND 2 review sheet. Scratch only.

Round 2 folds in the art-director ITERATE notes: face read inside the dome,
chest hardware cut, a dark keyline around the chrome silhouette, and a single
dome rim band. Adds a NIGHT gameplay panel so the keyline + face read are
checked against a dark sky too.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools import ninja_render as nr
from tools.astronaut_candidates.design_4 import build

from game import biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y

CONCEPT = "design_4 - ROCKETEER  (ROUND 2: face read + keyline + clean chest)"
BG = (16, 18, 28)
CARD = (26, 30, 44)
INK = (234, 240, 250)
SUB = (150, 160, 178)
ACCENT = (226, 59, 59)

pygame.font.init()
F_TITLE = pygame.font.SysFont("DejaVu Sans", 22, bold=True)
F_LABEL = pygame.font.SysFont("DejaVu Sans", 15, bold=True)
F_SMALL = pygame.font.SysFont("DejaVu Sans", 12)


def text(surf, s, pos, font=F_LABEL, color=INK):
    surf.blit(font.render(s, True, color), pos)


def gameplay_panel_phase(source, w, h, phase):
    """Same as nr.gameplay_panel but at an explicit day/night biome phase."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(phase)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, 0), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 96, 270
    frame = nr._frame(source, nr.FRAME_IDX, nr.TILT)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def rounded(panel):
    w, h = panel.get_size()
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=14)
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    out.blit(panel, (0, 0))
    out.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return out


def truth_read_40(source):
    frame = nr._frame(source, nr.FRAME_IDX, nr.TILT)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = 40 / max(sw, sh)
    small = pygame.transform.smoothscale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    big = pygame.transform.scale(
        small, (small.get_width() * 3, small.get_height() * 3))  # nearest
    return small, big


def filmstrip_cell(source, frame_idx, cell):
    panel = pygame.Surface((cell, cell), pygame.SRCALPHA)
    pygame.draw.rect(panel, (22, 26, 38), panel.get_rect(), border_radius=8)
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


def main():
    W, H = 1320, 760
    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    text(sheet, CONCEPT, (28, 18), F_TITLE, INK)
    text(sheet, "Exploration only - live skin_astronaut untouched, not in BUILDERS",
         (28, 48), F_SMALL, SUB)
    pygame.draw.line(sheet, ACCENT, (28, 70), (W - 28, 70), 2)

    top_y = 90
    # ── HERO ──
    hero_box = 300
    hero = nr.hero_panel(build, hero_box, frame_idx=nr.FRAME_IDX, tilt=0.0, bg=CARD)
    sheet.blit(hero, (28, top_y))
    text(sheet, "HERO", (28, top_y + hero_box + 6))

    # ── GAMEPLAY DAY ──
    gp_w, gp_h = 200, 300
    gx_day = 348
    sheet.blit(rounded(gameplay_panel_phase(build, gp_w, gp_h, 0.0)), (gx_day, top_y))
    text(sheet, "IN GAMEPLAY (DAY)", (gx_day, top_y + gp_h + 6))

    # ── GAMEPLAY NIGHT ──
    gx_night = gx_day + gp_w + 24
    sheet.blit(rounded(gameplay_panel_phase(build, gp_w, gp_h, 0.5)), (gx_night, top_y))
    text(sheet, "IN GAMEPLAY (NIGHT)", (gx_night, top_y + gp_h + 6))

    # ── 40px TRUTH READ ──
    small, big = truth_read_40(build)
    tx = gx_night + gp_w + 36
    pygame.draw.rect(sheet, CARD, (tx, top_y, 240, gp_h), border_radius=14)
    sheet.blit(big, big.get_rect(center=(tx + 120, top_y + 120)))
    sheet.blit(small, (tx + 120 - small.get_width() // 2, top_y + 250))
    text(sheet, "40px TRUTH READ", (tx + 12, top_y + gp_h + 6))
    text(sheet, "(actual size + 3x nearest)", (tx + 12, top_y + gp_h + 26),
         F_SMALL, SUB)

    # ── FILMSTRIP ──
    strip_y = 500
    pygame.draw.line(sheet, (56, 60, 78), (28, strip_y - 12), (W - 28, strip_y - 12), 1)
    text(sheet, "4-FRAME FILMSTRIP - antenna wobble + rocket flame flicker",
         (28, strip_y - 8))
    cell = 188
    labels = ["wing up", "mid-up", "level", "down"]
    for i in range(4):
        cx = 28 + i * (cell + 16)
        sheet.blit(filmstrip_cell(build, i, cell), (cx, strip_y + 18))
        text(sheet, f"frame {i} ({labels[i]})", (cx + 6, strip_y + 18 + cell + 2),
             F_SMALL, SUB)

    out = "/home/user/skybit/docs/store_redesign/costume/astronaut/design_4/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("SAVED", out)


if __name__ == "__main__":
    main()
