"""Render 5 BRIGHTER / softer lighting-gradient options at 3 key biome
phases, with a REFERENCE column on the left showing the original
unlit parrot for comparison.

Produces under docs/screenshots/biome_lighting_options_v2/:
  00_grid.png — 3 rows (phases) × 6 cols (ref + F/G/H/I/J), labeled

Run:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m tools.render_lighting_options_v2
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((360, 640))

from game.config import W, H, GROUND_Y
from game import biome as _biome
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
)
from game.world import World


OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "biome_lighting_options_v2")
os.makedirs(OUT_DIR, exist_ok=True)


# 5 candidate tunings, each BRIGHTER overall than the previous A-E set.
# Gradient deltas vary: F = barely-there, J = max top brightness.
OPTIONS = [
    ("F", "Soft & bright",
     "Very gentle gradient, nearly flat. Pip never dims much.",
     {
         "SUNSET": (1.00, 0.95),
         "DUSK":   (0.98, 0.92),
         "NIGHT":  (0.95, 0.88),
     }),
    ("G", "Bright + soft gradient",
     "Slight directional shadow, still very bright.",
     {
         "SUNSET": (1.00, 0.88),
         "DUSK":   (0.96, 0.82),
         "NIGHT":  (0.93, 0.78),
     }),
    ("H", "Bright + medium gradient",
     "Clear directional shadow without going dark.",
     {
         "SUNSET": (1.00, 0.82),
         "DUSK":   (0.96, 0.75),
         "NIGHT":  (0.92, 0.70),
     }),
    ("I", "Bright + extended gradient",
     "Stronger underside shadow, top stays bright.",
     {
         "SUNSET": (1.00, 0.78),
         "DUSK":   (0.97, 0.70),
         "NIGHT":  (0.93, 0.62),
     }),
    ("J", "Top at day-bright always",
     "Top never dims; only underside shadows mildly.",
     {
         "SUNSET": (1.00, 0.90),
         "DUSK":   (1.00, 0.85),
         "NIGHT":  (1.00, 0.78),
     }),
]

PHASES = (
    ("SUNSET", 0.36),
    ("DUSK",   0.51),
    ("NIGHT",  0.64),
)


def render_frame(world, target, phase, top_bot):
    """Render Pip at the given biome phase with the option's (top, bot).
    If `top_bot` is None, render the original sprite with NO lighting
    effect — used for the REF column."""
    world.biome_time = _biome.CYCLE_SECONDS * phase
    pal = _biome.palette_for_phase(phase)
    buckets = _biome.PHASE_BUCKETS
    bucket_f = (phase % 1.0) * buckets
    a = int(bucket_f) % buckets
    sky = get_sky_surface_biome(W, H, GROUND_Y, pal, a)
    target.blit(sky, (0, 0))
    for bx, by, sc, variant in (
            (40, 80, 0.9, 0), (220, 110, 1.0, 2), (110, 180, 0.8, 3)):
        draw_cloud(target, bx, by, sc, variant=variant)
    draw_mountains(target, 0, GROUND_Y, W,
                   pal["mtn_far"], pal["mtn_near"])
    draw_ground(target, GROUND_Y, W, H, 0,
                pal["ground_top"], pal["ground_mid"], (60, 40, 25))
    for p in world.pipes:
        p.draw(target, palette=pal)
    if top_bot is None:
        # Reference render — no lighting effect at all (light_gradient=None
        # AND light_level=1.0 makes Bird.draw skip the multiply entirely).
        world.bird.draw(target, light_gradient=None, light_level=1.0)
    else:
        world.bird.draw(target, light_gradient=top_bot)


def make_grid(ref_renders, option_renders):
    margin = 8
    tile_w = W // 2 + 20
    tile_h = H // 2 + 20
    header_h = 50
    leftcol_w = 110
    n_cols = 1 + len(option_renders)  # REF + options
    total_w = leftcol_w + tile_w * n_cols + margin * (n_cols + 2)
    total_h = header_h + tile_h * len(PHASES) + margin * (len(PHASES) + 2)
    sheet = pygame.Surface((total_w, total_h))
    sheet.fill((22, 22, 30))

    title_font = pygame.font.SysFont("Arial", 16, bold=True)
    sub_font = pygame.font.SysFont("Arial", 11)
    phase_font = pygame.font.SysFont("Arial", 14, bold=True)

    # Header — REF column first
    x_ref = leftcol_w + margin * 2
    hdr = title_font.render("REF — original parrot", True, (140, 220, 255))
    sheet.blit(hdr, (x_ref, margin))
    sub = sub_font.render("No lighting effect (baseline)", True,
                          (200, 200, 210))
    sheet.blit(sub, (x_ref, margin + 22))

    for i, (letter, label, desc, _) in enumerate(option_renders):
        x = leftcol_w + margin * 2 + (i + 1) * (tile_w + margin)
        hdr = title_font.render(f"{letter} — {label}", True, (255, 230, 140))
        sheet.blit(hdr, (x, margin))
        sub = sub_font.render(desc[:52], True, (200, 200, 210))
        sheet.blit(sub, (x, margin + 22))

    # Left column phase labels
    for r, (phase_name, _) in enumerate(PHASES):
        y = header_h + margin + r * (tile_h + margin)
        ph = phase_font.render(phase_name, True, (255, 255, 255))
        sheet.blit(ph, (margin, y + tile_h // 2 - ph.get_height() // 2))

    # REF tiles
    for r, (phase_name, _) in enumerate(PHASES):
        tile = pygame.transform.smoothscale(ref_renders[phase_name],
                                            (tile_w, tile_h))
        x = leftcol_w + margin * 2
        y = header_h + margin + r * (tile_h + margin)
        sheet.blit(tile, (x, y))
    # Option tiles
    for c, (letter, _, _, frames) in enumerate(option_renders):
        for r, (phase_name, _) in enumerate(PHASES):
            tile = pygame.transform.smoothscale(frames[phase_name],
                                                (tile_w, tile_h))
            x = leftcol_w + margin * 2 + (c + 1) * (tile_w + margin)
            y = header_h + margin + r * (tile_h + margin)
            sheet.blit(tile, (x, y))

    out = os.path.join(OUT_DIR, "00_grid.png")
    pygame.image.save(sheet, out)
    print(f"  saved {out}")


def main():
    surf = pygame.Surface((W, H))
    w = World()
    w.ready_t = 0
    w._spawn_pipe(W // 2 - 30)

    # REF column: render each phase with NO lighting effect.
    ref_renders = {}
    for phase_name, phase_val in PHASES:
        render_frame(w, surf, phase_val, None)
        ref_renders[phase_name] = surf.copy()

    option_renders = []
    for letter, label, desc, phase_map in OPTIONS:
        rendered = {}
        for phase_name, phase_val in PHASES:
            top, bot = phase_map[phase_name]
            render_frame(w, surf, phase_val, (top, bot))
            rendered[phase_name] = surf.copy()
            # Save per-option per-phase as well
            sub_dir = os.path.join(OUT_DIR, f"{letter}_tiles")
            os.makedirs(sub_dir, exist_ok=True)
            pygame.image.save(
                surf,
                os.path.join(
                    sub_dir,
                    f"{letter}_{phase_name.lower()}_{top:.2f}_{bot:.2f}.png"))
        option_renders.append((letter, label, desc, rendered))

    make_grid(ref_renders, option_renders)
    print("\nDone. Output in:", OUT_DIR)


if __name__ == "__main__":
    main()
