"""Render the round_2 review sheet for skeleton design_4 (DEADMAN'S FLAG).

Day gameplay + night gameplay + hero close-up + a 40px NEAREST "truth read",
composited onto one labeled sheet via the shared ninja_render harness.
Headless: SDL_VIDEODRIVER=dummy python tools/skeleton_candidates/render_design_4.py
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from game import biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from tools.ninja_render import gameplay_panel, hero_panel, _frame, FRAME_IDX, TILT
from tools.skeleton_candidates.design_4 import build


def night_gameplay_panel(source, w, h, *, frame_idx=FRAME_IDX, tilt=TILT):
    """Mirror of ninja_render.gameplay_panel but on a NIGHT-sky biome phase
    so the bandana red + gold + bright bone are judged against dark sky."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(0.5)        # deep night phase
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, 0), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 96, 270
    frame = _frame(source, frame_idx, tilt)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def truth_read_panel(source, box, frame_idx=FRAME_IDX):
    """The bird drawn at ~40px, NEAREST-upscaled into a box so the reviewer
    sees exactly what reads at gameplay size. On a flat dark card."""
    frame = _frame(source, frame_idx, 0.0)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = 40.0 / max(sw, sh)
    small = pygame.transform.smoothscale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    big = pygame.transform.scale(small, (box, box))   # NEAREST upscale
    panel = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.rect(panel, (18, 16, 26), panel.get_rect(), border_radius=10)
    panel.blit(big, big.get_rect(center=(box // 2, box // 2)))
    return panel


def main():
    font = pygame.font.SysFont("dejavusans", 18, bold=True)
    small = pygame.font.SysFont("dejavusans", 14)

    pad = 16
    label_h = 26
    pw, ph = 210, 300           # gameplay panel (w/h kept <= 360/499 so crop fits)
    hbox = 300                  # hero box
    tbox = 220                  # truth-read box

    cols_top = [
        ("DAY — gameplay", gameplay_panel(build, pw, ph)),
        ("NIGHT — gameplay", night_gameplay_panel(build, pw, ph)),
    ]
    cols_bot = [
        ("HERO close-up", hero_panel(build, hbox)),
        ("40px TRUTH READ (nearest)", truth_read_panel(build, tbox)),
    ]

    top_w = pad + sum(p.get_width() + pad for _, p in cols_top)
    bot_w = pad + sum(p.get_width() + pad for _, p in cols_bot)
    sheet_w = max(top_w, bot_w)
    title_h = 40
    row1_h = label_h + ph
    row2_h = label_h + max(hbox, tbox)
    sheet_h = title_h + pad + row1_h + pad + row2_h + pad

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((30, 28, 38))

    title = font.render("SKELETON design_4 — DEADMAN'S FLAG — round 2",
                        True, (244, 239, 224))
    sheet.blit(title, (pad, 12))

    def draw_row(cols, y):
        x = pad
        for label, panel in cols:
            lab = small.render(label, True, (210, 206, 196))
            sheet.blit(lab, (x, y))
            sheet.blit(panel, (x, y + label_h))
            x += panel.get_width() + pad

    draw_row(cols_top, title_h + pad)
    draw_row(cols_bot, title_h + pad + row1_h + pad)

    out = "docs/store_redesign/costume/skeleton/design_4/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
