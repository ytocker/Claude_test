"""Compose the design_4 (SMOKE PHANTOM) ROUND 2 review sheet. Scratch only.

Same shared harness as round 1 (hero + gameplay + 40px NEAREST truth read +
4-frame filmstrip); only the output path and round caption change.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools import ninja_render as nr
from tools.ninja_candidates.design_4 import build

CONCEPT = "design_4 - SMOKE PHANTOM (Mystic Shadow-Clone Ninja, LEGENDARY) - ROUND 2"
BG = (18, 16, 26)
CARD = (28, 24, 40)
INK = (236, 230, 250)
SUB = (150, 140, 175)
ACCENT = (123, 63, 228)

pygame.font.init()
F_TITLE = pygame.font.SysFont("DejaVu Sans", 22, bold=True)
F_LABEL = pygame.font.SysFont("DejaVu Sans", 15, bold=True)
F_SMALL = pygame.font.SysFont("DejaVu Sans", 12)


def text(surf, s, pos, font=F_LABEL, color=INK):
    surf.blit(font.render(s, True, color), pos)


def truth_read_40(source):
    """40px NEAREST-neighbor downscale of the mid pose, magnified 3x with the
    pixels intact — the 'does it survive shrink' read. Drawn on both the dark
    card and a daytime-sky swatch (where it actually ships)."""
    frame = nr._frame(source, nr.FRAME_IDX, nr.TILT)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = 40 / max(sw, sh)
    small = pygame.transform.smoothscale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    big = pygame.transform.scale(
        small, (small.get_width() * 3, small.get_height() * 3))  # nearest
    return small, big


def sky_swatch(w, h):
    """A daytime-sky tile to drop the truth-read onto, so the silhouette read
    is judged against the bright background it actually faces."""
    from game import biome
    from game.draw import get_sky_surface_biome
    from game.config import W as GW, H as GH, GROUND_Y
    pal = biome.palette_for_phase(0.0)
    sky = get_sky_surface_biome(GW, GH, GROUND_Y, pal, 0)
    return pygame.transform.smoothscale(
        sky.subsurface(pygame.Rect(0, 40, GW, 80)).copy(), (w, h))


def filmstrip_cell(source, frame_idx, cell):
    """One flap frame on a flat panel, scaled to fit, to show smoke/clone motion."""
    panel = pygame.Surface((cell, cell), pygame.SRCALPHA)
    pygame.draw.rect(panel, (22, 18, 32), panel.get_rect(), border_radius=8)
    frame = nr._frame(source, frame_idx, 0.0)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = (cell * 0.82) / max(sw, sh)
    frame = pygame.transform.smoothscale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    panel.blit(frame, frame.get_rect(center=(cell // 2, cell // 2)))
    return panel


def main():
    W, H = 1240, 720
    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    text(sheet, CONCEPT, (28, 18), F_TITLE, INK)
    text(sheet, "Exploration only - live skin_ninja untouched, not in BUILDERS",
         (28, 48), F_SMALL, SUB)
    pygame.draw.line(sheet, ACCENT, (28, 70), (W - 28, 70), 2)

    # ── HERO (clean product shot) ──
    hero_box = 300
    hero = nr.hero_panel(build, hero_box, frame_idx=nr.FRAME_IDX, tilt=0.0,
                         bg=CARD)
    sheet.blit(hero, (28, 90))
    text(sheet, "HERO", (28, 90 + hero_box + 6))

    # ── IN-GAMEPLAY ── (portrait, matching the 360x640 virtual canvas)
    gp_w, gp_h = 215, 320
    gp = nr.gameplay_panel(build, gp_w, gp_h)
    rounded = pygame.Surface((gp_w, gp_h), pygame.SRCALPHA)
    pygame.draw.rect(rounded, (255, 255, 255, 255), rounded.get_rect(),
                     border_radius=14)
    gp_clip = pygame.Surface((gp_w, gp_h), pygame.SRCALPHA)
    gp_clip.blit(gp, (0, 0))
    gp_clip.blit(rounded, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sheet.blit(gp_clip, (348, 90))
    text(sheet, "IN GAMEPLAY", (348, 90 + gp_h + 6))

    # ── 40px TRUTH READ ── (×3 — dark card, daytime sky, raw actual-size)
    small, big = truth_read_40(build)
    tx = 348 + gp_w + 40
    pygame.draw.rect(sheet, CARD, (tx, 90, 220, gp_h), border_radius=14)
    # On the dark card.
    sheet.blit(big, big.get_rect(center=(tx + 110, 90 + 95)))
    # On a daytime-sky swatch (the real ship background).
    sw_w, sw_h = big.get_width() + 16, big.get_height() + 16
    swatch = sky_swatch(sw_w, sw_h)
    swatch.blit(big, big.get_rect(center=(sw_w // 2, sw_h // 2)))
    sheet.blit(swatch, swatch.get_rect(center=(tx + 110, 90 + 215)))
    # Raw actual-size (the literal 40px).
    sheet.blit(small, (tx + 14, 90 + 215 - small.get_height() // 2))
    text(sheet, "40px TRUTH READ x3", (tx + 12, 90 + gp_h + 6))
    text(sheet, "(card / day-sky / actual-size)", (tx + 12, 90 + gp_h + 26),
         F_SMALL, SUB)

    # ── FILMSTRIP (4 flap frames — breathing teleport: smoke / clone / glow) ──
    strip_y = 470
    pygame.draw.line(sheet, (60, 54, 80), (28, strip_y - 12),
                     (W - 28, strip_y - 12), 1)
    text(sheet, "4-FRAME FILMSTRIP - breathing teleport: smoke / clone / eye pulse",
         (28, strip_y - 8))
    cell = 180
    labels = ["wing up", "mid-up", "level", "down"]
    for i in range(4):
        cx = 28 + i * (cell + 14)
        cell_surf = filmstrip_cell(build, i, cell)
        sheet.blit(cell_surf, (cx, strip_y + 18))
        text(sheet, f"frame {i} ({labels[i]})", (cx + 6, strip_y + 18 + cell + 2),
             F_SMALL, SUB)

    out = "/home/user/skybit/docs/store_redesign/costume/ninja/design_4/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("SAVED", out)


if __name__ == "__main__":
    main()
