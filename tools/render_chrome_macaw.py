"""Round-1 exploration sheet for design_5 · CHROME MACAW (SECRET).

In-gameplay capture of the scratch chrome builder across the reads that decide a
40px-in-motion secret skin: day + night gameplay panels (chrome must reflect
either sky), a clean hero close-up, a 40px NEAREST truth-read, a 4-frame
filmstrip, plus the masked "???" locked store-card state beside the revealed
look (it's a secret — show how it appears before purchase). Pure capture; the
candidate is a scratch builder, no production art touched.

Run headless from repo root:
``SDL_VIDEODRIVER=dummy python tools/render_chrome_macaw.py``.
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
from game.hud import _font

import tools.ninja_render as nr
from tools.parrot_wave2_candidates.design_5 import build as CHROME


_GOLD = (255, 232, 168)
_INK = (16, 18, 28)


def gameplay_panel_phase(source, w, h, phase, *, frame_idx=2, tilt=10.0):
    """nr.gameplay_panel pins phase 0.0 (day); this clones it at an arbitrary
    biome phase so the same crop can be captured on the night sky too."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(phase)
    bucket = int(phase * 16)
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
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def truth_read(source, px=40):
    """The frame downscaled NEAREST to px — the brutal 'does it survive at the
    store-card size' test, then nearest-up so the pixels are visible on-sheet."""
    frame = source(2, 8.0)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy() if bb.width else frame
    sw, sh = frame.get_size()
    sc = px / max(sw, sh)
    small = pygame.transform.scale(frame, (max(1, int(sw * sc)), max(1, int(sh * sc))))
    return small, pygame.transform.scale(small, (small.get_width() * 4, small.get_height() * 4))


def _sky_swatch(phase, box):
    """A flat crop of the real biome sky at `phase`, sized `box` — the honest
    backdrop the bird must hold its value against at 40px."""
    sky = get_sky_surface_biome(GW, GH, GROUND_Y, biome.palette_for_phase(phase),
                                int(phase * 16))
    crop = sky.subsurface(pygame.Rect(40, 120, GW - 80, GW - 80)).copy()
    return pygame.transform.smoothscale(crop, (box, box))


