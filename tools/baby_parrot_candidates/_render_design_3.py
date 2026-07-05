"""Render the BIG-EYES (design_3) round-1 review sheet.

Hero shot + day gameplay + night gameplay + 40px NEAREST truth-reads on BOTH a
bright day sky and a deep night sky (the day read is the make-or-break for this
skin). Exploration harness only — composites with the shared ninja_render panels
so the previews match the production capture path.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from game import biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from tools.ninja_render import hero_panel, FRAME_IDX, TILT
from tools.baby_parrot_candidates.design_3 import build as BUILD


FONT = pygame.font.SysFont("dejavusans", 15, bold=True)
FONT_SM = pygame.font.SysFont("dejavusans", 12)


def _label(surf, text, x, y, color=(240, 240, 245)):
    surf.blit(FONT.render(text, True, (0, 0, 0)), (x + 1, y + 1))
    surf.blit(FONT.render(text, True, color), (x, y))


def _gameplay(phase, w, h):
    """A Pip-over-biome crop at an arbitrary phase (ninja_render's gameplay_panel
    is day-only, so the night crop is built here with the same recipe)."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(phase)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, 0), (0, 0))
    for bx, by, sc, v in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=v)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 96, 270
    frame = BUILD(FRAME_IDX, TILT)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = min(int(GH * 0.78), GH)
    crop_w = min(int(crop_h * w / h), GW)
    crop_h = min(crop_h, int(crop_w * h / w))
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def _truth_read(sky_rgb, target=40):
    """Pip downscaled to ~target px with NEAREST onto a flat sky swatch — the
    honest 'does it read in motion' test. Returns a tile with the swatch behind
    the bird at three frames so the wing-flap read is visible."""
    pad = 10
    tile_w = pad * 2 + target * 3 + 16
    tile = pygame.Surface((tile_w, target + pad * 2), pygame.SRCALPHA)
    tile.fill((*sky_rgb, 255))
    x = pad
    for fi in (0, 2, 3):
        frame = BUILD(fi, 0.0)
        bb = frame.get_bounding_rect()
        frame = frame.subsurface(bb).copy()
        sw, sh = frame.get_size()
        scale = target / max(sw, sh)
        small = pygame.transform.scale(
            frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
        tile.blit(small, small.get_rect(center=(x + target // 2, target // 2 + pad)))
        x += target + 8
    return tile


def main():
    out = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..",
        "docs", "store_redesign", "parrot", "baby_parrot", "design_3", "round_1.png"))
    os.makedirs(os.path.dirname(out), exist_ok=True)

    W, H = 880, 560
    sheet = pygame.Surface((W, H))
    sheet.fill((26, 24, 34))

    _label(sheet, "BABY PARROT · design_3 · BIG-EYES  (round 1)", 20, 14,
           (255, 232, 180))
    _label(sheet, "neoteny dialed to 11 — giant glossy eyes inside the aviators",
           20, 36, (190, 210, 200))

    # Hero shot (clean product card).
    hero = hero_panel(BUILD, 300, frame_idx=FRAME_IDX, tilt=0.0, bg=(30, 40, 44))
    sheet.blit(hero, (20, 64))
    _label(sheet, "HERO", 28, 70)

    # Day + night gameplay crops.
    gp_day = _gameplay(0.0, 250, 250)
    gp_night = _gameplay(0.64, 250, 250)
    sheet.blit(gp_day, (340, 64))
    _label(sheet, "DAY gameplay", 348, 70)
    sheet.blit(gp_night, (606, 64))
    _label(sheet, "NIGHT gameplay", 614, 70)

    # 40px NEAREST truth-reads — the make-or-break, day FIRST.
    y = 360
    _label(sheet, "40px truth-read (NEAREST, wing frames 0 / 2 / 3)", 20, y - 6,
           (255, 220, 160))

    day_sky = (150, 200, 240)          # bright mid-day sky — the wash-out test
    night_sky = (12, 14, 40)           # deep night sky
    tr_day = _truth_read(day_sky)
    tr_night = _truth_read(night_sky)

    sheet.blit(tr_day, (40, y + 24))
    _label(sheet, "DAY sky  (make-or-break: eyes must not wash out)",
           40, y + 24 + tr_day.get_height() + 4, (210, 230, 245))
    sheet.blit(tr_night, (40, y + 110))
    _label(sheet, "NIGHT sky", 40, y + 110 + tr_night.get_height() + 4,
           (210, 220, 245))

    # A 2x-blown NEAREST of one day-read so the lens-eye contrast is judgeable.
    big = BUILD(2, 0.0)
    bb = big.get_bounding_rect()
    big = big.subsurface(bb).copy()
    bs = pygame.transform.scale(big, (bb.width * 2, bb.height * 2))
    panel = pygame.Surface(bs.get_size())
    panel.fill(day_sky)
    panel.blit(bs, (0, 0))
    sheet.blit(panel, (W - panel.get_width() - 30, y + 24))
    _label(sheet, "2x detail / day", W - panel.get_width() - 30,
           y + 24 + panel.get_height() + 4, (210, 230, 245))

    pygame.image.save(sheet, out)
    print(out)


if __name__ == "__main__":
    main()
