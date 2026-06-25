"""Compose the v4 design_2 (BOLD CARTOON BONE + CLOAK) round_6 review sheet.

Round_6 is the focused ribcage refinement the art-director gated round_5 on:
the dark rib gaps now carry all the way UP to within ~1px of the spine (every
rib individuated top-to-bottom, no fused top slab), each rib has a stronger
front-biased C-curve so the cage reads as a basket not a ladder, the gap rhythm
is evened, and the front ribs converge on a single deep sternum/keel point so
the cage bottom reads as a boat hull. The bottom dark moat (cage/pelvis split)
is frozen from round_5.

Panels: DAY + NIGHT in-gameplay hero, a >=9x TORSO ZOOM so the cage geometry is
auditable bone-by-bone, and the 40px NEAREST truth read on BOTH skies (the cage
must survive as a rib-ladder at thumbnail size).
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from game import biome
from game.draw import (get_sky_surface_biome, draw_mountains, draw_ground,
                       draw_cloud)
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from game.store_skins import COMPOSITE_W, COMPOSITE_H, PARROT_DY
from tools import ninja_render as NR
from tools.skeleton_candidates.v4_design_2 import build, _paint, _flesh_base

OUT = "docs/store_redesign/costume/skeleton/v4/design_2/round_6.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

font = pygame.font.SysFont("Arial", 16, bold=True)
small = pygame.font.SysFont("Arial", 13)


def label(surf, text, x, y, color=(235, 240, 250)):
    surf.blit(small.render(text, True, color), (x, y))


def gameplay_panel_phase(source, w, h, phase, clouds=True):
    """Pip mid-flight over a real biome scene at the given day/night phase."""
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
    frame = source(2, 10.0)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def torso_zoom(zoom, bg):
    """A >=9x NEAREST zoom of the un-rotated composite torso (the chest region)
    so the rebuilt ribcage is auditable rib-by-rib. Painted directly onto the
    flesh base (no rotozoom) so the bone geometry isn't blurred."""
    comp = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    comp.blit(_flesh_base(10.0), (0, PARROT_DY))
    _paint(comp, 10.0)
    # Chest window in native 64x100 composite coords (spine/keel/cage live
    # roughly y 43..68, x 18..46). Pad for context.
    win = pygame.Rect(14, 36, 40, 40)
    sub = comp.subsurface(win).copy()
    big = pygame.transform.scale(sub, (win.w * zoom, win.h * zoom))
    panel = pygame.Surface(big.get_size())
    panel.fill(bg)
    panel.blit(big, (0, 0))
    return panel


def truth_read(bg):
    """40px NEAREST downscale, upscaled x5, on a sky-coloured plate."""
    src = build(2, 10.0)
    tw, th = src.get_size()
    h40 = max(1, int(40 * th / tw))
    t40 = pygame.transform.scale(src, (40, h40))
    big = pygame.transform.scale(t40, (200, h40 * 5))
    plate = pygame.Surface((216, h40 * 5 + 16))
    plate.fill(bg)
    plate.blit(big, (8, 8))
    return plate, h40


# ── panels ───────────────────────────────────────────────────────────────────
hero = NR.hero_panel(build, 300, bg=(16, 18, 30))
day = gameplay_panel_phase(build, 200, 360, 0.0)
night = gameplay_panel_phase(build, 200, 360, 0.5)
zoom = torso_zoom(10, (10, 11, 18))           # 10x torso audit
day_truth, h40 = truth_read((120, 175, 210))
night_truth, _ = truth_read((20, 22, 40))


# ── compose ──────────────────────────────────────────────────────────────────
W, H = 1180, 760
sheet = pygame.Surface((W, H))
sheet.fill((10, 11, 18))
sheet.blit(font.render(
    "v4 SKELETON · design_2 R6 — RIBCAGE refined (gaps to spine, front-biased C-curves, even rhythm, single sternum)",
    True, (250, 252, 255)), (16, 12))

# Hero (left).
sheet.blit(hero, (16, 44))
label(sheet, "HERO — cloaked skeleton, new basket ribcage", 16, 348)

# Day gameplay.
sheet.blit(day, (330, 44))
label(sheet, "DAY gameplay", 330, 410)

# Night gameplay.
sheet.blit(night, (540, 44))
label(sheet, "NIGHT gameplay (navy)", 540, 410)

# Torso zoom (right block).
sheet.blit(zoom, (760, 44))
label(sheet, "TORSO ZOOM 10x (NEAREST) — audit: spine top, 6 even rib arcs,",
      760, 44 + zoom.get_height() + 4)
label(sheet, "keel bottom-front, dark gaps between ribs, dark moat to pelvis",
      760, 44 + zoom.get_height() + 20)

# 40px truth reads, both skies.
ty = 470
sheet.blit(day_truth, (16, ty))
label(sheet, "40px TRUTH READ — day sky (x5 nearest): cage = rib-ladder?",
      16, ty + h40 * 5 + 20)
sheet.blit(night_truth, (330, ty))
label(sheet, "40px TRUTH READ — night navy (x5 nearest): cage survives?",
      330, ty + h40 * 5 + 20)

pygame.image.save(sheet, OUT)
print("wrote", OUT, sheet.get_size())
