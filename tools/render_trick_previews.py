"""Render 6-keyframe gameplay previews of 4 proposed new
skateboard tricks (No Comply, Pop Shuvit, Heelflip, Tre Flip).
Each preview drives Pip + the skateboard sprite through the
trick's animation by monkey-patching the relevant rendering
hooks on a throwaway Bird — no live gameplay code is touched.

Outputs per trick:
  * <trick>_frame_<0..5>.png — single keyframe at p ∈ {0, 0.2,
                               0.4, 0.6, 0.8, 1.0}
  * <trick>_strip.png        — horizontal strip of the 6 frames
Plus 00_all_tricks.png       — vertical stack of all 4 strips

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_trick_previews.py
"""

import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import (
    SKATEBOARD_DURATION, BACKFLIP_DURATION, KICKFLIP_DURATION,
)
from game.entities import Bird, PowerUp
from tools.render_helmet_side_view_variants import (
    build_world, render_play_scene, _label_band,
)


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "skateboard_tricks")
os.makedirs(_OUT, exist_ok=True)


FRAMES_PER_TRICK = 6


def _eased(p):
    """Smootherstep 6p⁵ − 15p⁴ + 10p³ (matches the live tricks)."""
    return p * p * p * (p * (p * 6.0 - 15.0) + 10.0)


# ── trick painters — each receives a fresh world + bird and the
#     animation progress p in [0, 1]. They directly mutate bird
#     state / monkey-patch draw to mock the trick visual. ──

def _setup_world():
    """Build a world with skateboard active; return (world, bird)."""
    world = build_world()
    world.ready_t = 0
    for _ in range(40):
        world.world_idle_tick(1 / 60)
    world._activate_skateboard(PowerUp(0, 0, kind="skateboard"))
    return world


def _render_at(world, label_caption):
    """Render the gameplay scene and overlay a small label at top-
    left so each strip-frame is self-identifying."""
    frame = render_play_scene(world)
    f = pygame.font.SysFont(None, 18, bold=True)
    band = pygame.Surface((140, 24), pygame.SRCALPHA)
    pygame.draw.rect(band, (0, 0, 0, 170), band.get_rect(),
                     border_radius=4)
    t = f.render(label_caption, True, (255, 255, 255))
    band.blit(t, t.get_rect(center=band.get_rect().center))
    frame.blit(band, (8, 8))
    return frame


def _frame_no_comply(p):
    """No Comply: Pip hops upward (~22 px peak) over the trick
    duration via sin(p·π). Board stays at the original y."""
    world = _setup_world()
    bird = world.bird
    original_y = bird.y
    bird.y = original_y - int(22 * math.sin(p * math.pi))
    frame = _render_at(world, f"NO COMPLY  p={p:.2f}")
    bird.y = original_y
    return frame


def _frame_pop_shuvit(p):
    """Pop Shuvit: board scales horizontally cos(p·π) (1 → 0 →
    −1, then back), simulating a 180° flat-spin around the
    vertical axis. Scale is applied to a small sub-surface
    centred on the board so the position doesn't drift."""
    world = _setup_world()
    bird = world.bird

    original_draw = bird._draw_skateboard
    def patched(surf, cx, cy, flipped):
        pad = 80
        tmp = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
        original_draw(tmp, pad, pad, flipped)
        scale_x = math.cos(p * math.pi)
        abs_scale = max(abs(scale_x), 0.02)
        w, h = tmp.get_size()
        scaled = pygame.transform.scale(
            tmp, (max(1, int(w * abs_scale)), h))
        if scale_x < 0:
            scaled = pygame.transform.flip(scaled, True, False)
        surf.blit(scaled, scaled.get_rect(center=(cx, cy)))
    bird._draw_skateboard = patched
    try:
        frame = _render_at(world, f"POP SHUVIT  p={p:.2f}")
    finally:
        bird._draw_skateboard = original_draw
    return frame


def _frame_heelflip(p):
    """Heelflip: board rotates −360° (mirror of kickflip). The
    rotation is around the BOARD'S centre, not the screen
    centre — paint the board onto a small sub-surface whose
    centre coincides with (cx, cy), rotate that, blit at
    (cx, cy)."""
    world = _setup_world()
    bird = world.bird

    original_draw = bird._draw_skateboard
    def patched(surf, cx, cy, flipped):
        # Draw the board (with zero kickflip rotation) onto a
        # small padded sub-surface centred at the board.
        bird.kickflip_t = 0.0
        pad = 80
        tmp = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
        original_draw(tmp, pad, pad, flipped)
        # Rotate by -360 * eased(p) around tmp's centre.
        deg = -_eased(p) * 360.0
        rotated = pygame.transform.rotate(tmp, deg)
        surf.blit(rotated, rotated.get_rect(center=(cx, cy)))
    bird._draw_skateboard = patched
    try:
        frame = _render_at(world, f"HEELFLIP  p={p:.2f}")
    finally:
        bird._draw_skateboard = original_draw
        bird.kickflip_t = 0.0
    return frame


