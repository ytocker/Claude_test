"""Render 5 NIGHTGLOW visual-variant mockups for review.

Each variant paints the same canonical scene (night sky + 2 pillars + 2
coins + 1 powerup token + Pip mid-flap) with a different neon-green glow
treatment, then saves a 360×640 PNG. The user picks one; the live game
render path is updated separately.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_nightglow_variants.py
"""

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

# Ensure the repo root is on sys.path so `game` imports work when this
# file is invoked from the repo root or from anywhere else.
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

pygame.init()
pygame.display.set_mode((1, 1))  # required for some Surface ops

from game import biome
from game.config import W, H, PIPE_W, COIN_R, POWERUP_R, GROUND_Y, BIRD_X
from game.entities import Bird, Coin, PowerUp, Pipe


NEON       = (57, 255, 20)
NEON_CORE  = (170, 255, 140)
NEON_DEEP  = (20, 120, 40)


# ─── canonical scene ────────────────────────────────────────────────────────

def _night_sky(surf: pygame.Surface) -> None:
    pal = biome.palette_for_phase(0.64375)
    top, mid, bot = pal["sky_top"], pal["sky_mid"], pal["sky_bot"]
    for y in range(H):
        if y < H * 0.45:
            t = y / (H * 0.45)
            r = int(top[0] + (mid[0] - top[0]) * t)
            g = int(top[1] + (mid[1] - top[1]) * t)
            b = int(top[2] + (mid[2] - top[2]) * t)
        else:
            t = (y - H * 0.45) / (H * 0.55)
            r = int(mid[0] + (bot[0] - mid[0]) * t)
            g = int(mid[1] + (bot[1] - mid[1]) * t)
            b = int(mid[2] + (bot[2] - mid[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (W, y))


def _ground_band(surf: pygame.Surface) -> None:
    pygame.draw.rect(surf, (18, 28, 50), (0, GROUND_Y, W, H - GROUND_Y))
    pygame.draw.line(surf, (60, 90, 130), (0, GROUND_Y), (W, GROUND_Y), 1)


def _build_entities():
    """Returns (pipes, coins, powerup, bird) positioned for the mockup."""
    pal = biome.palette_for_phase(0.64375)
    pipes = [
        Pipe(x=70.0,  gap_y=H * 0.50, gap_h=170.0),
        Pipe(x=240.0, gap_y=H * 0.42, gap_h=160.0),
    ]
    coins = [
        Coin(x=160.0, y=H * 0.46),
        Coin(x=205.0, y=H * 0.40),
    ]
    powerup = PowerUp(x=295.0, y=H * 0.32, kind="nightglow")
    bird = Bird()
    bird.x = BIRD_X
    bird.y = H * 0.50
    bird.frame_t = 0.4
    return pipes, coins, powerup, bird, pal


def render_base() -> tuple[pygame.Surface, dict]:
    """One Surface containing the un-glowed scene + the entity refs we
    later overlay glows onto."""
    surf = pygame.Surface((W, H)).convert()
    _night_sky(surf)
    _ground_band(surf)

    pipes, coins, powerup, bird, pal = _build_entities()
    for p in pipes:
        p.draw(surf, pal)
    for c in coins:
        c.draw(surf)
    powerup.draw(surf)
    bird.draw(surf, 0, 0)

    return surf, {
        "pipes":   pipes,
        "coins":   coins,
        "powerup": powerup,
        "bird":    bird,
    }


# ─── shared helpers ─────────────────────────────────────────────────────────

def _dark_overlay(surf: pygame.Surface, alpha: int) -> None:
    tint = pygame.Surface((W, H), pygame.SRCALPHA)
    tint.fill((4, 6, 14, alpha))
    surf.blit(tint, (0, 0))


def _pipe_rects(pipe):
    top_h = max(0, int(pipe.gap_y - pipe.gap_h / 2))
    bot_y = int(pipe.gap_y + pipe.gap_h / 2)
    bot_h = max(0, GROUND_Y - bot_y)
    return int(pipe.x), top_h, bot_y, bot_h


def _entity_centers(refs):
    pts = []
    for c in refs["coins"]:
        pts.append(("coin",    int(c.x), int(c.y), COIN_R))
    pts.append(("powerup",
                int(refs["powerup"].x), int(refs["powerup"].y), POWERUP_R))
    pts.append(("bird",
                int(refs["bird"].x), int(refs["bird"].y), 14))
    return pts


# ─── VARIANT 1 — OUTLINE (sharp Tron edges) ─────────────────────────────────

def variant_outline(surf: pygame.Surface, refs: dict) -> None:
    _dark_overlay(surf, 145)

    # Pillars: thin vertical edge lines + horizontal caps.
    for p in refs["pipes"]:
        x, top_h, bot_y, bot_h = _pipe_rects(p)
        if top_h > 0:
            pygame.draw.line(surf, NEON, (x, 0), (x, top_h), 2)
            pygame.draw.line(surf, NEON,
                             (x + PIPE_W - 1, 0), (x + PIPE_W - 1, top_h), 2)
            pygame.draw.line(surf, NEON_CORE,
                             (x - 2, top_h), (x + PIPE_W + 1, top_h), 2)
        if bot_h > 0:
            pygame.draw.line(surf, NEON, (x, bot_y), (x, GROUND_Y), 2)
            pygame.draw.line(surf, NEON,
                             (x + PIPE_W - 1, bot_y),
                             (x + PIPE_W - 1, GROUND_Y), 2)
            pygame.draw.line(surf, NEON_CORE,
                             (x - 2, bot_y), (x + PIPE_W + 1, bot_y), 2)

    # Coins / powerup / bird: ring outlines.
    for kind, cx, cy, r in _entity_centers(refs):
        pygame.draw.circle(surf, NEON, (cx, cy), r + 3, 2)
        pygame.draw.circle(surf, NEON_CORE, (cx, cy), r + 1, 1)


# ─── VARIANT 2 — BLOOM (soft radial halo) ───────────────────────────────────

def _radial(surf, cx, cy, r, layers):
    """Multi-layer additive radial halo at (cx, cy)."""
    s = pygame.Surface((r * 2 + 6, r * 2 + 6), pygame.SRCALPHA)
    for rr, a, col in layers:
        if rr <= 0:
            continue
        pygame.draw.circle(s, (*col, a), (r + 3, r + 3), rr)
    surf.blit(s, (cx - r - 3, cy - r - 3), special_flags=pygame.BLEND_RGBA_ADD)


def variant_bloom(surf: pygame.Surface, refs: dict) -> None:
    _dark_overlay(surf, 120)

    for p in refs["pipes"]:
        x, top_h, bot_y, bot_h = _pipe_rects(p)
        # Pillar bloom: 3 vertical bands of decreasing width / increasing alpha.
        for w_off, alpha in ((26, 16), (14, 32), (6, 60)):
            for ry, rh in ((-w_off, top_h + w_off), (bot_y, bot_h + w_off)):
                if rh <= 0:
                    continue
                band = pygame.Surface(
                    (PIPE_W + w_off * 2, rh), pygame.SRCALPHA)
                band.fill((*NEON, alpha))
                surf.blit(band, (x - w_off, ry),
                          special_flags=pygame.BLEND_RGBA_ADD)

    # Coins/powerup/bird: 4-layer soft halo.
    for kind, cx, cy, r in _entity_centers(refs):
        budget = r + (16 if kind == "coin" else
                      22 if kind == "powerup" else 30)
        _radial(surf, cx, cy, budget, (
            (budget,             18, NEON),
            (int(budget * 0.7),  36, NEON),
            (int(budget * 0.45), 65, NEON),
            (int(budget * 0.2), 110, NEON_CORE),
        ))


# ─── VARIANT 3 — SCANLINE (CRT phosphor) ────────────────────────────────────

def _build_scanlines() -> pygame.Surface:
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    for y in range(0, H, 2):
        pygame.draw.line(s, (0, 0, 0, 70), (0, y), (W, y))
    return s


def variant_scanline(surf: pygame.Surface, refs: dict) -> None:
    _dark_overlay(surf, 105)

    # Moderate bloom first.
    for p in refs["pipes"]:
        x, top_h, bot_y, bot_h = _pipe_rects(p)
        for w_off, alpha in ((18, 24), (8, 52)):
            for ry, rh in ((-w_off, top_h + w_off), (bot_y, bot_h + w_off)):
                if rh <= 0:
                    continue
                band = pygame.Surface(
                    (PIPE_W + w_off * 2, rh), pygame.SRCALPHA)
                band.fill((*NEON, alpha))
                surf.blit(band, (x - w_off, ry),
                          special_flags=pygame.BLEND_RGBA_ADD)

    for kind, cx, cy, r in _entity_centers(refs):
        budget = r + 14
        _radial(surf, cx, cy, budget, (
            (budget,             28, NEON),
            (int(budget * 0.6),  60, NEON),
            (int(budget * 0.3), 110, NEON_CORE),
        ))

    # Phosphor smear: tinted offset blits before the scanlines mute the frame.
    teal_tint = pygame.Surface((W, H), pygame.SRCALPHA)
    teal_tint.fill((30, 120, 90, 18))
    surf.blit(teal_tint, (-1, 0), special_flags=pygame.BLEND_RGBA_ADD)
    green_tint = pygame.Surface((W, H), pygame.SRCALPHA)
    green_tint.fill((40, 180, 60, 22))
    surf.blit(green_tint, (1, 0), special_flags=pygame.BLEND_RGBA_ADD)

    surf.blit(_build_scanlines(), (0, 0))


# ─── VARIANT 4 — WIREFRAME (stroke-only, no fills) ──────────────────────────

def variant_wireframe(surf: pygame.Surface, refs: dict) -> None:
    _dark_overlay(surf, 180)  # heavier — entities almost vanish.

    # Pillars: open rectangle outlines + hatched interior verticals.
    for p in refs["pipes"]:
        x, top_h, bot_y, bot_h = _pipe_rects(p)
        if top_h > 0:
            pygame.draw.rect(surf, NEON,
                             pygame.Rect(x, 0, PIPE_W, top_h), 2)
            for vx in range(x + 8, x + PIPE_W - 4, 12):
                pygame.draw.line(surf, NEON_DEEP, (vx, 0), (vx, top_h), 1)
        if bot_h > 0:
            pygame.draw.rect(surf, NEON,
                             pygame.Rect(x, bot_y, PIPE_W, bot_h), 2)
            for vx in range(x + 8, x + PIPE_W - 4, 12):
                pygame.draw.line(surf, NEON_DEEP,
                                 (vx, bot_y), (vx, GROUND_Y), 1)

    # Coins: a single neon ring.
    for c in refs["coins"]:
        pygame.draw.circle(surf, NEON_CORE, (int(c.x), int(c.y)), COIN_R + 2, 2)
        pygame.draw.circle(surf, NEON, (int(c.x), int(c.y)), COIN_R - 2, 1)

    # Powerup: hollow diamond + inner ring.
    px, py = int(refs["powerup"].x), int(refs["powerup"].y)
    r = POWERUP_R + 6
    pygame.draw.polygon(surf, NEON,
        [(px, py - r), (px + r, py), (px, py + r), (px - r, py)], 2)
    pygame.draw.circle(surf, NEON_CORE, (px, py), POWERUP_R - 1, 1)

    # Bird: traced outline from sprite mask.
    bird = refs["bird"]
    # Sample what pygame drew of the bird so we can extract its silhouette.
    sample = pygame.Surface((48, 48), pygame.SRCALPHA)
    bird_copy = Bird()
    bird_copy.x = 24
    bird_copy.y = 24
    bird_copy.frame_t = bird.frame_t
    bird_copy.draw(sample, 0, 0)
    mask = pygame.mask.from_surface(sample)
    outline_pts = mask.outline(2)
    if outline_pts:
        offset = (int(bird.x) - 24, int(bird.y) - 24)
        traced = [(p[0] + offset[0], p[1] + offset[1]) for p in outline_pts]
        if len(traced) >= 3:
            pygame.draw.lines(surf, NEON, True, traced, 2)


# ─── VARIANT 5 — PLASMA (pulsing energy field) ──────────────────────────────

def variant_plasma(surf: pygame.Surface, refs: dict) -> None:
    _dark_overlay(surf, 125)

    # Pillars as vertical energy columns: 3 stacked vertically-stretched
    # ellipses with hot inner core.
    for p in refs["pipes"]:
        x, top_h, bot_y, bot_h = _pipe_rects(p)
        cx = x + PIPE_W // 2
        for ry, rh in ((0, top_h), (bot_y, bot_h)):
            if rh <= 0:
                continue
            col_w = PIPE_W + 36
            col = pygame.Surface((col_w, rh), pygame.SRCALPHA)
            # Outer faint glow
            pygame.draw.ellipse(col, (*NEON, 22),
                                pygame.Rect(0, 0, col_w, rh))
            # Mid ring
            margin = 12
            pygame.draw.ellipse(col, (*NEON, 55),
                pygame.Rect(margin, 0, col_w - margin * 2, rh))
            # Hot core
            core_m = col_w // 3
            pygame.draw.ellipse(col, (*NEON_CORE, 130),
                pygame.Rect(core_m, 0, col_w - core_m * 2, rh))
            surf.blit(col, (cx - col_w // 2, ry),
                      special_flags=pygame.BLEND_RGBA_ADD)

    # Coins/powerup/bird: triple-ring pulse, sampled at one phase so the
    # rings sit at staggered radii.
    for kind, cx, cy, r in _entity_centers(refs):
        base = r + (10 if kind == "coin" else
                    18 if kind == "powerup" else 26)
        for rfac, alpha, col, width in (
                (1.00,  90, NEON,      2),
                (0.74, 140, NEON,      2),
                (0.48, 200, NEON_CORE, 2)):
            rr = max(1, int(base * rfac))
            ring = pygame.Surface((rr * 2 + 4, rr * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(ring, (*col, alpha),
                               (rr + 2, rr + 2), rr, width)
            surf.blit(ring, (cx - rr - 2, cy - rr - 2),
                      special_flags=pygame.BLEND_RGBA_ADD)
        # Hot center dot.
        pygame.draw.circle(surf, (255, 255, 255), (cx, cy), 2)


# ─── driver ─────────────────────────────────────────────────────────────────

VARIANTS = [
    ("variant_1_outline.png",   variant_outline),
    ("variant_2_bloom.png",     variant_bloom),
    ("variant_3_scanline.png",  variant_scanline),
    ("variant_4_wireframe.png", variant_wireframe),
    ("variant_5_plasma.png",    variant_plasma),
]


def main() -> int:
    out_dir = os.path.join(_REPO, "docs", "screenshots", "nightglow_variants")
    os.makedirs(out_dir, exist_ok=True)

    base, refs = render_base()
    for fname, fn in VARIANTS:
        frame = base.copy()
        fn(frame, refs)
        out_path = os.path.join(out_dir, fname)
        pygame.image.save(frame, out_path)
        print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
