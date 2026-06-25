"""Compose the v4 design_5 (ETCHED WOODCUT · CLOAK) round_4 review sheet (scratch).

round_4 addresses the art-director's ITERATE on round_3: the cloak was undersold
and its fold hatch collided with the bone hatch into mush. The fix is two TONAL
registers — bones stay crisp/white/fine, the cloak drape drops to a mid-grey
COARSER fold hatch over a lifted dark-cool-grey cloth, so the Dürer memento-mori
grammar (white bone over hatched dark cloak) reads cleanly. The hero panel is
enlarged ~1.4x so the bone-vs-cloth hatch separation is auditable, and the truth
read is shown at 40px NEAREST for BOTH day and night.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from game import biome
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud,
)
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y

from tools import ninja_render as NR
from tools.skeleton_candidates.v4_design_5 import build

OUT = "docs/store_redesign/costume/skeleton/v4/design_5/round_4.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

font = pygame.font.SysFont("dejavusans", 16, bold=True)
small = pygame.font.SysFont("dejavusans", 13)

FRAME_IDX = 2
TILT = 10.0
DAY_PHASE = 0.0
NIGHT_PHASE = 0.64375


def label(surf, text, x, y, col=(230, 232, 240)):
    surf.blit(small.render(text, True, (8, 8, 12)), (x + 1, y + 1))
    surf.blit(small.render(text, True, col), (x, y))


def gameplay_panel(w, h, phase):
    """Pip mid-flight over a real biome scene at a given day-cycle phase, so the
    night panel renders under a dark sky and the cloak reads on both skies."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(phase)
    bucket = int(round(phase * 64))
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, bucket), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 96, 270
    frame = build(FRAME_IDX, TILT)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop_w = min(crop_w, GW)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def truth40(phase):
    """Mid-flight frame composited over the biome sky, cropped to the bird, scaled
    to 40px wide NEAREST then x5 — the honest read on a real sky (day or night)."""
    palette = biome.palette_for_phase(phase)
    bucket = int(round(phase * 64))
    scene = pygame.Surface((GW, GH))
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, bucket), (0, 0))
    src = build(FRAME_IDX, TILT)
    bb = src.get_bounding_rect()
    src = src.subsurface(bb).copy() if bb.width else src
    cx, cy = GW // 2, GH // 3
    scene.blit(src, src.get_rect(center=(cx, cy)))
    pad = 4
    crop = pygame.Rect(0, 0, bb.width + pad * 2, bb.height + pad * 2)
    crop.center = (cx, cy)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    chip = scene.subsurface(crop).copy()
    sw, sh = chip.get_size()
    t40 = pygame.transform.scale(chip, (40, max(1, int(40 * sh / sw))))
    tw, th = t40.get_size()
    return pygame.transform.scale(t40, (tw * 5, th * 5))


# ── panels ────────────────────────────────────────────────────────────────────
# Hero enlarged ~1.4x (360 -> 500) so the bone-vs-cloth hatch separation is
# auditable side by side with the gameplay reads.
HERO = 500
hero = NR.hero_panel(build, HERO, frame_idx=FRAME_IDX, tilt=TILT, bg=(20, 16, 26))
day = gameplay_panel(220, 392, DAY_PHASE)
night = gameplay_panel(220, 392, NIGHT_PHASE)
truth_day = truth40(DAY_PHASE)
truth_night = truth40(NIGHT_PHASE)

# ── compose sheet ─────────────────────────────────────────────────────────────
SW, SH = 1340, 600
sheet = pygame.Surface((SW, SH))
sheet.fill((20, 21, 30))   # ink-plate background

sheet.blit(font.render(
    "v4 SKELETON · design_5 — ETCHED WOODCUT · CLOAK (round 4)",
    True, (236, 238, 246)), (16, 12))
label(sheet, "TWO TONAL REGISTERS: bones = crisp WHITE fine engraving · cloak = "
             "mid-grey COARSE fold-hatch over a lifted dark-cool-grey cloth · "
             "toothed hem + cowl traced in engraved keyline · ribcage tops the open V",
      16, 36)

# Hero (large product shot) — left column.
sheet.blit(hero, (16, 64))
label(sheet, "HERO (1.4x) — white bone vs darker hatched cloth, two engraving tones",
      16, 64 + HERO + 4)

col2 = 16 + HERO + 24

# Day gameplay.
sheet.blit(day, (col2, 64))
label(sheet, "DAY sky — cloak reads as hatched cloth", col2, 64 + 392 + 4)

# Night gameplay.
nx = col2 + 232
sheet.blit(night, (nx, 64))
label(sheet, "NIGHT — lifted cloth holds the drape", nx, 64 + 392 + 4)

# 40px truth reads, day + night stacked.
tx = nx + 232
sheet.blit(truth_day, (tx, 64))
label(sheet, "40px DAY (x5) — hood/hem + hero", tx, 64 + truth_day.get_height() + 2)
ty = 64 + truth_day.get_height() + 36
sheet.blit(truth_night, (tx, ty))
label(sheet, "40px NIGHT (x5) — cloth + hero", tx, ty + truth_night.get_height() + 2)

pygame.image.save(sheet, OUT)
print("wrote", OUT, sheet.get_size())
