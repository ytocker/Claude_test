"""Review sheet for design_5 · BINKY (BABY-PARROT exploration), round 2.

Round 2 is a SUBTRACTION pass — ONE pink hero (pacifier ring-with-hole), a LIGHT
baby face, restored eye-domes, a quiet cream bib. The 40px row is the gate, and
the NIGHT reads MUST sit on real navy biome sky (R1's night chip was on bright
blue — invalid), so the night truth-read background is sampled straight from the
NIGHT palette sky surface at the bird's vertical band.

Headless: SDL_VIDEODRIVER=dummy python tools/render_baby_parrot_design_5_r2.py
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
from tools import ninja_render
from tools.baby_parrot_candidates.design_5 import build

OUT = "/home/user/skybit/docs/store_redesign/parrot/baby_parrot/design_5/round_2.png"
FONT = pygame.font.SysFont("DejaVuSans", 15, bold=True)
SMALL = pygame.font.SysFont("DejaVuSans", 12)

# Distinct sky-cache buckets per phase. get_sky_surface_biome caches by
# (w, h, phase_bucket) ONLY, so day and night must pass different buckets or the
# first-built sky is reused for both (the bug that made R1's night chip read as
# bright-blue day sky).
DAY_PHASE, DAY_BUCKET = 0.0, 0
NIGHT_PHASE, NIGHT_BUCKET = 0.64375, 41   # real NIGHT — navy sky_top (5,8,30)


def _sky_sample(phase, bucket, y):
    """The actual sky colour the bird flies on at phase/row y — so the truth-read
    chip background is the real biome sky, not a hand-picked swatch."""
    pal = biome.palette_for_phase(phase)
    sky = get_sky_surface_biome(GW, GH, GROUND_Y, pal, bucket)
    return sky.get_at((GW // 2, y))[:3]


def gameplay_panel_phase(source, w, h, phase, bucket, *, frame_idx=2, tilt=10.0):
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(phase)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, bucket), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 96, 270
    frame = source(frame_idx, tilt)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = min(int(crop_h * w / h), GW)
    crop_h = min(crop_h, GH)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def truth_read(source, bg, frame_idx=2, tilt=10.0):
    tile = pygame.Surface((40, 40), pygame.SRCALPHA)
    tile.fill(bg)
    frame = source(frame_idx, tilt)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = 36 / max(sw, sh)
    frame = pygame.transform.scale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    tile.blit(frame, frame.get_rect(center=(20, 20)))
    return tile


def label(surf, text, x, y, font=SMALL, color=(230, 235, 245)):
    surf.blit(font.render(text, True, color), (x, y))


# Real biome sky samples for the truth-read chips (mid-canopy band).
DAY_BG = _sky_sample(DAY_PHASE, DAY_BUCKET, 260)
NIGHT_BG = _sky_sample(NIGHT_PHASE, NIGHT_BUCKET, 260)
CARD_BG = (28, 26, 46)

W, H = 760, 560
sheet = pygame.Surface((W, H))
sheet.fill((18, 18, 26))
label(sheet, "design_5 · BINKY — BABY PARROT  R2  (ONE pink hero · light face · eye-domes · cream bib)",
      16, 12, FONT, (252, 224, 150))

pw, ph = 250, 300
day = gameplay_panel_phase(build, pw, ph, DAY_PHASE, DAY_BUCKET)
night = gameplay_panel_phase(build, pw, ph, NIGHT_PHASE, NIGHT_BUCKET)
sheet.blit(day, (16, 40))
label(sheet, "gameplay · DAY sky", 16, 344)
sheet.blit(night, (16 + pw + 12, 40))
label(sheet, "gameplay · NIGHT sky (real navy)", 16 + pw + 12, 344)

hero = ninja_render.hero_panel(build, 200, frame_idx=2, tilt=6.0)
sheet.blit(hero, (16 + 2 * (pw + 12), 40))
label(sheet, "hero · product shot", 16 + 2 * (pw + 12), 344)

label(sheet, "40px truth read (NEAREST, zoomed) — ring-with-hole + light face + eye-domes must pass:",
      16, 372, FONT)
backgrounds = [
    (DAY_BG, "day sky"),
    (NIGHT_BG, "NIGHT navy"),
    (CARD_BG, "store card"),
]
x = 16
for frame_idx in range(4):
    for bg, _name in backgrounds:
        tr = truth_read(build, bg, frame_idx=frame_idx, tilt=8.0)
        big = pygame.transform.scale(tr, (60, 60))
        sheet.blit(big, (x, 396))
        x += 64
    x += 14
label(sheet, "frame 0 | 1 | 2 | 3   (×3 real-biome backgrounds each)", 16, 460)

label(sheet, "exact 40px (no zoom):", 16, 488, SMALL)
x = 160
for bg, name in backgrounds:
    tr = truth_read(build, bg, frame_idx=2, tilt=8.0)
    sheet.blit(tr, (x, 482))
    label(sheet, name, x, 524, SMALL, (170, 178, 200))
    x += 90

os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
print("wrote", OUT)
print("DAY_BG", DAY_BG, "NIGHT_BG", NIGHT_BG)
