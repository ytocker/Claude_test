"""Render the BIG-EYES (design_3) round-2 polish review sheet.

The DAY 40px read is the verdict, so this sheet foregrounds it: a prominent DAY
head closeup up top, the hero + day/night gameplay, then the 40px NEAREST truth-
reads on BOTH skies (day first). Exploration harness only — composites with the
shared ninja_render panels so the previews match the production capture path.
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


def _head_closeup(sky_rgb, frame_idx, box, zoom=8):
    """A NEAREST-zoomed crop tight on the face over a flat sky swatch — the day
    version is the verdict, so it gets the most pixels. Crops to the head region
    of the native sprite, then nearest-scales so the lens contrast is judgeable
    without the smoothscale that the product card applies."""
    frame = BUILD(frame_idx, 0.0)
    # Head/lens region in composite space (base blit at y=PARROT_DY → lenses ~y40).
    crop = pygame.Rect(40, 26, 30, 26)
    crop.clamp_ip(frame.get_rect())
    head = frame.subsurface(crop).copy()
    big = pygame.transform.scale(head, (crop.w * zoom, crop.h * zoom))
    panel = pygame.Surface((box, box))
    panel.fill(sky_rgb)
    panel.blit(big, big.get_rect(center=(box // 2, box // 2)))
    pygame.draw.rect(panel, (0, 0, 0), panel.get_rect(), 1)
    return panel


def _truth_read(sky_rgb, target=40):
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
        "docs", "store_redesign", "parrot", "baby_parrot", "design_3", "round_2.png"))
    os.makedirs(os.path.dirname(out), exist_ok=True)

    day_sky = (150, 200, 240)          # bright mid-day sky — the wash-out test
    night_sky = (12, 14, 40)           # deep night sky

    W, H = 900, 640
    sheet = pygame.Surface((W, H))
    sheet.fill((26, 24, 34))

    _label(sheet, "BABY PARROT · design_3 · BIG-EYES  (round 2 — polish)", 20, 14,
           (255, 232, 180))
    _label(sheet, "darker lens floor + dome keyline + body one step down + sage "
           "silhouette edge", 20, 36, (190, 210, 200))

    # DAY head closeups across the three flap frames — THE VERDICT, up top + big.
    _label(sheet, "DAY head closeup (NEAREST 8x)  — verdict: dark floor / hard "
           "dome / dark pupil / aqua rim, all 3 frames", 20, 62, (255, 220, 160))
    bx = 20
    for fi in (0, 2, 3):
        cu = _head_closeup(day_sky, fi, 200, zoom=7)
        sheet.blit(cu, (bx, 86))
        _label(sheet, f"frame {fi}", bx + 6, 86 + 200 - 22, (20, 30, 50))
        bx += 210

    # Hero + day/night gameplay row.
    row_y = 300
    hero = hero_panel(BUILD, 200, frame_idx=FRAME_IDX, tilt=0.0, bg=(30, 40, 44))
    sheet.blit(hero, (20, row_y))
    _label(sheet, "HERO", 28, row_y + 6)
    gp_day = _gameplay(0.0, 200, 200)
    gp_night = _gameplay(0.64, 200, 200)
    sheet.blit(gp_day, (240, row_y))
    _label(sheet, "DAY gameplay", 248, row_y + 6)
    sheet.blit(gp_night, (460, row_y))
    _label(sheet, "NIGHT gameplay", 468, row_y + 6)

    # A 2x-blown NEAREST day-read so the full-body lens contrast is judgeable.
    big = BUILD(2, 0.0)
    bb = big.get_bounding_rect()
    big = big.subsurface(bb).copy()
    bs = pygame.transform.scale(big, (bb.width * 2, bb.height * 2))
    panel = pygame.Surface(bs.get_size())
    panel.fill(day_sky)
    panel.blit(bs, (0, 0))
    sheet.blit(panel, (W - panel.get_width() - 24, row_y))
    _label(sheet, "2x detail / day", W - panel.get_width() - 24,
           row_y + bs.get_height() + 4, (210, 230, 245))

    # 40px NEAREST truth-reads — day FIRST.
    y = 520
    _label(sheet, "40px truth-read (NEAREST, wing frames 0 / 2 / 3)", 20, y - 6,
           (255, 220, 160))
    tr_day = _truth_read(day_sky)
    tr_night = _truth_read(night_sky)
    sheet.blit(tr_day, (40, y + 20))
    _label(sheet, "DAY sky (make-or-break)", 40,
           y + 20 + tr_day.get_height() + 2, (210, 230, 245))
    sheet.blit(tr_night, (320, y + 20))
    _label(sheet, "NIGHT sky", 320, y + 20 + tr_night.get_height() + 2,
           (210, 220, 245))

    pygame.image.save(sheet, out)
    print(out)


if __name__ == "__main__":
    main()
