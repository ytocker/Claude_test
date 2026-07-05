"""Scratch round-2 sheet for TEMPEST CONDOR MACAW (design_4).

Hero product-shot + gameplay panel + 4-frame flap filmstrip + 40px NEAREST
truth-reads on day AND night, PLUS a day 40px crop with the additive bloom
DISABLED to prove the legendary halo ring reads hard on bright blue.
Exploration only.
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
from tools.ninja_render import hero_panel

import importlib.util
spec = importlib.util.spec_from_file_location(
    "tempest_design_4",
    os.path.join(os.path.dirname(__file__), "parrot_wave2_candidates", "design_4.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
build = mod.build

# A second getter instance built with the additive bloom OFF, so the proof crop
# shows ONLY the hard opaque shapes (the legendary day read must not lean on the
# additive layer that does nothing on bright blue).
mod._ADDITIVE = False
build_noadd = mod._tempest_getter()
mod._ADDITIVE = True

NIGHT_PHASE = 0.64375
DAY_SKY = (118, 196, 232)
NIGHT_SKY = (24, 30, 58)


def _gameplay_panel_phase(src, w, h, phase, frame_idx=2, tilt=10.0):
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(phase)
    bucket = biome.phase_bucket(phase)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, bucket), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 96, 270
    frame = src(frame_idx, tilt)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = min(int(crop_h * w / h), GW)
    crop_h = min(crop_h, GH)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def _truth_read(src, bg, frame_idx=2, tilt=8.0, size=40):
    tile = pygame.Surface((size + 24, size + 24), pygame.SRCALPHA)
    tile.fill(bg)
    frame = src(frame_idx, tilt)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = size / max(sw, sh)
    small = pygame.transform.scale(frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    tile.blit(small, small.get_rect(center=(tile.get_width() // 2, tile.get_height() // 2)))
    return tile


def _label(surf, text, x, y, color=(232, 240, 246)):
    f = pygame.font.SysFont("arial", 15, bold=True)
    surf.blit(f.render(text, True, (0, 0, 0)), (x + 1, y + 1))
    surf.blit(f.render(text, True, color), (x, y))


W, H = 1180, 780
sheet = pygame.Surface((W, H))
sheet.fill((34, 38, 48))

_label(sheet, "TEMPEST CONDOR MACAW — LEGENDARY  ·  round 2", 24, 16, (140, 230, 244))

# Row 1: hero product-shot (dark + day-tinted), gameplay day, gameplay night.
hero_dark = hero_panel(build, 300, frame_idx=2, tilt=0.0, bg=(20, 26, 36))
hero_day = hero_panel(build, 300, frame_idx=2, tilt=0.0, bg=(96, 168, 210))
sheet.blit(hero_dark, (24, 52))
sheet.blit(hero_day, (336, 52))
_label(sheet, "HERO (storm-dark)", 30, 56)
_label(sheet, "HERO (day-tint)", 342, 56)

gp_day = _gameplay_panel_phase(build, 244, 300, 0.0)
gp_night = _gameplay_panel_phase(build, 244, 300, NIGHT_PHASE)
sheet.blit(gp_day, (648, 52))
sheet.blit(gp_night, (904, 52))
_label(sheet, "GAMEPLAY — DAY", 654, 56)
_label(sheet, "GAMEPLAY — NIGHT", 910, 56)

# Row 2: 4-frame flap filmstrip on day, then on night, side by side.
fy = 388
_label(sheet, "FLAP CYCLE — DAY (halo arc + forked streamer alive across frames)", 24, fy)
_label(sheet, "FLAP CYCLE — NIGHT", 604, fy)
cell = 138
for i in range(4):
    for col, (sky, bx0) in enumerate(((DAY_SKY, 24), (NIGHT_SKY, 604))):
        tile = pygame.Surface((cell, cell), pygame.SRCALPHA)
        tile.fill(sky)
        frame = build(i, 6.0)
        bb = frame.get_bounding_rect()
        fr = frame.subsurface(bb).copy()
        sw, sh = fr.get_size()
        sc = (cell * 0.92) / max(sw, sh)
        fr = pygame.transform.smoothscale(fr, (int(sw * sc), int(sh * sc)))
        tile.blit(fr, fr.get_rect(center=(cell // 2, cell // 2)))
        sheet.blit(tile, (bx0 + i * (cell + 4), fy + 24))

# Row 3: 40px NEAREST truth-reads, day + night, PLUS the additive-OFF day proof.
ty = 580
_label(sheet, "40px TRUTH-READS (NEAREST · the in-motion make-or-break)", 24, ty)
truths = [
    (build, DAY_SKY, 2, 8.0, "day f2"),
    (build, DAY_SKY, 0, -6.0, "day f0"),
    (build_noadd, DAY_SKY, 2, 8.0, "day f2 · NO additive"),
    (build, NIGHT_SKY, 2, 8.0, "night f2"),
    (build, NIGHT_SKY, 3, -6.0, "night f3"),
]
tx = 24
for src, bg, fi, tl, name in truths:
    t = _truth_read(src, bg, frame_idx=fi, tilt=tl)
    big = pygame.transform.scale(t, (t.get_width() * 2, t.get_height() * 2))
    sheet.blit(big, (tx, ty + 26))
    hi = (255, 224, 120) if "NO additive" in name else (210, 220, 228)
    _label(sheet, name, tx, ty + 26 + big.get_height(), hi)
    tx += big.get_width() + 24

out = os.path.join(os.path.dirname(__file__), "..", "docs", "store_redesign",
                   "parrot", "wave2", "design_4", "round_2.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("wrote", out)
