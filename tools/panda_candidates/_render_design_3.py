"""Round sheet for CHUBBY DUMPLING (panda design_3): day | night | hero on
top, 4-frame NEAREST strip at 40px below. Scratch render only."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import importlib.util
import pygame
pygame.init()

from game import biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y

_spec = importlib.util.spec_from_file_location(
    "panda_design_3",
    os.path.join(os.path.dirname(__file__), "design_3.py"))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
get_skin = _mod.get_skin

FRAME_IDX, TILT = 2, 10.0


def _gameplay_panel(phase, w, h):
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
    frame = get_skin(FRAME_IDX, TILT)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    # Pick the largest crop matching the panel aspect that still fits the
    # 360x640 scene (panels are tall here, so width is the binding constraint).
    aspect = w / h
    crop_w = min(GW, int(GH * 0.78 * aspect))
    crop_h = min(GH, int(crop_w / aspect))
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def _hero_panel(box, bg=(22, 20, 32)):
    panel = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.rect(panel, bg, panel.get_rect(), border_radius=14)
    frame = get_skin(FRAME_IDX, 0.0)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = (box * 0.82) / max(sw, sh)
    frame = pygame.transform.smoothscale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    panel.blit(frame, frame.get_rect(center=(box // 2, box // 2)))
    return panel


def main():
    W, H = 900, 400
    sheet = pygame.Surface((W, H))
    sheet.fill((18, 18, 24))
    font = pygame.font.SysFont("arial", 16, bold=True)
    small = pygame.font.SysFont("arial", 13)

    pad = 12
    top_h = 300
    panel_w = (W - pad * 4) // 3
    labels = ("DAY GAMEPLAY", "NIGHT GAMEPLAY", "HERO")
    panels = [
        _gameplay_panel(0.0, panel_w, top_h - 24),
        _gameplay_panel(0.62, panel_w, top_h - 24),   # deep-night phase
        _hero_panel(top_h - 24),
    ]
    # Hero panel is square; centre it in its column slot.
    x = pad
    y = pad
    for lbl, p in zip(labels, panels):
        col_w = panel_w
        sheet.blit(small.render(lbl, True, (210, 210, 220)), (x, y))
        pw, ph = p.get_size()
        sheet.blit(p, (x + (col_w - pw) // 2, y + 18))
        x += panel_w + pad

    # ── Bottom strip: 4 frames at 40px NEAREST scale.
    sy = top_h + 8
    sheet.blit(font.render("4 FRAMES @ 40px (NEAREST)", True, (235, 235, 245)),
               (pad, sy))
    fy = sy + 22
    fx = pad
    cell = 80
    for i in range(4):
        frame = get_skin(i, 0.0)
        bb = frame.get_bounding_rect()
        if bb.width and bb.height:
            frame = frame.subsurface(bb).copy()
        sw, sh = frame.get_size()
        scale = 40.0 / max(sw, sh)
        big = pygame.transform.scale(
            frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
        cellsurf = pygame.Surface((cell, cell), pygame.SRCALPHA)
        # neutral mid bg behind each frame so the white+black read is judged
        pygame.draw.rect(cellsurf, (90, 110, 130), cellsurf.get_rect(),
                         border_radius=8)
        cellsurf.blit(big, big.get_rect(center=(cell // 2, cell // 2)))
        sheet.blit(cellsurf, (fx, fy))
        sheet.blit(small.render(f"f{i}", True, (220, 220, 230)), (fx + 4, fy + cell - 18))
        fx += cell + 10

    # Title block on the right of the bottom strip.
    tx = fx + 20
    sheet.blit(font.render("CHUBBY DUMPLING", True, (255, 157, 176)), (tx, fy + 4))
    sheet.blit(small.render("Round baby panda — design_3", True, (210, 210, 220)),
               (tx, fy + 26))
    sheet.blit(small.render("One-ball silhouette, oversized ears + eye patches",
                            True, (180, 180, 190)), (tx, fy + 44))

    out = "/home/user/skybit/docs/store_redesign/animal/panda/design_3/round_2.png"
    pygame.image.save(sheet, out)
    print("saved", out)


if __name__ == "__main__":
    main()
