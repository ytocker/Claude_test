"""Drop the Faceted Crystal lamp (variant 4) into each biome
phase's sky gradient + ground band so we can see whether it
reads clearly across the day-cycle.

Output: docs/screenshots/genie_designs/alamp_4_biome_test.png

Run from repo root:
    SDL_VIDEODRIVER=dummy python -m tools.render_alamp_biome_test
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game import biome as _biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground
from tools.render_a1_lamp_variants import (
    draw_lamp_4_faceted,
    draw_color_1_teal, draw_color_2_emerald, draw_color_3_amber,
    draw_color_4_rose, draw_color_5_amethyst,
    W, H, SS, PW, PH, DISPLAY_BIG,
)


# All 5 colour variants + original cyan, all dropped against DAY biome
# (the worst-case phase) so we can pick the most readable.
COLOR_VARIANTS = [
    ("Original Cyan", draw_lamp_4_faceted),
    ("1: Teal",       draw_color_1_teal),
    ("2: Emerald",    draw_color_2_emerald),
    ("3: Amber",      draw_color_3_amber),
    ("4: Rose",       draw_color_4_rose),
    ("5: Amethyst",   draw_color_5_amethyst),
]


def render_lamp_against_sky(phase, draw_fn=draw_lamp_4_faceted):
    """Build a gameplay-shaped background at the given biome phase
    (sky gradient + mountain band + ground band) and overlay the
    Faceted Crystal lamp at gameplay scale + position."""
    # Background — use the same dimensions as the gameplay canvas
    # (360x640) so the visual ratio matches what's in-game.
    GAME_W, GAME_H = 360, 640
    GROUND_Y = 595
    bg = pygame.Surface((GAME_W, GAME_H))
    pal = _biome.palette_for_phase(phase)
    buckets = _biome.PHASE_BUCKETS
    bucket_f = (phase % 1.0) * buckets
    a = int(bucket_f) % buckets
    sky = get_sky_surface_biome(GAME_W, GAME_H, GROUND_Y, pal, a)
    bg.blit(sky, (0, 0))
    draw_mountains(bg, 0, GROUND_Y, GAME_W,
                   pal["mtn_far"], pal["mtn_near"])
    draw_ground(bg, GROUND_Y, GAME_W, GAME_H, 0,
                pal["ground_top"], pal["ground_mid"], (60, 40, 25))
    # Render the lamp at supersample + smoothscale to in-game icon
    # size (≈ 44 px tall like the current in-game icon)
    lamp_big = pygame.Surface((PW, PH), pygame.SRCALPHA)
    draw_fn(lamp_big, PW // 2, PH // 2)
    # In-game icon scale: the lamp occupies ~44 px screen height.
    # Lamp native canvas is H=104. Target screen ≈ 56 px tall so
    # the icon reads at "powerup icon" scale.
    target_h = 84   # slightly bigger than in-game so detail reads
    target_w = int(target_h * (W / H))
    lamp_small = pygame.transform.smoothscale(lamp_big,
                                              (target_w, target_h))
    # Position the lamp at roughly where a powerup would float —
    # mid-height on the right side of the canvas.
    lx = GAME_W // 2 - target_w // 2
    ly = GAME_H // 2 - target_h // 2
    bg.blit(lamp_small, (lx, ly))
    return bg


def main():
    OUT_DIR = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "docs", "screenshots", "genie_designs")
    # Compare all 6 (original + 5 colour variants) against the
    # worst-case DAY biome side by side.
    GAME_W, GAME_H = 360, 640
    cols = len(COLOR_VARIANTS)
    cell_h = GAME_H + 32
    margin = 12
    sheet_w = GAME_W * cols + margin * (cols + 1)
    sheet_h = cell_h + margin * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((22, 24, 32))
    font = pygame.font.SysFont("Arial", 17, bold=True)
    for i, (name, draw_fn) in enumerate(COLOR_VARIANTS):
        x = margin + i * (GAME_W + margin)
        y = margin
        # Use DAY phase (0.00) — the worst case for cyan crystal
        bg = render_lamp_against_sky(0.00, draw_fn=draw_fn)
        pygame.draw.rect(sheet, (60, 65, 80),
                         (x - 2, y - 2, GAME_W + 4, GAME_H + 4), 2)
        sheet.blit(bg, (x, y))
        label = font.render(name, True, (240, 240, 240))
        sheet.blit(label, (x + (GAME_W - label.get_width()) // 2,
                            y + GAME_H + 4))
    out = os.path.join(OUT_DIR, "colorlamp_day_biome_test.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
