"""Compose the v4 design_4 (IVORY ANATOMICAL · cloak) round_4 sheet (scratch).

R4 brief (art-director ITERATE on r3): the hooded open-front cloak read in the
hero but collapsed to a dark blob at 40px and the clasp was lost. This round:
  • clasp relocated DOWN into the dark open chest gap (off the bright bones) with
    a dark ring + cream tick so a ~2px ivory toggle survives at 40px;
  • a near-black warm `inner` backs the widened open front so three BOLD ivory
    ribs win the opening at 40px;
  • lifted warm-brown `cloth` + warm tan `edge` so the (base-provided) hood arc +
    tattered hem teeth read on both day and night;
  • the truth-read strip is rebuilt as clearly SPACED 40px tiles (day AND night),
    and the hero panel is ~1.3× larger — r3's tiles overlapped into one cluster.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools import ninja_render as NR
from tools.skeleton_candidates.v4_design_4 import build
from game import biome
from game.draw import get_sky_surface_biome, draw_ground, draw_mountains, draw_cloud
from game.entities import Pipe


def gameplay_panel_phase(source, w, h, phase):
    """Same crop/scene as NR.gameplay_panel but at an arbitrary biome phase so a
    genuine NIGHT scene (not a flat navy fill) judges the cloak after dark."""
    GW, GH, GROUND_Y = NR.GW, NR.GH, NR.GROUND_Y
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
    frame = NR._frame(source, NR.FRAME_IDX, NR.TILT)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


OUT = "docs/store_redesign/costume/skeleton/v4/design_4/round_4.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

font = pygame.font.SysFont("dejavusans", 16, bold=True)
small = pygame.font.SysFont("dejavusans", 13)
tiny = pygame.font.SysFont("dejavusans", 11, bold=True)


def label(surf, text, x, y, col=(245, 240, 225), f=small):
    surf.blit(f.render(text, True, (10, 10, 14)), (x + 1, y + 1))
    surf.blit(f.render(text, True, col), (x, y))


def truth_tile(phase, scale=40, up=6):
    """A 40px-tall costume, composited onto its own biome sky chip so the cloak
    is judged against a real day/night background, then NEAREST-upscaled ×up."""
    src = build(2, 10.0)
    bb = src.get_bounding_rect()
    src = src.subsurface(bb).copy() if bb.width else src
    sw, sh = src.get_size()
    tw = max(1, int(scale * sw / sh))
    t = pygame.transform.scale(src, (tw, scale))
    # tiny biome sky chip behind it (real day/night colour, not flat fill)
    pal = biome.palette_for_phase(phase)
    pad = 6
    chip = pygame.Surface((tw + pad * 2, scale + pad * 2))
    chip.blit(pygame.transform.smoothscale(
        get_sky_surface_biome(NR.GW, NR.GH, NR.GROUND_Y, pal, 0),
        chip.get_size()), (0, 0))
    chip.blit(t, (pad, pad))
    cw, ch = chip.get_size()
    return pygame.transform.scale(chip, (cw * up, ch * up))   # nearest upscale


# ── panels ───────────────────────────────────────────────────────────────────
# Hero ~1.3× larger than r3 (360 → 468) so the cloak detail is clearly judged.
hero = NR.hero_panel(build, 468)
day = gameplay_panel_phase(build, 230, 470, 0.0)
night = gameplay_panel_phase(build, 230, 470, 0.6)
truth_day = truth_tile(0.0)
truth_night = truth_tile(0.6)

# ── compose sheet ────────────────────────────────────────────────────────────
SW, SH = 1400, 620
sheet = pygame.Surface((SW, SH))
sheet.fill((30, 26, 22))   # warm museum-plate background

sheet.blit(font.render("v4 SKELETON · design_4 — IVORY ANATOMICAL · CLOAK  ·  round_4",
                       True, (244, 234, 206)), (16, 12))
label(sheet, "R4 · clasp moved into the dark open chest (dark ring + cream tick, ~2px@40) · "
             "near-black cloak interior so 3 BOLD ribs win the open front · lifted warm-brown "
             "cloth + tan hood/hem-teeth rim read on day & night", 16, 36)

# Hero (large product shot).
hx, hy = 16, 62
sheet.blit(hero, (hx, hy))
label(sheet, "HERO — hooded cloak (peaked cowl + tattered hem) + bone-cord clasp + ivory bones",
      hx, hy + 468 + 4)

# Day + night gameplay, side by side, clearly to the right of the hero.
gx = hx + 468 + 24
sheet.blit(day, (gx, hy))
label(sheet, "DAY gameplay", gx, hy + 470 + 4)
sheet.blit(night, (gx + 230 + 16, hy))
label(sheet, "NIGHT gameplay (phase 0.6)", gx + 230 + 16, hy + 470 + 4)

# ── 40px truth-read strip: TWO clearly-spaced tiles (day + night) ─────────────
tx = gx + 2 * (230 + 16) + 24
ty = hy
label(sheet, "40px TRUTH READ (NEAREST ×6)", tx, ty, f=tiny)
sheet.blit(truth_day, (tx, ty + 18))
label(sheet, "DAY", tx, ty + 18 + truth_day.get_height() + 2, f=tiny)
ny = ty + 18 + truth_day.get_height() + 22
sheet.blit(truth_night, (tx, ny))
label(sheet, "NIGHT", tx, ny + truth_night.get_height() + 2, f=tiny)
label(sheet, "reads: hood arc +", tx, ny + truth_night.get_height() + 20, f=tiny)
label(sheet, "tattered hem + clasp;", tx, ny + truth_night.get_height() + 34, f=tiny)
label(sheet, "skull+beak+ribs hero", tx, ny + truth_night.get_height() + 48, f=tiny)

pygame.image.save(sheet, OUT)
print("wrote", OUT, sheet.get_size())
