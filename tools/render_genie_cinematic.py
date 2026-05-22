"""Render the Genie reveal cinematic.

Produces under docs/screenshots/genie_cinematic/:
  00_contact_sheet.png — 10-frame contact sheet, 2 rows × 5 columns
  01_rise_early.png    — t=0.20 s, genie just fading in
  02_rise_full.png     — t=0.40 s, genie fully risen, arms folded
  03_cast0_fire.png    — t=0.65 s, first offer conjured (poof + chime)
  04_cast0_after.png   — t=0.85 s, first offer settled, poof spreading
  05_cast1_fire.png    — t=1.05 s, second offer conjured
  06_cast1_after.png   — t=1.25 s, two offers visible
  07_cast2_fire.png    — t=1.45 s, third offer conjured
  08_cast2_after.png   — t=1.65 s, all three offers in view
  09_vanish.png        — t=1.85 s, genie collapsing into smoke swirl
  10_after.png         — t=2.05 s, genie gone, three offers floating
  genie_reveal.gif     — full 2.05-s sequence as 30-fps animated GIF

Run from repo root:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m tools.render_genie_cinematic
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import random
import pygame
from PIL import Image

pygame.init()
pygame.display.set_mode((360, 640))

from game.config import W, H, GROUND_Y
from game import biome as _biome
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
)
from game.world import World
from game.entities import PowerUp


OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "genie_cinematic")
os.makedirs(OUT_DIR, exist_ok=True)


def render_world(world, target):
    """Paint background + entities so each frame reads as a real
    gameplay snapshot. Mirrors the order in game/scenes.py."""
    phase = world.biome_phase
    pal = _biome.palette_for_phase(phase)
    buckets = _biome.PHASE_BUCKETS
    bucket_f = (phase % 1.0) * buckets
    a = int(bucket_f) % buckets
    sky = get_sky_surface_biome(W, H, GROUND_Y, pal, a)
    target.blit(sky, (0, 0))
    for bx, by, sc, variant in (
            (20, 90, 0.9, 0), (220, 130, 1.0, 2), (90, 200, 0.8, 3)):
        draw_cloud(target, bx, by, sc, variant=variant)
    draw_mountains(target, world.bg_scroll, GROUND_Y, W,
                   pal["mtn_far"], pal["mtn_near"])
    draw_ground(target, GROUND_Y, W, H, world.bg_scroll,
                pal["ground_top"], pal["ground_mid"], (60, 40, 25))
    for p in world.pipes:
        p.draw(target)
    for c in world.coins:
        c.draw(target)
    for m in world.powerups:
        m.draw(target)
    for p in world.particles:
        p.draw(target)
    for g in world.genie_actors:
        g.draw(target)
    world.bird.draw(target, flipped=False)
    for t in world.float_texts:
        t.draw(target)
    world.weather.draw(target)


def setup_world():
    random.seed(31)
    w = World()
    w.ready_t = 0
    # Daylight biome so the genie's lavender palette reads cleanly
    # against a calm sky (overrides the v5_powerups light-drizzle
    # bootstrap so screenshots aren't muddied by rain streaks).
    w.biome_time = _biome.CYCLE_SECONDS * 0.10
    for _ in range(20):
        w.weather.update(1 / 60, w.biome_phase)
    # No pipes — they crowd the genie sprite. Clouds + mountains +
    # ground + Pip read as gameplay context plenty well.
    return w


def save_frame(surf, name, label=None):
    out = surf.copy()
    if label:
        font = pygame.font.SysFont("Arial", 14, bold=True)
        img = font.render(label, True, (255, 255, 255))
        bg = pygame.Surface((img.get_width() + 12, img.get_height() + 6),
                            pygame.SRCALPHA)
        bg.fill((0, 0, 0, 150))
        out.blit(bg, (6, 6))
        out.blit(img, (12, 9))
    path = os.path.join(OUT_DIR, name)
    pygame.image.save(out, path)
    print(f"  saved {path}")
    return out


def make_contact_sheet(frames, name, cols=5):
    rows = (len(frames) + cols - 1) // cols
    margin = 6
    sw = W // 2
    sh = H // 2
    total_w = sw * cols + margin * (cols + 1)
    total_h = sh * rows + margin * (rows + 1)
    sheet = pygame.Surface((total_w, total_h))
    sheet.fill((20, 20, 28))
    for i, fr in enumerate(frames):
        col, row = i % cols, i // cols
        small = pygame.transform.smoothscale(fr, (sw, sh))
        sheet.blit(small,
                   (margin + col * (sw + margin),
                    margin + row * (sh + margin)))
    path = os.path.join(OUT_DIR, name)
    pygame.image.save(sheet, path)
    print(f"  saved {path}")


def save_gif(gif_frames, name, fps=30):
    """Stitch the per-tick frames into an animated GIF via Pillow.
    gif_frames is a list of pygame Surfaces; we convert each to a
    PIL Image and save the whole sequence with the given frame rate."""
    pil_frames = []
    for surf in gif_frames:
        raw = pygame.image.tostring(surf, "RGB")
        img = Image.frombytes("RGB", (W, H), raw)
        pil_frames.append(img)
    duration_ms = int(1000 / fps)
    path = os.path.join(OUT_DIR, name)
    pil_frames[0].save(
        path,
        save_all=True,
        append_images=pil_frames[1:],
        duration=duration_ms,
        loop=0,
        optimize=True,
    )
    print(f"  saved {path}  ({len(pil_frames)} frames @ {fps} fps)")


# Per-frame world step that ALSO scrolls the world (matches what
# World.update would do during play). We don't call World.update
# because it would also try to spawn new pipes / move physics in
# ways that would muddy the demo; here we tick only what the genie
# cinematic touches.
def tick(world, dt):
    # Scroll background + pipes + offers + genie at the world's scroll.
    speed = world._current_scroll()
    world.bg_scroll += speed * dt
    for p in world.pipes:
        p.x -= speed * dt
    for m in world.powerups:
        m.x -= speed * dt
        m.update(dt)
    # Particles + genie actors.
    for p in world.particles:
        p.update(dt)
    world.particles = [p for p in world.particles if p.alive()]
    for g in world.genie_actors:
        g.update(dt)
    world.genie_actors = [g for g in world.genie_actors if g.alive()]
    for t in world.float_texts:
        t.update(dt)
    world.float_texts = [t for t in world.float_texts if t.alive()]
    # Bird bob.
    import math
    world.bird.frame_t += dt * 8.0
    world.bird.y = H * 0.42 + math.sin(world.bg_scroll * 0.05) * 12


def advance_to(world, surf, target_t, gif_buf, dt=1/60):
    """Tick until world's genie has reached approximately target_t,
    recording one GIF frame per tick along the way."""
    if not world.genie_actors:
        return
    g = world.genie_actors[0]
    while g._t < target_t and g.alive():
        tick(world, dt)
        # Capture for the GIF.
        render_world(world, surf)
        gif_buf.append(surf.copy())
        if not world.genie_actors:
            break


def main():
    w = setup_world()
    # Trigger the genie cinematic.
    w._activate_genie(PowerUp(w.bird.x, w.bird.y, kind="genie"))
    surf = pygame.Surface((W, H))
    keyframes = []
    gif_buf = []

    schedule = [
        (0.20, "01_rise_early.png",    "1: rise — fading in"),
        (0.40, "02_rise_full.png",     "2: rise — fully formed"),
        (0.66, "03_cast0_fire.png",    "3: cast 1 — first offer"),
        (0.85, "04_cast0_after.png",   "4: cast 1 — poof spreads"),
        (1.06, "05_cast1_fire.png",    "5: cast 2 — second offer"),
        (1.25, "06_cast1_after.png",   "6: cast 2 — two offers"),
        (1.46, "07_cast2_fire.png",    "7: cast 3 — third offer"),
        (1.65, "08_cast2_after.png",   "8: cast 3 — all three"),
        (1.85, "09_vanish.png",        "9: vanish — smoke swirl"),
        (2.05, "10_after.png",         "10: gone — offers float"),
    ]

    for target_t, fname, label in schedule:
        advance_to(w, surf, target_t, gif_buf)
        # Render fresh after reaching target.
        render_world(w, surf)
        keyframes.append(save_frame(surf, fname, label))

    # Tick a tail of frames so the GIF ends on the "after" beat (the
    # cinematic finishes but the three offers keep drifting left for
    # ~0.5 s).
    for _ in range(int(0.5 * 60)):
        tick(w, 1/60)
        render_world(w, surf)
        gif_buf.append(surf.copy())

    make_contact_sheet(keyframes, "00_contact_sheet.png", cols=5)
    save_gif(gif_buf, "genie_reveal.gif", fps=30)
    print(f"\nWrote {len(keyframes)} keyframes + 1 GIF "
          f"({len(gif_buf)} frames) to {OUT_DIR}")


if __name__ == "__main__":
    main()