def truth_on_sky(source, phase, scale=5):
    """The A/B check that decides ship: the bird downscaled to a 40px-tall sprite
    composited onto the REAL sky of `phase`, then nearest-up. If the night value
    floor holds, the lower body keeps a lit edge against the navy; if it fails,
    the underbelly dissolves into the sky here."""
    frame = source(2, 8.0)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy() if bb.width else frame
    sw, sh = frame.get_size()
    sc = 40 / max(sw, sh)
    bird = pygame.transform.smoothscale(frame, (max(1, int(sw * sc)), max(1, int(sh * sc))))
    box = 52
    cell = _sky_swatch(phase, box)
    cell.blit(bird, bird.get_rect(center=(box // 2, box // 2)))
    return pygame.transform.scale(cell, (box * scale, box * scale))


def masked_card(source, box):
    """The secret store-card state: a darkened silhouette of the bird with a big
    '???' — how the locked skin reads before purchase. Built from the real frame
    so the mystery silhouette is honestly this skin's shape."""
    panel = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.rect(panel, (20, 22, 36), panel.get_rect(), border_radius=14)
    pygame.draw.rect(panel, (60, 66, 92), panel.get_rect(), 2, border_radius=14)
    frame = source(2, 0.0)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy() if bb.width else frame
    sw, sh = frame.get_size()
    scale = (box * 0.74) / max(sw, sh)
    frame = pygame.transform.smoothscale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    # Darken to a near-black mystery silhouette via a per-pixel alpha-keyed mask.
    sil = frame.copy()
    sil.fill((30, 34, 52, 255), special_flags=pygame.BLEND_RGBA_MULT)
    panel.blit(sil, sil.get_rect(center=(box // 2, box // 2)))
    q = _font(64, True).render("?", True, (150, 160, 190))
    panel.blit(q, q.get_rect(center=(box // 2, box // 2)))
    return panel


# ── compose the sheet ─────────────────────────────────────────────────────────
PAD = 26
sheet_w, sheet_h = 1180, 1170
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title = _font(30, True).render(
    "CHROME MACAW — SECRET (~6000, masked ???)  ·  design_5 · ROUND 2", True, _GOLD)
sheet.blit(title, (PAD, 18))
sub = _font(14, False).render(
    "R2: night value floor +18% · bottom rim-light · 2-hue magenta/cyan ring · travelling wing hotspot + up-flap rivet pop · hard spec on rear tail-vanes",
    True, (174, 168, 196))
sheet.blit(sub, (PAD, 54))


def label(x, y, text, col=_GOLD):
    sheet.blit(_font(15, True).render(text, True, col), (x, y))


# Row 1: day gameplay | night gameplay | hero close-up
GP_W, GP_H = 300, 440
y0 = 92
label(PAD, y0, "GAMEPLAY · DAY SKY")
sheet.blit(gameplay_panel_phase(CHROME, GP_W, GP_H, 0.0), (PAD, y0 + 22))

x1 = PAD + GP_W + 20
label(x1, y0, "GAMEPLAY · NIGHT SKY")
sheet.blit(gameplay_panel_phase(CHROME, GP_W, GP_H, 0.64375), (x1, y0 + 22))

x2 = x1 + GP_W + 20
label(x2, y0, "HERO CLOSE-UP")
sheet.blit(nr.hero_panel(CHROME, GP_H, tilt=0.0, bg=(24, 26, 40)), (x2, y0 + 22))

# Row 2: 4-frame filmstrip | 40px truth-read | masked secret card
y1 = y0 + GP_H + 44
label(PAD, y1, "FLIP · 4-FRAME FILMSTRIP (flap)")
fs_box = 132
for i in range(4):
    cell = pygame.Surface((fs_box, fs_box), pygame.SRCALPHA)
    pygame.draw.rect(cell, (24, 26, 40), cell.get_rect(), border_radius=10)
    fr = CHROME(i, 6.0)
    bb = fr.get_bounding_rect()
    fr = fr.subsurface(bb).copy() if bb.width else fr
    sw, sh = fr.get_size()
    sc = (fs_box * 0.82) / max(sw, sh)
    fr = pygame.transform.smoothscale(fr, (int(sw * sc), int(sh * sc)))
    cell.blit(fr, fr.get_rect(center=(fs_box // 2, fs_box // 2)))
    sheet.blit(cell, (PAD + i * (fs_box + 8), y1 + 22))

xt = PAD + 4 * (fs_box + 8) + 16
label(xt, y1, "40px TRUTH-READ")
small, big = truth_read(CHROME, 40)
sheet.blit(_font(12, False).render("native 40px", True, (160, 154, 184)), (xt, y1 + 22))
sheet.blit(small, (xt, y1 + 40))
sheet.blit(_font(12, False).render("×4 nearest", True, (160, 154, 184)),
           (xt + small.get_width() + 16, y1 + 22))
sheet.blit(big, (xt + small.get_width() + 16, y1 + 40))

xm = xt + small.get_width() + big.get_width() + 40
label(xm, y1, "LOCKED STORE CARD (secret)")
sheet.blit(masked_card(CHROME, 200), (xm, y1 + 22))
sheet.blit(_font(13, True).render("???  ·  6000", True, (150, 160, 190)),
           (xm + 56, y1 + 22 + 206))

# Row 3: the A/B that decides ship — 40px-on-DAY-sky vs 40px-on-NIGHT-sky, so
# the night value-floor fix can be judged against the actual sky it dissolved
# into in R1. Same bird, same scale, only the backdrop changes.
y2 = y1 + 280
label(PAD, y2, "40px ON REAL SKY · DAY  vs  NIGHT  (night value-floor A/B — the ship check)")
ab_day = truth_on_sky(CHROME, 0.0)
ab_night = truth_on_sky(CHROME, 0.64375)
pygame.draw.rect(sheet, (108, 188, 252), (PAD - 2, y2 + 20, ab_day.get_width() + 4, ab_day.get_height() + 4), 2)
sheet.blit(ab_day, (PAD, y2 + 22))
sheet.blit(_font(13, True).render("DAY", True, (140, 200, 255)), (PAD + 4, y2 + 26))
nx = PAD + ab_day.get_width() + 40
pygame.draw.rect(sheet, (120, 130, 200), (nx - 2, y2 + 20, ab_night.get_width() + 4, ab_night.get_height() + 4), 2)
sheet.blit(ab_night, (nx, y2 + 22))
sheet.blit(_font(13, True).render("NIGHT", True, (170, 180, 230)), (nx + 4, y2 + 26))
note = _font(13, False).render(
    "check: underbelly + tail keep a lit edge on navy (rim-light) · ring reads as a RING not rainbow pixels · hotspot lands as one clean white",
    True, (160, 154, 184))
sheet.blit(note, (nx + ab_night.get_width() + 40, y2 + 28))

out = os.path.join("docs", "store_redesign", "parrot", "wave2", "design_5", "round_2.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
