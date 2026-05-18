"""Render 5 NIGHTGLOW visual-variant mockups for review.

Approach: render the canonical scene (night sky + mountains + ground +
2 pillars + 2 coins + 1 powerup token + Pip mid-flap) ONCE, then for
each variant **preserve the original entity texture** and only

  (1) tint the visible colors toward neon green, and
  (2) add an aura around each entity silhouette

The previous approach (painting flat green shapes over the entities)
destroyed all texture detail and looked amateur. This one keeps the
sandstone pillar grain, the coin gradient, and Pip's sprite intact —
the rendering looks like the same scene shifted into a green-light
night vision, with a glow around the parts that matter.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_nightglow_variants.py
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

from game import biome
from game.config import W, H, PIPE_W, COIN_R, POWERUP_R, GROUND_Y, BIRD_X
from game.draw import draw_mountains, draw_ground
from game.entities import Bird, Coin, PowerUp, Pipe


# ─── scene composition (shared by every variant) ────────────────────────────

def _build_entities():
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


def _night_sky(surf):
    pal = biome.palette_for_phase(0.64375)
    top, mid, bot = pal["sky_top"], pal["sky_mid"], pal["sky_bot"]
    for y in range(H):
        if y < H * 0.45:
            t = y / (H * 0.45)
            c = tuple(int(top[i] + (mid[i] - top[i]) * t) for i in range(3))
        else:
            t = (y - H * 0.45) / (H * 0.55)
            c = tuple(int(mid[i] + (bot[i] - mid[i]) * t) for i in range(3))
        pygame.draw.line(surf, c, (0, y), (W, y))


def _scatter_stars(surf, seed=7):
    import random as _r
    rng = _r.Random(seed)
    for _ in range(40):
        x = rng.randint(0, W - 1)
        y = rng.randint(0, int(H * 0.55))
        a = rng.randint(120, 220)
        pygame.draw.circle(surf, (240, 240, 230), (x, y), 1)
        if rng.random() < 0.15:
            # tiny twinkle cross on a few of them
            pygame.draw.line(surf, (255, 250, 220, a),
                             (x - 2, y), (x + 2, y))
            pygame.draw.line(surf, (255, 250, 220, a),
                             (x, y - 2), (x, y + 2))


def render_base() -> tuple[pygame.Surface, pygame.Surface, dict]:
    """Returns (background_only, entities_only, refs).

    Splitting the scene into "background" and "entities" layers lets each
    variant darken the background while applying glow effects only to the
    entities — without re-rendering them and without losing texture."""
    pipes, coins, powerup, bird, pal = _build_entities()

    bg = pygame.Surface((W, H)).convert()
    _night_sky(bg)
    _scatter_stars(bg)
    draw_mountains(bg, scroll=120.0, ground_y=GROUND_Y, w=W,
                   far_color=(40, 50, 100), near_color=(20, 30, 70))
    draw_ground(bg, ground_y=GROUND_Y, w=W, h=H, scroll=120.0,
                top_color=(35, 50, 80),
                mid_color=(20, 30, 55),
                bot_color=(10, 15, 30))

    entities = pygame.Surface((W, H), pygame.SRCALPHA).convert_alpha()
    for p in pipes:
        p.draw(entities, pal)
    for c in coins:
        c.draw(entities)
    powerup.draw(entities)
    bird.draw(entities, 0, 0)

    return bg, entities, {
        "pipes":   pipes,
        "coins":   coins,
        "powerup": powerup,
        "bird":    bird,
    }


# ─── reusable building blocks ───────────────────────────────────────────────

def _green_tint_preserving_texture(entities: pygame.Surface,
                                   tint=(70, 255, 90),
                                   strength: float = 1.0) -> pygame.Surface:
    """Multiply the entities layer by a green tint so red/blue channels
    drop while the green-channel luminance (and therefore the
    texture-detail gradients) survive. `strength` blends between original
    and fully-tinted: 0.0 = no tint, 1.0 = full tint."""
    full = entities.copy()
    tint_surf = pygame.Surface(full.get_size(), pygame.SRCALPHA)
    tint_surf.fill((*tint, 255))
    full.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    if strength >= 1.0:
        return full
    # Cross-fade original ↔ tinted by `strength`.
    out = entities.copy()
    full.set_alpha(int(255 * strength))
    out.blit(full, (0, 0))
    return out


def _silhouette_alpha(entities: pygame.Surface) -> pygame.Surface:
    """A solid-white silhouette of the entities (alpha === entities alpha)
    — useful as a stamp for outlines/halos."""
    sil = pygame.Surface(entities.get_size(), pygame.SRCALPHA)
    sil.fill((255, 255, 255, 255))
    sil.blit(entities, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return sil


def _blurred_silhouette(entities: pygame.Surface,
                       scale: float,
                       color=(70, 255, 90)) -> pygame.Surface:
    """Downsample-and-back blur of the entity silhouette, recoloured —
    cheap glow halo. Smaller `scale` ⇒ softer, wider blur."""
    sw, sh = max(2, int(W * scale)), max(2, int(H * scale))
    small = pygame.transform.smoothscale(entities, (sw, sh))
    blurred = pygame.transform.smoothscale(small, (W, H))
    # Recolour: multiply by `color`, keep blurred alpha.
    tint = pygame.Surface((W, H), pygame.SRCALPHA)
    tint.fill((*color, 255))
    blurred.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return blurred


def _dilated_rim(entities: pygame.Surface,
                width: int,
                color=(110, 255, 130, 255)) -> pygame.Surface:
    """A solid-colour silhouette larger than `entities` by `width` pixels
    on each side — i.e. an outline you can blit *behind* the entities
    to make a thick rim. Implemented via mask + grow."""
    mask = pygame.mask.from_surface(entities, threshold=20)
    big = mask
    for _ in range(width):
        big = big.connected_component()  # noop fallback if empty
        break
    # Pygame masks don't expose a true dilation; we emulate by stamping
    # the silhouette at every (dx, dy) within radius `width`.
    rim_surf = pygame.Surface((W, H), pygame.SRCALPHA)
    stamp = pygame.Surface((W, H), pygame.SRCALPHA)
    stamp.fill((*color[:3], color[3]))
    stamp.blit(entities, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # Replace stamp's RGB with the rim colour, keep its alpha.
    stamp_recolour = pygame.Surface((W, H), pygame.SRCALPHA)
    stamp_recolour.fill((*color[:3], 255))
    stamp.blit(stamp_recolour, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    for dy in range(-width, width + 1):
        for dx in range(-width, width + 1):
            if dx * dx + dy * dy > width * width:
                continue
            rim_surf.blit(stamp, (dx, dy))
    return rim_surf


def _apply_dark_overlay(scene: pygame.Surface, alpha: int,
                       tint=(4, 8, 16)) -> None:
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((*tint, alpha))
    scene.blit(overlay, (0, 0))


# ─── VARIANT 1 — PHOSPHOR ────────────────────────────────────────────────────
# Soft green tint preserves texture; one wide soft halo behind entities.

def variant_phosphor(bg, entities, refs) -> pygame.Surface:
    scene = bg.copy()
    _apply_dark_overlay(scene, 110)

    halo = _blurred_silhouette(entities, scale=0.10, color=(60, 220, 80))
    halo.set_alpha(170)
    scene.blit(halo, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    tinted = _green_tint_preserving_texture(entities, tint=(80, 255, 100))
    scene.blit(tinted, (0, 0))
    # Tiny additive top-up so highlights pop without losing texture.
    top = _green_tint_preserving_texture(entities, tint=(50, 180, 70))
    top.set_alpha(110)
    scene.blit(top, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return scene


# ─── VARIANT 2 — RIM LIGHT ──────────────────────────────────────────────────
# Original sprite untouched colours; bright green rim hugs the silhouette.

def variant_rimlight(bg, entities, refs) -> pygame.Surface:
    scene = bg.copy()
    _apply_dark_overlay(scene, 130)

    # Wide soft outer halo (cheap blur).
    far_halo = _blurred_silhouette(entities, scale=0.06, color=(50, 200, 70))
    far_halo.set_alpha(140)
    scene.blit(far_halo, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Tight rim behind the entities (so it shows just at the edges).
    rim = _dilated_rim(entities, width=2, color=(140, 255, 160, 255))
    rim.set_alpha(220)
    scene.blit(rim, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Slight green wash on the entity itself (keeps colour, shifts hue).
    washed = _green_tint_preserving_texture(entities,
                                            tint=(190, 255, 200),
                                            strength=0.65)
    scene.blit(washed, (0, 0))
    return scene


# ─── VARIANT 3 — DOUBLE BLOOM ───────────────────────────────────────────────
# Green-tinted texture + multi-radius bloom for that big "Tron 2.0" look.

def variant_bloom(bg, entities, refs) -> pygame.Surface:
    scene = bg.copy()
    _apply_dark_overlay(scene, 115)

    # Three blur radii combined additively → smooth wide bloom.
    for scale, col, alpha in (
            (0.04, (40, 180, 60),  150),
            (0.10, (70, 220, 90),  170),
            (0.20, (110, 255, 130),180)):
        layer = _blurred_silhouette(entities, scale=scale, color=col)
        layer.set_alpha(alpha)
        scene.blit(layer, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    tinted = _green_tint_preserving_texture(entities, tint=(90, 255, 110))
    scene.blit(tinted, (0, 0))
    # Highlight pop.
    pop = _green_tint_preserving_texture(entities, tint=(70, 220, 90))
    pop.set_alpha(130)
    scene.blit(pop, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return scene


# ─── VARIANT 4 — GODRAYS ────────────────────────────────────────────────────
# Tinted entity + radial light beams fanning out from each centre.

def _draw_rays(scene: pygame.Surface, cx: int, cy: int,
              length: int, count: int, color, alpha_start: int,
              phase: float = 0.0, width: int = 2) -> None:
    rays = pygame.Surface((length * 2 + 4, length * 2 + 4), pygame.SRCALPHA)
    for i in range(count):
        a = (i / count) * math.tau + phase
        x2 = length + length * math.cos(a)
        y2 = length + length * math.sin(a)
        # Per-ray gradient: fade alpha by distance along line.
        for step in range(8, length, 4):
            t = step / length
            alpha = int(alpha_start * (1.0 - t) ** 2)
            if alpha <= 0:
                continue
            px = length + step * math.cos(a)
            py = length + step * math.sin(a)
            pygame.draw.circle(rays, (*color, alpha),
                               (int(px), int(py)), width)
    scene.blit(rays, (cx - length, cy - length),
               special_flags=pygame.BLEND_RGBA_ADD)


def variant_godrays(bg, entities, refs) -> pygame.Surface:
    scene = bg.copy()
    _apply_dark_overlay(scene, 125)

    NEON = (90, 255, 120)
    # Faint wide halo so the rays plant on something soft.
    halo = _blurred_silhouette(entities, scale=0.08, color=(50, 180, 70))
    halo.set_alpha(130)
    scene.blit(halo, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Rays per entity centre.
    for c in refs["coins"]:
        _draw_rays(scene, int(c.x), int(c.y),
                   length=70, count=10, color=NEON,
                   alpha_start=140, phase=0.3, width=1)
    m = refs["powerup"]
    _draw_rays(scene, int(m.x), int(m.y),
               length=110, count=14, color=NEON,
               alpha_start=170, phase=0.0, width=2)
    b = refs["bird"]
    _draw_rays(scene, int(b.x), int(b.y),
               length=130, count=16, color=NEON,
               alpha_start=180, phase=0.6, width=2)
    # Pillars get vertical "beam columns" via short horizontal rays.
    for p in refs["pipes"]:
        cx = int(p.x + PIPE_W / 2)
        cy = int(p.gap_y - p.gap_h / 2 - 30)
        _draw_rays(scene, cx, cy,
                   length=90, count=8, color=NEON,
                   alpha_start=120, phase=math.pi / 8, width=1)
        cy2 = int(p.gap_y + p.gap_h / 2 + 30)
        _draw_rays(scene, cx, cy2,
                   length=90, count=8, color=NEON,
                   alpha_start=120, phase=math.pi / 8, width=1)

    tinted = _green_tint_preserving_texture(entities, tint=(110, 255, 130))
    scene.blit(tinted, (0, 0))
    return scene


# ─── VARIANT 5 — ECHO RINGS ─────────────────────────────────────────────────
# Tinted entity + concentric pulsing rings around each (one frame of pulse).

def variant_echo(bg, entities, refs) -> pygame.Surface:
    scene = bg.copy()
    _apply_dark_overlay(scene, 120)

    # Soft tint halo first so the rings have a hint of glow underneath.
    halo = _blurred_silhouette(entities, scale=0.10, color=(40, 170, 60))
    halo.set_alpha(120)
    scene.blit(halo, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    def rings(cx, cy, base_r, ring_count, alpha_start, ring_w=2):
        for i in range(ring_count):
            rr = int(base_r * (1 + i * 0.55))
            a  = max(0, alpha_start - i * 60)
            if a <= 0:
                continue
            s = pygame.Surface((rr * 2 + 4, rr * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(s, (90, 255, 120, a),
                               (rr + 2, rr + 2), rr, ring_w)
            # Inner bright accent
            pygame.draw.circle(s, (180, 255, 200, a // 2),
                               (rr + 2, rr + 2), rr, 1)
            scene.blit(s, (cx - rr - 2, cy - rr - 2),
                       special_flags=pygame.BLEND_RGBA_ADD)

    for c in refs["coins"]:
        rings(int(c.x), int(c.y), base_r=COIN_R + 6, ring_count=3,
              alpha_start=180)
    m = refs["powerup"]
    rings(int(m.x), int(m.y), base_r=POWERUP_R + 8, ring_count=4,
          alpha_start=200)
    b = refs["bird"]
    rings(int(b.x), int(b.y), base_r=22, ring_count=4, alpha_start=210)

    # Pillar "echo": one pair of staggered rings around each pillar top/bottom.
    for p in refs["pipes"]:
        cx = int(p.x + PIPE_W / 2)
        cy_top = int(p.gap_y - p.gap_h / 2)
        cy_bot = int(p.gap_y + p.gap_h / 2)
        rings(cx, cy_top, base_r=PIPE_W // 2 + 8, ring_count=3,
              alpha_start=140)
        rings(cx, cy_bot, base_r=PIPE_W // 2 + 8, ring_count=3,
              alpha_start=140)

    tinted = _green_tint_preserving_texture(entities, tint=(80, 255, 100))
    scene.blit(tinted, (0, 0))
    return scene


# ─── driver ─────────────────────────────────────────────────────────────────

VARIANTS = [
    ("variant_1_phosphor.png", variant_phosphor),
    ("variant_2_rimlight.png", variant_rimlight),
    ("variant_3_bloom.png",    variant_bloom),
    ("variant_4_godrays.png",  variant_godrays),
    ("variant_5_echo.png",     variant_echo),
]


def main() -> int:
    out_dir = os.path.join(_REPO, "docs", "screenshots", "nightglow_variants")
    os.makedirs(out_dir, exist_ok=True)

    bg, entities, refs = render_base()
    for fname, fn in VARIANTS:
        frame = fn(bg, entities, refs)
        out_path = os.path.join(out_dir, fname)
        pygame.image.save(frame, out_path)
        print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
