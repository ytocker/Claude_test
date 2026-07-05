"""Round-1 exploration sheet for design_4 · NEST-BABY (baby parrot, rare).

Leads with the 40px TRUTH-READ on BOTH skies (the north star: the woven nest
ring + peep-beak must survive the in-game downsample), then the hero close-up
(judges the twig/grass detail the crop shrinks) and the in-gameplay day panel.
Pure capture; the builder is never registered.

Run headless from repo root:
``SDL_VIDEODRIVER=dummy python tools/render_baby_parrot_design4_round1.py``.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from game import biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from game.hud import _font, _GOLD_PALE
import tools.ninja_render as nr
from tools.baby_parrot_candidates.design_4 import build as BUILD


def _scene_panel(phase, w, h, *, frame_idx=2, tilt=10.0):
    """A gameplay crop around Pip mid-flight over the biome at the given phase,
    so day (0.0) and night (0.64375) can both be captured."""
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
    frame = BUILD(frame_idx, tilt)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def _truth40(bg, target=40):
    """The bird hard-downscaled to ~`target`px with smoothscale (the real in-game
    downsample path), then blown back up NEAREST so the actual gameplay pixels are
    visible — the 'lives or dies at 40px' check. A true-size swatch sits top-right."""
    frame = BUILD(2, 8.0)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = target / max(sw, sh)
    small = pygame.transform.smoothscale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    tile = pygame.Surface((150, 150))
    tile.fill(bg)
    big = pygame.transform.scale(small, (small.get_width() * 3, small.get_height() * 3))
    tile.blit(big, big.get_rect(center=(75, 75)))
    tile.blit(small, (tile.get_width() - small.get_width() - 6, 6))
    return tile


def _filmstrip(bg):
    """All four wing frames so the nest ring + cowlick are judged across the flap."""
    cell = 120
    strip = pygame.Surface((cell * 4, cell), pygame.SRCALPHA)
    strip.fill(bg)
    for i in range(4):
        frame = BUILD(i, 6.0)
        bb = frame.get_bounding_rect()
        f = frame.subsurface(bb).copy()
        sw, sh = f.get_size()
        sc = (cell * 0.84) / max(sw, sh)
        f = pygame.transform.smoothscale(f, (int(sw * sc), int(sh * sc)))
        strip.blit(f, f.get_rect(center=(i * cell + cell // 2, cell // 2)))
        pygame.draw.line(strip, (60, 56, 72), (i * cell, 8), (i * cell, cell - 8), 1)
    return strip


# ── compose the sheet ─────────────────────────────────────────────────────────
PAD = 24
TITLE_H = 70
GP_W, GP_H = 290, 410
HERO = 290
DARK = (24, 20, 16)

t40_day = _truth40((176, 214, 240))
t40_night = _truth40((20, 24, 48))
day_panel = _scene_panel(0.0, GP_W, GP_H)
night_panel = _scene_panel(0.64375, GP_W, GP_H)
hero = nr.hero_panel(BUILD, HERO, tilt=0.0, bg=(34, 26, 20))
film_day = _filmstrip((34, 26, 20))
film_night = _filmstrip((14, 16, 30))

t40_h = t40_day.get_height()
top_h = max(GP_H, HERO)
strip_h = film_day.get_height()

row_mid_w = GP_W * 2 + HERO + PAD * 2
sheet_w = PAD * 2 + max(row_mid_w, film_day.get_width())
sheet_h = (TITLE_H + (t40_h + 24) + (top_h + PAD + 16)
           + (strip_h + 28) * 2 + PAD * 2)

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(DARK)

title = _font(28, True).render(
    "NEST-BABY · RARE · baby_parrot design_4 · round 1",
    True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 18)))
sub = _font(14, False).render(
    "still in the nest · chunky woven twig collar · wide-open coral peep-beak · big-baby eyes · down cowlick + stray twig · aviators stay",
    True, (208, 190, 160))
sheet.blit(sub, sub.get_rect(midtop=(sheet_w // 2, 46)))

lab = _font(14, True)
small = _font(12, False)

y = TITLE_H
x = PAD
sheet.blit(lab.render("40px TRUTH-READ FIRST — does the nest + peep-beak read? (day | night)",
                      True, _GOLD_PALE), (x, y - 2))
y += 18
sheet.blit(t40_day, (x, y))
x += t40_day.get_width() + PAD
sheet.blit(t40_night, (x, y))
x += t40_night.get_width() + PAD
sheet.blit(small.render("3x upscaled NEAREST of the actual", True, (208, 190, 160)), (x, y + 40))
sheet.blit(small.render("in-game ~40px smoothscale; the tiny", True, (208, 190, 160)), (x, y + 56))
sheet.blit(small.render("swatch top-right is the true pixel count.", True, (208, 190, 160)), (x, y + 72))

y += t40_h + 24
x = PAD
sheet.blit(day_panel, (x, y))
sheet.blit(lab.render("GAMEPLAY · DAY", True, _GOLD_PALE), (x + 4, y + GP_H + 4))
x += GP_W + PAD
sheet.blit(night_panel, (x, y))
sheet.blit(lab.render("GAMEPLAY · NIGHT", True, _GOLD_PALE), (x + 4, y + GP_H + 4))
x += GP_W + PAD
pygame.draw.rect(sheet, (34, 26, 20), pygame.Rect(x, y, HERO, HERO), border_radius=14)
sheet.blit(hero, (x, y))
sheet.blit(lab.render("HERO CLOSE-UP (twig + grass detail)", True, _GOLD_PALE),
           (x + 4, y + HERO + 4))

y += top_h + PAD + 16
sheet.blit(lab.render("4-FRAME FILMSTRIP · DAY", True, _GOLD_PALE), (PAD, y - 14))
sheet.blit(film_day, (PAD, y))
y += strip_h + 28
sheet.blit(lab.render("4-FRAME FILMSTRIP · NIGHT", True, _GOLD_PALE), (PAD, y - 14))
sheet.blit(film_night, (PAD, y))

out_dir = os.path.join("docs", "store_redesign", "parrot", "baby_parrot", "design_4")
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, "round_1.png")
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
