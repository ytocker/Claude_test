"""Render the AFTERBURNER (design_5) round-1 review sheet.

Legendary tier → the loudest read in the set, so it earns a full filmstrip plus
day AND night gameplay/40px truth reads (the flame must glow against night).
Headless; saves ONE combined PNG to docs/store_redesign/shoes/design_5/round_1.png.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from game import parrot, biome
from game.store_skins import _make_skin
from game.shoe_skins import _foot_paint
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from tools.shoe_candidates.design_5 import draw_shoe
import tools.ninja_render as nr

NIGHT_PHASE = 0.64375

FONT = pygame.font.SysFont("dejavusans", 15, bold=True)
SMALL = pygame.font.SysFont("dejavusans", 12)


def label(surf, text, x, y, color=(236, 240, 248)):
    surf.blit(SMALL.render(text, True, color), (x, y))


def title(surf, text, x, y, color=(255, 226, 122)):
    surf.blit(FONT.render(text, True, color), (x, y))


def big_icon():
    # The plume runs behind the heel (t<0) and the cuff above the box top, so the
    # stock _build_icon padding clips it. Render onto a roomy SRCALPHA canvas with
    # extra rear+top headroom, same draw_shoe + house outline, then crop tight.
    bw, bh = 150, 84
    pad_l, pad_r, pad_t, pad_b = 150, 40, 80, 40  # generous rear/top for plume+cuff
    surf = pygame.Surface((bw + pad_l + pad_r, bh + pad_t + pad_b), pygame.SRCALPHA)
    draw_shoe(surf, pad_l, pad_t, bw, bh, 1)
    surf = parrot._add_outline(surf)
    bb = surf.get_bounding_rect()
    return surf.subsurface(bb).copy()


def scene_panel(build, w, h, phase, frame_idx=2, tilt=10.0):
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(phase)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette,
                                     int(palette.get('star_alpha', 0))), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 96, 270
    frame = build(frame_idx, tilt)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop_w = min(crop_w, GW)
    crop_h = min(crop_h, GH)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def worn_truth(build, target_h, phase, frame_idx=2):
    # True worn read: scale the bird frame to ~target_h px with NEAREST (no
    # smoothing) so we judge what the player actually sees at gameplay scale.
    frame = build(frame_idx, 0.0)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = target_h / sh
    small = pygame.transform.scale(frame, (max(1, int(sw * scale)), target_h))
    bg = (20, 26, 40) if phase > 0.4 else (150, 200, 235)
    panel = pygame.Surface(small.get_size(), pygame.SRCALPHA)
    panel.fill(bg)
    panel.blit(small, (0, 0))
    return panel


def main():
    build = _make_skin(_foot_paint(draw_shoe))

    sheet_w, sheet_h = 1280, 980
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 22, 32))

    title(sheet, "design_5 — AFTERBURNER  ·  legendary ~4800  ·  rocket thruster boot", 24, 16)

    # ── product-shot icon (big, uncropped plume) ──
    icon = big_icon()
    iw = 520
    ih = int(icon.get_height() * iw / icon.get_width())
    icon = pygame.transform.smoothscale(icon, (iw, ih))
    icard = pygame.Surface((iw + 32, ih + 32), pygame.SRCALPHA)
    pygame.draw.rect(icard, (34, 32, 46), icard.get_rect(), border_radius=16)
    icard.blit(icon, (16, 16))
    sheet.blit(icard, (24, 52))
    title(sheet, "PRODUCT SHOT", 30, 56 + ih + 18, (200, 210, 222))

    # ── hero panel (clean bird product shot) ──
    hero = nr.hero_panel(build, 360, frame_idx=2, tilt=0.0)
    sheet.blit(hero, (600, 52))
    title(sheet, "HERO", 606, 52 + 360 - 26, (200, 210, 222))

    # ── day + night gameplay panels ──
    gp_day = scene_panel(build, 290, 360, 0.0)
    gp_night = scene_panel(build, 290, 360, NIGHT_PHASE)
    sheet.blit(gp_day, (980, 52))
    sheet.blit(gp_night, (980, 52))  # placeholder, repositioned below
    sheet.blit(gp_day, (980, 52))
    label(sheet, "GAMEPLAY · DAY", 986, 54, (255, 255, 255))

    # second row
    ry = 470
    sheet.blit(gp_night, (24, ry))
    label(sheet, "GAMEPLAY · NIGHT", 30, ry + 4, (255, 235, 180))

    # ── 4-frame filmstrip (legendary) ──
    fx = 330
    title(sheet, "FILMSTRIP (flap 0–3)", fx, ry - 24, (200, 210, 222))
    for i in range(4):
        fp = nr.hero_panel(build, 150, frame_idx=i, tilt=8.0)
        sheet.blit(fp, (fx + i * 158, ry))
        label(sheet, f"f{i}", fx + i * 158 + 6, ry + 6)

    # ── 40px NEAREST truth reads: day & night, 1x and ~4x ──
    ty = ry + 330
    title(sheet, "40px WORN TRUTH READ (nearest · 1× and 4×)", 24, ty - 26, (255, 226, 122))
    cx = 24
    for phase, tag in ((0.0, "DAY"), (NIGHT_PHASE, "NIGHT")):
        w1 = worn_truth(build, 40, phase)
        w4 = pygame.transform.scale(w1, (w1.get_width() * 4, w1.get_height() * 4))
        # 1x
        c1 = pygame.Surface((w1.get_width() + 12, w1.get_height() + 28), pygame.SRCALPHA)
        pygame.draw.rect(c1, (34, 32, 46), c1.get_rect(), border_radius=8)
        c1.blit(w1, (6, 22))
        label(c1, f"{tag} 1×", 6, 4)
        sheet.blit(c1, (cx, ty))
        # 4x
        c4 = pygame.Surface((w4.get_width() + 16, w4.get_height() + 28), pygame.SRCALPHA)
        pygame.draw.rect(c4, (34, 32, 46), c4.get_rect(), border_radius=10)
        c4.blit(w4, (8, 22))
        label(c4, f"{tag} 4×", 8, 4)
        sheet.blit(c4, (cx + c1.get_width() + 16, ty))
        cx += c1.get_width() + c4.get_width() + 60

    out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                          "..", "..", "docs", "store_redesign", "shoes",
                          "design_5", "round_1.png"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, "exists:", os.path.exists(out))


if __name__ == "__main__":
    main()
