"""Round-2 review sheet for the SNUG CLOTH diaper (design_1, RE-ROLL).

R1 ran the cloth to the bottom of the silhouette and swallowed the legs. The
make-or-break read this round is two legs poking out BELOW a banded cream nappy,
so the sheet pairs a clean hero + in-gameplay panel with the 40px NEAREST
truth-reads on BOTH day and navy-night sky, plus a magnified rump crop that
isolates the band-over-legs construction so the legs-below read is checkable.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from game import biome
from tools.ninja_render import gameplay_panel, hero_panel
from tools.binky_diaper_candidates.design_1 import build as binky_build

FONT = pygame.font.SysFont("monospace", 14, bold=True)
SMALL = pygame.font.SysFont("monospace", 11)


def _label(surf, text, x, y, color=(230, 230, 240)):
    surf.blit(FONT.render(text, True, color), (x, y))


def _small(surf, text, x, y, color=(200, 200, 210)):
    surf.blit(SMALL.render(text, True, color), (x, y))


def _native_40(palette):
    """Frame at native sprite size scaled to 40px with NEAREST, then blown up so
    the per-pixel read is honest, on a flat sky-tint chip."""
    frame = binky_build(2, 10.0)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    sc = 40 / max(sw, sh)
    small = pygame.transform.scale(frame, (max(1, int(sw * sc)), max(1, int(sh * sc))))
    big = pygame.transform.scale(small, (small.get_width() * 4, small.get_height() * 4))
    return small, big


def _truth_tile(palette, label, box=200):
    small, big = _native_40(palette)
    tile = pygame.Surface((box, box))
    tile.fill(palette["sky_top"])
    tile.blit(big, big.get_rect(center=(box // 2, box // 2 - 8)))
    tile.blit(small, (box - small.get_width() - 6, 6))
    pygame.draw.rect(tile, (255, 255, 255), tile.get_rect(), 1)
    tile.blit(SMALL.render(label, True, (255, 255, 255)), (8, box - 18))
    return tile


def _legs_crop(bg=(34, 30, 44)):
    """Magnified crop of the rump/underside isolating band-over-legs: cream band
    on top, two legs poking out below, so the legs-below read is checkable."""
    frame = binky_build(2, 0.0)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy()
    fw, fh = frame.get_size()
    crop = pygame.Rect(int(fw * 0.12), int(fh * 0.46), int(fw * 0.72), int(fh * 0.52))
    crop.clamp_ip(frame.get_rect())
    sub = frame.subsurface(crop).copy()
    mag = 6
    big = pygame.transform.scale(sub, (crop.w * mag, crop.h * mag))
    panel = pygame.Surface(big.get_size())
    panel.fill(bg)
    panel.blit(big, (0, 0))
    pygame.draw.rect(panel, (255, 255, 255), panel.get_rect(), 1)
    return panel


def main():
    W, H = 1000, 640
    sheet = pygame.Surface((W, H))
    sheet.fill((28, 26, 38))
    _label(sheet, "BINKY — SNUG CLOTH diaper (design_1) — round 2 (was RE-ROLL)",
           20, 14, (255, 230, 180))

    hero = hero_panel(binky_build, 300, frame_idx=2, tilt=0.0, bg=(40, 38, 54))
    sheet.blit(hero, (20, 44))
    _label(sheet, "HERO", 20, 348)

    gp = gameplay_panel(binky_build, 210, 300)
    sheet.blit(gp, (340, 44))
    _label(sheet, "IN GAMEPLAY (day)", 340, 348)

    legs = _legs_crop()
    lx = 580
    sheet.blit(legs, (lx, 44))
    _label(sheet, "BAND-OVER-LEGS", lx, 44 + legs.get_height() + 4)
    _small(sheet, "cream band tops at hard seam; two legs poke out below", lx,
           44 + legs.get_height() + 22)

    day = biome.palette_for_phase(0.0)
    night = biome.palette_for_phase(0.64375)
    td = _truth_tile(day, "40px DAY (nearest)")
    tn = _truth_tile(night, "40px NAVY NIGHT (nearest)")
    ty = 380
    sheet.blit(td, (40, ty))
    sheet.blit(tn, (270, ty))

    _small(sheet,
           "Trim cloth band rides HIGH: lit #FFFFFF waistband + #ABA282 rib up top,",
           520, 400)
    _small(sheet,
           "powder underside arc holds navy value, hard #ABA282 seam ENDS cloth at",
           520, 418)
    _small(sheet,
           "~y61 — nothing cream below y62, so legs read clean below the band.",
           520, 436)
    _small(sheet, "Pacifier stays sole pink hero; cloth is cream-only.", 520, 462)

    out = ("/home/user/skybit/docs/store_redesign/parrot/baby_parrot/"
           "diaper_redo/design_1/round_2.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("WROTE", out)


if __name__ == "__main__":
    main()