def _frame_tre_flip(p):
    """Tre Flip: Pip rotates +360° AND board rotates +360°
    simultaneously. Done by setting both backflip_t and
    kickflip_t at the matching progress."""
    world = _setup_world()
    bird = world.bird
    # Both timers count DOWN from dur to 0 as p goes 0→1, so
    # remaining = dur * (1 - p).
    bird.backflip_t = BACKFLIP_DURATION * (1 - p)
    bird.backflip_dur = BACKFLIP_DURATION
    bird.kickflip_t = KICKFLIP_DURATION * (1 - p)
    bird.kickflip_dur = KICKFLIP_DURATION
    frame = _render_at(world, f"TRE FLIP  p={p:.2f}")
    bird.backflip_t = 0.0
    bird.kickflip_t = 0.0
    return frame


TRICKS = [
    ("no_comply",  "No Comply  (2 fast taps, gap ≤ 0.30 s)",
     _frame_no_comply),
    ("pop_shuvit", "Pop Shuvit (2 medium taps, gap 0.35–0.50 s)",
     _frame_pop_shuvit),
    ("heelflip",   "Heelflip   (3 slow taps, gap 0.55–0.75 s)",
     _frame_heelflip),
    ("tre_flip",   "Tre Flip   (4 fast taps, gap ≤ 0.40 s)",
     _frame_tre_flip),
]


def _crop_to_pip(frame, bird_x, bird_y):
    """Crop the gameplay frame to a 240×240 square around Pip so
    the trick animation reads clearly without the whole pillar
    landscape competing."""
    crop_w = 240
    crop_h = 240
    rect = pygame.Rect(0, 0, crop_w, crop_h)
    rect.center = (bird_x, bird_y - 10)
    rect.clamp_ip(frame.get_rect())
    cropped = pygame.Surface((crop_w, crop_h))
    cropped.blit(frame, (0, 0), rect)
    return cropped


def main():
    # All tricks share the same Pip anchor (from build_world).
    sample = build_world()
    bird_x = int(sample.bird.x)
    bird_y = int(sample.bird.y)
    del sample

    trick_strips = []
    for slug, caption, frame_fn in TRICKS:
        frames = []
        for i in range(FRAMES_PER_TRICK):
            p = i / (FRAMES_PER_TRICK - 1)
            full = frame_fn(p)
            small = _crop_to_pip(full, bird_x, bird_y)
            frames.append(small)
            path = os.path.join(_OUT,
                                 f"{slug}_frame_{i}.png")
            pygame.image.save(small, path)
            print(f"saved {path}")
        # Build horizontal strip.
        cell_w = frames[0].get_width()
        cell_h = frames[0].get_height()
        gap = 8
        strip = pygame.Surface(
            (cell_w * len(frames) + gap * (len(frames) - 1) + 24,
             cell_h + 60),
            pygame.SRCALPHA)
        strip.fill((10, 12, 24))
        for idx, fr in enumerate(frames):
            strip.blit(fr, (12 + idx * (cell_w + gap), 12))
        # Caption band at bottom.
        f = pygame.font.SysFont(None, 22, bold=True)
        cap = f.render(caption, True, (255, 215, 80))
        strip.blit(cap, cap.get_rect(
            center=(strip.get_width() // 2, cell_h + 36)))
        strip_path = os.path.join(_OUT, f"{slug}_strip.png")
        pygame.image.save(strip, strip_path)
        print(f"saved {strip_path}")
        trick_strips.append(strip)

    # Stack all 4 trick strips vertically.
    sw = trick_strips[0].get_width()
    sh = sum(s.get_height() for s in trick_strips) + 12 * (len(trick_strips) + 1)
    full = pygame.Surface((sw, sh))
    full.fill((10, 12, 24))
    y = 12
    for s in trick_strips:
        full.blit(s, (0, y))
        y += s.get_height() + 12
    all_path = os.path.join(_OUT, "00_all_tricks.png")
    pygame.image.save(full, all_path)
    print(f"saved {all_path}")

    base = ("https://raw.githubusercontent.com/ytocker/skybit/"
            "v5_powerups/docs/screenshots/skateboard_tricks")
    print()
    print(f"{base}/00_all_tricks.png")
    for slug, caption, _ in TRICKS:
        print(f"{base}/{slug}_strip.png  -- {caption}")


if __name__ == "__main__":
    main()
