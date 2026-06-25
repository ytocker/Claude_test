"""Render the v2_design_2 PIRATE-MACAW round-3 (final) review sheet for CAPTAIN.

CAPTAIN (``build_v2``, the art-director's lead take) shown across the four truth
columns — hero close-up, DAY gameplay, NIGHT gameplay, and a 40px NEAREST truth
read — so the C2 fixes (thin-edge tricorn rim with sharpened front/back horns,
chest X dropped to bone_sh so the cockade glint wins focal, widened 2px bone
bridge + nudged eyepatch, solid gold earring stud) are judged at both product
and gameplay size. Scratch only.

Headless:
  SDL_VIDEODRIVER=dummy PYTHONPATH=. python tools/skeleton_candidates/render_v2_design_2_r3.py
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
from tools.skeleton_candidates.v2_design_2 import build_v2

OUT = os.path.join(os.path.dirname(__file__), "..", "..",
                   "docs", "store_redesign", "costume", "skeleton", "v2",
                   "design_2", "round_3.png")


def _night_gameplay_panel(source, w, h):
    """Mirror of gameplay_panel on a deep NIGHT biome phase — the column that
    catches the tricorn vanishing into dark pillars if the rim fails."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(0.5)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, 0), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 96, 270
    frame = _frame(source, FRAME_IDX, TILT)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def _truth_read_panel(source, box):
    """The bird at ~40px, NEAREST-upscaled so the reviewer sees what actually
    reads at gameplay size, on a flat dark card."""
    frame = _frame(source, FRAME_IDX, 0.0)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = 40.0 / max(sw, sh)
    small = pygame.transform.smoothscale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    big = pygame.transform.scale(small, (box, box))
    panel = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.rect(panel, (18, 16, 22), panel.get_rect(), border_radius=10)
    panel.blit(big, big.get_rect(center=(box // 2, box // 2)))
    return panel


def main():
    title_font = pygame.font.SysFont("dejavusans", 22, bold=True)
    row_font = pygame.font.SysFont("dejavusans", 15, bold=True)
    col_font = pygame.font.SysFont("dejavusans", 13)

    pad = 16
    hbox = 220
    pw, ph = 220, 308
    tbox = 220
    label_h = 22

    col_titles = ["HERO", "DAY — gameplay", "NIGHT — gameplay", "40px TRUTH"]
    col_w = [hbox, pw, pw, tbox]
    row_h = label_h + max(hbox, ph, tbox)

    title_h = 34
    head_h = 18
    sheet_w = pad + sum(w + pad for w in col_w)
    sheet_h = title_h + head_h + pad + (row_h + pad)

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((30, 28, 38))

    sheet.blit(title_font.render(
        "SKELETON  v2_design_2  PIRATE-MACAW  CAPTAIN  round_3 (final)  "
        "(thin-edge tricorn + sharp horns / X->bone_sh / wide bone bridge / gold stud)",
        True, (244, 239, 224)), (pad, 8))

    x = pad
    for ct, w in zip(col_titles, col_w):
        sheet.blit(col_font.render(ct, True, (200, 196, 188)), (x, title_h))
        x += w + pad

    y = title_h + head_h + pad
    sheet.blit(row_font.render(
        "v2 CAPTAIN — black tricorn (thin bone edge, two upswept horns) + cockade focal",
        True, (236, 220, 200)), (pad, y - 2))
    panels = [
        hero_panel(build_v2, hbox, bg=(22, 20, 28)),
        gameplay_panel(build_v2, pw, ph),
        _night_gameplay_panel(build_v2, pw, ph),
        _truth_read_panel(build_v2, tbox),
    ]
    x = pad
    for p, w in zip(panels, col_w):
        sheet.blit(p, (x, y + label_h))
        x += w + pad

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("wrote", os.path.abspath(OUT), sheet.get_size())


if __name__ == "__main__":
    main()
